# Phase 1: Subtitle Fix + Visual Polish - Research

**Researched:** 2026-08-04
**Domain:** Python video pipeline (MoneyPrinterTurbo) — subtitle fallback, transitions, kinetic typography, color grading
**Confidence:** HIGH

---

## Summary

MoneyPrinterTurbo v1.3.3 has a working core pipeline but two critical gaps for marketing-quality output:

1. **Edge TTS subtitle bug** — periods in branded terms (`SMART SMB.AI`) break the cue parser, causing silent subtitle failure (no `.srt` generated). The codebase already has Whisper integration (`app/services/subtitle.py` with `faster-whisper`) but no fallback chain.

2. **No visual polish** — hard cuts only, no branding, no transitions, no kinetic typography, no color grading. MoviePy supports transitions via `CompositeVideoClip` crossfades and TextClip animations; LUTs can be applied via FFmpeg filters or PIL.

**Primary recommendation:** Add a `subtitle_provider` fallback chain (edge → whisper) in `voice.py`/`subtitle.py`, then extend `video.py` with branding system, transition engine, kinetic typography, and color grading pipeline.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Subtitle generation (Edge TTS) | `app/services/voice.py` | `app/services/subtitle.py` | Edge TTS produces cues; subtitle.py handles Whisper fallback |
| Subtitle generation (Whisper) | `app/services/subtitle.py` | — | Existing `faster-whisper` integration, just needs fallback trigger |
| Video composition | `app/services/video.py` | — | Core rendering logic, transitions, text overlays |
| Branding assets | `config.toml` `[branding]` | `app/services/video.py` | Config-driven, applied during composition |
| Transitions | `app/services/video.py` | — | MoviePy `CompositeVideoClip` crossfade/slide |
| Kinetic typography | `app/services/video.py` | `app/services/voice.py` | Word-level timestamps from TTS → TextClip animation |
| Color grading | `app/services/video.py` | — | FFmpeg filter complex or PIL ImageOps |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `moviepy` | 2.x (current) | Video composition, TextClip, transitions | Already in project, mature |
| `faster-whisper` | latest | Whisper subtitle fallback | Already integrated in `subtitle.py` |
| `edge-tts` | 7.x | Primary TTS + word boundaries | Already primary provider |
| `ffmpeg-python` / subprocess | system | Low-level encoding, LUT filters | Direct FFmpeg for complex filters |
| `pillow` | latest | Image processing, logo overlay | Already in project |
| `numpy` | latest | Frame manipulation for effects | Already in project |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `opencv-python` | latest | Advanced transitions, optical flow | If MoviePy transitions insufficient |
| `colour-science` | latest | LUT parsing, color space conversion | For `.cube`/`.3dl` LUT support |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `moviepy` transitions | FFmpeg `xfade` filter | More control, but complex filter graphs |
| `faster-whisper` | `openai-whisper` | `faster-whisper` is 4x faster (CTranslate2) |
| Custom kinetic text | `pysubs2` + ASS format | ASS supports karaoke, but MoviePy doesn't render ASS |

**Installation:**
```bash
uv sync  # or pip install -r requirements.txt
# No new packages needed — all deps already in project
```

**Version verification:**
```bash
# Already verified in project venv
python -c "import moviepy; print(moviepy.__version__)"
python -c "import faster_whisper; print(faster_whisper.__version__)"
python -c "import edge_tts; print(edge_tts.__version__)"
```

---

## Package Legitimacy Audit

