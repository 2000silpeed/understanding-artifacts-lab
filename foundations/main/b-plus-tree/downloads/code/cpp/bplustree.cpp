// B+ 트리: 리프 연결과 범위 탐색 (강의 16, data_structures) — C++17 판.
// ../python/bplustree.py 와 같은 알고리즘, 같은 이름 붙이기, 같은 출력 줄을 낸다(tests/test_lesson.py가 대조).
//
// build:  c++ -std=c++17 -O2 -Wall -Wextra -pedantic -o <out>/bplustree code/cpp/bplustree.cpp
// run:    <out>/bplustree fixtures/input.txt
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct Node {
  std::vector<int> keys;
  std::vector<Node*> children;  // 비어 있으면 리프
  Node* next = nullptr;         // 리프만 쓴다: 오른쪽 이웃 리프
  bool leaf = true;
  std::string name;
};

class BPlusTree {
 public:
  explicit BPlusTree(int maxKeys) : maxKeys_(maxKeys) {
    if (maxKeys < 3) throw std::invalid_argument("max_keys must be at least 3");
    root_ = make(true);
  }

  bool insert(int key) {
    bool dup = false;
    auto split = insertAt(root_, key, dup);
    if (dup) return false;
    if (split.second) {
      Node* r = make(false);
      r->keys = {split.first};
      r->children = {root_, split.second};
      root_ = r;
    }
    return true;
  }

  // 뿌리부터 층별 노드. 이름: 뿌리 R, 내부 I1.., 리프 L1.. (왼쪽부터)
  std::vector<std::vector<Node*>> levels() {
    std::vector<std::vector<Node*>> out;
    std::vector<Node*> level = {root_};
    while (!level.empty()) {
      out.push_back(level);
      std::vector<Node*> nextLevel;
      for (Node* n : level)
        if (!n->leaf) nextLevel.insert(nextLevel.end(), n->children.begin(), n->children.end());
      level = nextLevel;
    }
    int inner = 0;
    for (size_t d = 0; d < out.size(); ++d)
      for (size_t j = 0; j < out[d].size(); ++j) {
        Node* n = out[d][j];
        if (d == 0) n->name = "R";
        else if (n->leaf) n->name = "L" + std::to_string(j + 1);
        else n->name = "I" + std::to_string(++inner);
      }
    return out;
  }

  int height() const {
    int h = 1;
    for (Node* n = root_; !n->leaf; n = n->children[0]) ++h;
    return h;
  }

  std::vector<Node*> leafChain() const {
    Node* n = root_;
    while (!n->leaf) n = n->children[0];
    std::vector<Node*> chain;
    for (; n; n = n->next) chain.push_back(n);
    return chain;
  }

  std::pair<bool, std::vector<std::string>> search(int key) const {
    std::vector<std::string> path;
    Node* n = root_;
    while (true) {
      path.push_back(n->name);
      if (n->leaf) return {std::find(n->keys.begin(), n->keys.end(), key) != n->keys.end(), path};
      n = n->children[upper(n->keys, key)];
    }
  }

  struct RangeResult {
    std::vector<int> found;
    std::vector<std::string> descent, walked;
  };

  RangeResult rangeSearch(int lo, int hi) const {
    RangeResult r;
    Node* node = root_;
    while (!node->leaf) {  // 1) 한 번만 내려간다
      r.descent.push_back(node->name);
      node = node->children[upper(node->keys, lo)];
    }
    for (; node; node = node->next) {  // 2) 리프 링크를 따라 걷는다
      r.walked.push_back(node->name);
      for (int k : node->keys) {
        if (k > hi) return r;  // 3) hi를 넘으면 멈춘다
        if (k >= lo) r.found.push_back(k);
      }
    }
    return r;
  }

  // 비교용: next 링크를 쓰지 않는다. 리프를 다 읽으면 부모로 올라가 다음 자식으로 내려간다.
  std::pair<std::vector<int>, std::vector<std::string>> rangeSearchWithoutLinks(int lo, int hi) const {
    std::vector<std::string> route;
    std::vector<std::pair<Node*, size_t>> stack;
    Node* node = root_;
    while (!node->leaf) {
      route.push_back(node->name);
      size_t i = upper(node->keys, lo);
      stack.push_back({node, i});
      node = node->children[i];
    }
    std::vector<int> found;
    while (true) {
      route.push_back(node->name);
      for (int k : node->keys) {
        if (k > hi) return {found, route};
        if (k >= lo) found.push_back(k);
      }
      while (!stack.empty() && stack.back().second == stack.back().first->children.size() - 1) {
        route.push_back(stack.back().first->name);  // 마지막 자식까지 읽은 부모: 지나서 한 층 더 올라간다
        stack.pop_back();
      }
      if (stack.empty()) return {found, route};
      auto& parent = stack.back();
      route.push_back(parent.first->name);  // 부모로 올라가 다음 자식을 고른다
      parent.second += 1;
      node = parent.first->children[parent.second];
      while (!node->leaf) {
        route.push_back(node->name);
        stack.push_back({node, 0});
        node = node->children[0];
      }
    }
  }

 private:
  static size_t upper(const std::vector<int>& keys, int key) {
    return static_cast<size_t>(std::upper_bound(keys.begin(), keys.end(), key) - keys.begin());
  }

  Node* make(bool leaf) {
    pool_.push_back(std::make_unique<Node>());
    pool_.back()->leaf = leaf;
    return pool_.back().get();
  }

