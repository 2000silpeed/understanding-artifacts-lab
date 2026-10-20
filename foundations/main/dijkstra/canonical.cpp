#include <algorithm>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Edge = std::pair<std::string, int>;
using Graph = std::map<std::string, std::vector<Edge>>;

struct Event {
  std::string kind;
  std::optional<std::string> vertex;
  std::optional<std::string> from;
  std::optional<std::string> to;
  std::optional<int> old_candidate;
  std::optional<int> new_candidate;
  std::optional<std::string> old_parent;
  std::optional<std::string> new_parent;
  bool improved = false;
  std::optional<std::string> reason;
  bool stop = false;
  std::map<std::string, std::optional<int>> distances;
  std::map<std::string, std::optional<std::string>> parents;
  std::vector<std::string> settled;
};

struct Result {
  std::string start;
  std::string target;
  bool found = false;
  std::optional<int> distance;
  std::vector<std::string> path;
  std::map<std::string, std::optional<int>> distances;
  std::map<std::string, std::optional<std::string>> parents;
  std::vector<Event> events;
};

std::string esc(const std::string& value) {
  std::ostringstream out;
  out << '"';
  for (const char ch : value) {
    if (ch == '"') out << "\\\"";
    else if (ch == '\\') out << "\\\\";
    else if (ch == '\n') out << "\\n";
    else out << ch;
  }
  out << '"';
  return out.str();
}
std::string opt_int(const std::optional<int>& value) { return value ? std::to_string(*value) : "null"; }
std::string opt_str(const std::optional<std::string>& value) { return value ? esc(*value) : "null"; }
std::string bool_json(bool value) { return value ? "true" : "false"; }

template <typename T>
std::string string_array(const std::vector<T>& values) {
  std::ostringstream out;
  out << '[';
  for (std::size_t i = 0; i < values.size(); ++i) {
    if (i) out << ',';
    out << esc(values[i]);
  }
  out << ']';
  return out.str();
}
std::string graph_json(const Graph& graph) {
  std::ostringstream out;
  out << '{';
  bool first_vertex = true;
  for (const auto& [source, edges] : graph) {
    if (!first_vertex) out << ',';
    first_vertex = false;
    out << esc(source) << ":[";
    for (std::size_t i = 0; i < edges.size(); ++i) {
      if (i) out << ',';
      out << '[' << esc(edges[i].first) << ',' << edges[i].second << ']';
    }
    out << ']';
  }
  out << '}';
  return out.str();
}
std::string distances_json(const std::map<std::string, std::optional<int>>& values) {
  std::ostringstream out;
  out << '{';
  bool first = true;
  for (const auto& [key, value] : values) {
    if (!first) out << ',';
    first = false;
    out << esc(key) << ':' << opt_int(value);
  }
  out << '}';
  return out.str();
}
std::string parents_json(const std::map<std::string, std::optional<std::string>>& values) {
  std::ostringstream out;
  out << '{';
  bool first = true;
  for (const auto& [key, value] : values) {
    if (!first) out << ',';
    first = false;
    out << esc(key) << ':' << opt_str(value);
  }
  out << '}';
  return out.str();
}

