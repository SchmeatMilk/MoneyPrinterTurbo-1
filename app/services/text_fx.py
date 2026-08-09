"""Text & typography effects for the MPT pipeline (CPU-friendly, $0).

Two features:
1. Hook text overlay — a big, bold, high-contrast text block shown during
   the first ~2 seconds so the viewer's eye is grabbed before the footage
   even registers. Auto-derived from the script's first sentence when the
   caller doesn't supply one.
2. Word emphasis — in word-level kinetic subtitles, key words (from a
   highlight list) render in an accent color instead of the base color,
   drawing the eye to the selling points.

Both render with moviepy TextClip + PIL, no GPU, no extra services.
"""

import re

from loguru import logger

from app.config import config


def get_branding_style() -> dict:
    """Read text-effect settings from config.toml [branding] section."""
    branding = config._cfg.get("branding", {}) or {}
    return {
        "hook_enabled": bool(branding.get("hook_text_enabled", True)),
        "hook_text": str(branding.get("hook_text", "")).strip(),
        "hook_duration": float(branding.get("hook_duration", 2.0)),
        "hook_font_size_scale": float(branding.get("hook_font_size_scale", 0.12)),
        "hook_position": str(branding.get("hook_position", "center")),
        "hook_text_color": str(branding.get("hook_text_color", "#FFFFFF")),
        "hook_stroke_color": str(branding.get("hook_stroke_color", "#000000")),
        "hook_stroke_width": int(branding.get("hook_stroke_width", 4)),
        "hook_accent_color": str(branding.get("hook_accent_color", "#00D4AA")),
        "highlight_enabled": bool(branding.get("word_highlight_enabled", True)),
        "highlight_color": str(branding.get("word_highlight_color", "#00D4AA")),
    }


def derive_hook_text(video_script: str, max_chars: int = 60) -> str:
    """Pull a short attention-grabbing hook from the script.

    Strategy: use the first sentence up to a comma / question / exclamation
    (a natural beat), truncated to max_chars. Falls back to the first 60
    chars if no clean break is found.
    """
    script = (video_script or "").strip()
    if not script:
        return ""
    # split on sentence/beat punctuation, keep the first meaningful chunk
    parts = re.split(r"[.?!\n]+", script)
    candidate = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        candidate = part
        break
    if not candidate:
        candidate = script
    # cut at a comma if one appears early, else hard-truncate
    comma = candidate.find(",")
    if 10 < comma < max_chars:
        candidate = candidate[:comma]
    if len(candidate) > max_chars:
        candidate = candidate[: max_chars - 1].rstrip() + "…"
    return candidate.strip()


def build_hook_overlay(
    video_script: str,
    video_size: tuple[int, int],
    font_path: str,
    hook_text: str = "",
) -> "object | None":
    """Create a big bold hook-text TextClip for the first seconds.

    Returns a moviepy TextClip (or None when disabled/empty). The caller
    decides timing (with_start(0), with_duration(hook_duration)) so the
    overlay composes with intro cards.
    """
    style = get_branding_style()
    if not style["hook_enabled"]:
        return None
    text = (hook_text or style["hook_text"] or "").strip()
    if not text:
        text = derive_hook_text(video_script)
    if not text:
        return None

    video_width, video_height = video_size
    font_size = max(40, int(video_height * style["hook_font_size_scale"]))

    from moviepy import TextClip

    def _hex(c: str, default: str) -> tuple:
        c = c if isinstance(c, str) and c.startswith("#") and len(c) == 7 else default
        return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))

    clip = TextClip(
        text=text,
        font=font_path,
        font_size=font_size,
        color=_hex(style["hook_text_color"], "#FFFFFF"),
        stroke_color=_hex(style["hook_stroke_color"], "#000000"),
        stroke_width=style["hook_stroke_width"],
    )
    clip = clip.with_position("center")
    logger.info(f"hook overlay: '{text[:50]}...' ({font_size}px)")
    return clip


def get_highlight_words(video_script: str, extra: str = "") -> set[str]:
    """Derive words to emphasize in kinetic subtitles.

    Heuristic (no LLM call): pick uppercase acronyms (SMART, AI, SMB), key
    marketing words, plus any caller-provided comma-separated extras.
    Lowercased for matching.
    """
    script = (video_script or "").lower()
    marketing_terms = {
        "free", "now", "today", "instant", "fast", "smart", "no more",
        "guaranteed", "proven", "easy", "book", "audit", "lead", "call",
        "money", "lose", "win", "yes", "stop", "start",
    }
    words: set[str] = set()
    # explicit extras
    for w in re.split(r"[,\s]+", extra or ""):
        w = w.strip().lower()
        if w:
            words.add(w)
    # uppercase acronyms in the original script (e.g. SMART, SMB, AI)
    for m in re.findall(r"\b[A-Z]{2,}\b", video_script or ""):
        words.add(m.lower())
    # marketing terms present in the script
    for t in marketing_terms:
        if t in script:
            words.add(t)
    return words
