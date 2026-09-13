from pathlib import Path
from collections import defaultdict
import json,uuid,math,csv,copy
from kicad_sexpr import *
BASE=Path(__file__).resolve().parent.parent
LIBROOT=Path('E:/KiCad/share/kicad')
NS=uuid.UUID('2c0974a8-9270-4e50-af57-63e9e38bb2d2')
def uid(s):return str(uuid.uuid5(NS,s))
def q(s):return json.dumps(str(s),ensure_ascii=False)
def f(n):return f'{float(n):.4f}'.rstrip('0').rstrip('.') or '0'
def eff(size=1.1,extra=''):return f'(effects (font (size {size} {size})) {extra})'
CUSTOM={}
def custom(name,units,fp='',desc='',datasheet=''):
 s=f'(symbol {q(name)} (pin_names (offset 0.8)) (in_bom yes) (on_board yes)'
 for key,val in [('Reference','U'),('Value',name),('Footprint',fp),('Datasheet',datasheet),('Description',desc)]:s+=f'(property {q(key)} {q(val)} (at 0 0 0) {eff()})'
 for u,(left,right) in enumerate(units,1):
  n=max(len(left),len(right));h=(n+1)*2.54/2
  s+=f'(symbol {q(name+"_"+str(u)+"_1")} (rectangle (start -12.7 {f(h)}) (end 12.7 {f(-h)}) (stroke (width 0.254) (type default)) (fill (type background)))'
  pp=''
  for side,items in [('L',left),('R',right)]:
   for i,(num,nm,typ) in enumerate(items):
    x=-17.78 if side=='L' else 17.78;y=h-2.54-i*2.54;ang=0 if side=='L' else 180
    pp+=f'(pin {typ} line (at {f(x)} {f(y)} {ang}) (length 5.08) (name {q(nm)} {eff(1)}) (number {q(num)} {eff(1)}))'
  s=s+pp+')'
 s+=')';CUSTOM['Levi:'+name]=parse(s);return 'Levi:'+name
MAXFP='Levi:MAX14819_T4877_4C_EP5.5'
maxsym=custom('MAX14819AATM',[
 ([('48','~{CS}','input'),('47','SCLK','input'),('45','SDI','input'),('38','A0','input'),('39','A1','input'),('43','CLKI','input'),('41','XI','input')],[('46','SDO','tri_state'),('1','~{IRQ}','open_collector'),('44','CLKO','output'),('42','XO','output')]),
 ([('34','TXA','input'),('35','TXENA','input'),('14','DIA','input'),('13','L+A','input'),('10','SN1A','passive'),('11','SN2A','passive')],[('17','CQA','bidirectional'),('36','RXA','output'),('37','LIA','output'),('2','RXRDYA/LD1A','open_collector'),('3','RXERRA/LD2A','open_collector'),('9','G1A','output'),('12','G2A','output')]),
 ([('33','TXB','input'),('32','TXENB','input'),('23','DIB','input'),('24','L+B','input'),('27','SN1B','passive'),('26','SN2B','passive')],[('20','CQB','bidirectional'),('31','RXB','output'),('30','LIB','output'),('4','RXRDYB/LD1B','open_collector'),('5','RXERRB/LD2B','open_collector'),('28','G1B','output'),('25','G2B','output')]),
 ([('8','VCC','power_in'),('29','VCC','power_in'),('40','VL','power_in'),('6','V5','power_in'),('7','REGEN','input'),('49','EP/GND','power_in')],[('15','NC','no_connect'),('16','NC','no_connect'),('18','NC','no_connect'),('19','NC','no_connect'),('21','NC','no_connect'),('22','NC','no_connect')])],MAXFP,'Dual IO-Link master, complete 48 pins + exposed pad. ADI Rev 3 pp18-21.','https://www.analog.com/media/en/technical-documentation/data-sheets/max14819.pdf')
polos=[]
for name in ['U3V50F24','S13V30F5']:
 polos.append(custom(name,[([('1','EN','input'),('2','VIN','power_in'),('3','GND','power_in'),('4','GND','passive')],[('5','VOUT','power_out')])],('Levi:Pololu_U3V50' if name=='U3V50F24' else 'Levi:Pololu_S13V_5pin'),'Pololu module: EN VIN GND GND VOUT; duplicate same-net header pads.','https://www.pololu.com/product/'+('2569' if name=='U3V50F24' else '4082')))
mdd=custom('Cytron_MDD20A',[([('VB+','VB+','passive'),('VB-','VB-','passive'),('PWM1','PWM1','input'),('DIR1','DIR1','input'),('PWM2','PWM2','input'),('DIR2','DIR2','input'),('GND','GND','passive')],[('M1A','M1A','passive'),('M1B','M1B','passive'),('M2A','M2A','passive'),('M2B','M2B','passive')])],'','External complete driver; actual named terminals.','https://docs.google.com/document/d/1YHKcs8N0UBrRI4r2OaIqHs6m_B_NaVBF7EB5C3fPTG4/edit')
sw=lib('Switch:SW_SPDT');sw[1]=Q('50209LX_Harness');ss=[]
for u in range(1,4):
 for sub in children(sw,'symbol'):
  sub=copy.deepcopy(sub);sub[1]=Q('50209LX_Harness_'+str(u)+'_'+str(sub[1]).split('_')[-2])
  for p in children(sub,'pin'):child(p,'number')[1]=Q(str((u-1)*3+int(child(p,'number')[1])))
  ss.append(sub)
sw=[x for x in sw if not(isinstance(x,list) and x[0]=='symbol')]+ss;CUSTOM['Levi:50209LX_Harness']=sw
RFP='Resistor_SMD:R_0805_2012Metric';CFP='Capacitor_SMD:C_0805_2012Metric'
JFP=lambda n:f'Connector_JST:JST_XH_B{n}B-XH-A_1x{n:02}_P2.50mm_Vertical'
BOM=[];EXPECTED=[];SYMCACHE={};COUNTS=defaultdict(int);PAGES=[]
def getsym(name):
 if name not in SYMCACHE:
  s=copy.deepcopy(CUSTOM[name]) if name in CUSTOM else lib(name)
  for sub in children(s,'symbol'):sub[1]=Q(sub[1])
  s[1]=Q(name);SYMCACHE[name]=s
 return SYMCACHE[name]
