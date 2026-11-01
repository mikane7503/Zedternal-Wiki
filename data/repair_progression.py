"""Repair progression presentation using compiled-source description getters."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
namespace={'__file__':str(ROOT/'data/rebuild_ascension.py')}
exec((ROOT/'data/rebuild_ascension.py').read_text(encoding='utf-8-sig').split('old=json.loads')[0],namespace)
render,field,SRC=map(namespace.get,['render','field','SRC'])
path=ROOT/'docs/data/perks.json'
d=json.loads(path.read_text(encoding='utf-8'))
for group in ['basePerks','advancedPerks']:
 for p in d[group]:
  for i,line in enumerate(p['descriptions']):
   visible=re.sub('<[^>]+>','',line['raw']).strip()
   negative=bool(re.search(r'캡스톤.{0,12}(?:없|미구현|미적용)',visible))
   line['isCapstone']=not negative and bool(re.search(r'캡스톤',visible) or re.match(r'\[?(?:레벨\s*)?(?:10|20)\s*(?:레벨|단계|:)',visible))
   if '%x' in line['raw'] and not line['isCapstone']:
    line['levelValues']=[render(p['className'],p['key'],i,line['raw'],lv,field,SRC) for lv in range(1,p['maxLevel']+1)]
  p['passiveDescriptions']=[x for x in p['descriptions'] if not x['isCapstone']]
  p['capstoneDescriptions']=[x for x in p['descriptions'] if x['isCapstone']]
  p['noCapstoneNote']=None if p['capstoneDescriptions'] else '별도 캡스톤 효과가 없습니다.'
  p['overviewDescriptions']=p['passiveDescriptions']
path.write_text(json.dumps(d,ensure_ascii=False,indent=1),encoding='utf-8')
print('Progression descriptions repaired')
