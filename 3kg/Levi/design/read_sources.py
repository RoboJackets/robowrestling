from pathlib import Path
import pypdf
for n in ['pololu','banner']:
 r=pypdf.PdfReader('design/sources/'+n+'.pdf');Path('design/sources/'+n+'.txt').write_text('\n'.join(p.extract_text() for p in r.pages),encoding='utf8')
from bs4 import BeautifulSoup
s=BeautifulSoup(Path('design/sources/ml1.html').read_text(encoding='utf8'),'html.parser').get_text(' ',strip=True);i=s.find('Features Dimensions'); print(s[i:i+4500])
