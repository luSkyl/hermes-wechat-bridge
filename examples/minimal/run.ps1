$ErrorActionPreference = "Stop"
python -m bridge.cli doctor --config "$PSScriptRoot\config.yaml"
python -m bridge.cli simulate --config "$PSScriptRoot\config.yaml" --event "$PSScriptRoot\..\..\simulator\sample_events\text.json"
