#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剪映草稿程序化生成器（不启动剪映）

从一个简单 JSON spec 生成剪映可识别的 draft_content.json（可选映映加密），
配合 draft2ffmpeg.py 即可完成「脚本 → 草稿 → 无头渲染」全链路。

spec 示例:
{
  "canvas": [1920, 1080],
  "fps": 30,
  "clips": [
    {"kind": "video", "path": "D:/a.mp4", "src_start": 0, "src_dur": 5,
     "tgt_start": 0, "speed": 1.0, "volume": 1.0,
     "scale": [1, 1], "transform": [0, 0]},
    {"kind": "image", "path": "D:/p.jpg", "tgt_start": 5, "tgt_dur": 3},
    {"kind": "audio", "path": "D:/m.mp3", "src_start": 0, "src_dur": 8,
     "tgt_start": 0, "volume": 0.6},
    {"kind": "text", "text": "Hello", "tgt_start": 1, "tgt_dur": 3,
     "transform": [0, 0.7], "size": 8, "color": "#FFFFFF"}
  ]
}

用法:
  python make_draft.py spec.json --out <草稿目录> [--name MyDraft] [--encrypt]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
import math
import shutil
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

US = 1_000_000


def uid() -> str:
    return str(uuid.uuid4()).upper()


def hexid(n: int = 32) -> str:
    return uuid.uuid4().hex.upper()[:n]


def validate_spec(spec: dict) -> None:
    if not isinstance(spec, dict):
        raise ValueError("spec must be an object")
    canvas = spec.get("canvas", [1920, 1080])
    if not isinstance(canvas, list) or len(canvas) != 2 or any(isinstance(v, bool) or not isinstance(v, int) or v <= 0 for v in canvas):
        raise ValueError("canvas must contain two positive integers")
    def number(value, field, minimum=0, positive=False):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum or (positive and value == minimum):
            raise ValueError(f"{field} must be finite and {'greater than' if positive else 'at least'} {minimum}")
    number(spec.get("fps", 30), "fps", positive=True)
    clips = spec.get("clips")
    if not isinstance(clips, list) or not clips:
        raise ValueError("clips must be a nonempty list")
    for i, clip in enumerate(clips):
        if not isinstance(clip, dict) or clip.get("kind", "video") not in {"video", "image", "audio", "text"}:
            raise ValueError(f"clips[{i}] has an unsupported kind")
        for field in ("src_start", "tgt_start", "volume"):
            if field in clip:
                number(clip[field], f"clips[{i}].{field}")
        number(clip.get("speed", 1), f"clips[{i}].speed", positive=True)
        number(clip.get("tgt_dur", clip.get("src_dur", 0)), f"clips[{i}].duration", positive=True)
        if "src_dur" in clip:
            number(clip["src_dur"], f"clips[{i}].src_dur", positive=True)
        for field, default in (("scale", [1, 1]), ("transform", [0, 0])):
            pair = clip.get(field, default)
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError(f"clips[{i}].{field} must contain two numbers")
            for value in pair:
                number(value, f"clips[{i}].{field}", minimum=0 if field == "scale" else -math.inf, positive=field == "scale")
        if "alpha" in clip:
            number(clip["alpha"], f"clips[{i}].alpha")
            if clip["alpha"] > 1:
                raise ValueError("alpha must be between 0 and 1")
        if clip.get("kind") == "text":
            if not isinstance(clip.get("text"), str):
                raise ValueError(f"clips[{i}].text must be a string")
            number(clip.get("size", 8), f"clips[{i}].size", positive=True)
            for field in ("color", "stroke"):
                value = clip.get(field, "#FFFFFF")
                if not isinstance(value, str) or len(value) != 7 or value[0] != "#":
                    raise ValueError(f"clips[{i}].{field} must be #RRGGBB")
                try:
                    int(value[1:], 16)
                except ValueError:
                    raise ValueError(f"clips[{i}].{field} must be #RRGGBB") from None
        elif not isinstance(clip.get("path"), str) or not clip["path"]:
            raise ValueError(f"clips[{i}].path is required")


