//! Dependency-free exact CPU kernels for the saved E0=0 overlap problem.
//! Build: rustc -O -C target-cpu=native acceleration/overlap_cpu.rs -o acceleration/overlap_cpu.exe
//! score CUTS.txt CANDIDATES.txt OUTPUT.json [repeats]
//! walk CANDIDATES.txt OUTPUT.json steps seed
//!
//! C99CUTS1 <count>, then constant, 84*14 alpha, 84*84 beta per cut.
//! C99OVERLAPS1 <count>, then 168 canonical endpoint pairs per candidate.
//! All tokens are whitespace separated. Scores omit upper multipliers.
//! Walk input must have one candidate. Walk samples include the initial and
//! final states and at most about 100 intermediate states. Neither operation
//! constructs a disjoint completion or certifies an SRG.

use std::fmt::Write as FmtWrite;
use std::fs;
use std::hint::black_box;
use std::time::Instant;

const N: usize = 84;
const M: usize = 168;
const MASKS: usize = 128;
type Edge = (usize, usize);
type Result<T> = std::result::Result<T, String>;

fn canonical(u: usize, v: usize) -> Edge {
    if u < v {
        (u, v)
    } else {
        (v, u)
    }
}

struct Geometry {
    labels: [[usize; 2]; N],
    label_bits: [u16; N],
    supports: [u8; N],
    permutations: [[usize; N]; MASKS],
    disjoint: Vec<Edge>,
}

impl Geometry {
    fn new() -> Self {
        let mut labels = [[0; 2]; N];
        let mut label_bits = [0; N];
        let mut supports = [0; N];
        let mut permutations = [[0; N]; MASKS];
        let mut u = 0;
        for a in 0..7 {
            for b in a + 1..7 {
                for s in 0..2 {
                    for t in 0..2 {
                        labels[u] = [2 * a + s, 2 * b + t];
                        label_bits[u] = (1 << labels[u][0]) | (1 << labels[u][1]);
                        supports[u] = (1 << a) | (1 << b);
                        for (mask, permutation) in permutations.iter_mut().enumerate() {
                            permutation[u] =
                                4 * (u / 4) + 2 * (s ^ ((mask >> a) & 1)) + (t ^ ((mask >> b) & 1));
                        }
                        u += 1;
                    }
                }
            }
        }
        let mut disjoint = Vec::new();
        for u in 0..N {
            for v in u + 1..N {
                if supports[u] & supports[v] == 0 {
                    disjoint.push((u, v));
                }
            }
        }
        Self {
            labels,
            label_bits,
            supports,
            permutations,
            disjoint,
        }
    }
}

struct Tokens<'a> {
    values: std::str::SplitWhitespace<'a>,
}

impl<'a> Tokens<'a> {
    fn new(input: &'a str, magic: &str) -> Result<Self> {
        let mut values = input.split_whitespace();
        if values.next() != Some(magic) {
            return Err(format!("expected {magic} header"));
        }
        Ok(Self { values })
    }
    fn number<T: std::str::FromStr>(&mut self, description: &str) -> Result<T> {
        self.values
            .next()
            .ok_or_else(|| format!("missing {description}"))?
            .parse()
            .map_err(|_| format!("invalid {description}"))
    }
    fn finish(&mut self) -> Result<()> {
        if self.values.next().is_some() {
            Err("unexpected trailing input".into())
        } else {
            Ok(())
        }
    }
}

#[derive(Clone)]
struct Graph {
    edges: Vec<Edge>,
    bits: [u128; N],
    rows: [[usize; 4]; N],
}

impl Graph {
    fn new(mut edges: Vec<Edge>, geometry: &Geometry) -> Result<Self> {
        if edges.len() != M {
            return Err(format!("expected {M} edges"));
        }
        edges.sort_unstable();
        let mut bits = [0u128; N];
        for &(u, v) in &edges {
            if !(u < v && v < N) {
                return Err("edge endpoints must satisfy 0 <= u < v < 84".into());
            }
            if (geometry.supports[u] & geometry.supports[v]).count_ones() != 1 {
                return Err(format!("edge ({u},{v}) is not an overlap edge"));
            }
            if bits[u] & (1u128 << v) != 0 {
                return Err(format!("duplicate edge ({u},{v})"));
            }
            bits[u] |= 1u128 << v;
            bits[v] |= 1u128 << u;
        }
        let mut rows = [[0; 4]; N];
        for u in 0..N {
            if bits[u].count_ones() != 4 {
                return Err(format!("vertex {u} must have degree 4"));
            }
            let mut remaining = bits[u];
            for v in &mut rows[u] {
                *v = remaining.trailing_zeros() as usize;
                remaining &= remaining - 1;
            }
        }
        let graph = Self { edges, bits, rows };
        graph.validate_caps(geometry)?;
        Ok(graph)
    }

