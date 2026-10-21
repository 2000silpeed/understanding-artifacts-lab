#include <algorithm>
#include <iostream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct Graph {
  std::vector<std::string> vertices;
  std::map<std::string, std::vector<std::string>> adjacency;
};

struct Event {
  int time = 0;
  std::string kind;
  std::optional<std::string> vertex;
  std::optional<std::string> from;
  std::optional<std::string> to;
  std::optional<int> value;
  std::vector<std::string> queue;
  std::map<std::string, int> indegree;
  std::vector<std::string> output;
  std::vector<std::string> processed;
};

struct Result {
  std::vector<std::string> vertices;
  std::vector<std::string> order;
  bool has_cycle = false;
  std::vector<std::string> remaining;
  std::map<std::string, int> final_indegree;
  std::vector<Event> events;
};

std::string quote(const std::string& value) {
  std::string out = "\"";
  for (char ch : value) {
    if (ch == '\\') out += "\\\\";
    else if (ch == '"') out += "\\\"";
    else if (ch == '\n') out += "\\n";
    else out += ch;
  }
  out += '"';
  return out;
}

std::string opt_string(const std::optional<std::string>& value) {
  return value ? quote(*value) : "null";
}
std::string opt_int(const std::optional<int>& value) {
  return value ? std::to_string(*value) : "null";
}
std::string boolean(bool value) { return value ? "true" : "false"; }

template <typename T>
std::string array_json(const std::vector<T>& values) {
  std::string out = "[";
  for (std::size_t i = 0; i < values.size(); ++i) {
    if (i) out += ',';
    out += quote(values[i]);
  }
  out += ']';
  return out;
}

std::string int_map_json(const std::map<std::string, int>& values) {
  std::string out = "{";
  bool first = true;
  for (const auto& [key, value] : values) {
    if (!first) out += ',';
    first = false;
    out += quote(key) + ':' + std::to_string(value);
  }
  out += '}';
  return out;
}

std::string graph_json(const Graph& graph) {
  std::string out = "{";
  bool first = true;
  for (const auto& vertex : graph.vertices) {
    if (!first) out += ',';
    first = false;
    out += quote(vertex) + ":[";
    const auto& edges = graph.adjacency.at(vertex);
    for (std::size_t i = 0; i < edges.size(); ++i) {
      if (i) out += ',';
      out += quote(edges[i]);
    }
    out += ']';
  }
  out += '}';
  return out;
}

void validate(const Graph& graph) {
  std::vector<std::pair<std::string, std::string>> seen;
  for (const auto& source : graph.vertices) {
    const auto& edges = graph.adjacency.at(source);
    for (const auto& dest : edges) {
      if (std::find(graph.vertices.begin(), graph.vertices.end(), dest) == graph.vertices.end()) {
        throw std::runtime_error("invalid endpoint");
      }
      const std::pair<std::string, std::string> edge{source, dest};
      if (std::find(seen.begin(), seen.end(), edge) != seen.end()) {
        throw std::runtime_error("duplicate edge rejected");
      }
      seen.push_back(edge);
    }
  }
}

