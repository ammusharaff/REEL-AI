import os
import subprocess

def _ffmpeg_ass_path(p: str) -> str:
    """
    Convert Windows path to FFmpeg-safe ASS filter path.
    Example:
      G:/path/file.ass -> G\\:/path/file.ass
    """
    p = os.path.abspath(p).replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        p = p[0] + "\\:" + p[2:]
    return p

def compose_vertical_video(bg_image: str, audio_path: str, srt_path: str, out_mp4: str):
    audio_path = os.path.abspath(audio_path)
    out_mp4 = os.path.abspath(out_mp4)
    srt_path = os.path.abspath(srt_path)
    work_dir = os.path.dirname(out_mp4)
    base, ext = os.path.splitext(srt_path)
    ext = ext.lower()
    ass_path = base + ".ass"

    # Convert SRT -> ASS only when needed.
    if ext == ".srt":
        subprocess.run(
            ["ffmpeg", "-y", "-i", srt_path, ass_path],
            check=True
        )
    else:
        ass_path = srt_path

    try:
        rel_ass = os.path.relpath(ass_path, work_dir)
        rel_audio = os.path.relpath(audio_path, work_dir)
        rel_out = os.path.relpath(out_mp4, work_dir)
        ass_filter_path = rel_ass.replace("\\", "/")
    except ValueError:
        rel_audio = audio_path
        rel_out = out_mp4
        ass_filter_path = _ffmpeg_ass_path(ass_path)

    # Use "increase" for cover-style scaling (ffmpeg doesn't accept "cover").
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        f"ass={ass_filter_path}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1080x1920:r=30",
        "-i", rel_audio,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-threads", "1",
        "-c:a", "aac",
        "-shortest",
        rel_out
    ]

    print("FFMPEG CMD:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=work_dir)
