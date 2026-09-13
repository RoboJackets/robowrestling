import urllib.request,concurrent.futures
from pathlib import Path
urls={'max':'https://www.analog.com/media/en/technical-documentation/data-sheets/MAX14819.pdf','mdd':'https://docs.google.com/document/d/1YHKcs8N0UBrRI4r2OaIqHs6m_B_NaVBF7EB5C3fPTG4/export?format=pdf','baumer':'https://media.baumer.com/Baumer_O300.DI-GM1J.72N_EN_20250909_DS.pdf?download=1','traco':'https://www.tracopower.com/sites/default/files/products/datasheets/tsr2_datasheet.pdf'}
def get(it):
 k,u=it
 try:
  data=urllib.request.urlopen(u,timeout=15).read();Path('design/sources/'+k+'.pdf').write_bytes(data);return k,len(data)
 except Exception as e:return k,str(e)
with concurrent.futures.ThreadPoolExecutor() as p:print(list(p.map(get,urls.items())))
