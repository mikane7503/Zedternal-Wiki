"""Repair progression presentation using compiled-source description getters."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
namespace={'__file__':str(ROOT/'data/rebuild_ascension.py')}
exec((ROOT/'data/rebuild_ascension.py').read_text(encoding='utf-8-sig').split('old=json.loads')[0],namespace)
render,field,SRC=map(namespace.get,['render','field','SRC'])
path=ROOT/'docs/data/perks.json'
d=json.loads(path.read_text(encoding='utf-8'))
if not any(p['key']=='WaveGambler' for p in d['advancedPerks']):
 c='ZTUpgrade_Perk_WaveGambler';sec=namespace['section'](c)
 d['advancedPerks'].append(dict(key='WaveGambler',name=sec['upgradename'],className=c,parentPerk='Capitalist',unlockLevel=5,unlockRequirements=[dict(perk='Capitalist',level=5)],isCombinationUnlocked=False,isStatic=False,maxLevel=20,summary=namespace['KOR'].get('ztui_upgmenu',{}).get('perksummary_wavegambler',''),descriptions=namespace['descs'](c),passiveStats=[],fixedStats=[],skills=[],skillCount=0,icon='icons/wavegambler.png',rankIcons=[],extraSections=[]))
base_fields={
 'Berserker':[('최대 체력','HealthFlat',1,'HP'),('근접 공격·연사 속도','AttackSpeed',100,'%'),('버서커 무기 피해','Damage',100,'%')],
 'Commando':[('ZED 타임 연장 횟수',None,1,'회'),('재장전 속도','ReloadRate',100,'%'),('코만도 무기 피해','Damage',100,'%')],
 'Demolitionist':[('수류탄 피해','GrenadeDamage',100,'%'),('데몰리셔니스트 무기 피해','Damage',100,'%')],
 'FieldMedic':[('최대 체력','Health',1,'HP'),('주사기·다트 충전 속도','HealRate',100,'%'),('모든 무기 피해','Damage',100,'%')],
 'Firebug':[('화염·폭발·독·음파 저항','Defense',100,'%'),('파이어버그 무기 피해','Damage',100,'%')],
 'Gunslinger':[('이동 속도','MoveSpeed',100,'%'),('헤드샷 피해','HeadshotDamage',100,'%'),('건슬링거 무기 피해','Damage',100,'%')],
 'Sharpshooter':[('반동 감소','Recoil',100,'%'),('헤드샷 피해','DamageHead',100,'%'),('샤프슈터 무기 피해','Damage',100,'%')],
 'SWAT':[('최대 방어구','Armor',100,'%'),('탄창 용량','MagSize',100,'%'),('SWAT 무기 피해','Damage',100,'%')],
 'Support':[('비틀거림·넉다운 위력','StoppingPower',100,'%'),('관통력','Penetration',100,'%'),('서포트 무기 피해','Damage',100,'%')],
 'Survivalist':[('휴대 중량','WeightPerLevel',1,''),('예비 탄약','SpareAmmo',100,'%'),('모든 무기 피해','Damage',100,'%')]
}
for group in ['basePerks','advancedPerks']:
 for p in d[group]:
  for i,line in enumerate(p['descriptions']):
   visible=re.sub('<[^>]+>','',line['raw']).strip()
   line['isCapstone']=bool(re.match(r'\[(?:10|20)레벨\s*캡스톤',visible) or re.match(r'(?:레벨\s*(?:10|20)\s*:|(?:10|20)레벨(?:에서|부터|\s*[-—:]))',visible))
   line.pop('levelValues',None)
   if '%x' in line['raw'] and not line['isCapstone']:
    line['levelValues']=[render(p['className'],p['key'],i,line['raw'],lv,field,SRC) for lv in range(1,p['maxLevel']+1)]
  p['passiveDescriptions']=[x for x in p['descriptions'] if not x['isCapstone']]
  p['capstoneDescriptions']=[x for x in p['descriptions'] if x['isCapstone']]
  p['noCapstoneNote']=None if p['capstoneDescriptions'] else '별도 캡스톤 효과가 없습니다.'
  p['overviewDescriptions']=p['passiveDescriptions']
  if p['key'] in base_fields:
   p['passiveStats']=[]
   for label,factor,scale,unit in base_fields[p['key']]:
    v=float(field('ZTWrapper_Perk_'+p['key'],'Cfg_'+factor,'0'))*scale if factor else 0
    vals=[1+min(lv//2,5) if factor is None else v*lv for lv in range(1,p['maxLevel']+1)]
    p['passiveStats'].append(dict(label=label,key=factor or 'ZedTimeResets',value=v,baseValue=0,unit=unit,display=f'+{v:g}{unit}' if factor else '2레벨마다 +1회 (최대 6회)',levelValues=vals))
  if p['key']=='Artificer':
   for line in list(p['passiveDescriptions']):
    if re.search(r'(?:<font[^>]*>)?10레벨(?:</font>)?부터는',line['raw']):
     match=re.search(r'(?:<font[^>]*>)?10레벨(?:</font>)?부터는',line['raw']);left=line['raw'][:match.start()];right=line['raw'][match.end():]
     p['passiveDescriptions']=[dict(line,raw=left,displayRaw=left) if x is line else x for x in p['passiveDescriptions']]
     p['capstoneDescriptions'].insert(0,dict(raw='10레벨부터는'+right,displayRaw='10레벨부터는'+right,isCapstone=True))
  p['noCapstoneNote']=None if p['capstoneDescriptions'] else '별도 캡스톤 효과가 없습니다.'
  p['role']=p.get('role') or p.get('summary','')
d['meta']['advancedPerkCount']=len(d['advancedPerks'])
path.write_text(json.dumps(d,ensure_ascii=False,indent=1),encoding='utf-8')
print('Progression descriptions repaired')
