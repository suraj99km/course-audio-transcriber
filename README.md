# 🎙️ Course Audio Transcriber

A local, privacy-friendly terminal application that continuously captures **system audio from course videos** and transcribes it using **OpenAI Whisper**.

The project is designed to avoid microphone capture. Audio is routed from the operating system through a virtual audio device and then processed locally by Whisper.

> **Current status:** macOS implementation is working. Windows support is being developed as a parallel implementation.

---

## ✨ Features

- 🎧 Captures **system/browser audio**, not the physical microphone
- 🤖 Uses OpenAI Whisper locally for transcription
- 🔄 Continuous audio capture
- 🧩 Processes audio in chunks to support long lectures
- ⏱️ Uses overlapping chunks to reduce words being lost at chunk boundaries
- 📝 Saves transcripts incrementally
- 💾 Saves a WAV backup of the captured lecture
- 📅 Organizes output by date
- 🔊 Automatically handles the selected audio-output profile on macOS
- ⌨️ Runs from the terminal
- 🔒 Audio and transcription can remain local to the machine

---

# 🏗️ Architecture

## macOS

The current macOS implementation uses **BlackHole 2ch** as the virtual audio device.

```text
                    ┌─────────────────────┐
                    │   Course / Browser  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ macOS Audio Output  │
                    │   Multi-Output      │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             Mac Speakers            BlackHole 2ch
                                          │
                                          ▼
                                  Python / sounddevice
                                          │
                                          ▼
                                     Audio chunks
                                          │
                                          ▼
                                  Whisper (local)
                                          │
                           ┌──────────────┴──────────────┐
                           ▼                             ▼
                       Transcript                    WAV backup
                           │
                           ▼
                    CourseTranscripts/
```

## Windows — planned

The Windows implementation will use **VB-CABLE** as the initial virtual audio-device approach.

```text
                    ┌─────────────────────┐
                    │   Course / Browser  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Windows Audio       │
                    │ Output Routing      │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
                 Speakers /           VB-CABLE
                 Headphones               │
                                          ▼
                                  Python / sounddevice
                                          │
                                          ▼
                                     Audio chunks
                                          │
                                          ▼
                                  Whisper (local)
                                          │
                           ┌──────────────┴──────────────┐
                           ▼                             ▼
                       Transcript                    WAV backup
```

The transcription engine is intended to remain platform-independent while audio routing/device management is handled separately for macOS and Windows.

---

# 📁 Project Structure

The intended project structure is:

```text
Transcriber/
│
├── transcribe.py
├── start_transcription.sh       # macOS launcher
├── start_transcription.bat      # Windows launcher (planned)
│
├── list_devices.py              # Audio-device diagnostic
├── test_audio.py                # Audio-capture diagnostic
│
├── requirements.txt
├── README.md
│
└── CourseTranscripts/
    └── YYYY-MM-DD/
        ├── lecture_YYYY-MM-DD_HH-MM-SS.txt
        └── lecture_YYYY-MM-DD_HH-MM-SS.wav
```

Additional platform-specific modules may be introduced as the Windows implementation matures.

---

# 🖥️ macOS Setup

## Requirements

- macOS
- Python 3.11
- Homebrew
- Conda/Miniforge or another Python environment manager
- FFmpeg
- BlackHole 2ch
- `sounddevice`
- NumPy
- OpenAI Whisper

The current tested environment uses:

```text
Python 3.11
Whisper: small
Audio chunks: 20 seconds
Overlap: 3 seconds
```

---

## 1. Install Homebrew

If Homebrew is not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Verify:

```bash
brew --version
```

---

## 2. Install FFmpeg

```bash
brew install ffmpeg
```

Verify:

```bash
ffmpeg -version
```

---

## 3. Install BlackHole

```bash
brew install --cask blackhole-2ch
```

After installation, verify that **BlackHole 2ch** appears in:

```text
Applications
→ Utilities
→ Audio MIDI Setup
```

---

# 🔊 macOS Audio Routing

The transcriber needs access to the same audio that is being played through the Mac.

Create two Multi-Output Devices in **Audio MIDI Setup**.

### Speaker profile

```text
Multi-Output Device

✓ MacBook Air Speakers
✓ BlackHole 2ch
```

Set:

```text
Primary Device → MacBook Air Speakers
```

### Earphone profile

```text
Multi-Output Device 2

✓ Pixel Buds A-Series
✓ BlackHole 2ch
```

Set:

```text
Primary Device → Pixel Buds A-Series
```

The launcher detects whether Pixel Buds are available and selects the appropriate profile.

