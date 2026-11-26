#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剪映 / CapCut 草稿 → ffmpeg 无头渲染器（不启动剪映）

功能:
  - 自动识别并解密「映映」加密草稿（复用 scripts/decrypt/jy_draft_crypt.py）
  - 解析 draft_content.json：canvas / tracks / segments / materials
  - 展开「复合片段」(combination)：segment.extra_material_refs 指向 materials.drafts[i].draft
  - 时间轴换算：source_timerange / target_timerange / speed
  - 生成 ffmpeg filter_complex：视频轨(裁剪/变速/缩放/位移) + 图片 + 音频(音量/淡入淡出) + 文字(ASS 字幕)
  - --info 打印时间轴、--probe 检查素材存在性、--dry-run 只打印命令、--render 实际渲染

用法:
  python draft2ffmpeg.py --info   <草稿目录或 draft_content.json>
  python draft2ffmpeg.py --probe  <草稿>
  python draft2ffmpeg.py --dry-run <草稿> --out out.mp4
  python draft2ffmpeg.py --render <草稿> --out out.mp4 [--fit contain|cover|stretch] [--preset veryfast] [--crf 20]
  python draft2ffmpeg.py --render <草稿> --out out.mp4 --range 0:20          # 只渲染 0~20s
  python draft2ffmpeg.py --render <草稿> --out out.mp4 --collapse-gaps 0     # 消除时间轴空档

时间单位: 剪映内部一律为「微秒」(1e6 = 1 秒)。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, replace
from render_validation import unsupported_features, probe_media
from typing import Any, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:  # 首选：纯 Python 实现（需要 `cryptography`）
    from jy_draft_crypt import decrypt_bytes, looks_encrypted  # type: ignore
except Exception:  # pragma: no cover - 回退到 skill 自带的 Go 解密器
    decrypt_bytes = None  # type: ignore
    looks_encrypted = None  # type: ignore

_GO_HELPER: Optional[str] = None


def _go_decrypt(path: str) -> bytes:
    """回退路径：编译并调用 skill 自带的 decrypt_yingying_json.go。"""
    global _GO_HELPER
    src = os.path.join(HERE, "decrypt_yingying_json.go")
    if not os.path.isfile(src):
        raise RuntimeError("映映解密需要 Python `cryptography` 或 scripts/decrypt_yingying_json.go")
    if _GO_HELPER is None or not os.path.isfile(_GO_HELPER) \
            or os.path.getmtime(_GO_HELPER) < os.path.getmtime(src):
        exe = os.path.join(tempfile.gettempdir(), "codex-jianying-decrypt-yingying.exe")
        subprocess.run(["go", "build", "-o", exe, src], check=True, capture_output=True)
        _GO_HELPER = exe
    return subprocess.run([_GO_HELPER, path], check=True, capture_output=True).stdout

US = 1_000_000  # 微秒/秒
PLACEHOLDER_RE = re.compile(r"##_draftpath_placeholder_[0-9A-Fa-f-]+_##")
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv", ".ts", ".wmv", ".mts"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tif", ".tiff", ".heic"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma", ".opus"}


# --------------------------------------------------------------------------- #
# 加载 / 解密
# --------------------------------------------------------------------------- #
def load_json_auto(path: str) -> Any:
    """读取 JSON；若是映映加密格式则自动解密（Python 优先，Go 回退）。"""
    with open(path, "rb") as fh:
        raw = fh.read()
    stripped = raw.strip()
    if stripped[:1] in (b"{", b"["):
        return json.loads(raw.decode("utf-8"))
    if looks_encrypted is None:  # 无 cryptography：直接交给 Go 解密器
        return json.loads(_go_decrypt(path).decode("utf-8"))
    if looks_encrypted(raw):
        return json.loads(decrypt_bytes(raw).decode("utf-8"))  # type: ignore
    return json.loads(raw.decode("utf-8-sig"))


def find_draft_file(path: str) -> str:
    if os.path.isfile(path):
        return path
    cand = os.path.join(path, "draft_content.json")
    if os.path.isfile(cand):
        return cand
    raise FileNotFoundError("未找到 draft_content.json: %s" % path)