    fn validate_caps(&self, geometry: &Geometry) -> Result<()> {
        for u in 0..N {
            if !quota_pass(u, self.bits[u], geometry) {
                return Err(format!("label quota violation at vertex {u}"));
            }
            for v in u + 1..N {
                if !cap_pass(u, v, self.bits[u], self.bits[v], geometry) {
                    return Err(format!("partial pair cap violation at ({u},{v})"));
                }
            }
        }
        Ok(())
    }

    // Permutation preserves all validation invariants, so no repeated validation.
    fn transformed(&self, permutation: &[usize; N]) -> Self {
        let mut rows = [[0; 4]; N];
        let mut bits = [0u128; N];
        for u in 0..N {
            for k in 0..4 {
                let v = permutation[self.rows[u][k]];
                rows[permutation[u]][k] = v;
                bits[permutation[u]] |= 1u128 << v;
            }
        }
        let edges = self
            .edges
            .iter()
            .map(|&(u, v)| canonical(permutation[u], permutation[v]))
            .collect();
        Self { edges, bits, rows }
    }
}

fn load_candidates(path: &str, geometry: &Geometry) -> Result<Vec<Graph>> {
    let input = fs::read_to_string(path).map_err(|e| format!("read {path}: {e}"))?;
    let mut tokens = Tokens::new(&input, "C99OVERLAPS1")?;
    let count: usize = tokens.number("candidate count")?;
    if count == 0 || count > 100_000 {
        return Err("candidate count must be in 1..100000".into());
    }
    let mut candidates = Vec::new();
    for i in 0..count {
        let mut edges = Vec::with_capacity(M);
        for _ in 0..M {
            edges.push((
                tokens.number("edge endpoint")?,
                tokens.number("edge endpoint")?,
            ));
        }
        candidates.push(Graph::new(edges, geometry).map_err(|e| format!("candidate {i}: {e}"))?);
    }
    tokens.finish()?;
    Ok(candidates)
}

struct Cut {
    constant: i64,
    beta: Vec<i64>,
    edge_base: Vec<i64>,
}

fn load_cuts(path: &str, geometry: &Geometry) -> Result<Vec<Cut>> {
    let input = fs::read_to_string(path).map_err(|e| format!("read {path}: {e}"))?;
    let mut tokens = Tokens::new(&input, "C99CUTS1")?;
    let count: usize = tokens.number("cut count")?;
    if count == 0 || count > 10_000 {
        return Err("cut count must be in 1..10000".into());
    }
    let mut cuts = Vec::new();
    for index in 0..count {
        let constant: i64 = tokens.number("cut constant")?;
        let alpha: Vec<i64> = (0..N * 14)
            .map(|_| tokens.number("alpha coefficient"))
            .collect::<Result<_>>()?;
        let beta: Vec<i64> = (0..N * N)
            .map(|_| tokens.number("beta coefficient"))
            .collect::<Result<_>>()?;
        for u in 0..N {
            if beta[u * N + u] != 0 {
                return Err(format!("cut {index}: beta diagonal must vanish"));
            }
            for v in u + 1..N {
                if beta[u * N + v] < 0 || beta[u * N + v] != beta[v * N + u] {
                    return Err(format!(
                        "cut {index}: beta must be symmetric and nonnegative"
                    ));
                }
            }
        }
        // Conservative bound covers every intermediate sum below, including
        // negative alpha and constants. Reject instead of silently overflowing.
        let max_alpha = alpha.iter().map(|&x| (x as i128).abs()).max().unwrap();
        let max_beta = beta.iter().map(|&x| x as i128).max().unwrap();
        let bound = (constant as i128).abs()
            + M as i128 * (4 * max_alpha + max_beta)
            + (N * 6) as i128 * max_beta
            + geometry.disjoint.len() as i128 * (4 * max_alpha + 9 * max_beta);
        if bound > i64::MAX as i128 {
            return Err(format!(
                "cut {index}: coefficients exceed safe i64 score bounds"
            ));
        }
        let mut edge_base = vec![0; N * N];
        for u in 0..N {
            for v in u + 1..N {
                let value = alpha[u * 14 + geometry.labels[v][0]]
                    + alpha[u * 14 + geometry.labels[v][1]]
                    + alpha[v * 14 + geometry.labels[u][0]]
                    + alpha[v * 14 + geometry.labels[u][1]]
                    + beta[u * N + v];
                edge_base[u * N + v] = value;
                edge_base[v * N + u] = value;
            }
        }
        cuts.push(Cut {
            constant,
            beta,
            edge_base,
        });
    }
    tokens.finish()?;
    Ok(cuts)
}

