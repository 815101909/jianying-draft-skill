"""Media probing and explicit fidelity reports for the basic FFmpeg renderer."""
import json
import subprocess


def unsupported_features(draft):
    issues = []
    def add(segment, feature):
        item = {"segment": str(segment.get("id", "")), "feature": feature}
        if item not in issues:
            issues.append(item)
    def walk(document, depth=0):
        if depth > 8:
            issues.append({"segment": "", "feature": "compound nesting exceeds 8"})
            return
        index = {m.get("id"): (group, m) for group, items in (document.get("materials") or {}).items()
                 if isinstance(items, list) for m in items if isinstance(m, dict)}
        for track in document.get("tracks") or []:
            for seg in track.get("segments") or []:
                if seg.get("visible") is False:
                    continue
                group, material = index.get(seg.get("material_id"), (None, {}))
                if group not in {"videos", "images", "audios", "texts", "drafts"}:
                    add(seg, "unhandled primary material")
                if seg.get("common_keyframes") or seg.get("keyframe_refs"):
                    add(seg, "keyframe animation")
                clip = seg.get("clip") or {}
                crop = material.get("crop") or seg.get("crop") or {}
                full_crop = {"upper_left_x": 0, "upper_left_y": 0, "upper_right_x": 1, "upper_right_y": 0,
                             "lower_left_x": 0, "lower_left_y": 1, "lower_right_x": 1, "lower_right_y": 1}
                if crop and crop != full_crop:
                    add(seg, "crop")
                if clip.get("rotation") or any((clip.get("flip") or {}).values()):
                    add(seg, "rotation/flip")
                if material.get("has_audio") and seg.get("volume", 1) and group == "videos":
                    add(seg, "video source audio (use a separate audio track)")
                if group == "texts":
                    try:
                        styles = json.loads(material.get("content", "{}" )).get("styles") or []
                        if len(styles) > 1:
                            add(seg, "multiple text styles")
                        if any(s.get("font") or s.get("effectStyle") for s in styles):
                            add(seg, "native text font/effect")
                    except (ValueError, TypeError, AttributeError):
                        add(seg, "invalid text content")
                refs = [seg.get("material_id"), *(seg.get("extra_material_refs") or [])]
                for ref in refs:
                    attached_group, attached = index.get(ref, (None, {}))
                    if attached_group in {"masks", "common_mask", "effects", "video_effects", "transitions", "material_animations", "audio_effects", "audio_fades"}:
                        add(seg, attached_group)
                    if attached_group == "speeds" and attached.get("curve_speed"):
                        add(seg, "curve speed approximation")
                    if attached_group == "drafts" and isinstance(attached.get("draft"), dict):
                        walk(attached["draft"], depth + 1)
    walk(draft)
    return issues


def probe_media(timeline, ffprobe="ffprobe"):
    issues, cache = [], {}
    for clip in timeline.clips:
        if clip.kind == "text" or clip.missing or not clip.path:
            continue
        if clip.path not in cache:
            try:
                result = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", clip.path],
                                        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
                if result.returncode:
                    raise ValueError(result.stderr.strip()[-500:] or "ffprobe failed")
                cache[clip.path] = json.loads(result.stdout)
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                cache[clip.path] = {"error": str(exc)}
        media = cache[clip.path]
        required = "audio" if clip.kind == "audio" else "video"
        streams = [s for s in media.get("streams", []) if s.get("codec_type") == required]
        error = media.get("error")
        if not error and not streams:
            error = f"no {required} stream"
        if not error and required == "video" and not any(s.get("width", 0) > 0 and s.get("height", 0) > 0 for s in streams):
            error = "invalid video dimensions"
        if error:
            issues.append({"segment": clip.seg_id, "path": clip.path, "error": error})
    return issues
