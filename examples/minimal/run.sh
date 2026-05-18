#!/usr/bin/env sh
set -eu
python -m bridge.cli doctor --config "$(dirname "$0")/config.yaml"
python -m bridge.cli simulate --config "$(dirname "$0")/config.yaml" --event "$(dirname "$0")/../../simulator/sample_events/text.json"
