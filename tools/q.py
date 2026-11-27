#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Thin wrapper: call a kkwe tool and print readable result.

  python -I q.py <tool> '<json>' [--raw]
"""
import json
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from kkwe_client import MCP  # noqa: E402


def main():
    tool = sys.argv[1]
    raw = sys.argv[2] if len(sys.argv) > 2 else "{}"
    if raw.startswith("@"):
        with open(raw[1:], "r", encoding="utf-8") as f:
            raw = f.read()
    args = json.loads(raw)
    m = MCP()
    m.init()
    r = m.call(tool, args)
    if "error" in r:
        print("RPC ERROR:", json.dumps(r["error"], ensure_ascii=False))
        return
    res = r.get("result", {})
    parts = []
    for c in res.get("content", []):
        t = c.get("text", "")
        try:
            parts.append(json.loads(t))
        except Exception:
            parts.append(t)
    out = parts[0] if len(parts) == 1 else parts
    if "--raw" in sys.argv:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=1)[:20000])
    if res.get("isError"):
        print("[[IS_ERROR]]")


if __name__ == "__main__":
    main()
