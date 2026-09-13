from pathlib import Path
import re,json,copy

def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',s); stack=[]; root=None
 for t in ts:
  if t=='(':
   a=[]
   if stack: stack[-1].append(a)
   stack.append(a)
  elif t==')':root=stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root

def children(a,k):return [b for b in a if isinstance(b,list) and b and b[0]==k]
def child(a,k,default=None):return next(iter(children(a,k)),default)
def lib(name):
 cat,n=name.split(':'); root=parse(Path('E:/KiCad/share/kicad/symbols',cat+'.kicad_sym').read_text(encoding='utf-8'))
 allsy={s[1]:s for s in children(root,'symbol')}
 def resolve(n):
  s=copy.deepcopy(allsy[n]); ex=child(s,'extends')
  if ex:
   p=resolve(ex[1]); props={x[1] for x in children(s,'property')}
   for x in p[2:]:
    if x[0]=='property' and x[1] in props:continue
    if x[0]=='symbol':x[1]=x[1].replace(p[1]+'_',n+'_',1)
    s.append(x)
   s.remove(ex)
  return s
 return resolve(n)

def pins(s,u=1):
 out=[]
 for sub in children(s,'symbol'):
  unit=int(sub[1].split('_')[-2])
  if unit not in (0,u):continue
  for p in children(sub,'pin'):out.append((child(p,'number')[1],child(p,'name')[1],child(p,'at')[1:],p[1]))
 return out
if __name__=='__main__':
 for n in ['RF_Module:ESP32-S3-WROOM-1','Comparator:LM339','Regulator_Switching:TSR2-2433','74xGxx:74LVC2G08','Transistor_BJT:MMBT3904','Device:R','Switch:SW_SPDT','Connector_Generic:Conn_01x04']:
  try:
   s=lib(n);print(n,pins(s));print([(p[1],p[2]) for p in children(s,'property')][:4])
  except Exception as e:print(n,e)

class Q(str):pass

def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',s); stack=[];root=None
 for t in ts:
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif t==')':root=stack.pop()
  else:stack[-1].append(Q(json.loads(t)) if t.startswith('"') else t)
 return root

def dump(a):
 if isinstance(a,list):return '('+' '.join(dump(x) for x in a)+')'
 if isinstance(a,Q):return json.dumps(str(a),ensure_ascii=False)
 return str(a)
