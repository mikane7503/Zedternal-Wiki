import re

def value(cls,k,line,index,level,field,src,indexed=False):
 def scalar(name):return float(re.sub(r'[fF]$','',field(cls,name,'0')))
 if indexed:
  if k in ('Jagdkommando','DeltaForce'):return level*(.5 if index==2 else 1)
  if k=='NavySEALs':return level
  if k=='Michael':return level*(2 if index==0 else 1)
  if k=='Gabriel':return min(10,.5*level)
  if k=='Archangel':return [.5*level,scalar('FieldMedicine')*100*level,2*level][index]
  if k=='Ophanim':return 90 if line==1 else 60
  if k=='Fraulein':return level*({(0,0):3,(0,1):4,(1,0):5,(1,1):2}[(line,index)])
  if k=='Detonator' and line==3:return [max(0,50-level),400+30*level,300+5*level][index]
  fields={'Riot':['MeleeDamagePerLevel','DamageResistancePerLevel','AttackSpeedPerLevel'],'Diablo':['HeavyDamagePerLevel','LargeMeleeDamagePerLevel']}
  if k in fields:return scalar(fields[k][index])*100*level
  if k=='Metronome':return scalar({(1,0):'AssaultDamage',(1,1):'AssaultPenetration',(2,0):'TempoReload',(2,1):'TempoRateOfFire',(3,0):'MomentumSpeed',(3,1):'MomentumWeaponSwitch',(4,0):'BastionDamage'}[(line,index)])*100*level
  if k=='JohnWick':
   if line==0:return level
   if line==1:return [.5,.5,.25,.2][index]*level
   if line==2:return [1,2][index]*level
  return value(cls,k,line+index,0,level,field,src)
 if k=='Armageddon':return [2,.5][line]*level
 if k=='Omen':return [3,3,1.5][line]*level
 if k=='Frost':return (level+(10 if level>=10 else 0))/10 if line==0 else (9+level)/10 if level>0 else 0
 if k=='SlotMachine':return round(100-40*(max(1,min(level,20))-1)/19)
 special={('Cinder',0):1.5,('Hydra',0):1.5,('Medusa',0):1.5,('Scavenger',0):1.5,('SpecialAgent',0):1.5,('Headhunter',2):.5,('Pyrokinetic',1):1.25,('Venomancer',1):1.25,('Wendigo',1):.75,('Wendigo',2):1.5}
 if (k,line) in special:return special[k,line]*level
 names={'MissingNO':['SpareAmmoPerLevel','MagSizePerLevel','GlitchProcChancePerLevel'],'Reaper':['CritChance','HeadshotDamage','MovementSpeed'],'TimeTraveler':['Damage','RateOfFire']}
 if k in names:return scalar(names[k][line])*100*level
 if k=='JekyllHyde':return scalar('Jekyll_MovePerRank' if line==0 else 'Jekyll_ReloadPerRank')*100*level
 if k=='Predator':return (0.001+(max(1,min(level,20))-1)*0.009/19+(0.005 if level>=10 else 0)+(0.005 if level>=20 else 0))*100
 body=field(cls,f'PerkBonus({line})',None)
 if body:
  vals={a.lower():float(b) for a,b in re.findall(r'(\w+)\s*=\s*([+-]?[\d.]+)',body)}
  n=vals.get('basevalue',0)+vals.get('incvalue',0)*level
  return min(n,vals['maxvalue']) if vals.get('maxvalue',-1)>=0 else n
 raise ValueError(f'Unresolved live bonus: {cls}/{line}/{index}')
def render(cls,k,line,raw,level,field,src):
 def fmt(n):return f'{n:g}'
 def indexed(m):return fmt(value(cls,k,line,int(m[2])-1,level,field,src,True))
 s=re.sub(r'%x(\d+)_(\d+)%',indexed,raw)
 if '%x' in s:s=s.replace('%x%',fmt(value(cls,k,line,0,level,field,src))).replace('%x',fmt(value(cls,k,line,0,level,field,src)))
 return s
