#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""M1: 无尽传承 - 品阶/修为/三选一/无尽刷怪/计时。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, if_then, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")
NA = preset("player", "PlayerNA")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")
CMP = preset("ComparisonOperator", "OperatorEqual")

ed = Editor()
cats = {c["name"]: c["index"] for c in ed("list_categories")}

# 1) 停用旧 demo 的页面（保留可参考）
if "Demo" in cats:
    for t in ed("list_triggers", category_index=cats["Demo"])["triggers"]:
        if t["enabled"]:
            ed("set_trigger_enabled", category_index=cats["Demo"],
               trigger_index=t["trigger_index"], enabled=False)
    ed("save_map", file_path=MAP)
    print("disabled Demo triggers")

# 2) 新分类
if "无尽传承" in cats:
    core = cats["无尽传承"]
else:
    core = ed("create_category", name="无尽传承")["index"]
    ed("save_map", file_path=MAP)
print("category 无尽传承 =", core)

# 3) 变量
have = {v["name"] for v in ed("list_variables", limit=300)["variables"]}
for name, typ, init in [
    ("Altar", "unit", None),
    ("Tier", "integer", "1"),
    ("XiuWei", "integer", "0"),
    ("XiuNeed", "integer", "100"),
    ("XiuBonus", "integer", "0"),
    ("Secs", "integer", "0"),
    ("Tick5", "integer", "0"),
    ("BreakReady", "boolean", "false"),
    ("DlgBreak", "dialog", None),
    ("Bk1", "button", None),
    ("Bk2", "button", None),
    ("Bk3", "button", None),
    ("Msg", "string", None),
    ("TempInt", "integer", "0"),
]:
    if name in have:
        continue
    kw = dict(name=name, type=typ, is_array=False)
    if init is not None:
        kw["initial_value"] = init
    ed("create_variable", **kw)
ed("save_map", file_path=MAP)
print("variables ok")


def idx_of(name):
    for t in ed("list_triggers", category_index=core)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


def setv(t, n, v):
    return act("SetVariable", gvar(t, n), v)


def say(text):
    return act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"), lit("string", text))


def say_num(prefix, var, typ="integer"):
    return act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
               fn("string", "YDWEOperatorString3", lit("string", prefix),
                  fn("string", "I2S", gvar(typ, var)), lit("string", "")))


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


# ---------- WX_Init ----------
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
    act("DialogAddButtonBJ", gvar("dialog", "DlgBreak"), lit("string", "修为获取 +20%")),
    setv("button", "Bk3", fn("button", "GetLastCreatedButtonBJ")),
    act("CustomScriptCode", lit("scriptcode",
        "call TriggerRegisterDialogEvent(gg_trg_WX_Choice, udg_DlgBreak)")),
    say("杀怪攒修为，修为满会自动弹出突破选择。守住祭坛！"),
])

# ---------- WX_Tick ----------
build("WX_Tick", "每秒计时 + 状态显示", "TriggerRegisterTimerEventPeriodic", [lit("real", "1.0")], [
    setv("integer", "Secs", raw("udg_Secs + 1")),
    setv("integer", "Tick5", raw("udg_Tick5 + 1")),
    if_then("OperatorCompareInteger",
            [gvar("integer", "Tick5"), preset("ComparisonOperator", "OperatorGreaterEq"),
             lit("integer", "5")],
            [
                setv("integer", "Tick5", lit("integer", "0")),
                say_num("品阶 T=", "Tier"),
                say_num("修为 X=", "XiuWei"),
                say_num("需求 N=", "XiuNeed"),
                say_num("时间 S=", "Secs"),
            ]),
    if_then("OperatorCompareBoolean",
            [fn("boolean", "IsUnitAliveBJ", gvar("unit", "Altar")), EQ, lit("boolean", "true")],
            [], [say("祭坛被摧毁，本局结束"), act("ReturnAction")]),
])

