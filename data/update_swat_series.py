"""Scoped SWAT-series wiki generation from a verified published source snapshot.

No other perk object or aurora/settings data is regenerated.
"""
from pathlib import Path
import json, re, hashlib, html, shutil, argparse

WIKI=Path(__file__).resolve().parents[1]
PROJECT=WIKI.parent/'zedternal-unlimited-main'
SOURCE=PROJECT/'ZedternalTempered'
SCOPE=['SWAT','Scavenger','Taskmaster','Frost','Omen']
CLASSES={k:('ZUTUpgrade_Perk_Base_SWAT' if k=='SWAT' else 'ZTUpgrade_Perk_'+k) for k in SCOPE}
ICON_NAMES={'Scavenger':'SAS','Taskmaster':'GIGN','Frost':'Thor','Omen':'Reinhardt'}
DETAILS={
 'SWAT':('SWAT-UPDATE-KO.md',['적용한 패시브','활성 스킬']),
 'Scavenger':('SAS-REMAKE-KO.md',['패시브와 캡스톤','스킬 10종','판정과 상호작용']),
 'Taskmaster':('GIGN-REMAKE-KO.md',['패시브와 캡스톤','활성 스킬 11종','등록·설정·표시','코드와 검증']),
 'Frost':('ICETHOR-REMAKE-KO.md',['패시브와 캡스톤','활성 스킬','등록·표시·운영 설정']),
 'Omen':('REINHARDT-REMAKE-KO.md',['해금·패시브','철갑 돌진 — 10레벨','푸른 성채 — 20레벨','활성 스킬 9종'])}
ROLES={'SWAT':'방어구와 탄창 용량, SWAT 무기 화력으로 전선을 유지합니다.',
 'Scavenger':'예비 탄약 보급과 재생으로 탄약이 부족해도 전선을 유지하는 전문가입니다.',
 'Taskmaster':'직접 총탄 화력과 모든 무기의 V 밀치기를 결합한 돌파대입니다.',
 'Frost':'즉시 빙결과 순간 서리 폭풍으로 적의 진격을 붙잡습니다.',
 'Omen':'철갑 돌진으로 길을 열고 푸른 성채로 전선을 버티는 중장갑 돌격병입니다.'}
COUNTS={'SWAT':10,'Scavenger':10,'Taskmaster':11,'Frost':8,'Omen':9}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 b=Path(p).read_bytes();return b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig').replace('\r\n','\n')
def sections(text):
 result={};current=None
 for line in text.splitlines():
  line=line.strip()
  if line.startswith('[') and line.endswith(']'): current=line[1:-1];result[current]={}
  elif current and '=' in line and not line.startswith((';','#','//')):
   k,v=line.split('=',1);result[current][k]=v.strip().strip('"').replace('\\"','"')
 return result
def plain(s): return re.sub('<[^>]+>','',s)
def fmt(v,unit):
 if unit=='percent': return ('+' if v>=0 else '')+f'{v*100:g}%'
 if unit=='seconds': return f'{v:g}초'
 return str(v)
def stat(key,label,value,unit='percent',base=0,cap_level=None,cap_bonus=0):
 def val(l):return base+value*l+(cap_bonus if cap_level and l>=cap_level else 0)
 return dict(key=key,label=label,value=value,unit=unit,display=fmt(value,unit),baseValue=base,
             capstoneLevelBonus=cap_level,capstoneBonus=cap_bonus,lv10=val(10),lv20=val(20),
             lv10Display=fmt(val(10),unit),lv20Display=fmt(val(20),unit),scaling=True)
STATS={
 'SWAT':[stat('Armor','최대 방어구',.05),stat('MagSize','모든 무기 탄창 용량',.025),stat('Damage','SWAT 무기 피해',.02)],
 'Scavenger':[stat('SpareAmmo','예비 탄약 용량',.015),stat('ReloadSpeed','재장전 속도',.01),stat('MagSize','최대 장탄량',.01)],
 'Taskmaster':[stat('BulletDamage','직접 총탄 피해',.01),stat('Recoil','반동',-.01),stat('BashDamage','V 밀치기 피해',.10),stat('Movement','이동 속도',.01)],
 'Frost':[stat('FrostChance','서리 확률 (10레벨 캡스톤 포함)',.001,cap_level=10,cap_bonus=.01),stat('FrostDuration','서리 지속시간 (1레벨 1초)',.1,'seconds',base=.9)],
 'Omen':[stat('Health','최대 체력',.03),stat('Armor','최대 방어구',.03),stat('Resistance','피해 저항 (다른 저항과 곱연산)',.015)]}