def build(spec: dict) -> dict:
    validate_spec(spec)
    W, H = spec.get("canvas", [1920, 1080])
    fps = float(spec.get("fps", 30))
    clips = spec.get("clips", [])

    materials: dict = {
        "videos": [], "images": [], "audios": [], "texts": [], "canvases": [],
        "speeds": [], "material_animations": [], "transitions": [],
        "sound_channel_mappings": [], "vocal_separations": [], "material_colors": [],
    }
    tracks = {
        "video": {"id": uid(), "type": "video", "segments": [], "flag": 0, "attribute": 0},
        "image": {"id": uid(), "type": "video", "segments": [], "flag": 0, "attribute": 0},
        "audio": {"id": uid(), "type": "audio", "segments": []},
        "text":  {"id": uid(), "type": "text", "segments": []},
    }
    order = []

    total = 0
    for c in clips:
        kind = c.get("kind", "video")
        t_start = float(c.get("tgt_start", 0))
        t_dur = float(c.get("tgt_dur", c.get("src_dur", 0)))
        total = max(total, t_start + t_dur)

        if kind == "text":
            tid = hexid()
            size = float(c.get("size", 8.0))
            color = c.get("color", "#FFFFFF")
            content = {
                "text": c.get("text", ""),
                "styles": [{
                    "fill": {"content": {"render_type": "solid",
                                         "solid": {"color": [int(color[j:j+2], 16) / 255 for j in (1, 3, 5)]}}},
                    "range": [0, len(c.get("text", ""))],
                    "size": size,
                }],
            }
            materials["texts"].append({
                "id": tid, "type": "text", "name": c.get("name", "text"),
                "content": json.dumps(content, ensure_ascii=False),
                "font_size": size, "text_size": int(round(size * 8 / 3)),
                "text_color": color, "border_color": c.get("stroke", "#000000"),
                "border_width": 0.08, "has_shadow": True,
                "font_path": "", "line_spacing": 0.02, "initial_scale": 1.0,
                "layer_weight": 1, "bold_width": 0.03, "words": [],
                "current_words": [], "combo_info": {},
            })
            seg = {
                "id": uid(), "material_id": tid,
                "target_timerange": {"start": int(t_start * US), "duration": int(t_dur * US)},
                "clip": {"scale": {"x": 1.0, "y": 1.0},
                         "transform": {"x": float(c.get("transform", [0, 0])[0]),
                                       "y": float(c.get("transform", [0, 0])[1])},
                         "flip": {}},
                "render_index": 14000, "track_render_index": 1,
                "visible": True, "extra_material_refs": [],
            }
            tracks["text"]["segments"].append(seg)
            continue

        if kind == "audio":
            mid = hexid()
            audio_refs = []
            if float(c.get("speed", 1)) != 1:
                speed_id = hexid()
                materials["speeds"].append({"id": speed_id, "type": "speed", "speed": float(c["speed"]), "curve_speed": None, "mode": 0})
                audio_refs.append(speed_id)
            materials["audios"].append({
                "id": mid, "type": "audio", "name": os.path.basename(c["path"]),
                "path": c["path"], "duration": int(float(c.get("src_dur", t_dur)) * US),
                "music_id": "", "app_id": 0, "category_name": "", "check_flag": 3,
            })
            seg = {
                "id": uid(), "material_id": mid,
                "source_timerange": {"start": int(float(c.get("src_start", 0)) * US),
                                     "duration": int(float(c.get("src_dur", t_dur)) * US)},
                "target_timerange": {"start": int(t_start * US), "duration": int(t_dur * US)},
                "volume": float(c.get("volume", 1.0)), "visible": True,
                "extra_material_refs": audio_refs, "enable_adjust": False,
            }
            tracks["audio"]["segments"].append(seg)
            continue

        # video / image
        mid = hexid()
        grp = "images" if kind == "image" else "videos"
        materials[grp].append({
            "id": mid, "type": "photo" if kind == "image" else "video",
            "material_name": os.path.basename(c["path"]), "path": c["path"],
            "width": int(c.get("width", W)), "height": int(c.get("height", H)),
            "duration": int(float(c.get("src_dur", t_dur)) * US),
            "has_audio": bool(c.get("has_audio", False)), "crop": {},
            "material_id": "", "check_flag": 62978047,
        })
        sid = hexid()
        materials["speeds"].append({
            "id": sid, "type": "speed", "speed": float(c.get("speed", 1.0)),
            "curve_speed": None, "mode": 0,
        })
        seg = {
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": int(float(c.get("src_start", 0)) * US),
                                 "duration": int(float(c.get("src_dur", t_dur)) * US)},
            "target_timerange": {"start": int(t_start * US), "duration": int(t_dur * US)},
            "clip": {"scale": {"x": float(c.get("scale", [1, 1])[0]),
                               "y": float(c.get("scale", [1, 1])[1])},
                     "transform": {"x": float(c.get("transform", [0, 0])[0]),
                                   "y": float(c.get("transform", [0, 0])[1])},
                     "flip": {}, "rotation": 0.0, "alpha": float(c.get("alpha", 1.0))},
            "volume": float(c.get("volume", 1.0)),
            "visible": True, "extra_material_refs": [sid],
        }
        key = "image" if kind == "image" else "video"
        tracks[key]["segments"].append(seg)
        if key not in order:
            order.append(key)

    for k in ("video", "image", "audio", "text"):
        if tracks[k]["segments"]:
            if k not in order:
                order.append(k)

    draft = {
        "id": uid(),
        "name": spec.get("name", "programmatic-draft"),
        "duration": int(total * US),
        "fps": fps,
        "version": 360000,
        "new_version": "177.0.0",
        "canvas_config": {"width": W, "height": H, "ratio": spec.get("ratio", "16:9")},
        "config": {"maintrack_adsorb": False},
        "tracks": [tracks[k] for k in order],
        "materials": materials,
        "keyframes": {},
        "platform": {"app_id": 0, "os": "windows", "os_version": ""},
    }
    return draft


