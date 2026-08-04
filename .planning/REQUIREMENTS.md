# Requirements: MoneyPrinterTurbo — SmartSMB Marketing Video Upgrades

**Project:** MoneyPrinterTurbo Upgrades
**Version:** 1.0
**Date:** 2026-08-04

---

## Functional Requirements

### FR-1: Subtitle Reliability (Phase 1)
**Priority:** Critical
**Description:** Videos must always have subtitles, even when script contains branded terms with periods (`SMART SMB.AI`, `B.D.C.`, etc.)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-1.1 | Whisper subtitle provider as fallback | When `subtitle_provider = "edge"` fails, auto-fallback to `whisper` and generate `.srt` |
| FR-1.2 | Configurable fallback chain | `subtitle_provider = ["edge", "whisper"]` tries edge first, then whisper |
| FR-1.3 | Whisper model auto-download | `large-v3` model downloads on first use (CPU int8, ~1.5 GB) |
| FR-1.4 | Subtitle styling preserved | Font, color, position, stroke settings apply to Whisper-generated subs too |
| FR-1.5 | No manual intervention | Pipeline completes end-to-end without stopping for subtitle failures |

### FR-2: Visual Polish (Phase 1)
**Priority:** Critical
**Description:** Marketing-grade visual quality with branding, transitions, and professional effects

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-2.1 | Branded intro overlay | 2-3s intro with SmartSMB logo, tagline, animated entrance |
| FR-2.2 | Branded outro overlay | 2-3s outro with CTA (website, "Book Free Audit"), animated exit |
| FR-2.3 | Logo watermark | Persistent logo in corner (configurable position/opacity) throughout video |
| FR-2.4 | Smooth transitions | Crossfade/slide/push transitions between clips (configurable per project) |
| FR-2.5 | Kinetic typography | Subtitle words animate in sync with voiceover (pop, slide, fade per word) |
| FR-2.6 | Color grading / LUT | Apply consistent LUT/color grade across all clips for brand look |
| FR-2.7 | Configurable branding assets | Logo, colors, fonts, LUT file loaded from `config.toml` `[branding]` section |

### FR-3: Auto-Posting (Phase 2)
**Priority:** High
**Description:** One-click distribution to TikTok, Instagram Reels, YouTube Shorts

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-3.1 | Upload-Post integration | Configure `upload_post_api_key`, `platforms = ["tiktok", "instagram", "youtube"]` |
| FR-3.2 | Auto-upload on success | `upload_post_auto_upload = true` posts immediately after render |
| FR-3.3 | Platform-specific metadata | Per-platform titles, descriptions, hashtags, privacy status |
| FR-3.4 | YouTube privacy default | `unlisted` for review, flip to `public` after approval |
| FR-3.5 | Direct API migration path | Modular uploader interface; swap Upload-Post → direct TikTok/IG/YT APIs later |
| FR-3.6 | Upload status tracking | Log success/failure per platform with timestamps in task directory |

### FR-4: Script System (Phase 3)
**Priority:** High
**Description:** Systematic script generation with hooks, templates, and A/B testing

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-4.1 | Hook library | JSON file of proven opening formulas (problem, stat, question, story, bold claim) |
| FR-4.2 | Topic → template mapping | YAML config: topic category → script structure (beats, tone, CTA style) |
| FR-4.3 | A/B variant generation | `--video-count N` with `--script-variants` generates N scripts from same topic using different hooks/angles |
| FR-4.4 | Variant metadata | Each variant tagged with hook type, angle, target emotion for performance tracking |
| FR-4.5 | Performance tracking schema | CSV/JSON log: variant_id, topic, hook, views, engagement, conversion (manual entry initially) |

### FR-5: Batch/Queue & Automation (Phase 4)
**Priority:** Medium
**Description:** Hands-off weekly content production

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-5.1 | Topic queue file | `topics.yaml` with list of topics, priority, scheduled week |
| FR-5.2 | Weekly cron job | Runs every Monday, picks next topic, generates `--video-count 3` variants |
| FR-5.3 | Auto-deliver to Telegram | Best variant (or all) sent to Telegram chat with caption |
| FR-5.4 | Cleanup policy | Auto-delete task dirs older than 30 days, keep only final MP4s |

### FR-6: QA & Verification (Phase 1)
**Priority:** Critical
**Description:** Automated quality gates every render

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-6.1 | Duration check | 30–60s (configurable min/max) |
| FR-6.2 | Audio codec check | AAC, 44.1kHz or 48kHz |
| FR-6.3 | Subtitle presence check | `.srt` exists, >0 entries, timing matches audio |
| FR-6.4 | Branding presence check | Logo watermark detected (pixel sample), intro/outro frames present |
| FR-6.5 | Transition check | No hard cuts (frame diff analysis between clips) |
| FR-6.6 | Exit codes | Non-zero on any failure; CI/CD friendly |

---

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Render time per video | ≤ 5 minutes (16 GB RAM, no GPU) |
| NFR-2 | RAM usage | ≤ 12 GB peak |
| NFR-3 | Disk per task | ≤ 500 MB (cleanup after verify) |
| NFR-4 | Reliability | 95%+ unattended runs complete successfully |
| NFR-5 | Config-driven | All behavior via `config.toml` / YAML files, no code edits for new topics |

---

## Definition of Done (Per Phase)

**Phase 1 (Subtitle + Visual):**
- [ ] All FR-1.x and FR-2.x acceptance criteria met
- [ ] FR-6.x verification script passes on 5 consecutive test renders with `SMART SMB.AI` scripts
- [ ] Manual visual review: branding, transitions, kinetic text, color grade look professional
- [ ] Config documents all new `[branding]` and subtitle fallback settings

**Phase 2 (Auto-Post):**
- [ ] All FR-3.x acceptance criteria met
- [ ] Upload-Post free tier account created, 3 test posts to each platform successful
- [ ] Direct API interface defined (abstract base class), stub implementations ready

**Phase 3 (Script System):**
- [ ] All FR-4.x acceptance criteria met
- [ ] Hook library has ≥ 20 proven hooks categorized by type
- [ ] Template mapping covers ≥ 5 SmartSMB topic categories
- [ ] A/B test run: 3 variants from same topic, all render + verify

**Phase 4 (Automation):**
- [ ] All FR-5.x acceptance criteria met
- [ ] Cron runs 2 consecutive weeks unattended
- [ ] Telegram delivery works, cleanup executes

---

## Dependencies & Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MoviePy/FFmpeg transition bugs | Medium | High | Test transitions early; fallback to crossfade only |
| Whisper CPU speed (large-v3) | High | Medium | Use `int8` quantized; cache model; allow `base`/`small` for speed |
| Upload-Post rate limits | Low | Medium | Respect 10/mo free tier; queue overflow to manual |
| Platform API changes (TikTok/IG/YT) | Medium | High | Abstract uploader interface; monitor Upload-Post changelog |
| Edge TTS voice availability | Low | Low | Multiple English voices configured as fallbacks |

---

*Last updated: 2026-08-04*