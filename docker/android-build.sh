#!/bin/bash
# Run inside Docker: sync sources and build a debug APK with the mounted keystore.
set -euo pipefail

cd /app
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

if [[ ! -f /root/.android/debug.keystore ]]; then
    echo "ERROR: debug.keystore not found at /root/.android/debug.keystore" >&2
    echo "Run ./build-android.sh from the host to create the persistent keystore." >&2
    exit 1
fi

ANDROID_DIR="/app/build/dailyplanner/android"
if [[ ! -d "${ANDROID_DIR}" ]]; then
    echo "Creating Android Gradle project..."
    briefcase create android --no-input
fi

# Chaquopy / SDK compatibility patches
sed -i 's/matplotlib>=3\.7\.0/matplotlib==3.6.0/g' \
    /app/build/dailyplanner/android/gradle/app/requirements.txt 2>/dev/null || true

rm -rf /app/build/dailyplanner/android/gradle/app/src/main/res/values-v35

find /app/build -type f -name "*.gradle" | while read -r f; do
    sed -i -E \
        -e 's|google\(\)|maven { url "https://maven.aliyun.com/repository/google" }|g' \
        -e 's|mavenCentral\(\)|maven { url "https://maven.aliyun.com/repository/central" }|g' \
        -e 's|gradlePluginPortal\(\)|maven { url "https://maven.aliyun.com/repository/gradle-plugin" }|g' \
        -e 's|https://dl.google.com/dl/android/maven2|https://maven.aliyun.com/repository/google|g' \
        -e 's|https://maven.google.com|https://maven.aliyun.com/repository/google|g' \
        "$f"
done

echo "Syncing sources and resources..."
briefcase update android --no-input --update-resources

echo "Building debug APK..."
briefcase build android --no-input

APK="/app/build/dailyplanner/android/gradle/app/build/outputs/apk/debug/app-debug.apk"
if [[ ! -f "${APK}" ]]; then
    echo "ERROR: APK not found at ${APK}" >&2
    exit 1
fi

cp "${APK}" /output/app-debug.apk
echo "APK copied to /output/app-debug.apk"
