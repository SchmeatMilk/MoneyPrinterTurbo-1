"""Beat-synced editing: snap cut points to audio onsets using librosa.

Detects musical beats / audio onsets in the narration or BGM track and
returns cut timestamps aligned to them, so scene changes land on the
rhythm instead of arbitrary times. Pure CPU (librosa is NumPy-based),
safe on the AMD-iGPU / 13GB-RAM box.
"""

import os

from loguru import logger

try:
    import numpy as np
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("librosa not available; beat-synced editing disabled")


def detect_onsets(
    audio_path: str,
    frame_rate: float = 22050,
    hop_length: int = 512,
) -> list[float]:
    """Return onset times (seconds) detected in an audio file.

    Uses librosa.onset.onset_detect which finds energy spikes — good for
    both music beats and emphasized speech syllables. Returns [] on any
    failure (callers must fall back to non-synced cuts).
    """
    if not LIBROSA_AVAILABLE or not audio_path or not os.path.exists(audio_path):
        return []
    try:
        y, sr = librosa.load(audio_path, sr=frame_rate, mono=True)
        if y.size == 0:
            return []
        onset_frames = librosa.onset.onset_detect(
            y=y, sr=sr, hop_length=hop_length
        )
        times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)
        return [round(float(t), 3) for t in times]
    except Exception as exc:
        logger.warning(f"onset detection failed for {audio_path}: {exc}")
        return []


def detect_beats(
    audio_path: str,
    frame_rate: float = 22050,
    hop_length: int = 512,
) -> list[float]:
    """Return tempo-aligned beat times (seconds) using librosa.beat.beat_track."""
    if not LIBROSA_AVAILABLE or not audio_path or not os.path.exists(audio_path):
        return []
    try:
        y, sr = librosa.load(audio_path, sr=frame_rate, mono=True)
        if y.size == 0:
            return []
        tempo, beat_frames = librosa.beat.beat_track(
            y=y, sr=sr, hop_length=hop_length
        )
        times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)
        return [round(float(t), 3) for t in times]
    except Exception as exc:
        logger.warning(f"beat detection failed for {audio_path}: {exc}")
        return []


def snap_to_nearest(
    cut_points: list[float],
    anchors: list[float],
    max_shift: float = 0.35,
) -> list[float]:
    """Move each cut point to the nearest anchor (onset/beat) within max_shift.

    Cuts that are too far from any anchor stay where they are (fallback),
    so we never create an awkward jump just for sync.
    """
    if not anchors:
        return list(cut_points)
    snapped = []
    for cut in cut_points:
        best = min(anchors, key=lambda a: abs(a - cut))
        if abs(best - cut) <= max_shift:
            snapped.append(best)
        else:
            snapped.append(cut)
    # enforce strictly increasing order (snapping can create ties/regressions)
    ordered = []
    last = -1.0
    for t in sorted(snapped):
        if t > last:
            ordered.append(t)
            last = t
    return ordered


def get_beat_synced_cut_points(
    audio_path: str,
    desired_cuts: list[float],
    use_beats: bool = False,
) -> list[float]:
    """Top-level helper: detect anchors from audio, snap desired cuts to them."""
    if not LIBROSA_AVAILABLE:
        return list(desired_cuts)
    anchors = detect_beats(audio_path) if use_beats else detect_onsets(audio_path)
    if not anchors:
        return list(desired_cuts)
    return snap_to_nearest(desired_cuts, anchors)
