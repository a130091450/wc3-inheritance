globals
//globals from YDTriggerSaveLoadSystem:
constant boolean LIBRARY_YDTriggerSaveLoadSystem=true
hashtable YDHT
hashtable YDLOC
//endglobals from YDTriggerSaveLoadSystem
//globals from YDWEWakePlayerUnitsNull:
constant boolean LIBRARY_YDWEWakePlayerUnitsNull=true
//endglobals from YDWEWakePlayerUnitsNull
//globals from YDWEEnableCreepSleepBJNull:
constant boolean LIBRARY_YDWEEnableCreepSleepBJNull=true
//endglobals from YDWEEnableCreepSleepBJNull
rect gg_rct_Zone0= null
rect gg_rct_Zone1= null
rect gg_rct_Zone2= null
rect gg_rct_Zone3= null
unit udg_Hero= null
boolean udg_HeroPicked= false
integer array udg_Tier
integer array udg_XiuWei
integer array udg_XiuNeed
unit udg_TempUnit= null
integer udg_TempInt= 0
string udg_Msg
unit udg_H0= null
unit udg_H1= null
unit udg_H2= null
unit udg_H3= null
group udg_TempGroup= null
real udg_TempRealX= 0
real udg_TempRealY= 0
integer udg_PIdx= 0
unit array udg_HeroP
integer array udg_NeedTable
integer udg_TempInt2= 0
integer array udg_Deaths
boolean array udg_Out
unit udg_BossUnit= null
integer udg_BossCount= 0
boolean udg_GameOver= false
string udg_MsgPre
player udg_TempPl= null
integer array udg_CreepN
unit udg_LastCreep= null
integer array udg_CntTmp
hashtable udg_CreepHash= null
real array udg_ZoneHomeX
real array udg_ZoneHomeY
real udg_TstMin= 0
integer udg_TstCnt= 0
real udg_TstCur= 0
integer udg_TstCnt2= 0
trigger gg_trg_______u= null
trigger gg_trg_TST_Chk= null
trigger gg_trg_V3_CreepDead= null
trigger gg_trg_V3_Death= null
trigger gg_trg_V3_Boss= null
trigger gg_trg_V3_BossKill= null
trigger gg_trg_V3_Kill= null
trigger gg_trg_V3_TierUp= null
trigger gg_trg_V3_Setup= null
trigger gg_trg_V3_Spawn3= null
trigger gg_trg_V3_Spawn2= null
trigger gg_trg_V3_Spawn1= null
trigger gg_trg_V3_Spawn0= null
trigger gg_trg_V3_Init= null

trigger l__library_init

//JASSHelper struct globals:

endglobals


//library YDTriggerSaveLoadSystem:
//#  define YDTRIGGER_handle(SG)                          YDTRIGGER_HT##SG##(HashtableHandle)
    function YDTriggerSaveLoadSystem__Init takes nothing returns nothing
            set YDHT=InitHashtable()
        set YDLOC=InitHashtable()
    endfunction

//library YDTriggerSaveLoadSystem ends
//library YDWEWakePlayerUnitsNull:
function YDWEWakePlayerUnitsNull takes player whichPlayer returns nothing
    local group g= CreateGroup()
    call GroupEnumUnitsOfPlayer(g, whichPlayer, null)
    call ForGroup(g, function WakePlayerUnitsEnum)
    call DestroyGroup(g)
    set g=null
endfunction

//library YDWEWakePlayerUnitsNull ends
//library YDWEEnableCreepSleepBJNull:
function YDWEEnableCreepSleepBJNull takes boolean enable returns nothing
    call SetPlayerState(Player(PLAYER_NEUTRAL_AGGRESSIVE), PLAYER_STATE_NO_CREEP_SLEEP, IntegerTertiaryOp(enable, 0, 1))
    // If we're disabling, attempt to wake any already-sleeping creeps.
    if ( not enable ) then
        call YDWEWakePlayerUnitsNull(Player(PLAYER_NEUTRAL_AGGRESSIVE))
    endif
endfunction

