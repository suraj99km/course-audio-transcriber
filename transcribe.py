import os
import queue
import threading
import wave
import time
from datetime import datetime

import numpy as np
import sounddevice as sd
import whisper


# ============================================================
# CONFIGURATION
# ============================================================

# BlackHole 2ch
def find_blackhole():
    devices = sd.query_devices()

    for i, device in enumerate(devices):
        if (
            "BlackHole 2ch" in device["name"]
            and device["max_input_channels"] >= 2
        ):
            return i

    raise RuntimeError(
        "BlackHole 2ch was not found. "
        "Make sure BlackHole is installed and available."
    )


DEVICE = find_blackhole()

# BlackHole provides 2 input channels
CHANNELS = 2

# Whisper expects 16 kHz audio
SAMPLE_RATE = 16000

# Amount of audio sent to Whisper at a time
CHUNK_SECONDS = 20

# Overlap helps prevent words being cut between chunks
OVERLAP_SECONDS = 1

# Whisper model
MODEL_NAME = "small"

# Output directory
OUTPUT_ROOT = "CourseTranscripts"


# ============================================================
# CREATE OUTPUT FILES
# ============================================================

start_time = datetime.now()

date_folder = start_time.strftime("%Y-%m-%d")
file_timestamp = start_time.strftime("%Y-%m-%d_%H-%M-%S")

output_dir = os.path.join(
    OUTPUT_ROOT,
    date_folder
)

os.makedirs(output_dir, exist_ok=True)

transcript_file = os.path.join(
    output_dir,
    f"lecture_{file_timestamp}.txt"
)

audio_file = os.path.join(
    output_dir,
    f"lecture_{file_timestamp}.wav"
)


# ============================================================
# QUEUES
# ============================================================

# Everything captured by BlackHole goes into these queues.
recording_queue = queue.Queue()
transcription_queue = queue.Queue()

stop_event = threading.Event()


# ============================================================
# AUDIO CALLBACK
# ============================================================

def audio_callback(indata, frames, time_info, status):

    if status:
        print(f"\nAudio status: {status}")

    # Make a copy because sounddevice reuses its buffer.
    audio = indata.copy()

    # Send audio independently to both workers.
    recording_queue.put(audio)
    transcription_queue.put(audio)


# ============================================================
# CONTINUOUS AUDIO RECORDER
# ============================================================

def audio_recorder():

    print("Audio recorder started.")

    with wave.open(audio_file, "wb") as wav:

        wav.setnchannels(CHANNELS)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        while True:

            audio = recording_queue.get()

            # Stop signal
            if audio is None:
                break

            # Convert float32 → int16
            audio_int16 = np.int16(
                np.clip(audio, -1.0, 1.0) * 32767
            )

            wav.writeframes(
                audio_int16.tobytes()
            )

            # IMPORTANT:
            # Do NOT call wav.flush().
            # wave.Wave_write has no flush() method.

    print("Audio recorder stopped.")


# ============================================================
# TRANSCRIPTION WORKER
# ============================================================

def transcription_worker():

    print()
    print(f"Loading Whisper '{MODEL_NAME}' model...")

    model = whisper.load_model(MODEL_NAME)

    print("Whisper model loaded.")
    print("Transcription worker started.")
    print()

    chunk_samples = int(
        CHUNK_SECONDS * SAMPLE_RATE
    )

    overlap_samples = int(
        OVERLAP_SECONDS * SAMPLE_RATE
    )

    buffer = np.empty(
        (0, CHANNELS),
        dtype=np.float32
    )

    processed_seconds = 0

    while True:

        audio = transcription_queue.get()

        # Stop signal
        if audio is None:
            break

        # Add incoming audio to buffer
        buffer = np.concatenate(
            (buffer, audio),
            axis=0
        )

        # Process all complete chunks currently available
        while len(buffer) >= chunk_samples:

            chunk = buffer[:chunk_samples]

            # Keep overlap for next chunk
            buffer = buffer[
                chunk_samples - overlap_samples:
            ]

            # Stereo → mono
            mono_audio = np.mean(
                chunk,
                axis=1
            )

            chunk_start = processed_seconds
            chunk_end = (
                chunk_start + CHUNK_SECONDS
            )

            print(
                f"Transcribing "
                f"{format_time(chunk_start)} → "
                f"{format_time(chunk_end)} ..."
            )

            try:

                result = model.transcribe(
                    mono_audio,
                    language="en",
                    fp16=False,
                    temperature=0,
                    condition_on_previous_text=True
                )

                text = result["text"].strip()

                if text:

                    timestamp = datetime.now().strftime(
                        "%H:%M:%S"
                    )

                    line = (
                        f"[{timestamp}] {text}\n"
                    )

                    print()
                    print(line)

                    # Save immediately
                    with open(
                        transcript_file,
                        "a",
                        encoding="utf-8"
                    ) as f:

                        f.write(line)
                        f.flush()

            except Exception as e:

                print(
                    f"\nWhisper error: {e}"
                )

            processed_seconds += (
                CHUNK_SECONDS - OVERLAP_SECONDS
            )

    print("Transcription worker stopped.")


# ============================================================
# FORMAT TIME
# ============================================================

