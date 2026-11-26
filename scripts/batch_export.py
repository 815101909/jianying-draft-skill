#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量导出草稿库：对目录下所有（或筛选后的）草稿逐个渲染为 mp4。

用法:
    python batch_export.py <草稿库根目录> --out-dir <输出目录> [选项]

选项:
    --only-complete        只导出素材齐全的草稿（默认导出全部，缺失素材的会跳过缺失片段）
    --min-dur SEC          只导出时长 >= SEC 的草稿
    --max-dur SEC          只导出时长 <= SEC 的草稿
    --limit N              最多导出 N 个（按名称排序）
    --name-contains S      只导出名称含 S 的草稿
    --range START:DUR      只渲染时间窗口（对所有草稿生效）
    --collapse-gaps SEC    压缩时间轴空档
    --preset P             默认 veryfast
    --crf N                默认 24
    --jobs N               并行数（默认 1）
    --dry-run              只打印将要执行的命令，不实际渲染

输出:
    <out-dir>/<草稿名>.mp4
    <out-dir>/_batch_report.json  （逐个结果）
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, HERE)

import draft2ffmpeg as D  # noqa: E402
import scan_drafts as S  # noqa: E402
import hashlib

BAD = re.compile(r'[\\/:*?"<>|\r\n\t]+')


def safe_name(s: str) -> str:
    s = BAD.sub("_", s).strip(" .")
    return s[:120] or "draft"


def output_name(record):
    identity = os.path.normcase(os.path.abspath(record["dir"]))
    suffix = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return safe_name(record["name"]) + "-" + suffix + ".mp4"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--only-complete", action="store_true")
    ap.add_argument("--min-dur", type=float, default=0.0)
    ap.add_argument("--max-dur", type=float, default=1e9)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--name-contains", default=None)
    ap.add_argument("--range", dest="window", default=None)
    ap.add_argument("--collapse-gaps", type=float, default=None)
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--crf", type=int, default=24)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--media-root", action="append", default=[])
    args = ap.parse_args()
    if args.jobs < 1 or args.limit < 0 or args.min_dur < 0 or args.max_dur < args.min_dur:
        ap.error("jobs must be >=1; durations/limit must be valid and nonnegative")

    os.makedirs(args.out_dir, exist_ok=True)
    dirs = [d for d in sorted(glob.glob(os.path.join(args.root, "*")))
            if os.path.isfile(os.path.join(d, "draft_content.json"))]

    # 预扫描（拿时长/素材信息）
    print("扫描 %d 个草稿…" % len(dirs))
    picked: List[Dict[str, Any]] = []
    parse_failures = []
    for d in dirs:
        r = S.probe_one(d, args.media_root)
        if r["status"] != "OK":
            parse_failures.append(r)
            continue
        if args.name_contains and args.name_contains not in r["name"]:
            continue
        if not (args.min_dur <= r["span_dur"] <= args.max_dur):
            continue
        if args.only_complete and not (r["media_missing"] == 0 and r["media_ok"] > 0):
            continue
        picked.append(r)
    if args.limit:
        picked = picked[:args.limit]
    print("选中 %d 个草稿待导出\n" % len(picked))

    def do_one(rec: Dict[str, Any]) -> Dict[str, Any]:
        out = os.path.join(args.out_dir, output_name(rec))
        cmd = [sys.executable, os.path.join(HERE, "draft2ffmpeg.py"),
               "--render", rec["dir"], "--out", out,
               "--preset", args.preset, "--crf", str(args.crf)]
        if args.strict:
            cmd.append("--strict")
        if args.overwrite:
            cmd.append("--overwrite")
        for root in args.media_root:
            cmd += ["--media-root", root]
        if args.window:
            cmd += ["--range", args.window]
        if args.collapse_gaps is not None:
            cmd += ["--collapse-gaps", str(args.collapse_gaps)]
        t0 = time.time()
        if args.dry_run:
            return {"name": rec["name"], "out": out, "status": "DRY", "cmd": " ".join(cmd)}
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        except OSError as exc:
            return {"name": rec["name"], "out": out, "status": "FAIL", "rc": 1, "sec": round(time.time()-t0, 1), "size": 0, "err": str(exc)}
        dt = time.time() - t0
        ok = p.returncode == 0 and os.path.isfile(out) and os.path.getsize(out) > 1024
        return {
            "name": rec["name"], "out": out,
            "status": "OK" if ok else "FAIL",
            "rc": p.returncode, "sec": round(dt, 1),
            "size": os.path.getsize(out) if os.path.isfile(out) else 0,
            "err": "" if ok else (p.stderr or p.stdout or "")[-400:],
        }

    results: List[Dict[str, Any]] = []
    if args.jobs > 1:
        with cf.ThreadPoolExecutor(max_workers=args.jobs) as ex:
            for r in ex.map(do_one, picked):
                results.append(r)
                print("[%s] %s (%.1fs, %dKB)" % (r["status"], r["name"][:56],
                      r.get("sec", 0), r.get("size", 0) // 1024))
    else:
        for i, rec in enumerate(picked, 1):
            r = do_one(rec)
            results.append(r)
            print("[%2d/%d][%s] %s (%.1fs, %dKB)" % (
                i, len(picked), r["status"], r["name"][:56],
                r.get("sec", 0), r.get("size", 0) // 1024))

    ok = sum(1 for r in results if r["status"] == "OK")
    print("\n=== 批量导出汇总 ===")
    print("尝试=%d  成功=%d  失败=%d  未选中=%d" %
          (len(results), ok, sum(1 for r in results if r["status"] == "FAIL"),
           len(dirs) - len(picked)))
    rep = os.path.join(args.out_dir, "_batch_report.json")
    with open(rep, "w", encoding="utf-8") as fh:
        json.dump({"results": results, "parse_failures": parse_failures,
                   "unselected_count": len(dirs)-len(picked)}, fh, ensure_ascii=False, indent=2)
    print("报告:", rep)
    return 2 if parse_failures or any(r["status"] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
