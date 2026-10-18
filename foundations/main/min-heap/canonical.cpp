#include <iostream>
#include <optional>
#include <string>
#include <vector>

using namespace std;

bool is_heap(const vector<int>& a) {
    for (size_t i = 1; i < a.size(); ++i) {
        if (a[(i - 1) / 2] > a[i]) return false;
    }
    return true;
}

struct Event { string kind; optional<int> value; int index; int parent; int child; bool swapped; vector<int> heap; };
struct Result { vector<int> input, initial_heap, after_pop; vector<Event> events; optional<int> pop_min; optional<int> peek; };

void add(vector<Event>& e, const string& kind, const vector<int>& h, optional<int> value = nullopt, int index = -1, int parent = -1, int child = -1, bool swapped = false) {
    e.push_back({kind, value, index, parent, child, swapped, h});
}

Result run(const vector<int>& values, int extra = 0, bool has_extra = false) {
    vector<int> h;
    vector<Event> e;
    vector<int> to_push = values;
    if (has_extra) to_push.push_back(extra);
    for (int value : to_push) {
        h.push_back(value);
        add(e, "push_append", h, value, static_cast<int>(h.size()) - 1);
        int i = static_cast<int>(h.size()) - 1;
        while (i > 0) {
            int p = (i - 1) / 2;
            add(e, "push_compare", h, value, i, p);
            if (h[p] <= h[i]) break;
            swap(h[p], h[i]);
            add(e, "push_swap", h, value, i, p, -1, true);
            i = p;
        }
    }
    vector<int> initial = h;
    add(e, "before_pop", h);
    if (h.empty()) {
        add(e, "empty_pop", h);
        return {values, initial, {}, e, nullopt, nullopt};
    }
    int popped = h.front();
    int last = h.back();
    h.pop_back();
    if (!h.empty()) {
        h[0] = last;
        add(e, "pop_move_last", h, popped, 0);
        int i = 0;
        while (true) {
            int left = 2 * i + 1;
            int right = left + 1;
            if (left >= static_cast<int>(h.size())) break;
            int child = left;
            if (right < static_cast<int>(h.size()) && h[right] < h[left]) child = right;
            add(e, "pop_compare", h, popped, i, -1, child);
            if (h[i] <= h[child]) break;
            swap(h[i], h[child]);
            add(e, "pop_swap", h, popped, i, -1, child, true);
            i = child;
        }
    }
    add(e, "after_pop", h, popped);
    return {values, initial, h, e, popped, h.empty() ? nullopt : optional<int>(h.front())};
}

void json_array(const vector<int>& a) { cout << "["; for (size_t i=0;i<a.size();++i) { if(i) cout<<","; cout<<a[i]; } cout << "]"; }
void json_event(const Event& x) {
    cout << "{\"kind\":\"" << x.kind << "\",\"value\":";
    if (!x.value) cout << "null"; else cout << *x.value;
    cout << ",\"index\":"; if (x.index < 0) cout << "null"; else cout << x.index;
    cout << ",\"parent\":"; if (x.parent < 0) cout << "null"; else cout << x.parent;
    cout << ",\"child\":"; if (x.child < 0) cout << "null"; else cout << x.child;
    cout << ",\"swapped\":" << (x.swapped ? "true" : "false") << ",\"heap\":";
    json_array(x.heap);
    cout << ",\"is_heap\":" << (is_heap(x.heap) ? "true" : "false") << "}";
}
void json_result(const Result& r) {
    cout << "{\"input\":"; json_array(r.input); cout << ",\"initial_heap\":"; json_array(r.initial_heap); cout << ",\"events\":[";
    for(size_t i=0;i<r.events.size();++i){if(i)cout<<",";json_event(r.events[i]);}
    cout << "],\"pop_min\":"; if (!r.pop_min) cout << "null"; else cout << *r.pop_min; cout << ",\"after_pop\":"; json_array(r.after_pop); cout << ",\"peek\":" << (!r.peek ? "null" : to_string(*r.peek)) << "}";
}

int main(int argc, char** argv) {
    bool alternate = false, tracing = false;
    for(int i=1;i<argc;++i){alternate |= string(argv[i])=="--alternate";tracing |= string(argv[i])=="--trace";}
    int extra = alternate ? 0 : 3;
    Result c = run(alternate ? vector<int>{9,4,7,1} : vector<int>{4,9,7,15,12,10}, extra, true);
    if (tracing) {
        cout << "{\"canonical\":"; json_result(c); cout << ",\"edges\":{\"empty\":"; json_result(run({})); cout << ",\"one\":"; json_result(run({8})); cout << ",\"duplicates\":"; json_result(run({5,5,2,2})); cout << ",\"left_only\":"; json_result(run({1,2,3})); cout << ",\"alternate\":"; json_result(run({9,4,7,1},0,true)); cout << "}}\n";
        return 0;
    }
    auto display = [](const vector<int>& a) { cout << "["; for(size_t i=0;i<a.size();++i){if(i)cout<<", ";cout<<a[i];}cout<<"]"; };
    cout << "initial input: "; display(c.input); cout << "\n";
    cout << "heap after pushes: "; display(run(c.input).initial_heap); cout << "\n";
    cout << "push(" << extra << ") heap: "; display(c.initial_heap); cout << "\n";
    cout << "pop_min(): " << *c.pop_min << "\n";
    cout << "heap after pop_min: "; display(c.after_pop); cout << "\n";
    cout << "heap property: " << (is_heap(c.after_pop)?"true":"false") << "\n";
    cout << "pop trace events: " << c.events.size() << "\n";
}
