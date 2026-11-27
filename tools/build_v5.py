#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""无尽传承 v5: fix creep spawning (counter based) + force alliance among 4 players.

Stages:
  python -I -X utf8 build_v5.py players     # force_flags=7 via set_player_config
  python -I -X utf8 build_v5.py vars        # CreepN / LastCreep
  python -I -X utf8 build_v5.py spawn       # rebuild V3_Spawn0..3
  python -I -X utf8 build_v5.py creepdead   # new V3_CreepDead
  python -I -X utf8 build_v5.py ally        # append alliance to V3_Setup
  python -I -X utf8 build_v5.py test        # temp test pages
  python -I -X utf8 build_v5.py droptest    # delete temp test pages
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


def c_player(lhs, rhs):
    return node("condition", "OperatorComparePlayer", [lhs, EQ, rhs], 0)


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


def reset(name, comment=""):
    """Clear all ECAs of a trigger (create if missing). Avoids delete-trigger modal."""
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


def add_event(i, name, params):
    ed("add_event", category_index=CAT, trigger_index=i, event_name=name, parameters=params)


def add(i, a):
    ed("add_action", category_index=CAT, trigger_index=i, action_name=a["name"],
       parameters=a["parameters"], children=a["children"])


def savec():
    ed("save_map", file_path=MAP)
    print("  [saved]", flush=True)


# ---------------- stages ----------------
def stage_players():
    cfg = {
        "player_count": 4,
        "players": [
            {"id": 0, "name": "玩家 1", "controller_id": 1, "race": 1},
            {"id": 1, "name": "玩家 2", "controller_id": 1, "race": 1},
            {"id": 2, "name": "玩家 3", "controller_id": 1, "race": 1},
            {"id": 3, "name": "玩家 4", "controller_id": 1, "race": 1},
        ],
        "team_count": 1,
        "teams": [{"index": 0, "name": "同盟", "player_masks": 15, "force_flags": 7}],
    }
    print(ed("set_player_config", **cfg))
    savec()


def stage_vars():
    have = {v["name"] for v in ed("list_variables", limit=400)["variables"]}
    for name, typ in [("CreepN", "integer"), ("LastCreep", "unit")]:
        if name in have:
            continue
        ed("create_variable", name=name, type=typ, is_array=(name == "CreepN"))
        print("  var", name, flush=True)
    if "CreepN" in have:
        ed("modify_variable", name="CreepN", is_array=True, array_size=16)
    savec()


ZONE_RANGE = [
    ("-2600", "-1200", "-2500", "-1300"),   # Zone0
    ("1200", "2600", "-2500", "-1300"),     # Zone1
    ("-2600", "-1200", "1200", "2600"),     # Zone2
    ("1200", "2600", "1200", "2600"),       # Zone3
]


def stage_spawn():
    for n in range(4):
        i = reset("V3_Spawn%d" % n, "地盘%d 刷怪（独立计数：生成+1 / 死亡-1）" % n)
        add_event(i, "TriggerRegisterTimerEventPeriodic", [lit("real", "4.0")])
        x1, x2, y1, y2 = ZONE_RANGE[n]
        body = [
            setv("real", "TempRealX", fn("real", "I2R", fn("integer", "GetRandomInt",
                                                         lit("integer", x1), lit("integer", x2)))),
            setv("real", "TempRealY", fn("real", "I2R", fn("integer", "GetRandomInt",
                                                         lit("integer", y1), lit("integer", y2)))),
            setv("unit", "TempUnit", fn("unit", "CreateUnit", NA, lit("unitcode", "nban"),
                                        gvar("real", "TempRealX"), gvar("real", "TempRealY"),
                                        lit("real", "270"))),
            act("SetUnitUserData", gvar("unit", "TempUnit"), lit("integer", str(n + 1))),
            script("set udg_CreepN[%d] = udg_CreepN[%d] + 1" % (n, n)),
            setv("unit", "LastCreep", gvar("unit", "TempUnit")),
            ifn([c_bool(fn("boolean", "IsUnitAliveBJ", gvar("unit", "HeroP", index=n)), "true")],
                [act("IssueTargetOrder", gvar("unit", "TempUnit"),
                     preset("unitorderutarg", "UnitOrderAttackUnit"),
                     gvar("unit", "HeroP", index=n))]),
        ]
        add(i, ifn([c_int(gvar("integer", "CreepN", index=n), LT, lit("integer", "4"))], body))
        savec()
        print("  V3_Spawn%d ok" % n, flush=True)
    print("SPAWN OK")


