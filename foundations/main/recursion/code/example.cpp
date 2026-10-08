#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int MAX_N = 8;

void check(int n) {
  if (n < 0 || n > MAX_N) throw std::invalid_argument("n must be between 0 and 8");
}

int sum_to(int n) {
  check(n);
  if (n == 0) return 0;
  return n + sum_to(n - 1);
}

int iterative_sum_to(int n) {
  check(n);
  int total = 0;
  for (int value = 0; value <= n; ++value) total += value;
  return total;
}

struct TraceCase {
  int input;
  std::vector<int> calls;
  std::vector<std::pair<int, int>> returns;
  int result;
};

int visit(int value, TraceCase& trace) {
  trace.calls.push_back(value);
  if (value == 0) {
    trace.returns.push_back({0, 0});
    return 0;
  }
  const int result = value + visit(value - 1, trace);
  trace.returns.push_back({value, result});
  return result;
}

TraceCase trace_case(int n) {
  check(n);
  TraceCase trace{n, {}, {}, 0};
  trace.result = visit(n, trace);
  return trace;
}

void emit_case(std::ostringstream& out, const TraceCase& trace) {
  out << "{\"input\":" << trace.input << ",\"calls\":[";
  for (std::size_t i = 0; i < trace.calls.size(); ++i) {
    if (i) out << ',';
    out << trace.calls[i];
  }
  out << "],\"returns\":[";
  for (std::size_t i = 0; i < trace.returns.size(); ++i) {
    if (i) out << ',';
    out << "{\"n\":" << trace.returns[i].first << ",\"value\":" << trace.returns[i].second << "}";
  }
  out << "],\"result\":" << trace.result
      << ",\"call_count\":" << trace.calls.size()
      << ",\"max_depth\":" << trace.calls.size()
      << ",\"shrinks\":true}";
}

int main(int argc, char** argv) {
  if (argc > 1 && std::string(argv[1]) == "--trace") {
    const auto n0 = trace_case(0);
    const auto n3 = trace_case(3);
    const auto n4 = trace_case(4);
    std::ostringstream out;
    out << "{\"max_n\":" << MAX_N << ",\"cases\":{";
    out << "\"n0\":";
    emit_case(out, n0);
    out << ",\"n3\":";
    emit_case(out, n3);
    out << ",\"n4\":";
    emit_case(out, n4);
    out << "}}";
    std::cout << out.str() << '\n';
    return 0;
  }
  std::cout << "sum_to(4) = 4 + 3 + 2 + 1 + 0 = " << sum_to(4) << '\n';
  std::cout << "sum_to(0) = " << sum_to(0) << '\n';
  std::cout << "iterative_sum_to(4) = " << iterative_sum_to(4) << '\n';
  std::cout << "bounded input: 0 <= n <= 8\n";
  try {
    sum_to(-1);
  } catch (const std::invalid_argument&) {
    std::cout << "negative input rejected: -1\n";
  }
}
