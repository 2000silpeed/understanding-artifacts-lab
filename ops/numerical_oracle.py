#!/usr/bin/env python3
"""Independent Python numerical oracle for the illustrative next-token demo."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def softmax(z, t):
    if t <= 0 or not math.isfinite(t):
        raise ValueError('temperature must be finite and positive')
    peak = max(z)
    weights = [math.exp((x-peak)/t) for x in z]
    mass = sum(weights)
    return [w/mass for w in weights]

def nucleus(probabilities, threshold):
    if not 0 < threshold <= 1:
        raise ValueError('threshold must be in (0,1]')
    order = sorted(range(len(probabilities)), key=lambda i: (-probabilities[i], i))
    keep, mass = [], 0.0
    for i in order:
        keep.append(i)
        mass += probabilities[i]
        if mass >= threshold:
            break
    return {'keep':keep, 'mass':mass, 'probabilities':[p/mass if i in keep else 0.0 for i,p in enumerate(probabilities)]}

if __name__ == '__main__':
    spec = json.loads((ROOT/'contract.json').read_text())['example']['values']
    z = spec['logits']
    rows = []
    for t in [.2, .5, 1., 1.5, 2.]:
        p = softmax(z,t)
        for cutoff in [.05,.6,.8,.95,1.]:
            rows.append({'temperature':t,'top_p':cutoff,'base':p,**nucleus(p,cutoff)})
    reference = {'evidence_type':'computed_from_illustrative_inputs','rows':rows,'special_cases':{'extreme_logits':softmax([10000,9999,-10000],1.),'ties':nucleus([.25]*4,.5)}}
    (ROOT/'tests').mkdir(exist_ok=True)
    (ROOT/'tests/python-oracle.json').write_text(json.dumps(reference,indent=2)+'\n')
    default = next(x for x in rows if x['temperature']==1. and x['top_p']==.8)
    assert default['keep']==[0,1]
    assert abs(default['probabilities'][0] - .7310585786300049)<1e-14
    assert all(abs(sum(r['base'])-1)<1e-14 and abs(sum(r['probabilities'])-1)<1e-14 for r in rows)
    print(json.dumps({'oracle_cases':len(rows)+2,'default':default,'all_normalized':True},ensure_ascii=False))
