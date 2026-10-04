class ZUTUpgrade_Perk_Base_Gunslinger extends ZTUpgrade_Perk;

var float Damage, MoveSpeed, HeadshotDamage;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_Gunslinger') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_Gunslinger'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
	if (HitZoneIdx == HZI_HEAD)
		InDamage += Round(float(DefaultDamage) * default.HeadshotDamage * upgLevel);
}

static simulated function ModifySpeedPassive(out float speedFactor, int upgLevel)
{
	speedFactor += default.MoveSpeed * upgLevel;
}

defaultproperties
{
	Damage=0.02f
	MoveSpeed=0.015f
	HeadshotDamage=0.02f
	UpgradeName="Gunslinger"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">movement speed</font> <font color=\"#77D914\">+1.5%</font>."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">headshot damage with all weapons</font> <font color=\"#77D914\">+2%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">Gunslinger weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=2,maxValue=-1)
	PerkBonus(1)=(baseValue=0,incValue=2,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Gunslinger'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_Gunslinger"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_Gunslinger"
}
