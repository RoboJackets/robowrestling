from pathlib import Path
import csv, json, re, sys, html, math, hashlib
from collections import defaultdict
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable, CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
import pymupdf
from kicad_sexpr import parse,child,children,pins

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
TMP=ROOT/'tmp/pdfs';TMP.mkdir(parents=True,exist_ok=True)
BLUE=colors.HexColor('#133B53');TEAL=colors.HexColor('#087F8C');PALE=colors.HexColor('#EDF4F6');INK=colors.HexColor('#1F2933')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyGuide',fontName='Helvetica',fontSize=10,leading=14,textColor=INK,spaceAfter=7))
styles.add(ParagraphStyle(name='Chapter',fontName='Helvetica-Bold',fontSize=22,leading=26,textColor=BLUE,spaceAfter=15))
styles.add(ParagraphStyle(name='SubGuide',fontName='Helvetica-Bold',fontSize=13,leading=17,textColor=TEAL,spaceBefore=10,spaceAfter=6,keepWithNext=True))
styles.add(ParagraphStyle(name='AtlasHeading',parent=styles['SubGuide'],keepWithNext=False))
styles.add(ParagraphStyle(name='CellGuide',fontName='Helvetica',fontSize=8.1,leading=11,textColor=INK,spaceAfter=0,wordWrap='CJK'))
styles.add(ParagraphStyle(name='HeadCell',parent=styles['CellGuide'],fontName='Helvetica-Bold',textColor=colors.white))
styles.add(ParagraphStyle(name='TinyGuide',fontName='Helvetica',fontSize=8,leading=11,textColor=INK,spaceAfter=6))
styles.add(ParagraphStyle(name='CoverGuide',fontName='Helvetica-Bold',fontSize=40,leading=45,textColor=BLUE,spaceAfter=22))

def esc(s):return html.escape(str(s),quote=False)
def para(s,style='BodyGuide'):return Paragraph(esc(s),styles[style])
def table(rows,widths=None):
 data=[[Paragraph(esc(c),styles['HeadCell' if i==0 else 'CellGuide']) for c in row] for i,row in enumerate(rows)]
 if widths is None:widths=[499/len(rows[0])]*len(rows[0])
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BLUE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('LINEBELOW',(0,0),(-1,0),.6,TEAL)]))
 return t

class GuideDoc(SimpleDocTemplate):
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name=='Chapter' and f.getPlainText() not in ['Contents','From system architecture to every connection']:
   title=f.getPlainText();key='chapter_'+hashlib.sha1(title.encode()).hexdigest()[:12]
   self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,0,False)
   self.notify('TOCEntry',(0,title,self.page,key))

def footer(c,d):
 c.saveState();w,h=A4
 c.setStrokeColor(TEAL);c.setLineWidth(.6);c.line(48,40,w-48,40)
 c.setFont('Helvetica',8);c.setFillColor(BLUE)
 c.drawString(48,27,'LEVI / REV 1.0 / LEARNING HANDBOOK')
 c.drawRightString(w-48,27,str(d.page));c.restoreState()

