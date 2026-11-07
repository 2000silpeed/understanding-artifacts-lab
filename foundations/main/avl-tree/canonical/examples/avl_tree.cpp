// AVL tree: keep every node's left/right height difference within 1 by rotating on the way back up an insertion.
// The same program as avl_tree.py (C++17); for the same input it prints the same bytes.
//
//   c++ -std=c++17 -O2 -Wall -Wextra -pedantic -o avl_tree avl_tree.cpp
//   ./avl_tree input.txt
//
// Input format, heights, balance factors and "visits": see avl_tree.py.
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

const std::size_t SMALL = 32;  // inputs with at most this many keys print every insert step

struct Node {
    long long key;
    std::unique_ptr<Node> left, right;
    int height = 1;
    explicit Node(long long k) : key(k) {}
};
using Ptr = std::unique_ptr<Node>;

int height(const Ptr& n) { return n ? n->height : 0; }
int bf(const Ptr& n) { return height(n->left) - height(n->right); }
void update(Ptr& n) { n->height = 1 + std::max(height(n->left), height(n->right)); }

Ptr rotate_right(Ptr y) {
    Ptr x = std::move(y->left);
    y->left = std::move(x->right);
    update(y);
    x->right = std::move(y);
    update(x);
    return x;
}

Ptr rotate_left(Ptr x) {
    Ptr y = std::move(x->right);
    x->right = std::move(y->left);
    update(x);
    y->left = std::move(x);
    update(y);
    return y;
}

// for the report: the case, the node, its balance factor and the child on the tall side
struct Event { std::string kind; long long at; int b; long long child; };

// "LL", "LR", "RR" or "RL" when n is out of balance (|bf| = 2), else "". Used for the report only.
std::string case_of(const Ptr& n) {
    if (bf(n) > 1) return bf(n->left) < 0 ? "LR" : "LL";
    if (bf(n) < -1) return bf(n->right) > 0 ? "RL" : "RR";
    return "";
}

Ptr rebalance(Ptr n) {
    update(n);
    if (bf(n) > 1) {
        if (bf(n->left) < 0) n->left = rotate_left(std::move(n->left));
        return rotate_right(std::move(n));
    }
    if (bf(n) < -1) {
        if (bf(n->right) > 0) n->right = rotate_right(std::move(n->right));
        return rotate_left(std::move(n));
    }
    return n;
}

Ptr insert(Ptr n, long long key, std::vector<Event>& log) {
    if (!n) return std::make_unique<Node>(key);
    if (key < n->key) n->left = insert(std::move(n->left), key, log);
    else if (key > n->key) n->right = insert(std::move(n->right), key, log);
    else return n;                                // already in the tree
    update(n);
    std::string c = case_of(n);
    if (!c.empty()) log.push_back({c, n->key, bf(n), (bf(n) > 0 ? n->left : n->right)->key});
    return rebalance(std::move(n));
}

std::pair<bool, std::vector<long long>> search(const Node* n, long long key) {
    std::vector<long long> path;
    while (n) {
        path.push_back(n->key);
        if (key == n->key) return {true, path};
        n = key < n->key ? n->left.get() : n->right.get();
    }
    return {false, path};
}

// ---------- the plain binary search tree (no balancing), iterative ----------
struct Plain {
    std::vector<long long> key;
    std::vector<long> left, right;
    void insert(long long k) {
        if (key.empty()) { key.push_back(k); left.push_back(-1); right.push_back(-1); return; }
        long i = 0;
        while (true) {
            if (k == key[i]) return;
            std::vector<long>& side = k < key[i] ? left : right;
            if (side[i] < 0) {
                side[i] = static_cast<long>(key.size());
                key.push_back(k); left.push_back(-1); right.push_back(-1);
                return;
            }
            i = side[i];
        }
    }
    std::pair<bool, std::vector<long long>> search(long long k) const {
        std::vector<long long> path;
        long i = key.empty() ? -1 : 0;
        while (i >= 0) {
            path.push_back(key[i]);
            if (k == key[i]) return {true, path};
            i = k < key[i] ? left[i] : right[i];
        }
        return {false, path};
    }
    std::vector<long long> depths() const {
        std::vector<long long> out;
        std::vector<std::pair<long, long long>> stack;
        if (!key.empty()) stack.push_back({0, 1});
        while (!stack.empty()) {
            auto [i, d] = stack.back();
            stack.pop_back();
            out.push_back(d);
            for (long c : {left[i], right[i]})
                if (c >= 0) stack.push_back({c, d + 1});
        }
        return out;
    }
};

