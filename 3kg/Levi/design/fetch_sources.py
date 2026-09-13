import urllib.request,concurrent.futures
from pathlib import Path
urls={'max':'https://www.analog.com/media/en/technical-documentation/data-sheets/max14819.pdf','baumer':'https://media.baumer.com/Baumer_O300.DI-GM1J.72N_EN_20250909_DS.pdf','pololu':'https://www.pololu.com/file/0J1959/step-up-step-down-voltage-regulator-s13v25fx-dimensions.pdf','banner':'https://info.bannerengineering.com/cs/groups/public/documents/literature/127816.pdf','ml1':'https://www.jsumo.com/micro-line-sensor-ml1'}
def get(item):
 k,u=item
 try:
  r=urllib.request.urlopen(u,timeout=20); data=r.read(); Path('design/sources/'+k+('.html' if k=='ml1' else '.pdf')).write_bytes(data); return k,len(data)
 except Exception as e:return k,str(e)
with concurrent.futures.ThreadPoolExecutor() as p: print(list(p.map(get,urls.items())))

