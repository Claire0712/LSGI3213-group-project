"""Validate persisted evidence; assertions are scoped and independently inspect outputs."""
from pathlib import Path
import json,hashlib,gzip,xml.etree.ElementTree as E,collections,zipfile
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main():
    result={}
    for m in json.loads((ROOT/'data/source_manifest.json').read_text()):assert hashlib.sha256((ROOT/'data/raw'/m['file']).read_bytes()).hexdigest()==m['sha256']
    result['official_downloads_hash_verified']=5
    files=list((ROOT/'runs').glob('*.status.json'));assert len(files)==27
    for f in files:
        status=json.loads(f.read_text());assert status['exit_code']==0
        for path,digest in status['input_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
        key=f.stem.removesuffix('.status');r=ROOT/'runs'/key
        assert 'shutdown completed' in (ROOT/'runs'/f'{key}.console.log').read_text()
        assert (r/'output_events.xml.gz').stat().st_size>1000
        native=pd.read_csv(r/'output_trips.csv.gz',sep=';');trips=pd.read_csv(ROOT/'analysis'/f'{key}_trips.csv.gz')
        check=trips.merge(native[['person','trip_number','trav_time']],on=['person','trip_number'],validate='one_to_one')
        sec=check.trav_time.map(lambda x:sum(float(v)*w for v,w in zip(x.split(':'),[3600,60,1])))
        assert len(check)==len(native)==len(trips);assert np.allclose(check.travel_s,sec)
        h=pd.read_csv(r/'scorestats.txt',sep='\t');sc=pd.read_csv(ROOT/'analysis'/f'{key}_scores.csv.gz')
        assert int(h.iloc[-1,0])==status['iterations'];assert np.isclose(sc.score.mean(),h.iloc[-1]['avg. EXECUTED'])
        lm=pd.read_csv(ROOT/'analysis'/f'{key}_links.csv.gz');assert(lm.max_occupancy+1e-9>=lm.mean_occupancy).all()
        assert lm[lm.link.isin([1,20])].exit_flow_vph.isna().all()
    result['successful_and_independently_checked_runs']=len(files)
    s=pd.read_csv(ROOT/'analysis/summary_by_run.csv');main=s[s.scenario!='original100'];assert len(main)==15
    assert(main.completed_trips==4000).all() and (main.stuck==0).all()
    result['main_final_day_trips_verified']=int(main.completed_trips.sum())
    result['original_example_final_day_trips']=int(s[s.scenario=='original100'].completed_trips.iloc[0])
    # Direct network attribute comparison, not a construction-script assumption.
    base={l.get('id'):dict(l.attrib) for l in E.parse(ROOT/'data/raw/network.xml').findall('./links/link')}
    for scenario in ['baseline','capacity','stagger','combined','adaptive']:
        n={l.get('id'):dict(l.attrib) for l in E.parse(ROOT/'scenarios'/scenario/'network.xml').findall('./links/link')}
        assert n.keys()==base.keys()
        for k,v in n.items():
            expected=dict(base[k])
            if scenario in ['capacity','combined'] and 11<=int(k)<=19:expected['capacity']='2000'
            assert v==expected
        # Work activity durations from actual events, not plan attributes.
        starts={};dur=[]
        with gzip.open(ROOT/'runs'/f'{scenario}_s4711/output_events.xml.gz','rb') as stream:
            for _,el in E.iterparse(stream,events=['end']):
                if el.tag=='event':
                    a=el.attrib
                    if a.get('actType')=='w':
                        if a['type']=='actstart':starts[a['person']]=float(a['time'])
                        if a['type']=='actend':dur.append(float(a['time'])-starts.pop(a['person']))
                    el.clear()
        assert len(dur)==2000 and set(dur)=={28800.0}
    result['network_treatments_verified']=True;result['work_duration_events_verified']=10000
    comparison=json.loads((ROOT/'data/course_zip_comparison.json').read_text())
    assert len(comparison)==4
    for item in comparison:
        assert hashlib.sha256((ROOT/item['raw_file']).read_bytes()).hexdigest()==item['sha256']
    participation=pd.read_csv(ROOT/'analysis/participation_by_run.csv')
    assert len(participation)==15
    assert set(participation.participation_pct)=={0,25,50,75,100}
    assert (participation.completed_trips==4000).all() and (participation.stuck==0).all()
    previous=set()
    for rate in [25,50,75]:
        directory=ROOT/'scenarios'/f'participation{rate}'
        selected=set(json.loads((directory/'participants.json').read_text())['person_ids'])
        assert len(selected)==rate*20 and previous<=selected
        previous=selected
        people=E.parse(directory/'plans.xml').getroot().findall('person')
        times=[sum(float(v)*w for v,w in zip(p.find('.//act').get('end_time').split(':'),[3600,60,1])) if ':' in p.find('.//act').get('end_time') else float(p.find('.//act').get('end_time')) for p in people]
        assert len(people)==2000 and np.isclose(np.mean(times),21600)
        for person in people:
            if person.get('id') not in selected:assert person.find('.//act').get('end_time') in ['06:00:00','21600','21600.0']
        for seed in [4711,42,2025]:
            actual=E.parse(directory/f'config_s{seed}.xml').getroot()
            expected=E.parse(ROOT/'scenarios/baseline'/f'config_s{seed}.xml').getroot()
            actual.find('./module[@name="controler"]/param[@name="outputDirectory"]').set('value',expected.find('./module[@name="controler"]/param[@name="outputDirectory"]').get('value'))
            assert E.tostring(actual)==E.tostring(expected)
        assert (directory/'network.xml').read_bytes()==(ROOT/'scenarios/baseline/network.xml').read_bytes()
    result['participation_runs_verified']=15
    slides=json.loads((ROOT/'analysis/slides_content.json').read_text());assert len(slides)==19;assert sum(x['seconds'] for x in slides)==1200
    result['presentation_seconds']=1200
    ppt=ROOT/'deliverables/LSGI3213_Equil_Slides.pptx'
    with zipfile.ZipFile(ppt) as z:
        slide_names=[n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml') and '/_rels/' not in n]
        assert len(slide_names)==19
    result['pptx_slides']=19
    try:
        from pypdf import PdfReader
        rep=PdfReader(ROOT/'deliverables/LSGI3213_Equil_Report.pdf');sl=PdfReader(ROOT/'deliverables/LSGI3213_Equil_Slides.pdf')
        assert 18 <= len(rep.pages) <= 20 and len(sl.pages)==19
        text='\n'.join(x.extract_text() for x in rep.pages)
        for requirement in ['Abstract','Background','MATSim framework','Scenario design','Trip totals','Daily plan scores','link states','Conclusions','References','AI acknowledgment']:assert requirement.lower() in text.lower(),requirement
        assert all(len(p.extract_text().strip())>80 for p in rep.pages)
        result['report_pages']=len(rep.pages);result['report_body_pages']=len(rep.pages)-1;result['slides_pdf_pages']=19
    except ImportError:raise RuntimeError('Install pypdf to complete PDF verification')
    (ROOT/'docs/validation_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
