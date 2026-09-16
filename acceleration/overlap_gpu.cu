// Exact CUDA evaluator for scratch_next_overlap_cut_bank.evaluate(include_upper=False).
// One block evaluates one candidate/cut/root-sign-mask. No floating-point scores.
#include <cuda_runtime.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using I64 = long long;
constexpr int N = 84, DEGREE = 4, MASKS = 128, EDGES = 168, FREE_EDGES = 1680;
constexpr int THREADS = 256;
__constant__ unsigned char sign_permutations[MASKS * N];
__constant__ unsigned char free_u[FREE_EDGES], free_v[FREE_EDGES];

void check(cudaError_t error, const char* operation) {
    if (error != cudaSuccess)
        throw std::runtime_error(std::string(operation) + ": " + cudaGetErrorString(error));
}
#define CUDA(operation) check((operation), #operation)

template<class T> struct DeviceBuffer {
    T* ptr = nullptr;
    explicit DeviceBuffer(size_t count) { CUDA(cudaMalloc(&ptr, count * sizeof(T))); }
    ~DeviceBuffer() { if (ptr) cudaFree(ptr); }
    DeviceBuffer(const DeviceBuffer&) = delete;
    DeviceBuffer& operator=(const DeviceBuffer&) = delete;
};

struct Cut {
    I64 constant;
    std::array<I64, N * 14> alpha;
    std::array<I64, N * N> beta;
};

template<class T> T read_number(std::istream& stream, const char* field) {
    T value;
    if (!(stream >> value)) throw std::runtime_error(std::string("Missing or invalid ") + field);
    return value;
}

void require_end(std::istream& stream) {
    std::string extra;
    if (stream >> extra) throw std::runtime_error("Unexpected trailing input");
}

__global__ void evaluate(const unsigned char* neighbors, const I64* constants,
                         const I64* bases, const I64* betas, int cut_count,
                         I64* scores) {
    const size_t job = blockIdx.x;
    const int mask = job % MASKS;
    const int cut = (job / MASKS) % cut_count;
    const size_t candidate = job / (MASKS * cut_count);
    const unsigned char* permutation = sign_permutations + mask * N;
    const unsigned char* source = neighbors + candidate * N * DEGREE;
    const I64* base = bases + cut * N * N;
    const I64* beta = betas + cut * N * N;
    __shared__ unsigned char row[N * DEGREE];
    __shared__ I64 partial[THREADS];
    for (int i = threadIdx.x; i < N * DEGREE; i += THREADS) {
        const int u = i / DEGREE;
        row[i] = permutation[source[permutation[u] * DEGREE + i % DEGREE]];
    }
    __syncthreads();

    I64 total = 0;
    // Undirected known edges, each once.
    for (int i = threadIdx.x; i < N * DEGREE; i += THREADS) {
        const int u = i / DEGREE, v = row[i];
        if (u < v) total -= base[u * N + v];
    }
    // A common neighbor contributes one wedge: 84 * choose(4,2) = 504.
    for (int u = threadIdx.x; u < N; u += THREADS) {
        for (int a = 0; a < DEGREE; ++a)
            for (int b = a + 1; b < DEGREE; ++b)
                total -= beta[row[u * DEGREE + a] * N + row[u * DEGREE + b]];
    }
    for (int e = threadIdx.x; e < FREE_EDGES; e += THREADS) {
        const int u = free_u[e], v = free_v[e];
        I64 coefficient = base[u * N + v];
        #pragma unroll
        for (int j = 0; j < DEGREE; ++j)
            coefficient += beta[u * N + row[v * DEGREE + j]]
                         + beta[v * N + row[u * DEGREE + j]];
        if (coefficient < 0) total -= coefficient;
    }
    partial[threadIdx.x] = total;
    __syncthreads();
    for (int stride = THREADS / 2; stride; stride /= 2) {
        if (threadIdx.x < stride) partial[threadIdx.x] += partial[threadIdx.x + stride];
        __syncthreads();
    }
    if (threadIdx.x == 0) scores[job] = constants[cut] + partial[0];
}

