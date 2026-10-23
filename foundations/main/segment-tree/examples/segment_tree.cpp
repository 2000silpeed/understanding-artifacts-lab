// 세그먼트 트리: 한 점 갱신 + 구간 최솟값 질의 (재귀, 노드 번호는 1부터). C++17
// 입력 형식은 segment_tree.py와 같다.
// 빌드: c++ -std=c++17 -O2 -Wall -Wextra -o segment_tree segment_tree.cpp
// 사용: ./segment_tree < input.txt
#include <algorithm>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

using namespace std;

const long long INF = numeric_limits<long long>::max();

struct SegmentTree {
    int n;
    vector<long long> tree;

    explicit SegmentTree(const vector<long long>& a) : n(static_cast<int>(a.size())), tree(4 * a.size(), INF) {
        build(a, 1, 0, n - 1);
    }

    void build(const vector<long long>& a, int node, int start, int end) {
        if (start == end) {
            tree[node] = a[start];
            return;
        }
        int mid = (start + end) / 2;
        build(a, 2 * node, start, mid);
        build(a, 2 * node + 1, mid + 1, end);
        tree[node] = min(tree[2 * node], tree[2 * node + 1]);
    }

    long long query(int node, int start, int end, int l, int r) const {
        if (r < start || end < l) return INF;              // 밖: 겹치지 않음
        if (l <= start && end <= r) return tree[node];     // 안: 통째로 포함
        int mid = (start + end) / 2;                       // 걸침: 두 자식으로
        long long left = query(2 * node, start, mid, l, r);
        long long right = query(2 * node + 1, mid + 1, end, l, r);
        return min(left, right);
    }

    void update(int node, int start, int end, int i, long long x) {
        if (start == end) {                                // 잎: 값을 바꾼다
            tree[node] = x;
            return;
        }
        int mid = (start + end) / 2;
        if (i <= mid) update(2 * node, start, mid, i, x);
        else update(2 * node + 1, mid + 1, end, i, x);
        tree[node] = min(tree[2 * node], tree[2 * node + 1]);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    if (!(cin >> n)) return 1;
    vector<long long> a(n);
    for (auto& v : a) cin >> v;
    SegmentTree st(a);
    int q;
    cin >> q;
    for (int k = 0; k < q; k++) {
        string op;
        long long u, v;
        cin >> op >> u >> v;
        if (op == "query") {
            cout << st.query(1, 0, n - 1, static_cast<int>(u), static_cast<int>(v)) << '\n';
        } else if (op == "update") {
            st.update(1, 0, n - 1, static_cast<int>(u), v);
        } else {
            cerr << "unknown operation: " << op << '\n';
            return 2;
        }
    }
    return 0;
}
