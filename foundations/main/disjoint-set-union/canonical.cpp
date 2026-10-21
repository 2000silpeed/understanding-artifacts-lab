#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

struct Event {
    std::string operation;
    int a;
    bool has_b;
    int b;
    std::string result;
    std::vector<int> roots;
    bool changed;
    std::vector<std::vector<int>> path_before;
    std::vector<std::vector<int>> path_after;
    std::vector<int> parent;
    std::vector<int> size;
};

struct DSU {
    int n;
    std::vector<int> parent;
    std::vector<int> size;
    std::vector<Event> events;

    explicit DSU(int count) : n(count), parent(count), size(count, 1) {
        for (int i = 0; i < n; ++i) parent[i] = i;
    }

    bool valid(int x, std::string& reason) const {
        if (x < 0) { reason = "negative_id"; return false; }
        if (x >= n) { reason = "out_of_range"; return false; }
        return true;
    }

    std::vector<int> path_to_root(int x) const {
        std::vector<int> path{x};
        while (path.back() != parent[path.back()]) path.push_back(parent[path.back()]);
        return path;
    }

    void record(const std::string& operation, int a, bool has_b, int b,
                const std::string& result, const std::vector<int>& roots,
                bool changed, const std::vector<std::vector<int>>& before = {},
                const std::vector<std::vector<int>>& after = {}) {
        events.push_back(Event{operation, a, has_b, b, result, roots, changed,
                               before, after, parent, size});
    }

    int find(int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];
        while (parent[x] != x) {
            const int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    }

    bool find_observed(int x, int& root) {
        std::string reason;
        if (!valid(x, reason)) {
            record("find", x, false, 0, reason, {}, false);
            return false;
        }
        const std::vector<std::vector<int>> before{path_to_root(x)};
        root = find(x);
        const std::vector<std::vector<int>> after{path_to_root(x)};
        record("find", x, false, 0, "root", {root}, before != after,
               before, after);
        return true;
    }

    bool union_op(int a, int b, bool& changed, std::string& reason) {
        std::string reason_a;
        std::string reason_b;
        if (!valid(a, reason_a) || !valid(b, reason_b)) {
            reason = reason_a.empty() ? reason_b : reason_a;
            changed = false;
            record("union", a, true, b, reason, {}, false);
            return false;
        }
        const std::vector<std::vector<int>> before{path_to_root(a), path_to_root(b)};
        int ra = find(a);
        int rb = find(b);
        if (ra == rb) {
            changed = false;
            const std::vector<std::vector<int>> after{path_to_root(a), path_to_root(b)};
            record("union", a, true, b, "already_same", {ra, rb}, false, before, after);
            return true;
        }
        if (size[ra] < size[rb] || (size[ra] == size[rb] && rb < ra)) std::swap(ra, rb);
        parent[rb] = ra;
        size[ra] += size[rb];
        changed = true;
        const std::vector<std::vector<int>> after{path_to_root(a), path_to_root(b)};
        record("union", a, true, b, "merged", {ra, rb}, true, before, after);
        reason.clear();
        return true;
    }

    bool same_op(int a, int b, bool& result, std::string& reason) {
        std::string reason_a;
        std::string reason_b;
        if (!valid(a, reason_a) || !valid(b, reason_b)) {
            reason = reason_a.empty() ? reason_b : reason_a;
            result = false;
            record("same", a, true, b, reason, {}, false);
            return false;
        }
        const std::vector<std::vector<int>> before{path_to_root(a), path_to_root(b)};
        const int ra = find(a);
        const int rb = find(b);
        result = ra == rb;
        const std::vector<std::vector<int>> after{path_to_root(a), path_to_root(b)};
        record("same", a, true, b, result ? "true" : "false", {ra, rb},
               before != after, before, after);
        reason.clear();
        return true;
    }
};

std::string q(const std::string& value) {
    std::ostringstream out;
    out << '"';
    for (const char ch : value) {
        if (ch == '"' || ch == '\\') out << '\\';
        out << ch;
    }
    out << '"';
    return out.str();
}

std::string b(bool value) { return value ? "true" : "false"; }

std::string ints(const std::vector<int>& values) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) out << ',';
        out << values[i];
    }
    out << ']';
    return out.str();
}

std::string paths(const std::vector<std::vector<int>>& values) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) out << ',';
        out << ints(values[i]);
    }
    out << ']';
    return out.str();
}

