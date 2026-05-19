[CmdletBinding()]
param(
    [int[]]$Ports = @(8648, 8650, 8787)
)

$ErrorActionPreference = 'Continue'
foreach ($port in $Ports) {
    $connections = @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
    foreach ($conn in $connections) {
        try {
            $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$($conn.OwningProcess)"
            Write-Host "Stopping port $port pid=$($conn.OwningProcess) command=$($proc.CommandLine)"
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        } catch {}
    }
}
