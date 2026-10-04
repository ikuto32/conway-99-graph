// SOURCE ONLY. New exact ternary objective/RNG/state; no old binary gate transfers.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <csignal>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Triple = std::array<int,3>;
using Clock = std::chrono::steady_clock;
static constexpr int MAX_N=99;
static constexpr const char* OBJECTIVE="SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1";
static constexpr const char* KERNEL="ALL_LINE_EXCLUSIVE_SWAP_TERNARY_V1";
static constexpr const char* DISTRIBUTION="ALL_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1";
static volatile std::sig_atomic_t stop_signal=0;
static void signal_stop(int value){stop_signal=value;}
static void need(bool ok,const std::string& stage){if(!ok)throw std::runtime_error(stage);}
static bool hash_text(const std::string& x){return x.size()==64 && std::all_of(x.begin(),x.end(),[](char c){return (c>='0'&&c<='9')||(c>='a'&&c<='f');});}
static std::uint64_t integer(const std::string& x){
    need(!x.empty() && (x=="0" || x[0]!='0') && std::all_of(x.begin(),x.end(),[](char c){return c>='0'&&c<='9';}),"WIRE_INTEGER");
    std::size_t used=0;std::uint64_t value=0;
    try{value=std::stoull(x,&used);}catch(const std::exception&){need(false,"WIRE_INTEGER_OVERFLOW");}
    need(used==x.size(),"WIRE_INTEGER");return value;
}
static double real(const std::string& x){std::size_t used=0;double v=0;try{v=std::stod(x,&used);}catch(const std::exception&){need(false,"WIRE_REAL");}need(used==x.size()&&std::isfinite(v),"WIRE_REAL");return v;}
struct Reader{
    std::ifstream f;
    explicit Reader(const std::string& path):f(path){need(static_cast<bool>(f),"WIRE_OPEN");}
    std::string token(){std::string v;need(static_cast<bool>(f>>v),"WIRE_TRUNCATED");return v;}
    void tag(const std::string& expected){need(token()==expected,"WIRE_FIELD:"+expected);}
    std::uint64_t number(){return integer(token());}
    std::uint64_t num(const std::string& name){tag(name);return number();}
    std::string text(const std::string& name){tag(name);return token();}
    double floating(const std::string& name){tag(name);return real(token());}
    void end(){tag("END");std::string extra;need(!(f>>extra),"WIRE_TRAILING");}
};
static int small(std::uint64_t x,int maximum){need(x<=static_cast<std::uint64_t>(maximum),"WIRE_RANGE");return static_cast<int>(x);}
static void domain(int n,int degree){need((n==99&&degree==7)||((n==9||n==12)&&degree==2),"DOMAIN_DECLARED");}
static std::int64_t scalar_weight(int n,int degree){return n==99?819820:static_cast<std::int64_t>(n)*(n-1)/2*(2*degree)*(2*degree)+1;}
static std::vector<Triple> triples(Reader& r,const std::string& name,int n,int degree){
    const int count=small(r.num(name),231);need(count*3==n*degree,"TRIPLE_POPULATION");
    std::vector<Triple> rows(static_cast<std::size_t>(count));
    for(auto& row:rows)for(auto& x:row)x=small(r.number(),n-1);
    return rows;
}
static void write_rows(std::ostream& f,const std::string& name,const std::vector<Triple>& rows){f<<name<<' '<<rows.size()<<'\n';for(const auto& t:rows)f<<t[0]<<' '<<t[1]<<' '<<t[2]<<'\n';}

