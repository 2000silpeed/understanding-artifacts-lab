// Sparse table: range minimum queries on an array that never changes (C++17).
// Same algorithm and the same text report as sparse_table.py, character for character (run_examples.py checks it).
//
//   c++ -std=c++17 -O2 -Wall -Wextra -pedantic -o sparse_table sparse_table.cpp
//   ./sparse_table input.txt
// input: n / n integers / q / q lines "l r" (0-based, inclusive); text after # on a line is ignored.
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using std::vector;

// lg[x] = floor(log2 x) for 1 <= x <= n
vector<int> build_log(int n) {
    vector<int> lg(n + 1, 0);
    for (int x = 2; x <= n; ++x) lg[x] = lg[x / 2] + 1;
    return lg;
}

// table[k][i] = min(a[i .. i + 2^k - 1]) for every k with 2^k <= n
vector<vector<long long>> build(const vector<long long>& a) {
    int n = static_cast<int>(a.size());
    vector<vector<long long>> table{a};
    for (int k = 1; (1 << k) <= n; ++k) {
        const vector<long long>& prev = table[k - 1];
        int half = 1 << (k - 1);
        vector<long long> row;
        for (int i = 0; i + (1 << k) <= n; ++i) row.push_back(std::min(prev[i], prev[i + half]));
        table.push_back(row);
    }
    return table;
}

long long query(const vector<vector<long long>>& table, const vector<int>& lg, int l, int r) {
    int k = lg[r - l + 1];
    return std::min(table[k][l], table[k][r - (1 << k) + 1]);
}

std::string join(const vector<long long>& v) {
    std::string s;
    for (size_t i = 0; i < v.size(); ++i) s += (i ? " " : "") + std::to_string(v[i]);
    return s;
}

long long block_sum(const vector<long long>& a, int s, int e) {
    long long t = 0;
    for (int i = s; i <= e; ++i) t += a[i];
    return t;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: sparse_table input.txt\n";
        return 2;
    }
    std::ifstream in(argv[1]);
    if (!in) {
        std::cerr << "cannot open " << argv[1] << "\n";
        return 2;
    }
    std::string line, text;
    while (std::getline(in, line)) text += line.substr(0, line.find('#')) + "\n";
    std::istringstream ss(text);
    int n = 0, q = 0;
    ss >> n;
    vector<long long> a(n);
    for (auto& x : a) ss >> x;
    ss >> q;
    vector<std::pair<int, int>> qs(q);
    for (auto& p : qs) ss >> p.first >> p.second;
    if (!ss) {
        std::cerr << "bad input\n";
        return 1;
    }
    for (auto& p : qs)
        if (p.first < 0 || p.first > p.second || p.second >= n) {
            std::cerr << "query outside 0.." << n - 1 << "\n";
            return 1;
        }

    auto table = build(a);
    auto lg = build_log(n);
    size_t cells = 0;
    std::cout << "n = " << n << "\n";
    std::cout << "a     = " << join(a) << "\n";
    for (size_t k = 0; k < table.size(); ++k) {
        std::string len = std::to_string(1 << k);
        if (len.size() < 2) len += ' ';  // same as Python's f'{x:<2}': pad, never cut
        std::cout << "len " << len << "= " << join(table[k]) << "\n";
        cells += table[k].size();
    }
    std::cout << "cells = " << cells << "\n";
    for (auto& [l, r] : qs) {
        int k = lg[r - l + 1], s2 = r - (1 << k) + 1;
        std::cout << "query " << l << " " << r << ": len " << r - l + 1 << ", k " << k << ", [" << l << "," << l + (1 << k) - 1
                  << "] -> " << table[k][l] << ", [" << s2 << "," << r << "] -> " << table[k][s2] << ", min "
                  << query(table, lg, l, r) << "\n";
    }
    for (auto& [l, r] : qs) {
        int k = lg[r - l + 1], s2 = r - (1 << k) + 1;
        long long b1 = block_sum(a, l, l + (1 << k) - 1), b2 = block_sum(a, s2, r);
        std::cout << "sum " << l << " " << r << ": blocks " << b1 << " + " << b2 << " = " << b1 + b2 << ", true "
                  << block_sum(a, l, r) << "\n";
    }
    return 0;
}