> Device names can differ on another Mac. If so, update the names in `start_transcription.sh`.

---

# 🐍 Python Environment

The recommended environment for the current implementation is Python 3.11.

With Conda/Miniforge:

```bash
conda create -n transcribe python=3.11
```

Activate:

```bash
conda activate transcribe
```

Install dependencies:

```bash
pip install openai-whisper sounddevice numpy
```

Verify Python:

```bash
python --version
```

Expected:

```text
Python 3.11.x
```

---

# 🎙️ Find Audio Devices

Run:

```bash
python list_devices.py
```

A typical Mac setup may show:

```text
0 Pixel Buds A-Series
1 Pixel Buds A-Series
2 BlackHole 2ch
3 MacBook Air Microphone
4 MacBook Air Speakers
5 Microsoft Teams Audio
6 Multi-Output Device
```

The Python program should use **BlackHole 2ch** as the capture source.

> Avoid relying permanently on numeric device indexes because macOS can change device enumeration when Bluetooth devices connect or disconnect. Device-name discovery is preferred.

---

# ▶️ Running the Transcriber

The recommended launcher is:

```bash
./start_transcription.sh
```

The launcher:

1. Checks that the required audio tools are available.
2. Detects BlackHole.
3. Detects Pixel Buds.
4. Selects the appropriate Multi-Output Device.
5. Activates the Python environment.
6. Starts the transcription program.
7. Restores normal MacBook speakers when transcription exits normally.

---

# ⚡ One-Command Launch

To avoid navigating to the project directory every time, create a global terminal command.

Example:

```bash
mkdir -p ~/bin
```

Create:

```bash
nano ~/bin/transcribe
```

Add:

```bash
#!/bin/bash

cd "/Users/YOUR_USERNAME/MySpace/Projects/Transcriber" || exit 1

./start_transcription.sh
```

Make it executable:

```bash
chmod +x ~/bin/transcribe
```

Add `~/bin` to PATH:

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
```

Reload:

```bash
source ~/.zshrc
```

You can now start the transcriber from anywhere:

```bash
transcribe
```

---

# 📝 Output

Transcripts are stored under:

```text
CourseTranscripts/
```

Example:

```text
CourseTranscripts/
└── 2026-09-14/
    ├── lecture_2026-09-14_15-43-53.txt
    └── lecture_2026-09-14_15-43-53.wav
```

The `.txt` file is updated incrementally during transcription.

The `.wav` file provides a complete audio backup that can be used for re-transcription later with a different Whisper model or improved processing pipeline.

---

# ⚙️ Current Transcription Configuration

The current implementation uses:

```text
Whisper model : small
Chunk size    : 20 seconds
Overlap       : 3 seconds
Audio source  : System audio
Microphone    : Not used
```

### Why use overlapping chunks?

Without overlap, a sentence can be split between two chunks:

```text
Chunk 1:
"...the main concept we need to"

Chunk 2:
"understand is..."
```

The overlap gives Whisper additional context around the boundary and can improve continuity.

---

# 🔐 Privacy

The intended design is local processing:

```text
Course audio
     ↓
Virtual audio device
     ↓
Python
     ↓
Local Whisper model
     ↓
Local transcript
```

No audio needs to be sent to an external transcription API.

This makes the project suitable for transcribing locally available course material without uploading the audio to a cloud transcription service.

> The privacy properties of the overall setup also depend on the operating system, browser, other installed software, and any modifications made to this project.

---

# 🪟 Windows Support

Windows support is planned as a separate platform implementation.

## Initial Windows technology choices

| Component | Windows |
|---|---|
| OS | Windows 10/11 |
| Python | 3.11 |
| Virtual audio | VB-CABLE |
| Audio capture | `sounddevice` |
| Transcription | OpenAI Whisper |
| FFmpeg | FFmpeg |
| Launcher | `.bat` / PowerShell |
| Output | Same transcript/WAV structure |

The first Windows milestone is:

```text
Browser
   ↓
Windows audio
   ↓
VB-CABLE
   ↓
Python
   ↓
Whisper
   ↓