def stage_creepdead():
    i = reset("V3_CreepDead", "野怪死亡：对应地盘计数 -1（下限 0）")
    add_event(i, "TriggerRegisterAnyUnitEventBJ", [preset("playerunitevent", "PlayerUnitEventDeath")])
    add(i, setv("unit", "TempUnit", fn("unit", "GetDyingUnit")))
    add(i, setv("player", "TempPl", fn("player", "GetOwningPlayer", gvar("unit", "TempUnit"))))
    inner = [
        setv("integer", "TempInt", fn("integer", "GetUnitUserData", gvar("unit", "TempUnit"))),
        ifn([c_int(gvar("integer", "TempInt"), GE, lit("integer", "1"))], [
            script("set udg_TempInt = udg_TempInt - 1"),
            script("set udg_CreepN[udg_TempInt] = IMaxBJ(udg_CreepN[udg_TempInt] - 1, 0)"),
        ]),
    ]
    add(i, ifn([c_player(gvar("player", "TempPl"), NA)], inner))
    savec()
    print("CREEPDEAD OK")


def stage_ally():
    i = idx_of("V3_Setup")
    lines = []
    for a in range(4):
        for b in range(4):
            if a == b:
                continue
            lines.append("call SetPlayerAlliance(Player(%d), Player(%d), ALLIANCE_PASSIVE, true)" % (a, b))
            lines.append("call SetPlayerAlliance(Player(%d), Player(%d), ALLIANCE_SHARED_VISION, true)" % (a, b))
    for k in range(0, len(lines), 6):
        for code in lines[k:k + 6]:
            add(i, script(code))
        savec()
    print("ALLY OK", len(lines))


def stage_test():
    # 1) 每 2 秒用英雄打死最近刷出的怪（验证 生成+1/死亡-1 循环与杀怪得分）
    i = reset("V3_TKill", "临时自测：每2秒杀一只野怪")
    add_event(i, "TriggerRegisterTimerEventPeriodic", [lit("real", "2.0")])
    add(i, script("call UnitDamageTarget(udg_H0, udg_LastCreep, 99999, true, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_NORMAL, WEAPON_TYPE_WHOKNOWS)"))
    savec()

    # 2) 每 4 秒打印四个地盘的计数 + 玩家1 品阶/修为
    t = reset("V3_TStat", "临时自测：打印计数")
    add_event(t, "TriggerRegisterTimerEventPeriodic", [lit("real", "4.0")])
    add(t, script("set udg_Msg = \"S \" + I2S(udg_CreepN[0]) + I2S(udg_CreepN[1]) + I2S(udg_CreepN[2]) + I2S(udg_CreepN[3]) + \"  T\" + I2S(udg_Tier[0]) + \" X\" + I2S(udg_XiuWei[0]) + \"/\" + I2S(udg_XiuNeed[0])"))
    add(t, sayv(P[0]))
    savec()

    # 3) 3 秒时打印 12 组两两同盟状态（1=同盟 0=敌对）
    a = reset("V3_TAlly", "临时自测：同盟状态")
    add_event(a, "TriggerRegisterTimerEventSingle", [lit("real", "3.0")])
    add(a, setv("string", "Msg", lit("string", "AL ")))
    pairs = [(x, y) for x in range(4) for y in range(4) if x != y]
    for k, (x, y) in enumerate(pairs):
        cond = node("condition", "OperatorCompareBoolean",
                    [fn("boolean", "GetPlayerAlliance", P[x], P[y],
                        preset("alliancetype", "AllianceTypePassive")), EQ, lit("boolean", "true")], 0)
        add(a, ifn([cond],
                   [script("set udg_Msg = udg_Msg + \"%d%d:1 \"" % (x, y))],
                   [script("set udg_Msg = udg_Msg + \"%d%d:0 \"" % (x, y))]))
        print("  pair", x, y, flush=True)
    add(a, sayv(P[0]))
    savec()
    print("TEST OK")


def stage_droptest():
    for name in ("V3_TKill", "V3_TStat", "V3_TAlly"):
        try:
            i = idx_of(name)
        except KeyError:
            continue
        ed("delete_trigger", category_index=CAT, trigger_index=i)
        print("  deleted", name, flush=True)
    savec()
    print("DROPTEST OK")


STAGES = {
    "players": stage_players, "vars": stage_vars, "spawn": stage_spawn,
    "creepdead": stage_creepdead, "ally": stage_ally, "test": stage_test,
    "droptest": stage_droptest,
}

if __name__ == "__main__":
    STAGES[sys.argv[1]]()
