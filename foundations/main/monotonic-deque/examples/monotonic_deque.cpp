// Sliding-window maximum with a monotonic deque (단조 덱), plus the naive scan it replaces. C++17.
//
//   c++ -std=c++17 -O2 -Wall -Wextra -pedantic -o monotonic_deque monotonic_deque.cpp
//   ./monotonic_deque input.txt          # prints exactly what monotonic_deque.py prints for the same file
//
// Input: "k <window>" and either "a <values...>" or "gen latency <n> <seed>" ('#' starts a comment).
// The deque holds indices whose values strictly decrease from front to back. For each new index i:
//   1. drop the front index if it has left the window (index <= i - k)
//   2. drop back indices whose value is <= a[i]
//   3. push i
//   4. once i >= k - 1, a[front] is the window maximum
#include <algorithm>
#include <cstdint>
#include <deque>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using Vec = std::vector<long long>;

struct Stats {
  long long push = 0, popFront = 0, popBack = 0, compare = 0;
  std::size_t maxLen = 0;
};

struct Step {
  std::size_t i;
  long long v;
  std::vector<std::size_t> frontOut, backOut, dq;
  bool full;
  long long max;
};

// Same 32-bit LCG as lcg_latency() in monotonic_deque.py.
static Vec lcgLatency(std::size_t n, std::uint32_t seed) {
  Vec out;
  std::uint32_t x = seed;
  for (std::size_t j = 0; j < n; ++j) {
    x = 1664525u * x + 1013904223u;
    std::uint32_t r1 = x;
    x = 1664525u * x + 1013904223u;
    std::uint32_t r2 = x;
    long long v = 40 + (r1 >> 24) % 30;
    if ((r2 >> 16) % 200 == 0) v += 120 + (r2 >> 4) % 280;
    out.push_back(v);
  }
  return out;
}

static bool readInput(const char* path, Vec& a, std::size_t& k, std::string& source) {
  std::ifstream in(path);
  if (!in) return false;
  std::string raw;
  bool haveK = false, haveA = false;
  source = "values";
  while (std::getline(in, raw)) {
    std::istringstream ss(raw.substr(0, raw.find('#')));
    std::string word;
    if (!(ss >> word)) continue;
    if (word == "k") {
      ss >> k;
      haveK = true;
    } else if (word == "a") {
      long long v;
      while (ss >> v) a.push_back(v);
      haveA = true;
    } else if (word == "gen") {
      std::string kind;
      std::size_t n;
      std::uint32_t seed;
      ss >> kind >> n >> seed;
      if (kind != "latency") return false;
      a = lcgLatency(n, seed);
      source = "gen latency " + std::to_string(n) + " " + std::to_string(seed);
      haveA = true;
    } else {
      return false;
    }
  }
  return haveK && haveA && k >= 1 && k <= a.size();
}

// The teaching version (the lesson shows it): no counters.
static Vec windowMax(const Vec& a, std::size_t k) {
  std::deque<std::size_t> dq;
  Vec ans;
  for (std::size_t i = 0; i < a.size(); ++i) {
    if (!dq.empty() && dq.front() + k <= i) dq.pop_front();
    while (!dq.empty() && a[dq.back()] <= a[i]) dq.pop_back();
    dq.push_back(i);
    if (i + 1 >= k) ans.push_back(a[dq.front()]);
  }
  return ans;
}

// windowMax() with counters and an optional record of every step (what the program prints).
static Vec slidingMax(const Vec& a, std::size_t k, Stats& st, std::vector<Step>* steps) {
  std::deque<std::size_t> dq;
  Vec ans;
  for (std::size_t i = 0; i < a.size(); ++i) {
    Step s{i, a[i], {}, {}, {}, false, 0};
    if (!dq.empty() && dq.front() + k <= i) {  // 1. the front index has left the window
      s.frontOut.push_back(dq.front());
      dq.pop_front();
      ++st.popFront;
    }
    while (!dq.empty()) {  // 2. drop smaller-or-equal values at the back
      ++st.compare;
      if (a[dq.back()] > a[i]) break;
      s.backOut.insert(s.backOut.begin(), dq.back());
      dq.pop_back();
      ++st.popBack;
    }
    dq.push_back(i);  // 3. push the new index
    ++st.push;
    st.maxLen = std::max(st.maxLen, dq.size());
    if (i + 1 >= k) {  // 4. the front is the maximum of a[i-k+1 .. i]
      ans.push_back(a[dq.front()]);
      s.full = true;
      s.max = a[dq.front()];
    }
    if (steps) {
      s.dq.assign(dq.begin(), dq.end());
      steps->push_back(s);
    }
  }
  return ans;
}

static Vec naiveMax(const Vec& a, std::size_t k, long long& compare) {
  Vec ans;
  for (std::size_t s = 0; s + k <= a.size(); ++s) {
    long long best = a[s];
    for (std::size_t j = s + 1; j < s + k; ++j) {
      ++compare;
      if (a[j] > best) best = a[j];
    }
    ans.push_back(best);
  }
  return ans;
}

static std::string pairs(const std::vector<std::size_t>& idx, const Vec& a) {
  if (idx.empty()) return "-";
  std::string out = "[";
  for (std::size_t j = 0; j < idx.size(); ++j) {
    if (j) out += ' ';
    out += std::to_string(idx[j]) + ":" + std::to_string(a[idx[j]]);
  }
  return out + "]";
}

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: monotonic_deque <input.txt>\n";
    return 2;
  }
  Vec a;
  std::size_t k = 0;
  std::string source;
  if (!readInput(argv[1], a, k, source)) {
    std::cerr << argv[1] << ": need k and values with 1 <= k <= n\n";
    return 1;
  }
  const bool small = a.size() <= 30;
  Stats st;
  std::vector<Step> steps;
  Vec ans = slidingMax(a, k, st, small ? &steps : nullptr);
  long long ncmp = 0;
  Vec nans = naiveMax(a, k, ncmp);

  std::cout << "n " << a.size() << " k " << k;
  if (source != "values") std::cout << " (" << source << ")";
  std::cout << "\n";
  if (small) {
    for (const Step& s : steps) {
      std::cout << "step " << s.i << " in " << s.v << " | front-out " << pairs(s.frontOut, a) << " | back-out " << pairs(s.backOut, a)
                << " | deque " << pairs(s.dq, a) << " | " << (s.full ? "max " + std::to_string(s.max) : std::string("filling")) << "\n";
    }
    std::cout << "answers";
    for (long long v : ans) std::cout << ' ' << v;
    std::cout << "\n";
  } else {
    std::cout << "answers " << ans.size() << " values, first 5:";
    for (std::size_t j = 0; j < 5 && j < ans.size(); ++j) std::cout << ' ' << ans[j];
    std::cout << ", largest " << *std::max_element(ans.begin(), ans.end()) << "\n";
  }
  std::cout << "deque push " << st.push << " pop-front " << st.popFront << " pop-back " << st.popBack << " compare " << st.compare
            << " max-length " << st.maxLen << "\n";
  std::cout << "naive compare " << ncmp << "\n";
  std::cout << "check naive == deque: " << (nans == ans && ans == windowMax(a, k) ? "yes" : "NO") << "\n";
  return 0;
}
