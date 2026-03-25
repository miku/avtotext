# videototext

A small script to convert video to text using ASR (Automatic Speech Recognition).

## Features

- Transcribe local video/audio files
- Transcribe YouTube videos
- Uses OpenAI Whisper for transcription
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
uv run videototext.py check

# Transcribe a local video file
uv run videototext.py local video.mp4

# Transcribe a local file and save to file
uv run videototext.py local video.mp4 -o transcript.txt

# Use a different Whisper model (tiny, base, small, medium, large)
uv run videototext.py local video.mp4 --model small

# Transcribe a YouTube video
uv run videototext.py youtube "https://www.youtube.com/watch?v=..."

# Transcribe YouTube and save to file
uv run videototext.py youtube "https://www.youtube.com/watch?v=..." -o transcript.txt
```

## Dependencies

External tools (checked via `videototext.py check`):
- `ffmpeg` - for audio extraction
- `lame` - for MP3 encoding

Python dependencies (auto-installed by uv):
- `click` - CLI interface
- `rich` - terminal output
- `yt-dlp` - YouTube video download
- `ffmpeg-python` - audio extraction
- `openai-whisper` - ASR transcription (install separately)
