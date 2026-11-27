#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""无尽传承 v4 build: per-player 修为/品阶, deaths, boss, hud, spawn fix.

Run one stage at a time:
  python -I -X utf8 build_v4.py vars|spawn0|setup|kill|death|boss|hud|test|droptest
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor, preset, lit, gvar, fn, raw, act, node  # noqa: E402

MAP = "C:/Users/Administrator/Desktop/testmap/无尽传承.w3x"
CAT = 1
P = [preset("player", "Player0%d" % i) for i in range(4)]
NA = preset("player", "PlayerNA")
EQ = preset("EqualNotEqualOperator", "OperatorEqualENE")
LT = preset("ComparisonOperator", "OperatorLess")
GE = preset("ComparisonOperator", "OperatorGreaterEq")

ed = Editor()


# ---------------- helpers ----------------
def setv(t, n, v, idx=None):
    return act("SetVariable", gvar(t, n, index=idx), v)


def script(code):
    return act("CustomScriptCode", lit("scriptcode", code))


def say(p, text):
    return act("DisplayTextToPlayer", p, lit("real", "0"), lit("real", "0"), lit("string", text))


def sayv(p):
    return act("DisplayTextToPlayer", p, lit("real", "0"), lit("real", "0"), gvar("string", "Msg"))


def c_int(lhs, op, rhs):
    return node("condition", "OperatorCompareInteger", [lhs, op, rhs], 0)


def c_bool(lhs, rhs):
    return node("condition", "OperatorCompareBoolean", [lhs, EQ, lit("boolean", rhs)], 0)


def ifn(conds, thens, elses=None, group=0):
    n = node("action", "IfThenElseMultiple", [], group)
    ch = list(conds)
    for a in thens:
        a = dict(a)
        a["group_id"] = 1
        ch.append(a)
    for a in (elses or []):
        a = dict(a)
        a["group_id"] = 2
        ch.append(a)
    n["children"] = ch
    return n


def trigs():
    return ed("list_triggers", category_index=CAT)["triggers"]


def idx_of(name):
    for t in trigs():
        if t["name"] == name:
            return t["trigger_index"]
    raise KeyError(name)


def rebuild(name, comment=""):
    for t in trigs():
        if t["name"] == name:
            ed("delete_trigger", category_index=CAT, trigger_index=t["trigger_index"])
            break
    ed("create_trigger", category_index=CAT, name=name, comment=comment)
    return idx_of(name)


def add_event(i, name, params):
    ed("add_event", category_index=CAT, trigger_index=i, event_name=name, parameters=params)


def add(i, a):
    ed("add_action", category_index=CAT, trigger_index=i, action_name=a["name"],
       parameters=a["parameters"], children=a["children"])


def savec():
    ed("save_map", file_path=MAP)
    print("  [saved]", flush=True)


# ---------------- stages ----------------
def stage_vars():
    have = {v["name"] for v in ed("list_variables", limit=400)["variables"]}
    todo = [
        ("HeroP", "unit", True),
        ("NeedTable", "integer", True),
        ("PIdx", "integer", False),
        ("TempInt2", "integer", False),
        ("Deaths", "integer", True),
        ("Out", "boolean", True),
        ("BossUnit", "unit", False),
        ("BossCount", "integer", False),
        ("GameOver", "boolean", False),
        ("MsgPre", "string", False),
    ]
    for name, typ, arr in todo:
        if name in have:
            continue
        ed("create_variable", name=name, type=typ, is_array=arr)
        print("  var", name, flush=True)
    for name in ("Tier", "XiuWei", "XiuNeed"):
        ed("modify_variable", name=name, is_array=True)
        print("  array", name, flush=True)
    savec()
    print("VARS OK")


