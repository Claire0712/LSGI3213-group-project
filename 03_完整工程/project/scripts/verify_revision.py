"""Check revised narrative values against saved data and submission copies."""
from pathlib import Path
import json,hashlib
import pandas as pd
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
def main():
    slides=json.loads((ROOT/'analysis/slides_content.json').read_text())
    assert len(slides)==19 and sum(s['seconds'] for s in slides)==1200
    part=pd.read_csv(ROOT/'analysis/participation_by_run.csv')
    chart=next(s['chart'] for s in slides if s['title']=='Sensitivity to participation')
    expected=part.groupby('participation_pct').am_mean_min.mean()
    assert chart['categories']==[f'{int(x)}%' for x in expected.index]
    assert chart['series'][0]['y']==expected.tolist()
    losses=[]
    for seed in [4711,42,2025]:
        base=pd.read_csv(ROOT/'analysis'/f'baseline_s{seed}_scores.csv.gz').set_index('person').score
        for scenario in ['stagger','combined']:
            other=pd.read_csv(ROOT/'analysis'/f'{scenario}_s{seed}_scores.csv.gz').set_index('person').score
            assert base.index.is_unique and other.index.is_unique and set(base.index)==set(other.index)
            pct=100*(other.reindex(base.index)<base).mean();losses.append(pct)
    assert round(min(losses),1)==41.2 and round(max(losses),1)==41.6
    report=PdfReader(ROOT/'deliverables/LSGI3213_Equil_Report.pdf')
    text='\n'.join(p.extract_text() for p in report.pages)
    for claim in ['ZHANG Shizhuo','Sensitivity to participation','2026','byte-identical','25%','75%']:assert claim in text,claim
    slidepdf=PdfReader(ROOT/'deliverables/LSGI3213_Equil_Slides.pdf')
    assert len(slidepdf.pages)==19 and '20-minute' in slidepdf.pages[0].extract_text()
    target=ROOT.parents[1]/'02_提交成果'
    for f in ['LSGI3213_Equil_Report.pdf','LSGI3213_Equil_Slides.pdf','LSGI3213_Equil_Slides.pptx','Presentation_Script_and_QA.md']:
        assert (ROOT/'deliverables'/f).read_bytes()==(target/f).read_bytes(),f
    result=dict(slides=19,presentation_seconds=1200,report_pages=len(report.pages),score_loss_pct_range=[min(losses),max(losses)],submission_copies_identical=True)
    (ROOT/'docs/revision_validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
