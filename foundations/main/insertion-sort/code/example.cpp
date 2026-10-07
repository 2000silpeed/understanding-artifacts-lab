#include <iostream>
#include <string>
#include <vector>

// Logical counts, deliberately independent of wall-clock time.
// comparisons: each evaluated value comparison item[j].value > key.value.
// shifts: each existing item copied one cell right.
// inserts: one saved-key placement per outer pass.
// writes = shifts + inserts. Strict `>` makes equal tagged values stable.
struct Item {
    int value;
    std::string label;
};

struct Counts {
    long long comparisons = 0;
    long long shifts = 0;
    long long inserts = 0;
};

std::vector<Item> insertion_sort(std::vector<Item> items, Counts& counts) {
    for (std::size_t i = 1; i < items.size(); ++i) {
        Item key = items[i];
        int j = static_cast<int>(i) - 1;
        while (j >= 0) {
            ++counts.comparisons;
            if ((items[static_cast<std::size_t>(j)].value <= key.value)) break;
            items[static_cast<std::size_t>(j + 1)] = items[static_cast<std::size_t>(j)];
            ++counts.shifts;
            --j;
        }
        items[static_cast<std::size_t>(j + 1)] = key;
        ++counts.inserts;
    }
    return items;
}

std::string short_item(const Item& item) {
    return std::to_string(item.value) + item.label;
}

void print_items(const std::vector<Item>& items) {
    std::cout << '[';
    for (std::size_t i = 0; i < items.size(); ++i) {
        if (i) std::cout << ", ";
        std::cout << short_item(items[i]);
    }
    std::cout << ']';
}

void print_case(const std::string& name, const std::vector<Item>& source) {
    Counts counts;
    const auto result = insertion_sort(source, counts);
    std::cout << "CASE " << name << '\n';
    std::cout << "input: "; print_items(source); std::cout << '\n';
    std::cout << "sorted: "; print_items(result); std::cout << '\n';
    std::cout << "comparisons: " << counts.comparisons << '\n';
    std::cout << "shifts: " << counts.shifts << '\n';
    std::cout << "inserts: " << counts.inserts << '\n';
    std::cout << "writes: " << counts.shifts + counts.inserts << '\n';
}

int main() {
    print_case("main", {{8, ""}, {3, ""}, {5, ""}, {2, ""}});
    print_case("practice", {{6, ""}, {1, ""}, {4, ""}, {2, ""}, {5, ""}});
    print_case("best", {{1, ""}, {2, ""}, {3, ""}, {4, ""}});
    print_case("worst", {{4, ""}, {3, ""}, {2, ""}, {1, ""}});
    print_case("empty", {});
    print_case("single", {{7, ""}});
    print_case("duplicates_tagged", {{2, "A"}, {1, "X"}, {2, "B"}, {1, "Y"}});
    return 0;
}