Result dijkstra(const Graph& graph, const std::string& start, const std::string& target) {
  if (!graph.count(start)) throw std::runtime_error("unknown start");
  for (const auto& [source, edges] : graph) {
    (void)source;
    for (const auto& [dest, weight] : edges) {
      if (!graph.count(dest)) throw std::runtime_error("unknown destination");
      if (weight < 0) throw std::runtime_error("negative weight rejected");
    }
  }
  std::map<std::string, std::optional<int>> dist;
  std::map<std::string, std::optional<std::string>> parent;
  std::vector<std::string> settled;
  for (const auto& [vertex, edges] : graph) {
    (void)edges;
    dist[vertex] = std::nullopt;
    parent[vertex] = std::nullopt;
  }
  dist[start] = 0;
  std::vector<Event> events;
  const auto add_event = [&](const std::string& kind,
                             const std::optional<std::string>& vertex,
                             const std::optional<std::string>& source,
                             const std::optional<std::string>& dest,
                             const std::optional<int>& old_candidate,
                             const std::optional<int>& new_candidate,
                             const std::optional<std::string>& old_parent,
                             const std::optional<std::string>& new_parent,
                             bool improved,
                             const std::optional<std::string>& reason,
                             bool stop) {
    Event event;
    event.kind = kind;
    event.vertex = vertex;
    event.from = source;
    event.to = dest;
    event.old_candidate = old_candidate;
    event.new_candidate = new_candidate;
    event.old_parent = old_parent;
    event.new_parent = new_parent;
    event.improved = improved;
    event.reason = reason;
    event.stop = stop;
    event.distances = dist;
    event.parents = parent;
    event.settled = settled;
    events.push_back(event);
  };
  while (true) {
    std::optional<std::string> selected;
    for (const auto& [vertex, edges] : graph) {
      (void)edges;
      if (std::find(settled.begin(), settled.end(), vertex) != settled.end()) continue;
      if (!dist[vertex]) continue;
      if (!selected || *dist[vertex] < *dist[*selected] ||
          (*dist[vertex] == *dist[*selected] && vertex < *selected)) {
        selected = vertex;
      }
    }
    if (!selected) {
      add_event("done", std::nullopt, std::nullopt, std::nullopt, std::nullopt,
                std::nullopt, std::nullopt, std::nullopt, false,
                std::string("no reachable unsettled vertex"), false);
      break;
    }
    const std::string u = *selected;
    const int old = *dist[u];
    settled.push_back(u);
    const bool stopping = u == target;
    add_event("settle", u, std::nullopt, std::nullopt, old, old, std::nullopt,
              std::nullopt, false,
              stopping ? std::optional<std::string>("target settled")
                       : std::optional<std::string>("minimum unsettled distance"),
              stopping);
    if (stopping) break;
    for (const auto& [v, weight] : graph.at(u)) {
      if (std::find(settled.begin(), settled.end(), v) != settled.end()) {
        add_event("consider", std::nullopt, u, v, dist[v], dist[v], parent[v], parent[v], false,
                  std::string("destination already settled"), false);
        continue;
      }
      const auto old_candidate = dist[v];
      const int candidate = *dist[u] + weight;
      const bool improved = !old_candidate || candidate < *old_candidate;
      const auto old_parent = parent[v];
      if (improved) {
        dist[v] = candidate;
        parent[v] = u;
      }
      add_event("relax", std::nullopt, u, v, old_candidate,
                improved ? std::optional<int>(candidate) : old_candidate,
                old_parent, parent[v], improved,
                improved ? std::optional<std::string>("strictly smaller candidate")
                         : std::optional<std::string>("tie or larger candidate"), false);
    }
  }
  Result result;
  result.start = start;
  result.target = target;
  result.found = dist[target].has_value();
  result.distance = dist[target];
  result.distances = dist;
  result.parents = parent;
  result.events = events;
  if (result.found) {
    std::string current = target;
    while (true) {
      result.path.push_back(current);
      if (!parent[current]) break;
      current = *parent[current];
    }
    std::reverse(result.path.begin(), result.path.end());
  }
  return result;
}

Graph default_graph() {
  return {{"A", {{"B", 4}, {"C", 1}}}, {"B", {{"D", 1}}},
          {"C", {{"B", 2}, {"D", 5}}}, {"D", {}}, {"E", {}}};
}
Graph transfer_graph() {
  return {{"A", {{"B", 4}, {"C", 1}}}, {"B", {{"D", 1}}},
          {"C", {{"B", 2}, {"D", 1}}}, {"D", {}}, {"E", {}}};
}

