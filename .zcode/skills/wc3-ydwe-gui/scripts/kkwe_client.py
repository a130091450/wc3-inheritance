#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Minimal MCP-over-SSE client for KKWE editor plugin.

Usage:
  python -I kkwe_client.py list
  python -I kkwe_client.py call <tool_name> '<json args>'
  python -I kkwe_client.py call <tool_name> @args.json
"""
import json
import queue
import sys
import threading
import urllib.request
import urllib.parse

BASE = "http://127.0.0.1:19816"


class MCP:
    def __init__(self, base=BASE):
        self.base = base
        self.q = queue.Queue()
        self.endpoint = None
        self.ready = threading.Event()
        self.resp = urllib.request.urlopen(
            urllib.request.Request(
                base + "/sse", headers={"Accept": "text/event-stream"}
            ),
            timeout=600,
        )
        threading.Thread(target=self._read, daemon=True).start()
        if not self.ready.wait(10):
            raise RuntimeError("SSE endpoint handshake timeout")

    def _read(self):
        buf = []
        try:
            while True:
                raw = self.resp.readline()
                if not raw:
                    break
                line = raw.decode("utf-8", "replace").rstrip("\r\n")
                if line == "":
                    ev, data = None, []
                    for l in buf:
                        if l.startswith("event:"):
                            ev = l[6:].strip()
                        elif l.startswith("data:"):
                            data.append(l[5:].strip())
                    if data:
                        payload = "\n".join(data)
                        if ev == "endpoint":
                            ep = payload
                            if ep.startswith("http"):
                                self.endpoint = ep
                            else:
                                u = urllib.parse.urlsplit(self.base)
                                self.endpoint = "%s://%s%s" % (u.scheme, u.netloc, ep)
                            self.ready.set()
                        else:
                            self.q.put(payload)
                    buf = []
                else:
                    buf.append(line)
        except Exception:
            pass

    def _post(self, obj):
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(obj).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=120).read()

    def rpc(self, method, params=None, rid=1):
        self._post({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})
        while True:
            msg = json.loads(self.q.get(timeout=120))
            if msg.get("id") == rid:
                return msg

    def notify(self, method, params=None):
        self._post({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def init(self):
        r = self.rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "zcode-cli", "version": "1.0"},
            },
        )
        self.notify("notifications/initialized")
        return r

    def list_tools(self):
        out, cursor = [], None
        while True:
            p = {"cursor": cursor} if cursor else {}
            r = self.rpc("tools/list", p)
            res = r.get("result", {})
            out.extend(res.get("tools", []))
            cursor = res.get("nextCursor")
            if not cursor:
                break
        return out

    def call(self, name, args):
        r = self.rpc("tools/call", {"name": name, "arguments": args})
        return r


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    m = MCP()
    m.init()
    if cmd == "list":
        tools = m.list_tools()
        for t in tools:
            schema = t.get("inputSchema", {}).get("properties", {})
            req = t.get("inputSchema", {}).get("required", [])
            sig = ", ".join(("*" if k in req else "") + k for k in schema)
            print("%-38s %s" % (t["name"], "(" + sig + ")"))
        print("\nTOTAL:", len(tools))
    elif cmd == "call":
        name = sys.argv[2]
        raw = sys.argv[3] if len(sys.argv) > 3 else "{}"
        if raw.startswith("@"):
            with open(raw[1:], "r", encoding="utf-8") as f:
                raw = f.read()
        args = json.loads(raw)
        r = m.call(name, args)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print("unknown cmd")


if __name__ == "__main__":
    main()
