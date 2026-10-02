#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Triple = std::array<int, 3>;
using Clock = std::chrono::steady_clock;
static constexpr int MAX_N = 99;
static void need(bool value, const std::string &message) { if (!value) throw std::runtime_error(message); }
static std::uint64_t rotl(std::uint64_t x, int k) { return (x << k) | (x >> (64-k)); }

// Explicit reproducible RNG: seed expansion and transition are part of this version.
struct RNG {
    std::array<std::uint64_t, 4> s{};
    explicit RNG(std::uint64_t seed) {
        for (auto &v : s) {
            seed += UINT64_C(0x9e3779b97f4a7c15);
            std::uint64_t z = seed;
            z = (z ^ (z >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
            z = (z ^ (z >> 27)) * UINT64_C(0x94d049bb133111eb);
            v = z ^ (z >> 31);
        }
    }
    std::uint64_t next() {
        const std::uint64_t result = rotl(s[1] * 5, 7) * 9;
        const std::uint64_t t = s[1] << 17;
        s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3];
        s[2] ^= t; s[3] = rotl(s[3], 45);
        return result;
    }
};

struct Graph {
    int n, degree;
    std::vector<Triple> triples;
    int a[MAX_N][MAX_N]{};
    int cn[MAX_N][MAX_N]{};
    std::array<std::uint64_t, 2> masks[MAX_N]{};
    std::int64_t energy = 0;
    Graph(int vertices, int hyperdegree, std::vector<Triple> rows) : n(vertices), degree(hyperdegree), triples(std::move(rows)) {
        need(n >= 3 && n <= MAX_N && degree > 0 && degree * 2 < n, "valid domain size/degree");
        need(static_cast<int>(triples.size()) * 3 == n * degree, "exact triple count");
        std::vector<int> counts(n, 0);
        for (const auto &r : triples) {
            need(r[0] >= 0 && r[0] < n && r[1] >= 0 && r[1] < n && r[2] >= 0 && r[2] < n, "vertex range");
            need(r[0] != r[1] && r[0] != r[2] && r[1] != r[2], "three distinct vertices");
            for (int x : r) ++counts[x];
            for (int i=0; i<3; ++i) for (int j=i+1; j<3; ++j) {
                int u=r[i], v=r[j]; need(!a[u][v], "linear hypergraph pair multiplicity");
                a[u][v]=a[v][u]=1;
                masks[u][v/64] |= UINT64_C(1) << (v%64);
                masks[v][u/64] |= UINT64_C(1) << (u%64);
            }
        }
        for (int i=0; i<n; ++i) need(counts[i] == degree, "exact point degree");
        full_initialize();
    }
    int full_cn(int u, int v) const {
        return __builtin_popcountll(masks[u][0] & masks[v][0]) +
               __builtin_popcountll(masks[u][1] & masks[v][1]);
    }
    void full_initialize() {
        energy=0;
        for (int u=0; u<n; ++u) for (int v=u+1; v<n; ++v) {
            cn[u][v]=cn[v][u]=full_cn(u,v);
            std::int64_t r=cn[u][v]+a[u][v]-2; energy += r*r;
        }
    }
    void verify() const {
        std::int64_t total=0;
        for (int u=0; u<n; ++u) {
            need(a[u][u] == 0, "zero adjacency diagonal");
            int d=0;
            for (int v=0; v<n; ++v) { need(a[u][v] == a[v][u], "symmetric adjacency"); d += a[u][v]; }
            need(d == 2*degree, "point graph regularity");
            for (int v=u+1; v<n; ++v) {
                const int c=full_cn(u,v);
                need(c == cn[u][v] && c == cn[v][u], "exact common-neighbor cache");
                std::int64_t r=c+a[u][v]-2; total += r*r;
            }
        }
        need(total == energy, "exact incremental energy");
        Graph reconstructed(n,degree,triples);
        need(reconstructed.energy == energy, "raw triples reconstruct current energy");
        for (int u=0; u<n; ++u) for (int v=0; v<n; ++v) need(reconstructed.a[u][v] == a[u][v], "raw triples reconstruct adjacency");
    }
    void cn_change(int u, int v, int delta) {
        std::int64_t residual=cn[u][v]+a[u][v]-2;
        energy += 2*residual*delta + delta*delta;
        cn[u][v] += delta; cn[v][u] += delta;
    }
    void toggle(int u, int v, int delta) {
        need((delta == 1 && a[u][v] == 0) || (delta == -1 && a[u][v] == 1), "edge toggle precondition");
        for (int w=0; w<n; ++w) if (w != u && w != v) {
            if (a[v][w]) cn_change(u,w,delta);
            if (a[u][w]) cn_change(v,w,delta);
        }
        std::int64_t residual=cn[u][v]+a[u][v]-2;
        energy += 2*residual*delta + delta*delta;
        a[u][v] += delta; a[v][u] += delta;
        masks[u][v/64] ^= UINT64_C(1) << (v%64);
        masks[v][u/64] ^= UINT64_C(1) << (u%64);
    }
};

struct Options {
    std::string fixture="target99", out, resume;
    std::uint64_t seed=99032000, steps=0, mix_steps=10000, schedule_steps=1000000;
    std::uint64_t verify_every=100000, checkpoint_every=100000, trace_max=0, trace_stride=0;
    double start=20, end=0.5, seconds=30, checkpoint_seconds=15;
    bool forced=false, stop_zero=false;
};

struct State {
    Graph current;
    std::vector<Triple> best;
    std::int64_t best_energy;
    RNG rng;
    std::uint64_t step=0, admissible=0, accepted=0, best_updates=0;
    Options config;
    State(Graph graph, Options options) : current(std::move(graph)), best(current.triples),
        best_energy(current.energy), rng(options.seed), config(std::move(options)) {}
};

static std::vector<Triple> initial(const std::string &fixture) {
    std::vector<Triple> rows;
    if (fixture == "target99") {
        for (int x=0; x<33; ++x) rows.push_back({x,x+33,x+66});
        for (int x=0; x<99; ++x) rows.push_back({x,(x+1)%99,(x+4)%99});
        for (int x=0; x<99; ++x) rows.push_back({x,(x+7)%99,(x+18)%99});
    } else {
        need(fixture == "rook9", "explicit known fixture");
        for (int x=0; x<3; ++x) rows.push_back({3*x,3*x+1,3*x+2});
        for (int x=0; x<3; ++x) rows.push_back({x,x+3,x+6});
    }
    return rows;
}

static void write_state(const std::filesystem::path &path, const State &s) {
    need(!std::filesystem::exists(path), "immutable fresh checkpoint");
    std::ofstream f(path); need(static_cast<bool>(f), "checkpoint open"); f << std::setprecision(17);
    f << "HYPERGRAPH_ANNEAL_STATE_V1\n" << "n " << s.current.n << "\ndegree " << s.current.degree;
    f << "\nseed " << s.config.seed << "\nmix_steps " << s.config.mix_steps << "\nschedule_steps " << s.config.schedule_steps;
    f << "\nt_start " << s.config.start << "\nt_end " << s.config.end << "\nforced " << s.config.forced;
    f << "\nstep " << s.step << "\nadmissible " << s.admissible << "\naccepted " << s.accepted << "\nbest_updates " << s.best_updates;
    f << "\nenergy " << s.current.energy << "\nbest_energy " << s.best_energy << "\nrng";
    for (auto x : s.rng.s) f << ' ' << x;
    f << "\ncurrent " << s.current.triples.size() << '\n';
    for (const auto &r : s.current.triples) f << r[0] << ' ' << r[1] << ' ' << r[2] << '\n';
    f << "best " << s.best.size() << '\n'; for (const auto &r : s.best) f << r[0] << ' ' << r[1] << ' ' << r[2] << '\n';
    f << "cn " << s.current.n*(s.current.n-1)/2 << '\n';
    for (int u=0; u<s.current.n; ++u) for (int v=u+1; v<s.current.n; ++v) f << s.current.cn[u][v] << '\n';
    f << "END\n"; f.flush(); need(static_cast<bool>(f), "complete checkpoint write");
}

template<class T> static void field(std::istream &f, const std::string &name, T &value) {
    std::string actual; need(static_cast<bool>(f >> actual >> value) && actual == name, "checkpoint field "+name);
}
static State load_state(const std::string &path, const Options &runtime) {
    std::ifstream f(path); std::string tag; f >> tag; need(tag == "HYPERGRAPH_ANNEAL_STATE_V1", "checkpoint version");
    int n, degree; Options c=runtime;
    field(f,"n",n); field(f,"degree",degree); field(f,"seed",c.seed); field(f,"mix_steps",c.mix_steps);
    field(f,"schedule_steps",c.schedule_steps); field(f,"t_start",c.start); field(f,"t_end",c.end); field(f,"forced",c.forced);
    need((n == 99 && degree == 7) || (n == 9 && degree == 2), "exact target or positive control domain");
    need(std::isfinite(c.start) && std::isfinite(c.end) && c.start >= 0 && c.end >= 0 && c.start <= 1000 && c.end <= 1000 && c.schedule_steps > 0, "bounded checkpoint temperature schedule");
    std::uint64_t step, admissible, accepted, updates;
    std::int64_t energy, best_energy;
    field(f,"step",step); field(f,"admissible",admissible); field(f,"accepted",accepted); field(f,"best_updates",updates);
    field(f,"energy",energy); field(f,"best_energy",best_energy);
    std::array<std::uint64_t,4> rng{}; f >> tag; need(tag == "rng", "rng tag"); for (auto &x:rng) need(static_cast<bool>(f >> x), "rng integer");
    need((rng[0]|rng[1]|rng[2]|rng[3]) != 0, "nonzero RNG state");
    int count; field(f,"current",count); need(count == n*degree/3, "current triple population");
    std::vector<Triple> current(count); for (auto &r:current) for (auto &x:r) need(static_cast<bool>(f >> x), "current triple parse");
    State s(Graph(n,degree,current),c);
    field(f,"best",count); need(count == n*degree/3, "best triple population");
    std::vector<Triple> best(count); for (auto &r:best) for (auto &x:r) need(static_cast<bool>(f >> x), "best triple parse");
    Graph b(n,degree,best);
    need(s.current.energy == energy && b.energy == best_energy && best_energy <= energy, "checkpoint exact current/best scores");
    field(f,"cn",count); need(count == n*(n-1)/2, "cache population");
    for (int u=0; u<n; ++u) for (int v=u+1; v<n; ++v) { int x; need(static_cast<bool>(f >> x) && x == s.current.cn[u][v], "checkpoint exact CN cache"); }
    f >> tag; need(tag == "END" && !(f >> tag), "checkpoint complete exact record");
    need(accepted <= admissible && admissible <= step && updates <= accepted, "checkpoint counter consistency");
    s.best=best; s.best_energy=best_energy; s.rng.s=rng; s.step=step; s.admissible=admissible; s.accepted=accepted; s.best_updates=updates;
    return s;
}

static double temperature(const State &s) {
    std::uint64_t elapsed=s.step > s.config.mix_steps ? s.step-s.config.mix_steps : 0;
    double fraction=std::min(1.0,static_cast<double>(elapsed)/static_cast<double>(s.config.schedule_steps));
    return s.config.start + (s.config.end-s.config.start)*fraction;
}

static void save_adjacency(const std::filesystem::path &path, const Graph &g) {
    need(!std::filesystem::exists(path), "immutable adjacency"); std::ofstream f(path); f << g.n << '\n';
    for (int u=0; u<g.n; ++u) { for (int v=0; v<g.n; ++v) f << g.a[u][v]; f << '\n'; }
    f.flush(); need(static_cast<bool>(f), "complete adjacency write");
}

static Options parse(int argc,char **argv) {
    Options o;
    for (int i=1; i<argc; ++i) {
        std::string k=argv[i];
        if (k == "--forced") { o.forced=true; continue; }
        if (k == "--stop-at-zero") { o.stop_zero=true; continue; }
        need(i+1 < argc, "argument value"); std::string v=argv[++i];
        if (k == "--fixture") o.fixture=v; else if (k == "--out") o.out=v; else if (k == "--resume") o.resume=v;
        else if (k == "--seed") o.seed=std::stoull(v); else if (k == "--steps") o.steps=std::stoull(v);
        else if (k == "--mix-steps") o.mix_steps=std::stoull(v); else if (k == "--schedule-steps") o.schedule_steps=std::stoull(v);
        else if (k == "--verify-every") o.verify_every=std::stoull(v); else if (k == "--checkpoint-every") o.checkpoint_every=std::stoull(v);
        else if (k == "--trace-max") o.trace_max=std::stoull(v); else if (k == "--trace-stride") o.trace_stride=std::stoull(v);
        else if (k == "--temperature-start") o.start=std::stod(v); else if (k == "--temperature-end") o.end=std::stod(v);
        else if (k == "--seconds") o.seconds=std::stod(v); else if (k == "--checkpoint-seconds") o.checkpoint_seconds=std::stod(v);
        else need(false,"unknown argument "+k);
    }
    need(!o.out.empty() && std::isfinite(o.seconds) && o.seconds > 0 && o.seconds <= 21600, "out/time arguments");
    need(std::isfinite(o.start) && std::isfinite(o.end) && o.start >= 0 && o.end >= 0 && o.start <= 1000 && o.end <= 1000 && o.schedule_steps > 0,
         "explicit bounded temperature schedule");
    need(o.verify_every > 0 && o.checkpoint_every > 0 && o.checkpoint_seconds > 0 && std::isfinite(o.checkpoint_seconds), "checkpoint/verification intervals");
    return o;
}

int main(int argc,char **argv) {
    try {
        const auto started=Clock::now(); Options o=parse(argc,argv);
        need(!std::filesystem::exists(o.out), "fresh native output directory"); std::filesystem::create_directories(o.out);
        State s = o.resume.empty() ? State(Graph(o.fixture == "target99" ? 99 : 9,o.fixture == "target99" ? 7 : 2,initial(o.fixture)),o) : load_state(o.resume,o);
        s.current.verify(); const std::int64_t initial_energy=s.current.energy;
        write_state(std::filesystem::path(o.out)/"initial.state",s);
        std::ofstream trace(std::filesystem::path(o.out)/"moves.jsonl"); trace << std::setprecision(17);
        const std::uint64_t starting_step=s.step; std::uint64_t performed=0; auto last_checkpoint=Clock::now();
        std::string stop="REQUESTED_STEPS_COMPLETE";
        for (; performed < o.steps; ++performed) {
            if ((performed&1023) == 0) {
                double elapsed=std::chrono::duration<double>(Clock::now()-started).count();
                if (elapsed >= o.seconds) { stop="ALLOCATED_NATIVE_BUDGET_REACHED"; break; }
            }
            if (o.stop_zero && s.current.energy == 0) { stop="RAW_ZERO_PENDING_INDEPENDENT_SRG_VALIDATOR"; break; }
            const auto rng_before=s.rng.s;
            const int m=static_cast<int>(s.current.triples.size());
            const int ti=static_cast<int>(s.rng.next()%m);
            int tj=static_cast<int>(s.rng.next()%(m-1)); if (tj >= ti) ++tj;
            const int pi=static_cast<int>(s.rng.next()%3), pj=static_cast<int>(s.rng.next()%3);
            const auto t=s.current.triples[ti], q=s.current.triples[tj];
            bool disjoint=true; for (int x:t) for (int y:q) if (x == y) disjoint=false;
            int x=t[pi], y=q[pj], a=t[(pi+1)%3], b=t[(pi+2)%3], c=q[(pj+1)%3], d=q[(pj+2)%3];
            const bool absent=!s.current.a[y][a] && !s.current.a[y][b] && !s.current.a[x][c] && !s.current.a[x][d];
            const bool valid=disjoint && absent;
            const std::int64_t old_energy=s.current.energy;
            std::int64_t delta=0; std::uint64_t draw=0; bool accepted=false;
            const double temp=temperature(s); const bool mixing=s.step < s.config.mix_steps;
            const std::array<std::array<int,3>,8> edges={{{x,a,-1},{x,b,-1},{y,c,-1},{y,d,-1},{y,a,1},{y,b,1},{x,c,1},{x,d,1}}};
            if (valid) {
                ++s.admissible;
                for (auto e:edges) s.current.toggle(e[0],e[1],e[2]);
                delta=s.current.energy-old_energy;
                draw=s.rng.next(); double uniform=static_cast<double>(draw>>11)*0x1.0p-53;
                accepted=s.config.forced || mixing || delta <= 0 || (temp > 0 && uniform < std::exp(-static_cast<double>(delta)/temp));
                if (accepted) {
                    s.current.triples[ti][pi]=y; s.current.triples[tj][pj]=x; ++s.accepted;
                    if (s.current.energy < s.best_energy) { s.best_energy=s.current.energy; s.best=s.current.triples; ++s.best_updates; }
                } else {
                    for (auto it=edges.rbegin(); it!=edges.rend(); ++it) s.current.toggle((*it)[0],(*it)[1],-(*it)[2]);
                    need(s.current.energy == old_energy, "exact rejected-trade rollback");
                }
            }
            const bool log=performed < o.trace_max || (o.trace_stride && (s.step%o.trace_stride == 0));
            if (log) {
                auto proposed_t=t, proposed_q=q; proposed_t[pi]=y; proposed_q[pj]=x;
                trace << "{\"step\":" << s.step << ",\"ti\":" << ti << ",\"tj\":" << tj << ",\"pi\":" << pi << ",\"pj\":" << pj
                      << ",\"old_triples\":[[" << t[0] << ',' << t[1] << ',' << t[2] << "],[" << q[0] << ',' << q[1] << ',' << q[2] << "]]"
                      << ",\"proposed_triples\":[[" << proposed_t[0] << ',' << proposed_t[1] << ',' << proposed_t[2] << "],[" << proposed_q[0] << ',' << proposed_q[1] << ',' << proposed_q[2] << "]]"
                      << ",\"disjoint\":" << (disjoint?"true":"false") << ",\"new_pairs_absent\":" << (absent?"true":"false")
                      << ",\"admissible\":" << (valid?"true":"false") << ",\"accepted\":" << (accepted?"true":"false")
                      << ",\"mixing\":" << (mixing?"true":"false") << ",\"temperature\":" << temp
                      << ",\"delta\":" << delta << ",\"energy_before\":" << old_energy << ",\"energy_after\":" << s.current.energy
                      << ",\"best_energy\":" << s.best_energy << ",\"draw\":\"" << draw << "\",\"rng_before\":[";
                for (int i=0;i<4;++i) trace << (i?",":"") << '"' << rng_before[i] << '"';
                trace << "],\"rng_after\":["; for (int i=0;i<4;++i) trace << (i?",":"") << '"' << s.rng.s[i] << '"'; trace << "]}\n";
            }
            ++s.step;
            if (s.step%o.verify_every == 0) s.current.verify();
            double since=std::chrono::duration<double>(Clock::now()-last_checkpoint).count();
            if (s.step%o.checkpoint_every == 0 || since >= o.checkpoint_seconds) {
                s.current.verify(); write_state(std::filesystem::path(o.out)/("checkpoint_"+std::to_string(s.step)+".state"),s);
                last_checkpoint=Clock::now();
            }
        }
        s.current.verify(); Graph best(s.current.n,s.current.degree,s.best); best.verify();
        write_state(std::filesystem::path(o.out)/"final.state",s); save_adjacency(std::filesystem::path(o.out)/"best.adj",best);
        trace.flush(); need(static_cast<bool>(trace), "complete trace write");
        std::ofstream result(std::filesystem::path(o.out)/"result.json"); result << std::setprecision(17)
            << "{\"objective\":\"SRG_SQUARED_PAIR_RESIDUAL_V1\",\"n\":" << s.current.n << ",\"point_degree\":" << s.current.degree
            << ",\"triple_count\":" << s.current.triples.size() << ",\"initial_energy\":" << initial_energy << ",\"current_energy\":" << s.current.energy
            << ",\"best_energy\":" << s.best_energy << ",\"starting_step\":" << starting_step << ",\"ending_step\":" << s.step
            << ",\"proposals_this_invocation\":" << performed << ",\"admissible_total\":" << s.admissible << ",\"accepted_total\":" << s.accepted
            << ",\"best_updates_total\":" << s.best_updates << ",\"elapsed_seconds\":" << std::chrono::duration<double>(Clock::now()-started).count()
            << ",\"stop_reason\":\"" << stop << "\",\"target_resolution\":false,\"independent_approval\":false}\n";
        result.flush(); need(static_cast<bool>(result), "complete result write");
        std::cout << "NATIVE_RESULT_PRESERVED " << s.current.n << ' ' << s.current.energy << ' ' << s.best_energy << '\n';
        return 0;
    } catch (const std::exception &e) { std::cerr << e.what() << '\n'; return 2; }
}
