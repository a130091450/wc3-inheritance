#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""M1 剩余页面：两步拼接（不嵌套函数），逐动作存盘。"""
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
core = {c["name"]: c["index"] for c in ed("list_categories")}["无尽传承"]


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
    """先 Msg = I2S(var)，再拼串显示（两步，绝不嵌套）。"""
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
    ed("save_map", file_path=MAP)
    i = idx_of(name)
    ed("add_event", category_index=core, trigger_index=i,
       event_name=event_name, parameters=event_params)
    ed("save_map", file_path=MAP)
    for a in actions:
        ed("add_action", category_index=core, trigger_index=i,
           action_name=a["name"], parameters=a["parameters"], children=a["children"])
        ed("save_map", file_path=MAP)
    print("built", name, len(actions))


# ---------- WX_Tick ----------
hud = []
hud += say_var("品阶 T=", "Tier")
hud += say_var("修为 X=", "XiuWei")
hud += say_var("需求 N=", "XiuNeed")
hud += say_var("时间 S=", "Secs")

tick_actions = [
    setv("integer", "Secs", raw("udg_Secs + 1")),
    setv("integer", "Tick5", raw("udg_Tick5 + 1")),
    if_then("OperatorCompareInteger", [gvar("integer", "Tick5"), GE, lit("integer", "5")],
            [setv("integer", "Tick5", lit("integer", "0"))] + hud, []),
    if_then("OperatorCompareBoolean",
            [fn("boolean", "IsUnitAliveBJ", gvar("unit", "Altar")), EQ, lit("boolean", "true")],
            [], [say("祭坛被摧毁，本局结束")]),
]
build("WX_Tick", "每秒计时 + 状态显示", "TriggerRegisterTimerEventPeriodic", [lit("real", "1.0")],
      tick_actions)

# ---------- WX_Spawn ----------
spawn_actions = [
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
]
build("WX_Spawn", "无尽刷怪（阶梯加量）", "TriggerRegisterTimerEventPeriodic", [lit("real", "10.0")],
      spawn_actions)

# ---------- WX_Kill ----------
kill_actions = [
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
                                      preset("showhideoption", "ShowHideShow"))],
                                 [])],
                        []),
            ], []),
]
build("WX_Kill", "击杀加修为，满值弹突破", "TriggerRegisterAnyUnitEventBJ",
      [preset("playerunitevent", "PlayerUnitEventDeath")], kill_actions)

# ---------- WX_Choice ----------
choice_actions = [
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
] + say_var("当前品阶 T=", "Tier")
build("WX_Choice", "突破选择回调（事件由 Init 动态注册）",
      "TriggerRegisterTimerEventPeriodic", [lit("real", "3600.0")], choice_actions)

print("M1b DONE")