def stage_spawn0():
    """V3_Spawn0 spawn X range was -600..600 (outside Zone0) -> -2600..-1200."""
    i = idx_of("V3_Spawn0")
    d = ed("get_trigger", category_index=CAT, trigger_index=i)
    bi, block = None, None
    for k, e in enumerate(d["ecas"]):
        if e["name"] == "IfThenElseMultiple":
            bi, block = k, e
    assert block is not None, "no if block"

    def conv(p):
        if "func_call" in p:
            return {"type_id": 2, "type_name": p["type_name"], "value": p["func_call"]["name"],
                    "func_params": [conv(x) for x in p["func_call"]["params"]]}
        q = {"type_id": p["type_id"], "type_name": p["type_name"], "value": p["value"]}
        if "array_index" in p:
            q["array_index"] = {"type_id": 3, "type_name": "integer", "value": p["array_index"]["value"]}
        return q

    def fixr(p):
        if p.get("value") == "GetRandomInt":
            fp = p.get("func_params", [])
            if len(fp) == 2 and fp[0].get("value") == "-600" and fp[1].get("value") == "600":
                fp[0]["value"] = "-2600"
                fp[1]["value"] = "-1200"
                print("  fixed X range -> -2600 -1200")
        for q in p.get("func_params", []):
            fixr(q)

    ch = []
    for c in block["children"]:
        params = [conv(p) for p in c.get("params", c.get("parameters", []))]
        for p in params:
            fixr(p)
        ch.append({"type": c["type"], "group_id": c["group_id"], "name": c["name"],
                   "children": [], "parameters": params})
    ed("replace_eca", category_index=CAT, trigger_index=i, eca_index=bi,
       name="IfThenElseMultiple", parameters=[], children=ch)
    savec()
    print("SPAWN0 OK")


def stage_setup():
    i = rebuild("V3_Setup", "开局：英雄数组/需求表/状态/选中")
    add_event(i, "TriggerRegisterTimerEventSingle", [lit("real", "1.0")])
    for k in range(4):
        add(i, setv("unit", "HeroP", gvar("unit", "H%d" % k), idx=k))
    savec()
    for k, v in enumerate([100, 220, 430, 750, 1200, 1800, 2600], start=1):
        add(i, setv("integer", "NeedTable", lit("integer", v), idx=k))
    savec()
    for k in range(4):
        add(i, setv("integer", "Tier", lit("integer", "1"), idx=k))
    savec()
    for k in range(4):
        add(i, setv("integer", "XiuNeed", lit("integer", "100"), idx=k))
    savec()
    for k in range(4):
        add(i, act("SelectUnitForPlayerSingle", gvar("unit", "H%d" % k), P[k]))
    add(i, setv("string", "MsgPre", lit("string", "品阶")))
    savec()
    for k in range(4):
        add(i, say(P[k], "守住四角：杀怪攒修为，修为满自动破境；死 3 次出局"))
    savec()
    print("SETUP OK")