> No new packages required for Phase 1 — all dependencies already in `requirements.txt` and verified working in current installation.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| moviepy | PyPI | 8+ yrs | 1M+/wk | github.com/Zulko/moviepy | OK | Approved |
| faster-whisper | PyPI | 2+ yrs | 500k+/wk | github.com/SYSTRAN/faster-whisper | OK | Approved |
| edge-tts | PyPI | 3+ yrs | 200k+/wk | github.com/rany2/edge-tts | OK | Approved |
| ffmpeg-python | PyPI | 7+ yrs | 1M+/wk | github.com/kkroening/ffmpeg-python | OK | Approved |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────┐
│   CLI / API     │
│  (cli.py)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│  Script Gen     │────▶│  TTS (Edge)      │──▶ audio.mp3 + SubMaker(cues)
│  (DeepSeek)     │     └────────┬─────────┘
└─────────────────┘              │
                                 ▼
                        ┌──────────────────┐
                        │  Subtitle Gen    │
                        │  (edge cues)     │
                        └────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
            ┌───────────────┐         ┌───────────────┐
            │ Success: .srt │         │ Fail: unmatched │
            └───────────────┘         │ cues → FALLBACK │
                                      └────────┬────────┘
                                               ▼
                                      ┌──────────────────┐
                                      │  Whisper         │
                                      │  (faster-whisper)│
                                      │  → audio.mp3     │
                                      │  → subtitle.srt  │
                                      └────────┬─────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │  Video Compose   │
                                      │  (video.py)      │
                                      │  - Materials     │
                                      │  - Transitions   │
                                      │  - Branding      │
                                      │  - Kinetic Text  │
                                      │  - Color Grade   │
                                      └────────┬─────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │  final-1.mp4     │
                                      └──────────────────┘
```

### Recommended Project Structure

```
MoneyPrinterTurbo/
├── app/
│   ├── services/
│   │   ├── voice.py          # ← ADD: subtitle fallback chain
│   │   ├── subtitle.py       # ← Whisper fallback (exists)
│   │   ├── video.py          # ← ADD: branding, transitions, kinetic, LUT
│   │   └── ...
│   └── config.py             # ← ADD: branding config model
├── config.toml               # ← ADD: [branding] section
└── storage/
    ├── materials/            # Stock footage
    ├── branding/             # ← NEW: logo, LUT, fonts
    └── tasks/
        └── <task_id>/
            ├── final-1.mp4
            ├── subtitle.srt
            └── ...
```

### Pattern 1: Subtitle Fallback Chain

**What:** Try Edge TTS first; if `create_subtitle()` produces no `.srt` (unmatched cues), auto-fallback to Whisper.

**When to use:** Every render — subtitle reliability is critical for marketing.

**Example:**
```python
# In voice.py create_subtitle() or new wrapper
async def generate_subtitle_with_fallback(text, voice_name, audio_file, subtitle_file):
    # Try Edge TTS first
    sub_maker = await tts(text, voice_name, rate, audio_file)
    create_subtitle(sub_maker, text, subtitle_file)
    
    if not os.path.exists(subtitle_file) or os.path.getsize(subtitle_file) == 0:
        logger.warning("Edge TTS subtitle failed, falling back to Whisper")
        # Call Whisper directly
        from app.services.subtitle import create as whisper_create
        whisper_create(audio_file, subtitle_file)
```

### Pattern 2: MoviePy Transitions

**What:** Crossfade/slide transitions between clips using `CompositeVideoClip` with overlapping clips and `afx.audio_fadein/out`.

**When to use:** Between every material clip in `generate_video()`.

**Example:**
```python
# Crossfade transition
clip1 = VideoFileClip("clip1.mp4").subclip(0, 6)
clip2 = VideoFileClip("clip2.mp4").subclip(0, 6)

# Overlap last 1s of clip1 with first 1s of clip2
transition_duration = 1.0
clip1_fade = clip1.fx(afx.audio_fadeout, transition_duration)
clip2_fade = clip2.fx(afx.audio_fadein, transition_duration)

