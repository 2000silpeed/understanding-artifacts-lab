// Prim's minimum spanning tree — C++17 twin of prim.py (standard library only).
// Prints the same text as prim.py, byte for byte, for every input and flag.
//
//   c++ -std=c++17 -O2 -Wall -Wextra -o prim prim.cpp
//   ./prim garden.txt [--start NAME] [--naive | --dense]
#include <algorithm>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

using namespace std;

struct Edge { int u, v, w; };
struct Graph { vector<string> names; vector<Edge> edges; };
struct Result {
    int start = 0, n = 0, reached = 0, stuck = -1;
    vector<Edge> taken;
    vector<pair<char, Edge>> log;  // 'T' take, 'S' skip (lazy only), in order
    vector<int> treeAfter;         // tree size after each take
    long long total() const { long long s = 0; for (auto& e : taken) s += e.w; return s; }
    bool connected() const { return reached == n; }
};

Graph readGraph(const string& path) {
    ifstream in(path);
    if (!in) throw runtime_error("cannot open " + path);
    vector<vector<string>> rows;
    string line;
    while (getline(in, line)) {
        auto hash = line.find('#');
        if (hash != string::npos) line = line.substr(0, hash);
        istringstream ss(line);
        vector<string> row; string tok;
        while (ss >> tok) row.push_back(tok);
        if (!row.empty()) rows.push_back(row);
    }
    Graph g;
    g.names = rows.at(0);
    map<string, int> index;
    for (size_t i = 0; i < g.names.size(); ++i)
        if (!index.emplace(g.names[i], (int)i).second) throw runtime_error("duplicate vertex name");
    for (size_t r = 1; r < rows.size(); ++r) {
        if (rows[r].size() != 3) throw runtime_error("bad edge line");
        int u = index.at(rows[r][0]), v = index.at(rows[r][1]), w = stoi(rows[r][2]);
        if (u == v) throw runtime_error("self loop");
        g.edges.push_back({u, v, w});
    }
    return g;
}

vector<vector<pair<int, int>>> adjacency(const Graph& g) {
    vector<vector<pair<int, int>>> adj(g.names.size());
    for (auto& e : g.edges) {               // neighbours keep input order (both languages)
        adj[e.u].push_back({e.v, e.w});
        adj[e.v].push_back({e.u, e.w});
    }
    return adj;
}

// Lazy Prim: candidates (cost, push order, from, to) in a min-heap; a popped edge whose far end is
// already in the tree is dropped.
Result prim(const Graph& g, int start) {
    Result r; r.start = start; r.n = (int)g.names.size();
    auto adj = adjacency(g);
    vector<bool> inTree(r.n, false);
    using Cand = tuple<int, long long, int, int>;
    priority_queue<Cand, vector<Cand>, greater<Cand>> heap;
    long long seq = 0;
    auto add = [&](int x) {
        inTree[x] = true; ++r.reached;
        for (auto [y, w] : adj[x])
            if (!inTree[y]) heap.push({w, seq++, x, y});   // an edge back into the tree is never a candidate
    };
    add(start);
    while (!heap.empty() && (int)r.taken.size() < r.n - 1) {
        auto [w, s, x, y] = heap.top(); heap.pop();
        (void)s;
        if (inTree[y]) { r.log.push_back({'S', {x, y, w}}); continue; }   // would close a cycle
        r.taken.push_back({x, y, w});
        add(y);
        r.log.push_back({'T', {x, y, w}});
        r.treeAfter.push_back(r.reached);
    }
    return r;
}

// Common mistake: choose only among edges of the vertex added last.
Result primNaive(const Graph& g, int start) {
    Result r; r.start = start; r.n = (int)g.names.size();
    auto adj = adjacency(g);
    vector<bool> inTree(r.n, false);
    inTree[start] = true; r.reached = 1;
    int last = start;
    while ((int)r.taken.size() < r.n - 1) {
        int bw = 0, by = -1;
        for (auto [y, w] : adj[last])       // first cheapest in input order
            if (!inTree[y] && (by < 0 || w < bw)) { bw = w; by = y; }
        if (by < 0) { r.stuck = last; break; }
        r.taken.push_back({last, by, bw});
        inTree[by] = true; ++r.reached;
        last = by;
    }
    return r;
}

