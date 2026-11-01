from pathlib import Path
import argparse,shutil
p=argparse.ArgumentParser(description='Copy submission files with real group metadata')
p.add_argument('--group',required=True);p.add_argument('--leader',required=True);a=p.parse_args()
for x in [a.group,a.leader]:
    if not x.strip() or '/' in x or '\\' in x:raise ValueError('Use a nonempty group/name without path separators')
root=Path(__file__).resolve().parents[1]/'deliverables';gid=a.group if a.group.lower().startswith('group ') else 'Group '+a.group
for src,suffix in [('LSGI3213_Equil_Report.pdf','Report.pdf'),('LSGI3213_Equil_Slides.pdf','Slides.pdf'),('LSGI3213_Equil_Slides.pptx','Slides.pptx')]:
    dest=root/f'{gid}_{a.leader}_{suffix}'
    if dest.exists():raise FileExistsError(dest)
    shutil.copy2(root/src,dest);print(dest)
