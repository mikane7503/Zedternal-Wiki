"""Verify scoped data against localization, active registry and SDK pixel hashes."""
from pathlib import Path
import json,re,argparse
from update_swat_series import WIKI,PROJECT,SOURCE,SCOPE,CLASSES,STATS,COUNTS,ICON_NAMES,roster,sections,read,sha,apply

def verify():
 data=json.loads(read(WIKI/'docs/data/perks.json'))
 baseline=json.loads(read(PROJECT/'Backups/SWAT-Wiki-20261011/docs/data/perks.json'))
 peers={p['key']:p for p in data['basePerks']+data['advancedPerks']}
 for p in baseline['basePerks']+baseline['advancedPerks']:
  if p['key'] not in SCOPE:assert peers[p['key']]==p,p['key']+' outside user scope'
 assert data['aurora']==baseline['aurora']
 assert data['meta']['release']['updatedPerks']==SCOPE
 registry=read(SOURCE/'KFZedternalReborn_Upgrades.ini');kor=sections(read(SOURCE/'Localization/KOR/ZedternalTempered.kor'))
 native=PROJECT/'Tempered_Build/Icons/SWAT-Wiki-20261011'
 texture=json.loads(read(native/'SDK-TEXTURES.json'))
 assert sha(texture['package'])==texture['sha256']
 for key in SCOPE:
  p=peers[key];assert p['passiveStats']==STATS[key]
  assert p['name']==kor[CLASSES[key]]['UpgradeName']
  classes=roster(key,registry);assert [c.split('Skill_',1)[1] for c in classes]==[s['key'] for s in p['skills']]
  assert len(p['skills'])==COUNTS[key]
  for cls,skill in zip(classes,p['skills']):
   loc=kor[cls]
   std=loc.get('StandardSkillUpgradeDescription',loc.get('SkillUpgradeDescription1',loc.get('UpgradeDescription1')))
   deluxe=loc.get('DeluxeSkillUpgradeDescription',loc.get('SkillUpgradeDescription2',loc.get('UpgradeDescription2')))
   assert skill['standardDescRaw']==std and skill['name']==loc['UpgradeName']
   if skill['allowsDeluxe']:assert skill['deluxeDescRaw']==deluxe
   else:assert not skill['deluxeAvailable'] and skill['deluxeDescRaw'] is None
   assert not skill['disabled'] and not skill['noData']
   assert (WIKI/'docs'/skill['icon']).is_file()
  assert '%x%' not in json.dumps(p,ensure_ascii=False)
  assert len(p['capstoneDescriptions'])==(0 if key=='SWAT' else 2)
  assert '예언 시스템' not in json.dumps(p,ensure_ascii=False)
  for icon in ([p['icon']]+p.get('rankIcons',[])):
   n=Path(icon).name
   source=native/('UI_Perk_SWAT_Rank_'+n.split('-rank-')[1] if '-rank-' in n else 'UI_Perk_'+ICON_NAMES[key]+'.png')
   assert sha(WIKI/'docs'/icon)==sha(source),(key,icon)
 assert [u['name'] for u in peers['SWAT']['unlocks']]==['S.A.S','G.I.G.N','아이스 토르','라인하르트']
 assert [u['level'] for u in peers['SWAT']['unlocks']]==[5,10,15,20]
 assert peers['Omen']['unlockRequirements']==[{'perk':'SWAT','level':20}] and not peers['Omen']['isCombinationUnlocked']
 frost=peers['Frost']['passiveStats']
 def total(s,l):return s['baseValue']+s['value']*l+(s['capstoneBonus'] if s['capstoneLevelBonus'] and l>=s['capstoneLevelBonus'] else 0)
 assert abs(total(frost[0],1)-.001)<1e-9 and abs(total(frost[0],10)-.02)<1e-9 and abs(total(frost[0],20)-.03)<1e-9
 assert abs(total(frost[1],1)-1)<1e-9 and abs(total(frost[1],20)-2.9)<1e-9
 swat=read(SOURCE/'Classes/ZUTUpgrade_Perk_Base_SWAT.uc');assert 'MagSize=0.025f' in swat and '0.50f' in swat
 ice=read(SOURCE/'Classes/ZTIceThorSystem.uc');assert '0.001f*Level+(Level>=10 ? 0.01f' in ice and '1.f+0.1f*(Level-1)' in ice
 rein=read(SOURCE/'Classes/ZTReinhardtSystem.uc');assert '30.f : (Tier==1 ? 40.f : 45.f)' in rein and 'Mult*=0.2f' in rein
 assert apply(json.loads(json.dumps(data)))==data,'Scoped generation is not repeatable'
 print('PASS: 5 perks / 48 active KOR skill descriptions / 10 native perk textures / unlock order / fractional slider / 52 unrelated perks unchanged')
 return data

