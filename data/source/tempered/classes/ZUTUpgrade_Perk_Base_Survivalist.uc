class ZUTUpgrade_Perk_Base_Survivalist extends ZTUpgrade_Perk;

var float Damage, SpareAmmo;

static function ModifyDamageGivenPassive(out float damageFactor, int upgLevel)
{
	damageFactor += default.Damage * upgLevel;
}

static function ApplyWeightLimits(out int InWeightLimit, int DefaultWeightLimit, int upgLevel)
{
	InWeightLimit += upgLevel;
}

static simulated function ModifySpareAmmoAmountPassive(out float spareAmmoFactor, int upgLevel)
{
	spareAmmoFactor += default.SpareAmmo * upgLevel;
}

defaultproperties
{
	Damage=0.02f
	SpareAmmo=0.05f
	UpgradeName="Survivalist"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">carry weight</font> <font color=\"#77D914\">+1</font>."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">spare ammunition</font> <font color=\"#77D914\">+5%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">damage with all weapons</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=1,maxValue=-1)
	PerkBonus(1)=(baseValue=0,incValue=5,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Survivalist'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_Survivalist"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_Survivalist"
}
