#!/usr/bin/env python3
"""Extract and cluster Jianying text styles from one draft or a draft library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


_DECRYPT_HELPER: Path | None = None


def decrypt_helper() -> Path:
    global _DECRYPT_HELPER
    if _DECRYPT_HELPER and _DECRYPT_HELPER.exists():
        return _DECRYPT_HELPER
    source = Path(__file__).with_name("decrypt_yingying_json.go")
    target = Path(tempfile.gettempdir()) / "codex-jianying-decrypt-yingying.exe"
    if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
        subprocess.run(
            ["go", "build", "-o", str(target), str(source)],
            check=True,
            capture_output=True,
            text=True,
        )
    _DECRYPT_HELPER = target
    return target


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        result = subprocess.run(
            [str(decrypt_helper()), str(path)],
            check=True,
            capture_output=True,
        )
        value = json.loads(result.stdout.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("top-level JSON is not an object")
    return value


def round_value(value: Any, digits: int = 6) -> Any:
    if isinstance(value, float):
        return round(value, digits)
    if isinstance(value, list):
        return [round_value(item, digits) for item in value]
    if isinstance(value, dict):
        return {key: round_value(item, digits) for key, item in value.items()}
    return value


def color_of(style: dict[str, Any]) -> list[float] | None:
    fill = style.get("fill") or {}
    content = fill.get("content") or {}
    solid = content.get("solid") or {}
    color = solid.get("color")
    return round_value(color) if isinstance(color, list) else None


def basename(path: Any) -> str:
    if not isinstance(path, str) or not path:
        return ""
    return path.replace("\\", "/").rsplit("/", 1)[-1]


def normalized_style(style: dict[str, Any]) -> dict[str, Any]:
    strokes = []
    for stroke in style.get("strokes") or []:
        solid = (((stroke.get("content") or {}).get("solid")) or {})
        strokes.append({
            "color": round_value(solid.get("color")),
            "alpha": round_value(solid.get("alpha")),
            "width": round_value(stroke.get("width")),
        })
    shadows = []
    for shadow in style.get("shadows") or []:
        solid = (((shadow.get("content") or {}).get("solid")) or {})
        shadows.append({
            "color": round_value(solid.get("color")),
            "alpha": round_value(shadow.get("alpha")),
            "diffuse": round_value(shadow.get("diffuse")),
            "distance": round_value(shadow.get("distance")),
            "angle": round_value(shadow.get("angle")),
        })
    font = style.get("font") or {}
    effect_style = style.get("effectStyle") or {}
    return {
        "fill": color_of(style),
        "size": round_value(style.get("size")),
        "bold": bool(style.get("bold", False)),
        "italic": bool(style.get("italic", False)),
        "underline": bool(style.get("underline", False)),
        "font_file": basename(font.get("path")),
        "font_id": font.get("id") or "",
        "strokes": strokes,
        "shadows": shadows,
        "effect_style_id": str(effect_style.get("id") or ""),
        "use_letter_color": bool(style.get("useLetterColor", False)),
    }


def style_signature(record: dict[str, Any]) -> str:
    signature = {
        "material_type": record["material_type"],
        "styles": record["styles"],
        "background": record["background"],
        "line_spacing": record["line_spacing"],
        "alignment": record["alignment"],
        "animations": record["animations"],
        "effects": record["effects"],
    }
    return hashlib.sha1(
        json.dumps(signature, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:12]


def semantic_hints(text: str, material_type: str, start_s: float, sizes: list[float]) -> list[str]:
    hints: list[str] = []
    compact = re.sub(r"\s+", "", text)
    max_size = max(sizes or [0])
    if material_type == "subtitle":
        hints.append("spoken_subtitle")
    if start_s <= 2.0 and ("\n" in text or max_size >= 18):
        hints.append("opening_hook")
    if re.match(r"^(?:第?[一二三四五六七八九十\d]+[\.、：:]|[①②③④⑤⑥⑦⑧⑨⑩])", compact):
        hints.append("numbered_list")
    if re.search(r"\d|%|％|万|亿|\+", compact):
        hints.append("data_or_number")
    if any(word in compact for word in ("联系", "咨询", "私信", "评论区", "关注", "点赞", "收藏", "转发", "领取", "报名", "落地", "主页", "下方")):
        hints.append("cta")
    if any(word in compact for word in ("为什么", "如何", "怎么", "到底", "凭什么", "你知道", "是不是", "吗", "？", "?")):
        hints.append("question_hook")
    if any(word in compact for word in ("难", "错", "坑", "焦虑", "痛苦", "失败", "问题", "风险", "千万别", "不要", "不能", "后悔", "真相")):
        hints.append("pain_or_conflict")
    if any(word in compact for word in ("老板", "宝妈", "妈妈", "爸爸", "家长", "女性", "律师", "老师", "销售", "创业者", "中介", "学生")) and len(compact) <= 12:
        hints.append("audience_or_identity")
    if material_type != "subtitle" and len(compact) <= 12 and max_size >= 18:
        hints.append("emphasis_keyword")
    return hints or ["supporting_text"]


def project_kind(relative: Path) -> str:
    name = relative.parts[0] if relative.parts else ""
    if re.match(r"^[123]-[123]-", name):
        return "tutorial"
    return "industry_example"


def iter_draft_paths(root: Path, include_subdrafts: bool) -> list[Path]:
    if root.is_file():
        return [root]
    paths = []
    for path in root.rglob("draft_content.json"):
        lowered = {part.lower() for part in path.parts}
        if ".backup" in lowered or ".recycle_bin" in lowered:
            continue
        relative = path.relative_to(root)
        if not include_subdrafts and len(relative.parts) != 2:
            continue
        paths.append(path)
    return sorted(paths)


def extract(root: Path, include_subdrafts: bool) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    duplicate_files: list[str] = []
    seen_hashes: set[str] = set()
    parsed_drafts = 0
    draft_files = iter_draft_paths(root, include_subdrafts)

    for path in draft_files:
        try:
            draft = load_json(path)
            digest = hashlib.sha1(
                json.dumps(draft, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            if digest in seen_hashes:
                duplicate_files.append(str(path))
                continue
            seen_hashes.add(digest)
            parsed_drafts += 1
        except Exception as exc:
            parse_errors.append({"path": str(path), "error": str(exc)})
            continue

        relative = path.relative_to(root) if root.is_dir() else Path(path.name)
        materials = draft.get("materials") or {}
        texts = {item.get("id"): item for item in materials.get("texts") or [] if item.get("id")}
        animations = {
            item.get("id"): item for item in materials.get("material_animations") or [] if item.get("id")
        }
        attached_effects = {}
        for array_name in ("effects", "video_effects"):
            for item in materials.get(array_name) or []:
                if item.get("id"):
                    attached_effects[item["id"]] = item

        for track_index, track in enumerate(draft.get("tracks") or []):
            # Recent Jianying versions frequently place text segments on a
            # `mixed` track. The primary material reference is authoritative;
            # filtering only by track.type silently drops those subtitles.
            for segment in track.get("segments") or []:
                material = texts.get(segment.get("material_id"))
                if not material:
                    continue
                try:
                    content = material.get("content") or "{}"
                    content = json.loads(content) if isinstance(content, str) else content
                except Exception:
                    continue
                text = str(content.get("text") or "")
                styles = [normalized_style(style) for style in content.get("styles") or []]
                extra_refs = segment.get("extra_material_refs") or []
                animation_rows = []
                effect_rows = []
                for ref in extra_refs:
                    animation = animations.get(ref)
                    if animation:
                        for item in animation.get("animations") or []:
                            animation_rows.append({
                                "type": item.get("type") or "",
                                "name": item.get("name") or "",
                                "id": str(item.get("id") or ""),
                            })
                    effect = attached_effects.get(ref)
                    if effect:
                        effect_rows.append({
                            "type": effect.get("type") or "",
                            "effect_id": str(effect.get("effect_id") or effect.get("resource_id") or ""),
                        })
                timerange = segment.get("target_timerange") or {}
                start_s = float(timerange.get("start") or 0) / 1_000_000
                duration_s = float(timerange.get("duration") or 0) / 1_000_000
                clip = segment.get("clip") or {}
                transform = clip.get("transform") or {}
                scale = clip.get("scale") or {}
                background = {
                    key: round_value(material.get(key))
                    for key in (
                        "background_alpha", "background_color", "background_width",
                        "background_height", "background_round_radius", "background_style",
                        "background_horizontal_offset", "background_vertical_offset",
                    )
                    if material.get(key) is not None
                }
                sizes = [float(item["size"]) for item in styles if isinstance(item.get("size"), (int, float))]
                record = {
                    "project": relative.parts[0] if relative.parts else path.parent.name,
                    "project_kind": project_kind(relative),
                    "draft_path": str(relative),
                    "track_index": track_index,
                    "start_s": round(start_s, 3),
                    "duration_s": round(duration_s, 3),
                    "text": text,
                    "material_type": material.get("type") or "",
                    "styles": styles,
                    "background": background,
                    "line_spacing": round_value(material.get("line_spacing")),
                    "alignment": material.get("alignment"),
                    "position": {
                        "x": round_value(transform.get("x")),
                        "y": round_value(transform.get("y")),
                        "scale_x": round_value(scale.get("x")),
                        "scale_y": round_value(scale.get("y")),
                    },
                    "animations": sorted(animation_rows, key=lambda item: (item["type"], item["name"], item["id"])),
                    "effects": sorted(effect_rows, key=lambda item: (item["type"], item["effect_id"])),
                    "semantic_hints": semantic_hints(text, material.get("type") or "", start_s, sizes),
                }
                record["style_signature"] = style_signature(record)
                records.append(record)

    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        clusters[record["style_signature"]].append(record)
    style_clusters = []
    for signature, rows in clusters.items():
        sample = rows[0]
        style_clusters.append({
            "signature": signature,
            "count": len(rows),
            "project_count": len({row["project"] for row in rows}),
            "projects": sorted({row["project"] for row in rows})[:20],
            "sample_texts": list(dict.fromkeys(row["text"] for row in rows if row["text"]))[:12],
            "semantic_hints": dict(Counter(hint for row in rows for hint in row["semantic_hints"])),
            "material_type": sample["material_type"],
            "styles": sample["styles"],
            "background": sample["background"],
            "line_spacing": sample["line_spacing"],
            "alignment": sample["alignment"],
            "animations": sample["animations"],
            "effects": sample["effects"],
            "position_samples": list(dict.fromkeys(
                json.dumps(row["position"], ensure_ascii=False, sort_keys=True) for row in rows
            ))[:8],
        })
    style_clusters.sort(key=lambda item: (-item["count"], -item["project_count"], item["signature"]))

    animation_counter = Counter(
        (item["type"], item["name"], item["id"])
        for record in records for item in record["animations"]
    )
    font_counter = Counter(
        (style.get("font_file") or style.get("font_id") or "<system-default>")
        for record in records for style in record["styles"]
    )
    semantic_counter = Counter(hint for record in records for hint in record["semantic_hints"])

    return {
        "schema_version": 1,
        "source_root": str(root),
        "stats": {
            "draft_files_found": len(draft_files),
            "unique_drafts_parsed": parsed_drafts,
            "duplicate_files_skipped": len(duplicate_files),
            "parse_errors": len(parse_errors),
            "text_segments": len(records),
            "style_clusters": len(style_clusters),
            "projects": len({record["project"] for record in records}),
        },
        "semantic_counts": dict(semantic_counter.most_common()),
        "animation_catalog": [
            {"type": key[0], "name": key[1], "id": key[2], "count": count}
            for key, count in animation_counter.most_common()
        ],
        "font_catalog": [
            {"font": font, "count": count} for font, count in font_counter.most_common()
        ],
        "style_clusters": style_clusters,
        "records": records,
        "parse_errors": parse_errors,
        "duplicate_files": duplicate_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Draft JSON, draft folder, or library root")
    parser.add_argument("--output", type=Path, help="Write full catalog JSON to this path")
    parser.add_argument("--top-level-only", action="store_true", help="Skip subdraft and Timelines JSON")
    args = parser.parse_args()
    root = args.root.resolve()
    result = extract(root, include_subdrafts=not args.top_level_only)
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(json.dumps(result["stats"], ensure_ascii=False))
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
