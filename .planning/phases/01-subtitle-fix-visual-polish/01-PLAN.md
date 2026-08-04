---
phase: 01-subtitle-fix-visual-polish
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - app/services/voice.py
  - app/services/subtitle.py
  - app/services/video.py
  - config.toml
  - cli.py
autonomous: true
requirements:
  - FR-1.1
  - FR-1.2
  - FR-1.3
  - FR-1.4
  - FR-1.5
  - FR-2.1
  - FR-2.2
  - FR-2.3
  - FR-2.4
  - FR-2.5
  - FR-2.6
  - FR-2.7
  - FR-6.1
  - FR-6.2
  - FR-6.3
  - FR-6.4
  - FR-6.5
  - FR-6.6
user_setup: []
must_haves:
  truths:
    - Subtitle fallback chain (edge → whisper) works for scripts with branded periods
    - Branded intro/outro overlays render on every video
    - Logo watermark persists throughout video
    - Configurable transitions (crossfade/slide/push/zoom) replace hard cuts
    - Kinetic typography animates words in sync with voiceover
    - Color grading/LUT applied consistently across all clips
    - Verification script catches all quality issues automatically
  artifacts:
    - app/services/voice.py (subtitle fallback logic)
    - app/services/subtitle.py (Whisper integration unchanged)
    - app/services/video.py (branding, transitions, kinetic text, LUT)
    - config.toml ([branding] section, subtitle_provider array)
    - cli.py (new flags for transitions, branding, kinetic)
    - .planning/phases/01-subtitle-fix-visual-polish/01-SUMMARY.md
  key_links:
    - voice.py → subtitle.py fallback trigger
    - video.py → config.toml branding assets
    - cli.py → video.py new parameters
    - verify-mpt.py → all new quality checks

---

<objective>
Implement the core subtitle reliability fix and visual polish foundation for marketing-quality videos.

Purpose: The current pipeline fails subtitles on branded terms with periods (SMART SMB.AI) and produces only hard-cut videos with no branding. This plan adds the Whisper fallback chain, branding system, transition engine, kinetic typography, and color grading pipeline — the minimum for marketing-ready output.

Output: Modified voice.py (fallback), video.py (branding/transitions/kinetic/LUT), config.toml ([branding]), cli.py (new flags), extended verify-mpt.py.
</objective>

---

<execution_context>
@$HOME/AppData/Local/hermes/profiles/personal_assistant_klaus7/gsd-core/workflows/execute-plan.md
@$HOME/AppData/Local/hermes/profiles/personal_assistant_klaus7/gsd-core/templates/summary.md
</execution_context>

---

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-subtitle-fix-visual-polish/01-RESEARCH.md
@app/services/voice.py
@app/services/subtitle.py
@app/services/video.py
@config.toml
@cli.py
</context>

---

<tasks>

<task type="auto">
  <name>Task 1: Subtitle Fallback Chain (edge → whisper) in voice.py
  </name>
  <files>app/services/voice.py</files>
  <action>
Add a subtitle fallback mechanism to `create_subtitle()` or a new wrapper function. When Edge TTS cues fail to match script lines (len(sub_items) != len(script_lines)), automatically invoke Whisper via `app.services.subtitle.create()`.

Implementation steps per RESEARCH.md Pattern 1:
1. Add new function `generate_subtitle_with_fallback(text, voice_name, voice_rate, audio_file, subtitle_file, voice_volume)` in voice.py
2. Try Edge TTS first: call existing `tts()` → `create_subtitle()` 
3. Check if subtitle file exists and has content (>0 bytes, correct line count)
4. If failed, log warning and call `from app.services.subtitle import create as whisper_create`
5. Return True/False for success

Key integration point: The existing `create_subtitle()` at line 1677 returns early when `len(sub_items) != len(script_lines)` (line 1694-1698). This is the trigger for fallback.

Config support: Add `subtitle_provider` as array in config.toml (e.g., `["edge", "whisper"]`) and read in voice.py. Default to `["edge", "whisper"]`.

Preserve styling: Whisper-generated subtitles must use same font, color, position, stroke settings as Edge TTS (already handled by subtitle.py create() which writes SRT; styling applied in video.py during composition).
  </action>
  <verify>
pytest tests/test_subtitle_fallback.py -x
  </verify>
  <done>
