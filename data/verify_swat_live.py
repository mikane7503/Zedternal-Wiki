"""Read-only live Pages verification of the complete scoped output and resources."""
import urllib.request,json,hashlib,time,concurrent.futures
from update_swat_series import WIKI,SCOPE,read,sha
base='https://mikane7503.github.io/Zedternal-Wiki/'
def fetch(path):
 req=urllib.request.Request(base+path+'?verify='+str(time.time_ns()),headers={'User-Agent':'TemperedWikiAudit'})
 with urllib.request.urlopen(req,timeout=30) as r:return r.read()
local=json.loads(read(WIKI/'docs/data/perks.json'));live=json.loads(fetch('data/perks.json'))
assert live==local,'Live data differs from verified scoped output'
paths={'app.js','index.html'}
for perk in local['basePerks']+local['advancedPerks']:
 if perk['key'] in SCOPE:
  paths.add(perk['icon']);paths.update(perk.get('rankIcons',[]));paths.update(s['icon'] for s in perk['skills'] if s.get('icon'))
def check(path):
 expected=(WIKI/'docs'/path).read_bytes();actual=fetch(path)
 # Git stores text with LF; Windows checkout preserves the existing CRLF.
 if path in ['app.js','index.html']:
  expected=expected.replace(b'\r\n',b'\n');actual=actual.replace(b'\r\n',b'\n')
 assert hashlib.sha256(actual).digest()==hashlib.sha256(expected).digest(),'Live resource differs: '+path
 return path
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(check,sorted(paths)))
print('LIVE PASS: complete JSON matches local audited output; '+str(len(paths))+' referenced icons/frontend resources match SHA256; unrelated perk data unchanged')
