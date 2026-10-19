#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Vec = std::vector<double>;
using Mat = std::vector<Vec>;

const double LEARNING_RATE = 0.3;
const double EPSILON = 1e-6;
const int TARGET_ID = 2;
const int INPUT_ID = 1;

void validate(const Mat& w, const Mat& e, int input_id, int target, double lr) {
    if (w.size() != 2 || w[0].size() != 3 || w[1].size() != 3) throw std::invalid_argument("W shape");
    if (e.size() != 3 || e[0].size() != 2 || e[1].size() != 2 || e[2].size() != 2) throw std::invalid_argument("E shape");
    for (const auto& row : w) for (double x : row) if (!std::isfinite(x)) throw std::invalid_argument("W finite");
    for (const auto& row : e) for (double x : row) if (!std::isfinite(x)) throw std::invalid_argument("E finite");
    if (input_id < 0 || input_id >= 3) throw std::invalid_argument("input_id");
    if (target < 0 || target >= 3) throw std::invalid_argument("target_id");
    if (!std::isfinite(lr) || lr < 0) throw std::invalid_argument("learning_rate");
}

Vec vector_for(const Mat& e, int input_id) {
    if (input_id < 0 || input_id >= 3) throw std::invalid_argument("input_id");
    return e[input_id];
}

Vec logits(const Vec& h, const Mat& w) {
    if (h.size() != 2 || w.size() != 2 || w[0].size() != 3 || w[1].size() != 3) throw std::invalid_argument("shape");
    Vec z(3, 0.0);
    for (int j = 0; j < 3; ++j) for (int i = 0; i < 2; ++i) z[j] += h[i] * w[i][j];
    return z;
}

Vec softmax(const Vec& z) {
    if (z.size() != 3) throw std::invalid_argument("logits");
    double top = z[0];
    for (double x : z) { if (!std::isfinite(x)) throw std::invalid_argument("logits finite"); top = std::max(top, x); }
    Vec ex(3);
    double total = 0.0;
    for (int j = 0; j < 3; ++j) { ex[j] = std::exp(z[j] - top); total += ex[j]; }
    for (double& x : ex) x /= total;
    return ex;
}

struct Forward { Vec z, p, g; double loss; };

Forward forward(const Vec& h, const Mat& w, int target) {
    Vec z = logits(h, w);
    Vec p = softmax(z);
    Vec g = p;
    g[target] -= 1.0;
    return {z, p, g, -std::log(p[target])};
}

Vec input_gradient(const Mat& w, const Vec& g) {
    Vec dh(2, 0.0);
    for (int i = 0; i < 2; ++i) for (int j = 0; j < 3; ++j) dh[i] += w[i][j] * g[j];
    return dh;
}

Mat dE_for(int input_id, const Vec& dh) {
    Mat d(3, Vec(2, 0.0));
    d[input_id] = dh;
    return d;
}

Mat update_embedding(const Mat& e, int input_id, const Vec& dh, double lr) {
    Mat updated = e;
    for (int i = 0; i < 2; ++i) updated[input_id][i] -= lr * dh[i];
    return updated;
}

double loss_from(const Vec& h, const Mat& w, int target) { return forward(h, w, target).loss; }

Vec finite_difference(const Mat& e, int input_id, const Mat& w, int target) {
    Vec result(2);
    for (int i = 0; i < 2; ++i) {
        Mat plus = e, minus = e;
        plus[input_id][i] += EPSILON;
        minus[input_id][i] -= EPSILON;
        result[i] = (loss_from(vector_for(plus, input_id), w, target) - loss_from(vector_for(minus, input_id), w, target)) / (2.0 * EPSILON);
    }
    return result;
}

struct Calc {
    Mat w, e, dE, ePrime;
    Vec h, z, p, g, dh, finiteDiff, hPrime, zPrime, pPrime, gPrime;
    int inputId, targetId, selectedRow;
    double lr, loss, lossPrime;
};

Calc calculate(const Mat& w, const Mat& e, int input_id, int target, double lr) {
    validate(w, e, input_id, target, lr);
    Vec h = vector_for(e, input_id);
    Forward initial = forward(h, w, target);
    Vec dh = input_gradient(w, initial.g);
    Mat dE = dE_for(input_id, dh);
    Mat ePrime = update_embedding(e, input_id, dh, lr);
    Vec hPrime = vector_for(ePrime, input_id);
    Forward updated = forward(hPrime, w, target);
    return {w, e, dE, ePrime, h, initial.z, initial.p, initial.g, dh, finite_difference(e, input_id, w, target), hPrime, updated.z, updated.p, updated.g, input_id, target, input_id, lr, initial.loss, updated.loss};
}

std::string fmt(double x) { std::ostringstream out; out << std::fixed << std::setprecision(12) << x; return out.str(); }
std::string vec(const Vec& v) { std::string out = "["; for (size_t i = 0; i < v.size(); ++i) { if (i) out += ","; out += fmt(v[i]); } return out + "]"; }
std::string mat(const Mat& m) { std::string out = "["; for (size_t i = 0; i < m.size(); ++i) { if (i) out += ";"; out += vec(m[i]).substr(1, vec(m[i]).size() - 2); } return out + "]"; }

