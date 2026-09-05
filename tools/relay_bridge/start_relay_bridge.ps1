param(
  [int]$Port = 47821,
  [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (
  Split-Path -Parent $PSScriptRoot
)

$Bridge = Join-Path `
  $Root `
  "tools\relay_bridge\vertex_relay_bridge.py"

if (-not (Test-Path -LiteralPath $Bridge)) {
  Write-Error "Relay Bridge not found: $Bridge"
  exit 2
}

$Python = Get-Command python -ErrorAction SilentlyContinue

if (-not $Python) {
  Write-Error "Python was not found on PATH."
  exit 3
}

Write-Host ""
Write-Host "VERTEX RELAY BRIDGE"
Write-Host "-------------------"
Write-Host "Host : $HostAddress"
Write-Host "Port : $Port"
Write-Host ""

& $Python.Source `
  $Bridge `
  --host $HostAddress `
  --port $Port

exit $LASTEXITCODE
