"""Rebuild wiki from a verified deployed Ascension source snapshot, never legacy INIs."""
import json,re,os,sys,shutil,hashlib
from pathlib import Path
from PIL import Image
from ascension_values import render
ROOT=Path(__file__).resolve().parents[1]
PROJECT=Path(r'C:\Users\yss19\Documents\Projects\zedternal-unlimited-main')
SOURCE=PROJECT/'Ascension_Build/SDKStage/Src/ZedternalAscension'
CLASSES=SOURCE/'Classes'
OPS=Path('D:/KF2server/KFGame/Config/SV_Zedternal_Ascension_Workshop')
OUT=ROOT/'docs/data/perks.json'
def read(p):
 b=p.read_bytes();return b.decode('utf-16' if b[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8-sig')
def loc(p):
 result={};current={}
 for line in read(p).splitlines():
  line=line.strip()
  if line.startswith('[') and line.endswith(']'):current={};result[line[1:-1].lower()]=current
  elif '=' in line and not line.startswith((';','//')):
   k,v=line.split('=',1);v=v.strip().strip('"').replace('\\"','"');current[k.lower()]=v
 return result
ALL={}
for folder in ['INT','KOR','JPN']:
 for p in (SOURCE/'Localization'/folder).glob('*'):
  ALL[(folder,p.name)]=loc(p)
KOR={}
for (lang,_),sections in ALL.items():
 if lang=='KOR':KOR.update(sections)
SRC={p.stem:read(p) for p in CLASSES.glob('*.uc')}
REBORN=PROJECT/'Ascension_Build/SDKStage/Src/ZedternalReborn/Classes'
SRC.update({p.stem:read(p) for p in REBORN.glob('*.uc')})
def field(cls,key,default=None,seen=None):
 seen=set() if seen is None else seen
 if cls in seen:return default
 seen.add(cls);s=SRC.get(cls,'');m=re.search(r'^\s*'+re.escape(key)+r'\s*=\s*(.+?)\s*$',s,re.M|re.I)
 if m:return m[1].strip().rstrip(';').strip('"')
 parent=re.search(r'class\s+\w+\s+extends\s+(\w+)',s,re.I)
 return field(parent[1],key,default,seen) if parent else default
def section(cls):return KOR.get(field(cls,'LocSection',cls).lower(),KOR.get(cls.lower(),{}))
def key(cls):return re.sub(r'^(?:ZT|ZUT|WM)Upgrade_Perk_(?:Base_)?','',cls)
def text(x):return re.sub('<[^>]+>','',x).replace('\\n',' ')
def descs(cls):
 data=section(cls)
 return [dict(raw=v,text=text(v),isCapstone=('캡스톤' in v)) for k,v in sorted(data.items(),key=lambda kv:int(re.search(r'\d+',kv[0])[0]) if re.search(r'\d+',kv[0]) else -1) if re.match(r'(?:perk)?upgradedescription\d+$',k)]
old=json.loads(OUT.read_text(encoding='utf-8-sig'));oldmap={p['key']:p for kind in ['basePerks','advancedPerks'] for p in old[kind]}
# Build a texture-name index from existing exports and original icon import assets.
images={}
for base in [ROOT/'docs/icons',PROJECT/'Ascension_Build/Icons']:
 for p in base.rglob('*'):
  if p.suffix.lower() in ('.png','.tga'):
   images.setdefault(p.stem.lower(),p)
for p in (PROJECT/'Ascension_Build/Icons/WikiRefresh-20261029/PackageExport').glob('*.png'):
 images[p.stem.lower()]=p
missing=[]
def icon(cls,perk=False,oldicon=None):
 dynamic=field(cls,'IconName','')
 value=("Texture2D'ZedternalAscension_Resources.Skills."+dynamic+"'") if dynamic else field(cls,'UpgradeIcon(0)','')
 m=re.search(r"Texture2D'([^']+)'",value,re.I)
 if m:
  name=m[1].split('.')[-1];candidates=[name,name.replace('UI_Skill_','').replace('ZTUpgrade_Skill_',''),name.replace('UI_Perk_','')]
  for name in candidates:
   p=images.get(name.lower())
   if p:
    dest=ROOT/'docs/icons/ascension'/f'{cls}.png';dest.parent.mkdir(parents=True,exist_ok=True)
    Image.open(p).convert('RGBA').save(dest)
    return str(dest.relative_to(ROOT/'docs')).replace('\\','/')
 if oldicon and (ROOT/'docs'/oldicon).exists():return oldicon
 missing.append((cls,value));return None
ini={p.name:read(p) for p in OPS.glob('*.ini') if p.name in ['KFZedternalAscension.ini','KFZedternalAscension_Difficulty.ini','KFZedternalReborn_Game.ini','KFZedternalReborn_Events.ini','KFZedternalReborn_Upgrades.ini','KFZedternalReborn_Weapons.ini','KFZedternalAscension_Local.ini']}
upgrades=ini['KFZedternalReborn_Upgrades.ini'];main=ini['KFZedternalAscension.ini']
active={m[1].split('.')[-1]:m[2].lower()=='true' for m in re.finditer(r'PerkUpgrade_Upgrade=\(PerkPath="([^"]+)",bIsStatic=(True|False)',upgrades,re.I)}
systems='\n'.join(v for k,v in SRC.items() if k.endswith(('System','Remake','Catalog')))
for oldcls,newcls in re.findall(r'MigratePerkName\("(\w+)"\s*,\s*"(\w+)"',systems):
 if oldcls in active:active[newcls]=active.pop(oldcls)
active.pop('ZTUpgrade_Perk_Daredevil',None)
for cls,static in re.findall(r'EnsurePerk\("[^".]+\.(\w+)"\s*,\s*(true|false)',systems,re.I):active[cls]=static.lower()=='true'
for cls in ['ZTUpgrade_Perk_Override','ZTUpgrade_Perk_Armageddon','ZTUpgrade_Perk_Gilgamesh','ZTUpgrade_Perk_Gabriel','ZTUpgrade_Perk_Michael','ZTUpgrade_Perk_Ophanim']:active.setdefault(cls,False)
retired={'Agony','Parasite','Hivemind','Symbiote','Wishmaster','Domain','Possessor','Speedster','Fastball','Goalkeeper','Gambler','Tycoon'}
active={c:v for c,v in active.items() if c in SRC and key(c) not in retired and field(c,'bContentReady','true').lower()!='false'}
maxlevels={key(c.split('.')[-1]):int(n) for c,n in re.findall(r'PerkMaxLevels=\(PerkPath="([^"]+)",MaxLevel=(\d+)',main)}
rules={}
for line in main.splitlines():
 if not line.startswith('PerkUnlockRules='):continue
 m=re.search(r'PerkName="(\w+)"',line)
 if not m:continue
 reqs=[]
 for index in range(1,4):
  pm=re.search(r'Req'+str(index)+r'Perk="(\w+)"',line);lm=re.search(r'Req'+str(index)+r'Level=(\d+)',line)
  if pm and lm:
   r={'perk':key(pm[1]),'level':int(lm[1])}
   if r not in reqs:reqs.append(r)
 if reqs:rules[key(m[1])]=reqs
for c,parent,level in re.findall(r'AddOrUpdateSingleBaseUnlock\("(\w+)"\s*,\s*"(\w+)"\s*,\s*(\d+)\)',SRC['ZTConfig_PerkUnlockRules']):rules[key(c)]=[{'perk':key(parent),'level':int(level)}]
rosters={c:[] for c in active}
for p,s in re.findall(r'Skills\(\d+\)=\(PerkPath="[^"]*\.(\w+)",SkillPath="[^"]*\.(\w+)"',SRC['ZASkillCatalog']):
 if p in rosters:rosters[p].append(s)
# Medicine runtime replaces its catalog with the ordered Group mapping.
med={0:'ZUTUpgrade_Perk_Base_FieldMedic',1:'ZTUpgrade_Perk_Archangel',2:'ZTUpgrade_Perk_Gabriel',3:'ZTUpgrade_Perk_Michael'}
for c in med.values():rosters[c]=[]
for c in re.findall(r"Skills\(\d+\)=class'(\w+)'",SRC['ZTMedicRemake']):
 g=int(field(c,'Group','0'));rosters[med[g]].append(c)
for p,s in re.findall(r'AddSkill\("(\w+)"\s*,\s*"[^".]+\.(\w+)"\)',SRC['ZTMedicRemake']):
 if p in rosters:rosters[p].append(s)
# Explicit runtime system rosters supplement the canonical compiled catalog.
for system,source in SRC.items():
 if not system.endswith(('System','Remake','Catalog')):continue
 for sc in re.findall(r"(?:Skills|VanguardSkills|JohnWickSkills)\(\d+\)\s*=\s*class'(\w+)'",source):
  owner=next((c for c in active if sc.startswith('ZTUpgrade_Skill_'+key(c)+'_')),None)
  if sc.startswith('ZTUpgrade_Skill_Overclock_Module_'):owner='ZTUpgrade_Perk_Override'
  if owner in rosters:rosters[owner].append(sc)
retiredskills=set(re.findall(r'ZTUpgrade_Skill_(\w+)',SRC['ZTRetiredSkillFilter'].split('static function RemoveFromCatalog')[0]))
for owner in rosters:
 rosters[owner]=[c for c in rosters[owner] if c.removeprefix('ZTUpgrade_Skill_') not in retiredskills]
missingtext=[]
def skill(c,owner):
 sec=section(c);short=re.sub(r'^(?:ZT|ZUT|WM)Upgrade_Skill_','',c);short=short.removeprefix(owner+'_')
 oldskill=next((s for s in oldmap.get(owner,{}).get('skills',[]) if s['key']==short),{})
 std=sec.get('standardskillupgradedescription',sec.get('skillupgradedescription1',sec.get('skillupgradedescription','')))
 deluxe=sec.get('deluxeskillupgradedescription',sec.get('skillupgradedescription2',''))
 if owner=='Override' or short.lower()=='rackemup' or field(c,'bHasDeluxe','true').lower()=='false' or field(c,'bAllowDeluxe','true').lower()=='false':deluxe=''
 if not std:missingtext.append(c)
 return dict(key=short,className=c,name=sec.get('upgradename',field(c,'UpgradeName',short)),standardDescRaw=std,standardDesc=text(std),deluxeDescRaw=deluxe or None,deluxeDesc=text(deluxe) if deluxe else None,allowsDeluxe=bool(deluxe),rawValues=[],hasKorText=bool(std),note=None,disabled=False,icon=icon(c,oldicon=oldskill.get('icon')))
data=dict(basePerks=[],advancedPerks=[],aurora=old.get('aurora',{}),meta={})
for c,static in active.items():
 k=key(c);prev=oldmap.get(k,{});sec=section(c);ds=descs(c)
 if c.startswith('ZUTUpgrade_Perk_Base_'):
  for candidate in ['ZTWrapper_Perk_'+k,'ZUTUpgrade_Perk_Base_'+k]:
   if descs(candidate):ds=descs(candidate);break
 if not ds:missingtext.append(c)
 for index,d in enumerate(ds):
  d['displayRaw']=render(c,k,index,d['raw'],maxlevels.get(k,20),field,SRC)
 req=rules.get(k,prev.get('unlockRequirements',[]));summary=KOR.get('ztui_upgmenu',{}).get('perksummary_'+k.lower(),prev.get('summary',''))
 skills=[skill(sc,k) for sc in dict.fromkeys(rosters.get(c,[]))]
 p=dict(key=k,name=sec.get('upgradename',field(c,'UpgradeName',k)),className=c,parentPerk=req[0]['perk'] if req else prev.get('parentPerk'),unlockLevel=req[0]['level'] if len(req)==1 else None,unlockRequirements=req,isCombinationUnlocked=len(req)>1,isStatic=static,maxLevel=maxlevels.get(k,20),summary=summary,role=summary,descriptions=ds,overviewDescriptions=[d for d in ds if not d['isCapstone']],passiveDescriptions=[d for d in ds if not d['isCapstone']],capstoneDescriptions=[d for d in ds if d['isCapstone']],passiveStats=[],fixedStats=[],skills=skills,skillCount=len(skills),icon=icon(c,True,prev.get('icon')),rankIcons=prev.get('rankIcons',[]),extraSections=[],noCapstoneNote='캡스톤 없음' if not any(d['isCapstone'] for d in ds) else None)
 data['basePerks' if c.startswith('ZUTUpgrade_Perk_Base_') else 'advancedPerks'].append(p)
for group in ['basePerks','advancedPerks']:data[group].sort(key=lambda p:(p.get('parentPerk') or '',p.get('unlockLevel') or 0,p['key']))
data['meta']=dict(basePerkCount=len(data['basePerks']),advancedPerkCount=len(data['advancedPerks']),totalSkills=sum(p['skillCount'] for group in ['basePerks','advancedPerks'] for p in data[group]),release=dict(version='10.28.4',workshopId='3826086053',workshopUrl='https://steamcommunity.com/sharedfiles/filedetails/?id=3826086053',dataSource='운영 1번 v10.28.4 배포본·동일 빌드 SDK 소스·한국어 현지화',publicationState='published'))
# Only gameplay configuration is projected; never publish ranks/passwords.
game=ini['KFZedternalReborn_Game.ini']
fixed=re.findall(r'AddFixedEntry\("([^"]+)",\s*([\d.]+)f?\)',SRC['ZTConfig_FixedDamageGiven'])
weapon=re.findall(r'^Player_DamageGiven=\(DamageType="([^"]+)",Multiplier=([\d.]+)',game,re.M)
taken=re.findall(r'^Player_DamageTaken=\(DamageType="([^"]+)",Multiplier=([\d.]+)',game,re.M)
app=(ROOT/'docs/app.js').read_text(encoding='utf-8')
oldgame=read(ROOT/'KFZedternalReborn_Game.ini')
oldgiven=re.findall(r'^Player_DamageGiven=\(DamageType="([^"]+)"',oldgame,re.M)
oldlabels=re.findall(r'\{ label: "([^"]+)", (?:real|value):',app.split('const PATCH_NOTES')[0])
# Label identity must follow damage type, never current INI row positions.
labels={}
if len(oldlabels)>=len(oldgiven)+7:
 labels.update(dict(zip(oldgiven,oldlabels[:10]+oldlabels[17:])))
fixedlabels=['화염 피해','지면 화염 피해','네이팜 피해','폭발 피해','폭발 파편 피해','메딕 수류탄(독성) 피해','베기 피해','관통 피해','둔기 피해','샷건 피해']
for (t,_),label in zip(fixed,fixedlabels):labels[t]=label
data['aurora']['generalRows']=[dict(label=labels[t],real=float(v)) for t,v in fixed]
data['aurora']['weaponRows']=[dict(label=labels.get(t,t.split('.')[-1]),value=float(v)) for t,v in weapon]
takenlabels=['허스크 자폭 피해','플레쉬파운드 킹 가슴빔 피해','한스 유탄 피해','가부장 미사일 피해','여장부 플라즈마포 피해','허스크 화염방사기 피해']
data['aurora']['takenRows']=[dict(label=l,real=float(v)) for l,(t,v) in zip(takenlabels,taken)]
melee=re.search(r'^Player_DamageTakenMultiplierWhileHoldingMelee=.*?HOE=([\d.]+)',game,re.M)
if melee:data['aurora']['takenRows'].append(dict(label='근접무기 소지 중 전체 피해',real=float(melee[1])))
data['aurora']['damageGiven']=[float(v) for _,v in fixed+weapon]
data['aurora']['damageTaken']=[float(v) for _,v in taken]
OUT.write_text(json.dumps(data,ensure_ascii=False,indent=1),encoding='utf-8')
(ROOT/'data/ascension-rebuild-report.json').write_text(json.dumps(dict(missingIcons=missing,missingText=missingtext,counts=data['meta']),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(counts=data['meta'],missingIcons=len(missing),missingText=missingtext),ensure_ascii=True))
