#!/bin/bash
# Build Android APK using Docker with a persistent debug keystore.
# Every build uses the same signing key so APK updates install over the existing app.
#
# Usage: ./build-android.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
IMAGE="dailyplanner-android"
OUTPUT_DIR="${ROOT}/output"
OUTPUT_APK="${OUTPUT_DIR}/app-debug.apk"
KEYSTORE_DIR="${ROOT}/android-keystore"
GRADLE_CACHE="${ROOT}/.docker-gradle"

echo "=== Building Android APK via Docker ==="

echo "Step 1: Building base Docker image (cached after first run)..."
docker build -f "${ROOT}/Dockerfile.android" -t "${IMAGE}" "${ROOT}"

mkdir -p "${KEYSTORE_DIR}" "${OUTPUT_DIR}" "${GRADLE_CACHE}"

if [[ ! -f "${KEYSTORE_DIR}/debug.keystore" ]]; then
    echo "Step 2: Creating persistent debug keystore (one-time)..."
    docker run --rm \
        --entrypoint keytool \
        -v "${KEYSTORE_DIR}:/root/.android" \
        "${IMAGE}" \
        -genkeypair -v \
        -keystore /root/.android/debug.keystore \
        -storepass android \
        -alias androiddebugkey \
        -keypass android \
        -keyalg RSA \
        -keysize 2048 \
        -validity 10000 \
        -dname "CN=Android Debug,O=Android,C=US"
    echo "Keystore saved to: ${KEYSTORE_DIR}/debug.keystore"
    echo ""
    echo "NOTE: If the app is already installed with a different signature,"
    echo "      uninstall it once on your phone, then install the new APK."
    echo ""
else
    echo "Step 2: Using existing keystore at ${KEYSTORE_DIR}/debug.keystore"
fi

echo "Step 3: Building APK..."
docker run --rm \
    -v "${ROOT}:/app" \
    -v "${KEYSTORE_DIR}:/root/.android" \
    -v "${GRADLE_CACHE}:/root/.gradle" \
    -v "${OUTPUT_DIR}:/output" \
    "${IMAGE}"

if [[ ! -f "${OUTPUT_APK}" ]]; then
    echo "ERROR: APK not found at ${OUTPUT_APK}" >&2
    exit 1
fi

echo "=== Done! ==="
echo "APK saved to: ${OUTPUT_APK} ($(du -h "${OUTPUT_APK}" | cut -f1))"
echo "Signing key: ${KEYSTORE_DIR}/debug.keystore (keep this file to allow future updates)"