// SplitMix64 expansion and xoshiro256** transition adapted from preserved
// weight60 source2bc115; new unbiased bounded draws and words counter are V1.
static std::uint64_t rotl(std::uint64_t x,int k){return (x<<k)|(x>>(64-k));}
struct RNG{
    std::array<std::uint64_t,4> s{};
    std::uint64_t words=0;
    explicit RNG(std::uint64_t seed){for(auto& v:s){seed+=UINT64_C(0x9e3779b97f4a7c15);auto z=seed;z=(z^(z>>30))*UINT64_C(0xbf58476d1ce4e5b9);z=(z^(z>>27))*UINT64_C(0x94d049bb133111eb);v=z^(z>>31);}}
    std::uint64_t next(){need(words<std::numeric_limits<std::uint64_t>::max(),"RNG_WORD_OVERFLOW");++words;const auto result=rotl(s[1]*5,7)*9;const auto t=s[1]<<17;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=rotl(s[3],45);return result;}
    std::uint64_t bounded(std::uint64_t bound){need(bound>0,"RNG_BOUND");const auto threshold=(UINT64_C(0)-bound)%bound;for(;;){const auto x=next();if(x>=threshold)return x%bound;}}
};
struct Metrics{
    std::int64_t f3=0,el=0,em=0;
    std::array<std::int64_t,3> hist{};
    std::int64_t energy()const{return el+em;}
    std::int64_t scalar(std::int64_t weight)const{return weight*f3+energy();}
    bool operator==(const Metrics& b)const{return f3==b.f3&&el==b.el&&em==b.em&&hist==b.hist;}
};
static bool less(const Metrics& a,const Metrics& b){return std::make_pair(a.f3,a.energy())<std::make_pair(b.f3,b.energy());}
struct Cost{int residue;std::int64_t f3,el,em;};
static Cost cost(int c,int a){need(c>=0&&c<=MAX_N&&(a==0||a==1),"PAIR_COST_DOMAIN");const std::int64_t r=c+a-2;const int residue=static_cast<int>((r%3+3)%3);return {residue,residue!=0,a?r*r:0,a?0:r*r};}
static void change(Metrics& m,const Cost& old,const Cost& now){m.f3+=now.f3-old.f3;m.el+=now.el-old.el;m.em+=now.em-old.em;--m.hist[old.residue];++m.hist[now.residue];}
static void write_metrics(std::ostream& f,const std::string& name,const Metrics& m,std::int64_t w){f<<name<<' '<<m.f3<<' '<<m.el<<' '<<m.em<<' '<<m.hist[0]<<' '<<m.hist[1]<<' '<<m.hist[2]<<' '<<m.scalar(w)<<'\n';}
static Metrics read_metrics(Reader& r,const std::string& name,std::int64_t weight){
    r.tag(name);Metrics m;
    auto bounded=[&r](std::uint64_t maximum){const auto x=r.number();need(x<=maximum,"STATE_METRIC_TYPES");return static_cast<std::int64_t>(x);};
    m.f3=bounded(4851);m.el=bounded(819819);m.em=bounded(819819);
    for(auto& h:m.hist)h=bounded(4851);
    const auto saved=r.number();need(saved==static_cast<std::uint64_t>(m.scalar(weight)),"STATE_METRIC_TYPES");return m;
}

