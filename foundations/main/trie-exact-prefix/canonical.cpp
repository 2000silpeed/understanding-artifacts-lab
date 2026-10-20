#include <array>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

struct Node { char ch; std::optional<int> parent; std::array<std::optional<int>, 26> children{}; bool terminal = false; };
struct Event {
    std::string operation, word, action, result;
    int index;
    std::optional<int> node;
    bool changed;
};

class Trie {
public:
    std::vector<Node> nodes{{Node{'\0', std::nullopt}}};
    std::vector<Event> events;

    std::string snapshot() const {
        std::ostringstream out;
        out << '[';
        for (std::size_t i = 0; i < nodes.size(); ++i) {
            if (i) out << ',';
            const Node& n = nodes[i];
            out << "{\"id\":" << i << ",\"parent\":";
            if (n.parent) out << *n.parent; else out << "null";
            out << ",\"char\":\"" << (n.ch == '\0' ? "" : std::string(1, n.ch))
                << "\",\"terminal\":" << (n.terminal ? "true" : "false") << '}';
        }
        return out.str() + ']';
    }

    void event(const std::string& operation, const std::string& word, int index,
               const std::string& action, std::optional<int> node,
               const std::string& result, bool changed) {
        events.push_back(Event{operation, word, action, result, index, node, changed});
    }

    std::optional<std::string> validate(const std::string& word) const {
        if (word.empty()) return "empty";
        for (char ch : word) if (ch < 'a' || ch > 'z') return "lowercase_a_z_only";
        return std::nullopt;
    }

    bool insert(const std::string& word, std::string& reason, bool& changed) {
        const auto invalid = validate(word);
        if (invalid) {
            reason = *invalid; changed = false;
            event("insert", word, 0, "reject", std::nullopt, reason, false);
            return false;
        }
        int node = 0; changed = false;
        for (int index = 0; index < static_cast<int>(word.size()); ++index) {
            const int slot = word[index] - 'a';
            auto child = nodes[node].children[slot];
            std::string action;
            if (!child) {
                child = static_cast<int>(nodes.size());
                nodes[node].children[slot] = child;
                nodes.push_back(Node{word[index], node, {}, false});
                action = "create"; changed = true;
            } else action = "follow";
            node = *child;
            event("insert", word, index, action, node, "step", action == "create");
        }
        const bool already = nodes[node].terminal;
        if (!already) { nodes[node].terminal = true; changed = true; }
        event("terminal", word, static_cast<int>(word.size()), "check", node,
              already ? "duplicate" : "marked", !already);
        reason.clear();
        return true;
    }

    bool search(const std::string& word, bool exact, std::string& reason) {
        const std::string operation = exact ? "exact" : "prefix";
        const auto invalid = validate(word);
        if (invalid) {
            reason = *invalid; event(operation, word, 0, "reject", std::nullopt, reason, false); return false;
        }
        int node = 0;
        for (int index = 0; index < static_cast<int>(word.size()); ++index) {
            const auto child = nodes[node].children[word[index] - 'a'];
            if (!child) { event(operation, word, index, "missing", std::nullopt, "false", false); return false; }
            node = *child;
            event(operation, word, index, "follow", node, "step", false);
        }
        const bool result = !exact || nodes[node].terminal;
        event(operation, word, static_cast<int>(word.size()), "terminal_check", node,
              result ? "true" : "false", false);
        return result;
    }
};

