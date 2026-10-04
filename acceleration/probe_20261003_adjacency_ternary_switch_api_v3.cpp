// SOURCE_ONLY / UNCOMPILED / UNEXECUTED. Author /root/structural.
// Actual Graph getter probes, never reference-computed cache snapshots.
// No existing record checker or driver controls approve this new harness.
#include "adjacency_ternary_switch_kernel_20261003_v2.cpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <csignal>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>

namespace ats = adjacency_ternary_switch_v1;
namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;
static volatile std::sig_atomic_t stopped = 0;
static void stop_handler(int value) { stopped = value; }
static constexpr const char* kernel_sha = "ce35a195796266753cc123064e34a9bf0a9bda1880932576010089031bccba47";

static std::string json_quoted(const std::string& value) {
    std::ostringstream out; out << '"';
    for (unsigned char c : value) {
        if (c == '"' || c == '\\') out << '\\' << char(c);
        else if (c < 32) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << int(c) << std::dec;
        else out << char(c);
    }
    out << '"'; return out.str();
}
static std::string flat(const std::vector<int>& values) {
    std::ostringstream out; out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) { if (i) out << ','; out << values[i]; }
    out << ']'; return out.str();
}
static std::string role(const ats::Role& r) {
    std::ostringstream out; out << '[' << r.u << ',' << r.v << ',' << r.x << ',' << r.y << ',' << r.orientation << ']'; return out.str();
}
static std::string snapshot(const ats::Graph& graph) {
    const auto& m = graph.metrics(); std::ostringstream out;
    out << "{\"n\":" << graph.n() << ",\"degree\":" << graph.degree()
        << ",\"flat_adjacency\":" << flat(graph.adjacency())
        << ",\"flat_true_A_squared\":" << flat(graph.full_product_cache())
        << ",\"F3\":" << m.f3 << ",\"E_lambda\":" << m.e_lambda << ",\"E_mu\":" << m.e_mu
        << ",\"E\":" << m.energy() << ",\"scalar\":" << m.scalar()
        << ",\"residue_population\":[" << m.residue_population[0] << ',' << m.residue_population[1] << ',' << m.residue_population[2] << "]}";
    return out.str();
}
static std::string metric(const ats::Metrics& m) {
    std::ostringstream out;
    out << "{\"F3\":" << m.f3 << ",\"E_lambda\":" << m.e_lambda << ",\"E_mu\":" << m.e_mu
        << ",\"E\":" << m.energy() << ",\"scalar\":" << m.scalar()
        << ",\"residue_population\":[" << m.residue_population[0] << ',' << m.residue_population[1] << ',' << m.residue_population[2] << "]}";
    return out.str();
}
static std::string record(const ats::SwitchRecord& r) {
    std::ostringstream out;
    out << "{\"role\":" << role(r.role) << ",\"valid\":" << (r.valid ? "true" : "false")
        << ",\"diagnostic\":" << json_quoted(r.diagnostic) << ",\"affected_unordered_pairs\":" << r.affected_unordered_pairs
        << ",\"before_metrics\":" << metric(r.before) << ",\"after_metrics\":" << metric(r.after)
        << ",\"delta_F3\":" << r.delta_f3 << ",\"delta_lambda\":" << r.delta_lambda << ",\"delta_mu\":" << r.delta_mu
        << ",\"delta_E\":" << r.delta_energy << ",\"delta_scalar\":" << r.delta_scalar << '}';
    return out.str();
}
using Edge = std::pair<int,int>;
using Pairing = std::array<Edge,2>;
static Edge edge(int a, int b) { return {std::min(a,b),std::max(a,b)}; }
static Pairing pairing(Edge a, Edge b) { if (b < a) std::swap(a,b); return {{a,b}}; }
static Pairing additions(const ats::Role& r) {
    return r.orientation == 0 ? pairing(edge(r.u,r.x),edge(r.v,r.y)) : pairing(edge(r.u,r.y),edge(r.v,r.x));
}
static ats::Role reverse_role(const ats::Role& r) {
    const auto added = additions(r); const auto removed = pairing(edge(r.u,r.v),edge(r.x,r.y));
    ats::Role reverse{added[0].first,added[0].second,added[1].first,added[1].second,0};
    if (additions(reverse) != removed) reverse.orientation = 1;
    ats::need(additions(reverse) == removed, "HARNESS_REVERSE_PAIRING"); return reverse;
}