class SystemDiagram(Flowable):
 def __init__(self):Flowable.__init__(self);self.width=499;self.height=225
 def draw(self):
  c=self.canv
  def box(x,y,w,h,title,sub):
   c.setFillColor(PALE);c.setStrokeColor(TEAL);c.roundRect(x,y,w,h,5,fill=1,stroke=1)
   c.setFillColor(BLUE);c.setFont('Helvetica-Bold',9);c.drawCentredString(x+w/2,y+h-15,title)
   c.setFont('Helvetica',8);c.drawCentredString(x+w/2,y+10,sub)
  def arrow(x1,y1,x2,y2):
   c.setStrokeColor(TEAL);c.setFillColor(TEAL);c.line(x1,y1,x2,y2)
   a=math.atan2(y2-y1,x2-x1);p=c.beginPath();p.moveTo(x2,y2)
   for da in [-.5,.5]:p.lineTo(x2-6*math.cos(a+da),y2-6*math.sin(a+da))
   p.close();c.drawPath(p,fill=1,stroke=0)
  box(0,165,110,45,'3S BATTERY','11.1 V nominal')
  box(165,165,140,45,'FUSE + DISCONNECT','external high-current bus')
  box(365,165,132,45,'MDD20A + MOTORS','power switching')
  arrow(110,187,165,187);arrow(305,187,365,187)
  box(165,90,140,45,'REGULATORS','24 V / 5 V / 3.3 V');arrow(235,165,235,135)
  box(0,15,120,45,'SENSORS + INPUTS','industrial and analog')
  box(165,15,140,45,'ESP32-S3 CONTROL','decision + motor enable')
  box(365,15,132,45,'ESP32-C6','telemetry')
  arrow(120,37,165,37);arrow(305,37,365,37);arrow(235,90,235,60)
  c.setStrokeColor(TEAL);c.line(305,50,332,50);c.line(332,50,332,147);c.line(332,147,430,147);arrow(430,147,430,165)
  c.setFont('Helvetica',7);c.setFillColor(BLUE);c.drawString(338,112,'PWM / DIR')

src=(ROOT/'design/learning_guide.md').read_text(encoding='utf8')
story=[Spacer(1,55),para('LEVI','CoverGuide'),para('From system architecture to every connection','Chapter'),para('A guided study of the 3 kg robowrestling schematic'),Spacer(1,12),SystemDiagram(),Spacer(1,18),para('Includes worked circuit calculations, a battery recommendation with mechanical data, a component and pin atlas, exercises, and all ten original-size schematic sheets.'),Spacer(1,15),para('Schematic revision 1.0 | Prepared 10 September 2026','SubGuide'),para('Based on the saved KiCad files and exported netlist. Electrical connectivity checked; PCB layout and powered validation remain. Battery recommendation assumes a three-minute match unless your mechanical/runtime requirements say otherwise.','TinyGuide'),PageBreak()]
story+=[para('Contents','Chapter')]
toc=TableOfContents();toc.levelStyles=[ParagraphStyle(name='TOCGuide',fontName='Helvetica',fontSize=10,leading=13,leftIndent=0,firstLineIndent=0,spaceBefore=2,textColor=BLUE)]
story+=[toc,PageBreak()]

lines=src.splitlines();i=0
while i<len(lines):
 l=lines[i].strip()
 if not l:i+=1;continue
 if l.startswith('# '):
  if i>0:story.append(PageBreak())
  title=l[2:];story.append(para(title,'Chapter'))
  # Overview diagram is on the facing cover; leave room for the end-to-end example.
  i+=1;continue
 if l.startswith('## '):story.append(para(l[3:],'SubGuide'));i+=1;continue
 if l.startswith('|'):
  rows=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   cells=[v.strip() for v in lines[i].strip().strip('|').split('|')]
   if not all(re.fullmatch(r'[-: ]+',v) for v in cells):rows.append(cells)
   i+=1
  story+=[table(rows),Spacer(1,9)];continue
 if re.match(r'^\d+\. ',l):story.append(para(l));i+=1;continue
 chunks=[l];i+=1
 while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')) and not re.match(r'^\d+\. ',lines[i]):chunks.append(lines[i].strip());i+=1
 story.append(para(' '.join(chunks)))

