[CmdletBinding()]
param(
    [string]$BridgeRepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$PythonExe = 'python',
    [string]$Extras = 'yaml',
    [switch]$Dev,
    [switch]$SkipDoctor,
    [string]$ConfigPath = ''
)

$ErrorActionPreference = 'Stop'

$repo = (Resolve-Path -LiteralPath $BridgeRepoRoot).Path
$specifier = if ($Dev) { '.[dev,yaml]' } elseif ([string]::IsNullOrWhiteSpace($Extras)) { '.' } else { ".[${Extras}]" }
Write-Host "==> Installing bridge from $repo with extras $specifier"
Push-Location $repo
try {
    & $PythonExe -m pip install -e $specifier
    if ($LASTEXITCODE -ne 0) { throw 'Bridge install failed' }
}
finally {
    Pop-Location
}

if (-not $SkipDoctor) {
    if ([string]::IsNullOrWhiteSpace($ConfigPath)) { $ConfigPath = Join-Path $repo 'distribution\config.example.yaml' }
    Write-Host "==> Running bridge doctor against $ConfigPath"
    & $PythonExe -m bridge.cli doctor --config $ConfigPath
    if ($LASTEXITCODE -ne 0) { throw 'Bridge doctor failed' }
}

Write-Host 'Bridge install flow completed.'