// Every snapshot below comes directly from the actual candidate/base getters.
// Graph has no rollback API: candidate copy preservation and reverse apply are
// the exact branches recorded here, rather than a claimed rollback operation.
static std::string probe(const ats::Graph& base, const ats::Role& r, std::int64_t id) {
    ats::Graph candidate = base; const std::string before = snapshot(candidate);
    const auto applied = candidate.apply(r); const std::string after = snapshot(candidate);
    std::string reverse = "null", reverse_record = "null", restored = "null";
    if (applied.valid) {
        const auto inverse = reverse_role(r); reverse = role(inverse);
        reverse_record = record(candidate.apply(inverse)); restored = snapshot(candidate);
    }
    std::ostringstream out;
    out << "{\"schema\":\"ADJACENCY_TERNARY_SWITCH_NATIVE_API_PROBE_V1\",\"proposal_id\":" << id
        << ",\"canonical_old_edges\":[[" << r.u << ',' << r.v << "],[" << r.x << ',' << r.y << "]]"
        << ",\"orientation\":" << r.orientation << ",\"kernel_record\":" << record(applied)
        << ",\"before\":" << before << ",\"after\":" << after
        << ",\"invalid_apply_unchanged\":" << (applied.valid ? "null" : before == after ? "true" : "false")
        << ",\"reverse_role\":" << reverse << ",\"reverse_kernel_record\":" << reverse_record << ",\"restored\":" << restored << '}';
    return out.str();
}
static ats::Graph fixture(const std::string& name) {
    const int n = name == "rook9" ? 9 : name == "triangular_prism6" ? 6 : name == "cube8" ? 8 : 99;
    const int k = name == "rook9" ? 4 : name == "synthetic99_14" ? 14 : 3;
    std::vector<int> a(static_cast<std::size_t>(n)*n,0);
    auto link = [&](int u,int v) { a[u*n+v]=a[v*n+u]=1; };
    if (name == "rook9") {
        for (int u=0;u<n;++u) for (int v=u+1;v<n;++v) if (u/3==v/3 || u%3==v%3) link(u,v);
    } else if (name == "triangular_prism6") {
        for (int b : {0,3}) { link(b,b+1);link(b,b+2);link(b+1,b+2); } for (int i=0;i<3;++i) link(i,i+3);
    } else if (name == "cube8") {
        for (int u=0;u<n;++u) for (int v=u+1;v<n;++v) { int x=u^v; if (x && !(x&(x-1))) link(u,v); }
    } else if (name == "synthetic99_14") {
        for (int u=0;u<n;++u) for (int d=1;d<=7;++d) link(u,(u+d)%n);
    } else ats::need(false,"HARNESS_FIXTURE_NAME");
    return ats::Graph(n,k,a);
}
struct Budget {
    Clock::time_point start = Clock::now(); double seconds = 0, save_seconds = 0;
    double elapsed() const { return std::chrono::duration<double>(Clock::now()-start).count(); }
    void tick() const { ats::need(!stopped && elapsed() < seconds-save_seconds,"HARNESS_COOPERATIVE_STOP"); }
};
static double real(const std::string& value) {
    std::size_t end=0; const double result=std::stod(value,&end);
    ats::need(end==value.size() && std::isfinite(result) && result>0,"HARNESS_POSITIVE_SECONDS");return result;
}
static void write_new(const fs::path& path, const std::string& data) {
    ats::need(!fs::exists(path),"HARNESS_OUTPUT_EXISTS");
    std::ofstream out(path,std::ios::binary);ats::need(out.good(),"HARNESS_OUTPUT_OPEN");
    out << data;out.flush();ats::need(out.good(),"HARNESS_OUTPUT_WRITE");out.close();
}
static void append(std::ofstream& out,const std::string& value,const Budget& budget) {
    budget.tick();out << value << '\n';out.flush();ats::need(out.good(),"HARNESS_OUTPUT_WRITE");budget.tick();
}

