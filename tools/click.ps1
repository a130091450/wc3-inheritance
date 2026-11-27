param([int]$X=0,[int]$Y=0,[string]$Action="click",[int]$Key=0)
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Nat {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint dx,uint dy,uint d,UIntPtr e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@
if ($Action -eq "click") {
  [Nat]::SetCursorPos($X,$Y) | Out-Null
  Start-Sleep -Milliseconds 120
  [Nat]::mouse_event(0x0002,0,0,0,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 60
  [Nat]::mouse_event(0x0004,0,0,0,[UIntPtr]::Zero)
  Write-Output ("click {0},{1} fg={2}" -f $X,$Y,[Nat]::GetForegroundWindow())
} elseif ($Action -eq "key") {
  [Nat]::keybd_event([byte]$Key,0,0,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 60
  [Nat]::keybd_event([byte]$Key,0,2,[UIntPtr]::Zero)
  Write-Output ("key {0}" -f $Key)
} elseif ($Action -eq "enter") {
  [Nat]::keybd_event(13,0,0,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 60
  [Nat]::keybd_event(13,0,2,[UIntPtr]::Zero)
  Write-Output "enter"
}