sources={
'S1 ESP32-S3 module':'https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf',
'S2 ESP32-C6 module':'https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html',
'S3 MAX14819':'https://www.analog.com/media/en/technical-documentation/data-sheets/max14819.pdf',
'S4 TI LM339B':'https://www.ti.com/lit/ds/symlink/lm339.pdf',
'S5 Baumer O300':'https://media.baumer.com/Baumer_O300.DI-GM1J.72N_EN_20250909_DS.pdf',
'S6 Banner Q20':'https://info.bannerengineering.com/cs/groups/public/documents/literature/127816.pdf',
'S7 JSumo ML1':'https://www.jsumo.com/micro-line-sensor-ml1',
'S8 Cytron MDD20A':'https://docs.google.com/document/d/1YHKcs8N0UBrRI4r2OaIqHs6m_B_NaVBF7EB5C3fPTG4/edit',
'S9 Pololu 4743 motor':'https://www.pololu.com/product/4743',
'S10 Pololu U3V50F24':'https://www.pololu.com/product/2569',
'S10b Boost mechanical drawing':'https://www.pololu.com/file/0J1450/u3v50x-step-up-voltage-regulator-dimensions.pdf',
'S11 Traco TSR2':'https://www.tracopower.com/sites/default/files/products/datasheets/tsr2_datasheet.pdf',
'B1 Recommended 1300 mAh pack':'https://genstattu.com/tattu-1300mah-75c-3s1p-lipo-battery-pack-with-xt60-plug.html',
'B2 Lighter 1050 mAh pack':'https://www.tattuworld.com/products/tattu-classic-1050mah-3s1p-11-1v-75c-fpv-lipo-battery.html',
'B3 Longer 1800 mAh pack':'https://genstattu.com/tattu-1800mah-75c-3s1p-lipo-battery-pack-with-xt60-plug.html',
'B4 Battery manual':'https://www.genstattu.com/content/instock/Lipo-Manual.pdf',
'B5 Manufacturer battery guide':'https://www.genstattu.com/bw/'
}
story.extend([PageBreak(),para('Primary source links','Chapter')])
for name,url in sources.items():story.append(Paragraph('<link href="'+html.escape(url,quote=True)+'" color="#087F8C"><u>'+esc(name)+'</u></link>',styles['BodyGuide']))

bom=list(csv.DictReader((ROOT/'BOM.csv').open(encoding='utf-8-sig')));byref={r['Reference']:r for r in bom}
netroot=parse((ROOT/'design/review/Levi.net').read_text(encoding='utf8'));netby={};members={}
for n in children(child(netroot,'nets'),'net'):
 name=str(child(n,'name')[1]);members[name]=[]
 for v in children(n,'node'):
  key=(str(child(v,'ref')[1]),str(child(v,'pin')[1]));netby[key]=name;members[name].append(key)
symbols=defaultdict(dict)
for file in sorted(ROOT.glob('*.kicad_sch')):
 sch=parse(file.read_text(encoding='utf8'));lib={str(s[1]):s for s in children(child(sch,'lib_symbols'),'symbol')}
 for s in children(sch,'symbol'):
  props={str(p[1]):str(p[2]) for p in children(s,'property')};ref=props['Reference']
  if ref.startswith('#'):continue
  unit=int(child(s,'unit')[1]);name=str(child(s,'lib_id')[1])
  for pn,nm,at,typ in pins(lib[name],unit):symbols[ref][str(pn)]={'name':str(nm),'type':typ,'unit':unit}