fn score(graph: &Graph, cut: &Cut, geometry: &Geometry) -> i64 {
    let mut rhs = cut.constant;
    for &(u, v) in &graph.edges {
        rhs -= cut.edge_base[u * N + v];
    }
    // Each common neighbour contributes exactly one unordered wedge. This
    // replaces 3486 pairwise set intersections with 84 * choose(4,2) lookups.
    for row in &graph.rows {
        for i in 0..4 {
            for j in i + 1..4 {
                rhs -= cut.beta[row[i] * N + row[j]];
            }
        }
    }
    let mut lower = 0;
    for &(u, v) in &geometry.disjoint {
        let mut coefficient = cut.edge_base[u * N + v];
        for &a in &graph.rows[v] {
            coefficient += cut.beta[u * N + a];
        }
        for &a in &graph.rows[u] {
            coefficient += cut.beta[v * N + a];
        }
        lower += coefficient.min(0);
    }
    rhs - lower
}

fn run_score(args: &[String], geometry: &Geometry) -> Result<()> {
    if args.len() != 5 && args.len() != 6 {
        return Err(
            "usage: overlap_cpu score CUTS.txt CANDIDATES.txt OUTPUT.json [repeats]".into(),
        );
    }
    let cuts = load_cuts(&args[2], geometry)?;
    let candidates = load_candidates(&args[3], geometry)?;
    let repeats: usize = if args.len() == 6 {
        args[5].parse().map_err(|_| "invalid repeats")?
    } else {
        1
    };
    if repeats == 0 || repeats > 1_000_000 {
        return Err("repeats must be in 1..1000000".into());
    }
    let entries = candidates
        .len()
        .checked_mul(cuts.len())
        .and_then(|n| n.checked_mul(MASKS))
        .ok_or("score array too large")?;
    if entries > 100_000_000 {
        return Err("score array exceeds 100 million entries".into());
    }
    let evaluations = entries
        .checked_mul(repeats)
        .ok_or("evaluation count overflow")?;
    let mut scores = vec![0i64; entries];
    let start = Instant::now();
    for _ in 0..repeats {
        for (candidate_index, candidate) in candidates.iter().enumerate() {
            for mask in 0..MASKS {
                let image = candidate.transformed(&geometry.permutations[mask]);
                for (cut_index, cut) in cuts.iter().enumerate() {
                    scores[(candidate_index * cuts.len() + cut_index) * MASKS + mask] =
                        score(&image, cut, geometry);
                }
            }
        }
        black_box(&scores);
    }
    let elapsed = start.elapsed().as_secs_f64();
    let mut output = String::from("{\"scores\":[");
    for candidate in 0..candidates.len() {
        if candidate > 0 {
            output.push(',');
        }
        output.push('[');
        for cut in 0..cuts.len() {
            if cut > 0 {
                output.push(',');
            }
            let values = &scores[(candidate * cuts.len() + cut) * MASKS
                ..(candidate * cuts.len() + cut + 1) * MASKS];
            write!(&mut output, "{:?}", values).unwrap();
        }
        output.push(']');
    }
    write!(&mut output, "],\"elapsed_seconds\":{elapsed:.9},\"evaluations\":{evaluations},\"repeats\":{repeats},\"integer_type\":\"i64\",\"includes_upper_multipliers\":false}}\n").unwrap();
    fs::write(&args[4], output).map_err(|e| format!("write {}: {e}", args[4]))?;
    eprintln!(
        "scored {evaluations} cut/sign evaluations in {elapsed:.6} seconds (parsing excluded)"
    );
    Ok(())
}

