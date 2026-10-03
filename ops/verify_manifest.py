#!/usr/bin/env python3
from pathlib import Path,PurePosixPath
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('root',nargs='?',type=Path,default=Path(__file__).resolve().parent.parent);a=p.parse_args();root=a.root.resolve();m=json.loads((root/'MANIFEST.json').read_text());seen=set()
for x in m['files']:
 rel=PurePosixPath(x['path']);assert not rel.is_absolute() and '..' not in rel.parts and x['path'] not in seen;seen.add(x['path']);f=(root/x['path']).resolve();assert f.is_relative_to(root) and f.is_file(),x['path'];raw=f.read_bytes();assert len(raw)==x['bytes'] and hashlib.sha256(raw).hexdigest()==x['sha256'],x['path']
print(json.dumps({'passed':True,'manifest_files':len(seen),'all_sizes_and_sha256_match':True}))
