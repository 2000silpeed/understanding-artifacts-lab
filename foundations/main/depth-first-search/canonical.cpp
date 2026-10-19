#include <algorithm>
#include <iostream>
#include <set>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

using Pair = std::pair<std::string, std::string>;
using Graph = std::vector<std::pair<std::string, std::vector<std::string>>>;

const Graph MAIN = {
    {"A", {"B", "C"}},
    {"B", {"A", "D", "E"}},
    {"C", {"A", "F"}},
    {"D", {"B"}},
    {"E", {"B", "F"}},
    {"F", {"C", "E"}},
};
const Graph ALTERNATE = {
    {"P", {"Q", "R"}},
    {"Q", {"P", "S"}},
    {"R", {"P"}},
    {"S", {"Q"}},
};

struct Event {
    std::string kind;
    std::string vertex;
    std::string from;
    std::string to;
    std::string reason;
    bool has_vertex = false;
    bool has_from = false;
    bool has_to = false;
    bool has_reason = false;
    bool target = false;
    bool has_target = false;
    std::vector<std::string> stack;
    std::vector<std::string> visited;
    std::vector<Pair> parent;
};

struct Scenario {
    std::string start;
    bool has_target = false;
    std::string target;
    std::vector<std::string> order;
    bool found = false;
    std::vector<Pair> parent;
    std::vector<Event> events;
};

std::string quote(const std::string& value) {
    std::ostringstream out;
    out << '"';
    for (const char c : value) {
        if (c == '"' || c == '\\') out << '\\';
        out << c;
    }
    out << '"';
    return out.str();
}

template <typename T>
std::string strings(const std::vector<T>& values) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) out << ',';
        out << quote(values[i]);
    }
    out << ']';
    return out.str();
}

std::string parents(const std::vector<Pair>& values) {
    std::ostringstream out;
    out << '{';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) out << ',';
        out << quote(values[i].first) << ':';
        if (values[i].second.empty()) out << "null";
        else out << quote(values[i].second);
    }
    out << '}';
    return out.str();
}

const std::vector<std::string>* neighbors(const Graph& graph, const std::string& vertex) {
    for (const auto& entry : graph) {
        if (entry.first == vertex) return &entry.second;
    }
    return nullptr;
}

bool contains(const std::set<std::string>& values, const std::string& value) {
    return values.find(value) != values.end();
}

Event base_event(const std::string& kind, const std::vector<std::string>& stack,
                 const std::vector<std::string>& visited, const std::vector<Pair>& parent) {
    Event event;
    event.kind = kind;
    event.stack = stack;
    event.visited = visited;
    event.parent = parent;
    return event;
}

Scenario dfs(const Graph& graph, const std::string& start, const std::string& target = "") {
    Scenario result;
    result.start = start;
    result.has_target = !target.empty();
    result.target = target;
    std::vector<std::string> stack;
    std::vector<std::string> visited;
    std::set<std::string> seen;
    std::vector<Pair> parent;

    auto add_push = [&](const std::string& vertex, const std::string& from, const std::string& reason) {
        Event event = base_event("push", stack, visited, parent);
        event.vertex = vertex;
        event.has_vertex = true;
        event.from = from;
        event.has_from = true;
        event.reason = reason;
        event.has_reason = true;
        result.events.push_back(event);
    };

    if (neighbors(graph, start) == nullptr) return result;
    seen.insert(start);
    visited.push_back(start);
    parent.emplace_back(start, "");
    stack.push_back(start);
    add_push(start, "", "start");

    while (!stack.empty()) {
        const std::string vertex = stack.back();
        stack.pop_back();
        result.order.push_back(vertex);
        Event pop = base_event("pop", stack, visited, parent);
        pop.vertex = vertex;
        pop.has_vertex = true;
        pop.target = result.has_target && vertex == target;
        pop.has_target = true;
        result.events.push_back(pop);
        if (result.has_target && vertex == target) {
            Event found = base_event("target_found", stack, visited, parent);
            found.vertex = vertex;
            found.has_vertex = true;
            result.events.push_back(found);
            break;
        }
        const auto* list = neighbors(graph, vertex);
        for (auto it = list->rbegin(); it != list->rend(); ++it) {
            const std::string& next = *it;
            if (contains(seen, next)) {
                Event skip = base_event("skip", stack, visited, parent);
                skip.from = vertex;
                skip.has_from = true;
                skip.to = next;
                skip.has_to = true;
                skip.reason = "visited";
                skip.has_reason = true;
                result.events.push_back(skip);
                continue;
            }
            seen.insert(next);
            visited.push_back(next);
            parent.emplace_back(next, vertex);
            stack.push_back(next);
            add_push(next, vertex, "new");
        }
    }
    result.found = result.has_target && !result.order.empty() && result.order.back() == target;
    result.parent = parent;
    return result;
}

