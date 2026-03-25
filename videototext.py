# /// script
# dependencies = [
#     "click",
#     "rich",
#     "yt-dlp",
#     "ffmpeg-python",
# ]
# ///

"""
videototext.py - Standalone script to convert video/audio to text.

Supports:
- Local video/audio files
- YouTube URLs
- ASR via multiple backends (Whisper, NVIDIA Canary-Qwen)
"""

import click
import sys
import os
import tempfile
import subprocess
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def extract_audio(input_path: str, output_path: str) -> str:
    """Extract audio from video file or URL using ffmpeg."""
    console.print(f"[dim]Extracting audio to:[/dim] {output_path}")

    if input_path.startswith(("http://", "https://")):
        # For URLs, use yt-dlp to download audio directly
        import yt_dlp

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }],
            "outtmpl": output_path[:-4],  # Remove .wav extension
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([input_path])

        # yt-dlp may create the file with a different name
        # Find the created .wav file
        for f in os.listdir("."):
            if f.startswith(output_path[:-4].split("/")[-1]) and f.endswith(".wav"):
                return f

        return output_path
    else:
        # For local files, use ffmpeg directly
        import ffmpeg

        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path, ar="16000", ac=1)
            ffmpeg.run(stream, quiet=True, overwrite_output=True)
            return output_path
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            raise RuntimeError(f"FFmpeg error: {stderr}")


def transcribe_with_whisper(audio_path: str, model: str = "base") -> str:
    """Transcribe audio using OpenAI Whisper."""
    try:
        import whisper
    except ImportError:
        console.print("[red]✗ Whisper not installed. Run:[/red]")
        console.print("  pip install openai-whisper")
        sys.exit(1)

    console.print(f"[dim]Loading Whisper model:[/dim] {model}")
    whisper_model = whisper.load_model(model)

    console.print("[dim]Transcribing...[/dim]")
    result = whisper_model.transcribe(audio_path)
    return result["text"]


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Convert video to text using ASR."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--model", default="base", help="Whisper model size")
@click.option("--output", "-o", type=click.Path(), help="Output text file")
def local(path, model, output):
    """Transcribe a local video or audio file."""
    console.print(f"[blue]Processing local file:[/blue] {path}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_audio = tmp.name

    try:
        audio_path = extract_audio(path, tmp_audio)
        text = transcribe_with_whisper(audio_path, model)

        if output:
            Path(output).write_text(text)
            console.print(f"[green]✓ Transcription saved to:[/green] {output}")
        else:
            console.print("\n[bold]Transcription:[/bold]")
            console.print(text)
    finally:
        if os.path.exists(tmp_audio):
            os.remove(tmp_audio)


@cli.command()
@click.argument("url")
@click.option("--model", default="base", help="Whisper model size")
@click.option("--output", "-o", type=click.Path(), help="Output text file")
def youtube(url, model, output):
    """Transcribe a YouTube video."""
    console.print(f"[blue]Processing YouTube URL:[/blue] {url}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_audio = tmp.name

    try:
        audio_path = extract_audio(url, tmp_audio)
        text = transcribe_with_whisper(audio_path, model)

        if output:
            Path(output).write_text(text)
            console.print(f"[green]✓ Transcription saved to:[/green] {output}")
        else:
            console.print("\n[bold]Transcription:[/bold]")
            console.print(text)
    finally:
        if os.path.exists(tmp_audio):
            os.remove(tmp_audio)


@cli.command()
def check():
    """Check for required external tools (ffmpeg, lame)."""
    import shutil

    tools = {"ffmpeg": shutil.which("ffmpeg"), "lame": shutil.which("lame")}

    table = []
    for tool, path in tools.items():
        status = "[green]✓[/green]" if path else "[red]✗[/red]"
        location = path if path else "[dim]not found[/dim]"
        table.append((tool, status, location))

    console.print("\n[bold]External Tools Check[/bold]")
    for tool, status, location in table:
        console.print(f"{status} {tool:12} - {location}")

    missing = [k for k, v in tools.items() if not v]
    if missing:
        console.print(f"\n[yellow]Missing tools:[/yellow] {', '.join(missing)}")
        sys.exit(1)
    else:
        console.print("\n[green]All required tools are installed.[/green]")


if __name__ == "__main__":
    cli()