// Pairwise CN and category toggle mechanism adapted from2bc115; all F3,
// residue-population, scalar and typed-state handling is new and unapproved.
struct Graph{
    int n,degree;
    std::vector<Triple> rows;
    int a[MAX_N][MAX_N]{},cn[MAX_N][MAX_N]{};
    std::array<std::uint64_t,2> masks[MAX_N]{};
    Metrics metrics;
    Graph(int vertices,int pd,std::vector<Triple> lines):n(vertices),degree(pd),rows(std::move(lines)){
        domain(n,degree);need(static_cast<int>(rows.size())*3==n*degree,"TRIPLE_POPULATION");std::vector<int> counts(n);
        for(const auto& t:rows){for(int x:t){need(x>=0&&x<n,"TRIPLE_RANGE");++counts[x];}need(t[0]!=t[1]&&t[0]!=t[2]&&t[1]!=t[2],"TRIPLE_DISTINCT");
            for(int i=0;i<3;++i)for(int j=i+1;j<3;++j){const int u=t[i],v=t[j];need(!a[u][v],"TRIPLE_LINEARITY");a[u][v]=a[v][u]=1;masks[u][v/64]|=UINT64_C(1)<<(v%64);masks[v][u/64]|=UINT64_C(1)<<(u%64);}}
        for(int x:counts)need(x==degree,"POINT_DEGREE");
        for(int u=0;u<n;++u)for(int v=u+1;v<n;++v){cn[u][v]=cn[v][u]=full_cn(u,v);const auto c=cost(cn[u][v],a[u][v]);metrics.f3+=c.f3;metrics.el+=c.el;metrics.em+=c.em;++metrics.hist[c.residue];}
    }
    std::int64_t weight()const{return scalar_weight(n,degree);}
    int full_cn(int u,int v)const{return __builtin_popcountll(masks[u][0]&masks[v][0])+__builtin_popcountll(masks[u][1]&masks[v][1]);}
    std::string adjacency()const{std::string raw=std::to_string(n)+"\n";for(int u=0;u<n;++u){for(int v=0;v<n;++v)raw+=static_cast<char>('0'+a[u][v]);raw+='\n';}return raw;}
    void verify()const{
        Graph fresh(n,degree,rows);need(metrics==fresh.metrics,"VERIFY_FULL_METRICS");
        for(int u=0;u<n;++u)for(int v=0;v<n;++v){need(a[u][v]==fresh.a[u][v]&&masks[u]==fresh.masks[u],"VERIFY_ADJACENCY");need(cn[u][v]==fresh.cn[u][v],"VERIFY_CN_CACHE");}
        need(metrics.f3==metrics.hist[1]+metrics.hist[2]&&metrics.hist[0]+metrics.hist[1]+metrics.hist[2]==n*(n-1)/2,"VERIFY_RESIDUES");
        if(n==99)need(metrics.f3<=metrics.energy()&&metrics.energy()<=28*metrics.f3&&(metrics.hist[1]-metrics.hist[2])%3==0,"VERIFY_TARGET_NECESSITY");
    }
    void cn_change(int u,int v,int delta){const int updated=cn[u][v]+delta;const auto before=cost(cn[u][v],a[u][v]);const auto after=cost(updated,a[u][v]);change(metrics,before,after);cn[u][v]=cn[v][u]=updated;}
    void toggle(int u,int v,int delta){need(u!=v&&((delta==1&&!a[u][v])||(delta==-1&&a[u][v])),"EDGE_PRECONDITION");
        for(int w=0;w<n;++w)if(w!=u&&w!=v){if(a[v][w])cn_change(u,w,delta);if(a[u][w])cn_change(v,w,delta);}
        change(metrics,cost(cn[u][v],a[u][v]),cost(cn[u][v],a[u][v]+delta));a[u][v]+=delta;a[v][u]+=delta;masks[u][v/64]^=UINT64_C(1)<<(v%64);masks[v][u/64]^=UINT64_C(1)<<(u%64);
    }
};
struct Config{
    std::uint64_t seed=0,mix=0,schedule=0;
    double start=0,end=0;
    bool forced=false;
};
struct Options{
    Config config;
    std::string fixture,input,source,resume,out;
    std::uint64_t steps=0,verify_every=1,checkpoint_every=1,trace_prefix=0,trace_stride=0;
    double seconds=0,checkpoint_seconds=1;
    bool stop_zero=false,pair_costs=false,probes=false;
};
struct Zero{
    std::uint64_t step=0,admissible=0,accepted=0,updates=0,words=0;
    std::array<std::uint64_t,4> rng{};
    std::vector<Triple> rows;
};
struct State{
    Graph graph;
    std::vector<Triple> best;
    Metrics best_metrics;
    RNG rng;
    Config config;
    std::string source;
    std::uint64_t step=0,admissible=0,accepted=0,updates=0;
    std::vector<Zero> zeros;
    State(Graph g,Config c,std::string identity):graph(std::move(g)),best(graph.rows),best_metrics(graph.metrics),rng(c.seed),config(c),source(std::move(identity)){}
};
static void write_raw(const std::filesystem::path& p,const std::string& raw){need(!std::filesystem::exists(p),"OUTPUT_EXISTS");std::ofstream f(p,std::ios::binary);need(static_cast<bool>(f),"OUTPUT_OPEN");f<<raw;f.flush();need(static_cast<bool>(f),"OUTPUT_WRITE");}
static void write_rng(std::ostream& f,const std::string& name,const std::array<std::uint64_t,4>& values){f<<name;for(auto x:values)f<<' '<<x;f<<'\n';}
static std::array<std::uint64_t,4> read_rng(Reader& r,const std::string& name){r.tag(name);std::array<std::uint64_t,4> values{};for(auto& x:values)x=r.number();need((values[0]|values[1]|values[2]|values[3])!=0,"RNG_ZERO");return values;}
static void counters(std::uint64_t step,std::uint64_t valid,std::uint64_t accepted,std::uint64_t updates,std::uint64_t words){need(step<=UINT64_C(0x0fffffffffffffff)&&updates<=accepted&&accepted<=valid&&valid<=step&&words>=4*step+valid,"STATE_COUNTERS");}
static void config_check(const Config& c){need(c.schedule>0&&std::isfinite(c.start)&&std::isfinite(c.end)&&c.start>=0&&c.end>=0&&c.start<=1e12&&c.end<=1e12,"CONFIG_SCHEDULE");}
static bool capture(State& s){
    if(s.graph.metrics.f3!=0)return false;
    const auto bytes=s.graph.adjacency();for(const auto& z:s.zeros)if(Graph(s.graph.n,s.graph.degree,z.rows).adjacency()==bytes)return false;
    s.zeros.push_back(Zero{s.step,s.admissible,s.accepted,s.updates,s.rng.words,s.rng.s,s.graph.rows});
    return true;
}
static void save_state(const std::filesystem::path& path,const State& s){
    std::ostringstream f;f<<std::setprecision(17)<<"HYPERGRAPH_TERNARY_MIXED_STATE_V1\nobjective "<<OBJECTIVE<<"\nmove_kernel "<<KERNEL<<"\ndistribution "<<DISTRIBUTION<<"\nsource_graph_sha256 "<<s.source<<"\nn "<<s.graph.n<<"\ndegree "<<s.graph.degree<<"\nscalar_weight "<<s.graph.weight()<<'\n';
    f<<"seed "<<s.config.seed<<"\nmix_steps "<<s.config.mix<<"\nschedule_steps "<<s.config.schedule<<"\nt_start "<<s.config.start<<"\nt_end "<<s.config.end<<"\nforced "<<s.config.forced<<'\n';
    f<<"step "<<s.step<<"\nadmissible "<<s.admissible<<"\naccepted "<<s.accepted<<"\nbest_updates "<<s.updates<<"\nrng_words "<<s.rng.words<<'\n';write_rng(f,"rng",s.rng.s);
    write_metrics(f,"current_metrics",s.graph.metrics,s.graph.weight());write_metrics(f,"best_metrics",s.best_metrics,s.graph.weight());write_rows(f,"current",s.graph.rows);write_rows(f,"best",s.best);
    f<<"cn "<<s.graph.n*(s.graph.n-1)/2<<'\n';for(int u=0;u<s.graph.n;++u)for(int v=u+1;v<s.graph.n;++v)f<<s.graph.cn[u][v]<<'\n';
    f<<"zero_archive "<<s.zeros.size()<<'\n';for(const auto& z:s.zeros){f<<"zero_step "<<z.step<<"\nzero_admissible "<<z.admissible<<"\nzero_accepted "<<z.accepted<<"\nzero_updates "<<z.updates<<"\nzero_rng_words "<<z.words<<'\n';write_rng(f,"zero_rng",z.rng);write_rows(f,"zero_triples",z.rows);}f<<"END\n";write_raw(path,f.str());
}
static State resume(const Options& o){
    Reader r(o.resume);r.tag("HYPERGRAPH_TERNARY_MIXED_STATE_V1");need(r.text("objective")==OBJECTIVE&&r.text("move_kernel")==KERNEL&&r.text("distribution")==DISTRIBUTION,"STATE_VERSION");const auto source=r.text("source_graph_sha256");need(hash_text(source)&&source==o.source,"SOURCE_GRAPH_HASH");
    const int n=small(r.num("n"),MAX_N),degree=small(r.num("degree"),49);domain(n,degree);const auto w=r.num("scalar_weight");
    need(w==static_cast<std::uint64_t>(scalar_weight(n,degree)),"STATE_SCALAR_WEIGHT");
    Config c;c.seed=r.num("seed");c.mix=r.num("mix_steps");c.schedule=r.num("schedule_steps");c.start=r.floating("t_start");c.end=r.floating("t_end");const auto forced=r.num("forced");need(forced<=1,"STATE_FORCED");c.forced=forced!=0;config_check(c);
    need(c.seed==o.config.seed&&c.mix==o.config.mix&&c.schedule==o.config.schedule&&c.start==o.config.start&&c.end==o.config.end&&c.forced==o.config.forced,"RESUME_CONFIG_MISMATCH");
    const auto step=r.num("step"),valid=r.num("admissible"),accepted=r.num("accepted"),updates=r.num("best_updates"),words=r.num("rng_words");const auto rng=read_rng(r,"rng");counters(step,valid,accepted,updates,words);
    const auto current=read_metrics(r,"current_metrics",static_cast<std::int64_t>(w)),best=read_metrics(r,"best_metrics",static_cast<std::int64_t>(w));
    State s(Graph(n,degree,triples(r,"current",n,degree)),c,source);s.best=triples(r,"best",n,degree);const Graph b(n,degree,s.best);
    need(w==static_cast<std::uint64_t>(s.graph.weight())&&s.graph.metrics==current&&b.metrics==best&&!less(current,best),"STATE_SCORES");s.best_metrics=best;
    need(r.num("cn")==static_cast<std::uint64_t>(n*(n-1)/2),"STATE_CN_POPULATION");for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)need(r.number()==static_cast<std::uint64_t>(s.graph.cn[u][v]),"STATE_CN_CACHE");
    const auto count=r.num("zero_archive");need(count<=step+1,"STATE_ZERO_POPULATION");std::set<std::string> identities;
    for(std::uint64_t at=0;at<count;++at){Zero z;z.step=r.num("zero_step");z.admissible=r.num("zero_admissible");z.accepted=r.num("zero_accepted");z.updates=r.num("zero_updates");z.words=r.num("zero_rng_words");z.rng=read_rng(r,"zero_rng");z.rows=triples(r,"zero_triples",n,degree);Graph g(n,degree,z.rows);counters(z.step,z.admissible,z.accepted,z.updates,z.words);
        if(z.step==0){const RNG initial(c.seed);need(z.admissible==0&&z.accepted==0&&z.updates==0&&z.words==0&&z.rng==initial.s&&(step!=0||z.rows==s.graph.rows),"STATE_ZERO_INITIAL_RESET");}
        need(g.metrics.f3==0&&z.step<=step&&z.admissible<=valid&&z.accepted<=accepted&&z.updates<=updates&&z.words<=words&&identities.insert(g.adjacency()).second,"STATE_ZERO_OBJECT");if(!s.zeros.empty())need(s.zeros.back().step<z.step,"STATE_ZERO_ORDER");s.zeros.push_back(std::move(z));}
    need(s.graph.metrics.f3!=0||identities.count(s.graph.adjacency())!=0,"STATE_ZERO_COMPLETENESS");
    need(b.metrics.f3!=0||identities.count(b.adjacency())!=0,"STATE_BEST_ZERO_COMPLETENESS");
    need(s.zeros.empty()||b.metrics.f3==0,"STATE_ZERO_BEST_ORDER");
    if(step==0){const RNG initial(c.seed);need(valid==0&&accepted==0&&updates==0&&words==0&&rng==initial.s&&s.best==s.graph.rows,"STATE_INITIAL_RESET");}
    r.end();s.step=step;s.admissible=valid;s.accepted=accepted;s.updates=updates;s.rng.words=words;s.rng.s=rng;return s;
}
static void export_zero(const std::filesystem::path& out,const State& s,std::size_t index){
    need(index<s.zeros.size(),"ZERO_EXPORT_INDEX");const auto& z=s.zeros[index];Graph g(s.graph.n,s.graph.degree,z.rows);g.verify();
    std::filesystem::create_directories(out/"zero_objects");const auto prefix=out/"zero_objects"/("object_"+std::to_string(index));
    write_raw(prefix.string()+".adj",g.adjacency());std::ostringstream f;
    f<<"TERNARY_RETAINED_ZERO_TRIPLES_V1\nstep "<<z.step<<"\nn "<<g.n<<"\ndegree "<<g.degree<<'\n';write_rows(f,"triples",z.rows);f<<"END\n";write_raw(prefix.string()+".triples",f.str());
}
static std::vector<Triple> fixture(const std::string& name){
    if(name=="rook9")return {{0,1,2},{3,4,5},{6,7,8},{0,3,6},{1,4,7},{2,5,8}};
    if(name=="prism9")return {{0,2,6},{0,1,7},{1,2,8},{3,5,6},{3,4,7},{4,5,8}};
    if(name=="cube12")return {{0,1,2},{0,3,4},{1,5,6},{3,5,7},{2,8,9},{4,8,10},{6,9,11},{7,10,11}};
    need(name=="target99","FIXTURE_NAME");std::vector<Triple> rows;for(int x=0;x<33;++x)rows.push_back({x,x+33,x+66});for(int x=0;x<99;++x)rows.push_back({x,(x+1)%99,(x+4)%99});for(int x=0;x<99;++x)rows.push_back({x,(x+7)%99,(x+18)%99});return rows;
}
static State initialize(const Options& o){
    if(!o.resume.empty())return resume(o);
    if(!o.input.empty()){Reader r(o.input);r.tag("TERNARY_LINEAR_GRAPH_INPUT_V1");const int n=small(r.num("n"),MAX_N),degree=small(r.num("degree"),49);domain(n,degree);const auto source=r.text("source_graph_sha256");need(hash_text(source)&&source==o.source,"GRAPH_SOURCE_IDENTITY");State s(Graph(n,degree,triples(r,"triples",n,degree)),o.config,source);r.end();return s;}
    const int n=o.fixture=="target99"?99:o.fixture=="cube12"?12:9;return State(Graph(n,n==99?7:2,fixture(o.fixture)),o.config,std::string(64,'0'));
}
static void json_metrics(std::ostream& f,const Metrics& m,std::int64_t w){f<<"{\"F3\":"<<m.f3<<",\"E_lambda\":"<<m.el<<",\"E_mu\":"<<m.em<<",\"E\":"<<m.energy()<<",\"scalar_weight\":"<<w<<",\"scalar\":"<<m.scalar(w)<<",\"residue_population\":["<<m.hist[0]<<','<<m.hist[1]<<','<<m.hist[2]<<"]}";}
static void json_rng(std::ostream& f,const std::array<std::uint64_t,4>& words){f<<'[';for(int k=0;k<4;++k)f<<(k?",":"")<<'"'<<words[k]<<'"';f<<']';}
static double temperature(const State& s){const auto elapsed=s.step>s.config.mix?s.step-s.config.mix:0;const double fraction=std::min(1.0,static_cast<double>(elapsed)/static_cast<double>(s.config.schedule));return s.config.start+(s.config.end-s.config.start)*fraction;}
static void pair_costs(const std::filesystem::path& path){std::ostringstream f;for(int c=0;c<=99;++c)for(int a=0;a<=1;++a){const auto before=cost(c,a);for(int delta:{-1,1})if(c+delta>=0&&c+delta<=99){const auto after=cost(c+delta,a);f<<"{\"kind\":\"CN\",\"c\":"<<c<<",\"a\":"<<a<<",\"delta\":"<<delta<<",\"new_c\":"<<c+delta<<",\"new_a\":"<<a<<",\"old_residue\":"<<before.residue<<",\"new_residue\":"<<after.residue<<",\"delta_F3\":"<<after.f3-before.f3<<",\"delta_lambda\":"<<after.el-before.el<<",\"delta_mu\":"<<after.em-before.em<<"}\n";}
        const auto after=cost(c,1-a);f<<"{\"kind\":\"EDGE\",\"c\":"<<c<<",\"a\":"<<a<<",\"delta\":"<<1-2*a<<",\"new_c\":"<<c<<",\"new_a\":"<<1-a<<",\"old_residue\":"<<before.residue<<",\"new_residue\":"<<after.residue<<",\"delta_F3\":"<<after.f3-before.f3<<",\"delta_lambda\":"<<after.el-before.el<<",\"delta_mu\":"<<after.em-before.em<<"}\n";}write_raw(path,f.str());}
