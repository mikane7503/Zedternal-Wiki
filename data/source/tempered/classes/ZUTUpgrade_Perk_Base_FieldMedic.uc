class ZUTUpgrade_Perk_Base_FieldMedic extends ZTUpgrade_Perk;

var float Damage, Health, HealRate;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_FieldMedic') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_FieldMedic'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
}

static function ModifyHealth(out int InHealth, int DefaultHealth, int upgLevel)
{
	// Ascension Field Medic health is a flat +2 per perk level.
	InHealth += Round(default.Health * upgLevel);
}

static simulated function ModifyHealerRechargeTime(out float InRechargeTime, float DefaultRechargeTime, int upgLevel)
{
	InRechargeTime = DefaultRechargeTime / (DefaultRechargeTime / InRechargeTime + default.HealRate * upgLevel);
}

defaultproperties
{
	Damage=0.02f
	Health=2.0f
	HealRate=0.05f
	UpgradeName="Field Medic"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">maximum health</font> <font color=\"#77D914\">+2 HP</font>."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">syringe and healing dart recharge</font> <font color=\"#77D914\">+5%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">Field Medic weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=2,maxValue=-1)
	PerkBonus(1)=(baseValue=0,incValue=5,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Medic'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_FieldMedic"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_FieldMedic"
}
