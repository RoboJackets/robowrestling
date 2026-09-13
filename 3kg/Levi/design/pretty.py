from pathlib import Path
from kicad_sexpr import *
for p in Path('.').glob('*.kicad_sch'):
 s=p.read_text(encoding='utf8');a=parse(s);print(p,a[0],len(a),len(children(a,'symbol')))
 # pretty-format to support parser diagnostics
 def pretty(a,depth=0):
  if not isinstance(a,list):return dump(a)
  if not any(isinstance(b,list) for b in a):return dump(a)
  return '('+' '.join(dump(b) for b in a if not isinstance(b,list))+''.join('\n'+'\t'*(depth+1)+pretty(b,depth+1) for b in a if isinstance(b,list))+'\n'+'\t'*depth+')'
 p.write_text(pretty(a),encoding='utf8')