# Visual crossfade
from moviepy.video.compositing.transitions import crossfadein, crossfadeout
final = CompositeVideoClip([
    clip1_fade.set_start(0),
    clip2_fade.set_start(clip1.duration - transition_duration).crossfadein(transition_duration)
])
```

### Pattern 3: Kinetic Typography

**What:** Animate TextClip words sequentially using word-level timestamps from Edge TTS `cues` or Whisper `word_timestamps`.

**When to use:** When `subtitle_enabled=True` and kinetic mode configured.

**Example:**
```python
# Word-level animation using TextClip
def create_kinetic_text_clips(words_with_timestamps, video_size, style_config):
    clips = []
    for word_data in words_with_timestamps:
        word, start, end = word_data["word"], word_data["start"], word_data["end"]
        txt_clip = TextClip(
            word,
            font=style_config["font"],
            font_size=style_config["font_size"],
            color=style_config["color"],
            stroke_color=style_config["stroke_color"],
            stroke_width=style_config["stroke_width"]
        )
        # Pop-in animation
        txt_clip = txt_clip.set_start(start).set_duration(end - start)
        txt_clip = txt_clip.resize(lambda t: 1 + 0.3 * (1 - t/(end-start)))  # Scale pop
        clips.append(txt_clip)
    return CompositeVideoClip(clips, size=video_size)
```

### Pattern 4: Color Grading / LUT

**What:** Apply `.cube` LUT via FFmpeg `lut3d` filter or PIL `ImageOps.colorize` for simple grades.

**When to use:** On each source clip before composition, or on final composite.

**Example:**
```python
# FFmpeg LUT application (high quality)
ffmpeg -i input.mp4 -vf "lut3d=file=brand_lut.cube" -c:a copy output.mp4

# Or in Python via subprocess
subprocess.run([
    ffmpeg_binary, "-y", "-i", input_path,
    "-vf", f"lut3d=file={lut_path}",
    "-c:a", "copy", output_path
])
```

### Anti-Patterns to Avoid

- **Don't hand-roll subtitle parsing** — use existing `subtitle.py` Whisper + `voice.py` Edge TTS cue logic
- **Don't re-encode clips multiple times** — use FFmpeg concat demuxer for final assembly (already in `video.py`)
- **Don't hardcode branding assets** — all via `config.toml` `[branding]` section
- **Don't skip cleanup** — temp files from transitions/LUT processing must be deleted

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Whisper integration | Custom faster-whisper wrapper | `app.services.subtitle.create()` | Already handles model loading, VAD, word timestamps |
| Edge TTS subtitle cues | Custom cue parser | `edge_tts.SubMaker` + `_build_subtitle_items_from_edge_cues` | Handles WordBoundary events, Arabic normalization, punctuation matching |
| Video transitions | Custom frame blending | MoviePy `CompositeVideoClip` + `crossfadein/out` | GPU-accelerated, tested |
| LUT application | Custom color matrix | FFmpeg `lut3d` filter | Industry standard, hardware accelerated |
| Kinetic text | Custom TextClip animation | MoviePy `TextClip` + `set_start`/`set_duration` | Built-in, respects font/stroke config |

**Key insight:** MoneyPrinterTurbo already has 90% of the infrastructure. Phase 1 is wiring fallbacks and exposing existing capabilities via config.

---

## Runtime State Inventory

> Not a rename/refactor phase — omit.

---

## Common Pitfalls

### Pitfall 1: Edge TTS Unmatched Cues (The Core Bug)
**What goes wrong:** `SMART SMB.AI` period breaks `_match_script_line()` → cues never match script lines → `create_subtitle()` returns early without writing `.srt`

**Why it happens:** `_match_script_line()` uses regex `re.sub(r"[_\\W]+", "", ...)` which strips periods, but `current_text` accumulates raw cue content including periods → normalized comparison fails

**How to avoid:** 
1. Normalize both cue text AND script lines identically before matching (strip periods, `_`, punctuation)
2. Add fallback to Whisper when `len(sub_items) != len(script_lines)`

**Warning signs:** Log shows `"edge cues still have unmatched text after aggregation: SMARTSMB.AImakessure..."`

### Pitfall 2: Whisper Model Download on First Run
**What goes wrong:** `large-v3` model (1.5 GB) downloads on first Whisper call → render times out

**Why it happens:** `subtitle.py` downloads model lazily in `create()`

**How to avoid:** Pre-download model during setup, or use smaller model (`base`/`small`) for speed with config option

**Warning signs:** Log shows `"loading model: large-v3"` on first render

### Pitfall 3: MoviePy Transition Memory
**What goes wrong:** Crossfade composites multiple clips in RAM → OOM on long videos

**Why it happens:** `CompositeVideoClip` holds all frames in memory

**How to avoid:** Use FFmpeg `xfade` filter for transitions (single-pass encode) or limit transition duration to 0.5-1s

**Warning signs:** RAM spikes during `generate_video()`, `MemoryError` in logs

### Pitfall 4: Kinetic Typography Timing Drift
**What goes wrong:** Word animations drift from audio due to timestamp rounding

**Why it happens:** Edge TTS cues in 100ns units, MoviePy in float seconds; rounding accumulates

**How to avoid:** Use exact cue timestamps, don't round; validate sync with `ffprobe` on output

**Warning signs:** Subtitles visibly ahead/behind speech in output video

---

## Code Examples

### Common Operation 1: Subtitle Fallback Wrapper
```python
# Source: app/services/voice.py (new function)
async def generate_subtitle_with_fallback(
    text: str,
    voice_name: str,
    voice_rate: float,
    audio_file: str,
    subtitle_file: str,
    voice_volume: float = 1.0
) -> bool:
    """Try Edge TTS first, fallback to Whisper on failure."""
    # Primary: Edge TTS
    sub_maker = tts(text, voice_name, voice_rate, audio_file, voice_volume)
    if sub_maker:
        create_subtitle(sub_maker, text, subtitle_file)
        if os.path.exists(subtitle_file) and os.path.getsize(subtitle_file) > 0:
            return True
    
    # Fallback: Whisper
    logger.warning("Edge TTS subtitle failed, falling back to Whisper")
    from app.services.subtitle import create as whisper_create
    result = whisper_create(audio_file, subtitle_file)
    return result is not None