def stage_kill():
    # ---- V3_TierUp first (V3_Kill references gg_trg_V3_TierUp) ----
    t = rebuild("V3_TierUp", "破境（由 V3_Kill 调用）")
    add_event(t, "TriggerRegisterTimerEventSingle", [lit("real", "99999")])
    add(t, script("set udg_TempInt = udg_Tier[udg_PIdx]"))
    then = [
        script("set udg_Tier[udg_PIdx] = udg_Tier[udg_PIdx] + 1"),
        script("set udg_XiuWei[udg_PIdx] = 0"),
        script("set udg_XiuNeed[udg_PIdx] = udg_NeedTable[udg_Tier[udg_PIdx]]"),
        script("call SetHeroStr(udg_HeroP[udg_PIdx], GetHeroStr(udg_HeroP[udg_PIdx], true) + 6, true)"),
        script("call SetHeroAgi(udg_HeroP[udg_PIdx], GetHeroAgi(udg_HeroP[udg_PIdx], true) + 6, true)"),
        script("call SetHeroInt(udg_HeroP[udg_PIdx], GetHeroInt(udg_HeroP[udg_PIdx], true) + 6, true)"),
        script("call SetUnitState(udg_HeroP[udg_PIdx], UNIT_STATE_LIFE, GetUnitState(udg_HeroP[udg_PIdx], UNIT_STATE_MAX_LIFE))"),
        script("set udg_Msg = udg_MsgPre + I2S(udg_Tier[udg_PIdx]) + \"  X\" + I2S(udg_XiuWei[udg_PIdx]) + \"/\" + I2S(udg_XiuNeed[udg_PIdx])"),
        say(gvar("player", "TempPl"), "破境成功！力/敏/智 +6，生命全满"),
        sayv(gvar("player", "TempPl")),
    ]
    els = [
        script("set udg_XiuWei[udg_PIdx] = udg_XiuNeed[udg_PIdx]"),
        say(gvar("player", "TempPl"), "已达最高品阶（神话）"),
    ]
    add(t, ifn([c_int(gvar("integer", "TempInt"), LT, lit("integer", "7"))], then, els))
    savec()

    # ---- V3_Kill: 杀中立怪 -> 该玩家 +10 修为；满则破境 ----
    i = rebuild("V3_Kill", "击杀加修为（按击杀者拥有者）")
    add_event(i, "TriggerRegisterAnyUnitEventBJ", [preset("playerunitevent", "PlayerUnitEventDeath")])
    add(i, setv("unit", "TempUnit", fn("unit", "GetDyingUnit")))
    add(i, setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))))
    then = [
        setv("unit", "TempUnit", fn("unit", "GetKillingUnitBJ")),
        setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))),
        setv("integer", "PIdx", fn("integer", "GetPlayerId", gvar("player", "TempPl"))),
    ]
    inner = [
        script("set udg_XiuWei[udg_PIdx] = udg_XiuWei[udg_PIdx] + 10"),
        say(gvar("player", "TempPl"), "修为 +10"),
        script("set udg_Msg = udg_MsgPre + I2S(udg_Tier[udg_PIdx]) + \"  X\" + I2S(udg_XiuWei[udg_PIdx]) + \"/\" + I2S(udg_XiuNeed[udg_PIdx])"),
        sayv(gvar("player", "TempPl")),
        script("set udg_TempInt = udg_XiuWei[udg_PIdx]"),
        script("set udg_TempInt2 = udg_XiuNeed[udg_PIdx]"),
        ifn([c_int(gvar("integer", "TempInt"), GE, gvar("integer", "TempInt2"))],
            [act("TriggerExecute", gvar("trigger", "gg_trg_V3_TierUp"))]),
    ]
    add(i, ifn([c_int(gvar("integer", "PIdx"), LT, lit("integer", "4"))], inner))
    savec()

    b = rebuild("V3_BossKill", "首领死亡：全队修为 +300")
    add_event(b, "TriggerRegisterAnyUnitEventBJ", [preset("playerunitevent", "PlayerUnitEventDeath")])
    add(b, setv("unit", "TempUnit", fn("unit", "GetDyingUnit")))
    then = [
        script("set udg_BossUnit = null"),
        script("set udg_XiuWei[0] = udg_XiuWei[0] + 300"),
        script("set udg_XiuWei[1] = udg_XiuWei[1] + 300"),
        script("set udg_XiuWei[2] = udg_XiuWei[2] + 300"),
        script("set udg_XiuWei[3] = udg_XiuWei[3] + 300"),
    ] + [say(P[k], "首领伏诛！全队修为 +300") for k in range(4)]
    add(b, ifn([node("condition", "OperatorCompareUnit",
                     [gvar("unit", "TempUnit"), EQ, gvar("unit", "BossUnit")], 0)], then))
    savec()
    print("KILL OK")


