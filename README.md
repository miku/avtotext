# videototext

A small script to convert video to text using ASR (Automatic Speech Recognition).

## Features

- Transcribe local video/audio files
- Transcribe YouTube videos (by URL or video ID)
- Auto-detects input type (file, URL, or YouTube ID)
- Displays media info (duration, resolution, frame count) when available
- Multiple ASR backends: OpenAI Whisper (CPU), NVIDIA Canary-Qwen-2.5B (GPU)
- Caches downloaded audio and transcripts for instant repeat lookups
- Transcript goes to stdout, diagnostics to stderr (pipe-friendly)
- Self-contained with `uv` for dependency management

## Installation

```bash
# Install uv if needed
cargo install uv  # or: pip install uv

# The script manages its own dependencies via uv script metadata
```

## Usage

```bash
# Check required external tools (ffmpeg, lame)
videototext.py --check

# Transcribe a local video file
videototext.py video.mp4

# Save transcription to file
videototext.py video.mp4 -o transcript.txt

# Pipe-friendly: only the transcript goes to stdout
videototext.py video.mp4 > transcript.txt

# Use a different Whisper model (tiny, base, small, medium, large)
videototext.py video.mp4 --model small

# Transcribe a YouTube video by URL
videototext.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Transcribe by YouTube video ID
videototext.py dQw4w9WgXcQ

# Use NVIDIA Canary-Qwen-2.5B backend (requires NVIDIA GPU)
uv run --with 'nemo_toolkit[asr]' videototext.py video.mp4 --backend canary

# Bypass cache for a fresh transcription
videototext.py video.mp4 --no-cache
```

## ASR Backends

### Whisper (default)

OpenAI's Whisper model, running on CPU. Installed automatically on first use.

```bash
videototext.py video.mp4 --backend whisper --model large
```

Models are stored in `$XDG_DATA_HOME/videototext/whisper/` (defaults to `~/.local/share/videototext/whisper/`).

### NVIDIA Canary-Qwen-2.5B

NVIDIA's 2.5B parameter speech recognition model via NeMo toolkit. Requires an NVIDIA GPU. The `nemo_toolkit` dependency is not installed by default — pass it via `--with`:

```bash
uv run --with 'nemo_toolkit[asr]' videototext.py video.mp4 --backend canary
```

## Caching

Downloaded audio (for URLs) and transcripts are cached in `$XDG_CACHE_HOME/videototext/` (defaults to `~/.cache/videototext/`).

- **URLs**: keyed by URL — same URL hits cache instantly
- **Local files**: keyed by path + modification time + size — cache invalidates on edit
- **Transcripts**: keyed by source + backend + model — different models get separate entries

Use `--no-cache` to bypass.

## Dependencies

External tools (checked via `--check`):
- `ffmpeg` - for audio extraction
- `lame` - for MP3 encoding

Python dependencies (auto-installed by uv):
- `click` - CLI interface
- `rich` - terminal output
- `yt-dlp` - YouTube video download
- `ffmpeg-python` - audio extraction
- `openai-whisper` - Whisper ASR backend
- `torch` / `torchaudio` - (CPU-only by default)

Optional (installed on demand):
- `nemo_toolkit[asr]` - NVIDIA Canary-Qwen backend