def inline(s):
 s=html.escape(s)
 s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
 return re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
def markdown(text):
 lines=text.strip().splitlines();result=[];i=0
 while i<len(lines):
  s=lines[i].strip()
  if not s:i+=1;continue
  if s.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[x.strip() for x in lines[i].strip().strip('|').split('|')];i+=1
    if all(re.fullmatch('[: -]+',c) for c in cells):continue
    tag='th' if not rows else 'td';rows.append('<tr>'+''.join('<'+tag+'>'+inline(c)+'</'+tag+'>' for c in cells)+'</tr>')
   result.append('<div class="table-scroll"><table class="stat-table">'+''.join(rows)+'</table></div>');continue
  if s.startswith('- '):
   items=[]
   while i<len(lines) and lines[i].strip().startswith('- '):items.append('<li>'+inline(lines[i].strip()[2:])+'</li>');i+=1
   result.append('<ul>'+''.join(items)+'</ul>');continue
  para=[]
  while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('|','- ')):para.append(lines[i].strip());i+=1
  result.append('<p>'+inline(' '.join(para))+'</p>')
 return ''.join(result)

def code_details(key):
 filename,titles=DETAILS[key];text=read(PROJECT/'Docs'/filename)
 parts=dict((m.group(1),m.group(2)) for m in re.finditer(r'(?m)^## (.+)\n([\s\S]*?)(?=^## |\Z)',text))
 out=[]
 for title in titles:
  body=parts[title]
  if title=='코드와 검증':body=body.split('`Tools/Verify-GIGN.py`')[0]
  out.append({'title':title,'html':markdown(body),'note':'공개 v10.11.21 실행 코드·활성 설정과 대조'})
 out.append({'title':'서버 판정·표시와 검증 범위','html':'<p>전투·탄약·돌진·제어 효과는 서버에서 판정합니다. 필요한 남은 시간과 카운터는 소유 클라이언트에 복제하며 공용 상태 카드로 표시합니다. 상점 전환·사망·퍼크 제거에서 임시 상태를 정리하고 재접속 시 새 플레이어 상태를 사용합니다. 코드·현지화·등록·SDK 텍스처 및 공개 산출물은 대조했습니다. 실제 멀티플레이의 물리·AI·제어 애니메이션·화면·네트워크·중도 접속은 미검증입니다.</p>'})
 if key=='SWAT':out[-1]['html']='<p>SWAT는 별도 10·20레벨 캡스톤이 없습니다. 능력은 기존 서버 퍼크·무기 계산 경로에 적용합니다. 웨이브 종료 방어구 회복은 최대치로 제한됩니다. 실제 멀티플레이의 무기별 조준 속도·상태 이상·사망/중도 접속 화면은 미검증입니다.</p>'
 return out

def roster(key,registry):
 pattern=r'(?m)^SkillUpgrade_Upgrade=\(PerkPath="ZedternalTempered\.'+CLASSES[key]+r'",SkillPath="ZedternalTempered\.([^\"]+)"\)'
 result=re.findall(pattern,registry);assert len(result)==COUNTS[key],(key,result);return result