Result kahn(const Graph& graph) {
  validate(graph);
  std::map<std::string, int> indegree;
  for (const auto& vertex : graph.vertices) indegree[vertex] = 0;
  for (const auto& source : graph.vertices) {
    (void)source;
    for (const auto& dest : graph.adjacency.at(source)) ++indegree[dest];
  }
  std::vector<std::string> queue;
  for (const auto& vertex : graph.vertices) if (indegree[vertex] == 0) queue.push_back(vertex);
  std::vector<std::string> output;
  std::vector<std::string> processed;
  std::vector<Event> events;
  const auto add_event = [&](const std::string& kind,
                             const std::optional<std::string>& vertex,
                             const std::optional<std::string>& source,
                             const std::optional<std::string>& dest,
                             const std::optional<int>& value) {
    Event event;
    event.time = static_cast<int>(events.size());
    event.kind = kind;
    event.vertex = vertex;
    event.from = source;
    event.to = dest;
    event.value = value;
    event.queue = queue;
    event.indegree = indegree;
    event.output = output;
    event.processed = processed;
    events.push_back(event);
  };
  add_event("init", std::nullopt, std::nullopt, std::nullopt, std::nullopt);
  while (!queue.empty()) {
    const std::string vertex = queue.front();
    queue.erase(queue.begin());
    output.push_back(vertex);
    processed.push_back(vertex);
    add_event("pop", vertex, std::nullopt, std::nullopt, std::nullopt);
    for (const auto& dest : graph.adjacency.at(vertex)) {
      --indegree[dest];
      add_event("decrement", std::nullopt, vertex, dest, indegree[dest]);
      if (indegree[dest] == 0) {
        queue.push_back(dest);
        add_event("enqueue", dest, std::nullopt, std::nullopt, std::nullopt);
      }
    }
  }
  Result result;
  result.vertices = graph.vertices;
  result.order = output;
  result.has_cycle = output.size() != graph.vertices.size();
  result.final_indegree = indegree;
  result.events = events;
  result.remaining = graph.vertices;
  result.remaining.erase(std::remove_if(result.remaining.begin(), result.remaining.end(), [&](const std::string& vertex) {
    return std::find(processed.begin(), processed.end(), vertex) != processed.end();
  }), result.remaining.end());
  add_event("done", std::nullopt, std::nullopt, std::nullopt,
            static_cast<int>(graph.vertices.size() - output.size()));
  result.events = events;
  return result;
}

Graph make_graph(const std::vector<std::string>& vertices,
                 const std::map<std::string, std::vector<std::string>>& adjacency) {
  return Graph{vertices, adjacency};
}
Graph default_graph() {
  return make_graph({"A", "B", "C", "D", "E", "F"},
                    {{"A", {"C"}}, {"B", {"C", "D"}}, {"C", {"E"}},
                     {"D", {"E"}}, {"E", {}}, {"F", {}}});
}
Graph transfer_graph() {
  return make_graph({"A", "B", "C", "D", "E", "F"},
                    {{"A", {"C"}}, {"B", {"C", "D"}}, {"C", {"E"}},
                     {"D", {"E"}}, {"E", {"B"}}, {"F", {}}});
}

std::string result_json(const Result& result) {
  std::string out = "{\"events\":[";
  for (std::size_t i = 0; i < result.events.size(); ++i) {
    if (i) out += ',';
    const Event& event = result.events[i];
    out += "{\"from\":" + opt_string(event.from)
        + ",\"indegree\":" + int_map_json(event.indegree)
        + ",\"kind\":" + quote(event.kind)
        + ",\"output\":" + array_json(event.output)
        + ",\"processed\":" + array_json(event.processed)
        + ",\"queue\":" + array_json(event.queue)
        + ",\"time\":" + std::to_string(event.time)
        + ",\"to\":" + opt_string(event.to)
        + ",\"value\":" + opt_int(event.value)
        + ",\"vertex\":" + opt_string(event.vertex) + '}';
  }
  out += "],\"final_indegree\":" + int_map_json(result.final_indegree)
      + ",\"has_cycle\":" + boolean(result.has_cycle)
      + ",\"order\":" + array_json(result.order)
      + ",\"remaining\":" + array_json(result.remaining)
      + ",\"vertices\":" + array_json(result.vertices) + '}';
  return out;
}

std::string summary_line(const std::string& name, const Result& result) {
  std::string line = name + ": order=" + (result.order.empty() ? "[]" : array_json(result.order));
  if (!result.order.empty()) {
    line = name + ": order=";
    for (std::size_t i = 0; i < result.order.size(); ++i) {
      if (i) line += "->";
      line += result.order[i];
    }
  }
  line += " cycle=" + boolean(result.has_cycle) + '\n';
  if (result.has_cycle) {
    line += name + ": remaining=";
    for (std::size_t i = 0; i < result.remaining.size(); ++i) {
      if (i) line += "->";
      line += result.remaining[i];
    }
    line += '\n';
  }
  return line;
}

std::string rejected_summary(const std::string& name, const std::string& message) {
  return name + ": rejected=" + message + '\n';
}