Transcript
```

After basic capture works, automatic switching between speakers/headphones and the virtual audio device will be implemented.

---

# 🧭 Windows Migration Plan

### Phase 1 — Environment

- [ ] Install Python 3.11
- [ ] Install Git
- [ ] Install FFmpeg
- [ ] Create isolated Python environment
- [ ] Install Whisper
- [ ] Install `sounddevice`
- [ ] Install NumPy

### Phase 2 — Audio

- [ ] Install VB-CABLE
- [ ] Verify CABLE Input
- [ ] Verify CABLE Output
- [ ] Confirm browser audio reaches VB-CABLE
- [ ] Confirm Python can capture VB-CABLE
- [ ] Verify microphone is not being captured

### Phase 3 — Transcription

- [ ] Port `transcribe.py`
- [ ] Test Whisper
- [ ] Test continuous capture
- [ ] Test 20-second chunks
- [ ] Test 3-second overlap
- [ ] Test incremental transcript saving
- [ ] Test WAV backup

### Phase 4 — Automation

- [ ] Detect headphones
- [ ] Detect speakers
- [ ] Detect VB-CABLE
- [ ] Configure audio routing
- [ ] Restore normal audio on exit

### Phase 5 — Launcher

- [ ] Create Windows launcher
- [ ] Remove manual environment activation
- [ ] Support launching from any directory
- [ ] Add useful error messages

### Phase 6 — Testing

Test:

- [ ] Built-in speakers
- [ ] Wired headphones
- [ ] Bluetooth headphones
- [ ] Bluetooth connect/disconnect
- [ ] Browser audio
- [ ] Course platform audio
- [ ] Pause/resume
- [ ] Ctrl+C
- [ ] Windows sleep/wake
- [ ] Microphone exclusion
- [ ] Audio restoration

---

# 🧩 Platform-Specific Design

The long-term architecture should separate transcription from operating-system audio management.

```text
                  ┌──────────────────────┐
                  │    transcribe.py     │
                  │                      │
                  │ Platform-independent │
                  │ transcription engine │
                  └──────────┬───────────┘
                             │
                  ┌──────────┴───────────┐
                  │                      │
         ┌────────▼─────────┐  ┌─────────▼─────────┐
         │   mac_audio.py   │  │  windows_audio.py │
         │                  │  │                   │
         │ BlackHole        │  │ VB-CABLE          │
         │ Multi-Output     │  │ Windows routing   │
         └──────────────────┘  └───────────────────┘
```

This allows the same transcription engine to run on both platforms while keeping OS-specific audio logic isolated.

---

# 🛠️ Troubleshooting

## Whisper cannot find FFmpeg

Check:

```bash
ffmpeg -version
```

If FFmpeg is not found, install it and ensure it is available on PATH.

---

## BlackHole is not detected

Check:

```bash
python list_devices.py
```

Confirm that:

```text
BlackHole 2ch
```

appears as an audio device.

Also verify the Multi-Output Device includes BlackHole.

---

## No speech is being transcribed

Check the audio chain:

```text
Browser
  ↓
Selected system output
  ↓
Virtual audio device
  ↓
sounddevice
  ↓
Whisper
```

The physical microphone should not be used as the input.

---

## Bluetooth headphones cause problems

Bluetooth devices can change audio-device enumeration.

Do not rely solely on a fixed numeric device ID such as:

```python
DEVICE = 2
```

Prefer searching for the device by name.

---

## Transcript stops unexpectedly

Check:

- Python process output
- Audio device availability
- Virtual audio driver
- Bluetooth connection
- Available RAM
- Whisper model loading errors

The WAV backup can be used to recover the lecture audio even if live transcription fails.

---

# 🚀 Future Improvements

Potential future features:

- [ ] Near-real-time floating transcript overlay
- [ ] Word-level / phrase-level live display
- [ ] Automatic language detection
- [ ] Speaker diarization
- [ ] Better timestamp formatting
- [ ] Automatic lecture title detection
- [ ] Markdown transcript output
- [ ] Automatic summary generation
- [ ] Key-point extraction
- [ ] Searchable lecture archive
- [ ] macOS `.app` launcher
- [ ] Windows `.exe` launcher
- [ ] Cross-platform configuration file
- [ ] Automatic model selection
- [ ] Optional GPU acceleration
- [ ] Automatic cleanup/compression of WAV backups

---

# 📜 License

Choose an appropriate license before publishing the repository.

A common choice for an open-source personal project is the MIT License.

---

# 🙌 Acknowledgements

This project uses:

- **OpenAI Whisper** for local speech recognition
- **sounddevice** for audio capture
- **FFmpeg** for audio/video processing
- **BlackHole** for macOS virtual audio routing
- **VB-CABLE** for the planned Windows virtual audio routing

---

## Project Philosophy

The goal is simple:

> **Start one command → play a course → receive a continuously saved local transcript.**

The system should stay:

**Local · Simple · Reliable · Cross-platform**
