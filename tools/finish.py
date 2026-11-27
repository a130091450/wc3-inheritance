#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Finish Demo_Spawn / Demo_Reward one action at a time, saving after each."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, if_then, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")
NA = preset("player", "PlayerNA")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")


def setv(t, n, v):
    return act("SetVariable", gvar(t, n), v)


def show(text, player=None):
    return act("DisplayTextToPlayer", player or P1, lit("real", "0"), lit("real", "0"),
               lit("string", text)) if isinstance(text, str) else \
        act("DisplayTextToPlayer", player or P1, lit("real", "0"), lit("real", "0"), text)


ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]


def idx_of(name):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


def try_add(trg, a):
    label = a["name"] + "(" + ",".join(p.get("value", "?")[:18] for p in a["parameters"][:2]) + ")"
    sys.stdout.write("  + %s ... " % label)
    sys.stdout.flush()
    ed("add_action", category_index=demo, trigger_index=idx_of(trg),
       action_name=a["name"], parameters=a["parameters"], children=a["children"])
    ed("save_map", file_path=MAP)
    print("ok")


def try_event(trg, name, params):
    sys.stdout.write("  event %s ... " % name)
    sys.stdout.flush()
    ed("add_event", category_index=demo, trigger_index=idx_of(trg),
       event_name=name, parameters=params)
    ed("save_map", file_path=MAP)
    print("ok")


# ---- Demo_Spawn ----
spawn = [
    setv("group", "TempGroup", fn("group", "GetUnitsInRectAll", gvar("rect", "gg_rct_TrainArea"))),
    if_then("OperatorCompareBoolean",
            [gvar("boolean", "InTrain"), EQ, lit("boolean", "true")],
            [], [act("ReturnAction")]),
    setv("integer", "Wave", raw("Wave + 1")),
    setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                lit("real", "1984"), lit("real", "1984"), lit("real", "270"))),
    setv("string", "Msg", fn("string", "I2S", gvar("integer", "Wave"))),
    show(fn("string", "YDWEOperatorString3",
            lit("string", "|cffffcc00第"), gvar("string", "Msg"), lit("string", "波|r 怪物来袭"))),
]

print("== Demo_Spawn ==")
try:
    try_event("Demo_Spawn", "TriggerRegisterTimerEventPeriodic", [lit("real", "8.0")])
    for a in spawn:
        try_add("Demo_Spawn", a)
except Exception as e:
    print("\nFAILED at above action:", type(e).__name__, e)
    raise SystemExit(1)

# ---- Demo_Reward ----
reward = [
    setv("unit", "TempUnit", fn("unit", "GetDyingUnit")),
    setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))),
    if_then("OperatorComparePlayer",
            [gvar("player", "TempPl"), EQ, NA],
            [act("AdjustPlayerStateBJ", lit("integer", "50"), P1,
                 preset("playerstate", "PlayerStateGold")),
             show("|cffffcc00+50|r 金币")]),
]

print("== Demo_Reward ==")
try:
    try_event("Demo_Reward", "TriggerRegisterAnyUnitEventBJ",
              [preset("playerunitevent", "PlayerUnitEventDeath")])
    for a in reward:
        try_add("Demo_Reward", a)
except Exception as e:
    print("\nFAILED at above action:", type(e).__name__, e)
    raise SystemExit(1)

print("DONE")
