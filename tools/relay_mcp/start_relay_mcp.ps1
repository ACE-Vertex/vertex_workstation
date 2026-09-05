param(
  [string]$IngestToken = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (
  Split-Path -Parent $PSScriptRoot
)

$RuntimeRoot = Join-Path `
  $env:LOCALAPPDATA `
  "VertexWorkstation\runtimes\relay_mcp_v1"

$Python = Join-Path `
  $RuntimeRoot `
  "venv\Scripts\python.exe"

$Server = Join-Path `
  $Root `
  "tools\relay_mcp\vertex_relay_mcp.py"

if (-not (Test-Path $Python)) {
  Write-Error (
    "Relay MCP runtime is missing. Run " +
    "VERTEX_RELAY_MCP_SETUP.cmd first."
  )
  exit 2
}

if (-not (Test-Path $Server)) {
  Write-Error "Relay MCP server missing: $Server"
  exit 3
}

if ($IngestToken) {
  $env:VERTEX_RELAY_INGEST_TOKEN = $IngestToken
}

$env:PYTHONPATH = (
  Join-Path $Root "tools\relay_mcp"
)

Write-Host ""
Write-Host "VERTEX RELAY MCP APP BOUNDARY"
Write-Host "-----------------------------"
Write-Host "MCP      : http://127.0.0.1:8000/mcp"
Write-Host "INGEST   : http://127.0.0.1:8000/vertex-relay"
Write-Host "HEALTH   : http://127.0.0.1:8000/health"
Write-Host "MODE     : LOCAL DEVELOPMENT"
Write-Host ""
Write-Host (
  "NOTE: ChatGPT cloud cannot reach localhost. " +
  "Production requires a public HTTPS MCP endpoint."
)
Write-Host ""

& $Python $Server
exit $LASTEXITCODE
