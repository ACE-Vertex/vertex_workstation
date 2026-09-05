\
@echo off
setlocal
cd /d "%~dp0"
where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo [Vertex Workstation] npm.cmd not found.
  exit /b 1
)
call npm.cmd run tauri:dev