//library YDWEEnableCreepSleepBJNull ends
//===========================================================================
//*
//*  Global variables
//*
//===========================================================================
function InitGlobals takes nothing returns nothing
 local integer i= 0
	set udg_HeroPicked=false
	set i=0
	loop
		exitwhen ( i > 16 )
		set udg_Tier[i]=1
		set i=i + 1
	endloop
	set i=0
	loop
		exitwhen ( i > 16 )
		set udg_XiuWei[i]=0
		set i=i + 1
	endloop
	set i=0
	loop
		exitwhen ( i > 16 )
		set udg_XiuNeed[i]=100
		set i=i + 1
	endloop
	set udg_TempInt=0
	set udg_Msg=""
	set udg_TempGroup=CreateGroup()
	set udg_TempRealX=0
	set udg_TempRealY=0
	set udg_PIdx=0
	set i=0
	loop
		exitwhen ( i > 16 )
		set udg_NeedTable[i]=0
		set i=i + 1
	endloop
	set udg_TempInt2=0
	set i=0
	loop
		exitwhen ( i > 16 )
		set udg_Deaths[i]=0
		set i=i + 1
	endloop
	set i=0
	loop
		exitwhen ( i > 16 )
		set udg_Out[i]=false
		set i=i + 1
	endloop
	set udg_BossCount=0
	set udg_GameOver=false
	set udg_MsgPre=""
	set i=0
	loop
		exitwhen ( i > 1 )
		set udg_CreepN[i]=0
		set i=i + 1
	endloop
	set i=0
	loop
		exitwhen ( i > 1 )
		set udg_CntTmp[i]=0
		set i=i + 1
	endloop
	set i=0
	loop
		exitwhen ( i > 1 )
		set udg_ZoneHomeX[i]=0
		set i=i + 1
	endloop
	set i=0
	loop
		exitwhen ( i > 1 )
		set udg_ZoneHomeY[i]=0
		set i=i + 1
	endloop
	set udg_TstMin=0
	set udg_TstCnt=0
	set udg_TstCur=0
	set udg_TstCnt2=0
endfunction
function InitRandomGroups takes nothing returns nothing
 local integer curset
endfunction
function InitSounds takes nothing returns nothing
endfunction
function CreateDestructables takes nothing returns nothing
 local destructable d
 local trigger t
 local real life
endfunction
function CreateItems takes nothing returns nothing
 local integer itemID
endfunction
function CreateUnits takes nothing returns nothing
 local unit u
 local integer unitID
 local trigger t
 local real life
endfunction
function CreateRegions takes nothing returns nothing
 local weathereffect we
	set gg_rct_Zone0=Rect(- 2624, - 2624, - 1216, - 1216)
	set gg_rct_Zone1=Rect(1184, - 2624, 2592, - 1216)
	set gg_rct_Zone2=Rect(- 2624, 1184, - 1216, 2592)
	set gg_rct_Zone3=Rect(1184, 1184, 2592, 2592)
endfunction
function CreateCameras takes nothing returns nothing
endfunction
//===========================================================================
// Trigger: 简介
//===========================================================================
function Trig_______uActions takes nothing returns nothing
	//欢迎使用世界编辑器，开始你的地图创造之旅。
	//你可以从https://reckfeng.com/获取最新编辑器咨询。
	//当你的地图意外损坏时，你可以在backups目录找到你最近26次保存的地图。
	//任何疑问请加官方作者群：QQ433807374。
endfunction
//===========================================================================
function InitTrig_______u takes nothing returns nothing
	set gg_trg_______u=CreateTrigger()
	call TriggerAddAction(gg_trg_______u, function Trig_______uActions)
endfunction
//===========================================================================
// Trigger: TST_Chk
//===========================================================================
function Trig_TST_ChkActions takes nothing returns nothing
	set udg_Msg="T=" + R2S(GetTimeOfDay()) + "  HP=" + I2S(R2I(GetUnitState(udg_H0, UNIT_STATE_LIFE)))
	set udg_Msg=udg_Msg + "/" + I2S(R2I(GetUnitState(udg_H0, UNIT_STATE_MAX_LIFE)))
	set udg_Msg=udg_Msg + "  C0=" + I2S(udg_CreepN[0])
	call DisplayTextToPlayer(Player(0), 0, 0, udg_Msg)
endfunction
//===========================================================================
function InitTrig_TST_Chk takes nothing returns nothing
	set gg_trg_TST_Chk=CreateTrigger()
	call TriggerRegisterTimerEventPeriodic(gg_trg_TST_Chk, 5.0)
	call TriggerAddAction(gg_trg_TST_Chk, function Trig_TST_ChkActions)
endfunction
//===========================================================================
// Trigger: V3_CreepDead
//===========================================================================
function Trig_V3_CreepDeadActions takes nothing returns nothing
	set udg_TempUnit=GetDyingUnit()
	set udg_TempPl=GetOwningPlayer(udg_TempUnit)
	if ( ( udg_TempPl == Player(11) ) ) then
		set udg_TempInt=GetUnitUserData(udg_TempUnit)
		if ( ( udg_TempInt >= 1 ) ) then
			set udg_TempInt=udg_TempInt - 1
			set udg_CreepN[udg_TempInt]=IMaxBJ(udg_CreepN[udg_TempInt] - 1, 0)
		else
		endif
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_CreepDead takes nothing returns nothing
	set gg_trg_V3_CreepDead=CreateTrigger()
	call TriggerRegisterAnyUnitEventBJ(gg_trg_V3_CreepDead, EVENT_PLAYER_UNIT_DEATH)
	call TriggerAddAction(gg_trg_V3_CreepDead, function Trig_V3_CreepDeadActions)
