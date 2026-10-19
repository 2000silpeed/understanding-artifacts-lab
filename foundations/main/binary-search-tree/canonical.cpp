#include <algorithm>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

using std::string;
using std::vector;

struct Node {
    int value;
    std::unique_ptr<Node> left;
    std::unique_ptr<Node> right;
    explicit Node(int v) : value(v) {}
};

struct Event {
    string operation;
    int value;
    bool has_current;
    int current;
    string direction;
    vector<int> path;
    vector<int> snapshot;
    vector<bool> snapshot_null;
    string result;
    bool changed;
};

vector<int> main_input{8, 3, 10, 1, 6, 14, 4, 7, 13};
vector<int> transfer_input{5, 2, 8, 1, 3};

void snapshot_walk(const Node* node, vector<int>& values, vector<bool>& nulls) {
    vector<std::pair<const Node*, size_t>> queue{{node, 0}};
    size_t max_index = 0;
    vector<std::pair<size_t, int>> positions;
    while (!queue.empty()) {
        const Node* current = queue.front().first;
        const size_t index = queue.front().second;
        queue.erase(queue.begin());
        max_index = std::max(max_index, index);
        if (current == nullptr) continue;
        positions.push_back({index, current->value});
        queue.push_back({current->left.get(), index * 2 + 1});
        queue.push_back({current->right.get(), index * 2 + 2});
    }
    values.assign(max_index + 1, 0);
    nulls.assign(max_index + 1, true);
    for (const auto& [index, value] : positions) { values[index] = value; nulls[index] = false; }
    while (!values.empty() && nulls.back()) {
        values.pop_back();
        nulls.pop_back();
    }
}

Event make_event(const string& operation, int value, const Node* current,
                 const string& direction, const vector<int>& path,
                 const Node* root, const string& result, bool changed) {
    Event e{operation, value, current != nullptr, current ? current->value : 0,
            direction, path, {}, {}, result, changed};
    snapshot_walk(root, e.snapshot, e.snapshot_null);
    return e;
}

std::unique_ptr<Node> insert(std::unique_ptr<Node> root, int value,
                             vector<Event>& events, vector<int>& out_path,
                             bool& changed) {
    if (!root) {
        root = std::make_unique<Node>(value);
        out_path = {value};
        changed = true;
        events.push_back(make_event("insert", value, nullptr, "root", {}, root.get(), "inserted", true));
        return root;
    }
    Node* node = root.get();
    vector<int> path;
    while (true) {
        path.push_back(node->value);
        if (value == node->value) {
            out_path = path;
            changed = false;
            events.push_back(make_event("insert", value, node, "equal", path, root.get(), "duplicate", false));
            return root;
        }
        const bool left = value < node->value;
        const string direction = left ? "left" : "right";
        std::unique_ptr<Node>& child = left ? node->left : node->right;
        if (!child) {
            child = std::make_unique<Node>(value);
            path.push_back(value);
            out_path = path;
            changed = true;
            events.push_back(make_event("insert", value, node, direction, path, root.get(), "inserted", true));
            return root;
        }
        node = child.get();
    }
}

const Node* search(const Node* root, int value, vector<Event>& events,
                   vector<int>& out_path) {
    const Node* node = root;
    vector<int> path;
    while (node != nullptr) {
        path.push_back(node->value);
        if (value == node->value) {
            out_path = path;
            events.push_back(make_event("search", value, node, "equal", path, root, "found", false));
            return node;
        }
        const bool left = value < node->value;
        const string direction = left ? "left" : "right";
        const Node* child = left ? node->left.get() : node->right.get();
        if (!child) {
            out_path = path;
            events.push_back(make_event("search", value, node, direction, path, root, "missing", false));
            return nullptr;
        }
        node = child;
    }
    out_path.clear();
    events.push_back(make_event("search", value, nullptr, "empty", {}, root, "missing", false));
    return nullptr;
}

void inorder(const Node* root, vector<int>& out) {
    if (!root) return;
    inorder(root->left.get(), out);
    out.push_back(root->value);
    inorder(root->right.get(), out);
}

int height(const Node* root) {
    if (!root) return 0;
    return 1 + std::max(height(root->left.get()), height(root->right.get()));
}

struct Scenario {
    vector<int> input;
    vector<Event> events;
    vector<int> search7, search5_missing, insert5, search5_found, duplicate5;
    bool duplicate5_ignored = false;
    bool insert5_changed = false;
    vector<int> final_tree;
    vector<bool> final_tree_null;
    vector<int> inorder_values;
    int tree_height = 0;
};

