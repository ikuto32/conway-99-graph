// Full moment simplex PDHG; soft L1 rows and hard equality rows, explicit CSR and its exact transpose.
// Numerical ranking only. Binary little-endian protocol C99MHP01.
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

constexpr unsigned THREADS=256, MAX_DOMAIN=100000;
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
    need(g.n>=1 && g.n<=1000000 && g.m>=1 && g.m<=10000 && g.q<=g.m && g.blocks>=1 && g.blocks<=128 && g.blocks<=g.n && g.nnz<=100000000,"Unsupported candidate dimensions");
    total_n+=g.n;total_m+=g.m;total_nnz+=g.nnz;
    need(total_n<=2000000 && total_m<=1000000 && total_nnz<=100000000,"Aggregate geometry cap exceeded");
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

// Parser/storage/steps above adapted from star_pdhg_gpu.cu; new kernels below.
__global__ void dual(GPUModel g,unsigned iteration,int* error){
 unsigned r=blockIdx.x*blockDim.x+threadIdx.x;if(r>=g.m)return;
 double z=0;for(unsigned k=g.ar[r];k<g.ar[r+1];++k)z+=g.av[k]*g.pbar[g.ai[k]];
 z=g.y[r]+g.sigma[r]*(z-g.b[r]);
 if(!isfinite(z)){atomicExch(error,1);return;}
 if(r<g.q)z=fmin(1.,fmax(-1.,z)); // Remaining duals genuinely unbounded.
 g.y[r]=z;g.yavg[r]+=(z-g.yavg[r])/double(iteration);
 if(!isfinite(g.yavg[r]))atomicExch(error,2);
}
__device__ double reduce(double value,double* shared,bool maximum){
 unsigned t=threadIdx.x;shared[t]=value;__syncthreads();
 for(unsigned s=THREADS/2;s;s/=2){if(t<s)shared[t]=maximum?fmax(shared[t],shared[t+s]):shared[t]+shared[t+s];__syncthreads();}
 double answer=shared[0];__syncthreads();return answer;
}
__global__ void primal(GPUModel g,unsigned iteration,int* error){
 __shared__ double reduction[THREADS];unsigned u=blockIdx.x,lo=g.offsets[u],hi=g.offsets[u+1];
 double maximum=-CUDART_INF;
 for(unsigned j=lo+threadIdx.x;j<hi;j+=THREADS){
  double cost=0;for(unsigned k=g.tr[j];k<g.tr[j+1];++k)cost+=g.tv[k]*g.y[g.ti[k]];
  double value=g.p[j]-g.tau[u]*cost;g.trial[j]=value;
  if(!isfinite(value))atomicExch(error,3);maximum=fmax(maximum,value);
 }
 maximum=reduce(maximum,reduction,true);
 // Max-shifting puts the unique threshold in [-1,0]. Clipping inactive
 // tails at -1 is equivalent for every such threshold, avoiding overflow.
 for(unsigned j=lo+threadIdx.x;j<hi;j+=THREADS){
  double z=g.trial[j]-maximum;if(!isfinite(z))atomicExch(error,4);
  g.trial[j]=fmax(-1.,z);
 }
 __syncthreads();double left=-1.,right=0.;
 for(unsigned step=0;step<60;++step){
  double mid=(left+right)*.5,sum=0;
  for(unsigned j=lo+threadIdx.x;j<hi;j+=THREADS)sum+=fmax(0.,g.trial[j]-mid);
  sum=reduce(sum,reduction,false);if(sum>1.)left=mid;else right=mid;
 }
 double threshold=(left+right)*.5;
 for(unsigned j=lo+threadIdx.x;j<hi;j+=THREADS){
  double value=fmax(0.,g.trial[j]-threshold);g.pbar[j]=2.*value-g.p[j];g.p[j]=value;
  g.pavg[j]+=(value-g.pavg[j])/double(iteration);
  if(!isfinite(value)||!isfinite(g.pbar[j])||!isfinite(g.pavg[j]))atomicExch(error,5);
 }
}
void array_json(std::ostream& out,const std::vector<double>& a){out<<'[';for(size_t i=0;i<a.size();++i){need(std::isfinite(a[i]),"Nonfinite vector");if(i)out<<',';out<<a[i];}out<<']';}
void save(const std::string& path,const std::string& value){
 int fd=_open(path.c_str(),_O_WRONLY|_O_CREAT|_O_EXCL|_O_BINARY,_S_IREAD|_S_IWRITE);need(fd>=0,"Fresh output required");
 FILE* f=_fdopen(fd,"wb");need(f!=nullptr,"Output open failure");size_t count=fwrite(value.data(),1,value.size(),f);int close=fclose(f);need(count==value.size()&&close==0,"Output write failure");
}
void metrics(std::ostream& out,const Model& g,const std::vector<double>& p,const std::vector<double>& y){
 double soft=0,hard_l1=0,hard_max=0,lower=0,simplex=0;
 for(unsigned u=0;u<g.blocks;++u){double sum=0,minimum=INFINITY;
  for(unsigned j=g.offsets[u];j<g.offsets[u+1];++j){need(std::isfinite(p[j])&&p[j]>=0,"Invalid probability");sum+=p[j];double c=0;for(unsigned k=g.at.row[j];k<g.at.row[j+1];++k)c+=g.at.value[k]*y[g.at.index[k]];minimum=std::min(minimum,c);}
  simplex=std::max(simplex,std::abs(sum-1.));lower+=minimum;
 }
 need(simplex<1e-9,"Simplex residual exceeds fixed tolerance");
 for(unsigned r=0;r<g.m;++r){need(std::isfinite(y[r])&&(r>=g.q||std::abs(y[r])<=1.+1e-12),"Invalid dual");double residual=-g.b[r];
  for(unsigned k=g.a.row[r];k<g.a.row[r+1];++k)residual+=g.a.value[k]*p[g.a.index[k]];
  if(r<g.q)soft+=std::abs(residual);else{hard_l1+=std::abs(residual);hard_max=std::max(hard_max,std::abs(residual));}lower-=g.b[r]*y[r];
 }
 need(std::isfinite(soft)&&std::isfinite(hard_l1)&&std::isfinite(lower),"Nonfinite diagnostic");
 out<<"{\"soft_moment_L1_diagnostic\":"<<soft<<",\"hard_reciprocity_L1\":"<<hard_l1<<",\"hard_reciprocity_Linf\":"<<hard_max<<",\"simplex_Linf\":"<<simplex<<",\"dual_support_lower_numeric\":"<<lower<<",\"primal_upper\":null,\"primal_upper_null_reason\":\"Hard equality feasibility is not certified\"}";
}
int main(int argc,char** argv){try{
 need(argc==3,"Usage: moment_pdhg_gpu INPUT OUTPUT_PREFIX");std::string prefix=argv[2];
 Reader reader(argv[1]);char magic[8];reader.bytes(magic,8);need(memcmp(magic,"C99MHP01",8)==0,"Bad moment binary magic");
 need(reader.integer()==1,"Exactly one model per process");unsigned ncheck=reader.integer();need(ncheck>=1&&ncheck<=16,"Checkpoint count");
 auto checkpoints=reader.array<unsigned>(ncheck);for(unsigned i=0;i<ncheck;++i){need(checkpoints[i]>=1&&checkpoints[i]<=100000&&(i==0||checkpoints[i-1]<checkpoints[i]),"Checkpoint range/order");need(!std::filesystem::exists(prefix+"_"+std::to_string(checkpoints[i])+".json"),"Existing checkpoint");}
 need(!std::filesystem::exists(prefix+"_summary.json"),"Existing summary");
 uint64_t tn=0,tm=0,tz=0;Model model=read_model(reader,tn,tm,tz);need(reader.remaining==0,"Trailing bytes");
 cudaDeviceProp property{};CUDA(cudaGetDeviceProperties(&property,0));GPUStorage store(model);GPUModel g=store.view(model);Device<int> error(1);error.put(std::vector<int>(1,0));
 auto start=Clock::now();unsigned previous=0;double gpu_seconds=0;
 for(unsigned cp:checkpoints){cudaEvent_t a,b;CUDA(cudaEventCreate(&a));CUDA(cudaEventCreate(&b));CUDA(cudaEventRecord(a));
  for(unsigned i=previous+1;i<=cp;++i){dual<<<(g.m+THREADS-1)/THREADS,THREADS>>>(g,i,error.p);primal<<<g.blocks,THREADS>>>(g,i,error.p);}
  CUDA(cudaGetLastError());CUDA(cudaEventRecord(b));CUDA(cudaEventSynchronize(b));float ms;CUDA(cudaEventElapsedTime(&ms,a,b));gpu_seconds+=ms/1000.;CUDA(cudaEventDestroy(a));CUDA(cudaEventDestroy(b));need(error.get()[0]==0,"Kernel numerical failure");
  auto p=store.p.get(),pb=store.pbar.get(),y=store.y.get(),pa=store.pavg.get(),ya=store.yavg.get();
  std::ostringstream out;out<<std::setprecision(17)<<"{\"status\":\"NUMERICAL_FULL_MOMENT_PDHG_CHECKPOINT\",\"iterations\":"<<cp<<",\"numerical_scores_are_proofs\":false,\"last\":";metrics(out,model,p,y);out<<",\"average\":";metrics(out,model,pa,ya);
  out<<",\"p_last\":";array_json(out,p);out<<",\"pbar_last\":";array_json(out,pb);out<<",\"y_last\":";array_json(out,y);out<<",\"p_average\":";array_json(out,pa);out<<",\"y_average\":";array_json(out,ya);out<<"}\n";save(prefix+"_"+std::to_string(cp)+".json",out.str());previous=cp;
  std::cout<<"checkpoint="<<cp<<" elapsed_seconds="<<seconds(start)<<std::endl;
 }
 std::ostringstream summary;summary<<std::setprecision(17)<<"{\"status\":\"NUMERICAL_FULL_MOMENT_PDHG_FINISHED\",\"device\":\""<<property.name<<"\",\"iterations\":"<<previous<<",\"gpu_iteration_seconds\":"<<gpu_seconds<<",\"elapsed_seconds\":"<<seconds(start)<<",\"float_type\":\"float64\",\"projection_bisections\":60,\"threads_per_simplex\":256,\"eta\":0.9,\"theta\":1,\"cold\":true,\"numerical_scores_are_proofs\":false}\n";save(prefix+"_summary.json",summary.str());return 0;
 }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 2;}}
