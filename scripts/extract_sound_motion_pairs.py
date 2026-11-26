#!/usr/bin/env python3
import argparse
import collections
import json
import re
import subprocess
import tempfile
from pathlib import Path


FAMILY_RULES = [
    ("money_value", ("收银", "钱", "金币", "硬币", "到账", "money", "cash", "coin")),
    ("suspense_texture", ("紧张", "悬疑", "心跳", "诡异", "不对劲", "恐怖", "压迫", "发条", "suspense")),
    ("bell_chime", ("响铃", "风铃", "铃铛", "亮铃", "颂钵", "木鱼", "敲锣", "当当")),
    ("transition_reveal", ("转场", "扫光", "闪现", "突然出现", "亮一下", "刷一下", "旋风", "光效", "烟尘", "页面切换")),
    ("bubble_stamp", ("气泡", "盖章", "弹簧", "字幕音效震撼出场")),
    ("mechanical_weapon", ("枪", "拉栓", "拔刀", "宝剑", "出鞘", "匕首", "刀光", "刀砍", "刀子")),
    ("retro_media", ("胶片", "磁带", "录音机", "投影仪", "倒带", "快进")),
    ("technology_ui", ("高科技", "系统音", "电子", "故障", "扫描", "雷达", "off")),
    ("emotion_human", ("哭泣", "婴儿", "心碎", "笑声", "欢呼", "掌声")),
    ("ambient_foley", ("汽车", "引擎", "车辆", "脚步", "环境", "风声", "雨声", "开门")),
    ("comedy_variety", ("综艺", "沙锤", "尴尬", "疑惑", "无奈", "放屁", "玩具鸭", "青蛙", "tom鼓", "戏剧锣鼓")),
    ("typing_texture", ("打字", "键盘", "typewriter", "typing")),
    ("whoosh_slide", ("呼", "唰", "嗖", "咻", "whoosh", "swish")),
    ("ui_notification", ("提示", "叮", "滴", "点击", "鼠标", "click", "notification")),
    ("impact", ("咚", "撞击", "重拳", "拳", "boom", "impact", "hit")),
    ("premium_magic", ("仙尘", "闪光", "星光", "水滴", "sparkle", "magic")),
    ("paper_page", ("纸张", "翻页", "纸", "page", "paper")),
    ("risk_break", ("错误", "玻璃", "破碎", "悬疑", "error", "break")),
    ("camera_scene", ("快门", "相机", "闪回", "开门", "camera", "door")),
    ("time_tick", ("时钟", "滴答", "嘀嗒", "tick", "clock")),
    ("pop_cartoon", ("啵", "卡通", "跳跃", "pop", "cartoon")),
]

SCENE_RULES = [
    ("cta", ("联系", "私信", "咨询", "关注", "点赞", "评论", "领取", "报名", "下期", "找我", "点击")),
    ("proof_or_number", ("数据", "案例", "增长", "营收", "利润", "客户", "倍", "%", "万", "亿", "+")),
    ("method_step", ("第一", "第二", "第三", "步骤", "方法", "首先", "其次", "最后", "第1", "第2", "第3")),
    ("conflict_or_warning", ("不要", "不能", "错误", "失败", "风险", "骗局", "上当", "难", "问题", "痛苦", "消耗", "危机")),
    ("comparison_or_switch", ("但是", "然而", "区别", "对比", "相反", "不是", "而是", "从", "到", "比")),
    ("identity_or_authority", ("老板", "创始人", "专家", "老师", "客户", "普通人", "打工人", "企业", "团队")),
    ("solution_or_result", ("解决", "方法", "答案", "提效", "变现", "结果", "所以", "应该", "可以", "实现", "机会")),
    ("question_or_suspense", ("为什么", "怎么", "到底", "真的", "吗", "？", "?")),
    ("emotion_or_reflection", ("觉得", "感受", "回忆", "曾经", "幸福", "难过", "遗憾", "人生", "关系")),
]


def classify(name):
    lowered = name.lower()
    for family, needles in FAMILY_RULES:
        if any(needle.lower() in lowered for needle in needles):
            return family
    return "specific_foley"


def classify_scene(text, start):
    compact = re.sub(r"\s+", "", text or "")
    if start < 3_000_000:
        return "opening_hook"
    if re.search(r"\d", compact):
        return "proof_or_number"
    for scene, needles in SCENE_RULES:
        if any(needle.lower() in compact.lower() for needle in needles):
            return scene
    return "general_emphasis" if compact else "visual_transition_or_foley"


def new_sound_evidence():
    return {
        "scenes": collections.Counter(),
        "animations": collections.Counter(),
        "sources": collections.Counter(),
        "durations": [],
        "volumes": [],
        "samples": [],
    }


def timerange(segment):
    value = segment.get("target_timerange") or {}
    start = int(value.get("start") or 0)
    duration = int(value.get("duration") or 0)
    return start, duration


