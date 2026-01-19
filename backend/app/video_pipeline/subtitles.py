import json

STYLES = {
    "bold": {
        "font": "Arial",
        "size": 56,
        "primary": "&H00FFFFFF",
        "outline": 3,
    },
    "yellow": {
        "font": "Arial Black",
        "size": 60,
        "primary": "&H0000FFFF",
        "outline": 4,
    },
}


# =========================
# VIDEO / TEXT CONSTANTS
# =========================
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920

FONT_SIZE = 46
CENTER_X = SCREEN_WIDTH // 2
SAFE_Y = 1350          # fixed safe position (TikTok-style)

# Time window per subtitle block (seconds)
BLOCK_TIME = 1.4

# =========================
# ASS HEADER
# =========================
ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {SCREEN_WIDTH}
PlayResY: {SCREEN_HEIGHT}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{FONT_SIZE},&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,1,0,3,3,0,2,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Text
"""

def _ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

# =========================
# KARAOKE ASS BUILDER
# =========================
def build_karaoke_ass(word_timing_json: str, out_ass: str):
    with open(word_timing_json, "r", encoding="utf-8") as f:
        words = json.load(f)

    lines = [ASS_HEADER]

    buffer = []
    block_start = None
    block_duration = 0.0

    for w in words:
        text = w["text"].strip()
        if not text:
            continue

        dur = max(w["duration"] / 10_000_000.0, 0.12)

        if block_start is None:
            block_start = w["offset"] / 10_000_000.0

        buffer.append((text, dur))
        block_duration += dur

        # 🔑 TIME-BASED SEGMENTATION
        if block_duration >= BLOCK_TIME:
            _flush_block(lines, buffer, block_start, block_duration)
            buffer = []
            block_start = None
            block_duration = 0.0

    # ✅ ALWAYS flush remaining words (CRITICAL FIX)
    if buffer:
        _flush_block(lines, buffer, block_start, block_duration)

    with open(out_ass, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _flush_block(lines, buffer, start_time, duration):
    end_time = start_time + duration

    karaoke = ""
    for text, d in buffer:
        karaoke += f"{{\\k{int(d * 100)}}}{text} "

    lines.append(
        f"Dialogue: 0,{_ass_time(start_time)},{_ass_time(end_time)},Default,"
        f"{{\\an2\\pos({CENTER_X},{SAFE_Y})}}{karaoke.strip()}"
    )
