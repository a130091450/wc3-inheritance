#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Balance fix + reward diagnostics; drop one-shot AT triggers, keep status readout."""
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


def setv(t, n, v):
    return act("SetVariable", gvar(t, n), v)


def show(text, player=None):
    return act("DisplayTextToPlayer", player or P1, lit("real", "0"), lit("real", "0"), lit("string", text))


def build(name, event_name, event_params, actions, comment=""):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            ed("delete_trigger", category_index=demo, trigger_index=t["trigger_index"])
    ed("create_trigger", category_index=demo, name=name, comment=comment)
    ed("save_map", file_path=MAP)
    i = idx_of(name)
    ed("add_event", category_index=demo, trigger_index=i,
       event_name=event_name, parameters=event_params)
    ed("save_map", file_path=MAP)
    for a in actions:
        ed("add_action", category_index=demo, trigger_index=i,
           action_name=a["name"], parameters=a["parameters"], children=a["children"])
        ed("save_map", file_path=MAP)
    print("built", name, len(actions), "actions")


# 1) 删掉会抢操作的一次性 AT 触发器
for name in ["AT_1_Pick", "AT_2_F2", "AT_3_Spawn", "AT_4_Kill"]:
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            ed("delete_trigger", category_index=demo, trigger_index=t["trigger_index"])
            ed("save_map", file_path=MAP)
            print("deleted", name)

# 2) 刷怪：10 秒一波、每波 2 只、上限 8
spawn_actions = [
    setv("group", "TempGroup", fn("group", "GetUnitsInRectAll", gvar("rect", "gg_rct_TrainArea"))),
    if_then("OperatorCompareBoolean",
            [gvar("boolean", "InTrain"), EQ, lit("boolean", "true")],
            [], [act("ReturnAction")]),
    if_then("OperatorCompareInteger",
            [fn("integer", "CountUnitsInGroup", gvar("group", "TempGroup")),
             preset("ComparisonOperator", "OperatorGreater"), lit("integer", "8")],
            [act("DestroyGroup", gvar("group", "TempGroup")), act("ReturnAction")]),
    act("DestroyGroup", gvar("group", "TempGroup")),
    setv("integer", "Wave", raw("udg_Wave + 1")),
    setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                lit("real", "1984"), lit("real", "1984"), lit("real", "270"))),
    setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                lit("real", "2624"), lit("real", "2624"), lit("real", "270"))),
    setv("string", "Msg", fn("string", "I2S", gvar("integer", "Wave"))),
    act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
        fn("string", "YDWEOperatorString3", lit("string", "|cffffcc00第"), gvar("string", "Msg"),
           lit("string", "波|r 怪物来袭"))),
]
build("Demo_Spawn", "TriggerRegisterTimerEventPeriodic", [lit("real", "10.0")],
      spawn_actions, "练功房刷怪")

# 3) 奖励：加诊断输出（显示加完后的金币）
reward_actions = [
    setv("unit", "TempUnit", fn("unit", "GetDyingUnit")),
    setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))),
    if_then("OperatorComparePlayer",
            [gvar("player", "TempPl"), EQ, NA],
            [
                act("AdjustPlayerStateBJ", lit("integer", "50"), P1,
                    preset("playerstate", "PlayerStateGold")),
                setv("integer", "TempInt",
                     fn("integer", "GetPlayerState", P1, preset("playerstate", "PlayerStateGold"))),
                setv("string", "Msg", fn("string", "I2S", gvar("integer", "TempInt"))),
                act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
                    fn("string", "YDWEOperatorString3", lit("string", "REWARD +50 -> "),
                       gvar("string", "Msg"), lit("string", ""))),
            ]),
]
build("Demo_Reward", "TriggerRegisterAnyUnitEventBJ",
      [preset("playerunitevent", "PlayerUnitEventDeath")], reward_actions, "击杀奖励")

# 4) 英雄出生给经验，避免一进练功房就被秒
trg_pick = idx_of("Demo_Pick")
d = ed("get_trigger", category_index=demo, trigger_index=trg_pick)
for i, e in enumerate(d["ecas"]):
    params = e.get("params", [])
    fc = next((x for x in params if x.get("type_id") == 2), None)
    if fc and fc.get("value") == "CreateUnit":
        ed("add_action", category_index=demo, trigger_index=trg_pick,
           action_name="AddHeroXP",
           parameters=[gvar("unit", "Hero"), lit("integer", "1200"),
                       preset("showhideoption", "ShowHideShow")],
           children=[])
        ed("save_map", file_path=MAP)
        print("Demo_Pick: +AddHeroXP 1200 (after CreateUnit, appended at end)")
        break

print("DONE")
