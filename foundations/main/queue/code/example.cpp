// C++17 executable FIFO queue contract for the lesson.
#include <iostream>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

class Queue {
public:
    std::queue<int> items; // default underlying container is std::deque<int>

    void enqueue(int value) { items.push(value); }

    int front() const {
        if (items.empty()) throw std::out_of_range("empty");
        return items.front();
    }

    int dequeue() {
        if (items.empty()) throw std::out_of_range("empty");
        const int value = items.front();
        items.pop();
        return value;
    }
};

std::vector<int> state(std::queue<int> queue) {
    std::vector<int> values;
    while (!queue.empty()) {
        values.push_back(queue.front());
        queue.pop();
    }
    return values;
}

struct Trace {
    std::vector<int> initial;
    int enqueued{};
    std::vector<int> after_enqueue;
    int front_value{};
    std::vector<int> front_state;
    int dequeued{};
    std::vector<int> after_dequeue;
    int exercise_enqueued{};
    std::vector<int> exercise_after_enqueue;
    int exercise_dequeued{};
    std::vector<int> exercise_after_dequeue;
    std::string empty_front_guard;
    std::string empty_dequeue_guard;
};

Trace make_trace() {
    Queue queue;
    queue.enqueue(12);
    queue.enqueue(35);
    queue.enqueue(8);

    Trace trace;
    trace.initial = state(queue.items);
    queue.enqueue(47);
    trace.enqueued = 47;
    trace.after_enqueue = state(queue.items);
    trace.front_value = queue.front();
    trace.front_state = state(queue.items);
    trace.dequeued = queue.dequeue();
    trace.after_dequeue = state(queue.items);

    queue.enqueue(19);
    trace.exercise_enqueued = 19;
    trace.exercise_after_enqueue = state(queue.items);
    trace.exercise_dequeued = queue.dequeue();
    trace.exercise_after_dequeue = state(queue.items);

    Queue empty;
    try { empty.front(); } catch (const std::out_of_range& error) { trace.empty_front_guard = error.what(); }
    try { empty.dequeue(); } catch (const std::out_of_range& error) { trace.empty_dequeue_guard = error.what(); }
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
    out << "QUEUE initial=" << list_text(trace.initial) << '\n';
    out << "ENQUEUE value=" << trace.enqueued << " state=" << list_text(trace.after_enqueue) << '\n';
    out << "FRONT value=" << trace.front_value << " state=" << list_text(trace.front_state) << '\n';
    out << "DEQUEUE value=" << trace.dequeued << " remaining=" << list_text(trace.after_dequeue) << '\n';
    out << "EXERCISE enqueue=" << trace.exercise_enqueued << " state=" << list_text(trace.exercise_after_enqueue) << '\n';
    out << "EXERCISE dequeue=" << trace.exercise_dequeued << " remaining=" << list_text(trace.exercise_after_dequeue) << '\n';
    out << "EMPTY front_guard=" << trace.empty_front_guard << " dequeue_guard=" << trace.empty_dequeue_guard << '\n';
    out << "COST deque_append=O(1) deque_popleft=O(1) list_pop_zero=O(n) std_queue_default_deque=O(1)\n";
    return out.str();
}

std::string json_list(const std::vector<int>& values) { return list_text(values); }

std::string trace_json(const Trace& trace) {
    std::ostringstream out;
    out << "{\"after_dequeue\":{\"state\":" << json_list(trace.after_dequeue)
        << ",\"value\":" << trace.dequeued << "},"
        << "\"after_enqueue\":{\"state\":" << json_list(trace.after_enqueue)
        << ",\"value\":" << trace.enqueued << "},"
        << "\"costs\":{\"cpp_std_queue_default_deque_front\":\"O(1)\",\"cpp_std_queue_default_deque_pop\":\"O(1)\",\"cpp_std_queue_default_deque_push\":\"O(1)\",\"order_note\":\"logical order only; physical layout unspecified\",\"python_deque_append\":\"O(1)\",\"python_deque_popleft\":\"O(1)\",\"python_list_pop_zero\":\"O(n)\"},"
        << "\"empty\":{\"dequeue_guard\":\"" << trace.empty_dequeue_guard << "\",\"front_guard\":\"" << trace.empty_front_guard << "\",\"state\":[]},"
        << "\"exercise\":{\"after_dequeue\":{\"state\":" << json_list(trace.exercise_after_dequeue)
        << ",\"value\":" << trace.exercise_dequeued << "},\"after_enqueue\":{\"state\":"
        << json_list(trace.exercise_after_enqueue) << ",\"value\":" << trace.exercise_enqueued << "}},"
        << "\"front\":{\"state\":" << json_list(trace.front_state) << ",\"value\":" << trace.front_value << "},"
        << "\"initial\":" << json_list(trace.initial) << "}\n";
    return out.str();
}

int main(int argc, char** argv) {
    const Trace trace = make_trace();
    if (argc > 1 && std::string(argv[1]) == "--trace") std::cout << trace_json(trace);
    else std::cout << stdout_text(trace);
}