def resolve_media(p: Optional[str], draft_dir: str,
                  extra_roots: Optional[List[str]] = None) -> Optional[str]:
    """把草稿里的 path 解析成真实绝对路径；解析不到返回 None。

    extra_roots: 备用根目录（用于「解密镜像 + 原始媒体目录」组合场景）。
    """
    if not p:
        return None
    p = p.replace("\\", "/")
    roots = [draft_dir.replace("\\", "/")] + [r.replace("\\", "/") for r in (extra_roots or [])]
    for root in roots:
        cand = PLACEHOLDER_RE.sub(root, p)
        if os.path.isfile(cand):
            return os.path.normpath(cand)
    # 退化：按文件名在草稿目录 materials/ 下查找
    base = os.path.basename(p)
    if base:
        for root in roots:
            for sub in ("materials/video", "materials/audio", "materials", "Resources/local", "Resources"):
                cand = os.path.join(root, sub, base)
                if os.path.isfile(cand):
                    return os.path.normpath(cand)
    return None


# --------------------------------------------------------------------------- #
# 数据模型
# --------------------------------------------------------------------------- #
@dataclass
class Clip:
    kind: str                      # video | image | audio | text
    path: Optional[str]            # 媒体真实路径（text 为 None）
    src_start: float = 0.0         # 源内起点(秒)
    src_dur: float = 0.0           # 源内时长(秒)
    tgt_start: float = 0.0         # 时间轴起点(秒)
    tgt_dur: float = 0.0           # 时间轴时长(秒)
    speed: float = 1.0
    volume: float = 1.0
    scale: Tuple[float, float] = (1.0, 1.0)
    transform: Tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0
    alpha: float = 1.0
    crop: Optional[Dict[str, float]] = None
    text: Optional[str] = None
    text_px: float = 48.0
    text_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_w: float = 0.0
    track_index: int = 0
    seg_id: str = ""
    material_name: str = ""
    missing: bool = False


@dataclass
class Timeline:
    canvas_w: int = 1920
    canvas_h: int = 1080
    fps: float = 30.0
    duration: float = 0.0
    clips: List[Clip] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def videos(self) -> List[Clip]:
        return [c for c in self.clips if c.kind in ("video", "image")]

    @property
    def audios(self) -> List[Clip]:
        return [c for c in self.clips if c.kind == "audio"]

    @property
    def texts(self) -> List[Clip]:
        return [c for c in self.clips if c.kind == "text"]

    @property
    def max_end(self) -> float:
        return max((c.tgt_start + c.tgt_dur for c in self.clips), default=0.0)


def _us(v: Any) -> float:
    try:
        return float(v) / US
    except (TypeError, ValueError):
        return 0.0


def _timerange(seg: Dict[str, Any], key: str) -> Tuple[float, float]:
    tr = seg.get(key) or {}
    return _us(tr.get("start", 0)), _us(tr.get("duration", 0))


def analyze_gaps(tl: Timeline) -> List[Tuple[float, float, float]]:
    """返回时间轴上大于 1s 的空档列表 [(gap_start, gap_end, gap_seconds), ...]。"""
    ivs = sorted((c.tgt_start, c.tgt_start + c.tgt_dur) for c in tl.clips if c.tgt_dur > 0.0)
    out: List[Tuple[float, float, float]] = []
    if not ivs:
        return out
    _, ce = ivs[0]
    for s, e in ivs[1:]:
        if s - ce > 1.0:
            out.append((ce, s, s - ce))
        ce = max(ce, e)
    return out


