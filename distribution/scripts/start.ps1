[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HermesWorkspaceRoot,

    [string]$BridgeConfig = '',
    [string]$PythonExe = 'python',
    [int]$BridgePort = 8787,
    [switch]$NoNewWindow
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
if ([string]::IsNullOrWhiteSpace($BridgeConfig)) { $BridgeConfig = Join-Path $repo 'distribution\config.example.yaml' }

$webScript = Join-Path $HermesWorkspaceRoot 'scripts\start-hermes-web-ui.ps1'
$gatewayScript = Join-Path $HermesWorkspaceRoot 'scripts\start-hermes-gateway.ps1'
foreach ($script in @($gatewayScript, $webScript)) {
    if (Test-Path -LiteralPath $script) {
        Write-Host "==> Starting via $script"
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script
    }
}

Write-Host "==> Starting bridge service on 127.0.0.1:$BridgePort"
$args = @('-m', 'bridge.cli', 'serve', '--config', $BridgeConfig, '--host', '127.0.0.1', '--port', [string]$BridgePort)
if ($NoNewWindow) {
    Start-Process -FilePath $PythonExe -ArgumentList $args -NoNewWindow
} else {
    Start-Process -FilePath $PythonExe -ArgumentList $args
}
