// 크루스칼 알고리즘: 사이클을 피하며 최소 신장 트리 만들기 (C++17, 표준 라이브러리만).
//
//   c++ -std=c++17 -O2 -o kruskal kruskal.cpp
//   ./kruskal graph.txt            # 비용 순서대로 간선을 보며 고르기/버리기, 최소 신장 트리와 비용 합
//   ./kruskal graph.txt --naive    # 흔한 실수: "두 끝을 이미 방문했으면 버린다" 규칙
//
// 입력: 첫 줄 정점 이름, 그다음 줄마다 `u v 비용`. `#` 뒤는 주석.
// 출력은 kruskal.py(Python)와 글자 하나까지 같다(run_examples.py가 확인).
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

struct Edge {
    std::string u, v;
    int w;
};

struct UnionFind {
    std::map<std::string, std::string> parent;
    std::map<std::string, int> size;

    explicit UnionFind(const std::vector<std::string>& names) {
        for (const auto& v : names) { parent[v] = v; size[v] = 1; }   // 처음엔 모두 자기 자신이 대표
    }
    std::string find(std::string v) {
        std::string root = v;
        while (parent[root] != root) root = parent[root];            // 대표까지 따라 올라간다
        while (v != root) {                                           // 경로 압축
            std::string nxt = parent[v];
            parent[v] = root;
            v = nxt;
        }
        return root;
    }
    bool unite(const std::string& a, const std::string& b) {
        std::string ra = find(a), rb = find(b);
        if (ra == rb) return false;                                   // 같은 덩어리: 이으면 사이클
        if (size[ra] < size[rb]) std::swap(ra, rb);
        parent[rb] = ra;                                              // 작은 덩어리를 큰 덩어리 아래에
        size[ra] += size[rb];
        return true;
    }
};

static bool readGraph(const char* path, std::vector<std::string>& names, std::vector<Edge>& edges) {
    std::ifstream in(path);
    if (!in) return false;
    std::string line;
    bool first = true;
    while (std::getline(in, line)) {
        line = line.substr(0, line.find('#'));
        std::istringstream ss(line);
        std::vector<std::string> tok;
        for (std::string t; ss >> t;) tok.push_back(t);
        if (tok.empty()) continue;
        if (first) { names = tok; first = false; continue; }
        if (tok.size() != 3) return false;
        edges.push_back({tok[0], tok[1], std::stoi(tok[2])});
    }
    for (const auto& e : edges)
        if (std::find(names.begin(), names.end(), e.u) == names.end() ||
            std::find(names.begin(), names.end(), e.v) == names.end()) return false;
    return !first;
}

static std::vector<Edge> byCost(std::vector<Edge> edges) {
    std::stable_sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) { return a.w < b.w; });
    return edges;                                                     // 비용 순서(같으면 입력 순서)
}

static int countComponents(const std::vector<std::string>& names, const std::vector<Edge>& tree) {
    UnionFind uf(names);
    for (const auto& e : tree) uf.unite(e.u, e.v);
    std::set<std::string> roots;
    for (const auto& v : names) roots.insert(uf.find(v));
    return static_cast<int>(roots.size());
}

static void report(const std::vector<std::string>& names, const std::vector<Edge>& edges) {
    std::vector<Edge> sorted = byCost(edges);
    std::cout << "sorted:";
    for (const auto& e : sorted) std::cout << ' ' << e.u << '-' << e.v << ':' << e.w;
    std::cout << '\n';
    UnionFind uf(names);
    std::vector<Edge> tree;
    long long total = 0;
    int checked = 0;
    for (const auto& e : sorted) {
        if (tree.size() == names.size() - 1) break;                  // 간선 n-1개면 끝
        ++checked;
        std::string ru = uf.find(e.u), rv = uf.find(e.v);
        bool take = uf.unite(e.u, e.v);
        if (take) { tree.push_back(e); total += e.w; }
        std::cout << "step " << checked << ": " << e.u << '-' << e.v << " w=" << e.w
                  << " find(" << e.u << ")=" << ru << " find(" << e.v << ")=" << rv;
        if (take) std::cout << " take total=" << total << '\n';
        else std::cout << " skip cycle\n";
    }
    std::cout << "mst:";
    for (const auto& e : tree) std::cout << ' ' << e.u << '-' << e.v;
    std::cout << "\ntotal: " << total << '\n';
    std::cout << "edges: " << tree.size() << '/' << names.size() - 1 << " checked: " << checked << '/' << edges.size() << '\n';
    int groups = countComponents(names, tree);
    if (groups == 1) std::cout << "connected: yes\n";
    else std::cout << "connected: no (components " << groups << ")\n";
}

static void reportNaive(const std::vector<std::string>& names, const std::vector<Edge>& edges) {
    std::cout << "naive rule: skip an edge when both ends are already visited\n";
    std::set<std::string> seen;
    std::vector<Edge> tree;
    int k = 0;
    long long total = 0;
    for (const auto& e : byCost(edges)) {
        bool take = !(seen.count(e.u) && seen.count(e.v));
        if (take) { tree.push_back(e); seen.insert(e.u); seen.insert(e.v); total += e.w; }
        std::cout << "step " << ++k << ": " << e.u << '-' << e.v << " w=" << e.w << ' '
                  << (take ? "take" : "skip both-visited") << '\n';
    }
    std::cout << "edges: " << tree.size() << '/' << names.size() - 1 << " total: " << total
              << " components: " << countComponents(names, tree) << '\n';
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: kruskal graph.txt [--naive]\n";
        return 2;
    }
    std::vector<std::string> names;
    std::vector<Edge> edges;
    if (!readGraph(argv[1], names, edges)) {
        std::cerr << "cannot read graph " << argv[1] << '\n';
        return 1;
    }
    if (argc > 2 && std::string(argv[2]) == "--naive") reportNaive(names, edges);
    else report(names, edges);
    return 0;
}
