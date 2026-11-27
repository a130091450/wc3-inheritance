param([int]$X=0,[int]$Y=0)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class RC {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint dx,uint dy,uint d,UIntPtr e);
}
"@
[RC]::SetCursorPos($X,$Y) | Out-Null
Start-Sleep -Milliseconds 150
[RC]::mouse_event(0x0008,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 60
[RC]::mouse_event(0x0010,0,0,0,[UIntPtr]::Zero)
Write-Output ("rclick {0},{1}" -f $X,$Y)
