"""Check packaged examples and local document links; no third-party dependencies."""
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('kit', root / 'skills/khong-bon/scripts/khong_bon.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)
errors = []
required = ['README.md', 'LICENSE', 'WORKFLOW.md', 'AGENTS.md', 'THIRD_PARTY_NOTICES.md',
            'docs/DEMO.md', 'docs/TEST-REPORT.md', 'assets/banner.svg',
            'skills/khong-bon/SKILL.md', 'skills/khong-bon/assets/OFL.txt',
            'skills/khong-bon/assets/NotoSansThai.ttf', '.github/workflows/check.yml']
for name in required:
    if not (root / name).is_file():
        errors.append('missing: ' + name)
for slug in ('mug', 'aircon', 'laundry', 'dish-soap'):
    base = root / 'examples' / slug
    try:
        story = kit.validate(json.loads((base / 'story.json').read_text(encoding='utf-8')))
        packed = json.loads((base / 'pack/story.json').read_text(encoding='utf-8'))
        if story != packed:
            errors.append(slug + ': packed story differs from source')
        for name in ('character.txt', 'image-prompt.txt', 'shot-01.txt', 'shot-02.txt', 'shot-03.txt',
                     'storyboard.html', 'subtitles.srt', 'subtitles.ass', 'QC.md'):
            if not (base / 'pack' / name).is_file():
                errors.append(slug + ': missing pack/' + name)
        image = root / 'skills/khong-bon/assets' / (slug + '-reference.png')
        if image.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
            errors.append(slug + ': invalid reference PNG')
    except (OSError, ValueError) as error:
        errors.append(slug + ': ' + str(error))
links = 0
for path in root.rglob('*.md'):
    if {'.git', 'runs', 'dist'} & set(path.relative_to(root).parts):
        continue
    text = path.read_text(encoding='utf-8')
    if len(re.findall(r'^```', text, re.M)) % 2:
        errors.append(str(path.relative_to(root)) + ': unclosed code fence')
    prose = re.sub(r'^```.*?^```[^\n]*', '', text, flags=re.M | re.S)
    targets = re.findall(r'\]\(([^\s)]+)\)', prose) + re.findall(r'(?:href|src)="([^"]+)"', prose)
    for target in targets:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        links += 1
        dest = (path.parent / unquote(parsed.path)).resolve()
        if not dest.is_relative_to(root) or not dest.exists():
            errors.append(f'{path.relative_to(root)}: missing/escaping link {target}')
if errors:
    print('\n'.join('FAIL: ' + e for e in errors))
else:
    print(f'PASS: 4 story/pack pairs, reference images, required files, {links} local links')
sys.exit(bool(errors))
