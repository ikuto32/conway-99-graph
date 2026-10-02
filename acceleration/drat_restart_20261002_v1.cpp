// Candidate active-clause extraction only. This program checks syntax/state,
// never RAT/RUP validity or equisatisfiability. Preserve all original artifacts.
#include <algorithm>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

static bool space(char c) { return c == ' ' || c == '\t' || c == '\r' || c == '\n'; }
static void require(bool value, const std::string &reason) { if (!value) throw std::runtime_error(reason); }

struct Clause {
    uint64_t offset, copies;
    uint32_t size, next;
};
static constexpr uint32_t NONE = std::numeric_limits<uint32_t>::max();

struct Extractor {
    std::vector<int32_t> literals;
    std::vector<Clause> clauses;
    std::unordered_map<uint64_t, uint32_t> heads;
    uint64_t variables = 0, original_clauses = 0, original_literals = 0;
    uint64_t active_copies = 0, additions = 0, deletions = 0, effective_deletions = 0;
    uint64_t missing_deletions = 0, ignored_small_deletions = 0, duplicate_literals = 0;
    uint64_t duplicate_clause_additions = 0, tautology_records = 0;
    uint64_t processed_lines = 0, retained_prefix_bytes = 0, proof_bytes = 0, trailing_dropped_bytes = 0;
    bool appended_boundary_newline = false;
    double seconds;
    Clock::time_point start;
    fs::path output;

    Extractor(double allowance, fs::path directory) : seconds(allowance), start(Clock::now()), output(std::move(directory)) {}

    double elapsed() const { return std::chrono::duration<double>(Clock::now()-start).count(); }
    void deadline() const { require(elapsed() < seconds, "not completed within the allocated budget"); }
    void progress() {
        deadline();
        fs::path temporary = output/"progress.json.tmp";
        std::ofstream stream(temporary, std::ios::binary);
        stream << "{\"phase\":\"extracting_active_multiset\",\"processed_lines\":" << processed_lines
               << ",\"active_clause_occurrences\":" << active_copies << ",\"unique_recorded_clauses\":" << clauses.size()
               << ",\"stored_literals\":" << literals.size() << ",\"elapsed_seconds\":" << elapsed() << "}\n";
        stream.close();
        fs::rename(temporary, output/"progress.json");
    }

    std::vector<int32_t> parse_clause(const std::string &line, size_t offset) {
        std::vector<int32_t> result;
        bool terminated = false;
        const char *begin = line.data(), *end = begin+line.size(), *current = begin+offset;
        while (current < end) {
            while (current < end && space(*current)) ++current;
            if (current == end) break;
            int32_t literal = 0;
            auto parsed = std::from_chars(current, end, literal);
            require(parsed.ec == std::errc() && parsed.ptr != current &&
                    (parsed.ptr == end || space(*parsed.ptr)), "invalid canonical DRAT/DIMACS integer");
            current = parsed.ptr;
            require(!terminated, "tokens after clause terminator");
            if (literal == 0) { terminated = true; continue; }
            require(literal != std::numeric_limits<int32_t>::min(), "literal integer overflow");
            int64_t absolute = literal < 0 ? -int64_t(literal) : literal;
            require(uint64_t(absolute) <= variables, "proof introduces variable outside frozen DIMACS universe");
            result.push_back(literal);
            require(result.size() < 16*1024*1024, "single clause exceeds explicit parser literal guard");
        }
        require(terminated, "complete line lacks clause terminator");
        std::sort(result.begin(), result.end());
        auto unique = std::unique(result.begin(), result.end());
        duplicate_literals += uint64_t(result.end()-unique);
        result.erase(unique, result.end());
        bool tautology = false;
        for (int32_t literal : result) {
            if (literal < 0 && std::binary_search(result.begin(), result.end(), -literal)) { tautology = true; break; }
        }
        tautology_records += tautology ? 1 : 0;
        return result;
    }

    uint64_t hash(const std::vector<int32_t> &clause) const {
        uint64_t value = 1469598103934665603ULL;
        for (int32_t literal : clause) {
            uint32_t bits = uint32_t(literal);
            for (unsigned shift = 0; shift < 32; shift += 8) { value ^= (bits >> shift) & 255U; value *= 1099511628211ULL; }
        }
        value ^= clause.size();
        return value;
    }

    uint32_t locate(const std::vector<int32_t> &clause, uint64_t identity) const {
        auto head = heads.find(identity);
        if (head == heads.end()) return NONE;
        uint32_t index = head->second;
        while (index != NONE) {
            const Clause &candidate = clauses[index];
            if (candidate.size == clause.size() &&
                std::equal(clause.begin(), clause.end(), literals.begin()+candidate.offset)) return index;
            index = candidate.next;
        }
        return NONE;
    }

