# Course Audio Transcriber

An automated, real-time system audio capture and transcription application built with Python, [OpenAI Whisper](https://github.com/openai/whisper), and `sounddevice`.

This application continuously records system audio (e.g., live online lectures, video courses, webinars, podcasts), creates a real-time `.wav` audio backup, and generates a timestamped text transcript dynamically.

---

## Architecture & How It Works

The system runs on a multithreaded pipeline using two queue-based workers fed by a live audio stream:

1. **Audio Callback (`sounddevice.InputStream`)**: Captures raw float32 audio chunks in real-time from the designated loopback audio device.
2. **Recording Worker Thread (`audio_recorder`)**: Converts captured float32 PCM data into 16-bit PCM and streams it into a `.wav` file on disk.
3. **Transcription Worker Thread (`transcription_worker_with_model`)**: Accumulates audio frames into sliding buffers, converts stereo to mono, and invokes OpenAI Whisper to transcribe overlapping temporal chunks (e.g., 20s chunks with 3s overlap to avoid cutting words).
4. **Output Writer**: Appends transcribed text immediately with local timestamps (`HH:MM:SS`) to the output log file with instant buffer flushing.

---

## File Output & Folder Structure

Transcripts and audio backups are organized into date-based subdirectories within `CourseTranscripts/`:

