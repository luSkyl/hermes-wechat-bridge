[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HermesWorkspaceRoot,

    [string]$CoreRepoUrl = 'https://github.com/NousResearch/hermes-agent.git',
    [string]$CoreRef = 'v2026.5.16',
    [string]$WorkRoot = '',
    [switch]$SkipCore,
    [switch]$SkipWebUi,
    [switch]$SkipBridge,
    [switch]$SkipStart,
    [switch]$SkipVerify,
    [switch]$ForceWebUiRelease
)

$ErrorActionPreference = 'Stop'

$workspace = if (Test-Path -LiteralPath $HermesWorkspaceRoot) { (Resolve-Path -LiteralPath $HermesWorkspaceRoot).Path } else { $HermesWorkspaceRoot }
New-Item -ItemType Directory -Force -Path $workspace | Out-Null
$workspace = (Resolve-Path -LiteralPath $workspace).Path
if ([string]::IsNullOrWhiteSpace($WorkRoot)) { $WorkRoot = Join-Path $workspace 'local-state\distribution-install' }
New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null

$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\manifest.lock.json') -Raw | ConvertFrom-Json
$coreRoot = Join-Path $workspace "runtime\core\releases\$($manifest.core.release)"
$webReleaseRoot = Join-Path $workspace "runtime\web-ui\releases\$($manifest.web_ui.local_release)"

if (-not $SkipCore) {
    if (-not (Test-Path -LiteralPath $coreRoot)) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $coreRoot) | Out-Null
        Write-Host "==> Cloning Hermes core $CoreRef to $coreRoot"
        & git clone --branch $CoreRef --depth 1 $CoreRepoUrl $coreRoot
        if ($LASTEXITCODE -ne 0) { throw 'Hermes core clone failed' }
    }
    & (Join-Path $PSScriptRoot 'apply-core-patches.ps1') -CoreRoot $coreRoot -AllowDirty
    if ($LASTEXITCODE -ne 0) { throw 'Core patch flow failed' }
    Write-Host "==> Installing patched Hermes core from $coreRoot"
    & python -m pip install -e $coreRoot
    if ($LASTEXITCODE -ne 0) { throw 'Patched Hermes core install failed' }
}

if (-not $SkipWebUi) {
    $webArgs = @('-HermesWorkspaceRoot', $workspace, '-ReleaseName', $manifest.web_ui.local_release)
    if ($ForceWebUiRelease) { $webArgs += '-Force' }
    & (Join-Path $PSScriptRoot 'build-web-ui.ps1') @webArgs
    if ($LASTEXITCODE -ne 0) { throw 'Web UI build flow failed' }
}

if (-not $SkipBridge) {
    & (Join-Path $PSScriptRoot 'install-bridge.ps1') -Dev -SkipDoctor
    if ($LASTEXITCODE -ne 0) { throw 'Bridge install flow failed' }
}

if ((Test-Path -LiteralPath $coreRoot) -and (Test-Path -LiteralPath $webReleaseRoot)) {
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
    $hermes = (Get-Command hermes -ErrorAction SilentlyContinue).Source
    $node = (Get-Command node -ErrorAction SilentlyContinue).Source
    & (Join-Path $PSScriptRoot 'initialize-runtime.ps1') `
        -HermesWorkspaceRoot $workspace `
        -CoreRoot $coreRoot `
        -WebUiReleaseRoot $webReleaseRoot `
        -CoreVersion $manifest.core.version `
        -CoreRelease $manifest.core.release `
        -WebUiVersion $manifest.web_ui.upstream_version `
        -WebUiPort $manifest.runtime.default_web_ui_port `
        -ShadowPort $manifest.runtime.default_shadow_port `
        -PythonExe $python `
        -HermesExe $hermes `
        -NodeExe $node
    if ($LASTEXITCODE -ne 0) { throw 'Runtime initialization failed' }
} else {
    Write-Warning 'Skipping runtime initialization because core or Web UI release is missing.'
}

if (-not $SkipStart) {
    & (Join-Path $PSScriptRoot 'start.ps1') -HermesWorkspaceRoot $workspace
}

if (-not $SkipVerify) {
    & (Join-Path $PSScriptRoot 'verify.ps1') -HermesWorkspaceRoot $workspace -SkipBridgeHttp
    if ($LASTEXITCODE -ne 0) { throw 'Distribution verification failed' }
}

Write-Host 'Hermes WeChat distribution install flow completed.'
