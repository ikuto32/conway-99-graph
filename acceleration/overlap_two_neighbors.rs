//! Bounded, deterministic length-two overlap-trade proposals; no AC filtering.
//! Geometry derived from frozen overlap_neighbors.rs SHA256
//! 2c7fa9f6c7f4925135880d78c0e257e56c797615a8e92e50491a19ddd2c8b17d.
//! rustc -O -C target-cpu=native acceleration/overlap_two_neighbors.rs -o acceleration/build/overlap_two_neighbors.exe
//! overlap_two_neighbors INPUT.txt OUTPUT.json [sample_limit=128] [seed=0]
//! The sample is neither uniform nor exhaustive over length-two paths.

use std::collections::BTreeSet;
use std::fmt::Write as FmtWrite;
use std::{fs, time::Instant};

type Edge = (usize, usize);
type Rows = [u128; 99];
#[derive(Clone, Copy)]
struct Trade { removed: [Edge; 2], added: [Edge; 2] }
struct Graph { rows: Rows, edges: Vec<Edge> }

fn edge(a: usize, b: usize) -> Edge { (a.min(b), a.max(b)) }
fn add(rows: &mut Rows, u: usize, v: usize) {
    rows[u] |= 1u128 << v;
    rows[v] |= 1u128 << u;
}
fn random(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9e3779b97f4a7c15);
    let mut x = *state;
    x = (x ^ (x >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27)).wrapping_mul(0x94d049bb133111eb);
    x ^ (x >> 31)
}
fn shuffled_indices(count: usize, state: &mut u64) -> Vec<usize> {
    let mut indices: Vec<_> = (0..count).collect();
    for i in (1..count).rev() {
        let j = (random(state) % (i as u64 + 1)) as usize;
        indices.swap(i, j);
    }
    indices
}
fn pair_ok(rows: &Rows, u: usize, v: usize) -> bool {
    (rows[u] & rows[v]).count_ones() <= 2 - ((rows[u] >> v) & 1) as u32
}
fn own_quotas(rows: &Rows, supports: &[u8; 84], u: usize) -> bool {
    (0..14).filter(|s| supports[u] & (1 << (s / 2)) != 0).all(|s| {
        (rows[u+15] & rows[s+1]).count_ones() == 2 - ((rows[u+15] >> (s+1)) & 1) as u32
    })
}
fn read_graph(path: &str) -> Result<(Graph, [u8; 84]), String> {
    let raw = fs::read_to_string(path).map_err(|e| e.to_string())?;
    let mut tokens = raw.split_whitespace();
    if tokens.next() != Some("C99OVERLAPS1") || tokens.next() != Some("1") {
        return Err("Expected C99OVERLAPS1 1".into());
    }
    let mut rows = [0u128; 99];
    let mut supports = [0u8; 84];
    for s in 1..15 { add(&mut rows, 0, s); }
    for s in (1..15).step_by(2) { add(&mut rows, s, s+1); }
    let mut index = 0;
    for a in 0..7 { for b in a+1..7 { for s in 0..2 { for t in 0..2 {
        supports[index] = (1 << a) | (1 << b);
        add(&mut rows, index+15, 2*a+s+1);
        add(&mut rows, index+15, 2*b+t+1);
        index += 1;
    }}}}
    let mut edges = Vec::with_capacity(168);
    for _ in 0..168 {
        let u = tokens.next().ok_or("Missing endpoint")?.parse::<usize>().map_err(|_| "Invalid endpoint")?;
        let v = tokens.next().ok_or("Missing endpoint")?.parse::<usize>().map_err(|_| "Invalid endpoint")?;
        if u >= v || v >= 84 || (supports[u] & supports[v]).count_ones() != 1 ||
            (rows[u+15] >> (v+15)) & 1 != 0 {
            return Err("Invalid, duplicate or non-overlap edge".into());
        }
        add(&mut rows, u+15, v+15);
        edges.push((u,v));
    }
    if tokens.next().is_some() { return Err("Trailing input".into()); }
    edges.sort_unstable();
    for u in 0..99 {
        if rows[u].count_ones() != if u < 15 {14} else {6} { return Err("Invalid degree".into()); }
        for v in u+1..99 {
            if !pair_ok(&rows, u, v) { return Err("Invalid partial pair cap".into()); }
        }
    }
    if (0..84).any(|u| !own_quotas(&rows, &supports, u)) { return Err("Invalid own-root quota".into()); }
    Ok((Graph {rows, edges}, supports))
}
fn apply(graph: &Graph, trade: &Trade) -> Graph {
    let mut rows = graph.rows;
    for &(u,v) in &trade.removed {
        rows[u+15] ^= 1u128 << (v+15);
        rows[v+15] ^= 1u128 << (u+15);
    }
    for &(u,v) in &trade.added { add(&mut rows, u+15, v+15); }
    let mut edges: Vec<_> = graph.edges.iter().copied().filter(|e| !trade.removed.contains(e)).collect();
    edges.extend(trade.added);
    edges.sort_unstable();
    Graph {rows, edges}
}
fn legal_trades(graph: &Graph, supports: &[u8; 84]) -> Vec<Trade> {
    let mut result = Vec::new();
    for i in 0..168 { for j in i+1..168 {
        let (a,b) = graph.edges[i];
        let (c,d) = graph.edges[j];
        if a==c || a==d || b==c || b==d { continue; }
        let removed = [(a,b),(c,d)];
        let changed = [a,b,c,d];
        for mut added in [[edge(a,c),edge(b,d)], [edge(a,d),edge(b,c)]] {
            if added.iter().any(|&(u,v)| (supports[u] & supports[v]).count_ones() != 1 ||
                (graph.rows[u+15] >> (v+15)) & 1 != 0) { continue; }
            added.sort_unstable();
            let mut next = graph.rows;
            for &(u,v) in &removed {
                next[u+15] ^= 1u128 << (v+15);
                next[v+15] ^= 1u128 << (u+15);
            }
            for &(u,v) in &added { add(&mut next, u+15, v+15); }
            // The four affected rows contain every changed pair constraint.
            if changed.iter().any(|&u| !own_quotas(&next, supports, u) ||
                (0..99).any(|v| u+15 != v && !pair_ok(&next, u+15, v))) { continue; }
            result.push(Trade {removed, added});
        }
    }}
    result
}
fn write_edges(out: &mut String, edges: &[Edge]) {
    out.push('[');
    for (i,(u,v)) in edges.iter().enumerate() {
        if i > 0 { out.push(','); }
        write!(out, "[{u},{v}]").unwrap();
    }
    out.push(']');
}
fn write_trade(out: &mut String, trade: &Trade) {
    out.push_str("{\"removed\":"); write_edges(out, &trade.removed);
    out.push_str(",\"added\":"); write_edges(out, &trade.added); out.push('}');
}
fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args().collect();
    if args.len() < 3 || args.len() > 5 {
        return Err("usage: overlap_two_neighbors INPUT.txt OUTPUT.json [sample_limit=128] [seed=0]".into());
    }
    if std::path::Path::new(&args[2]).exists() { return Err("Output already exists".into()); }
    let limit = args.get(3).map(|s| s.parse::<usize>()).transpose().map_err(|_| "Invalid limit")?.unwrap_or(128);
    if !(1..=4096).contains(&limit) { return Err("sample_limit must be in 1..4096".into()); }
    let seed = args.get(4).map(|s| s.parse::<u64>()).transpose().map_err(|_| "Invalid seed")?.unwrap_or(0);
    let (original, supports) = read_graph(&args[1])?;
    let started = Instant::now();
    let first_trades = legal_trades(&original, &supports);
    let mut state = seed;
    let order = shuffled_indices(first_trades.len(), &mut state);
    let branch_cap = first_trades.len().min(limit.max(16));
    let per_branch = if branch_cap == 0 {0} else {limit.div_ceil(branch_cap)};
    let mut seen = BTreeSet::new();
    let mut sampled: Vec<(Vec<Edge>, [Trade;2])> = Vec::new();
    let (mut branches, mut second_count, mut considered, mut short_paths, mut duplicates) = (0usize,0usize,0usize,0usize,0usize);
    for &first_index in order.iter().take(branch_cap) {
        if sampled.len() == limit { break; }
        let first = first_trades[first_index];
        let middle = apply(&original, &first);
        let seconds = legal_trades(&middle, &supports);
        branches += 1;
        second_count += seconds.len();
        let mut from_branch = 0;
        for second_index in shuffled_indices(seconds.len(), &mut state) {
            if sampled.len() == limit || from_branch == per_branch { break; }
            considered += 1;
            let second = seconds[second_index];
            let final_graph = apply(&middle, &second);
            let net_removed = original.edges.iter().filter(|e| final_graph.edges.binary_search(e).is_err()).count();
            // Every one-step two-edge swap removes exactly two original edges.
            if net_removed < 3 { short_paths += 1; continue; }
            if !seen.insert(final_graph.edges.clone()) { duplicates += 1; continue; }
            sampled.push((final_graph.edges, [first, second]));
            from_branch += 1;
        }
    }
    let mut out = String::from("{\"status\":\"BOUNDED_TWO_TRADE_PROPOSALS\",\"overlap_candidates\":[");
    for (i,(edges,_)) in sampled.iter().enumerate() {
        if i > 0 {out.push(',');} write_edges(&mut out, edges);
    }
    out.push_str("],\"trade_paths\":[");
    for (i,(_,path)) in sampled.iter().enumerate() {
        if i > 0 {out.push(',');}
        out.push('['); write_trade(&mut out, &path[0]); out.push(','); write_trade(&mut out, &path[1]); out.push(']');
    }
    write!(&mut out, "],\"sample_limit\":{limit},\"seed\":{seed},\"first_legal_trades\":{},\"intermediate_branch_cap\":{branch_cap},\"intermediates_enumerated\":{branches},\"second_legal_trades_enumerated\":{second_count},\"paths_considered\":{considered},\"rejected_short_paths\":{short_paths},\"rejected_duplicate_finals\":{duplicates},\"returned_candidates\":{},\"elapsed_seconds\":{},\"scope\":\"Deterministic bounded nonuniform sampling of two legal overlap trades. Every intermediate preserves full 99-vertex partial caps, degree four in K and exact own-label quotas. Distinct final states remove at least three original edges. No local star or pair-AC filtering, no exhaustive two-step coverage and no completion/exclusion claim.\"}}\n", first_trades.len(), sampled.len(), started.elapsed().as_secs_f64()).unwrap();
    fs::write(&args[2], out).map_err(|e| e.to_string())?;
    eprintln!("Generated {} two-trade proposals from {branches}/{} first trades in {:.6}s", sampled.len(), first_trades.len(), started.elapsed().as_secs_f64());
    Ok(())
}
fn main() { if let Err(e) = run() {eprintln!("{e}"); std::process::exit(1);} }