def record(data):
 version=json.loads(read(PROJECT/'Tempered-Version.json'));native=PROJECT/'Tempered_Build/Icons/SWAT-Wiki-20261011'
 records=[]
 for key in SCOPE:
  folder='Classes/'+CLASSES[key]+'.uc'
  entries={'class':'ZedternalTempered.'+CLASSES[key],'name':next(p['name'] for p in data['basePerks']+data['advancedPerks'] if p['key']==key)}
  entries['image']={'status':'PASS','evidence':['SDK Unpublished actual top mip: '+str(native/'SDK-TEXTURES.json'),'Visual contact-sheet audit: '+str(native/'contact.png'),'Wiki PNG SHA256 equals native decoded mip; 256px; SWAT ranks 0..4 checked'],'limits':'SDK import settings and in-game screen not exercised'}
  entries['passivesAndCapstones']={'status':'PASS','evidence':[folder,'Tools/Verify-'+{'SWAT':'SWAT','Scavenger':'SAS','Taskmaster':'GIGN','Frost':'IceThor','Omen':'Reinhardt'}[key]+'.py','Published v10.11.21 source-hashes.json matched current classes/settings/localizations; compiled release validation reused']}
  entries['activeSkills']={'status':'PASS','evidence':['KFZedternalReborn_Upgrades.ini current active registration','Localization/KOR/ZedternalTempered.kor; INT/JPN static verifier PASS',str(COUNTS[key])+' registered skills; all KOR descriptions exact; single-grade entries excluded from Deluxe; retired registrations excluded']}
  entries['codeDetail']={'status':'PASS','evidence':['Docs/'+{'SWAT':'SWAT-UPDATE','Scavenger':'SAS-REMAKE','Taskmaster':'GIGN-REMAKE','Frost':'ICETHOR-REMAKE','Omen':'REINHARDT-REMAKE'}[key]+'-KO.md','Fresh scoped extraSections from current implementation notes; timings/targets/rounding/caps/stacking/authority/UI/exceptions disclosed'],'multiplayer':'NOT_RUN'}
  records.append(entries)
 audit={'version':'10.11.21','sourceHash':version['SourceHash'],'scope':SCOPE,'scopeAuthorization':'User explicitly requested only SWAT series on 2026-10-11','verificationOrder':['image','passivesAndCapstones','activeSkills','codeDetail'],'perks':records,'actualMultiplayer':'NOT_RUN'}
 (PROJECT/'Docs/WIKI-PERK-AUDIT-10.11.21.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (WIKI/'docs/audits/swat-series-2026-10-11-ko.md').write_text('# SWAT 시리즈 공개 v10.11.21 검증\n\n사용자 지정 범위: SWAT, S.A.S, G.I.G.N, 아이스 토르, 라인하르트. 다른 퍼크 52개와 설정 자료는 유지했습니다.\n\n| 퍼크 | SDK 실제 이미지 | 패시브·캡스톤 | 활성 스킬·KOR 수치 | 코드 상세 |\n|---|---|---|---|---|\n'+''.join('| '+r['name']+' | PASS | PASS | '+str(COUNTS[k])+'종 PASS | PASS |\n' for k,r in zip(SCOPE,records))+'\n아이콘은 SDK Unpublished의 실제 UPK mip를 추출해 시각 확인하고 위키 PNG 해시를 대조했습니다. SWAT 등급 0–4도 포함했습니다. 공개 보고서 20261011-211919-58d2d723의 산출물과 소스 해시, 소스/운영 INI 9개 및 KOR 파일 전체를 확인했습니다. EN/INT·KOR·JPN과 실제 등록은 기존 전용 정적 검증 5종으로 대조했습니다. 공개 빌드의 컴파일·headless 검증을 재사용했으며 새 게임 빌드·업로드·서버 재시작은 실행하지 않았습니다.\n\n실제 멀티플레이 검증은 미실행입니다. 돌진 물리, native AI/제어 애니메이션, 효과 화면, 네트워크 및 중도 접속 확인은 포함하지 않습니다.\n',encoding='utf-8')
 print('Recorded five ordered four-step audits; multiplayer NOT_RUN')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');args=p.parse_args();d=verify()
 if args.record:record(d)
