#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "click",
#     "rich",
#     "yt-dlp",
#     "ffmpeg-python",
#     "openai-whisper",
#     "nemo_toolkit[asr]",
# ]
# ///

"""
videototext.py - Convert video/audio to text.

Usage:
    uv run videototext.py <input> [options]

Input can be a local file path, a URL, or a YouTube video ID.
"""

import click
import sys
import os
import re
import tempfile
import shutil
from pathlib import Path
from rich.console import Console
import yt_dlp
import ffmpeg
import whisper

console = Console()


def get_data_dir() -> Path:
    """Get XDG-compliant data directory for videototext."""
    xdg = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    data_dir = Path(xdg) / "videototext"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def detect_input_type(input_str: str) -> str:
    """Detect whether input is a file path, URL, or YouTube ID."""
    if os.path.exists(input_str):
        return "file"
    if re.match(r"^https?://", input_str):
        return "url"
    # YouTube video IDs are 11 characters: alphanumeric, dash, underscore
    if re.match(r"^[A-Za-z0-9_-]{11}$", input_str):
        return "youtube_id"
    console.print(
        f"[red]✗ File not found and not recognized as URL or YouTube ID:[/red] {input_str}"
    )
    sys.exit(1)


def extract_audio(input_path: str, output_path: str) -> str:
    """Extract audio from video file or URL using ffmpeg."""
    console.print(f"[dim]Extracting audio...[/dim]")

    if input_path.startswith(("http://", "https://")):
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": output_path[:-4],  # Remove .wav extension
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([input_path])

        base = output_path[:-4].split("/")[-1]
        for f in os.listdir(os.path.dirname(output_path) or "."):
            if f.startswith(base) and f.endswith(".wav"):
                return os.path.join(os.path.dirname(output_path) or ".", f)

        return output_path
    else:
        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path, ar="16000", ac=1)
            ffmpeg.run(stream, quiet=True, overwrite_output=True)
            return output_path
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            raise RuntimeError(f"FFmpeg error: {stderr}")


def transcribe_with_whisper(audio_path: str, model_name: str = "base") -> str:
    """Transcribe audio using OpenAI Whisper."""
    data_dir = get_data_dir() / "whisper"
    data_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[dim]Loading Whisper model:[/dim] {model_name}")
    model = whisper.load_model(model_name, download_root=str(data_dir))
    console.print("[dim]Transcribing...[/dim]")
    result = model.transcribe(audio_path)
    return result["text"]


def transcribe_with_canary(audio_path: str) -> str:
    """Transcribe audio using NVIDIA Canary-Qwen-2.5B."""
    from nemo.collections.speechlm2.models import SALM

    console.print("[dim]Loading Canary-Qwen-2.5B model...[/dim]")
    model = SALM.from_pretrained("nvidia/canary-qwen-2.5b")
    console.print("[dim]Transcribing...[/dim]")
    answer_ids = model.generate(
        prompts=[
            [
                {
                    "role": "user",
                    "content": f"Transcribe the following: {model.audio_locator_tag}",
                    "audio": [audio_path],
                }
            ]
        ],
        max_new_tokens=1024,
    )
    return model.tokenizer.ids_to_text(answer_ids[0].cpu())


@click.command()
@click.argument("input_source", required=False)
@click.option(
    "--backend",
    type=click.Choice(["whisper", "canary"]),
    default="whisper",
    help="ASR backend (whisper or canary)",
)
@click.option(
    "--model",
    default="base",
    help="Whisper model size (tiny, base, small, medium, large)",
)
@click.option("--output", "-o", type=click.Path(), help="Output text file")
@click.option("--check", is_flag=True, help="Check for required external tools")
@click.version_option(version="0.2.0")
def cli(input_source, backend, model, output, check):
    """Convert video/audio to text.

    INPUT_SOURCE can be a local file path, a URL, or a YouTube video ID.
    """
    if check:
        tools = {"ffmpeg": shutil.which("ffmpeg"), "lame": shutil.which("lame")}
        console.print("\n[bold]External Tools[/bold]")
        for tool, path in tools.items():
            status = "[green]✓[/green]" if path else "[red]✗[/red]"
            location = path if path else "[dim]not found[/dim]"
            console.print(f"  {status} {tool:12} {location}")
        missing = [k for k, v in tools.items() if not v]
        if missing:
            console.print(f"\n[yellow]Missing:[/yellow] {', '.join(missing)}")
            sys.exit(1)
        else:
            console.print("\n[green]All tools installed.[/green]")
        return

    if not input_source:
        console.print("[red]✗ Please provide an input file, URL, or YouTube ID.[/red]")
        raise SystemExit(1)

    input_type = detect_input_type(input_source)

    if input_type == "youtube_id":
        input_source = f"https://www.youtube.com/watch?v={input_source}"
        input_type = "url"

    label = "file" if input_type == "file" else "URL"
    console.print(f"[blue]Processing {label}:[/blue] {input_source}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_audio = tmp.name

    try:
        audio_path = extract_audio(input_source, tmp_audio)

        if backend == "whisper":
            text = transcribe_with_whisper(audio_path, model)
        elif backend == "canary":
            text = transcribe_with_canary(audio_path)

        if output:
            Path(output).write_text(text)
            console.print(f"[green]✓ Saved to:[/green] {output}")
        else:
            console.print("\n[bold]Transcription:[/bold]")
            console.print(text)
    finally:
        if os.path.exists(tmp_audio):
            os.remove(tmp_audio)


if __name__ == "__main__":
    cli()
