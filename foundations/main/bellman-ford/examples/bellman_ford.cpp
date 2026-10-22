// Bellman-Ford on a small graph file, with a round-by-round trace (C++17) — films/bellman-ford-20261022.
// Prints exactly what bellman_ford.py prints for the same file (tests compare the two outputs byte for byte).
//   c++ -std=c++17 -O2 -Wall -Wextra -o bellman_ford bellman_ford.cpp && ./bellman_ford graph.txt
// Graph file: 'V <names...>' (the first is the source) and one 'E <from> <to> <weight>' per edge, in scan order.
#include <algorithm>
#include <climits>
#include <fstream>
#include <iostream>
#include <optional>
#include <queue>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

using namespace std;
const long long INF = LLONG_MAX;

struct Edge { int u, v; long long w; };

// The core, as on screen (Python version): V - 1 rounds of relaxing every edge, then one more pass.
optional<vector<long long>> bellman_ford(int n, const vector<Edge>& edges, int src) {
    vector<long long> dist(n, INF);
    dist[src] = 0;
    for (int round = 0; round < n - 1; ++round)
        for (const auto& e : edges)
            if (dist[e.u] != INF && dist[e.u] + e.w < dist[e.v])
                dist[e.v] = dist[e.u] + e.w;
    for (const auto& e : edges)
        if (dist[e.u] != INF && dist[e.u] + e.w < dist[e.v])
            return nullopt;  // negative cycle
    return dist;
}

static string fmt(long long x) { return x == INF ? "INF" : to_string(x); }

int main(int argc, char** argv) {
    if (argc < 2) { cerr << "usage: bellman_ford <graph.txt>\n"; return 2; }
    string path = argv[1];
    ifstream in(path);
    if (!in) { cerr << "cannot open " << path << "\n"; return 2; }
    vector<string> names;
    vector<Edge> edges;
    string line;
    auto idx = [&](const string& s) { return int(find(names.begin(), names.end(), s) - names.begin()); };
    while (getline(in, line)) {
        istringstream ss(line);
        string tag;
        if (!(ss >> tag) || tag[0] == '#') continue;
        if (tag == "V") { names.clear(); string s; while (ss >> s) names.push_back(s); }
        else if (tag == "E") { string a, b; long long w; ss >> a >> b >> w; edges.push_back({idx(a), idx(b), w}); }
    }
    const int n = int(names.size()), src = 0;
    auto E = [&](int u, int v) { return names[u] + "->" + names[v]; };
    auto row = [&](const vector<long long>& d) {
        string s;
        for (int i = 0; i < n; ++i) s += (i ? " " : "") + names[i] + "=" + fmt(d[i]);
        return s;
    };
    string base = path.substr(path.find_last_of("/\\") == string::npos ? 0 : path.find_last_of("/\\") + 1);
    cout << "graph: " << base << "\n";
    cout << "vertices:";
    for (auto& s : names) cout << " " << s;
    cout << " (source " << names[src] << ")\n";
    cout << "edges (scan order): ";
    for (size_t k = 0; k < edges.size(); ++k) cout << (k ? ", " : "") << E(edges[k].u, edges[k].v) << " " << edges[k].w;
    cout << "\n\n";

    // Textbook Dijkstra: a popped vertex is final and never updated again.
    {
        vector<vector<pair<int, long long>>> adj(n);
        for (auto& e : edges) adj[e.u].push_back({e.v, e.w});
        vector<long long> dist(n, INF);
        vector<bool> done(n, false);
        priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> pq;
        dist[src] = 0;
        pq.push({0, src});
        cout << "[dijkstra, finalize once]\n";
        while (!pq.empty()) {
            auto [d, u] = pq.top();
            pq.pop();
            if (done[u]) continue;
            done[u] = true;
            cout << "finalize " << names[u] << " " << fmt(d) << "\n";
            for (auto [v, w] : adj[u])
                if (!done[v] && d + w < dist[v]) { dist[v] = d + w; pq.push({dist[v], v}); }
        }
        cout << "result: " << row(dist) << "\n\n";
    }

    // Bellman-Ford with every check printed.
    vector<long long> dist(n, INF);
    vector<int> pred(n, -1);
    dist[src] = 0;
    cout << "[bellman-ford]\n";
    cout << "start: " << row(dist) << "\n";
    auto cand = [&](const Edge& e) { return dist[e.u] == INF ? INF : dist[e.u] + e.w; };
    for (int r = 1; r < n; ++r) {
        cout << "round " << r << "\n";
        for (auto& e : edges) {
            long long du = dist[e.u], before = dist[e.v], c = cand(e);
            bool updated = c < before;
            if (updated) { dist[e.v] = c; pred[e.v] = e.u; }
            if (du == INF && !updated) cout << "  " << E(e.u, e.v) << " skip (" << names[e.u] << "=INF)\n";
            else if (updated) cout << "  " << E(e.u, e.v) << " " << names[e.v] << ": " << fmt(before) << " -> " << fmt(c) << "\n";
            else cout << "  " << E(e.u, e.v) << " keep (" << fmt(du) << (e.w >= 0 ? "+" : "") << e.w << "=" << fmt(c) << " >= " << fmt(before) << ")\n";
        }
        cout << "  dist: " << row(dist) << "\n";
    }
    string upd;
    for (auto& e : edges) {
        long long c = cand(e);
        if (c < dist[e.v]) upd += (upd.empty() ? "" : ", ") + E(e.u, e.v) + " " + fmt(dist[e.v]) + " -> " + fmt(c);
    }
    cout << (upd.empty() ? "check: no update -> no negative cycle" : "check: " + upd + " -> negative cycle") << "\n";
    auto plain = bellman_ford(n, edges, src);
    if (!upd.empty()) {
        if (plain) { cerr << "core and trace disagree\n"; return 1; }
        cout << "result: negative cycle (no shortest paths)\n";
        return 0;
    }
    if (!plain || *plain != dist) { cerr << "core and trace disagree\n"; return 1; }
    cout << "result: " << row(*plain) << "\n";
    for (int v = 0; v < n; ++v) {
        if (v == src || dist[v] == INF) continue;
        vector<int> p{v};
        while (p.back() != src && pred[p.back()] != -1 && int(p.size()) <= n) p.push_back(pred[p.back()]);
        reverse(p.begin(), p.end());
        cout << "path " << names[v] << ":";
        for (size_t k = 0; k < p.size(); ++k) cout << (k ? " -> " : " ") << names[p[k]];
        cout << "\n";
    }
    return 0;
}