def collapse_gaps(tl: Timeline, threshold: float = 0.0) -> float:
    """把所有大于 threshold 秒的簇间空档压缩到 threshold 秒，返回压缩掉的总时长。"""
    ivs = sorted((c.tgt_start, c.tgt_start + c.tgt_dur) for c in tl.clips if c.tgt_dur > 0.0)
    if len(ivs) < 2:
        return 0.0
    clusters: List[List[float]] = []  # [start, end, shift]
    cs, ce = ivs[0]
    for s, e in ivs[1:]:
        if s - ce > threshold:
            clusters.append([cs, ce, 0.0])
            cs, ce = s, e
        else:
            ce = max(ce, e)
    clusters.append([cs, ce, 0.0])
    if len(clusters) < 2:
        return 0.0
    removed = 0.0
    for i in range(1, len(clusters)):
        prev, cur = clusters[i - 1], clusters[i]
        new_start = (prev[1] - prev[2]) + threshold
        cur[2] = cur[0] - new_start
        removed += cur[2]

    def shift_of(t: float) -> float:
        for cs2, ce2, sh in clusters:
            if cs2 - 1e-6 <= t <= ce2 + 1e-6:
                return sh
        for cs2, _ce2, sh in clusters:
            if t < cs2:
                return sh
        return clusters[-1][2]

    for c in tl.clips:
        c.tgt_start = max(0.0, c.tgt_start - shift_of(c.tgt_start))
    tl.duration = tl.max_end
    return removed


def apply_window(tl: Timeline, start: float, dur: float) -> None:
    """裁剪到 [start, start+dur] 时间窗口，并把窗口起点对齐到 0。"""
    end = start + dur
    kept: List[Clip] = []
    for c in tl.clips:
        cs, ce = c.tgt_start, c.tgt_start + c.tgt_dur
        if ce <= start + 1e-6 or cs >= end - 1e-6:
            continue
        head = max(cs, start) - cs          # 被裁掉的前段（秒）
        c.src_start += head * c.speed
        c.tgt_start = max(cs, start) - start
        c.tgt_dur = (min(ce, end) - max(cs, start))
        kept.append(c)
    tl.clips = kept
    tl.duration = dur


def _rgb(hexstr: str) -> Tuple[int, int, int]:
    h = (hexstr or "#FFFFFF").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except Exception:
        return 255, 255, 255


