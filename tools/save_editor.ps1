param([int]$EditorPid=6388,[int]$WaitMs=2500)
Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class SaveEd {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint flags, UIntPtr extra);
  static string Txt(IntPtr h){ var sb=new StringBuilder(512); GetWindowTextW(h,sb,512); return sb.ToString(); }
  static string Cls(IntPtr h){ var sb=new StringBuilder(256); GetClassNameW(h,sb,256); return sb.ToString(); }
  public static long FindMain(uint pid){
    long found=0;
    EnumWindows((h,l)=>{
      uint p; GetWindowThreadProcessId(h,out p);
      if(p==pid && Txt(h).StartsWith("KKWE - [") && IsWindowVisible(h)){ found=h.ToInt64(); return false; }
      return true;
    }, IntPtr.Zero);
    return found;
  }
  public static List<long> Dialogs(uint pid){
    var res=new List<long>();
    EnumWindows((h,l)=>{
      uint p; GetWindowThreadProcessId(h,out p);
      if(p==pid && IsWindowVisible(h) && Cls(h)=="#32770") res.Add(h.ToInt64());
      return true;
    }, IntPtr.Zero);
    return res;
  }
  public static string TitleOf(long h){ return Txt(new IntPtr(h)); }
  public static void CtrlS(){ keybd_event(0x11,0,0,UIntPtr.Zero); keybd_event(0x53,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(80); keybd_event(0x53,0,2,UIntPtr.Zero); keybd_event(0x11,0,2,UIntPtr.Zero); }
  public static void Enter(){ keybd_event(0x0D,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(60); keybd_event(0x0D,0,2,UIntPtr.Zero); }
  public static bool Focus(long h){ return SetForegroundWindow(new IntPtr(h)); }
}
"@
$main = [SaveEd]::FindMain([uint32]$EditorPid)
Write-Output ("main=" + $main)
if ($main -eq 0) { Write-Output "main window not found"; exit 1 }
[SaveEd]::Focus($main) | Out-Null
Start-Sleep -Milliseconds 400
[SaveEd]::CtrlS()
Write-Output "ctrl+s sent"
Start-Sleep -Milliseconds $WaitMs
for ($i=0; $i -lt 6; $i++) {
  $ds = [SaveEd]::Dialogs([uint32]$EditorPid)
  if ($ds.Count -eq 0) { Write-Output ("no dialog at round " + $i); break }
  foreach ($d in $ds) {
    Write-Output ("dialog: " + $d + " " + [SaveEd]::TitleOf($d))
    [SaveEd]::Focus($d) | Out-Null
    Start-Sleep -Milliseconds 250
    [SaveEd]::Enter()
    Start-Sleep -Milliseconds 700
  }
}
Start-Sleep -Milliseconds 1500
Write-Output ("remaining dialogs: " + ([SaveEd]::Dialogs([uint32]$EditorPid)).Count)
