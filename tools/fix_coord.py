#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Move base hero spawn point from y=-2080 to y=-1856 (avoid castle footprint)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")

ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]
trigs = {t["name"]: t["trigger_index"] for t in ed("list_triggers", category_index=demo)["triggers"]}


def replace(trg_name, idx, name, params, children=None):
    ed("replace_eca", category_index=demo, trigger_index=trigs[trg_name], eca_index=idx,
       name=name, parameters=params, children=children or [])


def dump(trg_name):
    return ed("get_trigger", category_index=demo, trigger_index=trigs[trg_name])["ecas"]


# --- Demo_Pick: CreateUnit y ---
for i, e in enumerate(dump("Demo_Pick")):
    p = e.get("params", [])
    fc = next((x for x in p if x.get("type_id") == 2), None)
    if fc and fc.get("value") == "CreateUnit":
        replace("Demo_Pick", i, "SetVariable", [
            gvar("unit", "Hero"),
            fn("unit", "CreateUnit", P1, gvar("unitcode", "HeroType"),
               lit("real", "-2304"), lit("real", "-1856"), lit("real", "270")),
        ])
        print("Demo_Pick CreateUnit y -> -1856")

# --- Demo_F3: DzSetUnitXY + Pan + Ping ---
for i, e in enumerate(dump("Demo_F3")):
    name = e.get("name")
    p = e.get("params", [])
    values = [str(x.get("value")) for x in p]
    if "-2080" not in values:
        continue
    if name == "DzSetUnitXY":
        replace("Demo_F3", i, name, [gvar("unit", "Hero"), lit("real", "-2304"), lit("real", "-1856")])
    elif name == "PanCameraToTimed":
        replace("Demo_F3", i, name, [lit("real", "-2304"), lit("real", "-1856"), lit("real", "0.8")])
    elif name == "PingMinimap":
        replace("Demo_F3", i, name, [lit("real", "-2304"), lit("real", "-1856"), lit("real", "1.5")])
    else:
        continue
    print("Demo_F3", name, "-> -1856")

ed("save_map", file_path=MAP)
print("saved")
