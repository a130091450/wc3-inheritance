#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""扫描/关闭 KKWE 编辑器的模态弹窗，防止弹窗卡死 MCP 会话。

用法:
  python -I tools/close_dialogs.py            # 只列出（安全）
  python -I tools/close_dialogs.py --close    # 关闭已知弹窗
  python -I tools/close_dialogs.py --close --all   # 关闭所有非主窗口
"""
import ctypes
import ctypes.wintypes as wt
import subprocess
import sys

user32 = ctypes.WinDLL("user32", use_last_error=True)

EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

# 已知必须处理的弹窗关键字
KNOWN = ["警告", "提示", "错误", "Syntax Errors", "新物体的ID", "确认", "信息", "无法"]
# 绝不关闭的内部窗口
KEEP = ["ydwe保存加速插件", "MSCTFIME UI", "Default IME", "触发编辑器", "另存为", "输入法"]


def list_windows(pid):
    out = []

    def cb(hwnd, lparam):
        p = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(n + 2)
            user32.GetWindowTextW(hwnd, buf, n + 2)
            cbuf = ctypes.create_unicode_buffer(128)
            user32.GetClassNameW(hwnd, cbuf, 128)
            if buf.value:
                out.append((hwnd, buf.value, cbuf.value))
        return True

    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return out


def find_pids():
    ps = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-Process | Where-Object {$_.ProcessName -match 'KKWE|worldedit|War3'} | ForEach-Object { $_.Id }"],
        capture_output=True, text=True)
    pids = []
    for line in ps.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            pids.append(int(line))
    return pids


def main():
    do_close = "--close" in sys.argv
    close_all = "--all" in sys.argv
    pids = find_pids()
    if not pids:
        print("no KKWE/war3 process")
        return

    found = 0
    for pid in pids:
        for hwnd, title, cls in list_windows(pid):
            if title.startswith("KKWE - [") or title == "KKWE" or "Warcraft" in title:
                continue
            if any(k in title for k in KEEP):
                continue
            hit = any(k in title for k in KNOWN)
            if not hit and not close_all:
                continue
            found += 1
            if do_close:
                ok = user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                print("CLOSE pid=%d hwnd=%s title=%r class=%s ok=%s" % (pid, hwnd, title, cls, bool(ok)))
            else:
                print("FOUND pid=%d hwnd=%s title=%r class=%s" % (pid, hwnd, title, cls))
    if found == 0:
        print("no dialog")


if __name__ == "__main__":
    main()
