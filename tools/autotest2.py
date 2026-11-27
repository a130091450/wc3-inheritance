#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Periodic on-screen status readout for the auto test."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")

ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]


def idx_of(name):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


for t in ed("list_triggers", category_index=demo)["triggers"]:
    if t["name"] == "AT_5_Gold":
        ed("delete_trigger", category_index=demo, trigger_index=t["trigger_index"])

ed("create_trigger", category_index=demo, name="AT_Status", comment="自动测试状态条")
ed("save_map", file_path=MAP)
i = idx_of("AT_Status")
ed("add_event", category_index=demo, trigger_index=i,
   event_name="TriggerRegisterTimerEventPeriodic", parameters=[lit("real", "3.0")])
ed("save_map", file_path=MAP)

steps = [
    act("SetVariable", gvar("group", "TempGroup"),
        fn("group", "GetUnitsInRectAll", gvar("rect", "gg_rct_TrainArea"))),
    act("SetVariable", gvar("integer", "TempInt"),
        fn("integer", "CountUnitsInGroup", gvar("group", "TempGroup"))),
    act("DestroyGroup", gvar("group", "TempGroup")),
    act("SetVariable", gvar("string", "Msg"), fn("string", "I2S", gvar("integer", "TempInt"))),
    act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
        fn("string", "YDWEOperatorString3", lit("string", "STAT SPAWN="), gvar("string", "Msg"), lit("string", ""))),
    act("SetVariable", gvar("string", "Msg"), fn("string", "I2S", gvar("integer", "Wave"))),
    act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
        fn("string", "YDWEOperatorString3", lit("string", "STAT WAVE="), gvar("string", "Msg"), lit("string", ""))),
    act("SetVariable", gvar("integer", "TempInt"),
        fn("integer", "GetPlayerState", P1, preset("playerstate", "PlayerStateGold"))),
    act("SetVariable", gvar("string", "Msg"), fn("string", "I2S", gvar("integer", "TempInt"))),
    act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
        fn("string", "YDWEOperatorString3", lit("string", "STAT GOLD="), gvar("string", "Msg"), lit("string", ""))),
]
for a in steps:
    ed("add_action", category_index=demo, trigger_index=i,
       action_name=a["name"], parameters=a["parameters"], children=a["children"])
    ed("save_map", file_path=MAP)
print("AT_Status built:", len(steps), "actions")
