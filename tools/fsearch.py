#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Search trigger functions compactly.

  python -I fsearch.py <keyword> [section] [limit]
"""
import json
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from kkwe_client import MCP  # noqa: E402


def main():
    kw = sys.argv[1] if len(sys.argv) > 1 else ""
    section = sys.argv[2] if len(sys.argv) > 2 else ""
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    args = {"search": kw, "limit": limit}
    if section:
        args["section"] = section
    m = MCP()
    m.init()
    r = m.call("list_trigger_functions", args)
    res = r.get("result", {})
    text = res["content"][0]["text"]
    data = json.loads(text)
    funcs = data.get("functions", data)
    print("total=%s" % data.get("total_matched", len(funcs)))
    for f in funcs:
        params = ",".join(p.get("type", "?") for p in f.get("params", []))
        print("%-12s %-42s (%s)  %s" % (
            f.get("section", "")[:12],
            f.get("name", ""),
            params,
            (f.get("display") or "")[:60],
        ))


if __name__ == "__main__":
    main()
