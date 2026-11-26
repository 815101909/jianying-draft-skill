# Draft Editing and Packaging Rules

Read this reference when creating or modifying timeline materials, styled captions, effects, transitions, or compound clips. Paths beginning with `references/` are relative to the skill root.

## Shared invariants

- `material_id` identifies the primary material; `extra_material_refs` identifies attached materials across groups.
- Generate fresh runtime IDs for materials, segments, tracks, and keyframes. Catalog resource IDs are not runtime IDs.
- Timeline times are microseconds; multiply milliseconds by 1000.
- Use a Windows absolute draft root for native imports and normalize paths consistently.
- Serialize text `content` as JSON inside a string and write UTF-8 JSON with a trailing newline.
- Keep content/meta ID, name, and file paths consistent. Reference a cover only when it exists.

## Draft Patterns

Use these placements unless the existing draft shows a stronger local convention:

| Capability | Main JSON location | Segment reference |
| --- | --- | --- |
| Subtitle text/style | `materials.texts` | text segment `material_id` |
| Text animation | `materials.material_animations` | text segment `extra_material_refs` |
| Text effect / 花字 | `materials.effects[type=text_effect]` | text segment `extra_material_refs` and `content.styles[*].effectStyle.id` |
| Text bubble / shape | `materials.effects[type=text_shape]` | text segment `extra_material_refs` |
| Filter | `materials.effects[type=filter]` | video `extra_material_refs` or filter track `material_id` |
| Video scene effect | `materials.video_effects[type=video_effect]` | video `extra_material_refs` or effect track `material_id` |
| Face effect | `materials.video_effects[type=face_effect]` | video `extra_material_refs` or effect track `material_id` |
| Audio effect | `materials.audio_effects` | audio segment `extra_material_refs` |
| Audio fade | `materials.audio_fades` | audio segment `extra_material_refs` |
| Transition | `materials.transitions` | usually video segment `extra_material_refs` or transition fields, follow local draft |
| Compound clip/subdraft | `materials.drafts[type=combination]` | main video segment `material_id` |

## Production Timeline Rules

- Native transitions only work reliably when adjacent clips are on the same video track and have no real gap. Compress timeline gaps before applying transitions.
- Clamp transition duration to fit both neighboring clips; a safe upper bound observed in production code is `500000` microseconds, and durations below `100000` microseconds are usually skipped.
- For static image clips, use `common_keyframes` on `KFTypeScaleX` and `KFTypeScaleY` for subtle photo motion. When slicing or repeating a photo segment, offset the keyframe interpolation so the motion remains continuous.
- Apply ending fade-out with `KFTypeAlpha` on the last video segment. Add native text out animations only when the exact animation resource is known to resolve in the target Jianying install.
- If keeping a video's source audio is not intentional, set segment `volume` and `last_nonzero_volume` to `0`; use a separate audio track for narration/music when possible.
- For long projects, duplicate clean timeline ranges after a large gap rather than trying to force one unbroken timeline when the product workflow expects recap/repeat sections.

## Text Rules