static void probes(const std::filesystem::path& out,State& s){
    need(s.graph.n<=12&&s.step==0,"PROBE_SCOPE");std::ostringstream f;std::uint64_t id=0;
    const auto original=s.graph.rows;const auto before=s.graph.metrics;const int m=static_cast<int>(original.size());
    for(int ti=0;ti<m;++ti)for(int tj=ti+1;tj<m;++tj)for(int pi=0;pi<3;++pi)for(int pj=0;pj<3;++pj,++id){
        const auto t=original[ti],q=original[tj];const int x=t[pi],y=q[pj];
        const bool exclusive=std::find(q.begin(),q.end(),x)==q.end()&&std::find(t.begin(),t.end(),y)==t.end();bool disjoint=true;for(int u:t)for(int v:q)if(u==v)disjoint=false;
        const int a=t[(pi+1)%3],b=t[(pi+2)%3],c=q[(pj+1)%3],d=q[(pj+2)%3];const std::array<std::array<int,3>,8> edges={{{x,a,-1},{x,b,-1},{y,c,-1},{y,d,-1},{y,a,1},{y,b,1},{x,c,1},{x,d,1}}};
        bool absent=true;for(int k=4;k<8;++k){bool removed=false;const int u=edges[k][0],v=edges[k][1];for(int j=0;j<4;++j)if((u==edges[j][0]&&v==edges[j][1])||(u==edges[j][1]&&v==edges[j][0]))removed=true;if(u==v||(s.graph.a[u][v]&&!removed))absent=false;}
        const bool valid=exclusive&&absent;Metrics candidate=before;
        if(valid){for(const auto& edge:edges)s.graph.toggle(edge[0],edge[1],edge[2]);s.graph.rows[ti][pi]=y;s.graph.rows[tj][pj]=x;s.graph.verify();candidate=s.graph.metrics;
            for(auto e=edges.rbegin();e!=edges.rend();++e){s.graph.toggle((*e)[0],(*e)[1],-(*e)[2]);}
            s.graph.rows=original;s.graph.verify();need(s.graph.metrics==before,"PROBE_ROLLBACK");}
        f<<"{\"schema\":\"HYPERGRAPH_TERNARY_MIXED_PROBE_V1\",\"proposal_id\":"<<id<<",\"ti\":"<<ti<<",\"tj\":"<<tj<<",\"pi\":"<<pi<<",\"pj\":"<<pj<<",\"disjoint\":"<<(disjoint?"true":"false")<<",\"exclusive\":"<<(exclusive?"true":"false")<<",\"absent_after_removal\":"<<(absent?"true":"false")<<",\"admissible\":"<<(valid?"true":"false")<<",\"retained\":false,\"before\":";json_metrics(f,before,s.graph.weight());f<<",\"candidate\":";json_metrics(f,candidate,s.graph.weight());f<<",\"rollback\":";json_metrics(f,s.graph.metrics,s.graph.weight());f<<",\"delta_scalar\":"<<candidate.scalar(s.graph.weight())-before.scalar(s.graph.weight())<<"}\n";
    }
    write_raw(out/"probes.jsonl",f.str());
}
static Options parse(int argc,char** argv){
    Options o;std::set<std::string> seen;
    for(int k=1;k<argc;++k){const std::string name=argv[k];need(seen.insert(name).second,"ARG_DUPLICATE");
        if(name=="--forced"){o.config.forced=true;continue;}if(name=="--stop-at-zero"){o.stop_zero=true;continue;}if(name=="--emit-pair-costs"){o.pair_costs=true;continue;}if(name=="--probe-all"){o.probes=true;continue;}need(k+1<argc,"ARG_VALUE");const std::string value=argv[++k];
        if(name=="--fixture")o.fixture=value;else if(name=="--graph-input")o.input=value;else if(name=="--source-graph-sha256")o.source=value;else if(name=="--resume")o.resume=value;else if(name=="--out")o.out=value;
        else if(name=="--seed")o.config.seed=integer(value);else if(name=="--steps")o.steps=integer(value);else if(name=="--mix-steps")o.config.mix=integer(value);else if(name=="--schedule-steps")o.config.schedule=integer(value);
        else if(name=="--verify-every")o.verify_every=integer(value);else if(name=="--checkpoint-every")o.checkpoint_every=integer(value);else if(name=="--trace-prefix")o.trace_prefix=integer(value);else if(name=="--trace-stride")o.trace_stride=integer(value);
        else if(name=="--temperature-start")o.config.start=real(value);else if(name=="--temperature-end")o.config.end=real(value);else if(name=="--seconds")o.seconds=real(value);else if(name=="--checkpoint-seconds")o.checkpoint_seconds=real(value);else need(false,"ARG_UNKNOWN");}
    for(const std::string name:{"--out","--seed","--steps","--mix-steps","--schedule-steps","--temperature-start","--temperature-end","--seconds"})need(seen.count(name)!=0,"ARG_REQUIRED:"+name);
    need(static_cast<int>(!o.fixture.empty())+static_cast<int>(!o.input.empty())+static_cast<int>(!o.resume.empty())==1,"ARG_INPUT_EXCLUSIVE");need((!o.input.empty()||!o.resume.empty())==!o.source.empty()&&(o.source.empty()||hash_text(o.source)),"ARG_GRAPH_SOURCE");
    config_check(o.config);need(o.steps<=UINT64_C(0x0fffffffffffffff)&&o.verify_every>0&&o.checkpoint_every>0&&o.checkpoint_seconds>0&&o.seconds>0&&o.seconds<=21600,"ARG_LIMITS");return o;
}

