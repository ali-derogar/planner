#!/bin/bash
# Build Android APK using Docker (bypasses dl.google.com network issues)
# Usage: ./build-android.sh
set -euo pipefail

APK_PATH="/app/build/dailyplanner/android/gradle/app/build/outputs/apk/debug/app-debug.apk"
OUTPUT_DIR="$(pwd)/output"
OUTPUT_APK="${OUTPUT_DIR}/app-debug.apk"

echo "=== Building Android APK via Docker ==="

echo "Step 1: Building Docker image (this may take several minutes)..."
docker build -f Dockerfile.android -t dailyplanner-android .

echo "Step 2: Extracting APK..."
mkdir -p "${OUTPUT_DIR}"
docker run --rm \
  -v "${OUTPUT_DIR}:/output" \
  dailyplanner-android \
  sh -c "test -f '${APK_PATH}' && cp '${APK_PATH}' /output/app-debug.apk"

if [[ ! -f "${OUTPUT_APK}" ]]; then
  echo "ERROR: APK not found at ${OUTPUT_APK}" >&2
  exit 1
fi

echo "=== Done! ==="
echo "APK saved to: ${OUTPUT_APK} ($(du -h "${OUTPUT_APK}" | cut -f1))"
