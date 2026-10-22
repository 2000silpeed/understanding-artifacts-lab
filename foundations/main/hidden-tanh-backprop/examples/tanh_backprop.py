"""작은 신경망의 역전파 — tanh 은닉층 가중치 하나가 학습되는 과정 (Python 3, 표준 라이브러리만).

신경망: 입력 2개 → tanh 은닉 뉴런 2개 → 선형 출력 1개, 편향 없음, 학습 예 1개.
손실 L = ½(ŷ − y)². 영상이 따라가는 가중치 w = W[0][0] (입력 x1 → 은닉 뉴런 h1).

    dL/dw = (ŷ − y) · v1 · (1 − h1²) · x1
            오차      출력 가중치  tanh 기울기  입력

실행:
    python3 tanh_backprop.py                  # 계산 과정을 출력
    python3 tanh_backprop.py --json out.json  # 영상이 읽는 값도 저장
같은 계산을 tanh_backprop.cpp(C++17)와 lab.html(브라우저)이 한다. 출력 텍스트는 C++판과 글자 하나까지 같다.
"""
import json
import math
import sys

X = [1.0, 0.5]                    # 입력 x1, x2
Y = 1.0                           # 목표값
W0 = [[0.5, 0.2], [-0.3, 0.4]]    # 은닉층 가중치 W[j][i]: 입력 i → 은닉 뉴런 j
V0 = [0.8, -0.6]                  # 출력 가중치 v[j]: 은닉 뉴런 j → 출력
ETA = 0.5                         # 학습률
STEPS = 10                        # 반복 학습 횟수
SAT_Z = 3.0                       # 포화 예: 은닉 뉴런 입력이 3일 때
EPS = 1e-6                        # 수치 미분 간격


def forward(W, v):
    z = [W[j][0] * X[0] + W[j][1] * X[1] for j in range(2)]
    h = [math.tanh(a) for a in z]
    y_hat = v[0] * h[0] + v[1] * h[1]
    loss = 0.5 * (y_hat - Y) ** 2
    return z, h, y_hat, loss


def backward(W, v):
    z, h, y_hat, loss = forward(W, v)
    delta = y_hat - Y                                    # dL/dŷ
    grad_v = [delta * h[j] for j in range(2)]            # dL/dv_j = δ · h_j
    slope = [1 - h[j] ** 2 for j in range(2)]            # tanh'(z_j) = 1 − h_j²
    delta_h = [delta * v[j] * slope[j] for j in range(2)]  # dL/dz_j
    grad_W = [[delta_h[j] * X[i] for i in range(2)] for j in range(2)]  # dL/dW_ji = δ_j · x_i
    return dict(z=z, h=h, y_hat=y_hat, loss=loss, delta=delta, grad_v=grad_v, slope=slope, delta_h=delta_h, grad_W=grad_W)


def grad_w_four_lines(y_hat, v1, h1, x1):
    """w 하나의 기울기만, 영상의 코드 장면 그대로 네 줄."""
    delta = y_hat - Y                  # 오차
    back = delta * v1                  # 출력 가중치를 곱해 뒤로
    delta_h = back * (1 - h1 ** 2)     # tanh 기울기를 곱하고
    return delta_h * x1                # 마지막에 입력을 곱한다


def step(W, v, g):
    W = [[W[j][i] - ETA * g['grad_W'][j][i] for i in range(2)] for j in range(2)]
    v = [v[j] - ETA * g['grad_v'][j] for j in range(2)]
    return W, v


def main():
    W, v = [r[:] for r in W0], V0[:]
    g = backward(W, v)
    f = lambda a: f'{a:.6f}'
    out = []
    p = out.append
    p('# forward')
    p(f'z1 = w*x1 + W12*x2 = {f(g["z"][0])}')
    p(f'h1 = tanh(z1) = {f(g["h"][0])}')
    p(f'z2 = {f(g["z"][1])}  h2 = {f(g["h"][1])}')
    p(f'y_hat = v1*h1 + v2*h2 = {f(g["y_hat"])}')
    p(f'loss = 0.5*(y_hat - y)^2 = {f(g["loss"])}')
    p('# backward')
    p(f'delta = y_hat - y = {f(g["delta"])}')
    p(f'dL/dv1 = delta*h1 = {f(g["grad_v"][0])}')
    p(f'tanh slope = 1 - h1^2 = {f(g["slope"][0])}')
    p(f'delta_h1 = delta*v1*slope = {f(g["delta_h"][0])}')
    p(f'dL/dw = delta_h1*x1 = {f(g["grad_W"][0][0])}')
    # 수치 미분으로 확인: w를 ±EPS만큼 움직여 손실 차이를 잰다
    Wp = [r[:] for r in W]; Wp[0][0] += EPS
    Wm = [r[:] for r in W]; Wm[0][0] -= EPS
    numeric = (forward(Wp, v)[3] - forward(Wm, v)[3]) / (2 * EPS)
    p(f'numeric dL/dw = {f(numeric)}')
    four = grad_w_four_lines(g['y_hat'], v[0], g['h'][0], X[0])
    p(f'dL/dw (4 lines) = {f(four)}')
    p('# update')
    W1, v1 = step(W, v, g)
    p(f'w: {f(W[0][0])} -> {f(W1[0][0])}')
    after = forward(W1, v1)
    p(f'loss: {f(g["loss"])} -> {f(after[3])}')
    p(f'y_hat: {f(g["y_hat"])} -> {f(after[2])}')
    p('# training')
    curve, ws, yhs = [], [], []
    Wt, vt = [r[:] for r in W], v[:]
    for k in range(STEPS + 1):
        gt = backward(Wt, vt)
        curve.append(gt['loss']); ws.append(Wt[0][0]); yhs.append(gt['y_hat'])
        p(f'step {k:2d}  loss {f(gt["loss"])}  w {f(Wt[0][0])}  y_hat {f(gt["y_hat"])}')
        Wt, vt = step(Wt, vt, gt)
    p('# saturation')
    hs = math.tanh(SAT_Z)
    sat_slope = 1 - hs ** 2
    sat_grad = g['delta'] * v[0] * sat_slope * X[0]
    p(f'z = {f(SAT_Z)}  h = {f(hs)}  slope = {f(sat_slope)}')
    p(f'dL/dw at z=3 = {f(sat_grad)}  (vs {f(g["grad_W"][0][0])})')
    print('\n'.join(out))

    if '--json' in sys.argv:
        path = sys.argv[sys.argv.index('--json') + 1]
        values = {
            'inputs': {'x': X, 'y': Y, 'W': W0, 'v': V0, 'eta': ETA, 'steps': STEPS, 'satZ': SAT_Z},
            'forward': {'z': g['z'], 'h': g['h'], 'y_hat': g['y_hat'], 'loss': g['loss']},
            'backward': {'delta': g['delta'], 'grad_v': g['grad_v'], 'slope': g['slope'], 'delta_h': g['delta_h'],
                         'grad_W': g['grad_W'], 'numeric_grad_w': numeric, 'four_lines_grad_w': four},
            'update': {'w_before': W[0][0], 'w_after': W1[0][0], 'loss_after': after[3], 'y_hat_after': after[2]},
            'training': {'loss': curve, 'w': ws, 'y_hat': yhs},
            'saturation': {'z': SAT_Z, 'h': hs, 'slope': sat_slope, 'grad_w': sat_grad},
            'trace': out,
        }
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(values, fh, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
