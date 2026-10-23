// 플로이드–워셜: 모든 출발점과 도착점 사이의 최단 거리 (C++17).
//
// 빌드: c++ -std=c++17 -O2 -Wall -Wextra -pedantic floyd_warshall.cpp -o floyd_warshall
// 실행: ./floyd_warshall graph.txt
//
// 입력 형식(graph.txt): 첫 줄 "정점수 간선수", 다음 줄마다 "출발 도착 거리". '#' 뒤는 주석.
// floyd_warshall.py 와 같은 입력에 글자 하나까지 같은 글을 출력한다.
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

using Dist = std::optional<long long>;  // 값이 없으면 무한대(아직 길을 모름)
using Table = std::vector<std::vector<Dist>>;

struct Edge { int u, v; long long w; };
struct Change { int i, j; Dist old; long long now, ik, kj; };

// i -> k -> j 의 거리. 둘 중 하나라도 무한대면 무한대 (무한대끼리 더해 넘치는 일이 없다).
static Dist via(const Table& d, int i, int k, int j) {
  if (!d[i][k] || !d[k][j]) return std::nullopt;
  return *d[i][k] + *d[k][j];
}

// a가 b보다 짧은가 (무한대는 어떤 수보다도 길다).
static bool shorter(const Dist& a, const Dist& b) { return a && (!b || *a < *b); }

static std::string cell(const Dist& x) { return x ? std::to_string(*x) : "∞"; }

// UTF-8 글자 수(∞ 한 글자 = 1)로 오른쪽 맞춤.
static std::size_t width(const std::string& s) {
  std::size_t n = 0;
  for (unsigned char c : s) n += (c & 0xC0) != 0x80;
  return n;
}
static std::string rjust(const std::string& s, std::size_t w) { return width(s) >= w ? s : std::string(w - width(s), ' ') + s; }
static std::string ljust(const std::string& s, std::size_t w) { return width(s) >= w ? s : s + std::string(w - width(s), ' '); }