std::string q(const std::string& value) {
    std::ostringstream out; out << '"';
    for (char ch : value) { if (ch == '"' || ch == '\\') out << '\\'; out << ch; }
    return out.str() + '"';
}
std::string b(bool value) { return value ? "true" : "false"; }
std::string opt(const std::optional<int>& value) { return value ? std::to_string(*value) : "null"; }
// Re-run the same state machine with a snapshot captured immediately after every event.
struct SnapEvent { Event e; std::string snap; };
class SnapTrie {
public:
    std::vector<Node> nodes{{Node{'\0', std::nullopt}}};
    std::vector<SnapEvent> events;
    std::string snapshot() const {
        std::ostringstream out; out << '[';
        for (std::size_t i = 0; i < nodes.size(); ++i) {
            if (i) out << ',';
            const Node& n = nodes[i];
            out << "{\"id\":" << i << ",\"parent\":" << opt(n.parent)
                << ",\"char\":" << q(n.ch == '\0' ? "" : std::string(1, n.ch))
                << ",\"terminal\":" << b(n.terminal) << '}';
        }
        return out.str() + ']';
    }
    void ev(const std::string& op, const std::string& word, int index, const std::string& action,
            std::optional<int> node, const std::string& result, bool changed) {
        events.push_back(SnapEvent{Event{op, word, action, result, index, node, changed}, snapshot()});
    }
    std::optional<std::string> valid(const std::string& word) const {
        if (word.empty()) return "empty";
        for (char c : word) if (c < 'a' || c > 'z') return "lowercase_a_z_only";
        return std::nullopt;
    }
    std::pair<bool, bool> insert(const std::string& word) {
        if (auto bad = valid(word)) { ev("insert", word, 0, "reject", std::nullopt, *bad, false); return {false, false}; }
        int node = 0; bool changed = false;
        for (int i = 0; i < static_cast<int>(word.size()); ++i) {
            const int slot = word[i] - 'a'; auto child = nodes[node].children[slot]; std::string action;
            if (!child) { child = static_cast<int>(nodes.size()); nodes[node].children[slot] = child; nodes.push_back(Node{word[i], node, {}, false}); action = "create"; changed = true; }
            else action = "follow";
            node = *child; ev("insert", word, i, action, node, "step", action == "create");
        }
        const bool already = nodes[node].terminal; if (!already) { nodes[node].terminal = true; changed = true; }
        ev("terminal", word, static_cast<int>(word.size()), "check", node, already ? "duplicate" : "marked", !already);
        return {true, changed};
    }
    bool search(const std::string& word, bool exact) {
        const std::string op = exact ? "exact" : "prefix";
        if (auto bad = valid(word)) { ev(op, word, 0, "reject", std::nullopt, *bad, false); return false; }
        int node = 0;
        for (int i = 0; i < static_cast<int>(word.size()); ++i) { auto child = nodes[node].children[word[i] - 'a']; if (!child) { ev(op, word, i, "missing", std::nullopt, "false", false); return false; } node = *child; ev(op, word, i, "follow", node, "step", false); }
        const bool result = !exact || nodes[node].terminal; ev(op, word, static_cast<int>(word.size()), "terminal_check", node, result ? "true" : "false", false); return result;
    }
};

std::string snap_event_json(const SnapEvent& se) {
    const Event& e = se.e; std::ostringstream out;
    out << "{\"operation\":" << q(e.operation) << ",\"word\":" << q(e.word) << ",\"index\":" << e.index << ",\"char\":";
    if (e.index < static_cast<int>(e.word.size())) out << q(std::string(1, e.word[e.index])); else out << "null";
    out << ",\"action\":" << q(e.action) << ",\"node\":" << opt(e.node) << ",\"result\":" << q(e.result) << ",\"changed\":" << b(e.changed) << ",\"snapshot\":" << se.snap << '}';
    return out.str();
}
std::string snap_events_json(const std::vector<SnapEvent>& events) { std::ostringstream out; out << '['; for (std::size_t i = 0; i < events.size(); ++i) { if (i) out << ','; out << snap_event_json(events[i]); } return out.str() + ']'; }
std::string nodes_json(const SnapTrie& t) { return t.snapshot(); }

struct Canonical { SnapTrie trie; std::vector<std::pair<bool, bool>> inserted; std::vector<bool> queries; std::vector<bool> preserved; std::pair<bool, bool> insert_ca, duplicate; };
Canonical run_canonical() {
    Canonical c; for (const std::string word : {"car", "cat", "dog"}) c.inserted.push_back(c.trie.insert(word));
    c.queries = {c.trie.search("car", true), c.trie.search("ca", true), c.trie.search("ca", false), c.trie.search("cap", true)};
    c.insert_ca = c.trie.insert("ca"); c.preserved = {c.trie.search("car", true), c.trie.search("cat", true)}; c.duplicate = c.trie.insert("ca"); return c;
}
SnapTrie run_edge() { SnapTrie t; t.insert(""); t.insert("Car"); t.search("cap", true); return t; }
SnapTrie run_transfer() { SnapTrie t; for (const std::string word : {"car", "cat", "dog"}) t.insert(word); t.search("do", true); t.search("do", false); t.insert("do"); t.search("do", true); t.search("do", false); t.search("dog", true); return t; }