    void add(const std::vector<int32_t> &clause) {
        uint64_t identity = hash(clause);
        uint32_t index = locate(clause, identity);
        if (index == NONE) {
            require(clauses.size() < NONE, "unique-clause index overflow");
            auto old = heads.find(identity);
            index = uint32_t(clauses.size());
            clauses.push_back(Clause{literals.size(), 0, uint32_t(clause.size()), old == heads.end() ? NONE : old->second});
            literals.insert(literals.end(), clause.begin(), clause.end());
            heads[identity] = index;
        } else { ++duplicate_clause_additions; }
        require(clauses[index].copies != std::numeric_limits<uint64_t>::max(), "clause multiplicity overflow");
        ++clauses[index].copies;
        ++active_copies;
    }

    void remove(const std::vector<int32_t> &clause) {
        ++deletions;
        // Match exact pinned default BACKWARD_UNSAT parser profile. The raw
        // prefix retains these instructions; the checker ignores them too.
        if (clause.size() <= 1) { ++ignored_small_deletions; return; }
        uint32_t index = locate(clause, hash(clause));
        if (index == NONE || clauses[index].copies == 0) { ++missing_deletions; return; }
        --clauses[index].copies;
        --active_copies;
        ++effective_deletions;
    }

    void initial(const fs::path &path) {
        std::ifstream stream(path, std::ios::binary);
        require(bool(stream), "cannot open original CNF");
        std::string line;
        require(bool(std::getline(stream, line)), "missing original DIMACS header");
        require(line.rfind("p cnf ", 0) == 0, "canonical single DIMACS header required");
        size_t pos = 6;
        auto variable = std::from_chars(line.data()+pos, line.data()+line.size(), variables);
        require(variable.ec == std::errc() && variable.ptr < line.data()+line.size() && space(*variable.ptr), "DIMACS variables");
        const char *current = variable.ptr;
        while (current < line.data()+line.size() && space(*current)) ++current;
        auto count = std::from_chars(current, line.data()+line.size(), original_clauses);
        require(count.ec == std::errc() && variables > 0 && variables <= uint64_t(std::numeric_limits<int32_t>::max()), "DIMACS dimensions");
        current = count.ptr;
        while (current < line.data()+line.size() && space(*current)) ++current;
        require(current == line.data()+line.size(), "extra DIMACS header data");
        require(original_clauses < NONE, "original clause count index bound");
        heads.reserve(size_t(original_clauses));
        clauses.reserve(size_t(original_clauses));
        uint64_t read_clauses = 0;
        while (std::getline(stream, line)) {
            ++processed_lines;
            if ((processed_lines & 65535U) == 0) progress();
            require(line.size() < 128*1024*1024, "DIMACS line exceeds parser guard");
            if (line.empty() || line[0] == 'c') continue;
            auto clause = parse_clause(line, 0);
            original_literals += clause.size();
            add(clause);
            ++read_clauses;
        }
        require(stream.eof() && read_clauses == original_clauses, "all frozen original clauses parsed exactly");
        progress();
    }

    void prefix(const fs::path &path) {
        std::ifstream stream(path, std::ios::binary);
        require(bool(stream), "cannot open original partial DRAT");
        proof_bytes = fs::file_size(path);
        std::ofstream retained(output/"retained_prefix.drat", std::ios::binary);
        require(bool(retained), "cannot create retained prefix");
        std::string line;
        uint64_t consumed = 0;
        while (std::getline(stream, line)) {
            ++processed_lines;
            if ((processed_lines & 65535U) == 0) progress();
            require(line.size() < 128*1024*1024, "DRAT line exceeds parser guard");
            const bool has_newline = consumed+line.size() < proof_bytes;
            const uint64_t bytes = line.size()+(has_newline ? 1U : 0U);
            size_t first = 0;
            while (first < line.size() && space(line[first])) ++first;
            bool deletion = false, blank_or_comment = first == line.size() || line[first] == 'c';
            if (!blank_or_comment && line[first] == 'd') {
                if (!has_newline && first+1 == line.size()) {
                    trailing_dropped_bytes = bytes;
                    consumed += bytes;
                    break;
                }
                require(first+1 < line.size() && space(line[first+1]), "invalid deletion prefix");
                deletion = true;
                ++first;
            }
            // Only an unterminated final raw record may be dropped. A complete
            // malformed record, even the final one, fails closed.
            if (!has_newline && !blank_or_comment) {
                size_t end = line.size();
                while (end > first && space(line[end-1])) --end;
                size_t begin = end;
                while (begin > first && !space(line[begin-1])) --begin;
                if (line.substr(begin, end-begin) != "0") {
                    const char *current = line.data()+first, *limit = line.data()+line.size();
                    while (current < limit) {
                        while (current < limit && space(*current)) ++current;
                        if (current == limit) break;
                        int32_t literal = 0;
                        auto parsed = std::from_chars(current, limit, literal);
                        require(parsed.ec == std::errc() && parsed.ptr != current &&
                                (parsed.ptr == limit || space(*parsed.ptr)), "malformed final raw record");
                        require(literal != 0, "extra token after final raw record terminator");
                        require(literal != std::numeric_limits<int32_t>::min(), "final raw integer overflow");
                        int64_t absolute = literal < 0 ? -int64_t(literal) : literal;
                        require(uint64_t(absolute) <= variables, "final raw record uses extra variable");
                        current = parsed.ptr;
                    }
                    trailing_dropped_bytes = bytes;
                    consumed += bytes;
                    break;
                }
            }
            if (!blank_or_comment) {
                auto clause = parse_clause(line, first);
                if (deletion) remove(clause); else { ++additions; add(clause); }
            }
            retained.write(line.data(), std::streamsize(line.size()));
            retained.put('\n');
            retained_prefix_bytes += bytes;
            if (!has_newline) appended_boundary_newline = true;
            consumed += bytes;
        }
        require(stream.eof() && consumed == proof_bytes, "exact entire proof byte accounting");
        retained.close();
        require(bool(retained), "retained proof write failure");
        progress();
    }

