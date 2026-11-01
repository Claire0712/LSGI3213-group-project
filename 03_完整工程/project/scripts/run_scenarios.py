"""Run MATSim sequentially; skip only previously verified successful completions."""
from pathlib import Path
import subprocess,json,time,sys,hashlib,datetime,os,shutil
ROOT=Path(__file__).resolve().parents[1]
JAR=ROOT/'runtime/matsim-12.0.jar'
JAVA=os.environ.get('MATSIM_JAVA') or shutil.which('java')
if not JAVA:raise RuntimeError('Java 11 is required; set MATSIM_JAVA to the Java executable.')
def input_hashes(r):
    config=ROOT/r['config'];directory=config.parent
    paths=[config,directory/'network.xml',directory/'plans.xml',directory/'facilities.xml']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def run(r):
    (ROOT/'runs').mkdir(exist_ok=True)
    key=f"{r['scenario']}_s{r['seed']}";out=ROOT/'runs'/key;status=ROOT/'runs'/f'{key}.status.json'
    if status.exists() and json.loads(status.read_text()).get('exit_code')==0 and (out/'output_events.xml.gz').exists():
        old=json.loads(status.read_text())
        if old.get('input_sha256')!=input_hashes(r) or old.get('jar_sha256')!=hashlib.sha256(JAR.read_bytes()).hexdigest():raise RuntimeError(f'{key}: input/runtime changed; archive runs before rerunning')
        print('Verified cached completion',key,flush=True);return
    if out.exists():raise RuntimeError(f'Refusing to overwrite unverified output {out}')
    command=[JAVA,'-Xmx2g','-Djava.awt.headless=true','-cp',str(JAR),'org.matsim.run.Controler',r['config']]
    t=time.time();print('START',key,flush=True)
    with (ROOT/'runs'/f'{key}.console.log').open('w') as log:
        p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    record={**r,'input_sha256':input_hashes(r),'command':command,'exit_code':p.returncode,'seconds':round(time.time()-t,2),'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'jar_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest()}
    status.write_text(json.dumps(record,indent=2));print('END',key,p.returncode,record['seconds'],flush=True)
    if p.returncode:raise RuntimeError(f'{key}: inspect console log')
if __name__=='__main__':
    matrix=json.loads((ROOT/'scenarios/run_matrix.json').read_text())
    for r in matrix:
        if len(sys.argv)==1 or r['scenario'] in sys.argv[1:]:run(r)
