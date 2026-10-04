class ZUTUpgrade_Perk_Base_Support extends ZTUpgrade_Perk;

var float Damage, Penetration, StoppingPower;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_Support') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_Support'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
}

static function ModifyStumblePowerPassive(out float stumblePowerFactor, int upgLevel)
{
	stumblePowerFactor += default.StoppingPower * upgLevel;
}

static function ModifyKnockdownPowerPassive(out float knockdownPowerFactor, int upgLevel)
{
	knockdownPowerFactor += default.StoppingPower * upgLevel;
}

static simulated function ModifyPenetrationPassive(out float penetrationFactor, int upgLevel)
{
	penetrationFactor += default.Penetration * upgLevel;
}

defaultproperties
{
	Damage=0.02f
	Penetration=0.10f
	StoppingPower=0.02f
	UpgradeName="Support"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">stumble and knockdown power</font> <font color=\"#77D914\">+2%</font>."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">penetration</font> <font color=\"#77D914\">+10%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">Support weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=2,maxValue=-1)
	PerkBonus(1)=(baseValue=0,incValue=10,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Support'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_Support"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_Support"
}
