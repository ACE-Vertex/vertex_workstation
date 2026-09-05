param(
  [switch]$Force
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (
  Split-Path -Parent $PSScriptRoot
)

$RuntimeRoot = Join-Path `
  $env:LOCALAPPDATA `
  "VertexWorkstation\runtimes\relay_mcp_v1"

$Venv = Join-Path $RuntimeRoot "venv"
$RuntimePython = Join-Path $Venv "Scripts\python.exe"
$Requirements = Join-Path `
  $Root `
  "tools\relay_mcp\requirements.txt"

$PublicPyPI = "https://pypi.org/simple"

function Test-CompatiblePython {
  param(
    [Parameter(Mandatory = $true)]
    [string]$PythonPath
  )

  if (-not (Test-Path -LiteralPath $PythonPath)) {
    return $false
  }

  try {
    $Result = & $PythonPath -c `
      "import sys; print(int(sys.version_info >= (3,10))); print(sys.version.split()[0]); print(sys.executable)" `
      2>$null

    if ($LASTEXITCODE -ne 0) {
      return $false
    }

    $Lines = @($Result)
    if ($Lines.Count -lt 3) {
      return $false
    }

    if ($Lines[0].Trim() -ne "1") {
      Write-Host (
        "SKIP PYTHON < 3.10 : " +
        $Lines[1].Trim() +
        " @ " +
        $Lines[2].Trim()
      )
      return $false
    }

    return $true
  } catch {
    return $false
  }
}

function Get-PythonVersion {
  param(
    [Parameter(Mandatory = $true)]
    [string]$PythonPath
  )

  return (
    & $PythonPath -c `
      "import sys; print(sys.version.split()[0])"
  ).Trim()
}

function Add-Candidate {
  param(
    [System.Collections.Generic.List[string]]$List,
    [string]$Path
  )

  if (-not $Path) {
    return
  }

  try {
    $Resolved = (
      Resolve-Path -LiteralPath $Path -ErrorAction Stop
    ).Path
  } catch {
    return
  }

  if (-not $List.Contains($Resolved)) {
    $List.Add($Resolved)
  }
}

function Resolve-CompatiblePython {
  $Candidates = New-Object `
    "System.Collections.Generic.List[string]"

  # Prefer ecosystem-stable CPython versions before the globally-resolved
  # `python`, which may point to an older Anaconda installation.
  $PyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue

  if ($PyLauncher) {
    foreach ($Version in @(
      "3.12",
      "3.11",
      "3.13",
      "3.10",
      "3.14"
    )) {
      try {
        $Resolved = & $PyLauncher.Source `
          "-$Version" `
          -c `
          "import sys; print(sys.executable)" `
          2>$null

        if ($LASTEXITCODE -eq 0 -and $Resolved) {
          Add-Candidate `
            -List $Candidates `
            -Path ($Resolved | Select-Object -First 1)
        }
      } catch {
        # Continue probing.
      }
    }
  }

  foreach ($CommandName in @(
    "python3.12",
    "python3.11",
    "python3.13",
    "python3.10",
    "python3",
    "python"
  )) {
    $Command = Get-Command `
      $CommandName `
      -ErrorAction SilentlyContinue

    if ($Command -and $Command.Source) {
      Add-Candidate `
        -List $Candidates `
        -Path $Command.Source
    }
  }

  foreach ($VersionDir in @(
    "Python312",
    "Python311",
    "Python313",
    "Python310",
    "Python314"
  )) {
    foreach ($Base in @(
      (Join-Path $env:LOCALAPPDATA "Programs\Python"),
      "C:\Program Files",
      "C:\"
    )) {
      $Candidate = Join-Path `
        (Join-Path $Base $VersionDir) `
        "python.exe"

      Add-Candidate `
        -List $Candidates `
        -Path $Candidate
    }
  }

  Write-Host ""
  Write-Host "PYTHON CANDIDATE PROBE"
  Write-Host "----------------------"

  foreach ($Candidate in $Candidates) {
    if (Test-CompatiblePython -PythonPath $Candidate) {
      $Version = Get-PythonVersion `
        -PythonPath $Candidate

      Write-Host (
        "SELECTED PYTHON " +
        $Version +
        " @ " +
        $Candidate
      )

      return $Candidate
    }
  }

  throw (
    "No compatible CPython 3.10+ runtime was found. " +
    "The MCP Python SDK requires Python 3.10+. " +
    "The globally resolved Python may be an older Anaconda runtime."
  )
}

New-Item `
  -ItemType Directory `
  -Force `
  -Path $RuntimeRoot `
  | Out-Null

$BasePython = Resolve-CompatiblePython

$ExistingRuntimeCompatible = $false

if (Test-Path -LiteralPath $RuntimePython) {
  $ExistingRuntimeCompatible = Test-CompatiblePython `
    -PythonPath $RuntimePython
}

if (
  $Force -or
  (
    (Test-Path -LiteralPath $Venv) -and
    -not $ExistingRuntimeCompatible
  )
) {
  Write-Host (
    "RECREATE MCP VENV: " +
    $Venv
  )

  Remove-Item `
    -LiteralPath $Venv `
    -Recurse `
    -Force
}

if (-not (Test-Path -LiteralPath $RuntimePython)) {
  Write-Host (
    "CREATE MCP VENV FROM: " +
    $BasePython
  )

  & $BasePython -m venv $Venv

  if ($LASTEXITCODE -ne 0) {
    throw "Failed to create Relay MCP venv."
  }
}

if (-not (Test-CompatiblePython -PythonPath $RuntimePython)) {
  throw (
    "Created MCP venv is not Python 3.10+."
  )
}

$RuntimeVersion = Get-PythonVersion `
  -PythonPath $RuntimePython

Write-Host ""
Write-Host (
  "MCP RUNTIME PYTHON=" +
  $RuntimeVersion
)
Write-Host (
  "MCP RUNTIME EXE=" +
  $RuntimePython
)
Write-Host (
  "PIP INDEX=" +
  $PublicPyPI
)
Write-Host ""

# Isolated pip ignores Anaconda/user pip configuration and environment-based
# package indexes for this private Vertex runtime.
& $RuntimePython -m pip `
  --isolated `
  install `
  --disable-pip-version-check `
  --index-url $PublicPyPI `
  --upgrade `
  "pip>=24.0"

if ($LASTEXITCODE -ne 0) {
  throw "Relay MCP isolated pip bootstrap failed."
}

& $RuntimePython -m pip `
  --isolated `
  install `
  --disable-pip-version-check `
  --index-url $PublicPyPI `
  -r $Requirements

if ($LASTEXITCODE -ne 0) {
  throw (
    "Relay MCP dependency installation failed. " +
    "Python=" +
    $RuntimeVersion +
    "; Index=" +
    $PublicPyPI
  )
}

& $RuntimePython -c `
  "import mcp,sys; print('MCP_IMPORT=PASS'); print('PYTHON=' + sys.version.split()[0]); print('EXE=' + sys.executable)"

if ($LASTEXITCODE -ne 0) {
  throw "Relay MCP import probe failed."
}

Write-Host ""
Write-Host "VERTEX RELAY MCP RUNTIME READY"
Write-Host "Python: $RuntimePython"
Write-Host "Runtime: $RuntimeRoot"
Write-Host "PYTHON_310_PLUS=PASS"
Write-Host "PUBLIC_PYPI_ISOLATED=PASS"
