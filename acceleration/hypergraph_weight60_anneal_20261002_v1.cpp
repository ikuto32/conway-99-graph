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
static constexpr std::int64_t LAMBDA_WEIGHT = 60;
static constexpr const char *OBJECTIVE = "SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2";
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
    std::int64_t lambda_energy = 0, mu_energy = 0;
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
        energy=0; lambda_energy=mu_energy=0;
        for (int u=0; u<n; ++u) for (int v=u+1; v<n; ++v) {
            cn[u][v]=cn[v][u]=full_cn(u,v);
            std::int64_t r=cn[u][v]+a[u][v]-2;
            if (a[u][v]) lambda_energy+=r*r; else mu_energy+=r*r;
        }
        energy=LAMBDA_WEIGHT*lambda_energy+mu_energy;
    }
    void verify() const {
        std::int64_t el=0,em=0;
        for (int u=0; u<n; ++u) {
            need(a[u][u] == 0, "zero adjacency diagonal");
            int d=0;
            for (int v=0; v<n; ++v) { need(a[u][v] == a[v][u], "symmetric adjacency"); d += a[u][v]; }
            need(d == 2*degree, "point graph regularity");
            for (int v=u+1; v<n; ++v) {
                const int c=full_cn(u,v);
                need(c == cn[u][v] && c == cn[v][u], "exact common-neighbor cache");
                std::int64_t r=c+a[u][v]-2;
                if (a[u][v]) el+=r*r; else em+=r*r;
            }
        }
        need(el==lambda_energy && em==mu_energy && LAMBDA_WEIGHT*el+em==energy, "exact incremental weighted/component energies");
        Graph reconstructed(n,degree,triples);
        need(reconstructed.energy == energy, "raw triples reconstruct current energy");
        for (int u=0; u<n; ++u) for (int v=0; v<n; ++v) need(reconstructed.a[u][v] == a[u][v], "raw triples reconstruct adjacency");
    }
    void cn_change(int u, int v, int delta) {
        std::int64_t residual=cn[u][v]+a[u][v]-2;
        const std::int64_t change=2*residual*delta+delta*delta;
        if (a[u][v]) lambda_energy+=change; else mu_energy+=change;
        energy+=(a[u][v]?LAMBDA_WEIGHT:1)*change;
        cn[u][v] += delta; cn[v][u] += delta;
    }
    void toggle(int u, int v, int delta) {
        need((delta == 1 && a[u][v] == 0) || (delta == -1 && a[u][v] == 1), "edge toggle precondition");
        for (int w=0; w<n; ++w) if (w != u && w != v) {
            if (a[v][w]) cn_change(u,w,delta);
            if (a[u][w]) cn_change(v,w,delta);
        }
        // The toggled pair changes category; its common-neighbor count is fixed.
        const std::int64_t c=cn[u][v],old_lambda=a[u][v]?(c-1)*(c-1):0;
        const std::int64_t old_mu=a[u][v]?0:(c-2)*(c-2);
        const int new_a=a[u][v]+delta;
        const std::int64_t new_lambda=new_a?(c-1)*(c-1):0,new_mu=new_a?0:(c-2)*(c-2);
        lambda_energy+=new_lambda-old_lambda;mu_energy+=new_mu-old_mu;
        energy+=LAMBDA_WEIGHT*(new_lambda-old_lambda)+(new_mu-old_mu);
        a[u][v] += delta; a[v][u] += delta;
        masks[u][v/64] ^= UINT64_C(1) << (v%64);
        masks[v][u/64] ^= UINT64_C(1) << (u%64);
    }
};

struct Options {
    std::string fixture="target99", out, resume, import_weight6, import_select="current";
    std::uint64_t seed=99032000, steps=0, mix_steps=10000, schedule_steps=1000000;
    std::uint64_t verify_every=100000, checkpoint_every=100000, trace_max=0, trace_stride=0;
    double start=20, end=0.5, seconds=30, checkpoint_seconds=15;
    bool forced=false, stop_zero=false, emit_pair_costs=false;
};

