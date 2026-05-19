[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CoreRoot,

    [string]$PatchRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\patches\hermes-core')).Path,
    [switch]$CheckOnly,
    [switch]$AllowDirty
)

$ErrorActionPreference = 'Stop'

function Resolve-RequiredPath {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path -LiteralPath $Path)) { throw "$Description not found: $Path" }
    return (Resolve-Path -LiteralPath $Path).Path
}

$core = Resolve-RequiredPath -Path $CoreRoot -Description 'Hermes core root'
$patches = Resolve-RequiredPath -Path $PatchRoot -Description 'Core patch root'
$patchFiles = @(Get-ChildItem -LiteralPath $patches -Filter '*.patch' -File | Sort-Object Name)
if ($patchFiles.Count -eq 0) { throw "No core patch files found in $patches" }

& git -C $core rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) { throw "Core root must be a Git checkout: $core" }

$status = & git -C $core status --porcelain
if ($status -and -not $AllowDirty) {
    throw "Core checkout is not clean. Use -AllowDirty only for disposable integration worktrees."
}

if ($CheckOnly) {
    $tempCore = Join-Path ([System.IO.Path]::GetTempPath()) ("hermes-core-patch-check-" + [guid]::NewGuid().ToString('N'))
    try {
        Write-Host "==> Creating temporary patch-check worktree"
        & git -C $core worktree add --detach $tempCore HEAD | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "Could not create temporary core worktree: $tempCore" }
        & $PSCommandPath -CoreRoot $tempCore -PatchRoot $patches -AllowDirty
        if ($LASTEXITCODE -ne 0) { throw "Core patch check failed in temporary worktree: $tempCore" }
    } finally {
        & git -C $core worktree remove --force $tempCore *> $null
        if (Test-Path -LiteralPath $tempCore) { Remove-Item -LiteralPath $tempCore -Recurse -Force }
    }
    Write-Host "Core patch gate passed. check_only=True"
    return
}

foreach ($patch in $patchFiles) {
    Write-Host "==> Checking $($patch.Name)"
    & git -C $core apply --check --whitespace=nowarn $patch.FullName
    $canApply = ($LASTEXITCODE -eq 0)
    if (-not $canApply) {
        & git -C $core apply --reverse --check --whitespace=nowarn $patch.FullName *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "==> Already applied $($patch.Name)"
            continue
        }
        throw "Core patch check failed: $($patch.FullName)"
    }
    if (-not $CheckOnly) {
        Write-Host "==> Applying $($patch.Name)"
        & git -C $core apply --whitespace=nowarn $patch.FullName
        if ($LASTEXITCODE -ne 0) { throw "Core patch apply failed: $($patch.FullName)" }
    }
}

Write-Host "Core patch gate passed. check_only=$CheckOnly"