int main(int argc,char** argv) {
    Budget budget;fs::path output;std::int64_t tiny=0,synthetic=0,negative=0;
    std::signal(SIGINT,stop_handler);std::signal(SIGTERM,stop_handler);
    try {
        ats::need(argc==9,"HARNESS_EXACT_FOUR_PAIRS");std::map<std::string,std::string> options;
        const std::set<std::string> names{"--out","--seconds","--save-seconds","--source-context"};
        for (int i=1;i<argc;i+=2) ats::need(names.count(argv[i]) && options.emplace(argv[i],argv[i+1]).second,"HARNESS_OPTION_NAME_OR_DUPLICATE");
        budget.seconds=real(options.at("--seconds"));budget.save_seconds=real(options.at("--save-seconds"));
        ats::need(budget.seconds>budget.save_seconds,"HARNESS_SAVE_RESERVE");
        const auto context=options.at("--source-context");ats::need(context.size()==40 && context.find_first_not_of("0123456789abcdef")==std::string::npos,"HARNESS_SOURCE_CONTEXT");
        output=fs::absolute(options.at("--out"));ats::need(!fs::exists(output),"HARNESS_OUTPUT_ROOT_EXISTS");budget.tick();fs::create_directories(output);budget.tick();
        for (const auto& name : {"rook9","triangular_prism6","cube8","synthetic99_14"}) {
            budget.tick();const auto base=fixture(name);const auto edges=base.canonical_edges();
            const bool is_synthetic=std::string(name)=="synthetic99_14";
            const std::int64_t total=is_synthetic ? 2 : static_cast<std::int64_t>(edges.size())*(edges.size()-1);
            const auto final=output/(std::string(name)+".probes.jsonl");const auto pending=fs::path(final.string()+".partial");
            std::ofstream stream(pending,std::ios::binary);ats::need(stream.good(),"HARNESS_OUTPUT_OPEN");
            append(stream,"{\"schema\":\"ADJACENCY_SWITCH_API_FIXTURE_HEADER_V1\",\"fixture\":"+json_quoted(name)+",\"declared_roles\":"+std::to_string(total)+",\"baseline_before\":"+snapshot(base)+"}",budget);
            std::int64_t id=0;
            if (is_synthetic) {
                for (int orientation : {0,1}) { append(stream,probe(base,{0,1,20,21,orientation},id++),budget);++synthetic; }
            } else {
                for (std::size_t i=0;i<edges.size();++i) for (std::size_t j=i+1;j<edges.size();++j) for (int orientation : {0,1}) {
                    budget.tick();const ats::Role r{edges[i].first,edges[i].second,edges[j].first,edges[j].second,orientation};
                    append(stream,probe(base,r,id++),budget);++tiny;
                }
            }
            ats::need(id==total,"HARNESS_COMPLETE_ROLE_COUNT");
            append(stream,"{\"schema\":\"ADJACENCY_SWITCH_API_FIXTURE_FOOTER_V1\",\"completed_roles\":"+std::to_string(id)+",\"baseline_after\":"+snapshot(base)+"}",budget);
            stream.close();budget.tick();fs::rename(pending,final);budget.tick();
        }
        const auto rook=fixture("rook9");
        const auto negative_path=output/"negative_calls.jsonl.partial";std::ofstream cases(negative_path,std::ios::binary);ats::need(cases.good(),"HARNESS_OUTPUT_OPEN");
        auto constructor_case=[&](const std::string& name,const char* expected,int n,int k,std::vector<int> a) {
            budget.tick();std::string observed="ACCEPTED_UNEXPECTED",accepted="null";
            try { const ats::Graph graph(n,k,a);accepted=snapshot(graph); } catch(const std::exception& error) { observed=error.what(); }
            append(cases,"{\"schema\":\"ADJACENCY_SWITCH_API_CONSTRUCTOR_CASE_V1\",\"case\":"+json_quoted(name)+",\"n\":"+std::to_string(n)+",\"degree\":"+std::to_string(k)+",\"input_flat_adjacency\":"+flat(a)+",\"expected_stage\":"+json_quoted(expected)+",\"actual_stage\":"+json_quoted(observed)+",\"unexpected_accepted_snapshot\":"+accepted+"}",budget);++negative;
        };
        constructor_case("dimension_below4","GRAPH_DIMENSIONS",3,2,std::vector<int>(9,0));
        auto broken=rook.adjacency();broken.pop_back();constructor_case("wrong_flat_shape","GRAPH_SHAPE",9,4,broken);
        broken=rook.adjacency();broken[1]=2;constructor_case("nonbinary_integer_entry","GRAPH_BINARY",9,4,broken);
        broken=rook.adjacency();broken[1]=0;constructor_case("one_sided_edge","GRAPH_SYMMETRY",9,4,broken);
        broken=rook.adjacency();broken[0]=1;constructor_case("diagonal_one","GRAPH_DIAGONAL",9,4,broken);
        broken=rook.adjacency();broken[1]=broken[9]=0;constructor_case("removed_edge_wrong_degree","GRAPH_DEGREE",9,4,broken);
        const std::array<std::pair<ats::Role,const char*>,6> rejected{{
            {{-1,1,3,4,1},"ROLE_VERTEX_RANGE"},{{0,1,3,4,2},"ROLE_ORIENTATION"},
            {{1,0,3,4,1},"ROLE_CANONICAL_OLD_EDGES"},{{0,1,1,2,0},"ROLE_FOUR_DISTINCT_VERTICES"},
            {{0,4,3,5,0},"ROLE_OLD_EDGE_ABSENT"},{{0,1,3,4,0},"ROLE_NEW_EDGE_PRESENT"}}};
        for (std::size_t i=0;i<rejected.size();++i) {
            budget.tick();append(cases,"{\"schema\":\"ADJACENCY_SWITCH_API_ROLE_CASE_V1\",\"case\":"+json_quoted(rejected[i].second)+",\"expected_stage\":"+json_quoted(rejected[i].second)+",\"probe\":"+probe(rook,rejected[i].first,static_cast<std::int64_t>(i))+"}",budget);++negative;
        }
        cases.close();budget.tick();fs::rename(negative_path,output/"negative_calls.jsonl");budget.tick();
        ats::need(tiny==510 && synthetic==2 && negative==12,"HARNESS_COMPLETE_POPULATION");
        std::ostringstream manifest;manifest << "{\"schema\":\"ADJACENCY_SWITCH_ACTUAL_API_HARNESS_V1\",\"status\":\"COMPLETE_CANDIDATE_REQUIRES_INDEPENDENT_API_REPLAY\",\"producer\":\"/root/structural\",\"kernel_source_sha256\":" << json_quoted(kernel_sha)
            << ",\"source_context\":" << json_quoted(context) << ",\"complete_tiny_roles\":" << tiny << ",\"synthetic99_probes\":" << synthetic << ",\"negative_calls\":" << negative
            << ",\"actual_graph_getter_snapshots\":true,\"actual_target_input_read\":false,\"rng_used\":false,\"rollback_API_claimed\":false,\"independent_approval\":false,\"target_resolution\":\"NONE\",\"elapsed_seconds\":" << std::setprecision(17) << budget.elapsed() << ",\"allocated_seconds\":" << budget.seconds << ",\"save_seconds\":" << budget.save_seconds << "}\n";
        budget.tick();write_new(output/"manifest.json",manifest.str());budget.tick();return 0;
    } catch(const std::exception& error) {
        std::cerr << "FAILED " << error.what() << '\n';
        if (!output.empty() && fs::is_directory(output) && !fs::exists(output/"failure.json")) {
            try { write_new(output/"failure.json","{\"schema\":\"ADJACENCY_SWITCH_ACTUAL_API_FAILURE_V1\",\"error\":"+json_quoted(error.what())+",\"completed_tiny_roles\":"+std::to_string(tiny)+",\"completed_synthetic_probes\":"+std::to_string(synthetic)+",\"completed_negative_calls\":"+std::to_string(negative)+",\"automatic_retry\":false,\"provisional_manifest_is_approval\":false,\"target_resolution\":\"NONE\"}\n"); } catch(...) {}
        }
        return 1;
    }
}