def apply(data):
 kor=sections(read(SOURCE/'Localization/KOR/ZedternalTempered.kor'))
 registry=read(SOURCE/'KFZedternalReborn_Upgrades.ini');rules=read(SOURCE/'KFZedternalUnlimited.ini')
 old={p['key']:p for p in data['basePerks']+data['advancedPerks']}
 for key in SCOPE:
  p=old[key];classname=CLASSES[key];loc=kor[classname]
  p.update(name=loc['UpgradeName'],role=ROLES[key],summary=ROLES[key],passiveStats=STATS[key],fixedStats=[],
           summaryHtml=None,endgame=None,verdict=None,grade=None,isPatched=False,patchNote=None,
           recentChangeTag='SWAT 시리즈 리메이크 · v10.11.21',testWarning=None,extraSections=code_details(key),
           valueSourceNote='공개 v10.11.21 실행 코드 기준. 서리 확률은 10레벨 캡스톤을 포함하며 서리 지속시간은 1레벨 1초에서 시작합니다.' if key=='Frost' else '공개 v10.11.21 실행 코드 기준. 용량·속도·상태 이상은 기존 공용 상한과 반올림을 따릅니다.',
           verifiedRelease='10.11.21')
  p['strengths']=[];p['weaknesses']=[]
  descriptions=[]
  for name,value in loc.items():
   if not re.fullmatch(r'(?:PerkUpgradeDescription|UpgradeDescription)\d+',name) or not value:continue
   idx=int(re.search(r'\d+$',name).group())-1
   if '%x%' in value:
    amount=({'Frost':{0:'3.0',1:'2.9'},'Omen':{0:'60',1:'60',2:'30.0'}}.get(key,{}))[idx]
    value=value.replace('%x%',amount)
   cap=bool(re.match(r'(?:레벨\s*(?:10|20)|(?:10|20)레벨)',plain(value)))
   descriptions.append({'raw':value,'text':plain(value),'isCapstone':cap})
  expected=0 if key=='SWAT' else 2
  assert sum(d['isCapstone'] for d in descriptions)==expected,(key,descriptions)
  p['descriptions']=descriptions;p['capstoneDescriptions']=[d for d in descriptions if d['isCapstone']]
  p['noCapstoneNote']='별도 10·20레벨 캡스톤은 없습니다.' if key=='SWAT' else None
  skills=[]
  oldskills={s['key']:s for s in p['skills']}
  for cls in roster(key,registry):
   short=cls.split('Skill_',1)[1];sloc=kor[cls];code=read(SOURCE/'Classes'/(cls+'.uc'))
   single=bool(re.search(r'bHasDeluxe\s*=\s*False',code,re.I))
   std=sloc.get('StandardSkillUpgradeDescription',sloc.get('SkillUpgradeDescription1',sloc.get('UpgradeDescription1')))
   deluxe=None if single else sloc.get('DeluxeSkillUpgradeDescription',sloc.get('SkillUpgradeDescription2',sloc.get('UpgradeDescription2')))
   assert std and (single or deluxe),(cls,sloc)
   iconmatch=re.search(r"UpgradeIcon\(0\)=Texture2D'[^']+\.UI_Skill_([^']+)'",code)
   icon='icons/skills/'+(iconmatch.group(1) if iconmatch else short)+'.png'
   assert (WIKI/'docs'/icon).is_file(),(cls,icon)
   skills.append(dict(key=short,name=sloc['UpgradeName'],standardDesc=plain(std),deluxeDesc=plain(deluxe) if deluxe else None,
    standardDescRaw=std,deluxeDescRaw=deluxe,allowsDeluxe=not single,deluxeAvailable=not single,
    rawValues=[],hasKorText=True,note=None,isPatched=False,patchNote=None,textFixed=False,disabled=False,
    disabledNote=None,noData=False,icon=icon))
  p['skills']=skills;p['skillCount']=len(skills)
  if key!='SWAT':
   match=re.search(r'(?m)^PerkUnlockRules=\(PerkName="'+classname+r'",([^\n]+)',rules);assert match
   required=re.findall(r'Req[12]Perk="ZUTUpgrade_Perk_Base_SWAT",Req[12]Level=(\d+)',match.group(1))
   assert len(required)==2 and len(set(required))==1
   level=int(required[0]);p.update(parentPerk='SWAT',unlockLevel=level,unlockRequirements=[{'perk':'SWAT','level':level}],isCombinationUnlocked=False,hasIniConfig=True,isStatic=False)
   p['icon']='icons/'+ICON_NAMES[key].lower()+'.png'
  else:
   p['unlocks']=[{'level':int(re.search(r'Req1Level=(\d+)',re.search(r'(?m)^PerkUnlockRules=\(PerkName="'+CLASSES[k]+r'",([^\n]+)',rules).group(1)).group(1)),'perk':k,'name':kor[CLASSES[k]]['UpgradeName']} for k in SCOPE[1:]]
  assert len(p['capstoneDescriptions'])==expected
 return data

