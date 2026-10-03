#include <array>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using Clock=std::chrono::steady_clock;
using Words=std::vector<std::uint64_t>;
static void need(bool value,const std::string &message){if(!value)throw std::runtime_error(message);}
static std::uint64_t number(const std::string &s){
    need(!s.empty() && s.find_first_not_of("0123456789")==std::string::npos,"unsigned decimal option");
    return std::stoull(s);
}
struct Options{
    std::string input,input_sha,out,resume;
    double seconds=0;
    std::uint64_t checkpoint_every=4096,stop_after=std::numeric_limits<std::uint64_t>::max();
};
static Options options(int argc,char **argv){
    Options o;
    for(int i=1;i<argc;++i){std::string k=argv[i];need(i+1<argc,"option value");std::string v=argv[++i];
        if(k=="--input")o.input=v;else if(k=="--input-sha256")o.input_sha=v;else if(k=="--out")o.out=v;
        else if(k=="--resume")o.resume=v;else if(k=="--seconds")o.seconds=std::stod(v);
        else if(k=="--checkpoint-every")o.checkpoint_every=number(v);else if(k=="--stop-after-rows")o.stop_after=number(v);
        else need(false,"unknown option");
    }
    need(!o.input.empty() && !o.out.empty() && o.input_sha.size()==64 && o.input_sha.find_first_not_of("0123456789abcdef")==std::string::npos,"input/output/hash options");
    need(o.seconds>0 && o.seconds<=21600 && o.checkpoint_every>0,"finite command allocation");
    return o;
}
struct State{
    std::uint64_t n,m,words,processed=0;
    std::vector<Words> basis;
    std::vector<unsigned char> rhs,present;
    std::vector<std::uint64_t> origin,order_index,order;
    std::vector<std::vector<std::uint64_t>> dependencies;
    State(std::uint64_t columns,std::uint64_t rows):n(columns),m(rows),words((columns+63)/64),basis(columns),rhs(columns,0),present(columns,0),origin(columns),order_index(columns),dependencies(columns){}
};
static void write_u64(std::ostream &f,std::uint64_t x){f.write(reinterpret_cast<const char *>(&x),sizeof(x));}
static std::uint64_t read_u64(std::istream &f){std::uint64_t x;need(static_cast<bool>(f.read(reinterpret_cast<char *>(&x),sizeof(x))),"checkpoint integer");return x;}
static void checkpoint(const Options &o,const State &s,Clock::time_point started,const std::string &reason){
    const auto tmp=std::filesystem::path(o.out)/"checkpoint.tmp",path=std::filesystem::path(o.out)/"checkpoint.bin";
    std::ofstream f(tmp,std::ios::binary|std::ios::trunc);need(static_cast<bool>(f),"checkpoint open");
    f.write("GF2_PRIMAL_CP_V2\n",17);f.write(o.input_sha.data(),64);
    write_u64(f,s.n);write_u64(f,s.m);write_u64(f,s.words);write_u64(f,s.processed);
    for(std::uint64_t p=0;p<s.n;++p){f.put(static_cast<char>(s.present[p]));if(s.present[p]){f.put(static_cast<char>(s.rhs[p]));
        write_u64(f,s.origin[p]);write_u64(f,s.order_index[p]);write_u64(f,s.dependencies[p].size());
        for(auto d:s.dependencies[p])write_u64(f,d);
        f.write(reinterpret_cast<const char *>(s.basis[p].data()),s.words*sizeof(std::uint64_t));}}
    f.flush();need(static_cast<bool>(f),"complete checkpoint write");f.close();std::filesystem::rename(tmp,path);
    std::ofstream log(std::filesystem::path(o.out)/"progress.jsonl",std::ios::app);
    log<<std::setprecision(17)<<"{\"processed_rows\":"<<s.processed<<",\"total_rows\":"<<s.m<<",\"checkpoint_bytes\":"<<std::filesystem::file_size(path)
       <<",\"elapsed_seconds\":"<<std::chrono::duration<double>(Clock::now()-started).count()<<",\"reason\":\""<<reason<<"\"}\n";
    log.flush();need(static_cast<bool>(log),"checkpoint progress write");
}
static void restore(const Options &o,State &s){
    std::ifstream f(o.resume,std::ios::binary);std::array<char,17> magic{};std::array<char,64> sha{};
    need(static_cast<bool>(f.read(magic.data(),17)) && std::string(magic.data(),17)=="GF2_PRIMAL_CP_V2\n","checkpoint version");
    need(static_cast<bool>(f.read(sha.data(),64)) && std::string(sha.data(),64)==o.input_sha,"checkpoint exact input hash");
    need(read_u64(f)==s.n && read_u64(f)==s.m && read_u64(f)==s.words,"checkpoint dimensions");s.processed=read_u64(f);need(s.processed<=s.m,"checkpoint completed row range");
    for(std::uint64_t p=0;p<s.n;++p){int present=f.get();need(present==0 || present==1,"checkpoint presence");s.present[p]=static_cast<unsigned char>(present);
        if(present){int rhs=f.get();need(rhs>=0 && rhs<=7,"checkpoint rhs mask");s.rhs[p]=static_cast<unsigned char>(rhs);
            s.origin[p]=read_u64(f);s.order_index[p]=read_u64(f);auto count=read_u64(f);
            need(s.origin[p]<s.processed && s.order_index[p]<s.n && count<=s.n,"checkpoint DAG record range");
            for(std::uint64_t k=0;k<count;++k){auto d=read_u64(f);need(d<s.n,"checkpoint DAG reference range");s.dependencies[p].push_back(d);}
            s.basis[p].resize(s.words);
            need(static_cast<bool>(f.read(reinterpret_cast<char *>(s.basis[p].data()),s.words*sizeof(std::uint64_t))),"checkpoint packed basis");
            need((s.basis[p][p/64]>>(p%64)&1)!=0,"checkpoint pivot bit");
            for(std::uint64_t w=0;w<p/64;++w)need(s.basis[p][w]==0,"checkpoint pivot prefix");
            need((s.basis[p][p/64]&((UINT64_C(1)<<(p%64))-1))==0,"checkpoint pivot low prefix");
            if(s.n%64)need((s.basis[p].back()>>(s.n%64))==0,"checkpoint padding bits");
        }
    }
    std::uint64_t count=0;for(auto v:s.present)count+=v;s.order.resize(count,s.n);
    for(std::uint64_t p=0;p<s.n;++p)if(s.present[p]){
        need(s.order_index[p]<count && s.order[s.order_index[p]]==s.n,"checkpoint DAG unique insertion order");s.order[s.order_index[p]]=p;
        for(auto d:s.dependencies[p])need(s.present[d] && s.order_index[d]<s.order_index[p],"checkpoint DAG acyclic earlier reference");
    }
    need(f.get()==std::char_traits<char>::eof(),"checkpoint exact end");
}
static void relation(const Options &o,const State &s,std::uint64_t current,const std::vector<std::uint64_t>&used,std::uint64_t expected){
    std::vector<unsigned char> active(s.n,0),rows(s.m,0);rows[current]=1;for(auto p:used)active[p]^=1;
    for(auto it=s.order.rbegin();it!=s.order.rend();++it){const auto p=*it;if(active[p]){rows[s.origin[p]]^=1;for(auto d:s.dependencies[p])active[d]^=1;}}
    std::ofstream f(std::filesystem::path(o.out)/"xor_original_row_indices.json");f<<"{\"format\":\"NORMALIZED_LITERAL_GF2_ROW_XOR_CANDIDATE_V1\",\"rhs_affine_mask\":"<<expected<<",\"matrix_rows\":"<<s.m<<",\"matrix_columns\":"<<s.n<<",\"original_row_indices\":[";
    bool first=true;for(std::uint64_t i=0;i<s.m;++i)if(rows[i]){if(!first)f<<',';f<<i;first=false;}f<<"],\"independent_approval\":false,\"target_resolution\":false}\n";f.flush();need(static_cast<bool>(f),"complete XOR witness");
    // Producer packed replay of selected normalized sparse rows. Independent
    // verifier must separately divide/check the original integer JSON rows.
    std::ifstream input(o.input);std::string tag;std::uint64_t n,m;input>>tag>>n>>m;Words total(s.words,0);std::uint64_t rhs=0;
    for(std::uint64_t i=0;i<m;++i){std::uint64_t mask,count;need(static_cast<bool>(input>>mask>>count),"XOR producer replay row");if(rows[i])rhs^=mask;
        for(std::uint64_t k=0;k<count;++k){std::uint64_t c;need(static_cast<bool>(input>>c),"XOR producer replay column");if(rows[i])total[c/64]^=UINT64_C(1)<<(c%64);}}
    need(rhs==expected && rhs!=0,"XOR producer expected affine residual");for(auto word:total)need(word==0,"XOR producer zero left side");
}
static std::array<Words,3> back_substitute(const State &s){
    std::array<Words,3>x={Words(s.words,0),Words(s.words,0),Words(s.words,0)};
    for(std::uint64_t p=s.n;p-->0;)if(s.present[p])for(int j=0;j<3;++j){
        int bit=s.rhs[p]>>j&1;
        for(std::uint64_t w=p/64;w<s.words;++w)bit^=__builtin_parityll(s.basis[p][w]&x[j][w]);
        if(bit)x[j][p/64]|=UINT64_C(1)<<(p%64);
    }
    return x;
}
static void vector_file(const Options &o,const Words &x,std::uint64_t n,const std::string &label){
    const auto path=std::filesystem::path(o.out)/("x_"+label+".bits");need(!std::filesystem::exists(path),"immutable primal vector");std::ofstream f(path);
    f<<"GF2_AFFINE_PRIMAL_V1 "<<n<<' '<<label<<'\n';for(std::uint64_t i=0;i<n;++i)f<<(x[i/64]>>(i%64)&1);f<<'\n';f.flush();need(static_cast<bool>(f),"complete primal vector");
}
int main(int argc,char **argv){
    try{
        const auto started=Clock::now();const Options o=options(argc,argv);need(!std::filesystem::exists(o.out),"fresh native output");std::filesystem::create_directories(o.out);
        std::ifstream f(o.input);std::string tag;std::uint64_t n,m;need(static_cast<bool>(f>>tag>>n>>m) && tag=="GF2_AFFINE_SPARSE_V1" && n>0 && n<=100000 && m>0 && m<=1000000,"sparse input header");
        State s(n,m);if(!o.resume.empty())restore(o,s);const std::uint64_t starting=s.processed;
        auto expired=[&](){return std::chrono::duration<double>(Clock::now()-started).count()>=o.seconds;};
        for(std::uint64_t i=0;i<m;++i){
            std::uint64_t mask,count;need(static_cast<bool>(f>>mask>>count) && mask<=7 && count<=n,"sparse rhs/population");Words row(s.words,0);std::uint64_t previous=0;
            for(std::uint64_t k=0;k<count;++k){std::uint64_t c;need(static_cast<bool>(f>>c) && c<n && (k==0 || c>previous),"sparse ordered column range");row[c/64]|=UINT64_C(1)<<(c%64);previous=c;}
            if(i<starting)continue;
            if(expired() || s.processed>=o.stop_after){checkpoint(o,s,started,expired()?"ALLOCATED_NATIVE_BUDGET_REACHED":"DECLARED_PREFIX_CONTROL_STOP");std::cout<<"PRIMAL_INCOMPLETE_CHECKPOINT "<<s.processed<<'\n';return 4;}
            std::uint64_t first=0,operations=0;bool inserted=false;std::vector<std::uint64_t> used;
            while(first<s.words){
                while(first<s.words && row[first]==0)++first;if(first==s.words)break;
                const std::uint64_t pivot=first*64+__builtin_ctzll(row[first]);
                if(!s.present[pivot]){s.present[pivot]=1;s.rhs[pivot]=static_cast<unsigned char>(mask);s.basis[pivot]=std::move(row);
                    s.origin[pivot]=i;s.order_index[pivot]=s.order.size();s.order.push_back(pivot);s.dependencies[pivot]=std::move(used);inserted=true;break;}
                for(std::uint64_t w=first;w<s.words;++w)row[w]^=s.basis[pivot][w];mask^=s.rhs[pivot];
                used.push_back(pivot);
                if((++operations&1023)==0 && expired()){checkpoint(o,s,started,"ALLOCATED_NATIVE_BUDGET_REACHED");std::cout<<"PRIMAL_INCOMPLETE_CHECKPOINT "<<s.processed<<'\n';return 4;}
            }
            if(!inserted && mask){checkpoint(o,s,started,"INCONSISTENT_FIXED_INPUT");relation(o,s,i,used,mask);std::cout<<"INCONSISTENT_FIXED_INPUT "<<i<<' '<<mask<<'\n';return 3;}
            s.processed=i+1;
            if(s.processed%o.checkpoint_every==0)checkpoint(o,s,started,"COMPLETED_ROW_PREFIX");
        }
        need(!(f>>tag),"sparse exact end");checkpoint(o,s,started,"COMPLETE_ELIMINATION_BACKSUB_PENDING");
        const auto x=back_substitute(s);
        for(int j=0;j<3;++j)vector_file(o,x[j],n,std::array<std::string,3>{"const","a","b"}[j]);
        // Producer check uses the separate sparse input, not the raw JSON model.
        f.close();f.open(o.input);f>>tag>>n>>m;std::ofstream residual(std::filesystem::path(o.out)/"row_residuals.bin",std::ios::binary);
        for(std::uint64_t i=0;i<m;++i){std::uint64_t mask,count;need(static_cast<bool>(f>>mask>>count),"producer replay row");
            for(std::uint64_t k=0;k<count;++k){std::uint64_t c;need(static_cast<bool>(f>>c),"producer replay column");for(int j=0;j<3;++j)mask^=(x[j][c/64]>>(c%64)&1)<<j;}
            need(mask==0,"producer exact primal row residual");residual.put(static_cast<char>(mask));
        }
        residual.flush();need(static_cast<bool>(residual),"complete residual file");
        std::ofstream result(std::filesystem::path(o.out)/"result.json");result<<std::setprecision(17)<<"{\"status\":\"CANDIDATE_THREE_LITERAL_GF2_PRIMALS\",\"columns\":"<<n<<",\"rows\":"<<m
            <<",\"starting_completed_rows\":"<<starting<<",\"completed_rows\":"<<s.processed<<",\"primal_vectors\":3,\"producer_sparse_row_residuals_zero\":true,\"rank_claim\":false,\"target_resolution\":false,\"independent_approval\":false,\"elapsed_seconds\":"<<std::chrono::duration<double>(Clock::now()-started).count()<<"}\n";
        result.flush();need(static_cast<bool>(result),"complete result");std::cout<<"THREE_PRIMALS_PRESERVED "<<n<<' '<<m<<'\n';return 0;
    }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 2;}
}