fn quota_pass(u: usize, mut row: u128, geometry: &Geometry) -> bool {
    let mut counts = [0u8; 14];
    while row != 0 {
        let v = row.trailing_zeros() as usize;
        row &= row - 1;
        for &s in &geometry.labels[v] {
            counts[s] += 1;
        }
    }
    for (s, &count) in counts.iter().enumerate() {
        if geometry.supports[u] & (1 << (s / 2)) != 0 {
            if count != 1 {
                return false;
            }
        } else if count > 2 {
            return false;
        }
    }
    true
}

fn cap_pass(u: usize, v: usize, row_u: u128, row_v: u128, geometry: &Geometry) -> bool {
    let common = (row_u & row_v).count_ones()
        + (geometry.label_bits[u] & geometry.label_bits[v]).count_ones();
    common <= if row_u & (1u128 << v) != 0 { 1 } else { 2 }
}

#[derive(Clone, Copy)]
struct Trade {
    removed: [Edge; 2],
    added: [Edge; 2],
}

#[derive(Default)]
struct Counters {
    disjoint: usize,
    overlap: usize,
    block: usize,
    quota: usize,
    caps: usize,
}

impl Counters {
    fn json(&self) -> String {
        format!("{{\"disjoint_edge_pairs\":{},\"overlap_and_absence_pass\":{},\"block_total_pass\":{},\"label_quota_pass\":{},\"all_partial_caps_pass\":{}}}",
            self.disjoint, self.overlap, self.block, self.quota, self.caps)
    }
}

fn block_key(edges: &[Edge; 2]) -> [Edge; 2] {
    let mut blocks = [
        canonical(edges[0].0 / 4, edges[0].1 / 4),
        canonical(edges[1].0 / 4, edges[1].1 / 4),
    ];
    if blocks[0] > blocks[1] {
        blocks.swap(0, 1);
    }
    blocks
}

fn legal_trades(graph: &Graph, geometry: &Geometry) -> (Counters, Vec<Trade>) {
    let mut counters = Counters::default();
    let mut trades = Vec::new();
    for i in 0..M {
        let (a, b) = graph.edges[i];
        for j in i + 1..M {
            let (c, d) = graph.edges[j];
            if a == c || a == d || b == c || b == d {
                continue;
            }
            counters.disjoint += 1;
            let removed = [(a, b), (c, d)];
            let old_blocks = block_key(&removed);
            for added in [
                [canonical(a, c), canonical(b, d)],
                [canonical(a, d), canonical(b, c)],
            ] {
                if added.iter().any(|&(u, v)| {
                    graph.bits[u] & (1u128 << v) != 0
                        || (geometry.supports[u] & geometry.supports[v]).count_ones() != 1
                }) {
                    continue;
                }
                counters.overlap += 1;
                if block_key(&added) != old_blocks {
                    continue;
                }
                counters.block += 1;
                let changed = [a, b, c, d];
                let mut rows = [
                    graph.bits[a] ^ (1u128 << b),
                    graph.bits[b] ^ (1u128 << a),
                    graph.bits[c] ^ (1u128 << d),
                    graph.bits[d] ^ (1u128 << c),
                ];
                for &(u, v) in &added {
                    for k in 0..4 {
                        if changed[k] == u {
                            rows[k] |= 1u128 << v;
                        }
                        if changed[k] == v {
                            rows[k] |= 1u128 << u;
                        }
                    }
                }
                if (0..4).any(|k| !quota_pass(changed[k], rows[k], geometry)) {
                    continue;
                }
                counters.quota += 1;
                let mut valid = true;
                'caps: for k in 0..4 {
                    let u = changed[k];
                    for v in 0..N {
                        if v == u {
                            continue;
                        }
                        let row_v = match changed.iter().position(|&x| x == v) {
                            Some(l) => rows[l],
                            None => graph.bits[v],
                        };
                        if !cap_pass(u, v, rows[k], row_v, geometry) {
                            valid = false;
                            break 'caps;
                        }
                    }
                }
                if !valid {
                    continue;
                }
                counters.caps += 1;
                trades.push(Trade { removed, added });
            }
        }
    }
    (counters, trades)
}

fn next_random(state: &mut u64) -> u64 {
    // SplitMix64 has specified wrapping arithmetic, including for seed zero.
    *state = state.wrapping_add(0x9e3779b97f4a7c15);
    let mut z = *state;
    z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
    z ^ (z >> 31)
}

