#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""在全新地图上重建《无尽传承》v2：固定总数 12、死一个补一个、随机位置。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, if_then, act

MAP = "C:/Users/Administrator/Desktop/testmap/无尽传承.w3x"
P1 = preset("player", "Player00")
NA = preset("player", "PlayerNA")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")
GE = preset("ComparisonOperator", "OperatorGreaterEq")
LT = preset("ComparisonOperator", "OperatorLess")

ed = Editor()
cats = {c["name"]: c["index"] for c in ed("list_categories")}
core = cats.get("无尽传承")
if core is None:
    core = ed("create_category", name="无尽传承")["index"]
print("category:", core)

have = {v["name"] for v in ed("list_variables", limit=400)["variables"]}
for name, typ, init in [
    ("Hero", "unit", None), ("HeroPicked", "boolean", "false"),
    ("Tier", "integer", "1"), ("XiuWei", "integer", "0"),
    ("XiuNeed", "integer", "100"), ("XiuBonus", "integer", "0"),
    ("Secs", "integer", "0"), ("Tick5", "integer", "0"),
    ("Deaths", "integer", "0"), ("IsOver", "boolean", "false"),
    ("BreakReady", "boolean", "false"),
    ("DlgBreak", "dialog", None), ("Bk1", "button", None),
    ("Bk2", "button", None), ("Bk3", "button", None),
    ("Msg", "string", None), ("TempInt", "integer", "0"),
    ("TempUnit", "unit", None), ("TempPl", "player", None),
    ("TempGroup", "group", None),
    ("TempRealX", "real", "0"), ("TempRealY", "real", "0"),
]:
    if name in have:
        continue
    kw = dict(name=name, type=typ, is_array=False)
    if init is not None:
        kw["initial_value"] = init
    ed("create_variable", **kw)
ed("save_map", file_path=MAP)
print("vars ok")


def idx_of(n):
    for t in ed("list_triggers", category_index=core)["triggers"]:
        if t["name"] == n:
            return t["trigger_index"]
    raise KeyError(n)


def setv(t, n, v):
    return act("SetVariable", gvar(t, n), v)


def say(text):
    return act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"), lit("string", text))


def say_var(prefix, var):
    return [
        setv("string", "Msg", fn("string", "I2S", gvar("integer", var))),
        act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
            fn("string", "YDWEOperatorString3", lit("string", prefix),
               gvar("string", "Msg"), lit("string", ""))),
    ]


def creep_at(x, y):
    return [
        setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                    lit("real", x), lit("real", y), lit("real", "270"))),
        act("IssueTargetOrder", gvar("unit", "TempUnit"),
            preset("unitorderutarg", "UnitOrderAttackUnit"), gvar("unit", "Hero")),
    ]


def build(name, comment, ev, evp, actions):
    for t in ed("list_triggers", category_index=core)["triggers"]:
        if t["name"] == name:
            ed("delete_trigger", category_index=core, trigger_index=t["trigger_index"])
    ed("create_trigger", category_index=core, name=name, comment=comment)
    i = idx_of(name)
    ed("add_event", category_index=core, trigger_index=i, event_name=ev, parameters=evp)
    for a in actions:
        ed("add_action", category_index=core, trigger_index=i,
           action_name=a["name"], parameters=a["parameters"], children=a["children"])
    ed("save_map", file_path=MAP)
    print("built", name, len(actions), flush=True)


# 1) 初始化
build("V2_Init", "开局", "TriggerRegisterTimerEventSingle", [lit("real", "0.50")], [
    setv("unit", "Hero", fn("unit", "CreateUnit", P1, lit("unitcode", "Hmkg"),
                            lit("real", "0"), lit("real", "-512"), lit("real", "270"))),
    setv("boolean", "HeroPicked", lit("boolean", "true")),
    act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
    act("PanCameraToTimed", lit("real", "0"), lit("real", "-512"), lit("real", "0.5")),
    act("FogEnable", preset("enableddisabledoption", "EnabledDisabledDisabled")),
    act("FogMaskEnable", preset("enableddisabledoption", "EnabledDisabledDisabled")),
    setv("dialog", "DlgBreak", fn("dialog", "DialogCreate")),
    act("DialogSetMessageBJ", gvar("dialog", "DlgBreak"), lit("string", "选择突破方向")),
    act("DialogAddButtonBJ", gvar("dialog", "DlgBreak"), lit("string", "力量 +6")),
    setv("button", "Bk1", fn("button", "GetLastCreatedButtonBJ")),
    act("DialogAddButtonBJ", gvar("dialog", "DlgBreak"), lit("string", "敏捷 +6")),
    setv("button", "Bk2", fn("button", "GetLastCreatedButtonBJ")),
    act("DialogAddButtonBJ", gvar("dialog", "DlgBreak"), lit("string", "修为 +20%")),
    setv("button", "Bk3", fn("button", "GetLastCreatedButtonBJ")),
    act("CustomScriptCode", lit("scriptcode",
        "call TriggerRegisterDialogEvent(gg_trg_V2_Choice, udg_DlgBreak)")),
    say("地图上恒定 12 只怪，杀一只补一只。守住自己，别死超过 3 次。"),
])

# 2) 计时 HUD
hud = say_var("品阶 T=", "Tier") + say_var("修为 X=", "XiuWei") + \
      say_var("需求 N=", "XiuNeed") + say_var("时间 S=", "Secs")
