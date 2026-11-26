"""Delivery regressions, including actual FFmpeg video/audio/subtitle rendering."""
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import struct
from pathlib import Path
from unittest.mock import patch

import batch_export
import draft2ffmpeg
import make_draft
from render_validation import unsupported_features, probe_media


class DeliveryTests(unittest.TestCase):
    def test_rejects_invalid_spec(self):
        for change in ({"fps": 0}, {"canvas": [0, 720]}, {"clips": [{"kind": "alien"}]},
                       {"clips": [{"kind": "text", "text": "hello", "tgt_dur": -1}]}):
            spec = {"clips": [{"kind": "text", "text": "ok", "tgt_dur": 1}], **change}
            with self.assertRaises(ValueError):
                make_draft.build(spec)

    def test_generated_fill_color_is_correct(self):
        draft = make_draft.build({"clips": [{"kind": "text", "text": "ok", "color": "#FF0000", "tgt_dur": 1}]})
        content = json.loads(draft["materials"]["texts"][0]["content"])
        self.assertEqual(content["styles"][0]["fill"]["content"]["solid"]["color"], [1, 0, 0])

    def test_same_name_has_different_batch_destinations(self):
        self.assertNotEqual(batch_export.output_name({"name": "same", "dir": "a"}),
                            batch_export.output_name({"name": "same", "dir": "b"}))

    def test_unsupported_used_effect_and_keyframes_are_reported(self):
        draft = {"materials": {"videos": [{"id": "v"}], "transitions": [{"id": "fx"}]},
                 "tracks": [{"segments": [{"id": "s", "material_id": "v", "extra_material_refs": ["fx"], "common_keyframes": [{}]}]}]}
        self.assertEqual({x["feature"] for x in unsupported_features(draft)}, {"transitions", "keyframe animation"})

    def test_strict_mode_stops_before_ffmpeg(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "draft_content.json")
            path.write_text(json.dumps({"materials": {"videos": [{"id": "v", "path": "missing.mp4"}]},
                "tracks": [{"segments": [{"id": "s", "material_id": "v", "target_timerange": {"start": 0, "duration": 1000000}}]}]}), encoding="utf-8")
            with patch.object(sys, "argv", ["render", str(path), "--render", "--strict", "--out", str(Path(directory, "out.mp4"))]), patch("draft2ffmpeg.subprocess.call") as render, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(draft2ffmpeg.main(), 2)
                render.assert_not_called()
            report = json.loads(Path(directory, "out.mp4.render-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "blocked")

    def test_batch_returns_failure_and_preserves_failure_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "library/a").mkdir(parents=True)
            (root / "library/a/draft_content.json").write_text("{}", encoding="utf-8")
            record = {"status": "OK", "name": "example", "dir": str(root / "library/a"), "span_dur": 1}
            failure = subprocess.CompletedProcess([], 2, stdout="", stderr="render failed")
            with patch.object(sys, "argv", ["batch", str(root / "library"), "--out-dir", str(root / "out")]), patch("batch_export.S.probe_one", return_value=record), patch("batch_export.subprocess.run", return_value=failure), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(batch_export.main(), 2)
            report = json.loads((root / "out/_batch_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["results"][0]["status"], "FAIL")

    def test_repeated_command_build_does_not_mutate_text_size(self):
        with tempfile.TemporaryDirectory() as directory:
            clip = draft2ffmpeg.Clip(kind="text", path=None, text="hello", text_px=20, tgt_dur=1)
            timeline = draft2ffmpeg.Timeline(duration=1, clips=[clip])
            draft2ffmpeg.build_command(timeline, str(Path(directory, "one.mp4")), text_scale=2)
            draft2ffmpeg.build_command(timeline, str(Path(directory, "two.mp4")), text_scale=2)
            self.assertEqual(clip.text_px, 20)
            self.assertTrue(Path(directory, "one.subs.ass").exists())
            self.assertTrue(Path(directory, "two.subs.ass").exists())

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg integration requires ffmpeg and ffprobe")
    def test_actual_packaged_draft_render_and_probe(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def command(args):
                result = subprocess.run(args, capture_output=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace")[-2000:])
                return result.stdout
            command(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=red:s=320x180:r=10:d=1", "-c:v", "libx264", str(root / "video.mp4")])
            command(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=blue:s=320x180", "-frames:v", "1", str(root / "image.png")])
            command(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=2", str(root / "audio.wav")])
            spec = {"name": "smoke", "canvas": [320, 180], "fps": 10, "clips": [
                {"kind": "video", "path": "video.mp4", "src_dur": 1},
                {"kind": "image", "path": "image.png", "tgt_start": 1, "tgt_dur": 1},
                {"kind": "audio", "path": "audio.wav", "src_dur": 2},
                {"kind": "text", "text": "TEST", "size": 80, "color": "#FFFF00", "tgt_dur": 2}]}
            (root / "spec.json").write_text(json.dumps(spec), encoding="utf-8")
            scripts = Path(__file__).parent
            command([sys.executable, str(scripts / "make_draft.py"), str(root / "spec.json"), "--out", str(root / "draft"), "--copy-media", "--name", "delivery-smoke"])
            self.assertTrue((root / "draft/draft_meta_info.json").is_file())
            command([sys.executable, str(scripts / "inspect_draft.py"), str(root / "draft")])
            command([sys.executable, str(scripts / "draft2ffmpeg.py"), str(root / "draft"), "--render", "--strict", "--out", str(root / "out.mp4"), "--preset", "ultrafast"])
            media = json.loads(command(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(root / "out.mp4")]))
            self.assertEqual({s["codec_type"] for s in media["streams"]}, {"video", "audio"})
            self.assertAlmostEqual(float(media["format"]["duration"]), 2, delta=0.15)
            pcm = command(["ffmpeg", "-v", "error", "-i", str(root / "out.mp4"), "-vn", "-f", "s16le", "-ac", "1", "-ar", "8000", "pipe:1"])
            samples = struct.unpack("<" + "h" * (len(pcm)//2), pcm)
            self.assertGreater(sum(s*s for s in samples) / len(samples), 10000, "audio must not be silent")
            for instant, channel in (("0.5", 0), ("1.5", 2)):
                raw = command(["ffmpeg", "-v", "error", "-ss", instant, "-i", str(root / "out.mp4"), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"])
                self.assertGreater(raw[channel], 150)
                yellow = sum(1 for i in range(0, len(raw), 3) if raw[i] > 160 and raw[i+1] > 160 and raw[i+2] < 100)
                self.assertGreater(yellow, 10, "subtitle must be visible and yellow")
            broken = root / "broken.png"
            broken.write_bytes(b"not an image")
            timeline = draft2ffmpeg.Timeline(clips=[draft2ffmpeg.Clip(kind="image", path=str(broken))])
            self.assertTrue(probe_media(timeline))


if __name__ == "__main__":
    unittest.main()
