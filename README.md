# 🎙️ Course Audio Transcriber

A local, privacy-friendly terminal tool that captures **system audio
from course videos** and transcribes it using **OpenAI Whisper**.

-   Captures system/browser audio, not the physical microphone.
-   Runs Whisper locally; no transcription API is required.
-   Saves timestamped `.txt` transcripts and `.wav` audio backups.
-   Processes audio continuously in overlapping chunks.

## How it works

Audio routing is platform-specific:

-   **macOS:** BlackHole 2ch + a Multi-Output Device.
-   **Windows:** A compatible system-audio capture input exposed by the
    laptop's audio driver (often **Stereo Mix**). Windows does **not**
    use BlackHole.

## 1. Get the project

Install Git, then clone the repository:

``` bash
git clone YOUR_REPOSITORY_URL
cd course-audio-transcriber
```

Or download the repository and open its folder in Terminal/PowerShell.

## 2. Install common requirements

Use **Python 3.11**.

### macOS

Install Homebrew if needed, then:

``` bash
brew install ffmpeg
conda create -n transcribe python=3.11
conda activate transcribe
```

### Windows 10/11

In PowerShell:

``` powershell
winget install --id Python.Python.3.11 -e
winget install --id Git.Git -e
winget install --id Gyan.FFmpeg -e
```

Close and reopen PowerShell, then verify:

``` powershell
py -3.11 --version
git --version
ffmpeg -version
```

Install the Python packages on either platform:

``` bash
python -m pip install --upgrade pip
python -m pip install openai-whisper sounddevice numpy
```

On Windows, use `py -3.11 -m pip` if multiple Python versions are
installed:

``` powershell
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install openai-whisper sounddevice numpy
```

If your version of `transcribe.py` imports SciPy, install it too:

``` bash
python -m pip install scipy
```

## 3. Configure audio capture

### macOS: BlackHole

Install BlackHole 2ch:

``` bash
brew install --cask blackhole-2ch
```

Open **Applications → Utilities → Audio MIDI Setup** and create a
Multi-Output Device containing: - Your normal output device (speakers or
headphones) - BlackHole 2ch

Select this Multi-Output Device as the macOS sound output. The
transcriber captures from **BlackHole 2ch**.

If you use the supplied launcher, check that its device names match your
Mac.

### Windows: select a compatible input device

Windows does **not** use BlackHole. Available capture devices depend on
the laptop and audio driver. A common option is **Stereo Mix**, but it
may not be available on every computer.

1.  Set your normal speakers/headphones as the Windows playback output.

2.  In PowerShell, go to the project folder and list audio devices:

    ``` powershell
    py -3.11 list_devices.py
    ```

3.  Find an **input** device that captures system playback (for example,
    `Stereo Mix`). Do not select the physical microphone or a
    playback-only device.

4.  Note its device index, host API, input channel count and supported
    sample rate. Device indexes differ between computers and can change
    when Bluetooth devices connect/disconnect.

5.  Update `DEVICE`, `CHANNELS` and `SAMPLE_RATE` in `transcribe.py` to
    match the selected device and a sample rate it supports.

6.  Test capture:

    ``` powershell
    py -3.11 test_audio.py
    ```

    Play a course video and listen to the resulting WAV. It should
    contain the course audio clearly.

**There is no universal Windows device number or sample rate.** Choose a
compatible system-audio input from your own `list_devices.py` output. If
no system-audio capture input is available, check Windows sound
settings/audio-driver options or ask your IT administrator. Do not
substitute the microphone.

## 4. Run the transcriber

### macOS

``` bash
./start_transcription.sh
```

### Windows

``` powershell
py -3.11 transcribe.py
```

The first run downloads the Whisper model. When audio capture starts,
play your course video. Press **Ctrl+C** to stop.

## 5. Output

Files are saved under `CourseTranscripts/`, organized by date:

``` text
CourseTranscripts/
└── YYYY-MM-DD/
    ├── lecture_YYYY-MM-DD_HH-MM-SS.txt
    └── lecture_YYYY-MM-DD_HH-MM-SS.wav
```

The transcript is updated as the lecture progresses. The WAV is an audio
backup for playback or later re-transcription.

## 6. Optional: one-command launch

### macOS

The supplied `start_transcription.sh` can be called from a small shell
command placed in a folder on your `PATH`.

### Windows

Create `%USERPROFILE%\bin\transcribe.cmd` with:

``` bat
@echo off
cd /d "%USERPROFILE%\Projects\course-audio-transcriber"
py -3.11 transcribe.py
```

Add `%USERPROFILE%\bin` to your user `Path`, then open a new PowerShell
window. Run:

``` powershell
transcribe
```

Change the project path in the `.cmd` file if you cloned the repository
elsewhere.

## Troubleshooting

-   **No audio in the WAV:** Recheck the selected capture input and
    audio routing using `list_devices.py` and `test_audio.py`.
-   **Windows device/channel error:** Recheck the current device list.
    Device indexes can change; confirm the selected device is an input
    and that `CHANNELS` and `SAMPLE_RATE` are supported.
-   **No speech or poor transcription:** Play the WAV backup first. If
    it is silent or distorted, fix audio capture before changing Whisper
    settings.
-   **FFmpeg not found:** Confirm `ffmpeg -version` works in a new
    terminal.
-   **Bluetooth changes device indexes:** Run `list_devices.py` again
    and update the selected Windows input if necessary.

## Privacy

Audio capture and transcription are performed locally by this
application using the local Whisper model. No audio needs to be sent to
an external transcription API. Overall privacy also depends on the
operating system, browser, installed software and any changes made to
the project.

## Acknowledgements

-   [OpenAI Whisper](https://github.com/openai/whisper) --- speech
    recognition
-   [python-sounddevice](https://python-sounddevice.readthedocs.io/) ---
    audio capture
-   [BlackHole](https://github.com/ExistentialAudio/BlackHole) --- macOS
    virtual audio routing
-   FFmpeg --- audio processing

------------------------------------------------------------------------

**Project goal:** Start one command, play a course, and receive a
continuously saved local transcript.