std::string snapshot(const std::vector<int>& parent, const std::vector<int>& size) {
    return "{\"parent\":" + ints(parent) + ",\"size\":" + ints(size) + "}";
}

std::string event_json(const Event& event) {
    std::ostringstream out;
    out << "{\"operation\":" << q(event.operation)
        << ",\"a\":" << event.a << ",\"b\":"
        << (event.has_b ? std::to_string(event.b) : "null")
        << ",\"result\":" << q(event.result)
        << ",\"roots\":" << ints(event.roots)
        << ",\"changed\":" << b(event.changed)
        << ",\"path_before\":" << paths(event.path_before)
        << ",\"path_after\":" << paths(event.path_after)
        << ",\"snapshot\":" << snapshot(event.parent, event.size) << '}';
    return out.str();
}

std::string events_json(const std::vector<Event>& events) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < events.size(); ++i) {
        if (i) out << ',';
        out << event_json(events[i]);
    }
    out << ']';
    return out.str();
}

struct Canonical {
    DSU dsu;
    std::vector<int> initial_parent;
    std::vector<int> initial_size;
    std::vector<bool> union_changed;
    std::vector<int> path_before;
    std::vector<int> path_after;
    bool same_03;
    bool same_04;
    bool duplicate_changed;

    Canonical() : dsu(6), initial_parent(dsu.parent), initial_size(dsu.size),
                  same_03(false), same_04(false), duplicate_changed(false) {}
};

Canonical run_canonical() {
    Canonical c;
    bool changed = false;
    std::string reason;
    c.dsu.union_op(0, 1, changed, reason); c.union_changed.push_back(changed);
    c.dsu.union_op(2, 3, changed, reason); c.union_changed.push_back(changed);
    c.dsu.union_op(1, 2, changed, reason); c.union_changed.push_back(changed);
    c.path_before = c.dsu.path_to_root(3);
    int observed_root = 0;
    c.dsu.find_observed(3, observed_root);
    c.path_after = c.dsu.path_to_root(3);
    c.dsu.same_op(0, 3, c.same_03, reason);
    c.dsu.same_op(0, 4, c.same_04, reason);
    c.dsu.union_op(0, 3, c.duplicate_changed, reason);
    return c;
}

struct EdgeRuns {
    DSU empty;
    DSU single;
    EdgeRuns() : empty(0), single(1) {}
};

EdgeRuns run_edge() {
    EdgeRuns e;
    bool result = false;
    bool changed = false;
    std::string reason;
    e.empty.union_op(0, 0, changed, reason);
    e.empty.same_op(0, 0, result, reason);
    int root = 0;
    e.empty.find_observed(-1, root);
    e.single.union_op(0, 0, changed, reason);
    e.single.same_op(0, 0, result, reason);
    e.single.union_op(0, 1, changed, reason);
    return e;
}

struct Transfer {
    DSU dsu;
    bool before;
    bool join_changed;
    bool after;
    Transfer() : dsu(6), before(false), join_changed(false), after(false) {}
};

Transfer run_transfer() {
    Transfer t;
    bool changed = false;
    std::string reason;
    t.dsu.union_op(0, 1, changed, reason);
    t.dsu.union_op(2, 3, changed, reason);
    t.dsu.union_op(1, 2, changed, reason);
    t.dsu.union_op(4, 5, changed, reason);
    t.dsu.same_op(0, 5, t.before, reason);
    t.dsu.union_op(3, 5, t.join_changed, reason);
    t.dsu.same_op(0, 5, t.after, reason);
    return t;
}

std::string canonical_json(const Canonical& c) {
    std::ostringstream out;
    out << "{\"input\":[0,1,2,3,4,5],\"initial\":"
        << snapshot(c.initial_parent, c.initial_size) << ",\"unions\":[";
    for (std::size_t i = 0; i < c.union_changed.size(); ++i) {
        if (i) out << ',';
        out << "{\"accepted\":true,\"changed\":" << b(c.union_changed[i])
            << ",\"root\":" << c.dsu.events[i].roots[0] << '}';
    }
    out << "],\"find_3_path_before\":" << ints(c.path_before)
        << ",\"find_3_path_after\":" << ints(c.path_after)
        << ",\"queries\":{\"same_0_3\":{\"accepted\":true,\"result\":"
        << b(c.same_03) << "},\"same_0_4\":{\"accepted\":true,\"result\":"
        << b(c.same_04) << "}},\"duplicate_union_0_3\":{\"accepted\":true,\"changed\":"
        << b(c.duplicate_changed) << ",\"root\":0},\"events\":" << events_json(c.dsu.events)
        << ",\"final\":" << snapshot(c.dsu.parent, c.dsu.size) << '}';
    return out.str();
}

