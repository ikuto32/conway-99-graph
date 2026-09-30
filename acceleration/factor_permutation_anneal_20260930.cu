// Integer cross-Gram objective v1; prototype, not a target-graph validator.
#include <cuda_runtime.h>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int NMAX=20, MMAX=180, RMAX=60, WORDS=3;
using U64=unsigned long long;
struct Problem { int n,m,target[RMAX*RMAX],edge[3][MMAX][2]; };
struct State {
  int perm[3][MMAX],best[3][MMAX],score,best_score;
  U64 rows[RMAX][WORDS],rng,proposals;
};
struct Trace { int block,a,b,delta,accepted,score,best_score; };
void require(bool b,const char* s){if(!b)throw std::runtime_error(s);}
void check(cudaError_t e){if(e!=cudaSuccess)throw std::runtime_error(cudaGetErrorString(e));}
__host__ __device__ U64 next(U64& x){x^=x>>12;x^=x<<25;x^=x>>27;return x*2685821657736338717ULL;}
int pop_cpu(U64 x){int s=0;while(x){x&=x-1;++s;}return s;}
void masks(const Problem& p,State& s){
  std::fill(&s.rows[0][0],&s.rows[0][0]+RMAX*WORDS,0ULL);
  for(int g=0;g<3;++g)for(int d=0;d<p.m;++d)for(int k=0;k<2;++k)
    s.rows[g*p.n+p.edge[g][s.perm[g][d]][k]][d/64]|=1ULL<<(d%64);
}
// Deliberately full recomputation: CPU calibration does not call GPU delta.
int full_cpu(const Problem& p,const State& s){
  int score=0;
  for(int g=0;g<3;++g)for(int h=g+1;h<3;++h)
    for(int i=g*p.n;i<(g+1)*p.n;++i)for(int j=h*p.n;j<(h+1)*p.n;++j){
      int count=0;for(int w=0;w<WORDS;++w)count+=pop_cpu(s.rows[i][w]&s.rows[j][w]);
      int q=count-p.target[i*RMAX+j];score+=q*q;
    }
  return score;
}
__host__ __device__ void proposal(State& s,int m,int& g,int& a,int& b,double& u){
  g=1+int(next(s.rng)%2);a=int(next(s.rng)%m);b=int(next(s.rng)%(m-1));if(b>=a)++b;
  u=double((next(s.rng)>>11)+1ULL)/9007199254740993.0;
}
__host__ __device__ bool accept(int delta,int mode,double temperature,double u){
  return mode==0||delta<=0||(temperature>0&&u<exp(-double(delta)/temperature));
}
__host__ __device__ void remember(const Problem& p,State& s){
  if(s.score<s.best_score){s.best_score=s.score;for(int g=0;g<3;++g)for(int d=0;d<p.m;++d)s.best[g][d]=s.perm[g][d];}
}
__global__ void run_gpu(const Problem* pp,State* states,Trace* traces,int chains,int steps,int mode,double temperature){
  int c=blockIdx.x*blockDim.x+threadIdx.x;if(c>=chains)return;
  const Problem& p=*pp;State& s=states[c];
  for(int t=0;t<steps;++t){
    int g,a,b;double u;proposal(s,p.m,g,a,b,u);int delta=0;
    // Swapping two columns toggles those bits only in rows incident to exactly one column.
    for(int r=g*p.n;r<(g+1)*p.n;++r){
      int ba=int((s.rows[r][a/64]>>(a%64))&1ULL),bb=int((s.rows[r][b/64]>>(b%64))&1ULL;
      if(ba==bb)continue;
      U64 changed[WORDS];for(int w=0;w<WORDS;++w)changed[w]=s.rows[r][w];
      changed[a/64]^=1ULL<<(a%64);changed[b/64]^=1ULL<<(b%64);
      for(int j=0;j<3*p.n;++j)if(j/p.n!=g){
        int old_count=0,new_count=0;for(int w=0;w<WORDS;++w){
          old_count+=__popcll(s.rows[r][w]&s.rows[j][w]);new_count+=__popcll(changed[w]&s.rows[j][w]);
        }
        int old_error=old_count-p.target[r*RMAX+j],new_error=new_count-p.target[r*RMAX+j];
        delta+=new_error*new_error-old_error*old_error;
      }
    }
    bool yes=accept(delta,mode,temperature,u);
    if(yes){
      for(int r=g*p.n;r<(g+1)*p.n;++r){
        int ba=int((s.rows[r][a/64]>>(a%64))&1ULL),bb=int((s.rows[r][b/64]>>(b%64))&1ULL);
        if(ba!=bb){s.rows[r][a/64]^=1ULL<<(a%64);s.rows[r][b/64]^=1ULL<<(b%64);}
      }
      int q=s.perm[g][a];s.perm[g][a]=s.perm[g][b];s.perm[g][b]=q;s.score+=delta;remember(p,s);
    }
    ++s.proposals;traces[c*steps+t]={g,a,b,delta,int(yes),s.score,s.best_score};
  }
}
void run_cpu(const Problem& p,std::vector<State>& states,std::vector<Trace>& traces,int steps,int mode,double temperature){
  for(size_t c=0;c<states.size();++c){State& s=states[c];for(int t=0;t<steps;++t){
    int g,a,b;double u;proposal(s,p.m,g,a,b,u);State test=s;std::swap(test.perm[g][a],test.perm[g][b]);masks(p,test);
    int new_score=full_cpu(p,test),delta=new_score-s.score;bool yes=accept(delta,mode,temperature,u);
    if(yes){s=test;s.score=new_score;remember(p,s);}++s.proposals;
    traces[c*steps+t]={g,a,b,delta,int(yes),s.score,s.best_score};
  }}
}
void permutation(std::istream& in,int* q,int m){
  std::vector<int> seen(m,0);for(int d=0;d<m;++d){require(bool(in>>q[d]),"truncated permutation");require(q[d]>=0&&q[d]<m,"permutation range");require(++seen[q[d]]==1,"duplicate permutation");}
}
void list(std::ostream& out,const int* v,int n){out<<'[';for(int i=0;i<n;++i){if(i)out<<',';out<<v[i];}out<<']';}
int main(int argc,char** argv){try{
  require(argc==4,"usage: executable cpu|gpu INPUT OUTPUT (fresh output)");std::string backend=argv[1];require(backend=="cpu"||backend=="gpu","backend");
  std::ifstream old(argv[3]);require(!old.good(),"refusing existing output");std::ifstream in(argv[2]);require(in.good(),"input open");
  Problem p{};std::string magic;int chains,steps,mode;double temperature;
  require(bool(in>>magic>>p.n>>chains>>steps>>mode>>temperature)&&magic=="FACTOR_PERMUTATION_V1","header");
  require(p.n>=4&&p.n<=NMAX&&p.n%2==0,"n bound");p.m=p.n*(p.n-2)/2;
  require(chains>=1&&chains<=256&&steps>=0&&steps<=1024,"chunk bounds");require(mode==0||mode==1,"mode");require(std::isfinite(temperature)&&temperature>=0&&temperature<=1e6,"temperature");
  for(int i=0;i<3*p.n;++i)for(int j=0;j<3*p.n;++j){int& q=p.target[i*RMAX+j];require(bool(in>>q)&&q>=-3&&q<=p.n,"target range");}
  for(int i=0;i<3*p.n;++i)for(int j=0;j<3*p.n;++j)require(p.target[i*RMAX+j]==p.target[j*RMAX+i],"target symmetry");
  for(int g=0;g<3;++g){int seen[NMAX][NMAX]={},degree[NMAX]={};for(int d=0;d<p.m;++d){
    int& a=p.edge[g][d][0];int& b=p.edge[g][d][1];require(bool(in>>a>>b)&&a>=0&&a<b&&b<p.n,"catalog pair");require(++seen[a][b]==1,"catalog duplicate");++degree[a];++degree[b];
  }for(int r=0;r<p.n;++r)require(degree[r]==p.n-2,"catalog degrees");}
  std::vector<State> states(chains);for(State& s:states){
    require(bool(in>>s.rng>>s.proposals)&&s.rng!=0,"rng state");for(int d=0;d<p.m;++d)s.perm[0][d]=s.best[0][d]=d;
    for(int g=1;g<3;++g)permutation(in,s.perm[g],p.m);for(int g=1;g<3;++g)permutation(in,s.best[g],p.m);
    masks(p,s);s.score=full_cpu(p,s);State best=s;for(int g=1;g<3;++g)for(int d=0;d<p.m;++d)best.perm[g][d]=s.best[g][d];masks(p,best);s.best_score=full_cpu(p,best);require(s.best_score<=s.score,"best worse than current");
  }
  std::string extra;require(!(in>>extra),"trailing input");std::vector<Trace> traces(size_t(chains)*steps);
  float kernel_ms=0;std::string device="CPU full recomputation";int runtime=0,driver=0;
  if(backend=="gpu"){
    cudaDeviceProp prop{};check(cudaGetDeviceProperties(&prop,0));device=prop.name;check(cudaRuntimeGetVersion(&runtime));check(cudaDriverGetVersion(&driver));
    Problem* dp;State* ds;Trace* dt;check(cudaMalloc(&dp,sizeof(p)));check(cudaMalloc(&ds,sizeof(State)*chains));check(cudaMalloc(&dt,sizeof(Trace)*std::max(size_t(1),traces.size())));
    check(cudaMemcpy(dp,&p,sizeof(p),cudaMemcpyHostToDevice));check(cudaMemcpy(ds,states.data(),sizeof(State)*chains,cudaMemcpyHostToDevice));
    cudaEvent_t begin,end;check(cudaEventCreate(&begin));check(cudaEventCreate(&end));check(cudaEventRecord(begin));
    run_gpu<<<(chains+31)/32,32>>>(dp,ds,dt,chains,steps,mode,temperature);check(cudaGetLastError());check(cudaEventRecord(end));check(cudaEventSynchronize(end));check(cudaEventElapsedTime(&kernel_ms,begin,end));
    check(cudaMemcpy(states.data(),ds,sizeof(State)*chains,cudaMemcpyDeviceToHost));if(!traces.empty())check(cudaMemcpy(traces.data(),dt,sizeof(Trace)*traces.size(),cudaMemcpyDeviceToHost));
    check(cudaFree(dt));check(cudaFree(ds));check(cudaFree(dp));check(cudaEventDestroy(begin));check(cudaEventDestroy(end));
  }else run_cpu(p,states,traces,steps,mode,temperature);
  for(State& s:states){State rebuilt=s;masks(p,rebuilt);require(full_cpu(p,rebuilt)==s.score,"final CPU score mismatch");for(int r=0;r<3*p.n;++r)for(int w=0;w<WORDS;++w)require(s.rows[r][w]==rebuilt.rows[r][w],"final row-mask mismatch");
    for(int g=1;g<3;++g)for(int d=0;d<p.m;++d)rebuilt.perm[g][d]=s.best[g][d];masks(p,rebuilt);require(full_cpu(p,rebuilt)==s.best_score,"best CPU score mismatch");}
  std::ofstream out(argv[3]);require(out.good(),"output open");out<<"{\"backend\":\""<<backend<<"\",\"device\":\""<<device<<"\",\"cuda_runtime\":"<<runtime<<",\"cuda_driver\":"<<driver<<",\"kernel_ms\":"<<kernel_ms<<",\"chains\":[";
  for(int c=0;c<chains;++c){if(c)out<<',';const State& s=states[c];out<<"{\"rng\":\""<<s.rng<<"\",\"proposals\":"<<s.proposals<<",\"score\":"<<s.score<<",\"best_score\":"<<s.best_score<<",\"permutations\":[";list(out,s.perm[1],p.m);out<<',';list(out,s.perm[2],p.m);out<<"],\"best_permutations\":[";list(out,s.best[1],p.m);out<<',';list(out,s.best[2],p.m);out<<"],\"trace\":[";
    for(int t=0;t<steps;++t){if(t)out<<',';const Trace& q=traces[c*steps+t];int v[7]={q.block,q.a,q.b,q.delta,q.accepted,q.score,q.best_score};list(out,v,7);}out<<"]}";
  }out<<"]}\n";require(out.good(),"output write");return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}}
