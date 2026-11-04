"""Independently reconstruct extension metrics from saved MATSim events and native outputs."""
from pathlib import Path
import argparse,json,gzip,xml.etree.ElementTree as E,collections,hashlib
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parent
CORRIDOR={str(i) for i in range(11,20)}
def seconds(t):
 h,m,s=map(float,t.split(':'));return h*3600+m*60+s
def check_run(folder,config_folder,iterations):
 dep={};seq=collections.Counter();trips=[];entered={};delays=[];occupancy=0;peak=0;flows=collections.Counter();stuck=0;work={};dur=[]
 net={e.get('id'):dict(e.attrib) for e in E.parse(config_folder/'network.xml').findall('./links/link')}
 with gzip.open(folder/'output_events.xml.gz','rb') as f:
  for _,el in E.iterparse(f,events=['end']):
   if el.tag!='event':continue
   a=el.attrib;typ=a['type'];t=float(a['time']);p=a.get('person');v=a.get('vehicle');l=a.get('link')
   if typ=='departure' and a.get('legMode')=='car':assert p not in dep;seq[p]+=1;dep[p]=t
   elif typ=='arrival' and a.get('legMode')=='car':trips.append((p,seq[p],dep.pop(p),t))
   elif typ=='stuckAndAbort':stuck+=1
   elif typ=='entered link' and l in CORRIDOR:entered[(v,l)]=t;occupancy+=1;peak=max(peak,occupancy)
   elif typ=='left link' and l in CORRIDOR:
    start=entered.pop((v,l));ff=float(net[l]['length'])/float(net[l]['freespeed']);delays.append((v,l,t-start,max(0,t-start-ff)));occupancy-=1;assert occupancy>=0;flows[(l,int(t//300))]+=1
   if a.get('actType')=='w':
    if typ=='actstart':work[p]=t
    elif typ=='actend':dur.append(t-work.pop(p))
   el.clear()
 assert not dep and not entered and occupancy==0 and stuck==0 and len(trips)==4000 and len(delays)==2000
 assert len(dur)==2000 and np.allclose(dur,28800)
 tr=pd.DataFrame(trips,columns=['person','trip_number','departure_s','arrival_s']);tr['travel_s']=tr.arrival_s-tr.departure_s
 native=pd.read_csv(folder/'output_trips.csv.gz',sep=';',dtype={'person':str});m=tr.merge(native,on=['person','trip_number'],validate='one_to_one');assert len(m)==4000 and np.allclose(m.travel_s,m.trav_time.map(seconds),rtol=0,atol=1e-9)
 pop=E.fromstring(gzip.open(folder/'output_plans.xml.gz').read());sc=pd.DataFrame([{'person':p.get('id'),'score':float(p.find("./plan[@selected='yes']").get('score'))} for p in pop.findall('person')]);assert len(sc)==2000
 history=pd.read_csv(folder/'scorestats.txt',sep='\t');assert int(history.iloc[-1,0])==iterations and np.isclose(sc.score.mean(),history.iloc[-1]['avg. EXECUTED'],rtol=0,atol=1e-9)
 am=m[m.trip_number==1].copy();am['preopening_gap_min']=np.maximum(0,25200-am.arrival_s)/60
 individual=am[['person','departure_s','arrival_s','travel_s','preopening_gap_min']].merge(sc,on='person',validate='one_to_one')
 speeds={float(x['freespeed']) for x in net.values()};assert len(speeds)==1;ff=am.traveled_distance.iloc[0]/speeds.pop()/60
 metrics=dict(completed_trips=len(m),stuck=stuck,agents=len(sc),am_mean_min=am.travel_s.mean()/60,am_p95_min=am.travel_s.quantile(.95)/60,daily_mean_min=m.travel_s.mean()/60,mean_score=sc.score.mean(),corridor_mean_delay_min=np.mean([x[3] for x in delays])/60,corridor_peak_vehicles=peak,max_single_link_5min_exit_flow_vph=max(flows.values())*12,am_route_freeflow_min=ff,am_mean_distance_m=am.traveled_distance.mean(),mean_preopening_gap_min=am.preopening_gap_min.mean(),am_departure_mean_h=am.departure_s.mean()/3600,am_departure_sd_min=am.departure_s.std()/60)
 return metrics,individual,history

def main(source):
 results=ROOT/'results';results.mkdir(exist_ok=True);matrix=json.loads((ROOT/'experiment_matrix.json').read_text());rows=[];people=[];histories=[];checkpoints=[];proof=[]
 bases={}
 for seed in [4711,42,2025]:
  _,ind,_=check_run(source/'runs'/f'baseline_s{seed}',source/'scenarios/baseline',100);bases[seed]=ind[['person','score','travel_s']].rename(columns={'score':'baseline_score','travel_s':'baseline_travel_s'})
 for r in matrix:
  name=r.get('source_scenario',r['scenario']);root=source if r['origin']=='verified_existing' else ROOT;key=f"{name}_s{r['seed']}";folder=root/'runs'/key;status=json.loads((root/'runs'/f'{key}.status.json').read_text());assert status['exit_code']==0
  for path,digest in status['input_sha256'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest
  assert 'shutdown completed' in (root/'runs'/f'{key}.console.log').read_text()
  metrics,ind,h=check_run(folder,root/'scenarios'/name,r['iterations']);ind=ind.merge(bases[r['seed']],on='person',validate='one_to_one');ind['score_change']=ind.score-ind.baseline_score;ind['travel_change_min']=(ind.travel_s-ind.baseline_travel_s)/60
  metrics['score_losers_pct']=(ind.score_change < -1e-9).mean()*100;metrics['score_winners_pct']=(ind.score_change>1e-9).mean()*100
  rows.append({**r,**metrics});ind['scenario']=r['scenario'];ind['seed']=r['seed'];ind['departure_bin_15min']=np.floor(ind.departure_s/900).astype(int);people.append(ind)
  proof.append(dict(run=key,origin=r['origin'],events_sha256=hashlib.sha256((folder/'output_events.xml.gz').read_bytes()).hexdigest(),native_trips_sha256=hashlib.sha256((folder/'output_trips.csv.gz').read_bytes()).hexdigest(),checked_trips=4000,checked_people=2000))
  if r['kind']=='convergence':
   h['seed']=r['seed'];histories.append(h)
   old=pd.read_csv(source/'runs'/f"adaptive_s{r['seed']}"/'scorestats.txt',sep='\t')
   assert np.allclose(old['avg. EXECUTED'],h['avg. EXECUTED'].iloc[:len(old)],rtol=0,atol=1e-9)
   for it in [100,200,300,400,500]:
    t=pd.read_csv(folder/f'ITERS/it.{it}/{it}.trips.csv.gz',sep=';');am=t[t.trip_number==1]
    checkpoints.append(dict(seed=r['seed'],iteration=it,am_mean_min=am.trav_time.map(seconds).mean()/60,departure_mean_h=am.dep_time.map(seconds).mean()/3600,mean_score=float(h.loc[h.iloc[:,0]==it,'avg. EXECUTED'].iloc[0])))
  print('CHECKED',key,round(metrics['am_mean_min'],4),flush=True)
 allruns=pd.DataFrame(rows);allruns.to_csv(results/'all_runs.csv',index=False);pd.DataFrame(proof).to_json(results/'validation.json',orient='records',indent=2)
 grid=allruns[allruns.kind=='grid'];measure=['am_mean_min','am_p95_min','mean_score','corridor_mean_delay_min','corridor_peak_vehicles','score_losers_pct','mean_preopening_gap_min']
 grid.groupby(['capacity_factor','spread_minutes'])[measure].agg(['mean','min','max','std']).to_csv(results/'grid_summary.csv')
 paired=[]
 for seed in [4711,42,2025]:
  x=grid[grid.seed==seed].set_index(['capacity_factor','spread_minutes'])
  for w in [0,30,60]:
   base=x.loc[(1.,w)]
   for c in [1.5,2.]:
    treat=x.loc[(c,w)];paired.append(dict(seed=seed,comparison='capacity_vs_1x_same_spread',spread_minutes=w,capacity_factor=c,minutes_saved=base.am_mean_min-treat.am_mean_min,pct_saved=100*(base.am_mean_min-treat.am_mean_min)/base.am_mean_min,score_change=treat.mean_score-base.mean_score))
  for w in [0,30]:
   base=x.loc[(1.,w)];treat=x.loc[(1.,60)];paired.append(dict(seed=seed,comparison='spread60_vs_existing_spread',spread_minutes=w,capacity_factor=1.,minutes_saved=base.am_mean_min-treat.am_mean_min,pct_saved=100*(base.am_mean_min-treat.am_mean_min)/base.am_mean_min,score_change=treat.mean_score-base.mean_score))
 pd.DataFrame(paired).to_csv(results/'paired_effects.csv',index=False)
 people=pd.concat(people);people.to_csv(results/'individual_outcomes.csv.gz',index=False)
 people.groupby(['scenario','seed','departure_bin_15min']).agg(n=('person','size'),mean_score_change=('score_change','mean'),losers_pct=('score_change',lambda x:100*(x < -1e-9).mean()),mean_travel_change_min=('travel_change_min','mean'),mean_preopening_gap_min=('preopening_gap_min','mean')).to_csv(results/'departure_group_outcomes.csv')
 history=pd.concat(histories);history.to_csv(results/'adaptive_score_histories.csv',index=False);pd.DataFrame(checkpoints).to_csv(results/'adaptive_checkpoints.csv',index=False)
 stability=[]
 for seed,h in history.groupby('seed'):
  prev=h[h.iloc[:,0].between(401,450)]['avg. EXECUTED'];last=h[h.iloc[:,0].between(451,500)]['avg. EXECUTED'];delta=last.mean()-prev.mean()
  stability.append(dict(seed=int(seed),previous50_mean=prev.mean(),last50_mean=last.mean(),mean_change=delta,last50_range=last.max()-last.min(),last50_slope_utils_per_iteration=float(np.polyfit(np.arange(50),last,1)[0]),passes_descriptive_005_screen=bool(abs(delta)<=.05)))
 pd.DataFrame(stability).to_csv(results/'adaptive_stability.csv',index=False)
 print('ALL 30 RUN RECORDS VERIFIED',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);a=ap.parse_args();main(a.source.resolve())
