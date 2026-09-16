// Layout-only derivative: readonly global geometry and slot-major quota gathers.
// Float64 Chambolle-Pock phase-I ranking. Numerical diagnostics only, no proof.
// C99CP1 count checkpoint_count; checkpoints;1680X;4326Y;count*168(u,v).
#include <cuda_runtime.h>
#include <algorithm>
#include <array>
#include <charconv>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int V=84,N=1680,Q=840,P=3486,M=Q+P,T=256,TILE=256;
constexpr double STEP=.09;
constexpr size_t SHARED_BYTES=size_t(2*N+M)*sizeof(double)+V*4+M;
struct Geometry {
    const short *x_index,*quota_index,*pair_index,*quota_columns;
    const unsigned char *x_u,*x_v,*pair_u,*pair_v,*vertex_labels;
};
// Only the nine uniform pointers use constant memory. Table contents are global.
__constant__ Geometry geometry;

void check(cudaError_t code,const char* operation){
    if(code!=cudaSuccess)throw std::runtime_error(std::string(operation)+": "+cudaGetErrorString(code));
}
#define CUDA(call) check((call),#call)
template<class U>struct Device{
    U* p=nullptr;
    explicit Device(size_t count){if(count)CUDA(cudaMalloc(&p,count*sizeof(U)));}
    ~Device(){if(p)cudaFree(p);}
    Device(const Device&)=delete;
    Device& operator=(const Device&)=delete;
};
std::string token(std::istream& input,const char* what){
    std::string value;
    if(!(input>>value))throw std::runtime_error(std::string("Missing ")+what);
    return value;
}
int integer(std::istream& input,const char* what){
    const std::string value=token(input,what);
    int number=0;
    const auto parsed=std::from_chars(value.data(),value.data()+value.size(),number);
    if(parsed.ec!=std::errc()||parsed.ptr!=value.data()+value.size())throw std::runtime_error(std::string("Invalid integer ")+what);
    return number;
}
double real(std::istream& input,const char* what){
    const std::string value=token(input,what);
    size_t consumed=0;
    double number=std::stod(value,&consumed);
    if(consumed!=value.size()||!std::isfinite(number))throw std::runtime_error(std::string("Nonfinite/invalid ")+what);
    return number;
}
struct Bits{unsigned long long low=0,high=0;};
void setbit(Bits& row,int vertex){if(vertex<64)row.low|=1ULL<<vertex;else row.high|=1ULL<<(vertex-64);}
bool hasbit(const Bits& row,int vertex){return vertex<64?(row.low>>vertex)&1ULL:(row.high>>(vertex-64))&1ULL;}
int pop(unsigned long long bits){int result=0;while(bits){bits&=bits-1;++result;}return result;}
int common(const Bits& a,const Bits& b){return pop(a.low&b.low)+pop(a.high&b.high);}

