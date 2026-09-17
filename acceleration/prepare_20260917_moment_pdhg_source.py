"""One-time disclosed derivation of a NEW CUDA implementation; never edits old source."""
from pathlib import Path

root=Path(__file__).resolve().parent
old=(root/'star_pdhg_gpu.cu').read_text()
prefix=old[:old.index('struct Job')]
prefix=prefix.replace('Cold star-simplex PDHG','Full moment simplex PDHG; soft L1 rows and hard equality rows')
prefix=prefix.replace('C99SCP01','C99MHP01').replace('MAX_DOMAIN=8192','MAX_DOMAIN=100000')
prefix=prefix.replace('g.n<=100000','g.n<=1000000').replace('g.nnz<=8000000','g.nnz<=100000000')
prefix=prefix.replace('total_nnz<=64000000','total_nnz<=100000000')
prefix=prefix.replace('g.m<=20000','g.m<=10000')
suffix=r'''
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
'''
with (root/'moment_pdhg_gpu.cu').open('x',encoding='utf-8') as f:f.write(prefix+suffix)
build=(root/'build_star_pdhg_gpu.ps1').read_text().replace('star_pdhg_gpu','moment_pdhg_gpu')
with (root/'build_moment_pdhg_gpu.ps1').open('x',encoding='utf-8') as f:f.write(build)
