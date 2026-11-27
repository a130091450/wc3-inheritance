#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Probe: validate literal writing (unitcode / Chinese text / arithmetic)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, act

DEMO = 1

ed = Editor()

# variables used by probe
for name, typ in [
    ("HeroType", "unitcode"),
    ("BtnP", "button"),
    ("BtnA", "button"),
    ("BtnI", "button"),
    ("TempUnit", "unit"),
    ("TempPl", "player"),
    ("TempInt", "integer"),
    ("TempGroup", "group"),
]:
    try:
        ed("create_variable", name=name, type=typ, is_array=False)
    except Exception as e:
        print("var %s: %s" % (name, e))

ed("create_trigger", category_index=DEMO, name="ZZ_Probe", comment="参数字面量探针")

ed(
    "add_event",
    category_index=DEMO,
    trigger_index=0,
    event_name="TriggerRegisterTimerEventSingle",
    parameters=[lit("real", "0.10")],
)

probe_actions = [
    act(
        "DisplayTextToPlayer",
        preset("player", "Player00"),
        lit("real", "0"),
        lit("real", "0"),
        lit("string", "测试中文 |cffffcc00OK|r"),
    ),
    act("SetVariable", gvar("unitcode", "HeroType"), lit("unitcode", "Hmkg")),
    act(
        "SetVariable",
        gvar("integer", "Wave"),
        fn("integer", " ", lit("scriptcode", "Wave + 1")),
    ),
    act(
        "SetVariable",
        gvar("unit", "TempUnit"),
        fn("unit", "CreateUnit",
           preset("player", "Player00"), lit("unitcode", "hcas"),
           lit("real", "-2304"), lit("real", "-2304"), lit("real", "270")),
    ),
]

for i, a in enumerate(probe_actions):
    ed(
        "add_action",
        category_index=DEMO,
        trigger_index=0,
        action_name=a["name"],
        parameters=a["parameters"],
        children=a["children"],
    )
    print("added action", i, a["name"])

print(json.dumps(ed("get_trigger", category_index=DEMO, trigger_index=0), ensure_ascii=False, indent=1))
