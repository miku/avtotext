# videototext

A small script to convert video to text using ASR (Automatic Speech Recognition).

## Features

- Transcribe local video/audio files
- Transcribe YouTube videos (by URL or video ID)
- Auto-detects input type (file, URL, or YouTube ID)
- Multiple ASR backends: OpenAI Whisper, NVIDIA Canary-Qwen-2.5B
- Self-contained with `uv` for dependency management

## Installation

```bash
# Install uv if needed
pip install uv

# The script manages its own dependencies via uv script metadata
```

## Usage

```bash
# Check required external tools (ffmpeg, lame)
uv run videototext.py --check

# Transcribe a local video file
uv run videototext.py video.mp4

# Save transcription to file
uv run videototext.py video.mp4 -o transcript.txt

# Use a different Whisper model (tiny, base, small, medium, large)
uv run videototext.py video.mp4 --model small

# Transcribe a YouTube video by URL
uv run videototext.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Transcribe by YouTube video ID
uv run videototext.py dQw4w9WgXcQ

# Use NVIDIA Canary-Qwen-2.5B backend
uv run videototext.py video.mp4 --backend canary
```

## ASR Backends

### Whisper (default)

OpenAI's Whisper model. Installed on first use if missing.

```bash
uv run videototext.py video.mp4 --backend whisper --model large
```

Models are stored in `$XDG_DATA_HOME/videototext/whisper/` (defaults to `~/.local/share/videototext/whisper/`).

### NVIDIA Canary-Qwen-2.5B

NVIDIA's 2.5B parameter speech recognition model via NeMo toolkit. Requires NVIDIA GPU.

```bash
uv run videototext.py video.mp4 --backend canary
```

Requires NeMo toolkit — the script will offer to install it if missing.

## Dependencies

External tools (checked via `--check`):
- `ffmpeg` - for audio extraction
- `lame` - for MP3 encoding

Python dependencies (auto-installed by uv):
- `click` - CLI interface
- `rich` - terminal output
- `yt-dlp` - YouTube video download
- `ffmpeg-python` - audio extraction

Optional (installed on demand):
- `openai-whisper` - Whisper ASR backend
- `nemo_toolkit[asr]` - NVIDIA Canary-Qwen backend
