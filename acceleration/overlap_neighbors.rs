//! Enumerate legal two-edge overlap trades using full 99-vertex bit rows.
//! rustc -O -C target-cpu=native acceleration/overlap_neighbors.rs -o acceleration/build/overlap_neighbors.exe
//! overlap_neighbors INPUT.txt OUTPUT.json [sample_limit] [seed]
//! C99OVERLAPS1 input must contain exactly one complete overlap assignment.
//! This is a candidate generator, never an infeasibility certificate.

use std::fmt::Write as FmtWrite;
use std::{fs, time::Instant};
type Edge = (usize, usize);
fn edge(a: usize, b: usize) -> Edge { (a.min(b), a.max(b)) }
fn random(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9e3779b97f4a7c15);
    let mut x = *state;
    x = (x ^ (x >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27)).wrapping_mul(0x94d049bb133111eb);
    x ^ (x >> 31)
}
fn pair_ok(rows: &[u128; 99], u: usize, v: usize) -> bool {
    (rows[u] & rows[v]).count_ones() <= 2 - ((rows[u] >> v) & 1) as u32
}
fn write_edges(out: &mut String, edges: &[Edge]) {
    out.push('[');
    for (i, (u,v)) in edges.iter().enumerate() {
        if i > 0 { out.push(','); }
        write!(out, "[{u},{v}]").unwrap();
    }
    out.push(']');
}
fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args().collect();
    if args.len() < 3 || args.len() > 5 {
        return Err("usage: overlap_neighbors INPUT.txt OUTPUT.json [sample_limit] [seed]".into());
    }
    if std::path::Path::new(&args[2]).exists() { return Err("Output already exists".into()); }
    let limit = args.get(3).map(|s| s.parse::<usize>()).transpose().map_err(|_| "Invalid limit")?.unwrap_or(0);
    let seed = args.get(4).map(|s| s.parse::<u64>()).transpose().map_err(|_| "Invalid seed")?.unwrap_or(0);
    let mut state = seed;
    let raw = fs::read_to_string(&args[1]).map_err(|e| e.to_string())?;
    let mut tokens = raw.split_whitespace();
    if tokens.next() != Some("C99OVERLAPS1") || tokens.next() != Some("1") {
        return Err("Expected C99OVERLAPS1 1".into());
    }
    let mut rows = [0u128; 99];
    let mut supports = [0u8; 84];
    fn add(rows: &mut [u128;99], u:usize,v:usize) { rows[u] |= 1u128 << v; rows[v] |= 1u128 << u; }
    for s in 1..15 { add(&mut rows,0,s); }
    for s in (1..15).step_by(2) { add(&mut rows,s,s+1); }
    let mut index = 0;
    for a in 0..7 { for b in a+1..7 { for s in 0..2 { for t in 0..2 {
        supports[index] = (1 << a) | (1 << b);
        add(&mut rows,index+15,2*a+s+1);
        add(&mut rows,index+15,2*b+t+1);
        index += 1;
    }}}}
    let mut original = Vec::with_capacity(168);
    for _ in 0..168 {
        let u = tokens.next().ok_or("Missing endpoint")?.parse::<usize>().map_err(|_| "Invalid endpoint")?;
        let v = tokens.next().ok_or("Missing endpoint")?.parse::<usize>().map_err(|_| "Invalid endpoint")?;
        if u >= v || v >= 84 || (supports[u] & supports[v]).count_ones() != 1 || (rows[u+15] >> (v+15)) & 1 != 0 {
            return Err("Invalid, duplicate or non-overlap edge".into());
        }
        add(&mut rows,u+15,v+15);
        original.push((u,v));
    }
    if tokens.next().is_some() { return Err("Trailing input".into()); }
    original.sort_unstable();
    for u in 0..99 {
        if rows[u].count_ones() != if u < 15 {14} else {6} { return Err("Invalid degree".into()); }
        for v in u+1..99 { if !pair_ok(&rows,u,v) { return Err("Invalid partial pair cap".into()); } }
    }
    let started = Instant::now();
    let mut total = 0usize;
    let mut sampled: Vec<([Edge;2],[Edge;2])> = Vec::new();
    for i in 0..168 { for j in i+1..168 {
        let (a,b) = original[i]; let (c,d) = original[j];
        if a==c || a==d || b==c || b==d { continue; }
        let changed = [a+15,b+15,c+15,d+15];
        let removed = [(a,b),(c,d)];
        for added in [[edge(a,c),edge(b,d)],[edge(a,d),edge(b,c)]] {
            if added.iter().any(|&(u,v)| (supports[u]&supports[v]).count_ones()!=1 || (rows[u+15]>>(v+15))&1 != 0) {continue;}
            let mut next = rows;
            for &(u,v) in &removed { next[u+15] ^= 1u128<<(v+15); next[v+15] ^= 1u128<<(u+15); }
            for &(u,v) in &added { add(&mut next,u+15,v+15); }
            // Rows of all other vertices and their mutual adjacency are unchanged.
            if changed.iter().any(|&u| (0..99).any(|v| u!=v && !pair_ok(&next,u,v))) {continue;}
            total += 1;
            if limit==0 || sampled.len()<limit { sampled.push((removed,added)); }
            else {
                let k = (random(&mut state) % total as u64) as usize;
                if k < limit { sampled[k] = (removed,added); }
            }
        }
    }}
    let mut out = String::from("{\"overlap_candidates\":[");
    for (index,(removed,added)) in sampled.iter().enumerate() {
        if index>0 {out.push(',');}
        let mut edges:Vec<_> = original.iter().copied().filter(|e| !removed.contains(e)).collect();
        edges.extend(added);
        edges.sort_unstable();
        write_edges(&mut out,&edges);
    }
    out.push_str("],\"trades\":[");
    for (index,(removed,added)) in sampled.iter().enumerate() {
        if index>0 {out.push(',');}
        out.push_str("{\"removed\":");write_edges(&mut out,removed);
        out.push_str(",\"added\":");write_edges(&mut out,added);out.push('}');
    }
    write!(&mut out,"],\"legal_trades\":{total},\"sample_limit\":{limit},\"seed\":{seed},\"elapsed_seconds\":{},\"scope\":\"Candidate generation only. Variable overlap compression. No exclusion or full graph claim.\"}}\n",started.elapsed().as_secs_f64()).unwrap();
    fs::write(&args[2],out).map_err(|e| e.to_string())?;
    eprintln!("Generated {}/{} legal neighbors in {:.6}s",sampled.len(),total,started.elapsed().as_secs_f64());
    Ok(())
}
fn main() { if let Err(e)=run() {eprintln!("{e}");std::process::exit(1);} }
