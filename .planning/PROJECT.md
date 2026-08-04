# Project: MoneyPrinterTurbo — SmartSMB Marketing Video Upgrades

**Initialized:** 2026-08-04
**Status:** Active — Phase 1 planning

---

## Vision

Upgrade the working MoneyPrinterTurbo pipeline into a **marketing-grade faceless video factory** for SmartSMB: reliable subtitles, professional visual quality, automated distribution, and systematic script optimization — producing 9:16 shorts ready for TikTok/Reels/Shorts at scale.

---

## Current State (Baseline)

| Component | Status | Notes |
|-----------|--------|-------|
| **Core pipeline** | ✅ Working | Generates 48s 9:16 MP4 with voice, music, stock footage |
| **LLM script gen** | ✅ Working | DeepSeek `deepseek-chat` produces solid marketing copy |
| **Voiceover** | ✅ Working | Edge TTS `en-US-ChristopherNeural` (male, deep, business) |
| **Footage** | ✅ Working | Local Pexels clips (manual curl workaround for downloader bug) |
| **Subtitles** | ❌ Broken | Edge TTS parser chokes on `SMART SMB.AI` periods → no `.srt` |
| **Transitions** | ❌ None | Hard cuts only (`--video-transition-mode none`) |
| **Branding** | ❌ None | No logo, watermark, intro/outro, color grading |
| **Auto-post** | ❌ Not configured | Upload-Post free tier available (10/mo), not set up |
| **Script system** | ⚠️ Ad-hoc | Single prompt, no A/B, no hook library, no templates |

**Test video generated:** `storage/tasks/a4723ff0-ae6c-4fac-953f-cc58c85d23d2/final-1.mp4` (48s, AAC audio, no subs)

---

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **Phase 1 = Subtitle fix + visual quality** | Core video quality must be solid before distribution | — Pending |
| **Visual upgrades: all (branding, transitions, kinetic text, color grading)** | Marketing needs professional polish | — Pending |
| **Auto-post: Upload-Post first → direct APIs later** | Quick win (free tier, no auth complexity), then full control | — Pending |
| **Script system: all (A/B, hooks, templates)** | Systematic content optimization beats one-off prompts | — Pending |
| **Subtitle fix: Whisper fallback for branded terms** | Edge TTS bug is upstream-unfixed; Whisper handles periods robustly | — Pending |

---

## Requirements (Hypotheses)

### Validated
- ✅ Core pipeline renders 9:16 video with voice + music + footage on this machine (16+ GB RAM)
- ✅ DeepSeek `deepseek-chat` produces usable marketing scripts
- ✅ Edge TTS English voice works when no branded periods in script
- ✅ Manual Pexels curl + `--video-source local` is reliable

### Active
- [ ] **Subtitle reliability** — Whisper fallback when Edge TTS fails (branded terms with periods)
- [ ] **Visual polish** — Branded intro/outro, logo watermark, smooth transitions, kinetic typography, color grading
- [ ] **Auto-posting** — Upload-Post integration (TikTok, IG, YT Shorts), then direct APIs
- [ ] **Script system** — Hook library, topic→template mapping, A/B variant generation
- [ ] **Batch/queue** — `--video-count` with topic queue, automated weekly runs
- [ ] **QA/verification** — Automated checks (duration, subs, audio, branding present)

### Out of Scope
- Custom footage generation (Sora/Veo/Gen-3) — budget, not needed for v1
- Real-time avatar/lip-sync — different product category
- Multi-language — English-only for SmartSMB launch
- Live streaming — not short-form marketing

---

## Context & References

- **Repo:** https://github.com/harry0703/MoneyPrinterTurbo (v1.3.3, MIT)
- **Local install:** `C:\Users\mbapt\MoneyPrinterTurbo`
- **Config:** `config.toml` (DeepSeek, Pexels, Edge TTS, English voice set)
- **Footage:** 3 portrait clips in `storage/materials/` + `storage/local_videos/`
- **Skills:** `moneyprinter-turbo-pipeline` (full working recipe + pitfalls)
- **Handoff doc:** `skills/media/moneyprinter-turbo-pipeline/references/handoff.md` (from Misty, Aug 3)
- **Edge TTS bug:** `skills/media/moneyprinter-turbo-pipeline/references/edge-tts-subtitle-bug.md`
- **Verify script:** `skills/media/moneyprinter-turbo-pipeline/scripts/verify-mpt.py`

---

## Success Metrics (Phase 1)

- Video renders with **subtitles 100% of the time** (including `SMART SMB.AI` scripts)
- **Visual quality** passes manual review: branded intro/outro, logo, transitions, kinetic text, color grade
- **Duration** consistently 30–60s
- **Audio** English, AAC, proper volume mix with BGM
- **Verification script** passes all checks automatically

---

*Last updated: 2026-08-04 after initialization*