endfunction
//===========================================================================
// Trigger: V3_Death
//===========================================================================
function Trig_V3_DeathActions takes nothing returns nothing
	set udg_TempUnit=GetDyingUnit()
	set udg_TempPl=GetOwningPlayer(udg_TempUnit)
	set udg_PIdx=GetPlayerId(udg_TempPl)
	if ( ( udg_PIdx < 4 ) ) then
		set udg_Deaths[udg_PIdx]=udg_Deaths[udg_PIdx] + 1
		set udg_TempInt=udg_Deaths[udg_PIdx]
		if ( ( udg_TempInt >= 3 ) ) then
			set udg_Out[udg_PIdx]=true
			call RemoveUnit(udg_HeroP[udg_PIdx])
			set udg_HeroP[udg_PIdx]=null
			call DisplayTextToPlayer(udg_TempPl, 0, 0, "第 3 次阵亡，你已出局")
			if ( ( udg_Out[0] == true ) and ( udg_Out[1] == true ) and ( udg_Out[2] == true ) and ( udg_Out[3] == true ) ) then
				set udg_GameOver=true
				call DisplayTextToPlayer(Player(0), 0, 0, "全员出局，本局结束")
				call DisplayTextToPlayer(Player(1), 0, 0, "全员出局，本局结束")
				call DisplayTextToPlayer(Player(2), 0, 0, "全员出局，本局结束")
				call DisplayTextToPlayer(Player(3), 0, 0, "全员出局，本局结束")
			else
			endif
		else
			call DisplayTextToPlayer(udg_TempPl, 0, 0, "阵亡，已在原地复活（死 3 次出局）")
			call ReviveHero(udg_HeroP[udg_PIdx], GetUnitX(udg_HeroP[udg_PIdx]), GetUnitY(udg_HeroP[udg_PIdx]), true)
			call SelectUnitForPlayerSingle(udg_HeroP[udg_PIdx], udg_TempPl)
		endif
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_Death takes nothing returns nothing
	set gg_trg_V3_Death=CreateTrigger()
	call TriggerRegisterAnyUnitEventBJ(gg_trg_V3_Death, EVENT_PLAYER_UNIT_DEATH)
	call TriggerAddAction(gg_trg_V3_Death, function Trig_V3_DeathActions)
endfunction
//===========================================================================
// Trigger: V3_Boss
//===========================================================================
function Trig_V3_BossActions takes nothing returns nothing
	if ( ( udg_GameOver == false ) ) then
		set udg_BossCount=udg_BossCount + 1
		set udg_BossUnit=CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), 'ninf', 0, 0, 270)
		if ( ( IsUnitAliveBJ(udg_HeroP[0]) == true ) ) then
			call IssueTargetOrder(udg_BossUnit, "attack", udg_HeroP[0])
		else
		endif
		call PingMinimap(0, 0, 4)
		call DisplayTextToPlayer(Player(0), 0, 0, "首领已降临地图中央！击杀可全队 +300 修为")
		call DisplayTextToPlayer(Player(1), 0, 0, "首领已降临地图中央！击杀可全队 +300 修为")
		call DisplayTextToPlayer(Player(2), 0, 0, "首领已降临地图中央！击杀可全队 +300 修为")
		call DisplayTextToPlayer(Player(3), 0, 0, "首领已降临地图中央！击杀可全队 +300 修为")
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_Boss takes nothing returns nothing
	set gg_trg_V3_Boss=CreateTrigger()
	call TriggerRegisterTimerEventPeriodic(gg_trg_V3_Boss, 480.0)
	call TriggerAddAction(gg_trg_V3_Boss, function Trig_V3_BossActions)
endfunction
//===========================================================================
// Trigger: V3_BossKill
//===========================================================================
function Trig_V3_BossKillActions takes nothing returns nothing
	set udg_TempUnit=GetDyingUnit()
	if ( ( udg_TempUnit == udg_BossUnit ) ) then
		set udg_BossUnit=null
		set udg_XiuWei[0]=udg_XiuWei[0] + 300
		set udg_XiuWei[1]=udg_XiuWei[1] + 300
		set udg_XiuWei[2]=udg_XiuWei[2] + 300
		set udg_XiuWei[3]=udg_XiuWei[3] + 300
		call DisplayTextToPlayer(Player(0), 0, 0, "首领伏诛！全队修为 +300")
		call DisplayTextToPlayer(Player(1), 0, 0, "首领伏诛！全队修为 +300")
		call DisplayTextToPlayer(Player(2), 0, 0, "首领伏诛！全队修为 +300")
		call DisplayTextToPlayer(Player(3), 0, 0, "首领伏诛！全队修为 +300")
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_BossKill takes nothing returns nothing
	set gg_trg_V3_BossKill=CreateTrigger()
	call TriggerRegisterAnyUnitEventBJ(gg_trg_V3_BossKill, EVENT_PLAYER_UNIT_DEATH)
	call TriggerAddAction(gg_trg_V3_BossKill, function Trig_V3_BossKillActions)