Mat baseW() { return {{-0.1, -0.1, 0.2}, {-0.2, -0.2, 0.4}}; }
Mat baseE() { return {{0.0, 1.0}, {1.0, 2.0}, {-1.0, 1.0}}; }

void print_default(const Calc& main, const Calc& transfer, const Vec& zeroWDh, const Vec& zeroInputDh) {
    std::cout << "EMBEDDING_INPUT_ROW_UPDATE\n";
    std::cout << "W=" << mat(main.w) << " E=" << mat(main.e) << "\n";
    std::cout << "input_id=1 h=" << vec(main.h) << " target_id=2 lr=" << fmt(main.lr) << "\n";
    std::cout << "z=" << vec(main.z) << " p=" << vec(main.p) << " loss=" << fmt(main.loss) << "\n";
    std::cout << "g=" << vec(main.g) << " dh=" << vec(main.dh) << " dE=" << mat(main.dE) << "\n";
    std::cout << "finite_difference=" << vec(main.finiteDiff) << "\n";
    std::cout << "E_prime=" << mat(main.ePrime) << " h_prime=" << vec(main.hPrime) << "\n";
    std::cout << "z_prime=" << vec(main.zPrime) << " p_prime=" << vec(main.pPrime) << " loss_prime=" << fmt(main.lossPrime) << "\n";
    std::cout << "transfer_input_id=0 h=" << vec(transfer.h) << " z=" << vec(transfer.z) << " dh=" << vec(transfer.dh) << "\n";
    std::cout << "zero_W_dh=" << vec(zeroWDh) << " zero_input_dh=" << vec(zeroInputDh) << "\n";
}

std::string jsonVec(const Vec& v) { return vec(v); }
std::string jsonMat(const Mat& m) { std::string out = "["; for (size_t i = 0; i < m.size(); ++i) { if (i) out += ","; out += jsonVec(m[i]); } return out + "]"; }
std::string jsonCalc(const Calc& c) {
    std::ostringstream o;
    o << "{\"w\":" << jsonMat(c.w) << ",\"e\":" << jsonMat(c.e) << ",\"input_id\":" << c.inputId << ",\"target_id\":" << c.targetId << ",\"learning_rate\":" << fmt(c.lr) << ",\"selected_row\":" << c.selectedRow;
    o << ",\"h\":" << jsonVec(c.h) << ",\"initial\":{\"z\":" << jsonVec(c.z) << ",\"p\":" << jsonVec(c.p) << ",\"loss\":" << fmt(c.loss) << ",\"g\":" << jsonVec(c.g) << "}";
    o << ",\"dh\":" << jsonVec(c.dh) << ",\"dE\":" << jsonMat(c.dE) << ",\"finite_difference\":" << jsonVec(c.finiteDiff) << ",\"E_prime\":" << jsonMat(c.ePrime) << ",\"h_prime\":" << jsonVec(c.hPrime);
    o << ",\"updated\":{\"z\":" << jsonVec(c.zPrime) << ",\"p\":" << jsonVec(c.pPrime) << ",\"loss\":" << fmt(c.lossPrime) << ",\"g\":" << jsonVec(c.gPrime) << "}}";
    return o.str();
}

int main(int argc, char** argv) {
    Mat w = baseW(), e = baseE();
    Calc main = calculate(w, e, INPUT_ID, TARGET_ID, LEARNING_RATE);
    Calc transfer = calculate(w, e, 0, TARGET_ID, LEARNING_RATE);
    Mat zeroW{{0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}};
    Calc zero = calculate(zeroW, e, INPUT_ID, TARGET_ID, LEARNING_RATE);
    Mat zeroE{{0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}};
    Calc zeroInput = calculate(w, zeroE, INPUT_ID, TARGET_ID, LEARNING_RATE);
    if (argc > 1 && std::string(argv[1]) == "--trace") {
        std::cout << "{\"contract\":{\"W\":" << jsonMat(main.w) << ",\"E\":" << jsonMat(main.e) << ",\"input_id\":1,\"target_id\":2,\"learning_rate\":" << fmt(LEARNING_RATE) << ",\"selected_row\":1,\"bias\":false},";
        std::cout << "\"main\":" << jsonCalc(main) << ",\"transfer\":" << jsonCalc(transfer);
        std::cout << ",\"zero_W\":{\"dh\":" << jsonVec(zero.dh) << ",\"dE\":" << jsonMat(zero.dE) << ",\"g\":" << jsonVec(zero.g) << "}";
        std::cout << ",\"zero_input\":{\"dh\":" << jsonVec(zeroInput.dh) << ",\"dE\":" << jsonMat(zeroInput.dE) << "}}\n";
    } else {
        print_default(main, transfer, zero.dh, zeroInput.dh);
    }
}