// Array version for dense graphs: best[v] = cheapest known edge from the tree to v. O(n^2).
Result primDense(const Graph& g, int start) {
    Result r; r.start = start; r.n = (int)g.names.size();
    const long long INF = numeric_limits<long long>::max();
    vector<vector<long long>> cost(r.n, vector<long long>(r.n, INF));
    for (auto& e : g.edges)
        if (e.w < cost[e.u][e.v]) cost[e.u][e.v] = cost[e.v][e.u] = e.w;
    vector<bool> inTree(r.n, false);
    vector<long long> best(r.n, INF);
    vector<int> via(r.n, -1);
    best[start] = 0;
    for (int it = 0; it < r.n; ++it) {
        int x = -1;
        for (int v = 0; v < r.n; ++v)      // smallest best[] outside the tree; ties -> smaller index
            if (!inTree[v] && best[v] < INF && (x < 0 || best[v] < best[x])) x = v;
        if (x < 0) break;
        inTree[x] = true; ++r.reached;
        if (via[x] >= 0) r.taken.push_back({via[x], x, (int)best[x]});
        for (int v = 0; v < r.n; ++v)
            if (!inTree[v] && cost[x][v] < best[v]) { best[v] = cost[x][v]; via[v] = x; }
    }
    return r;
}

void print(const Graph& g, const Result& r, const string& mode) {
    const auto& nm = g.names;
    string head = mode == "naive" ? " (실수: 방금 붙인 정점만 봄)" : mode == "dense" ? " (배열 버전)" : "";
    cout << "시작 " << nm[r.start] << head << '\n';
    if (mode == "lazy") {
        size_t k = 0;
        for (auto& [kind, e] : r.log) {
            if (kind == 'T') cout << "고름 " << nm[e.u] << '-' << nm[e.v] << ' ' << e.w << " | 트리 " << r.treeAfter[k++] << '/' << r.n << '\n';
            else cout << "버림 " << nm[e.u] << '-' << nm[e.v] << ' ' << e.w << " | 두 끝이 이미 트리 안\n";
        }
    } else {
        for (size_t k = 0; k < r.taken.size(); ++k) {
            auto& e = r.taken[k];
            cout << "고름 " << nm[e.u] << '-' << nm[e.v] << ' ' << e.w << " | 트리 " << k + 2 << '/' << r.n << '\n';
        }
        if (mode == "naive" && r.stuck >= 0)
            cout << "막힘 " << nm[r.stuck] << " | 이 정점에서 트리 밖으로 나가는 간선 없음\n";
    }
    cout << "합계 " << r.total() << " | 간선 " << r.taken.size() << "개 | ";
    if (r.connected()) cout << "연결됨\n";
    else cout << "연결 안 됨 (트리 " << r.reached << '/' << r.n << ")\n";
}

int main(int argc, char** argv) {
    if (argc < 2) { cerr << "usage: prim GRAPH [--start NAME] [--naive | --dense]\n"; return 2; }
    string path, startName, mode = "lazy";
    for (int i = 1; i < argc; ++i) {
        string a = argv[i];
        if (a == "--start" && i + 1 < argc) startName = argv[++i];
        else if (a == "--naive") mode = "naive";
        else if (a == "--dense") mode = "dense";
        else if (path.empty()) path = a;
        else { cerr << "unexpected argument: " << a << '\n'; return 2; }
    }
    try {
        Graph g = readGraph(path);
        int start = 0;
        if (!startName.empty()) {
            auto it = find(g.names.begin(), g.names.end(), startName);
            if (it == g.names.end()) { cerr << "unknown start vertex\n"; return 2; }
            start = (int)(it - g.names.begin());
        }
        Result r = mode == "naive" ? primNaive(g, start) : mode == "dense" ? primDense(g, start) : prim(g, start);
        print(g, r, mode);
    } catch (const exception& e) {
        cerr << "error: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
