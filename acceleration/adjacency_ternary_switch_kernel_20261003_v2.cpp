// SOURCE_ONLY proposal by /root/structural, 2026-10-03T13:34:14+00:00.
// No main, parser, RNG, annealer, compiler invocation or execution is supplied.
// New code: no historical engine/checker gate approves this implementation.
#include <array>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace adjacency_ternary_switch_v1 {

constexpr std::int64_t scalar_weight = 819820;
constexpr const char* objective = "SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1";
constexpr const char* move_kernel = "FOUR_DISTINCT_VERTEX_EDGE_SWITCH_V1";

static void need(bool condition, const char* diagnostic) {
    if (!condition) throw std::runtime_error(diagnostic);
}

struct Metrics {
    std::int64_t f3 = 0, e_lambda = 0, e_mu = 0;
    std::array<std::int64_t, 3> residue_population{{0, 0, 0}};
    std::int64_t energy() const { return e_lambda + e_mu; }
    std::int64_t scalar() const { return scalar_weight * f3 + energy(); }
};

struct Role {
    int u, v, x, y, orientation;
};

struct SwitchRecord {
    Role role;
    bool valid = false;
    std::string diagnostic;
    int affected_unordered_pairs = 0;
    Metrics before, after;
    std::int64_t delta_f3 = 0, delta_lambda = 0, delta_mu = 0;
    std::int64_t delta_energy = 0, delta_scalar = 0;
};

class Graph {
public:
    // Generic fixtures: n<=99, 0<=k<=14. The scientific domain is exactly99/14.
    Graph(int n, int k, const std::vector<int>& flat_adjacency)
        : n_(n), k_(k), a_(flat_adjacency) {
        need(n_ >= 4 && n_ <= 99 && k_ >= 0 && k_ <= 14 && k_ < n_, "GRAPH_DIMENSIONS");
        need(a_.size() == static_cast<std::size_t>(n_) * n_, "GRAPH_SHAPE");
        for (int u = 0; u < n_; ++u) {
            int degree = 0;
            for (int v = 0; v < n_; ++v) {
                need(A(u, v) == 0 || A(u, v) == 1, "GRAPH_BINARY");
                need(A(u, v) == A(v, u), "GRAPH_SYMMETRY");
                degree += A(u, v);
            }
            need(A(u, u) == 0, "GRAPH_DIAGONAL");
            need(degree == k_, "GRAPH_DEGREE");
        }
        c_.assign(a_.size(), 0);
        for (int u = 0; u < n_; ++u)
            for (int v = 0; v < n_; ++v)
                for (int w = 0; w < n_; ++w) C(u, v) += A(u, w) * A(w, v);
        // C is the true full product, including diagonal k, not a zero-diagonal cache.
        for (int u = 0; u < n_; ++u)
            for (int v = u + 1; v < n_; ++v) add_pair(metrics_, C(u, v), A(u, v), 1);
    }

    int n() const { return n_; }
    int degree() const { return k_; }
    const std::vector<int>& adjacency() const { return a_; }
    const std::vector<int>& full_product_cache() const { return c_; }
    const Metrics& metrics() const { return metrics_; }

    std::vector<std::pair<int, int>> canonical_edges() const {
        std::vector<std::pair<int, int>> edges;
        for (int u = 0; u < n_; ++u)
            for (int v = u + 1; v < n_; ++v) if (A(u, v)) edges.emplace_back(u, v);
        return edges;
    }