std::string graph_json(const Graph& graph) {
    std::ostringstream out;
    out << '{';
    for (std::size_t i = 0; i < graph.size(); ++i) {
        if (i) out << ',';
        out << quote(graph[i].first) << ':' << strings(graph[i].second);
    }
    out << '}';
    return out.str();
}

std::string event_json(const Event& event) {
    std::ostringstream out;
    out << '{' << "\"kind\":" << quote(event.kind);
    if (event.has_vertex) out << ",\"vertex\":" << quote(event.vertex);
    if (event.has_from) {
        out << ",\"from_vertex\":";
        if (event.from.empty()) out << "null";
        else out << quote(event.from);
    }
    if (event.has_to) out << ",\"to\":" << quote(event.to);
    if (event.has_reason) out << ",\"reason\":" << quote(event.reason);
    if (event.has_target) out << ",\"target\":" << (event.target ? "true" : "false");
    out << ",\"stack\":" << strings(event.stack);
    out << ",\"visited\":" << strings(event.visited);
    out << ",\"parent\":" << parents(event.parent) << '}';
    return out.str();
}

std::string scenario_json(const Scenario& scenario) {
    std::ostringstream out;
    out << '{' << "\"start\":" << quote(scenario.start) << ",\"target\":";
    if (scenario.has_target) out << quote(scenario.target);
    else out << "null";
    out << ",\"order\":" << strings(scenario.order);
    out << ",\"found\":" << (scenario.found ? "true" : "false");
    out << ",\"parent\":" << parents(scenario.parent) << ",\"events\":[";
    for (std::size_t i = 0; i < scenario.events.size(); ++i) {
        if (i) out << ',';
        out << event_json(scenario.events[i]);
    }
    out << "]}";
    return out.str();
}

std::string trace_json() {
    const Scenario full = dfs(MAIN, "A");
    const Scenario early = dfs(MAIN, "A", "F");
    const Scenario unreachable = dfs(MAIN, "A", "Z");
    const Scenario cycle = dfs(MAIN, "E");
    const Scenario alternate = dfs(ALTERNATE, "P", "S");
    std::ostringstream out;
    out << "{\"contract\":{";
    out << "\"graph\":\"fixed adjacency list\",";
    out << "\"adjacency\":" << graph_json(MAIN) << ',';
    out << "\"alternate_adjacency\":" << graph_json(ALTERNATE) << ',';
    out << "\"stack_orientation\":\"bottom_to_top_left_to_right\",";
    out << "\"stack_top\":\"rightmost_item\",";
    out << "\"neighbor_scan\":\"reverse_listed_order\",";
    out << "\"visited_mark\":\"at_push\",";
    out << "\"target_boundary\":\"success_on_pop\",";
    out << "\"duplicate_push\":false},\"scenarios\":{";
    out << "\"full\":" << scenario_json(full) << ',';
    out << "\"early_target\":" << scenario_json(early) << ',';
    out << "\"unreachable\":" << scenario_json(unreachable) << ',';
    out << "\"cycle\":" << scenario_json(cycle) << ',';
    out << "\"alternate\":" << scenario_json(alternate) << "}}";
    return out.str();
}

std::string order_text(const std::vector<std::string>& order) {
    if (order.empty()) return "(empty)";
    std::ostringstream out;
    for (std::size_t i = 0; i < order.size(); ++i) {
        if (i) out << ',';
        out << order[i];
    }
    return out.str();
}

int main(int argc, char** argv) {
    const bool emit_trace = argc > 1 && std::string(argv[1]) == "--trace";
    if (emit_trace) {
        std::cout << trace_json() << '\n';
        return 0;
    }
    const Scenario full = dfs(MAIN, "A");
    const Scenario early = dfs(MAIN, "A", "F");
    const Scenario unreachable = dfs(MAIN, "A", "Z");
    const Scenario cycle = dfs(MAIN, "E");
    const Scenario alternate = dfs(ALTERNATE, "P", "S");
    std::cout << "DFS explicit-stack contract\n";
    std::cout << "full order: " << order_text(full.order) << '\n';
    std::cout << "early target F order: " << order_text(early.order) << '\n';
    std::cout << "unreachable Z order: " << order_text(unreachable.order) << '\n';
    std::cout << "cycle from E order: " << order_text(cycle.order) << '\n';
    std::cout << "alternate target S order: " << order_text(alternate.order) << '\n';
    std::cout << "full events: " << full.events.size() << '\n';
    return 0;
}
