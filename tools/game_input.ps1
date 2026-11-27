# Win32 input injection for the Warcraft III window (test only).
# Usage:
#   powershell -File tools/game_input.ps1 -Action click -X 906 -Y 472
#   powershell -File tools/game_input.ps1 -Action key -Key F2
param(
  [string]$Action = "click",
  [int]$X = 0,
  [int]$Y = 0,
  [string]$Key = "F2"
)

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class Inp {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();

    [StructLayout(LayoutKind.Sequential)]
    public struct KEYBDINPUT { public ushort wVk; public ushort wScan; public uint dwFlags; public uint time; public IntPtr dwExtraInfo; }
    [StructLayout(LayoutKind.Explicit)]
    public struct INPUTUNION { [FieldOffset(0)] public KEYBDINPUT ki; }
    [StructLayout(LayoutKind.Sequential)]
    public struct INPUT { public uint type; public INPUTUNION u; }

    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint SendInput(uint n, INPUT[] inputs, int size);

    public const uint INPUT_KEYBOARD = 1;
    public const uint KEYEVENTF_KEYUP = 0x0002;
    public const uint KEYEVENTF_SCANCODE = 0x0008;

    public static void KeyScan(ushort scan) {
        INPUT[] down = new INPUT[1];
        down[0].type = INPUT_KEYBOARD;
        down[0].u.ki.wScan = scan;
        down[0].u.ki.dwFlags = KEYEVENTF_SCANCODE;
        SendInput(1, down, Marshal.SizeOf(typeof(INPUT)));
        INPUT[] up = new INPUT[1];
        up[0].type = INPUT_KEYBOARD;
        up[0].u.ki.wScan = scan;
        up[0].u.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;
        SendInput(1, up, Marshal.SizeOf(typeof(INPUT)));
    }

    public static void KeyVk(ushort vk) {
        INPUT[] down = new INPUT[1];
        down[0].type = INPUT_KEYBOARD;
        down[0].u.ki.wVk = vk;
        SendInput(1, down, Marshal.SizeOf(typeof(INPUT)));
        INPUT[] up = new INPUT[1];
        up[0].type = INPUT_KEYBOARD;
        up[0].u.ki.wVk = vk;
        up[0].u.ki.dwFlags = KEYEVENTF_KEYUP;
        SendInput(1, up, Marshal.SizeOf(typeof(INPUT)));
    }
}
'@

$MAP = @{ "F1"=0x3B; "F2"=0x3C; "F3"=0x3D; "F4"=0x3E; "ESC"=0x01; "ENTER"=0x1C; "SPACE"=0x39 }

$game = Get-Process War3 -ErrorAction SilentlyContinue
if (-not $game) { Write-Output "game not running"; exit 1 }
[void][Inp]::SetForegroundWindow($game.MainWindowHandle)
Start-Sleep -Milliseconds 300

if ($Action -eq "click") {
    [void][Inp]::SetCursorPos($X, $Y)
    Start-Sleep -Milliseconds 120
    [Inp]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)   # left down
    Start-Sleep -Milliseconds 60
    [Inp]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)   # left up
    Write-Output "clicked $X,$Y"
} elseif ($Action -eq "key") {
    $code = $MAP[$Key.ToUpper()]
    if (-not $code) { Write-Output "unknown key $Key"; exit 1 }
    [Inp]::KeyScan([uint16]$code)
    Start-Sleep -Milliseconds 120
    [Inp]::KeyVk([uint16]$code)
    Write-Output "pressed $Key"
} else {
    Write-Output "unknown action"
}

# --- PostMessage based key injection (works for games reading window messages) ---
if ($Action -eq "postkey") {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class PM {
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
}
'@ -ErrorAction SilentlyContinue
    $vk = @{ "F1"=0x70; "F2"=0x71; "F3"=0x72; "ENTER"=0x0D; "ESC"=0x1B }[$Key.ToUpper()]
    if (-not $vk) { Write-Output "unknown key"; exit 1 }
    $h = $game.MainWindowHandle
    [void][PM]::PostMessage($h, 0x0100, [IntPtr]$vk, [IntPtr]0x00000001)  # WM_KEYDOWN
    Start-Sleep -Milliseconds 80
    [void][PM]::PostMessage($h, 0x0101, [IntPtr]$vk, [IntPtr]0xC0000001)  # WM_KEYUP
    Write-Output "posted $Key (vk=$vk)"
}