struct FirstLambda0 {
    bool found=false;
    std::uint64_t step=0, admissible=0, accepted=0, best_updates=0;
    std::array<std::uint64_t,4> rng{};
    std::vector<Triple> current,best;
};

struct State {
    Graph current;
    std::vector<Triple> best;
    std::int64_t best_energy;
    RNG rng;
    std::uint64_t step=0, admissible=0, accepted=0, best_updates=0;
    Options config;
    FirstLambda0 first_lambda0;
    State(Graph graph, Options options) : current(std::move(graph)), best(current.triples),
        best_energy(current.energy), rng(options.seed), config(std::move(options)) {}
};

static void capture_first_lambda0(State &s, std::uint64_t completed_step) {
    if(s.first_lambda0.found || s.current.lambda_energy!=0)return;
    auto &r=s.first_lambda0;r.found=true;r.step=completed_step;r.admissible=s.admissible;
    r.accepted=s.accepted;r.best_updates=s.best_updates;r.rng=s.rng.s;
    r.current=s.current.triples;r.best=s.best;
}

static std::vector<Triple> initial(const std::string &fixture) {
    std::vector<Triple> rows;
    if (fixture == "target99") {
        for (int x=0; x<33; ++x) rows.push_back({x,x+33,x+66});
        for (int x=0; x<99; ++x) rows.push_back({x,(x+1)%99,(x+4)%99});
        for (int x=0; x<99; ++x) rows.push_back({x,(x+7)%99,(x+18)%99});
    } else if(fixture=="prism9"){
        // Points are the nine edges of the triangular prism; triples are its
        // six vertex stars. This linear degree2 control begins with E_lambda>0.
        rows={{{0,2,6}},{{0,1,7}},{{1,2,8}},{{3,5,6}},{{3,4,7}},{{4,5,8}}};
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
    Graph best(s.current.n,s.current.degree,s.best);
    f << "HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V1\nobjective " << OBJECTIVE << "\nlambda_weight " << LAMBDA_WEIGHT << "\nn " << s.current.n << "\ndegree " << s.current.degree;
    f << "\nseed " << s.config.seed << "\nmix_steps " << s.config.mix_steps << "\nschedule_steps " << s.config.schedule_steps;
    f << "\nt_start " << s.config.start << "\nt_end " << s.config.end << "\nforced " << s.config.forced;
    f << "\nstep " << s.step << "\nadmissible " << s.admissible << "\naccepted " << s.accepted << "\nbest_updates " << s.best_updates;
    f << "\nweighted_energy " << s.current.energy << "\nbase_energy " << s.current.lambda_energy+s.current.mu_energy
      << "\nlambda_energy " << s.current.lambda_energy << "\nmu_energy " << s.current.mu_energy
      << "\nbest_weighted_energy " << s.best_energy << "\nbest_base_energy " << best.lambda_energy+best.mu_energy
      << "\nbest_lambda_energy " << best.lambda_energy << "\nbest_mu_energy " << best.mu_energy << "\nrng";
    for (auto x : s.rng.s) f << ' ' << x;
    f << "\ncurrent " << s.current.triples.size() << '\n';
    for (const auto &r : s.current.triples) f << r[0] << ' ' << r[1] << ' ' << r[2] << '\n';
    f << "best " << s.best.size() << '\n'; for (const auto &r : s.best) f << r[0] << ' ' << r[1] << ' ' << r[2] << '\n';
    f << "cn " << s.current.n*(s.current.n-1)/2 << '\n';
    for (int u=0; u<s.current.n; ++u) for (int v=u+1; v<s.current.n; ++v) f << s.current.cn[u][v] << '\n';
    f << "first_lambda0 " << s.first_lambda0.found << '\n';
    if(s.first_lambda0.found){
        const auto &r=s.first_lambda0;
        Graph fc(s.current.n,s.current.degree,r.current),fb(s.current.n,s.current.degree,r.best);
        need(fc.lambda_energy==0 && fb.energy<=fc.energy,"first lambda0 snapshot scores");
        f << "first_step " << r.step << "\nfirst_admissible " << r.admissible << "\nfirst_accepted " << r.accepted
          << "\nfirst_best_updates " << r.best_updates << "\nfirst_rng";
        for(auto x:r.rng)f << ' ' << x;
        f << "\nfirst_current " << r.current.size() << '\n';
        for(const auto &t:r.current)f << t[0] << ' ' << t[1] << ' ' << t[2] << '\n';
        f << "first_best " << r.best.size() << '\n';
        for(const auto &t:r.best)f << t[0] << ' ' << t[1] << ' ' << t[2] << '\n';
    }
    f << "END\n"; f.flush(); need(static_cast<bool>(f), "complete checkpoint write");
}

template<class T> static void field(std::istream &f, const std::string &name, T &value) {
    std::string actual; need(static_cast<bool>(f >> actual >> value) && actual == name, "checkpoint field "+name);
}
static State load_state(const std::string &path, const Options &runtime) {
    std::ifstream f(path); std::string tag; f >> tag; need(tag == "HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V1", "checkpoint version");
    std::string objective; std::int64_t weight; field(f,"objective",objective);field(f,"lambda_weight",weight);
    need(objective==OBJECTIVE && weight==LAMBDA_WEIGHT,"checkpoint exact objective/weight");
    int n, degree; Options c=runtime;
    field(f,"n",n); field(f,"degree",degree); field(f,"seed",c.seed); field(f,"mix_steps",c.mix_steps);
    field(f,"schedule_steps",c.schedule_steps); field(f,"t_start",c.start); field(f,"t_end",c.end); field(f,"forced",c.forced);
    need((n == 99 && degree == 7) || (n == 9 && degree == 2), "exact target or positive control domain");
    need(std::isfinite(c.start) && std::isfinite(c.end) && c.start >= 0 && c.end >= 0 && c.start <= 1000 && c.end <= 1000 && c.schedule_steps > 0, "bounded checkpoint temperature schedule");
    std::uint64_t step, admissible, accepted, updates;
    std::int64_t energy,best_energy,base,el,em,bbase,bel,bem;
    field(f,"step",step); field(f,"admissible",admissible); field(f,"accepted",accepted); field(f,"best_updates",updates);
    field(f,"weighted_energy",energy);field(f,"base_energy",base);field(f,"lambda_energy",el);field(f,"mu_energy",em);
    field(f,"best_weighted_energy",best_energy);field(f,"best_base_energy",bbase);field(f,"best_lambda_energy",bel);field(f,"best_mu_energy",bem);
    std::array<std::uint64_t,4> rng{}; f >> tag; need(tag == "rng", "rng tag"); for (auto &x:rng) need(static_cast<bool>(f >> x), "rng integer");
    need((rng[0]|rng[1]|rng[2]|rng[3]) != 0, "nonzero RNG state");
    int count; field(f,"current",count); need(count == n*degree/3, "current triple population");
    std::vector<Triple> current(count); for (auto &r:current) for (auto &x:r) need(static_cast<bool>(f >> x), "current triple parse");
    State s(Graph(n,degree,current),c);
    field(f,"best",count); need(count == n*degree/3, "best triple population");
    std::vector<Triple> best(count); for (auto &r:best) for (auto &x:r) need(static_cast<bool>(f >> x), "best triple parse");
    Graph b(n,degree,best);
    need(s.current.energy==energy && b.energy==best_energy && best_energy<=energy,"checkpoint exact weighted current/best scores");
    need(s.current.lambda_energy==el && s.current.mu_energy==em && el+em==base && b.lambda_energy==bel && b.mu_energy==bem && bel+bem==bbase,"checkpoint exact component/base scores");
    field(f,"cn",count); need(count == n*(n-1)/2, "cache population");
    for (int u=0; u<n; ++u) for (int v=u+1; v<n; ++v) { int x; need(static_cast<bool>(f >> x) && x == s.current.cn[u][v], "checkpoint exact CN cache"); }
    int first_found;field(f,"first_lambda0",first_found);need(first_found==0 || first_found==1,"checkpoint first lambda0 flag");
    if(first_found){
        auto &r=s.first_lambda0;r.found=true;
        field(f,"first_step",r.step);field(f,"first_admissible",r.admissible);field(f,"first_accepted",r.accepted);field(f,"first_best_updates",r.best_updates);
        f>>tag;need(tag=="first_rng","checkpoint first lambda0 RNG tag");for(auto &x:r.rng)need(static_cast<bool>(f>>x),"checkpoint first lambda0 RNG integer");
        need((r.rng[0]|r.rng[1]|r.rng[2]|r.rng[3])!=0,"checkpoint first lambda0 nonzero RNG");
        field(f,"first_current",count);need(count==n*degree/3,"checkpoint first lambda0 current population");r.current.resize(count);
        for(auto &t:r.current)for(auto &x:t)need(static_cast<bool>(f>>x),"checkpoint first lambda0 current parse");
        field(f,"first_best",count);need(count==n*degree/3,"checkpoint first lambda0 best population");r.best.resize(count);
        for(auto &t:r.best)for(auto &x:t)need(static_cast<bool>(f>>x),"checkpoint first lambda0 best parse");
        Graph fc(n,degree,r.current),fb(n,degree,r.best);
        need(fc.lambda_energy==0 && fb.energy<=fc.energy,"checkpoint first lambda0 exact scores");
        need(r.step<=step && r.admissible<=admissible && r.accepted<=accepted && r.best_updates<=updates &&
             r.best_updates<=r.accepted && r.accepted<=r.admissible && r.admissible<=r.step,"checkpoint first lambda0 counters");
    }
    need(s.current.lambda_energy!=0 || first_found,"checkpoint lambda0 selection completeness");
    f >> tag; need(tag == "END" && !(f >> tag), "checkpoint complete exact record");
    need(accepted <= admissible && admissible <= step && updates <= accepted, "checkpoint counter consistency");
    s.best=best; s.best_energy=best_energy; s.rng.s=rng; s.step=step; s.admissible=admissible; s.accepted=accepted; s.best_updates=updates;
    return s;
}

// Explicit graph import only: validate the whole old record, then reset all RNG,
    // counters/configuration and current/best selection under the new objective.
static State import_weight6(const std::string &path,const Options &runtime) {
    std::ifstream f(path);std::string tag;f>>tag;need(tag=="HYPERGRAPH_WEIGHTED_ANNEAL_STATE_V1","import weight6 version");
    std::string objective;std::int64_t weight;field(f,"objective",objective);field(f,"lambda_weight",weight);
    need(objective=="SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V1" && weight==6,"import weight6 exact objective/weight");
    int n,degree;Options old=runtime;
    field(f,"n",n);field(f,"degree",degree);field(f,"seed",old.seed);field(f,"mix_steps",old.mix_steps);
    field(f,"schedule_steps",old.schedule_steps);field(f,"t_start",old.start);field(f,"t_end",old.end);field(f,"forced",old.forced);
    need((n==99 && degree==7)||(n==9 && degree==2),"import weight6 domain");
    need(std::isfinite(old.start) && std::isfinite(old.end) && old.start>=0 && old.end>=0 && old.start<=1000 && old.end<=1000 && old.schedule_steps>0,"import weight6 schedule");
    std::uint64_t step,admissible,accepted,updates;std::int64_t energy,best_energy,base,el,em,bbase,bel,bem;
    field(f,"step",step);field(f,"admissible",admissible);field(f,"accepted",accepted);field(f,"best_updates",updates);
    field(f,"weighted_energy",energy);field(f,"base_energy",base);field(f,"lambda_energy",el);field(f,"mu_energy",em);
    field(f,"best_weighted_energy",best_energy);field(f,"best_base_energy",bbase);field(f,"best_lambda_energy",bel);field(f,"best_mu_energy",bem);
    std::array<std::uint64_t,4> rng{};f>>tag;need(tag=="rng","import weight6 rng tag");for(auto &x:rng)need(static_cast<bool>(f>>x),"import weight6 rng integer");
    need((rng[0]|rng[1]|rng[2]|rng[3])!=0,"import weight6 nonzero RNG");
    int count;field(f,"current",count);need(count==n*degree/3,"import weight6 current population");
    std::vector<Triple> current(count);for(auto &r:current)for(auto &x:r)need(static_cast<bool>(f>>x),"import weight6 current parse");
    Graph c(n,degree,current);field(f,"best",count);need(count==n*degree/3,"import weight6 best population");
    std::vector<Triple> best(count);for(auto &r:best)for(auto &x:r)need(static_cast<bool>(f>>x),"import weight6 best parse");Graph b(n,degree,best);
    need(6*c.lambda_energy+c.mu_energy==energy && 6*b.lambda_energy+b.mu_energy==best_energy && best_energy<=energy,"import weight6 exact weighted current/best scores");
    need(c.lambda_energy==el && c.mu_energy==em && el+em==base && b.lambda_energy==bel && b.mu_energy==bem && bel+bem==bbase,"import weight6 exact component/base scores");
    field(f,"cn",count);need(count==n*(n-1)/2,"import weight6 cache population");
    for(int u=0;u<n;++u)for(int v=u+1;v<n;++v){int x;need(static_cast<bool>(f>>x) && x==c.cn[u][v],"import weight6 exact CN cache");}
    f>>tag;need(tag=="END" && !(f>>tag),"import weight6 exact end");
    need(updates<=accepted && accepted<=admissible && admissible<=step,"import weight6 counters");
    need(runtime.import_select=="current" || runtime.import_select=="best","import weight6 graph selector");
    return State(Graph(n,degree,runtime.import_select=="current"?current:best),runtime);
}

static void pair_costs(const std::filesystem::path &path) {
    need(!std::filesystem::exists(path),"immutable pair costs");std::ofstream f(path);
    for(int c=0;c<=14;++c)for(int a=0;a<=1;++a){
        const std::int64_t ol=a?(c-1)*(c-1):0,om=a?0:(c-2)*(c-2);
        for(int delta:std::array<int,2>{-1,1})if(c+delta>=0 && c+delta<=14){
            const int nc=c+delta;const std::int64_t nl=a?(nc-1)*(nc-1):0,nm=a?0:(nc-2)*(nc-2);
            f<<"{\"kind\":\"CN\",\"c\":"<<c<<",\"a\":"<<a<<",\"delta\":"<<delta<<",\"new_c\":"<<nc<<",\"new_a\":"<<a
             <<",\"old_lambda\":"<<ol<<",\"old_mu\":"<<om<<",\"new_lambda\":"<<nl<<",\"new_mu\":"<<nm<<",\"delta_F\":"<<LAMBDA_WEIGHT*(nl-ol)+nm-om<<"}\n";
        }
        const int na=1-a;const std::int64_t nl=na?(c-1)*(c-1):0,nm=na?0:(c-2)*(c-2);
        f<<"{\"kind\":\"EDGE\",\"c\":"<<c<<",\"a\":"<<a<<",\"delta\":"<<na-a<<",\"new_c\":"<<c<<",\"new_a\":"<<na
         <<",\"old_lambda\":"<<ol<<",\"old_mu\":"<<om<<",\"new_lambda\":"<<nl<<",\"new_mu\":"<<nm<<",\"delta_F\":"<<LAMBDA_WEIGHT*(nl-ol)+nm-om<<"}\n";
    }
    f.flush();need(static_cast<bool>(f),"complete pair costs");
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
        if (k == "--emit-pair-costs") { o.emit_pair_costs=true; continue; }
        need(i+1 < argc, "argument value"); std::string v=argv[++i];
        if (k == "--fixture") o.fixture=v; else if (k == "--out") o.out=v; else if (k == "--resume") o.resume=v;
        else if(k=="--import-weight6")o.import_weight6=v;else if(k=="--import-select")o.import_select=v;
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
    need(o.resume.empty() || o.import_weight6.empty(),"resume and import are exclusive");
    return o;
}

int main(int argc,char **argv) {
    try {
        const auto started=Clock::now(); Options o=parse(argc,argv);
        need(!std::filesystem::exists(o.out), "fresh native output directory"); std::filesystem::create_directories(o.out);
        State s = !o.resume.empty()?load_state(o.resume,o):(!o.import_weight6.empty()?import_weight6(o.import_weight6,o):State(Graph(o.fixture == "target99" ? 99 : 9,o.fixture == "target99" ? 7 : 2,initial(o.fixture)),o));
        capture_first_lambda0(s,s.step);
        s.current.verify(); const std::int64_t initial_energy=s.current.energy;
        const std::int64_t initial_lambda=s.current.lambda_energy,initial_mu=s.current.mu_energy;
        write_state(std::filesystem::path(o.out)/"initial.state",s);
        if(o.emit_pair_costs)pair_costs(std::filesystem::path(o.out)/"pair_costs.jsonl");
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
            const bool first_lambda0_before=s.first_lambda0.found;
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
            const std::int64_t old_lambda=s.current.lambda_energy,old_mu=s.current.mu_energy;
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
                    need(s.current.energy==old_energy && s.current.lambda_energy==old_lambda && s.current.mu_energy==old_mu,"exact rejected-trade component rollback");
                }
            }
            capture_first_lambda0(s,s.step+1);
            const bool log=performed < o.trace_max || (o.trace_stride && (s.step%o.trace_stride == 0));
            if (log) {
                auto proposed_t=t, proposed_q=q; proposed_t[pi]=y; proposed_q[pj]=x;
                trace << "{\"trace_schema\":\"HYPERGRAPH_WEIGHT60_MOVE_V1\",\"step\":" << s.step << ",\"ti\":" << ti << ",\"tj\":" << tj << ",\"pi\":" << pi << ",\"pj\":" << pj
                      << ",\"old_triples\":[[" << t[0] << ',' << t[1] << ',' << t[2] << "],[" << q[0] << ',' << q[1] << ',' << q[2] << "]]"
                      << ",\"proposed_triples\":[[" << proposed_t[0] << ',' << proposed_t[1] << ',' << proposed_t[2] << "],[" << proposed_q[0] << ',' << proposed_q[1] << ',' << proposed_q[2] << "]]"
                      << ",\"disjoint\":" << (disjoint?"true":"false") << ",\"new_pairs_absent\":" << (absent?"true":"false")
                      << ",\"admissible\":" << (valid?"true":"false") << ",\"accepted\":" << (accepted?"true":"false")
                      << ",\"mixing\":" << (mixing?"true":"false") << ",\"temperature\":" << temp
                      << ",\"objective\":\""<<OBJECTIVE<<"\",\"lambda_weight\":"<<LAMBDA_WEIGHT
                      << ",\"delta\":" << delta << ",\"weighted_energy_before\":" << old_energy << ",\"weighted_energy_after\":" << s.current.energy
                      << ",\"lambda_energy_before\":"<<old_lambda<<",\"mu_energy_before\":"<<old_mu
                      << ",\"lambda_energy_after\":"<<s.current.lambda_energy<<",\"mu_energy_after\":"<<s.current.mu_energy
                      << ",\"best_weighted_energy\":" << s.best_energy
                      << ",\"first_lambda0_before\":" << (first_lambda0_before?"true":"false")
                      << ",\"first_lambda0_after\":" << (s.first_lambda0.found?"true":"false")
                      << ",\"first_lambda0_step\":" << (s.first_lambda0.found?std::to_string(s.first_lambda0.step):"null")
                      << ",\"draw\":\"" << draw << "\",\"rng_before\":[";
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
        write_state(std::filesystem::path(o.out)/"final.state",s); save_adjacency(std::filesystem::path(o.out)/"best.adj",best);save_adjacency(std::filesystem::path(o.out)/"current.adj",s.current);
        if(s.first_lambda0.found){
            const auto &r=s.first_lambda0;
            State first(Graph(s.current.n,s.current.degree,r.current),s.config);
            first.best=r.best;first.best_energy=Graph(s.current.n,s.current.degree,r.best).energy;first.rng.s=r.rng;
            first.step=r.step;first.admissible=r.admissible;first.accepted=r.accepted;first.best_updates=r.best_updates;first.first_lambda0=r;
            write_state(std::filesystem::path(o.out)/"first_lambda0.state",first);
            save_adjacency(std::filesystem::path(o.out)/"first_lambda0.adj",first.current);
        }
        std::ofstream selection(std::filesystem::path(o.out)/"lambda0_selection.json");
        selection << "{\"schema\":\"FIRST_LAMBDA0_SELECTION_V1\",\"found\":" << (s.first_lambda0.found?"true":"false")
          << ",\"selection_rule\":\"First observed current graph with exact E_lambda0, including invocation initial state; retained across exact weight60 resumes, independent of best F60\""
          << ",\"first_step\":" << (s.first_lambda0.found?std::to_string(s.first_lambda0.step):"null")
          << ",\"carried_from_resume\":" << ((!o.resume.empty() && s.first_lambda0.found && s.first_lambda0.step<=starting_step)?"true":"false")
          << ",\"target_resolution\":false,\"independent_approval\":false}\n";
        selection.flush();need(static_cast<bool>(selection),"complete lambda0 selection write");
        trace.flush(); need(static_cast<bool>(trace), "complete trace write");
        std::ofstream result(std::filesystem::path(o.out)/"result.json"); result << std::setprecision(17)
            << "{\"objective\":\""<<OBJECTIVE<<"\",\"lambda_weight\":"<<LAMBDA_WEIGHT<<",\"n\":" << s.current.n << ",\"point_degree\":" << s.current.degree
            << ",\"triple_count\":" << s.current.triples.size() << ",\"initial_weighted_energy\":" << initial_energy
            << ",\"initial_lambda_energy\":"<<initial_lambda<<",\"initial_mu_energy\":"<<initial_mu<<",\"initial_base_energy\":"<<initial_lambda+initial_mu
            << ",\"current_weighted_energy\":" << s.current.energy<<",\"current_lambda_energy\":"<<s.current.lambda_energy<<",\"current_mu_energy\":"<<s.current.mu_energy<<",\"current_base_energy\":"<<s.current.lambda_energy+s.current.mu_energy
            << ",\"best_weighted_energy\":" << s.best_energy<<",\"best_lambda_energy\":"<<best.lambda_energy<<",\"best_mu_energy\":"<<best.mu_energy<<",\"best_base_energy\":"<<best.lambda_energy+best.mu_energy
            << ",\"starting_step\":" << starting_step << ",\"ending_step\":" << s.step
            << ",\"proposals_this_invocation\":" << performed << ",\"admissible_total\":" << s.admissible << ",\"accepted_total\":" << s.accepted
            << ",\"best_updates_total\":" << s.best_updates << ",\"elapsed_seconds\":" << std::chrono::duration<double>(Clock::now()-started).count()
            << ",\"first_lambda0_found\":" << (s.first_lambda0.found?"true":"false")
            << ",\"first_lambda0_step\":" << (s.first_lambda0.found?std::to_string(s.first_lambda0.step):"null")
            << ",\"stop_reason\":\"" << stop << "\",\"target_resolution\":false,\"independent_approval\":false}\n";
        result.flush(); need(static_cast<bool>(result), "complete result write");
        std::cout << "NATIVE_RESULT_PRESERVED " << s.current.n << ' ' << s.current.energy << ' ' << s.best_energy << '\n';
        return 0;
    } catch (const std::exception &e) { std::cerr << e.what() << '\n'; return 2; }
}