def order(s):return (re.sub(r'\d+','',s),int(re.search(r'\d+',s).group()) if re.search(r'\d+',s) else 0)
def netshort(s):return 'NC' if s.startswith('unconnected-') else s.replace('/01_Control/','').replace('/02_Telemetry/','').replace('/03_Baumer/','').replace('/04_Banner/','').replace('/07_Line_Motor/','').replace('/09_Enable_Debug/','')
def role(r):
 ref=r['Reference'];v=r['Value'];sh=r['Sheet'];n=int(re.search(r'\d+',ref).group()) if re.search(r'\d+',ref) else 0
 if r['Placement']=='External sensor':return 'Purchased sensor; connect through its sheet 4, 5 or 8 harness.'
 if ref=='A1':return 'External dual motor power stage.'
 if ref=='BT1':return '3S battery; handbook recommends Tattu 1300 mAh.'
 if ref.startswith('M'):return 'External brushed gearmotor; no encoder in selected part.'
 if ref.startswith('J'):return 'Board harness/service interface; exact pin map below.'
 if ref.startswith('TP'):return 'Baumer industrial-voltage teach access.'
 if ref.startswith('SW'):return 'Reset / boot switch.' if n<100 else ('Physical battery disconnect.' if n==100 else 'Mechanically linked 3PDT mode selector.')
 if ref.startswith('F'):return 'Branch overcurrent protection; check time-current behavior.'
 if ref.startswith('Y'):return 'IO-Link reference crystal; load tuning required.'
 if ref.startswith('Q'):return 'Buffered sensor-logic LED driver.'
 if ref.startswith('D'):return 'Reverse-input blocking.' if n==1 else ('Transient suppression; not a precision clamp.' if n in [2,3,4,5,15] else 'HIGH-state indicator LED.')
 if ref.startswith('U'):return {'U1':'24 V boost module.','U2':'5 V buck-boost module.','U3':'3.3 V switching module.','U10':'Main controller.','U11':'Telemetry processor.','U20':'Three Baumer comparators plus unused unit.','U21':'Four Banner comparators.','U22':'Two Banner comparators plus unused units.','U30':'Left/center IO-Link master.','U31':'Right IO-Link master; spare channel unused.','U40':'Dual PWM enable AND gate.'}.get(ref,'Integrated circuit.')
 if ref.startswith('C'):
  if n in [9,13]:return 'EN reset RC capacitor.'
  if n in [14,15,16,19,20,21,22,23,24]:return 'Raw comparator input noise filter.'
  if n==18:return 'Shared comparator reference filtering.'
  if n in [27,28,33,34]:return 'Crystal load capacitor.'
  if n in [39,41,43,45]:return 'ML1 ADC low-pass capacitor.'
  if n==47:return 'Battery ADC low-pass capacitor.'
  if n==49:return 'External motor-bus bulk reservoir.'
  return 'Supply bypass / local energy reservoir.'
 if ref.startswith('R'):
  if n in [1,5]:return 'EN pull-up; with C gives reset ramp.'
  if n in [2,6,7]:return 'BOOT/strap default HIGH.'
  if n in [3,4]:return 'Inter-MCU UART series damping.'
  if n in [8,13,18]:return 'Baumer TEACH default LOW.'
  if n in [23,24]:return 'Shared 1.245 V reference divider.'
  if 9<=n<=54:
   return {'30k 1%':'Raw-input divider series arm.','10k 1%':'Raw-input divider shunt arm.','1M 1%':'Positive feedback / hysteresis.','4.7k':'3.3 V comparator output pull-up.','10k':'24 V Banner NPN pull-up.'}.get(v,'Comparator conditioning.')
  if n in [55,57]:return 'IO-Link CS default HIGH.'
  if n in [56,58]:return 'Open-drain IRQ pull-up.'
  if 59<=n<=66:return 'ML1 2/3 ADC scaling divider.'
  if n in [67,68]:return 'Battery 22/122 scaling divider.'
  if n in [69,71,72,74]:return 'Motor command series damping.'
  if n in [70,73,75,76,77,78,79,80]:return 'Motor command/enable default LOW.'
  return 'Indicator base-current limiter.' if v=='47k' else 'Indicator LED current limiter.'
 return 'See schematic and connection atlas.'