int main(int argc, char** argv) {
  if (argc < 2) { std::cerr << "사용법: floyd_warshall graph.txt\n"; return 2; }
  std::ifstream in(argv[1]);
  if (!in) { std::cerr << "파일을 열 수 없습니다: " << argv[1] << "\n"; return 1; }

  // ---- 입력 ----
  std::vector<std::vector<std::string>> rows;
  for (std::string line; std::getline(in, line);) {
    line = line.substr(0, line.find('#'));
    std::istringstream ss(line);
    std::vector<std::string> words;
    for (std::string w; ss >> w;) words.push_back(w);
    if (!words.empty()) rows.push_back(words);
  }
  const int n0 = std::stoi(rows[0][0]), m = std::stoi(rows[0][1]);
  std::vector<std::string> names;
  auto id = [&](const std::string& x) {
    for (int i = 0; i < (int)names.size(); ++i) if (names[i] == x) return i;
    names.push_back(x);
    return (int)names.size() - 1;
  };
  std::vector<Edge> edges;
  for (int e = 1; e <= m; ++e) {
    int u = id(rows[e][0]), v = id(rows[e][1]);
    edges.push_back({u, v, std::stoll(rows[e][2])});
  }
  const int n = (int)names.size();
  if (n != n0) { std::cerr << "정점 수가 맞지 않습니다\n"; return 1; }

  // ---- 초기 표: 자기 자신은 0, 바로 가는 도로는 그 거리, 나머지는 무한대 ----
  Table dist(n, std::vector<Dist>(n));
  std::vector<std::vector<int>> nxt(n, std::vector<int>(n, -1));  // i에서 j로 갈 때의 첫걸음
  for (int i = 0; i < n; ++i) { dist[i][i] = 0; nxt[i][i] = i; }
  for (const Edge& e : edges)
    if (shorter(e.w, dist[e.u][e.v])) { dist[e.u][e.v] = e.w; nxt[e.u][e.v] = e.v; }
  const Table initial = dist;

  // ---- 플로이드–워셜: 바깥 반복문이 경유지 k ----
  std::vector<std::vector<Change>> rounds(n);
  for (int k = 0; k < n; ++k)            // 경유지 k를 하나씩 허락한다
    for (int i = 0; i < n; ++i)          // 출발
      for (int j = 0; j < n; ++j) {      // 도착
        Dist d = via(dist, i, k, j);
        if (shorter(d, dist[i][j])) {
          rounds[k].push_back({i, j, dist[i][j], *d, *dist[i][k], *dist[k][j]});
          dist[i][j] = d;
          nxt[i][j] = nxt[i][k];         // 첫걸음은 k로 가는 길의 첫걸음
        }
      }

  // ---- 흔한 실수: k 반복문을 맨 안쪽에 둔다 ----
  Table wrong = initial;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      for (int k = 0; k < n; ++k) {
        Dist d = via(wrong, i, k, j);
        if (shorter(d, wrong[i][j])) wrong[i][j] = d;
      }

  // ---- 출력 (floyd_warshall.py text_report와 같은 형식) ----
  auto table = [&](const Table& t) {
    std::string head = "    ";
    for (const auto& s : names) head += rjust(s, 5);
    std::cout << head << "\n";
    for (int i = 0; i < n; ++i) {
      std::string row = "  " + ljust(names[i], 2);
      for (int j = 0; j < n; ++j) row += rjust(cell(t[i][j]), 5);
      std::cout << row << "\n";
    }
  };
  std::cout << "그래프: 정점 " << n << "개, 간선 " << edges.size() << "개\n";
  std::cout << "초기 표 (행 = 출발, 열 = 도착)\n";
  table(initial);
  for (int k = 0; k < n; ++k) {
    std::cout << "경유지 " << names[k] << ": 바뀐 칸 " << rounds[k].size() << "개\n";
    for (const Change& c : rounds[k]) {
      const std::string &I = names[c.i], &J = names[c.j], &K = names[k];
      std::cout << "  " << I << "→" << J << ": " << cell(c.old) << " → " << c.now << "  (" << I << "→" << K << " " << c.ik
                << " + " << K << "→" << J << " " << c.kj << ")\n";
    }
  }
  std::cout << "최종 표\n";
  table(dist);

  std::vector<int> neg;
  for (int i = 0; i < n; ++i) if (dist[i][i] && *dist[i][i] < 0) neg.push_back(i);  // 대각선이 음수 = 음수 사이클
  if (!neg.empty()) {
    std::cout << "음수 사이클: 있음 (대각선이 0보다 작은 정점: ";
    for (std::size_t x = 0; x < neg.size(); ++x) std::cout << (x ? ", " : "") << names[neg[x]] << "=" << *dist[neg[x]][neg[x]];
    std::cout << ")\n경로: 음수 사이클이 있어 최단 경로가 정의되지 않음\n";
    std::cout << "실수(k 반복문을 맨 안쪽에 둠) 비교: 음수 사이클이 있어 생략\n";
    return 0;
  }
  std::cout << "음수 사이클: 없음\n모든 경로\n";
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      if (i == j) continue;
      std::cout << "  " << names[i] << "→" << names[j] << ": ";
      if (nxt[i][j] < 0) { std::cout << "길 없음\n"; continue; }
      std::string p = names[i];
      for (int x = i; x != j;) { x = nxt[x][j]; p += " → " + names[x]; }
      std::cout << p << " (거리 " << *dist[i][j] << ")\n";
    }
  std::vector<std::pair<int, int>> diff;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (i != j && wrong[i][j] != dist[i][j]) diff.push_back({i, j});
  if (diff.empty()) {
    std::cout << "실수(k 반복문을 맨 안쪽에 둠)와 다른 칸: 없음\n";
  } else {
    std::cout << "실수(k 반복문을 맨 안쪽에 둠)와 다른 칸\n";
    for (auto [i, j] : diff)
      std::cout << "  " << names[i] << "→" << names[j] << ": 정답 " << cell(dist[i][j]) << ", 실수한 결과 " << cell(wrong[i][j]) << "\n";
  }
  return 0;
}