def newref(prefix):COUNTS[prefix]+=1;return prefix+str(COUNTS[prefix])
class Part:
 def __init__(self,page,libid,x,y,ref=None,val=None,fp=None,unit=1,rot=0,on=True,ds=None):
  self.page=page;self.name=libid;self.x=x;self.y=y;self.u=unit;self.rot=rot
  
  if ref:
   match=re.fullmatch(r'([A-Za-z#]+)([0-9]+)',ref)
   if match:COUNTS[match[1]]=max(COUNTS[match[1]],int(match[2]))
  s=getsym(libid);props={p[1]:p[2] for p in children(s,'property')};self.ref=ref or newref(props['Reference']);self.id=uid(page.name+self.ref+str(unit));self.value=val or props['Value'];self.fp=props.get('Footprint','') if fp is None else fp
  self.on=on;self.ds=ds or props.get('Datasheet','');self.pins={}
  for num,nm,at,typ in pins(s,unit):
   px,py,pa=map(float,at);a=math.radians(rot);xx=x+px*math.cos(a)-py*math.sin(a);yy=y-(px*math.sin(a)+py*math.cos(a));self.pins[num]=(round(xx,4),round(yy,4),(pa+rot)%360,nm,typ)
  self.used=set();page.parts.append(self);BOM.append(self)
 def pt(self,p):return self.pins[str(p)][:2]
 def net(self,p,net,length=7.62):
  p=str(p);self.used.add(p);x,y,a,_,_=self.pins[p];a=math.radians(a);end=(round(x-length*math.cos(a),4),round(y+length*math.sin(a),4));self.page.wire((x,y),end);self.page.label(net,end,left=(abs(math.cos(a)-1)<.1),power_symbol=abs(math.cos(a))<.1);EXPECTED.append((self.ref,p,net));return end
 def nc(self,p):
  p=str(p);self.used.add(p);self.page.add(f'(no_connect (at {f(self.pt(p)[0])} {f(self.pt(p)[1])}) (uuid {q(uid(self.id+"nc"+p))}))')
 def allnets(self,m):
  seen={}
  for p,(x,y,a,nm,t) in self.pins.items():
   net=m.get(p,m.get(nm))
   if (x,y) in seen:
    self.used.add(p)
    if net:EXPECTED.append((self.ref,p,net))
    continue
   seen[x,y]=net
   if net:self.net(p,net)
   else:self.nc(p)
  return self
 def output(self):
  ys=[p[1] for p in self.pins.values()]
  small=self.name.startswith(('Device:','Transistor_BJT:','Switch:','power:'))
  tx,ty=(self.x+4,self.y-1.8) if small and self.rot==0 else (self.x,min(ys)-7.5)
  if self.name.startswith('Comparator:'):tx,ty=self.x,self.y-7.5
  if self.name=='Device:Crystal':tx,ty=self.x,self.y-7.5
  if self.name.startswith('RF_Module:') or (self.ref=='U40' and self.u==3):tx-=22
  if self.name=='Device:LED':tx,ty=self.x+8,self.y-1.8
  if self.name.startswith('power:'):tx,ty=self.x,self.y+(3 if self.name=='power:GND' else -6)
  if self.name.startswith('Connector'):tx,ty=self.x+2,min(ys)-6
  body=f'(symbol (lib_id {q(self.name)}) (at {f(self.x)} {f(self.y)} {self.rot}) (unit {self.u}) (exclude_from_sim no) (in_bom {"no" if self.ref.startswith("#") else "yes"}) (on_board {"yes" if self.on else "no"}) (dnp no) (uuid {q(self.id)})'
  for k,v,xx,yy,hide in [('Reference',self.ref,tx,ty,self.ref.startswith('#')),('Value',self.value,tx,ty+2.2,False),('Footprint',self.fp,self.x,self.y,True),('Datasheet',self.ds,self.x,self.y,True)]:body+=f'(property {q(k)} {q(v)} (at {f(xx)} {f(yy)} {self.rot%180}) {eff(1 if k=="Value" else 1.1,("(hide yes)" if hide else "")+(" (justify left)" if small and self.rot==0 and not self.name.startswith("power:") else ""))})'
  for p in self.pins:body+=f'(pin {q(p)} (uuid {q(uid(self.id+"pin"+p))}))'
  body+=f'(instances (project "Levi" (path {q(self.page.path)} (reference {q(self.ref)}) (unit {self.u}))))';return body+')'
class Page:
 def __init__(self,name,title,num):
  self.name=name;self.title=title;self.num=num;self.id=uid('page:'+name);self.parts=[];self.items=[];self.count=0
  self.path='/'+uid('page:Levi')+('' if name=='Levi' else '/'+uid('sheet:'+name));PAGES.append(self)
 def add(self,s):self.items.append(s)
 def wire(self,a,b):
  if a==b:return
  self.count+=1;self.add(f'(wire (pts (xy {f(a[0])} {f(a[1])}) (xy {f(b[0])} {f(b[1])})) (stroke (width 0) (type default)) (uuid {q(uid(self.name+"w"+str(self.count)))}))')
 def dot(self,p):self.add(f'(junction (at {f(p[0])} {f(p[1])}) (diameter 0) (color 0 0 0 0) (uuid {q(uid(self.name+"j"+str(p)))}))')
 def label(self,n,p,left=False,power_symbol=True):
  if power_symbol and n in ('GND','+3V3','+5V'):
   part=self.part('power:'+n,p[0],p[1],ref=newref('#PWR'),fp='',on=False);part.used.add('1');return
  self.count+=1
  self.add(f'(global_label {q(n)} (shape bidirectional) (at {f(p[0])} {f(p[1])} {180 if left else 0}) {eff(1,"(justify "+("right" if left else "left")+")")} (uuid {q(uid(self.name+"l"+str(self.count)))}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {f(p[0])} {f(p[1])} 0) {eff(1,"(hide yes)")}))')
 def text(self,t,x,y,size=1.3):
  self.count+=1;self.add(f'(text {q(t)} (at {f(x)} {f(y)} 0) {eff(size,"(justify left top)")} (uuid {q(uid(self.name+"t"+str(self.count)))}))')
 def part(self,*args,**kw):return Part(self,*args,**kw)
 def conn(self,n,x,y,val,nets,ref=None):return self.part(f'Connector_Generic:Conn_01x{n:02}',x,y,ref=ref,val=val,fp=JFP(n)).allnets({str(i+1):v for i,v in enumerate(nets) if v})
 def r(self,x,y,val,a,b,rot=0):return self.part('Device:R',x,y,val=val,fp=RFP,rot=rot).allnets({'1':a,'2':b})
 def cap(self,x,y,val,a,b='GND',fp=CFP):return self.part('Device:C_Polarized' if 'CP_Radial' in fp else 'Device:C',x,y,val=val,fp=fp).allnets({'1':a,'2':b})
 def write(self):
  split_wires(self)
  names=sorted({p.name for p in self.parts});txt=f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid {q(self.id)}) (paper "A3") (title_block (title {q(self.title)}) (date "2026-09-10") (rev "1.0") (company "RoboJackets | Levi | 3 kg") (comment 1 "Schematic revision - PCB layout and bench validation required")) (lib_symbols '+''.join(dump(getsym(n)) for n in names)+')'+''.join(self.items)+''.join(p.output() for p in self.parts)
  if self.name=='Levi':txt+='(sheet_instances (path "/" (page "1")))'
  txt+='(embedded_fonts no))';(BASE/(self.name+'.kicad_sch')).write_text(txt,encoding='utf8')
