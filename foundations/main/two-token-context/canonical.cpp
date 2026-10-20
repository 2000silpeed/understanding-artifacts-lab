#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Vec = std::vector<double>;
using Mat = std::vector<Vec>;

const std::vector<std::string> TOKENS{"a", "b", "c"};
const Mat E{{1, 0}, {0, 1}, {1, 1}};
const Mat W{{1, 0, -1}, {0, 1, 0}, {0, -1, 1}, {1, 0, 0}};
const std::vector<int> SEQUENCE{0, 1, 2, 0};

struct Term { double left; double right; double product; };
struct DotProduct { int output_id; std::vector<Term> terms; Vec partial_sums; double result; };
struct Forward { std::vector<int> context; Vec h; std::vector<DotProduct> dot_products; Vec z; Vec p; int prediction; };
struct Pair { std::vector<int> context; int target; std::vector<int> future; };

double clean_zero(double value) { return value == 0.0 ? 0.0 : value; }

Vec softmax(const Vec& z) {
    const double max_z = *std::max_element(z.begin(), z.end());
    Vec weights;
    double total = 0.0;
    for (double value : z) {
        weights.push_back(std::exp(value - max_z));
        total += weights.back();
    }
    for (double& value : weights) value /= total;
    return weights;
}

std::vector<DotProduct> dot_products(const Vec& h) {
    if (h.size() != W.size()) throw std::invalid_argument("h width");
    std::vector<DotProduct> details;
    for (size_t j = 0; j < W.front().size(); ++j) {
        DotProduct column{static_cast<int>(j), {}, {}, 0.0};
        double total = 0.0;
        for (size_t i = 0; i < h.size(); ++i) {
            const double product = clean_zero(h[i] * W[i][j]);
            total = clean_zero(total + product);
            column.terms.push_back({h[i], W[i][j], product});
            column.partial_sums.push_back(total);
        }
        column.result = total;
        details.push_back(column);
    }
    return details;
}

Forward forward(const std::vector<int>& ids) {
    if (ids.size() != 2) throw std::invalid_argument("context length");
    Vec h{E.at(ids.at(0)).at(0), E.at(ids.at(0)).at(1), E.at(ids.at(1)).at(0), E.at(ids.at(1)).at(1)};
    const std::vector<DotProduct> products = dot_products(h);
    Vec z;
    for (const DotProduct& column : products) z.push_back(column.result);
    Vec p = softmax(z);
    const int prediction = static_cast<int>(std::distance(p.begin(), std::max_element(p.begin(), p.end())));
    return {ids, h, products, z, p, prediction};
}

std::vector<Pair> build_training_pairs() {
    std::vector<Pair> pairs;
    for (size_t i = 0; i + 2 < SEQUENCE.size(); ++i) {
        pairs.push_back({{SEQUENCE[i], SEQUENCE[i + 1]}, SEQUENCE[i + 2], std::vector<int>(SEQUENCE.begin() + static_cast<long>(i + 3), SEQUENCE.end())});
    }
    return pairs;
}

std::string number(double value) { std::ostringstream out; out << std::fixed << std::setprecision(6) << value; return out.str(); }
std::string json_number(double value) { std::ostringstream out; out << std::setprecision(17) << value; return out.str(); }
std::string vector_text(const Vec& values) { std::string out{"["}; for (size_t i = 0; i < values.size(); ++i) { if (i) out += ","; out += number(values[i]); } return out + "]"; }
std::string json_vec(const Vec& values) { std::string out{"["}; for (size_t i = 0; i < values.size(); ++i) { if (i) out += ","; out += json_number(values[i]); } return out + "]"; }
std::string json_ints(const std::vector<int>& values) { std::string out{"["}; for (size_t i = 0; i < values.size(); ++i) { if (i) out += ","; out += std::to_string(values[i]); } return out + "]"; }
std::string context_text(const std::vector<int>& ids) { return "[" + TOKENS.at(ids.at(0)) + "," + TOKENS.at(ids.at(1)) + "]"; }
std::string pair_text(const Pair& pair) {
    std::string future;
    for (int id : pair.future) { if (!future.empty()) future += ","; future += TOKENS.at(id); }
    return context_text(pair.context) + "->" + TOKENS.at(pair.target) + " future_excluded=[" + future + "]";
}
std::string json_mat(const Mat& matrix) { std::string out{"["}; for (size_t i = 0; i < matrix.size(); ++i) { if (i) out += ","; out += json_vec(matrix[i]); } return out + "]"; }
std::string json_dot_products(const std::vector<DotProduct>& products) {
    std::string out{"["};
    for (size_t j = 0; j < products.size(); ++j) {
        if (j) out += ",";
        const DotProduct& column = products[j];
        out += "{\"output_id\":" + std::to_string(column.output_id) + ",\"terms\":[";
        for (size_t i = 0; i < column.terms.size(); ++i) {
            if (i) out += ",";
            const Term& term = column.terms[i];
            out += "{\"left\":" + json_number(term.left) + ",\"right\":" + json_number(term.right) + ",\"product\":" + json_number(term.product) + "}";
        }
        out += "],\"partial_sums\":" + json_vec(column.partial_sums) + ",\"result\":" + json_number(column.result) + "}";
    }
    return out + "]";
}

