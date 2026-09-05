@echo off
setlocal
set "ROOT=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%tools\relay_bridge\start_relay_bridge.ps1" %*
endlocal
