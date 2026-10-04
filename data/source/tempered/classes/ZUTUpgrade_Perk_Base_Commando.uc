class ZUTUpgrade_Perk_Base_Commando extends ZTUpgrade_Perk;

var float Damage, ReloadRate;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_Commando') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_Commando'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
}

static simulated function GetReloadRateScalePassive(out float reloadRateFactor, int upgLevel)
{
	reloadRateFactor = 1.0f / (1.0f / reloadRateFactor + default.ReloadRate * upgLevel);
}

static simulated function GetZedTimeExtension(out float InExtension, float DefaultExtension, int upgLevel)
{
	InExtension += float(Min(upgLevel, 10));
}

defaultproperties
{
	Damage=0.02f
	ReloadRate=0.015f
	UpgradeName="Commando"
	UpgradeDescription(0)="Per level: <font color=\"#FFD700\">ZED Time extension</font> <font color=\"#77D914\">+1 second</font> (max <font color=\"#77D914\">10 seconds</font>)."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">reload speed</font> <font color=\"#77D914\">+1.5%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">Commando weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=1,maxValue=10)
	PerkBonus(1)=(baseValue=0,incValue=2,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Commando'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_Commando"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_Commando"
}
