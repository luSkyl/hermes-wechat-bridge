[CmdletBinding()]
param(
    [string]$HermesWorkspaceRoot = '',
    [string]$ManifestPath = '',
    [int]$WebUiPort = 8648,
    [int]$BridgePort = 8787,
    [string]$PythonExe = 'python',
    [string]$BridgeConfig = '',
    [switch]$SkipBridgeDoctor,
    [switch]$SkipBridgeHttp,
    [switch]$SkipRuntimeVerify
)

$ErrorActionPreference = 'Stop'
$checks = New-Object System.Collections.Generic.List[object]

function Add-Check {
    param([string]$Name, [bool]$Ok, [string]$Message = '', [object]$Data = $null)
    $checks.Add([ordered]@{ name = $Name; ok = $Ok; message = $Message; data = $Data })
    $mark = if ($Ok) { 'PASS' } else { 'FAIL' }
    Write-Host "[$mark] $Name $Message"
}

function Resolve-OptionalPath {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return '' }
    if (Test-Path -LiteralPath $Path) { return (Resolve-Path -LiteralPath $Path).Path }
    return $Path
}

if ([string]::IsNullOrWhiteSpace($HermesWorkspaceRoot)) {
    $candidate = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..') -ErrorAction SilentlyContinue
    if ($candidate -and (Test-Path -LiteralPath (Join-Path $candidate.Path 'runtime\active-runtime.json'))) {
        $HermesWorkspaceRoot = $candidate.Path
    }
}

if (-not [string]::IsNullOrWhiteSpace($HermesWorkspaceRoot)) {
    $HermesWorkspaceRoot = Resolve-OptionalPath $HermesWorkspaceRoot
    if ([string]::IsNullOrWhiteSpace($ManifestPath)) { $ManifestPath = Join-Path $HermesWorkspaceRoot 'runtime\active-runtime.json' }
}

$ManifestPath = Resolve-OptionalPath $ManifestPath
$manifest = $null
if (Test-Path -LiteralPath $ManifestPath) {
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    Add-Check 'runtime manifest exists' $true $ManifestPath
    Add-Check 'manifest web ui root exists' (Test-Path -LiteralPath $manifest.web_ui.root) ([string]$manifest.web_ui.root)
    Add-Check 'manifest web ui cli exists' (Test-Path -LiteralPath $manifest.web_ui.cli) ([string]$manifest.web_ui.cli)
    Add-Check 'manifest web ui is local release' ([string]$manifest.web_ui.root -match 'local\.\d+$') ([string]$manifest.web_ui.root)
    Add-Check 'manifest core root exists' (Test-Path -LiteralPath $manifest.core.root) ([string]$manifest.core.root)
    Add-Check 'manifest gateway wrapper exists' (Test-Path -LiteralPath $manifest.paths.gateway_wrapper) ([string]$manifest.paths.gateway_wrapper)
} else {
    Add-Check 'runtime manifest exists' $false $ManifestPath
}

try {
    $health = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$WebUiPort/health" -TimeoutSec 10
    $payload = $health.Content | ConvertFrom-Json
    Add-Check 'web ui health ok' ($payload.status -eq 'ok') $health.Content $payload
    Add-Check 'gateway running in web ui health' ($payload.gateway -eq 'running') "gateway=$($payload.gateway)"
    Add-Check 'web ui version is 0.5.28' ($payload.webui_version -eq '0.5.28') "webui_version=$($payload.webui_version)"
} catch {
    Add-Check 'web ui health ok' $false ([string]$_.Exception.Message)
}

try {
    $conn = Get-NetTCPConnection -LocalPort $WebUiPort -State Listen -ErrorAction Stop | Select-Object -First 1
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$($conn.OwningProcess)"
    $command = [string]$proc.CommandLine
    Add-Check 'web ui port has listener' $true "pid=$($proc.ProcessId)" $command
    if ($manifest) { Add-Check 'web ui listener matches manifest root' $command.Contains([string]$manifest.web_ui.root) $command }
} catch {
    Add-Check 'web ui port has listener' $false ([string]$_.Exception.Message)
}

if (-not $SkipBridgeDoctor) {
    if ([string]::IsNullOrWhiteSpace($BridgeConfig)) { $BridgeConfig = Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path 'distribution\config.example.yaml' }
    try {
        $doctorOutput = & $PythonExe -m bridge.cli doctor --config $BridgeConfig 2>&1 | Out-String
        Add-Check 'bridge doctor succeeds' ($LASTEXITCODE -eq 0) $doctorOutput.Trim()
    } catch {
        Add-Check 'bridge doctor succeeds' $false ([string]$_.Exception.Message)
    }
}

if (-not $SkipBridgeHttp) {
    try {
        $bridgeHealth = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$BridgePort/health" -TimeoutSec 5
        Add-Check 'bridge http health reachable' ($bridgeHealth.StatusCode -eq 200) $bridgeHealth.Content
    } catch {
        Add-Check 'bridge http health reachable' $false ([string]$_.Exception.Message)
    }
}

if (-not $SkipRuntimeVerify -and -not [string]::IsNullOrWhiteSpace($HermesWorkspaceRoot)) {
    $verifyScript = Join-Path $HermesWorkspaceRoot 'scripts\verify-hermes-runtime.ps1'
    if (Test-Path -LiteralPath $verifyScript) {
        $evidenceDir = Join-Path $HermesWorkspaceRoot 'local-state\distribution-verify'
        New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
        $evidencePath = Join-Path $evidenceDir ('verify-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
        $verifyOutput = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $verifyScript -EvidencePath $evidencePath 2>&1 | Out-String
        Add-Check 'hermes runtime verifier succeeds' ($LASTEXITCODE -eq 0) $verifyOutput.Trim() $evidencePath
    } else {
        Add-Check 'hermes runtime verifier exists' $false $verifyScript
    }
}

$failed = @($checks | Where-Object { -not $_.ok })
$result = [ordered]@{
    ok = ($failed.Count -eq 0)
    generated_at = (Get-Date).ToString('o')
    checks = $checks
    summary = [ordered]@{ total = $checks.Count; failed = $failed.Count }
}
$result | ConvertTo-Json -Depth 8
if ($failed.Count -gt 0) { exit 1 }
