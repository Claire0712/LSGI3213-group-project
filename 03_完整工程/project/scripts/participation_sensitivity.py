"""Nested participation sensitivity; separate from the original factorial experiment."""
from pathlib import Path
import json, shutil, random, xml.etree.ElementTree as E
import pandas as pd
from build_scenarios import write, param
from run_scenarios import run
from analyze import analyze_run
ROOT=Path(__file__).resolve().parents[1]

def main():
    people=E.parse(ROOT/'scenarios/baseline/plans.xml').getroot().findall('person')
    ids=[p.get('id') for p in people]
    random.Random(3213).shuffle(ids)
    rows=[];matrix=[]
    for rate in [25,50,75]:
        name=f'participation{rate}';d=ROOT/'scenarios'/name;d.mkdir(exist_ok=True)
        selected=ids[:len(ids)*rate//100];times={pid:19800+(i+.5)*3600/len(selected) for i,pid in enumerate(selected)}
        pop=E.parse(ROOT/'scenarios/baseline/plans.xml').getroot()
        for person in pop.findall('person'):
            if person.get('id') in times:person.find('.//act').set('end_time',str(times[person.get('id')]))
        assert len(times)==20*rate
        write(pop,d/'plans.xml','plans')
        for f in ['network.xml','facilities.xml']:shutil.copy2(ROOT/'scenarios/baseline'/f,d/f)
        (d/'participants.json').write_text(json.dumps({'rate_percent':rate,'selection_seed':3213,'person_ids':selected},indent=2))
        for seed in [4711,42,2025]:
            c=E.parse(ROOT/'scenarios/baseline'/f'config_s{seed}.xml').getroot()
            param(c,'controler','outputDirectory',f'./runs/{name}_s{seed}')
            write(c,d/f'config_s{seed}.xml','config')
            r=dict(scenario=name,seed=seed,iterations=100,config=str((d/f'config_s{seed}.xml').relative_to(ROOT)))
            matrix.append(r);run(r);row=analyze_run(r);row['participation_pct']=rate;rows.append(row)
            pd.DataFrame(rows).to_csv(ROOT/'analysis/participation_partial.csv',index=False)
    base=pd.read_csv(ROOT/'analysis/summary_by_run.csv')
    for name,rate in [('baseline',0),('stagger',100)]:
        for row in base[base.scenario==name].to_dict('records'):row['participation_pct']=rate;rows.append(row)
    result=pd.DataFrame(rows).sort_values(['participation_pct','seed'])
    result.to_csv(ROOT/'analysis/participation_by_run.csv',index=False)
    result.groupby('participation_pct').agg({k:['mean','min','max'] for k in ['am_mean_min','mean_score','am_p95_min']}).to_csv(ROOT/'analysis/participation_summary.csv')
    (ROOT/'scenarios/participation_matrix.json').write_text(json.dumps(matrix,indent=2))
    print(result[['participation_pct','seed','am_mean_min','mean_score']].to_string(index=False))
if __name__=='__main__':main()
