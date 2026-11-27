#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix the arithmetic expression in Demo_Spawn (bare Wave -> udg_Wave)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, lit, gvar, raw, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]
trg = [t["trigger_index"] for t in ed("list_triggers", category_index=demo)["triggers"]
       if t["name"] == "Demo_Spawn"][0]

d = ed("get_trigger", category_index=demo, trigger_index=trg)
ecas = d["ecas"]
target = None
for i, e in enumerate(ecas):
    if e.get("name") == "SetVariable" and e.get("type") == "action":
        p = e.get("params", [])
        if p and p[0].get("value") == "Wave":
            target = i
            break
print("target eca index =", target)
if target is None:
    raise SystemExit("not found")

ed("replace_eca", category_index=demo, trigger_index=trg, eca_index=target,
   name="SetVariable",
   parameters=[gvar("integer", "Wave"), raw("udg_Wave + 1")],
   children=[])
ed("save_map", file_path=MAP)
print("replaced & saved")

d = ed("get_trigger", category_index=demo, trigger_index=trg)
print([e.get("params") for e in d["ecas"] if e.get("name") == "SetVariable"
       and (e.get("params") or [{}])[0].get("value") == "Wave"])
