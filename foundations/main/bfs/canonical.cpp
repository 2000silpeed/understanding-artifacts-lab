#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;

struct Rec {
    string kind, vertex, from, action;
    vector<string> queue, visited;
    map<string, int> distance;
    map<string, string> parent;
};

struct Result {
    string start, target;
    vector<string> order, path;
    map<string, int> distance;
    map<string, string> parent;
    vector<Rec> records;
};

map<string, vector<string>> graph() {
    return {{"A", {"B", "C"}}, {"B", {"A", "D"}}, {"C", {"A", "D", "E"}},
            {"D", {"B", "C", "F"}}, {"E", {"C", "F"}}, {"F", {"D", "E"}}, {"G", {}}};
}

string q(const string& s) {
    string r = "\"";
    for (char c : s) {
        if (c == '"' || c == '\\') r += '\\';
        r += c;
    }
    return r + '"';
}

string nullable(const string& s) { return s == "null" ? "null" : q(s); }

string arr(const vector<string>& values) {
    string r = "[";
    for (size_t i = 0; i < values.size(); ++i) {
        if (i) r += ',';
        r += q(values[i]);
    }
    return r + ']';
}

string imap(const map<string, int>& values) {
    string r = "{";
    size_t i = 0;
    for (const auto& [k, v] : values) {
        if (i++) r += ',';
        r += q(k) + ':' + to_string(v);
    }
    return r + '}';
}

string smap(const map<string, string>& values) {
    string r = "{";
    size_t i = 0;
    for (const auto& [k, v] : values) {
        if (i++) r += ',';
        r += q(k) + ':' + nullable(v);
    }
    return r + '}';
}

string recjson(const Rec& r) {
    return "{\"kind\":" + q(r.kind) + ",\"vertex\":" + q(r.vertex) +
           ",\"from\":" + nullable(r.from) + ",\"action\":" + q(r.action) +
           ",\"queue\":" + arr(r.queue) + ",\"visited\":" + arr(r.visited) +
           ",\"distance\":" + imap(r.distance) + ",\"parent\":" + smap(r.parent) + '}';
}

Result bfs(const string& start, const string& target, const map<string, vector<string>>& g) {
    vector<string> queue{start};
    map<string, bool> seen{{start, true}};
    map<string, int> distance{{start, 0}};
    map<string, string> parent{{start, "null"}};
    vector<string> order;
    vector<Rec> records;
    size_t head = 0;

    auto record = [&](const string& kind, const string& vertex, const string& from, const string& action) {
        Rec r{kind, vertex, from, action, {}, {}, distance, parent};
        for (size_t i = head; i < queue.size(); ++i) r.queue.push_back(queue[i]);
        for (const auto& [k, present] : seen) if (present) r.visited.push_back(k);
        records.push_back(r);
    };

    record("enqueue", start, "null", "enqueue");
    while (head < queue.size()) {
        const string u = queue[head++];
        order.push_back(u);
        record("dequeue", u, "null", "dequeue");
        for (const string& v : g.at(u)) {
            if (!seen[v]) {
                seen[v] = true;
                distance[v] = distance[u] + 1;
                parent[v] = u;
                queue.push_back(v);
                record("enqueue", v, u, "enqueue");
            } else {
                record("skip", v, u, "skip");
            }
        }
        if (u == target) break;
    }

    vector<string> path;
    if (distance.count(target)) {
        string current = target;
        while (current != "null") {
            path.push_back(current);
            current = parent[current];
        }
        reverse(path.begin(), path.end());
    }
    return {start, target, queue, path, distance, parent, records};
}

string resultjson(const Result& r) {
    string s = "{\"start\":" + q(r.start) + ",\"target\":" + q(r.target) +
               ",\"order\":" + arr(r.order) + ",\"distance\":" + imap(r.distance) +
               ",\"parent\":" + smap(r.parent) + ",\"path\":" + arr(r.path) +
               ",\"records\":[";
    for (size_t i = 0; i < r.records.size(); ++i) {
        if (i) s += ',';
        s += recjson(r.records[i]);
    }
    return s + "]}";
}

int main(int argc, char** argv) {
    const auto g = graph();
    const auto canonical = bfs("A", "F", g);
    const auto unreachable = bfs("A", "G", g);
    if (argc > 1 && string(argv[1]) == "--trace") {
        cout << "{\"graph\":{";
        size_t i = 0;
        for (const auto& [k, v] : g) {
            if (i++) cout << ',';
            cout << q(k) << ':' << arr(v);
        }
        cout << "},\"canonical\":" << resultjson(canonical)
             << ",\"unreachable\":" << resultjson(unreachable) << "}\n";
    } else {
        cout << "graph=undirected stable adjacency\n"
             << "start=A target=F\norder=";
        for (size_t i = 0; i < canonical.order.size(); ++i) {
            if (i) cout << "->";
            cout << canonical.order[i];
        }
        cout << "\ndistance(F)=" << canonical.distance.at("F") << "\npath=";
        for (size_t i = 0; i < canonical.path.size(); ++i) {
            if (i) cout << "->";
            cout << canonical.path[i];
        }
        cout << "\nunreachable G=" << (unreachable.distance.count("G") ? "false" : "true") << "\n";
    }
}