// ---------- reading, walking, checking ----------
std::vector<long long> lcg(long long n, std::uint32_t seed, long long top) {
    std::uint32_t x = seed;
    std::vector<long long> out;
    for (long long i = 0; i < n; ++i) {
        x = 1664525u * x + 1013904223u;
        out.push_back(1 + static_cast<long long>(x >> 8) % top);
    }
    return out;
}

struct Input { std::vector<long long> keys, searches; std::string src = "keys"; };

Input read_input(const std::string& path) {
    std::ifstream f(path);
    if (!f) throw std::runtime_error("cannot open " + path);
    Input in;
    std::string raw;
    while (std::getline(f, raw)) {
        std::string line = raw.substr(0, raw.find('#'));
        std::istringstream ss(line);
        std::vector<std::string> w;
        for (std::string t; ss >> t;) w.push_back(t);
        if (w.empty()) continue;
        if (w[0] == "insert") {
            for (std::size_t i = 1; i < w.size(); ++i) in.keys.push_back(std::stoll(w[i]));
        } else if (w[0] == "search") {
            for (std::size_t i = 1; i < w.size(); ++i) in.searches.push_back(std::stoll(w[i]));
        } else if (w[0] == "gen" && w[1] == "sequential") {
            long long n = std::stoll(w[2]), first = std::stoll(w[4]);
            for (long long k = first; k < first + n; ++k) in.keys.push_back(k);
            in.src = "gen sequential " + w[2] + " first " + w[4];
        } else if (w[0] == "gen" && w[1] == "random") {
            auto r = lcg(std::stoll(w[2]), static_cast<std::uint32_t>(std::stoull(w[4])), std::stoll(w[6]));
            in.keys.insert(in.keys.end(), r.begin(), r.end());
            in.src = "gen random " + w[2] + " seed " + w[4] + " max " + w[6];
        } else {
            throw std::runtime_error(path + ": unknown directive '" + raw + "'");
        }
    }
    return in;
}

std::vector<long long> preorder(const Node* n) {
    std::vector<long long> out;
    std::vector<const Node*> stack;
    if (n) stack.push_back(n);
    while (!stack.empty()) {
        const Node* x = stack.back();
        stack.pop_back();
        out.push_back(x->key);
        if (x->right) stack.push_back(x->right.get());
        if (x->left) stack.push_back(x->left.get());
    }
    return out;
}

std::vector<long long> inorder(const Node* n) {
    std::vector<long long> out;
    std::vector<const Node*> stack;
    while (!stack.empty() || n) {
        while (n) { stack.push_back(n); n = n->left.get(); }
        n = stack.back();
        stack.pop_back();
        out.push_back(n->key);
        n = n->right.get();
    }
    return out;
}

std::vector<const Node*> nodes(const Node* n) {
    std::vector<const Node*> out, stack;
    if (n) stack.push_back(n);
    while (!stack.empty()) {
        const Node* x = stack.back();
        stack.pop_back();
        out.push_back(x);
        if (x->left) stack.push_back(x->left.get());
        if (x->right) stack.push_back(x->right.get());
    }
    return out;
}

std::vector<long long> depth_counts(const Node* n) {
    std::vector<long long> out;
    std::vector<const Node*> level;
    if (n) level.push_back(n);
    while (!level.empty()) {
        out.push_back(static_cast<long long>(level.size()));
        std::vector<const Node*> next;
        for (const Node* x : level) {
            if (x->left) next.push_back(x->left.get());
            if (x->right) next.push_back(x->right.get());
        }
        level.swap(next);
    }
    return out;
}

int h(const Node* n) { return n ? n->height : 0; }

bool avl_ok(const Node* root) {
    for (const Node* x : nodes(root)) {
        int hl = h(x->left.get()), hr = h(x->right.get());
        if (x->height != 1 + std::max(hl, hr) || std::abs(hl - hr) > 1) return false;
    }
    return true;
}

long long min_nodes(int ht) {
    if (ht == 0) return 0;
    long long a = 0, b = 1;
    for (int i = 0; i < ht - 1; ++i) { long long c = a + b + 1; a = b; b = c; }
    return b;
}

int max_height(long long n) {
    int ht = 0;
    while (min_nodes(ht + 1) <= n) ++ht;
    return ht;
}

std::string sgn(int b) { return b > 0 ? "+" + std::to_string(b) : std::to_string(b); }

std::string join(const std::vector<long long>& v) {
    std::string s;
    for (std::size_t i = 0; i < v.size(); ++i) s += (i ? " " : "") + std::to_string(v[i]);
    return s;
}