class DraftParser:
    def __init__(self, draft_dir: str, draft: Dict[str, Any],
                 media_roots: Optional[List[str]] = None):
        self.dir = draft_dir
        self.draft = draft
        self.media_roots = media_roots or []
        self.notes: List[str] = []

    # --- material 索引 ---------------------------------------------------- #
    def _index(self, mats: Dict[str, Any]) -> Dict[str, Tuple[str, Dict[str, Any]]]:
        idx: Dict[str, Tuple[str, Dict[str, Any]]] = {}
        for grp, lst in (mats or {}).items():
            if isinstance(lst, list):
                for it in lst:
                    if isinstance(it, dict) and it.get("id"):
                        idx[it["id"]] = (grp, it)
        return idx

    def parse(self, tgt_offset: float = 0.0, src_offset: float = 0.0,
              depth: int = 0) -> Timeline:
        d = self.draft
        canvas = d.get("canvas_config") or {}
        tl = Timeline(
            canvas_w=int(canvas.get("width") or 0),
            canvas_h=int(canvas.get("height") or 0),
            fps=float(d.get("fps") or 0) or 30.0,
            duration=_us(d.get("duration", 0)),
        )
        idx = self._index(d.get("materials") or {})

        tracks = d.get("tracks") or []
        # 轨道自下而上：render_index / 列表顺序
        for ti, track in enumerate(tracks):
            ttype = track.get("type")
            for seg in track.get("segments") or []:
                self._emit(tl, idx, ti, ttype, seg, tgt_offset, src_offset, depth)
        tl.notes.extend(self.notes)
        return tl

    def _emit(self, tl: Timeline, idx, ti, ttype, seg, tgt_offset, src_offset, depth):
        if seg.get("visible") is False:
            return
        mid = seg.get("material_id")
        grp, mat = idx.get(mid, (None, None))
        extra = seg.get("extra_material_refs") or []
        if grp == "drafts" and mat and isinstance(mat.get("draft"), dict):
            self._emit_compound(tl, mat["draft"], seg, tgt_offset, src_offset, depth)
            return

        # ---- 复合片段：extra_refs 指向 materials.drafts[i].draft -------------
        for r in extra:
            g, m = idx.get(r, (None, None))
            if g == "drafts" and m and isinstance(m.get("draft"), dict):
                self._emit_compound(tl, m["draft"], seg, tgt_offset, src_offset, depth)
                return

        s_start, s_dur = _timerange(seg, "source_timerange")
        t_start, t_dur = _timerange(seg, "target_timerange")
        if t_dur <= 0:
            t_dur = s_dur
        clip = seg.get("clip") or {}
        cscale = clip.get("scale") or {}
        ctrans = clip.get("transform") or {}

        speed = 1.0
        for r in extra:
            g, m = idx.get(r, (None, None))
            if g == "speeds" and m:
                speed = float(m.get("speed") or 1.0)

        vol = seg.get("volume")
        vol = 1.0 if vol is None else float(vol)

        common = dict(
            src_start=s_start, src_dur=s_dur,
            tgt_start=t_start + tgt_offset, tgt_dur=t_dur,
            speed=speed, volume=vol,
            scale=(float(cscale.get("x", 1.0)), float(cscale.get("y", 1.0))),
            transform=(float(ctrans.get("x", 0.0)), float(ctrans.get("y", 0.0))),
            rotation=float(clip.get("rotation") or 0.0),
            alpha=float(clip.get("alpha", 1.0) if clip.get("alpha") is not None else 1.0),
            crop=(mat or {}).get("crop") or seg.get("crop") or None,
            track_index=ti, seg_id=str(seg.get("id") or ""),
        )

        if grp == "texts" and mat:
            c = mat.get("content")
            txt = ""
            styles = []
            if isinstance(c, str):
                try:
                    obj = json.loads(c)
                    txt = obj.get("text", "")
                    styles = obj.get("styles") or []
                except Exception:
                    txt = c
            st = styles[0] if styles else {}
            size = float(st.get("size") or mat.get("font_size") or 6.0)
            # 剪映字号 → 像素（近似映射，可用 --text-scale 调整）
            px = size * 4.0 * (tl.canvas_h / 1920.0)
            fill = (((st.get("fill") or {}).get("content") or {}).get("solid") or {}).get("color")
            color = mat.get("text_color") or "#FFFFFF"
            if fill:
                color = "#%02X%02X%02X" % tuple(int(max(0, min(1, v)) * 255) for v in fill)
            tl.clips.append(Clip(kind="text", path=None, text=txt, text_px=px,
                                 text_color=color, stroke_color=mat.get("border_color") or "#000000",
                                 stroke_w=float(mat.get("border_width") or 0.0) * 100,
                                 material_name=mat.get("name") or "", **common))
            return

        if grp in ("videos", "images") and mat:
            p = resolve_media(mat.get("path"), self.dir, self.media_roots)
            kind = "image" if (grp == "images" or os.path.splitext(p or mat.get("path") or "")[1].lower() in IMAGE_EXT) else "video"
            if not p:
                tl.notes.append("素材缺失: %s (%s)" % (mat.get("material_name") or mat.get("path"), mat.get("id")))
            tl.clips.append(Clip(kind=kind, path=p, missing=p is None,
                                 material_name=mat.get("material_name") or "", **common))
            return

        if grp == "audios" and mat:
            p = resolve_media(mat.get("path"), self.dir, self.media_roots)
            if not p:
                tl.notes.append("音频缺失: %s (%s)" % (mat.get("name") or mat.get("path"), mat.get("id")))
            tl.clips.append(Clip(kind="audio", path=p, missing=p is None,
                                 material_name=mat.get("name") or "", **common))
            return

        if grp:
            self.notes.append("未处理的素材类型: track=%s material=%s" % (ttype, grp))

    def _emit_compound(self, tl: Timeline, inner: Dict[str, Any], seg: Dict[str, Any],
                       tgt_offset: float, src_offset: float, depth: int) -> None:
        if depth > 8:
            tl.notes.append("复合片段嵌套过深，已停止展开")
            return
        s_start, s_dur = _timerange(seg, "source_timerange")
        t_start, t_dur = _timerange(seg, "target_timerange")
        sub = DraftParser(self.dir, inner, self.media_roots).parse(
            tgt_offset=tgt_offset + t_start - s_start,
            src_offset=src_offset,
            depth=depth + 1,
        )
        if sub.canvas_w and not tl.canvas_w:
            tl.canvas_w, tl.canvas_h = sub.canvas_w, sub.canvas_h
        tl.notes.extend(sub.notes)
        # 复合片段内的 clips 已被偏移到外层时间轴
        for c in sub.clips:
            c.track_index = seg.get("track_render_index", c.track_index)
            tl.clips.append(c)


