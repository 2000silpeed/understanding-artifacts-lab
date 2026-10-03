#!/usr/bin/env python3
"""Synthetic subtitle regression fixtures, not a human comprehension study."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('captions',Path(__file__).with_name('audit_captions.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  (self.root/'x.mp4').write_bytes(b'synthetic media-binding fixture, not a decodable video')
  self.contract={'subtitles':{'required':True,'language':'ko'},'artifacts':{'captions_srt':'ko.srt','captions_vtt':'ko.vtt','caption_alignment':'alignment.json','caption_timeline':'timeline.json'}}
  self.timeline={'duration':2,'scenes':[{'id':'one','start':0,'words':[{'text':'Example','start':0,'end':.8},{'text':'token.','start':1,'end':1.8}]}]}
  self.alignment={'timing_transform':{'scale':1,'offset':0},'cues':[{'scene':'one','word_start':0,'word_end':1,'start':0,'end':1.8,'source':'Example token.','ko':'예제 토큰이에요.'}]}
  self.save()
 def tearDown(self):self.tmp.cleanup()
 def save(self):
  for f,j in [('contract.json',self.contract),('timeline.json',self.timeline),('alignment.json',self.alignment)]: (self.root/f).write_text(json.dumps(j,ensure_ascii=False))
  self.write_subs()
 def write_subs(self):
  def stamp(t,sep):
   ms=round(t*1000);h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{mi:02}:{s:02}{sep}{ms:03}'
  cues=self.alignment.get('cues',[]) if isinstance(self.alignment,dict) else []
  blocks=lambda sep:[f'{i+1}\n{stamp(c["start"],sep)} --> {stamp(c["end"],sep)}\n{c["ko"]}' for i,c in enumerate(cues) if isinstance(c.get('start'),(int,float)) and isinstance(c.get('end'),(int,float)) and c['start']>=0 and c['end']>=0]
  (self.root/'ko.srt').write_text('\n\n'.join(blocks(','))+'\n');(self.root/'ko.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(blocks('.'))+'\n')
 def check(self):return m.audit(self.root,duration=2)
 def reject(self):self.save();self.assertFalse(self.check()['passed'])
 def test_inferred_korean(self):
  self.contract['subtitles'].pop('language');self.contract['language']={'screen':'ko','narration':'en'};self.alignment['cues'][0]['ko']='English only';self.reject()
 def test_language_disagreement(self):self.contract['language']={'subtitles':'en'};self.reject()
 def test_nonobject_language(self):self.contract['language']=[];self.reject()
 def test_timeline_hash_mismatch(self):self.alignment['timeline_sha256']='0'*64;self.reject()
 def test_original_hash_mismatch(self):self.contract['artifacts']['original_video']='x.mp4';self.alignment['original_video_sha256']='0'*64;self.reject()
 def test_missing_original_reference(self):self.alignment['original_video_sha256']='0'*64;self.reject()
 def test_required_binding_missing(self):self.contract['subtitles']['require_media_binding']=True;self.reject()
 def bind_media(self):
  self.save()
  import hashlib
  self.contract['artifacts']['video_master']='x.mp4';self.contract['subtitles']['require_media_binding']=True
  digest=hashlib.sha256((self.root/'x.mp4').read_bytes()).hexdigest()
  self.alignment['media_bindings']=[{'artifact':a,'sha256':digest} for a in ['video','video_master']]
 def test_valid_media_binding(self):self.bind_media();self.assertTrue(self.check()['passed'])
 def test_tampered_media_binding(self):self.bind_media();self.alignment['media_bindings'][0]['sha256']='0'*64;self.reject()
 def test_valid(self):
  import hashlib
  self.save();self.contract['artifacts']['original_video']='x.mp4'
  self.alignment['timeline_sha256']=hashlib.sha256((self.root/self.contract['artifacts']['caption_timeline']).read_bytes()).hexdigest()
  self.alignment['original_video_sha256']=hashlib.sha256((self.root/'x.mp4').read_bytes()).hexdigest()
  self.assertTrue(self.check()['passed'])
 def test_missing_srt(self):(self.root/'ko.srt').unlink();self.assertFalse(self.check()['passed'])
 def test_missing_vtt(self):(self.root/'ko.vtt').unlink();self.assertFalse(self.check()['passed'])
 def test_no_cues(self):self.alignment['cues']=[];self.reject()
 def test_english_only(self):self.alignment['cues'][0]['ko']='English only';self.reject()
 def test_three_lines(self):self.alignment['cues'][0]['ko']='첫 줄\n둘째 줄\n셋째 줄';self.reject()
 def test_long_line(self):self.alignment['cues'][0]['ko']='한'*33;self.reject()
 def test_fast_reading(self):self.alignment['cues'][0]['ko']='한'*25+'\n'+'글'*25;self.reject()
 def test_short_exposure(self):self.alignment['cues'][0]['end']=.5;self.reject()
 def test_outside_video(self):self.alignment['cues'][0]['end']=3;self.reject()
 def test_start_drift(self):self.alignment['cues'][0]['start']=.5;self.reject()
 def test_wrong_source(self):self.alignment['cues'][0]['source']='Not spoken';self.reject()
 def test_omitted_word(self):self.alignment['cues'][0]['word_end']=0;self.alignment['cues'][0]['source']='Example';self.reject()
 def test_duplicate_word(self):self.alignment['cues'].append(dict(self.alignment['cues'][0]));self.reject()
 def test_wrong_scene(self):self.alignment['cues'][0]['scene']='absent';self.reject()
 def test_invalid_index(self):self.alignment['cues'][0]['word_end']=5;self.reject()
 def test_bool_index(self):self.alignment['cues'][0]['word_start']=False;self.reject()
 def test_negative_scale(self):self.alignment['timing_transform']['scale']=-1;self.reject()
 def test_nonobject_alignment(self):self.alignment=[];self.reject()
 def test_escape(self):self.contract['artifacts']['captions_srt']='../outside.srt';self.reject()
 def test_srt_divergence(self):(self.root/'ko.srt').write_text('1\n00:00:00,000 --> 00:00:01,800\n다른 자막\n');self.assertFalse(self.check()['passed'])
 def test_invalid_utf8(self):(self.root/'ko.vtt').write_bytes(b'\xff');self.assertFalse(self.check()['passed'])
if __name__=='__main__':unittest.main()
