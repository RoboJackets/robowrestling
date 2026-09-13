import urllib.request,concurrent.futures
from pathlib import Path
urls={'pkg':'https://www.analog.com/media/en/package-pcb-resources/package/pkg_pdf/tqfn/21-0144.pdf','boost':'https://www.pololu.com/product/2569/resources'}
def get(it):
 k,u=it
 try:
  b=urllib.request.urlopen(u,timeout=15).read();Path('design/sources/'+k+('.pdf' if k=='pkg' else '.html')).write_bytes(b);return k,len(b)
 except Exception as e:return str(e)
with concurrent.futures.ThreadPoolExecutor() as p:print(list(p.map(get,urls.items())))
