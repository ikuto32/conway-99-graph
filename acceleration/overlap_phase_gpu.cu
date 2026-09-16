// Numerical frozen-X phase-I merits only; no infeasibility or completion claims.
// C99GLOBAL1 n, 1680 doubles X in lexicographic disjoint-pair order,
// then n complete overlap assignments of 168 canonical endpoint pairs each.
#include <cuda_runtime.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
constexpr int N=84,Q=840,P=3486,T=256;
struct Bits { unsigned long long low=0,high=0; };
__constant__ unsigned char qu[Q],qs[Q],pu[P],pv[P],shared_labels[P],labels[168];
void check(cudaError_t e,const char* op) { if(e!=cudaSuccess)throw std::runtime_error(std::string(op)+": "+cudaGetErrorString(e)); }
#define CUDA(x) check((x),#x)
template<class V> struct Device { V* p=nullptr;explicit Device(size_t n){if(n)CUDA(cudaMalloc(&p,n*sizeof(V)));}~Device(){if(p)cudaFree(p);} };
template<class V> V number(std::istream& in,const char* name){V x;if(!(in>>x))throw std::runtime_error(std::string("Missing/invalid ")+name);return x;}
void put(Bits& row,int v){if(v<64)row.low|=1ULL<<v;else row.high|=1ULL<<(v-64);}
bool has(const Bits& row,int v){return v<64?(row.low>>v)&1ULL:(row.high>>(v-64))&1ULL;}
int pop(unsigned long long bits){int n=0;while(bits){bits&=bits-1;++n;}return n;}
__global__ void merits(const unsigned char* neighbors,const Bits* bits,const double* x,
                       const double* xquota,double* summaries,double* residuals){
    const int candidate=blockIdx.x;
    const unsigned char* row=neighbors+size_t(candidate)*N*4;
    const Bits* known=bits+size_t(candidate)*N;
    double quota_sum=0,pair_sum=0,quota_max=0,pair_max=0;
    for(int i=threadIdx.x;i<Q;i+=T){
        const int u=qu[i],symbol=qs[i];
        int count=0;
        #pragma unroll
        for(int k=0;k<4;++k){const int v=row[u*4+k];count+=(labels[v*2]==symbol)+(labels[v*2+1]==symbol);}
        const double value=xquota[i]+count-2;
        quota_sum+=fabs(value);quota_max=fmax(quota_max,fabs(value));
        if(residuals)residuals[size_t(candidate)*(Q+P)+i]=value;
    }
    for(int i=threadIdx.x;i<P;i+=T){
        const int u=pu[i],v=pv[i];
        const Bits a=known[u],b=known[v];
        const int common=__popcll(a.low&b.low)+__popcll(a.high&b.high);
        const int adjacent=v<64?(a.low>>v)&1ULL:(a.high>>(v-64))&1ULL;
        double value=shared_labels[i]+common+adjacent-2+x[u*N+v];
        #pragma unroll
        for(int k=0;k<4;++k)value+=x[v*N+row[u*4+k]]+x[u*N+row[v*4+k]];
        const double positive=fmax(0.0,value);pair_sum+=positive;pair_max=fmax(pair_max,positive);
        if(residuals)residuals[size_t(candidate)*(Q+P)+Q+i]=value;
    }
    __shared__ double sums[4][T];
    sums[0][threadIdx.x]=quota_sum;sums[1][threadIdx.x]=pair_sum;
    sums[2][threadIdx.x]=quota_max;sums[3][threadIdx.x]=pair_max;
    __syncthreads();
    for(int stride=T/2;stride;stride/=2){
        if(threadIdx.x<stride){
            sums[0][threadIdx.x]+=sums[0][threadIdx.x+stride];sums[1][threadIdx.x]+=sums[1][threadIdx.x+stride];
            sums[2][threadIdx.x]=fmax(sums[2][threadIdx.x],sums[2][threadIdx.x+stride]);
            sums[3][threadIdx.x]=fmax(sums[3][threadIdx.x],sums[3][threadIdx.x+stride]);
        }__syncthreads();
    }
    if(threadIdx.x==0)for(int j=0;j<4;++j)summaries[size_t(candidate)*4+j]=sums[j][0];
}
int main(int argc,char** argv){try{
    if(argc<3||argc>4||(argc==4&&std::string(argv[3])!="--residuals"))throw std::runtime_error("Usage: overlap_phase_gpu INPUT.txt OUTPUT.json [--residuals]");
    if(std::ifstream(argv[2]).good())throw std::runtime_error("Output already exists");
    const auto start=std::chrono::steady_clock::now();
    std::array<unsigned char,168> lab{};std::array<unsigned char,N> supports{};int index=0;
    for(int a=0;a<7;++a)for(int b=a+1;b<7;++b)for(int s=0;s<2;++s)for(int t=0;t<2;++t){lab[index*2]=2*a+s;lab[index*2+1]=2*b+t;supports[index++]=(1<<a)|(1<<b);}
    std::array<unsigned char,Q> quota_u{},quota_s{};std::array<unsigned char,P> pair_u{},pair_v{},intersections{};
    int nq=0,np=0;for(int u=0;u<N;++u){for(int s=0;s<14;++s)if(!(supports[u]&(1<<(s/2)))){quota_u[nq]=u;quota_s[nq++]=s;}
        for(int v=u+1;v<N;++v){pair_u[np]=u;pair_v[np]=v;int count=0;for(int a=0;a<2;++a)for(int b=0;b<2;++b)count+=lab[u*2+a]==lab[v*2+b];intersections[np++]=count;}}
    if(nq!=Q||np!=P)throw std::runtime_error("Internal geometry mismatch");
    std::ifstream input(argv[1]);std::string magic;input>>magic;if(magic!="C99GLOBAL1")throw std::runtime_error("Wrong input header");
    const int count=number<int>(input,"candidate count");if(count<1||count>100000)throw std::runtime_error("Invalid candidate count");
    std::vector<double> x(N*N,0.0);int nx=0;
    for(int u=0;u<N;++u)for(int v=u+1;v<N;++v)if(!(supports[u]&supports[v])){
        double value=number<double>(input,"X value");if(!std::isfinite(value)||value<0||value>1)throw std::runtime_error("X must be finite and in [0,1]");x[u*N+v]=x[v*N+u]=value;++nx;}
    if(nx!=1680)throw std::runtime_error("Internal X dimension");
    std::vector<double> xquota(Q,0.0);for(int i=0;i<Q;++i)for(int v=0;v<N;++v)if(lab[v*2]==quota_s[i]||lab[v*2+1]==quota_s[i])xquota[i]+=x[quota_u[i]*N+v];
    std::vector<unsigned char> neighbors(size_t(count)*N*4);std::vector<Bits> known(size_t(count)*N);
    for(int c=0;c<count;++c){
        std::array<int,N> degrees{};std::array<Bits,99> full{};
        auto add=[&](int u,int v){put(full[u],v);put(full[v],u);};
        for(int s=1;s<15;++s)add(0,s);for(int s=1;s<15;s+=2)add(s,s+1);
        for(int u=0;u<N;++u){add(u+15,lab[u*2]+1);add(u+15,lab[u*2+1]+1);}
        for(int e=0;e<168;++e){
            const int u=number<int>(input,"edge endpoint"),v=number<int>(input,"edge endpoint");
            if(u<0||u>=v||v>=N||pop(supports[u]&supports[v])!=1||has(known[size_t(c)*N+u],v))throw std::runtime_error("Invalid/duplicate overlap edge");
            if(degrees[u]>=4||degrees[v]>=4)throw std::runtime_error("Overlap degree exceeds four");
            neighbors[size_t(c)*N*4+u*4+degrees[u]++]=v;neighbors[size_t(c)*N*4+v*4+degrees[v]++]=u;
            put(known[size_t(c)*N+u],v);put(known[size_t(c)*N+v],u);add(u+15,v+15);
        }
        for(int d:degrees)if(d!=4)throw std::runtime_error("Overlap degrees must equal four");
        for(int u=0;u<99;++u)for(int v=u+1;v<99;++v)if(pop(full[u].low&full[v].low)+pop(full[u].high&full[v].high)>2-int(has(full[u],v)))throw std::runtime_error("Partial full99 pair cap violated");
    }
    std::string extra;if(input>>extra)throw std::runtime_error("Trailing input");
    CUDA(cudaSetDevice(0));cudaDeviceProp device{};CUDA(cudaGetDeviceProperties(&device,0));
    Device<unsigned char>d_neighbors(neighbors.size());Device<Bits>d_known(known.size());Device<double>d_x(x.size()),d_quota(Q),d_summaries(size_t(count)*4),d_residuals(argc==4?size_t(count)*(Q+P):0);
    std::vector<double> summaries(size_t(count)*4),residuals(argc==4?size_t(count)*(Q+P):0);
    cudaEvent_t begin,end;CUDA(cudaEventCreate(&begin));CUDA(cudaEventCreate(&end));const auto timed=std::chrono::steady_clock::now();
    CUDA(cudaMemcpyToSymbol(qu,quota_u.data(),Q));CUDA(cudaMemcpyToSymbol(qs,quota_s.data(),Q));CUDA(cudaMemcpyToSymbol(pu,pair_u.data(),P));CUDA(cudaMemcpyToSymbol(pv,pair_v.data(),P));CUDA(cudaMemcpyToSymbol(shared_labels,intersections.data(),P));CUDA(cudaMemcpyToSymbol(labels,lab.data(),168));
    CUDA(cudaMemcpy(d_neighbors.p,neighbors.data(),neighbors.size(),cudaMemcpyHostToDevice));CUDA(cudaMemcpy(d_known.p,known.data(),known.size()*sizeof(Bits),cudaMemcpyHostToDevice));CUDA(cudaMemcpy(d_x.p,x.data(),x.size()*sizeof(double),cudaMemcpyHostToDevice));CUDA(cudaMemcpy(d_quota.p,xquota.data(),Q*sizeof(double),cudaMemcpyHostToDevice));
    CUDA(cudaEventRecord(begin));merits<<<count,T>>>(d_neighbors.p,d_known.p,d_x.p,d_quota.p,d_summaries.p,d_residuals.p);CUDA(cudaGetLastError());CUDA(cudaEventRecord(end));CUDA(cudaEventSynchronize(end));
    float ms=0;CUDA(cudaEventElapsedTime(&ms,begin,end));CUDA(cudaMemcpy(summaries.data(),d_summaries.p,summaries.size()*sizeof(double),cudaMemcpyDeviceToHost));if(argc==4)CUDA(cudaMemcpy(residuals.data(),d_residuals.p,residuals.size()*sizeof(double),cudaMemcpyDeviceToHost));
    double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-timed).count();CUDA(cudaEventDestroy(begin));CUDA(cudaEventDestroy(end));
    std::ofstream out(argv[2]);if(!out)throw std::runtime_error("Could not open output");
    out<<std::setprecision(17)<<"{\"status\":\"NUMERICAL_FIXED_X_PHASE1_HEURISTIC\",\"device\":\""<<device.name<<"\",\"candidate_count\":"<<count<<",\"quota_rows\":840,\"pair_rows\":3486,\"elapsed_seconds\":"<<elapsed<<",\"kernel_seconds\":"<<ms/1000.0<<",\"results\":[";
    for(int c=0;c<count;++c){if(c)out<<',';const double* score=summaries.data()+c*4;
        out<<"{\"candidate_index\":"<<c<<",\"total_violation\":"<<score[0]+score[1]<<",\"quota_violation\":"<<score[0]<<",\"pair_violation\":"<<score[1]<<",\"quota_max_abs\":"<<score[2]<<",\"pair_max_positive\":"<<score[3];
        if(argc==4){out<<",\"quota_residuals\":[";for(int i=0;i<Q;++i){if(i)out<<',';out<<residuals[size_t(c)*(Q+P)+i];}out<<"],\"pair_residuals\":[";for(int i=0;i<P;++i){if(i)out<<',';out<<residuals[size_t(c)*(Q+P)+Q+i];}out<<']';}out<<'}';}
    out<<"],\"scope\":\"Double-precision fixed-X ranking merit only. Sum absolute840quota residuals plus positive3486linear pair-cap residuals; unknown-unknown products dropped. No exclusion, LP optimum or completion claim.\"}\n";if(!out)throw std::runtime_error("Output write failed");
    std::cout<<"CUDA phase-I "<<count<<" candidates: "<<elapsed<<" s transfer+kernel, "<<ms/1000.0<<" s kernel, "<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<" s total\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
