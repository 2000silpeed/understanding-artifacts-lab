// 수업 화면에 쓰는 실행 기록을 찍는다. python/scc.py의 텍스트 출력과 글자 하나까지 같아야 한다.
// build: c++ -std=c++17 -O2 -Wall -Wextra -Werror main.cpp -o scc
// usage: ./scc <graph file>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>

#include "scc.hpp"

namespace {

bool read_graph(const std::string& path, std::vector<std::string>& names, scc::Edges& edges) {
    std::ifstream in(path);
    if (!in) {
        std::cerr << path << ": 열 수 없다\n";
        return false;
    }
    std::map<std::string, int> idx;
    bool have_nodes = false;
    std::string line;
    for (int no = 1; std::getline(in, line); ++no) {
        std::istringstream ss(line);
        std::vector<std::string> parts;
        for (std::string p; ss >> p;) parts.push_back(p);
        if (parts.empty() || parts[0][0] == '#') continue;
        if (parts[0] == "nodes") {
            names.assign(parts.begin() + 1, parts.end());
            for (size_t i = 0; i < names.size(); ++i) idx[names[i]] = static_cast<int>(i);
            have_nodes = true;
            continue;
        }
        if (!have_nodes || parts.size() != 3 || parts[1] != "->" || !idx.count(parts[0]) || !idx.count(parts[2])) {
            std::cerr << path << ":" << no << ": \"" << line << "\"\n";
            return false;
        }
        edges.push_back({idx[parts[0]], idx[parts[2]]});
    }
    if (!have_nodes) std::cerr << path << ": nodes 줄이 없다\n";
    return have_nodes;
}

std::string join(const std::vector<int>& vs, const std::vector<std::string>& names) {
    std::string s;
    for (size_t i = 0; i < vs.size(); ++i) s += (i ? " " : "") + names[vs[i]];
    return s;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: scc <graph file>\n";
        return 2;
    }
    std::vector<std::string> names;
    scc::Edges edges;
    if (!read_graph(argv[1], names, edges)) return 1;
    int n = static_cast<int>(names.size());

    auto kr = scc::kosaraju(n, edges);
    auto cedges = scc::condense(n, edges, kr.comps);
    auto tj = scc::tarjan(n, edges);
    int c = static_cast<int>(kr.comps.size());

    std::vector<int> rev(kr.order.rbegin(), kr.order.rend()), starts;
    for (auto& comp : kr.comps) starts.push_back(comp[0]);

    std::cout << "그래프: 정점 " << n << "개, 간선 " << edges.size() << "개\n";
    std::cout << "1단계 끝난 순서: " << join(kr.order, names) << "\n";
    std::cout << "2단계 살펴볼 순서(끝난 순서의 역순): " << join(rev, names) << "\n";
    std::cout << "2단계 실제 출발점: " << join(starts, names) << "\n";
    for (int k = 0; k < c; ++k) std::cout << "묶음 " << k + 1 << ": {" << join(kr.comps[k], names) << "}\n";
    std::cout << "응축 간선: ";
    for (size_t i = 0; i < cedges.size(); ++i)
        std::cout << (i ? ", " : "") << cedges[i].first + 1 << "->" << cedges[i].second + 1;
    std::cout << "\n위상 순서(호출하는 쪽 먼저):";
    for (int k = 1; k <= c; ++k) std::cout << " " << k;
    std::cout << "\n배포 순서(호출받는 쪽 먼저):";
    for (int k = c; k >= 1; --k) std::cout << " " << k;
    std::cout << "\nTarjan 묶음 순서:";
    for (auto& comp : tj) std::cout << " {" << join(comp, names) << "}";

    auto canon = [](std::vector<std::vector<int>> cs) {
        for (auto& x : cs) std::sort(x.begin(), x.end());
        std::sort(cs.begin(), cs.end());
        return cs;
    };
    std::cout << "\nTarjan과 같은 분할: " << (canon(kr.comps) == canon(tj) ? "예" : "아니오") << "\n";
    return 0;
}
