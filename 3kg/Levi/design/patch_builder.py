from pathlib import Path
p=Path('design/build_schematic.py');s=p.read_text()
s=s.replace('{0 if left else 180}', '{180 if left else 0}').replace('("left" if left else "right")','("right" if left else "left")')
# Properties need orientation matching the symbol for horizontal rendered text.
s=s.replace('(at {f(xx)} {f(yy)} 0) {eff(1 if k=="Value" else 1.1', '(at {f(xx)} {f(yy)} {self.rot%180}) {eff(1 if k=="Value" else 1.1')
s=s.replace("('Reference',self.ref,tx,ty,False)","('Reference',self.ref,tx,ty,self.ref.startswith('#'))")
# Move the receiver output label beyond its feedback loop (no text over wire).
s=s.replace("u.net(minus,'SENSE_REF');u.net(op,out)","u.net(minus,'SENSE_REF');u.used.add(op);outend=(x+106.68,u.pt(op)[1]);page.wire(u.pt(op),outend);page.label(out,outend);EXPECTED.append((u.ref,op,out))")
# Keep Banner right hand circuits away from page border
s=s.replace('124.46+j*170.18','114.3+j*165.1')
# Standard power symbols in place of repeated boxed power labels
s=s.replace("def label(self,n,p,left=False):\n  self.count+=1", "def label(self,n,p,left=False):\n  if n in ('GND','+3V3','+5V'):\n   part=self.part('power:'+n,p[0],p[1],ref=newref('#PWR'),fp='',on=False);part.used.add('1');return\n  self.count+=1")
s=s.replace("if self.name.startswith('Comparator:'):tx,ty=self.x,self.y-7.5", "if self.name.startswith('Comparator:'):tx,ty=self.x,self.y-7.5\n  if self.name.startswith('power:'):tx,ty=self.x,self.y+(3 if self.name=='power:GND' else -6)")
p.write_text(s)
