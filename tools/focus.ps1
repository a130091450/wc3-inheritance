Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class F {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x,int y,int cx,int cy,uint flags);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
}
"@
$h = [IntPtr]::new([int64]$args[0])
[F]::ShowWindow($h, 9) | Out-Null      # SW_RESTORE
[F]::SetWindowPos($h, [IntPtr]::new(-1), 0,0,0,0, 0x0001 -bor 0x0002) | Out-Null  # HWND_TOPMOST, NOSIZE|NOMOVE
[F]::SetWindowPos($h, [IntPtr]::new(-2), 0,0,0,0, 0x0001 -bor 0x0002) | Out-Null  # NOTOPMOST
[F]::BringWindowToTop($h) | Out-Null
[F]::SetForegroundWindow($h) | Out-Null
Write-Output ("fg=" + [F]::GetForegroundWindow().ToInt64() + " target=" + $h.ToInt64())
