param([int]$TargetPid=6388,[string]$CloseTitle="")
Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class WEnum {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  static string Txt(IntPtr h){ var sb=new StringBuilder(512); GetWindowTextW(h,sb,512); return sb.ToString(); }
  static string Cls(IntPtr h){ var sb=new StringBuilder(256); GetClassNameW(h,sb,256); return sb.ToString(); }
  public static List<string> List(uint pid){
    var res=new List<string>();
    EnumWindows((h,l)=>{
      uint p; GetWindowThreadProcessId(h, out p);
      if(p==pid) res.Add(h.ToInt64()+"\t"+IsWindowVisible(h)+"\t"+Cls(h)+"\t"+Txt(h));
      return true;
    }, IntPtr.Zero);
    return res;
  }
  public static List<string> Children(long hwnd){
    var res=new List<string>();
    EnumChildWindows(new IntPtr(hwnd),(h,l)=>{
      res.Add(h.ToInt64()+"\t"+IsWindowVisible(h)+"\t"+Cls(h)+"\t"+Txt(h));
      return true;
    }, IntPtr.Zero);
    return res;
  }
  public static long FindByTitle(string part){
    long found=0;
    EnumWindows((h,l)=>{
      uint p; GetWindowThreadProcessId(h, out p);
      if(Txt(h).Contains(part)){ found=h.ToInt64(); return false; }
      return true;
    }, IntPtr.Zero);
    return found;
  }
  public static bool Close(long hwnd){ return PostMessage(new IntPtr(hwnd), 0x0010, IntPtr.Zero, IntPtr.Zero); }
}
"@
if ($CloseTitle -ne "") {
  $h = [WEnum]::FindByTitle($CloseTitle)
  Write-Output ("found=" + $h)
  if ($h -ne 0) { Write-Output ("close=" + [WEnum]::Close($h)) }
} else {
  foreach ($l in [WEnum]::List([uint32]$TargetPid)) { Write-Output $l }
  Write-Output ("fg=" + [WEnum]::GetForegroundWindow().ToInt64())
}
