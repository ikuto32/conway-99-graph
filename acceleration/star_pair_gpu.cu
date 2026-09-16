// Initial support against ORIGINAL complete star domains. No AC propagation.
// Binary: "C99PAIR1", u32 candidates, then per candidate 84*u32 counts,
// followed by (u64 low,u64 high) full99 neighborhoods in vertex/domain order.
#include <cuda_runtime.h>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct Row { unsigned long long low, high; };
void check(cudaError_t e, const char* operation) {
    if (e != cudaSuccess) throw std::runtime_error(std::string(operation)+": "+cudaGetErrorString(e));
}
#define CUDA(x) check((x), #x)
template<class T> struct Device {
    T* p = nullptr;
    explicit Device(size_t n) { if(n) CUDA(cudaMalloc(&p, n*sizeof(T))); }
    ~Device() { if(p) cudaFree(p); }
};
template<class T> T read_le(std::istream& input) {
    T result=0;
    for(size_t j=0;j<sizeof(T);++j) {
        int byte=input.get();
        if(byte==EOF) throw std::runtime_error("Truncated binary input");
        result |= T(static_cast<unsigned char>(byte)) << (8*j);
    }
    return result;
}
bool host_bit(const Row& row, unsigned int bit) {
    return bit<64 ? (row.low>>bit)&1ULL : (row.high>>(bit-64))&1ULL;
}
int host_popcount(unsigned long long value) {
    int count=0;
    while(value) { value &= value-1; ++count; }
    return count;
}
__device__ bool bit(const Row& row, unsigned int index) {
    return index<64 ? (row.low>>index)&1ULL : (row.high>>(index-64))&1ULL;
}
__global__ void supports(const Row* rows, const unsigned int* owners,
                         const unsigned int* offsets, size_t jobs,
                         unsigned char* flags) {
    const size_t job=size_t(blockIdx.x)*blockDim.x+threadIdx.x;
    if(job>=jobs) return;
    const unsigned int index=job/84, v=job%84, owner=owners[index];
    const unsigned int candidate=owner/84, u=owner%84;
    if(u==v) { flags[job]=1; return; } // Self relation is an ignored sentinel.
    const Row left=rows[index];
    const bool adjacent=bit(left,v+15);
    bool found=false;
    for(unsigned int j=offsets[candidate*85+v];j<offsets[candidate*85+v+1];++j) {
        const Row right=rows[j];
        if(bit(right,u+15)==adjacent &&
           __popcll(left.low & right.low)+__popcll(left.high & right.high)==2-int(adjacent)) {
            found=true; break;
        }
    }
    flags[job]=found;
}
int main(int argc,char** argv) {
    try {
        if(argc<3 || argc>4 || (argc==4 && std::string(argv[3])!="--flags"))
            throw std::runtime_error("Usage: star_pair_gpu INPUT.bin OUTPUT.json [--flags]");
        if(std::ifstream(argv[2]).good()) throw std::runtime_error("Output already exists");
        const auto started=std::chrono::steady_clock::now();
        std::ifstream input(argv[1],std::ios::binary);
        char magic[8]; input.read(magic,8);
        if(!input || std::string(magic,8)!="C99PAIR1") throw std::runtime_error("Wrong binary header");
        const unsigned int count=read_le<uint32_t>(input);
        if(count==0 || count>10000) throw std::runtime_error("Invalid candidate count");
        std::vector<Row> rows;
        std::vector<unsigned int> owners,offsets;
        std::vector<std::array<unsigned int,84>> counts(count);
        for(unsigned int c=0;c<count;++c) {
            uint64_t total=0;
            for(unsigned int u=0;u<84;++u) { counts[c][u]=read_le<uint32_t>(input); total+=counts[c][u]; }
            if(total+rows.size()>2000000) throw std::runtime_error("Batch exceeds two million star domains");
            for(unsigned int u=0;u<84;++u) {
                offsets.push_back(static_cast<unsigned int>(rows.size()));
                for(unsigned int d=0;d<counts[c][u];++d) {
                    Row row{read_le<uint64_t>(input),read_le<uint64_t>(input)};
                    if((row.high>>35)!=0 || host_bit(row,u+15) || host_bit(row,0) ||
                       host_popcount(row.low)+host_popcount(row.high)!=14)
                        throw std::runtime_error("Neighborhood must be a loop-free degree14 outer full99 row");
                    rows.push_back(row); owners.push_back(c*84+u);
                }
            }
            offsets.push_back(static_cast<unsigned int>(rows.size()));
        }
        if(input.get()!=EOF) throw std::runtime_error("Trailing binary input");
        CUDA(cudaSetDevice(0));
        cudaDeviceProp device{}; CUDA(cudaGetDeviceProperties(&device,0));
        const size_t jobs=rows.size()*84;
        Device<Row> d_rows(rows.size()); Device<unsigned int> d_owners(owners.size()),d_offsets(offsets.size());
        Device<unsigned char> d_flags(jobs);
        std::vector<unsigned char> flags(jobs);
        cudaEvent_t begin,end; CUDA(cudaEventCreate(&begin));CUDA(cudaEventCreate(&end));
        const auto compute_start=std::chrono::steady_clock::now();
        CUDA(cudaMemcpy(d_offsets.p,offsets.data(),offsets.size()*sizeof(unsigned int),cudaMemcpyHostToDevice));
        if(jobs) {
            CUDA(cudaMemcpy(d_rows.p,rows.data(),rows.size()*sizeof(Row),cudaMemcpyHostToDevice));
            CUDA(cudaMemcpy(d_owners.p,owners.data(),owners.size()*sizeof(unsigned int),cudaMemcpyHostToDevice));
        }
        CUDA(cudaEventRecord(begin));
        if(jobs) {
            supports<<<static_cast<unsigned int>((jobs+255)/256),256>>>(d_rows.p,d_owners.p,d_offsets.p,jobs,d_flags.p);
            CUDA(cudaGetLastError());
        }
        CUDA(cudaEventRecord(end));CUDA(cudaEventSynchronize(end));
        float kernel_ms=0;CUDA(cudaEventElapsedTime(&kernel_ms,begin,end));
        if(jobs) CUDA(cudaMemcpy(flags.data(),d_flags.p,jobs,cudaMemcpyDeviceToHost));
        const double compute=std::chrono::duration<double>(std::chrono::steady_clock::now()-compute_start).count();
        CUDA(cudaEventDestroy(begin));CUDA(cudaEventDestroy(end));
        std::ofstream output(argv[2]);
        if(!output) throw std::runtime_error("Could not open output");
        output<<std::setprecision(12)<<"{\"status\":\"INITIAL_PAIR_SUPPORT_SCORES_ONLY\",\"backend\":\"cuda\",\"device\":\""
              <<device.name<<"\",\"candidate_count\":"<<count<<",\"total_domains\":"<<rows.size()
              <<",\"relations_evaluated\":"<<rows.size()*83<<",\"elapsed_seconds\":"<<compute
              <<",\"kernel_seconds\":"<<kernel_ms/1000.0<<",\"results\":[";
        for(unsigned int c=0;c<count;++c) {
            if(c) output<<',';
            std::array<unsigned int,84*84> unsupported{};
            std::array<unsigned int,84> surviving{};
            uint64_t total_unsupported=0;
            for(unsigned int u=0;u<84;++u) {
                for(unsigned int i=offsets[c*85+u];i<offsets[c*85+u+1];++i) {
                    bool all=true;
                    for(unsigned int v=0;v<84;++v) if(u!=v && !flags[size_t(i)*84+v]) {
                        ++unsupported[u*84+v]; ++total_unsupported; all=false;
                    }
                    surviving[u]+=all;
                }
            }
            output<<"{\"candidate_index\":"<<c<<",\"total_domains\":"<<offsets[c*85+84]-offsets[c*85]<<",\"domain_counts\":[";
            for(unsigned int u=0;u<84;++u) {if(u)output<<',';output<<counts[c][u];}
            output<<"],\"initial_pair_supported_domain_counts\":[";
            unsigned int vertices=0;uint64_t survivor_count=0;
            for(unsigned int u=0;u<84;++u) {if(u)output<<',';output<<surviving[u];vertices+=surviving[u]>0;survivor_count+=surviving[u];}
            output<<"],\"per_vertex_initial_supported_domains\":[";
            for(unsigned int u=0;u<84;++u) {if(u)output<<',';output<<surviving[u];}
            output<<"],\"vertices_with_initial_pair_supported_domain\":"<<vertices
                  <<",\"total_initial_pair_supported_domains\":"<<survivor_count
                  <<",\"total_unsupported_relations\":"<<total_unsupported<<",\"unsupported_domain_counts_by_pair\":[";
            for(unsigned int u=0;u<84;++u) {if(u)output<<',';output<<'[';
                for(unsigned int v=0;v<84;++v) {if(v)output<<',';output<<unsupported[u*84+v];}output<<']';}
            output<<']';
            if(argc==4) {
                output<<",\"support_rows_bits\":[";
                for(unsigned int i=offsets[c*85];i<offsets[c*85+84];++i) {
                    if(i!=offsets[c*85])output<<',';output<<'"';
                    for(unsigned int v=0;v<84;++v)output<<char('0'+flags[size_t(i)*84+v]);
                    output<<'"';
                }
                output<<']';
            }
            output<<'}';
        }
        output<<"],\"scope\":\"Scores against original domains only. All83other outer vertices checked. Self support bits are true sentinels. No AC iteration, proof, completion or infeasibility claim.\"}\n";
        if(!output) throw std::runtime_error("Failed writing output");
        std::cout<<"CUDA initial support: "<<rows.size()<<" domains, "<<compute<<" s transfer+kernel, "
                 <<kernel_ms/1000.0<<" s kernel, total "
                 <<std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count()<<" s\n";
    } catch(const std::exception& error) { std::cerr<<error.what()<<'\n';return 1; }
    return 0;
}
