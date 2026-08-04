# Roadmap: MoneyPrinterTurbo — SmartSMB Marketing Video Upgrades

**Project:** MoneyPrinterTurbo Upgrades
**Version:** 1.0
**Date:** 2026-08-04

---

## Phase Overview

| Phase | Name | Focus | Est. Effort | Dependencies |
|-------|------|-------|-------------|--------------|
| 1 | **Subtitle Fix + Visual Polish** | Core video quality: reliable subs + marketing-grade visuals | 3-5 days | None |
| 2 | **Auto-Posting (Upload-Post)** | Distribution to TikTok/IG/YT Shorts | 2-3 days | Phase 1 |
| 3 | **Script System** | Hooks, templates, A/B variants | 3-4 days | Phase 1 |
| 4 | **Automation & Queue** | Weekly cron, topic queue, Telegram delivery | 2-3 days | Phases 1-3 |

---

## Phase 1: Subtitle Fix + Visual Polish (Current)

**Goal:** Every render produces a marketing-ready 9:16 video with subtitles, branding, transitions, kinetic typography, and color grading — no manual fixes.

### Plans

| Plan | Title | Scope |
|------|-------|-------|
| P1.1 | **Whisper Subtitle Fallback** | Add `subtitle_provider` fallback chain (edge → whisper), auto-download model, preserve styling |
| P1.2 | **Branding System** | `[branding]` config section: logo, colors, fonts, LUT, intro/outro templates, watermark |
| P1.3 | **Transition Engine** | Replace hard cuts with configurable transitions (crossfade, slide, push, zoom) |
| P1.4 | **Kinetic Typography** | Word-level subtitle animation synced to Edge TTS/Whisper timestamps |
| P1.5 | **Color Grading Pipeline** | Apply LUT/color grade to all clips before composition |
| P1.6 | **Verification & QA** | Extend `verify-mpt.py` with branding, transition, kinetic text, color checks |
| P1.7 | **Integration Test** | 5 consecutive renders with `SMART SMB.AI` scripts — all pass verification |

### Acceptance Criteria (Phase 1 Gate)

- [ ] All 5 test renders pass automated verification (duration, audio, subs, branding, transitions, color)
- [ ] Subtitles generated 100% of the time (including branded terms with periods)
- [ ] Visual review: intro/outro, watermark, transitions, kinetic text, color grade look professional
- [ ] Config documents all new settings in `config.toml` and `README.md`
- [ ] Render time ≤ 5 min, RAM ≤ 12 GB

---

## Phase 2: Auto-Posting (Upload-Post)

**Goal:** One-click publish to TikTok, Instagram Reels, YouTube Shorts via Upload-Post free tier.

### Plans

| Plan | Title | Scope |
|------|-------|-------|
| P2.1 | **Upload-Post Config & Auth** | `upload_post_api_key`, `platforms`, `youtube_privacy_status`, `auto_upload` in config |
| P2.2 | **Uploader Module** | `app/services/uploader.py` with abstract `VideoUploader` base + `UploadPostUploader` impl |
| P2.3 | **Per-Platform Metadata** | Platform-specific titles, descriptions, hashtags from script + topic config |
| P2.4 | **Upload Status Tracking** | Log results per platform in task dir (`upload_status.json`) |
| P2.5 | **Direct API Interface** | Define `TikTokUploader`, `InstagramUploader`, `YouTubeUploader` stubs for future migration |
| P2.6 | **Integration Test** | 3 test posts to each platform (TikTok, IG, YT) — all successful |

### Acceptance Criteria (Phase 2 Gate)

- [ ] Upload-Post free tier account active, API key configured
- [ ] Auto-upload works: render → post to all 3 platforms without manual steps
- [ ] Per-platform metadata looks native (hashtags, formatting, privacy)
- [ ] Upload status logged, failures alerted
- [ ] Direct API interface defined and documented for Phase 3+ migration

---

## Phase 3: Script System

**Goal:** Systematic content generation with hook library, topic templates, and A/B testing.

### Plans