endfunction
//===========================================================================
// Trigger: V3_Kill
//===========================================================================
function Trig_V3_KillActions takes nothing returns nothing
	set udg_TempUnit=GetDyingUnit()
	set udg_TempPl=GetOwningPlayer(udg_TempUnit)
	if ( ( udg_TempPl == Player(11) ) ) then
		set udg_TempUnit=GetKillingUnitBJ()
		set udg_TempPl=GetOwningPlayer(udg_TempUnit)
		set udg_PIdx=GetPlayerId(udg_TempPl)
		if ( ( udg_PIdx < 4 ) ) then
			set udg_XiuWei[udg_PIdx]=udg_XiuWei[udg_PIdx] + 10
			call DisplayTextToPlayer(udg_TempPl, 0, 0, "修为 +10")
			set udg_Msg=udg_MsgPre + I2S(udg_Tier[udg_PIdx]) + "  X" + I2S(udg_XiuWei[udg_PIdx]) + "/" + I2S(udg_XiuNeed[udg_PIdx])
			call DisplayTextToPlayer(udg_TempPl, 0, 0, udg_Msg)
			set udg_TempInt=udg_XiuWei[udg_PIdx]
			set udg_TempInt2=udg_XiuNeed[udg_PIdx]
			if ( ( udg_TempInt >= udg_TempInt2 ) ) then
				call TriggerExecute(gg_trg_V3_TierUp)
			else
			endif
		else
		endif
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_Kill takes nothing returns nothing
	set gg_trg_V3_Kill=CreateTrigger()
	call TriggerRegisterAnyUnitEventBJ(gg_trg_V3_Kill, EVENT_PLAYER_UNIT_DEATH)
	call TriggerAddAction(gg_trg_V3_Kill, function Trig_V3_KillActions)
endfunction
//===========================================================================
// Trigger: V3_TierUp
//===========================================================================
function Trig_V3_TierUpActions takes nothing returns nothing
	set udg_TempInt=udg_Tier[udg_PIdx]
	if ( ( udg_TempInt < 7 ) ) then
		set udg_Tier[udg_PIdx]=udg_Tier[udg_PIdx] + 1
		set udg_XiuWei[udg_PIdx]=0
		set udg_XiuNeed[udg_PIdx]=udg_NeedTable[udg_Tier[udg_PIdx]]
		call SetHeroStr(udg_HeroP[udg_PIdx], GetHeroStr(udg_HeroP[udg_PIdx], true) + 6, true)
		call SetHeroAgi(udg_HeroP[udg_PIdx], GetHeroAgi(udg_HeroP[udg_PIdx], true) + 6, true)
		call SetHeroInt(udg_HeroP[udg_PIdx], GetHeroInt(udg_HeroP[udg_PIdx], true) + 6, true)
		call SetUnitState(udg_HeroP[udg_PIdx], UNIT_STATE_LIFE, GetUnitState(udg_HeroP[udg_PIdx], UNIT_STATE_MAX_LIFE))
		set udg_Msg=udg_MsgPre + I2S(udg_Tier[udg_PIdx]) + "  X" + I2S(udg_XiuWei[udg_PIdx]) + "/" + I2S(udg_XiuNeed[udg_PIdx])
		call DisplayTextToPlayer(udg_TempPl, 0, 0, "破境成功！力/敏/智 +6，生命全满")
		call DisplayTextToPlayer(udg_TempPl, 0, 0, udg_Msg)
	else
		set udg_XiuWei[udg_PIdx]=udg_XiuNeed[udg_PIdx]
		call DisplayTextToPlayer(udg_TempPl, 0, 0, "已达最高品阶（神话）")
	endif
endfunction
//===========================================================================
function InitTrig_V3_TierUp takes nothing returns nothing
	set gg_trg_V3_TierUp=CreateTrigger()
	call TriggerRegisterTimerEventSingle(gg_trg_V3_TierUp, 99999)
	call TriggerAddAction(gg_trg_V3_TierUp, function Trig_V3_TierUpActions)
