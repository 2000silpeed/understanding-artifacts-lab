// Minibatch training of a tiny bigram language model — C++17 twin of minibatch.py.
//
// Model: a V x V score table W (row = previous word, column = next word), p = softmax(W[prev]).
// Loss of one example = -log p[next]; its gradient is p - onehot(next) in row `prev` only.
// Minibatch step: average B losses and B gradients, then W <- W - lr * mean gradient.
// Same inputs (data/corpus.txt, data/config.txt), same LCG shuffle, same arithmetic order as the Python file,
// so the JSON it prints matches examples/out/python-result.json (test_source.py compares them).
//
// build: c++ -std=c++17 -O2 -Wall -Wextra -pedantic -o out/minibatch-cpp minibatch.cpp
// run:   out/minibatch-cpp data/ > out/cpp-result.json
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using Row = std::vector<double>;
using Mat = std::vector<Row>;

struct Config {
  double lr = 0;
  uint32_t seed = 0;
  int walkB = 0, walkSteps = 0, epochs = 0;
  std::vector<int> curveBatches;
  double eps = 0;
};

struct Lcg {  // 32-bit LCG, Numerical Recipes constants (as in minibatch.py)
  uint32_t state;
  explicit Lcg(uint32_t s) : state(s) {}
  uint32_t next() { state = 1664525u * state + 1013904223u; return state; }
};

static std::vector<int> shuffled(int n, Lcg& rng) {
  std::vector<int> order(n);
  for (int i = 0; i < n; i++) order[i] = i;
  for (int i = n - 1; i > 0; i--) std::swap(order[i], order[rng.next() % static_cast<uint32_t>(i + 1)]);
  return order;
}

static Row softmax(const Row& row) {
  double m = *std::max_element(row.begin(), row.end()), s = 0;
  Row e(row.size());
  for (size_t j = 0; j < row.size(); j++) { e[j] = std::exp(row[j] - m); s += e[j]; }
  for (double& x : e) x /= s;
  return e;
}

struct Example { int index, prev, next; Row probs; double loss; Row grad; };
struct Batch { double loss; Mat G; std::vector<Example> per; };

static Mat zeros(int V) { return Mat(V, Row(V, 0.0)); }

static Batch batchLossGrad(const Mat& W, const std::vector<std::pair<int, int>>& pairs, const std::vector<int>& idx, bool mean = true) {
  const int V = static_cast<int>(W.size());
  Batch b{0.0, zeros(V), {}};
  double total = 0;
  for (int k : idx) {
    auto [prev, nxt] = pairs[k];
    Row p = softmax(W[prev]);
    double loss = -std::log(p[nxt]);
    Row grad(V);
    for (int j = 0; j < V; j++) grad[j] = p[j] - (j == nxt ? 1.0 : 0.0);
    total += loss;
    for (int j = 0; j < V; j++) b.G[prev][j] += grad[j];
    b.per.push_back({k, prev, nxt, p, loss, grad});
  }
  double scale = mean ? 1.0 / static_cast<double>(idx.size()) : 1.0;
  b.loss = total * scale;
  for (auto& r : b.G) for (double& g : r) g *= scale;
  return b;
}

static std::vector<int> range(int n) { std::vector<int> v(n); for (int i = 0; i < n; i++) v[i] = i; return v; }

static double fullLoss(const Mat& W, const std::vector<std::pair<int, int>>& pairs) {
  return batchLossGrad(W, pairs, range(static_cast<int>(pairs.size()))).loss;
}

static Mat step(const Mat& W, const Mat& G, double lr) {
  Mat out = W;
  for (size_t i = 0; i < W.size(); i++) for (size_t j = 0; j < W[i].size(); j++) out[i][j] = W[i][j] - lr * G[i][j];
  return out;
}

