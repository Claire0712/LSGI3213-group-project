from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for s in ['capacity','stagger','combined','adaptive']:
    for seed in [4711,42,2025]:
        b=pd.read_csv(ROOT/'analysis'/f'baseline_s{seed}_scores.csv.gz');a=pd.read_csv(ROOT/'analysis'/f'{s}_s{seed}_scores.csv.gz')
        d=a.merge(b,on='person',suffixes=('_t','_b'),validate='one_to_one');delta=d.score_t-d.score_b
        rows.append(dict(scenario=s,seed=seed,score_losers_pct=100*(delta < -1e-9).mean(),score_winners_pct=100*(delta > 1e-9).mean(),mean_score_change=delta.mean()))
pd.DataFrame(rows).to_csv(ROOT/'analysis/individual_score_changes.csv',index=False)
