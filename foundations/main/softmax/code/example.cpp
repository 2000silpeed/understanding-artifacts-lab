#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

// Source-only toy contract: public embedding lookup [0, 2] and hand-chosen W.
int main() {
    const std::vector<double> embedding{0.0, 2.0};
    const double W[2][3]{{1.0, 0.0, -1.0}, {0.0, 1.0, 2.0}};
    std::vector<double> logits(3, 0.0);
    for (int c = 0; c < 3; ++c) {
        for (int r = 0; r < 2; ++r) logits[c] += embedding[r] * W[r][c];
    }
    const double peak = *std::max_element(logits.begin(), logits.end());
    std::vector<double> shifted;
    std::vector<double> weights;
    for (double z : logits) {
        shifted.push_back(z - peak);
        weights.push_back(std::exp(z - peak));
    }
    const double denominator = std::accumulate(weights.begin(), weights.end(), 0.0);
    std::vector<double> probabilities;
    for (double weight : weights) probabilities.push_back(weight / denominator);
    auto fixed = [](double value) {
        std::ostringstream out;
        out << std::fixed << std::setprecision(6) << value;
        return out.str();
    };
    auto print = [&](const std::vector<double>& values) {
        for (std::size_t i = 0; i < values.size(); ++i) {
            if (i) std::cout << ',';
            std::cout << fixed(values[i]);
        }
    };
    std::vector<double> displayedProbabilities;
    for (double probability : probabilities) displayedProbabilities.push_back(std::stod(fixed(probability)));
    std::cout << "embedding: ["; print(embedding); std::cout << "]\n";
    std::cout << "W shape: [2, 3]\n";
    std::cout << "logits: ["; print(logits); std::cout << "]\n";
    std::cout << "max(logits): " << fixed(peak) << "\n";
    std::cout << "shifted: ["; print(shifted); std::cout << "]\n";
    std::cout << "positive weights exp(shifted): ["; print(weights); std::cout << "]\n";
    std::cout << "denominator: " << fixed(denominator) << "\n";
    std::cout << "probabilities: ["; print(probabilities); std::cout << "]\n";
    std::cout << "prediction: class 2\n";
    std::cout << "displayed probability sum: " << fixed(std::accumulate(displayedProbabilities.begin(), displayedProbabilities.end(), 0.0)) << "\n";
    std::cout << "floating normalization sum: " << fixed(std::accumulate(probabilities.begin(), probabilities.end(), 0.0)) << " (before display rounding)\n";
    std::cout << "equal logits transfer: each probability = 1/3 (exact)\n";
}
