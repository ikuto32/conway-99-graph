#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <sys/resource.h>
#include <vector>

// Producer ancestry: the versioned GF2 primal worker's containment/checkpoint
// shape, with NEW ternary algebra and weighted original-row DAG. Independent
// checking must use raw scalar rows, never import/reuse this eliminator.
using Clock=std::chrono::steady_clock;
using Words=std::vector<std::uint64_t>;
using RHS=std::array<unsigned char,3>;
static void need(bool ok,const std::string& text){if(!ok)throw std::runtime_error(text);}
static std::uint64_t number(const std::string& s){need(!s.empty()&&s.find_first_not_of("0123456789")==std::string::npos,"unsigned decimal option");return std::stoull(s);}
struct ResourceReport{
    std::string out;Clock::time_point started;
    ResourceReport(const std::string& path,Clock::time_point time):out(path),started(time){}
    ~ResourceReport(){
        struct rusage usage{};if(getrusage(RUSAGE_SELF,&usage)!=0)return;
        std::ofstream f(std::filesystem::path(out)/"native_resources.json");
        f<<std::setprecision(17)<<"{\"method\":\"getrusage_RUSAGE_SELF\",\"ru_maxrss\":"<<usage.ru_maxrss<<",\"ru_maxrss_unit\":\"LinuxKiB\",\"user_microseconds\":"<<usage.ru_utime.tv_sec*UINT64_C(1000000)+usage.ru_utime.tv_usec
         <<",\"system_microseconds\":"<<usage.ru_stime.tv_sec*UINT64_C(1000000)+usage.ru_stime.tv_usec<<",\"wall_seconds\":"<<std::chrono::duration<double>(Clock::now()-started).count()<<",\"whole_group_peak_memory\":false,\"performance_guarantee\":false}\n";
    }
};
struct Options{
    std::string input,input_sha,out,resume;
    double seconds=0;
    std::uint64_t checkpoint_every=4096,stop_after=std::numeric_limits<std::uint64_t>::max();
    bool arithmetic=false;
};
static Options options(int argc,char** argv){
    Options o;
    for(int i=1;i<argc;++i){std::string k=argv[i];if(k=="--arithmetic-controls"){o.arithmetic=true;continue;}
        need(i+1<argc,"option value");std::string v=argv[++i];
        if(k=="--input")o.input=v;else if(k=="--input-sha256")o.input_sha=v;else if(k=="--out")o.out=v;
        else if(k=="--resume")o.resume=v;else if(k=="--seconds")o.seconds=std::stod(v);
        else if(k=="--checkpoint-every")o.checkpoint_every=number(v);else if(k=="--stop-after-rows")o.stop_after=number(v);
        else need(false,"unknown option");
    }
    need(std::isfinite(o.seconds)&&o.seconds>0&&o.seconds<=21600&&o.checkpoint_every>0,"finite command allocation");
    need(!o.out.empty(),"output option");
    if(!o.arithmetic)need(!o.input.empty()&&o.input_sha.size()==64&&o.input_sha.find_first_not_of("0123456789abcdef")==std::string::npos,"input/hash options");
    return o;
}
struct Packed{
    Words one,two;
    explicit Packed(std::uint64_t words=0):one(words,0),two(words,0){}
};
static unsigned char trit(const Packed& row,std::uint64_t c){return static_cast<unsigned char>(((row.one[c/64]>>(c%64))&1)+2*((row.two[c/64]>>(c%64))&1));}
static void set_trit(Packed& row,std::uint64_t c,unsigned char v){
    need(v<=2,"packed trit domain");const auto bit=UINT64_C(1)<<(c%64);row.one[c/64]&=~bit;row.two[c/64]&=~bit;
    if(v==1)row.one[c/64]|=bit;else if(v==2)row.two[c/64]|=bit;
}
static void packed_add(Packed& x,const Packed& y,unsigned char scale,std::uint64_t first=0){
    need(scale==1||scale==2,"packed nonzero scale");
    for(std::uint64_t w=first;w<x.one.size();++w){
        const auto x1=x.one[w],x2=x.two[w],y1=scale==1?y.one[w]:y.two[w],y2=scale==1?y.two[w]:y.one[w];
        const auto x0=~(x1|x2),y0=~(y1|y2);
        x.one[w]=(x0&y1)|(x1&y0)|(x2&y2);
        x.two[w]=(x0&y2)|(x2&y0)|(x1&y1);
    }
}
static RHS rhs_add(const RHS& x,const RHS& y,unsigned char scale){RHS z{};for(int j=0;j<3;++j)z[j]=static_cast<unsigned char>((x[j]+scale*y[j])%3);return z;}
struct Dep{std::uint32_t pivot;unsigned char coefficient;};
struct State{
    std::uint64_t n,m,words,processed=0;
    std::vector<Packed> basis;
    std::vector<RHS> rhs;
    std::vector<unsigned char> present,origin_scale;
    std::vector<std::uint64_t> origin,order_index,order;
    std::vector<std::vector<Dep>> dependencies;
    State(std::uint64_t n_,std::uint64_t m_):n(n_),m(m_),words((n_+63)/64),basis(n_),rhs(n_),present(n_,0),origin_scale(n_,0),origin(n_),order_index(n_),dependencies(n_){}
};
static void write_u64(std::ostream& f,std::uint64_t x){f.write(reinterpret_cast<const char*>(&x),sizeof(x));}
static std::uint64_t read_u64(std::istream& f){std::uint64_t x;need(static_cast<bool>(f.read(reinterpret_cast<char*>(&x),sizeof(x))),"checkpoint integer");return x;}
static void write_u32(std::ostream& f,std::uint32_t x){f.write(reinterpret_cast<const char*>(&x),sizeof(x));}
static std::uint32_t read_u32(std::istream& f){std::uint32_t x;need(static_cast<bool>(f.read(reinterpret_cast<char*>(&x),sizeof(x))),"checkpoint reference integer");return x;}
static void checkpoint(const Options& o,const State& s,Clock::time_point started,const std::string& reason){
    const auto tmp=std::filesystem::path(o.out)/"checkpoint.tmp",path=std::filesystem::path(o.out)/"checkpoint.bin";
    std::ofstream f(tmp,std::ios::binary|std::ios::trunc);need(static_cast<bool>(f),"checkpoint open");const std::string magic="GF3_PRIMAL_CP_V1\n";
    f.write(magic.data(),magic.size());f.write(o.input_sha.data(),64);write_u64(f,s.n);write_u64(f,s.m);write_u64(f,s.words);write_u64(f,s.processed);
    for(std::uint64_t p=0;p<s.n;++p){f.put(static_cast<char>(s.present[p]));if(s.present[p]){
        for(auto v:s.rhs[p]){f.put(static_cast<char>(v));}
        f.put(static_cast<char>(s.origin_scale[p]));
        write_u64(f,s.origin[p]);write_u64(f,s.order_index[p]);write_u64(f,s.dependencies[p].size());
        for(auto d:s.dependencies[p]){write_u32(f,d.pivot);f.put(static_cast<char>(d.coefficient));}
        f.write(reinterpret_cast<const char*>(s.basis[p].one.data()),s.words*sizeof(std::uint64_t));
        f.write(reinterpret_cast<const char*>(s.basis[p].two.data()),s.words*sizeof(std::uint64_t));
    }}
    f.flush();need(static_cast<bool>(f),"complete checkpoint write");f.close();std::filesystem::rename(tmp,path);
    std::ofstream log(std::filesystem::path(o.out)/"progress.jsonl",std::ios::app);
    log<<std::setprecision(17)<<"{\"processed_rows\":"<<s.processed<<",\"total_rows\":"<<s.m<<",\"checkpoint_bytes\":"<<std::filesystem::file_size(path)
       <<",\"elapsed_seconds\":"<<std::chrono::duration<double>(Clock::now()-started).count()<<",\"reason\":\""<<reason<<"\"}\n";
    log.flush();need(static_cast<bool>(log),"checkpoint progress write");
}
static void restore(const Options& o,State& s){
    std::ifstream f(o.resume,std::ios::binary);const std::string magic="GF3_PRIMAL_CP_V1\n";std::string observed(magic.size(),' '),sha(64,' ');
    need(static_cast<bool>(f.read(observed.data(),observed.size()))&&observed==magic,"checkpoint version");
    need(static_cast<bool>(f.read(sha.data(),sha.size()))&&sha==o.input_sha,"checkpoint exact input hash");
    need(read_u64(f)==s.n&&read_u64(f)==s.m&&read_u64(f)==s.words,"checkpoint dimensions");s.processed=read_u64(f);need(s.processed<=s.m,"checkpoint completed row range");
    for(std::uint64_t p=0;p<s.n;++p){int present=f.get();need(present==0||present==1,"checkpoint presence");s.present[p]=static_cast<unsigned char>(present);
        if(present){for(auto& v:s.rhs[p]){int digit=f.get();need(digit>=0&&digit<=2,"checkpoint rhs trit");v=static_cast<unsigned char>(digit);}
            int scale=f.get();need(scale==1||scale==2,"checkpoint origin scale");s.origin_scale[p]=static_cast<unsigned char>(scale);
            s.origin[p]=read_u64(f);s.order_index[p]=read_u64(f);auto count=read_u64(f);
            need(s.origin[p]<s.processed&&s.order_index[p]<s.n&&count<=s.n,"checkpoint DAG record range");
            std::uint32_t prior=0;
            for(std::uint64_t k=0;k<count;++k){auto d=read_u32(f);int c=f.get();need(d<s.n&&(k==0||d>prior),"checkpoint ordered DAG reference");need(c==1||c==2,"checkpoint DAG coefficient");s.dependencies[p].push_back(Dep{d,static_cast<unsigned char>(c)});prior=d;}
            s.basis[p]=Packed(s.words);
            need(static_cast<bool>(f.read(reinterpret_cast<char*>(s.basis[p].one.data()),s.words*sizeof(std::uint64_t)))&&static_cast<bool>(f.read(reinterpret_cast<char*>(s.basis[p].two.data()),s.words*sizeof(std::uint64_t))),"checkpoint packed basis");
            for(std::uint64_t w=0;w<s.words;++w)need((s.basis[p].one[w]&s.basis[p].two[w])==0,"checkpoint disjoint planes");
            need(trit(s.basis[p],p)==1,"checkpoint leading one");
            for(std::uint64_t w=0;w<p/64;++w)need((s.basis[p].one[w]|s.basis[p].two[w])==0,"checkpoint pivot prefix");
            need(((s.basis[p].one[p/64]|s.basis[p].two[p/64])&((UINT64_C(1)<<(p%64))-1))==0,"checkpoint pivot low prefix");
            if(s.n%64)need(((s.basis[p].one.back()|s.basis[p].two.back())>>(s.n%64))==0,"checkpoint padding bits");
        }
    }
    std::uint64_t count=0;for(auto v:s.present)count+=v;s.order.resize(count,s.n);
    for(std::uint64_t p=0;p<s.n;++p)if(s.present[p]){
        need(s.order_index[p]<count&&s.order[s.order_index[p]]==s.n,"checkpoint DAG unique insertion order");s.order[s.order_index[p]]=p;
        for(auto d:s.dependencies[p])need(s.present[d.pivot]&&s.order_index[d.pivot]<s.order_index[p],"checkpoint DAG acyclic earlier reference");
    }
    need(f.get()==std::char_traits<char>::eof(),"checkpoint exact end");
}
struct InputRow{RHS rhs{};Packed packed;explicit InputRow(std::uint64_t words):packed(words){}};
static InputRow read_row(std::istream& f,std::uint64_t n,std::uint64_t words){
    InputRow row(words);std::uint64_t count=0,prior=0;
    for(auto& v:row.rhs){std::uint64_t x;need(static_cast<bool>(f>>x)&&x<=2,"sparse rhs trit");v=static_cast<unsigned char>(x);}
    need(static_cast<bool>(f>>count)&&count<=n,"sparse population");
    for(std::uint64_t k=0;k<count;++k){std::uint64_t c,v;need(static_cast<bool>(f>>c>>v)&&c<n&&(k==0||c>prior),"sparse ordered column range");need(v==1||v==2,"sparse coefficient trit");set_trit(row.packed,c,static_cast<unsigned char>(v));prior=c;}
    return row;
}
static void relation(const Options& o,const State& s,std::uint64_t current,const std::vector<Dep>& used,const RHS& expected){
    std::vector<unsigned char> active(s.n,0),rows(s.m,0);rows[current]=1;
    for(auto d:used)active[d.pivot]=static_cast<unsigned char>((active[d.pivot]+d.coefficient)%3);
    for(auto it=s.order.rbegin();it!=s.order.rend();++it){const auto p=*it;const auto t=active[p];if(t){
        rows[s.origin[p]]=static_cast<unsigned char>((rows[s.origin[p]]+t*s.origin_scale[p])%3);
        for(auto d:s.dependencies[p])active[d.pivot]=static_cast<unsigned char>((active[d.pivot]+t*d.coefficient)%3);
    }}
    std::ofstream out(std::filesystem::path(o.out)/"original_row_relation.json");
    out<<"{\"format\":\"ORIGINAL_LITERAL_GF3_ROW_RELATION_CANDIDATE_V1\",\"matrix_rows\":"<<s.m<<",\"matrix_columns\":"<<s.n<<",\"rhs_affine_residue\":["<<int(expected[0])<<','<<int(expected[1])<<','<<int(expected[2])<<"],\"original_row_coefficients\":[";
    bool first=true;for(std::uint64_t i=0;i<s.m;++i)if(rows[i]){if(!first)out<<',';out<<'['<<i<<','<<int(rows[i])<<']';first=false;}
    out<<"],\"independent_approval\":false,\"rank_claim\":false,\"target_resolution\":false}\n";out.flush();need(static_cast<bool>(out),"complete original row relation");
    std::ifstream input(o.input);std::string tag;std::uint64_t n,m;input>>tag>>n>>m;Packed total(s.words);RHS rhs{};
    for(std::uint64_t i=0;i<m;++i){auto row=read_row(input,n,s.words);if(rows[i]){packed_add(total,row.packed,rows[i]);rhs=rhs_add(rhs,row.rhs,rows[i]);}}
    need(rhs==expected&&rhs!=RHS{},"relation producer expected affine residual");for(std::uint64_t w=0;w<s.words;++w)need((total.one[w]|total.two[w])==0,"relation producer zero left side");
}
static unsigned char dot(const Packed& a,const Packed& b,std::uint64_t first=0){
    std::uint64_t sum=0;for(std::uint64_t w=first;w<a.one.size();++w){
        sum+=__builtin_popcountll(a.one[w]&b.one[w])+__builtin_popcountll(a.two[w]&b.two[w]);
        sum+=2*(__builtin_popcountll(a.one[w]&b.two[w])+__builtin_popcountll(a.two[w]&b.one[w]));
    }return static_cast<unsigned char>(sum%3);
}
static std::array<Packed,3> back_substitute(const State& s){
    std::array<Packed,3>x={Packed(s.words),Packed(s.words),Packed(s.words)};
    for(std::uint64_t p=s.n;p-->0;)if(s.present[p])for(int j=0;j<3;++j)set_trit(x[j],p,static_cast<unsigned char>((s.rhs[p][j]+3-dot(s.basis[p],x[j],p/64))%3));
    return x;
}
static void vector_file(const Options& o,const Packed& x,std::uint64_t n,const std::string& label){
    auto path=std::filesystem::path(o.out)/("x_"+label+".trits");need(!std::filesystem::exists(path),"immutable primal vector");std::ofstream f(path);
    f<<"GF3_AFFINE_PRIMAL_V1 "<<n<<' '<<label<<'\n';for(std::uint64_t i=0;i<n;++i)f<<int(trit(x,i));f<<'\n';f.flush();need(static_cast<bool>(f),"complete primal vector");
}
static int arithmetic_controls(const Options& o){
    std::ofstream f(std::filesystem::path(o.out)/"arithmetic.jsonl");
    for(unsigned char a=0;a<3;++a)for(unsigned char b=0;b<3;++b)for(unsigned char scale=1;scale<3;++scale){
        Packed x(3),y(3);for(auto p:{0,63,64,65,127,128,129}){set_trit(x,p,a);set_trit(y,p,b);}packed_add(x,y,scale);
        f<<"{\"kind\":\"PACKED_ADD\",\"a\":"<<int(a)<<",\"b\":"<<int(b)<<",\"scale\":"<<int(scale)<<",\"n\":130,\"one\":[";
        for(std::size_t w=0;w<3;++w){if(w)f<<',';f<<x.one[w];}f<<"],\"two\":[";for(std::size_t w=0;w<3;++w){if(w)f<<',';f<<x.two[w];}f<<"]}\n";
    }
    for(unsigned char a=0;a<3;++a)for(unsigned char b=0;b<3;++b)for(unsigned char c=0;c<3;++c)for(unsigned char scale=0;scale<3;++scale){RHS x{a,b,c},y{2,1,2};auto z=rhs_add(x,y,scale);
        f<<"{\"kind\":\"RHS_ADD\",\"rhs\":["<<int(a)<<','<<int(b)<<','<<int(c)<<"],\"other\":[2,1,2],\"scale\":"<<int(scale)<<",\"result\":["<<int(z[0])<<','<<int(z[1])<<','<<int(z[2])<<"]}\n";
    }
    f.flush();need(static_cast<bool>(f),"complete arithmetic control trace");return 0;
}
int main(int argc,char** argv){
    try{
        const auto started=Clock::now();const auto o=options(argc,argv);need(!std::filesystem::exists(o.out),"fresh native output");std::filesystem::create_directories(o.out);
        ResourceReport resources(o.out,started);
        if(o.arithmetic)return arithmetic_controls(o);
        std::ifstream f(o.input);std::string tag;std::uint64_t n,m;need(static_cast<bool>(f>>tag>>n>>m)&&tag=="GF3_AFFINE_SPARSE_V1"&&n>0&&n<=100000&&m>0&&m<=1000000,"sparse input header");
        State s(n,m);if(!o.resume.empty())restore(o,s);const auto starting=s.processed;
        auto expired=[&](){return std::chrono::duration<double>(Clock::now()-started).count()>=o.seconds;};
        auto stop=[&](const std::string& why){checkpoint(o,s,started,why);std::cout<<"PRIMAL_INCOMPLETE_CHECKPOINT "<<s.processed<<'\n';return 4;};
        for(std::uint64_t i=0;i<m;++i){auto input=read_row(f,n,s.words);if(i<starting)continue;
            if(expired()||s.processed>=o.stop_after)return stop(expired()?"ALLOCATED_NATIVE_BUDGET_REACHED":"DECLARED_PREFIX_CONTROL_STOP");
            auto row=std::move(input.packed);RHS rhs=input.rhs;std::uint64_t first=0,operations=0;bool inserted=false;std::vector<Dep> used;
            while(first<s.words){
                while(first<s.words&&(row.one[first]|row.two[first])==0)++first;
                if(first==s.words)break;
                const auto p=first*64+__builtin_ctzll(row.one[first]|row.two[first]);const auto value=trit(row,p);
                if(!s.present[p]){const auto scale=value;if(scale==2){std::swap(row.one,row.two);for(auto& v:rhs)v=static_cast<unsigned char>(2*v%3);for(auto& d:used)d.coefficient=static_cast<unsigned char>(2*d.coefficient%3);}
                    s.present[p]=1;s.basis[p]=std::move(row);s.rhs[p]=rhs;s.origin[p]=i;s.origin_scale[p]=scale;s.order_index[p]=s.order.size();s.order.push_back(p);s.dependencies[p]=std::move(used);inserted=true;break;
                }
                const auto scale=static_cast<unsigned char>(3-value);packed_add(row,s.basis[p],scale,first);rhs=rhs_add(rhs,s.rhs[p],scale);used.push_back(Dep{static_cast<std::uint32_t>(p),scale});
                if((++operations&1023)==0&&expired())return stop("ALLOCATED_NATIVE_BUDGET_REACHED");
            }
            if(!inserted&&rhs!=RHS{}){checkpoint(o,s,started,"INCONSISTENT_FIXED_INPUT");relation(o,s,i,used,rhs);std::cout<<"INCONSISTENT_FIXED_INPUT "<<i<<' '<<int(rhs[0])<<' '<<int(rhs[1])<<' '<<int(rhs[2])<<'\n';return 3;}
            s.processed=i+1;if(s.processed%o.checkpoint_every==0)checkpoint(o,s,started,"COMPLETED_ROW_PREFIX");
        }
        need(!(f>>tag),"sparse exact end");checkpoint(o,s,started,"COMPLETE_ELIMINATION_BACKSUB_PENDING");const auto x=back_substitute(s);
        for(int j=0;j<3;++j)vector_file(o,x[j],n,std::array<std::string,3>{"const","a","b"}[j]);
        f.close();f.open(o.input);f>>tag>>n>>m;std::ofstream residual(std::filesystem::path(o.out)/"row_residuals.bin",std::ios::binary);
        for(std::uint64_t i=0;i<m;++i){auto row=read_row(f,n,s.words);for(int j=0;j<3;++j){auto v=static_cast<unsigned char>((dot(row.packed,x[j])+3-row.rhs[j])%3);need(v==0,"producer exact primal row residual");residual.put(static_cast<char>(v));}}
        residual.flush();need(static_cast<bool>(residual),"complete residual file");struct rusage usage{};need(getrusage(RUSAGE_SELF,&usage)==0,"native resource measurement");
        std::ofstream result(std::filesystem::path(o.out)/"result.json");result<<std::setprecision(17)<<"{\"status\":\"CANDIDATE_THREE_LITERAL_GF3_PRIMALS\",\"columns\":"<<n<<",\"rows\":"<<m<<",\"starting_completed_rows\":"<<starting<<",\"completed_rows\":"<<s.processed
            <<",\"primal_vectors\":3,\"producer_sparse_row_residuals_zero\":true,\"rank_claim\":false,\"target_resolution\":false,\"independent_approval\":false,\"native_ru_maxrss\":"<<usage.ru_maxrss<<",\"native_ru_maxrss_unit\":\"LinuxKiB\",\"elapsed_seconds\":"<<std::chrono::duration<double>(Clock::now()-started).count()<<"}\n";
        result.flush();need(static_cast<bool>(result),"complete result");std::cout<<"THREE_PRIMALS_PRESERVED "<<n<<' '<<m<<'\n';return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
