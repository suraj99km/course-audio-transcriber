#!/bin/bash

# ============================================
# Course Audio Transcriber Launcher
# ============================================

SPEAKER_OUTPUT="Multi-Output Device"
EARPHONE_OUTPUT="Multi-Output Device 2"

CONDA_ENV="transcribe"

echo
echo "======================================"
echo "      Course Transcriber"
echo "======================================"
echo

# --------------------------------------------
# Check SwitchAudioSource
# --------------------------------------------

if ! command -v SwitchAudioSource >/dev/null 2>&1; then
    echo "❌ SwitchAudioSource is not installed."
    echo
    echo "Install it with:"
    echo "brew install switchaudio-osx"
    exit 1
fi

# --------------------------------------------
# Get available OUTPUT devices
# --------------------------------------------

OUTPUT_DEVICES=$(SwitchAudioSource -a -t output)

echo "Available output devices:"
echo "$OUTPUT_DEVICES"
echo

# --------------------------------------------
# Check BlackHole
# --------------------------------------------

if ! echo "$OUTPUT_DEVICES" | grep -qi "BlackHole 2ch"; then
    echo "❌ BlackHole 2ch was not found."
    echo
    echo "Make sure BlackHole is installed."
    exit 1
fi

echo "✅ BlackHole 2ch detected."

# --------------------------------------------
# Detect Pixel Buds
# --------------------------------------------
# We intentionally search for "Pixel Buds"
# instead of requiring an exact device name.
#
# This avoids problems if macOS changes the
# Bluetooth device name slightly.
# --------------------------------------------

if echo "$OUTPUT_DEVICES" | grep -qi "Pixel Buds"; then

    echo "🎧 Pixel Buds detected."
    echo "🔊 Selecting: $EARPHONE_OUTPUT"

    if ! echo "$OUTPUT_DEVICES" | grep -Fxq "$EARPHONE_OUTPUT"; then
        echo
        echo "❌ '$EARPHONE_OUTPUT' was not found."
        echo
        echo "Available devices:"
        echo "$OUTPUT_DEVICES"
        exit 1
    fi

    SwitchAudioSource -t output -s "$EARPHONE_OUTPUT"

    if [ $? -ne 0 ]; then
        echo "❌ Failed to select $EARPHONE_OUTPUT"
        exit 1
    fi

    echo "✅ Pixel Buds + BlackHole selected."

else

    echo "🔊 Pixel Buds not detected."
    echo "🔊 Selecting: $SPEAKER_OUTPUT"

    if ! echo "$OUTPUT_DEVICES" | grep -Fxq "$SPEAKER_OUTPUT"; then
        echo
        echo "❌ '$SPEAKER_OUTPUT' was not found."
        echo
        echo "Available devices:"
        echo "$OUTPUT_DEVICES"
        exit 1
    fi

    SwitchAudioSource -t output -s "$SPEAKER_OUTPUT"

    if [ $? -ne 0 ]; then
        echo "❌ Failed to select $SPEAKER_OUTPUT"
        exit 1
    fi

    echo "✅ MacBook Speakers + BlackHole selected."

fi

echo
echo "🎙 Starting transcription..."
echo

# --------------------------------------------
# Activate Conda environment
# --------------------------------------------

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

# --------------------------------------------
# Start transcription
# --------------------------------------------

python transcribe.py

# --------------------------------------------
# Restore normal MacBook speakers
# --------------------------------------------

echo
echo "======================================"
echo "Transcription stopped."
echo "Restoring normal audio..."
echo "======================================"

SwitchAudioSource -t output -s "MacBook Air Speakers"

echo "✅ MacBook Air Speakers restored."
echo