  // 반환: (올릴 구분 키, 새 오른쪽 노드). 나뉘지 않았으면 second == nullptr.
  std::pair<int, Node*> insertAt(Node* node, int key, bool& dup) {
    if (node->leaf) {
      auto it = std::upper_bound(node->keys.begin(), node->keys.end(), key);
      if (it != node->keys.begin() && *(it - 1) == key) { dup = true; return {0, nullptr}; }
      node->keys.insert(it, key);
      if (static_cast<int>(node->keys.size()) <= maxKeys_) return {0, nullptr};
      size_t mid = node->keys.size() / 2;
      Node* right = make(true);
      right->keys.assign(node->keys.begin() + mid, node->keys.end());
      node->keys.resize(mid);
      right->next = node->next;
      node->next = right;
      return {right->keys[0], right};  // 리프 분할: 오른쪽 첫 키를 복사해서 올린다
    }
    size_t i = upper(node->keys, key);
    auto split = insertAt(node->children[i], key, dup);
    if (!split.second) return {0, nullptr};
    node->keys.insert(node->keys.begin() + i, split.first);
    node->children.insert(node->children.begin() + i + 1, split.second);
    if (static_cast<int>(node->keys.size()) <= maxKeys_) return {0, nullptr};
    size_t mid = node->keys.size() / 2;
    Node* right = make(false);
    int up = node->keys[mid];  // 내부 분할: 가운데 키는 옮겨서 올린다(복사하지 않는다)
    right->keys.assign(node->keys.begin() + mid + 1, node->keys.end());
    right->children.assign(node->children.begin() + mid + 1, node->children.end());
    node->keys.resize(mid);
    node->children.resize(mid + 1);
    return {up, right};
  }

  int maxKeys_;
  Node* root_;
  std::vector<std::unique_ptr<Node>> pool_;
};

static std::string join(const std::vector<std::string>& v) {
  std::string s;
  for (size_t i = 0; i < v.size(); ++i) s += (i ? " " : "") + v[i];
  return s;
}

static std::string joinInts(const std::vector<int>& v, const char* sep) {
  std::string s;
  for (size_t i = 0; i < v.size(); ++i) s += (i ? sep : "") + std::to_string(v[i]);
  return s;
}

int main(int argc, char** argv) {
  if (argc < 2) { std::cerr << "usage: bplustree fixtures/input.txt\n"; return 2; }
  std::ifstream in(argv[1]);
  if (!in) { std::cerr << "cannot open " << argv[1] << "\n"; return 2; }
  std::map<std::string, std::vector<int>> spec;
  std::string line;
  while (std::getline(in, line)) {
    line = line.substr(0, line.find('#'));
    std::istringstream ss(line);
    std::string name;
    if (!(ss >> name)) continue;
    int v;
    while (ss >> v) spec[name].push_back(v);
  }
  const int mk = spec.at("max_keys").at(0);
  const auto& keys = spec.at("keys");
  BPlusTree t(mk);
  for (int k : keys) t.insert(k);
  auto levels = t.levels();
  std::cout << "tree max_keys=" << mk << " n=" << keys.size() << " height=" << t.height() << "\n";
  for (size_t d = 0; d < levels.size(); ++d) {
    std::cout << "level " << d << ":";
    for (Node* n : levels[d]) std::cout << " " << n->name << "[" << joinInts(n->keys, ",") << "]";
    std::cout << "\n";
  }
  std::vector<std::string> chain;
  for (Node* n : t.leafChain()) chain.push_back(n->name);
  std::cout << "chain " << join(chain) << "\n";

  const int sk = spec.at("search").at(0);
  auto sr = t.search(sk);
  std::cout << "search " << sk << ": found=" << (sr.first ? 1 : 0) << " path=" << join(sr.second) << "\n";

  const int lo = spec.at("range").at(0), hi = spec.at("range").at(1);
  auto r = t.rangeSearch(lo, hi);
  auto nr = t.rangeSearchWithoutLinks(lo, hi);
  if (nr.first != r.found) { std::cerr << "mismatch between link and no-link results\n"; return 1; }
  std::cout << "range " << lo << " " << hi << ": found=" << joinInts(r.found, " ") << "\n";
  std::cout << "range.descent " << join(r.descent) << "\n";
  std::cout << "range.walked " << join(r.walked) << "\n";
  std::cout << "range.moves " << r.descent.size() + r.walked.size() - 1 << "\n";
  std::cout << "nolink.route " << join(nr.second) << "\n";
  std::cout << "nolink.moves " << nr.second.size() - 1 << "\n";

  const auto& sc = spec.at("scale");
  const int n = sc.at(0), step = sc.at(1), smk = sc.at(2), slo = sc.at(3), shi = sc.at(4);
  std::vector<int> bigKeys;
  bigKeys.reserve(n);
  for (long long i = 0; i < n; ++i) bigKeys.push_back(static_cast<int>((i * step) % n));
  BPlusTree big(smk);
  for (int k : bigKeys) big.insert(k);
  big.levels();
  auto br = big.rangeSearch(slo, shi);
  auto bnr = big.rangeSearchWithoutLinks(slo, shi);
  if (bnr.first != br.found || static_cast<int>(br.found.size()) != shi - slo + 1) { std::cerr << "scale mismatch\n"; return 1; }
  const size_t leaves = big.leafChain().size();
  std::cout << "scale n=" << n << " max_keys=" << smk << " height=" << big.height() << " leaves=" << leaves << "\n";
  std::cout << "scale range " << slo << " " << shi << ": found=" << br.found.size() << " leaves_read=" << br.walked.size()
            << " moves_links=" << br.descent.size() + br.walked.size() - 1 << " moves_nolinks=" << bnr.second.size() - 1
            << " fullscan_leaves=" << leaves << "\n";
  return 0;
}
