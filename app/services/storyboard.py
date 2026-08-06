"""Storyboard-driven video material generation.

Pipeline: script → storyboard (per-beat visual prompts) → Wan 2.1 clips →
local material list fed into the standard MPT combine step.

This is the free "dynamic video, not stock" layer:
- Reasoning: LLM splits the script into beats and writes a visual prompt per beat
- Generation: the official Wan-AI/Wan2.1 Gradio space (free, HF token) renders
  each beat as a 5s vertical clip
- Fallback: if Wan 2.1 is unavailable, falls back to Pexels stock terms so the
  pipeline never breaks
"""

import asyncio
import json
import os
from pathlib import Path

from loguru import logger

from app.services import llm, wan21
from app.utils import utils

STORYBOARD_SEGMENT_COUNT = 5
STORYBOARD_SEGMENT_DURATION = 5


def save_storyboard(task_id: str, storyboard: dict) -> str:
    """Persist the storyboard JSON next to the task."""
    task_dir = Path(utils.task_dir(task_id))
    task_dir.mkdir(parents=True, exist_ok=True)
    storyboard_path = task_dir / "storyboard.json"
    storyboard_path.write_text(
        json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"storyboard saved: {storyboard_path}")
    return str(storyboard_path)


def load_storyboard(task_id: str) -> dict | None:
    """Load a previously saved storyboard, if any."""
    storyboard_path = Path(utils.task_dir(task_id)) / "storyboard.json"
    if not storyboard_path.exists():
        return None
    try:
        return json.loads(storyboard_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning(f"failed to load storyboard: {exc}")
        return None


def generate_storyboard_materials(
    task_id: str,
    video_script: str,
    segment_count: int = STORYBOARD_SEGMENT_COUNT,
    duration_per_segment: int = STORYBOARD_SEGMENT_DURATION,
    use_wan: bool = True,
) -> list[str]:
    """
    Generate one video clip per storyboard beat.

    Returns a list of local video file paths (in storyboard order). When Wan
    2.1 generation fails, returns [] so the caller can fall back to Pexels.
    """
    storyboard = llm.generate_storyboard(
        video_script=video_script,
        segment_count=segment_count,
        duration_per_segment=duration_per_segment,
    )
    if not storyboard:
        logger.warning("empty storyboard; falling back to stock pipeline")
        return []
    save_storyboard(task_id, storyboard)

    if not use_wan:
        logger.info("use_wan=False; returning storyboard only (no clips)")
        return []

    # generate clips for each beat
    ordered_keys = sorted(storyboard.keys(), key=lambda k: int(k))
    clips: list[str] = []
    for seg_idx, key in enumerate(ordered_keys):
        beat = storyboard[key]
        prompt = beat.get("prompt") or ""
        method = beat.get("method") or "t2v"
        logger.info(f"[seg {seg_idx + 1}/{len(ordered_keys)}] {method}: {prompt[:90]}...")
        try:
            if method == "i2v" and beat.get("img"):
                # i2v needs an actual image file; skip with a warning if we
                # don't have one (future: generate a keyframe image first)
                logger.warning(f"[seg {seg_idx + 1}] i2v requested but no image; using t2v")
                clip = wan21.t2v(prompt, seg_idx)
            else:
                clip = wan21.t2v(prompt, seg_idx)
        except Exception as exc:
            logger.error(f"[seg {seg_idx + 1}] generation failed: {exc}")
            clip = ""
        if clip and os.path.exists(clip):
            clips.append(clip)
        else:
            logger.warning(f"[seg {seg_idx + 1}] no clip produced")
            # stop early — a gap in the timeline would break the render
            break

    if not clips:
        logger.warning("no Wan 2.1 clips produced; caller should fall back to stock")
    return clips


def storyboard_terms(video_script: str, segment_count: int = 5) -> list[str]:
    """
    Derive per-beat Pexels search terms from a storyboard, for stock fallback.
    """
    storyboard = llm.generate_storyboard(
        video_script=video_script,
        segment_count=segment_count,
        duration_per_segment=5,
    )
    terms = []
    for key in sorted(storyboard.keys(), key=lambda k: int(k)):
        prompt = storyboard[key].get("prompt", "")
        # take a compact keyword-ish slice of the prompt as a search term
        words = [w for w in prompt.replace(",", " ").split() if len(w) > 3][:6]
        terms.append(" ".join(words) if words else "business technology")
    return terms


# async shim for callers that prefer await (kept for API compatibility)
async def generate_storyboard_materials_async(*args, **kwargs):
    return generate_storyboard_materials(*args, **kwargs)