std::string trace_json() {
  const Graph base = default_graph();
  const Graph transfer = transfer_graph();
  const Graph empty = make_graph({}, {});
  const Graph single = make_graph({"X"}, {{"X", {}}});
  const Graph disconnected = make_graph({"A", "B", "C", "D", "E", "F"},
                                        {{"A", {"B"}}, {"B", {}}, {"C", {}}, {"D", {}}, {"E", {}}, {"F", {}}});
  const Graph self_loop = make_graph({"X"}, {{"X", {"X"}}});
  const Graph duplicate = make_graph({"A", "B"}, {{"A", {"B", "B"}}, {"B", {}}});
  const Graph invalid = make_graph({"A", "B"}, {{"A", {"Z"}}, {"B", {}}});
  const Result def = kahn(base);
  const Result trans = kahn(transfer);
  const Result emp = kahn(empty);
  const Result one = kahn(single);
  const Result disc = kahn(disconnected);
  const Result loop = kahn(self_loop);
  std::string out = "{\"contract\":{";
  out += "\"algorithm\":\"topological_sort_kahn\",\"complexity\":\"O(V + E)\","
      "\"cycle_rule\":\"cycle exists when processed output length is smaller than vertex count\","
      "\"default_adjacency\":" + graph_json(base)
      + ",\"dependency_meaning\":\"u -> v means u must be processed before v\","
      "\"duplicate_edges\":\"rejected before execution\","
      "\"graph_kind\":\"directed\","
      "\"instrumentation\":\"each event stores a full queue, indegree, output, and processed snapshot; this is separate from algorithm cost\","
      "\"queue_policy\":\"FIFO; initial zero-indegree vertices follow input order\","
      "\"self_loops\":\"accepted by validation and make a cycle\","
      "\"transfer_adjacency\":" + graph_json(transfer)
      + ",\"vertices\":[\"A\",\"B\",\"C\",\"D\",\"E\",\"F\"],"
      "\"zero_indegree\":\"indegree counts remaining incoming edges\"},\"scenarios\":{";
  out += "\"default\":" + result_json(def) + ",\"disconnected\":" + result_json(disc)
      + ",\"duplicate\":{\"accepted\":false,\"error\":\"duplicate edge rejected\"}"
      + ",\"empty\":" + result_json(emp)
      + ",\"invalid_endpoint\":{\"accepted\":false,\"error\":\"invalid endpoint\"}"
      + ",\"self_loop\":" + result_json(loop)
      + ",\"single\":" + result_json(one)
      + ",\"transfer\":" + result_json(trans) + "}}";
  (void)invalid;
  return out;
}

int main(int argc, char** argv) {
  try {
    bool trace = false;
    bool edge = false;
    bool transfer = false;
    for (int i = 1; i < argc; ++i) {
      trace = trace || std::string(argv[i]) == "--trace";
      edge = edge || std::string(argv[i]) == "--edge";
      transfer = transfer || std::string(argv[i]) == "--transfer";
    }
    if (trace) {
      std::cout << trace_json() << '\n';
      return 0;
    }
    if (edge) {
      const Result empty = kahn(make_graph({}, {}));
      const Result single = kahn(make_graph({"X"}, {{"X", {}}}));
      const Result disconnected = kahn(make_graph({"A", "B", "C", "D", "E", "F"},
          {{"A", {"B"}}, {"B", {}}, {"C", {}}, {"D", {}}, {"E", {}}, {"F", {}}}));
      const Result loop = kahn(make_graph({"X"}, {{"X", {"X"}}}));
      std::cout << summary_line("empty", empty) << summary_line("single", single)
                << summary_line("disconnected", disconnected) << summary_line("self_loop", loop)
                << rejected_summary("duplicate", "duplicate edge rejected")
                << rejected_summary("invalid_endpoint", "invalid endpoint");
      return 0;
    }
    if (transfer) {
      std::cout << summary_line("transfer", kahn(transfer_graph()));
      return 0;
    }
    std::cout << summary_line("default", kahn(default_graph()));
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 2;
  }
}
