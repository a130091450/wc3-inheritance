#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the hero-selection / training-room demo (idempotent, saves after each trigger)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, if_then, act

DEMO_NAME = "Demo"
MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")
NA = preset("player", "PlayerNA")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")


def setv(typ, name, value):
    return act("SetVariable", gvar(typ, name), value)


def show(text, player=None):
    return act(
        "DisplayTextToPlayer",
        player or P1,
        lit("real", "0"),
        lit("real", "0"),
        lit("string", text),
    )


def pan(x, y, t):
    return act("PanCameraToTimed", lit("real", x), lit("real", y), lit("real", t))


def ping(x, y, t):
    return act("PingMinimap", lit("real", x), lit("real", y), lit("real", t))


ed = Editor()

# ---------- setup: category / variables / regions ----------
cats = ed("list_categories")
demo = None
for c in cats:
    if c["name"] == DEMO_NAME:
        demo = c["index"]
if demo is None:
    demo = ed("create_category", name=DEMO_NAME)["index"]
print("category Demo =", demo)

have = {v["name"] for v in ed("list_variables", limit=200)["variables"]}
for name, typ, init in [
    ("HeroDialog", "dialog", None),
    ("Wave", "integer", "0"),
    ("Hero", "unit", None),
    ("InTrain", "boolean", "false"),
    ("HeroType", "unitcode", None),
    ("BtnP", "button", None),
    ("BtnA", "button", None),
    ("BtnI", "button", None),
    ("TempUnit", "unit", None),
    ("TempPl", "player", None),
    ("TempInt", "integer", "0"),
    ("TempGroup", "group", None),
    ("Msg", "string", None),
    ("HeroPicked", "boolean", "false"),
    ("Killer", "unit", None),
]:
    if name in have:
        continue
    kwargs = dict(name=name, type=typ, is_array=False)
    if init is not None:
        kwargs["initial_value"] = init
    ed("create_variable", **kwargs)
print("variables ok")

regs = {r["name"] for r in ed("list_regions")["regions"]}
if "BaseArea" not in regs:
    ed("create_region", name="BaseArea", left=-2816.0, right=-1792.0, bottom=-2816.0, top=-1792.0)
if "TrainArea" not in regs:
    ed("create_region", name="TrainArea", left=1664.0, right=2944.0, bottom=1664.0, top=2944.0)
print("regions ok")

# ---------- triggers ----------
specs = [
    ("Demo_Init", "开局：建基地 + 英雄选择对话框"),
    ("Demo_Pick", "点击英雄按钮 -> 创建英雄"),
    ("Demo_F2", "F2 进入练功房"),
    ("Demo_F3", "F3 返回基地"),
    ("Demo_Spawn", "练功房刷怪"),
    ("Demo_Reward", "击杀奖励"),
]
existing = {t["name"]: t["trigger_index"] for t in ed("list_triggers", category_index=demo)["triggers"]}
for name, comment in specs:
    if name not in existing:
        ed("create_trigger", category_index=demo, name=name, comment=comment)


def idx_of(name):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


def add(trg, action):
    ed("add_action", category_index=demo, trigger_index=idx_of(trg),
       action_name=action["name"], parameters=action["parameters"], children=action["children"])


def event(trg, name, params):
    ed("add_event", category_index=demo, trigger_index=idx_of(trg),
       event_name=name, parameters=params)


def save():
    ed("save_map", file_path=MAP)


def built(name):
    trigs = ed("list_triggers", category_index=demo)["triggers"]
    for t in trigs:
        if t["name"] == name:
            return t["action_count"] > 0
    return False


