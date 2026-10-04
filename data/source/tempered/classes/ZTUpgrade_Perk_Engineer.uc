class ZTUpgrade_Perk_Engineer extends ZTUpgrade_Perk config(ZedternalUnlimited);
// Runtime log guard; never saved to INI.
var config bool bIconLogged;
static simulated function Texture2D GetUpgradeIcon(int index)
{
    local Texture2D Icon;
    local WorldInfo W;
    Icon=Texture2D(DynamicLoadObject("ZedternalTemperedPerkIcons.Perks.UI_Perk_Engineer",class'Texture2D',true));
    if (!default.bIconLogged)
    {
        W=class'WorldInfo'.static.GetWorldInfo();
        `log("[ZT_ENGINEER][" $ ((W!=None && W.NetMode==NM_DedicatedServer) ? "Server" : "Client") $ "] icon=" $ (Icon==None ? "MISSING: import UI_Perk_Engineer" : PathName(Icon)));
        default.bIconLogged=true;
    }
    return Icon;
}
defaultproperties
{
    UpgradeName="Engineer"
    bShouldLocalize=True
    LocPackage="ZedternalTempered"
    LocSection="ZTUpgrade_Perk_Engineer"
    LocalizeDescriptionLineCount=4
    UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Engineer'
    UpgradeDescription(0)="Drone damage <font color=\"#77D914\">+2%</font> per Engineer level."
    UpgradeDescription(1)="Drone ammunition capacity <font color=\"#77D914\">+3%</font> and detection radius <font color=\"#77D914\">+1%</font> per Engineer level."
    UpgradeDescription(2)="Level <font color=\"#77D914\">10</font> capstone: drone fire rate <font color=\"#77D914\">+15%</font>, ammunition capacity <font color=\"#77D914\">+20%</font>, and <font color=\"#77D914\">+1</font> shared deployed-drone limit (<font color=\"#77D914\">2</font> total)."
    UpgradeDescription(3)="If any player reaches Engineer <font color=\"#77D914\">5</font>, normal Sentinel and HRG Warthog drones appear in the team trader for the match. Personal bonuses affect only your drones. Drone weapon upgrades are disabled. HRG Warthog rounds cannot cause knockdown, stumble, stun, or other incapacitation effects; their damage and payload effects remain."
}
