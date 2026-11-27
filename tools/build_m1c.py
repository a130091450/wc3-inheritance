#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""M1 全量重建到健康分类 M1。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, if_then, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")
NA = preset("player", "PlayerNA")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")
GE = preset("ComparisonOperator", "OperatorGreaterEq")

ed = Editor()
cats = {c["name"]: c["index"] for c in ed("list_categories")}
core = cats.get("M1")
if core is None:
    core = ed("create_category", name="M1")["index"]
print("category M1 =", core)


def idx_of(name):
    for t in ed("list_triggers", category_index=core)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


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


def build(name, comment, event_name, event_params, actions):
    for t in ed("list_triggers", category_index=core)["triggers"]:
        if t["name"] == name:
            ed("delete_trigger", category_index=core, trigger_index=t["trigger_index"])
    ed("create_trigger", category_index=core, name=name, comment=comment)
    i = idx_of(name)
    ed("add_event", category_index=core, trigger_index=i,
       event_name=event_name, parameters=event_params)
    for a in actions:
        ed("add_action", category_index=core, trigger_index=i,
           action_name=a["name"], parameters=a["parameters"], children=a["children"])
    ed("save_map", file_path=MAP)
    print("built", name, len(actions))


# WX_Init
build("WX_Init", "开局：祭坛+英雄+突破对话框", "TriggerRegisterTimerEventSingle", [lit("real", "0.50")], [
    setv("unit", "Altar", fn("unit", "CreateUnit", P1, lit("unitcode", "hcas"),
                             lit("real", "0"), lit("real", "0"), lit("real", "270"))),
    setv("unit", "Hero", fn("unit", "CreateUnit", P1, lit("unitcode", "Hmkg"),
                            lit("real", "0"), lit("real", "-512"), lit("real", "270"))),
    setv("boolean", "HeroPicked", lit("boolean", "true")),
    act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
    act("PanCameraToTimed", lit("real", "0"), lit("real", "-512"), lit("real", "0.5")),
    setv("dialog", "DlgBreak", fn("dialog", "DialogCreate")),
    act("DialogSetMessageBJ", gvar("dialog", "DlgBreak"), lit("string", "选择突破方向")),
    act("DialogAddButtonBJ", gvar("dialog", "DlgBreak"), lit("string", "力量 +6")),
    setv("button", "Bk1", fn("button", "GetLastCreatedButtonBJ")),
    act("DialogAddButtonBJ", gvar("dialog", "DlgBreak"), lit("string", "敏捷 +6")),
    setv("button", "Bk2", fn("button", "GetLastCreatedButtonBJ")),
    act("DialogAddButtonBJ", gvar("dialog", "DlgBreak"), lit("string", "修为 +20%")),
    setv("button", "Bk3", fn("button", "GetLastCreatedButtonBJ")),
    act("CustomScriptCode", lit("scriptcode",
        "call TriggerRegisterDialogEvent(gg_trg_WX_Choice, udg_DlgBreak)")),
    say("杀怪攒修为，修为满会自动弹出突破选择。守住祭坛！"),
])

# WX_Tick
hud = say_var("品阶 T=", "Tier") + say_var("修为 X=", "XiuWei") + \
      say_var("需求 N=", "XiuNeed") + say_var("时间 S=", "Secs")
build("WX_Tick", "每秒计时 + 状态显示", "TriggerRegisterTimerEventPeriodic", [lit("real", "1.0")], [
    setv("integer", "Secs", raw("udg_Secs + 1")),
    setv("integer", "Tick5", raw("udg_Tick5 + 1")),
    if_then("OperatorCompareInteger", [gvar("integer", "Tick5"), GE, lit("integer", "5")],
            [setv("integer", "Tick5", lit("integer", "0"))] + hud, []),
])

# WX_Spawn
build("WX_Spawn", "无尽刷怪", "TriggerRegisterTimerEventPeriodic", [lit("real", "10.0")], [
    setv("integer", "TempInt", raw("4 + udg_Secs / 600")),
    if_then("OperatorCompareInteger", [gvar("integer", "TempInt"), GE, lit("integer", "6")],
            [setv("integer", "TempInt", lit("integer", "6"))], []),
    setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                lit("real", "-2600"), lit("real", "2600"), lit("real", "270"))),
    setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                lit("real", "2600"), lit("real", "2600"), lit("real", "270"))),
    setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                lit("real", "-2600"), lit("real", "-2600"), lit("real", "270"))),
    setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                lit("real", "2600"), lit("real", "-2600"), lit("real", "270"))),
    if_then("OperatorCompareInteger", [gvar("integer", "TempInt"), GE, lit("integer", "5")],
            [setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                         lit("real", "0"), lit("real", "2800"), lit("real", "270")))], []),
    if_then("OperatorCompareInteger", [gvar("integer", "TempInt"), GE, lit("integer", "6")],
            [setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                         lit("real", "0"), lit("real", "-2800"), lit("real", "270")))], []),
])

# WX_Kill
build("WX_Kill", "击杀加修为", "TriggerRegisterAnyUnitEventBJ",
      [preset("playerunitevent", "PlayerUnitEventDeath")], [
    setv("unit", "TempUnit", fn("unit", "GetDyingUnit")),
    setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))),
    if_then("OperatorComparePlayer", [gvar("player", "TempPl"), EQ, NA],
            [
                setv("integer", "XiuWei", raw("udg_XiuWei + 10 + udg_XiuBonus / 5")),
                if_then("OperatorCompareInteger",
                        [gvar("integer", "XiuWei"), GE, gvar("integer", "XiuNeed")],
                        [if_then("OperatorCompareBoolean",
                                 [gvar("boolean", "BreakReady"), EQ, lit("boolean", "false")],
                                 [setv("boolean", "BreakReady", lit("boolean", "true")),
                                  act("DialogDisplay", P1, gvar("dialog", "DlgBreak"),
                                      preset("showhideoption", "ShowHideShow"))], [])], []),
            ], []),
])

# WX_Choice
build("WX_Choice", "突破选择回调", "TriggerRegisterTimerEventPeriodic", [lit("real", "3600.0")], [
    act("DialogDisplay", P1, gvar("dialog", "DlgBreak"), preset("showhideoption", "ShowHideHide")),
    if_then("OperatorCompareUnit", [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk1")],
            [setv("integer", "TempInt", raw("GetHeroStr(udg_Hero, true) + 6")),
             act("SetHeroStr", gvar("unit", "Hero"), gvar("integer", "TempInt"),
                 preset("enabledisableoption", "EnableDisableEnable"))], []),
    if_then("OperatorCompareUnit", [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk2")],
            [setv("integer", "TempInt", raw("GetHeroAgi(udg_Hero, true) + 6")),
             act("SetHeroAgi", gvar("unit", "Hero"), gvar("integer", "TempInt"),
                 preset("enabledisableoption", "EnableDisableEnable"))], []),
    if_then("OperatorCompareUnit", [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk3")],
            [setv("integer", "XiuBonus", raw("udg_XiuBonus + 20"))], []),
    setv("integer", "Tier", raw("udg_Tier + 1")),
    setv("integer", "XiuWei", lit("integer", "0")),
    setv("integer", "XiuNeed", raw("udg_XiuNeed * 3 / 2")),
    setv("boolean", "BreakReady", lit("boolean", "false")),
    say("突破成功！"),
] + say_var("当前品阶 T=", "Tier"))

print("M1c DONE")
