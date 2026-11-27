#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build helpers for KKWE ECA payloads.

Import in build scripts:
    from eca import *
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kkwe_client import MCP  # noqa: E402


# ---------- parameter constructors ----------
def preset(type_name, value):
    """Enum / keyword dropdown value."""
    return {"type_id": 0, "type_name": type_name, "value": value}


def gvar(type_name, name, index=None):
    """Global variable (optionally array element)."""
    p = {"type_id": 1, "type_name": type_name, "value": name}
    if index is not None:
        p["array_index"] = {"type_id": 3, "type_name": "integer", "value": str(index)}
    return p


def fn(ret_type, name, *params):
    """Function call."""
    return {"type_id": 2, "type_name": ret_type, "value": name, "func_params": list(params)}


def lit(type_name, value):
    """Literal value."""
    return {"type_id": 3, "type_name": type_name, "value": str(value)}


def local(type_name, name):
    """Local variable reference (bare name)."""
    return {"type_id": 3, "type_name": "scriptcode", "value": name}


def raw(code):
    """Raw scriptcode expression (YDWE arithmetic / code)."""
    return {"type_id": 3, "type_name": "scriptcode", "value": code}


def node(kind, name, params, group_id=0, children=None):
    return {
        "type": kind,
        "group_id": group_id,
        "name": name,
        "children": children or [],
        "parameters": params,
    }


def if_then(cond_name, cond_params, actions, else_actions=None):
    """Build IfThenElseMultiple node; groups: 0=cond 1=then 2=else."""
    children = [node("condition", cond_name, cond_params, 0)]
    for a in actions:
        a = dict(a)
        a["group_id"] = 1
        children.append(a)
    for a in (else_actions or []):
        a = dict(a)
        a["group_id"] = 2
        children.append(a)
    return node("action", "IfThenElseMultiple", [], -1, children)


def act(name, *params, children=None):
    return node("action", name, list(params), -1, children)


# ---------- MCP driver ----------
class Editor:
    def __init__(self):
        self.m = MCP()
        self.m.init()

    def __call__(self, tool, **args):
        r = self.m.call(tool, args)
        res = r.get("result", {})
        txt = ""
        if res.get("content"):
            txt = res["content"][0].get("text", "")
        try:
            val = json.loads(txt)
        except Exception:
            val = txt
        if res.get("isError"):
            raise RuntimeError("%s 失败: %s" % (tool, txt))
        return val
