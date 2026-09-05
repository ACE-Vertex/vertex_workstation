param(
  [switch]$Force
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Setup = Join-Path $Root "VERTEX_RELAY_MCP_SETUP.cmd"
$RuntimeVerify = Join-Path `
  $Root `
  "scripts\verify_vertex_relay_mcp_runtime_000014.py"

if (-not (Test-Path -LiteralPath $Setup)) {
  Write-Error "Missing MCP setup launcher: $Setup"
  exit 2
}

if (-not (Test-Path -LiteralPath $RuntimeVerify)) {
  Write-Error "Missing MCP runtime verifier: $RuntimeVerify"
  exit 3
}

Write-Host ""
Write-Host "VERTEX RELAY MCP RUNTIME BOOTSTRAP 000015"
Write-Host "-----------------------------------------"
Write-Host "Scope  : isolated LOCALAPPDATA runtime"
Write-Host "Global : no Python package mutation"
Write-Host ""

if ($Force) {
  & $Setup -Force
} else {
  & $Setup
}

if ($LASTEXITCODE -ne 0) {
  Write-Error "MCP runtime setup failed."
  exit $LASTEXITCODE
}

$RuntimePython = Join-Path `
  $env:LOCALAPPDATA `
  "VertexWorkstation\runtimes\relay_mcp_v1\venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $RuntimePython)) {
  Write-Error "Isolated MCP Python runtime missing: $RuntimePython"
  exit 4
}

Write-Host ""
Write-Host "RUNNING REAL MCP PROTOCOL VERIFIER..."
Write-Host ""

& $RuntimePython $RuntimeVerify

if ($LASTEXITCODE -ne 0) {
  Write-Error "Real MCP runtime verification failed."
  exit $LASTEXITCODE
}

& $RuntimePython -c `
  "import mcp,sys; print('MCP_IMPORT=PASS'); print('PYTHON=' + sys.executable)"

if ($LASTEXITCODE -ne 0) {
  Write-Error "MCP import verification failed."
  exit $LASTEXITCODE
}

Write-Host ""
Write-Host "MCP_RUNTIME_BOOTSTRAP_000015=PASS"
Write-Host "NEXT_GATE=SECURE_MCP_TUNNEL_OR_REMOTE_MCP_CONNECTION"
