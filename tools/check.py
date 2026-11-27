#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read back a trigger and validate for silent-failure markers."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eca import Editor

ed = Editor()
demo = [c["index"] for c in ed("list_categories") if c["name"] == "Demo"][0]
trigs = ed("list_triggers", category_index=demo)["triggers"]
name = sys.argv[1] if len(sys.argv) > 1 else None
if name:
    trigs = [t for t in trigs if t["name"] == name]

for t in sorted(trigs, key=lambda x: x["name"]):
    d = ed("get_trigger", category_index=demo, trigger_index=t["trigger_index"])
    print("\n=== %s (idx %d, actions=%d) ===" % (d["name"], t["trigger_index"], t["action_count"]))
    bad = []

    def walk(nodes, depth=0):
        for n in nodes:
            p = n.get("params", []) or n.get("parameters", [])
            flags = []
            for x in p:
                if x.get("type_id") == -1:
                    flags.append("TYPE_ID:-1")
                v = x.get("value")
                if isinstance(v, str) and "TRIGSTR" in v:
                    flags.append("TRIGSTR")
                fc = x.get("func_call")
                if fc:
                    for y in fc.get("params", []):
                        if y.get("type_id") == -1:
                            flags.append("NEST:-1")
            if depth > 0 and n.get("group_id") == -1:
                flags.append("GROUP:-1")
            if flags:
                bad.append((n.get("name"), flags))
            vals = []
            for x in p:
                if x.get("type_id") == 2:
                    vals.append("%s(...)" % (x.get("value") or x.get("func_call", {}).get("name")))
                else:
                    vals.append(str(x.get("value"))[:24])
            print("  " * depth + "- %s.%s g=%s  %s  %s" % (
                n.get("type"), n.get("name"), n.get("group_id"), " | ".join(vals),
                ("<<" + ",".join(flags) + ">>") if flags else ""))
            walk(n.get("children", []), depth + 1)

    walk(d.get("ecas", []))
    print("  EVENTS:", [e.get("name") for e in d.get("ecas", []) if e.get("type") == "event"])
    print("  BAD:", bad if bad else "none")