endfunction
//===========================================================================
// Trigger: V3_Setup
//===========================================================================
function Trig_V3_SetupActions takes nothing returns nothing
	set udg_HeroP[0]=udg_H0
	set udg_HeroP[1]=udg_H1
	set udg_HeroP[2]=udg_H2
	set udg_HeroP[3]=udg_H3
	set udg_NeedTable[1]=100
	set udg_NeedTable[2]=220
	set udg_NeedTable[3]=430
	set udg_NeedTable[4]=750
	set udg_NeedTable[5]=1200
	set udg_NeedTable[6]=1800
	set udg_NeedTable[7]=2600
	set udg_Tier[0]=1
	set udg_Tier[1]=1
	set udg_Tier[2]=1
	set udg_Tier[3]=1
	set udg_XiuNeed[0]=100
	set udg_XiuNeed[1]=100
	set udg_XiuNeed[2]=100
	set udg_XiuNeed[3]=100
	call SelectUnitForPlayerSingle(udg_H0, Player(0))
	call SelectUnitForPlayerSingle(udg_H1, Player(1))
	call SelectUnitForPlayerSingle(udg_H2, Player(2))
	call SelectUnitForPlayerSingle(udg_H3, Player(3))
	set udg_MsgPre="品阶"
	call DisplayTextToPlayer(Player(0), 0, 0, "守住四角：杀怪攒修为，修为满自动破境；死 3 次出局")
	call DisplayTextToPlayer(Player(1), 0, 0, "守住四角：杀怪攒修为，修为满自动破境；死 3 次出局")
	call DisplayTextToPlayer(Player(2), 0, 0, "守住四角：杀怪攒修为，修为满自动破境；死 3 次出局")
	call DisplayTextToPlayer(Player(3), 0, 0, "守住四角：杀怪攒修为，修为满自动破境；死 3 次出局")
	call SetPlayerAlliance(Player(0), Player(1), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(0), Player(1), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(0), Player(2), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(0), Player(2), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(0), Player(3), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(0), Player(3), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(1), Player(0), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(1), Player(0), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(1), Player(2), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(1), Player(2), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(1), Player(3), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(1), Player(3), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(2), Player(0), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(2), Player(0), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(2), Player(1), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(2), Player(1), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(2), Player(3), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(2), Player(3), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(3), Player(0), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(3), Player(0), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(3), Player(1), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(3), Player(1), ALLIANCE_SHARED_VISION, true)
	call SetPlayerAlliance(Player(3), Player(2), ALLIANCE_PASSIVE, true)
	call SetPlayerAlliance(Player(3), Player(2), ALLIANCE_SHARED_VISION, true)
	call UnitRemoveAbility(udg_H0, 'AHtb')
	call UnitRemoveAbility(udg_H0, 'AHtc')
	call UnitRemoveAbility(udg_H0, 'AHbh')
	call UnitRemoveAbility(udg_H0, 'AHav')
	call UnitRemoveAbility(udg_H1, 'AHtb')
	call UnitRemoveAbility(udg_H1, 'AHtc')
	call UnitRemoveAbility(udg_H1, 'AHbh')
	call UnitRemoveAbility(udg_H1, 'AHav')
	call UnitRemoveAbility(udg_H2, 'AHtb')
	call UnitRemoveAbility(udg_H2, 'AHtc')
	call UnitRemoveAbility(udg_H2, 'AHbh')
	call UnitRemoveAbility(udg_H2, 'AHav')
	call UnitRemoveAbility(udg_H3, 'AHtb')
	call UnitRemoveAbility(udg_H3, 'AHtc')
	call UnitRemoveAbility(udg_H3, 'AHbh')
	call UnitRemoveAbility(udg_H3, 'AHav')
	call UnitAddAbility(udg_H0, 'A000')
	call UnitAddAbility(udg_H1, 'A000')
	call UnitAddAbility(udg_H2, 'A000')
	call UnitAddAbility(udg_H3, 'A000')
	call SetUnitAbilityLevel(udg_H0, 'A000', 1)
	call SetUnitAbilityLevel(udg_H1, 'A000', 1)
	call SetUnitAbilityLevel(udg_H2, 'A000', 1)
	call SetUnitAbilityLevel(udg_H3, 'A000', 1)
	call SetHeroLevelBJ(udg_H0, 1, false)
	call SetHeroLevelBJ(udg_H1, 1, false)
	call SetHeroLevelBJ(udg_H2, 1, false)
	call SetHeroLevelBJ(udg_H3, 1, false)
	call SetHeroStr(udg_H0, 10, true)
	call SetHeroStr(udg_H1, 10, true)
	call SetHeroStr(udg_H2, 10, true)
	call SetHeroStr(udg_H3, 10, true)
	call SetHeroAgi(udg_H0, 10, true)
	call SetHeroAgi(udg_H1, 10, true)
	call SetHeroAgi(udg_H2, 10, true)
	call SetHeroAgi(udg_H3, 10, true)
	call SetHeroInt(udg_H0, 10, true)
	call SetHeroInt(udg_H1, 10, true)
	call SetHeroInt(udg_H2, 10, true)
	call SetHeroInt(udg_H3, 10, true)
	set udg_ZoneHomeX[0]=- 1900
	set udg_ZoneHomeY[0]=- 1900
	set udg_ZoneHomeX[1]=1900
	set udg_ZoneHomeY[1]=- 1900
	set udg_ZoneHomeX[2]=- 1900
	set udg_ZoneHomeY[2]=1900
	set udg_ZoneHomeX[3]=1900
	set udg_ZoneHomeY[3]=1900
	call SetPlayerAlliance(Player(11), Player(0), ALLIANCE_PASSIVE, false)
	call SetPlayerAlliance(Player(0), Player(11), ALLIANCE_PASSIVE, false)
	call SetPlayerAlliance(Player(11), Player(1), ALLIANCE_PASSIVE, false)
	call SetPlayerAlliance(Player(1), Player(11), ALLIANCE_PASSIVE, false)
	call SetPlayerAlliance(Player(11), Player(2), ALLIANCE_PASSIVE, false)
	call SetPlayerAlliance(Player(2), Player(11), ALLIANCE_PASSIVE, false)
	call SetPlayerAlliance(Player(11), Player(3), ALLIANCE_PASSIVE, false)
	call SetPlayerAlliance(Player(3), Player(11), ALLIANCE_PASSIVE, false)
