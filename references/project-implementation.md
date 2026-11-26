# Countdown Video Jianying Draft Reference

Use this self-contained reference for countdown-video style Jianying draft generation. Source paths below are repository-relative examples from the original implementation; do not assume those repositories or absolute paths exist on the user's machine.

## Source Files

| Purpose | Path |
| --- | --- |
| Draft JSON structure and fixed catalogs | `references/draft-json-structure-and-catalog.md` |
| Service generator | `viral-countdown-service/src/workflow/countdown-video.service.ts` |
| Service routes | `viral-countdown-service/src/workflow/countdown-video.controller.ts` |
| Frontend API types | `viral-countdown-web/src/api/workflow/countdown-video.ts` |
| Desktop local generator UI/client | `viral-countdown-desktop/src/main.ts` |
| Subtitle animation ID map | `viral-countdown-service/src/libs/jianying/draft-subtitle-animation.ts` |

## Current Behavior

The service builds Jianying draft folders for Top countdown videos. The main output folder contains:

- `draft_content.json`
- `draft_meta_info.json`
- `draft_cover.jpg`
- `manifest.json`
- `README.txt`
- `Resources/local/*`
- optional `subdraft/<subdraft-id>/draft_content.json`
- optional `subdraft/<subdraft-id>/sub_draft_config.json`

The main `composeDraft` flow:

1. Normalize payload items and generation settings.
2. Build permutation orders.
3. Download/convert media with ffmpeg.
4. Resolve titles with optional multimodal recognition.
5. Build timeline variations.
6. Export draft cover.
7. Build subdraft plan and draft JSON.
8. Write files, and optionally copy them to the local Jianying draft directory.

## Key Service Methods

| Method | Why it matters |
| --- | --- |
| `composeDraft` | Full backend draft generation path. |
| `buildDesktopComposeDraftBlueprintByUid` | Desktop path: returns JSON blueprint for local file writing. |
| `buildCountdownSubdraftPlan` | Creates compound clips/subdrafts and main timeline placeholders. |
| `buildDraftContent` | Builds the top-level Jianying `draft_content.json`. |
| `buildDraftMaterials` | Assembles all `materials` arrays. Add new material categories here. |
| `buildDraftMetaInfo` | Builds `draft_meta_info.json`; keep it aligned with timeline assets. |
| `buildManifest` | Project-specific metadata used for history/debugging. |
| `buildTextMaterial` | Creates `materials.texts[*]`; `content` is JSON-stringified style data. |
| `buildTextSegment` | Creates text track segments and attaches `extra_material_refs`. |
| `buildTextAnimationMaterial` | Creates `materials.material_animations` for text reveal animations. |
| `buildVideoMotionAnimationMaterial` | Creates video material animations under `materials.material_animations`. |
| `buildTransitionMaterial` | Creates default transition material, currently 闪白. |
| `tryCopyDraftToLocalJianyingFolder` | Windows-only direct sync to the Jianying project folder. |

## Existing Constants To Reuse

Use these instead of introducing duplicate IDs:

- `DRAFT_RATIO = '9:16'`, `DRAFT_WIDTH = 1080`, `DRAFT_HEIGHT = 1920`
- default clip/transition/typewriter values near the top of `countdown-video.service.ts`
- `COUNTDOWN_DEFAULT_TRANSITION_RESOURCE_ID = '6724845376098013708'` for 闪白
- `COUNTDOWN_VIDEO_MASK_RESOURCE_ID = '7356934318301647410'` for 矩形 mask
- `COUNTDOWN_TITLE_BUBBLE_OPTIONS` for text shapes
- `COUNTDOWN_STICKER_STYLE_OPTIONS` and `COUNTDOWN_STICKER_PLACEMENTS`
- `COUNTDOWN_TEXT_FONT_OPTIONS` / `COUNTDOWN_TEXT_CJK_FONT_OPTIONS`
- `COUNTDOWN_VIDEO_MOTION_ANIMATION_OPTIONS`
- `COUNTDOWN_TITLE_REVEAL_ANIMATION_KEYS`
- `JIANYING_DRAFT_SUBTITLE_ANIMATION_OPTIONS` in `draft-subtitle-animation.ts`

## API Contract

Backend controller routes:

- `POST /api/workflow/novel-video/countdown-video/compose-draft`
- `POST /api/workflow/novel-video/countdown-video/compose-draft-job`
- `GET /api/workflow/novel-video/countdown-video/compose-draft-progress`
- `GET /api/workflow/novel-video/countdown-video/drafts`
- `GET /api/workflow/novel-video/countdown-video/draft-detail`
- `POST /api/workflow/novel-video/countdown-video/desktop-compose-task/create`
- `GET /api/tasks/:uid`
- `POST /api/tasks/:uid/claim`
- `POST /api/tasks/:uid/draft-blueprint`
- `POST /api/tasks/:uid/status`

Frontend TypeScript types live in `viral-countdown-web/src/api/workflow/countdown-video.ts`.

## Local Output Notes

Local output paths are project-specific. Prefer a caller-provided draft folder, then write that folder consistently into `draft_meta_info.json` and any desktop compose blueprint.

## Safe Extension Checklist

When adding a new Jianying draft capability:

1. Add fixed resource IDs to a local option list or to `src/libs/jianying/*` if reused.
2. Add a builder for the material structure.
3. Push the material into the correct `materials` array in `buildDraftMaterials`.
4. Attach the material from the segment using `material_id` or `extra_material_refs`.
5. Update `manifest` only for project debugging metadata, not for Jianying compatibility.
6. Run service tests/build if possible, then inspect a generated draft JSON.
