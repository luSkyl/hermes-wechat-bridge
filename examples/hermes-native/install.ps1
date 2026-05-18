#!/usr/bin/env pwsh
param(
  [string]$HermesHome = "$PSScriptRoot\.demo-hermes-home",
  [string]$Target = "wxid_home"
)

$Config = Join-Path $PSScriptRoot "config.yaml"
python -m bridge.cli install-hermes-native --hermes-home $HermesHome --config $Config --target $Target --force
python -m bridge.cli verify-hermes-native --hermes-home $HermesHome
python -m bridge.cli notify --config $Config --target $Target --title "集成测试" --text "Hermes Native Integration Kit 已安装。" --priority high
python -m bridge.cli flush --config $Config --target $Target --limit 3
