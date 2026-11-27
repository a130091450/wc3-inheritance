#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Temporary in-map auto test: simulates pick/teleport, checks spawn & reward."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, if_then, act

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
P1 = preset("player", "Player00")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")

ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]


def idx_of(name):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


def show_plain(text):
    return act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"), lit("string", text))


def show_parts(a, b, c):
    return act("DisplayTextToPlayer", P1, lit("real", "0"), lit("real", "0"),
               fn("string", "YDWEOperatorString3", lit("string", a), gvar("string", "Msg"), lit("string", c)))


def setv(t, n, v):
    return act("SetVariable", gvar(t, n), v)


def build(name, delay, actions, comment=""):
    for t in ed("list_triggers", category_index=demo)["triggers"]:
        if t["name"] == name:
            ed("delete_trigger", category_index=demo, trigger_index=t["trigger_index"])
    ed("create_trigger", category_index=demo, name=name, comment=comment or "自动测试")
    i = idx_of(name)
    ed("add_event", category_index=demo, trigger_index=i,
       event_name="TriggerRegisterTimerEventSingle", parameters=[lit("real", delay)])
    ed("save_map", file_path=MAP)
    for a in actions:
        ed("add_action", category_index=demo, trigger_index=i,
           action_name=a["name"], parameters=a["parameters"], children=a["children"])
        ed("save_map", file_path=MAP)
    print("built", name, len(actions), "actions")


# 1) 模拟选英雄
build("AT_1_Pick", "2.0", [
    setv("unit", "Hero", fn("unit", "CreateUnit", P1, lit("unitcode", "Hmkg"),
                            lit("real", "-2304"), lit("real", "-1856"), lit("real", "270"))),
    setv("boolean", "HeroPicked", lit("boolean", "true")),
    act("SelectUnitForPlayerSingle", gvar("unit", "Hero"), P1),
    show_plain("AT1 PICK OK"),
])

# 2) 模拟按 F2
build("AT_2_F2", "5.0", [
    act("DzSetUnitXY", gvar("unit", "Hero"), lit("real", "2304"), lit("real", "2304")),
    setv("boolean", "InTrain", lit("boolean", "true")),
    show_plain("AT2 F2 OK"),
])

# 3) 检查刷怪（8s 首次刷怪）
build("AT_3_Spawn", "12.0", [
    setv("group", "TempGroup", fn("group", "GetUnitsInRectAll", gvar("rect", "gg_rct_TrainArea"))),
    setv("integer", "TempInt", fn("integer", "CountUnitsInGroup", gvar("group", "TempGroup"))),
    act("DestroyGroup", gvar("group", "TempGroup")),
    setv("string", "Msg", fn("string", "I2S", gvar("integer", "TempInt"))),
    show_parts("AT3 SPAWNED=", "", ""),
    setv("string", "Msg", fn("string", "I2S", gvar("integer", "Wave"))),
    show_parts("AT3 WAVE=", "", ""),
])

# 4) 杀一只怪（测试奖励）
build("AT_4_Kill", "15.0", [
    setv("group", "TempGroup", fn("group", "GetUnitsInRectAll", gvar("rect", "gg_rct_TrainArea"))),
    setv("unit", "TempUnit", fn("unit", "FirstOfGroup", gvar("group", "TempGroup"))),
    act("DestroyGroup", gvar("group", "TempGroup")),
    act("DzKillUnit", gvar("unit", "TempUnit"), gvar("unit", "Hero")),
    show_plain("AT4 KILL SENT"),
])

# 5) 检查金币
build("AT_5_Gold", "18.0", [
    setv("integer", "TempInt",
         fn("integer", "GetPlayerState", P1, preset("playerstate", "PlayerStateGold"))),
    setv("string", "Msg", fn("string", "I2S", gvar("integer", "TempInt"))),
    show_parts("AT5 GOLD=", "", ""),
    show_plain("AT DONE"),
])

print("AUTOTEST READY")