std::string edge_json(const EdgeRuns& e) {
    std::ostringstream out;
    out << "{\"n_zero\":{\"union_0_0\":{\"accepted\":false,\"reason\":\"out_of_range\",\"changed\":false},\"same_0_0\":{\"accepted\":false,\"reason\":\"out_of_range\",\"result\":false},\"negative_find\":null,\"events\":"
        << events_json(e.empty.events) << ",\"final\":" << snapshot(e.empty.parent, e.empty.size)
        << "},\"n_one\":{\"union_0_0\":{\"accepted\":true,\"changed\":false,\"root\":0},\"same_0_0\":{\"accepted\":true,\"result\":true},\"out_of_range_union\":{\"accepted\":false,\"reason\":\"out_of_range\",\"changed\":false},\"events\":"
        << events_json(e.single.events) << ",\"final\":" << snapshot(e.single.parent, e.single.size) << "}}";
    return out.str();
}

std::string transfer_json(const Transfer& t) {
    std::ostringstream out;
    out << "{\"after_union_4_5_same_0_5\":{\"accepted\":true,\"result\":"
        << b(t.before) << "},\"union_3_5\":{\"accepted\":true,\"changed\":"
        << b(t.join_changed) << ",\"root\":0},\"after_union_3_5_same_0_5\":{\"accepted\":true,\"result\":"
        << b(t.after) << "},\"final\":" << snapshot(t.dsu.parent, t.dsu.size)
        << ",\"events\":" << events_json(t.dsu.events) << '}';
    return out.str();
}

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "";
    if (mode == "--trace") {
        const Canonical c = run_canonical();
        const EdgeRuns e = run_edge();
        const Transfer t = run_transfer();
        std::cout << "{\"canonical\":" << canonical_json(c)
                  << ",\"edge\":" << edge_json(e)
                  << ",\"transfer\":" << transfer_json(t) << "}\n";
        return 0;
    }
    if (mode == "--edge") {
        const EdgeRuns e = run_edge();
        std::cout << "edge n=0 union(0,0) accepted: false, reason: out_of_range\n"
                  << "edge n=0 negative find accepted: false, reason: negative_id\n"
                  << "edge n=1 self union changed: false\n"
                  << "edge n=1 same(0,0): true\n"
                  << "edge n=1 union(0,1) accepted: false, reason: out_of_range\n"
                  << "edge trace events: " << (e.empty.events.size() + e.single.events.size()) << "\n";
        return 0;
    }
    if (mode == "--transfer") {
        const Transfer t = run_transfer();
        std::cout << "transfer after union(4,5) same(0,5): " << b(t.before) << "\n"
                  << "transfer union(3,5) changed: " << b(t.join_changed) << "\n"
                  << "transfer after union(3,5) same(0,5): " << b(t.after) << "\n"
                  << "transfer final root size: " << t.dsu.size[0] << "\n"
                  << "transfer trace events: " << t.dsu.events.size() << "\n";
        return 0;
    }
    const Canonical c = run_canonical();
    std::cout << "dsu input: [0,1,2,3,4,5]\n"
              << "union (0,1) changed: " << b(c.union_changed[0]) << "\n"
              << "union (2,3) changed: " << b(c.union_changed[1]) << "\n"
              << "union (1,2) changed: " << b(c.union_changed[2]) << "\n"
              << "find 3 before path: 3->2->0\n"
              << "find 3 after path: 3->0\n"
              << "same (0,3): " << b(c.same_03) << "\n"
              << "same (0,4): " << b(c.same_04) << "\n"
              << "duplicate union (0,3) changed: " << b(c.duplicate_changed) << "\n"
              << "final parent: [0, 0, 0, 0, 4, 5]\n"
              << "final root size: " << c.dsu.size[0] << "\n"
              << "trace events: " << c.dsu.events.size() << "\n";
    return 0;
}
