from pathlib import Path
import xml.etree.ElementTree as E
import shutil,json
from build_scenarios import ROOT,param,write
from run_scenarios import run
from analyze import analyze_run

def main():
    rows=[]
    for name in ['baseline','adaptive']:
        long=name+'200';d=ROOT/'scenarios'/long;d.mkdir(exist_ok=True)
        for f in ['network.xml','plans.xml','facilities.xml']:shutil.copy2(ROOT/'scenarios'/name/f,d/f)
        c=E.parse(ROOT/'scenarios'/name/'config_s4711.xml').getroot()
        param(c,'controler','lastIteration',200);param(c,'controler','outputDirectory',f'./runs/{long}_s4711')
        write(c,d/'config_s4711.xml','config')
        r=dict(scenario=long,seed=4711,iterations=200,config=f'scenarios/{long}/config_s4711.xml')
        run(r);a=analyze_run(r)
        import pandas as pd
        original=pd.read_csv(ROOT/'analysis/summary_by_run.csv');o=original[(original.scenario==name)&(original.seed==4711)].iloc[0]
        rows.append(dict(scenario=name,seed=4711,am_mean_min=a['am_mean_min'],mean_score=a['mean_score'],original_am_mean_min=float(o.am_mean_min),original_score=float(o.mean_score),score_tail_change=a['score_tail_change']))
        (ROOT/'analysis/sensitivity.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
