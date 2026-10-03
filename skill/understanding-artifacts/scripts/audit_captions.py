#!/usr/bin/env python3
"""Validate subtitle files and source-word alignment. NOT translation/listening certification.
Usage: python3 audit_captions.py ROOT --report report.json
ROOT/contract.json declares subtitle settings and relative caption artifact paths.
"""
import argparse,hashlib,html,json,math,re,subprocess
from pathlib import Path

def finite(x):return type(x) in (int,float) and math.isfinite(x)
def parse_cues(text,vtt=False):
 text=text.replace('\r\n','\n').strip()
 if vtt:
  if not text.startswith('WEBVTT\n'):raise ValueError('Missing WEBVTT header')
  text=text.split('\n',1)[1].strip()
 if not text:raise ValueError('Empty captions')
 cues=[];sep='.' if vtt else ','
 def seconds(s):
  match=re.fullmatch(r'(\d{2,}):(\d{2}):(\d{2})'+re.escape(sep)+r'(\d{3})',s)
  if not match:raise ValueError('Invalid subtitle timestamp')
  h,m,se,ms=map(int,match.groups())
  if m>=60 or se>=60:raise ValueError('Invalid minutes/seconds')
  return h*3600+m*60+se+ms/1000
 for i,block in enumerate(re.split(r'\n\s*\n',text)):
  lines=block.splitlines()
  if lines and '-->' not in lines[0]:
   if lines.pop(0)!=str(i+1):raise ValueError('Nonconsecutive cue number')
  if len(lines)<2:raise ValueError('Missing timing or text')
  times=lines.pop(0).split(' --> ')
  if len(times)!=2:raise ValueError('Invalid timing line')
  content='\n'.join(lines)
  cues.append({'start':seconds(times[0]),'end':seconds(times[1]),'ko':html.unescape(content) if vtt else content})
 return cues