def main() -> int:
    ap = argparse.ArgumentParser(description="程序化生成剪映草稿")
    ap.add_argument("spec", help="spec JSON 文件（或 - 从 stdin 读）")
    ap.add_argument("--out", required=True, help="输出草稿目录")
    ap.add_argument("--encrypt", action="store_true", help="输出为映映加密格式")
    ap.add_argument("--name", help="覆盖 spec 的草稿名称")
    ap.add_argument("--copy-media", action="store_true", help="复制素材到 Resources/local，生成可搬移草稿包")
    args = ap.parse_args()

    if args.spec == "-":
        spec = json.load(sys.stdin)
    else:
        with open(args.spec, encoding="utf-8") as fh:
            spec = json.load(fh)

    if args.name:
        spec["name"] = args.name
    validate_spec(spec)
    base = Path.cwd() if args.spec == "-" else Path(args.spec).resolve().parent
    for clip in spec["clips"]:
        if clip.get("kind", "video") != "text":
            media = Path(clip["path"])
            media = media if media.is_absolute() else base / media
            if not media.is_file():
                raise ValueError(f"素材不存在: {media}")
            clip["path"] = media.resolve().as_posix()
    if Path(args.out, "draft_content.json").exists() or Path(args.out, "draft_meta_info.json").exists():
        raise ValueError("输出目录已有草稿，请使用新目录")
    os.makedirs(args.out, exist_ok=True)
    if args.copy_media:
        media_dir = Path(args.out, "Resources", "local")
        media_dir.mkdir(parents=True, exist_ok=True)
        copied = {}
        for clip in spec["clips"]:
            if clip.get("kind", "video") == "text":
                continue
            source = clip["path"]
            if source not in copied:
                destination = media_dir / (uuid.uuid4().hex + Path(source).suffix)
                shutil.copy2(source, destination)
                copied[source] = destination.resolve().as_posix()
            clip["path"] = copied[source]
    draft = build(spec)
    path = os.path.join(args.out, "draft_content.json")
    data = (json.dumps(draft, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    if args.encrypt:
        try:
            from jy_draft_crypt import encrypt_bytes  # type: ignore
        except Exception as exc:  # pragma: no cover
            print("--encrypt 需要 Python 包 `cryptography`（pip install cryptography）: %s" % exc,
                  file=sys.stderr)
            return 1
        data = encrypt_bytes(data)
    with open(path, "wb") as fh:
        fh.write(data)
    root = Path(args.out).resolve()
    meta = {"draft_id": draft["id"], "draft_name": draft["name"],
            "draft_root_path": root.parent.as_posix(), "draft_fold_path": root.as_posix(),
            "draft_json_file": Path(path).resolve().as_posix(), "tm_duration": draft["duration"],
            "draft_materials": []}
    (root / "draft_meta_info.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps({"generator": "make_draft", "media_copied": args.copy_media,
        "encrypted": args.encrypt, "jianying_open_verified": False}, indent=2) + "\n", encoding="utf-8")
    print("OK 生成草稿: %s (%d 字节, clips=%d, encrypt=%s)" %
          (path, len(data), len(spec.get("clips", [])), args.encrypt))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
