param(
    [Parameter(Mandatory = $true)]
    [string]$ReleaseRoot,
    [int]$Port = 8650,
    [Parameter(Mandatory = $true)]
    [string]$WorkspaceRoot,
    [string]$ShadowHome = (Join-Path $WorkspaceRoot ('local-state\overlay-shadow-webui-home-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))),
    [string]$NodeExe = 'node',
    [string]$HermesHome = (Join-Path $HOME '.hermes'),
    [string]$HermesBin = 'hermes'
)

$ErrorActionPreference = 'Stop'

function Resolve-RequiredPath {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Description not found: $Path"
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

function Assert-UnderRoot {
    param([string]$Path, [string]$Root)
    $fullPath = [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
    $fullRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd('\')
    if (-not $fullPath.StartsWith($fullRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing path outside workspace root: $fullPath"
    }
}

$release = Resolve-RequiredPath -Path $ReleaseRoot -Description 'Release root'
$workspace = Resolve-RequiredPath -Path $WorkspaceRoot -Description 'Workspace root'
Assert-UnderRoot -Path $ShadowHome -Root $workspace
$cli = Resolve-RequiredPath -Path (Join-Path $release 'bin\hermes-web-ui.mjs') -Description 'Web UI CLI'
Resolve-RequiredPath -Path $NodeExe -Description 'Node executable' | Out-Null

try {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop | Select-Object -First 1
    if ($conn) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
} catch {}

if (Test-Path -LiteralPath $ShadowHome) {
    Remove-Item -LiteralPath $ShadowHome -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $ShadowHome | Out-Null

$env:HERMES_WEB_UI_HOME = $ShadowHome
$env:HERMES_HOME = $HermesHome
$env:HERMES_BIN = $HermesBin
$env:NO_PROXY = '127.0.0.1,localhost,::1'
$env:no_proxy = $env:NO_PROXY
$env:HTTP_PROXY = ''
$env:HTTPS_PROXY = ''
$env:ALL_PROXY = ''
$env:http_proxy = ''
$env:https_proxy = ''
$env:all_proxy = ''

Push-Location $release
try {
    & $NodeExe $cli start --port $Port
    if ($LASTEXITCODE -ne 0) { throw "shadow start failed: $LASTEXITCODE" }
} finally {
    Pop-Location
}

try {
    Start-Sleep -Seconds 3
    $health = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 10
    if ($health.StatusCode -ne 200) { throw "Unexpected health status: $($health.StatusCode)" }
    Write-Host "Shadow smoke passed: $($health.Content)"
}
finally {
    & $NodeExe $cli stop
}
