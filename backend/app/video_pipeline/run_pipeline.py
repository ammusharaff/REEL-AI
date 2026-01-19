import os
from ..config import settings
from .tts_edge import run_tts
from .subtitles import build_karaoke_ass
from .ffmpeg_compose import compose_vertical_video

def run_full_pipeline(text: str, job_id: str) -> str:
    work_dir = os.path.join(settings.OUTPUTS_DIR, job_id)
    os.makedirs(work_dir, exist_ok=True)

    audio_path = os.path.join(work_dir, "voice.mp3")
    timing_json = os.path.join(work_dir, "timings.json")
    ass_path = os.path.join(work_dir, "captions.ass")
    out_mp4 = os.path.join(work_dir, "final.mp4")

    # TTS
    run_tts(text=text, out_audio_path=audio_path, out_timing_json=timing_json)

    # Karaoke subtitles (dynamic layout)
    build_karaoke_ass(word_timing_json=timing_json, out_ass=ass_path)

    # Compose video
    compose_vertical_video(
        bg_image=None,          # unused (color source)
        audio_path=audio_path,
        srt_path=ass_path,
        out_mp4=out_mp4,
    )

    return out_mp4