```

### Common Operation 2: Transition Between Clips
```python
# Source: app/services/video.py (extend generate_video)
def apply_transition(clip1: VideoFileClip, clip2: VideoFileClip, 
                     transition_mode: str, duration: float = 1.0):
    """Apply transition between two clips."""
    if transition_mode == "crossfade":
        from moviepy.video.compositing.transitions import crossfadein, crossfadeout
        clip1 = clip1.fx(afx.audio_fadeout, duration)
        clip2 = clip2.fx(afx.audio_fadein, duration).crossfadein(duration)
        return CompositeVideoClip([
            clip1.set_start(0),
            clip2.set_start(clip1.duration - duration)
        ])
    elif transition_mode == "slide":
        # Slide left/right
        w, h = clip1.size
        clip2_pos = lambda t: (w * (1 - t/duration), 0) if t < duration else (0, 0)
        return CompositeVideoClip([
            clip1.set_start(0),
            clip2.set_start(clip1.duration - duration).set_position(clip2_pos)
        ])
    # ... push, zoom, etc.
    return concatenate_videoclips([clip1, clip2])  # fallback: hard cut
```

### Common Operation 3: Kinetic Text from Word Timestamps
```python
# Source: app/services/video.py (new function)
def create_kinetic_subtitles(sub_maker: SubMaker, video_size: tuple, 
                              style: dict) -> CompositeVideoClip:
    """Create word-level animated subtitles from SubMaker cues."""
    clips = []
    formatter = _build_subtitle_formatter()
    
    for cue in sub_maker.cues:
        word = unescape(cue.content)
        start = cue.start.total_seconds()
        end = cue.end.total_seconds()
        
        txt_clip = TextClip(
            word,
            font=style["font_name"],
            font_size=style["font_size"],
            color=style["text_fore_color"],
            stroke_color=style["stroke_color"],
            stroke_width=style["stroke_width"]
        )
        # Pop animation: scale 1.3 → 1.0 over word duration
        txt_clip = txt_clip.resize(lambda t: 1.3 - 0.3 * (t / (end - start)))
        txt_clip = txt_clip.set_start(start).set_duration(end - start)
        clips.append(txt_clip)
    
    return CompositeVideoClip(clips, size=video_size)
