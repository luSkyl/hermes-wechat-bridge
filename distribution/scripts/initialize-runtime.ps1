[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HermesWorkspaceRoot,
    [Parameter(Mandatory = $true)]
    [string]$CoreRoot,
    [Parameter(Mandatory = $true)]
    [string]$WebUiReleaseRoot,
    [string]$CoreVersion = 'v0.14.0',
    [string]$CoreRelease = 'v2026.5.16',
    [string]$WebUiVersion = '0.5.28',
    [int]$WebUiPort = 8648,
    [int]$ShadowPort = 8650,
    [string]$PythonExe = '',
    [string]$HermesExe = '',
    [string]$NodeExe = '',
    [string]$HermesHome = (Join-Path $HOME '.hermes')
)

$ErrorActionPreference = 'Stop'

function Resolve-OrCommand {
    param([string]$Configured, [string]$CommandName)
    if (-not [string]::IsNullOrWhiteSpace($Configured) -and (Test-Path -LiteralPath $Configured)) { return (Resolve-Path -LiteralPath $Configured).Path }
    $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    if (-not [string]::IsNullOrWhiteSpace($Configured)) { return $Configured }
    return $CommandName
}

function Write-TextNoBom {
    param([string]$Path, [string]$Content)
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

$workspace = if (Test-Path -LiteralPath $HermesWorkspaceRoot) { (Resolve-Path -LiteralPath $HermesWorkspaceRoot).Path } else { $HermesWorkspaceRoot }
New-Item -ItemType Directory -Force -Path $workspace | Out-Null
$workspace = (Resolve-Path -LiteralPath $workspace).Path
$coreRoot = (Resolve-Path -LiteralPath $CoreRoot).Path
$webRoot = (Resolve-Path -LiteralPath $WebUiReleaseRoot).Path
$python = Resolve-OrCommand -Configured $PythonExe -CommandName 'python'
$hermes = Resolve-OrCommand -Configured $HermesExe -CommandName 'hermes'
$node = Resolve-OrCommand -Configured $NodeExe -CommandName 'node'

$scriptsRoot = Join-Path $workspace 'scripts'
$manifestPath = Join-Path $workspace 'runtime\active-runtime.json'
$gatewayWrapper = Join-Path $HermesHome 'gateway-service\Hermes_Gateway.cmd'
$webStart = Join-Path $scriptsRoot 'start-hermes-web-ui.ps1'
$gatewayStart = Join-Path $scriptsRoot 'start-hermes-gateway.ps1'

$manifest = [ordered]@{
    schema_version = 1
    updated_at = (Get-Date).ToString('o')
    workspace_root = $workspace
    core = [ordered]@{ name = 'hermes-agent'; version = $CoreVersion; release = $CoreRelease; root = $coreRoot; python = $python; exe = $hermes; source_repo = 'https://github.com/NousResearch/hermes-agent.git'; install_mode = 'source-with-distribution-patches' }
    web_ui = [ordered]@{ package = 'hermes-web-ui'; version = $WebUiVersion; root = $webRoot; node = $node; cli = (Join-Path $webRoot 'bin\hermes-web-ui.mjs'); port = $WebUiPort; shadow_port = $ShadowPort; npm_dist_tag = 'latest' }
    paths = [ordered]@{ hermes_home = $HermesHome; gateway_wrapper = $gatewayWrapper; webui_start_script = $webStart; gateway_start_script = $gatewayStart; core_releases_root = (Join-Path $workspace 'runtime\core\releases'); web_ui_releases_root = (Join-Path $workspace 'runtime\web-ui\releases'); upgrade_lock = (Join-Path $workspace 'runtime\upgrade.lock') }
    policy = [ordered]@{ manifest_is_source_of_truth = $true; require_shadow_validation = $true; require_final_verify = $true; block_source_pythonpath = $true }
}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $manifestPath) | Out-Null
$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

$webStartContent = @'
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $repoRoot 'runtime\active-runtime.json') -Raw | ConvertFrom-Json
$webRoot = [string]$manifest.web_ui.root
$nodeExe = [string]$manifest.web_ui.node
$webCli = [string]$manifest.web_ui.cli
$port = [int]$manifest.web_ui.port
$env:HERMES_HOME = [string]$manifest.paths.hermes_home
$env:HERMES_BIN = [string]$manifest.core.exe
$env:NO_PROXY = '127.0.0.1,localhost,::1'
$env:no_proxy = $env:NO_PROXY
$env:HTTP_PROXY = ''
$env:HTTPS_PROXY = ''
$env:ALL_PROXY = ''
$env:http_proxy = ''
$env:https_proxy = ''
$env:all_proxy = ''
try {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop | Select-Object -First 1
    if ($conn) {
        $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$($conn.OwningProcess)"
        $command = [string]$proc.CommandLine
        if ($command.Contains($webRoot)) { Write-Host "hermes-web-ui already running on $port"; exit 0 }
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
} catch {}
Push-Location $webRoot
try { & $nodeExe $webCli start --port $port; exit $LASTEXITCODE } finally { Pop-Location }
'@
Write-TextNoBom -Path $webStart -Content $webStartContent

$gatewayStartContent = @'
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $repoRoot 'runtime\active-runtime.json') -Raw | ConvertFrom-Json
$gatewayCmd = [string]$manifest.paths.gateway_wrapper
$coreRoot = [string]$manifest.core.root
if (-not (Test-Path -LiteralPath $gatewayCmd)) { throw "gateway wrapper not found: $gatewayCmd" }
Start-Process -FilePath 'cmd.exe' -ArgumentList @('/d', '/c', "`"$gatewayCmd`"") -WindowStyle Hidden -WorkingDirectory $coreRoot
Write-Host 'gateway start process launched'
'@
Write-TextNoBom -Path $gatewayStart -Content $gatewayStartContent

$gatewayWrapperContent = @"
@echo off
rem Hermes Agent Gateway - WeChat distribution runtime
cd /d $coreRoot
set "HERMES_HOME=$HermesHome"
set "PYTHONIOENCODING=utf-8"
set "HERMES_GATEWAY_DETACHED=1"
set "HERMES_ACCEPT_HOOKS=1"
"$python" -m hermes_cli.main gateway run --replace --accept-hooks
"@.TrimStart()
Write-TextNoBom -Path $gatewayWrapper -Content $gatewayWrapperContent

[ordered]@{ ok = $true; manifest = $manifestPath; webui_start_script = $webStart; gateway_start_script = $gatewayStart; gateway_wrapper = $gatewayWrapper } | ConvertTo-Json -Depth 5
