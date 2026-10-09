import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import shutil
import subprocess
import hashlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('kit', ROOT / 'skills/khong-bon/scripts/khong_bon.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


def story():
    return {'title': 'แก้ว <โปรด>', 'character': {'name': 'แก้ว', 'appearance': 'Ivory mug',
            'voice': 'Thai adult male, dry humor'}, 'setting': 'Teal kitchen counter',
            'scenes': [{'action': 'Raises eyebrows', 'camera': 'Medium close-up',
                        'line': 'เรียกผมว่าแก้วโปรด\nแต่ไม่เคยล้างเลย', 'duration': 8} for _ in range(3)]}


class KitTests(unittest.TestCase):
    def test_pack_creates_consistent_prompts_and_thai_subtitles(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'pack'
            kit.pack(story(), out)
            for i in range(1, 4):
                prompt = (out / f'shot-{i:02}.txt').read_text(encoding='utf-8')
                self.assertIn('Ivory mug', prompt)
                self.assertIn('Teal kitchen counter', prompt)
                self.assertIn('เรียกผมว่าแก้วโปรด', prompt)
            self.assertIn('00:00:16,600', (out / 'subtitles.srt').read_text(encoding='utf-8'))
            board = (out / 'storyboard.html').read_text(encoding='utf-8')
            self.assertIn('&lt;โปรด&gt;', board)
            self.assertNotIn('แก้ว <โปรด>', board)

    def test_pack_refuses_existing_folder(self):
        with tempfile.TemporaryDirectory() as d:
            marker = Path(d) / 'owner.txt'
            marker.write_text('keep', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                kit.pack(story(), Path(d))
            self.assertEqual(marker.read_text(), 'keep')

    def test_invalid_story_never_creates_output(self):
        for field, value in [('scenes', []), ('title', ''), ('character', [])]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                data = story()
                data[field] = value
                out = Path(d) / 'bad'
                with self.assertRaises(ValueError):
                    kit.pack(data, out)
                self.assertFalse(out.exists())

    def test_bad_duration_and_ass_injection_rejected(self):
        for field, value in [('duration', True), ('duration', 9), ('line', '{\\pos(1,1)}hello'),
                             ('line', 'hello\\Nworld'), ('action', ''), ('line', 'a' * 100)]:
            with self.subTest(field=field):
                data = story()
                data['scenes'][0][field] = value
                with self.assertRaises(ValueError):
                    kit.validate(data)

    def test_check_requires_exactly_three_audio_clips(self):
        meta = {'duration': 8, 'video': True, 'audio': True}
        kit.check_media([meta, meta, meta])
        for bad in [[meta], [dict(meta, audio=False), meta, meta],
                    [dict(meta, duration=7), meta, meta]]:
            with self.assertRaises(ValueError):
                kit.check_media(bad)

    def test_examples_validate(self):
        paths = list((ROOT / 'examples').glob('*/story.json'))
        self.assertEqual(len(paths), 4)
        for path in paths:
            with self.subTest(path=path):
                kit.validate(json.loads(path.read_text(encoding='utf-8')))

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg not installed')
    def test_assemble_real_video_and_audio_preserves_input_and_output(self):
        filters = subprocess.run(['ffmpeg', '-filters'], capture_output=True, text=True, check=True)
        if ' ass ' not in filters.stdout:
            self.skipTest('FFmpeg needs libass for subtitle integration')
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "ต้นฉบับ ' clip.mp4"
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=teal:s=160x90:r=30:d=8',
                            '-f', 'lavfi', '-i', 'sine=frequency=440:duration=8', '-c:v', 'libx264',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-t', '8', str(source)], check=True)
            before = hashlib.sha256(source.read_bytes()).digest()
            out = Path(d) / 'ซับไทย final.mp4'
            kit.assemble(story(), [source] * 3, out)
            info = kit.probe(out)
            self.assertAlmostEqual(info['duration'], 24, delta=.2)
            self.assertTrue(info['video'] and info['audio'])
            self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), before)
            with self.assertRaises(FileExistsError):
                kit.assemble(story(), [source] * 3, out)
            copied = Path(d) / 'installed-skill'
            shutil.copytree(ROOT / 'skills/khong-bon', copied)
            story_path = Path(d) / 'story.json'
            story_path.write_text(json.dumps(story(), ensure_ascii=False), encoding='utf-8')
            result = subprocess.run([__import__('sys').executable, str(copied / 'scripts/khong_bon.py'),
                                     'pack', str(story_path), '--out', str(Path(d) / 'copied-pack')], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
