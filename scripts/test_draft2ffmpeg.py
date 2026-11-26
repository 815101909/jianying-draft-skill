"""Regression tests for the headless renderer and the programmatic draft generator.

These tests are self-contained: they build synthetic drafts in a temp directory and
never touch the user's real Jianying projects or any external media file.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

import draft2ffmpeg as R
import make_draft as G


SPEC = {
    "name": "unit-draft",
    "canvas": [1280, 720],
    "fps": 30,
    "ratio": "16:9",
    "clips": [
        {"kind": "video", "path": "D:/media/a.mp4", "src_start": 0.0, "src_dur": 8.0,
         "tgt_start": 0.0, "tgt_dur": 4.0, "speed": 2.0, "volume": 1.0,
         "scale": [1.0, 1.0], "transform": [0.0, 0.0]},
        {"kind": "image", "path": "D:/media/cover.jpg", "tgt_start": 4.0, "tgt_dur": 3.0,
         "scale": [0.6, 0.6], "transform": [0.35, -0.35]},
        {"kind": "audio", "path": "D:/media/music.mp3", "src_start": 0.0, "src_dur": 7.0,
         "tgt_start": 0.0, "volume": 0.6},
        {"kind": "text", "text": "Hello 世界", "tgt_start": 1.0, "tgt_dur": 3.0,
         "transform": [0.0, 0.7], "size": 8.0, "color": "#FFE24D"},
    ],
}


class GeneratorTests(unittest.TestCase):
    def test_build_places_materials_and_segments(self):
        draft = G.build(SPEC)
        mats = draft["materials"]
        self.assertEqual(len(mats["videos"]), 1)
        self.assertEqual(len(mats["images"]), 1)
        self.assertEqual(len(mats["audios"]), 1)
        self.assertEqual(len(mats["texts"]), 1)
        self.assertEqual(len(mats["speeds"]), 2)  # 仅 video/image 带 speed
        self.assertEqual(draft["canvas_config"]["width"], 1280)
        self.assertEqual(draft["fps"], 30)
        # 时间单位必须是微秒
        self.assertEqual(draft["duration"], 7_000_000)
        # 视频段必须通过 extra_material_refs 关联 speed 素材
        vid_track = next(t for t in draft["tracks"] if t["type"] == "video"
                         and t["segments"] and t["segments"][0]["material_id"] == mats["videos"][0]["id"])
        seg = vid_track["segments"][0]
        speed_ids = {s["id"] for s in mats["speeds"]}
        self.assertTrue(set(seg["extra_material_refs"]) & speed_ids)
        # 文字 content 必须是「字符串套 JSON」
        self.assertIsInstance(mats["texts"][0]["content"], str)
        self.assertEqual(json.loads(mats["texts"][0]["content"])["text"], "Hello 世界")

    def test_generated_draft_roundtrips_through_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = G.build(SPEC)
            path = Path(tmp) / "draft_content.json"
            path.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
            loaded = R.load_json_auto(str(path))
            self.assertEqual(loaded["name"], "unit-draft")


class ParserTests(unittest.TestCase):
    def _parsed(self, spec):
        with tempfile.TemporaryDirectory() as tmp:
            draft = G.build(spec)
            path = Path(tmp) / "draft_content.json"
            path.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
            return R.DraftParser(str(tmp), R.load_json_auto(str(path))).parse()

    def test_parser_recovers_timeline(self):
        tl = self._parsed(SPEC)
        self.assertEqual((tl.canvas_w, tl.canvas_h), (1280, 720))
        self.assertEqual(tl.fps, 30.0)
        self.assertEqual(tl.duration, 7.0)
        self.assertEqual(len(tl.videos), 2)
        self.assertEqual(len(tl.audios), 1)
        self.assertEqual(len(tl.texts), 1)

        video = next(c for c in tl.videos if c.kind == "video")
        self.assertEqual(video.speed, 2.0)
        self.assertAlmostEqual(video.tgt_dur, 4.0, places=6)
        self.assertAlmostEqual(video.src_dur, 8.0, places=6)

        image = next(c for c in tl.videos if c.kind == "image")
        self.assertAlmostEqual(image.scale[0], 0.6, places=6)
        self.assertAlmostEqual(image.transform[1], -0.35, places=6)

        audio = tl.audios[0]
        self.assertAlmostEqual(audio.volume, 0.6, places=6)

        text = tl.texts[0]
        self.assertEqual(text.text, "Hello 世界")
        self.assertAlmostEqual(text.transform[1], 0.7, places=6)

    def test_parser_reports_missing_media(self):
        tl = self._parsed(SPEC)  # 引用的 D:/media/* 在测试机上不存在
        self.assertEqual(len(tl.clips), 4)
        media = [c for c in tl.clips if c.kind != "text"]
        self.assertEqual(len(media), 3)
        self.assertTrue(all(c.missing for c in media))
        # 文字片段没有媒体路径，不应被标记为缺失
        self.assertFalse(tl.texts[0].missing)


def _spec_with_real_files(root: Path) -> dict:
    """把 spec 的媒体路径换成临时目录下的真实（占位）文件，使素材不被跳过。"""
    for name in ("a.mp4", "cover.jpg", "music.mp3"):
        (root / name).write_bytes(b"fixture")
    spec = json.loads(json.dumps(SPEC))
    spec["clips"][0]["path"] = str(root / "a.mp4")
    spec["clips"][1]["path"] = str(root / "cover.jpg")
    spec["clips"][2]["path"] = str(root / "music.mp3")
    return spec


class CommandTests(unittest.TestCase):
    def _tl(self, root: Path):
        draft = G.build(_spec_with_real_files(root))
        path = root / "draft_content.json"
        path.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
        return R.DraftParser(str(root), R.load_json_auto(str(path))).parse()

    def test_odd_canvas_is_aligned_to_even(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tl = self._tl(root)
            tl.canvas_w, tl.canvas_h = 1920, 1447
            cmd, _ = R.build_command(tl, str(root / "out.mp4"))
            fc = cmd[cmd.index("-filter_complex") + 1]
            self.assertIn("s=1920x1448", fc)

    def test_audio_index_is_not_broken_by_image_inputs(self):
        # 图片输入占 6 个 argv token；音频流序号必须用独立计数器推导。
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tl = self._tl(root)
            cmd, _ = R.build_command(tl, str(root / "out.mp4"))
            fc = cmd[cmd.index("-filter_complex") + 1]
            # 2 个视频/图片输入 + 1 个音频输入 -> 音频是第 3 路输入
            self.assertIn("[2:a]", fc)
            self.assertNotIn("[3:a]", fc)

    def test_gap_collapse_and_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tl = self._tl(root)
            tl.clips[0].tgt_start = 0.0
            tl.clips[0].tgt_dur = 1.0
            tl.clips[1].tgt_start = 1000.0
            tl.clips[1].tgt_dur = 1.0
            tl.clips[2].tgt_start = 0.0
            tl.clips[2].tgt_dur = 7.0
            tl.clips[3].tgt_start = 1.0
            tl.clips[3].tgt_dur = 3.0
            gaps = R.analyze_gaps(tl)
            self.assertEqual(len(gaps), 1)
            self.assertAlmostEqual(gaps[0][2], 993.0, places=3)  # 1000 - 7
            removed = R.collapse_gaps(tl, 0.0)
            self.assertAlmostEqual(removed, 993.0, places=3)
            self.assertAlmostEqual(tl.max_end, 8.0, places=3)

            tl2 = self._tl(root)
            R.apply_window(tl2, 4.0, 2.0)
            self.assertTrue(all(0.0 <= c.tgt_start < 2.0 for c in tl2.clips))


class MediaResolutionTests(unittest.TestCase):
    def test_placeholder_and_media_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            mirror = Path(tmp) / "mirror"
            real = Path(tmp) / "real"
            (real / "materials" / "video").mkdir(parents=True)
            media = real / "materials" / "video" / "clip.mp4"
            media.write_bytes(b"fixture")
            mirror.mkdir()

            ph = "##_draftpath_placeholder_ABCD-1234_##/materials/video/clip.mp4"
            # 占位符在镜像目录下解析不到，但在 media_root 下解析得到
            self.assertIsNone(R.resolve_media(ph, str(mirror)))
            got = R.resolve_media(ph, str(mirror), [str(real)])
            self.assertEqual(Path(got).resolve(), media.resolve())

    def test_bare_filename_falls_back_to_materials_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "materials" / "audio").mkdir(parents=True)
            (root / "materials" / "audio" / "m.mp3").write_bytes(b"x")
            got = R.resolve_media("m.mp3", str(root))
            self.assertTrue(got and got.endswith("m.mp3"))


@unittest.skipUnless(importlib.util.find_spec("cryptography"),
                     "encrypted round-trip requires the cryptography package")
class EncryptedRoundTripTests(unittest.TestCase):
    def test_encrypt_then_parse(self):
        import jy_draft_crypt as C

        with tempfile.TemporaryDirectory() as tmp:
            draft = G.build(SPEC)
            plaintext = json.dumps(draft, ensure_ascii=False).encode("utf-8")
            enc = C.encrypt_bytes(plaintext)
            self.assertFalse(enc.lstrip()[:1] in (b"{", b"["))
            path = Path(tmp) / "draft_content.json"
            path.write_bytes(enc)
            loaded = R.load_json_auto(str(path))
            self.assertEqual(loaded["name"], "unit-draft")
            self.assertEqual(R.load_json_auto(str(path)), draft)

    def test_tampered_ciphertext_is_rejected(self):
        import jy_draft_crypt as C

        enc = bytearray(C.encrypt_bytes(json.dumps(G.build(SPEC)).encode("utf-8")))
        enc[10] = enc[10] ^ 1
        with self.assertRaises(Exception):
            C.decrypt_bytes(bytes(enc))


if __name__ == "__main__":
    unittest.main()