story += [PageBreak(),para('Component reference atlas','Chapter'),para('All 226 BOM entries are listed, including 207 PCB components and purchased external items. Repeated circuits are explained once in the teaching chapters; this atlas locates each physical part. Pin numbers below are physical symbol/footprint identifiers. The footprint dictionary follows the ledger.','BodyGuide')]
fps=sorted({r['Footprint'] for r in bom if r['Footprint']});fpids={v:'FP'+str(i+1) for i,v in enumerate(fps)}
by_sheet=defaultdict(list)
for r in bom:by_sheet[r['Sheet']].append(r)
for sh in ['Levi','01_Control','02_Telemetry','03_Baumer','04_Banner','05_IOLink_A','06_IOLink_B','07_Line_Motor','08_Harness','09_Enable_Debug','Connector harness']:
 story.extend([CondPageBreak(85),para(sh,'AtlasHeading')]);rows=[['Ref / value','Purpose','Connections / footprint']]
 for r in sorted(by_sheet[sh],key=lambda r:order(r['Reference'])):
  ref=r['Reference'];pinitems=sorted(symbols.get(ref,{}),key=order)
  if len(pinitems)<=3 and r['Placement']=='PCB':conn='; '.join(p+': '+netshort(netby.get((ref,p),'NC')) for p in pinitems)
  elif r['Placement']=='PCB':conn='See full pin atlas.'
  else:conn='External; see harness/sensor chapter.'
  rows.append([ref+' / '+r['Value'],role(r),conn+' '+fpids.get(r['Footprint'],'No PCB footprint')])
 story.extend([table(rows,[110,178,211]),Spacer(1,8)])

story.extend([PageBreak(),para('Footprint dictionary','Chapter'),para('All assigned PCB footprints, including the local module and MAX14819 land patterns. These names identify the actual KiCad library entries; do not replace them solely on package appearance.')])
story.append(table([['ID','KiCad footprint']]+[[fpids[f],f] for f in fps],[45,454]))
story.extend([PageBreak(),para('Full IC and connector pin atlas','Chapter'),para('Generated from embedded schematic symbols and the exported PCB netlist. Package pin numbers are the left column. NC indicates an unused, unconnected pin in this design. GPIO names are separate from pad numbers. Internal local nets retain their KiCad-generated names.')])
pin_count=0
for ref in sorted(symbols,key=order):
 if ref not in byref or byref[ref]['Placement']!='PCB' or not ref.startswith(('U','J')):continue
 story.extend([CondPageBreak(85),para(ref+' - '+byref[ref]['Value'],'AtlasHeading')]);rows=[['Pin','Signal / pin name','Electrical net']]
 for pn,p in sorted(symbols[ref].items(),key=lambda v:order(v[0])):
  rows.append([pn,p['name'],netshort(netby.get((ref,pn),'NC'))]);pin_count+=1
 story+=[table(rows,[40,170,289]),Spacer(1,8)]

story.extend([PageBreak(),para('Schematic sheet collection','Chapter'),para('The next ten pages reproduce the saved schematic at its original A3 page size using vector artwork. Zoom rather than printing multiple sheets on one small page. The PDF sidebar has a bookmark for each sheet. Return to the relevant teaching chapter when tracing a repeated circuit.')])
schematic_files=[ROOT/'design/review/release/Levi.svg']+sorted((ROOT/'design/review/release').glob('Levi-*.svg'))
story.append(table([['Sheet','Source file']]+[[str(i+1),p.stem.replace('Levi-','')+'.kicad_sch'] for i,p in enumerate(schematic_files)],[50,449]))
doc=GuideDoc(str(TMP/'handbook_text.pdf'),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=46,bottomMargin=54,title='Levi: complete schematic learning handbook',author='RoboJackets / Levi project')
doc.multiBuild(story,onFirstPage=footer,onLaterPages=footer)
writer=PdfWriter();writer.append(str(TMP/'handbook_text.pdf'));main_count=len(writer.pages)
for i,p in enumerate(schematic_files):
 with pymupdf.open(p) as sv:buf=sv.convert_to_pdf()
 import io
 reader=PdfReader(io.BytesIO(buf));page_index=len(writer.pages);writer.append(reader,import_outline=False)
 writer.add_outline_item('Schematic '+str(i+1)+': '+p.stem.replace('Levi-',''),page_index)
