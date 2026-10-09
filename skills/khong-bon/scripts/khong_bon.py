#!/usr/bin/env python3
"""Pack a Thai talking-object episode and assemble three reviewed local clips."""
import argparse
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def text_field(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ValueError(f'{key}: ต้องเป็นข้อความ 1–2000 ตัวอักษร')
    if any(ord(c) < 32 and c != '\n' for c in value):
        raise ValueError(f'{key}: มี control character')
    return value


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('story ต้องเป็น JSON object')
    text_field(data, 'title')
    text_field(data, 'setting')
    character = data.get('character')
    if not isinstance(character, dict):
        raise ValueError('character ต้องเป็น object')
    for key in ('name', 'appearance', 'voice'):
        text_field(character, key)
    scenes = data.get('scenes')
    if not isinstance(scenes, list) or len(scenes) != 3:
        raise ValueError('ต้องมี 3 scenes ช็อตละ 8 วินาที')
    for scene in scenes:
        if not isinstance(scene, dict):
            raise ValueError('scene ต้องเป็น object')
        for key in ('action', 'camera', 'line'):
            text_field(scene, key)
        if type(scene.get('duration')) is not int or scene['duration'] != 8:
            raise ValueError('duration ต้องเป็นจำนวนเต็ม 8')
        line = scene['line']
        if len(line) > 85 or any(c in line for c in '{}\\'):
            raise ValueError('line: ไม่เกิน 85 ตัวอักษร และไม่มี { } หรือ backslash')
    return data


def timestamp(seconds, ass=False):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    secs, ms = divmod(ms, 1000)
    return (f'{hours}:{minutes:02}:{secs:02}.{ms // 10:02}' if ass else
            f'{hours:02}:{minutes:02}:{secs:02},{ms:03}')


def subtitle_files(data):
    srt, events = [], []
    for i, scene in enumerate(data['scenes']):
        start, end = i * 8 + .6, i * 8 + 7.4
        line = scene['line']
        srt.append(f'{i + 1}\n{timestamp(start)} --> {timestamp(end)}\n{line}\n')
        events.append(f'Dialogue: 0,{timestamp(start, True)},{timestamp(end, True)},Default,,0,0,0,,{line.replace(chr(10), chr(92) + "N")}')
    ass = '''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans Thai,38,&H00FFFFFF,&H00FFFFFF,&H00181922,&H80000000,0,0,0,0,100,100,0,0,1,3,0,2,56,56,180,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    return '\n'.join(srt), ass + '\n'.join(events) + '\n'


def shot_prompt(data, scene):
    char = data['character']
    return f'''Vertical 9:16, 8-second stylized 3D animation. Exactly one talking object.
CHARACTER: {char['appearance']}
SETTING: {data['setting']}
VOICE: {char['voice']}
CAMERA: {scene['camera']}
ACTION: {scene['action']}
The object is the sole speaker. Animate its mouth while it speaks naturally in Thai.
Speak only this exact line, from about 0.6s, finish by 7.4s, then hold the expression:
"{scene['line'].replace(chr(10), ' ')}"
Keep the object's shape, colors, face, props, background and voice consistent with the approved reference.
No humans, additional speakers, extra limbs, written captions, music or logos.
Leave the bottom 22 percent clear for subtitles added in editing. Use gentle room tone.
'''


def pack(data, out):
    validate(data)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(exist_ok=False)
    (out / 'story.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    char = data['character']
    (out / 'character.txt').write_text(
        f"{char['name']}\n{char['appearance']}\nVoice: {char['voice']}\nSetting: {data['setting']}\n",
        encoding='utf-8')
    (out / 'image-prompt.txt').write_text(
        f"Vertical 9:16 original stylized 3D character still. {char['appearance']}. "
        f"{data['setting']}. Exactly one object, no humans, no text. Medium close-up, "
        "soft warm light. Bottom 22 percent empty for subtitles.\n", encoding='utf-8')
    cards = []
    for i, scene in enumerate(data['scenes'], 1):
        prompt = shot_prompt(data, scene)
        (out / f'shot-{i:02}.txt').write_text(prompt, encoding='utf-8')
        cards.append(f'<article><h2>ช็อต {i} · 8 วินาที</h2><p class="line">{html.escape(scene["line"]).replace(chr(10), "<br>")}</p><p>{html.escape(scene["action"])}</p><details><summary>Flow Prompt</summary><pre>{html.escape(prompt)}</pre></details></article>')
    srt, ass = subtitle_files(data)
    (out / 'subtitles.srt').write_text(srt, encoding='utf-8')
    (out / 'subtitles.ass').write_text(ass, encoding='utf-8')
    page = '''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ของบ่น · Storyboard</title><style>body{background:#151923;color:#f6f0e7;font:18px/1.65 system-ui,sans-serif;max-width:1040px;margin:auto;padding:32px}h1{font-size:42px;color:#ffd063}.label{color:#86d7cc}article{padding:24px;border:1px solid #48505b;border-radius:18px;margin:20px 0;background:#202632}.line{font-size:28px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}summary{cursor:pointer}footer{color:#b9c1cd}</style>'''
    page += f'<p class="label">ของบ่น / KHONG BON</p><h1>{html.escape(data["title"])}</h1><p>สตอรีบอร์ด 24 วินาที · ยังไม่ใช่คลิปที่เรนเดอร์แล้ว</p>' + ''.join(cards)
    page += '<footer>ตรวจภาพและฟังเสียงจริงทุกช็อตก่อนนำไปใช้ · ซับเป็นเวลาเริ่มต้น ให้ปรับตามเสียงที่ได้</footer></html>'
    (out / 'storyboard.html').write_text(page, encoding='utf-8')
    (out / 'QC.md').write_text('# ตรวจคลิปก่อนประกอบ\n\nสถานะเริ่มต้น: NEEDS_HUMAN_REVIEW\n\n- [ ] รูปร่าง สี ใบหน้า และฉากตรงภาพอ้างอิงทั้ง 3 ช็อต\n- [ ] มีสิ่งของผู้พูดตัวเดียว ไม่มีแขนขางอกหรือคนเพิ่ม\n- [ ] ฟังภาษาไทยครบ ตรงบท ไม่มีคำพูดเพิ่ม\n- [ ] เสียงบุคลิกเดียวกันทั้ง 3 ช็อต\n- [ ] ซับตรงเสียงและไม่บังหน้า/ปุ่มบนแพลตฟอร์ม\n- [ ] ดูคลิปประกอบจบครบ 24 วินาที\n\nจดชื่อเทคและจุดที่ต้องซ่อมไว้ใต้รายการนี้\n', encoding='utf-8')


def run(args, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise ValueError(result.stderr[-2000:] or 'คำสั่งไม่สำเร็จ')
    return result.stdout


def probe(path):
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    streams = info.get('streams', [])
    return {'duration': float(info.get('format', {}).get('duration', 0)),
            'video': any(s.get('codec_type') == 'video' for s in streams),
            'audio': any(s.get('codec_type') == 'audio' for s in streams)}


def check_media(media):
    if len(media) != 3:
        raise ValueError('ต้องเลือก 3 คลิปตามลำดับช็อต 01, 02, 03')
    for i, item in enumerate(media, 1):
        duration = item['duration']
        if not math.isfinite(duration) or not 7.9 <= duration <= 8.3:
            raise ValueError(f'ช็อต {i}: ต้องยาวประมาณ 8 วินาที ได้ {duration}')
        if not item['video'] or not item['audio']:
            raise ValueError(f'ช็อต {i}: ต้องมีทั้งภาพและเสียงพูด')


def assemble(data, clips, out):
    validate(data)
    for tool in ('ffmpeg', 'ffprobe'):
        if not shutil.which(tool):
            raise ValueError(f'ไม่พบ {tool}: ติดตั้ง FFmpeg ก่อนประกอบคลิป')
    if ' ass ' not in run(['ffmpeg', '-hide_banner', '-filters']):
        raise ValueError('FFmpeg รุ่นนี้ไม่มีตัวกรอง ass/libass: ใช้ FFmpeg ที่รองรับซับ เช่น brew install ffmpeg-full แล้วเพิ่ม bin ของรุ่น full ใน PATH')
    clips = [Path(p).resolve(strict=True) for p in clips]
    out = Path(out)
    if out.suffix.lower() != '.mp4':
        raise ValueError('ไฟล์ปลายทางต้องเป็น .mp4')
    if out.exists() or out.is_symlink():
        raise FileExistsError(f'ไม่ทับไฟล์เดิม: {out}')
    check_media([probe(p) for p in clips])
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='khong-bon-') as d:
        temp = Path(d)
        shutil.copyfile(ASSETS / 'NotoSansThai.ttf', temp / 'NotoSansThai.ttf')
        # Relative filter paths avoid platform-specific escaping of user filenames.
        (temp / 'subtitles.ass').write_text(subtitle_files(data)[1], encoding='utf-8')
        for i, clip in enumerate(clips):
            run(['ffmpeg', '-v', 'error', '-nostdin', '-n', '-i', str(clip), '-t', '8',
                 '-map', '0:v:0', '-map', '0:a:0', '-vf',
                 'scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30',
                 '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
                 '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(temp / f'{i}.mp4')])
        (temp / 'list.txt').write_text("file '0.mp4'\nfile '1.mp4'\nfile '2.mp4'\n", encoding='utf-8')
        run(['ffmpeg', '-v', 'error', '-nostdin', '-n', '-f', 'concat', '-safe', '1', '-i', 'list.txt',
             '-vf', 'ass=subtitles.ass:fontsdir=.', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
             '-c:a', 'aac', '-t', '24', '-movflags', '+faststart', 'final.mp4'], cwd=d)
        final = temp / 'final.mp4'
        metadata = probe(final)
        if not 23.9 <= metadata['duration'] <= 24.2 or not metadata['audio'] or not metadata['video']:
            raise ValueError('คลิปประกอบไม่ครบ 24 วินาที หรือไม่มีภาพ/เสียง')
        # Exclusive creation prevents overwriting a file created during rendering.
        with out.open('xb') as dest, final.open('rb') as source:
            shutil.copyfileobj(source, dest)


def main():
    parser = argparse.ArgumentParser(description='ของบ่น: สร้างชุดบท/Prompt และประกอบคลิป 24 วินาที')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('check', 'pack', 'assemble'):
        sub = commands.add_parser(name)
        sub.add_argument('story', type=Path)
        if name != 'check':
            sub.add_argument('--out', type=Path, required=True)
        if name == 'assemble':
            sub.add_argument('--clips', type=Path, nargs=3, required=True)
    args = parser.parse_args()
    try:
        data = validate(json.loads(args.story.read_text(encoding='utf-8-sig')))
        if args.command == 'pack':
            pack(data, args.out)
        elif args.command == 'assemble':
            assemble(data, args.clips, args.out)
        print('PASS: ' + args.command + (f' → {args.out}' if hasattr(args, 'out') else ''))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
