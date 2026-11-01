"""Audit MATSim events, derive trip/link measures, and aggregate paired seeds."""
from pathlib import Path
import gzip,xml.etree.ElementTree as E,json,collections
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def parse_events(events):
    departures={};seq=collections.Counter();trips=[];enters={};trav=[];occup=[];stuck=0;nd=0;missing_arr=0
    for a in events:
        typ=a['type'];t=float(a['time']);p=a.get('person');v=a.get('vehicle');l=a.get('link')
        if typ=='departure' and a.get('legMode')=='car':
            assert p not in departures,(p,'duplicate departure')
            nd+=1;seq[p]+=1;departures[p]=t
        elif typ=='arrival' and a.get('legMode')=='car':
            if p not in departures:missing_arr+=1;continue
            dep=departures.pop(p);trips.append(dict(person=p,trip_number=seq[p],departure_s=dep,arrival_s=t,travel_s=t-dep))
        elif typ=='stuckAndAbort':
            stuck+=1;departures.pop(p,None)
        elif typ=='entered link':
            enters[(v,l)]=t;occup.append((t,l,1))
        elif typ=='left link':
            occup.append((t,l,-1))
            if (v,l) in enters:
                enter=enters.pop((v,l));trav.append(dict(vehicle=v,link=l,entry_s=enter,exit_s=t,travel_s=t-enter))
        elif typ=='vehicle enters traffic':occup.append((t,l,1))
        elif typ=='vehicle leaves traffic':
            occup.append((t,l,-1));enters.pop((v,l),None)
    return dict(trips=trips,traversals=trav,occupancy_events=occup,departures=nd,stuck=stuck,unmatched_departures=len(departures),unmatched_arrivals=missing_arr)

def stream(path):
    with gzip.open(path,'rb') as f:
        for _,elem in E.iterparse(f,events=['end']):
            if elem.tag=='event':yield dict(elem.attrib);elem.clear()

def seconds(x):
    h,m,s=map(float,x.split(':'));return 3600*h+60*m+s

