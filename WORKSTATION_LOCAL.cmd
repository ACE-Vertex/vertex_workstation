\
@echo off
setlocal
cd /d "%~dp0"

set "PSH=%ProgramFiles%\PowerShell\7\pwsh.exe"
if not exist "%PSH%" set "PSH=powershell.exe"

start "" /min "%PSH%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_workstation_local.ps1"
exit /b 0