fn append_edges(output: &mut String, edges: &[Edge]) {
    output.push('[');
    for (i, &(u, v)) in edges.iter().enumerate() {
        if i > 0 {
            output.push(',');
        }
        write!(output, "[{u},{v}]").unwrap();
    }
    output.push(']');
}

fn run_walk(args: &[String], geometry: &Geometry) -> Result<()> {
    if args.len() != 6 {
        return Err("usage: overlap_cpu walk CANDIDATES.txt OUTPUT.json steps seed".into());
    }
    let mut candidates = load_candidates(&args[2], geometry)?;
    if candidates.len() != 1 {
        return Err("walk requires exactly one initial candidate".into());
    }
    let steps: usize = args[4].parse().map_err(|_| "invalid step count")?;
    if steps > 1_000_000 {
        return Err("step count must be at most 1000000".into());
    }
    let seed: u64 = args[5].parse().map_err(|_| "invalid u64 seed")?;
    let mut random_state = seed;
    let stride = (steps / 100).max(1);
    let mut graph = candidates.pop().unwrap();
    let mut samples = vec![graph.edges.clone()];
    let mut candidate_steps = vec![0];
    let mut trace = Vec::new();
    let start = Instant::now();
    let (initial_counters, mut choices) = legal_trades(&graph, geometry);
    let initial_legal_trades = choices.len();
    let mut completed = 0;
    for step in 1..=steps {
        if choices.is_empty() {
            break;
        }
        let trade = choices[(next_random(&mut random_state) % choices.len() as u64) as usize];
        trace.push((choices.len(), trade));
        let mut edges: Vec<_> = graph
            .edges
            .iter()
            .copied()
            .filter(|edge| !trade.removed.contains(edge))
            .collect();
        edges.extend(trade.added);
        // The full validator is inexpensive relative to enumeration and makes
        // a broken incremental invariant an explicit error at the exact step.
        graph = Graph::new(edges, geometry).map_err(|e| format!("walk step {step}: {e}"))?;
        completed = step;
        if step % stride == 0 || step == steps {
            candidate_steps.push(step);
            samples.push(graph.edges.clone());
        }
        if step < steps {
            choices = legal_trades(&graph, geometry).1;
        }
    }
    if *candidate_steps.last().unwrap() != completed {
        candidate_steps.push(completed);
        samples.push(graph.edges.clone());
    }
    let elapsed = start.elapsed().as_secs_f64();
    let mut output = String::from("{\"overlap_candidates\":[");
    for (i, sample) in samples.iter().enumerate() {
        if i > 0 {
            output.push(',');
        }
        append_edges(&mut output, sample);
    }
    write!(&mut output, "],\"candidate_steps\":{:?},\"steps\":{},\"completed_steps\":{},\"seed\":{},\"sample_stride\":{},\"initial_legal_trades\":{},\"initial_trade_counters\":{},\"elapsed_seconds\":{:.9},\"trade_trace\":[",
        candidate_steps, steps, completed, seed, stride, initial_legal_trades, initial_counters.json(), elapsed).unwrap();
    for (i, (count, trade)) in trace.iter().enumerate() {
        if i > 0 {
            output.push(',');
        }
        write!(
            &mut output,
            "{{\"step\":{},\"legal_trades\":{},\"removed\":",
            i + 1,
            count
        )
        .unwrap();
        append_edges(&mut output, &trade.removed);
        output.push_str(",\"added\":");
        append_edges(&mut output, &trade.added);
        output.push('}');
    }
    output.push_str("],\"scope\":\"Bounded seeded local walk preserving overlap block totals, degree four, label quotas and partial pair caps. No disjoint completion or SRG certificate.\"}\n");
    fs::write(&args[3], output).map_err(|e| format!("write {}: {e}", args[3]))?;
    eprintln!("walked {completed}/{steps} trades in {elapsed:.6} seconds (initial legal trades: {initial_legal_trades})");
    Ok(())
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let geometry = Geometry::new();
    let result = match args.get(1).map(String::as_str) {
        Some("score") => run_score(&args, &geometry),
        Some("walk") => run_walk(&args, &geometry),
        _ => Err("usage: overlap_cpu score CUTS.txt CANDIDATES.txt OUTPUT.json [repeats]\n       overlap_cpu walk CANDIDATES.txt OUTPUT.json steps seed".into()),
    };
    if let Err(message) = result {
        eprintln!("error: {message}");
        std::process::exit(1);
    }
}
