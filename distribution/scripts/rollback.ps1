[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HermesWorkspaceRoot,

    [string]$BackupManifest = '',
    [string]$FallbackWebUiRelease = '0.5.28'
)

$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath $HermesWorkspaceRoot).Path
$manifestPath = Join-Path $workspace 'runtime\active-runtime.json'
if (-not (Test-Path -LiteralPath $manifestPath)) { throw "active runtime manifest not found: $manifestPath" }

if (-not [string]::IsNullOrWhiteSpace($BackupManifest)) {
    Copy-Item -LiteralPath $BackupManifest -Destination $manifestPath -Force
    Write-Host "Restored manifest from $BackupManifest"
} else {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $fallbackRoot = Join-Path $workspace "runtime\web-ui\releases\$FallbackWebUiRelease"
    if (-not (Test-Path -LiteralPath $fallbackRoot)) { throw "fallback Web UI release not found: $fallbackRoot" }
    $manifest.updated_at = (Get-Date).ToString('o')
    $manifest.web_ui.root = (Resolve-Path -LiteralPath $fallbackRoot).Path
    $manifest.web_ui.cli = Join-Path $manifest.web_ui.root 'bin\hermes-web-ui.mjs'
    $manifest.web_ui.version = $FallbackWebUiRelease
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    Write-Host "Switched Web UI fallback to $fallbackRoot"
}

& (Join-Path $PSScriptRoot 'stop.ps1') -Ports @(8648, 8650)
$startWeb = Join-Path $workspace 'scripts\start-hermes-web-ui.ps1'
if (Test-Path -LiteralPath $startWeb) { & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $startWeb }
Write-Host 'Rollback flow completed.'