def generate(report_path):
 report_path=Path(report_path);report=json.loads(read(report_path));assert report['status']=='published' and report['publicVerified'] and str(report['workshopId'])=='3809067086'
 snapshot=json.loads(read(report_path.parent/'source-hashes.json'))
 relevant=[r for r in snapshot if str(SOURCE).lower() in r['path'].lower() or 'Unpublished\\BrewedPC' in r['path']]
 for row in relevant:assert sha(row['path']).upper()==row['sha256'].upper(),row['path']+' differs from uploaded snapshot'
 for row in report['files']:assert sha(report_path.parent/'content'/row['path']).upper()==row['sha256'].upper(),row['path']
 source_ini=[]
 ops=Path('D:/KF2server/KFGame/Config/SV_Zedternal_Tempered')
 for p in sorted(SOURCE.glob('*.ini')):
  if p.name.startswith('KFZedternal'):
   read(p);read(ops/p.name);source_ini.append({'name':p.name,'sourceSha256':sha(p),'operatingSha256':sha(ops/p.name),'differs':sha(p)!=sha(ops/p.name)})
 assert len(source_ini)==9
 for p in (SOURCE/'Localization/KOR').glob('*.kor'):sections(read(p))
 path=WIKI/'docs/data/perks.json';before=json.loads(read(path));old=json.loads(json.dumps(before));data=apply(before)
 for group in ['basePerks','advancedPerks']:
  for a,b in zip(old[group],data[group]):
   if a['key'] not in SCOPE:assert a==b,a['key']+' unexpectedly changed'
 assert old['aurora']==data['aurora']
 icons=PROJECT/'Tempered_Build/Icons/SWAT-Wiki-20261011'
 for k,n in ICON_NAMES.items():shutil.copy2(icons/('UI_Perk_'+n+'.png'),WIKI/'docs/icons'/(n.lower()+'.png'))
 for i in range(5):shutil.copy2(icons/('UI_Perk_SWAT_Rank_'+str(i)+'.png'),WIKI/'docs/icons/ranks'/('SWAT-rank-'+str(i)+'.png'))
 prior=old['meta']['release']
 if prior.get('publicationState')=='scoped-published':prior=prior['previousDataRelease']
 data['meta']['release']={'version':'10.11.21','workshopId':'3809067086','workshopUrl':'https://steamcommunity.com/sharedfiles/filedetails/?id=3809067086','publishedUtc':report.get('publishedUtc',report.get('finishedUtc')),'publicationState':'scoped-published','updatedPerks':SCOPE,'updatedPerkNames':[p['name'] for p in data['basePerks']+data['advancedPerks'] if p['key'] in SCOPE],'previousDataRelease':prior,'dataSource':'SWAT 시리즈 5개만 공개 v10.11.21 코드·현지화·SDK 아이콘에 맞춰 검증. 다른 퍼크 자료는 이전 상태를 유지합니다.'}
 data['meta']['totalSkills']=sum(p['skillCount'] for p in data['basePerks']+data['advancedPerks'])
 path.write_bytes((json.dumps(data,ensure_ascii=False,indent=1)+'\n').replace('\n','\r\n').encode('utf-8'))
 manifest={'version':'10.11.21','scope':SCOPE,'report':str(report_path),'sourceHash':json.loads(read(PROJECT/'Tempered-Version.json'))['SourceHash'],'sourceSnapshotSha256':sha(report_path.parent/'source-hashes.json'),'uploadedFiles':report['files'],'sourceIni':source_ini,'scopeOnly':True,'unchangedPerks':[p['key'] for p in old['basePerks']+old['advancedPerks'] if p['key'] not in SCOPE],'outputSha256':sha(path)}
 (WIKI/'data/release-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('SWAT series generated: 5 perks / 48 active skills; unrelated perk objects and aurora unchanged; release hashes verified')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('report');args=parser.parse_args();generate(args.report)
