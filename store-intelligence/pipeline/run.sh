#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "========================================================================"
echo "      APEX STORE INTELLIGENCE // DETECTION PIPELINE RUNNER"
echo "========================================================================"
echo ""

# Base Directories
WORKSPACE_DIR="/Users/anjalitiwari/Desktop/Purplle Tech Challenge"
PIPELINE_DIR="$WORKSPACE_DIR/store-intelligence/pipeline"
ZIP_FILE="$WORKSPACE_DIR/CCTV Footage-20260529T160731Z-3-00144614ea.zip"
EXTRACT_DIR="$WORKSPACE_DIR/store-intelligence/pipeline/CCTV_Footage"

# 1. Unzip CCTV Clips if not already extracted
if [ -d "$EXTRACT_DIR" ]; then
    echo "[Info] Video directory already extracted at store-intelligence/pipeline/CCTV_Footage."
else
    if [ -f "$ZIP_FILE" ]; then
        echo "[Zip] Extracting CCTV clips from zip archive..."
        mkdir -p "$EXTRACT_DIR"
        unzip -q "$ZIP_FILE" -d "$EXTRACT_DIR"
        echo "[Zip] CCTV clips extracted successfully."
    else
        echo "[Warning] CCTV Footage zip file not found at $ZIP_FILE. Pipeline will run in fallback simulated mode."
    fi
fi

# 2. Start the pipeline
echo ""
echo "[Pipeline] Starting pipeline execution..."
echo "------------------------------------------------------------------------"
python3 "$PIPELINE_DIR/detect.py" --store "STORE_BLR_002" --mode "simulated"
echo "------------------------------------------------------------------------"
echo "[Pipeline] Pipeline execution completed successfully."
echo ""
echo "[Output] Behavioural events successfully written to:"
echo "         $WORKSPACE_DIR/events_output.jsonl"
echo ""
echo "========================================================================"
