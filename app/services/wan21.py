"""Wan 2.1 free video generation via the official Wan-AI/Wan2.1 Gradio space.

Uses the HuggingFace token from the environment (HUGGINGFACE_API_KEY) — the
official Wan 2.1 space is free to use. Falls back gracefully to the classic
moneyprinterturbo material pipeline (Pexels) when generation fails.

Port of q1uki/MoneyPrinterAICreate's wan21.py, updated for gradio_client 2.x
and the current Wan-AI/Wan2.1 space API (t2v/i2v async + online_process_change).
"""

import asyncio
import os
import shutil
import time
from pathlib import Path
from uuid import uuid4

from loguru import logger

WAN_SPACE = "Wan-AI/Wan2.1"
T2V_SIZE = "720*1280"  # 9:16 vertical (short-form)
I2V_SIZE = "720*1280"
POLL_INTERVAL = 30
MAX_WAIT_SECONDS = 1800  # 30 min hard cap per segment (free queue can be very slow)
PROCESS_POLL_TIMEOUT = 120  # how long online_process_change may be polled


def _get_token() -> str:
    token = os.environ.get("HUGGINGFACE_API_KEY", "") or os.environ.get("HF_TOKEN", "")
    if not token:
        logger.warning("No HUGGINGFACE_API_KEY found; Wan 2.1 generation will fail")
    return token or None


def _client():
    from gradio_client import Client

    return Client(WAN_SPACE, token=_get_token())


def _submit_t2v(client, prompt: str) -> tuple:
    """Submit a text-to-video job; returns (cost_timesecs, estimated_waiting_timesecs)."""
    return client.predict(
        prompt=prompt,
        size=T2V_SIZE,
        watermark_wan=False,
        seed=-1,
        api_name="/t2v_generation_async",
    )


def _submit_i2v(client, prompt: str, image_path: str) -> tuple:
    """Submit an image-to-video job."""
    from gradio_client import handle_file

    return client.predict(
        prompt=prompt,
        image=handle_file(image_path),
        watermark_wan=False,
        seed=-1,
        api_name="/i2v_generation_async",
    )


def _fetch_ready_video(client) -> str | None:
    """Poll /online_process_change; returns the downloaded video path or None."""
    result = client.predict(api_name="/online_process_change")
    if isinstance(result, dict):
        video = result.get("video")
        # the space may wrap the payload under {"value": {...}}
        if not video and isinstance(result.get("value"), dict):
            video = result["value"].get("video")
        if video:
            return video
    return None


def _poll_until_ready(client, seg_id: int, method: str, timeout: int = MAX_WAIT_SECONDS) -> str:
    """Submit already-done; poll /online_process_change until a video drops."""
    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)
        polls += 1
        logger.info(f"[seg{seg_id}]-{method}-poll #{polls}...")
        try:
            video_path = _fetch_ready_video(client)
            if video_path:
                dst = str(Path("storage/tasks/wan21") / f"{uuid4()}.mp4")
                Path("storage/tasks/wan21").mkdir(parents=True, exist_ok=True)
                if os.path.exists(video_path):
                    shutil.move(video_path, dst)
                else:
                    dst = video_path
                logger.info(f"[seg{seg_id}]-{method}-[success]-output: {dst}")
                return dst
        except Exception as exc:
            logger.debug(f"[seg{seg_id}]-{method}-poll error: {exc}")
    raise TimeoutError(f"[seg{seg_id}] Wan 2.1 {method} timed out after {timeout}s")


def t2v(prompt: str, seg_id: int, timeout: int = MAX_WAIT_SECONDS) -> str:
    """Generate a 5s vertical clip from a text prompt. Returns local path."""
    try:
        client = _client()
        logger.info(f"[seg{seg_id+1}]-t2v-submit: {prompt[:80]}...")
        _submit_t2v(client, prompt)
        return _poll_until_ready(client, seg_id + 1, "t2v", timeout)
    except Exception as exc:
        logger.error(f"[seg{seg_id+1}]-t2v-FAILED: {exc}")
        return ""


def i2v(prompt: str, image_path: str, seg_id: int, timeout: int = MAX_WAIT_SECONDS) -> str:
    """Generate a 5s vertical clip from an image + prompt. Returns local path."""
    try:
        client = _client()
        logger.info(f"[seg{seg_id+1}]-i2v-submit: {prompt[:80]}...")
        _submit_i2v(client, prompt, image_path)
        return _poll_until_ready(client, seg_id + 1, "i2v", timeout)
    except Exception as exc:
        logger.error(f"[seg{seg_id+1}]-i2v-FAILED: {exc}")
        return ""
