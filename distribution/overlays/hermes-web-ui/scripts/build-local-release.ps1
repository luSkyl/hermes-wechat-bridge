param(
    [string]$OverlayRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [Parameter(Mandatory = $true)]
    [string]$RuntimeReleasesRoot,
    [string]$Worktree = '',
    [string]$ReleaseName = '',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Resolve-RequiredPath {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Description not found: $Path"
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

function Copy-DirectoryRobust {
    param([string]$Source, [string]$Destination)
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    & robocopy $Source $Destination /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "robocopy failed from $Source to $Destination with exit code $LASTEXITCODE"
    }
    $global:LASTEXITCODE = 0
}

$overlay = Resolve-RequiredPath -Path $OverlayRoot -Description 'Overlay root'
$releasesRoot = Resolve-RequiredPath -Path $RuntimeReleasesRoot -Description 'Runtime releases root'

if ([string]::IsNullOrWhiteSpace($Worktree)) {
    $reportPath = Join-Path $overlay 'verification-latest.json'
    $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    if (-not $report.ok) {
        throw "Latest overlay verification did not pass: $reportPath"
    }
    $Worktree = [string]$report.worktree
}

$source = Resolve-RequiredPath -Path $Worktree -Description 'Verified worktree'
foreach ($required in @('package.json', 'package-lock.json', 'bin', 'dist', 'node_modules')) {
    Resolve-RequiredPath -Path (Join-Path $source $required) -Description "Verified worktree item $required" | Out-Null
}

$package = Get-Content -LiteralPath (Join-Path $source 'package.json') -Raw | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace($ReleaseName)) {
    $baseName = "$($package.version)-local"
    $index = 1
    do {
        $ReleaseName = "$baseName.$index"
        $candidate = Join-Path $releasesRoot $ReleaseName
        $index++
    } while (Test-Path -LiteralPath $candidate)
}

$destination = Join-Path $releasesRoot $ReleaseName
if ((Test-Path -LiteralPath $destination) -and -not $Force) {
    throw "Release destination already exists: $destination. Use -Force to replace."
}

if (Test-Path -LiteralPath $destination) {
    Remove-Item -LiteralPath $destination -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $destination | Out-Null

foreach ($file in @('package.json', 'package-lock.json', 'README.md', 'LICENSE')) {
    $sourceFile = Join-Path $source $file
    if (Test-Path -LiteralPath $sourceFile) {
        Copy-Item -LiteralPath $sourceFile -Destination (Join-Path $destination $file) -Force
    }
}

foreach ($directory in @('bin', 'dist', 'node_modules')) {
    Copy-DirectoryRobust -Source (Join-Path $source $directory) -Destination (Join-Path $destination $directory)
}

$metadata = [ordered]@{
    release_name = $ReleaseName
    source_worktree = $source
    overlay = $overlay
    upstream_version = $package.version
    created_at = (Get-Date).ToString('o')
    activation_note = 'Update runtime/active-runtime.json only after shadow-port smoke validation.'
}
$metadata | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $destination 'overlay-release.json') -Encoding UTF8

Write-Host "Local overlay runtime built: $destination"
Write-Host 'Run a shadow validation before switching active-runtime.json.'
