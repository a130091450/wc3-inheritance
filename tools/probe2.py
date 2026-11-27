#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Probe: does the editor accept array_index as a global variable (dynamic index)?"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, act

ed = Editor()
CAT = 1

have = {v["name"] for v in ed("list_variables", limit=400)["variables"]}
for name, typ, arr in [("PIdx", "integer", False), ("XA", "integer", True), ("HA", "unit", True)]:
    if name not in have:
        ed("create_variable", name=name, type=typ, is_array=arr)
print("vars:", sorted({v['name'] for v in ed('list_variables', limit=400)['variables']}))

# create probe trigger
trigs = ed("list_triggers", category_index=CAT)["triggers"]
for t in trigs:
    if t["name"] == "ZZ_Probe":
        ed("delete_trigger", category_index=CAT, trigger_index=t["trigger_index"])
ed("create_trigger", category_index=CAT, name="ZZ_Probe", comment="probe")
idx = [t["trigger_index"] for t in ed("list_triggers", category_index=CAT)["triggers"] if t["name"] == "ZZ_Probe"][0]
print("idx", idx)

ed("add_event", category_index=CAT, trigger_index=idx,
   event_name="TriggerRegisterTimerEventSingle", parameters=[lit("real", "99")])

# 1) XA[PIdx] = 5  (dynamic index write)
ed("add_action", category_index=CAT, trigger_index=idx, action_name="SetVariable",
   parameters=[gvar("integer", "XA", index=gvar("integer", "PIdx")), lit("integer", "5")])
print("w1 ok")

# 2) TempUnit = HA[PIdx] (dynamic index read as value)
ed("add_action", category_index=CAT, trigger_index=idx, action_name="SetVariable",
   parameters=[gvar("unit", "TempUnit"), gvar("unit", "HA", index=gvar("integer", "PIdx"))])
print("w2 ok")

# 3) SetHeroStr(HA[PIdx], TempInt, enable) (dynamic array read as action arg)
ed("add_action", category_index=CAT, trigger_index=idx, action_name="SetHeroStr",
   parameters=[gvar("unit", "HA", index=gvar("integer", "PIdx")),
               gvar("integer", "TempInt"),
               preset("enabledisableoption", "EnableDisableEnable")])
print("w3 ok")

# 4) raw arithmetic on array element with dynamic index
ed("add_action", category_index=CAT, trigger_index=idx, action_name="SetVariable",
   parameters=[gvar("integer", "TempInt"), raw("udg_XA[udg_PIdx] + 10")])
print("w4 ok")

d = ed("get_trigger", category_index=CAT, trigger_index=idx)
print(json.dumps(d, ensure_ascii=False, indent=1)[:6000])
