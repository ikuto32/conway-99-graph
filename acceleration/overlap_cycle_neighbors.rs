//! Complete atomic matching-cycle subfamily, final partial graph checked only.
//! Derived geometry from frozen overlap_two_neighbors.rs; SHA256
//! f262c63ce4495ce397c4afac20815221b84ba68aca0a61f2a6e0812333b7fe10.
//! rustc -O -C target-cpu=native acceleration/overlap_cycle_neighbors.rs -o acceleration/build/overlap_cycle_neighbors.exe
//! overlap_cycle_neighbors INPUT.txt OUTPUT.json [3|4|both] (default 3)
//! Complete only for one alternating cycle in one matching, not all K moves.

use std::collections::BTreeSet;
use std::fmt::Write as FmtWrite;
use std::{fs, time::Instant};

type Edge = (usize, usize);
type Rows = [u128; 99];
struct Graph { rows: Rows, edges: Vec<Edge> }

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

#[derive(Clone)]
struct Move { removed: Vec<Edge>, added: Vec<Edge>, group: usize, class: usize, k: usize, cycle: Vec<usize> }
struct Count { group: usize, class: usize, k: usize, raw: usize, support_rejected: usize, cap_rejected: usize, legal: usize }
fn class_name(class: usize) -> &'static str { ["same_0", "same_1", "cross"][class] }
fn combinations(n: usize, k: usize) -> Vec<Vec<usize>> {
    fn rec(n: usize, k: usize, next: usize, prefix: &mut Vec<usize>, out: &mut Vec<Vec<usize>>) {
        if prefix.len() == k {out.push(prefix.clone()); return;}
        for i in next..=n-(k-prefix.len()) {
            prefix.push(i); rec(n,k,i+1,prefix,out); prefix.pop();
        }
    }
    let mut out=Vec::new(); rec(n,k,0,&mut Vec::new(),&mut out); out
}
fn permutations(values: &[usize]) -> Vec<Vec<usize>> {
    fn rec(values: &mut [usize], at: usize, out: &mut Vec<Vec<usize>>) {
        if at == values.len() {out.push(values.to_vec()); return;}
        for i in at..values.len() {values.swap(at,i);rec(values,at+1,out);values.swap(at,i);}
    }
    let mut out=Vec::new();rec(&mut values.to_vec(),0,&mut out);out
}
fn write_edges(out: &mut String, edges: &[Edge]) {
    out.push('[');
    for (i,(u,v)) in edges.iter().enumerate() {
        if i>0 {out.push(',');}write!(out,"[{u},{v}]").unwrap();
    }
    out.push(']');
}
fn run() -> Result<(), String> {
    let args:Vec<_>=std::env::args().collect();
    if args.len()<3 || args.len()>4 {return Err("usage: overlap_cycle_neighbors INPUT.txt OUTPUT.json [3|4|both]".into());}
    if std::path::Path::new(&args[2]).exists() {return Err("Output already exists".into());}
    let mode=args.get(3).map(|s|s.as_str()).unwrap_or("3");
    let sizes:Vec<usize>=match mode {"3"=>vec![3],"4"=>vec![4],"both"=>vec![3,4],_=>return Err("cycle size must be 3, 4 or both".into())};
    let (graph,supports)=read_graph(&args[1])?;
    let started=Instant::now();
    let mut matchings:Vec<Vec<Edge>>=vec![Vec::new();21];
    for &(u,v) in &graph.edges {
        let group=(supports[u]&supports[v]).trailing_zeros() as usize;
        let su=((graph.rows[u+15]>>(2*group+2))&1) as usize;
        let sv=((graph.rows[v+15]>>(2*group+2))&1) as usize;
        let class=if su==sv {su} else {2};
        matchings[3*group+class].push(if class==2 && su==1 {(v,u)} else {(u,v)});
    }
    for (index,matching) in matchings.iter().enumerate() {
        let expected=if index%3==2 {12} else {6};
        let endpoints:BTreeSet<_>=matching.iter().flat_map(|&(u,v)|[u,v]).collect();
        if matching.len()!=expected || endpoints.len()!=2*expected {return Err("Matching decomposition failed".into());}
    }
    let mut counts=Vec::new();
    let mut candidates:Vec<(Vec<Edge>,Move)>=Vec::new();
    let mut seen=BTreeSet::new();
    for &k in &sizes {for group in 0..7 {for class in 0..3 {
        let matching=&matchings[3*group+class];
        let mut count=Count{group,class,k,raw:0,support_rejected:0,cap_rejected:0,legal:0};
        let tails=permutations(&(1..k).collect::<Vec<_>>());
        for choice in combinations(matching.len(),k) {
            let old:Vec<_>=choice.iter().map(|&i|matching[i]).collect();
            let mut removed:Vec<_>=old.iter().map(|&(u,v)|edge(u,v)).collect();removed.sort_unstable();
            for tail in &tails {
                let order:Vec<_>=std::iter::once(0).chain(tail.iter().copied()).collect();
                let orientations=if class==2 {1} else {1usize<<(k-1)};
                for bits in 0..orientations {
                    count.raw+=1;
                    let mut cycle=Vec::with_capacity(2*k);
                    for (position,&index) in order.iter().enumerate() {
                        let (mut u,mut v)=old[index];
                        if position>0 && bits&(1<<(position-1))!=0 {std::mem::swap(&mut u,&mut v);}
                        cycle.extend([u,v]);
                    }
                    let mut added:Vec<_>=(0..k).map(|i|edge(cycle[2*i+1],cycle[(2*i+2)%(2*k)])).collect();added.sort_unstable();
                    if added.iter().any(|&(u,v)|(supports[u]&supports[v]).count_ones()!=1 || (graph.rows[u+15]>>(v+15))&1!=0) {
                        count.support_rejected+=1;continue;
                    }
                    let mut next=graph.rows;
                    for &(u,v) in &removed {next[u+15]^=1u128<<(v+15);next[v+15]^=1u128<<(u+15);}
                    for &(u,v) in &added {add(&mut next,u+15,v+15);}
                    if cycle.iter().any(|&u|!own_quotas(&next,&supports,u) || (0..99).any(|v|u+15!=v && !pair_ok(&next,u+15,v))) {
                        count.cap_rejected+=1;continue;
                    }
                    let mut edges:Vec<_>=graph.edges.iter().copied().filter(|e|!removed.contains(e)).collect();edges.extend(&added);edges.sort_unstable();
                    if !seen.insert(edges.clone()) {return Err("Duplicate final candidate: cycle canonicalization failed".into());}
                    candidates.push((edges,Move{removed:removed.clone(),added,group,class,k,cycle}));
                    count.legal+=1;
                }
            }
        }
        let expected=match(k,class==2){(3,false)=>160,(3,true)=>440,(4,false)=>720,(4,true)=>2970,_=>unreachable!()};
        if count.raw!=expected {return Err("Raw cycle count mismatch".into());}
        counts.push(count);
    }}}
    let raw:usize=counts.iter().map(|c|c.raw).sum();
    let legal=candidates.len();
    let mut out=String::from("{\"status\":\"COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION\",\"overlap_candidates\":[");
    for (i,(edges,_)) in candidates.iter().enumerate(){if i>0 {out.push(',');}write_edges(&mut out,edges);}
    out.push_str("],\"moves\":[");
    for (i,(_,m)) in candidates.iter().enumerate(){
        if i>0 {out.push(',');}out.push_str("{\"removed\":");write_edges(&mut out,&m.removed);out.push_str(",\"added\":");write_edges(&mut out,&m.added);
        write!(&mut out,",\"root_group\":{},\"matching_class\":\"{}\",\"cycle_size\":{},\"alternating_cycle\":{:?}}}",m.group,class_name(m.class),m.k,m.cycle).unwrap();
    }
    write!(&mut out,"],\"cycle_size\":\"{mode}\",\"raw_cycles\":{raw},\"legal_cycles\":{legal},\"by_class\":[").unwrap();
    for (i,c) in counts.iter().enumerate(){
        if i>0 {out.push(',');}
        write!(&mut out,"{{\"root_group\":{},\"matching_class\":\"{}\",\"cycle_size\":{},\"raw_cycles\":{},\"support_rejected\":{},\"cap_rejected\":{},\"legal_cycles\":{}}}",c.group,class_name(c.class),c.k,c.raw,c.support_rejected,c.cap_rejected,c.legal).unwrap();
    }
    write!(&mut out,"],\"elapsed_seconds\":{},\"scope\":\"Complete enumeration only of one alternating cycle with the selected 3 or 4 old edges inside one of the 21 overlap matchings. Final full-99 partial caps and exact own-label quotas checked; no intermediate-state requirement and no star-domain or pair-AC filtering. Not all overlap moves, no global exhaustion, no completion or exclusion claim.\"}}\n",started.elapsed().as_secs_f64()).unwrap();
    fs::write(&args[2],out).map_err(|e|e.to_string())?;
    eprintln!("Enumerated {legal}/{raw} legal atomic cycles in {:.6}s",started.elapsed().as_secs_f64());
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("{e}");std::process::exit(1);}}