# ---------- WX_Spawn ----------
build("WX_Spawn", "无尽刷怪：四角刷怪，每分钟加量", "TriggerRegisterTimerEventPeriodic", [lit("real", "10.0")], [
    setv("integer", "TempInt", raw("4 + udg_Secs / 600")),
    if_then("OperatorCompareInteger",
            [gvar("integer", "TempInt"), preset("ComparisonOperator", "OperatorGreater"),
             lit("integer", "6")],
            [setv("integer", "TempInt", lit("integer", "6"))]),
    if_then("OperatorCompareInteger",
            [gvar("integer", "TempInt"), preset("ComparisonOperator", "OperatorGreaterEq"),
             lit("integer", "1")],
            [setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                         lit("real", "-2600"), lit("real", "2600"), lit("real", "270")))]),
    if_then("OperatorCompareInteger",
            [gvar("integer", "TempInt"), preset("ComparisonOperator", "OperatorGreaterEq"),
             lit("integer", "2")],
            [setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                         lit("real", "2600"), lit("real", "2600"), lit("real", "270")))]),
    if_then("OperatorCompareInteger",
            [gvar("integer", "TempInt"), preset("ComparisonOperator", "OperatorGreaterEq"),
             lit("integer", "3")],
            [setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                         lit("real", "-2600"), lit("real", "-2600"), lit("real", "270")))]),
    if_then("OperatorCompareInteger",
            [gvar("integer", "TempInt"), preset("ComparisonOperator", "OperatorGreaterEq"),
             lit("integer", "4")],
            [setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                         lit("real", "2600"), lit("real", "-2600"), lit("real", "270")))]),
    if_then("OperatorCompareInteger",
            [gvar("integer", "TempInt"), preset("ComparisonOperator", "OperatorGreaterEq"),
             lit("integer", "5")],
            [setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                         lit("real", "0"), lit("real", "2800"), lit("real", "270")))]),
    if_then("OperatorCompareInteger",
            [gvar("integer", "TempInt"), preset("ComparisonOperator", "OperatorGreaterEq"),
             lit("integer", "6")],
            [setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                         lit("real", "0"), lit("real", "-2800"), lit("real", "270")))]),
])

# ---------- WX_Kill ----------
build("WX_Kill", "击杀加修为，满值弹突破", "TriggerRegisterAnyUnitEventBJ",
      [preset("playerunitevent", "PlayerUnitEventDeath")], [
    setv("unit", "TempUnit", fn("unit", "GetDyingUnit")),
    setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))),
    if_then("OperatorComparePlayer",
            [gvar("player", "TempPl"), EQ, NA],
            [
                setv("integer", "XiuWei", raw("udg_XiuWei + 10 + udg_XiuBonus / 5")),
                if_then("OperatorCompareInteger",
                        [gvar("integer", "XiuWei"),
                         preset("ComparisonOperator", "OperatorGreaterEq"),
                         gvar("integer", "XiuNeed")],
                        [if_then("OperatorCompareBoolean",
                                 [gvar("boolean", "BreakReady"), EQ, lit("boolean", "false")],
                                 [setv("boolean", "BreakReady", lit("boolean", "true")),
                                  act("DialogDisplay", P1, gvar("dialog", "DlgBreak"),
                                      preset("showhideoption", "ShowHideShow"))],
                                 [])],
                        []),
            ]),
])

# ---------- WX_Choice ----------
build("WX_Choice", "突破选择回调（事件由 Init 动态注册）", "TriggerRegisterTimerEventPeriodic",
      [lit("real", "3600.0")], [
    act("DialogDisplay", P1, gvar("dialog", "DlgBreak"), preset("showhideoption", "ShowHideHide")),
    if_then("OperatorCompareUnit",
            [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk1")],
            [setv("integer", "TempInt", raw("GetHeroStr(udg_Hero, true) + 6")),
             act("SetHeroStr", gvar("unit", "Hero"), gvar("integer", "TempInt"),
                 preset("enabledisableoption", "EnableDisableEnable"))],
            []),
    if_then("OperatorCompareUnit",
            [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk2")],
            [setv("integer", "TempInt", raw("GetHeroAgi(udg_Hero, true) + 6")),
             act("SetHeroAgi", gvar("unit", "Hero"), gvar("integer", "TempInt"),
                 preset("enabledisableoption", "EnableDisableEnable"))],
            []),
    if_then("OperatorCompareUnit",
            [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "Bk3")],
            [setv("integer", "XiuBonus", raw("udg_XiuBonus + 20"))],
            []),
    setv("integer", "Tier", raw("udg_Tier + 1")),
    setv("integer", "XiuWei", lit("integer", "0")),
    setv("integer", "XiuNeed", raw("udg_XiuNeed * 3 / 2")),
    setv("boolean", "BreakReady", lit("boolean", "false")),
    say("突破成功！"),
    say_num("当前品阶 T=", "Tier"),
])

print("M1 DONE")
