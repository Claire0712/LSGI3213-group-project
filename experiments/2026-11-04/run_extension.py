"""Additive sensitivity study. Usage: python run_extension.py --source /path/to/project --workers 3"""
from pathlib import Path
import argparse,xml.etree.ElementTree as E,json,hashlib,shutil,subprocess,time,datetime,concurrent.futures
ROOT=Path(__file__).resolve().parent
SEEDS=[4711,42,2025]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def param(tree,module,name,value):
 m=tree.find(f'./module[@name="{module}"]');p=m.find(f'./param[@name="{name}"]')
 if p is None:p=E.SubElement(m,'param',name=name)
 p.set('value',str(value))
def xml(tree,path,kind):
 E.indent(tree);version=2 if kind=='config' else 4 if kind=='plans' else 1
 path.write_bytes(f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE {kind} SYSTEM "http://www.matsim.org/files/dtd/{kind}_v{version}.dtd">\n'.encode()+E.tostring(tree))
def build(source):
 (ROOT/'scenarios').mkdir(exist_ok=True);(ROOT/'runs').mkdir(exist_ok=True)
 reuse={(1.,0):'baseline',(2.,0):'capacity',(1.,60):'stagger',(2.,60):'combined'}
 matrix=[]
 for factor in [1.,1.5,2.]:
  for width in [0,30,60]:
   for seed in SEEDS:
    name=f'cap{int(factor*100)}_spread{width}';r=dict(scenario=name,seed=seed,capacity_factor=factor,spread_minutes=width,iterations=100,kind='grid')
    if (factor,width) in reuse:
     r.update(origin='verified_existing',source_scenario=reuse[(factor,width)]);matrix.append(r);continue
    d=ROOT/'scenarios'/name;d.mkdir(exist_ok=True)
    n=E.parse(source/'scenarios/baseline/network.xml').getroot()
    for l in n.findall('./links/link'):
     if 11<=int(l.get('id'))<=19:l.set('capacity',str(int(1000*factor)))
    xml(n,d/'network.xml','network');shutil.copyfile(source/'scenarios/baseline/facilities.xml',d/'facilities.xml')
    p=E.parse(source/'scenarios/baseline/plans.xml').getroot();people=p.findall('person');assert len(people)==2000
    if width:
     for i,person in enumerate(people):person.find('.//act').set('end_time',str(21600-width*30+(i+.5)*width*60/len(people)))
    xml(p,d/'plans.xml','plans')
    c=E.parse(source/f'scenarios/baseline/config_s{seed}.xml').getroot();param(c,'controler','outputDirectory',f'./runs/{name}_s{seed}')
    xml(c,d/f'config_s{seed}.xml','config');r.update(origin='new',config=f'scenarios/{name}/config_s{seed}.xml');matrix.append(r)
 for seed in SEEDS:
  name='adaptive500';d=ROOT/'scenarios'/name;d.mkdir(exist_ok=True)
  for f in ['network.xml','plans.xml','facilities.xml']:shutil.copyfile(source/'scenarios/adaptive'/f,d/f)
  c=E.parse(source/f'scenarios/adaptive/config_s{seed}.xml').getroot();param(c,'controler','lastIteration',500);param(c,'controler','outputDirectory',f'./runs/{name}_s{seed}')
  xml(c,d/f'config_s{seed}.xml','config');matrix.append(dict(scenario=name,seed=seed,iterations=500,kind='convergence',origin='new',config=f'scenarios/{name}/config_s{seed}.xml'))
 (ROOT/'experiment_matrix.json').write_text(json.dumps(matrix,indent=2))
 manifest={'source_jar_sha256':sha(source/'runtime/matsim-12.0.jar'),'source_files':{str(p.relative_to(source)):sha(p) for folder in ['scenarios','analysis'] for p in (source/folder).rglob('*') if p.is_file()},'design':'3x3 capacity/spread grid, 3 paired seeds; 12 verified existing + 15 new grid runs; 3 adaptive runs to iteration 500','convergence_screen':'absolute difference of mean executed score in iterations 451-500 vs 401-450 <=0.05 utils; descriptive screening, not equilibrium proof; also report full score trajectory and checkpoint travel measures','assignment':'Same deterministic person-order midpoint quantiles as original; no randomized assignment sensitivity; mean scheduled departure 06:00; observed departures rounded by simulator','source_project':str(source)}
 (ROOT/'provenance.json').write_text(json.dumps(manifest,indent=2))
 return matrix
def run(r,source,java):
 key=f"{r['scenario']}_s{r['seed']}";status=ROOT/'runs'/f'{key}.status.json';d=(ROOT/r['config']).parent
 hashes={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/r['config'],d/'network.xml',d/'plans.xml',d/'facilities.xml']};jar=source/'runtime/matsim-12.0.jar'
 if status.exists():
  old=json.loads(status.read_text());assert old['exit_code']==0 and old['input_sha256']==hashes and old['jar_sha256']==sha(jar);assert (ROOT/'runs'/key/'output_events.xml.gz').exists();return old
 assert not (ROOT/'runs'/key).exists(),f'Refusing overwrite: {key}'
 cmd=[java,'-Xmx2g','-Djava.awt.headless=true','-cp',str(jar),'org.matsim.run.Controler',r['config']];start=time.time();print('START',key,flush=True)
 with (ROOT/'runs'/f'{key}.console.log').open('w') as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 record={**r,'exit_code':p.returncode,'seconds':round(time.time()-start,2),'input_sha256':hashes,'jar_sha256':sha(jar),'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd}
 status.write_text(json.dumps(record,indent=2));print('END',key,p.returncode,record['seconds'],flush=True);assert p.returncode==0,key
 return record
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,type=Path);ap.add_argument('--workers',type=int,default=3);ap.add_argument('--java',default=shutil.which('java'));a=ap.parse_args();source=a.source.resolve()
 matrix=build(source)
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  futures=[pool.submit(run,r,source,a.java) for r in matrix if r['origin']=='new']
  for f in concurrent.futures.as_completed(futures):f.result()
 print('ALL 18 NEW RUNS COMPLETE',flush=True)
