from pathlib import Path
import argparse,json,xml.etree.ElementTree as E
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,type=Path);a=ap.parse_args();S=a.source
m=json.loads((R/'experiment_matrix.json').read_text());assert len(m)==30 and sum(r['origin']=='new' for r in m)==18
base_net={l.get('id'):dict(l.attrib) for l in E.parse(S/'scenarios/baseline/network.xml').findall('./links/link')}
base_people=E.parse(S/'scenarios/baseline/plans.xml').getroot()
for r in m:
 if r['origin']!='new':continue
 d=R/'scenarios'/r['scenario'];ref='adaptive' if r['kind']=='convergence' else 'baseline'
 c=E.parse(R/r['config']).getroot();bc=E.parse(S/f'scenarios/{ref}/config_s{r["seed"]}.xml').getroot()
 for tree in [c,bc]:
  tree.find('./module[@name="controler"]/param[@name="outputDirectory"]').set('value','normalized')
  tree.find('./module[@name="controler"]/param[@name="lastIteration"]').set('value','normalized')
 assert E.tostring(c)==E.tostring(bc),r
 assert (d/'facilities.xml').read_bytes()==(S/f'scenarios/{ref}/facilities.xml').read_bytes()
 net={l.get('id'):dict(l.attrib) for l in E.parse(d/'network.xml').findall('./links/link')}
 for k,v in net.items():
  expected=dict(base_net[k]);factor=r.get('capacity_factor',1.)
  if 11<=int(k)<=19:expected['capacity']=str(int(1000*factor))
  assert v==expected,(r,k)
 p=E.parse(d/'plans.xml').getroot();bp=E.parse(S/f'scenarios/{ref}/plans.xml').getroot()
 if r['kind']=='grid' and r['spread_minutes']:
  for i,person in enumerate(p.findall('person')):
   sec=float(person.find('.//act').get('end_time'));w=r['spread_minutes'];assert abs(sec-(21600-w*30+(i+.5)*w*60/2000))<1e-8
   person.find('.//act').set('end_time',bp.findall('person')[i].find('.//act').get('end_time'))
 assert E.tostring(p)==E.tostring(bp),r
print('PASS: 18 new configs; only designated capacity, departure-window, output-path and horizon changes. Same 2000 people, facilities, scoring and paired seeds.')