def stage_death():
    i = rebuild("V3_Death", "阵亡计数：3 次出局，全员出局结束")
    add_event(i, "TriggerRegisterAnyUnitEventBJ", [preset("playerunitevent", "PlayerUnitEventDeath")])
    add(i, setv("unit", "TempUnit", fn("unit", "GetDyingUnit")))
    add(i, setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))))
    add(i, setv("integer", "PIdx", fn("integer", "GetPlayerId", gvar("player", "TempPl"))))
    allout_conds = [c_bool(gvar("boolean", "Out", index=k), "true") for k in range(4)]
    allout = [setv("boolean", "GameOver", lit("boolean", "true"))] + \
             [say(P[k], "全员出局，本局结束") for k in range(4)]
    out_then = [
        script("set udg_Out[udg_PIdx] = true"),
        script("call RemoveUnit(udg_HeroP[udg_PIdx])"),
        script("set udg_HeroP[udg_PIdx] = null"),
        say(gvar("player", "TempPl"), "第 3 次阵亡，你已出局"),
        ifn(allout_conds, allout),
    ]
    alive_then = [
        say(gvar("player", "TempPl"), "阵亡，已在原地复活（死 3 次出局）"),
        script("call ReviveHero(udg_HeroP[udg_PIdx], GetUnitX(udg_HeroP[udg_PIdx]), GetUnitY(udg_HeroP[udg_PIdx]), true)"),
        script("call SelectUnitForPlayerSingle(udg_HeroP[udg_PIdx], udg_TempPl)"),
    ]
    body = [
        script("set udg_Deaths[udg_PIdx] = udg_Deaths[udg_PIdx] + 1"),
        script("set udg_TempInt = udg_Deaths[udg_PIdx]"),
        ifn([c_int(gvar("integer", "TempInt"), GE, lit("integer", "3"))], out_then, alive_then),
    ]
    add(i, ifn([c_int(gvar("integer", "PIdx"), LT, lit("integer", "4"))], body))
    savec()
    print("DEATH OK")


def stage_boss():
    i = rebuild("V3_Boss", "每 8 分钟首领降临中央")
    add_event(i, "TriggerRegisterTimerEventPeriodic", [lit("real", "480.0")])
    then = [
        setv("integer", "BossCount", raw("udg_BossCount + 1")),
        setv("unit", "BossUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "ninf"),
                                    lit("real", "0"), lit("real", "0"), lit("real", "270"))),
        ifn([node("condition", "OperatorCompareBoolean",
                  [fn("boolean", "IsUnitAliveBJ", gvar("unit", "HeroP", index=0)), EQ,
                   lit("boolean", "true")], 0)],
            [act("IssueTargetOrder", gvar("unit", "BossUnit"),
                 preset("unitorderutarg", "UnitOrderAttackUnit"), gvar("unit", "HeroP", index=0))]),
        act("PingMinimap", lit("real", "0"), lit("real", "0"), lit("real", "4")),
    ] + [say(P[k], "首领已降临地图中央！击杀可全队 +300 修为") for k in range(4)]
    add(i, ifn([c_bool(gvar("boolean", "GameOver"), "false")], then))
    savec()
    print("BOSS OK")


def stage_hud():
    i = rebuild("V3_HUD", "每 10 秒显示各自修为")
    add_event(i, "TriggerRegisterTimerEventPeriodic", [lit("real", "10.0")])
    for k in range(4):
        add(i, script("set udg_Msg = udg_MsgPre + I2S(udg_Tier[%d]) + \"  X\" + I2S(udg_XiuWei[%d]) + \"/\" + I2S(udg_XiuNeed[%d])" % (k, k, k)))
        add(i, sayv(P[k]))
    savec()
    print("HUD OK")


def stage_test():
    i = rebuild("V3_Test", "临时自测：6 秒直接放首领")
    add_event(i, "TriggerRegisterTimerEventSingle", [lit("real", "6.0")])
    add(i, act("TriggerExecute", gvar("trigger", "gg_trg_V3_Boss")))
    savec()
    print("TEST OK")


def stage_droptest():
    for t in trigs():
        if t["name"] == "V3_Test":
            ed("delete_trigger", category_index=CAT, trigger_index=t["trigger_index"])
            print("  deleted V3_Test", flush=True)
    savec()
    print("DROPTEST OK")


def reset(name, comment=""):
    """Clear ECAs of an existing trigger (or create it). Avoids delete-trigger dialog."""
    try:
        i = idx_of(name)
    except KeyError:
        ed("create_trigger", category_index=CAT, name=name, comment=comment)
        return idx_of(name)
    d = ed("get_trigger", category_index=CAT, trigger_index=i)
    for k in range(len(d["ecas"]) - 1, -1, -1):
        ed("remove_eca", category_index=CAT, trigger_index=i, eca_index=k)
    if comment:
        ed("set_trigger_description", category_index=CAT, trigger_index=i, description=comment)
    return idx_of(name)


