// 작은 신경망의 역전파 — tanh 은닉층 가중치 하나가 학습되는 과정 (C++17, 표준 라이브러리만).
//
// 신경망: 입력 2개 → tanh 은닉 뉴런 2개 → 선형 출력 1개, 편향 없음, 학습 예 1개.
// 손실 L = ½(ŷ − y)². 영상이 따라가는 가중치 w = W[0][0] (입력 x1 → 은닉 뉴런 h1).
//
//     dL/dw = (ŷ − y) · v1 · (1 − h1²) · x1
//
// 빌드·실행:
//     c++ -std=c++17 -O2 -Wall -Wextra -o tanh_backprop tanh_backprop.cpp && ./tanh_backprop
// 출력은 tanh_backprop.py와 글자 하나까지 같다.
#include <array>
#include <cmath>
#include <cstdio>

using Mat = std::array<std::array<double, 2>, 2>;
using Vec = std::array<double, 2>;

constexpr Vec X{1.0, 0.5};      // 입력 x1, x2
constexpr double Y = 1.0;       // 목표값
constexpr double ETA = 0.5;     // 학습률
constexpr int STEPS = 10;       // 반복 학습 횟수
constexpr double SAT_Z = 3.0;   // 포화 예: 은닉 뉴런 입력이 3일 때
constexpr double EPS = 1e-6;    // 수치 미분 간격

struct Fwd { Vec z, h; double y_hat, loss; };
struct Grad { Fwd f; double delta; Vec grad_v, slope, delta_h; Mat grad_W; };

Fwd forward(const Mat& W, const Vec& v) {
  Fwd r{};
  for (int j = 0; j < 2; ++j) {
    r.z[j] = W[j][0] * X[0] + W[j][1] * X[1];
    r.h[j] = std::tanh(r.z[j]);
  }
  r.y_hat = v[0] * r.h[0] + v[1] * r.h[1];
  r.loss = 0.5 * (r.y_hat - Y) * (r.y_hat - Y);
  return r;
}

Grad backward(const Mat& W, const Vec& v) {
  Grad g{};
  g.f = forward(W, v);
  g.delta = g.f.y_hat - Y;                                  // dL/dŷ
  for (int j = 0; j < 2; ++j) {
    g.grad_v[j] = g.delta * g.f.h[j];                       // dL/dv_j = δ · h_j
    g.slope[j] = 1 - g.f.h[j] * g.f.h[j];                   // tanh'(z_j) = 1 − h_j²
    g.delta_h[j] = g.delta * v[j] * g.slope[j];             // dL/dz_j
    for (int i = 0; i < 2; ++i) g.grad_W[j][i] = g.delta_h[j] * X[i];  // dL/dW_ji = δ_j · x_i
  }
  return g;
}

// w 하나의 기울기만, 영상의 코드 장면(Python) 그대로 네 줄.
double grad_w_four_lines(double y_hat, double v1, double h1, double x1) {
  const double delta = y_hat - Y;              // 오차
  const double back = delta * v1;              // 출력 가중치를 곱해 뒤로
  const double delta_h = back * (1 - h1 * h1); // tanh 기울기를 곱하고
  return delta_h * x1;                         // 마지막에 입력을 곱한다
}

void step(Mat& W, Vec& v, const Grad& g) {
  for (int j = 0; j < 2; ++j) {
    for (int i = 0; i < 2; ++i) W[j][i] -= ETA * g.grad_W[j][i];
    v[j] -= ETA * g.grad_v[j];
  }
}

int main() {
  Mat W{{{0.5, 0.2}, {-0.3, 0.4}}};
  Vec v{0.8, -0.6};
  const Grad g = backward(W, v);
  std::printf("# forward\n");
  std::printf("z1 = w*x1 + W12*x2 = %.6f\n", g.f.z[0]);
  std::printf("h1 = tanh(z1) = %.6f\n", g.f.h[0]);
  std::printf("z2 = %.6f  h2 = %.6f\n", g.f.z[1], g.f.h[1]);
  std::printf("y_hat = v1*h1 + v2*h2 = %.6f\n", g.f.y_hat);
  std::printf("loss = 0.5*(y_hat - y)^2 = %.6f\n", g.f.loss);
  std::printf("# backward\n");
  std::printf("delta = y_hat - y = %.6f\n", g.delta);
  std::printf("dL/dv1 = delta*h1 = %.6f\n", g.grad_v[0]);
  std::printf("tanh slope = 1 - h1^2 = %.6f\n", g.slope[0]);
  std::printf("delta_h1 = delta*v1*slope = %.6f\n", g.delta_h[0]);
  std::printf("dL/dw = delta_h1*x1 = %.6f\n", g.grad_W[0][0]);
  Mat Wp = W, Wm = W;
  Wp[0][0] += EPS;
  Wm[0][0] -= EPS;
  const double numeric = (forward(Wp, v).loss - forward(Wm, v).loss) / (2 * EPS);
  std::printf("numeric dL/dw = %.6f\n", numeric);
  std::printf("dL/dw (4 lines) = %.6f\n", grad_w_four_lines(g.f.y_hat, v[0], g.f.h[0], X[0]));
  std::printf("# update\n");
  Mat W1 = W;
  Vec v1 = v;
  step(W1, v1, g);
  std::printf("w: %.6f -> %.6f\n", W[0][0], W1[0][0]);
  const Fwd after = forward(W1, v1);
  std::printf("loss: %.6f -> %.6f\n", g.f.loss, after.loss);
  std::printf("y_hat: %.6f -> %.6f\n", g.f.y_hat, after.y_hat);
  std::printf("# training\n");
  Mat Wt = W;
  Vec vt = v;
  for (int k = 0; k <= STEPS; ++k) {
    const Grad gt = backward(Wt, vt);
    std::printf("step %2d  loss %.6f  w %.6f  y_hat %.6f\n", k, gt.f.loss, Wt[0][0], gt.f.y_hat);
    step(Wt, vt, gt);
  }
  std::printf("# saturation\n");
  const double hs = std::tanh(SAT_Z), sat_slope = 1 - hs * hs, sat_grad = g.delta * v[0] * sat_slope * X[0];
  std::printf("z = %.6f  h = %.6f  slope = %.6f\n", SAT_Z, hs, sat_slope);
  std::printf("dL/dw at z=3 = %.6f  (vs %.6f)\n", sat_grad, g.grad_W[0][0]);
  return 0;
}
