// Cold star-simplex PDHG, explicit CSR and its exact transpose.
// Numerical ranking only. Binary little-endian protocol C99SCP01.
#include <cuda_runtime.h>
#include <math_constants.h>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <fcntl.h>
#include <io.h>
#include <sys/stat.h>

constexpr unsigned THREADS=256, MAX_DOMAIN=8192;
constexpr double ETA=.9, MAGNITUDE_CAP=1e290;
void need(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
void cuda_check(cudaError_t e,const char* what){if(e!=cudaSuccess)throw std::runtime_error(std::string(what)+": "+cudaGetErrorString(e));}
#define CUDA(x) cuda_check((x),#x)
using Clock=std::chrono::steady_clock;
double seconds(Clock::time_point start){return std::chrono::duration<double>(Clock::now()-start).count();}

template<class T>struct Device {
    T* p=nullptr; size_t n=0;
    explicit Device(size_t count):n(count){if(n)CUDA(cudaMalloc(&p,n*sizeof(T)));}
    ~Device(){if(p)cudaFree(p);}
    Device(const Device&)=delete; Device& operator=(const Device&)=delete;
    void put(const std::vector<T>& value){need(value.size()==n,"Device input size mismatch");if(n)CUDA(cudaMemcpy(p,value.data(),n*sizeof(T),cudaMemcpyHostToDevice));}
    std::vector<T> get()const{std::vector<T> r(n);if(n)CUDA(cudaMemcpy(r.data(),p,n*sizeof(T),cudaMemcpyDeviceToHost));return r;}
};

struct Reader {
    std::ifstream file; uint64_t remaining;
    explicit Reader(const std::string& path):file(path,std::ios::binary|std::ios::ate){
        need(bool(file),"Cannot open input"); auto length=file.tellg();
        need(length>=0 && uint64_t(length)<=uint64_t(2)*1024*1024*1024,"Input exceeds2GiB limit");
        remaining=uint64_t(length);file.seekg(0);
    }
    void bytes(void* dst,size_t count){need(count<=remaining,"Truncated binary input");if(count)file.read(static_cast<char*>(dst),std::streamsize(count));need(bool(file),"Binary input read failed");remaining-=count;}
    unsigned integer(){uint32_t n;bytes(&n,sizeof n);return n;}
    template<class T>std::vector<T> array(size_t n){need(n<=remaining/sizeof(T),"Truncated binary array");std::vector<T> v(n);bytes(v.data(),n*sizeof(T));return v;}
};

struct CSR {std::vector<unsigned> row,index;std::vector<double> value;};
struct Model {
    unsigned n,m,q,blocks,nnz,max_pad=1;
    std::vector<unsigned> offsets;
    CSR a,at;
    std::vector<double> b,tau,sigma;
};
void validate_csr(const CSR& a,unsigned rows,unsigned cols,unsigned nnz){
    need(a.row.size()==size_t(rows)+1 && a.row.front()==0 && a.row.back()==nnz,"Bad CSR row pointer endpoints");
    for(unsigned r=0;r<rows;++r){
        need(a.row[r]<=a.row[r+1] && a.row[r+1]<=nnz,"Bad CSR row pointers");
        unsigned previous=0;
        for(unsigned k=a.row[r];k<a.row[r+1];++k){
            need(a.index[k]<cols && (k==a.row[r] || previous<a.index[k]),"CSR columns must be sorted, unique, in range");
            need(std::isfinite(a.value[k]) && a.value[k]!=0,"CSR values must be finite and nonzero");
            previous=a.index[k];
        }
    }
}
Model read_model(Reader& in,uint64_t& total_n,uint64_t& total_m,uint64_t& total_nnz){
    Model g;g.n=in.integer();g.m=in.integer();g.q=in.integer();g.blocks=in.integer();g.nnz=in.integer();
    need(g.n>=1 && g.n<=100000 && g.m>=1 && g.m<=20000 && g.q<=g.m && g.blocks>=1 && g.blocks<=128 && g.blocks<=g.n && g.nnz<=8000000,"Unsupported candidate dimensions");
    total_n+=g.n;total_m+=g.m;total_nnz+=g.nnz;
    need(total_n<=2000000 && total_m<=1000000 && total_nnz<=64000000,"Aggregate geometry cap exceeded");
    const uint64_t required=uint64_t(g.blocks+1+g.m+1+g.n+1)*4+uint64_t(g.nnz)*24+uint64_t(g.m)*8;
    need(required<=in.remaining,"Truncated candidate geometry");
    g.offsets=in.array<unsigned>(g.blocks+1);
    need(g.offsets.front()==0 && g.offsets.back()==g.n,"Invalid domain offsets");
    for(unsigned u=0;u<g.blocks;++u){
        need(g.offsets[u]<g.offsets[u+1] && g.offsets[u+1]<=g.n && g.offsets[u+1]-g.offsets[u]<=MAX_DOMAIN,"Invalid/oversized simplex domain");
        unsigned pad=1;while(pad<g.offsets[u+1]-g.offsets[u])pad*=2;g.max_pad=std::max(g.max_pad,pad);
    }
    g.a.row=in.array<unsigned>(g.m+1);g.a.index=in.array<unsigned>(g.nnz);g.a.value=in.array<double>(g.nnz);
    g.at.row=in.array<unsigned>(g.n+1);g.at.index=in.array<unsigned>(g.nnz);g.at.value=in.array<double>(g.nnz);
    g.b=in.array<double>(g.m);
    validate_csr(g.a,g.m,g.n,g.nnz);validate_csr(g.at,g.n,g.m,g.nnz);
    // Because A rows and AT rows are strictly sorted, insertion in source row
    // order visits every expected AT entry in exactly its canonical order.
    std::vector<unsigned> position=g.at.row;
    for(unsigned r=0;r<g.m;++r)for(unsigned k=g.a.row[r];k<g.a.row[r+1];++k){
        const unsigned col=g.a.index[k], target=position[col]++;
        need(target<g.at.row[col+1] && g.at.index[target]==r && g.at.value[target]==g.a.value[k],"AT is not the exact transpose of A");
    }
    for(unsigned j=0;j<g.n;++j)need(position[j]==g.at.row[j+1],"Transpose has unmatched entries");
    g.sigma.resize(g.m);g.tau.resize(g.blocks);
    for(unsigned r=0;r<g.m;++r){
        double sum=0;for(unsigned k=g.a.row[r];k<g.a.row[r+1];++k)sum+=std::abs(g.a.value[k]);
        need(std::isfinite(sum) && sum<=MAGNITUDE_CAP && std::isfinite(g.b[r]) && std::abs(g.b[r])<=MAGNITUDE_CAP,"Nonfinite/unsupported row magnitude or target");
        g.sigma[r]=ETA/std::max(1.,sum);
    }
    for(unsigned u=0;u<g.blocks;++u){
        double maximum=1;
        for(unsigned j=g.offsets[u];j<g.offsets[u+1];++j){
            double sum=0;for(unsigned k=g.at.row[j];k<g.at.row[j+1];++k)sum+=std::abs(g.at.value[k]);
            need(std::isfinite(sum) && sum<=MAGNITUDE_CAP,"Nonfinite/unsupported column magnitude");maximum=std::max(maximum,sum);
        }
        g.tau[u]=ETA/maximum;
    }
    return g;
}

struct GPUModel {
    unsigned n,m,q,blocks;
    const unsigned *ar,*ai,*tr,*ti,*offsets;
    const double *av,*tv,*b,*tau,*sigma;
    double *p,*pbar,*y,*pavg,*yavg,*trial;
};
struct GPUStorage {
    Device<unsigned> ar,ai,tr,ti,offsets;
    Device<double> av,tv,b,tau,sigma,p,pbar,y,pavg,yavg,trial;
    explicit GPUStorage(const Model& g):ar(g.a.row.size()),ai(g.nnz),tr(g.at.row.size()),ti(g.nnz),offsets(g.offsets.size()),
        av(g.nnz),tv(g.nnz),b(g.m),tau(g.blocks),sigma(g.m),p(g.n),pbar(g.n),y(g.m),pavg(g.n),yavg(g.m),trial(g.n){
        ar.put(g.a.row);ai.put(g.a.index);tr.put(g.at.row);ti.put(g.at.index);offsets.put(g.offsets);
        av.put(g.a.value);tv.put(g.at.value);b.put(g.b);tau.put(g.tau);sigma.put(g.sigma);
        std::vector<double> start(g.n),z(g.n,0),zy(g.m,0);
        for(unsigned u=0;u<g.blocks;++u)for(unsigned j=g.offsets[u];j<g.offsets[u+1];++j)start[j]=1./(g.offsets[u+1]-g.offsets[u]);
        p.put(start);pbar.put(start);pavg.put(z);y.put(zy);yavg.put(zy);
    }
    GPUModel view(const Model& g){return GPUModel{g.n,g.m,g.q,g.blocks,ar.p,ai.p,tr.p,ti.p,offsets.p,av.p,tv.p,b.p,tau.p,sigma.p,p.p,pbar.p,y.p,pavg.p,yavg.p,trial.p};}
};
struct Job {unsigned candidate,index;};

__global__ void dual_rows(const GPUModel* models,const Job* jobs,unsigned count,unsigned iteration,int* error){
    const unsigned tid=blockIdx.x*blockDim.x+threadIdx.x;if(tid>=count)return;
    const Job job=jobs[tid];const GPUModel g=models[job.candidate];const unsigned r=job.index;
    double sum=0;for(unsigned k=g.ar[r];k<g.ar[r+1];++k)sum+=g.av[k]*g.pbar[g.ai[k]];
    const double z=g.y[r]+g.sigma[r]*(sum-g.b[r]);
    if(!isfinite(sum)||!isfinite(z)){atomicExch(error,1);return;}
    const double value=fmin(1.,fmax(r<g.q?-1.:0.,z));
    g.y[r]=value;g.yavg[r]+=(value-g.yavg[r])/double(iteration);
    if(!isfinite(g.yavg[r]))atomicExch(error,2);
}

// Collective block routine. Values are max-shifted and clipped at -1 before
// sorting, so finite tails cannot overflow the prefix sum. Threshold is a
// serial prefix in sorted order, matching the frozen CPU reference semantics.
__device__ double threshold(double* shared,double* reduction,const double* trial,unsigned begin,unsigned size,unsigned pad,int* error){
    const unsigned t=threadIdx.x;double maximum=-CUDART_INF;
    for(unsigned j=t;j<size;j+=THREADS)maximum=fmax(maximum,trial[begin+j]);
    reduction[t]=maximum;__syncthreads();
    for(unsigned stride=THREADS/2;stride;stride/=2){if(t<stride)reduction[t]=fmax(reduction[t],reduction[t+stride]);__syncthreads();}
    maximum=reduction[0];
    for(unsigned j=t;j<pad;j+=THREADS){
        double value=-2.;
        if(j<size){const double shifted=trial[begin+j]-maximum;if(!isfinite(shifted))atomicExch(error,3);value=fmax(shifted,-1.);}
        shared[j]=value;
    }
    __syncthreads();
    for(unsigned stage=2;stage<=pad;stage*=2)for(unsigned distance=stage/2;distance;distance/=2){
        for(unsigned j=t;j<pad;j+=THREADS){
            const unsigned other=j^distance;
            if(other>j){const double left=shared[j],right=shared[other];const bool descending=(j&stage)==0;
                if((descending&&left<right)||(!descending&&left>right)){shared[j]=right;shared[other]=left;}}
        }
        __syncthreads();
    }
    if(t==0){double sum=0,theta=-1.;for(unsigned j=0;j<size;++j){sum+=shared[j];const double test=(sum-1.)/double(j+1);if(shared[j]>test)theta=test;}
        reduction[0]=theta;reduction[1]=maximum;
    }
    __syncthreads();return reduction[0];
}

__global__ void primal_simplexes(const GPUModel* models,const Job* jobs,unsigned iteration,int* error){
    const Job job=jobs[blockIdx.x];const GPUModel g=models[job.candidate];const unsigned u=job.index;
    const unsigned begin=g.offsets[u],end=g.offsets[u+1],size=end-begin;
    unsigned pad=1;while(pad<size)pad*=2;
    extern __shared__ double storage[];double* reduction=storage+pad;
    for(unsigned j=begin+threadIdx.x;j<end;j+=THREADS){
        double cost=0;for(unsigned k=g.tr[j];k<g.tr[j+1];++k)cost+=g.tv[k]*g.y[g.ti[k]];
        const double trial=g.p[j]-g.tau[u]*cost;
        if(!isfinite(cost)||!isfinite(trial))atomicExch(error,4);
        g.trial[j]=trial;
    }
    __syncthreads();const double theta=threshold(storage,reduction,g.trial,begin,size,pad,error);
    const double maximum=reduction[1];
    for(unsigned j=begin+threadIdx.x;j<end;j+=THREADS){
        const double value=fmax(fmax(g.trial[j]-maximum,-1.)-theta,0.);
        g.pbar[j]=2*value-g.p[j];g.p[j]=value;g.pavg[j]+=(value-g.pavg[j])/double(iteration);
        if(!isfinite(value)||!isfinite(g.pbar[j])||!isfinite(g.pavg[j]))atomicExch(error,5);
    }
}

__global__ void projection_only(const double* values,double* result,unsigned size,int* error){
    unsigned pad=1;while(pad<size)pad*=2;
    extern __shared__ double storage[];double* reduction=storage+pad;
    const double theta=threshold(storage,reduction,values,0,size,pad,error);const double maximum=reduction[1];
    for(unsigned j=threadIdx.x;j<size;j+=THREADS){result[j]=fmax(fmax(values[j]-maximum,-1.)-theta,0.);if(!isfinite(result[j]))atomicExch(error,6);}
}

struct Bound {double upper,lower;};
Bound bounds(const Model& g,const std::vector<double>& p,const std::vector<double>& y){
    need(p.size()==g.n && y.size()==g.m,"Checkpoint vector size mismatch");
    for(unsigned u=0;u<g.blocks;++u){double sum=0;for(unsigned j=g.offsets[u];j<g.offsets[u+1];++j){need(std::isfinite(p[j]) && p[j]>=0,"Checkpoint nonfinite/negative probability");sum+=p[j];}need(std::abs(sum-1)<1e-9,"Checkpoint simplex normalization failure");}
    for(unsigned r=0;r<g.m;++r)need(std::isfinite(y[r]) && y[r]>=((r<g.q?-1.:0.)-1e-12) && y[r]<=1.+1e-12,"Checkpoint dual box failure");
    double upper=0,lower=0;
    for(unsigned r=0;r<g.m;++r){double sum=-g.b[r];for(unsigned k=g.a.row[r];k<g.a.row[r+1];++k)sum+=g.a.value[k]*p[g.a.index[k]];
        upper+=r<g.q?std::abs(sum):std::max(0.,sum);lower-=g.b[r]*y[r];}
    for(unsigned u=0;u<g.blocks;++u){double minimum=std::numeric_limits<double>::infinity();
        for(unsigned j=g.offsets[u];j<g.offsets[u+1];++j){double sum=0;for(unsigned k=g.at.row[j];k<g.at.row[j+1];++k)sum+=g.at.value[k]*y[g.at.index[k]];minimum=std::min(minimum,sum);}lower+=minimum;}
    need(std::isfinite(upper)&&std::isfinite(lower),"Nonfinite checkpoint merit");return {upper,lower};
}
struct Point {unsigned iteration;Bound last,average;double best_upper,best_lower;std::vector<double> p,pbar,y,pavg,yavg;};
struct Result {Bound initial;double best_upper,best_lower;std::vector<Point> points;};
void array_json(std::ostream& out,const std::vector<double>& a){out<<'[';for(size_t i=0;i<a.size();++i){need(std::isfinite(a[i]),"Nonfinite output vector");if(i)out<<',';out<<a[i];}out<<']';}
void bound_json(std::ostream& out,const Bound& b){out<<"{\"primal_upper_numeric\":"<<b.upper<<",\"dual_lower_numeric\":"<<b.lower<<",\"numeric_gap\":"<<b.upper-b.lower<<'}';}
void save_exclusive(const std::string& path,const std::string& value){
    const int fd=_open(path.c_str(),_O_WRONLY|_O_CREAT|_O_EXCL|_O_BINARY,_S_IREAD|_S_IWRITE);
    need(fd>=0,"Cannot create fresh output");FILE* file=_fdopen(fd,"wb");if(!file){_close(fd);throw std::runtime_error("Cannot open output stream");}
    const size_t written=std::fwrite(value.data(),1,value.size(),file);const int closed=std::fclose(file);
    need(written==value.size() && closed==0,"Output write failed");
}
void shared_configuration(size_t bytes,bool projection){
    cudaDeviceProp property{};CUDA(cudaGetDeviceProperties(&property,0));need(bytes<=size_t(property.sharedMemPerBlockOptin),"GPU cannot support requested simplex shared memory");
    if(projection)CUDA(cudaFuncSetAttribute(projection_only,cudaFuncAttributeMaxDynamicSharedMemorySize,int(bytes)));
    else CUDA(cudaFuncSetAttribute(primal_simplexes,cudaFuncAttributeMaxDynamicSharedMemorySize,int(bytes)));
}

int selftest(const std::string& out_path){
    need(!std::filesystem::exists(out_path),"Output already exists");
    std::vector<std::vector<double>> cases={{0.,-1e308,-1e308},{-5.},{-3.,-3.},std::vector<double>(1053,0.),std::vector<double>(2049),std::vector<double>(8192,0.)};
    const char* names[]={"extreme_negative_tail","singleton","equal_negative_pair","uniform_1053","pattern_2049","maximum_uniform_8192"};
    for(unsigned j=0;j<2049;++j)cases[4][j]=(int(j%17)-8)/16.;
    shared_configuration((MAX_DOMAIN+THREADS)*sizeof(double),true);
    Device<int> error(1);std::vector<int> zero(1,0);error.put(zero);
    std::ostringstream out;out<<std::setprecision(17)<<"{\"status\":\"NUMERICAL_SIMPLEX_PROJECTION_SELF_TEST_FINISHED\",\"numerical_scores_are_proofs\":false,\"cases\":[";
    for(size_t c=0;c<cases.size();++c){Device<double> input(cases[c].size()),output(cases[c].size());input.put(cases[c]);
        unsigned pad=1;while(pad<cases[c].size())pad*=2;
        projection_only<<<1,THREADS,(pad+THREADS)*sizeof(double)>>>(input.p,output.p,unsigned(cases[c].size()),error.p);CUDA(cudaGetLastError());CUDA(cudaDeviceSynchronize());need(error.get()[0]==0,"Projection kernel numerical failure");
        const auto result=output.get();if(c)out<<',';out<<"{\"case_index\":"<<c<<",\"name\":\""<<names[c]<<"\",\"size\":"<<cases[c].size()<<",\"input\":";array_json(out,cases[c]);out<<",\"projected\":";array_json(out,result);out<<'}';}
    out<<"]}\n";save_exclusive(out_path,out.str());return 0;
}

int main(int argc,char** argv){
    try {
        if(argc==3 && std::string(argv[1])=="--projection-self-test")return selftest(argv[2]);
        need(argc==3 || (argc==4 && std::string(argv[3])=="--vectors"),"Usage: star_pdhg_gpu INPUT OUTPUT [--vectors]");
        const bool vectors=argc==4;const std::string output=argv[2];need(!std::filesystem::exists(output),"Output already exists");
        const auto started=Clock::now();Reader reader(argv[1]);char magic[8];reader.bytes(magic,8);need(std::memcmp(magic,"C99SCP01",8)==0,"Bad binary magic");
        const unsigned count=reader.integer(),ncheck=reader.integer();need(count>=1&&count<=256&&ncheck>=1&&ncheck<=16,"Invalid candidate/checkpoint count");
        need(!vectors||count<=16,"Vectors require at most16 candidates");const auto checkpoints=reader.array<unsigned>(ncheck);
        for(unsigned i=0;i<ncheck;++i)need(checkpoints[i]>=1&&checkpoints[i]<=20000&&(i==0||checkpoints[i-1]<checkpoints[i]),"Invalid checkpoint order/range");
        std::vector<Model> models;models.reserve(count);uint64_t total_n=0,total_m=0,total_nnz=0;unsigned max_pad=1;
        for(unsigned c=0;c<count;++c){models.push_back(read_model(reader,total_n,total_m,total_nnz));max_pad=std::max(max_pad,models.back().max_pad);}
        need(reader.remaining==0,"Trailing binary input");need(!vectors||uint64_t(ncheck)*(3*total_n+2*total_m)<=20000000,"Vector output cap exceeded");
        const double parse_seconds=seconds(started);
        cudaDeviceProp property{};CUDA(cudaGetDeviceProperties(&property,0));shared_configuration((max_pad+THREADS)*sizeof(double),false);
        std::vector<std::unique_ptr<GPUStorage>> storage;std::vector<GPUModel> views;std::vector<Job> rows,vertices;std::vector<Result> results;
        for(unsigned c=0;c<count;++c){const Model& g=models[c];storage.emplace_back(new GPUStorage(g));views.push_back(storage.back()->view(g));
            for(unsigned r=0;r<g.m;++r)rows.push_back({c,r});for(unsigned u=0;u<g.blocks;++u)vertices.push_back({c,u});
            std::vector<double> p(g.n),y(g.m,0);for(unsigned u=0;u<g.blocks;++u)for(unsigned j=g.offsets[u];j<g.offsets[u+1];++j)p[j]=1./(g.offsets[u+1]-g.offsets[u]);
            const Bound initial=bounds(g,p,y);results.push_back(Result{initial,initial.upper,initial.lower,{}});
        }
        Device<GPUModel> gpu_models(views.size());gpu_models.put(views);Device<Job> gpu_rows(rows.size()),gpu_vertices(vertices.size());gpu_rows.put(rows);gpu_vertices.put(vertices);
        Device<int> error(1);error.put(std::vector<int>(1,0));cudaEvent_t begin,end;CUDA(cudaEventCreate(&begin));CUDA(cudaEventCreate(&end));
        double gpu_seconds=0,check_seconds=0;unsigned previous=0;
        for(unsigned checkpoint:checkpoints){CUDA(cudaEventRecord(begin));
            for(unsigned iteration=previous+1;iteration<=checkpoint;++iteration){
                dual_rows<<<unsigned((rows.size()+THREADS-1)/THREADS),THREADS>>>(gpu_models.p,gpu_rows.p,unsigned(rows.size()),iteration,error.p);
                primal_simplexes<<<unsigned(vertices.size()),THREADS,(max_pad+THREADS)*sizeof(double)>>>(gpu_models.p,gpu_vertices.p,iteration,error.p);
            }
            CUDA(cudaGetLastError());CUDA(cudaEventRecord(end));CUDA(cudaEventSynchronize(end));float ms=0;CUDA(cudaEventElapsedTime(&ms,begin,end));gpu_seconds+=ms/1000.;
            need(error.get()[0]==0,"PDHG kernel numerical failure");const auto checking=Clock::now();
            for(unsigned c=0;c<count;++c){Point point;point.iteration=checkpoint;
                point.p=storage[c]->p.get();point.pbar=storage[c]->pbar.get();point.y=storage[c]->y.get();point.pavg=storage[c]->pavg.get();point.yavg=storage[c]->yavg.get();
                for(double value:point.pbar)need(std::isfinite(value),"Nonfinite extrapolated probability");
                point.last=bounds(models[c],point.p,point.y);point.average=bounds(models[c],point.pavg,point.yavg);
                auto& result=results[c];result.best_upper=std::min({result.best_upper,point.last.upper,point.average.upper});result.best_lower=std::max({result.best_lower,point.last.lower,point.average.lower});
                point.best_upper=result.best_upper;point.best_lower=result.best_lower;
                if(!vectors){point.p.clear();point.pbar.clear();point.y.clear();point.pavg.clear();point.yavg.clear();}
                result.points.push_back(std::move(point));
            }
            check_seconds+=seconds(checking);previous=checkpoint;
        }
        CUDA(cudaEventDestroy(begin));CUDA(cudaEventDestroy(end));
        std::ostringstream out;out<<std::setprecision(17)<<"{\"status\":\"NUMERICAL_COLD_STAR_PDHG_BATCH_FINISHED\",\"eta\":0.9,\"theta\":1,\"float_type\":\"float64\",\"device\":\""<<property.name
            <<"\",\"candidate_count\":"<<count<<",\"parse_seconds\":"<<parse_seconds<<",\"gpu_iteration_seconds\":"<<gpu_seconds<<",\"checkpoint_transfer_and_metrics_seconds\":"<<check_seconds
            <<",\"elapsed_seconds\":"<<seconds(started)<<",\"scalar_metrics_computed_on_host\":true,\"numerical_scores_are_proofs\":false,\"initialization\":\"uniform_per_simplex_probability_zero_dual\",\"best_scope\":\"initial_and_requested_checkpoint_last_and_average\",\"results\":[";
        for(unsigned c=0;c<count;++c){if(c)out<<',';const auto& g=models[c];const auto& result=results[c];
            out<<"{\"candidate_index\":"<<c<<",\"n_variables\":"<<g.n<<",\"n_rows\":"<<g.m<<",\"n_equalities\":"<<g.q<<",\"domain_counts\":[";
            for(unsigned u=0;u<g.blocks;++u){if(u)out<<',';out<<g.offsets[u+1]-g.offsets[u];}out<<"],\"initial\":";bound_json(out,result.initial);out<<",\"checkpoints\":[";
            for(size_t i=0;i<result.points.size();++i){if(i)out<<',';const auto& point=result.points[i];out<<"{\"iterations\":"<<point.iteration<<",\"last\":";bound_json(out,point.last);out<<",\"average\":";bound_json(out,point.average);
                out<<",\"best_upper_numeric\":"<<point.best_upper<<",\"best_lower_numeric\":"<<point.best_lower;
                if(vectors){out<<",\"p_last\":";array_json(out,point.p);out<<",\"pbar_last\":";array_json(out,point.pbar);out<<",\"y_last\":";array_json(out,point.y);out<<",\"p_average\":";array_json(out,point.pavg);out<<",\"y_average\":";array_json(out,point.yavg);}
                out<<'}';}
            out<<"]}";
        }
        out<<"]}\n";save_exclusive(output,out.str());
        std::cout<<"{\"candidate_count\":"<<count<<",\"gpu_iteration_seconds\":"<<gpu_seconds<<",\"elapsed_seconds\":"<<seconds(started)<<"}\n";
        return 0;
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 2;}
}