// total / n with two decimals, rounded half up, in integers (same as avl_tree.py)
std::string avg(long long total, long long n) {
    long long c = (total * 100 * 2 + n) / (2 * n);
    char buf[64];
    std::snprintf(buf, sizeof buf, "%lld.%02lld", c / 100, c % 100);
    return buf;
}

std::vector<std::string> report(const Input& in) {
    Ptr root;
    Plain plain;
    std::set<long long> seen;
    std::map<std::string, long long> count{{"LL", 0}, {"RR", 0}, {"LR", 0}, {"RL", 0}};
    std::vector<std::string> steps;
    std::size_t step = 0;
    for (long long k : in.keys) {
        ++step;
        auto path = search(root.get(), k).second;
        std::vector<Event> log;
        root = insert(std::move(root), k, log);
        plain.insert(k);
        bool dup = seen.count(k) > 0;
        seen.insert(k);
        for (const auto& e : log) ++count[e.kind];
        if (in.keys.size() <= SMALL) {
            std::string fix;
            if (dup) fix = "already in tree";
            else if (!log.empty()) {
                const Event& e = log[0];
                std::string at = std::to_string(e.at), ch = std::to_string(e.child), rot;
                if (e.kind == "LL") rot = "right(" + at + ")";
                else if (e.kind == "RR") rot = "left(" + at + ")";
                else if (e.kind == "LR") rot = "left(" + ch + ") right(" + at + ")";
                else rot = "right(" + ch + ") left(" + at + ")";
                fix = "unbalanced " + at + " bf " + sgn(e.b) + " | " + e.kind + " " + rot;
            } else fix = "balanced";
            steps.push_back("step " + std::to_string(step) + " insert " + std::to_string(k) + " | path " +
                            (path.empty() ? std::string("-") : join(path)) + " | " + fix + " | height " + std::to_string(height(root)));
        }
    }
    long long n = static_cast<long long>(nodes(root.get()).size());
    std::vector<std::string> out{"keys " + std::to_string(in.keys.size()) + " nodes " + std::to_string(n) + " (" + in.src + ")"};
    out.insert(out.end(), steps.begin(), steps.end());
    if (in.keys.size() <= SMALL) {
        out.push_back("preorder " + join(preorder(root.get())));
        out.push_back("inorder " + join(inorder(root.get())));
    }
    out.push_back("avl height " + std::to_string(height(root)) + " | max for " + std::to_string(n) + " nodes " + std::to_string(max_height(n)));
    out.push_back("rotations LL " + std::to_string(count["LL"]) + " RR " + std::to_string(count["RR"]) + " LR " + std::to_string(count["LR"]) +
                  " RL " + std::to_string(count["RL"]));
    out.push_back("avl levels " + join(depth_counts(root.get())));
    auto pd = plain.depths();
    long long ph = pd.empty() ? 0 : *std::max_element(pd.begin(), pd.end());
    out.push_back("plain height " + std::to_string(ph));
    for (long long q : in.searches) {
        auto [fa, pa] = search(root.get(), q);
        auto pp = plain.search(q).second;
        std::string shown = pa.size() <= 20 ? join(pa) : std::to_string(pa.size()) + " nodes";
        out.push_back("search " + std::to_string(q) + " " + (fa ? "found" : "missing") + " | visits avl " + std::to_string(pa.size()) +
                      " plain " + std::to_string(pp.size()) + " | path " + shown);
    }
    auto keys_sorted = inorder(root.get());
    if (n) {
        long long ta = 0, tp = 0;
        for (long long k : keys_sorted) ta += static_cast<long long>(search(root.get(), k).second.size());
        for (long long d : pd) tp += d;
        out.push_back("average visits over " + std::to_string(n) + " keys | avl " + avg(ta, n) + " | plain " + avg(tp, n));
    }
    bool sorted_ok = std::is_sorted(keys_sorted.begin(), keys_sorted.end()) &&
                     std::adjacent_find(keys_sorted.begin(), keys_sorted.end()) == keys_sorted.end() &&
                     std::vector<long long>(seen.begin(), seen.end()) == keys_sorted;
    out.push_back(std::string("check inorder sorted: ") + (sorted_ok ? "yes" : "NO"));
    out.push_back(std::string("check avl heights and balance: ") + (avl_ok(root.get()) ? "yes" : "NO"));
    out.push_back(std::string("check height <= max height: ") + (height(root) <= max_height(n) ? "yes" : "NO"));
    return out;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: avl_tree <input.txt>\n";
        return 2;
    }
    try {
        for (const auto& line : report(read_input(argv[1]))) std::cout << line << '\n';
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
    return 0;
}