// ---------- JSON output (numbers with 17 significant digits, like Python's repr) ----------
static std::string num(double x) { char b[40]; std::snprintf(b, sizeof b, "%.17g", x); return b; }
static std::string arr(const Row& r) { std::string s = "["; for (size_t i = 0; i < r.size(); i++) s += (i ? ", " : "") + num(r[i]); return s + "]"; }
static std::string arrI(const std::vector<int>& r) { std::string s = "["; for (size_t i = 0; i < r.size(); i++) s += (i ? ", " : "") + std::to_string(r[i]); return s + "]"; }
static std::string mat(const Mat& m) { std::string s = "["; for (size_t i = 0; i < m.size(); i++) s += (i ? ", " : "") + arr(m[i]); return s + "]"; }
static std::string str(const std::string& x) { return "\"" + x + "\""; }  // corpus words carry no quotes or backslashes

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: minibatch-cpp <data-dir>\n"); return 2; }
  std::string dir = argv[1];
  if (dir.back() != '/') dir += '/';

  std::vector<std::vector<std::string>> sentences;
  {
    std::ifstream f(dir + "corpus.txt");
    if (!f) { std::fprintf(stderr, "cannot read %scorpus.txt\n", dir.c_str()); return 1; }
    for (std::string line; std::getline(f, line);) {
      std::istringstream ss(line);
      std::vector<std::string> words;
      for (std::string w; ss >> w;) words.push_back(w);
      if (!words.empty()) sentences.push_back(words);
    }
  }
  std::map<std::string, std::vector<std::string>> kv;
  {
    std::ifstream f(dir + "config.txt");
    if (!f) { std::fprintf(stderr, "cannot read %sconfig.txt\n", dir.c_str()); return 1; }
    for (std::string line; std::getline(f, line);) {
      line = line.substr(0, line.find('#'));
      std::istringstream ss(line);
      std::string k;
      if (!(ss >> k)) continue;
      for (std::string v; ss >> v;) kv[k].push_back(v);
    }
  }
  Config cfg;
  cfg.lr = std::stod(kv.at("learning_rate")[0]);
  cfg.seed = static_cast<uint32_t>(std::stoul(kv.at("seed")[0]));
  cfg.walkB = std::stoi(kv.at("walkthrough_batch")[0]);
  cfg.walkSteps = std::stoi(kv.at("walkthrough_steps")[0]);
  for (auto& x : kv.at("curve_batches")) cfg.curveBatches.push_back(std::stoi(x));
  cfg.epochs = std::stoi(kv.at("curve_epochs")[0]);
  cfg.eps = std::stod(kv.at("grad_check_eps")[0]);

  std::vector<std::string> vocab;
  auto id = [&](const std::string& w) { return static_cast<int>(std::find(vocab.begin(), vocab.end(), w) - vocab.begin()); };
  for (auto& s : sentences) for (auto& w : s) if (id(w) == static_cast<int>(vocab.size())) vocab.push_back(w);
  std::vector<std::pair<int, int>> pairs;
  for (auto& s : sentences) for (size_t i = 0; i + 1 < s.size(); i++) pairs.push_back({id(s[i]), id(s[i + 1])});
  const int V = static_cast<int>(vocab.size()), N = static_cast<int>(pairs.size());

  std::string out = "{\n \"schema\": \"MINIBATCH_EXAMPLE_V1\",\n \"implementation\": \"C++17\",\n \"vocab\": [";
  for (int i = 0; i < V; i++) out += (i ? ", " : "") + str(vocab[i]);
  out += "],\n \"pairs\": [";
  for (int i = 0; i < N; i++) out += (i ? ", " : "") + std::string("[") + std::to_string(pairs[i].first) + ", " + std::to_string(pairs[i].second) + "]";
  out += "],\n";

  // walkthrough
  Lcg rng(cfg.seed);
  Mat W = zeros(V);
  std::vector<int> order = shuffled(N, rng);
  Mat firstW;
  std::vector<int> firstBatch;
  Mat firstG;
  out += " \"walkthrough\": {\"batchSize\": " + std::to_string(cfg.walkB) + ", \"learningRate\": " + num(cfg.lr) + ", \"epochOrder\": " + arrI(order) + ", \"steps\": [\n";
  for (int k = 0; k < cfg.walkSteps; k++) {
    std::vector<int> idx(order.begin() + k * cfg.walkB, order.begin() + (k + 1) * cfg.walkB);
    double before = fullLoss(W, pairs);
    Batch b = batchLossGrad(W, pairs, idx);
    Mat W2 = step(W, b.G, cfg.lr);
    if (k == 0) { firstW = W; firstBatch = idx; firstG = b.G; }
    out += std::string(k ? ",\n" : "") + "  {\"step\": " + std::to_string(k + 1) + ", \"batch\": " + arrI(idx) + ", \"examples\": [";
    for (size_t e = 0; e < b.per.size(); e++) {
      const Example& x = b.per[e];
      out += std::string(e ? ", " : "") + "{\"index\": " + std::to_string(x.index) + ", \"prev\": " + std::to_string(x.prev) + ", \"next\": " + std::to_string(x.next) +
             ", \"probs\": " + arr(x.probs) + ", \"loss\": " + num(x.loss) + ", \"grad\": " + arr(x.grad) + "}";
    }
    Mat pa;
    for (auto& r : W2) pa.push_back(softmax(r));
    out += "], \"meanLoss\": " + num(b.loss) + ", \"meanGrad\": " + mat(b.G) + ", \"Wafter\": " + mat(W2) + ", \"probsAfter\": " + mat(pa) +
           ", \"batchLossAfter\": " + num(batchLossGrad(W2, pairs, idx).loss) + ", \"fullLossBefore\": " + num(before) + ", \"fullLossAfter\": " + num(fullLoss(W2, pairs)) + "}";
    W = W2;
  }
  out += "\n ]},\n";

  // gradient check at the first step
  double worst = 0;
  for (int i = 0; i < V; i++)
    for (int j = 0; j < V; j++) {
      Mat Wp = firstW, Wm = firstW;
      Wp[i][j] += cfg.eps;
      Wm[i][j] -= cfg.eps;
      double numg = (batchLossGrad(Wp, pairs, firstBatch).loss - batchLossGrad(Wm, pairs, firstBatch).loss) / (2 * cfg.eps);
      worst = std::max(worst, std::fabs(numg - firstG[i][j]));
    }
  out += " \"gradCheck\": {\"eps\": " + num(cfg.eps) + ", \"maxAbsDiff\": " + num(worst) + "},\n";

  // mean vs sum, one full-batch step from W = 0
  out += " \"meanVsSum\": {\"batch\": " + std::to_string(N) + ", \"learningRate\": " + num(cfg.lr);
  for (bool mean : {true, false}) {
    Batch b = batchLossGrad(zeros(V), pairs, range(N), mean);
    Mat W2 = step(zeros(V), b.G, cfg.lr);
    double big = 0;
    for (auto& r : b.G) for (double g : r) big = std::max(big, std::fabs(cfg.lr * g));
    Mat pa;
    for (auto& r : W2) pa.push_back(softmax(r));
    out += std::string(", \"") + (mean ? "mean" : "sum") + "\": {\"loss\": " + num(b.loss) + ", \"maxAbsStep\": " + num(big) + ", \"fullLossAfter\": " + num(fullLoss(W2, pairs)) + ", \"probsAfter\": " + mat(pa) + "}";
  }
  out += "},\n";

  // step size against batch size: the first batch of each run (same seed), from W = 0, mean vs sum
  out += " \"stepScale\": [";
  for (size_t c = 0; c < cfg.curveBatches.size(); c++) {
    const int B = cfg.curveBatches[c];
    Lcg r1(cfg.seed);
    std::vector<int> ord = shuffled(N, r1), idx(ord.begin(), ord.begin() + B);
    double big[2] = {0, 0};
    for (int m = 0; m < 2; m++) {
      Batch b = batchLossGrad(zeros(V), pairs, idx, m == 0);
      for (auto& r : b.G) for (double g : r) big[m] = std::max(big[m], std::fabs(cfg.lr * g));
    }
    out += std::string(c ? ", " : "") + "{\"batch\": " + std::to_string(B) + ", \"firstBatch\": " + arrI(idx) + ", \"meanMaxStep\": " + num(big[0]) + ", \"sumMaxStep\": " + num(big[1]) + "}";
  }
  out += "],\n";

  // curves
  out += " \"curves\": {";
  for (size_t c = 0; c < cfg.curveBatches.size(); c++) {
    const int B = cfg.curveBatches[c];
    Lcg r2(cfg.seed);
    Mat Wc = zeros(V);
    Row full{fullLoss(Wc, pairs)}, bl;
    std::vector<int> seen{0};
    int updates = 0;
    for (int e = 0; e < cfg.epochs; e++) {
      std::vector<int> ord = shuffled(N, r2);
      for (int s = 0; s < N; s += B) {
        std::vector<int> idx(ord.begin() + s, ord.begin() + std::min(N, s + B));
        Batch b = batchLossGrad(Wc, pairs, idx);
        Wc = step(Wc, b.G, cfg.lr);
        updates++;
        bl.push_back(b.loss);
        seen.push_back(seen.back() + static_cast<int>(idx.size()));
        full.push_back(fullLoss(Wc, pairs));
      }
    }
    Mat pr;
    for (auto& r : Wc) pr.push_back(softmax(r));
    out += std::string(c ? ", " : "") + "\"" + std::to_string(B) + "\": {\"batch\": " + std::to_string(B) + ", \"updates\": " + std::to_string(updates) +
           ", \"examplesSeen\": " + arrI(seen) + ", \"fullLoss\": " + arr(full) + ", \"batchLoss\": " + arr(bl) + ", \"W\": " + mat(Wc) + ", \"probs\": " + mat(pr) + "}";
  }
  out += "},\n";

  // best possible loss: each row equals the observed next-word frequencies
  double best = 0;
  for (int prev = 0; prev < V; prev++) {
    std::vector<int> nx;
    for (auto& pr : pairs) if (pr.first == prev) nx.push_back(pr.second);
    std::vector<int> seenN;
    for (int n : nx) {
      if (std::find(seenN.begin(), seenN.end(), n) != seenN.end()) continue;
      seenN.push_back(n);
      double cnt = static_cast<double>(std::count(nx.begin(), nx.end(), n));
      best -= cnt * std::log(cnt / static_cast<double>(nx.size()));
    }
  }
  best /= N;
  out += " \"bestPossibleLoss\": " + num(best) + "\n}\n";
  std::fputs(out.c_str(), stdout);
  return 0;
}
