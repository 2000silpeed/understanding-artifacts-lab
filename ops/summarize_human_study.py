#!/usr/bin/env python3
"""Re-score submitted self-declared sessions, not verified people or causal effects."""
import argparse,collections,json,math,statistics
from datetime import datetime,timedelta
from pathlib import Path
VERSION='1.1.0-pilot1'
def timestamp(value):
 if not isinstance(value,str):raise ValueError('invalid_timestamp')
 try:d=datetime.fromisoformat(value.replace('Z','+00:00'))
 except ValueError:raise ValueError('invalid_timestamp')
 if d.tzinfo is None:raise ValueError('invalid_timestamp')
 return d

def score(qs,answers):
 if not isinstance(answers,list) or len(answers)!=len(qs):raise ValueError('incomplete_answers')
 if any(type(a)is not int or not 0<=a<len(q['options']) for a,q in zip(answers,qs)):raise ValueError('invalid_answers')
 return sum(a==q['answer'] for a,q in zip(answers,qs))

def summarize(input_dir,bank,content):
 if not input_dir.is_dir():raise ValueError('Input directory does not exist; do not report a missing source as zero people')
 accepted={};excluded=collections.Counter();files=sorted(input_dir.glob('*.json'));duplicates=0;conflicted=set()
 for path in files:
  try:
   r=json.loads(path.read_text())
   if r.get('synthetic')is not False:raise ValueError('synthetic_or_unverified_origin')
   if r.get('study_version')!=VERSION or r.get('schema_version')!=1 or r.get('consent')is not True or r.get('human')is not True or r.get('participant_mode')!='self_declared_human':raise ValueError('version_or_consent')
   if not isinstance(r.get('id'),str) or not r['id']:raise ValueError('missing_id')
   if r['id'] in conflicted:raise ValueError('conflicting_duplicate_id')
   if r.get('kind')not in ('learning','listening'):raise ValueError('unknown_kind')
   if r.get('topic')not in bank:raise ValueError('unknown_topic')
   expected=content[r['topic']]['fingerprints']
   if r.get('artifact_fingerprints')!=expected:raise ValueError('artifact_identity_mismatch')
   if any(v=='pending' for v in expected.values()):raise ValueError('unfinalized_artifact')
   times=r.get('timings')or{}
   if not isinstance(times,dict) or any(type(v)not in (int,float) or not math.isfinite(v) or v<0 for v in times.values()):raise ValueError('invalid_timing')
   started=timestamp(r.get('started_at'));exported=timestamp(r.get('exported_at'));completed=timestamp(r.get('completed_at'))
   if not started<=completed<=exported:raise ValueError('invalid_timestamp_order')
   if r.get('phase')!='complete':raise ValueError('incomplete_session')
   r['_exported']=exported
   if r['kind']=='learning':
    if type(r.get('format'))is not int or not 0<=r['format']<4:raise ValueError('invalid_format')
    if type(r.get('cross_format_exposure'))is not bool:raise ValueError('missing_exposure_declaration')
    q=bank[r['topic']];responses=r.get('responses')or{}
    r['_pre']=score(q['pre'],responses.get('pre'));r['_post']=score(q['post'],responses.get('post'));r['_retention']=None
    if responses.get('retention')is not None:
     retained=timestamp(r.get('retention_completed_at'))
     if retained-completed<timedelta(hours=24) or retained>exported:raise ValueError('retention_gate_not_met')
     if type(r.get('retention_cross_format_exposure'))is not bool:raise ValueError('missing_retention_exposure')
     r['_retention']=score(q['retention'],responses['retention'])
   else:
    responses=(r.get('responses')or{}).get('listening')or{}
    for key,size in [('audibility',3),('readability',5),('synchronization',4),('english_comprehension',4)]:
     if type(responses.get(key))is not int or not 0<=responses[key]<size:raise ValueError('incomplete_listening')
   old=accepted.get(r['id'])
   if old:
    if (old['kind'],old['topic'],old.get('format'))!=(r['kind'],r['topic'],r.get('format')):
     del accepted[r['id']];conflicted.add(r['id']);excluded['conflicting_duplicate_id']+=2;continue
    duplicates+=1
    if old['_exported']>r['_exported']:continue
   accepted[r['id']]=r
  except (ValueError,KeyError,TypeError,IndexError,AttributeError)as e:excluded[str(e)or type(e).__name__]+=1
 learning=[r for r in accepted.values() if r['kind']=='learning'];listening=[r for r in accepted.values() if r['kind']=='listening']
 def avg(rows,key):return statistics.mean(r[key] for r in rows) if rows else None
 groups=[]
 for topic in bank:
  for f,name in enumerate(('writing','diagram','web','video')):
   all_rows=[r for r in learning if r['topic']==topic and r['format']==f]
   clean=[r for r in all_rows if r['cross_format_exposure']is False];dirty=[r for r in all_rows if r['cross_format_exposure']is True]
   retention=[r for r in clean if r['_retention']is not None and r['retention_cross_format_exposure']is False]
   dirty_retention=[r for r in all_rows if r['_retention']is not None and (r['cross_format_exposure']or r['retention_cross_format_exposure'])]
   groups.append({'topic':topic,'format':name,'submitted_sessions':len(all_rows),'primary_sessions':len(clean),'mean_pre_correct':avg(clean,'_pre'),'mean_post_correct':avg(clean,'_post'),'mean_gain_correct':statistics.mean(r['_post']-r['_pre'] for r in clean) if clean else None,'cross_format_sessions':len(dirty),'contaminated_mean_gain_correct':statistics.mean(r['_post']-r['_pre'] for r in dirty) if dirty else None,'retention_submissions':len(retention),'mean_retention_correct':avg(retention,'_retention'),'retention_cross_format_sessions':len(dirty_retention)})
 return {'evidence_status':'submitted_self_declared_responses' if accepted else 'not_measured','scope':'Submitted sessions, not verified people or causal format effects','human_identity_verified':False,'human_learning_claim':'NOT ESTABLISHED','submitted_files':len(files),'submitted_self_declared_human_sessions':len(accepted),'learning_sessions':len(learning),'listening_sessions':len(listening),'duplicate_exports_ignored':duplicates,'conflicting_ids_excluded':len(conflicted),'excluded_by_reason':dict(excluded),'groups':groups,'listening':{'sessions':len(listening),'audible_output_verified':False,'mean_observed_unmuted_media_progress_seconds':statistics.mean(r.get('timings',{}).get('observed_unmuted_media_progress_seconds',0) for r in listening) if listening else None},'limits':['Self-declaration is not authentication; multiple sessions may belong to one person.','Timestamps are checked for consistency, not clock authentication.','Question bank and artifact fingerprints must match the release.','Primary means exclude cross-format exposure; contaminated records are separately reported.','Scores do not establish learning effects, rankings, causal effects or population inference.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input_dir',type=Path);p.add_argument('--bank',type=Path,default=Path(__file__).resolve().parents[1]/'study/question-bank.json');p.add_argument('--report',type=Path);a=p.parse_args();bank={b['id']:b for b in json.loads(a.bank.read_text())};content=json.loads((a.bank.parent/'content.json').read_text())
 import hashlib
 digest=hashlib.sha256(a.bank.read_bytes()).hexdigest()
 if any(v.get('fingerprints',{}).get('question_bank',digest)!=digest for v in content.values()):raise ValueError('Question bank does not match the frozen release artifact identity')
 data=summarize(a.input_dir,bank,content);text=json.dumps(data,ensure_ascii=False,indent=2)
 if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(text+'\n')
 print(text)
