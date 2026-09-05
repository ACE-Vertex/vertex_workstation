@echo off
setlocal
set "ROOT=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\bootstrap_vertex_relay_mcp_runtime_000015.ps1" %*
endlocal