std::string display() {
    const Forward ab = forward({0, 1});
    const Forward ba = forward({1, 0});
    const Forward ca = forward({2, 0});
    const std::vector<Pair> pairs = build_training_pairs();
    const Vec average_ab{(E[0][0] + E[1][0]) / 2.0, (E[0][1] + E[1][1]) / 2.0};
    const Vec average_ba{(E[1][0] + E[0][0]) / 2.0, (E[1][1] + E[0][1]) / 2.0};
    const bool same = average_ab == average_ba;
    const double softmax_sum = std::accumulate(ab.p.begin(), ab.p.end(), 0.0);
    std::ostringstream out;
    out << "contract E=" << E.size() << "x" << E.front().size() << " h=1x" << W.size() << " W=" << W.size() << "x" << W.front().size() << " context_length=2\n";
    out << context_text(ab.context) << " -> h=" << vector_text(ab.h) << " z=" << vector_text(ab.z) << "\n";
    out << context_text(ba.context) << " -> h=" << vector_text(ba.h) << " z=" << vector_text(ba.z) << "\n";
    out << "order_preserved=" << (same ? "true" : "false") << " average_ab=average_ba=" << vector_text(average_ab) << "\n";
    out << "stable_softmax_sum=" << number(softmax_sum) << " prediction_ab=" << TOKENS.at(ab.prediction) << "\n";
    out << "pair_0=" << pair_text(pairs.at(0)) << "\n";
    out << "pair_1=" << pair_text(pairs.at(1)) << "\n";
    out << "transfer=" << context_text(ca.context) << "->h=" << vector_text(ca.h) << " z=" << vector_text(ca.z) << "\n";
    out << "p_ab=" << vector_text(ab.p) << " p_ba=" << vector_text(ba.p) << " p_transfer=" << vector_text(ca.p) << "\n";
    return out.str();
}

std::string trace_json() {
    const Forward ab = forward({0, 1});
    const Forward ba = forward({1, 0});
    const Forward ca = forward({2, 0});
    const std::vector<Pair> pairs = build_training_pairs();
    const Vec average_ab{(E[0][0] + E[1][0]) / 2.0, (E[0][1] + E[1][1]) / 2.0};
    const Vec average_ba{(E[1][0] + E[0][0]) / 2.0, (E[1][1] + E[0][1]) / 2.0};
    const double stable_sum = std::accumulate(ab.p.begin(), ab.p.end(), 0.0);
    std::ostringstream out;
    out << "{\"contract\":{\"tokens\":[\"a\",\"b\",\"c\"],\"E\":" << json_mat(E) << ",\"W\":" << json_mat(W) << ",\"context_length\":2,\"embedding_dim\":2,\"hidden_width\":4,\"vocab_size\":3,\"window\":2},";
    auto emit_forward = [&](const char* name, const Forward& f) { out << "\"" << name << "\":{\"context_ids\":" << json_ints(f.context) << ",\"h\":" << json_vec(f.h) << ",\"dot_products\":" << json_dot_products(f.dot_products) << ",\"z\":" << json_vec(f.z) << ",\"p\":" << json_vec(f.p) << ",\"prediction_id\":" << f.prediction << "},"; };
    emit_forward("main", ab); emit_forward("reverse", ba); emit_forward("transfer", ca);
    out << "\"average\":{\"ab\":" << json_vec(average_ab) << ",\"ba\":" << json_vec(average_ba) << ",\"same\":" << (average_ab == average_ba ? "true" : "false") << "},\"training_pairs\":[";
    for (size_t i = 0; i < pairs.size(); ++i) {
        if (i) out << ",";
        out << "{\"context\":[\"" << TOKENS.at(pairs[i].context[0]) << "\",\"" << TOKENS.at(pairs[i].context[1]) << "\"],\"context_ids\":" << json_ints(pairs[i].context) << ",\"target\":\"" << TOKENS.at(pairs[i].target) << "\",\"target_id\":" << pairs[i].target << ",\"future_tokens_excluded\":[";
        for (size_t j = 0; j < pairs[i].future.size(); ++j) { if (j) out << ","; out << "\"" << TOKENS.at(pairs[i].future[j]) << "\""; }
        out << "]}";
    }
    out << "],\"stable_softmax_sum\":" << json_number(stable_sum) << "}";
    return out.str();
}

int main(int argc, char** argv) { if (argc > 1 && std::string(argv[1]) == "--trace") std::cout << trace_json() << "\n"; else std::cout << display(); }
