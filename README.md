# videototext

A small script to convert video to text using ASR (Automatic Speech Recognition).

Two self-contained scripts — pick the one that fits your hardware:

| Script | Backend | Hardware | Deps installed |
|---|---|---|---|
| `videototext.py` | OpenAI Whisper | CPU | CPU-only torch |
| `videototext-gpu.py` | NVIDIA Canary-Qwen-2.5B | NVIDIA GPU | CUDA torch + NeMo |

## Features

- Transcribe local video/audio files
- Transcribe YouTube videos (by URL or video ID)
- Auto-detects input type (file, URL, or YouTube ID)
- Displays media info (duration, resolution, frame count) when available
- Caches downloaded audio and transcripts for instant repeat lookups
- Transcript goes to stdout, diagnostics to stderr (pipe-friendly)
- Self-contained with `uv` for dependency management

## Installation

```bash
# Install uv if needed
cargo install uv  # or: pip install uv

# Each script manages its own dependencies via uv script metadata
```

## Usage

### CPU (Whisper)

```bash
# Check required external tools (ffmpeg, lame)
videototext.py --check

# Transcribe a local video file
videototext.py video.mp4

# Pipe-friendly: only the transcript goes to stdout
videototext.py video.mp4 > transcript.txt

# Save transcription to file
videototext.py video.mp4 -o transcript.txt

# Use a different Whisper model (tiny, base, small, medium, large)
videototext.py video.mp4 --model small

# Transcribe a YouTube video by URL
videototext.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Transcribe by YouTube video ID
videototext.py dQw4w9WgXcQ
```

### GPU (NVIDIA Canary-Qwen-2.5B)

```bash
# Check required external tools (ffmpeg, lame, nvidia-smi)
videototext-gpu.py --check

# Transcribe a local video file
videototext-gpu.py video.mp4

# Transcribe a YouTube video
videototext-gpu.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Caching

Downloaded audio (for URLs) and transcripts are cached in `$XDG_CACHE_HOME/videototext/` (defaults to `~/.cache/videototext/`). Both scripts share the same cache directory.

- **URLs**: keyed by URL — same URL hits cache instantly
- **Local files**: keyed by path + modification time + size — cache invalidates on edit
- **Transcripts**: keyed by source + backend + model — different backends get separate entries

Use `--no-cache` to bypass, `--clear-cache` to remove all cached data.

## Dependencies

External tools (checked via `--check`):
- `ffmpeg` - for audio extraction
- `lame` - for MP3 encoding
- `nvidia-smi` - GPU script only

Python dependencies are auto-installed by uv on first run. Whisper models are stored in `$XDG_DATA_HOME/videototext/whisper/` (defaults to `~/.local/share/videototext/whisper/`).