Scenario run_main() {
    Scenario s;
    s.input = main_input;
    std::unique_ptr<Node> root;
    bool changed = false;
    for (int value : main_input) {
        vector<int> unused;
        root = insert(std::move(root), value, s.events, unused, changed);
    }
    search(root.get(), 7, s.events, s.search7);
    search(root.get(), 5, s.events, s.search5_missing);
    root = insert(std::move(root), 5, s.events, s.insert5, changed);
    s.insert5_changed = changed;
    search(root.get(), 5, s.events, s.search5_found);
    root = insert(std::move(root), 5, s.events, s.duplicate5, changed);
    s.duplicate5_ignored = !changed;
    snapshot_walk(root.get(), s.final_tree, s.final_tree_null);
    inorder(root.get(), s.inorder_values);
    s.tree_height = height(root.get());
    return s;
}

struct EdgeScenario {
    vector<Event> events;
    vector<int> empty_search, insert_path, one_search, final_tree, inorder_values;
    vector<bool> final_tree_null;
    bool inserted = false;
};

EdgeScenario run_edge() {
    EdgeScenario s;
    std::unique_ptr<Node> root;
    search(root.get(), 42, s.events, s.empty_search);
    root = insert(std::move(root), 42, s.events, s.insert_path, s.inserted);
    search(root.get(), 42, s.events, s.one_search);
    snapshot_walk(root.get(), s.final_tree, s.final_tree_null);
    inorder(root.get(), s.inorder_values);
    return s;
}

struct TransferScenario {
    vector<int> input{transfer_input};
    vector<Event> events;
    vector<int> insert_path, final_tree, inorder_values;
    vector<bool> final_tree_null;
    bool inserted = false;
    int tree_height = 0;
};

TransferScenario run_transfer() {
    TransferScenario s;
    std::unique_ptr<Node> root;
    for (int value : transfer_input) {
        vector<int> unused;
        bool changed = false;
        root = insert(std::move(root), value, s.events, unused, changed);
    }
    root = insert(std::move(root), 4, s.events, s.insert_path, s.inserted);
    snapshot_walk(root.get(), s.final_tree, s.final_tree_null);
    inorder(root.get(), s.inorder_values);
    s.tree_height = height(root.get());
    return s;
}

string json_string(const string& value) {
    string out = "\"";
    for (char c : value) {
        if (c == '\\' || c == '"') out += '\\';
        out += c;
    }
    return out + "\"";
}

void json_ints(std::ostream& out, const vector<int>& values) {
    out << '[';
    for (size_t i = 0; i < values.size(); ++i) { if (i) out << ','; out << values[i]; }
    out << ']';
}

void json_path(std::ostream& out, const vector<int>& values) { json_ints(out, values); }

void json_snapshot(std::ostream& out, const vector<int>& values, const vector<bool>& nulls) {
    out << '[';
    for (size_t i = 0; i < values.size(); ++i) {
        if (i) out << ',';
        if (nulls[i]) out << "null"; else out << values[i];
    }
    out << ']';
}

void json_event(std::ostream& out, const Event& e) {
    out << "{\"operation\":" << json_string(e.operation)
        << ",\"value\":" << e.value << ",\"current\":";
    if (e.has_current) out << e.current; else out << "null";
    out << ",\"direction\":" << json_string(e.direction)
        << ",\"path\"}";
}

void json_event_full(std::ostream& out, const Event& e) {
    out << "{\"operation\":" << json_string(e.operation)
        << ",\"value\":" << e.value << ",\"current\":";
    if (e.has_current) out << e.current; else out << "null";
    out << ",\"direction\":" << json_string(e.direction) << ",\"path\":";
    json_path(out, e.path);
    out << ",\"snapshot\":";
    json_snapshot(out, e.snapshot, e.snapshot_null);
    out << ",\"result\":" << json_string(e.result)
        << ",\"changed\":" << (e.changed ? "true" : "false") << '}';
}

void json_events(std::ostream& out, const vector<Event>& events) {
    out << '[';
    for (size_t i = 0; i < events.size(); ++i) { if (i) out << ','; json_event_full(out, events[i]); }
    out << ']';
}

void json_scenario(std::ostream& out, const Scenario& s) {
    out << "{\"input\":"; json_ints(out, s.input);
    out << ",\"events\":"; json_events(out, s.events);
    out << ",\"search_7_path\":"; json_ints(out, s.search7);
    out << ",\"search_5_missing_path\":"; json_ints(out, s.search5_missing);
    out << ",\"insert_5_path\":"; json_ints(out, s.insert5);
    out << ",\"search_5_found_path\":"; json_ints(out, s.search5_found);
    out << ",\"duplicate_5_path\":"; json_ints(out, s.duplicate5);
    out << ",\"duplicate_5_ignored\":" << (s.duplicate5_ignored ? "true" : "false");
    out << ",\"insert_5_changed\":" << (s.insert5_changed ? "true" : "false");
    out << ",\"final_tree\":"; json_snapshot(out, s.final_tree, s.final_tree_null);
    out << ",\"inorder\":"; json_ints(out, s.inorder_values);
    out << ",\"height\":" << s.tree_height << '}';
}