def audit(root,duration=None):
 root=Path(root).resolve();checks=[]
 def check(name,ok,detail=''):checks.append({'name':name,'passed':bool(ok),'detail':detail})
 def result():return {'passed':bool(checks) and all(c['passed'] for c in checks),'scope':'Structure, readability thresholds, timing and source-word coverage; not translation quality, audible sync, visual overlap, WCAG certification or learning effectiveness.','checks':checks}
 def path(rel):
  if not isinstance(rel,str) or not rel or Path(rel).is_absolute():raise ValueError('Expected relative artifact path')
  p=(root/rel).resolve()
  if not p.is_relative_to(root):raise ValueError('Artifact path escapes root')
  return p
 try:
  contract=json.loads((root/'contract.json').read_text(encoding='utf-8'))
  if not isinstance(contract,dict):raise ValueError('Contract must be object')
  settings=contract.get('subtitles',{});art=contract.get('artifacts',{})
  if not isinstance(settings,dict) or not isinstance(art,dict):raise ValueError('Invalid subtitle contract')
  language_contract=contract.get('language',{})
  if not isinstance(language_contract,dict):raise ValueError('Invalid language contract')
  caption_language=settings.get('language',language_contract.get('subtitles',language_contract.get('screen')))
  if language_contract.get('subtitles') and language_contract['subtitles']!=caption_language:raise ValueError('Subtitle language declarations disagree')
  srt=parse_cues(path(art['captions_srt']).read_text(encoding='utf-8'))
  vtt=parse_cues(path(art['captions_vtt']).read_text(encoding='utf-8'),True)
  alignment=json.loads(path(art['caption_alignment']).read_text(encoding='utf-8'))
  timeline_path=path(art['caption_timeline']);timeline=json.loads(timeline_path.read_text(encoding='utf-8'))
  if not isinstance(alignment,dict) or not isinstance(timeline,dict):raise ValueError('Alignment/timeline must be objects')
  def matches_hash(filename,digest):return isinstance(digest,str) and bool(re.fullmatch('[0-9a-f]{64}',digest)) and hashlib.sha256(path(filename).read_bytes()).hexdigest()==digest
  if 'timeline_sha256' in alignment:check('timeline_sha256',matches_hash(art['caption_timeline'],alignment['timeline_sha256']))
  if 'original_video_sha256' in alignment:check('original_video_sha256',matches_hash(art['original_video'],alignment['original_video_sha256']))
  bindings=alignment.get('media_bindings',[])
  if not isinstance(bindings,list):raise ValueError('Media bindings must be a list')
  bound=set()
  for i,binding in enumerate(bindings):
   if not isinstance(binding,dict):raise ValueError('Invalid media binding')
   name=binding['artifact']
   check(f'media_binding_unique_{i}',name not in bound);bound.add(name)
   check(f'media_binding_hash_{name}',matches_hash(art[name],binding['sha256']))
  if settings.get('require_media_binding',False):check('required_media_bindings',{'video','video_master'}<=bound)
  cues=alignment.get('cues');scenes=timeline.get('scenes')
  if not isinstance(cues,list) or not cues or not isinstance(scenes,list) or not scenes:raise ValueError('Missing cues/scenes')
  if alignment.get('timeline_sha256'):check('timeline_hash',alignment['timeline_sha256']==hashlib.sha256(timeline_path.read_bytes()).hexdigest(),'Source timeline SHA-256')
  transform=alignment.get('timing_transform',{});scale=transform.get('scale',1);offset=transform.get('offset',0)
  if not finite(scale) or scale<=0 or not finite(offset):raise ValueError('Invalid timing transform')
  if duration is None:
   probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path(art['video']))],capture_output=True,text=True,check=True,timeout=30)
   duration=float(json.loads(probe.stdout)['format']['duration'])
  if not finite(duration) or duration<=0:raise ValueError('Invalid video duration')
  check('cue_count',len(cues)==len(srt)==len(vtt),{'alignment':len(cues),'srt':len(srt),'vtt':len(vtt)})
  limits={'max_lines':2,'max_chars_per_line':32,'min_duration':1.0,'max_cps':20,'max_sync_error':.12,'max_end_hold':1.0}
  limits.update({k:settings[k] for k in limits if k in settings})
  if any(not finite(v) or v<=0 for v in limits.values()):raise ValueError('Invalid subtitle threshold')
  by_id={s['id']:s for s in scenes};total=sum(len(s['words']) for s in scenes);covered=set();previous_end=0;max_cps=0;max_error=0
  if len(by_id)!=len(scenes):raise ValueError('Duplicate scene IDs')
  for i,c in enumerate(cues):
   if not isinstance(c,dict):raise ValueError('Cue must be object')
   start,end,text=c['start'],c['end'],c['ko'];a,b=c['word_start'],c['word_end'];scene=by_id[c['scene']];words=scene['words']
   if not finite(start) or not finite(end) or not isinstance(text,str):raise ValueError('Invalid cue value')
   if type(a)!=int or type(b)!=int or not 0<=a<=b<len(words):raise ValueError('Invalid source-word range')
   source=' '.join(w['text'] for w in words[a:b+1]);check(f'cue_{i}_source',c.get('source')==source,'Exact source words')
   keys={(scene['id'],n) for n in range(a,b+1)};check(f'cue_{i}_unique',not covered.intersection(keys),'No duplicated source-word assignment');covered.update(keys)
   expected_start=(scene['start']+words[a]['start'])*scale+offset;expected_end=(scene['start']+words[b]['end'])*scale+offset
   error=abs(start-expected_start);max_error=max(max_error,error)
   check(f'cue_{i}_sync',finite(expected_start) and finite(expected_end) and error<=limits['max_sync_error'] and expected_end-limits['max_sync_error']<=end<=expected_end+limits['max_end_hold'],{'start_error_seconds':round(error,4)})
   span=end-start;check(f'cue_{i}_time',0<=start<end<=duration+.02 and start>=previous_end-.002 and span>=limits['min_duration'],'Within video, ordered, no overlap, minimum exposure');previous_end=end
   lines=text.splitlines();chars=sum(len(l) for l in lines);cps=chars/span if span>0 else float('inf');max_cps=max(max_cps,cps)
   check(f'cue_{i}_readable',bool(text.strip()) and 1<=len(lines)<=limits['max_lines'] and max(map(len,lines),default=0)<=limits['max_chars_per_line'] and cps<=limits['max_cps'],{'characters_per_second':round(cps,3)})
   if caption_language=='ko':check(f'cue_{i}_korean',bool(re.search('[가-힣]',text)),'Hangul present; translation quality is a separate review')
   if i<len(srt) and i<len(vtt):check(f'cue_{i}_sidecars',all(abs(p['start']-start)<=.0011 and abs(p['end']-end)<=.0011 and p['ko']==text for p in (srt[i],vtt[i])),'SRT/VTT/translation text and milliseconds agree')
  check('source_coverage',len(covered)==total,{'covered_timed_words':len(covered),'total_timed_words':total})
  report=result();report.update({'cue_count':len(cues),'covered_source_words':len(covered),'total_source_words':total,'video_duration':duration,'max_cps':round(max_cps,3),'max_start_error':round(max_error,4)});return report
 except (OSError,ValueError,TypeError,KeyError,IndexError,AttributeError,subprocess.SubprocessError) as e:
  check('parse_or_probe',False,str(e).replace(str(root),'.'));return result()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('root');ap.add_argument('--report');args=ap.parse_args();report=audit(args.root);text=json.dumps(report,ensure_ascii=False,indent=2)
 if args.report:Path(args.report).write_text(text+'\n',encoding='utf-8')
 print(text);raise SystemExit(0 if report['passed'] else 1)
if __name__=='__main__':main()
