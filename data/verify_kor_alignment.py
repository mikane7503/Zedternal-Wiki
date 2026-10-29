"""Validate the deployed-source KOR refresh and all linked assets."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=Path(r'C:\Users\yss19\Documents\Projects\zedternal-unlimited-main')
SOURCE=PROJECT/'Ascension_Build/SDKStage/Src/ZedternalAscension'
values=set()
for p in (SOURCE/'Localization/KOR').glob('*'):
 b=p.read_bytes();s=b.decode('utf-16' if b[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8-sig')
 for line in s.splitlines():
  if '=' in line:
   values.add(line.split('=',1)[1].strip().strip('"').replace('\\"','"'))
d=json.loads((ROOT/'docs/data/perks.json').read_text(encoding='utf-8'))
errors=[];skills=0
for base in d['basePerks']:
 if not isinstance(base.get('unlocks'),list):errors.append('Missing unlock list '+base['key'])
 elif any(not any(a['key']==u['perk'] for a in d['advancedPerks']) for u in base['unlocks']):errors.append('Invalid unlock reference '+base['key'])
for group in ['basePerks','advancedPerks']:
 for p in d[group]:
  if not p['descriptions']:errors.append('Empty perk '+p['key'])
  for line in p['descriptions']:
   if line['raw'] not in values:errors.append('KOR perk '+p['key'])
   if '%x' in line.get('displayRaw',''):errors.append('Unresolved display '+p['key'])
  for s in p['skills']:
   skills+=1
   for field in ['standardDescRaw','deluxeDescRaw']:
    if s.get(field) and s[field] not in values:errors.append('KOR skill '+s['className'])
  for item in [p]+p['skills']:
   if not item.get('icon') or not (ROOT/'docs'/item['icon']).is_file():errors.append('Icon '+item.get('className',item['key']))
  if p['skillCount']!=len(p['skills']):errors.append('Skill count '+p['key'])
  if '\ufffd' in json.dumps(p,ensure_ascii=False):errors.append('Encoding '+p['key'])
rep=json.loads((ROOT/'data/ascension-rebuild-report.json').read_text(encoding='utf-8'))
if rep['missingText'] or rep['missingIcons']:errors.append('Incomplete source mapping')
if errors:
 print('\n'.join(errors));sys.exit(1)
print(f"KOR/encoding/icon checks passed: {len(d['basePerks'])+len(d['advancedPerks'])} perks, {skills} skills")
