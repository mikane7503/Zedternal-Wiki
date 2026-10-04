// Base economy perk. No combat modifiers, capstones or savings mechanics.
class ZTUpgrade_Perk_Capitalist extends ZTUpgrade_Perk config(ZedternalUnlimited);
var config bool bIconChecked; // Runtime log flag; never saved.
static simulated function Texture2D GetUpgradeIcon(int index)
{
    local WorldInfo W;
    local Texture2D Icon;
    Icon=Texture2D(DynamicLoadObject("ZedternalTemperedPerkIcons.Perks.UI_Perk_Capitalist",class'Texture2D',true));
    if(!default.bIconChecked)
    {
        default.bIconChecked=true;
        W=class'WorldInfo'.static.GetWorldInfo();
        `log("[ZT_CAPITALIST][" $ ((W!=None && W.NetMode==NM_Client) ? "Client" : "Server") $ "] icon=Perks.UI_Perk_Capitalist loaded=" $ (Icon!=None) @ "fallback=" $ (Icon==None));
    }
    return Icon!=None ? Icon : default.UpgradeIcon[0];
}
defaultproperties
{
    UpgradeIcon(0)=Texture2D'ZedternalTemperedPerkIcons.Perks.UI_Perk_Support'
    bShouldLocalize=True
    LocPackage="ZedternalTempered"
    LocSection="ZTUpgrade_Perk_Capitalist"
    LocalizeDescriptionLineCount=3
    UpgradeName="Capitalist"
    UpgradeDescription(0)="Salary: +%x Dosh per successful wave survived from start to finish without dying."
    UpgradeDescription(1)="Direct-kill Dosh reward <font color=\"#77D914\">+%x%%</font>. Assist rewards are unchanged."
    UpgradeDescription(2)="No combat bonuses. No level<font color=\"#77D914\">-10</font> or level<font color=\"#77D914\">-20</font> capstones. Advances into Gambler at level <font color=\"#77D914\">5</font> and Tycoon at level <font color=\"#77D914\">10</font>."
    PerkBonus(0)=(baseValue=0,incValue=10,maxValue=-1)
    PerkBonus(1)=(baseValue=0,incValue=1,maxValue=-1)
}
