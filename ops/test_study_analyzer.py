"""All inputs here are synthetic unit fixtures, including fake self-declaration flags."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('study',Path(__file__).with_name('summarize_human_study.py'));assert spec is not None and spec.loader is not None;mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name);qs=[{'options':['A','B'],'answer':1}]*3;self.bank={'next-token':{'pre':qs,'post':qs,'retention':qs}};self.content={'next-token':{'fingerprints':{'x':'expected'}}}
  self.x={'id':'12-34-56-78','schema_version':1,'study_version':'1.1.0-pilot1','kind':'learning','phase':'complete','synthetic':False,'consent':True,'participant_mode':'self_declared_human','topic':'next-token','format':0,'artifact_fingerprints':{'x':'expected'},'responses':{'pre':[0,0,0],'post':[1,1,1]},'timings':{},'exported_at':'2026-10-03T01:00:00Z'}
  self.x.update(human=True,started_at='2026-10-03T00:58:00Z',completed_at='2026-10-03T00:59:00Z',cross_format_exposure=False)
 def tearDown(self):self.t.cleanup()
 def save(self,x=None,name='a.json'):(self.p/name).write_text(json.dumps(self.x if x is None else x))
 def run_report(self):return mod.summarize(self.p,self.bank,self.content)
 def test_empty(self):
  q=self.run_report();self.assertEqual(q['submitted_self_declared_human_sessions'],0);self.assertIsNone(q['groups'][0]['mean_gain_correct']);self.assertEqual(q['evidence_status'],'not_measured')
 def test_QA_never_human(self):self.x['synthetic']=True;self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_no_QA_flag_rejected(self):del self.x['synthetic'];self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_no_consent(self):self.x['consent']=False;self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_recompute_not_trust_exported_scores(self):
  self.x['score']=999;self.save();q=self.run_report();self.assertEqual(q['groups'][0]['mean_post_correct'],3);self.assertFalse(q['human_identity_verified'])
 def test_missing_answers(self):self.x['responses']['post']=[];self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_bool_not_valid_answer(self):self.x['responses']['post']=[True]*3;self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_hash_mismatch(self):self.x['artifact_fingerprints']['x']='bad';self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_duplicate_latest_only(self):
  self.save();self.x['exported_at']='2026-10-03T02:00:00Z';self.x['responses']['post']=[0]*3;self.save(name='b.json');q=self.run_report();self.assertEqual(q['submitted_self_declared_human_sessions'],1);self.assertEqual(q['groups'][0]['mean_post_correct'],0)
 def test_conflicting_duplicate_rejected(self):self.save();self.x['format']=1;self.save(name='b.json');self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_no_negative_time(self):self.x['timings']={'elapsed':-1};self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def retention(self,seconds):
  from datetime import datetime,timedelta
  t=datetime.fromisoformat(self.x['completed_at'].replace('Z','+00:00'))+timedelta(seconds=seconds)
  self.x.update(retention_completed_at=t.isoformat(),exported_at=(t+timedelta(seconds=1)).isoformat(),retention_cross_format_exposure=False);self.x['responses']['retention']=[1,0,1]
 def test_retention_rescored(self):self.retention(86400);self.save();self.assertEqual(self.run_report()['groups'][0]['mean_retention_correct'],2)
 def test_early_retention_rejected(self):self.retention(1);self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_retention_boundary_below(self):self.retention(86399);self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_missing_retention_stamp(self):self.x['responses']['retention']=[1,0,1];self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_dirty_learning_not_primary(self):self.x['cross_format_exposure']=True;self.save();g=self.run_report()['groups'][0];self.assertEqual(g['primary_sessions'],0);self.assertIsNone(g['mean_gain_correct']);self.assertEqual(g['cross_format_sessions'],1)
 def test_dirty_retention_not_primary(self):self.retention(86400);self.x['retention_cross_format_exposure']=True;self.save();g=self.run_report()['groups'][0];self.assertEqual(g['retention_submissions'],0);self.assertEqual(g['retention_cross_format_sessions'],1)
 def test_duplicate_reverse_file_order(self):self.x['format']=1;self.save();self.x['format']=0;self.save(name='b.json');self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_nan_timing(self):self.x['timings']={'elapsed':float('nan')};self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_human_declaration_required(self):self.x['human']=False;self.save();self.assertEqual(self.run_report()['submitted_self_declared_human_sessions'],0)
 def test_missing_directory(self):
  with self.assertRaises(ValueError):mod.summarize(self.p/'missing',self.bank,self.content)
if __name__=='__main__':unittest.main(verbosity=2)
