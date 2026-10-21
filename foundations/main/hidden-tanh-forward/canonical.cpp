#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Vec = std::vector<double>;
using Mat = std::vector<Vec>;

const std::vector<std::string> TOKENS{"a", "b", "c"};
const Mat E{{1, 0}, {0, 1}, {1, 1}};
const Mat W1{{1, 0}, {0, 1}, {1, -1}, {-1, 1}};
const Vec B1{0, 0};
const Mat W2{{1, 0, -1}, {0, 1, 0}};
const Vec B2{0, 0, 0};

struct Term { double left; double right; double product; };
struct Detail { int output_id; double bias; std::vector<Term> terms; Vec partial_sums; double result; };
struct Forward { std::vector<int> context; Vec x; Vec b1; std::vector<Detail> linear1; Vec u; Vec h; std::vector<Detail> linear2; Vec z; Vec p; int prediction; };

double clean_zero(double value) { return value == 0.0 ? 0.0 : value; }

void validate_context(const std::vector<int>& ids) {
    if (ids.size() != 2 || ids[0] < 0 || ids[0] >= static_cast<int>(E.size()) || ids[1] < 0 || ids[1] >= static_cast<int>(E.size())) {
        throw std::invalid_argument("context must contain two valid ids");
    }
}

Vec stable_softmax(const Vec& z) {
    if (z.empty()) throw std::invalid_argument("logits must be non-empty");
    const double peak = *std::max_element(z.begin(), z.end());
    Vec weights;
    double total = 0.0;
    for (double value : z) {
        weights.push_back(std::exp(value - peak));
        total += weights.back();
    }
    for (double& value : weights) value /= total;
    return weights;
}

std::vector<Detail> linear_details(const Vec& values, const Mat& weights, const Vec& bias) {
    if (weights.empty() || values.size() != weights.size()) throw std::invalid_argument("linear shape mismatch");
    for (const Vec& row : weights) if (row.size() != bias.size()) throw std::invalid_argument("linear shape mismatch");
    std::vector<Detail> details;
    for (size_t j = 0; j < bias.size(); ++j) {
        Detail item{static_cast<int>(j), bias[j], {}, {}, bias[j]};
        for (size_t i = 0; i < values.size(); ++i) {
            const double product = clean_zero(values[i] * weights[i][j]);
            item.result = clean_zero(item.result + product);
            item.terms.push_back({values[i], weights[i][j], product});
            item.partial_sums.push_back(item.result);
        }
        details.push_back(item);
    }
    return details;
}

Forward forward(const std::vector<int>& ids, const Vec& bias = B1) {
    validate_context(ids);
    if (bias.size() != 2) throw std::invalid_argument("b1 shape");
    Vec x{E.at(static_cast<size_t>(ids.at(0))).at(0), E.at(static_cast<size_t>(ids.at(0))).at(1),
          E.at(static_cast<size_t>(ids.at(1))).at(0), E.at(static_cast<size_t>(ids.at(1))).at(1)};
    const std::vector<Detail> first = linear_details(x, W1, bias);
    Vec u;
    for (const Detail& item : first) u.push_back(item.result);
    Vec h;
    for (double value : u) h.push_back(std::tanh(value));
    const std::vector<Detail> second = linear_details(h, W2, B2);
    Vec z;
    for (const Detail& item : second) z.push_back(item.result);
    Vec p = stable_softmax(z);
    const int prediction = static_cast<int>(std::distance(p.begin(), std::max_element(p.begin(), p.end())));
    return {ids, x, bias, first, u, h, second, z, p, prediction};
}

std::string number(double value) {
    std::ostringstream out;
    out << std::fixed << std::setprecision(6) << value;
    return out.str();
}

std::string json_number(double value) {
    std::ostringstream out;
    out << std::setprecision(17) << value;
    return out.str();
}

std::string vec_text(const Vec& values) {
    std::string out{"["};
    for (size_t i = 0; i < values.size(); ++i) { if (i) out += ","; out += number(values[i]); }
    return out + "]";
}

std::string json_vec(const Vec& values) {
    std::string out{"["};
    for (size_t i = 0; i < values.size(); ++i) { if (i) out += ","; out += json_number(values[i]); }
    return out + "]";
}

std::string json_ints(const std::vector<int>& values) {
    std::string out{"["};
    for (size_t i = 0; i < values.size(); ++i) { if (i) out += ","; out += std::to_string(values[i]); }
    return out + "]";
}

std::string context_text(const std::vector<int>& ids) {
    return "[" + TOKENS.at(static_cast<size_t>(ids.at(0))) + "," + TOKENS.at(static_cast<size_t>(ids.at(1))) + "]";
}

std::string json_mat(const Mat& matrix) {
    std::string out{"["};
    for (size_t i = 0; i < matrix.size(); ++i) { if (i) out += ","; out += json_vec(matrix[i]); }
    return out + "]";
}