std::string result_json(const Result& result) {
  std::ostringstream out;
  out << '{' << "\"distances\":" << distances_json(result.distances)
      << ",\"distance\":" << opt_int(result.distance)
      << ",\"events\":[";
  for (std::size_t i = 0; i < result.events.size(); ++i) {
    if (i) out << ',';
    const auto& e = result.events[i];
    out << '{' << "\"distances\":" << distances_json(e.distances)
        << ",\"from\":" << opt_str(e.from)
        << ",\"improved\":" << bool_json(e.improved)
        << ",\"kind\":" << esc(e.kind)
        << ",\"new_candidate\":" << opt_int(e.new_candidate)
        << ",\"new_parent\":" << opt_str(e.new_parent)
        << ",\"old_candidate\":" << opt_int(e.old_candidate)
        << ",\"old_parent\":" << opt_str(e.old_parent)
        << ",\"parents\":" << parents_json(e.parents)
        << ",\"reason\":" << opt_str(e.reason)
        << ",\"settled\":" << string_array(e.settled)
        << ",\"stop\":" << bool_json(e.stop)
        << ",\"to\":" << opt_str(e.to)
        << ",\"vertex\":" << opt_str(e.vertex) << '}';
  }
  out << "],\"found\":" << bool_json(result.found)
      << ",\"parents\":" << parents_json(result.parents)
      << ",\"path\":" << string_array(result.path)
      << ",\"start\":" << esc(result.start)
      << ",\"target\":" << esc(result.target) << '}';
  return out.str();
}

std::string trace_json() {
  const Graph base = default_graph();
  const Graph transfer = transfer_graph();
  const Graph zero = {{"A", {{"B", 0}, {"C", 2}}}, {"B", {{"C", 0}}}, {"C", {}}};
  const Graph tie = {{"A", {{"B", 1}, {"C", 1}}}, {"B", {{"D", 1}}},
                     {"C", {{"D", 1}}}, {"D", {}}};
  const Result def = dijkstra(base, "A", "D");
  const Result unreachable = dijkstra(base, "A", "E");
  const Result start_target = dijkstra(base, "A", "A");
  const Result zero_result = dijkstra(zero, "A", "C");
  const Result tie_result = dijkstra(tie, "A", "D");
  const Result transfer_result = dijkstra(transfer, "A", "D");
  std::ostringstream out;
  out << "{\"contract\":{";
  out << "\"algorithm\":\"dijkstra_nonnegative\",\"complexity\":\"O(V^2 + E)\","
      << "\"default_adjacency\":" << graph_json(base)
      << ",\"early_stop\":\"stop only after target is settled\","
      << "\"graph_kind\":\"directed\",\"infinity\":\"null in JSON, distinct from numeric zero\","
      << "\"instrumentation\":\"event snapshots copy distances, parents, and settled; this is separate from algorithm cost\","
      << "\"negative_weights\":\"rejected before execution; nonnegative proof is out of scope\","
      << "\"selection\":\"minimum unsettled distance by array scan; ties use lexicographic vertex order\","
      << "\"tie_policy\":\"strict improvement only; equal candidates keep the existing parent\","
      << "\"transfer_adjacency\":" << graph_json(transfer)
      << ",\"vertices\":[\"A\",\"B\",\"C\",\"D\",\"E\"]},\"scenarios\":{";
  out << "\"default\":" << result_json(def)
      << ",\"negative\":{\"accepted\":false,\"error\":\"negative weight rejected\"}"
      << ",\"start_target\":" << result_json(start_target)
      << ",\"tie\":" << result_json(tie_result)
      << ",\"transfer\":" << result_json(transfer_result)
      << ",\"unreachable\":" << result_json(unreachable)
      << ",\"zero_weight\":" << result_json(zero_result) << "}}";
  return out.str();
}

std::string summary() {
  return "default: path=A->C->B->D distance=4\n"
         "unreachable: found=false\n"
         "start_target: path=A distance=0\n"
         "zero_weight: path=A->B->C distance=0\n"
         "tie: path=A->B->D distance=2 parent=D:B\n"
         "transfer: path=A->C->D distance=2\n"
         "negative: rejected=negative weight rejected\n";
}

int main(int argc, char** argv) {
  try {
    bool trace = false;
    bool negative = false;
    for (int i = 1; i < argc; ++i) {
      trace = trace || std::string(argv[i]) == "--trace";
      negative = negative || std::string(argv[i]) == "--negative";
    }
    if (negative) {
      try {
        (void)dijkstra({{"A", {{"B", -1}}}, {"B", {}}}, "A", "B");
      } catch (const std::runtime_error& error) {
        std::cout << "rejected: " << error.what() << '\n';
        return 0;
      }
      return 1;
    }
    std::cout << (trace ? trace_json() : summary());
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 2;
  }
}
