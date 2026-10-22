// 펜윅 트리(Fenwick tree, Binary Indexed Tree) — 영상 'films/fenwick-20261022'의 실행 예제, C++17 판.
// fenwick.py와 같은 출력을 글자 하나까지 똑같이 낸다(run_examples.sh가 diff로 확인).
//
// build: c++ -std=c++17 -O2 -Wall -Wextra -o fenwick fenwick.cpp
// run:   ./fenwick
#include <cassert>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

using ll = long long;

// 1번부터 n번까지. tree[i]는 (i - lowbit(i), i] 구간의 합을 맡는다.
struct Fenwick {
    int n;
    std::vector<ll> tree;  // tree[0]은 쓰지 않는다
    explicit Fenwick(int n) : n(n), tree(n + 1, 0) {}

    // i번 값에 d를 더한다. 맨 오른쪽 1(i & -i)을 더해 가며 위로 올라간다.
    void update(int i, ll d, std::vector<int>* path = nullptr) {
        for (; i <= n; i += i & -i) {
            if (path) path->push_back(i);
            tree[i] += d;
        }
    }
    // 1번부터 i번까지의 합. 맨 오른쪽 1을 빼 가며 내려온다.
    ll prefix(int i, std::vector<int>* path = nullptr) const {
        ll s = 0;
        for (; i > 0; i -= i & -i) {
            if (path) path->push_back(i);
            s += tree[i];
        }
        return s;
    }
    // l번부터 r번까지의 합 = prefix(r) - prefix(l - 1).
    ll range_sum(int l, int r) const { return prefix(r) - prefix(l - 1); }
};

static int lowbit(int i) { return i & -i; }

// x의 하위 width비트(음수는 2의 보수).
static std::string bits(ll x, int width) {
    std::string s;
    for (int b = width - 1; b >= 0; --b) s += ((static_cast<uint64_t>(x) >> b) & 1) ? '1' : '0';
    return s;
}

template <class T>
static std::string list(const std::vector<T>& v, size_t from = 0) {
    std::string s = "[";
    for (size_t i = from; i < v.size(); ++i) s += (i > from ? ", " : "") + std::to_string(v[i]);
    return s + "]";
}

// fenwick.py와 같은 수열을 내는 작은 난수기(64비트 LCG).
struct Lcg {
    uint64_t x;
    explicit Lcg(uint64_t seed) : x(seed) {}
    ll next(ll k) {
        x = x * 6364136223846793005ULL + 1442695040888963407ULL;
        return static_cast<ll>((x >> 33) % static_cast<uint64_t>(k));
    }
};

static std::string pad2(int i) { return (i < 10 ? " " : "") + std::to_string(i); }

int main() {
    std::vector<ll> A = {3, 1, 4, 1, 5, 9, 2, 6};  // 1번..8번 (예시 값)
    const int n = static_cast<int>(A.size());
    Fenwick fw(n);
    for (int i = 1; i <= n; ++i) fw.update(i, A[i - 1]);

    std::cout << "== 1. 배열과 펜윅 트리 ==\n";
    std::cout << "A    = " << list(A) << "\n";
    std::cout << "tree = " << list(fw.tree, 1) << "\n";
    for (int i = 1; i <= n; ++i)
        std::cout << "tree[" << i << "] bin=" << bits(i, 4) << " lowbit=" << lowbit(i) << " covers " << i - lowbit(i) + 1 << ".." << i << " = " << fw.tree[i] << "\n";

    std::cout << "== 2. prefix(7) ==\n";
    std::vector<int> path;
    ll s = fw.prefix(7, &path);
    std::vector<ll> vals;
    for (int i : path) vals.push_back(fw.tree[i]);
    ll naive = 0;
    for (int i = 0; i < 7; ++i) naive += A[i];
    std::cout << "path = " << list(path) << " values = " << list(vals) << " sum = " << s << "\n";
    std::cout << "naive sum(A[1..7]) = " << naive << " cells read = 7\n";

    std::cout << "== 3. update(3, +5): A[3] 4 -> 9 ==\n";
    auto prefixes = [&]() { std::vector<ll> p; ll acc = 0; for (ll v : A) p.push_back(acc += v); return p; };
    std::vector<ll> before = prefixes();
    A[2] += 5;
    std::vector<ll> after = prefixes();
    std::vector<int> changed;
    for (int i = 0; i < n; ++i) if (before[i] != after[i]) changed.push_back(i + 1);
    path.clear();
    fw.update(3, 5, &path);
    std::cout << "path = " << list(path) << " next = " << path.back() + lowbit(path.back()) << " > n\n";
    std::cout << "tree = " << list(fw.tree, 1) << "\n";
    std::cout << "prefix table before = " << list(before) << "\n";
    std::cout << "prefix table after  = " << list(after) << "\n";
    std::cout << "prefix table cells changed = " << changed.size() << " " << list(changed) << "\n";
    std::cout << "fenwick cells changed = " << path.size() << " " << list(path) << "\n";

    std::cout << "== 4. range_sum(3, 7) ==\n";
    ll p7 = fw.prefix(7), p2 = fw.prefix(2), check = 0;
    for (int i = 2; i < 7; ++i) check += A[i];
    std::cout << "prefix(7) = " << p7 << ", prefix(2) = " << p2 << ", range_sum(3, 7) = " << p7 << " - " << p2 << " = " << fw.range_sum(3, 7) << "\n";
    std::cout << "check sum(A[3..7]) = " << check << "\n";

    std::cout << "== 5. lowbit: i & -i (8-bit) ==\n";
    for (int i : {6, 7, 8})
        std::cout << pad2(i) << " = " << bits(i, 8) << "  -" << i << " = " << bits(-i, 8) << "  " << i << " & -" << i << " = " << bits(i & -i, 8) << " = " << (i & -i) << "\n";

    std::cout << "== 6. steps for n = 1,000,000 ==\n";
    const int N = 1000000;
    int maxPrefix = 0, maxUpdate = 0, bitLength = 0;
    for (int i = 1; i <= N; ++i) {
        int c = 0;
        for (int j = i; j > 0; j -= j & -j) ++c;
        if (c > maxPrefix) maxPrefix = c;
        c = 0;
        for (int j = i; j <= N; j += j & -j) ++c;
        if (c > maxUpdate) maxUpdate = c;
    }
    for (int x = N; x; x >>= 1) ++bitLength;
    std::cout << "max prefix steps = " << maxPrefix << " max update steps = " << maxUpdate << " bit length of n = " << bitLength << "\n";

    std::cout << "== 7. random check vs plain array ==\n";
    Lcg rnd(20261022);
    const int m = 1000, ops = 20000;
    std::vector<ll> plain(m + 1, 0);
    Fenwick fw2(m);
    for (int k = 0; k < ops; ++k) {
        if (rnd.next(2)) {
            int i = static_cast<int>(rnd.next(m)) + 1;
            ll d = rnd.next(201) - 100;
            plain[i] += d;
            fw2.update(i, d);
        } else {
            int l = static_cast<int>(rnd.next(m)) + 1;
            int r = l + static_cast<int>(rnd.next(m - l + 1));
            ll want = 0;
            for (int i = l; i <= r; ++i) want += plain[i];
            if (fw2.range_sum(l, r) != want) { std::cerr << "MISMATCH " << l << " " << r << "\n"; return 1; }
        }
    }
    std::cout << ops << " random ops on n = " << m << ": all range sums match\n";
    return 0;
}