writer.add_metadata({'/Title':'Levi - Complete Schematic Learning Handbook','/Author':'RoboJackets / Levi','/Subject':'Revision 1.0 circuits, pin atlas, battery selection and bring-up'})
final=OUT/'Levi_Schematic_Learning_Handbook.pdf'
with final.open('wb') as f:writer.write(f)
manifest={'pdf':str(final),'pages':len(writer.pages),'teaching_and_atlas_pages':main_count,'schematic_pages':len(schematic_files),'bom_entries':len(bom),'pcb_components':sum(r['Placement']=='PCB' for r in bom),'atlas_ic_connector_pins':pin_count,'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.kicad_sch')}}
(TMP/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))

# Searchable offline companion, generated from the same teaching source and pin data.
def mdhtml(text):
 lines=text.splitlines();out=[];i=0
 while i<len(lines):
  l=lines[i].strip()
  if not l:i+=1;continue
  if l.startswith('# '):out.append('<h2>'+esc(l[2:])+'</h2>');i+=1;continue
  if l.startswith('## '):out.append('<h3>'+esc(l[3:])+'</h3>');i+=1;continue
  if l.startswith('|'):
   out.append('<table>');rowno=0
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[v.strip() for v in lines[i].strip().strip('|').split('|')];i+=1
    if all(re.fullmatch(r'[-: ]+',v) for v in cells):continue
    tag='th' if rowno==0 else 'td';out.append('<tr>'+''.join('<'+tag+'>'+esc(v)+'</'+tag+'>' for v in cells)+'</tr>');rowno+=1
   out.append('</table>');continue
  if re.match(r'^\d+\. ',l):out.append('<p>'+esc(l)+'</p>');i+=1;continue
  chunks=[l];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')) and not re.match(r'^\d+\. ',lines[i]):chunks.append(lines[i].strip());i+=1
  out.append('<p>'+esc(' '.join(chunks))+'</p>')
 return ''.join(out)
cards=[]
for r in sorted(bom,key=lambda r:order(r['Reference'])):
 ref=r['Reference'];rows=''.join('<tr><td>'+esc(pn)+'</td><td>'+esc(p['name'])+'</td><td>'+esc(netshort(netby.get((ref,pn),'NC' if r['Placement']=='PCB' else 'See external harness')))+'</td></tr>' for pn,p in sorted(symbols.get(ref,{}).items(),key=lambda v:order(v[0])))
 cards.append('<details class="part" data-search="'+html.escape((ref+' '+r['Value']+' '+r['Sheet']+' '+role(r)).lower(),quote=True)+'"><summary>'+esc(ref+' | '+r['Value'])+'</summary><p>'+esc(role(r))+'</p><p>'+esc(r['Sheet']+' | '+r['Placement']+' | '+r['Footprint'])+'</p><table><tr><th>Pin</th><th>Name</th><th>Net</th></tr>'+rows+'</table></details>')
