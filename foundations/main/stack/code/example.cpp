// C++17 executable LIFO stack contract for the lesson.
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

class Stack {
public:
    std::vector<int> items;

    void push(int value) { items.push_back(value); }

    int top() const {
        if (items.empty()) throw std::out_of_range("underflow");
        return items.back();
    }

    int pop() {
        if (items.empty()) throw std::out_of_range("underflow");
        const int value = items.back();
        items.pop_back();
        return value;
    }
};

struct Trace {
    std::vector<int> after_push;
    int top_value{};
    int popped{};
    std::vector<int> after_pop;
    int second_pop{};
    std::vector<int> after_second_pop;
    std::string empty_pop_error;
    std::string empty_top_error;
};

Trace make_trace() {
    Stack stack;
    stack.push(10);
    stack.push(20);
    stack.push(30);
    Trace trace;
    trace.after_push = stack.items;
    trace.top_value = stack.top();
    trace.popped = stack.pop();
    trace.after_pop = stack.items;
    trace.second_pop = stack.pop();
    trace.after_second_pop = stack.items;

    Stack empty;
    try { empty.pop(); } catch (const std::out_of_range& error) { trace.empty_pop_error = error.what(); }
    try { empty.top(); } catch (const std::out_of_range& error) { trace.empty_top_error = error.what(); }
    return trace;
}

std::string list_text(const std::vector<int>& values) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) out << ',';
        out << values[i];
    }
    out << ']';
    return out.str();
}

std::string stdout_text(const Trace& trace) {
    std::ostringstream out;
    out << "STACK after_push=" << list_text(trace.after_push) << '\n';
    out << "TOP value=" << trace.top_value << '\n';
    out << "POP value=" << trace.popped << " remaining=" << list_text(trace.after_pop) << '\n';
    out << "SECOND_POP value=" << trace.second_pop << " remaining=" << list_text(trace.after_second_pop) << '\n';
    out << "EMPTY pop_error=" << trace.empty_pop_error << " top_error=" << trace.empty_top_error << '\n';
    out << "COST top=O(1) logical_pop=O(1) python_pop_amortized=O(1) python_pop_worst=O(n) cpp_vector_pop_back=O(1)\n";
    return out.str();
}

std::string trace_json(const Trace& trace) {
    std::ostringstream out;
    out << "{\"after_pop\":{\"state\":" << list_text(trace.after_pop)
        << ",\"value\":" << trace.popped << "},"
        << "\"after_push\":" << list_text(trace.after_push) << ','
        << "\"costs\":{\"cpp_vector_pop_back\":\"O(1) for int\",\"pop_logical\":\"O(1)\",\"python_pop_amortized\":\"O(1)\",\"python_pop_worst\":\"O(n) possible shrink/reallocation\",\"push_amortized\":\"O(1)\",\"push_worst\":\"O(n)\",\"resize_note\":\"dynamic array relocation\",\"top\":\"O(1)\"},"
        << "\"empty\":{\"pop_error\":\"" << trace.empty_pop_error << "\",\"state\":[],\"top_error\":\"" << trace.empty_top_error << "\"},"
        << "\"top\":{\"state\":" << list_text(trace.after_push) << ",\"value\":" << trace.top_value << "},"
        << "\"second_pop\":{\"state\":" << list_text(trace.after_second_pop) << ",\"value\":" << trace.second_pop << "}}";
    return out.str();
}

int main(int argc, char** argv) {
    const Trace trace = make_trace();
    if (argc > 1 && std::string(argv[1]) == "--trace") std::cout << trace_json(trace) << '\n';
    else std::cout << stdout_text(trace);
}