def wirepins(page,a,pa,b,pb):
 a.used.add(str(pa));b.used.add(str(pb));page.wire(a.pt(pa),b.pt(pb))

def comparator(page,x,y,raw,out,ref,unit,pull=False):
 rt=page.part('Device:R',x,y,val='30k 1%',fp=RFP,rot=270);rt.net(2,raw)
 lo=page.part('Device:R',x+15.24,y+12.7,val='10k 1%',fp=RFP)
 c=page.part('Device:C',x+27.94,y+12.7,val='1n 50V C0G',fp=CFP)
 u=page.part('Comparator:LM339',x+53.34,y+2.54,ref=ref,val='LM339BIDR',fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',unit=unit,ds='https://www.ti.com/lit/ds/symlink/lm339.pdf')
 pp=pins(getsym('Comparator:LM339'),unit);plus=next(p[0] for p in pp if p[1]=='+');minus=next(p[0] for p in pp if p[1]=='-');op=next(p[0] for p in pp if p[3]=='open_collector')
 node=(x+15.24,y);page.wire(rt.pt(1),node);rt.used.add('1');page.wire(node,(x+27.94,y));page.wire((x+27.94,y),u.pt(plus));u.used.add(plus)
 for v in [lo,c]:page.wire((v.x,y),v.pt(1));v.used.add('1');v.net(2,'GND');page.dot((v.x,y))
 u.net(minus,'SENSE_REF');u.used.add(op);outend=(x+106.68,u.pt(op)[1]);page.wire(u.pt(op),outend);page.label(out,outend);EXPECTED.append((u.ref,op,out))
 pu=page.part('Device:R',x+78.74,y-10.16,val='4.7k',fp=RFP);pu.net(1,'+3V3');pu.used.add('2');page.wire(pu.pt(2),(pu.x,u.pt(op)[1]));page.wire((pu.x,u.pt(op)[1]),u.pt(op));page.dot(u.pt(op))
 fb=page.part('Device:R',x+40.64,y-17.78,val='1M 1%',fp=RFP,rot=270)
 fb.used.update(['1','2']);page.wire(fb.pt(1),(pu.x+12.7,fb.y));page.wire((pu.x+12.7,fb.y),(pu.x+12.7,u.pt(op)[1]));page.wire((pu.x+12.7,u.pt(op)[1]),(pu.x,u.pt(op)[1]));page.dot((pu.x,u.pt(op)[1]))
 page.wire(fb.pt(2),(node[0],fb.y));page.wire((node[0],fb.y),node);page.dot(node)
 if pull:
  rp=page.part('Device:R',x-20.32,y-12.7,val='10k',fp=RFP);rp.net(1,'+24V_SENS');rp.used.add('2');page.wire(rp.pt(2),(rp.x,y));page.wire((rp.x,y),rt.pt(2));page.dot(rt.pt(2))
 return u

power=Page('Levi','Power and sheet index',1)
control=Page('01_Control','ESP32-S3 control and programming',2)
tele=Page('02_Telemetry','ESP32-C6 telemetry and programming',3)
baum=Page('03_Baumer','Baumer O300 inputs and mode selector',4)
banner=Page('04_Banner','Banner Q20NDXL complementary inputs',5)
iola=Page('05_IOLink_A','MAX14819A: left and center IO-Link',6)
iolb=Page('06_IOLink_B','MAX14819A: right IO-Link',7)
line=Page('07_Line_Motor','ML1 edge sensing and motor gating',8)
harness=Page('08_Harness','External battery, disconnect and drivetrain',9)
support=Page('09_Enable_Debug','Enable interlock and sensor indicators',10)
power.text('POWER DISTRIBUTION',15,12,2)
# Direct wired input protection chain
j=power.part('Connector_Generic:Conn_01x02',43.18,43.18,ref='J1',val='B2B-XH-A | power',fp=JFP(2));j.net(2,'GND');j.net(1,'BAT_FUSED')
fu=power.part('Device:Fuse',83.82,43.18,val='0451002.MRL / 2A',fp='Fuse:Fuse_Littelfuse-NANO2-451_453',rot=270)
d=power.part('Device:D_Schottky',124.46,43.18,val='SS34',fp='Diode_SMD:D_SMA',rot=180)
# J connector faces left: wire from left through an upper dogleg to fuse input
j.used.add('1');fu.used.update(['1','2']);d.used.add('2');a=j.pt(1);b=fu.pt(2);power.wire(a,(a[0]-5.08,a[1]));power.wire((a[0]-5.08,a[1]),(a[0]-5.08,30.48));power.wire((a[0]-5.08,30.48),(b[0],30.48));power.wire((b[0],30.48),b);power.dot(a);power.wire(fu.pt(1),d.pt(2));d.net(1,'LOGIC_IN')
tv=power.part('Device:D_Zener',165.1,53.34,val='SMBJ13A',fp='Diode_SMD:D_SMB',rot=270);tv.net(2,'GND');tv.used.add('1');power.wire(d.pt(1),(tv.x,d.y));power.wire((tv.x,d.y),tv.pt(1));power.dot(d.pt(1))
cc=power.part('Device:C_Polarized',205.74,53.34,val='47u 35V',fp='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm');cc.net(2,'GND');cc.used.add('1');power.wire((tv.x,d.y),(cc.x,d.y));power.wire((cc.x,d.y),cc.pt(1));power.dot((tv.x,d.y))
power.text('J1: external fused battery bus (sheet 9).\nMotor current bypasses control PCB.',15,68)
power.text('SS34 reverse-input isolation. SMBJ13A: 21.5 V rated clamp\nfor the Pololu modules with 22 V maximum input.',111,76)
for i,(name,rail) in enumerate(zip(polos,['+24V_RAW','+5V'])):
 x=63.5+i*119.38;y=116.84
 u=power.part(name,x,y,ref='U'+str(i+1)).allnets({'2':'LOGIC_IN','3':'GND','4':'GND','5':rail})
 oc=power.cap(x+45.72,y+5.08,'22u 50V' if i==0 else '22u 25V',rail,fp='Capacitor_THT:CP_Radial_D8.0mm_P3.50mm' if i==0 else CFP)
 power.wire(u.pt(5),(oc.x,u.pt(5)[1]));power.wire((oc.x,u.pt(5)[1]),oc.pt(1));power.dot(u.pt(5))
 power.text('EN open: internal pull-up.\nHeader-mounted regulator module.',x-30,y+32)
power.part('Regulator_Switching:TSR2-2433',317.5,116.84,ref='U3',ds='https://www.tracopower.com/sites/default/files/products/datasheets/tsr2_datasheet.pdf').allnets({'1':'LOGIC_IN','2':'GND','3':'+3V3'})
power.cap(360.68,124.46,'22u 10V','+3V3');power.text('3.3 V / 2 A switching supply\nreplaces AP2112K.',280,148)
power.part('Device:Polyfuse',50.8,185.42,val='1812L050/30 / 0.5A',fp='Fuse:Fuse_1812_4532Metric',rot=270).allnets({'1':'+24V_RAW','2':'+24V_SENS'});power.cap(88.9,195.58,'22u 50V','+24V_SENS',fp='Capacitor_THT:CP_Radial_D8.0mm_P3.50mm')
power.text('0.5 A sensor branch.\nUse >=24 AWG sensor power wire.',15,216)
for i,net in enumerate(['GND','BAT_FUSED','LOGIC_IN','+24V_SENS']):power.part('power:PWR_FLAG',132.08+i*40.64,182.88,ref='#FLG'+str(i+1),fp='',on=False).allnets({'1':net})
power.text('SCHEMATIC SHEETS',135,204,1.7)
for i,p in enumerate(PAGES[1:]):
 if i==8:x=15;y=246;w=103
 else:col=i%4;row=i//4;x=137+col*64;y=214+row*22;w=58
 power.add(f'(sheet (at {f(x)} {f(y)}) (size {w} 13) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {q(uid("sheet:"+p.name))}) (property "Sheetname" {q(p.name)} (at {f(x)} {f(y-1)} 0) {eff(1,"(justify left bottom)")}) (property "Sheetfile" {q(p.name+".kicad_sch")} (at {f(x)} {f(y+14)} 0) {eff(.9,"(justify left top)")}) (instances (project "Levi" (path {q('/'+power.id)} (page {q(p.num)})))))')
mp={'EN':'CTRL_EN','IO0':'CTRL_BOOT','IO1':'LINE_FL_ADC','IO2':'LINE_FR_ADC','IO4':'LINE_RL_ADC','IO5':'LINE_RR_ADC','IO6':'BAT_ADC','IO7':'BAUM_L','IO8':'BAUM_C','IO9':'BAUM_R','IO10':'BAN_L_BK','IO11':'BAN_L_WH','IO12':'BAN_C_BK','IO13':'BAN_C_WH','IO14':'BAN_R_BK','IO15':'BAN_R_WH','IO16':'IOL_CS_A','IO17':'IOL_CS_B','IO18':'IOL_SCK','IO21':'IOL_MOSI','IO35':'IOL_MISO','IO36':'IOL_IRQ_A','IO37':'IOL_IRQ_B','IO38':'PWM_L_RAW','IO39':'DIR_L_RAW','IO40':'PWM_R_RAW','IO41':'DIR_R_RAW','IO42':'CTRL_TX','IO47':'CTRL_RX','IO48':'MOTOR_ARM','TXD0':'CTRL_PROG_TX','RXD0':'CTRL_PROG_RX','3V3':'+3V3','GND':'GND'}
control.text('CONTROL | ESP32-S3-WROOM-1-N8 (no PSRAM)',15,12,2)
control.part('RF_Module:ESP32-S3-WROOM-1',106.68,96.52,ref='U10',val='ESP32-S3-WROOM-1-N8').allnets(mp)
control.text('GPIO35-37: use N8 module WITHOUT octal PSRAM.\nGPIO3/45/46 unused; GPIO0 is BOOT only.\nADC1: GPIO1,2,4,5,6. Control radio stays off.\nSPI initial target: 1 MHz.',20,150)
# Wiring helper for real local supply rails and EN/BOOT networks

def bypass_bank(page,x,y,rail):
 cs=[page.part('Device:C',x+i*30.48,y,val=v,fp='Capacitor_SMD:C_1210_3225Metric' if v.startswith('47u') else CFP) for i,v in enumerate(['100n 10V','10u 10V','47u 10V'])]
 for c in cs:c.used.update(['1','2'])
 for pin in ['1','2']:
  for a,b in zip(cs,cs[1:]):page.wire(a.pt(pin),b.pt(pin));page.dot(b.pt(pin))
 cs[0].net(1,rail);cs[0].net(2,'GND');page.dot(cs[0].pt(1));page.dot(cs[0].pt(2))
def reset_circuit(page,x,y,en,boot):
 r=page.part('Device:R',x,y,val='10k',fp=RFP);r.net(1,'+3V3')
 c=page.part('Device:C',x+25.4,y+17.78,val='1u 10V',fp=CFP);c.net(2,'GND')
 sw=page.part('Switch:SW_Push',x+50.8,y+7.62,val='RESET',fp='Button_Switch_SMD:SW_SPST_TL3342');sw.net(2,'GND')
 node=(x,y+7.62);r.used.add('2');c.used.add('1');sw.used.add('1');page.wire(r.pt(2),node);page.wire(node,(c.x,node[1]));page.wire((c.x,node[1]),sw.pt(1));page.wire((c.x,node[1]),c.pt(1));page.dot((c.x,node[1]));page.label(en,node,True)
 rb=page.part('Device:R',x+93.98,y,val='10k',fp=RFP);rb.net(1,'+3V3');sb=page.part('Switch:SW_Push',x+124.46,y+7.62,val='BOOT',fp='Button_Switch_SMD:SW_SPST_TL3342');sb.net(2,'GND');rb.used.add('2');sb.used.add('1');nb=(rb.x,sb.y);page.wire(rb.pt(2),nb);page.wire(nb,sb.pt(1));page.label(boot,nb,True)

bypass_bank(control,187.96,63.5,'+3V3');reset_circuit(control,187.96,114.3,'CTRL_EN','CTRL_BOOT')
control.conn(6,350.52,66.04,'B6B-XH-A | program',['GND','+3V3','CTRL_PROG_TX','CTRL_PROG_RX','CTRL_EN','CTRL_BOOT'])
control.text('UART adapter: 3.3 V logic. Pin 2 is VREF only.\nMCU TX -> adapter RX; MCU RX <- adapter TX.\nHold BOOT, pulse RESET, release BOOT.\nUSB pins unused; program through UART0.',230,157)
control.r(190.5,213.36,'100R','CTRL_TX','TELEM_RX');control.r(259.08,213.36,'100R','TELEM_TX','CTRL_RX')
control.text('UART1: CRC-framed messages and timeout.\nControl remains independent of telemetry.\nClear MOTOR_ARM on boot, watchdog and sensor faults.',160,243)
control.text('PCB: local 3V3 bypassing and EN RC.\nAntenna keepout on every copper layer.',15,218)
tele.text('TELEMETRY | ESP32-C6-MINI-1-N4',15,12,2)
tele.part('RF_Module:ESP32-C6-MINI-1',106.68,96.52,ref='U11',val='ESP32-C6-MINI-1-N4').allnets({'EN':'TEL_EN','IO9':'TEL_BOOT','IO8':'TEL_STRAP8','IO18':'TELEM_RX','IO19':'TELEM_TX','TXD0':'TEL_PROG_TX','RXD0':'TEL_PROG_RX','3V3':'+3V3','GND':'GND'})
bypass_bank(tele,187.96,63.5,'+3V3');reset_circuit(tele,187.96,114.3,'TEL_EN','TEL_BOOT')
tele.r(190.5,185.42,'10k','+3V3','TEL_STRAP8')
tele.conn(6,350.52,66.04,'B6B-XH-A | program',['GND','+3V3','TEL_PROG_TX','TEL_PROG_RX','TEL_EN','TEL_BOOT'])
tele.text('UART1: GPIO18 RX <- S3 GPIO42; GPIO19 TX -> S3 GPIO47.\nGPIO8 pulled HIGH for download; GPIO9 is BOOT.\nIndependent UART0 service port, same pinout as control.\nBoth modules share 3.3 V and ground.',20,156)
tele.text('Logging/telemetry only; motor authority remains on S3.\nPacket loss must not delay edge sensing or control.\nKeep antenna beyond board edge and away from chassis metal.',20,211)
baum.text('BAUMER O300.DI-GM1J.72N | M8-4 harness',15,12,2)
baum.text('Board pins match M8: 1 brown +24 V, 2 white TEACH, 3 blue GND, 4 black C/Q.\nComparator HIGH = raw C/Q high. DIGITAL readings invalid in IO-Link mode. Change mode only while stopped.',15,22,1.15)
for i,side in enumerate(['L','C','R']):
 y=63.5+i*66.04
 baum.conn(4,48.26,y,'B4B-XH-A | '+side,['+24V_SENS','TEACH_'+side,'GND','CQ_'+side])
 baum.r(88.9,y+7.62,'10k','TEACH_'+side,'GND')
 comparator(baum,152.4,y,'BAUM_'+side+'_DIGRAW','BAUM_'+side,'U20',i+1)
 baum.text(side+' : DIGITAL input after selector',120,y+32,1.1)
 baum.part('Device:D_Zener',330.2,y+5.08,val='SMCJ48A',fp='Diode_SMD:D_SMC',rot=270).allnets({'1':'CQ_'+side,'2':'GND'})
 baum.part('Connector:TestPoint',109.22,y+12.7,val='TEACH '+side,fp='TestPoint:TestPoint_Pad_D2.0mm').allnets({'1':'TEACH_'+side})
baum.conn(9,388.62,109.22,'B9B-XH-A | selector',['BAUM_L_DIGRAW','CQ_L','IOL_CQ_L','BAUM_C_DIGRAW','CQ_C','IOL_CQ_C','BAUM_R_DIGRAW','CQ_R','IOL_CQ_R'])
baum.text('To 50209LX on sheet 9.\nGroups of 3:\ndigital / common / IO-Link.\nMatch actual switch lugs\nby continuity.',343,157,1.1)
baum.part('Comparator:LM339',48.26,254,ref='U20',val='LM339BIDR',fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',unit=4).allnets({'+':'GND','-':'SENSE_REF'})
baum.part('Comparator:LM339',96.52,254,ref='U20',val='LM339BIDR',fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',unit=5).allnets({'3':'+24V_SENS','12':'GND'})
baum.cap(132.08,254,'100n 50V','+24V_SENS')
# Actual wired reference divider
ra=baum.part('Device:R',180.34,241.3,val='16.5k 1%',fp=RFP);rb=baum.part('Device:R',180.34,259.08,val='10k 1%',fp=RFP);cr=baum.part('Device:C',228.6,259.08,val='100n 10V',fp=CFP)
ra.net(1,'+3V3');rb.net(2,'GND');cr.net(2,'GND');wirepins(baum,ra,2,rb,1);nd=(180.34,250.19);baum.wire(nd,(cr.x,nd[1]));baum.wire((cr.x,nd[1]),cr.pt(1));cr.used.add('1');baum.dot(nd);baum.label('SENSE_REF',nd,True)
baum.text('Vref = 1.245 V; raw threshold ~5 V.\n30k/10k + 1M feedback: ~0.1 V hysteresis.',275,241,1.1)
banner.text('BANNER Q20NDXL | 24 V NPN complementary outputs',15,12,2)
banner.text('Board pins: 1 brown +24 V, 2 white, 3 blue GND, 4 black.\n24 V pull-ups accommodate specified output leakage and saturation voltage. Comparator outputs: 3.3 V.',15,23,1.15)
for i,side in enumerate(['L','C','R']):
 y=66.04+i*66.04
 banner.conn(4,45.72,y,'B4B-XH-A | '+side,['+24V_SENS','BN_'+side+'_WH_RAW','GND','BN_'+side+'_BK_RAW'])
 for j,color in enumerate(['BK','WH']):
  idx=i*2+j;ref='U'+str(21+idx//4);unit=idx%4+1
  comparator(banner,114.3+j*165.1,y,'BN_'+side+'_'+color+'_RAW','BAN_'+side+'_'+color,ref,unit,True)
for ref,x in [('U21',48.26),('U22',124.46)]:
 banner.part('Comparator:LM339',x,254,ref=ref,val='LM339BIDR',fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',unit=5).allnets({'3':'+24V_SENS','12':'GND'});banner.cap(x+30.48,254,'100n 50V','+24V_SENS')
for unit,x in [(3,228.6),(4,307.34)]:banner.part('Comparator:LM339',x,241.3,ref='U22',val='LM339BIDR',fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',unit=unit).allnets({'+':'GND','-':'SENSE_REF'})

for idx,page in enumerate([iola,iolb]):
 ref='U'+str(30+idx);cs='IOL_CS_'+('A' if idx==0 else 'B');irq='IOL_IRQ_'+('A' if idx==0 else 'B');prefix='PHY'+str(idx)
 page.text('MAX14819AATM+ | '+('LEFT + CENTER' if idx==0 else 'RIGHT + UNUSED'),15,12,2)
 page.text('SPI framer. VCC = 24 V; VL = 3.3 V; external V5 = 5 V; REGEN = GND.\nL+ controllers omitted: sensors use fused 24 V directly. Disable L+ diagnostics in firmware.',15,23,1.15)
 page.part(maxsym,88.9,73.66,ref=ref,unit=1).allnets({'48':cs,'47':'IOL_SCK','45':'IOL_MOSI','46':'IOL_MISO','1':irq,'38':'GND','39':'GND','43':'GND','41':prefix+'_XI','42':prefix+'_XO'})
 page.r(157.48,60.96,'10k','+3V3',cs);page.r(198.12,60.96,'4.7k','+3V3',irq)
 # crystal with wired capacitors
 xt=page.part('Device:Crystal',170.18,116.84,val='14.7456MHz CL18pF',fp='Crystal:Crystal_SMD_HC49-SD',ds='https://www.digikey.com/en/products/detail/citizen-finedevice-co-ltd/HCM4914745600ABJT/284279')
 for pin,x,suffix in [('1',139.7,'XI'),('2',200.66,'XO')]:
  c=page.part('Device:C',x,139.7,val='22p C0G',fp=CFP);c.net(2,'GND');c.used.add('1');xt.used.add(pin);page.wire(xt.pt(pin),(x,xt.y));page.wire((x,xt.y),c.pt(1));page.label(prefix+'_'+suffix,(x,xt.y),pin=='1')
 page.text('HCM4914745600ABJT, CL18 pF.\n22 pF external/leg: initial tuning value,\n10 pF internal + estimated 4 pF stray/leg.\nVerify frequency and startup on PCB.',123,156,1.1)
 page.part(maxsym,299.72,73.66,ref=ref,unit=4).allnets({'8':'+24V_SENS','29':'+24V_SENS','40':'+3V3','6':'+5V','7':'GND','49':'GND'})
 for x,net,val in [(248.92,'+24V_SENS','1u 50V'),(292.1,'+24V_SENS','1u 50V'),(335.28,'+5V','1u 10V'),(378.46,'+3V3','100n 10V')]:page.cap(x,127,val,net)
 for ch,u,x,side in [('A',2,86.36,'L' if idx==0 else 'R'),('B',3,289.56,'C' if idx==0 else None)]:
  m={'TX'+ch:'GND','TXEN'+ch:'GND','DI'+ch:'GND','L+'+ch:'GND','SN1'+ch:prefix+'_SN_'+ch,'SN2'+ch:prefix+'_SN_'+ch}
  if side:m['CQ'+ch]='IOL_CQ_'+side
  page.part(maxsym,x,218.44,ref=ref,unit=u).allnets(m)
 page.text('TX/TXEN LOW: select internal framer in registers before use. A0/A1 LOW, independent CS.\nExposed pad to ground plane. Unused SN1/SN2 tied together, otherwise floating per ADI instructions.\nL+ diagnostics: L+ outputs unused; disable their fault reporting. Short robot harness.',15,256,1.1)

line.text('EDGE INPUTS + MOTOR HARDWARE ENABLE',15,12,2)
for i,side in enumerate(['FL','FR','RL','RR']):
 x=43.18+i*93.98
 line.conn(3,x,50.8,'B3B-XH-A | '+side,['+3V3','GND','LINE_'+side+'_RAW'])
 r=line.part('Device:R',x,86.36,val='10k 1%',fp=RFP,rot=270);r.net(2,'LINE_'+side+'_RAW')
 rl=line.part('Device:R',x+25.4,104.14,val='20k 1%',fp=RFP);c=line.part('Device:C',x+53.34,104.14,val='10n 10V',fp=CFP)
 nd=(rl.x,r.y);r.used.add('1');rl.used.add('1');c.used.add('1');line.wire(r.pt(1),nd);line.wire(nd,(c.x,r.y));line.wire(nd,rl.pt(1));line.wire((c.x,r.y),c.pt(1));line.dot(nd);line.label('LINE_'+side+'_ADC',(c.x,r.y));rl.net(2,'GND');c.net(2,'GND')
 line.cap(x+30.48,55.88,'100n 10V','+3V3')
line.text('ML1 harness: + -> 1, GND -> 2, OUT -> 3 (follow sensor silkscreen). Supply 3.3 V.\n10k/20k scales 0-3.3 V to 0-2.2 V on ADC1; 10 nF filters noise. Calibrate with sensors mounted.',15,130,1.15)
r1=line.part('Device:R',43.18,170.18,val='100k 1%',fp=RFP);r2=line.part('Device:R',43.18,200.66,val='22k 1%',fp=RFP);cap=line.part('Device:C',99.06,200.66,val='100n 10V',fp=CFP)
r1.net(1,'BAT_FUSED');r2.net(2,'GND');cap.net(2,'GND');wirepins(line,r1,2,r2,1);nd=(r1.x,185.42);line.wire(nd,(cap.x,nd[1]));line.wire((cap.x,nd[1]),cap.pt(1));cap.used.add('1');line.dot(nd);line.label('BAT_ADC',(cap.x,nd[1]))
line.text('Battery: 22/122; 12.6 V -> 2.27 V.\nStop before the pack is over-discharged.',15,226,1.1)
for i,side in enumerate(['L','R']):
 y=177.8+i*53.34
 gate=line.part('74xGxx:74LVC2G08',208.28,y,ref='U40',val='SN74LVC2G08DCUR',fp='Package_SO:VSSOP-8_2.3x2mm_P0.5mm',unit=i+1)
 gate.net(1 if i==0 else 5,'PWM_'+side+'_RAW');gate.net(2 if i==0 else 6,'MOTOR_ENABLE')
 op='7' if i==0 else '3';sr=line.part('Device:R',261.62,y,val='100R',fp=RFP,rot=270);wirepins(line,gate,op,sr,2);sr.net(1,'PWM_'+side)
 pd=line.part('Device:R',289.56,y+15.24,val='10k',fp=RFP);pd.net(2,'GND');pd.used.add('1');line.wire(sr.pt(1),(pd.x,y));line.wire((pd.x,y),pd.pt(1));line.dot(sr.pt(1))
 line.r(335.28,y+7.62,'100R','DIR_'+side+'_RAW','DIR_'+side)
line.conn(5,393.7,149.86,'MDD20A control',['GND','PWM_L','DIR_L','PWM_R','DIR_R'])
line.text('Map to named MDD20A terminals.\nPWM LOW = dynamic brake; <=20 kHz.',145,265,1.05)

support.text('MOTOR INTERLOCK + SENSOR LOGIC INDICATORS',15,12,2)
support.conn(2,50.8,45.72,'ARM removable link',['MOTOR_ARM','MOTOR_ENABLE'])
support.r(93.98,48.26,'10k','MOTOR_ARM','GND');support.r(137.16,48.26,'10k','MOTOR_ENABLE','GND')
support.part('74xGxx:74LVC2G08',195.58,48.26,ref='U40',val='SN74LVC2G08DCUR',fp='Package_SO:VSSOP-8_2.3x2mm_P0.5mm',unit=3).allnets({'8':'+3V3','4':'GND'});support.cap(233.68,48.26,'100n 10V','+3V3')
for i,n in enumerate(['PWM_L_RAW','PWM_R_RAW','DIR_L_RAW','DIR_R_RAW']):support.r(279.4+i*33.02,48.26,'10k',n,'GND')
support.text('Remove ARM link to force both PWM outputs LOW. Raise MOTOR_ARM only after startup checks.\nLogic inhibit only; battery disconnect is on sheet 9. No independent hardware watchdog is fitted.',15,75,1.15)
for i,net in enumerate(['BAUM_L','BAUM_C','BAUM_R','BAN_L_BK','BAN_L_WH','BAN_C_BK','BAN_C_WH','BAN_R_BK','BAN_R_WH']):
 col=i%3;row=i//3;x=35.56+col*129.54;y=119.38+row*53.34
 r=support.part('Device:R',x,y+10.16,val='47k',fp=RFP,rot=270);r.net(2,net)
 t=support.part('Transistor_BJT:MMBT3904',x+20.32,y+10.16,val='MMBT3904',fp='Package_TO_SOT_SMD:SOT-23');wirepins(support,r,1,t,1);t.net(2,'GND')
 led=support.part('Device:LED',x+22.86,y-5.08,val='GREEN',fp='LED_SMD:LED_0805_2012Metric',rot=90);wirepins(support,led,1,t,3)
 rr=support.part('Device:R',x+22.86,y-17.78,val='1k',fp=RFP);wirepins(support,rr,2,led,2);rr.used.add('1');end=(rr.x-10.16,rr.pt(1)[1]);support.wire(rr.pt(1),end);support.label('+3V3',end,left=True,power_symbol=False);EXPECTED.append((rr.ref,'1','+3V3'))
 support.text(net+'\nLit = GPIO HIGH',x+48.26,y+5.08,1.1)
harness.text('EXTERNAL HARNESS | MOTOR CURRENT BYPASSES CONTROL PCB',15,12,2)
harness.text('External parts intentionally have no PCB footprint; their board connectors are on sheets 1, 4 and 8.\nUse short motor loops and a separate signal ground to MDD20A. Terminals below are the actual driver markings.',15,24,1.15)
bat=harness.part('Device:Battery',38.1,76.2,ref='BT1',val='3S LiPo / XT60',fp='',on=False);bat.net(2,'GND')
hf=harness.part('Device:Fuse',88.9,63.5,ref='F100',val='ATC 20A inline',fp='',rot=270,on=False)
hs=harness.part('Switch:SW_SPST',154.94,63.5,ref='SW100',val='XT60 removable power link',fp='',on=False)
bat.used.add('1');hf.used.add('2');harness.wire(bat.pt(1),(bat.x,hf.y));harness.wire((bat.x,hf.y),hf.pt(2));wirepins(harness,hf,1,hs,1);hs.net(2,'BAT_FUSED')
harness.text('20 A fuse is provisional: verify measured startup/stall\ncurrent against wire and connector ratings.\nKey all power connectors: MDD20A has no\nreverse-polarity protection.',15,109,1.15)
drv=harness.part(mdd,271.78,81.28,ref='A1',fp='',on=False).allnets({'VB+':'BAT_FUSED','VB-':'GND','GND':'GND','PWM1':'PWM_L','DIR1':'DIR_L','PWM2':'PWM_R','DIR2':'DIR_R'})
for pin in ['M1A','M1B','M2A','M2B']:
 harness.items=[v for v in harness.items if uid(drv.id+'nc'+pin) not in v]
for i in range(2):
 mot=harness.part('Motor:Motor_DC',370.84,60.96+i*43.18,ref='M'+str(i+1),val='Pololu 4743 / 50:1',fp='',on=False)
 for pin,suffix,route in [('1','A',330.2+i*7.62),('2','B',317.5+i*7.62)]:
  dp='M'+str(i+1)+suffix;drv.used.add(dp);mot.used.add(pin);a=drv.pt(dp);b=mot.pt(pin)
  harness.wire(a,(route,a[1]));harness.wire((route,a[1]),(route,b[1]));harness.wire((route,b[1]),b)
# Continuous switched positive supply to driver, branch to control PCB by global label.
a=hs.pt(2);b=drv.pt('VB+');harness.wire(a,(226.06,a[1]));harness.wire((226.06,a[1]),(226.06,b[1]));harness.wire((226.06,b[1]),b);harness.dot(a)
harness.part('Device:C_Polarized',213.36,144.78,val='1000u 35V low ESR',fp='',on=False).allnets({'1':'BAT_FUSED','2':'GND'})
harness.part('Device:D_Zener',274.32,144.78,val='SMBJ15A / harness board',fp='',rot=270,on=False).allnets({'1':'BAT_FUSED','2':'GND'})
harness.text('Bulk + TVS physically at driver VB+/VB-.\nInsulate and strain-relieve assembly.\nPWM LOW = brake; <=20 kHz.',304,143,1.1)
for i,side in enumerate(['L','C','R']):harness.part('Levi:50209LX_Harness',68.58+i*116.84,220.98,ref='SW101',val='50209LX',fp='',unit=i+1,on=False).allnets({str(3*i+1):'BAUM_'+side+'_DIGRAW',str(3*i+2):'CQ_'+side,str(3*i+3):'IOL_CQ_'+side})
harness.text('SW101 is ONE physical 3PDT break-before-make switch, all poles mechanically linked.\nLogical groups 1/2/3, 4/5/6, 7/8/9 match the board 9-pin harness. Identify actual lugs by continuity.\nDrawn state: DIGITAL. Stop motors and disable IO-Link framers before changing mode.',15,250,1.1)

def split_wires(page):
 wires=[];other=[];points=set()
 for text in page.items:
  a=parse(text)
  if a[0]=='wire':
   xy=children(child(a,'pts'),'xy');ends=[tuple(map(float,p[1:])) for p in xy];wires.append(ends);points.update(ends)
  else:
   other.append(text)
   if a[0] in ('junction','global_label','label'):points.add(tuple(map(float,child(a,'at')[1:3])))
 for part in page.parts:
  for p in part.pins.values():points.add(p[:2])
 page.items=other;seen=set()
 for a,b in wires:
  dx=b[0]-a[0];dy=b[1]-a[1];length=dx*dx+dy*dy
  cuts=[]
  for pt in points:
   cross=(pt[0]-a[0])*dy-(pt[1]-a[1])*dx
   t=((pt[0]-a[0])*dx+(pt[1]-a[1])*dy)/length
   if abs(cross)<1e-5 and -1e-6<=t<=1+1e-6:cuts.append((t,pt))
  cuts.sort()
  for (_,p1),(_,p2) in zip(cuts,cuts[1:]):
   key=tuple(sorted([p1,p2]))
   if p1!=p2 and key not in seen:page.wire(p1,p2);seen.add(key)

# Library outputs
for p in PAGES:p.write()
(BASE/'libraries/Levi.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(dump(s) for s in CUSTOM.values())+')',encoding='utf8')
(BASE/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Levi") (type "KiCad") (uri "${KIPRJMOD}/libraries/Levi.kicad_sym") (options "") (descr "Levi vendor pin maps")))',encoding='utf8')
(BASE/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Levi") (type "KiCad") (uri "${KIPRJMOD}/libraries/Levi.pretty") (options "") (descr "Source-dimensioned module footprint")))',encoding='utf8')
fp='(footprint "Pololu_S13V_5pin" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr through_hole) (descr "Pololu S13V25Fx/S13V30F5, 5-pin header, top view, source 0J1959") (property "Reference" "REF**" (at 5.08 -22 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)))) (property "Value" "Pololu_S13V" (at 5.08 3 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))'
for i in range(5):fp+=f'(pad "{i+1}" thru_hole {"rect" if i==0 else "circle"} (at {f(i*2.54)} 0) (size 1.8 1.8) (drill 1.05) (layers "*.Cu" "*.Mask"))'
for x in [-4.15,14.35]:fp+=f'(pad "" np_thru_hole circle (at {x} -0.93) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask"))'
for layer,w,pad in [('F.Fab',.1,0),('F.SilkS',.12,.15),('F.CrtYd',.05,.5)]:fp+=f'(fp_rect (start {f(-6.35-pad)} {f(-21.63-pad)}) (end {f(16.55+pad)} {f(1.27+pad)}) (stroke (width {w}) (type default)) (fill none) (layer "{layer}"))'
for i,name in enumerate(['EN','VIN','GND','GND','OUT']):fp+=f'(fp_text user "{name}" (at {f(i*2.54)} -3.2 90) (layer "F.Fab") (effects (font (size .8 .8) (thickness .12))))'
fp+=')';(BASE/'libraries/Levi.pretty/Pololu_S13V_5pin.kicad_mod').write_text(fp,encoding='utf8')
# Vendor-dimensioned U3V50 module, top view, input at top. All nine header holes used.
fp='(footprint "Pololu_U3V50" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr through_hole) (descr "Pololu 0J1450 top view; U3V50F24; 9 header pins")'
for num,x,y in [('1',1.27,7.62),('2',6.35,5.08),('2',8.89,5.08),('3',11.43,5.08),('3',13.97,5.08),('5',1.27,43.18),('5',3.81,43.18),('4',6.35,43.18),('4',8.89,43.18)]:
 fp+=f'(pad "{num}" thru_hole {"rect" if num=="1" else "circle"} (at {x} {y}) (size 1.8 1.8) (drill 1.05) (layers "*.Cu" "*.Mask"))'
for x,y in [(2.54,2.54),(12.7,45.72)]:fp+=f'(pad "" np_thru_hole circle (at {x} {y}) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask"))'
for layer,w,d in [('F.Fab',.1,0),('F.SilkS',.12,.15),('F.CrtYd',.05,.5)]:fp+=f'(fp_rect (start {-d} {-d}) (end {15.24+d} {48.26+d}) (stroke (width {w}) (type default)) (fill none) (layer "{layer}"))'
for label,x,y in [('VIN',7.62,8),('GND',12.7,8),('EN',2.54,10.5),('VOUT',2.54,40.2),('GND',7.62,40.2)]:fp+=f'(fp_text user "{label}" (at {x} {y}) (layer "F.Fab") (effects (font (size .8 .8) (thickness .12))))'
fp+='(property "Reference" "REF**" (at 7.62 -2) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))) (property "Value" "U3V50F24" (at 7.62 50.3) (layer "F.Fab") (effects (font (size 1 1) (thickness .15)))))'
(BASE/'libraries/Levi.pretty/Pololu_U3V50.kicad_mod').write_text(fp)
src=LIBROOT/'footprints/Package_DFN_QFN.pretty/TQFN-48-1EP_7x7mm_P0.5mm_EP5.1x5.1mm.kicad_mod'
ff=parse(src.read_text());ff[1]=Q('MAX14819_T4877_4C_EP5.5')
for pad in children(ff,'pad'):
 if str(pad[1])=='49':child(pad,'size')[1:]=['5.5','5.5']
# Retain 4 stock paste windows (~53% coverage of 5.5-mm pad); no mismatched 3D model.
ff=[v for v in ff if not (isinstance(v,list) and v[0]=='model')]
(BASE/'libraries/Levi.pretty/MAX14819_T4877_4C_EP5.5.kicad_mod').write_text(dump(ff))
unique={p.ref:p for p in BOM if not p.ref.startswith('#')}
with (BASE/'BOM.csv').open('w',newline='',encoding='utf-8-sig') as out:
 w=csv.writer(out);w.writerow(['Reference','Value','Footprint','Placement','Sheet','Datasheet'])
 for ref,p in sorted(unique.items()):w.writerow([ref,p.value,p.fp,'PCB' if p.on else 'External harness',p.page.name,p.ds])
with (BASE/'BOM.csv').open('a',newline='',encoding='utf-8') as out:
 w=csv.writer(out)
 for model,count,url,prefix in [('Baumer O300.DI-GM1J.72N',3,'https://media.baumer.com/Baumer_O300.DI-GM1J.72N_EN_20250909_DS.pdf','BAUM'),('Banner Q20NDXL',3,'https://info.bannerengineering.com/cs/groups/public/documents/literature/127816.pdf','BANNER'),('JSumo ML1',4,'https://www.jsumo.com/micro-line-sensor-ml1','ML1')]:
  for i in range(count):w.writerow([prefix+str(i+1),model,'','External sensor','Connector harness',url])
(BASE/'design/expected_nets.json').write_text(json.dumps(EXPECTED,indent=2),encoding='utf8')
(BASE/'design/gpio_map.json').write_text(json.dumps(mp,indent=2),encoding='utf8')
issues=[]
for p in unique.values():
 if not p.on:continue
 if not p.fp:issues.append(p.ref+': missing footprint');continue
 cat,name=p.fp.split(':');path=(BASE/'libraries/Levi.pretty' if cat=='Levi' else LIBROOT/'footprints'/(cat+'.pretty'))/(name+'.kicad_mod')
 if not path.exists():issues.append(p.ref+': missing '+str(path));continue
 pads={str(x[1]) for x in children(parse(path.read_text(encoding='utf8')),'pad') if str(x[1])}
 needed={n for part in BOM if part.ref==p.ref for n in part.pins}
 if needed-pads:issues.append(p.ref+': absent pads '+str(needed-pads))
print('Sheets',len(PAGES),'physical components',len(unique),'PCB',sum(p.on for p in unique.values()))
print('Footprint issues:',issues)
(BASE/'design/review/footprint_audit.json').write_text(json.dumps({'components':len(unique),'pcb_components':sum(p.on for p in unique.values()),'issues':issues},indent=2))




