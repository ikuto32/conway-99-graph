//! Complete same-sign whole-matching replacements, final partial graph only.
//! Geometry derived from frozen overlap_cycle_neighbors.rs SHA256
//! d6c6563b974050246b14e996a737feb9936d18094257a3b47993d64339aaf41c.
//! rustc -O -C target-cpu=native acceleration/overlap_matching_neighbors.rs -o acceleration/build/overlap_matching_neighbors.exe
//! overlap_matching_neighbors INPUT.txt OUTPUT.json [all|root_group:sign]

use std::collections::BTreeSet;
use std::fmt::Write as FmtWrite;
use std::io::Write as IoWrite;
use std::{fs, time::Instant};

type Edge = (usize, usize);
type Rows = [u128; 99];
struct Graph { rows: Rows, edges: Vec<Edge> }
struct Move { removed: Vec<Edge>, added: Vec<Edge>, group: usize, sign: usize, cycles: Vec<Vec<usize>> }
struct Count { group: usize, sign: usize, raw: usize, unchanged: usize, rejected: usize, legal: usize }

fn edge(a: usize, b: usize) -> Edge { (a.min(b), a.max(b)) }
fn add(rows: &mut Rows, u: usize, v: usize) {
    rows[u] |= 1u128 << v;
    rows[v] |= 1u128 << u;
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

// The least unmatched vertex has exactly one partner in each perfect matching.
// Recursing over its increasing allowed partners enumerates each matching once.
fn enumerate(vertices: &[usize], supports: &[u8; 84], prefix: &mut Vec<Edge>, out: &mut Vec<Vec<Edge>>) {
    if vertices.is_empty() {
        let mut matching = prefix.clone();
        matching.sort_unstable();
        out.push(matching);
        return;
    }
    let u = vertices[0];
    for i in 1..vertices.len() {
        let v = vertices[i];
        if (supports[u] & supports[v]).count_ones() != 1 { continue; }
        let remaining: Vec<_> = vertices[1..].iter().copied().filter(|&w| w != v).collect();
        prefix.push(edge(u,v));
        enumerate(&remaining, supports, prefix, out);
        prefix.pop();
    }
}

fn alternating_cycles(removed: &[Edge], added: &[Edge]) -> Result<Vec<Vec<usize>>, String> {
    let mut old = [usize::MAX; 84];
    let mut new = [usize::MAX; 84];
    for &(u,v) in removed { old[u]=v; old[v]=u; }
    for &(u,v) in added { new[u]=v; new[v]=u; }
    let mut unused: BTreeSet<_> = removed.iter().flat_map(|&(u,v)| [u,v]).collect();
    let mut cycles = Vec::new();
    while let Some(&start) = unused.iter().next() {
        let mut cycle = Vec::new();
        let mut u = start;
        loop {
            let v = old[u];
            if v == usize::MAX || !unused.remove(&u) || !unused.remove(&v) {
                return Err("Invalid symmetric-difference cycle".into());
            }
            cycle.extend([u,v]);
            u = new[v];
            if u == start { break; }
            if u == usize::MAX || cycle.len() > 12 { return Err("Unclosed alternating cycle".into()); }
        }
        if cycle.len() < 4 { return Err("Unchanged edge in alternating cycle".into()); }
        cycles.push(cycle);
    }
    if cycles.iter().map(|c| c.len()).sum::<usize>() != 2*removed.len() {
        return Err("Incomplete alternating-cycle decomposition".into());
    }
    Ok(cycles)
}

fn write_edges(out: &mut String, edges: &[Edge]) {
    out.push('[');
    for (i,(u,v)) in edges.iter().enumerate() {
        if i>0 {out.push(',');}write!(out,"[{u},{v}]").unwrap();
    }
    out.push(']');
}

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args().collect();
    if args.len()<3 || args.len()>4 {
        return Err("usage: overlap_matching_neighbors INPUT.txt OUTPUT.json [all|root_group:sign]".into());
    }
    if std::path::Path::new(&args[2]).exists() { return Err("Output already exists".into()); }
    let mode=args.get(3).map(|s|s.as_str()).unwrap_or("all");
    let coordinates: Vec<(usize,usize)> = if mode=="all" {
        (0..7).flat_map(|g| (0..2).map(move |s| (g,s))).collect()
    } else {
        let pieces: Vec<_> = mode.split(':').collect();
        if pieces.len()!=2 { return Err("Selector must be all or root_group:sign".into()); }
        let group=pieces[0].parse::<usize>().map_err(|_| "Invalid root group")?;
        let sign=pieces[1].parse::<usize>().map_err(|_| "Invalid sign")?;
        if group>=7 || sign>=2 { return Err("Selector requires root group 0..6 and sign 0..1".into()); }
        vec![(group,sign)]
    };
    let (graph,supports)=read_graph(&args[1])?;
    let started=Instant::now();
    let mut counts=Vec::new();
    let mut candidates: Vec<(Vec<Edge>,Move)> = Vec::new();
    for (group,sign) in coordinates {
        let vertices: Vec<_> = (0..84).filter(|&u| ((graph.rows[u+15]>>(2*group+sign+1))&1)!=0).collect();
        if vertices.len()!=12 { return Err("Invalid same-sign cohort".into()); }
        let matching: Vec<_> = graph.edges.iter().copied().filter(|&(u,v)| vertices.contains(&u) && vertices.contains(&v)).collect();
        let endpoints: BTreeSet<_> = matching.iter().flat_map(|&(u,v)| [u,v]).collect();
        if matching.len()!=6 || endpoints.len()!=12 { return Err("Invalid same-sign matching decomposition".into()); }
        let mut replacements=Vec::new();
        enumerate(&vertices,&supports,&mut Vec::new(),&mut replacements);
        if replacements.len()!=6040 { return Err("Support-allowed matching count is not 6040".into()); }
        let mut count=Count{group,sign,raw:replacements.len(),unchanged:0,rejected:0,legal:0};
        for replacement in replacements {
            if replacement==matching { count.unchanged+=1; continue; }
            let removed: Vec<_> = matching.iter().copied().filter(|e| !replacement.contains(e)).collect();
            let added: Vec<_> = replacement.iter().copied().filter(|e| !matching.contains(e)).collect();
            if removed.len()!=added.len() || !(2..=6).contains(&removed.len()) {
                return Err("Invalid matching replacement size".into());
            }
            let mut next=graph.rows;
            for &(u,v) in &removed { next[u+15]^=1u128<<(v+15); next[v+15]^=1u128<<(u+15); }
            for &(u,v) in &added { add(&mut next,u+15,v+15); }
            // Only rows incident to changed matching edges can change a pair cap.
            // Checking all cohort rows against all 99 vertices covers every such pair.
            if vertices.iter().any(|&u| !own_quotas(&next,&supports,u) ||
                (0..99).any(|v| u+15!=v && !pair_ok(&next,u+15,v))) {
                count.rejected+=1; continue;
            }
            let cycles=alternating_cycles(&removed,&added)?;
            let mut edges: Vec<_> = graph.edges.iter().copied().filter(|e| !removed.contains(e)).collect();
            edges.extend(&added);
            edges.sort_unstable();
            candidates.push((edges,Move{removed,added,group,sign,cycles}));
            count.legal+=1;
        }
        if count.unchanged!=1 || count.raw!=count.unchanged+count.rejected+count.legal {
            return Err("Matching partition count mismatch".into());
        }
        counts.push(count);
    }
    // Distinct coordinates have disjoint possible edge domains; after excluding
    // the base matching they cannot yield the same final graph. Within a
    // coordinate, least-unmatched-vertex recursion is injective.
    let raw: usize=counts.iter().map(|c|c.raw).sum();
    let unchanged: usize=counts.iter().map(|c|c.unchanged).sum();
    let rejected: usize=counts.iter().map(|c|c.rejected).sum();
    let legal=candidates.len();
    let mut out=String::from("{\"status\":\"COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION\",\"overlap_candidates\":[");
    for (i,(edges,_)) in candidates.iter().enumerate() { if i>0 {out.push(',');}write_edges(&mut out,edges); }
    out.push_str("],\"moves\":[");
    for (i,(_,m)) in candidates.iter().enumerate() {
        if i>0 {out.push(',');}
        write!(&mut out,"{{\"root_group\":{},\"matching_class\":\"same_{}\",\"removed\":",m.group,m.sign).unwrap();
        write_edges(&mut out,&m.removed);out.push_str(",\"added\":");write_edges(&mut out,&m.added);
        write!(&mut out,",\"changed_edges\":{},\"alternating_cycles\":{:?}}}",m.removed.len(),m.cycles).unwrap();
    }
    write!(&mut out,"],\"selector\":\"{mode}\",\"coordinate_count\":{},\"raw_including_initial\":{raw},\"unchanged_count\":{unchanged},\"cap_rejected_count\":{rejected},\"legal_count\":{legal},\"by_class\":[",counts.len()).unwrap();
    for (i,c) in counts.iter().enumerate() {
        if i>0 {out.push(',');}
        write!(&mut out,"{{\"root_group\":{},\"matching_class\":\"same_{}\",\"raw_including_initial\":{},\"unchanged_count\":{},\"cap_rejected_count\":{},\"legal_count\":{}}}",c.group,c.sign,c.raw,c.unchanged,c.rejected,c.legal).unwrap();
    }
    write!(&mut out,"],\"elapsed_seconds\":{},\"scope\":\"Complete support-allowed perfect matchings within the selected same-sign coordinates, one coordinate replaced at a time, other20 fixed. Unchanged base excluded. All final full99 partial pair caps and exact own-label quotas enforced; multiple disjoint alternating cycles and 2..6 changed matching edges allowed. No intermediate-state requirement, star-domain filtering, pair-AC filtering, cross-matching enumeration, global exhaustion, completion or exclusion claim.\"}}\n",started.elapsed().as_secs_f64()).unwrap();
    let mut output=fs::OpenOptions::new().write(true).create_new(true).open(&args[2]).map_err(|e|e.to_string())?;
    output.write_all(out.as_bytes()).map_err(|e|e.to_string())?;
    eprintln!("Enumerated {legal} legal replacements from {raw} matchings ({unchanged} unchanged, {rejected} rejected) in {:.6}s",started.elapsed().as_secs_f64());
    Ok(())
}
fn main() { if let Err(e)=run() { eprintln!("{e}");std::process::exit(1); } }
