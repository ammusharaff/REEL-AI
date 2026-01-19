import os
import json
import asyncio
import edge_tts

from ..config import settings

async def synthesize_with_word_timings(text: str, out_audio_path: str, out_timing_json: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=settings.EDGE_TTS_VOICE,
        rate=settings.EDGE_TTS_RATE,
        pitch=settings.EDGE_TTS_PITCH,
    )

    word_events = []
    audio_bytes = b""

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            # offset/duration are in 100-nanosecond units
            word_events.append({
                "text": chunk.get("text", ""),
                "offset": chunk.get("offset", 0),
                "duration": chunk.get("duration", 0),
            })

    os.makedirs(os.path.dirname(out_audio_path), exist_ok=True)
    with open(out_audio_path, "wb") as f:
        f.write(audio_bytes)

    with open(out_timing_json, "w", encoding="utf-8") as f:
        json.dump(word_events, f, ensure_ascii=False, indent=2)

def run_tts(text: str, out_audio_path: str, out_timing_json: str):
    asyncio.run(synthesize_with_word_timings(text, out_audio_path, out_timing_json))
