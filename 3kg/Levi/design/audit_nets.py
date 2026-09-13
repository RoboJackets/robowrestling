from pathlib import Path
from kicad_sexpr import *
import json,csv
root=parse(Path('design/review/Levi.net').read_text(encoding='utf8'))
actual={};allnets={}
for n in children(child(root,'nets'),'net'):
 name=child(n,'name')[1];nodes=children(n,'node');allnets[name]=[(child(a,'ref')[1],child(a,'pin')[1]) for a in nodes]
 for a in nodes:actual[child(a,'ref')[1],child(a,'pin')[1]]=name
bom={r['Reference']:r for r in csv.DictReader(Path('BOM.csv').open(encoding='utf-8-sig'))}
exp=json.loads(Path('design/expected_nets.json').read_text());bad=[];checked=0
for ref,p,n in exp:
 if ref not in bom or bom[ref]['Placement']!='PCB':continue
 checked+=1
 if actual.get((ref,p))!=n:bad.append([ref,p,n,actual.get((ref,p))])
assert not bad,bad
# Independent topology checks from exported KiCad netlist, including local unlabelled wires.
checks=[]
def require(ok,description):
 assert ok,description
 checks.append(description)
def values(net):return [(r,p,bom[r]['Value']) for r,p in allnets[net] if r in bom]
for ref,units in [('U20',[(5,4,2),(7,6,1),(11,10,13)]),('U21',[(5,4,2),(7,6,1),(9,8,14),(11,10,13)]),('U22',[(5,4,2),(7,6,1)])]:
 for plus,minus,out in units:
  net=actual[ref,str(plus)];v=values(net)
  require(len(v)==5 and sorted(x[2] for x in v if x[0]!=ref)==sorted(['30k 1%','10k 1%','1n 50V C0G','1M 1%']),f'{ref} input {plus}: divider, filter and feedback connected')
  require(actual[ref,str(minus)]=='SENSE_REF',f'{ref} input {minus}: reference connected')
  require(any(val=='4.7k' for r,p,val in values(actual[ref,str(out)])),f'{ref} output {out}: pull-up connected')
for side in ['FL','FR','RL','RR']:
 v=values('LINE_'+side+'_ADC')
 require(sorted(val for r,p,val in v if r.startswith(('R','C')))==sorted(['10k 1%','20k 1%','10n 10V']),side+' ADC divider and capacitor')
require(sorted(val for r,p,val in values('BAT_ADC') if r.startswith(('R','C')))==sorted(['100k 1%','22k 1%','100n 10V']),'Battery ADC divider and filter')
for side in ['L','R']:
 require(any(val=='100R' for r,p,val in values('PWM_'+side)) and any(val=='10k' for r,p,val in values('PWM_'+side)),side+' PWM series resistor and default-low pull-down')
for r in ['U30','U31']:
 require(all(actual[r,p]=='+24V_SENS' for p in ['8','29']) and actual[r,'6']=='+5V' and actual[r,'40']=='+3V3' and actual[r,'49']=='GND',r+' correct power domains')
require(len({actual['U10',p] for p in ['3','4','5','6','7']})==5,'Distinct assigned main-MCU pin nets')
report={'pcb_label_connections_checked':checked,'mismatches':bad,'independent_topology_checks':checks,'external_harness':'Excluded by KiCad PCB netlist; visually inspected separately'}
Path('design/review/net_audit.json').write_text(json.dumps(report,indent=2))
print('PASS:',checked,'PCB pin-to-net expectations;',len(checks),'topology checks')

