#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression check for testmap.w3x demo.

Verifies: variables / regions / trigger structure / silent-failure markers /
compiled script content. Exit code 0 = all pass.

  python -I tools/verify.py [--compiled]
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor

MAP = "C:/Users/Administrator/Desktop/testmap/testmap.w3x"
W2L = "C:/games/KKWE_editor/plugin/w3x2lni_zhCN_v2.7.3/w2l.exe"
OUT = "C:/Users/Administrator/Desktop/testmap/.verify_out"

EXPECT = {
    "Demo_Init": ("TriggerRegisterTimerEventSingle", 16),
    "Demo_Pick": (None, 11),
    "Demo_F2": ("DzTriggerRegisterKeyEventTrg", 8),
    "Demo_F3": ("DzTriggerRegisterKeyEventTrg", 8),
    "Demo_Spawn": ("TriggerRegisterTimerEventPeriodic", 10),
    "Demo_Reward": ("TriggerRegisterAnyUnitEventBJ", 4),
}
VARS = {
    "HeroDialog": "dialog", "Hero": "unit", "HeroType": "unitcode",
    "HeroPicked": "boolean", "InTrain": "boolean", "Wave": "integer",
    "BtnP": "button", "BtnA": "button", "BtnI": "button",
    "Msg": "string", "TempUnit": "unit", "TempPl": "player",
    "TempGroup": "group", "gg_rct_BaseArea": "rect", "gg_rct_TrainArea": "rect",
}

results = []


def check(name, ok, detail=""):
    results.append((ok, name, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + (("  -> " + detail) if detail and not ok else ""))
    return ok


ed = Editor()
print("== 1. 分类与触发器 ==")
cats = {c["name"]: c["index"] for c in ed("list_categories")}
if not check("分类 Demo 存在", "Demo" in cats):
    print("无法继续"); sys.exit(1)
demo = cats["Demo"]
trigs = {t["name"]: t for t in ed("list_triggers", category_index=demo)["triggers"]}

for name, (ev, count) in EXPECT.items():
    t = trigs.get(name)
    check("触发器 %s 存在且启用" % name, bool(t) and t["enabled"])
    if t:
        check("%s 动作数 = %d" % (name, count), t["action_count"] == count,
              "实际 %d" % t["action_count"])

print("== 2. 事件 / 参数 / 静默失效标记 ==")
for name in EXPECT:
    if name not in trigs:
        continue
    d = ed("get_trigger", category_index=demo, trigger_index=trigs[name]["trigger_index"])
    events = [e["name"] for e in d["ecas"] if e.get("type") == "event"]
    want = EXPECT[name][0]
    if want is None:
        check("%s 无静态事件（运行时注册）" % name, len(events) == 0, str(events))
    else:
        check("%s 有且仅有 1 个事件" % name, len(events) == 1, str(events))
        if events:
            check("%s 事件类型正确" % name, events[0] == want, events[0])

    problems = []

    def walk(nodes, depth=0):
        for n in nodes:
            params = n.get("params", []) or n.get("parameters", [])
            for p in params:
                if p.get("type_id") == -1:
                    problems.append("%s 参数 type_id=-1" % n.get("name"))
                if p.get("type_id") == 2 and not (p.get("func_call") or {}).get("name"):
                    problems.append("%s 空函数调用" % n.get("name"))
                for q in (p.get("func_call") or {}).get("params", []):
                    if q.get("type_id") == -1:
                        problems.append("%s 嵌套参数丢失" % n.get("name"))
            if depth and n.get("group_id") == -1:
                problems.append("%s 子节点 group_id=-1" % n.get("name"))
            walk(n.get("children", []), depth + 1)

    walk(d["ecas"])
    check("%s 无静默失效标记" % name, not problems, "; ".join(problems))

print("== 3. 变量与区域 ==")
have = {v["name"]: v for v in ed("list_variables", limit=300)["variables"]}
for vname, vtype in VARS.items():
    v = have.get(vname)
    check("变量 %s (%s)" % (vname, vtype), bool(v) and v["type"] == vtype,
          v["type"] if v else "缺失")

regs = {r["name"]: r for r in ed("list_regions")["regions"]}
for rname, box in [("BaseArea", (-2816, -1792, -2816, -1792)),
                   ("TrainArea", (1664, 2944, 1664, 2944))]:
    r = regs.get(rname)
    ok = bool(r) and (r["left"], r["right"], r["bottom"], r["top"]) == box
    check("区域 %s 坐标" % rname, ok, json.dumps(r, ensure_ascii=False) if r else "缺失")

if "--compiled" in sys.argv:
    print("== 4. 编译产物 ==")
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    subprocess.run([W2L, "lni", MAP, OUT], capture_output=True)
    j_path = os.path.join(OUT, "map", "war3map.j")
    if check("解包得到 war3map.j", os.path.isfile(j_path)):
        src = open(j_path, encoding="utf-8", errors="replace").read()
        checks = [
            ("6 个 Demo 页面都编译进脚本", len(re.findall(r"^function InitTrig_Demo_", src, re.M)) == 6),
            ("无裸 Wave 变量（编译必失败）", "= Wave + 1" not in src and "( Wave)" not in src),
            ("波次自增使用 udg_Wave", "set udg_Wave = udg_Wave + 1" in src),
            ("F2 场景注册", "DzTriggerRegisterKeyEventTrg(gg_trg_Demo_F2, 1, 113)" in src),
            ("F3 场景注册", "DzTriggerRegisterKeyEventTrg(gg_trg_Demo_F3, 1, 114)" in src),
            ("对话框事件运行时注册", "TriggerRegisterDialogEvent(gg_trg_Demo_Pick, udg_HeroDialog)" in src),
            ("F3 复活分支", "ReviveHero(" in src),
            ("刷怪 2 只强盗", src.count("'nban'") == 2),
            ("刷怪上限 6", "> 6" in src),
            ("金币 +50", "AdjustPlayerStateBJ( 50" in src),
            ("英雄类型 3 种", all(x in src for x in ["'Hmkg'", "'Obla'", "'Hjai'"])),
            ("中文文案已解析（非 TRIGSTR 残留）",
             not any("TRIGSTR_" in ln for ln in src.splitlines() if not ln.strip().startswith("//"))),
        ]
        for label, ok in checks:
            check(label, ok)
        shutil.rmtree(OUT, ignore_errors=True)

print("\n" + "=" * 46)
bad = [r for r in results if not r[0]]
print("结果: %d 通过, %d 失败" % (len(results) - len(bad), len(bad)))
if bad:
    for _, n, d in bad:
        print("  - " + n + ("  " + d if d else ""))
sys.exit(1 if bad else 0)
