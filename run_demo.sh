#!/usr/bin/env bash
set -euo pipefail


# Path to your UnrealEditor binary 
UE_BIN="/Users/Shared/Epic Games/UE_5.6/Engine/Binaries/Mac/UnrealEditor"

# Path to .uproject file
UPROJECT="/Users/alexandervalverde/Documents/Unreal Projects/OneZero/OneZero.uproject"

# Directory containing parser.py, BuildScene.py, requirements.txt
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

# Generate the JSON based on a prompt and a model
PROMPT=${1:-"Give me a cosy loft with a skylight and put a rocket-shaped lamp on the bedside table."}
MODEL=${2:-"gpt-4.1"}

# Write the parser’s JSON
OUTPUT_JSON="$SCRIPTS_DIR/scene.json"

# Install libraries
pip install -r "$SCRIPTS_DIR/requirements.txt"

# Obtain the Json
python3 "$SCRIPTS_DIR/parser.py" \
  "$PROMPT" \
  --model "$MODEL" \
  --output "$OUTPUT_JSON"

echo "scene.json written at $OUTPUT_JSON"

if [[ ! -f "$UPROJECT" ]]; then
    echo "ERROR: .uproject not found at: $UPROJECT"
    exit 1
fi

# Run Unreal Engine with the BuildScene script

"$UE_BIN" "$UPROJECT" \
    -run=pythonscript \
    -script="$SCRIPTS_DIR/BuildScene.py" \
    -unattended \
    -nullrhi \
    "$OUTPUT_JSON" \
    | tee "$SCRIPTS_DIR/build.log"

# Verify output
PROJECT_DIR="$(dirname "$UPROJECT")"
MAP_FILE="$PROJECT_DIR/Content/Maps/BlockOut.umap"

if [[ -f "$MAP_FILE" ]]; then
    echo "Success! BlockOut.umap saved at:"
    echo "    $MAP_FILE"
    exit 0
else
    echo "Build failed. Check build.log for details:"
    echo "    $SCRIPTS_DIR/build.log"
    exit 1
fi