def analyze_run(r):
    key=f"{r['scenario']}_s{r['seed']}";d=ROOT/'runs'/key
    result=parse_events(stream(d/'output_events.xml.gz'))
    trip=pd.DataFrame(result.pop('trips'));tr=pd.DataFrame(result.pop('traversals'))
    occ=result.pop('occupancy_events')
    native=pd.read_csv(d/'output_trips.csv.gz',sep=';');native['person']=native.person.astype(str)
    check=trip.merge(native[['person','trip_number','trav_time']],on=['person','trip_number'],validate='one_to_one')
    assert len(check)==len(trip)==len(native)
    assert np.allclose(check.travel_s,check.trav_time.map(seconds))
    assert not result['unmatched_departures'] and not result['unmatched_arrivals'] and not result['stuck']
    assert result['departures']==len(trip)
    expected=201 if r['scenario']=='original100' else 4000
    if r['scenario']!='original100':
        corridor_counts=tr[tr.link.isin(list(map(str,range(11,20))))].groupby('vehicle').size()
        assert len(corridor_counts)==2000 and (corridor_counts==1).all()
    assert len(trip)==expected,(key,len(trip),expected)
    score=pd.read_csv(d/'scorestats.txt',sep='\t');last=score.iloc[-1]
    assert int(last.iloc[0])==r['iterations']
    pop=E.fromstring(gzip.open(d/'output_plans.xml.gz').read())
    scores=pd.DataFrame([{'person':p.get('id'),'score':float(p.find("./plan[@selected='yes']").get('score'))} for p in pop.findall('person')])
    assert np.isclose(scores.score.mean(),float(last['avg. EXECUTED']))
    nodes=E.parse(ROOT/'scenarios'/r['scenario']/'network.xml').getroot()
    links={l.get('id'):l.attrib for l in nodes.findall('./links/link')}
    metrics=[]
    for width in [300,900]:
        # Integrate exact occupancy over bins; activity-link insertion/removal events are included.
        area=collections.defaultdict(float);state=collections.defaultdict(int);prev=collections.defaultdict(float);peak=collections.defaultdict(int)
        for t,l,delta in occ:
            start=prev[l]
            while start<t:
                b=int(start//width);end=min(t,(b+1)*width)
                area[(l,b)]+=state[l]*(end-start);peak[(l,b)]=max(peak[(l,b)],state[l]);start=end
            state[l]+=delta;assert state[l]>=0,(key,l,t,state[l]);prev[l]=t
            peak[(l,int(t//width))]=max(peak[(l,int(t//width))],state[l])
        assert all(v==0 for v in state.values()),state
        for l,meta in links.items():
            lt=tr[tr.link==l];length=float(meta['length']);cap=float(meta['capacity']);ff=length/float(meta['freespeed'])
            for b in range(96*900//width):
                x=lt[(lt.entry_s>=b*width)&(lt.entry_s<(b+1)*width)]
                exits=((lt.exit_s>=b*width)&(lt.exit_s<(b+1)*width)).sum()
                metrics.append(dict(link=l,bin_seconds=width,bin_start_s=b*width,entries=len(x),exits=int(exits),exit_flow_vph=float(exits)*3600/width,capacity_vph=cap,flow_capacity_ratio=float(exits)*3600/width/cap,mean_travel_s=x.travel_s.mean() if len(x) else np.nan,free_flow_s=ff,mean_delay_s=(x.travel_s-ff).clip(lower=0).mean() if len(x) else np.nan,speed_kmh=length/1000/(x.travel_s.mean()/3600) if len(x) and x.travel_s.mean()>0 else np.nan,mean_occupancy=area[(l,b)]/width,density_veh_km_lane=area[(l,b)]/width/(length/1000)/float(meta['permlanes']),max_occupancy=peak[(l,b)],full_link_measure=l not in ['1','20']))
    link_metrics=pd.DataFrame(metrics)
    endpoint=~link_metrics.full_link_measure
    link_metrics.loc[endpoint,['entries','exits','exit_flow_vph','flow_capacity_ratio','mean_travel_s','mean_delay_s','speed_kmh']]=np.nan
    assert (link_metrics.max_occupancy+1e-9>=link_metrics.mean_occupancy).all()
    for obj,label in [(trip,'trips'),(tr,'traversals'),(link_metrics,'links'),(scores,'scores'),(score,'score_history')]:obj.to_csv(ROOT/'analysis'/f'{key}_{label}.csv.gz',index=False)
    am=trip[trip.trip_number==1];pm=trip[trip.trip_number==2]
    corridor=tr[tr.link.isin(list(map(str,range(11,20))))]
    summary={**r,**result,'completed_trips':len(trip),'agents':len(scores),'mean_trip_min':trip.travel_s.mean()/60,'p95_trip_min':trip.travel_s.quantile(.95)/60,'total_travel_h':trip.travel_s.sum()/3600,'am_mean_min':am.travel_s.mean()/60,'am_p95_min':am.travel_s.quantile(.95)/60,'pm_mean_min':pm.travel_s.mean()/60,'mean_score':scores.score.mean(),'score_p05':scores.score.quantile(.05),'score_p95':scores.score.quantile(.95),'am_departure_mean_h':am.departure_s.mean()/3600,'am_departure_sd_min':am.departure_s.std()/60,'am_departure_min_h':am.departure_s.min()/3600,'am_departure_max_h':am.departure_s.max()/3600,'am_before_7_pct':100*(am.arrival_s<25200).mean(),'score_last10_mean':score['avg. EXECUTED'].tail(10).mean(),'score_previous10_mean':score['avg. EXECUTED'].iloc[-20:-10].mean(),'score_last10_range':score['avg. EXECUTED'].tail(10).max()-score['avg. EXECUTED'].tail(10).min(),'corridor_mean_delay_min':(corridor.travel_s-5000/27.78).clip(lower=0).mean()/60}
    summary['score_tail_change']=summary['score_last10_mean']-summary['score_previous10_mean']
    print(key,'trips',len(trip),'AM',round(summary['am_mean_min'],2),'score',round(summary['mean_score'],3),'tailchange',round(summary['score_tail_change'],3),flush=True)
    return summary

def main():
    rows=[]
    for r in json.loads((ROOT/'scenarios/run_matrix.json').read_text()):
        key=f"{r['scenario']}_s{r['seed']}";s=ROOT/'runs'/f'{key}.status.json'
        if s.exists() and json.loads(s.read_text())['exit_code']==0:rows.append(analyze_run(r))
    result=pd.DataFrame(rows);result.to_csv(ROOT/'analysis/summary_by_run.csv',index=False)
    result.groupby('scenario').agg({k:['mean','min','max','std'] for k in ['am_mean_min','am_p95_min','mean_trip_min','total_travel_h','mean_score','corridor_mean_delay_min','score_tail_change']}).to_csv(ROOT/'analysis/summary_by_scenario.csv')
    print(result[['scenario','seed','am_mean_min','mean_score']].to_string(index=False))
if __name__=='__main__':main()
