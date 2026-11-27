#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""F3: revive if dead; spawn cap 8 -> 6; hero starts stronger."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, if_then, act

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


def setv(t, n, v):
    return act("SetVariable", gvar(t, n), v)


def show(text, player=None):
    return act("DisplayTextToPlayer", player or P1, lit("real", "0"), lit("real", "0"), lit("string", text))


# ---------- Demo_F3: 死亡即在基地复活 ----------
for t in ed("list_triggers", category_index=demo)["triggers"]:
    if t["name"] == "Demo_F3":
        ed("delete_trigger", category_index=demo, trigger_index=t["trigger_index"])
ed("save_map", file_path=MAP)
ed("create_trigger", category_index=demo, name="Demo_F3", comment="F3 返回基地（死亡则复活）")
ed("save_map", file_path=MAP)
i = idx_of("Demo_F3")
ed("add_event", category_index=demo, trigger_index=i,
   event_name="DzTriggerRegisterKeyEventTrg",
   parameters=[preset("gamekeyaction", "GameKeyAction_Press"), preset("gamekey", "GameKey_F3")])
ed("save_map", file_path=MAP)

f3_actions = [
    if_then("OperatorCompareBoolean",
            [gvar("boolean", "HeroPicked"), EQ, lit("boolean", "true")],
            [], [show("请先选择英雄"), act("ReturnAction")]),
    if_then("OperatorCompareBoolean",
            [fn("boolean", "IsUnitAliveBJ", gvar("unit", "Hero")), EQ, lit("boolean", "true")],
            [act("DzSetUnitXY", gvar("unit", "Hero"), lit("real", "-2304"), lit("real", "-1856"))],
            [act("ReviveHero", gvar("unit", "Hero"), lit("real", "-2304"), lit("real", "-1856"),
                 preset("showhideoption", "ShowHideShow")),
             show("英雄已阵亡，已在基地复活")]),
    setv("boolean", "InTrain", lit("boolean", "false")),
    act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
    act("PanCameraToTimed", lit("real", "-2304"), lit("real", "-1856"), lit("real", "0.8")),
    act("PingMinimap", lit("real", "-2304"), lit("real", "-1856"), lit("real", "1.5")),
    show("已返回基地，|cff00ff00F2|r 前往练功房"),
]
for a in f3_actions:
    ed("add_action", category_index=demo, trigger_index=i,
       action_name=a["name"], parameters=a["parameters"], children=a["children"])
    ed("save_map", file_path=MAP)
print("Demo_F3 rebuilt:", len(f3_actions), "actions")

# ---------- 刷怪上限 8 -> 6 ----------
spawn_i = idx_of("Demo_Spawn")
d = ed("get_trigger", category_index=demo, trigger_index=spawn_i)
for n, e in enumerate(d["ecas"]):
    if e.get("name") != "IfThenElseMultiple":
        continue
    conds = [c for c in e.get("children", []) if c.get("type") == "condition"]
    vals = [p.get("value") for c in conds for p in c.get("params", [])]
    if "8" in vals:
        new_if = if_then("OperatorCompareInteger",
                         [fn("integer", "CountUnitsInGroup", gvar("group", "TempGroup")),
                          preset("ComparisonOperator", "OperatorGreater"), lit("integer", "6")],
                         [act("DestroyGroup", gvar("group", "TempGroup")), act("ReturnAction")])
        ed("replace_eca", category_index=demo, trigger_index=spawn_i, eca_index=n,
           name="IfThenElseMultiple", parameters=[], children=new_if["children"])
        ed("save_map", file_path=MAP)
        print("spawn cap -> 6 (eca", n, ")")
        break

# ---------- 英雄初始经验 1200 -> 2500 ----------
pick_i = idx_of("Demo_Pick")
d = ed("get_trigger", category_index=demo, trigger_index=pick_i)
for n, e in enumerate(d["ecas"]):
    if e.get("name") == "AddHeroXP":
        ed("replace_eca", category_index=demo, trigger_index=pick_i, eca_index=n,
           name="AddHeroXP",
           parameters=[gvar("unit", "Hero"), lit("integer", "2500"),
                       preset("showhideoption", "ShowHideShow")],
           children=[])
        ed("save_map", file_path=MAP)
        print("hero xp -> 2500 (eca", n, ")")
        break
print("DONE")