    // Invalid roles leave this Graph unchanged. Valid roles commit even if score worsens.
    // An eventual driver must evaluate on a copy before deciding to retain a proposal.
    SwitchRecord apply(const Role& r) {
        SwitchRecord record{};
        record.role = r;
        record.before = record.after = metrics_;
        const char* rejection = role_rejection(r);
        if (rejection) { record.diagnostic = rejection; return record; }

        Graph next = *this; // Atomic proposal boundary; copy cost is intentionally explicit.
        const std::array<int, 4> vertices{{r.u, r.v, r.x, r.y}};
        std::vector<std::pair<int, int>> affected;
        for (int p = 0; p < n_; ++p) {
            for (int q = p + 1; q < n_; ++q) {
                bool touches = false;
                for (const int v : vertices) touches = touches || p == v || q == v;
                if (touches) affected.emplace_back(p, q);
            }
        }
        need(affected.size() == static_cast<std::size_t>(4 * n_ - 10), "AFFECTED_PAIR_COUNT");
        for (const auto& pair : affected)
            add_pair(next.metrics_, C(pair.first, pair.second), A(pair.first, pair.second), -1);

        // Every toggle uses the CURRENT adjacency, including preceding toggles.
        next.toggle(r.u, r.v, -1);
        next.toggle(r.x, r.y, -1);
        if (r.orientation == 0) {
            next.toggle(r.u, r.x, 1);
            next.toggle(r.v, r.y, 1);
        } else {
            next.toggle(r.u, r.y, 1);
            next.toggle(r.v, r.x, 1);
        }
        for (const auto& pair : affected)
            add_pair(next.metrics_, next.C(pair.first, pair.second), next.A(pair.first, pair.second), 1);
        for (const int v : vertices) {
            int degree = 0;
            for (int w = 0; w < n_; ++w) degree += next.A(v, w);
            need(degree == k_ && next.C(v, v) == k_, "FINAL_SWITCH_DEGREE");
        }
        need(next.metrics_.f3 >= 0 && next.metrics_.energy() >= 0, "FINAL_METRICS_DOMAIN");
        record.valid = true;
        record.diagnostic = "VALID_SWITCH_PENDING_INDEPENDENT_CHECK";
        record.affected_unordered_pairs = static_cast<int>(affected.size());
        record.after = next.metrics_;
        record.delta_f3 = record.after.f3 - record.before.f3;
        record.delta_lambda = record.after.e_lambda - record.before.e_lambda;
        record.delta_mu = record.after.e_mu - record.before.e_mu;
        record.delta_energy = record.after.energy() - record.before.energy();
        record.delta_scalar = record.after.scalar() - record.before.scalar();
        *this = std::move(next);
        return record;
    }

private:
    int n_, k_;
    std::vector<int> a_, c_;
    Metrics metrics_;
    int A(int u, int v) const { return a_[static_cast<std::size_t>(u) * n_ + v]; }
    int C(int u, int v) const { return c_[static_cast<std::size_t>(u) * n_ + v]; }
    int& A(int u, int v) { return a_[static_cast<std::size_t>(u) * n_ + v]; }
    int& C(int u, int v) { return c_[static_cast<std::size_t>(u) * n_ + v]; }

    static void add_pair(Metrics& m, int cn, int edge, int multiplier) {
        const std::int64_t residual = static_cast<std::int64_t>(cn) + edge - 2;
        const int residue = static_cast<int>((residual % 3 + 3) % 3);
        m.f3 += multiplier * (residue != 0 ? 1 : 0);
        (edge ? m.e_lambda : m.e_mu) += multiplier * residual * residual;
        m.residue_population[residue] += multiplier;
    }

    const char* role_rejection(const Role& r) const {
        for (const int v : {r.u, r.v, r.x, r.y}) if (v < 0 || v >= n_) return "ROLE_VERTEX_RANGE";
        if (r.orientation != 0 && r.orientation != 1) return "ROLE_ORIENTATION";
        if (!(r.u < r.v && r.x < r.y && std::pair<int, int>(r.u, r.v) < std::pair<int, int>(r.x, r.y)))
            return "ROLE_CANONICAL_OLD_EDGES";
        if (r.u == r.x || r.u == r.y || r.v == r.x || r.v == r.y) return "ROLE_FOUR_DISTINCT_VERTICES";
        if (!A(r.u, r.v) || !A(r.x, r.y)) return "ROLE_OLD_EDGE_ABSENT";
        if (r.orientation == 0 ? (A(r.u, r.x) || A(r.v, r.y)) : (A(r.u, r.y) || A(r.v, r.x)))
            return "ROLE_NEW_EDGE_PRESENT";
        return nullptr;
    }

    void toggle(int a, int b, int sign) {
        need(a != b && (sign == 1 || sign == -1), "TOGGLE_ROLE");
        need((sign == 1 && A(a, b) == 0) || (sign == -1 && A(a, b) == 1), "TOGGLE_EDGE_DOMAIN");
        for (int w = 0; w < n_; ++w) if (w != a && w != b) {
            const int ca = C(a, w) + sign * A(b, w);
            const int cb = C(b, w) + sign * A(a, w);
            need(ca >= 0 && ca <= 99 && cb >= 0 && cb <= 99, "TOGGLE_CACHE_RANGE");
            C(a, w) = C(w, a) = ca;
            C(b, w) = C(w, b) = cb;
        }
        C(a, a) += sign;
        C(b, b) += sign;
        A(a, b) = A(b, a) = (sign == 1 ? 1 : 0);
        // The off-diagonal C(a,b) is unchanged by this one toggle in a loopless graph.
    }
};

} // namespace adjacency_ternary_switch_v1
