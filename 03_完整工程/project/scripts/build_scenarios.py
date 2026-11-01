"""Build reproducible, independent MATSim 12.0 equil interventions."""
from pathlib import Path
import xml.etree.ElementTree as E
import gzip, json, copy
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'

def write(root,path,kind):
    E.indent(root)
    path.write_bytes(b'<?xml version="1.0" encoding="utf-8"?>\n'+f'<!DOCTYPE {kind} SYSTEM "http://www.matsim.org/files/dtd/{kind}_v{2 if kind=="config" else 4 if kind=="plans" else 1}.dtd">\n'.encode()+E.tostring(root))
def param(root,module,name,value):
    m=root.find(f'./module[@name="{module}"]')
    if m is None:m=E.SubElement(root,'module',name=module)
    p=m.find(f'./param[@name="{name}"]')
    if p is None:p=E.SubElement(m,'param',name=name)
    p.set('value',str(value))

def build():
    runs=[]
    for name in ['original100','baseline','capacity','stagger','combined','adaptive']:
        d=ROOT/'scenarios'/name;d.mkdir(parents=True,exist_ok=True)
        net=E.parse(RAW/'network.xml').getroot()
        if name in ['capacity','combined']:
            for l in net.findall('./links/link'):
                if 11<=int(l.get('id'))<=19:l.set('capacity','2000')
        write(net,d/'network.xml','network')
        (d/'facilities.xml').write_bytes((RAW/'facilities.xml').read_bytes())
        if name=='original100':
            (d/'plans.xml').write_bytes((RAW/'plans100.xml').read_bytes())
        else:
            pop=E.fromstring(gzip.open(RAW/'plans2000.xml.gz').read())
            for i,p in enumerate(pop.findall('person')):
                # Legacy v4 routes refer to an old link numbering; reroute on the current network.
                for leg in p.findall('.//leg'):
                    for route in leg.findall('route'):leg.remove(route)
                    for a in ['dep_time','trav_time','arr_time']:leg.attrib.pop(a,None)
                if name in ['stagger','combined']:
                    # Deterministic midpoint quantiles: mean exactly 06:00, range 05:30-06:30.
                    sec=19800+(i+.5)*3600/2000
                    p.find('.//act').set('end_time',str(sec))
            write(pop,d/'plans.xml','plans')
        for seed in ([4711] if name=='original100' else [4711,42,2025]):
            c=E.parse(RAW/'config.xml').getroot()
            for mod,key,val in [('global','randomSeed',seed),('global','numberOfThreads',1),('plans','inputPlansFile','plans.xml'),('controler','lastIteration',10 if name=='original100' else 100),('controler','outputDirectory',f'./runs/{name}_s{seed}'),('controler','writeEventsInterval',100),('controler','writePlansInterval',100),('controler','createGraphs','false'),('qsim','numberOfThreads',1),('parallelEventHandling','numberOfThreads',1)]:param(c,mod,key,val)
            if name=='adaptive':
                strat=c.find('./module[@name="strategy"]')
                strat.find('./parameterset/param[@name="weight"]').set('value','0.8')
                ss=E.SubElement(strat,'parameterset',type='strategysettings')
                E.SubElement(ss,'param',name='strategyName',value='TimeAllocationMutator')
                E.SubElement(ss,'param',name='weight',value='0.1')
                param(c,'TimeAllocationMutator','mutationRange',1800)
                param(c,'TimeAllocationMutator','mutationAffectsDuration','false')
            write(c,d/f'config_s{seed}.xml','config')
            runs.append(dict(scenario=name,seed=seed,iterations=10 if name=='original100' else 100,config=str((d/f'config_s{seed}.xml').relative_to(ROOT))))
    (ROOT/'scenarios/run_matrix.json').write_text(json.dumps(runs,indent=2))
    print(f'Built {len(runs)} runs')
if __name__=='__main__':build()