# --------------------------------------------------------------------------- #
# ffmpeg 命令构建
# --------------------------------------------------------------------------- #
def esc_filter_path(p: str) -> str:
    """ffmpeg filter 参数里的路径转义（Windows 盘符冒号 + 反斜杠）。"""
    q = p.replace("\\", "/")
    q = q.replace(":", "\\:")
    q = q.replace("'", r"\'")
    return q


def build_ass(texts: List[Clip], w: int, h: int, path: str) -> None:
    def ts(t: float) -> str:
        if t < 0:
            t = 0
        cs = int(round((t - int(t)) * 100))
        s = int(t)
        return "%d:%02d:%02d.%02d" % (s // 3600, (s % 3600) // 60, s % 60, cs)

    def col(c: str) -> str:
        r, g, b = _rgb(c)
        return "&H%02X%02X%02X" % (b, g, r)  # ASS 是 BGR

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: %d" % w,
        "PlayResY: %d" % h,
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: D,Microsoft YaHei,{fs},{pc},&H000000FF,{oc},&H80000000,0,0,0,0,100,100,0,0,"
        "1,{ow},1,5,10,10,10,1".format(fs=int(round(texts[0].text_px)) if texts else 48,
                                      pc=col(texts[0].text_color) if texts else "&HFFFFFF",
                                      oc=col(texts[0].stroke_color) if texts else "&H000000",
                                      ow=max(0, int(round(texts[0].stroke_w))) if texts else 2),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for c in sorted(texts, key=lambda x: x.tgt_start):
        x = (c.transform[0] + 1.0) / 2.0 * w
        y = (1.0 - c.transform[1]) / 2.0 * h          # 剪映 y 向上为正
        txt = (c.text or "").replace("\n", r"\N")
        over = r"{\an5\pos(%.0f,%.0f)\fs%d\1c%s\3c%s\bord%d}" % (
            x, y, int(round(c.text_px)), col(c.text_color), col(c.stroke_color),
            max(0, int(round(c.stroke_w))),
        )
        lines.append("Dialogue: 0,%s,%s,D,,0,0,0,,%s%s" % (
            ts(c.tgt_start), ts(c.tgt_start + c.tgt_dur), over, txt))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def build_command(tl: Timeline, out_path: str, *, fit: str = "contain",
                  crf: int = 20, preset: str = "medium", text_scale: float = 1.0,
                  ffmpeg: str = "ffmpeg", ass_path: Optional[str] = None,
                  progress: bool = True) -> Tuple[List[str], List[str]]:
    W = tl.canvas_w or 1920
    H = tl.canvas_h or 1080
    # libx264/yuv420p 要求宽高为偶数；剪映画布可能是奇数（如 1920x1447），
    # 向上对齐到偶数，避免 "height not divisible by 2"。
    if W % 2:
        W += 1
    if H % 2:
        H += 1
    FPS = tl.fps or 30.0
    total = tl.duration or tl.max_end

    inputs: List[str] = []
    filters: List[str] = []
    warnings: List[str] = []
    vlabel_seq: List[str] = []
    n_in = 0  # 输入序号（与 argv token 数无关，避免图片输入多 token 导致错位）

    # 背景画布
    filters.append("color=c=black:s=%dx%d:r=%s:d=%.6f,format=yuv420p[bg]" % (W, H, FPS, total))
    cur = "bg"

    # --- 视频 / 图片 ------------------------------------------------------- #
    vclips = sorted(tl.videos, key=lambda c: (c.track_index, c.tgt_start))
    for i, c in enumerate(vclips):
        if c.missing or not c.path:
            warnings.append("跳过缺失视频: %s" % (c.material_name or c.seg_id))
            continue
        if c.kind == "image":
            inputs += ["-loop", "1", "-t", "%.6f" % max(c.tgt_dur, 0.04), "-i", c.path]
        else:
            inputs += ["-i", c.path]
        src = "%d:v" % n_in
        n_in += 1
        chain = []
        if c.kind == "video":
            st = max(0.0, c.src_start)
            en = st + max(c.src_dur, 0.001)
            chain.append("trim=start=%.6f:end=%.6f" % (st, en))
            chain.append("setpts=(PTS-STARTPTS)/%.6f" % max(c.speed, 0.01))
        else:
            chain.append("setpts=PTS-STARTPTS")
        if fit == "stretch":
            chain.append("scale=%d:%d" % (W, H))
        elif fit == "cover":
            chain.append("scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (W, H, W, H))
        else:
            chain.append("scale=%d:%d:force_original_aspect_ratio=decrease" % (W, H))
        sx, sy = c.scale
        if abs(sx - 1.0) > 1e-6 or abs(sy - 1.0) > 1e-6:
            chain.append("scale=iw*%.6f:ih*%.6f" % (max(sx, 0.01), max(sy, 0.01)))
        chain.append("setsar=1")
        chain.append("format=rgba")
        chain.append("fps=%s" % FPS)
        # 放到时间轴正确位置
        chain.append("setpts=PTS+%.6f/TB" % max(0.0, c.tgt_start))
        if c.alpha < 0.999:
            chain.append("colorchannelmixer=aa=%.4f" % max(0.0, c.alpha))
        lab = "v%d" % i
        filters.append("[%s]%s[%s]" % (src, ",".join(chain), lab))
        # 叠加到画布
        ox = (W - W) / 2 + c.transform[0] * W / 2.0
        oy = (H - H) / 2 - c.transform[1] * H / 2.0
        nl = "ov%d" % i
        filters.append(
            "[%s][%s]overlay=x='%.4f+(W-w)/2':y='%.4f+(H-h)/2':eof_action=pass:"
            "enable='between(t,%.6f,%.6f)'[%s]" % (
                cur, lab, ox, oy, max(0.0, c.tgt_start),
                c.tgt_start + c.tgt_dur + 1e-3, nl)
        )
        cur = nl
        vlabel_seq.append(lab)

    # --- 文字（ASS） ------------------------------------------------------- #
    if tl.texts:
        ass = ass_path or os.path.splitext(os.path.abspath(out_path))[0] + ".subs.ass"
        build_ass([replace(c, text_px=c.text_px * text_scale) for c in tl.texts], W, H, ass)
        filters.append("[%s]subtitles='%s'[vtxt]" % (cur, esc_filter_path(ass)))
        cur = "vtxt"

    # --- 音频 -------------------------------------------------------------- #
    alabels: List[str] = []
    for i, c in enumerate(tl.audios):
        if c.missing or not c.path:
            warnings.append("跳过缺失音频: %s" % (c.material_name or c.seg_id))
            continue
        idx = n_in
        inputs += ["-i", c.path]
        n_in += 1
        st = max(0.0, c.src_start)
        en = st + max(c.src_dur, 0.001)
        chain = ["atrim=start=%.6f:end=%.6f" % (st, en), "asetpts=PTS-STARTPTS"]
        if abs(c.speed - 1.0) > 1e-6:
            remaining = max(c.speed, 0.01)
            while remaining > 2:
                chain.append("atempo=2")
                remaining /= 2
            while remaining < 0.5:
                chain.append("atempo=0.5")
                remaining /= 0.5
            chain.append("atempo=%.6f" % remaining)
        if abs(c.volume - 1.0) > 1e-6:
            chain.append("volume=%.4f" % max(0.0, c.volume))
        chain.append("adelay=%d|%d" % (int(c.tgt_start * 1000), int(c.tgt_start * 1000)))
        lab = "a%d" % i
        filters.append("[%d:a]%s[%s]" % (idx, ",".join(chain), lab))
        alabels.append(lab)

    amap: Optional[str] = None
    if alabels:
        if len(alabels) == 1:
            amap = alabels[0]
        else:
            filters.append("".join("[%s]" % a for a in alabels) +
                           "amix=inputs=%d:normalize=0:dropout_transition=0[amix]" % len(alabels))
            amap = "amix"

    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "warning" if not progress else "info"]
    cmd += inputs
    cmd += ["-filter_complex", ";".join(filters), "-map", "[%s]" % cur]
    if amap:
        cmd += ["-map", "[%s]" % amap, "-c:a", "aac", "-b:a", "192k"]
    cmd += [
        "-t", "%.6f" % total,
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        out_path,
    ]
    return cmd, warnings


# --------------------------------------------------------------------------- #
# 展示
# --------------------------------------------------------------------------- #
def print_info(tl: Timeline) -> None:
    print("画布: %dx%d  fps=%s  时长=%.3fs  时间轴末端=%.3fs" %
          (tl.canvas_w, tl.canvas_h, tl.fps, tl.duration, tl.max_end))
    print("片段总数: %d  (视频/图片=%d 音频=%d 文字=%d)" %
          (len(tl.clips), len(tl.videos), len(tl.audios), len(tl.texts)))
    gaps = analyze_gaps(tl)
    if gaps:
        big = [g for g in gaps if g[2] > 30.0]
        print("时间轴空档: %d 处 (其中 >30s 的 %d 处，最大 %.1fs)" %
              (len(gaps), len(big), max(g[2] for g in gaps)))
    print("-" * 78)
    for c in sorted(tl.clips, key=lambda x: (x.track_index, x.tgt_start)):
        tag = {"video": "V", "image": "I", "audio": "A", "text": "T"}[c.kind]
        flag = " [缺失]" if c.missing else ""
        name = (c.material_name or c.text or "")[:26]
        print("  %s t=%8.3f→%8.3f  src=%8.3f+%-8.3f spd=%-5.2f vol=%-5.2f %s%s" %
              (tag, c.tgt_start, c.tgt_start + c.tgt_dur, c.src_start, c.src_dur,
               c.speed, c.volume, name, flag))
    if tl.notes:
        print("-" * 78)
        for n in tl.notes:
            print("  ! " + n)


def main() -> int:
    ap = argparse.ArgumentParser(description="剪映草稿 → ffmpeg 无头渲染器")
    ap.add_argument("draft", help="草稿目录或 draft_content.json")
    ap.add_argument("--out", default="out.mp4")
    ap.add_argument("--info", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--fit", choices=["contain", "cover", "stretch"], default="contain")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--text-scale", type=float, default=1.0)
    ap.add_argument("--range", dest="window", default=None,
                    help="只渲染时间窗口 START:DUR（秒），如 0:20 或 1685:30")
    ap.add_argument("--collapse-gaps", type=float, default=None, metavar="SEC",
                    help="把 >SEC 秒的时间轴空档压缩到 SEC 秒（默认 0 = 全部消除）")
    ap.add_argument("--media-root", action="append", default=None, metavar="DIR",
                    help="备用素材根目录（可多次指定；用于解密镜像 + 原始媒体目录）")
    ap.add_argument("--ffmpeg", default="ffmpeg")
    ap.add_argument("--ffprobe", default="ffprobe")
    ap.add_argument("--strict", action="store_true", help="缺失/损坏素材或未支持能力时停止")
    ap.add_argument("--report", help="JSON 检查/渲染报告路径")
    ap.add_argument("--overwrite", action="store_true", help="允许覆盖已有输出视频")
    args = ap.parse_args()
    if args.text_scale <= 0 or not 0 <= args.crf <= 51:
        ap.error("text-scale must be positive; crf must be 0..51")
    if args.render and os.path.exists(args.out) and not args.overwrite:
        ap.error("output exists; choose a new path or use --overwrite")
    if args.render or args.dry_run:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    fp = find_draft_file(args.draft)
    draft_dir = os.path.dirname(os.path.abspath(fp))
    draft = load_json_auto(fp)
    tl = DraftParser(draft_dir, draft, media_roots=args.media_root).parse()
    report = {"draft": fp, "unsupported_features": unsupported_features(draft),
              "missing_media": [{"segment": c.seg_id, "name": c.material_name} for c in tl.clips if c.missing],
              "invalid_media": [], "notes": tl.notes, "status": "checked"}
    report_path = args.report or (args.out + ".render-report.json" if args.render else None)
    def save_report():
        if report_path:
            os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, ensure_ascii=False, indent=2)
    if args.probe or args.strict or args.render:
        report["invalid_media"] = probe_media(tl, args.ffprobe)
    for item in report["unsupported_features"]:
        print("WARN: unsupported " + json.dumps(item, ensure_ascii=False), file=sys.stderr)
    for item in report["invalid_media"]:
        print("ERROR: invalid media " + json.dumps(item, ensure_ascii=False), file=sys.stderr)
    if report["invalid_media"] or (args.strict and (report["missing_media"] or report["unsupported_features"] or tl.notes)):
        report["status"] = "blocked"
        save_report()
        return 2

    if args.collapse_gaps is not None:
        removed = collapse_gaps(tl, max(0.0, args.collapse_gaps))
        print("空档折叠: 压缩掉 %.3fs 空隙 -> 时间轴 %.3fs" % (removed, tl.max_end),
              file=sys.stderr)

    if args.window:
        try:
            a, b = args.window.split(":", 1)
            if float(a) < 0 or float(b) <= 0:
                raise ValueError("START must be nonnegative and DUR must be positive")
            apply_window(tl, float(a), float(b))
            print("时间窗口: 起点=%.3fs 时长=%.3fs" % (float(a), float(b)), file=sys.stderr)
        except Exception as e:
            print("--range 解析失败（应为 START:DUR）: %s" % e, file=sys.stderr)
            return 2

    if args.info or not (args.probe or args.dry_run or args.render):
        print_info(tl)

    if args.probe:
        miss = [c for c in tl.clips if c.missing]
        ok = [c for c in tl.clips if not c.missing and c.path]
        print("素材检查: 可用=%d 缺失=%d" % (len(ok), len(miss)))
        for c in miss:
            print("  MISSING %s (%s)" % (c.material_name or c.seg_id, c.kind))
        if tl.notes:
            for n in tl.notes:
                print("  ! " + n)

    if args.dry_run or args.render:
        cmd, warns = build_command(tl, os.path.abspath(args.out), fit=args.fit,
                                   crf=args.crf, preset=args.preset,
                                   text_scale=args.text_scale, ffmpeg=args.ffmpeg)
        for w in warns:
            print("WARN: " + w, file=sys.stderr)
        print(" ".join(("'%s'" % a if " " in a else a) for a in cmd))
        if args.render:
            if not shutil.which(args.ffmpeg) and not os.path.isfile(args.ffmpeg):
                print("找不到 ffmpeg: %s" % args.ffmpeg, file=sys.stderr)
                report["status"] = "failed"
                report["error"] = "ffmpeg not found"
                save_report()
                return 3
            print("--- 开始渲染 ---", file=sys.stderr)
            rc = subprocess.call(cmd)
            report["status"] = ("rendered_with_limitations" if report["unsupported_features"] or report["missing_media"] else "rendered") if rc == 0 else "failed"
            report["ffmpeg_exit_code"] = rc
            report["warnings"] = warns
            save_report()
            print("--- 渲染结束 rc=%d -> %s ---" % (rc, args.out), file=sys.stderr)
            return rc
    save_report()
    return 2 if args.probe and report["missing_media"] else 0


if __name__ == "__main__":
    sys.exit(main())
