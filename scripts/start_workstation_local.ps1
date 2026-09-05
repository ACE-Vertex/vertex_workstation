$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $Root "runtime\local"
$PidFile = Join-Path $RuntimeDir "vite.pid"
$StdOut = Join-Path $RuntimeDir "vite.stdout.log"
$StdErr = Join-Path $RuntimeDir "vite.stderr.log"
$Url = "http://127.0.0.1:1420"

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

function Test-VertexLocalReady {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 1
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
    } catch {
        return $false
    }
}

function Resolve-NpmCmd {
    $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($npm) { return $npm.Source }

    $fallback = "C:\Program Files\nodejs\npm.cmd"
    if (Test-Path $fallback) { return $fallback }

    throw "npm.cmd not found"
}

function Resolve-Edge {
    $candidates = @(
        "$env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }
    return $null
}

function Start-VertexVite {
    $npm = Resolve-NpmCmd

    if (Test-Path $PidFile) {
        $existingPid = Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($existingPid) {
            $existing = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
            if ($existing -and (Test-VertexLocalReady)) {
                return
            }
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }

    if (Test-VertexLocalReady) {
        return
    }

    Remove-Item $StdOut, $StdErr -Force -ErrorAction SilentlyContinue

    $process = Start-Process `
        -FilePath $npm `
        -ArgumentList @("run", "dev") `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $StdOut `
        -RedirectStandardError $StdErr `
        -PassThru

    Set-Content -Path $PidFile -Value $process.Id -Encoding ascii
}

function Wait-VertexLocal {
    $deadline = [DateTime]::UtcNow.AddSeconds(20)
    while ([DateTime]::UtcNow -lt $deadline) {
        if (Test-VertexLocalReady) {
            return
        }
        Start-Sleep -Milliseconds 250
    }

    $tail = ""
    if (Test-Path $StdErr) {
        $tail = (Get-Content $StdErr -Tail 30 -ErrorAction SilentlyContinue) -join [Environment]::NewLine
    }
    throw "Vertex Workstation local server did not become ready.`n$tail"
}

function Open-VertexLocal {
    $edge = Resolve-Edge

    if ($edge) {
        Start-Process `
            -FilePath $edge `
            -ArgumentList @(
                "--app=$Url",
                "--new-window",
                "--start-maximized"
            ) | Out-Null
        return
    }

    Start-Process $Url | Out-Null
}

Start-VertexVite
Wait-VertexLocal
Open-VertexLocal