def parse_text(material):
    content = material.get("content")
    if not isinstance(content, str):
        return ""
    try:
        return str(json.loads(content).get("text") or "")
    except (TypeError, ValueError, json.JSONDecodeError):
        return ""


def build_decryptor(temp_dir):
    source = Path(__file__).with_name("decrypt_yingying_json.go")
    if not source.exists():
        return None
    executable = Path(temp_dir) / "decrypt_yingying_json.exe"
    result = subprocess.run(
        ["go", "build", "-o", str(executable), str(source)],
        capture_output=True,
        text=True,
    )
    return executable if result.returncode == 0 else None


def load_draft(path, decryptor):
    try:
        return json.loads(path.read_text(encoding="utf-8")), False
    except Exception as plain_error:
        if not decryptor:
            raise plain_error
        result = subprocess.run(
            [str(decryptor), str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            raise ValueError(result.stderr.strip() or "decrypt failed")
        return json.loads(result.stdout), True


def scan_draft(path, root, aggregates, decryptor):
    try:
        data, encrypted = load_draft(path, decryptor)
    except Exception as error:
        aggregates["parse_errors"] += 1
        if len(aggregates["parse_error_samples"]) < 30:
            aggregates["parse_error_samples"].append(
                {"source": str(path), "error": str(error)[:240]}
            )
        return
    if encrypted:
        aggregates["encrypted_drafts"] += 1

    materials = data.get("materials") or {}
    audios = {item.get("id"): item for item in materials.get("audios", []) if item.get("id")}
    texts = {item.get("id"): item for item in materials.get("texts", []) if item.get("id")}
    animations = {
        item.get("id"): item
        for item in materials.get("material_animations", [])
        if item.get("id")
    }

    text_events = []
    for track in data.get("tracks", []):
        if track.get("type") != "text":
            continue
        for segment in track.get("segments", []):
            material = texts.get(segment.get("material_id"))
            if not material:
                continue
            start, duration = timerange(segment)
            animation_names = []
            for ref in segment.get("extra_material_refs") or []:
                pack = animations.get(ref)
                if not pack:
                    continue
                animation_names.extend(
                    str(item.get("name"))
                    for item in pack.get("animations", [])
                    if item.get("name") and item.get("type") in (None, "in", "group")
                )
            text_events.append(
                {
                    "start": start,
                    "end": start + duration,
                    "text": parse_text(material),
                    "animations": animation_names,
                }
            )

    relative_source = str(path.relative_to(root))
    project_name = Path(relative_source).parts[0] if Path(relative_source).parts else relative_source
    for material in audios.values():
        if material.get("type") != "sound":
            continue
        name = str(material.get("name") or "未命名音效").strip()
        aggregates["sound_material_names"][name] += 1
        aggregates["sound_material_families"][classify(name)] += 1
        aggregates["sound_material_sources"][name][project_name] += 1
        source_path = str(material.get("path") or "")
        if source_path:
            aggregates["sound_material_paths"][name].add(source_path)

    for track in data.get("tracks", []):
        if track.get("type") != "audio":
            continue
        for segment in track.get("segments", []):
            material = audios.get(segment.get("material_id"))
            if not material or material.get("type") != "sound":
                continue
            start, duration = timerange(segment)
            name = str(material.get("name") or "未命名音效").strip()
            family = classify(name)
            aggregates["sound_segments"] += 1
            aggregates["sound_names"][name] += 1
            aggregates["families"][family] += 1
            aggregates["durations"][family].append(duration)
            aggregates["placed_sources"][name][project_name] += 1

            nearest = None
            nearest_distance = None
            for event in text_events:
                if event["start"] <= start <= event["end"]:
                    distance = 0
                else:
                    distance = abs(event["start"] - start)
                if distance <= 1_000_000 and (nearest_distance is None or distance < nearest_distance):
                    nearest = event
                    nearest_distance = distance

            if nearest:
                animation_list = nearest["animations"] or ["none"]
                for animation_name in animation_list:
                    aggregates["pairs"][(family, name, animation_name)] += 1
                    aggregates["family_animations"][(family, animation_name)] += 1
                if nearest["text"] and len(aggregates["samples"][family]) < 12:
                    aggregates["samples"][family].append(
                        {
                            "sound": name,
                            "text": nearest["text"][:80],
                            "animations": nearest["animations"],
                            "delta_us": nearest_distance,
                            "source": relative_source,
                        }
                    )
            else:
                aggregates["pairs"][(family, name, "none")] += 1

            evidence = aggregates["sound_evidence"][name]
            evidence["scenes"][classify_scene(nearest["text"] if nearest else "", start)] += 1
            evidence["sources"][project_name] += 1
            evidence["durations"].append(duration)
            evidence["volumes"].append(float(segment.get("volume") or 0))
            animation_list = nearest["animations"] if nearest and nearest["animations"] else ["none"]
            for animation_name in animation_list:
                evidence["animations"][animation_name] += 1
            if len(evidence["samples"]) < 20:
                evidence["samples"].append(
                    {
                        "time_us": start,
                        "text": (nearest["text"] if nearest else "")[:120],
                        "animations": animation_list,
                        "scene": classify_scene(nearest["text"] if nearest else "", start),
                        "source": relative_source,
                    }
                )


def percentile_median(values):
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", help="Draft library roots")
    parser.add_argument("--output", required=True, help="Output JSON report")
    args = parser.parse_args()

    aggregates = {
        "parse_errors": 0,
        "parse_error_samples": [],
        "encrypted_drafts": 0,
        "sound_segments": 0,
        "sound_names": collections.Counter(),
        "sound_material_names": collections.Counter(),
        "sound_material_families": collections.Counter(),
        "sound_material_sources": collections.defaultdict(collections.Counter),
        "sound_material_paths": collections.defaultdict(set),
        "placed_sources": collections.defaultdict(collections.Counter),
        "sound_evidence": collections.defaultdict(new_sound_evidence),
        "families": collections.Counter(),
        "durations": collections.defaultdict(list),
        "pairs": collections.Counter(),
        "family_animations": collections.Counter(),
        "samples": collections.defaultdict(list),
    }
    scanned = 0
    roots = [Path(item) for item in args.roots]
    with tempfile.TemporaryDirectory(prefix="jianying-sound-extract-") as temp_dir:
        decryptor = build_decryptor(temp_dir)
        for root in roots:
            for path in root.rglob("draft_content.json"):
                scanned += 1
                scan_draft(path, root, aggregates, decryptor)

    family_report = {}
    for family, count in aggregates["families"].most_common():
        names = [
            {"name": name, "count": value}
            for name, value in aggregates["sound_names"].most_common()
            if classify(name) == family
        ][:20]
        animations = [
            {"animation": animation, "count": value}
            for (pair_family, animation), value in aggregates["family_animations"].most_common()
            if pair_family == family
        ][:15]
        family_report[family] = {
            "segment_count": count,
            "median_duration_us": percentile_median(aggregates["durations"][family]),
            "top_sound_names": names,
            "top_animation_pairs": animations,
            "samples": aggregates["samples"][family],
        }

    report = {
        "schema_version": 1,
        "roots": [str(item) for item in roots],
        "draft_files_scanned": scanned,
        "parse_errors": aggregates["parse_errors"],
        "parse_error_samples": aggregates["parse_error_samples"],
        "encrypted_drafts": aggregates["encrypted_drafts"],
        "sound_segments": aggregates["sound_segments"],
        "unique_sound_names": len(aggregates["sound_names"]),
        "sound_material_instances": sum(aggregates["sound_material_names"].values()),
        "unique_sound_material_names": len(aggregates["sound_material_names"]),
        "all_sound_materials": [
            {
                "name": name,
                "family": classify(name),
                "material_count": count,
                "placed_count": aggregates["sound_names"][name],
                "source_projects": [
                    {"project": project, "count": value}
                    for project, value in aggregates["sound_material_sources"][name].most_common()
                ],
                "placed_projects": [
                    {"project": project, "count": value}
                    for project, value in aggregates["placed_sources"][name].most_common()
                ],
                "paths": sorted(aggregates["sound_material_paths"][name]),
            }
            for name, count in aggregates["sound_material_names"].most_common()
        ],
        "sound_scene_catalog": [
            {
                "name": name,
                "family": classify(name),
                "placed_count": aggregates["sound_names"][name],
                "median_duration_us": percentile_median(evidence["durations"]),
                "median_volume": percentile_median(evidence["volumes"]),
                "scene_counts": [
                    {"scene": scene, "count": count}
                    for scene, count in evidence["scenes"].most_common()
                ],
                "animation_counts": [
                    {"animation": animation, "count": count}
                    for animation, count in evidence["animations"].most_common()
                ],
                "source_projects": [
                    {"project": project, "count": count}
                    for project, count in evidence["sources"].most_common()
                ],
                "samples": evidence["samples"],
            }
            for name, evidence in sorted(
                aggregates["sound_evidence"].items(),
                key=lambda item: (-aggregates["sound_names"][item[0]], item[0]),
            )
        ],
        "families": family_report,
        "top_exact_pairs": [
            {
                "family": family,
                "sound": sound,
                "animation": animation,
                "count": count,
            }
            for (family, sound, animation), count in aggregates["pairs"].most_common(100)
        ],
    }
    Path(args.output).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: report[key] for key in (
        "draft_files_scanned", "parse_errors", "encrypted_drafts", "sound_segments",
        "unique_sound_names", "sound_material_instances", "unique_sound_material_names"
    )}, ensure_ascii=False))


if __name__ == "__main__":
    main()