Edge TTS subtitle failure on "SMART SMB.AI" script triggers Whisper fallback automatically; subtitle.srt generated with correct timing; styling preserved
  </done>
</task>

<task type="auto">
  <name>Task 2: Branding System in video.py and config.toml
  </name>
  <files>app/services/video.py, config.toml</files>
  <action>
Implement the branding system per RESEARCH.md Pattern 1 and FR-2.1 through FR-2.3, FR-2.7.

In config.toml, add new `[branding]` section:
```toml
[branding]
# Logo overlay (PNG with transparency)
logo_path = "storage/branding/logo.png"
logo_position = "top-right"  # top-left, top-right, bottom-left, bottom-right
logo_opacity = 0.8
logo_scale = 0.15  # fraction of video width

# Intro overlay (2-3 seconds)
intro_enabled = true
intro_duration = 2.5
intro_logo_path = "storage/branding/intro_logo.png"
intro_text = "SmartSMB"
intro_tagline = "Never Miss a Lead"
intro_animation = "fade-in"  # fade-in, slide-up, zoom-in
intro_bg_color = "#0F172A"  # dark navy
intro_text_color = "#FFFFFF"
intro_accent_color = "#00D4AA"  # teal

# Outro overlay (2-3 seconds)
outro_enabled = true
outro_duration = 3.0
outro_logo_path = "storage/branding/outro_logo.png"
outro_text = "Book a Free Lead Leak Audit"
outro_cta = "smartsmb.ai"
outro_animation = "fade-out"
outro_bg_color = "#0F172A"
outro_text_color = "#FFFFFF"

# Color grading
lut_enabled = true
lut_path = "storage/branding/brand_lut.cube"
lut_intensity = 1.0  # 0.0-1.0
```

In video.py:
1. Add `BrandingConfig` dataclass / Pydantic model to parse `[branding]` section
2. Add `apply_branding()` function that:
   - Loads logo/image assets from configured paths (validate with file_security)
   - Creates intro clip: ColorClip background + ImageClip(logo) + TextClip(text/tagline) with animation
   - Creates outro clip: similar with CTA
   - Creates watermark: ImageClip(logo) with opacity, positioned persistently
3. Modify `generate_video()` to:
   - Call `apply_branding()` to get intro/outro/watermark clips
   - Prepend intro, append outro to clip sequence
   - Overlay watermark on all clips (CompositeVideoClip)
   - Apply LUT via FFmpeg `lut3d` filter on each source clip before composition (or on final composite)
4. Add helper `apply_lut_to_clip(input_path, output_path, lut_path)` using FFmpeg subprocess (RESEARCH.md Pattern 4)

Asset validation: Check files exist, are valid PNG/images, LUT is valid .cube format. Log warnings if missing but don't fail render.
  </action>
  <verify>
pytest tests/test_branding.py -x
  </verify>
  <done>
Branding system loads config, renders intro/outro/watermark on test video; LUT applied; assets validated
  </done>
</task>

<task type="auto">
  <name>Task 3: Transition Engine in video.py
  </name>
  <files>app/services/video.py</files>
  <action>
Implement configurable transitions between material clips per RESEARCH.md Pattern 2 and FR-2.4.

Extend `VideoTransitionMode` enum in `app/models/schema.py` (or add to video.py):
- `none` (existing, hard cut)
- `crossfade` (1s default overlap with audio fade)
- `slide-left` / `slide-right` / `slide-up` / `slide-down`
- `push` (new clip pushes old clip out)
- `zoom` (zoom in/out transition)

In config.toml, add:
```toml
[branding]
# ... existing ...
transition_mode = "crossfade"  # crossfade, slide-left, slide-right, push, zoom, none
transition_duration = 1.0  # seconds
```

In video.py `generate_video()`:
1. Read transition config
2. Replace clip concatenation logic with transition application
3. For each adjacent clip pair, call `apply_transition(clip1, clip2, mode, duration)` (RESEARCH.md Pattern 2)
4. Use MoviePy `CompositeVideoClip` with overlapping clips for visual transitions
5. Use `afx.audio_fadein/out` for audio crossfade
6. For slide/push/zoom: use position functions with time-based interpolation
7. Fallback to hard cut (`concatenate_videoclips`) if transition fails

