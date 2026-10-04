class ZUTUpgrade_Perk_Base_Sharpshooter extends ZTUpgrade_Perk;

var float Damage, DamageHead, Recoil;

static function ModifyDamageGiven(out int InDamage, int DefaultDamage, int upgLevel, optional Actor DamageCauser, optional KFPawn_Monster MyKFPM, optional KFPlayerController DamageInstigator, optional class<KFDamageType> DamageType, optional int HitZoneIdx, optional KFWeapon MyKFW)
{
	if (IsWeaponOnSpecificPerk(MyKFW, class'KFGame.KFPerk_Sharpshooter') || IsDamageTypeOnSpecificPerk(DamageType, class'KFGame.KFPerk_Sharpshooter'))
		InDamage += Round(float(DefaultDamage) * default.Damage * upgLevel);
	if (HitZoneIdx == HZI_HEAD)
		InDamage += Round(float(DefaultDamage) * default.DamageHead * upgLevel);
}

static simulated function ModifyRecoilPassive(out float recoilFactor, int upgLevel)
{
	recoilFactor -= recoilFactor * FMin(default.Recoil * upgLevel, 0.8f);
}

defaultproperties
{
	Damage=0.02f
	DamageHead=0.02f
	Recoil=0.02f
	UpgradeName="Sharpshooter"
	UpgradeDescription(0)="Per level: <font color=\"#66CCFF\">recoil with all weapons</font> <font color=\"#77D914\">-2%</font> (max <font color=\"#77D914\">80%</font>)."
	UpgradeDescription(1)="Per level: <font color=\"#66CCFF\">headshot damage with all weapons</font> <font color=\"#77D914\">+2%</font>."
	UpgradeDescription(2)="Per level: <font color=\"#66CCFF\">Sharpshooter weapon damage</font> <font color=\"#77D914\">+2%</font>."
	PerkBonus(0)=(baseValue=0,incValue=2,maxValue=80)
	PerkBonus(1)=(baseValue=0,incValue=2,maxValue=-1)
	PerkBonus(2)=(baseValue=0,incValue=2,maxValue=-1)
	UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Sharpshooter'
	bShouldLocalize=True
	LocPackage="ZedternalTempered"
	LocSection="ZUTUpgrade_Perk_Base_Sharpshooter"
	LocalizeDescriptionLineCount=4
	Name="Default__ZUTUpgrade_Perk_Base_Sharpshooter"
}
