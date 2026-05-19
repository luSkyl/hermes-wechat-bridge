param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRoot,

    [string]$OverlayRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,

    [switch]$AllowDirty
)

$ErrorActionPreference = 'Stop'

function Resolve-RequiredPath {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Description not found: $Path"
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

$target = Resolve-RequiredPath -Path $TargetRoot -Description 'Target root'
$overlay = Resolve-RequiredPath -Path $OverlayRoot -Description 'Overlay root'
$patch = Resolve-RequiredPath -Path (Join-Path $overlay 'patches\0001-local-enhancements.patch') -Description 'Overlay patch'
$filesRoot = Join-Path $overlay 'files'
$untrackedManifest = Join-Path $overlay 'untracked-files.txt'

if (-not $AllowDirty) {
    $status = & git -C $target status --porcelain 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Target must be a Git checkout so the overlay can apply with three-way safety: $target"
    }
    if ($status) {
        throw "Target checkout is not clean. Re-run with -AllowDirty only for disposable verification worktrees."
    }
}

Write-Host "Applying overlay patch to $target"
& git -C $target apply --3way --whitespace=nowarn $patch
if ($LASTEXITCODE -ne 0) {
    throw "Overlay patch failed to apply cleanly. Resolve conflicts in a disposable worktree before promotion."
}

if (Test-Path -LiteralPath $untrackedManifest) {
    Get-Content -LiteralPath $untrackedManifest | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object {
        $relative = $_
        $source = Join-Path $filesRoot ($relative -replace '/', '\')
        $destination = Join-Path $target ($relative -replace '/', '\')
        if (-not (Test-Path -LiteralPath $source)) {
            throw "Overlay file listed but missing: $relative"
        }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
        Copy-Item -LiteralPath $source -Destination $destination -Force
        Write-Host "Copied overlay file $relative"
    }
}

$stampDir = Join-Path $target '.overlay-applied'
New-Item -ItemType Directory -Force -Path $stampDir | Out-Null
$stamp = [ordered]@{
    overlay = $overlay
    applied_at = (Get-Date).ToString('o')
    patch = $patch
}
$stamp | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $stampDir 'hermes-web-ui.json') -Encoding UTF8

Write-Host 'Overlay applied successfully.'
