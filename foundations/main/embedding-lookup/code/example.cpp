#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Matrix = std::vector<std::vector<int>>;
const Matrix E{{1, 0}, {0, 2}, {-1, 1}};
const std::vector<int> IDS{0, 1, 0, 2};

void check_id(int id) {
    if (id < 0 || id >= static_cast<int>(E.size())) {
        throw std::out_of_range("id must satisfy 0 <= id < vocab_size");
    }
}

std::vector<int> one_hot(int id) {
    check_id(id);
    std::vector<int> result(E.size(), 0);
    result[id] = 1;
    return result;
}

std::vector<int> matmul_one_hot(const std::vector<int>& weights, const Matrix& matrix) {
    if (weights.size() != matrix.size()) throw std::invalid_argument("shape mismatch");
    std::vector<int> result(matrix[0].size(), 0);
    for (std::size_t col = 0; col < matrix[0].size(); ++col) {
        for (std::size_t row = 0; row < matrix.size(); ++row) {
            result[col] += weights[row] * matrix[row][col];
        }
    }
    return result;
}

std::vector<int> lookup(int id) {
    return matmul_one_hot(one_hot(id), E);
}

bool equal(const std::vector<int>& left, const std::vector<int>& right) {
    return left == right;
}

int main() {
    const auto weights = one_hot(1);
    const auto output = matmul_one_hot(weights, E);
    std::vector<std::vector<int>> sequence;
    for (int id : IDS) sequence.push_back(lookup(id));
    if (E.size() != 3 || E[0].size() != 2) throw std::runtime_error("shape test failed");
    if (!equal(output, E[1]) || !equal(output, {0, 2})) throw std::runtime_error("lookup test failed");
    if (sequence != Matrix{{1, 0}, {0, 2}, {1, 0}, {-1, 1}}) throw std::runtime_error("sequence test failed");
    if (!equal(sequence[0], sequence[2])) throw std::runtime_error("repeat test failed");
    for (int bad : {3, -1}) {
        try { lookup(bad); throw std::runtime_error("invalid id accepted"); }
        catch (const std::out_of_range&) {}
    }
    std::cout << "lesson: one-hot-to-embedding lookup\n";
    std::cout << "vocab: a=0,b=1,c=2\n";
    std::cout << "E shape: 3x2\n";
    std::cout << "E rows: [1,0] [0,2] [-1,1]\n";
    std::cout << "id=1 onehot: [0,1,0]\n";
    std::cout << "id=1 weighted_rows: [0,0] [0,2] [0,0]\n";
    std::cout << "id=1 output: [0,2]\n";
    std::cout << "id=1 equals E[1]: true\n";
    std::cout << "sequence ids: [0,1,0,2]\n";
    std::cout << "sequence output shape: 4x2\n";
    std::cout << "sequence outputs: [1,0] [0,2] [1,0] [-1,1]\n";
    std::cout << "repeat id=0: true\n";
    std::cout << "invalid id=3: rejected\n";
    std::cout << "invalid id=-1: rejected\n";
    std::cout << "tests: shape=pass, lookup=pass, sequence=pass, bounds=pass\n";
}