void json_edge(std::ostream& out, const EdgeScenario& s) {
    out << "{\"input\":[],\"events\":"; json_events(out, s.events);
    out << ",\"empty_search_path\":"; json_ints(out, s.empty_search);
    out << ",\"insert_path\":"; json_ints(out, s.insert_path);
    out << ",\"one_node_search_path\":"; json_ints(out, s.one_search);
    out << ",\"inserted\":" << (s.inserted ? "true" : "false");
    out << ",\"final_tree\":"; json_snapshot(out, s.final_tree, s.final_tree_null);
    out << ",\"inorder\":"; json_ints(out, s.inorder_values);
    out << ",\"height\":1}";
}

void json_transfer(std::ostream& out, const TransferScenario& s) {
    out << "{\"input\":"; json_ints(out, s.input);
    out << ",\"events\":"; json_events(out, s.events);
    out << ",\"insert_4_path\":"; json_ints(out, s.insert_path);
    out << ",\"inserted\":" << (s.inserted ? "true" : "false");
    out << ",\"final_tree\":"; json_snapshot(out, s.final_tree, s.final_tree_null);
    out << ",\"inorder\":"; json_ints(out, s.inorder_values);
    out << ",\"height\":" << s.tree_height << '}';
}

string fmt(const vector<int>& values) { std::ostringstream out; json_ints(out, values); return out.str(); }

void print_default() {
    const Scenario s = run_main();
    std::cout << "BST input: " << fmt(s.input) << '\n';
    std::cout << "inorder before search: [1,3,4,6,7,8,10,13,14]\n";
    std::cout << "search(7) path: " << fmt(s.search7) << ", found: true\n";
    std::cout << "search(5) path: " << fmt(s.search5_missing) << ", found: false\n";
    std::cout << "insert(5) path: " << fmt(s.insert5) << ", inserted: true\n";
    std::cout << "search(5) path: " << fmt(s.search5_found) << ", found: true\n";
    std::cout << "insert(5) path: " << fmt(s.duplicate5) << ", duplicate ignored: true\n";
    std::cout << "inorder after: " << fmt(s.inorder_values) << '\n';
    std::cout << "final tree: "; std::ostringstream tree; json_snapshot(tree, s.final_tree, s.final_tree_null); std::cout << tree.str() << '\n';
    std::cout << "height: " << s.tree_height << '\n';
    std::cout << "trace events: " << s.events.size() << '\n';
}

int main(int argc, char** argv) {
    bool trace = false, edge = false, transfer = false;
    for (int i = 1; i < argc; ++i) {
        trace = trace || string(argv[i]) == "--trace";
        edge = edge || string(argv[i]) == "--edge";
        transfer = transfer || string(argv[i]) == "--transfer";
    }
    if (trace) {
        const Scenario c = run_main(); const EdgeScenario e = run_edge(); const TransferScenario t = run_transfer();
        std::cout << "{\"canonical\":"; json_scenario(std::cout, c);
        std::cout << ",\"edge\":"; json_edge(std::cout, e);
        std::cout << ",\"transfer\":";
        json_transfer(std::cout, t);
        std::cout << '}';
        std::cout << '\n';
        return 0;
    }
    if (edge) {
        const EdgeScenario s = run_edge();
        std::cout << "edge input: []\n";
        std::cout << "empty search(42) path: " << fmt(s.empty_search) << ", found: false\n";
        std::cout << "insert(42) path: " << fmt(s.insert_path) << ", inserted: true\n";
        std::cout << "one-node search(42) path: " << fmt(s.one_search) << ", found: true\n";
        std::cout << "edge final inorder: " << fmt(s.inorder_values) << "\nedge trace events: " << s.events.size() << '\n';
        return 0;
    }
    if (transfer) {
        const TransferScenario s = run_transfer();
        std::cout << "transfer input: " << fmt(s.input) << '\n';
        std::cout << "insert(4) path: " << fmt(s.insert_path) << ", inserted: true\n";
        std::ostringstream tree; json_snapshot(tree, s.final_tree, s.final_tree_null);
        std::cout << "transfer final tree: " << tree.str() << '\n';
        std::cout << "transfer inorder: " << fmt(s.inorder_values) << '\n';
        std::cout << "transfer height: " << s.tree_height << '\n';
        std::cout << "transfer trace events: " << s.events.size() << '\n';
        return 0;
    }
    print_default();
}
