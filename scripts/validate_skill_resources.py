#!/usr/bin/env python3
"""Validate bundled resource paths and JSON Pointer references without modifying files."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def pointer_target(document, reference):
    if reference == "#":
        return document
    if not isinstance(reference, str) or not reference.startswith("#/"):
        raise ValueError(f"unsupported reference: {reference!r}")
    value = document
    for part in reference[2:].split("/"):
        token = part.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def validate(root: Path):
    issues = []
    path_count = ref_count = json_count = 0
    for path in [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]:
        source = path.read_text(encoding="utf-8-sig")
        for match in re.finditer(r"(?<![\w/\\-])(?:references|scripts)/[\w.-]+\.(?:md|json|py|go)\b", source):
            relative = match.group()
            path_count += 1
            if not (root / relative).is_file():
                issues.append({"file": str(path.relative_to(root)), "type": "missing_resource", "target": relative})
    for path in sorted((root / "references").glob("*.json")):
        json_count += 1
        try:
            document = json.loads(path.read_text(encoding="utf-8-sig"))
        except (ValueError, UnicodeError) as exc:
            issues.append({"file": path.name, "type": "invalid_json", "error": str(exc)})
            continue

        def walk(value, location=""):
            nonlocal ref_count
            if isinstance(value, dict):
                if "$ref" in value:
                    ref_count += 1
                    try:
                        pointer_target(document, value["$ref"])
                    except (KeyError, IndexError, TypeError, ValueError) as exc:
                        issues.append({"file": path.name, "type": "invalid_json_ref", "location": location, "target": value["$ref"], "error": str(exc)})
                for key, child in value.items():
                    walk(child, f"{location}/{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{location}/{index}")

        walk(document)
    return {"status": "invalid" if issues else "ok", "resource_path_checks": path_count,
            "json_files": json_count, "json_ref_checks": ref_count, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = validate(args.path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
