# Vertex Workstation — Local Development Entry 000003

## Canonical local-development entry

`G:\Vertex_Project\Development\vertex_workstation\WORKSTATION_LOCAL.cmd`

## Purpose

Fast UI/React development without rebuilding or launching the Tauri shell.

Flow:

`WORKSTATION_LOCAL.cmd`
→ hidden PowerShell helper
→ `npm run dev`
→ Vite on `127.0.0.1:1420`
→ Microsoft Edge app-mode window

## Behavior

- Reuses an already-running local Vite server when available.
- Tracks the Vite process PID in `runtime/local/vite.pid`.
- Captures stdout/stderr to `runtime/local/`.
- Waits for the local HTTP endpoint before opening the app window.
- Uses Edge app mode when Edge is installed; otherwise opens the system browser.
- Does not invoke `tauri dev`.
- Does not alter the Tauri production build protocol.

## Canonical entries

- `WORKSTATION_LOCAL.cmd` — browser/Vite local development
- `WORKSTATION_DEV.cmd` — Tauri development

Production candidates continue to use:

`npm run tauri:build`

through the existing Workstation production builder.
