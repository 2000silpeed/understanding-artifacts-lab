// C++17 executable linked-list contract. The trace is computed by pointer operations.
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <memory>

struct Node {
    int value;
    Node* next = nullptr;
};

class SinglyLinkedList {
    // Ownership is separate from the logical link-update count.
    // Unlinked nodes remain owned until destruction; no memory is leaked.
    std::vector<std::unique_ptr<Node>> owned;
    Node* make_node(int value) {
        owned.push_back(std::make_unique<Node>(Node{value, nullptr}));
        return owned.back().get();
    }
public:
    Node* head = nullptr;
    Node* tail = nullptr;
    explicit SinglyLinkedList(const std::vector<int>& values = {}) {
        for (int value : values) append(value);
    }
    int append(int value) {
        Node* node = make_node(value);
        if (!head) { head = tail = node; return 0; }
        tail->next = node;
        tail = node;
        return 1;
    }
    std::vector<int> values() const {
        std::vector<int> result;
        for (Node* current = head; current; current = current->next)
            result.push_back(current->value);
        return result;
    }
    std::pair<int,int> index_at(int index) const {
        if (index < 0) throw std::out_of_range("negative index");
        Node* current = head;
        int steps = 0;
        while (current && steps < index) { current = current->next; ++steps; }
        if (!current) throw std::out_of_range("index out of range");
        return {current->value, steps};
    }
    std::pair<int,int> find(int value) const {
        int position = 0;
        for (Node* current = head; current; current = current->next, ++position)
            if (current->value == value) return {position, position};
        return {-1, position};
    }
    Node* node_at(int index) const {
        if (index < 0) throw std::out_of_range("negative index");
        Node* current = head;
        for (int i = 0; i < index && current; ++i) current = current->next;
        if (!current) throw std::out_of_range("index out of range");
        return current;
    }
    int insert_after(Node* predecessor, int value) {
        if (!predecessor) throw std::out_of_range("missing predecessor");
        Node* new_node = make_node(value);
        new_node->next = predecessor->next;
        predecessor->next = new_node;
        if (tail == predecessor) tail = new_node;
        return 2;
    }
    std::pair<int,int> delete_after(Node* predecessor) {
        if (!predecessor || !predecessor->next) throw std::out_of_range("no successor");
        Node* target = predecessor->next;
        predecessor->next = target->next;
        if (tail == target) tail = predecessor;
        return {target->value, 1};
    }
};

std::string arrow(const std::vector<int>& values) {
    std::ostringstream out;
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) out << " -> ";
        out << values[i];
    }
    out << " -> null";
    return out.str();
}

struct Trace {
    std::vector<int> initial;
    int index_value;
    int index_steps;
    int lookup_position;
    int lookup_steps;
    int insert_links;
    std::vector<int> after_insert;
    int inserted_position;
    int inserted_steps;
    int removed;
    int delete_links;
    std::vector<int> after_delete;
    int empty_length;
    int append_links;
    std::vector<int> appended_state;
};

Trace make_trace() {
    SinglyLinkedList linked({10, 20, 30, 40});
    const auto index = linked.index_at(2);
    const auto lookup = linked.find(40);
    Node* const predecessor = linked.node_at(1);
    Trace trace{};
    trace.initial = linked.values();
    trace.index_value = index.first;
    trace.index_steps = index.second;
    trace.lookup_position = lookup.first;
    trace.lookup_steps = lookup.second;
    trace.insert_links = linked.insert_after(predecessor, 25);
    trace.after_insert = linked.values();
    const auto inserted = linked.find(25);
    trace.inserted_position = inserted.first;
    trace.inserted_steps = inserted.second;
    const auto deleted = linked.delete_after(predecessor);
    trace.removed = deleted.first;
    trace.delete_links = deleted.second;
    trace.after_delete = linked.values();
    SinglyLinkedList empty;
    trace.empty_length = static_cast<int>(empty.values().size());
    trace.append_links = empty.append(50);
    trace.appended_state = empty.values();
    return trace;
}

std::string json_array(const std::vector<int>& values) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) { if (i) out << ','; out << values[i]; }
    out << ']';
    return out.str();
}

std::string trace_json(const Trace& t) {
    std::ostringstream out;
    out << "{"
        << "\"boundaries\":{";
    out << "\"append_link_updates\":" << t.append_links << ",\"append_value\":50,\"empty_head\":null,\"empty_length\":" << t.empty_length << ",\"state\":" << json_array(t.appended_state) << ",\"tail\":50},";
    out << "\"costs\":{\"delete_requires_predecessor\":true,\"index_access\":\"O(n)\",\"known_predecessor_insert\":\"O(1)\",\"position_search\":\"O(n)\"},";
    out << "\"delete_after\":{";
    out << "\"link_updates\":" << t.delete_links << ",\"predecessor\":20,\"removed\":" << t.removed << ",\"state\":" << json_array(t.after_delete) << "},";
    out << "\"index_access\":{";
    out << "\"index\":2,\"steps\":" << t.index_steps << ",\"value\":" << t.index_value << ",\"visited\":[10,20,30]},";
    out << "\"initial\":" << json_array(t.initial) << ",";
    out << "\"insert_after\":{";
    out << "\"link_updates\":" << t.insert_links << ",\"predecessor\":20,\"state\":" << json_array(t.after_insert) << ",\"value\":25},";
    out << "\"lookup\":{\"position\":" << t.lookup_position << ",\"steps\":" << t.lookup_steps << ",\"value\":40,\"visited\":[10,20,30,40]},";
    out << "\"lookup_after_insert\":{\"position\":" << t.inserted_position << ",\"steps\":" << t.inserted_steps << ",\"value\":25}"
        << "}";
    return out.str();
}

std::string stdout_text(const Trace& t) {
    std::ostringstream out;
    out << "LIST initial=" << arrow(t.initial) << '\n';
    out << "INDEX index=2 value=" << t.index_value << " visited=3 steps=" << t.index_steps << '\n';
    out << "LOOKUP value=40 position=" << t.lookup_position << " visited=4 steps=" << t.lookup_steps << '\n';
    out << "INSERT_AFTER predecessor=20 value=25 link_updates=" << t.insert_links << " state=" << arrow(t.after_insert) << '\n';
    out << "LOOKUP_AFTER value=25 position=" << t.inserted_position << " steps=" << t.inserted_steps << '\n';
    out << "DELETE_AFTER predecessor=20 removed=" << t.removed << " link_updates=" << t.delete_links << " state=" << arrow(t.after_delete) << '\n';
    out << "EMPTY head=null length=" << t.empty_length << '\n';
    out << "APPEND value=50 tail=50 link_updates=" << t.append_links << " state=" << arrow(t.appended_state) << '\n';
    out << "COST index_access=O(n) known_predecessor_insert=O(1) position_search=O(n) delete_requires_predecessor=true\n";
    return out.str();
}

int main(int argc, char** argv) {
    const Trace trace = make_trace();
    if (argc > 1 && std::string(argv[1]) == "--trace") std::cout << trace_json(trace) << '\n';
    else std::cout << stdout_text(trace);
}
