class ZUTUpgrade_Perk_Base_Berserker extends ZTUpgrade_Perk;

var float AttackSpeed, Damage, Health;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_Berserker') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_Berserker'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
}

static function ModifyHealth(out int InHealth, int DefaultHealth, int upgLevel)
{
	// Ascension Berserker health is a flat +5 per perk level, not a
	// percentage of the pawn's base health.
	InHealth += Round(default.Health * upgLevel);
}

static simulated function ModifyMeleeAttackSpeedPassive(out float durationFactor, int upgLevel)
{
	durationFactor = 1.0f / (1.0f / durationFactor + default.AttackSpeed * upgLevel);
}

static simulated function ModifyRateOfFirePassive(out float rateOfFireFactor, int upgLevel)
{
	rateOfFireFactor = 1.0f / (1.0f / rateOfFireFactor + default.AttackSpeed * upgLevel);
}

defaultproperties
{
	AttackSpeed=0.02f
	Damage=0.02f
	Health=5.0f
	UpgradeName="Berserker"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">maximum health</font> <font color=\"#77D914\">+5 HP</font>."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">melee and fire rate</font> <font color=\"#77D914\">+2%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">Berserker weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=5,maxValue=-1)
	PerkBonus(1)=(baseValue=0,incValue=2,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Berserker'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_Berserker"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_Berserker"
}