int main(int argc, char** argv) {
    try {
        if (argc < 4 || argc > 5)
            throw std::runtime_error("Usage: overlap_gpu CUTS.txt CANDIDATES.txt OUTPUT.json [repeats]");
        int repeats = 1;
        if (argc == 5) {
            size_t consumed = 0;
            repeats = std::stoi(argv[4], &consumed);
            if (consumed != std::string(argv[4]).size() || repeats < 1)
                throw std::runtime_error("repeats must be a positive integer");
        }
        const auto process_start = std::chrono::steady_clock::now();
        std::array<std::array<int, 2>, N> labels{}, groups{};
        int vertex = 0;
        for (int a = 0; a < 7; ++a) for (int b = a + 1; b < 7; ++b)
            for (int s = 0; s < 2; ++s) for (int t = 0; t < 2; ++t) {
                labels[vertex] = {2*a+s, 2*b+t};
                groups[vertex++] = {a,b};
            }
        auto support_intersection = [&](int u, int v) {
            int count = 0;
            for (int a : groups[u]) for (int b : groups[v]) count += a == b;
            return count;
        };
        std::array<unsigned char, MASKS * N> permutations{};
        for (int mask = 0; mask < MASKS; ++mask) for (int u = 0; u < N; ++u) {
            const int s = (u % 4) / 2, t = u % 2;
            permutations[mask*N+u] = 4*(u/4) + 2*(s ^ ((mask >> groups[u][0]) & 1))
                                                       + (t ^ ((mask >> groups[u][1]) & 1));
        }
        std::vector<unsigned char> free_us, free_vs;
        for (int u = 0; u < N; ++u) for (int v = u+1; v < N; ++v)
            if (!support_intersection(u,v)) { free_us.push_back(u); free_vs.push_back(v); }
        if (free_us.size() != FREE_EDGES) throw std::runtime_error("Internal free edge count");

        std::ifstream cut_input(argv[1]);
        std::string magic;
        cut_input >> magic;
        if (magic != "C99CUTS1") throw std::runtime_error("Invalid cuts header");
        const int cut_count = read_number<int>(cut_input, "cut count");
        if (cut_count < 1 || cut_count > 10000) throw std::runtime_error("Invalid cut count");
        std::vector<I64> constants, bases, betas;
        for (int k = 0; k < cut_count; ++k) {
            Cut cut{};
            cut.constant = read_number<I64>(cut_input, "constant");
            long double max_alpha = 0, max_beta = 0;
            for (I64& value : cut.alpha) {
                value = read_number<I64>(cut_input, "alpha");
                max_alpha = std::max(max_alpha, std::fabs(static_cast<long double>(value)));
            }
            for (I64& value : cut.beta) {
                value = read_number<I64>(cut_input, "beta");
                if (value < 0) throw std::runtime_error("Negative beta multiplier");
                max_beta = std::max(max_beta, static_cast<long double>(value));
            }
            for (int u = 0; u < N; ++u) for (int v = 0; v < N; ++v) {
                if (cut.beta[u*N+v] != cut.beta[v*N+u] || (u == v && cut.beta[u*N+v]))
                    throw std::runtime_error("Beta must be symmetric with zero diagonal");
            }
            // Bounds every partial sum, box coefficient and final score. Reject
            // huge coefficients instead of silently overflowing signed arithmetic.
            const long double bound = std::fabs(static_cast<long double>(cut.constant))
                                    + 7392.0L * max_alpha + 15792.0L * max_beta;
            // 2^62 leaves an exact safety margin even if long double is binary64.
            if (bound >= 4611686018427387904.0L)
                throw std::runtime_error("Cut coefficients exceed conservative int64 safety bound");
            constants.push_back(cut.constant);
            betas.insert(betas.end(), cut.beta.begin(), cut.beta.end());
            for (int u = 0; u < N; ++u) for (int v = 0; v < N; ++v)
                bases.push_back(cut.alpha[u*14+labels[v][0]] + cut.alpha[u*14+labels[v][1]]
                              + cut.alpha[v*14+labels[u][0]] + cut.alpha[v*14+labels[u][1]]
                              + cut.beta[u*N+v]);
        }
        require_end(cut_input);
        std::ifstream candidate_input(argv[2]);
        candidate_input >> magic;
        if (magic != "C99OVERLAPS1") throw std::runtime_error("Invalid candidates header");
        const int candidate_count = read_number<int>(candidate_input, "candidate count");
        if (candidate_count < 1) throw std::runtime_error("Candidate count must be positive");
        const uint64_t job_count = uint64_t(candidate_count) * cut_count * MASKS;
        if (job_count > 2147483647ULL) throw std::runtime_error("Too many GPU blocks; split the batch");
        std::vector<unsigned char> neighbors;
        for (int c = 0; c < candidate_count; ++c) {
            std::array<unsigned char, N*DEGREE> rows{};
            std::array<int, N> degree{};
            std::array<bool, N*N> seen{};
            for (int e = 0; e < EDGES; ++e) {
                const int u = read_number<int>(candidate_input, "edge endpoint");
                const int v = read_number<int>(candidate_input, "edge endpoint");
                if (u < 0 || v >= N || u >= v) throw std::runtime_error("Invalid canonical edge endpoints");
                if (support_intersection(u,v) != 1) throw std::runtime_error("Edge must join supports intersecting once");
                if (seen[u*N+v]) throw std::runtime_error("Duplicate edge");
                seen[u*N+v] = true;
                if (degree[u] >= DEGREE || degree[v] >= DEGREE) throw std::runtime_error("Overlap degree exceeds four");
                rows[u*DEGREE + degree[u]++] = v;
                rows[v*DEGREE + degree[v]++] = u;
            }
            for (int d : degree) if (d != DEGREE) throw std::runtime_error("Every overlap degree must be four");
            neighbors.insert(neighbors.end(), rows.begin(), rows.end());
        }
        require_end(candidate_input);

        CUDA(cudaSetDevice(0));
        cudaDeviceProp device{};
        CUDA(cudaGetDeviceProperties(&device, 0));
        DeviceBuffer<unsigned char> d_neighbors(neighbors.size());
        DeviceBuffer<I64> d_constants(constants.size()), d_bases(bases.size()), d_betas(betas.size());
        DeviceBuffer<I64> d_scores(static_cast<size_t>(job_count));
        std::vector<I64> scores(static_cast<size_t>(job_count));
        cudaEvent_t start_event, stop_event;
        CUDA(cudaEventCreate(&start_event));
        CUDA(cudaEventCreate(&stop_event));
        const auto timed_start = std::chrono::steady_clock::now();
        CUDA(cudaMemcpyToSymbol(sign_permutations, permutations.data(), permutations.size()));
        CUDA(cudaMemcpyToSymbol(free_u, free_us.data(), free_us.size()));
        CUDA(cudaMemcpyToSymbol(free_v, free_vs.data(), free_vs.size()));
        CUDA(cudaMemcpy(d_neighbors.ptr, neighbors.data(), neighbors.size(), cudaMemcpyHostToDevice));
        CUDA(cudaMemcpy(d_constants.ptr, constants.data(), constants.size()*sizeof(I64), cudaMemcpyHostToDevice));
        CUDA(cudaMemcpy(d_bases.ptr, bases.data(), bases.size()*sizeof(I64), cudaMemcpyHostToDevice));
        CUDA(cudaMemcpy(d_betas.ptr, betas.data(), betas.size()*sizeof(I64), cudaMemcpyHostToDevice));
        CUDA(cudaEventRecord(start_event));
        for (int repeat = 0; repeat < repeats; ++repeat) {
            evaluate<<<static_cast<unsigned int>(job_count), THREADS>>>(d_neighbors.ptr, d_constants.ptr,
                      d_bases.ptr, d_betas.ptr, cut_count, d_scores.ptr);
            CUDA(cudaGetLastError());
        }
        CUDA(cudaEventRecord(stop_event));
        CUDA(cudaEventSynchronize(stop_event));
        float kernel_ms = 0;
        CUDA(cudaEventElapsedTime(&kernel_ms, start_event, stop_event));
        CUDA(cudaMemcpy(scores.data(), d_scores.ptr, scores.size()*sizeof(I64), cudaMemcpyDeviceToHost));
        const double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now()-timed_start).count();
        const double setup_elapsed = std::chrono::duration<double>(timed_start-process_start).count();
        CUDA(cudaEventDestroy(start_event));
        CUDA(cudaEventDestroy(stop_event));
        std::ofstream output(argv[3]);
        if (!output) throw std::runtime_error("Cannot open output file");
        output << std::setprecision(12) << "{\"backend\":\"cuda\",\"device\":\"" << device.name
               << "\",\"elapsed_seconds\":" << elapsed << ",\"kernel_seconds\":" << kernel_ms/1000.0
               << ",\"setup_seconds\":" << setup_elapsed
               << ",\"evaluations\":" << job_count*repeats << ",\"repeats\":" << repeats
               << ",\"candidate_count\":" << candidate_count << ",\"cut_count\":" << cut_count
               << ",\"masks\":128,\"include_upper_multipliers\":false,\"scores\":[";
        size_t offset = 0;
        for (int c = 0; c < candidate_count; ++c) {
            if (c) output << ',';
            output << '[';
            for (int k = 0; k < cut_count; ++k) {
                if (k) output << ',';
                output << '[';
                for (int mask = 0; mask < MASKS; ++mask) {
                    if (mask) output << ',';
                    output << scores[offset++];
                }
                output << ']';
            }
            output << ']';
        }
        output << "]}\n";
        if (!output) throw std::runtime_error("Failed writing output");
        std::cout << "CUDA " << device.name << ": " << job_count*repeats << " evaluations, "
                  << elapsed << " s transfers+kernel, " << kernel_ms/1000.0 << " s kernel\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "overlap_gpu: " << error.what() << '\n';
        return 1;
    }
}