endfunction
//===========================================================================
function InitTrig_V3_Setup takes nothing returns nothing
	set gg_trg_V3_Setup=CreateTrigger()
	call TriggerRegisterTimerEventSingle(gg_trg_V3_Setup, 1.0)
	call TriggerAddAction(gg_trg_V3_Setup, function Trig_V3_SetupActions)
endfunction
//===========================================================================
// Trigger: V3_Spawn3
//===========================================================================
function Trig_V3_Spawn3Actions takes nothing returns nothing
	if ( ( udg_CreepN[3] < 4 ) ) then
		set udg_TempRealX=I2R(GetRandomInt(1200, 2600))
		set udg_TempRealY=I2R(GetRandomInt(1200, 2600))
		set udg_TempUnit=CreateUnit(Player(11), 'nban', udg_TempRealX, udg_TempRealY, 270)
		call SetUnitUserData(udg_TempUnit, 4)
		call SaveInteger(udg_CreepHash, GetHandleId(udg_TempUnit), 0, 4)
		set udg_CreepN[3]=udg_CreepN[3] + 1
		set udg_LastCreep=udg_TempUnit
		if ( ( IsUnitAliveBJ(udg_HeroP[3]) == true ) ) then
			call IssueTargetOrder(udg_TempUnit, "attack", udg_HeroP[3])
		else
		endif
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_Spawn3 takes nothing returns nothing
	set gg_trg_V3_Spawn3=CreateTrigger()
	call TriggerRegisterTimerEventPeriodic(gg_trg_V3_Spawn3, 4.0)
	call TriggerAddAction(gg_trg_V3_Spawn3, function Trig_V3_Spawn3Actions)
endfunction
//===========================================================================
// Trigger: V3_Spawn2
//===========================================================================
function Trig_V3_Spawn2Actions takes nothing returns nothing
	if ( ( udg_CreepN[2] < 4 ) ) then
		set udg_TempRealX=I2R(GetRandomInt(- 2600, - 1200))
		set udg_TempRealY=I2R(GetRandomInt(1200, 2600))
		set udg_TempUnit=CreateUnit(Player(11), 'nban', udg_TempRealX, udg_TempRealY, 270)
		call SetUnitUserData(udg_TempUnit, 3)
		call SaveInteger(udg_CreepHash, GetHandleId(udg_TempUnit), 0, 3)
		set udg_CreepN[2]=udg_CreepN[2] + 1
		set udg_LastCreep=udg_TempUnit
		if ( ( IsUnitAliveBJ(udg_HeroP[2]) == true ) ) then
			call IssueTargetOrder(udg_TempUnit, "attack", udg_HeroP[2])
		else
		endif
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_Spawn2 takes nothing returns nothing
	set gg_trg_V3_Spawn2=CreateTrigger()
	call TriggerRegisterTimerEventPeriodic(gg_trg_V3_Spawn2, 4.0)
	call TriggerAddAction(gg_trg_V3_Spawn2, function Trig_V3_Spawn2Actions)
endfunction
//===========================================================================
// Trigger: V3_Spawn1
//===========================================================================
function Trig_V3_Spawn1Actions takes nothing returns nothing
	if ( ( udg_CreepN[1] < 4 ) ) then
		set udg_TempRealX=I2R(GetRandomInt(1200, 2600))
		set udg_TempRealY=I2R(GetRandomInt(- 2500, - 1300))
		set udg_TempUnit=CreateUnit(Player(11), 'nban', udg_TempRealX, udg_TempRealY, 270)
		call SetUnitUserData(udg_TempUnit, 2)
		call SaveInteger(udg_CreepHash, GetHandleId(udg_TempUnit), 0, 2)
		set udg_CreepN[1]=udg_CreepN[1] + 1
		set udg_LastCreep=udg_TempUnit
		if ( ( IsUnitAliveBJ(udg_HeroP[1]) == true ) ) then
			call IssueTargetOrder(udg_TempUnit, "attack", udg_HeroP[1])
		else
		endif
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_Spawn1 takes nothing returns nothing
	set gg_trg_V3_Spawn1=CreateTrigger()
	call TriggerRegisterTimerEventPeriodic(gg_trg_V3_Spawn1, 4.0)
	call TriggerAddAction(gg_trg_V3_Spawn1, function Trig_V3_Spawn1Actions)