- `materials.texts[*].content` is a JSON string, not an object. Parse it, edit it, then stringify it.
- Put fill color, size, font, stroke, shadow, and `effectStyle` inside `content.styles`.
- Use `range` for partial highlights. Ranges are character offsets over the text string.
- For styled text backgrounds, the important outer text material fields include `background_alpha`, `background_color`, `background_height`, `background_width`, `background_round_radius`, and background offsets.
- Keep text coordinates in draft space: positive `clip.transform.y` is higher on screen in this project's Jianying draft output.
- Attach animation packs by adding a `materials.material_animations` item and referencing that item's `id` from the text segment. One pack may contain both `type: "in"` and `type: "out"` animation entries.
- Do not mix text and video animation catalogs. Text segments need text animation IDs/resources, for example text out animations from the text-out catalog, not same-named video out animations from the video-out catalog.
- Treat native Jianying animation entries as resource-backed, not portable keyframes. If any `materials.material_animations[*].animations[*].path` is empty or points to a missing cache resource after Jianying opens/saves the draft, the timeline can show `动画丢失` on every segment that references that pack. Prefer `common_keyframes` for portable text alpha/scale motion, or omit unresolved native `out` animations such as `渐隐` while keeping verified `in` animations.
- Treat `references/knowledge-payment-subtitle-presets.json` as a blueprint registry, not as draft-ready material IDs. Resolve its `$ref` fragments, replace placeholders, calculate character ranges, stringify `material.content`, generate fresh runtime IDs, and only attach a native animation when its local resource path resolves.
- When styling or adding subtitles for a knowledge-payment, founder-IP, startup, business, or editing-education talking-head draft, automatically apply the registry's `composition_engine`: classify the script into semantic beats, choose a subprofile, keep one base subtitle identity, and add justified combination recipes without asking the user to select each style. Suppress redundant base captions while a large overlay repeats the same words. Respect density budgets, collision rules, and the source video's existing visual hierarchy. A request such as “做字幕样式”, “帮我剪辑”, or “运用这个模板” authorizes this automatic composition pass; only use a single plain style when the user explicitly requests minimal/plain captions.
- Treat combination recipes as semantic choreography rather than fixed text. Adapt wording, timing, track count, and positions to the current script while preserving the recipe's role sequence. For animated emphasis roles, consult `references/talking-head-sound-motion-system.json` and add sound only when the semantic beat and a resolved local asset justify it.
- Treat `references/talking-head-font-flower-system.json` as the automatic typography selector. Choose fonts by semantic role and visual family, keep continuous captions stable, and reserve font switching or flower text for justified short overlays. Do not wait for the user to ask separately for another font or 花字. Resolve the complete text-effect material before attaching it; if the resource is unavailable, use the documented portable typography fallback instead of a broken effect.
- Treat `references/talking-head-industry-style-system.json` as the cross-industry selector. Choose one `industry_profile`, keep one base subtitle identity, and add only the role templates justified by the script. Its `$ref` fragments and placeholders require the same resolution and fresh-ID rules.
- Treat `references/original-edit-packaging-system.json` as a full-edit decision system, not a caption pack. Choose one visual family, map script beats to semantic roles, coordinate text with the frame, and add motion, sound, and compound components selectively. Filter tutorial labels and source branding before audience-facing export.
- Treat `references/talking-head-sound-motion-system.json` as a semantic pairing system, not an asset license. Select sound after the text role and animation, align the transient perceptually, keep ordinary captions silent, and resolve an intentional local or licensed audio file before writing the audio material. Enforce its repetition controls: do not reuse the same resolved sound asset as a generic fallback, prefer another justified family or silence, and audit exact-asset counts before saving.
- Use `references/talking-head-sound-scene-catalog.json` as the evidence index behind sound selection. Query the current semantic scene first, then compare exact sound samples and animation counts. Evidence frequency increases confidence but never overrides genre, narration clarity, repetition limits, or the need for silence.

## Project Implementation Pattern

The bundled JSON systems are decision rules and blueprint registries. Codex applies them when composing a draft; `composition_engine` is not an executable renderer. The implementation references describe existing project code, which must be located before reuse. For draft **generation** and **headless rendering** the skill does bundle runnable tools — see `references/headless-render-and-generation.md`.

For countdown-video style implementations, follow the bundled pattern in `references/project-implementation.md` instead of inventing a separate draft writer.

When adding new draft capabilities, prefer adding small builder functions next to the existing `buildDraftContent`, `buildDraftMaterials`, `buildTextMaterial`, `buildTextSegment`, `buildTextAnimationMaterial`, `buildDraftMetaInfo`, and `buildManifest` patterns.

For production novel-video implementations, follow `references/aigc-factory-implementation.md`. It contains the richer bundled pattern for background draft export, desktop UID blueprints, native transition selection, ASR subtitles, visual keyword overlays, matting overlays, audio slicing, and cover export.