| Plan | Title | Scope |
|------|-------|-------|
| P3.1 | **Hook Library** | `config/hooks.json` — 20+ hooks categorized: problem, stat, question, story, bold claim, pattern interrupt |
| P3.2 | **Topic → Template Mapping** | `config/templates.yaml` — topic category → script structure (beats, tone, CTA, hook types) |
| P3.3 | **Variant Generator** | `--script-variants N` flag: generates N scripts from same topic using different hooks/angles |
| P3.4 | **Variant Metadata** | Each variant tagged: `hook_type`, `angle`, `target_emotion`, `template_id` in `script.json` |
| P3.5 | **Performance Tracking Schema** | `tracking/variants.csv` — variant_id, topic, hook, template, views, likes, comments, shares, conversions |
| P3.6 | **A/B Test Run** | Generate 3 variants from one topic, render all, verify, deliver to Telegram for review |

### Acceptance Criteria (Phase 3 Gate)

- [ ] Hook library has ≥ 20 hooks across 5+ categories
- [ ] Template mapping covers ≥ 5 SmartSMB categories (missed calls, lead leak, BDC, CRM, pricing)
- [ ] `--script-variants 3` produces 3 distinct scripts with different hooks/angles
- [ ] Variant metadata complete and queryable
- [ ] Tracking schema ready for manual entry (CSV/JSON)

---

## Phase 4: Automation & Queue

**Goal:** Hands-off weekly content production — queue topic, get videos in Telegram.

### Plans

| Plan | Title | Scope |
|------|-------|-------|
| P4.1 | **Topic Queue** | `config/topics.yaml` — list of topics with priority, category, scheduled week, variants count |
| P4.2 | **Weekly Cron Job** | Runs Monday 9 AM: picks next topic, generates `--video-count N` variants, verifies |
| P4.3 | **Best Variant Selection** | Heuristic: shortest duration in range, all QA checks pass, highest hook engagement potential |
| P4.4 | **Telegram Delivery** | Best variant (or all) sent to Telegram with caption: topic, variant info, CTA |
| P4.5 | **Cleanup Policy** | Delete task dirs > 30 days old; keep final MP4s in `storage/archive/` |
| P4.6 | **Monitoring & Alerts** | Cron failure → Telegram alert; disk space warning; API quota warning |

### Acceptance Criteria (Phase 4 Gate)

- [ ] Cron runs 2 consecutive weeks unattended
- [ ] Videos delivered to Telegram automatically
- [ ] Cleanup executes, disk usage stable
- [ ] Failure alerts work (test by breaking something)
- [ ] Topic queue manages 4+ weeks of content

---

## Cross-Phase Technical Debt

| Item | Phase | Notes |
|------|-------|-------|
| MoviePy → FFmpeg direct for transitions | 1 | MoviePy transition support is limited; may need FFmpeg filter complex |
| Whisper model size config | 1 | Allow `base`/`small`/`medium`/`large-v3` for speed/accuracy tradeoff |
| Config validation schema | 1 | Pydantic model for `config.toml` + YAML files |
| Structured logging | 1 | JSON logs per task for debugging/analytics |
| Git tracking for planning docs | All | Commit `.planning/` to repo (configurable) |

---

## Milestone Checkpoints

| Milestone | Target Date | Criteria |
|-----------|-------------|----------|
| **M1: Marketing-Ready Video** | 2026-08-09 | Phase 1 complete — 5/5 test renders pass |
| **M2: Auto-Distribution** | 2026-08-13 | Phase 2 complete — 3 platforms posting automatically |
| **M3: Content System** | 2026-08-18 | Phase 3 complete — A/B test run delivered |
| **M4: Hands-Off Factory** | 2026-08-22 | Phase 4 complete — 2 weeks unattended runs |

---

## Resource Allocation

| Resource | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|----------|---------|---------|---------|---------|
| Dev time (days) | 3-5 | 2-3 | 3-4 | 2-3 |
| Tokens (est.) | High (research + code) | Medium | High (prompt engineering) | Low |
| External deps | Whisper model (1.5 GB) | Upload-Post account | None | Cron/Telegram |

---

## Risk Register (Top 5)

| Risk | Phase | Probability | Impact | Mitigation |
|------|-------|-------------|--------|------------|
| MoviePy transition bugs | 1 | Medium | High | Early spike; FFmpeg fallback |
| Whisper CPU too slow | 1 | High | Medium | Quantized models; cache; async |
| Upload-Post API changes | 2 | Low | High | Abstract interface; version pin |
| Hook/template quality | 3 | Medium | High | Curate from proven marketing frameworks |
| Cron reliability | 4 | Medium | Medium | Health checks; alerts; manual override |

---

*Last updated: 2026-08-04*