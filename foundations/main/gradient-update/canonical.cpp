#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

std::vector<double> stable_softmax(const std::vector<double>& z) {
    if (z.empty()) throw std::invalid_argument("empty logits");
    for (double x : z) if (!std::isfinite(x)) throw std::invalid_argument("nonfinite logit");
    const double shift = *std::max_element(z.begin(), z.end());
    std::vector<double> weights;
    double denominator = 0.0;
    for (double x : z) { weights.push_back(std::exp(x - shift)); denominator += weights.back(); }
    std::vector<double> p;
    for (double w : weights) p.push_back(w / denominator);
    return p;
}

double loss(const std::vector<double>& z, int target) {
    if (target < 0 || target >= static_cast<int>(z.size())) throw std::out_of_range("target ID");
    stable_softmax(z); // finite/nonempty validation
    const double shift = *std::max_element(z.begin(), z.end());
    double denominator = 0.0;
    for (double value : z) denominator += std::exp(value - shift);
    const double result = (shift - z[target]) + std::log(denominator);
    if (!std::isfinite(result)) throw std::invalid_argument("loss outside finite numeric range");
    return result;
}

std::vector<double> gradient(const std::vector<double>& z, int target) {
    auto p = stable_softmax(z);
    if (target < 0 || target >= static_cast<int>(z.size())) throw std::out_of_range("target ID");
    p[target] -= 1.0;
    return p;
}

std::vector<double> finite_difference(const std::vector<double>& z, int target, double eps) {
    std::vector<double> result;
    for (int i = 0; i < static_cast<int>(z.size()); ++i) {
        auto plus = z; auto minus = z;
        plus[i] += eps; minus[i] -= eps;
        result.push_back((loss(plus, target) - loss(minus, target)) / (2.0 * eps));
    }
    return result;
}

std::vector<double> update(const std::vector<double>& z, const std::vector<double>& g, double eta) {
    std::vector<double> result;
    for (int i = 0; i < static_cast<int>(z.size()); ++i) result.push_back(z[i] - eta * g[i]);
    return result;
}

double vector_sum(const std::vector<double>& values) {
    double total = 0.0; for (double value : values) total += value; return total;
}

std::string fmt(const std::vector<double>& values) {
    std::ostringstream out; out << "[" << std::fixed << std::setprecision(6);
    for (size_t i = 0; i < values.size(); ++i) { if (i) out << ", "; out << values[i]; }
    return out.str() + "]";
}

int main() {
    const std::vector<double> logits{1.0, 0.0, -0.5};
    const int target = 1; const double eps = 1e-5; const double eta = 0.4; const double large_eta = 20.0;
    const auto p = stable_softmax(logits); const auto g = gradient(logits, target); const auto fd = finite_difference(logits, target, eps);
    const auto next = update(logits, g, eta); const auto next_p = stable_softmax(next);
    const auto large = update(logits, g, large_eta); const auto large_p = stable_softmax(large);
    std::cout << "initial logits: " << fmt(logits) << "\n";
    std::cout << "initial probabilities: " << fmt(p) << "\n";
    std::cout << "target probability: " << std::fixed << std::setprecision(15) << p[target] << "\n";
    std::cout << "initial loss: " << loss(logits, target) << "\n";
    std::cout << "finite difference gradient: " << fmt(fd) << "\n";
    std::cout << "p-minus-y gradient: " << fmt(g) << "\n";
    std::cout << "gradient sum: " << vector_sum(g) << "\n";
    std::cout << "small learning rate: 0.400000\n";
    std::cout << "updated logits: " << fmt(next) << "\n";
    std::cout << "updated probabilities: " << fmt(next_p) << "\n";
    std::cout << "updated target probability: " << next_p[target] << "\n";
    std::cout << "updated loss: " << loss(next, target) << "\n";
    std::cout << "large learning rate: 20.000000\n";
    std::cout << "large-step target probability: " << large_p[target] << "\n";
    std::cout << "large-step loss: " << loss(large, target) << "\n";
    std::cout << "boundary: stable softmax; toy logits only; no transformer training\n";
    return 0;
}