int main(int argc,char** argv){
    try{
        std::signal(SIGTERM,signal_stop);std::signal(SIGINT,signal_stop);const auto started=Clock::now();const Options o=parse(argc,argv);need(!std::filesystem::exists(o.out),"OUTPUT_EXISTS");std::filesystem::create_directories(o.out);
        State s=initialize(o);need(s.step<=UINT64_C(0x0fffffffffffffff)-o.steps,"STATE_RUN_COUNTER_LIMIT");capture(s);s.graph.verify();save_state(std::filesystem::path(o.out)/"initial.state",s);
        for(std::size_t k=0;k<s.zeros.size();++k)export_zero(o.out,s,k);
        if(o.pair_costs)pair_costs(std::filesystem::path(o.out)/"pair_costs.jsonl");
        if(o.probes)probes(o.out,s);
        const auto initial=s.graph.metrics;const auto starting=s.step;std::uint64_t performed=0;auto last=Clock::now();std::ofstream trace(std::filesystem::path(o.out)/"moves.jsonl");trace<<std::setprecision(17);std::string stop="REQUESTED_STEPS_COMPLETE";
        for(;performed<o.steps;++performed){
            if((performed&255)==0){if(stop_signal){stop="SIGNAL_STOP_SAVED";break;}if(std::chrono::duration<double>(Clock::now()-started).count()>=o.seconds){stop="ALLOCATED_NATIVE_BUDGET_REACHED";break;}}
            if((o.stop_zero||s.graph.n==99)&&s.graph.metrics.f3==0){stop="RAW_F3_ZERO_PENDING_INDEPENDENT_FULL_INTEGER_SRG_VALIDATOR";break;}
            const auto before_rng=s.rng.s;const auto before_words=s.rng.words;const auto before=s.graph.metrics;const int m=static_cast<int>(s.graph.rows.size());const int ti=static_cast<int>(s.rng.bounded(m));int tj=static_cast<int>(s.rng.bounded(m-1));if(tj>=ti)++tj;const int pi=static_cast<int>(s.rng.bounded(3)),pj=static_cast<int>(s.rng.bounded(3));
            const auto t=s.graph.rows[ti],q=s.graph.rows[tj];const int x=t[pi],y=q[pj];bool exclusive=std::find(q.begin(),q.end(),x)==q.end()&&std::find(t.begin(),t.end(),y)==t.end();bool disjoint=true;for(int a:t)for(int b:q)if(a==b)disjoint=false;
            const int a=t[(pi+1)%3],b=t[(pi+2)%3],c=q[(pj+1)%3],d=q[(pj+2)%3];const std::array<std::array<int,3>,8> edges={{{x,a,-1},{x,b,-1},{y,c,-1},{y,d,-1},{y,a,1},{y,b,1},{x,c,1},{x,d,1}}};
            bool absent=true;for(int k=4;k<8;++k){bool removed=false;const int u=edges[k][0],v=edges[k][1];for(int j=0;j<4;++j)if((u==edges[j][0]&&v==edges[j][1])||(u==edges[j][1]&&v==edges[j][0]))removed=true;if(u==v||(s.graph.a[u][v]&&!removed))absent=false;}
            const bool valid=exclusive&&absent;const double temp=temperature(s);const bool mixing=s.step<s.config.mix;bool accepted=false;std::uint64_t draw=0;Metrics proposed=before;std::int64_t delta=0;
            if(valid){++s.admissible;for(const auto& e:edges)s.graph.toggle(e[0],e[1],e[2]);proposed=s.graph.metrics;delta=proposed.scalar(s.graph.weight())-before.scalar(s.graph.weight());draw=s.rng.next();const double u=static_cast<double>(draw>>11)*0x1.0p-53;accepted=s.config.forced||mixing||delta<=0||(temp>0&&u<std::exp(-static_cast<double>(delta)/temp));
                if(accepted){s.graph.rows[ti][pi]=y;s.graph.rows[tj][pj]=x;++s.accepted;if(less(s.graph.metrics,s.best_metrics)){s.best=s.graph.rows;s.best_metrics=s.graph.metrics;++s.updates;}}
                else{for(auto e=edges.rbegin();e!=edges.rend();++e)s.graph.toggle((*e)[0],(*e)[1],-(*e)[2]);need(s.graph.metrics==before,"ROLLBACK_METRICS");}}
            ++s.step;if(capture(s)){s.graph.verify();export_zero(o.out,s,s.zeros.size()-1);save_state(std::filesystem::path(o.out)/("zero_capture_"+std::to_string(s.step)+".state"),s);}
            if(s.step-1<o.trace_prefix||(o.trace_stride&&(s.step-1)%o.trace_stride==0)){
                auto nt=t,nq=q;nt[pi]=y;nq[pj]=x;trace<<"{\"schema\":\"HYPERGRAPH_TERNARY_MIXED_MOVE_V1\",\"objective\":\""<<OBJECTIVE<<"\",\"move_kernel\":\""<<KERNEL<<"\",\"distribution\":\""<<DISTRIBUTION<<"\",\"step\":"<<s.step-1<<",\"ti\":"<<ti<<",\"tj\":"<<tj<<",\"pi\":"<<pi<<",\"pj\":"<<pj<<",\"old_triples\":[["<<t[0]<<','<<t[1]<<','<<t[2]<<"],["<<q[0]<<','<<q[1]<<','<<q[2]<<"]],\"proposed_triples\":[["<<nt[0]<<','<<nt[1]<<','<<nt[2]<<"],["<<nq[0]<<','<<nq[1]<<','<<nq[2]<<"]],\"disjoint\":"<<(disjoint?"true":"false")<<",\"exclusive\":"<<(exclusive?"true":"false")<<",\"absent_after_removal\":"<<(absent?"true":"false")<<",\"admissible\":"<<(valid?"true":"false")<<",\"accepted\":"<<(accepted?"true":"false")<<",\"mixing\":"<<(mixing?"true":"false")<<",\"temperature\":"<<temp<<",\"delta_scalar\":"<<delta<<",\"before\":";json_metrics(trace,before,s.graph.weight());trace<<",\"candidate\":";json_metrics(trace,proposed,s.graph.weight());trace<<",\"after\":";json_metrics(trace,s.graph.metrics,s.graph.weight());trace<<",\"best\":";json_metrics(trace,s.best_metrics,s.graph.weight());trace<<",\"draw\":\""<<draw<<"\",\"rng_words_before\":"<<before_words<<",\"rng_words_after\":"<<s.rng.words<<",\"rng_before\":";json_rng(trace,before_rng);trace<<",\"rng_after\":";json_rng(trace,s.rng.s);trace<<",\"retained_zero_objects\":"<<s.zeros.size()<<"}\n";}
            if(s.step%o.verify_every==0)s.graph.verify();
            if(s.step%o.checkpoint_every==0||std::chrono::duration<double>(Clock::now()-last).count()>=o.checkpoint_seconds){s.graph.verify();save_state(std::filesystem::path(o.out)/("checkpoint_"+std::to_string(s.step)+".state"),s);last=Clock::now();std::cout<<"CHECKPOINT "<<s.step<<' '<<s.graph.metrics.f3<<' '<<s.graph.metrics.energy()<<' '<<s.best_metrics.f3<<' '<<s.best_metrics.energy()<<std::endl;}
        }
        s.graph.verify();Graph best(s.graph.n,s.graph.degree,s.best);best.verify();save_state(std::filesystem::path(o.out)/"final.state",s);write_raw(std::filesystem::path(o.out)/"current.adj",s.graph.adjacency());write_raw(std::filesystem::path(o.out)/"best.adj",best.adjacency());
        std::ostringstream selection;selection<<"{\"schema\":\"TERNARY_RETAINED_ZERO_SELECTION_V1\",\"selection_rule\":\"First RETAINED current F3zero object, including initial; every distinct retained zero matrix preserved. No unobserved earliest trajectory claim.\",\"found\":"<<(!s.zeros.empty()?"true":"false")<<",\"first_step\":"<<(s.zeros.empty()?"null":std::to_string(s.zeros[0].step))<<",\"retained_distinct_objects\":"<<s.zeros.size()<<",\"carried_from_resume\":"<<(!o.resume.empty()&&!s.zeros.empty()&&s.zeros[0].step<=starting?"true":"false")<<",\"target_resolution\":false,\"independent_approval\":false}\n";write_raw(std::filesystem::path(o.out)/"zero_selection.json",selection.str());
        trace.flush();need(static_cast<bool>(trace),"TRACE_WRITE");std::ostringstream result;result<<std::setprecision(17)<<"{\"objective\":\""<<OBJECTIVE<<"\",\"move_kernel\":\""<<KERNEL<<"\",\"distribution\":\""<<DISTRIBUTION<<"\",\"n\":"<<s.graph.n<<",\"point_degree\":"<<s.graph.degree<<",\"initial\":";json_metrics(result,initial,s.graph.weight());result<<",\"current\":";json_metrics(result,s.graph.metrics,s.graph.weight());result<<",\"best\":";json_metrics(result,s.best_metrics,s.graph.weight());result<<",\"starting_step\":"<<starting<<",\"ending_step\":"<<s.step<<",\"proposals_this_invocation\":"<<performed<<",\"admissible_total\":"<<s.admissible<<",\"accepted_total\":"<<s.accepted<<",\"best_updates_total\":"<<s.updates<<",\"rng_words_total\":"<<s.rng.words<<",\"retained_zero_objects\":"<<s.zeros.size()<<",\"stop_reason\":\""<<stop<<"\",\"elapsed_seconds\":"<<std::chrono::duration<double>(Clock::now()-started).count()<<",\"historical_native_state_written\":false,\"independent_approval\":false,\"target_resolution\":false}\n";write_raw(std::filesystem::path(o.out)/"result.json",result.str());std::cout<<"NATIVE_RESULT_PRESERVED "<<s.graph.n<<' '<<s.graph.metrics.f3<<' '<<s.graph.metrics.energy()<<' '<<s.best_metrics.f3<<' '<<s.best_metrics.energy()<<std::endl;return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 2;}
}
