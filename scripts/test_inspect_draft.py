"""Regression tests for inspector input selection and actionable validation failures."""
import contextlib
import base64
import importlib.util
import io
import json
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch

import inspect_draft
from validate_skill_resources import validate


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "Resources/local").mkdir(parents=True)
        (self.root / "Resources/local/clip.mp4").write_bytes(b"fixture")
        self.draft = {"id": "draft", "name": "example", "materials": {
            "videos": [{"id": "video", "path": "Resources/local/clip.mp4"}],
            "texts": [{"id": "text", "type": "text", "content": json.dumps({"text": "hello"})}]},
            "tracks": [{"id": "track", "type": "video", "segments": [{"id": "segment", "material_id": "video"}]}]}

    def run_inspector(self):
        path = self.root / "draft_content.json"
        path.write_text(json.dumps(self.draft), encoding="utf-8")
        output = io.StringIO()
        with patch.object(sys, "argv", ["inspect_draft.py", str(path)]), contextlib.redirect_stdout(output):
            code = inspect_draft.main()
        return code, json.loads(output.getvalue())

    def test_file_input_checks_sibling_media_and_meta(self):
        (self.root / "draft_meta_info.json").write_text(json.dumps({"draft_id": "draft", "draft_name": "example"}), encoding="utf-8")
        code, report = self.run_inspector()
        self.assertEqual(code, 0)
        self.assertTrue(report["meta_present"])

    def test_missing_media_is_not_matched_by_filename_suffix(self):
        (self.root / "Resources/local/clip.mp4").rename(self.root / "Resources/local/not-clip.mp4")
        code, report = self.run_inspector()
        self.assertEqual(code, 2)
        self.assertEqual(len(report["missing_draft_resource_path_refs"]), 1)

    def test_invalid_text_after_first_five_samples_fails(self):
        self.draft["materials"]["texts"] = [{"id": f"text-{i}", "type": "text", "content": json.dumps({"text": "ok"})} for i in range(6)]
        self.draft["materials"]["texts"][-1]["content"] = "bad json"
        code, report = self.run_inspector()
        self.assertEqual(code, 2)
        self.assertEqual(report["validation_issues"][0]["type"], "invalid_text_content")

    def test_duplicate_ids_missing_primary_and_meta_mismatch(self):
        self.draft["tracks"][0]["segments"][0] = {"id": "video"}
        (self.root / "draft_meta_info.json").write_text('{"draft_id":"other"}', encoding="utf-8")
        code, report = self.run_inspector()
        self.assertEqual(code, 2)
        self.assertTrue(report["missing_primary_material_refs"])
        self.assertEqual({item["type"] for item in report["validation_issues"]}, {"duplicate_runtime_id", "meta_mismatch"})

    def test_ambiguous_folder_requires_explicit_path(self):
        for name in ("a", "b"):
            (self.root / name).mkdir()
            (self.root / name / "draft_content.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "found 2"):
            inspect_draft.load_draft(self.root)

    def test_resource_validator_detects_broken_paths_and_pointers(self):
        (self.root / "references").mkdir()
        (self.root / "SKILL.md").write_text('Read `references/missing.md`.', encoding="utf-8")
        (self.root / "references/presets.json").write_text('{"a":{"$ref":"#/missing"}}', encoding="utf-8")
        report = validate(self.root)
        self.assertEqual({item["type"] for item in report["issues"]}, {"missing_resource", "invalid_json_ref"})

    @unittest.skipUnless(shutil.which("go") and importlib.util.find_spec("cryptography"), "encrypted integration test requires Go and cryptography")
    def test_encrypted_input_and_authentication_failure(self):
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import subprocess

        key = b"0123456789abcdef0123456789abcdef"
        nonce = b"0123456789abcdef"
        sealed = AESGCM(key).encrypt(nonce, json.dumps(self.draft).encode(), None)

        def encode(payload):
            work = base64.b64encode(payload).decode()
            key_nonce = (key + nonce).decode()
            for index, position in enumerate([0, 7, 20, 33, 40, 47, 59, 66, 76, 89, 99, 127]):
                work = work[:position] + key_nonce[index * 4:index * 4 + 4] + work[position:]
            return work

        path = self.root / "draft_content.json"
        source = encode(sealed)
        path.write_text(source, encoding="ascii")
        draft, _, files = inspect_draft.load_draft(path)
        self.assertEqual(draft, self.draft)
        self.assertFalse(inspect_draft.inspect_references(draft, files)["missing_draft_resource_path_refs"])
        self.assertEqual(path.read_text(encoding="ascii"), source)
        path.write_text(encode(sealed[:-1] + bytes([sealed[-1] ^ 1])), encoding="ascii")
        with self.assertRaises(subprocess.CalledProcessError):
            inspect_draft.load_draft(path)


if __name__ == "__main__":
    unittest.main()
