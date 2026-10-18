#!/usr/bin/env python3
import json, math, sys
H=[1.0,2.0]
W=[[0.0,0.0,0.0],[0.0,0.0,0.0]]
TARGET_ID=2
LEARNING_RATE=0.3
EPSILON=1e-6

def validate(h,w,target):
    if len(h)!=2 or len(w)!=2 or any(len(r)!=3 for r in w): raise ValueError('shape')
    if not all(math.isfinite(x) for row in w for x in row): raise ValueError('finite')
    if not all(math.isfinite(x) for x in h): raise ValueError('finite')
    if type(target) is not int or target not in range(3): raise ValueError('target')

def logits(h,w):
    validate(h,w,TARGET_ID)
    return [sum(h[i]*w[i][j] for i in range(2)) for j in range(3)]

def softmax(z):
    if len(z)!=3 or not all(math.isfinite(x) for x in z): raise ValueError('logits')
    m=max(z); ex=[math.exp(x-m) for x in z]; s=sum(ex)
    return [x/s for x in ex]

def loss_from_z(z,target=TARGET_ID):
    p=softmax(z)
    if type(target) is not int or target not in range(3): raise ValueError('target')
    return -math.log(p[target])

def gradient_from(h,w,target=TARGET_ID):
    validate(h,w,target)
    p=softmax(logits(h,w)); g=[v for v in p]; g[target]-=1.0
    dW=[[h[i]*g[j] for j in range(3)] for i in range(2)]
    return p,g,dW

def update(h,w,target=TARGET_ID,lr=LEARNING_RATE):
    _,_,d=gradient_from(h,w,target)
    return [[w[i][j]-lr*d[i][j] for j in range(3)] for i in range(2)]

def finite_difference(h,w,target=TARGET_ID,eps=EPSILON):
    out=[]
    for i in range(2):
        row=[]
        for j in range(3):
            plus=[r[:] for r in w]; minus=[r[:] for r in w]
            plus[i][j]+=eps; minus[i][j]-=eps
            row.append((loss_from_z(logits(h,plus),target)-loss_from_z(logits(h,minus),target))/(2*eps))
        out.append(row)
    return out

def trace():
    p,g,d=gradient_from(H,W); nw=update(H,W); zn=logits(H,nw); pn=softmax(zn)
    alt_h=[1.0,0.0]; ap,ag,ad=gradient_from(alt_h,W)
    return {'contract':{'h':H,'W':W,'target_id':TARGET_ID,'learning_rate':LEARNING_RATE,'bias':False},'initial':{'z':logits(H,W),'p':p,'loss':loss_from_z(logits(H,W))},'gradient':{'g':g,'dW':d,'finite_difference':finite_difference(H,W)},'update':{'W_prime':nw,'z_prime':zn,'p_prime':pn,'loss_prime':loss_from_z(zn)},'alternate_h':{'h':alt_h,'z':logits(alt_h,W),'g':ag,'dW':ad,'W_prime':update(alt_h,W)},'edge':{'h':[0.0,0.0],'z':logits([0.0,0.0],W),'g':gradient_from([0.0,0.0],W)[1],'dW':gradient_from([0.0,0.0],W)[2]}}

def f(x): return format(x,'.12f')
def line_matrix(m): return '['+';'.join(','.join(f(x) for x in r) for r in m)+']'
def line_vec(v): return '['+','.join(f(x) for x in v)+']'

def main():
    t=trace(); fd=t['gradient']['finite_difference']; d=t['gradient']['dW']
    lines=[
      'OUTPUT_WEIGHT_MATRIX_MANUAL',
      'h='+line_vec(H)+' target_id=2 lr=0.300000000000',
      'z='+line_vec(t['initial']['z'])+' p='+line_vec(t['initial']['p'])+' loss='+f(t['initial']['loss']),
      'g='+line_vec(t['gradient']['g'])+' dW='+line_matrix(d),
      'finite_difference='+line_matrix(fd),
      'W_prime='+line_matrix(t['update']['W_prime'])+' z_prime='+line_vec(t['update']['z_prime']),
      'p_prime='+line_vec(t['update']['p_prime'])+' loss_prime='+f(t['update']['loss_prime']),
      'alternate_h=[1.000000000000,0.000000000000] dW='+line_matrix(t['alternate_h']['dW']),
      'edge_h=[0.000000000000,0.000000000000] dW='+line_matrix(t['edge']['dW']),
    ]
    if '--trace' in sys.argv: print(json.dumps(t,ensure_ascii=False,separators=(',',':')))
    else: print('\n'.join(lines))
if __name__=='__main__': main()
