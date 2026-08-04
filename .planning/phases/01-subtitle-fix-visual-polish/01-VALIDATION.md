# Validation Architecture — Phase 1: Subtitle Fix + Visual Polish

**Generated:** 2026-08-04
**Phase:** 01-subtitle-fix-visual-polish
**Nyquist Validation:** Enabled

---

## Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (project standard) |
| Config file | `pyproject.toml` / `pytest.ini` |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ --tb=short` |

---

## Phase Requirements → Test Map

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

---

## Sampling Rate

- **Per task commit:** `pytest tests/ -x -q` (quick)
- **Per wave merge:** `pytest tests/ --tb=short` (full)
- **Phase gate:** Full suite green + 5 consecutive renders pass verification before `/gsd-verify-work`

---

## Wave 0 Gaps

- [ ] `tests/test_subtitle_fallback.py` — covers FR-1.1, FR-1.2
- [ ] `tests/test_branding.py` — covers FR-2.1, FR-2.2, FR-2.3
- [ ] `tests/test_transitions.py` — covers FR-2.4
- [ ] `tests/test_kinetic.py` — covers FR-2.5
- [ ] `tests/test_lut.py` — covers FR-2.6
- [ ] `tests/test_verification.py` — covers FR-6.x
- [ ] `tests/conftest.py` — shared fixtures (test clips, config, sample scripts)
- [ ] Framework install: `uv sync` — if test deps missing

---

## Verification Gates

### Gate 1: Subtitle Fallback (FR-1.1, FR-1.2)
**Command:** `pytest tests/test_subtitle_fallback.py -x`
**Pass criteria:** Test renders script with "SMART SMB.AI" → subtitle.srt generated via Whisper fallback

### Gate 2: Branding System (FR-2.1, FR-2.2, FR-2.3)
**Command:** `pytest tests/test_branding.py -x`
**Pass criteria:** Intro/outro frames present, watermark detected at configured position

### Gate 3: Transitions (FR-2.4)
**Command:** `pytest tests/test_transitions.py -x`
**Pass criteria:** Frame diff analysis shows smooth transitions (no hard cuts) at clip boundaries

### Gate 4: Kinetic Typography (FR-2.5)
**Command:** `pytest tests/test_kinetic.py -x`
**Pass criteria:** Subtitle entries exceed script sentence count (word-level), timing syncs with audio

### Gate 5: LUT Color Grading (FR-2.6)
**Command:** `pytest tests/test_lut.py -x`
**Pass criteria:** Statistical color shift detected between raw and LUT-processed frames

### Gate 6: Full Verification (FR-6.1-6.6)
**Command:** `python scripts/verify-mpt.py latest`
**Pass criteria:** Exit code 0, all checks pass (duration, audio, subs, branding, transitions, kinetic, color)

---

## Acceptance Criteria for Phase Completion

- [ ] All 5 consecutive test renders with "SMART SMB.AI" scripts pass `verify-mpt.py`
- [ ] Subtitles generated 100% of the time (including branded terms with periods)
- [ ] Visual review: intro/outro, watermark, transitions, kinetic text, color grade professional
- [ ] Render time ≤ 5 min, RAM ≤ 12 GB per render
- [ ] All new CLI flags functional and override config.toml
- [ ] Config documents all new settings in config.toml

---

*End of VALIDATION.md*