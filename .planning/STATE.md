# Project State: MoneyPrinterTurbo — SmartSMB Marketing Video Upgrades

**Project:** MoneyPrinterTurbo Upgrades
**Current Phase:** 1 — Subtitle Fix + Visual Polish
**Status:** Planning complete, ready for Phase 1 execution
**Last Updated:** 2026-08-04

---

## Phase Progress

| Phase | Name | Status | Started | Completed |
|-------|------|--------|---------|-----------|
| 1 | Subtitle Fix + Visual Polish | **Planning Done** | 2026-08-04 | — |
| 2 | Auto-Posting (Upload-Post) | Not Started | — | — |
| 3 | Script System | Not Started | — | — |
| 4 | Automation & Queue | Not Started | — | — |

---

## Phase 1 Plan Status

| Plan | Title | Status | Notes |
|------|-------|--------|-------|
| P1.1 | Whisper Subtitle Fallback | **Next** | Core fix for Edge TTS bug |
| P1.2 | Branding System | Pending | Logo, colors, fonts, LUT, intro/outro, watermark |
| P1.3 | Transition Engine | Pending | Crossfade, slide, push, zoom transitions |
| P1.4 | Kinetic Typography | Pending | Word-level animation synced to voice |
| P1.5 | Color Grading Pipeline | Pending | LUT/color grade applied to all clips |
| P1.6 | Verification & QA | Pending | Extended verify-mpt.py |
| P1.7 | Integration Test | Pending | 5 consecutive passing renders |

---

## Current Context

**Working Directory:** `C:\Users\mbapt\MoneyPrinterTurbo`
**Config:** `config.toml` (DeepSeek, Pexels, Edge TTS, English voice)
**Footage:** `storage/materials/` (3 clips) + `storage/local_videos/` (3 clips)
**Test Task:** `storage/tasks/a4723ff0-ae6c-4fac-953f-cc58c85d23d2/` — 48s video, no subs (Edge TTS bug)
**Verification Script:** `skills/media/moneyprinter-turbo-pipeline/scripts/verify-mpt.py`

---

## Key Files to Modify (Phase 1)

| File | Purpose | Changes Needed |
|------|---------|----------------|
| `app/services/voice.py` | Subtitle generation | Add Whisper fallback chain, fix Edge TTS cue parser |
| `app/services/video.py` | Video composition | Add transitions, branding overlays, kinetic typography, color grading |
| `config.toml` | Configuration | Add `[branding]` section, subtitle fallback config |
| `cli.py` | CLI entry | New flags for transitions, branding, script variants |
| `scripts/verify-mpt.py` | QA verification | Add branding, transition, kinetic text, color checks |

---

## Research Needed (Phase 1)

- [ ] MoviePy transition capabilities vs FFmpeg filter_complex
- [ ] Whisper integration patterns (faster-whisper vs openai-whisper)
- [ ] Kinetic typography implementation in MoviePy (TextClip animation)
- [ ] LUT application in MoviePy/FFmpeg
- [ ] Branding asset specs (logo format, size, safe zones)

---

## Decisions Log

| Date | Decision | Context |
|------|----------|---------|
| 2026-08-04 | Phase 1 = Subtitle fix + visual quality | Core video quality before distribution |
| 2026-08-04 | Visual: all (branding, transitions, kinetic, color) | Marketing needs professional polish |
| 2026-08-04 | Auto-post: Upload-Post first → direct APIs | Quick win, then full control |
| 2026-08-04 | Script system: all (A/B, hooks, templates) | Systematic optimization |
| 2026-08-04 | Subtitle fix: Whisper fallback | Edge TTS bug upstream-unfixed |

---

## Blockers / Open Questions

| Issue | Status | Owner |
|-------|--------|-------|
| MoviePy transition reliability | Open | — |
| Whisper CPU performance (large-v3 int8) | Open | — |
| Kinetic typography approach (MoviePy vs FFmpeg drawtext) | Open | — |
| Branding assets (logo, LUT, fonts) — need from Malik | Open | Malik |

---

## Next Action

**Start Plan P1.1: Whisper Subtitle Fallback**
1. Research Whisper integration in MoneyPrinterTurbo codebase
2. Add fallback chain logic to `app/services/voice.py`
3. Test with `SMART SMB.AI` script (periods in brand name)
4. Verify `.srt` generated with correct timing

---

*State updates after each plan completion. Run `/gsd-progress` to advance.*