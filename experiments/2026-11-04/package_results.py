"""Package portable scripts, inputs, reports and reduced native simulation evidence."""
from pathlib import Path
import json,hashlib,shutil,zipfile
R=Path(__file__).resolve().parent
O=R.parents[1]/'outputs';P=O/'experiment_extension';U=O/'github_upload'
P.mkdir(exist_ok=True);U.mkdir(exist_ok=True)
for name in ['run_extension.py','validate_design.py','analyze_extension.py','make_report.py','package_results.py','experiment_matrix.json','provenance.json','runtime_sha256.json','README.md']:
 shutil.copy2(R/name,P/name)
for name in ['scenarios','results','figures']:
 shutil.copytree(R/name,P/name,dirs_exist_ok=True)
for r in json.loads((R/'experiment_matrix.json').read_text()):
 if r['origin']!='new':continue
 key=f"{r['scenario']}_s{r['seed']}";target=P/'runs'/key;target.mkdir(parents=True,exist_ok=True)
 for f in ['output_events.xml.gz','output_trips.csv.gz','output_plans.xml.gz','output_config.xml','output_network.xml.gz','scorestats.txt','traveldistancestats.txt']:
  shutil.copy2(R/'runs'/key/f,target/f)
 for suffix in ['.status.json','.console.log']:shutil.copy2(R/'runs'/(key+suffix),P/'runs'/(key+suffix))
 if r['kind']=='convergence':
  for it in [100,200,300,400,500]:
   f=Path(f'ITERS/it.{it}/{it}.trips.csv.gz');(target/f).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'runs'/key/f,target/f)
V=P/'prior_verification';V.mkdir(exist_ok=True)
for name in ['rerun_comparison.json','original_results_independent_check.json','仿真核验结果.txt']:
 if (O/name).exists():shutil.copy2(O/name,V/name)
manifest={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and f.name!='SHA256SUMS.json'}
(P/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
archive=U/'experiment_extension.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in P.rglob('*'):
  if f.is_file():z.write(f,Path('experiment_extension')/f.relative_to(P))
assert archive.stat().st_size<25_000_000,archive.stat().st_size
for f in list((P/'figures').glob('*.png'))+list((P/'results').glob('*'))+list(P.glob('*.py'))+list(P.glob('*.json')):shutil.copy2(f,U/f.name)
readme=(P/'README.md').read_text().replace('](figures/','](').replace('`results/','`')
readme=readme.replace('## 5. 如何复现','完整脚本、输入、结果、原生核验证据和文件校验值均见 [下载实验包](experiment_extension.zip)。下载并解压后，在 experiment_extension 目录中运行下列命令。\n\n## 5. 如何复现')
(U/'README.md').write_text(readme)
(U/'ARCHIVE_SHA256.txt').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  experiment_extension.zip\n')
print('archive bytes',archive.stat().st_size,'files',len(manifest),'upload files',len(list(U.iterdir())))