```

### Common Operation 4: Apply LUT via FFmpeg
```python
# Source: app/services/video.py (new function)
def apply_lut_to_clip(input_path: str, output_path: str, lut_path: str) -> bool:
    """Apply .cube LUT to video clip using FFmpeg."""
    ffmpeg_binary = utils.get_ffmpeg_binary()
    cmd = [
        ffmpeg_binary, "-y",
        "-i", input_path,
        "-vf", f"lut3d=file={lut_path}",
        "-c:a", "copy",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hard cuts only | MoviePy transitions (crossfade, slide) | v1.3+ | Professional flow |
| Single subtitle provider | Fallback chain (edge → whisper) | **Phase 1** | 100% subtitle reliability |
| Static subtitles | Kinetic typography (word-pop) | **Phase 1** | Higher engagement |
| Raw footage colors | LUT color grading | **Phase 1** | Brand consistency |
| No branding | Config-driven branding system | **Phase 1** | Marketing-ready output |

**Deprecated/outdated:**
- `subtitle_provider = "edge"` only — must support array `["edge", "whisper"]`
- `--video-transition-mode none` only — must support `crossfade`, `slide`, `push`, `zoom`

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `faster-whisper` CPU `int8` `large-v3` runs in <60s for 60s audio | Standard Stack | If too slow, need smaller model config |
| A2 | MoviePy 2.x `TextClip` supports per-word animation | Pattern 3 | If not, need ASS/FFmpeg drawtext fallback |
| A3 | FFmpeg `lut3d` filter available in bundled binary | Pattern 4 | If not, need PIL-based color grading |
| A4 | Edge TTS `cues` provide word-level timestamps reliably | Pattern 1 | If not, kinetic text needs Whisper timestamps |
| A5 | Config `[branding]` section can be added without breaking existing configs | Standard Stack | If not, need migration script |

---

## Open Questions

1. **Whisper model size default** — `large-v3` (accurate, slow) vs `base`/`small` (fast, less accurate)? 
   - *What we know:* `large-v3` ~1.5 GB, ~4x realtime on CPU int8
   - *What's unclear:* Acceptable latency for marketing pipeline
   - *Recommendation:* Config option `whisper_model_size` default `small`, allow override

2. **Kinetic typography approach** — MoviePy `TextClip` per-word vs FFmpeg `drawtext` with ASS?
   - *What we know:* MoviePy `TextClip` is Python-native but slower; ASS is standard for karaoke
   - *What's unclear:* MoviePy 2.x `TextClip` animation performance
   - *Recommendation:* Start with MoviePy `TextClip` (simpler), benchmark, fallback to ASS if needed

3. **Branding asset formats** — Logo: PNG (transparent)? LUT: `.cube`? Fonts: `.ttf`/`.otf`?
   - *What we know:* MoviePy `ImageClip` supports PNG; FFmpeg `lut3d` needs `.cube`
   - *What's unclear:* User's asset delivery format
   - *Recommendation:* Document required formats in config comments; support PNG/logo, `.cube`/LUT, TTF/fonts

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `faster-whisper` | Whisper fallback | ✅ | latest | — |
| `moviepy` | Transitions, kinetic text, composition | ✅ | 2.x | — |
| `ffmpeg` | LUT, encoding, concat | ✅ | system | — |
| `edge-tts` | Primary TTS + cues | ✅ | 7.x | — |
| `pillow` | Logo overlay, image processing | ✅ | latest | — |
| `numpy` | Frame manipulation | ✅ | latest | — |

**Missing dependencies with no fallback:** none
**Missing dependencies with fallback:** none

---

## Validation Architecture

> `workflow.nyquist_validation` is enabled in `.planning/config.json`

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (project standard) |
| Config file | `pyproject.toml` / `pytest.ini` |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ --tb=short` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FR-1.1 | Whisper fallback triggers on Edge TTS failure | integration | `pytest tests/test_subtitle_fallback.py -x` | ❌ Wave 0 |
| FR-1.2 | Fallback chain config `["edge", "whisper"]` works | unit | `pytest tests/test_config_fallback.py -x` | ❌ Wave 0 |
| FR-2.1 | Branded intro overlay renders | visual | `pytest tests/test_branding.py::test_intro -x` | ❌ Wave 0 |
| FR-2.3 | Logo watermark persists throughout video | visual | `pytest tests/test_branding.py::test_watermark -x` | ❌ Wave 0 |
| FR-2.4 | Transitions (crossfade/slide) between clips | integration | `pytest tests/test_transitions.py -x` | ❌ Wave 0 |
| FR-2.5 | Kinetic typography word-pop animation | visual | `pytest tests/test_kinetic.py -x` | ❌ Wave 0 |
| FR-2.6 | LUT color grading applied | visual | `pytest tests/test_lut.py -x` | ❌ Wave 0 |
| FR-6.1-6.6 | Verification script passes all checks | integration | `python scripts/verify-mpt.py latest` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/ -x -q` (quick)
- **Per wave merge:** `pytest tests/ --tb=short` (full)
- **Phase gate:** Full suite green + 5 consecutive renders pass verification before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_subtitle_fallback.py` — covers FR-1.1, FR-1.2
- [ ] `tests/test_branding.py` — covers FR-2.1, FR-2.2, FR-2.3
- [ ] `tests/test_transitions.py` — covers FR-2.4
- [ ] `tests/test_kinetic.py` — covers FR-2.5
- [ ] `tests/test_lut.py` — covers FR-2.6
- [ ] `tests/test_verification.py` — covers FR-6.x
- [ ] `tests/conftest.py` — shared fixtures (test clips, config, sample scripts)
- [ ] Framework install: `uv sync` — if test deps missing

---

## Security Domain

> `security_enforcement` not explicitly disabled — include.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `pydantic` config models, path validation via `file_security` |
| V6 Cryptography | no | — |

### Known Threat Patterns for Python Video Pipeline

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal in material/logo/LUT paths | Tampering | `file_security.validate_path()` (exists in `app/utils/file_security.py`) |
| FFmpeg command injection | Injection | `subprocess.run()` with list args, no shell=True |
| Malicious subtitle file (ASS script injection) | Injection | Sanitize subtitle text, no ASS rendering |
| Resource exhaustion (huge video files) | DoS | Config limits: max duration, max resolution, max file size |

---

## Sources

### Primary (HIGH confidence)
- [MoneyPrinterTurbo repo](https://github.com/harry0703/MoneyPrinterTurbo) — source code analysis of `voice.py`, `subtitle.py`, `video.py`
- [faster-whisper docs](https://github.com/SYSTRAN/faster-whisper) — model sizes, CPU performance, word timestamps
- [MoviePy 2.x docs](https://moviepy.readthedocs.io/) — TextClip, transitions, CompositeVideoClip
- [Edge TTS 7.x](https://github.com/rany2/edge-tts) — SubMaker, WordBoundary cues

### Secondary (MEDIUM confidence)
- [FFmpeg lut3d filter](https://ffmpeg.org/ffmpeg-filters.html#lut3d) — LUT application
- [Whisper model benchmarks](https://github.com/SYSTRAN/faster-whisper#models) — speed/accuracy tradeoffs

### Tertiary (LOW confidence)
- Community examples of kinetic typography in MoviePy
- Marketing video best practices for branding/transitions

---

*End of RESEARCH.md*