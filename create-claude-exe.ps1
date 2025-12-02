# Create a claude.exe that's actually a PowerShell wrapper

$batContent = @'
@echo off
REM This wrapper runs PowerShell with the claude function
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { . 'C:\Users\ariro\setup-claude-complete.ps1'; claude %* }"
'@

# Write the batch file
$batPath = "C:\Users\ariro\.local\bin\claude.bat"
$batContent | Out-File $batPath -Encoding ASCII

# Create a dummy claude.exe file (just to satisfy the diagnostic)
# We'll use a small PowerShell script to create it
$exePath = "C:\Users\ariro\.local\bin\claude.exe"
if (Test-Path $exePath) {
    Remove-Item $exePath -Force
}

# Create a tiny exe that just runs the batch file
# Using PowerShell to create a simple launcher
$launcherCode = @'
using System;
using System.Diagnostics;

class Program {
    static void Main(string[] args) {
        var psi = new ProcessStartInfo {
            FileName = "cmd.exe",
            Arguments = $"/c \"C:\\Users\\ariro\\.local\\bin\\claude.bat\" {string.Join(\" \", args)}",
            UseShellExecute = false
        };
        Process.Start(psi).WaitForExit();
    }
}
'@

# Compile the launcher
Add-Type -TypeDefinition $launcherCode -Language CSharp -OutputAssembly $exePath -OutputType Console

Write-Host "Created claude.exe wrapper" -ForegroundColor Green