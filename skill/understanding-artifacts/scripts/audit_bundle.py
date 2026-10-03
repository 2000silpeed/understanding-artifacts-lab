#!/usr/bin/env python3
"""Audit bundle packaging/media; does not certify semantics or comprehension.
Usage: python3 audit_bundle.py ROOT --report audit.json
Stdlib only; ffprobe needed for video. Browser network tests are separate.
"""
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources, self.code = [], []
        self.in_code = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ('src', 'href', 'poster'):
            if a.get(k):
                self.resources.append((tag, a[k]))
        if tag == 'object' and a.get('data'):
            self.resources.append((tag, a['data']))
        if a.get('srcset'):
            for url in re.findall(r'(?:https?:)?//[^\s,]+', a['srcset']):
                self.resources.append((tag, url))
        if a.get('style'):
            self.code.append(a['style'])
        if tag in ('style', 'script'):
            self.in_code = True
    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self.in_code = False
    def handle_data(self, data):
        if self.in_code:
            self.code.append(data)

def faststart(path):
    """Require a normal unfragmented MP4 with moov preceding mdat."""
    atoms = {}
    with path.open('rb') as f:
        length = path.stat().st_size
        while f.tell() < length:
            pos = f.tell()
            header = f.read(8)
            if len(header) != 8:
                return False
            size, kind = struct.unpack('>I4s', header)
            header_size = 8
            if size == 1:
                ext = f.read(8)
                if len(ext) != 8:
                    return False
                size = struct.unpack('>Q', ext)[0]
                header_size = 16
            elif size == 0:
                size = length - pos
            if size < header_size or pos + size > length:
                return False
            atoms.setdefault(kind, pos)
            f.seek(pos + size)
    return b'moov' in atoms and b'mdat' in atoms and atoms[b'moov'] < atoms[b'mdat'] and b'moof' not in atoms

def audit(root, manifest='contract.json'):
    root = Path(root).resolve()
    checks, files = [], {}
    def redact(value):
        return str(value).replace(str(root), '.')
    def check(name, ok, detail):
        checks.append({'name': name, 'passed': bool(ok), 'detail': detail})
    def result():
        return {'schema_version': 1, 'generated_at': datetime.now(timezone.utc).isoformat(), 'scope': 'Packaging, static HTML resource references and media metadata only. Dynamic/offline browser network, factual correctness, audio quality, accessibility and learning are separate checks.', 'passed': bool(checks) and all(c['passed'] for c in checks), 'checks': checks, 'files': files}
    def safe_path(value):
        if not isinstance(value, str) or not value or Path(value).is_absolute():
            raise ValueError('Asset paths must be nonempty relative strings')
        p = (root / value).resolve()
        if not p.is_relative_to(root):
            raise ValueError('Path escapes bundle root')
        return p
    try:
        contract = json.loads(safe_path(manifest).read_text(encoding='utf-8'))
        if not isinstance(contract, dict):
            raise ValueError('Contract must be a JSON object')
        check('contract_parse', True, manifest)
    except (OSError, ValueError, TypeError) as e:
        check('contract_parse', False, redact(e))
        return result()
    artifacts = contract.get('artifacts', {})
    check('required_modes', isinstance(artifacts, dict) and all(k in artifacts for k in ('writing', 'diagram', 'web', 'video', 'transcript', 'sources', 'tests')), 'Required artifact keys; semantic contract completeness is not checked')
    if not isinstance(artifacts, dict):
        artifacts = {}
    for role, rel in artifacts.items():
        try:
            p = safe_path(rel)
            exists = p.is_file() and p.stat().st_size > 0
            check('asset_' + role, exists, rel)
            if exists:
                files[role] = {'path': rel, 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        except (OSError, ValueError, TypeError) as e:
            check('asset_' + role, False, redact(e))
    web = files.get('web')
    if web:
        parser = Links()
        try:
            parser.feed(safe_path(web['path']).read_text(encoding='utf-8'))
            check('web_parse', True, 'UTF-8 HTML parsed')
        except (OSError, UnicodeError, ValueError) as e:
            check('web_parse', False, redact(e))
        for tag, raw in parser.resources:
            try:
                u = urlsplit(raw)
                if u.scheme in ('data', 'mailto', 'tel'):
                    continue
                if u.scheme or u.netloc:
                    if tag != 'a':
                        check('html_attribute_resource_check', False, raw)
                    continue
                if not u.path:
                    continue
                p = (safe_path(web['path']).parent / unquote(u.path)).resolve()
                check('local_link', p.is_relative_to(root) and p.is_file(), raw)
            except (OSError, ValueError):
                check('html_attribute_resource_check', False, raw)
        # Conservative literals only. Computed URLs require real browser network interception.
        pattern = r'''(?:url\s*\(\s*["']?|@import\s*["']|fetch\s*\(\s*["']|import\s*\(\s*["']|\.open\s*\(\s*["'][A-Z]+["']\s*,\s*["'])(https?://[^\s"'\)]+|//[^\s"'\)]+)'''
        literals = re.findall(pattern, '\n'.join(parser.code), flags=re.I)
        check('static_network_literal_check', not literals, literals or 'No supported literal remote loads found; not a dynamic network guarantee')
    video = files.get('video')
    if video:
        probe = shutil.which('ffprobe')
        check('ffprobe_available', probe is not None, 'ffprobe')
        if probe:
            cmd = [probe, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(safe_path(video['path']))]
            try:
                run = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if run.returncode:
                    check('video_probe', False, {'exit_code': run.returncode, 'stderr': redact(run.stderr[:500])})
                else:
                    info = json.loads(run.stdout)
                    info.setdefault('format', {})['filename'] = video['path']
                    vs = [s for s in info.get('streams', []) if s.get('codec_type') == 'video']
                    aud = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']
                    check('video_probe', True, {'command': 'ffprobe -show_format -show_streams -of json <video>', 'exit_code': run.returncode})
                    check('video_stream', bool(vs), 'Decoded metadata')
                    if vs:
                        v = vs[0]
                        check('video_compatibility', v.get('codec_name') == 'h264' and v.get('pix_fmt') == 'yuv420p', {k: v.get(k) for k in ('codec_name', 'pix_fmt', 'width', 'height', 'duration', 'nb_frames')})
                    check('audio_stream_present', bool(aud), [{k: s.get(k) for k in ('codec_name', 'duration', 'sample_rate', 'channels')} for s in aud])
                    check('positive_duration', float(info.get('format', {}).get('duration', 0)) > 0, info.get('format', {}).get('duration'))
                    check('mp4_faststart', faststart(safe_path(video['path'])), 'Unfragmented MP4: moov before mdat')
                    files['video']['probe'] = info
            except (OSError, subprocess.SubprocessError, ValueError, TypeError) as e:
                check('video_probe', False, redact(e))
    return result()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root')
    ap.add_argument('--manifest', default='contract.json')
    ap.add_argument('--report')
    args = ap.parse_args()
    report = audit(args.root, args.manifest)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(text + '\n', encoding='utf-8')
    print(text)
    raise SystemExit(0 if report['passed'] else 1)

if __name__ == '__main__':
    main()
