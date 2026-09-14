# Course Audio Transcriber

An automated, real-time audio capture and transcription tool using [OpenAI Whisper](https://github.com/openai/whisper) and `sounddevice`. This tool captures live audio playing on your computer (such as online lectures or course videos), saves a `.wav` audio backup, and generates a timestamped text transcript continuously.

---

## Features

- **Real-time Audio Capture:** Continuously records system audio (using virtual audio cables like BlackHole) without missing sound.
- **Live Transcription:** Uses OpenAI Whisper to transcribe audio in chunks with overlapping windows to prevent words from being cut off.
- **Audio Backup:** Automatically saves the recorded audio as a `.wav` file alongside the transcript.
- **Timestamped Transcripts:** Saves transcribed text immediately to a structured log file with precise real-time timestamps.
- **Organized Storage:** Creates date-wise folders under `CourseTranscripts/` for structured transcript management.

---

## File Structure & Output

When you run the script, output files are generated under the following directory layout:

