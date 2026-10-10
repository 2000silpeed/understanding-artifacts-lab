#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

void validate_probability(double probability) {
    if (!std::isfinite(probability) || probability <= 0.0 || probability > 1.0) {
        throw std::invalid_argument("probability must satisfy 0 < p <= 1; p=0 has mathematical loss +infinity");
    }
}

void validate_target(int target_id, const std::vector<double>& probabilities) {
    if (target_id < 0 || target_id >= static_cast<int>(probabilities.size())) {
        throw std::out_of_range("target token ID is outside the probability vector");
    }
}

double next_token_loss(const std::vector<double>& probabilities, int target_id) {
    validate_target(target_id, probabilities);
    const double target_probability = probabilities[target_id];
    validate_probability(target_probability);
    return -std::log(target_probability);
}

std::string fixed(double value) {
    std::ostringstream output;
    output << std::fixed << std::setprecision(6) << value;
    return output.str();
}

std::string full(double value) {
    std::ostringstream output;
    output << std::fixed << std::setprecision(15) << value;
    return output.str();
}

int main() {
    const std::vector<double> probabilities{0.1, 0.7, 0.2};
    const double primary_loss = next_token_loss(probabilities, 1);
    const double comparison_loss = next_token_loss(probabilities, 0);
    const double mean_loss = (primary_loss + comparison_loss) / 2.0;

    // Exercise the rejection contract without changing the public stdout.
    try { validate_probability(0.0); return 2; } catch (const std::invalid_argument&) {}
    try { validate_probability(1.2); return 2; } catch (const std::invalid_argument&) {}
    try { validate_target(3, probabilities); return 2; } catch (const std::out_of_range&) {}

    std::cout << "probabilities: [" << fixed(probabilities[0]) << "," << fixed(probabilities[1]) << "," << fixed(probabilities[2]) << "]\n";
    std::cout << "target token ID: 1\n";
    std::cout << "target probability: 0.700000\n";
    std::cout << "loss full: " << full(primary_loss) << "\n";
    std::cout << "loss displayed rounded: " << fixed(primary_loss) << "\n";
    std::cout << "comparison target token ID: 0\n";
    std::cout << "comparison target probability: 0.100000\n";
    std::cout << "comparison loss full: " << full(comparison_loss) << "\n";
    std::cout << "comparison loss displayed rounded: " << fixed(comparison_loss) << "\n";
    std::cout << "mean of two losses full: " << full(mean_loss) << "\n";
    std::cout << "mean of two losses displayed rounded: " << fixed(mean_loss) << "\n";
    std::cout << "validation: p=0 rejected; mathematical loss limit is +infinity\n";
    std::cout << "validation: p=1.2 rejected; target token ID=3 rejected\n";
    std::cout << "boundary: toy probabilities only; no training, gradient, autograd, framework, or Transformer inference\n";
}
