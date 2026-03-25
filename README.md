# videototext

A small script to convert video to text using ASR (Automatic Speech Recognition).

Two self-contained scripts — pick the one that fits your hardware:

| Script | Backend | Hardware | Deps installed |
|---|---|---|---|
| `videototext.py` | OpenAI Whisper | CPU | CPU-only torch |
| `videototext-gpu.py` | NVIDIA NeMo ASR | NVIDIA GPU | CUDA torch + NeMo |

## Features

- Transcribe local video/audio files
- Transcribe YouTube videos (by URL or video ID)
- Auto-detects input type (file, URL, or YouTube ID)
- Displays media info (duration, resolution, frame count) when available
- Multiple GPU models: Canary-Qwen-2.5B, Canary-1B-v2, Parakeet-0.6B
- Multilingual support and speech translation (Canary models)
- Caches downloaded audio and transcripts for instant repeat lookups
- Transcript goes to stdout, diagnostics to stderr (pipe-friendly)
- Self-contained with `uv` for dependency management

## Installation

The only prerequisite is [uv](https://docs.astral.sh/uv/). Each script is
self-contained and manages all its Python dependencies automatically on first
run.

```bash
# Install uv
cargo install uv  # or: pip install uv, or: curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy the script(s) somewhere in PATH and make executable
cp videototext.py ~/.local/bin/
chmod +x ~/.local/bin/videototext.py
```

That's it. No virtualenvs, no `pip install`, no setup.py. On first run, `uv`
resolves and caches the dependencies automatically.

A `.deb`/`.rpm` package is also available (see `make deb` / `make rpm`).

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

### GPU (NVIDIA NeMo)

```bash
# List available models
videototext-gpu.py --list-models

# Transcribe with default model (canary-1b-v2)
videototext-gpu.py video.mp4

# Choose a specific model
videototext-gpu.py video.mp4 --model canary-qwen-2.5b
videototext-gpu.py video.mp4 --model parakeet-0.6b

# Multilingual: set source language (canary models)
videototext-gpu.py video.mp4 --lang de

# Translation: transcribe German audio to English text
videototext-gpu.py video.mp4 --lang de --target-lang en

# Transcribe a YouTube video
videototext-gpu.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### Available GPU models

| Model | Size | Languages | Notes |
|---|---|---|---|
| `canary-1b-v2` (default) | 1B | 25 languages | Multilingual, translation support |
| `canary-qwen-2.5b` | 2.5B | multilingual | Highest quality, speech-language model |
| `parakeet-0.6b` | 600M | English only | Fast and lightweight |

## Caching

Downloaded audio (for URLs) and transcripts are cached in `$XDG_CACHE_HOME/videototext/` (defaults to `~/.cache/videototext/`). Both scripts share the same cache directory.

- **URLs**: keyed by URL — same URL hits cache instantly
- **Local files**: keyed by path + modification time + size — cache invalidates on edit
- **Transcripts**: keyed by source + model + language — different models/languages get separate entries

Use `--no-cache` to bypass, `--clear-cache` to remove all cached data.

## Dependencies

External tools (checked via `--check`):
- `ffmpeg` - for audio extraction
- `lame` - for MP3 encoding
- `nvidia-smi` - GPU script only

Python dependencies are auto-installed by uv on first run. Whisper models are stored in `$XDG_DATA_HOME/videototext/whisper/` (defaults to `~/.local/share/videototext/whisper/`).
