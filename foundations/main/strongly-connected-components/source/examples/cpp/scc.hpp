// 강한 연결 요소(SCC): Kosaraju(DFS 두 번)와 Tarjan(DFS 한 번). C++17.
// python/scc.py와 같은 알고리즘·같은 방문 순서. DFS는 명시적 스택으로 짜서 깊은 그래프에서도 스택이 넘치지 않는다.
#pragma once

#include <algorithm>
#include <set>
#include <utility>
#include <vector>

namespace scc {

using Graph = std::vector<std::vector<int>>;
using Edges = std::vector<std::pair<int, int>>;

inline Graph adjacency(int n, const Edges& edges) {
    Graph adj(n);
    for (auto [u, v] : edges) adj[u].push_back(v);
    return adj;
}

// 간선 방향을 모두 뒤집은 인접 리스트
inline Graph reverse(int n, const Edges& edges) {
    Graph radj(n);
    for (auto [u, v] : edges) radj[v].push_back(u);
    return radj;
}

// 1단계: DFS가 정점을 끝낸 순서
inline std::vector<int> finish_order(const Graph& adj) {
    int n = static_cast<int>(adj.size());
    std::vector<char> seen(n, 0);
    std::vector<int> order;
    std::vector<std::pair<int, size_t>> stack;
    for (int s = 0; s < n; ++s) {
        if (seen[s]) continue;
        seen[s] = 1;
        stack.push_back({s, 0});
        while (!stack.empty()) {
            auto& [v, i] = stack.back();
            if (i < adj[v].size()) {
                int w = adj[v][i++];
                if (!seen[w]) {
                    seen[w] = 1;
                    stack.push_back({w, 0});  // 참조 v, i는 여기서 무효가 되므로 이후에 쓰지 않는다
                }
            } else {
                order.push_back(v);
                stack.pop_back();
            }
        }
    }
    return order;
}

struct KosarajuResult {
    std::vector<int> order;               // 1단계 끝난 순서
    std::vector<std::vector<int>> comps;  // 응축 그래프의 위상 순서
};

// 2단계: 끝난 순서의 역순으로, 뒤집은 그래프에서 DFS. 한 번의 DFS가 닿는 곳이 한 묶음.
inline KosarajuResult kosaraju(int n, const Edges& edges) {
    KosarajuResult r;
    r.order = finish_order(adjacency(n, edges));
    Graph radj = reverse(n, edges);
    std::vector<char> seen(n, 0);
    std::vector<std::pair<int, size_t>> stack;
    for (auto it = r.order.rbegin(); it != r.order.rend(); ++it) {
        int s = *it;
        if (seen[s]) continue;
        seen[s] = 1;
        std::vector<int> comp{s};
        stack.push_back({s, 0});
        while (!stack.empty()) {
            auto& [v, i] = stack.back();
            if (i < radj[v].size()) {
                int w = radj[v][i++];
                if (!seen[w]) {
                    seen[w] = 1;
                    comp.push_back(w);
                    stack.push_back({w, 0});
                }
            } else {
                stack.pop_back();
            }
        }
        r.comps.push_back(std::move(comp));
    }
    return r;
}

// DFS 한 번. low[v] == index[v]이면 v가 묶음의 뿌리. 묶음은 역위상 순서로 나온다.
inline std::vector<std::vector<int>> tarjan(int n, const Edges& edges) {
    Graph adj = adjacency(n, edges);
    std::vector<int> index(n, -1), low(n, 0), st;
    std::vector<char> on(n, 0);
    std::vector<std::vector<int>> comps;
    std::vector<std::pair<int, size_t>> call;
    int t = 0;
    for (int s = 0; s < n; ++s) {
        if (index[s] != -1) continue;
        index[s] = low[s] = t++;
        st.push_back(s);
        on[s] = 1;
        call.push_back({s, 0});
        while (!call.empty()) {
            int v = call.back().first;
            size_t& i = call.back().second;
            if (i < adj[v].size()) {
                int w = adj[v][i++];
                if (index[w] == -1) {
                    index[w] = low[w] = t++;
                    st.push_back(w);
                    on[w] = 1;
                    call.push_back({w, 0});
                } else if (on[w]) {
                    low[v] = std::min(low[v], index[w]);
                }
            } else {
                call.pop_back();
                if (!call.empty()) {
                    int u = call.back().first;
                    low[u] = std::min(low[u], low[v]);
                }
                if (low[v] == index[v]) {
                    std::vector<int> comp;
                    while (true) {
                        int w = st.back();
                        st.pop_back();
                        on[w] = 0;
                        comp.push_back(w);
                        if (w == v) break;
                    }
                    comps.push_back(std::move(comp));
                }
            }
        }
    }
    return comps;
}

// 묶음 하나를 점 하나로 줄인 그래프의 간선(중복·자기 간선 제외, 처음 나온 순서)
inline Edges condense(int n, const Edges& edges, const std::vector<std::vector<int>>& comps,
                      std::vector<int>* cid_out = nullptr) {
    std::vector<int> cid(n, 0);
    for (size_t k = 0; k < comps.size(); ++k)
        for (int v : comps[k]) cid[v] = static_cast<int>(k);
    Edges out;
    std::set<std::pair<int, int>> seen;
    for (auto [u, v] : edges) {
        std::pair<int, int> e{cid[u], cid[v]};
        if (e.first != e.second && seen.insert(e).second) out.push_back(e);
    }
    if (cid_out) *cid_out = cid;
    return out;
}

}  // namespace scc