Key implementation detail: The existing `concat_video_clips_with_ffmpeg()` at line 332 does single-pass FFmpeg concat. Transitions require MoviePy composition first, then FFmpeg encode. Flow:
- Build composite with transitions in MoviePy
- Write intermediate composite to temp file
- FFmpeg encode final with codec fallback (existing `_write_videofile_with_codec_fallback`)

Memory consideration: Limit transition duration to 1-2s max; process clips in waves if needed.
  </action>
  <verify>
pytest tests/test_transitions.py -x
  </verify>
  <done>
Crossfade, slide, push, zoom transitions work between test clips; audio crossfade syncs; fallback to hard cut on failure
  </done>
</task>

<task type="auto">
  <name>Task 4: Kinetic Typography in video.py
  </name>
  <files>app/services/video.py</files>
  <action>
Implement word-level subtitle animation synced to TTS timestamps per RESEARCH.md Pattern 3 and FR-2.5.

In config.toml, extend `[branding]`:
```toml
[branding]
# ... existing ...
kinetic_enabled = true
kinetic_style = "pop"  # pop, slide, fade, scale
kinetic_pop_scale = 1.3  # max scale for pop animation
kinetic_slide_distance = 50  # pixels for slide animation
```

In video.py:
1. Add `create_kinetic_subtitles(sub_maker, video_size, style_config)` function (RESEARCH.md Pattern 3)
2. Extract word-level timestamps from:
   - Edge TTS: `sub_maker.cues` (WordBoundary events) — already available
   - Whisper: `word_timestamps=True` in subtitle.py create() — already returns word timestamps
3. For each word cue, create `TextClip` with configured style (font, size, color, stroke from existing subtitle config)
4. Apply animation based on `kinetic_style`:
   - `pop`: scale 1.3 → 1.0 over word duration
   - `slide`: translate X from -distance to 0
   - `fade`: opacity 0 → 1
   - `scale`: subtle scale pulse
5. Position subtitles per existing `subtitle_position` config (bottom, top, center, custom)
6. Return `CompositeVideoClip` of all word clips
7. In `generate_video()`, when `kinetic_enabled` and `subtitle_enabled`:
   - Call `create_kinetic_subtitles()` instead of static `SubtitlesClip`
   - Overlay on composite

Sync validation: After render, verify word timing matches audio using ffprobe frame timestamps vs cue timestamps.
  </action>
  <verify>
pytest tests/test_kinetic.py -x
  </verify>
  <done>
Word-pop kinetic subtitles render in sync with voiceover; style config respected; position configurable
  </done>
</task>

<task type="auto">
  <name>Task 5: Color Grading / LUT Pipeline in video.py
  </name>
  <files>app/services/video.py</files>
  <action>
Implement LUT color grading per RESEARCH.md Pattern 4 and FR-2.6.

Config already added in Task 2 (`lut_enabled`, `lut_path`, `lut_intensity`).

In video.py:
1. Add `apply_lut_to_clip(input_path, output_path, lut_path, intensity)` using FFmpeg `lut3d` filter
2. For `intensity < 1.0`, blend original + LUT using FFmpeg `blend` filter:
   ```bash
   ffmpeg -i input -vf "lut3d=file=lut.cube,blend=all_mode=normal:all_opacity=0.5" output
   ```
3. In `generate_video()`, before clip composition:
   - For each source material clip, apply LUT to temp file
   - Use LUT-processed clips for composition
   - Clean up temp LUT files after
4. Alternative: Apply LUT to final composite (single pass) — simpler but affects intro/outro/branding too. Decision: apply to source clips only, keep branding clean.

Validation: Render test video with known LUT; verify color shift with ffprobe/visual inspection.
  </action>
  <verify>
pytest tests/test_lut.py -x
  </verify>
  <done>
LUT applied to source clips; intensity blending works; branding clips unaffected; temp files cleaned
  </done>
</task>

<task type="auto">
  <name>Task 6: CLI Flags and Config Integration
  </name>
  <files>cli.py, config.toml</files>
  <action>
Wire new features through CLI and config.toml.

