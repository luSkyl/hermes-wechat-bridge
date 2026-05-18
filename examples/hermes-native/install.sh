#!/usr/bin/env sh
set -eu
HERMES_HOME="${HERMES_HOME:-$(dirname "$0")/.demo-hermes-home}"
TARGET="${WECHAT_TARGET:-wxid_home}"
CONFIG="$(dirname "$0")/config.yaml"

python -m bridge.cli install-hermes-native --hermes-home "$HERMES_HOME" --config "$CONFIG" --target "$TARGET" --force
python -m bridge.cli verify-hermes-native --hermes-home "$HERMES_HOME"
python -m bridge.cli notify --config "$CONFIG" --target "$TARGET" --title "集成测试" --text "Hermes Native Integration Kit 已安装。" --priority high
python -m bridge.cli flush --config "$CONFIG" --target "$TARGET" --limit 3
