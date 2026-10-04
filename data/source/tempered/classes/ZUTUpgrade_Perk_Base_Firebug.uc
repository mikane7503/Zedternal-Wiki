class ZUTUpgrade_Perk_Base_Firebug extends ZTUpgrade_Perk;

var float Damage, Defense;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_Firebug') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_Firebug'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
}

static function ModifyDamageTaken(out int InDamage, int DefaultDamage, int upgLevel, KFPawn OwnerPawn, optional class<DamageType> DamageType, optional Controller InstigatedBy, optional KFWeapon MyKFW)
{
	if (ClassIsChildOf(DamageType, class'KFDT_Fire') || ClassIsChildOf(DamageType, class'KFDT_Explosive') || ClassIsChildOf(DamageType, class'KFDT_Toxic') || ClassIsChildOf(DamageType, class'KFDT_Sonic'))
		InDamage -= Round(float(DefaultDamage) * FMin(default.Defense * upgLevel, 0.4f));
}

defaultproperties
{
	Damage=0.02f
	Defense=0.01f
	UpgradeName="Firebug"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">fire, explosive, toxic and sonic resistance</font> <font color=\"#77D914\">+1%</font> (max <font color=\"#77D914\">40%</font>)."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">Firebug weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=1,maxValue=40)
	PerkBonus(1)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Firebug'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_Firebug"
	LocalizeDescriptionLineCount=3
	Name="Default__ZUTUpgrade_Perk_Base_Firebug"
}
