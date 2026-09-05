@echo off
setlocal
set "ROOT=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%tools\relay_mcp\setup_relay_mcp.ps1" %*
endlocal
