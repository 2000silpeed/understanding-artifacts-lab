#!/usr/bin/env python3
"""Synthetic regression fixtures for audit_bundle.py, NOT demo/learning results.
Requires ffmpeg/ffprobe. Usage: python3 test_audit_bundle.py --report results.json
"""
import argparse
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('auditor', Path(__file__).with_name('audit_bundle.py'))
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)

class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            raise unittest.SkipTest('ffmpeg and ffprobe required; fixtures not exercised')
        cls.tmp = tempfile.TemporaryDirectory(prefix='understanding-fixtures-')
        cls.base = Path(cls.tmp.name)
        cls.good_video = cls.base/'fixture.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=navy:s=128x72:r=10','-f','lavfi','-i','sine=frequency=440:sample_rate=24000','-t','0.4','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart','-y',str(cls.good_video)], check=True, timeout=30)
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'tmp'):
            cls.tmp.cleanup()
    def setUp(self):
        self.root = self.base/'bundle'
        if self.root.exists():
            shutil.rmtree(self.root)
        (self.root/'video').mkdir(parents=True)
        self.manifest = {'artifacts':{'writing':'writing.md','diagram':'diagram.svg','web':'index.html','video':'video/video.mp4','transcript':'video/script.md','sources':'sources.md','tests':'test-report.json'}}
        self.write_contract(self.manifest)
        for role, rel in self.manifest['artifacts'].items():
            if role != 'video':
                (self.root/rel).write_text('<html><body>fixture</body></html>' if role == 'web' else 'synthetic fixture\n')
        shutil.copyfile(self.good_video,self.root/'video/video.mp4')
    def write_contract(self, value):
        (self.root/'contract.json').write_text(json.dumps(value))
    def run_audit(self):
        return auditor.audit(self.root)
    def html_failure(self, text):
        (self.root/'index.html').write_text(text)
        self.assertFalse(self.run_audit()['passed'])
    def test_english_korean_requires_subtitles(self):
        self.manifest['language'] = {'narration': 'en', 'screen': 'ko'}
        self.write_contract(self.manifest)
        report = self.run_audit()
        self.assertFalse(report['passed'])
        self.assertTrue(any(c['name'] == 'subtitles_required_audit' and not c['passed'] for c in report['checks']))
    def test_valid_with_actual_video(self):
        report = self.run_audit()
        self.assertTrue(report['passed'], report['checks'])
        self.assertNotIn(str(self.root),json.dumps(report))
    def test_missing_asset(self):
        (self.root/'video/video.mp4').unlink()
        self.assertFalse(self.run_audit()['passed'])
    def test_empty_asset(self):
        (self.root/'video/video.mp4').write_bytes(b'')
        self.assertFalse(self.run_audit()['passed'])
    def test_traversal(self):
        self.manifest['artifacts']['writing'] = '../outside.md'
        self.write_contract(self.manifest)
        self.assertFalse(self.run_audit()['passed'])
    def test_remote_attribute_no_path(self):
        self.html_failure('<img src="https://example.com">')
    def test_remote_attribute_path(self):
        self.html_failure('<script src="https://example.com/a.js"></script>')
    def test_protocol_relative(self):
        self.html_failure('<img src="//example.com">')
    def test_css_load(self):
        self.html_failure('<style>@import "https://example.com/a.css"; body{background:url(https://example.com/a.png)}</style>')
    def test_static_js_fetch(self):
        self.html_failure('<script>fetch("https://example.com")</script>')
    def test_nonobject_contract(self):
        for value in ([],None,'x',12):
            self.write_contract(value)
            report = self.run_audit()
            self.assertFalse(report['passed'])
            self.assertEqual(report['checks'][0]['name'],'contract_parse')
    def test_invalid_utf8(self):
        (self.root/'index.html').write_bytes(b'\xff')
        report = self.run_audit()
        self.assertFalse(report['passed'])
        self.assertTrue(any(c['name']=='web_parse' and not c['passed'] for c in report['checks']))
    def test_no_audio(self):
        subprocess.run(['ffmpeg','-v','error','-i',str(self.good_video),'-an','-c:v','copy','-movflags','+faststart','-y',str(self.root/'video/video.mp4')],check=True,timeout=30)
        report = self.run_audit()
        self.assertFalse(report['passed'])
        self.assertTrue(any(c['name']=='audio_stream_present' and not c['passed'] for c in report['checks']))
    def test_invalid_video(self):
        (self.root/'video/video.mp4').write_bytes(b'not an mp4')
        self.assertFalse(self.run_audit()['passed'])
    def test_no_faststart(self):
        subprocess.run(['ffmpeg','-v','error','-i',str(self.good_video),'-c','copy','-y',str(self.root/'video/video.mp4')],check=True,timeout=30)
        self.assertFalse(auditor.faststart(self.root/'video/video.mp4'))
        self.assertFalse(self.run_audit()['passed'])
    def test_external_citation_allowed(self):
        (self.root/'index.html').write_text('<a href="https://example.com">Source</a><a href="#section">Jump</a>')
        self.assertTrue(self.run_audit()['passed'])

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report')
    args = p.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AuditTests))
    report = {'scope':'Synthetic regression fixtures, not actual artifact or learning measurements','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.wasSuccessful() and not result.skipped}
    if args.report:
        Path(args.report).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    raise SystemExit(0 if report['passed'] else 1)
