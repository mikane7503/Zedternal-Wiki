class ZUTUpgrade_Perk_Base_Demolitionist extends ZTUpgrade_Perk;

var float Damage, GrenadeDamage, LZDamage;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_Demolitionist') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_Demolitionist'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
	if (DamageType != None && static.IsGrenadeDTAdvance(DamageType, DamageInstigator))
		InDamage += Round(float(DefaultDamage) * default.GrenadeDamage * upgLevel);
	if (MyKFPM != None && (MyKFPM.static.IsLargeZed() || MyKFPM.static.IsABoss()))
		InDamage += Round(float(DefaultDamage) * default.LZDamage * upgLevel);
}

defaultproperties
{
	Damage=0.02f
	GrenadeDamage=0.05f
	LZDamage=0.03f
	UpgradeName="Demolitionist"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">grenade damage</font> <font color=\"#77D914\">+5%</font>."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">damage to large Zeds and bosses</font> <font color=\"#77D914\">+3%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">Demolitionist weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=5,maxValue=-1)
	PerkBonus(1)=(baseValue=0,incValue=3,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Demolition'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_Demolitionist"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_Demolitionist"
}
