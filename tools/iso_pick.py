#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Isolation test: step prints + create a footman instead of a hero."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")

ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]

# 静音状态条，避免刷屏
for t in ed("list_triggers", category_index=demo)["triggers"]:
    if t["name"] == "AT_Status":
        ed("delete_trigger", category_index=demo, trigger_index=t["trigger_index"])
        ed("save_map", file_path=MAP)
        print("deleted AT_Status")


def idx_of(name):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


for t in ed("list_triggers", category_index=demo)["triggers"]:
    if t["name"] == "Demo_Pick":
        ed("delete_trigger", category_index=demo, trigger_index=t["trigger_index"])
ed("save_map", file_path=MAP)
ed("create_trigger", category_index=demo, name="Demo_Pick", comment="隔离测试")
ed("save_map", file_path=MAP)
i = idx_of("Demo_Pick")
ed("add_event", category_index=demo, trigger_index=i,
   event_name="TriggerRegisterDialogEventBJ", parameters=[gvar("dialog", "HeroDialog")])
ed("save_map", file_path=MAP)


def say(text):
    return act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"), lit("string", text))


steps = [
    act("DialogDisplay", P1, gvar("dialog", "HeroDialog"), preset("showhideoption", "ShowHideHide")),
    say("STEP 1 dialog hidden"),
    act("SetVariable", gvar("unitcode", "HeroType"), lit("unitcode", "hfoo")),
    say("STEP 2 type set"),
    act("SetVariable", gvar("unit", "Hero"),
        fn("unit", "CreateUnit", P1, gvar("unitcode", "HeroType"),
           lit("real", "-2304"), lit("real", "-1856"), lit("real", "270"))),
    say("STEP 3 unit created"),
    act("SetVariable", gvar("integer", "TempInt"), fn("integer", "GetUnitTypeId", gvar("unit", "Hero"))),
    act("SetVariable", gvar("string", "Msg"), fn("string", "I2S", gvar("integer", "TempInt"))),
    act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
        fn("string", "YDWEOperatorString3", lit("string", "STEP 4 id="), gvar("string", "Msg"), lit("string", ""))),
    act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
    say("STEP 5 selected"),
]

for a in steps:
    ed("add_action", category_index=demo, trigger_index=i,
       action_name=a["name"], parameters=a["parameters"], children=a["children"])
    ed("save_map", file_path=MAP)
print("isolation Demo_Pick built:", len(steps))