endfunction
//===========================================================================
// Trigger: V3_Spawn0
//===========================================================================
function Trig_V3_Spawn0Actions takes nothing returns nothing
	if ( ( udg_CreepN[0] < 4 ) ) then
		set udg_TempRealX=I2R(GetRandomInt(- 2600, - 1200))
		set udg_TempRealY=I2R(GetRandomInt(- 2500, - 1300))
		set udg_TempUnit=CreateUnit(Player(11), 'nban', udg_TempRealX, udg_TempRealY, 270)
		call SetUnitUserData(udg_TempUnit, 1)
		call SaveInteger(udg_CreepHash, GetHandleId(udg_TempUnit), 0, 1)
		set udg_CreepN[0]=udg_CreepN[0] + 1
		set udg_LastCreep=udg_TempUnit
		if ( ( IsUnitAliveBJ(udg_HeroP[0]) == true ) ) then
			call IssueTargetOrder(udg_TempUnit, "attack", udg_HeroP[0])
		else
		endif
	else
	endif
endfunction
//===========================================================================
function InitTrig_V3_Spawn0 takes nothing returns nothing
	set gg_trg_V3_Spawn0=CreateTrigger()
	call TriggerRegisterTimerEventPeriodic(gg_trg_V3_Spawn0, 4.0)
	call TriggerAddAction(gg_trg_V3_Spawn0, function Trig_V3_Spawn0Actions)
endfunction
//===========================================================================
// Trigger: V3_Init
//===========================================================================
function Trig_V3_InitActions takes nothing returns nothing
	set udg_H0=CreateUnit(Player(0), 'H000', - 1900, - 1900, 270)
	call PanCameraToTimedLocForPlayer(Player(0), Location(- 1900, - 1900), 0.5)
	set udg_H1=CreateUnit(Player(1), 'H000', 1900, - 1900, 270)
	call PanCameraToTimedLocForPlayer(Player(1), Location(1900, - 1900), 0.5)
	set udg_H2=CreateUnit(Player(2), 'H000', - 1900, 1900, 270)
	call PanCameraToTimedLocForPlayer(Player(2), Location(- 1900, 1900), 0.5)
	set udg_H3=CreateUnit(Player(3), 'H000', 1900, 1900, 270)
	call PanCameraToTimedLocForPlayer(Player(3), Location(1900, 1900), 0.5)
	call DisplayTextToPlayer(Player(0), 0, 0, "四地盘模式：每人一个英雄，各守一块")
	call FogEnable(false)
	call FogMaskEnable(false)
	set udg_CreepHash=InitHashtable()
	call YDWEEnableCreepSleepBJNull(false)
	call SetTimeOfDay(12.0)
	call SetTimeOfDayScale(0.0)
endfunction
//===========================================================================
function InitTrig_V3_Init takes nothing returns nothing
	set gg_trg_V3_Init=CreateTrigger()
	call TriggerRegisterTimerEventSingle(gg_trg_V3_Init, 0.50)
	call TriggerAddAction(gg_trg_V3_Init, function Trig_V3_InitActions)
endfunction
//===========================================================================
function InitCustomTriggers takes nothing returns nothing
	call InitTrig_______u()
	call InitTrig_TST_Chk()
	call InitTrig_V3_CreepDead()
	call InitTrig_V3_Death()
	call InitTrig_V3_Boss()
	call InitTrig_V3_BossKill()
	call InitTrig_V3_Kill()
	call InitTrig_V3_TierUp()
	call InitTrig_V3_Setup()
	call InitTrig_V3_Spawn3()
	call InitTrig_V3_Spawn2()
	call InitTrig_V3_Spawn1()
	call InitTrig_V3_Spawn0()
	call InitTrig_V3_Init()
endfunction
//===========================================================================
function RunInitializationTriggers takes nothing returns nothing
endfunction
function InitCustomPlayerSlots takes nothing returns nothing
	call SetPlayerStartLocation(Player(0), 0)
	call SetPlayerColor(Player(0), ConvertPlayerColor(0))
	call SetPlayerRacePreference(Player(0), RACE_PREF_HUMAN)
	call SetPlayerRaceSelectable(Player(0), false)
	call SetPlayerController(Player(0), MAP_CONTROL_USER)
	call SetPlayerStartLocation(Player(1), 1)
	call SetPlayerColor(Player(1), ConvertPlayerColor(1))
	call SetPlayerRacePreference(Player(1), RACE_PREF_HUMAN)
	call SetPlayerRaceSelectable(Player(1), false)
	call SetPlayerController(Player(1), MAP_CONTROL_USER)
	call SetPlayerStartLocation(Player(2), 2)
	call SetPlayerColor(Player(2), ConvertPlayerColor(2))
	call SetPlayerRacePreference(Player(2), RACE_PREF_HUMAN)
	call SetPlayerRaceSelectable(Player(2), false)
	call SetPlayerController(Player(2), MAP_CONTROL_USER)
	call SetPlayerStartLocation(Player(3), 3)
	call SetPlayerColor(Player(3), ConvertPlayerColor(3))
	call SetPlayerRacePreference(Player(3), RACE_PREF_HUMAN)
	call SetPlayerRaceSelectable(Player(3), false)
	call SetPlayerController(Player(3), MAP_CONTROL_USER)
