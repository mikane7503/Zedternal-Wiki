class ZUTUpgrade_Perk_Base_SWAT extends ZTUpgrade_Perk;

var float Armor, Damage, MagSize;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_Swat') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_Swat'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
}

static function ModifyArmor(out int MaxArmor, int DefaultArmor, int upgLevel)
{
	MaxArmor += Round(float(DefaultArmor) * FMin(default.Armor * upgLevel, 1.0f));
}

static simulated function ModifyMagSizeAndNumberPassive(out float magazineCapacityFactor, int upgLevel)
{
	magazineCapacityFactor += default.MagSize * upgLevel;
}

defaultproperties
{
	Armor=0.05f
	Damage=0.02f
	MagSize=0.05f
	UpgradeName="SWAT"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">maximum armor</font> <font color=\"#77D914\">+5%</font> (max <font color=\"#77D914\">100%</font>)."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">magazine capacity</font> <font color=\"#77D914\">+5%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">SWAT weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=5,maxValue=100)
	PerkBonus(1)=(baseValue=0,incValue=5,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_SWAT'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_SWAT"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_SWAT"
}
