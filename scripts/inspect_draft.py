#!/usr/bin/env python3
"""Inspect Jianying/CapCut draft JSON reference integrity.

Usage:
  python inspect_draft.py path/to/draft-folder
  python inspect_draft.py path/to/draft_content.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from extract_text_style_catalog import load_json


MATERIAL_ARRAY_HINTS = {
    "ai_translates",
    "audio_balances",
    "audio_effects",
    "audio_fades",
    "audios",
    "canvases",
    "common_mask",
    "drafts",
    "effects",
    "keyframes",
    "masks",
    "material_animations",
    "sound_channel_mappings",
    "speeds",
    "stickers",
    "texts",
    "transitions",
    "video_effects",
    "videos",
}


def read_json(path: Path) -> Any:
    return load_json(path)


def load_draft(path: Path) -> tuple[dict[str, Any], dict[str, Any] | None, list[str]]:
    if path.is_file():
        content_path = path
    elif path.is_dir():
        content_path = path / "draft_content.json"
        if not content_path.exists():
            matches = list(path.rglob("draft_content.json"))
            if len(matches) != 1:
                raise ValueError(f"Expected one draft_content.json under {path}, found {len(matches)}; specify a draft file")
            content_path = matches[0]
    else:
        raise FileNotFoundError(path)
    meta_path = content_path.parent / "draft_meta_info.json"
    meta = read_json(meta_path) if meta_path.exists() else None
    root = content_path.parent
    files = [str(item.relative_to(root)).replace("\\", "/") for item in root.rglob("*") if item.is_file()]
    return read_json(content_path), meta, files


def iter_materials(materials: Any) -> list[tuple[str, dict[str, Any]]]:
    result: list[tuple[str, dict[str, Any]]] = []
    if not isinstance(materials, dict):
        return result
    for key, value in materials.items():
        if key not in MATERIAL_ARRAY_HINTS and not isinstance(value, list):
            continue
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict):
                result.append((key, item))
    return result


def summarize_text_content(material: dict[str, Any]) -> dict[str, Any]:
    raw = material.get("content")
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {"content_json_error": str(exc)}
    styles = parsed.get("styles") if isinstance(parsed, dict) else None
    return {
        "text": parsed.get("text") if isinstance(parsed, dict) else None,
        "style_count": len(styles) if isinstance(styles, list) else 0,
    }


def normalize_embedded_path(raw: Any) -> str:
    value = str(raw or "").strip().replace("\\", "/")
    if not value:
        return ""
    lower = value.lower()
    for marker in ("resources/local/", "subdraft/", "draft_cover.jpg"):
        index = lower.find(marker)
        if index >= 0:
            return value[index:]
    return value


def collect_draft_resource_path_refs(draft: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for array_name, material in iter_materials(draft.get("materials")):
        material_id = str(material.get("id", ""))
        for field in ("path", "file_Path", "draft_file_path", "draft_cover_path", "draft_config_path"):
            normalized = normalize_embedded_path(material.get(field))
            if not normalized:
                continue
            if normalized.startswith("#") or "://" in normalized:
                continue
            refs.append({
                "array": array_name,
                "material_id": material_id,
                "field": field,
                "path": normalized,
                "original_path": str(material.get(field)),
            })

    cover_path = normalize_embedded_path(draft.get("cover_path") or draft.get("static_cover_image_path"))
    if cover_path and not cover_path.startswith("#") and "://" not in cover_path:
        refs.append({
            "array": "<draft>",
            "material_id": str(draft.get("id", "")),
            "field": "cover_path",
            "path": cover_path,
            "original_path": str(draft.get("cover_path") or draft.get("static_cover_image_path")),
        })
    return refs


def inspect_draft_resource_paths(draft: dict[str, Any], files: list[str]) -> dict[str, Any]:
    normalized_files = {
        str(item).replace("\\", "/").strip("/").casefold()
        for item in files
        if str(item).strip()
    }
    refs = collect_draft_resource_path_refs(draft)
    missing: list[dict[str, str]] = []
    checkable = 0
    for ref in refs:
        path_ref = ref["path"].strip("/")
        if not path_ref:
            continue
        checkable += 1
        if path_ref.casefold() in normalized_files:
            continue
        original_path = Path(ref["original_path"])
        if original_path.is_absolute() and original_path.is_file():
            continue
        missing.append(ref)

    return {
        "draft_resource_path_ref_count": len(refs),
        "checkable_draft_resource_path_ref_count": checkable,
        "missing_draft_resource_path_refs": missing,
    }


def inspect_references(draft: dict[str, Any], files: list[str] | None = None) -> dict[str, Any]:
    material_entries = iter_materials(draft.get("materials"))
    material_ids = {
        str(item.get("id"))
        for _, item in material_entries
        if item.get("id") not in (None, "")
    }
    material_counts = Counter(key for key, _ in material_entries)
    material_type_counts = Counter(
        f"{key}:{item.get('type', 'unknown')}"
        for key, item in material_entries
    )

    tracks = draft.get("tracks") if isinstance(draft.get("tracks"), list) else []
    track_counts = Counter(
        str(track.get("type", "unknown"))
        for track in tracks
        if isinstance(track, dict)
    )

    segment_count = 0
    missing_primary: list[dict[str, str]] = []
    missing_extra: list[dict[str, str]] = []

    for track in tracks:
        if not isinstance(track, dict):
            continue
        track_id = str(track.get("id", ""))
        track_type = str(track.get("type", "unknown"))
        segments = track.get("segments") if isinstance(track.get("segments"), list) else []
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            segment_count += 1
            segment_id = str(segment.get("id", ""))
            material_id = segment.get("material_id")
            if not material_id or str(material_id) not in material_ids:
                missing_primary.append({
                    "track": track_id,
                    "track_type": track_type,
                    "segment": segment_id,
                    "material_id": str(material_id),
                })
            refs = segment.get("extra_material_refs")
            if isinstance(refs, list):
                for ref in refs:
                    if ref and str(ref) not in material_ids:
                        missing_extra.append({
                            "track": track_id,
                            "track_type": track_type,
                            "segment": segment_id,
                            "extra_material_ref": str(ref),
                        })

    text_samples = []
    for _, material in material_entries:
        if material.get("type") in {"subtitle", "text"}:
            sample = summarize_text_content(material)
            if sample:
                sample["id"] = material.get("id")
                text_samples.append(sample)
            if len(text_samples) >= 5:
                break

    report = {
        "draft_id": draft.get("id"),
        "name": draft.get("name"),
        "duration_us": draft.get("duration"),
        "track_count": len(tracks),
        "track_types": dict(sorted(track_counts.items())),
        "segment_count": segment_count,
        "material_array_counts": dict(sorted(material_counts.items())),
        "material_type_counts": dict(sorted(material_type_counts.items())),
        "material_id_count": len(material_ids),
        "missing_primary_material_refs": missing_primary,
        "missing_extra_material_refs": missing_extra,
        "text_samples": text_samples,
        "validation_issues": [],
        "animation_resource_warnings": [],
    }
    issues = report["validation_issues"]
    runtime_ids = [str(item["id"]) for _, item in material_entries if item.get("id")]
    for track in tracks:
        if isinstance(track, dict):
            if track.get("id"):
                runtime_ids.append(str(track["id"]))
            for segment in track.get("segments") or []:
                if isinstance(segment, dict) and segment.get("id"):
                    runtime_ids.append(str(segment["id"]))
    for runtime_id, count in Counter(runtime_ids).items():
        if count > 1:
            issues.append({"type": "duplicate_runtime_id", "id": runtime_id, "count": count})
    for array_name, material in material_entries:
        if array_name == "texts":
            raw = material.get("content")
            try:
                if not isinstance(raw, str):
                    raise ValueError("content must be a JSON string")
                content = json.loads(raw)
                if not isinstance(content, dict) or not isinstance(content.get("text"), str):
                    raise ValueError("content must contain a text string")
            except (ValueError, TypeError) as exc:
                issues.append({"type": "invalid_text_content", "id": material.get("id"), "error": str(exc)})
        if array_name == "material_animations":
            for animation in material.get("animations") or []:
                if isinstance(animation, dict) and (not animation.get("path") or not Path(animation["path"]).exists()):
                    report["animation_resource_warnings"].append({"id": material.get("id"), "path": animation.get("path"), "name": animation.get("name")})
    if files is not None:
        report.update(inspect_draft_resource_paths(draft, files))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Jianying draft_content.json references.")
    parser.add_argument("path", help="Draft folder or draft_content.json")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    draft_path = Path(args.path)
    try:
        draft, meta, files = load_draft(draft_path)
        report = inspect_references(draft, files)
        report["meta_present"] = meta is not None
        if meta:
            report["meta"] = {
                "draft_id": meta.get("draft_id"),
                "draft_name": meta.get("draft_name"),
                "draft_root_path": meta.get("draft_root_path"),
                "draft_json_file": meta.get("draft_json_file"),
                "tm_duration": meta.get("tm_duration"),
            }
            for content_field, meta_field in (("id", "draft_id"), ("name", "draft_name")):
                if draft.get(content_field) and meta.get(meta_field) and draft[content_field] != meta[meta_field]:
                    report["validation_issues"].append({"type": "meta_mismatch", "field": content_field, "content": draft[content_field], "meta": meta[meta_field]})
        report["file_count"] = len(files)
        has_missing_refs = bool(report["missing_primary_material_refs"] or report["missing_extra_material_refs"])
        has_missing_paths = bool(report.get("missing_draft_resource_path_refs"))
        report["status"] = "has_missing_refs" if has_missing_refs or has_missing_paths else "invalid" if report["validation_issues"] else "ok"
        print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0 if report["status"] == "ok" else 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