__device__ __forceinline__ double read_x(const double* x,int u,int v){
    const int i=__ldg(geometry.x_index+u*V+v);return i<0?0.0:x[i];
}
__device__ __forceinline__ double forward_row(int row,const double* x,const unsigned char* neighbors){
    double value=0;
    if(row<Q){
        #pragma unroll
        for(int k=0;k<8;++k)value+=x[__ldg(geometry.quota_columns+k*Q+row)];
    }else{
        const int p=row-Q,u=__ldg(geometry.pair_u+p),v=__ldg(geometry.pair_v+p);
        value=read_x(x,u,v);
        #pragma unroll
        for(int k=0;k<4;++k){
            value+=read_x(x,v,neighbors[u*4+k]);
            value+=read_x(x,u,neighbors[v*4+k]);
        }
    }
    return value;
}
__device__ __forceinline__ double transpose_column(int column,const double* y,const unsigned char* neighbors){
    const int u=__ldg(geometry.x_u+column),v=__ldg(geometry.x_v+column);
    double value=y[__ldg(geometry.quota_index+u*14+__ldg(geometry.vertex_labels+v*2))];
    value+=y[__ldg(geometry.quota_index+u*14+__ldg(geometry.vertex_labels+v*2+1))];
    value+=y[__ldg(geometry.quota_index+v*14+__ldg(geometry.vertex_labels+u*2))];
    value+=y[__ldg(geometry.quota_index+v*14+__ldg(geometry.vertex_labels+u*2+1))];
    value+=y[Q+__ldg(geometry.pair_index+u*V+v)];
    #pragma unroll
    for(int k=0;k<4;++k){
        value+=y[Q+__ldg(geometry.pair_index+v*V+neighbors[u*4+k])];
        value+=y[Q+__ldg(geometry.pair_index+u*V+neighbors[v*4+k])];
    }
    return value;
}
// All threads call this collective. The two answers remain in scratch[0,T].
__device__ void objectives(const double* x,const double* y,const unsigned char* neighbors,
                           const unsigned char* rhs,double* scratch){
    double primal=0,dual=0;
    for(int row=threadIdx.x;row<M;row+=T){
        const double residual=forward_row(row,x,neighbors)-rhs[row];
        primal+=row<Q?fabs(residual):fmax(0.0,residual);
        dual-=rhs[row]*y[row];
    }
    for(int j=threadIdx.x;j<N;j+=T)dual+=fmin(0.0,transpose_column(j,y,neighbors));
    scratch[threadIdx.x]=primal;scratch[T+threadIdx.x]=dual;
    __syncthreads();
    for(int stride=T/2;stride;stride/=2){
        if(threadIdx.x<stride){scratch[threadIdx.x]+=scratch[threadIdx.x+stride];scratch[T+threadIdx.x]+=scratch[T+threadIdx.x+stride];}
        __syncthreads();
    }
}
__global__ void cp_kernel(int first,const unsigned char* all_neighbors,const unsigned char* all_rhs,
                          const double* initial_x,const double* initial_y,const int* checkpoints,int ncheck,
                          double* averages,double* initials,double* statistics,double* vectors){
    const int candidate=first+blockIdx.x;
    extern __shared__ double storage[];
    double* x=storage;
    double* xbar=x+N;
    double* y=xbar+N;
    unsigned char* neighbors=reinterpret_cast<unsigned char*>(y+M);
    unsigned char* rhs=neighbors+V*4;
    __shared__ double reduction[2*T];
    double* average_x=averages+size_t(candidate)*(N+M);
    double* average_y=average_x+N;
    for(int i=threadIdx.x;i<N;i+=T){x[i]=xbar[i]=initial_x[i];average_x[i]=0;}
    for(int i=threadIdx.x;i<M;i+=T){y[i]=initial_y[i];average_y[i]=0;rhs[i]=all_rhs[size_t(candidate)*M+i];}
    for(int i=threadIdx.x;i<V*4;i+=T)neighbors[i]=all_neighbors[size_t(candidate)*V*4+i];
    __syncthreads();
    objectives(x,y,neighbors,rhs,reduction);
    double best_upper=0,best_lower=0;
    if(threadIdx.x==0){
        best_upper=reduction[0];best_lower=reduction[T];
        initials[size_t(candidate)*2]=best_upper;initials[size_t(candidate)*2+1]=best_lower;
    }
    __syncthreads();
    int checkpoint=0;
    for(int iteration=1;iteration<=checkpoints[ncheck-1];++iteration){
        for(int i=threadIdx.x;i<M;i+=T){
            const double value=y[i]+STEP*(forward_row(i,xbar,neighbors)-rhs[i]);
            const double next=fmin(1.0,fmax(i<Q?-1.0:0.0,value));
            y[i]=next;
            average_y[i]+=(next-average_y[i])/double(iteration);
        }
        __syncthreads();
        for(int j=threadIdx.x;j<N;j+=T){
            const double old=x[j];
            const double next=fmin(1.0,fmax(0.0,old-STEP*transpose_column(j,y,neighbors)));
            x[j]=next;xbar[j]=2.0*next-old;
            average_x[j]+=(next-average_x[j])/double(iteration);
        }
        __syncthreads();
        if(iteration==checkpoints[checkpoint]){
            const size_t index=(size_t(candidate)*ncheck+checkpoint)*6;
            objectives(x,y,neighbors,rhs,reduction);
            if(threadIdx.x==0){
                statistics[index]=reduction[0];statistics[index+1]=reduction[T];
                best_upper=fmin(best_upper,reduction[0]);best_lower=fmax(best_lower,reduction[T]);
            }
            __syncthreads();
            objectives(average_x,average_y,neighbors,rhs,reduction);
            if(threadIdx.x==0){
                statistics[index+2]=reduction[0];statistics[index+3]=reduction[T];
                best_upper=fmin(best_upper,reduction[0]);best_lower=fmax(best_lower,reduction[T]);
                statistics[index+4]=best_upper;statistics[index+5]=best_lower;
            }
            if(vectors){
                double* destination=vectors+(size_t(candidate)*ncheck+checkpoint)*2*(N+M);
                for(int j=threadIdx.x;j<N;j+=T){destination[j]=x[j];destination[N+M+j]=average_x[j];}
                for(int i=threadIdx.x;i<M;i+=T){destination[N+i]=y[i];destination[2*N+M+i]=average_y[i];}
            }
            __syncthreads();
            ++checkpoint;
        }
    }
}