def format_time(seconds):

    hours = int(seconds // 3600)

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = int(seconds % 60)

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


# ============================================================
# WRITE TRANSCRIPT HEADER
# ============================================================

with open(
    transcript_file,
    "w",
    encoding="utf-8"
) as f:

    f.write("COURSE TRANSCRIPT\n")
    f.write("=================\n\n")

    f.write(
        "Started: "
        f"{start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    f.write(
        f"Whisper model: {MODEL_NAME}\n"
    )

    f.write(
        f"Chunk size: {CHUNK_SECONDS} seconds\n"
    )

    f.write(
        f"Overlap: {OVERLAP_SECONDS} seconds\n"
    )

    f.write("\n")
    f.write(
        "----------------------------------------\n\n"
    )


# ============================================================
# START
# ============================================================

print()
print("==========================================")
print("       COURSE AUDIO TRANSCRIBER")
print("==========================================")
print()

print(f"Transcript:")
print(f"  {transcript_file}")
print()

print(f"Audio backup:")
print(f"  {audio_file}")
print()

print(f"Whisper model : {MODEL_NAME}")
print(f"Chunk size    : {CHUNK_SECONDS}s")
print(f"Overlap       : {OVERLAP_SECONDS}s")
print()

print("Loading Whisper before recording...")
print()


# ============================================================
# START WHISPER FIRST
# ============================================================

# We load Whisper before asking you to start the lecture.
# This prevents model-loading time from becoming a gap.

print(f"Loading Whisper '{MODEL_NAME}' model...")

model = whisper.load_model(MODEL_NAME)

print("Whisper model loaded.")
print()


# ============================================================
# TRANSCRIPTION WORKER
# ============================================================

def transcription_worker_with_model():

    chunk_samples = int(
        CHUNK_SECONDS * SAMPLE_RATE
    )

    overlap_samples = int(
        OVERLAP_SECONDS * SAMPLE_RATE
    )

    buffer = np.empty(
        (0, CHANNELS),
        dtype=np.float32
    )

    processed_seconds = 0

    print("Transcription worker started.")

    while True:

        audio = transcription_queue.get()

        if audio is None:
            break

        buffer = np.concatenate(
            (buffer, audio),
            axis=0
        )

        while len(buffer) >= chunk_samples:

            chunk = buffer[:chunk_samples]

            buffer = buffer[
                chunk_samples - overlap_samples:
            ]

            mono_audio = np.mean(
                chunk,
                axis=1
            )

            chunk_start = processed_seconds
            chunk_end = (
                chunk_start + CHUNK_SECONDS
            )

            print(
                f"Transcribing "
                f"{format_time(chunk_start)} → "
                f"{format_time(chunk_end)} ..."
            )

            try:

                result = model.transcribe(
                    mono_audio,
                    language="en",
                    fp16=False,
                    temperature=0,
                    condition_on_previous_text=True
                )

                text = result["text"].strip()

                if text:

                    timestamp = datetime.now().strftime(
                        "%H:%M:%S"
                    )

                    line = (
                        f"[{timestamp}] {text}\n"
                    )

                    print()
                    print(line)

                    with open(
                        transcript_file,
                        "a",
                        encoding="utf-8"
                    ) as f:

                        f.write(line)
                        f.flush()

            except Exception as e:

                print(
                    f"\nWhisper error: {e}"
                )

            processed_seconds += (
                CHUNK_SECONDS - OVERLAP_SECONDS
            )

    print("Transcription worker stopped.")


# ============================================================
# CREATE THREADS
# ============================================================

recorder_thread = threading.Thread(
    target=audio_recorder,
    name="AudioRecorder"
)

transcriber_thread = threading.Thread(
    target=transcription_worker_with_model,
    name="WhisperTranscriber"
)


# ============================================================
# START AUDIO STREAM
# ============================================================

stream = sd.InputStream(
    device=DEVICE,
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="float32",
    callback=audio_callback,
    blocksize=1024
)

stream.start()

recorder_thread.start()
transcriber_thread.start()


print()
print("==========================================")
print(" AUDIO CAPTURE IS NOW CONTINUOUS")
print("==========================================")
print()
print("Start your course video now.")
print("Press Ctrl+C to stop.")
print()


# ============================================================
# KEEP PROGRAM RUNNING
# ============================================================

try:

    while True:
        time.sleep(1)


except KeyboardInterrupt:

    print()
    print()
    print("Stopping...")
    print("Finishing captured audio and transcription...")


finally:

    # Stop receiving audio
    try:
        stream.stop()
        stream.close()
    except Exception:
        pass

    # Tell recorder no more audio is coming
    recording_queue.put(None)

    # Tell transcriber no more audio is coming
    transcription_queue.put(None)

    # Wait for recorder
    recorder_thread.join()

    # Wait for Whisper
    transcriber_thread.join()

    end_time = datetime.now()

    # Write footer
    with open(
        transcript_file,
        "a",
        encoding="utf-8"
    ) as f:

        f.write("\n")
        f.write(
            "----------------------------------------\n"
        )

        f.write(
            "Finished: "
            f"{end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

    print()
    print("==========================================")
    print("       TRANSCRIPTION COMPLETE")
    print("==========================================")
    print()

    print(
        f"Transcript:\n  {transcript_file}"
    )

    print()

    print(
        f"Audio backup:\n  {audio_file}"
    )

    print()