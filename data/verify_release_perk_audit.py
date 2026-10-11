"""Enforce the project's mandatory four-step audit before publishing wiki data."""
from pathlib import Path
import json,re,sys
root=Path('C:/Users/yss19/Documents/Projects/zedternal-unlimited-main')
version=sys.argv[1]
requested_scope=sys.argv[2].split(',') if len(sys.argv)>2 else None
audit_path=root/'Docs'/('WIKI-PERK-AUDIT-'+version+'.json')
if not audit_path.is_file():
 raise SystemExit('Wiki publication withheld: mandatory image/passives/active-skills/code-detail audit is missing for v'+version+'. Expected '+str(audit_path))
audit=json.loads(audit_path.read_text(encoding='utf-8-sig'))
build=json.loads((root/'Tempered-Version.json').read_text(encoding='utf-8-sig'))
assert audit.get('version')==version and audit.get('sourceHash')==build['SourceHash'],'Wiki audit belongs to different code'
raw=(root/'ZedternalTempered/KFZedternalReborn_Upgrades.ini').read_bytes()
text=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
active=set(re.findall(r'(?m)^PerkUpgrade_Upgrade=\(PerkPath="([^"]+)"',text))
records={p['class']:p for p in audit.get('perks',[])}
expected=active
if requested_scope:
 assert set(requested_scope)==set(audit.get('scope',[])),'Requested scope differs from audited scope'
 expected={'ZedternalTempered.'+('ZUTUpgrade_Perk_Base_SWAT' if k=='SWAT' else 'ZTUpgrade_Perk_'+k) for k in requested_scope}
 assert expected<=active,'Scoped audit contains inactive perks'
assert set(records)==expected,'Wiki audit does not cover requested active perks'
for name in expected:
 for step in ['image','passivesAndCapstones','activeSkills','codeDetail']:
  row=records[name].get(step,{})
  assert row.get('status')=='PASS' and row.get('evidence'),name+' '+step+' unverified'
print('Mandatory four-step wiki audit passed for v'+version+'; perks='+str(len(expected)))