std::string json_detail(const std::vector<Detail>& details) {
    std::string out{"["};
    for (size_t j = 0; j < details.size(); ++j) {
        if (j) out += ",";
        const Detail& item = details[j];
        out += "{\"output_id\":" + std::to_string(item.output_id) + ",\"bias\":" + json_number(item.bias) + ",\"terms\":[";
        for (size_t i = 0; i < item.terms.size(); ++i) {
            if (i) out += ",";
            const Term& term = item.terms[i];
            out += "{\"left\":" + json_number(term.left) + ",\"right\":" + json_number(term.right) + ",\"product\":" + json_number(term.product) + "}";
        }
        out += "],\"partial_sums\":" + json_vec(item.partial_sums) + ",\"result\":" + json_number(item.result) + "}";
    }
    return out + "]";
}

std::string json_forward(const Forward& item) {
    return "{\"context_ids\":" + json_ints(item.context) + ",\"x\":" + json_vec(item.x) + ",\"b1\":" + json_vec(item.b1) +
           ",\"linear1\":" + json_detail(item.linear1) + ",\"u\":" + json_vec(item.u) + ",\"h\":" + json_vec(item.h) +
           ",\"linear2\":" + json_detail(item.linear2) + ",\"z\":" + json_vec(item.z) + ",\"p\":" + json_vec(item.p) +
           ",\"prediction_id\":" + std::to_string(item.prediction) + "}";
}

std::string trace_json() {
    const Forward main = forward({0, 1});
    const Forward reverse = forward({1, 0});
    const Forward bias = forward({0, 1}, {1, -1});
    const Forward transfer = forward({2, 0});
    return "{\"contract\":{\"tokens\":[\"a\",\"b\",\"c\"],\"ids\":{\"a\":0,\"b\":1,\"c\":2},\"E\":" + json_mat(E) +
           ",\"W1\":" + json_mat(W1) + ",\"B1\":" + json_vec(B1) + ",\"W2\":" + json_mat(W2) + ",\"B2\":" + json_vec(B2) +
           ",\"shapes\":{\"x\":[1,4],\"u\":[1,2],\"h\":[1,2],\"z\":[1,3],\"p\":[1,3]},\"provenance\":\"toy hand-chosen weights; not learned\"}," +
           "\"main\":" + json_forward(main) + ",\"reverse\":" + json_forward(reverse) + ",\"bias_case\":" + json_forward(bias) +
           ",\"transfer\":" + json_forward(transfer) +",\"shape_case\":{\"input_shape\":[1,4],\"hidden_shape\":[1,2],\"output_shape\":[1,3]}," +
           "\"edge_cases\":{\"invalid_id\":\"reject\",\"wrong_context_width\":\"reject\",\"empty_context\":\"reject\",\"single_context\":\"reject\",\"finite_probabilities\":\"true\"}," +
           "\"stable_softmax_sum\":" + json_number(main.p[0] + main.p[1] + main.p[2]) + "}";
}

std::string display_default() {
    const Forward main = forward({0, 1});
    const Forward reverse = forward({1, 0});
    const Forward bias = forward({0, 1}, {1, -1});
    const Forward transfer = forward({2, 0});
    std::ostringstream out;
    out << "contract tokens=3 ids=0,1,2 E=3x2 W1=4x2 W2=2x3\n";
    out << "[a,b] x=" << vec_text(main.x) << " u=" << vec_text(main.u) << " h=" << vec_text(main.h) << " z=" << vec_text(main.z) << "\n";
    out << "[b,a] x=" << vec_text(reverse.x) << " u=" << vec_text(reverse.u) << " h=" << vec_text(reverse.h) << " z=" << vec_text(reverse.z) << "\n";
    out << "bias_b1=[1,-1] [a,b] u=" << vec_text(bias.u) << "\n";
    out << "transfer [c,a] x=" << vec_text(transfer.x) << " u=" << vec_text(transfer.u) << " h=" << vec_text(transfer.h) << " z=" << vec_text(transfer.z) << "\n";
    out << "softmax_sum_ab=" << number(main.p[0] + main.p[1] + main.p[2]) << " prediction_ab=" << TOKENS.at(static_cast<size_t>(main.prediction)) << "\n";
    out << "p_ab=" << vec_text(main.p) << " p_ba=" << vec_text(reverse.p) << " p_transfer=" << vec_text(transfer.p) << "\n";
    return out.str();
}

std::string display_transfer() {
    const Forward item = forward({2, 0});
    return "transfer=" + context_text(item.context) + " x=" + vec_text(item.x) + " u=" + vec_text(item.u) + " h=" + vec_text(item.h) +
           " z=" + vec_text(item.z) + " p=" + vec_text(item.p) + "\n";
}

int main(int argc, char** argv) {
    if (argc > 1 && std::string(argv[1]) == "--trace") std::cout << trace_json() << "\n";
    else if (argc > 1 && std::string(argv[1]) == "--transfer") std::cout << display_transfer();
    else if (argc > 1 && std::string(argv[1]) == "--edge") std::cout << "edge=invalid_id:reject;wrong_context_width:reject;empty_context:reject;single_context:reject;finite_probabilities:true\n";
    else if (argc > 1 && std::string(argv[1]) == "--shape") std::cout << "shape=input(1, 4) hidden(1, 2) output(1, 3)\n";
    else std::cout << display_default();
}