# ============ T1 Demo_Init ============
if not built("Demo_Init"):
    event("Demo_Init", "TriggerRegisterTimerEventSingle", [lit("real", "0.10")])
    for a in [
        setv("unit", "TempUnit", fn("unit", "CreateUnit", P1, lit("unitcode", "hcas"),
                                    lit("real", "-2304"), lit("real", "-2304"), lit("real", "270"))),
        setv("unit", "TempUnit", fn("unit", "CreateUnit", P1, lit("unitcode", "hgtw"),
                                    lit("real", "-2640"), lit("real", "-2304"), lit("real", "270"))),
        setv("unit", "TempUnit", fn("unit", "CreateUnit", P1, lit("unitcode", "hgtw"),
                                    lit("real", "-1968"), lit("real", "-2304"), lit("real", "270"))),
        setv("dialog", "HeroDialog", fn("dialog", "DialogCreate")),
        act("DialogSetMessageBJ", gvar("dialog", "HeroDialog"), lit("string", "请选择你的英雄")),
        act("DialogAddButtonBJ", gvar("dialog", "HeroDialog"), lit("string", "|cffc0c0c0力量|r · 山丘之王")),
        setv("button", "BtnP", fn("button", "GetLastCreatedButtonBJ")),
        act("DialogAddButtonBJ", gvar("dialog", "HeroDialog"), lit("string", "|cff00ff00敏捷|r · 剑圣")),
        setv("button", "BtnA", fn("button", "GetLastCreatedButtonBJ")),
        act("DialogAddButtonBJ", gvar("dialog", "HeroDialog"), lit("string", "|cff8080ff智力|r · 大法师")),
        setv("button", "BtnI", fn("button", "GetLastCreatedButtonBJ")),
        act("DialogDisplay", P1, gvar("dialog", "HeroDialog"), preset("showhideoption", "ShowHideShow")),
        show("选好英雄后：|cffffcc00F2|r 进练功房，|cffffcc00F3|r 回基地"),
        pan("-2304", "-2304", "0.5"),
    ]:
        add("Demo_Init", a)
    save()
    print("Demo_Init built & saved")

# ============ T2 Demo_Pick ============
if not built("Demo_Pick"):
    event("Demo_Pick", "TriggerRegisterDialogEventBJ", [gvar("dialog", "HeroDialog")])
    for a in [
        act("DialogDisplay", P1, gvar("dialog", "HeroDialog"), preset("showhideoption", "ShowHideHide")),
        setv("unitcode", "HeroType", lit("unitcode", "Hmkg")),
        if_then("OperatorCompareUnit",
                [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "BtnA")],
                [setv("unitcode", "HeroType", lit("unitcode", "Obla"))]),
        if_then("OperatorCompareUnit",
                [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "BtnI")],
                [setv("unitcode", "HeroType", lit("unitcode", "Hjai"))]),
        setv("unit", "Hero", fn("unit", "CreateUnit", P1, gvar("unitcode", "HeroType"),
                                lit("real", "-2304"), lit("real", "-2080"), lit("real", "270"))),
        setv("boolean", "HeroPicked", lit("boolean", "true")),
        act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
        pan("-2304", "-2080", "0.6"),
        ping("-2304", "-2080", "1.5"),
        show("英雄已就位，按 |cffffcc00F2|r 进入练功房"),
    ]:
        add("Demo_Pick", a)
    save()
    print("Demo_Pick built & saved")

# ============ T3 Demo_F2 ============
if not built("Demo_F2"):
    event("Demo_F2", "DzTriggerRegisterKeyEventTrg",
          [preset("gamekeyaction", "GameKeyAction_Press"), preset("gamekey", "GameKey_F2")])
    for a in [
        if_then("OperatorCompareBoolean",
                [gvar("boolean", "HeroPicked"), EQ, lit("boolean", "true")],
                [], [show("请先选择英雄"), act("ReturnAction")]),
        act("DzSetUnitXY", gvar("unit", "Hero"), lit("real", "2304"), lit("real", "2304")),
        setv("boolean", "InTrain", lit("boolean", "true")),
        act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
        pan("2304", "2304", "0.8"),
        ping("2304", "2304", "1.5"),
        show("已进入练功房，|cff00ff00F3|r 返回基地"),
    ]:
        add("Demo_F2", a)
    save()
    print("Demo_F2 built & saved")