    void emit() {
        deadline();
        std::ofstream formula(output/"restart.cnf", std::ios::binary);
        formula << "p cnf " << variables << ' ' << active_copies << '\n';
        uint64_t emitted = 0;
        for (const Clause &clause : clauses) {
            for (uint64_t copy = 0; copy < clause.copies; ++copy) {
                if ((emitted & 65535U) == 0) deadline();
                for (uint32_t i = 0; i < clause.size; ++i) formula << literals[clause.offset+i] << ' ';
                formula << "0\n";
                ++emitted;
            }
        }
        formula.close();
        require(bool(formula) && emitted == active_copies, "complete restart formula write");
        std::ofstream summary(output/"parser_summary.json", std::ios::binary);
        summary << "{\"schema\":\"DRAT_ACTIVE_MULTISET_PARSER_V1\",\"status\":\"CANDIDATE_RESTART_STATE\","
          << "\"profile\":\"PINNED_BACKWARD_UNSAT_SINGLE_COPY_IGNORE_SMALL_DELETE_V1\","
          << "\"variables\":" << variables << ",\"original_clauses\":" << original_clauses
          << ",\"original_literals\":" << original_literals << ",\"active_clause_occurrences\":" << active_copies
          << ",\"unique_recorded_clauses\":" << clauses.size() << ",\"stored_literals\":" << literals.size()
          << ",\"proof_additions\":" << additions << ",\"proof_deletions\":" << deletions
          << ",\"effective_deletions\":" << effective_deletions << ",\"missing_deletions\":" << missing_deletions
          << ",\"ignored_small_deletions\":" << ignored_small_deletions << ",\"duplicate_literals_normalized\":" << duplicate_literals
          << ",\"duplicate_clause_additions\":" << duplicate_clause_additions << ",\"tautology_records_retained\":" << tautology_records
          << ",\"original_proof_bytes\":" << proof_bytes << ",\"retained_original_bytes\":" << retained_prefix_bytes
          << ",\"trailing_dropped_bytes\":" << trailing_dropped_bytes << ",\"appended_boundary_newline\":" << (appended_boundary_newline?"true":"false")
          << ",\"elapsed_seconds\":" << elapsed() << ",\"rat_rup_checked\":false,\"equisatisfiability_asserted\":false,"
          << "\"target_resolution\":false}\n";
        summary.close();
        require(bool(summary), "parser summary write failure");
    }
};

int main(int argc, char **argv) {
    fs::path output;
    try {
        require(argc == 9, "usage: parser --cnf FILE --proof FILE --out NEWDIR --seconds POSITIVE");
        std::unordered_map<std::string, std::string> options;
        for (int i = 1; i < argc; i += 2) require(options.emplace(argv[i], argv[i+1]).second, "duplicate option");
        require(options.count("--cnf") && options.count("--proof") && options.count("--out") && options.count("--seconds"), "exact options");
        size_t used = 0;
        double seconds = std::stod(options.at("--seconds"), &used);
        require(used == options.at("--seconds").size() && seconds > 0 && seconds <= 21600, "finite parser allocation");
        output = options.at("--out");
        require(fs::create_directory(output), "new immutable parser output directory required");
        Extractor parser(seconds, output);
        parser.initial(options.at("--cnf"));
        parser.prefix(options.at("--proof"));
        parser.emit();
        std::cout << "CANDIDATE_RESTART_STATE\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        if (!output.empty() && fs::exists(output)) {
            std::ofstream failure(output/"parser_failure.txt", std::ios::binary);
            failure << error.what() << '\n';
        }
        return 2;
    }
}