def stage_fixkill():
    i = reset("V3_Kill", "击杀加修为（按击杀者拥有者）")
    add_event(i, "TriggerRegisterAnyUnitEventBJ", [preset("playerunitevent", "PlayerUnitEventDeath")])
    add(i, setv("unit", "TempUnit", fn("unit", "GetDyingUnit")))
    add(i, setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))))
    inner = [
        script("set udg_XiuWei[udg_PIdx] = udg_XiuWei[udg_PIdx] + 10"),
        say(gvar("player", "TempPl"), "修为 +10"),
        script("set udg_Msg = udg_MsgPre + I2S(udg_Tier[udg_PIdx]) + \"  X\" + I2S(udg_XiuWei[udg_PIdx]) + \"/\" + I2S(udg_XiuNeed[udg_PIdx])"),
        sayv(gvar("player", "TempPl")),
        script("set udg_TempInt = udg_XiuWei[udg_PIdx]"),
        script("set udg_TempInt2 = udg_XiuNeed[udg_PIdx]"),
        ifn([c_int(gvar("integer", "TempInt"), GE, gvar("integer", "TempInt2"))],
            [act("TriggerExecute", gvar("trigger", "gg_trg_V3_TierUp"))]),
    ]
    add(i, ifn([c_int(gvar("integer", "PIdx"), LT, lit("integer", "4"))], inner))
    savec()
    print("FIXKILL OK")


def stage_fixkill2():
    """V3_Kill: guard dying unit is neutral hostile, THEN resolve killer -> credit."""
    i = reset("V3_Kill", "击杀加修为（按击杀者拥有者）")
    add_event(i, "TriggerRegisterAnyUnitEventBJ", [preset("playerunitevent", "PlayerUnitEventDeath")])
    add(i, setv("unit", "TempUnit", fn("unit", "GetDyingUnit")))
    add(i, setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))))
    credit = [
        setv("unit", "TempUnit", fn("unit", "GetKillingUnitBJ")),
        setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))),
        setv("integer", "PIdx", fn("integer", "GetPlayerId", gvar("player", "TempPl"))),
    ]
    inner = [
        script("set udg_XiuWei[udg_PIdx] = udg_XiuWei[udg_PIdx] + 10"),
        say(gvar("player", "TempPl"), "修为 +10"),
        script("set udg_Msg = udg_MsgPre + I2S(udg_Tier[udg_PIdx]) + \"  X\" + I2S(udg_XiuWei[udg_PIdx]) + \"/\" + I2S(udg_XiuNeed[udg_PIdx])"),
        sayv(gvar("player", "TempPl")),
        script("set udg_TempInt = udg_XiuWei[udg_PIdx]"),
        script("set udg_TempInt2 = udg_XiuNeed[udg_PIdx]"),
        ifn([c_int(gvar("integer", "TempInt"), GE, gvar("integer", "TempInt2"))],
            [act("TriggerExecute", gvar("trigger", "gg_trg_V3_TierUp"))]),
    ]
    credit.append(ifn([c_int(gvar("integer", "PIdx"), LT, lit("integer", "4"))], inner))
    add(i, ifn([node("condition", "OperatorComparePlayer",
                     [gvar("player", "TempPl"), EQ, NA], 0)], credit))
    savec()
    print("FIXKILL2 OK")


STAGES = {
    "vars": stage_vars, "spawn0": stage_spawn0, "setup": stage_setup,
    "kill": stage_kill, "death": stage_death, "boss": stage_boss,
    "hud": stage_hud, "test": stage_test, "droptest": stage_droptest,
    "fixkill": stage_fixkill, "fixkill2": stage_fixkill2,
}

if __name__ == "__main__":
    STAGES[sys.argv[1]]()