# ============ T4 Demo_F3 ============
if not built("Demo_F3"):
    event("Demo_F3", "DzTriggerRegisterKeyEventTrg",
          [preset("gamekeyaction", "GameKeyAction_Press"), preset("gamekey", "GameKey_F3")])
    for a in [
        if_then("OperatorCompareBoolean",
                [gvar("boolean", "HeroPicked"), EQ, lit("boolean", "true")],
                [], [show("请先选择英雄"), act("ReturnAction")]),
        act("DzSetUnitXY", gvar("unit", "Hero"), lit("real", "-2304"), lit("real", "-2080")),
        setv("boolean", "InTrain", lit("boolean", "false")),
        act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
        pan("-2304", "-2080", "0.8"),
        ping("-2304", "-2080", "1.5"),
        show("已返回基地，|cff00ff00F2|r 前往练功房"),
    ]:
        add("Demo_F3", a)
    save()
    print("Demo_F3 built & saved")

# ============ T5 Demo_Spawn ============
if not built("Demo_Spawn"):
    event("Demo_Spawn", "TriggerRegisterTimerEventPeriodic", [lit("real", "8.0")])
    for a in [
        if_then("OperatorCompareBoolean",
                [gvar("boolean", "InTrain"), EQ, lit("boolean", "true")],
                [], [act("ReturnAction")]),
        setv("group", "TempGroup", fn("group", "GetUnitsInRectAll", gvar("rect", "gg_rct_TrainArea"))),
        if_then("OperatorCompareInteger",
                [fn("integer", "CountUnitsInGroup", gvar("group", "TempGroup")),
                 preset("ComparisonOperator", "OperatorGreater"), lit("integer", "16")],
                [act("DestroyGroup", gvar("group", "TempGroup")), act("ReturnAction")]),
        act("DestroyGroup", gvar("group", "TempGroup")),
        setv("integer", "Wave", raw("Wave + 1")),
        setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                    lit("real", "1984"), lit("real", "1984"), lit("real", "270"))),
        setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                    lit("real", "2624"), lit("real", "1984"), lit("real", "270"))),
        setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                    lit("real", "1984"), lit("real", "2624"), lit("real", "270"))),
        setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                    lit("real", "2624"), lit("real", "2624"), lit("real", "270"))),
        setv("string", "Msg", fn("string", "I2S", gvar("integer", "Wave"))),
        show(fn("string", "YDWEOperatorString3",
                lit("string", "|cffffcc00第"),
                gvar("string", "Msg"),
                lit("string", "波|r 怪物来袭"))),
    ]:
        add("Demo_Spawn", a)
    save()
    print("Demo_Spawn built & saved")

# ============ T6 Demo_Reward ============
if not built("Demo_Reward"):
    event("Demo_Reward", "TriggerRegisterAnyUnitEventBJ",
          [preset("playerunitevent", "PlayerUnitEventDeath")])
    for a in [
        setv("unit", "TempUnit", fn("unit", "GetDyingUnit")),
        setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))),
        if_then("OperatorComparePlayer",
                [gvar("player", "TempPl"), EQ, NA],
                [
                    setv("unit", "Killer", fn("unit", "GetKillingUnitBJ")),
                    setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "Killer"))),
                    act("AdjustPlayerStateBJ", lit("integer", "50"), gvar("player", "TempPl"),
                        preset("playerstate", "PlayerStateGold")),
                    show("|cffffcc00+50|r 金币", gvar("player", "TempPl")),
                ]),
    ]:
        add("Demo_Reward", a)
    save()
    print("Demo_Reward built & saved")

print("=== ALL DONE ===")
print(json.dumps(ed("list_triggers", category_index=demo), ensure_ascii=False, indent=1))
