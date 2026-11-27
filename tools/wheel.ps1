param([int]$X=800,[int]$Y=500,[int]$N=6)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WH {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint dx,uint dy,int d,UIntPtr e);
}
"@
[WH]::SetCursorPos($X,$Y) | Out-Null
Start-Sleep -Milliseconds 150
for ($i=0;$i -lt $N;$i++){ [WH]::mouse_event(0x0800,0,0,-120,[UIntPtr]::Zero); Start-Sleep -Milliseconds 120 }
Write-Output "wheel done"