In cli.py:
1. Add new CLI arguments:
   - `--subtitle-provider` (array: edge,whisper) — overrides config
   - `--transition-mode` (crossfade/slide-left/slide-right/push/zoom/none) — overrides config
   - `--transition-duration` (float) — overrides config
   - `--kinetic-enabled` / `--no-kinetic` — overrides config
   - `--kinetic-style` (pop/slide/fade/scale) — overrides config
   - `--lut-enabled` / `--no-lut` — overrides config
   - `--intro-enabled` / `--no-intro` — overrides config
   - `--outro-enabled` / `--no-outro` — overrides config
   - `--watermark-enabled` / `--no-watermark` — overrides config
2. Pass all new params to `VideoParams` schema and `generate_video()`

In config.toml, ensure all new keys documented with comments (see Tasks 2-5).

Backward compatibility: All new flags optional; defaults from config.toml; config.toml defaults sensible for marketing (transition_mode="crossfade", kinetic_enabled=true, lut_enabled=true, intro/outro/watermark enabled).
  </action>
  <verify>
python cli.py --help | grep -E "subtitle-provider|transition|kinetic|lut|intro|outro|watermark"
  </verify>
  <done>
All new CLI flags appear in help; override config correctly; passed to generate_video()
  </done>
</task>

<task type="auto">
  <name>Task 7: Extended Verification Script
  </name>
  <files>scripts/verify-mpt.py</files>
  <action>
Extend `scripts/verify-mpt.py` to validate all new quality gates per FR-6.1 through FR-6.6.

Add new verification functions:
1. `verify_branding_present(task_dir)` — check intro/outro frames exist (sample first/last 3s), watermark detected (pixel sampling at configured position), logo colors present
2. `verify_transitions(task_dir)` — analyze frame differences at clip boundaries; confirm no hard cuts (frame diff > threshold indicates transition)
3. `verify_kinetic_subtitles(task_dir)` — check subtitle.srt has word-level entries (more entries than script sentences), timing matches audio
4. `verify_lut_applied(task_dir)` — sample frames before/after LUT; verify color shift (statistical: mean RGB difference > threshold)
5. `verify_subtitle_fallback(task_dir)` — confirm subtitle.srt exists even for scripts with periods in brand names

Update `main()` to run all checks and return non-zero on any failure.

Add config verification for new `[branding]` section keys.
  </action>
  <verify>
python scripts/verify-mpt.py latest
  </verify>
  <done>
Verification script passes on test render with SMART SMB.AI script; all 6 new checks pass; exits non-zero on any failure
  </done>
</task>

</tasks>

---

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| User config → video pipeline | `config.toml` paths (logo, LUT, fonts) validated before use |
| External material clips → composition | Pexels/local clips validated for resolution, duration |
| Subtitle text → rendering | Text sanitized in `_format_text()` (removes markdown, brackets) |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01-01 | Tampering | Logo/LUT path traversal | high | mitigate | `file_security.validate_path()` on all asset paths |
| T-01-02 | Injection | FFmpeg command args | high | mitigate | `subprocess.run(list_args)`, no shell=True |
| T-01-03 | Tampering | Malicious subtitle content | medium | mitigate | Sanitize in `_format_text()`, no ASS rendering |
| T-01-04 | DoS | Huge video files OOM | medium | mitigate | Config limits: max_duration, max_resolution, max_file_size |
| T-01-SC | Tampering | npm/pip installs | high | mitigate | No new packages; all deps verified in RESEARCH.md |

</threat_model>

---

<verification>
Overall phase checks:
1. Run 5 consecutive test renders with `SMART SMB.AI` scripts (periods in brand name)
2. Each render must pass `python scripts/verify-mpt.py latest` (exit code 0)
3. Manual visual review: intro/outro present, watermark visible, transitions smooth, kinetic text synced, color grade consistent
4. Render time ≤ 5 min, RAM ≤ 12 GB per render
5. All CLI flags functional and override config
</verification>

---

<success_criteria>
- [ ] All 7 tasks implemented and verified
- [ ] 5/5 consecutive test renders pass automated verification
- [ ] Subtitles generated 100% of time including branded periods
- [ ] Visual review: marketing-grade quality (intro/outro, watermark, transitions, kinetic, LUT)
- [ ] Config documents all new settings in config.toml
- [ ] Render time ≤ 5 min, RAM ≤ 12 GB
- [ ] .planning/phases/01-subtitle-fix-visual-polish/01-SUMMARY.md created
</success_criteria>

---

<output>
Create `.planning/phases/01-subtitle-fix-visual-polish/01-SUMMARY.md` when done
</output>