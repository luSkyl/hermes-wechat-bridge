param(
    [Parameter(Mandatory = $true)]
    [string]$UpstreamRepo,
    [string]$Ref = 'v0.5.28',
    [Parameter(Mandatory = $true)]
    [string]$WorkRoot,
    [string]$OverlayRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [switch]$SkipFetch,
    [switch]$SkipInstall,
    [switch]$SkipTests,
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'

function Invoke-Step {
    param([string]$Name, [scriptblock]$Script)
    Write-Host "==> $Name"
    & $Script
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

$repo = (Resolve-Path -LiteralPath $UpstreamRepo).Path
$overlay = (Resolve-Path -LiteralPath $OverlayRoot).Path
New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null

$safeRef = ($Ref -replace '[^A-Za-z0-9._-]', '-')
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$worktree = Join-Path $WorkRoot "hermes-web-ui-$safeRef-$timestamp"

if (-not $SkipFetch) {
    Invoke-Step "fetch upstream refs" { git -C $repo fetch --tags origin }
}
Invoke-Step "create clean worktree $Ref" { git -C $repo worktree add --detach $worktree $Ref }

try {
    Invoke-Step 'apply local overlay' { & (Join-Path $overlay 'scripts\apply-overlay.ps1') -TargetRoot $worktree -OverlayRoot $overlay }

    if (-not $SkipInstall) {
        Invoke-Step 'install dependencies' { npm --prefix $worktree install --ignore-scripts }
    }

    if (-not $SkipTests) {
        Invoke-Step 'run focused overlay tests' {
            npm --prefix $worktree test -- tests/client/semantic-message.test.ts tests/shared/chat-protocol.test.ts tests/server/chat-run-message-flush.test.ts tests/client/friendly-notice.test.ts tests/server/friendly-error.test.ts
        }
    }

    if (-not $SkipBuild) {
        Invoke-Step 'build overlay runtime' { npm --prefix $worktree run build }
    }

    $result = [ordered]@{
        ok = $true
        ref = $Ref
        worktree = $worktree
        overlay = $overlay
        completed_at = (Get-Date).ToString('o')
    }
    $resultPath = Join-Path $overlay 'verification-latest.json'
    $result | ConvertTo-Json -Depth 5 | Set-Content -Path $resultPath -Encoding UTF8
    Write-Host "Overlay verification passed. Report: $resultPath"
}
catch {
    $result = [ordered]@{
        ok = $false
        ref = $Ref
        worktree = $worktree
        overlay = $overlay
        error = [string]$_
        failed_at = (Get-Date).ToString('o')
    }
    $resultPath = Join-Path $overlay 'verification-latest.json'
    $result | ConvertTo-Json -Depth 5 | Set-Content -Path $resultPath -Encoding UTF8
    throw
}