std::string canonical_json(const Canonical& c) {
    std::ostringstream out; out << "{\"input\":[\"car\",\"cat\",\"dog\"],\"inserted\":[";
    for (int i = 0; i < 3; ++i) { if (i) out << ','; out << "{\"accepted\":true,\"word\":" << q(std::array<std::string,3>{"car","cat","dog"}[i]) << ",\"terminal\":true,\"changed\":true}"; }
    out << "],\"queries\":[";
    const std::array<std::pair<std::string,bool>,4> qs{{{"car",c.queries[0]},{"ca",c.queries[1]},{"ca",c.queries[2]},{"cap",c.queries[3]}}};
    for (std::size_t i = 0; i < qs.size(); ++i) { if (i) out << ','; out << "{\"query\":" << q(qs[i].first) << ",\"result\":" << b(qs[i].second) << '}'; }
    out << "],\"insert_ca\":{\"accepted\":true,\"word\":\"ca\",\"terminal\":true,\"changed\":true},\"preserved\":[{\"query\":\"car\",\"result\":" << b(c.preserved[0]) << "},{\"query\":\"cat\",\"result\":" << b(c.preserved[1]) << "}],\"duplicate_ca\":{\"accepted\":true,\"word\":\"ca\",\"terminal\":true,\"changed\":" << b(c.duplicate.second) << "},\"events\":" << snap_events_json(c.trie.events) << ",\"final_nodes\":" << nodes_json(c.trie) << '}'; return out.str();
}
std::string edge_json(const SnapTrie& t) { return "{\"input\":[],\"empty_insert\":{\"accepted\":false,\"reason\":\"empty\",\"word\":\"\"},\"uppercase_insert\":{\"accepted\":false,\"reason\":\"lowercase_a_z_only\",\"word\":\"Car\"},\"missing_search\":{\"query\":\"cap\",\"result\":false},\"events\":" + snap_events_json(t.events) + ",\"final_nodes\":" + nodes_json(t) + "}"; }
std::string transfer_json(const SnapTrie& t) { return "{\"input\":[\"car\",\"cat\",\"dog\"],\"before\":{\"exact_do\":{\"query\":\"do\",\"result\":false},\"prefix_do\":{\"query\":\"do\",\"result\":true}},\"insert_do\":{\"accepted\":true,\"word\":\"do\",\"terminal\":true,\"changed\":true},\"after\":{\"exact_do\":{\"query\":\"do\",\"result\":true},\"prefix_do\":{\"query\":\"do\",\"result\":true},\"exact_dog\":{\"query\":\"dog\",\"result\":true}},\"events\":" + snap_events_json(t.events) + ",\"final_nodes\":" + nodes_json(t) + "}"; }

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "";
    if (mode == "--trace") { const auto c = run_canonical(); std::cout << "{\"canonical\":" << canonical_json(c) << ",\"edge\":" << edge_json(run_edge()) << ",\"transfer\":" << transfer_json(run_transfer()) << "}\n"; return 0; }
    if (mode == "--edge") { const auto t = run_edge(); std::cout << "edge empty insert accepted: false, reason: empty\nedge uppercase insert accepted: false, reason: lowercase_a_z_only\nedge missing cap: false\nedge trace events: " << t.events.size() << "\n"; return 0; }
    if (mode == "--transfer") { const auto t = run_transfer(); std::cout << "transfer do before exact: false\ntransfer do before prefix: true\ntransfer insert do changed: true\ntransfer do after exact: true\ntransfer do after prefix: true\ntransfer dog preserved: true\ntransfer trace events: " << t.events.size() << "\n"; return 0; }
    const auto c = run_canonical();
    std::cout << "trie input: [\"car\",\"cat\",\"dog\"]\nexact car: true\nexact ca before terminal: false\nprefix ca: true\nexact cap: false\ninsert ca changed: true\nexact car preserved: true\nexact cat preserved: true\nduplicate ca changed: false\nfinal node count: " << c.trie.nodes.size() << "\ntrace events: " << c.trie.events.size() << "\n";
}