int main(int argc,char** argv){try{
    if(argc<3||argc>4||(argc==4&&std::string(argv[3])!="--vectors"))throw std::runtime_error("Usage: overlap_cp_gpu INPUT OUTPUT [--vectors]");
    if(std::ifstream(argv[2]).good())throw std::runtime_error("Output already exists");
    const bool save_vectors=argc==4;
    const auto start=std::chrono::steady_clock::now();
    std::ifstream input(argv[1]);
    if(token(input,"magic")!="C99CP1")throw std::runtime_error("Wrong input header");
    const int count=integer(input,"candidate count"),ncheck=integer(input,"checkpoint count");
    if(count<1||count>100000||ncheck<1||ncheck>32)throw std::runtime_error("Invalid candidate/checkpoint count");
    if(save_vectors&&count>64)throw std::runtime_error("--vectors requires candidate count <=64");
    std::vector<int> checkpoints(ncheck);
    for(int i=0;i<ncheck;++i){checkpoints[i]=integer(input,"checkpoint");if(checkpoints[i]<1||checkpoints[i]>1000000||(i&&checkpoints[i]<=checkpoints[i-1]))throw std::runtime_error("Checkpoints must be strictly ascending in1..1000000");}
    std::vector<double> initial_x(N),initial_y(M);
    for(double& value:initial_x){value=real(input,"initial X");if(value<0||value>1)throw std::runtime_error("X outside[0,1]");}
    for(int i=0;i<M;++i){initial_y[i]=real(input,"initial Y");if(initial_y[i]<(i<Q?-1.0:0.0)||initial_y[i]>1)throw std::runtime_error("Y outside semantic dual box");}
    std::array<unsigned char,V*2> labels{};
    std::array<unsigned char,V> support{};
    int vertex=0;
    for(int a=0;a<7;++a)for(int b=a+1;b<7;++b)for(int s=0;s<2;++s)for(int t=0;t<2;++t){labels[2*vertex]=2*a+s;labels[2*vertex+1]=2*b+t;support[vertex++]=(1<<a)|(1<<b);}
    std::array<short,V*V> xi{},pi{};xi.fill(-1);pi.fill(-1);
    std::array<short,V*14> qi{};qi.fill(-1);
    std::array<short,Q*8> qcols{};
    std::array<unsigned char,N> xu{},xv{};
    std::array<unsigned char,P> pu{},pv{};
    std::array<unsigned char,Q> qu{},qs{};
    int nx=0,np=0,nq=0;
    for(int u=0;u<V;++u){
        for(int s=0;s<14;++s)if(!(support[u]&(1<<(s/2)))){qi[u*14+s]=nq;qu[nq]=u;qs[nq++]=s;}
        for(int v=u+1;v<V;++v){pi[u*V+v]=pi[v*V+u]=np;pu[np]=u;pv[np++]=v;if(!(support[u]&support[v])){xi[u*V+v]=xi[v*V+u]=nx;xu[nx]=u;xv[nx++]=v;}}
    }
    if(nx!=N||np!=P||nq!=Q)throw std::runtime_error("Internal coordinate dimensions differ");
    for(int i=0;i<Q;++i){
        int terms=0;
        for(int v=0;v<V;++v)if((labels[2*v]==qs[i]||labels[2*v+1]==qs[i])&&xi[qu[i]*V+v]>=0){if(terms>=8)throw std::runtime_error("Quota row too long");qcols[i*8+terms++]=xi[qu[i]*V+v];}
        if(terms!=8)throw std::runtime_error("Quota row has not eight unknowns");
        std::sort(qcols.begin()+i*8,qcols.begin()+i*8+8);
    }
    std::array<short,Q*8> qcols_slot_major{};
    for(int row=0;row<Q;++row)for(int slot=0;slot<8;++slot)qcols_slot_major[slot*Q+row]=qcols[row*8+slot];
    std::vector<unsigned char> neighbors(size_t(count)*V*4),rhs(size_t(count)*M);
    for(int candidate=0;candidate<count;++candidate){
        std::array<Bits,99> full{};
        std::array<int,V> degrees{};
        auto add=[&](int u,int v){setbit(full[u],v);setbit(full[v],u);};
        for(int s=1;s<15;++s)add(0,s);
        for(int s=1;s<15;s+=2)add(s,s+1);
        for(int u=0;u<V;++u){add(u+15,labels[u*2]+1);add(u+15,labels[u*2+1]+1);}
        for(int edge=0;edge<168;++edge){
            const int u=integer(input,"edge endpoint"),v=integer(input,"edge endpoint");
            if(u<0||u>=v||v>=V||pop(support[u]&support[v])!=1||hasbit(full[u+15],v+15))throw std::runtime_error("Invalid/duplicate overlap edge");
            if(degrees[u]>=4||degrees[v]>=4)throw std::runtime_error("Overlap degree exceeds4");
            neighbors[size_t(candidate)*V*4+u*4+degrees[u]++]=v;
            neighbors[size_t(candidate)*V*4+v*4+degrees[v]++]=u;
            add(u+15,v+15);
        }
        for(int u=0;u<V;++u){
            if(degrees[u]!=4)throw std::runtime_error("Overlap degree is not4");
            auto first=neighbors.begin()+size_t(candidate)*V*4+u*4;std::sort(first,first+4);
            for(int s=0;s<14;++s)if(support[u]&(1<<(s/2))){
                if(common(full[u+15],full[s+1])!=2-int(hasbit(full[u+15],s+1)))throw std::runtime_error("Exact own-label quota violated");
            }
        }
        for(int u=0;u<99;++u){
            if(pop(full[u].low)+pop(full[u].high)!=(u<15?14:6))throw std::runtime_error("Full99 partial degree mismatch");
            for(int v=u+1;v<99;++v)if(common(full[u],full[v])>2-int(hasbit(full[u],v)))throw std::runtime_error("Full99 partial common-neighbor cap violated");
        }
        for(int i=0;i<Q;++i){const int target=2-common(full[qu[i]+15],full[qs[i]+1]);if(target<0||target>2)throw std::runtime_error("Invalid quota target");rhs[size_t(candidate)*M+i]=target;}
        for(int i=0;i<P;++i){const int u=pu[i]+15,v=pv[i]+15;const int target=2-common(full[u],full[v])-int(hasbit(full[u],v));if(target<0||target>2)throw std::runtime_error("Invalid cap target");rhs[size_t(candidate)*M+Q+i]=target;}
    }
    std::string extra;if(input>>extra)throw std::runtime_error("Trailing input token");
    CUDA(cudaSetDevice(0));cudaDeviceProp device{};CUDA(cudaGetDeviceProperties(&device,0));
    if(SHARED_BYTES+2*T*sizeof(double)>size_t(device.sharedMemPerBlockOptin))throw std::runtime_error("GPU opt-in shared memory too small");
    CUDA(cudaFuncSetAttribute(cp_kernel,cudaFuncAttributeMaxDynamicSharedMemorySize,int(SHARED_BYTES)));
    CUDA(cudaFuncSetAttribute(cp_kernel,cudaFuncAttributePreferredSharedMemoryCarveout,100));
    Device<unsigned char> d_neighbors(neighbors.size()),d_rhs(rhs.size());
    Device<double> d_x(N),d_y(M),d_average(size_t(count)*(N+M)),d_initials(size_t(count)*2),d_stats(size_t(count)*ncheck*6),
                   d_vectors(save_vectors?size_t(count)*ncheck*2*(N+M):0);
    Device<int> d_checkpoints(ncheck);
    Device<short> d_x_index(xi.size()),d_quota_index(qi.size()),d_pair_index(pi.size()),d_quota_columns(qcols.size());
    Device<unsigned char> d_x_u(N),d_x_v(N),d_pair_u(P),d_pair_v(P),d_vertex_labels(labels.size());
    const Geometry host_geometry{d_x_index.p,d_quota_index.p,d_pair_index.p,d_quota_columns.p,
                                 d_x_u.p,d_x_v.p,d_pair_u.p,d_pair_v.p,d_vertex_labels.p};
    std::vector<double> initials(size_t(count)*2),statistics(size_t(count)*ncheck*6),vectors(save_vectors?size_t(count)*ncheck*2*(N+M):0);
    cudaEvent_t begin,end;CUDA(cudaEventCreate(&begin));CUDA(cudaEventCreate(&end));
    const auto timed=std::chrono::steady_clock::now();
    CUDA(cudaMemcpy(d_x_index.p,xi.data(),xi.size()*sizeof(short),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_quota_index.p,qi.data(),qi.size()*sizeof(short),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_pair_index.p,pi.data(),pi.size()*sizeof(short),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_quota_columns.p,qcols_slot_major.data(),qcols_slot_major.size()*sizeof(short),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_x_u.p,xu.data(),N,cudaMemcpyHostToDevice));CUDA(cudaMemcpy(d_x_v.p,xv.data(),N,cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_pair_u.p,pu.data(),P,cudaMemcpyHostToDevice));CUDA(cudaMemcpy(d_pair_v.p,pv.data(),P,cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_vertex_labels.p,labels.data(),labels.size(),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpyToSymbol(geometry,&host_geometry,sizeof(Geometry)));
    CUDA(cudaMemcpy(d_x.p,initial_x.data(),N*sizeof(double),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_y.p,initial_y.data(),M*sizeof(double),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_neighbors.p,neighbors.data(),neighbors.size(),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_rhs.p,rhs.data(),rhs.size(),cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(d_checkpoints.p,checkpoints.data(),ncheck*sizeof(int),cudaMemcpyHostToDevice));
    CUDA(cudaEventRecord(begin));
    int launches=0;
    for(int first=0;first<count;first+=TILE){
        cp_kernel<<<std::min(TILE,count-first),T,SHARED_BYTES>>>(first,d_neighbors.p,d_rhs.p,d_x.p,d_y.p,d_checkpoints.p,ncheck,d_average.p,d_initials.p,d_stats.p,d_vectors.p);
        CUDA(cudaGetLastError());++launches;
    }
    CUDA(cudaEventRecord(end));CUDA(cudaEventSynchronize(end));
    float milliseconds=0;CUDA(cudaEventElapsedTime(&milliseconds,begin,end));
    CUDA(cudaMemcpy(initials.data(),d_initials.p,initials.size()*sizeof(double),cudaMemcpyDeviceToHost));
    CUDA(cudaMemcpy(statistics.data(),d_stats.p,statistics.size()*sizeof(double),cudaMemcpyDeviceToHost));
    if(save_vectors)CUDA(cudaMemcpy(vectors.data(),d_vectors.p,vectors.size()*sizeof(double),cudaMemcpyDeviceToHost));
    const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-timed).count();
    CUDA(cudaEventDestroy(begin));CUDA(cudaEventDestroy(end));
    for(double value:initials)if(!std::isfinite(value))throw std::runtime_error("Nonfinite initial objective");
    for(double value:statistics)if(!std::isfinite(value))throw std::runtime_error("Nonfinite CP objective");
    for(double value:vectors)if(!std::isfinite(value))throw std::runtime_error("Nonfinite CP vector");
    std::ofstream out(argv[2]);if(!out)throw std::runtime_error("Could not open output");
    out<<std::setprecision(17);
    out<<"{\"status\":\"NUMERICAL_CHAMBOLLE_POCK_PHASE1_HEURISTIC\",\"candidate_count\":"<<count
       <<",\"device\":\""<<device.name<<"\",\"precision\":\"float64\",\"tau\":0.09,\"sigma\":0.09,\"theta\":1,\"checkpoints\":[";
    for(int i=0;i<ncheck;++i){if(i)out<<',';out<<checkpoints[i];}
    out<<"],\"elapsed_seconds\":"<<elapsed<<",\"kernel_seconds\":"<<milliseconds/1000.0
       <<",\"launch_candidate_batch_limit\":"<<TILE<<",\"kernel_launches\":"<<launches
       <<",\"dynamic_shared_bytes_per_block\":"<<SHARED_BYTES<<",\"static_reduction_shared_bytes_per_block\":"<<2*T*sizeof(double)
       <<",\"full99_partial_caps_and_degrees_validated\":true,\"own_label_equalities_validated_per_candidate\":336"
       <<",\"best_scope\":\"initial plus requested checkpoints, each last and average; not every iteration\",\"results\":[";
    auto bounds=[&](double primal,double dual){out<<"{\"primal_upper\":"<<primal<<",\"dual_lower\":"<<dual<<'}';};
    auto vector_json=[&](const char* name,const double* values,int length){out<<",\""<<name<<"\":[";for(int j=0;j<length;++j){if(j)out<<',';out<<values[j];}out<<']';};
    for(int c=0;c<count;++c){
        if(c)out<<',';out<<"{\"candidate_index\":"<<c<<",\"initial\":";bounds(initials[size_t(c)*2],initials[size_t(c)*2+1]);out<<",\"checkpoints\":[";
        for(int k=0;k<ncheck;++k){
            if(k)out<<',';const double* s=statistics.data()+(size_t(c)*ncheck+k)*6;
            out<<"{\"iterations\":"<<checkpoints[k]<<",\"last\":";bounds(s[0],s[1]);out<<",\"average\":";bounds(s[2],s[3]);
            out<<",\"best_upper\":"<<s[4]<<",\"best_lower\":"<<s[5];
            if(save_vectors){const double* v=vectors.data()+(size_t(c)*ncheck+k)*2*(N+M);vector_json("x_last",v,N);vector_json("y_last",v+N,M);vector_json("x_average",v+N+M,N);vector_json("y_average",v+2*N+M,M);}
            out<<'}';
        }out<<"]}";
    }
    out<<"],\"scope\":\"Floating Chambolle-Pock iterates and primal/dual objectives are numerical ranking diagnostics only, not certificates, exclusions, exact LP optima or graph completions.\"}\n";
    if(!out)throw std::runtime_error("Output write failed");
    std::cout<<"CUDA CP "<<count<<" candidates,"<<checkpoints.back()<<" iterations: "<<milliseconds/1000.0<<" s kernels,"<<elapsed<<" s transfer+kernel,"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<" s total\n";
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}return 0;}
