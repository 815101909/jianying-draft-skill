#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量扫描草稿库：解密 → 解析 → 素材可用性统计。

用法:
    python scan_drafts.py <草稿库根目录> [--json out.json] [--limit N]

对每个含 draft_content.json 的目录，输出:
    解密/解析状态、画布、时长、片段数(视频/音频/文字)、素材可用/缺失
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import traceback
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, HERE)

import draft2ffmpeg as D  # noqa: E402


def probe_one(draft_dir: str, media_roots: List[str]) -> Dict[str, Any]:
    rec: Dict[str, Any] = {"dir": draft_dir, "name": os.path.basename(draft_dir.rstrip("/\\"))}
    try:
        fp = D.find_draft_file(draft_dir)
        rec["file"] = os.path.basename(fp)
        raw = open(fp, "rb").read()
        head = raw.strip()[:1]
        rec["plaintext"] = head in (b"{", b"[")
        draft = D.load_json_auto(fp)
    except Exception as e:
        rec["status"] = "DECRYPT_FAIL"
        rec["error"] = "%s: %s" % (type(e).__name__, e)
        return rec
    try:
        tl = D.DraftParser(os.path.dirname(os.path.abspath(fp)), draft,
                           media_roots=media_roots).parse()
    except Exception as e:
        rec["status"] = "PARSE_FAIL"
        rec["error"] = "%s: %s" % (type(e).__name__, e)
        return rec
    vids = [c for c in tl.clips if c.kind in ("video", "image")]
    auds = [c for c in tl.clips if c.kind == "audio"]
    txts = [c for c in tl.clips if c.kind == "text"]
    missing = [c for c in tl.clips if c.missing]
    total_dur = max((c.tgt_start + c.tgt_dur for c in tl.clips), default=0.0)
    gaps = D.analyze_gaps(tl)
    rec.update({
        "status": "OK",
        "canvas": "%dx%d" % (tl.canvas_w, tl.canvas_h),
        "fps": tl.fps,
        "declared_dur": round(tl.duration, 3),
        "span_dur": round(total_dur, 3),
        "clips": len(tl.clips),
        "videos": len(vids), "audios": len(auds), "texts": len(txts),
        "media_ok": len([c for c in tl.clips if not c.missing and c.kind != "text"]),
        "media_missing": len(missing),
        "gaps": len(gaps),
        "max_gap": round(max((g[2] for g in gaps), default=0.0), 1),
    })
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="草稿库根目录")
    ap.add_argument("--json", default=None, help="把结果写入 JSON")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--media-root", action="append", default=[])
    args = ap.parse_args()

    dirs = [d for d in sorted(glob.glob(os.path.join(args.root, "*")))
            if os.path.isfile(os.path.join(d, "draft_content.json"))]
    if args.limit:
        dirs = dirs[:args.limit]
    print("含 draft_content.json 的草稿: %d\n" % len(dirs))

    recs: List[Dict[str, Any]] = []
    counts = {"OK": 0, "DECRYPT_FAIL": 0, "PARSE_FAIL": 0}
    full_ok = 0
    for i, d in enumerate(dirs, 1):
        r = probe_one(d, args.media_root)
        recs.append(r)
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        if r["status"] == "OK":
            miss = r["media_missing"]
            ok = r["media_ok"]
            tag = "★全素材" if miss == 0 and (ok + miss) > 0 else ("缺失%d" % miss)
            if miss == 0 and (ok + miss) > 0:
                full_ok += 1
            print("[%3d] %-58s %-8s %-10s clips=%-4d v/a/t=%d/%d/%d ok=%d miss=%d gap=%d(%.0fs)" % (
                i, r["name"][:58], r["status"], tag, r["clips"],
                r["videos"], r["audios"], r["texts"], ok, miss, r["gaps"], r["max_gap"]))
        else:
            print("[%3d] %-58s %s  %s" % (i, r["name"][:58], r["status"], r.get("error", "")[:60]))

    print("\n=== 汇总 ===")
    print("总数=%d  OK=%d  DECRYPT_FAIL=%d  PARSE_FAIL=%d" %
          (len(recs), counts["OK"], counts["DECRYPT_FAIL"], counts["PARSE_FAIL"]))
    print("素材齐全(可完整导出)=%d" % full_ok)
    if args.json:
        json.dump(recs, open(args.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("结果已写入:", args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