endfunction
function InitCustomTeams takes nothing returns nothing
	// Force: TRIGSTR_006
	call SetPlayerTeam(Player(0), 0)
	call SetPlayerState(Player(0), PLAYER_STATE_ALLIED_VICTORY, 1)
	call SetPlayerTeam(Player(1), 0)
	call SetPlayerState(Player(1), PLAYER_STATE_ALLIED_VICTORY, 1)
	call SetPlayerTeam(Player(2), 0)
	call SetPlayerState(Player(2), PLAYER_STATE_ALLIED_VICTORY, 1)
	call SetPlayerTeam(Player(3), 0)
	call SetPlayerState(Player(3), PLAYER_STATE_ALLIED_VICTORY, 1)
	call SetPlayerAllianceStateAllyBJ(Player(0), Player(1), true)
	call SetPlayerAllianceStateAllyBJ(Player(0), Player(2), true)
	call SetPlayerAllianceStateAllyBJ(Player(0), Player(3), true)
	call SetPlayerAllianceStateAllyBJ(Player(1), Player(0), true)
	call SetPlayerAllianceStateAllyBJ(Player(1), Player(2), true)
	call SetPlayerAllianceStateAllyBJ(Player(1), Player(3), true)
	call SetPlayerAllianceStateAllyBJ(Player(2), Player(0), true)
	call SetPlayerAllianceStateAllyBJ(Player(2), Player(1), true)
	call SetPlayerAllianceStateAllyBJ(Player(2), Player(3), true)
	call SetPlayerAllianceStateAllyBJ(Player(3), Player(0), true)
	call SetPlayerAllianceStateAllyBJ(Player(3), Player(1), true)
	call SetPlayerAllianceStateAllyBJ(Player(3), Player(2), true)
endfunction
function InitAllyPriorities takes nothing returns nothing
	call SetStartLocPrioCount(0, 3)
	call SetStartLocPrio(0, 0, 1, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrio(0, 1, 2, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrio(0, 2, 3, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrioCount(1, 3)
	call SetStartLocPrio(1, 0, 0, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrio(1, 1, 2, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrio(1, 2, 3, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrioCount(2, 3)
	call SetStartLocPrio(2, 0, 0, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrio(2, 1, 1, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrio(2, 2, 3, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrioCount(3, 3)
	call SetStartLocPrio(3, 0, 0, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrio(3, 1, 1, MAP_LOC_PRIO_HIGH)
	call SetStartLocPrio(3, 2, 2, MAP_LOC_PRIO_HIGH)
endfunction
//===========================================================================
//*
//*  Main Initialization
//*
//===========================================================================
function main takes nothing returns nothing
	call SetCameraBounds(- 3328.000000 + GetCameraMargin(CAMERA_MARGIN_LEFT), - 3584.000000 + GetCameraMargin(CAMERA_MARGIN_BOTTOM), 3328.000000 - GetCameraMargin(CAMERA_MARGIN_RIGHT), 3072.000000 - GetCameraMargin(CAMERA_MARGIN_TOP), - 3328.000000 + GetCameraMargin(CAMERA_MARGIN_LEFT), 3072.000000 - GetCameraMargin(CAMERA_MARGIN_TOP), 3328.000000 - GetCameraMargin(CAMERA_MARGIN_RIGHT), - 3584.000000 + GetCameraMargin(CAMERA_MARGIN_BOTTOM))
	call SetDayNightModels("Environment\\DNC\\DNCLordaeron\\DNCLordaeronTerrain\\DNCLordaeronTerrain.mdl", "Environment\\DNC\\DNCLordaeron\\DNCLordaeronUnit\\DNCLordaeronUnit.mdl")
	call NewSoundEnvironment("Default")
	call SetAmbientDaySound("LordaeronSummerDay")
	call SetAmbientNightSound("LordaeronSummerNight")
	call SetMapMusic("Music", true, 0)
	call InitSounds()
	call InitRandomGroups()
	call CreateRegions()
	call CreateCameras()
	call CreateDestructables()
	call CreateItems()
	call CreateUnits()
	call InitBlizzard()

call ExecuteFunc("YDTriggerSaveLoadSystem__Init")

	call InitGlobals()
	call InitCustomTriggers()
	call RunInitializationTriggers()
endfunction
//===========================================================================
//*
//*  Map Configuration
//*
//===========================================================================
function config takes nothing returns nothing
	call SetMapName("无尽刷怪")
	call SetMapDescription("四人同盟·四地盘·无尽刷怪·破境成神")
	call SetPlayers(4)
	call SetTeams(4)
	call SetGamePlacement(MAP_PLACEMENT_TEAMS_TOGETHER)
	call DefineStartLocation(0, 0.000000, 0.000000)
	call DefineStartLocation(1, 0.000000, 0.000000)
	call DefineStartLocation(2, 0.000000, 0.000000)
	call DefineStartLocation(3, 0.000000, 0.000000)
	call InitCustomPlayerSlots()
	call InitCustomTeams()
	call InitAllyPriorities()
endfunction




//Struct method generated initializers/callers:

