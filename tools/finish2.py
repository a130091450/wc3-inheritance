#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rebuild Demo_Spawn in correct order (delete + recreate, save after each step)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, if_then, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")
NA = preset("player", "PlayerNA")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")

ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]


def idx_of(name):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


# delete old spawn
ed("delete_trigger", category_index=demo, trigger_index=idx_of("Demo_Spawn"))
ed("create_trigger", category_index=demo, name="Demo_Spawn", comment="练功房刷怪")
print("recreated Demo_Spawn")

steps = [
    ("event", "TriggerRegisterTimerEventPeriodic", [lit("real", "8.0")]),
    ("action", act("SetVariable", gvar("group", "TempGroup"),
                   fn("group", "GetUnitsInRectAll", gvar("rect", "gg_rct_TrainArea"))), None),
    ("action", if_then("OperatorCompareBoolean",
                       [gvar("boolean", "InTrain"), EQ, lit("boolean", "true")],
                       [], [act("ReturnAction")]), None),
    ("action", if_then("OperatorCompareInteger",
                       [fn("integer", "CountUnitsInGroup", gvar("group", "TempGroup")),
                        preset("ComparisonOperator", "OperatorGreater"), lit("integer", "16")],
                       [act("DestroyGroup", gvar("group", "TempGroup")), act("ReturnAction")]), None),
    ("action", act("DestroyGroup", gvar("group", "TempGroup")), None),
    ("action", act("SetVariable", gvar("integer", "Wave"), raw("Wave + 1")), None),
    ("action", act("SetVariable", gvar("unit", "TempUnit"), fn(
        "unit", "CreateUnit", NA, lit("unitcode", "nban"),
        lit("real", "1984"), lit("real", "1984"), lit("real", "270"))), None),
    ("action", act("SetVariable", gvar("unit", "TempUnit"), fn(
        "unit", "CreateUnit", NA, lit("unitcode", "nban"),
        lit("real", "2624"), lit("real", "1984"), lit("real", "270"))), None),
    ("action", act("SetVariable", gvar("unit", "TempUnit"), fn(
        "unit", "CreateUnit", NA, lit("unitcode", "nban"),
        lit("real", "1984"), lit("real", "2624"), lit("real", "270"))), None),
    ("action", act("SetVariable", gvar("unit", "TempUnit"), fn(
        "unit", "CreateUnit", NA, lit("unitcode", "nban"),
        lit("real", "2624"), lit("real", "2624"), lit("real", "270"))), None),
    ("action", act("SetVariable", gvar("string", "Msg"),
                   fn("string", "I2S", gvar("integer", "Wave"))), None),
    ("action", act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
                   fn("string", "YDWEOperatorString3",
                      lit("string", "|cffffcc00第"), gvar("string", "Msg"),
                      lit("string", "波|r 怪物来袭"))), None),
]

for i, (kind, obj, _) in enumerate(steps):
    label = obj if kind == "event" else obj["name"]
    sys.stdout.write("  %2d %s ... " % (i, label))
    sys.stdout.flush()
    if kind == "event":
        ed("add_event", category_index=demo, trigger_index=idx_of("Demo_Spawn"),
           event_name=obj, parameters=[lit("real", "8.0")])
    else:
        ed("add_action", category_index=demo, trigger_index=idx_of("Demo_Spawn"),
           action_name=obj["name"], parameters=obj["parameters"], children=obj["children"])
    ed("save_map", file_path=MAP)
    print("ok")

print("DONE")
