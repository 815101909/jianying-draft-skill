# AIGC Factory Jianying Draft Implementation

Use this self-contained reference for production novel-video / AIGC Factory style Jianying draft generation. Source paths below are repository-relative examples from the original implementation; do not assume those repositories or absolute paths exist on the user's machine.

## Source Files

| Purpose | Path |
| --- | --- |
| Main service | `app/service/novel-video-project.ts` |
| Controller | `app/controller/workflow/novel-video.ts` |
| Router | `app/routers/workflow.ts` |
| Subtitle animation catalog | `app/libs/jianying/draft-subtitle-animation.ts` |
| Runtime config | `config/env.ts`, `config/config.default.ts`, `config/config.local.ts`, `config/config.prod.ts` |
| API documentation | `docs/workflow-novel-video.md` |

## Current Workflow

This project builds editable Jianying draft folders and desktop draft blueprints for a production rendering workflow. It supports:

- background draft export progress with restart recovery
- desktop compose task UID and local draft blueprints
- `none` / `random` / `specified` native transition selection
- ASR subtitles mapped onto compressed shot timelines
- science-channel subtitle template styling
- visual keyword overlays from cover timelines or ASR
- duplicated foreground/matting overlay layers for keyword moments
- optional high-light mix appendages after the main story
- cover conversion to `draft_cover.jpg`
- narration/audio sliced into one segment per shot slot

## API Surface

Important routes:

- `POST /api/workflow/novel-video/compose-final-video`: build final Jianying draft/video export artifacts. Supports `async`, `append_highlight_mix`, `draft_transition_mode`, and `draft_transition_key`.
- `POST /api/workflow/novel-video/jianying-draft-export-progress`: poll or long-poll draft export progress.
- `GET /api/workflow/novel-video/draft-transitions`: list native transition options.
- `POST /api/workflow/novel-video/project/update-draft-transition`: save project-level transition config.
- `GET /api/workflow/novel-video/draft-subtitle-animations`: list subtitle intro animations.
- `POST /api/workflow/novel-video/project/update-draft-subtitle-animation`: save project-level subtitle animation.
- `POST /api/workflow/novel-video/desktop-compose-task/create`: create a desktop UID task.
- `GET /api/tasks/:uid`, `POST /api/tasks/:uid/claim`, `POST /api/tasks/:uid/draft-blueprint`, `POST /api/tasks/:uid/status`: desktop task lifecycle.

Progress status includes `currentStage`, `message`, `progress`, `isProcessing`, and optional `error`.

## Key Service Methods

| Method | Why it matters |
| --- | --- |
| `prepareJianyingDraftExportTask` | Prevents duplicate running exports and stores progress in project `ext`. |
| `markJianyingDraftExportFailed` | Marks interrupted async export as failed; app startup also calls this pattern. |
| `composeFinalVideo` | Main server-side draft export path. |
| `buildDesktopComposeDraftBlueprintByUid` | Desktop path; returns draft JSON plus `resource_plan` for local downloads/crops. |
| `buildJianyingDraftContent` | Assembles full `draft_content.json`. |
| `buildJianyingDraftMetaInfo` | Builds `draft_meta_info.json` with unique material paths and subtitle count. |
| `buildJianyingDraftManifest` | Debug/trace metadata for shots, transitions, subtitles, visual keywords, cover, and audio. |
| `buildDraftNativeTransitionAssets` | Adds native transitions only between adjacent same-track clips. |
| `buildDraftTrackSegment` | Builds video/photo segments with speed, canvas, transition refs, photo keyframes, and fade-out. |
| `buildDraftTextMaterial` | Rich text material builder with backgrounds, strokes, shadows, fonts, and science styles. |
| `buildDraftTextAnimationMaterial` | Packs both intro and out animations into `materials.material_animations`. |
| `buildDraftTextEffectMaterial` | Adds text effect material for science keyword burst text. |
| `buildDraftAudioTrackSegments` | Slices narration/audio by shot slot so audio, shots, and subtitles align. |
| `buildDraftVisualKeywordMattingAssets` | Duplicates underlying visual clips as foreground/matting overlays during keyword moments. |
| `compressDraftTrackAssetGaps` | Removes source timeline gaps before applying native transitions. |
| `applyDraftEndingFadeOut` / `applyDraftEndingFadeOutToTextAssets` | Adds ending fade-out to final video and overlapping text. |
| `prepareDraftProjectCover` | Downloads/converts project cover to `draft_cover.jpg`. |

## Native Transition Pattern

The built-in transition pool:

| Name | Resource ID |
| --- | --- |
| 叠化 | `6724845717472416269` |
| 模糊 | `6911569618171597320` |
| 闪白 | `6724845376098013708` |
| 叠加 | `6914112332205396488` |
| 雾化 | `7216171159589491259` |
| 推近 | `6724226861666144779` |
| 泛光 | `6914112263645303303` |
| 翻页 | `6747979085894390279` |
| 闪黑 | `6724239388189921806` |
| 云朵 | `6955722927161479694` |
| 竖向模糊 | `7125661387568714247` |
| 向左擦除 | `6724849999336706573` |
| 开幕 | `6750893890712113677` |
| 左移 | `6726711499676455435` |
| 向右擦除 | `6724849898857959950` |
| 窗格 | `6747989545448378888` |
| 风车 | `6748286529921094157` |
| 倒影 | `6748313807031898627` |
| 粒子 | `6855565313715474952` |
| 色彩溶解II | `6724866927933526542` |

Rules:

- `mode: none` means no transitions.
- `mode: specified` uses the selected transition key/resource ID everywhere.
- `mode: random` uses a deterministic seed from `wid:shotNo:nextShotNo`.
- Only attach a transition when the next clip starts within `1000us` of the current clip's end.
- Transition duration is `min(500000, currentDuration - 1000, nextDuration - 1000)`.
- Skip transitions shorter than `100000us`.
- Store transition materials in `materials.transitions`.
- Attach the transition material ID to the outgoing video segment's `extra_material_refs`.

## Draft JSON Patterns

`buildJianyingDraftContent` includes these material arrays:

- `videos`: video/photo material records, including optional `matting` data.
- `canvases`: only for video media.
- `sound_channel_mappings`: video and audio mapping materials.
- `speeds`: video and audio speed materials.
- `transitions`: native transition materials.
- `texts`: subtitles, visual keyword text, and science keyword burst text.
- `material_animations`: text intro/out animation packs.
- `effects`: text effects for selected science keyword burst styles.
- `video_effects`: science-channel overlay effects.
- `audios`: narration/music material, usually `type: extract_music`.
- `beats`: audio beat material referenced by audio segments.

Track order observed in production:

1. main video/storyboard track
2. science keyword burst text tracks
3. visual keyword text tracks
4. visual keyword matting video overlay tracks
5. subtitle text tracks
6. science video effect tracks
7. audio track

## Text And Subtitle Details

- ASR segments are mapped from original audio timeline to compressed draft timeline with `mapOriginalTimelineUsToDraftUs`.
- `buildDraftSubtitleAssets` uses `subtitle_text` for possibly wrapped text and `subtitle_plain_text` for manifest/debug output.
- The science subtitle template uses strong background styling and both intro/out animations.
- `buildDraftTextMaterial` stores color, stroke, shadow, and text in `content`, but background and several typography fields live on the outer material.
- Visual keyword text may use custom local Windows font paths. Normalize font paths through `path.win32.normalize(...).replace(/\\/g, '/')`.
- `buildDraftTextTrackSegment` attaches animation and text effect IDs through `extra_material_refs`.

## Video, Photo, And Matting Details

- Static images are material `type: photo`; videos are `type: video`.
- Photo clips get subtle scale motion through `common_keyframes` for `KFTypeScaleX` and `KFTypeScaleY`.
- Final clip fade-out is represented through `KFTypeAlpha` keyframes.
- Visual keyword matting overlays duplicate the best-overlapping source clip and add:
  - `matting_flag: 3`
  - `matting_draft_path`
  - `custom_matting_id`
  - blank transition fields
  - fresh material/segment IDs
- Matting overlay video segments should mute source audio even when the main video keeps audio.

## Audio Details

- The project builds a single audio material and then creates one audio segment per shot slot.
- Audio segment `extra_material_refs` includes speed, sound channel mapping, and beat IDs.
- Source audio start follows the original slot start (`original_target_start_us`) so compressed video timelines still line up with narration.
- When a separate audio track is present, main video segment audio is normally muted.

## Path Details

- `draft_root_path` must be a Windows absolute path.
- `buildDraftAbsolutePath` uses `path.win32.join` and then converts backslashes to `/`.
- Cover assets are stored as `draft_cover.jpg`; non-JPEG cover sources are converted with ffmpeg.

## Extension Checklist

When changing this project:

1. Decide whether the capability is server-side draft export, desktop blueprint export, or both.
2. Keep both paths using the same builder helpers when possible.
3. Update route docs in `docs/workflow-novel-video.md` if the API contract changes.
4. Preserve async progress behavior and failure recovery for background exports.
5. Validate native transitions by ensuring clips are on the same track and adjacent after compression.
6. Validate draft JSON with `scripts/inspect_draft.py`.
