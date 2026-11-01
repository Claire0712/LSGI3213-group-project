"""Explicit OOXML defaults for portable chart rendering (no data changes)."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,sys
p=Path(sys.argv[1]);ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for k,v in ns.items():E.register_namespace(k,v)
c='{'+ns['c']+'}'
with zipfile.ZipFile(p) as z:parts={n:z.read(n) for n in z.namelist()}
for n,b in list(parts.items()):
    if '/charts/chart' not in n or not n.endswith('.xml'):continue
    r=E.fromstring(b)
    for sc in r.findall('.//c:scatterChart',ns):
        for ser in sc.findall('c:ser',ns):
            for s in ser.findall('c:smooth',ns):ser.remove(s)
            E.SubElement(ser,c+'smooth',val='0')
    for a in r.findall('.//c:valAx',ns)+r.findall('.//c:catAx',ns):
        title=a.find('c:title',ns)
        if title is not None and not ''.join(title.itertext()).strip():a.remove(title)
        for tag in ['crosses','crossesAt']:
            for e in a.findall('c:'+tag,ns):a.remove(e)
        cross=a.find('c:crossAx',ns);idx=list(a).index(cross)+1 if cross is not None else len(a)
        a.insert(idx,E.Element(c+'crosses',val='min'))
    parts[n]=E.tostring(r,encoding='utf-8',xml_declaration=True)
tmp=p.with_suffix('.normalized.pptx')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in parts.items():z.writestr(n,b)
tmp.replace(p)
