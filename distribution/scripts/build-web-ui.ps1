[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HermesWorkspaceRoot,

    [string]$UpstreamRepoUrl = 'https://github.com/EKKOLearnAI/hermes-web-ui.git',
    [string]$UpstreamRef = 'v0.5.28',
    [string]$WorkRoot = '',
    [string]$RuntimeReleasesRoot = '',
    [string]$ReleaseName = '0.5.28-local.1',
    [switch]$SkipInstall,
    [switch]$SkipTests,
    [switch]$SkipBuild,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Resolve-RequiredPath {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path -LiteralPath $Path)) { throw "$Description not found: $Path" }
    return (Resolve-Path -LiteralPath $Path).Path
}

$workspace = Resolve-RequiredPath -Path $HermesWorkspaceRoot -Description 'Hermes workspace root'
if ([string]::IsNullOrWhiteSpace($WorkRoot)) { $WorkRoot = Join-Path $workspace 'local-state\distribution-web-ui' }
if ([string]::IsNullOrWhiteSpace($RuntimeReleasesRoot)) { $RuntimeReleasesRoot = Join-Path $workspace 'runtime\web-ui\releases' }
New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null
New-Item -ItemType Directory -Force -Path $RuntimeReleasesRoot | Out-Null

$overlay = Resolve-RequiredPath -Path (Join-Path $PSScriptRoot '..\overlays\hermes-web-ui') -Description 'Hermes Web UI overlay'
$upstream = Join-Path $WorkRoot 'hermes-web-ui-upstream'
if (-not (Test-Path -LiteralPath $upstream)) {
    Write-Host "==> Cloning Hermes Web UI upstream into $upstream"
    & git clone $UpstreamRepoUrl $upstream
    if ($LASTEXITCODE -ne 0) { throw 'git clone failed for Hermes Web UI upstream' }
}

$verifyArgs = @(
    '-UpstreamRepo', $upstream,
    '-Ref', $UpstreamRef,
    '-WorkRoot', (Join-Path $WorkRoot 'overlay-verify'),
    '-OverlayRoot', $overlay
)
if ($SkipInstall) { $verifyArgs += '-SkipInstall' }
if ($SkipTests) { $verifyArgs += '-SkipTests' }
if ($SkipBuild) { $verifyArgs += '-SkipBuild' }
& (Join-Path $overlay 'scripts\verify-overlay.ps1') @verifyArgs
if ($LASTEXITCODE -ne 0) { throw 'Web UI overlay verification failed' }

if (-not $SkipBuild) {
    $buildArgs = @(
        '-OverlayRoot', $overlay,
        '-RuntimeReleasesRoot', $RuntimeReleasesRoot,
        '-ReleaseName', $ReleaseName
    )
    if ($Force) { $buildArgs += '-Force' }
    & (Join-Path $overlay 'scripts\build-local-release.ps1') @buildArgs
    if ($LASTEXITCODE -ne 0) { throw 'Web UI local release build failed' }
}

Write-Host 'Web UI overlay build flow completed.'
