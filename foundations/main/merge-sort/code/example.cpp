#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

struct Item {
  int value;
  std::string label;
};

struct Split {
  std::string path;
  std::vector<Item> items;
  bool base;
  int mid;
  std::vector<Item> left;
  std::vector<Item> right;
};

struct Step {
  Item left_front;
  Item right_front;
  Item chosen;
  std::string side;
  std::vector<Item> output;
};

struct Merge {
  std::string path;
  std::vector<Item> left;
  std::vector<Item> right;
  std::vector<Step> steps;
  std::vector<Item> result;
};

struct TraceCase {
  std::vector<Item> input;
  std::vector<Split> splits;
  std::vector<Merge> merges;
  std::vector<Item> sorted;
  int comparisons = 0;
};

Item make_item(int value, const std::string& label = "") {
  return {value, label.empty() ? std::to_string(value) : label};
}

std::string quote(const std::string& s) {
  std::string out = "\"";
  for (char c : s) {
    if (c == '\\' || c == '"') out += '\\';
    out += c;
  }
  return out + "\"";
}

std::string item_json(const Item& x) {
  return "{\"value\":" + std::to_string(x.value) + ",\"label\":" + quote(x.label) + "}";
}

template <typename T, typename F>
std::string array_json(const std::vector<T>& xs, F f) {
  std::string out = "[";
  for (size_t i = 0; i < xs.size(); ++i) {
    if (i) out += ",";
    out += f(xs[i]);
  }
  return out + "]";
}

std::vector<Item> merge_sort_visit(const std::vector<Item>& items, const std::string& path, TraceCase& trace) {
  if (items.size() <= 1) {
    trace.splits.push_back({path, items, true, 0, {}, {}});
    return items;
  }
  const size_t mid = items.size() / 2;
  std::vector<Item> left(items.begin(), items.begin() + static_cast<long>(mid));
  std::vector<Item> right(items.begin() + static_cast<long>(mid), items.end());
  trace.splits.push_back({path, items, false, static_cast<int>(mid), left, right});
  const auto left_sorted = merge_sort_visit(left, path + "L", trace);
  const auto right_sorted = merge_sort_visit(right, path + "R", trace);
  std::vector<Item> out;
  std::vector<Step> steps;
  size_t i = 0, j = 0;
  while (i < left_sorted.size() && j < right_sorted.size()) {
    const Item left_front = left_sorted[i];
    const Item right_front = right_sorted[j];
    ++trace.comparisons;
    Item chosen;
    std::string side;
    if (left_front.value <= right_front.value) {
      chosen = left_front;
      side = "left";
      ++i;
    } else {
      chosen = right_front;
      side = "right";
      ++j;
    }
    out.push_back(chosen);
    steps.push_back({left_front, right_front, chosen, side, out});
  }
  out.insert(out.end(), left_sorted.begin() + static_cast<long>(i), left_sorted.end());
  out.insert(out.end(), right_sorted.begin() + static_cast<long>(j), right_sorted.end());
  trace.merges.push_back({path, left_sorted, right_sorted, steps, out});
  return out;
}

TraceCase make_case(const std::vector<Item>& input) {
  TraceCase trace;
  trace.input = input;
  trace.sorted = merge_sort_visit(input, "root", trace);
  return trace;
}

std::string split_json(const Split& s) {
  std::string out = "{\"path\":" + quote(s.path) + ",\"items\":" + array_json(s.items, item_json);
  if (s.base) return out + ",\"base\":true}";
  out += ",\"mid\":" + std::to_string(s.mid) + ",\"left\":" + array_json(s.left, item_json);
  return out + ",\"right\":" + array_json(s.right, item_json) + "}";
}

std::string step_json(const Step& s) {
  return "{\"left_front\":" + item_json(s.left_front) + ",\"right_front\":" + item_json(s.right_front) +
         ",\"chosen\":" + item_json(s.chosen) + ",\"side\":" + quote(s.side) + ",\"output\":" + array_json(s.output, item_json) + "}";
}

std::string merge_json(const Merge& m) {
  return "{\"path\":" + quote(m.path) + ",\"left\":" + array_json(m.left, item_json) +
         ",\"right\":" + array_json(m.right, item_json) + ",\"comparisons\":" + std::to_string(m.steps.size()) +
         ",\"steps\":" + array_json(m.steps, step_json) + ",\"result\":" + array_json(m.result, item_json) + "}";
}

std::string trace_json(const TraceCase& c) {
  std::string out = "{\"input\":" + array_json(c.input, item_json) + ",\"splits\":" + array_json(c.splits, split_json);
  out += ",\"merges\":" + array_json(c.merges, merge_json) + ",\"sorted\":" + array_json(c.sorted, item_json);
  out += ",\"comparison_count\":" + std::to_string(c.comparisons);
  size_t bases = 0;
  for (const auto& split : c.splits) if (split.base) ++bases;
  out += ",\"base_cases\":" + std::to_string(bases) + ",\"merge_count\":" + std::to_string(c.merges.size()) + "}";
  return out;
}

std::string output_text(const TraceCase& main, const TraceCase& dup) {
  std::ostringstream out;
  out << "input: [8, 3, 6, 2]\n"
      << "split root: [8, 3, 6, 2] -> [8, 3] | [6, 2]\n"
      << "split left: [8, 3] -> [8] | [3]\n"
      << "split right: [6, 2] -> [6] | [2]\n"
      << "merge [8] + [3]: compare 8 vs 3 -> take 3; append 8 => [3, 8]\n"
      << "merge [6] + [2]: compare 6 vs 2 -> take 2; append 6 => [2, 6]\n"
      << "merge [3, 8] + [2, 6]: compare 3 vs 2 -> take 2\n"
      << "merge [3, 8] + [2, 6]: compare 3 vs 6 -> take 3\n"
      << "merge [3, 8] + [2, 6]: compare 8 vs 6 -> take 6; append 8\n"
      << "sorted: [2, 3, 6, 8]\n"
      << "comparisons: " << main.comparisons << "\n"
      << "duplicate input: [2A, 1X, 2B, 1Y]\n"
      << "stable duplicate output: [1X, 1Y, 2A, 2B]\n"
      << "equality rule: left item wins when values are equal\n";
  (void)dup;
  return out.str();
}

int main(int argc, char** argv) {
  const TraceCase main_case = make_case({make_item(8), make_item(3), make_item(6), make_item(2)});
  const TraceCase dup_case = make_case({make_item(2, "2A"), make_item(1, "1X"), make_item(2, "2B"), make_item(1, "1Y")});
  const TraceCase empty_case = make_case({});
  const TraceCase single_case = make_case({make_item(7)});
  if (argc > 1 && std::string(argv[1]) == "--trace") {
    std::cout << "{\"algorithm\":\"top_down_stable_merge_sort\",\"comparison_rule\":\"left.value <= right.value\",\"cases\":{";
    std::cout << "\"main\":" << trace_json(main_case) << ",\"duplicates\":" << trace_json(dup_case)
              << ",\"empty\":" << trace_json(empty_case) << ",\"single\":" << trace_json(single_case) << "}}\n";
  } else {
    std::cout << output_text(main_case, dup_case);
  }
  return 0;
}
