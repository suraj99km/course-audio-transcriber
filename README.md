# Course Audio Transcriber

An automated, real-time system audio capture and live transcription tool built using Python, [OpenAI Whisper](https://github.com/openai/whisper), `sounddevice`, `numpy`, and Python's native multithreading modules.

This tool captures audio from continuous live sources—such as university lectures, online courses, webinars, or podcasts—and simultaneously saves an uncompressed `.wav` audio backup while appending live, timestamped text transcripts to a dedicated output file.

---

## Technical Architecture & Design

`transcribe.py` utilizes a decoupled, multithreaded architecture designed to handle real-time streaming without dropping audio frames or stalling live recording during heavy inference tasks.