site='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Learn Levi</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f8f9;color:#20323e;font:17px/1.65 system-ui,sans-serif}header{background:#133b53;color:white;padding:45px max(24px,calc((100vw - 1100px)/2))}header h1{font-size:48px;margin:0}main{max-width:1100px;margin:auto;padding:24px}h2{color:#133b53;margin-top:55px;border-top:3px solid #087f8c;padding-top:22px}h3{color:#087f8c}table{width:100%;border-collapse:collapse;font-size:14px;margin:20px 0}td,th{padding:10px;border:1px solid #dae4e8;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#133b53;color:white}tr:nth-child(even){background:#edf4f6}a{color:#087f8c}details{background:white;border:1px solid #d3e0e6;padding:14px;margin:10px 0;border-radius:7px}summary{cursor:pointer;font-weight:650}input{font:inherit;padding:8px;max-width:100%;border:1px solid #9bb2bd;border-radius:5px}.tools{background:white;border:1px solid #cedfe7;padding:25px;border-radius:10px}.tools label{display:inline-block;margin:8px}output{display:block;font-size:24px;color:#087f8c;font-weight:bold}.sheet svg{width:100%;height:auto}.sheet{overflow:auto}nav{display:flex;gap:20px;flex-wrap:wrap}nav a{color:white}#toc{columns:2;font-size:15px}@media(max-width:700px){#toc{columns:1}header h1{font-size:36px}table{font-size:12px}td,th{padding:6px}}</style><header><h1>Learn Levi</h1><p>Architecture. Circuits. Every connection.</p><nav><a href="#course">Handbook</a><a href="#calculator">Calculators</a><a href="#atlas">Part finder</a><a href="#sheets">Schematics</a></nav></header><main><p>Revision 1.0 | Schematic study, not a claim of powered validation. Use the PDF for printing and this offline page for searching and zooming.</p><div id="toc"></div><section id="course">'''+mdhtml(src)+'''</section><h2>Primary source links</h2><ul>'''+''.join('<li><a href="'+html.escape(u,quote=True)+'">'+esc(n)+'</a></li>' for n,u in sources.items())+'''</ul><section class="tools" id="calculator"><h2>Calculate, then predict the measurement</h2><p>Illustrative ideal calculations. These do not establish safe continuous motor load.</p><label>Capacity (mAh) <input id="cap" type="number" value="1300" min="1"></label><label>Average battery current (A) <input id="amps" type="number" value="6" min="0.01" step="0.1"></label><label>Usable fraction <input id="frac" type="number" value="0.8" min="0.1" max="1" step="0.05"></label><output id="runtime"></output><label>ML1 output (V) <input id="sensor" type="number" value="3.3" min="0" max="3.3" step="0.1"></label><output id="adc"></output><label>Battery ADC voltage (V) <input id="batadc" type="number" value="2" min="0" max="2.5" step="0.01"></label><output id="pack"></output></section><section id="atlas"><h2>Part finder - all 226 BOM entries</h2><p>Search by reference, value, function or sheet; expand a result for pins and footprint.</p><input id="search" type="search" placeholder="Try U30, R9, 47k, Banner..." style="width:100%">'''+''.join(cards)+'''</section><section id="sheets"><h2>All ten schematic sheets</h2><p>Expand a sheet and zoom in your browser. These are embedded vector copies of the actual saved schematic.</p>'''
for p in schematic_files:
 svg=p.read_text(encoding='utf8');svg=svg[svg.index('<svg'):]
 site+='<details><summary>'+esc(p.stem)+'</summary><div class="sheet">'+svg+'</div></details>'
site+='''</section></main><script>
document.querySelectorAll('#course h2').forEach((h,i)=>{h.id='lesson-'+i;let a=document.createElement('a');a.href='#'+h.id;a.textContent=h.textContent;let d=document.createElement('div');d.append(a);document.querySelector('#toc').append(d)});
function calc(){let c=+document.querySelector('#cap').value,a=+document.querySelector('#amps').value,f=+document.querySelector('#frac').value;document.querySelector('#runtime').textContent=c>0&&a>0&&f>0&&f<=1?'Estimated runtime: '+(60*c/1000*f/a).toFixed(2)+' minutes':'Enter positive capacity/current and usable fraction 0-1';document.querySelector('#adc').textContent='Ideal ML1 ADC node: '+(+document.querySelector('#sensor').value*2/3).toFixed(3)+' V';document.querySelector('#pack').textContent='Inferred pack voltage: '+(+document.querySelector('#batadc').value*122/22).toFixed(3)+' V'}document.querySelectorAll('.tools input').forEach(e=>e.addEventListener('input',calc));calc();document.querySelector('#search').addEventListener('input',e=>{let q=e.target.value.toLowerCase();document.querySelectorAll('.part').forEach(d=>d.hidden=!d.dataset.search.includes(q))});</script></html>'''
(ROOT/'output/Levi_Learning_Companion.html').write_text(site,encoding='utf8')
print('Offline companion written.')
