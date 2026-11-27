#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix hero dialog: register the dialog event at runtime, after the dialog exists."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, if_then, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")

ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]


def idx_of(name):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


def setv(t, n, v):
    return act("SetVariable", gvar(t, n), v)


# ---------- 1) 重建 Demo_Pick：完整逻辑，无静态事件 ----------
for t in ed("list_triggers", category_index=demo)["triggers"]:
    if t["name"] == "Demo_Pick":
        ed("delete_trigger", category_index=demo, trigger_index=t["trigger_index"])
ed("save_map", file_path=MAP)
ed("create_trigger", category_index=demo, name="Demo_Pick",
   comment="英雄选择回调：事件由 Demo_Init 运行时动态注册")
ed("save_map", file_path=MAP)
i = idx_of("Demo_Pick")

actions = [
    act("DialogDisplay", P1, gvar("dialog", "HeroDialog"), preset("showhideoption", "ShowHideHide")),
    setv("unitcode", "HeroType", lit("unitcode", "Hmkg")),
    if_then("OperatorCompareUnit",
            [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "BtnA")],
            [setv("unitcode", "HeroType", lit("unitcode", "Obla"))]),
    if_then("OperatorCompareUnit",
            [fn("unit", "GetClickedButtonBJ"), EQ, gvar("button", "BtnI")],
            [setv("unitcode", "HeroType", lit("unitcode", "Hjai"))]),
    setv("unit", "Hero", fn("unit", "CreateUnit", P1, gvar("unitcode", "HeroType"),
                            lit("real", "-2304"), lit("real", "-1856"), lit("real", "270"))),
    setv("boolean", "HeroPicked", lit("boolean", "true")),
    act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
    act("PanCameraToTimed", lit("real", "-2304"), lit("real", "-1856"), lit("real", "0.6")),
    act("PingMinimap", lit("real", "-2304"), lit("real", "-1856"), lit("real", "1.5")),
    act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
        lit("string", "英雄已就位，按 |cffffcc00F2|r 进入练功房")),
    act("AddHeroXP", gvar("unit", "Hero"), lit("integer", "1200"),
        preset("showhideoption", "ShowHideShow")),
]
for a in actions:
    ed("add_action", category_index=demo, trigger_index=i,
       action_name=a["name"], parameters=a["parameters"], children=a["children"])
    ed("save_map", file_path=MAP)
print("Demo_Pick rebuilt (no static event):", len(actions), "actions")

# ---------- 2) Demo_Init 末尾加动态注册 ----------
init_i = idx_of("Demo_Init")
ed("add_action", category_index=demo, trigger_index=init_i,
   action_name="CustomScriptCode",
   parameters=[lit("scriptcode", "call TriggerRegisterDialogEvent(gg_trg_Demo_Pick, udg_HeroDialog)")],
   children=[])
ed("save_map", file_path=MAP)
print("Demo_Init: dynamic dialog registration appended")