build("V2_Tick", "计时HUD", "TriggerRegisterTimerEventPeriodic", [lit("real", "1.0")], [
    setv("integer", "Secs", raw("udg_Secs + 1")),
    setv("integer", "Tick5", raw("udg_Tick5 + 1")),
    if_then("OperatorCompareInteger", [gvar("integer", "Tick5"), GE, lit("integer", "5")],
            [setv("integer", "Tick5", lit("integer", "0"))] + hud, []),
])

# 3) 初始铺 8 只
init_acts = []
for x, y in [("-2000", "2000"), ("0", "2400"), ("2000", "2000"), ("-2400", "0"),
             ("2400", "0"), ("-2000", "-2000"), ("0", "-2400"), ("2000", "-2000")]:
    init_acts += creep_at(x, y)
build("V2_SpawnInit", "初始铺怪", "TriggerRegisterTimerEventSingle", [lit("real", "1.0")], init_acts)

# 4) 击杀：加修为 + 补怪（总数上限 12）
respawn = if_then("OperatorCompareInteger",
                  [gvar("integer", "TempInt"), LT, lit("integer", "12")],
                  [
                      setv("integer", "TempInt", fn("integer", "GetRandomInt",
                                                    lit("integer", "-2800"), lit("integer", "2800"))),
                      setv("real", "TempRealX", fn("real", "I2R", gvar("integer", "TempInt"))),
                      setv("integer", "TempInt", fn("integer", "GetRandomInt",
                                                    lit("integer", "-2800"), lit("integer", "2800"))),
                      setv("real", "TempRealY", fn("real", "I2R", gvar("integer", "TempInt"))),
                      setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                                  gvar("real", "TempRealX"), gvar("real", "TempRealY"),
                                                  lit("real", "270"))),
                      act("IssueTargetOrder", gvar("unit", "TempUnit"),
                          preset("unitorderutarg", "UnitOrderAttackUnit"), gvar("unit", "Hero")),
                  ], [])
build("V2_Kill", "击杀加修为+补怪", "TriggerRegisterAnyUnitEventBJ",
      [preset("playerunitevent", "PlayerUnitEventDeath")], [
          setv("unit", "TempUnit", fn("unit", "GetDyingUnit")),
          setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))),
          if_then("OperatorComparePlayer", [gvar("player", "TempPl"), EQ, NA], [
              setv("integer", "XiuWei", raw("udg_XiuWei + 10 + udg_XiuBonus / 5")),
              if_then("OperatorCompareInteger",
                      [gvar("integer", "XiuWei"), GE, gvar("integer", "XiuNeed")], [
                          if_then("OperatorCompareBoolean",
                                  [gvar("boolean", "BreakReady"), EQ, lit("boolean", "false")], [
                                      setv("boolean", "BreakReady", lit("boolean", "true")),
                                      act("DialogDisplay", P1, gvar("dialog", "DlgBreak"),
                                          preset("showhideoption", "ShowHideShow"))], [])], []),
              setv("group", "TempGroup", fn("group", "GetUnitsOfPlayerAll", NA)),
              setv("integer", "TempInt", fn("integer", "CountUnitsInGroup", gvar("group", "TempGroup"))),
              act("DestroyGroup", gvar("group", "TempGroup")),
              respawn,
          ], []),
      ])

# 5) 突破选择
build("V2_Choice", "突破回调", "TriggerRegisterTimerEventPeriodic", [lit("real", "3600.0")], [
    act("DialogDisplay", P1, gvar("dialog", "DlgBreak"), preset("showhideoption", "ShowHideHide")),
    if_then("OperatorCompareUnit", [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk1")], [
        setv("integer", "TempInt", raw("GetHeroStr(udg_Hero, true) + 6")),
        act("SetHeroStr", gvar("unit", "Hero"), gvar("integer", "TempInt"),
            preset("enabledisableoption", "EnableDisableEnable"))], []),
    if_then("OperatorCompareUnit", [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk2")], [
        setv("integer", "TempInt", raw("GetHeroAgi(udg_Hero, true) + 6")),
        act("SetHeroAgi", gvar("unit", "Hero"), gvar("integer", "TempInt"),
            preset("enabledisableoption", "EnableDisableEnable"))], []),
    if_then("OperatorCompareUnit", [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk3")], [
        setv("integer", "XiuBonus", raw("udg_XiuBonus + 20"))], []),
    setv("integer", "Tier", raw("udg_Tier + 1")),
    setv("integer", "XiuWei", lit("integer", "0")),
    setv("integer", "XiuNeed", raw("udg_XiuNeed * 3 / 2")),
    setv("boolean", "BreakReady", lit("boolean", "false")),
    say("突破成功！"),
] + say_var("当前品阶 T=", "Tier"))

# 6) 阵亡处理
build("V2_Death", "阵亡计数", "TriggerRegisterAnyUnitEventBJ",
      [preset("playerunitevent", "PlayerUnitEventDeath")], [
          if_then("OperatorCompareUnit", [fn("unit", "GetDyingUnit"), EQ, gvar("unit", "Hero")], [
              setv("integer", "Deaths", raw("udg_Deaths + 1")),
              if_then("OperatorCompareInteger", [gvar("integer", "Deaths"), GE, lit("integer", "3")], [
                  setv("boolean", "IsOver", lit("boolean", "true")),
                  say("三次阵亡，本局结束"),
              ], [
                  act("ReviveHero", gvar("unit", "Hero"), lit("real", "0"), lit("real", "-512"),
                      preset("showhideoption", "ShowHideShow")),
                  say("阵亡，已原地复活（上限 3 次）"),
              ]),
          ], []),
      ])

print("ALL DONE")
