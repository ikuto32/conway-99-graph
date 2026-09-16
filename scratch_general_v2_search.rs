use std::fs;
use std::sync::{
    atomic::{AtomicBool, AtomicI64, Ordering},
    Arc, Mutex,
};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

// General local search for the 84 vertices outside the closed neighbourhood of
// a distinguished vertex.  The 15-vertex scaffold is forced, but NO symmetry
// or Cayley/voltage ansatz is imposed on the 84-vertex graph.
const N: usize = 99;
const O: usize = 15;
const M: usize = N - O;
const MUTABLE_EDGES: usize = M * 12 / 2;
const NONE: u16 = u16::MAX;

type Edge = (usize, usize);

#[derive(Clone)]
struct Rng(u64);
impl Rng {
    fn new(mut seed: u64) -> Self {
        if seed == 0 { seed = 0x9e37_79b9_7f4a_7c15; }
        Self(seed)
    }
    #[inline]
    fn u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x2545_f491_4f6c_dd1d)
    }
    #[inline]
    fn us(&mut self, n: usize) -> usize { (self.u64() as usize) % n }
    #[inline]
    fn unit(&mut self) -> f64 { ((self.u64() >> 11) as f64) * (1.0 / ((1u64 << 53) as f64)) }
}

#[inline]
fn canon(a: usize, b: usize) -> Edge { if a < b { (a, b) } else { (b, a) } }

#[derive(Clone)]
struct Graph {
    adj: [u128; N],
    cn: [[u8; N]; N],
    energy: i64,
    guided: i64,
    io_energy: i64,
    oo_energy: i64,
    io_weight: i64,
}

impl Graph {
    fn new(io_weight: i64) -> Self {
        Self {
            adj: [0; N], cn: [[0; N]; N], energy: 0, guided: 0,
            io_energy: 0, oo_energy: 0, io_weight,
        }
    }
    #[inline]
    fn has(&self, u: usize, v: usize) -> bool { (self.adj[u] >> v) & 1 != 0 }
    #[inline]
    fn raw(&mut self, u: usize, v: usize, on: bool) {
        debug_assert_ne!(u, v);
        let bu = 1u128 << u;
        let bv = 1u128 << v;
        if on { self.adj[u] |= bv; self.adj[v] |= bu; }
        else { self.adj[u] &= !bv; self.adj[v] &= !bu; }
    }
    #[inline]
    fn residual(&self, u: usize, v: usize) -> i16 {
        self.cn[u][v] as i16 + self.has(u, v) as i16 - 2
    }
    #[inline]
    fn penalty(&self, u: usize, v: usize) -> i64 {
        let r = self.residual(u, v) as i64;
        r * r
    }
    #[inline]
    fn category(u: usize, v: usize) -> u8 {
        if u < O && v >= O { 1 } else if u >= O { 2 } else { 0 }
    }
    #[inline]
    fn subtract_pair(&mut self, u: usize, v: usize) {
        let (a, b) = canon(u, v);
        let p = self.penalty(a, b);
        self.energy -= p;
        match Self::category(a, b) {
            1 => { self.io_energy -= p; self.guided -= p * self.io_weight; }
            2 => { self.oo_energy -= p; self.guided -= p; }
            _ => self.guided -= p,
        }
    }
    #[inline]
    fn add_pair(&mut self, u: usize, v: usize) {
        let (a, b) = canon(u, v);
        let p = self.penalty(a, b);
        self.energy += p;
        match Self::category(a, b) {
            1 => { self.io_energy += p; self.guided += p * self.io_weight; }
            2 => { self.oo_energy += p; self.guided += p; }
            _ => self.guided += p,
        }
    }
    #[inline]
    fn change_common(&mut self, u: usize, v: usize, delta: i8) {
        if u == v { return; }
        let (a, b) = canon(u, v);
        self.subtract_pair(a, b);
        let z = self.cn[a][b] as i16 + delta as i16;
        debug_assert!(z >= 0);
        self.cn[a][b] = z as u8;
        self.cn[b][a] = z as u8;
        self.add_pair(a, b);
    }
    // Incremental exact update. During a k-switch all removals precede all
    // additions, so no temporary degree exceeds 14.
    fn toggle(&mut self, u: usize, v: usize, on: bool) {
        debug_assert!(u != v && self.has(u, v) != on);
        if on {
            let nv = self.adj[v];
            let nu = self.adj[u];
            let mut bits = nv;
            while bits != 0 {
                let w = bits.trailing_zeros() as usize;
                bits &= bits - 1;
                self.change_common(u, w, 1);
            }
            bits = nu;
            while bits != 0 {
                let w = bits.trailing_zeros() as usize;
                bits &= bits - 1;
                self.change_common(v, w, 1);
            }
            self.subtract_pair(u, v);
            self.raw(u, v, true);
            self.add_pair(u, v);
        } else {
            self.subtract_pair(u, v);
            self.raw(u, v, false);
            self.add_pair(u, v);
            let nv = self.adj[v];
            let nu = self.adj[u];
            let mut bits = nv;
            while bits != 0 {
                let w = bits.trailing_zeros() as usize;
                bits &= bits - 1;
                self.change_common(u, w, -1);
            }
            bits = nu;
            while bits != 0 {
                let w = bits.trailing_zeros() as usize;
                bits &= bits - 1;
                self.change_common(v, w, -1);
            }
        }
    }
    fn init(&mut self) {
        self.energy = 0;
        self.guided = 0;
        self.io_energy = 0;
        self.oo_energy = 0;
        for u in 0..N {
            for v in u + 1..N {
                let c = (self.adj[u] & self.adj[v]).count_ones() as u8;
                self.cn[u][v] = c;
                self.cn[v][u] = c;
            }
        }
        for u in 0..N { for v in u + 1..N { self.add_pair(u, v); } }
    }
    fn recalc(&self) -> (i64, i64, i64, i64) {
        let mut e = 0i64;
        let mut io = 0i64;
        let mut oo = 0i64;
        for u in 0..N {
            for v in u + 1..N {
                let c = (self.adj[u] & self.adj[v]).count_ones() as i64;
                let r = c + self.has(u, v) as i64 - 2;
                let p = r * r;
                e += p;
                match Self::category(u, v) { 1 => io += p, 2 => oo += p, _ => {} }
            }
        }
        (e, io * self.io_weight + oo, io, oo)
    }
    fn set_io_weight(&mut self, w: i64) {
        self.io_weight = w;
        self.guided = self.energy + (w - 1) * self.io_energy;
    }
}

#[derive(Clone)]
struct State {
    g: Graph,
    edges: Vec<Edge>,
    // Matrix on the mutable 84 vertices. Values are indices into edges.
    edge_index: Vec<u16>,
}

impl State {
    #[inline]
    fn map_pos(u: usize, v: usize) -> usize { (u - O) * M + (v - O) }
    #[inline]
    fn edge_id(&self, u: usize, v: usize) -> Option<usize> {
        if u < O || v < O { return None; }
        let z = self.edge_index[Self::map_pos(u, v)];
        if z == NONE { None } else { Some(z as usize) }
    }
    fn rebuild_index(&mut self) {
        self.edge_index.fill(NONE);
        for (i, &(u, v)) in self.edges.iter().enumerate() {
            self.edge_index[Self::map_pos(u, v)] = i as u16;
            self.edge_index[Self::map_pos(v, u)] = i as u16;
        }
    }
    fn validate(&self) {
        assert_eq!(self.edges.len(), MUTABLE_EDGES);
        let mut seen = vec![false; M * M];
        for (i, &(u, v)) in self.edges.iter().enumerate() {
            assert!(u >= O && v >= O && u < v && self.g.has(u, v));
            assert!(!seen[Self::map_pos(u, v)]);
            seen[Self::map_pos(u, v)] = true;
            assert_eq!(self.edge_id(u, v), Some(i));
        }
        for u in 0..N { assert_eq!(self.g.adj[u].count_ones(), 14); }
        let (e, guided, io, oo) = self.g.recalc();
        assert_eq!((self.g.energy, self.g.guided, self.g.io_energy, self.g.oo_energy), (e, guided, io, oo));
    }
}

fn add_scaffold(g: &mut Graph) {
    for s in 0..14 { g.raw(0, 1 + s, true); }
    for i in 0..7 { g.raw(1 + 2 * i, 2 + 2 * i, true); }
    let mut x = O;
    for i in 0..7 {
        for j in i + 1..7 {
            for a in 0..2 {
                for b in 0..2 {
                    g.raw(x, 1 + 2 * i + a, true);
                    g.raw(x, 1 + 2 * j + b, true);
                    x += 1;
                }
            }
        }
    }
    assert_eq!(x, N);
}

fn state_from_mutable(edges: Vec<Edge>, io_weight: i64) -> State {
    assert_eq!(edges.len(), MUTABLE_EDGES);
    let mut g = Graph::new(io_weight);
    add_scaffold(&mut g);
    for &(u, v) in &edges {
        assert!(u >= O && v >= O && u < v && !g.has(u, v));
        g.raw(u, v, true);
    }
    g.init();
    let mut s = State { g, edges, edge_index: vec![NONE; M * M] };
    s.rebuild_index();
    s.validate();
    s
}

fn state_from_full(edges: Vec<Edge>, io_weight: i64) -> Option<State> {
    if edges.len() != 693 { return None; }
    let mut g = Graph::new(io_weight);
    let mut mutable = Vec::with_capacity(MUTABLE_EDGES);
    for &(u, v) in &edges {
        if u >= N || v >= N || u == v || g.has(u, v) { return None; }
        g.raw(u, v, true);
        if u >= O { mutable.push((u, v)); }
    }
    if mutable.len() != MUTABLE_EDGES || g.adj.iter().any(|a| a.count_ones() != 14) {
        return None;
    }
    g.init();
    let mut s = State { g, edges: mutable, edge_index: vec![NONE; M * M] };
    s.rebuild_index();
    s.validate();
    Some(s)
}

// Minimal, dependency-free parser: only numbers after the JSON "edges" key
// are considered. This also lets the program warm-start from v1's best file.
fn load_seed(path: &str, io_weight: i64) -> Option<State> {
    let text = fs::read_to_string(path).ok()?;
    let at = text.find("\"edges\"")?;
    let mut nums = Vec::<usize>::new();
    let bytes = text[at..].as_bytes();
    let mut i = 0;
    while i < bytes.len() && bytes[i] != b'[' { i += 1; }
    if i == bytes.len() { return None; }
    let mut depth = 0i32;
    while i < bytes.len() {
        if bytes[i] == b'[' { depth += 1; i += 1; }
        else if bytes[i] == b']' {
            depth -= 1;
            i += 1;
            if depth == 0 { break; }
        } else if bytes[i].is_ascii_digit() {
            let mut z = 0usize;
            while i < bytes.len() && bytes[i].is_ascii_digit() {
                z = z * 10 + (bytes[i] - b'0') as usize;
                i += 1;
            }
            nums.push(z);
        } else { i += 1; }
    }
    if nums.len() % 2 != 0 { return None; }
    let mut all_edges = Vec::new();
    for q in nums.chunks_exact(2) {
        if q[0] == 0 || q[1] == 0 || q[0] > N || q[1] > N { return None; }
        let (u, v) = canon(q[0] - 1, q[1] - 1);
        all_edges.push((u, v));
    }
    state_from_full(all_edges, io_weight)
}

fn random_state(rng: &mut Rng, io_weight: i64) -> State {
    let mut edges = Vec::with_capacity(MUTABLE_EDGES);
    let mut used = vec![false; M * M];
    // 12-regular circulant, followed by many degree-preserving switches.
    for x in 0..M {
        for d in 1..=6 {
            let y = (x + d) % M;
            let (u, v) = canon(O + x, O + y);
            let p = (u - O) * M + (v - O);
            if !used[p] {
                used[p] = true;
                used[(v - O) * M + (u - O)] = true;
                edges.push((u, v));
            }
        }
    }
    let mut s = state_from_mutable(edges, io_weight);
    for _ in 0..30_000 {
        if let Some(mv) = random_2switch(&s, rng) { apply_move(&mut s, &mv); }
    }
    s.g.init();
    s.validate();
    s
}

#[derive(Copy, Clone)]
struct Move {
    k: usize,
    idx: [usize; 3],
    old: [Edge; 3],
    new: [Edge; 3],
}

fn blank_move() -> Move {
    Move { k: 0, idx: [0; 3], old: [(0, 0); 3], new: [(0, 0); 3] }
}

fn make_move(s: &State, old: &[Edge], new: &[Edge]) -> Option<Move> {
    if old.len() != new.len() || !(2..=3).contains(&old.len()) { return None; }
    let mut mv = blank_move();
    mv.k = old.len();
    for q in 0..mv.k {
        let e = canon(old[q].0, old[q].1);
        let f = canon(new[q].0, new[q].1);
        if e.0 < O || f.0 < O || e.0 == e.1 || f.0 == f.1 { return None; }
        mv.old[q] = e;
        mv.new[q] = f;
        mv.idx[q] = s.edge_id(e.0, e.1)?;
        if s.g.has(f.0, f.1) { return None; }
        for p in 0..q {
            if mv.idx[p] == mv.idx[q] || mv.new[p] == f { return None; }
        }
    }
    // Degree preservation is checked rather than assumed by constructors.
    let mut balance = [0i8; N];
    for q in 0..mv.k {
        balance[mv.old[q].0] -= 1;
        balance[mv.old[q].1] -= 1;
        balance[mv.new[q].0] += 1;
        balance[mv.new[q].1] += 1;
    }
    if balance.iter().any(|&z| z != 0) { return None; }
    Some(mv)
}

fn apply_move(s: &mut State, mv: &Move) {
    for q in 0..mv.k { s.g.toggle(mv.old[q].0, mv.old[q].1, false); }
    for q in 0..mv.k { s.g.toggle(mv.new[q].0, mv.new[q].1, true); }
    for q in 0..mv.k {
        let (u, v) = mv.old[q];
        s.edge_index[State::map_pos(u, v)] = NONE;
        s.edge_index[State::map_pos(v, u)] = NONE;
    }
    for q in 0..mv.k {
        let (u, v) = mv.new[q];
        s.edges[mv.idx[q]] = (u, v);
        s.edge_index[State::map_pos(u, v)] = mv.idx[q] as u16;
        s.edge_index[State::map_pos(v, u)] = mv.idx[q] as u16;
    }
}

fn undo_move(s: &mut State, mv: &Move) {
    for q in 0..mv.k { s.g.toggle(mv.new[q].0, mv.new[q].1, false); }
    for q in 0..mv.k { s.g.toggle(mv.old[q].0, mv.old[q].1, true); }
    for q in 0..mv.k {
        let (u, v) = mv.new[q];
        s.edge_index[State::map_pos(u, v)] = NONE;
        s.edge_index[State::map_pos(v, u)] = NONE;
    }
    for q in 0..mv.k {
        let (u, v) = mv.old[q];
        s.edges[mv.idx[q]] = (u, v);
        s.edge_index[State::map_pos(u, v)] = mv.idx[q] as u16;
        s.edge_index[State::map_pos(v, u)] = mv.idx[q] as u16;
    }
}

fn random_2switch(s: &State, rng: &mut Rng) -> Option<Move> {
    for _ in 0..24 {
        let i = rng.us(s.edges.len());
        let mut j = rng.us(s.edges.len() - 1);
        if j >= i { j += 1; }
        let (a, b) = s.edges[i];
        let (c, d) = s.edges[j];
        if a == c || a == d || b == c || b == d { continue; }
        let new = if rng.us(2) == 0 { [(a, c), (b, d)] } else { [(a, d), (b, c)] };
        if let Some(mv) = make_move(s, &[(a, b), (c, d)], &new) { return Some(mv); }
    }
    None
}

fn random_3switch(s: &State, rng: &mut Rng) -> Option<Move> {
    for _ in 0..40 {
        let ids = [rng.us(s.edges.len()), rng.us(s.edges.len()), rng.us(s.edges.len())];
        if ids[0] == ids[1] || ids[0] == ids[2] || ids[1] == ids[2] { continue; }
        let mut e = [s.edges[ids[0]], s.edges[ids[1]], s.edges[ids[2]]];
        for z in &mut e { if rng.us(2) == 1 { *z = (z.1, z.0); } }
        let all = [e[0].0, e[0].1, e[1].0, e[1].1, e[2].0, e[2].1];
        let mut distinct = true;
        for i in 0..6 { for j in 0..i { if all[i] == all[j] { distinct = false; } } }
        if !distinct { continue; }
        let new = if rng.us(2) == 0 {
            [(e[0].0, e[1].1), (e[1].0, e[2].1), (e[2].0, e[0].1)]
        } else {
            [(e[0].0, e[2].1), (e[2].0, e[1].1), (e[1].0, e[0].1)]
        };
        if let Some(mv) = make_move(s, &e, &new) { return Some(mv); }
    }
    None
}

fn mutable_neighbors(s: &State, u: usize) -> Vec<usize> {
    let mut bits = s.g.adj[u] & (!0u128 << O);
    let mut out = Vec::with_capacity(14);
    while bits != 0 {
        let v = bits.trailing_zeros() as usize;
        bits &= bits - 1;
        out.push(v);
    }
    out
}

fn push_limited(out: &mut Vec<Move>, mv: Option<Move>, cap: usize) {
    if out.len() < cap { if let Some(x) = mv { out.push(x); } }
}

// Add a requested nonedge by a 2-switch. Neighbour pairs are randomized by
// offsets; trying many alternatives is the local-delta candidate selection.
fn forced_add2(s: &State, u: usize, v: usize, rng: &mut Rng, out: &mut Vec<Move>, cap: usize) {
    if u < O || v < O || u == v || s.g.has(u, v) || out.len() >= cap { return; }
    let nu = mutable_neighbors(s, u);
    let nv = mutable_neighbors(s, v);
    if nu.is_empty() || nv.is_empty() { return; }
    let ou = rng.us(nu.len());
    let ov = rng.us(nv.len());
    for qi in 0..nu.len() {
        let a = nu[(qi + ou) % nu.len()];
        for qj in 0..nv.len() {
            let b = nv[(qj + ov) % nv.len()];
            if a == b || a == v || b == u { continue; }
            push_limited(out, make_move(s, &[(u, a), (v, b)], &[(u, v), (a, b)]), cap);
            if out.len() >= cap { return; }
        }
    }
}

// The same requested insertion via a 3-switch; this escapes cases where the
// closing a--b edge of every useful 2-switch already exists.
fn forced_add3(s: &State, u: usize, v: usize, rng: &mut Rng, out: &mut Vec<Move>, cap: usize) {
    if u < O || v < O || u == v || s.g.has(u, v) || out.len() >= cap { return; }
    let nu = mutable_neighbors(s, u);
    let nv = mutable_neighbors(s, v);
    if nu.is_empty() || nv.is_empty() { return; }
    for _ in 0..48 {
        let a = nu[rng.us(nu.len())];
        let b = nv[rng.us(nv.len())];
        let (c, d) = s.edges[rng.us(s.edges.len())];
        let all = [u, a, v, b, c, d];
        let mut distinct = true;
        for i in 0..6 { for j in 0..i { if all[i] == all[j] { distinct = false; } } }
        if !distinct { continue; }
        let old = [(u, a), (v, b), (c, d)];
        push_limited(out, make_move(s, &old, &[(u, v), (a, c), (b, d)]), cap);
        push_limited(out, make_move(s, &old, &[(u, v), (a, d), (b, c)]), cap);
        if out.len() >= cap { return; }
    }
}

fn forced_remove2(s: &State, u: usize, v: usize, rng: &mut Rng, out: &mut Vec<Move>, cap: usize) {
    if u < O || v < O || !s.g.has(u, v) || out.len() >= cap { return; }
    for _ in 0..64 {
        let (a, b) = s.edges[rng.us(s.edges.len())];
        if u == a || u == b || v == a || v == b { continue; }
        let old = [(u, v), (a, b)];
        push_limited(out, make_move(s, &old, &[(u, a), (v, b)]), cap);
        push_limited(out, make_move(s, &old, &[(u, b), (v, a)]), cap);
        if out.len() >= cap { return; }
    }
}

fn forced_remove3(s: &State, u: usize, v: usize, rng: &mut Rng, out: &mut Vec<Move>, cap: usize) {
    if u < O || v < O || !s.g.has(u, v) || out.len() >= cap { return; }
    for _ in 0..64 {
        let e1 = s.edges[rng.us(s.edges.len())];
        let e2 = s.edges[rng.us(s.edges.len())];
        let mut e = [(u, v), e1, e2];
        for z in &mut e[1..] { if rng.us(2) == 1 { *z = (z.1, z.0); } }
        let all = [e[0].0, e[0].1, e[1].0, e[1].1, e[2].0, e[2].1];
        let mut distinct = true;
        for i in 0..6 { for j in 0..i { if all[i] == all[j] { distinct = false; } } }
        if !distinct { continue; }
        push_limited(out, make_move(s, &e, &[(e[0].0, e[1].1), (e[1].0, e[2].1), (e[2].0, e[0].1)]), cap);
        push_limited(out, make_move(s, &e, &[(e[0].0, e[2].1), (e[2].0, e[1].1), (e[1].0, e[0].1)]), cap);
        if out.len() >= cap { return; }
    }
}

fn choose_bad_pair(s: &State, rng: &mut Rng) -> Option<(usize, usize, i16)> {
    // Tournament sampling is much cheaper than rebuilding a violation list on
    // every move. A deterministic fallback prevents starvation near a solution.
    let mut best = None;
    let mut best_key = 0i64;
    for _ in 0..96 {
        let u = rng.us(N - 1);
        let v = u + 1 + rng.us(N - u - 1);
        let r = s.g.residual(u, v);
        if r == 0 { continue; }
        let cat_w = if u < O && v >= O { s.g.io_weight } else { 1 };
        let key = (r as i64).abs() * cat_w * 16 + rng.us(16) as i64;
        if key > best_key { best_key = key; best = Some((u, v, r)); }
    }
    if best.is_some() { return best; }
    let start = rng.us(N * (N - 1) / 2);
    for q in 0..N * (N - 1) / 2 {
        let mut z = (start + q) % (N * (N - 1) / 2);
        let mut u = 0;
        while z >= N - u - 1 { z -= N - u - 1; u += 1; }
        let v = u + 1 + z;
        let r = s.g.residual(u, v);
        if r != 0 { return Some((u, v, r)); }
    }
    None
}

fn targeted_candidates(s: &State, pair: (usize, usize, i16), rng: &mut Rng) -> Vec<Move> {
    let (u, v, r) = pair;
    let cap = 56usize;
    let mut out = Vec::with_capacity(cap);
    if r < 0 {
        if u >= O && !s.g.has(u, v) {
            forced_add2(s, u, v, rng, &mut out, cap);
            forced_add3(s, u, v, rng, &mut out, cap);
        }
        // Add an outer common neighbour. One of the two incident edges may be
        // fixed scaffold data; only the missing outer--outer edge is requested.
        let off = rng.us(M);
        for q in 0..M {
            let w = O + (q + off) % M;
            if w == u || w == v { continue; }
            let uw = s.g.has(u, w);
            let vw = s.g.has(v, w);
            if uw && !vw && v >= O {
                forced_add2(s, v, w, rng, &mut out, cap);
                if out.len() < cap / 2 { forced_add3(s, v, w, rng, &mut out, cap); }
            } else if vw && !uw && u >= O {
                forced_add2(s, u, w, rng, &mut out, cap);
                if out.len() < cap / 2 { forced_add3(s, u, w, rng, &mut out, cap); }
            }
            if out.len() >= cap { break; }
        }
    } else {
        if u >= O && s.g.has(u, v) {
            forced_remove2(s, u, v, rng, &mut out, cap);
            forced_remove3(s, u, v, rng, &mut out, cap);
        }
        let common = s.g.adj[u] & s.g.adj[v] & (!0u128 << O);
        let mut ws = Vec::new();
        let mut bits = common;
        while bits != 0 {
            let w = bits.trailing_zeros() as usize;
            bits &= bits - 1;
            ws.push(w);
        }
        // Shuffle the usually tiny common-neighbour list.
        for i in (1..ws.len()).rev() { let j = rng.us(i + 1); ws.swap(i, j); }
        for w in ws {
            if u >= O {
                forced_remove2(s, u, w, rng, &mut out, cap);
                if out.len() < cap / 2 { forced_remove3(s, u, w, rng, &mut out, cap); }
            }
            if v >= O {
                forced_remove2(s, v, w, rng, &mut out, cap);
                if out.len() < cap / 2 { forced_remove3(s, v, w, rng, &mut out, cap); }
            }
            if out.len() >= cap { break; }
        }
    }
    // Retain a little unbiased connectivity of the regular-graph state space.
    for _ in 0..4 {
        if let Some(mv) = random_2switch(s, rng) { push_limited(&mut out, Some(mv), cap); }
    }
    out
}

fn best_candidate(s: &mut State, candidates: &[Move], rng: &mut Rng, temperature: f64) -> Option<(Move, i64, i64)> {
    let before = s.g.guided;
    let before_global = s.g.energy;
    let mut selected = None;
    let mut selected_rank = f64::INFINITY;
    let mut selected_dg = 0;
    let mut selected_de = 0;
    for mv in candidates {
        apply_move(s, mv);
        let dg = s.g.guided - before;
        let de = s.g.energy - before_global;
        // Gumbel perturbation avoids every thread following the same steepest
        // trajectory while still using exact local deltas.
        let u = rng.unit().clamp(1e-12, 1.0 - 1e-12);
        let noise = -(-u.ln()).ln() * temperature.max(0.05);
        let rank = dg as f64 - noise;
        undo_move(s, mv);
        if rank < selected_rank {
            selected_rank = rank;
            selected = Some(*mv);
            selected_dg = dg;
            selected_de = de;
        }
    }
    selected.map(|mv| (mv, selected_dg, selected_de))
}

fn publish(
    id: usize, step: u64, s: &State,
    global_best: &AtomicI64, best: &Mutex<Option<State>>,
    io_best: &AtomicI64, best_io: &Mutex<Option<State>>,
    stop: &AtomicBool,
) {
    let old = global_best.fetch_min(s.g.energy, Ordering::Relaxed);
    if s.g.energy < old {
        let mut lock = best.lock().unwrap();
        if lock.as_ref().map_or(true, |q| s.g.energy < q.g.energy) { *lock = Some(s.clone()); }
        if s.g.energy < old - 3 || s.g.energy < 1000 {
            eprintln!("worker={id} step={step} best={} io={} oo={} guided={} w={}",
                s.g.energy, s.g.io_energy, s.g.oo_energy, s.g.guided, s.g.io_weight);
        }
        if s.g.energy == 0 {
            s.validate();
            stop.store(true, Ordering::Relaxed);
        }
    }
    let old_io = io_best.fetch_min(s.g.io_energy, Ordering::Relaxed);
    if s.g.io_energy <= old_io {
        let mut lock = best_io.lock().unwrap();
        let old_total_at_level = lock.as_ref().filter(|q| q.g.io_energy == s.g.io_energy)
            .map_or(i64::MAX, |q| q.g.energy);
        let is_better = lock.as_ref().map_or(true, |q| {
            s.g.io_energy < q.g.io_energy ||
            (s.g.io_energy == q.g.io_energy && s.g.energy < q.g.energy)
        });
        if is_better { *lock = Some(s.clone()); }
        if is_better && (s.g.io_energy < old_io - 3 ||
                         (s.g.io_energy == 0 && s.g.energy < old_total_at_level - 20)) {
            eprintln!("worker={id} step={step} io_best={} total={} oo={} w={}",
                s.g.io_energy, s.g.energy, s.g.oo_energy, s.g.io_weight);
        }
    }
}

fn kick(s: &mut State, rng: &mut Rng, count: usize) {
    for _ in 0..count {
        let mv = if rng.us(4) == 0 { random_3switch(s, rng) } else { random_2switch(s, rng) };
        if let Some(mv) = mv { apply_move(s, &mv); }
    }
}

fn worker(
    id: usize, deadline: Instant, base: Option<State>, global_best: Arc<AtomicI64>,
    best: Arc<Mutex<Option<State>>>, io_best: Arc<AtomicI64>,
    best_io: Arc<Mutex<Option<State>>>, stop: Arc<AtomicBool>,
) {
    let nanos = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64;
    let mut rng = Rng::new(nanos ^ ((id as u64 + 1).wrapping_mul(0x9e37_79b9_7f4a_7c15)));
    let weights = [
        1i64, 1, 2, 2, 3, 3, 5, 5, 8, 8, 13, 13, 21, 21, 34, 34,
        55, 55, 89, 89, 144, 144, 233, 233, 377, 377, 610, 610, 987, 987, 1597, 2584,
    ];
    let mut restart = 0usize;
    let mut total_steps = 0u64;
    while Instant::now() < deadline && !stop.load(Ordering::Relaxed) {
        let w = weights[(id + restart) % weights.len()];
        let mut s = if let Some(ref q) = base {
            let mut z = q.clone();
            z.g.set_io_weight(w);
            // Different basin per worker/restart while retaining the good seed.
            kick(&mut z, &mut rng, 8 + (id * 7 + restart * 19) % 180);
            z
        } else { random_state(&mut rng, w) };
        publish(id, total_steps, &s, &global_best, &best, &io_best, &best_io, &stop);
        let mut local_best = s.clone();
        let mut last_improve = 0usize;
        let epoch_len = 32_768usize;
        for step in 0..600_000usize {
            total_steps += 1;
            if step & 0xfff == 0 {
                if Instant::now() >= deadline || stop.load(Ordering::Relaxed) { break; }
                let (e, gd, io, oo) = s.g.recalc();
                assert_eq!((s.g.energy, s.g.guided, s.g.io_energy, s.g.oo_energy), (e, gd, io, oo));
            }
            let phase = (step % epoch_len) as f64 / epoch_len as f64;
            let temp_hi = if w == 1 { 7.0 } else { 10.0 + w as f64 };
            let temperature = temp_hi * (0.12f64 / temp_hi).powf(phase);
            let Some(pair) = choose_bad_pair(&s, &mut rng) else {
                publish(id, total_steps, &s, &global_best, &best, &io_best, &best_io, &stop);
                break;
            };
            let candidates = targeted_candidates(&s, pair, &mut rng);
            let chosen = if candidates.is_empty() {
                random_3switch(&s, &mut rng).map(|mv| (mv, 0, 0))
            } else { best_candidate(&mut s, &candidates, &mut rng, temperature) };
            let Some((mv, mut dg, _de)) = chosen else { continue; };
            if candidates.is_empty() {
                let old = s.g.guided;
                apply_move(&mut s, &mv);
                dg = s.g.guided - old;
                undo_move(&mut s, &mv);
            }
            let accept = dg <= 0 || rng.unit() < (-(dg as f64) / temperature).exp();
            if accept {
                apply_move(&mut s, &mv);
                if s.g.guided < local_best.g.guided ||
                   (s.g.guided == local_best.g.guided && s.g.energy < local_best.g.energy) {
                    local_best = s.clone();
                    last_improve = step;
                }
                publish(id, total_steps, &s, &global_best, &best, &io_best, &best_io, &stop);
            }
            if step > 0 && step % epoch_len == epoch_len - 1 {
                // Cyclic annealing: return to the epoch record, then cross the
                // basin boundary with a short mixture of 2- and 3-switches.
                s = local_best.clone();
                let kick_count = 3 + rng.us(10);
                kick(&mut s, &mut rng, kick_count);
            }
            if step.saturating_sub(last_improve) > 180_000 { break; }
        }
        restart += 1;
    }
}

fn diagnostics(s: &State) -> (usize, usize, [usize; 9]) {
    let mut bad = 0usize;
    let mut max_abs = 0usize;
    let mut histogram = [0usize; 9]; // residuals -4..4, clamped
    for u in 0..N {
        assert_eq!(s.g.adj[u].count_ones(), 14);
        for v in u + 1..N {
            let r = s.g.residual(u, v);
            if r != 0 { bad += 1; }
            max_abs = max_abs.max(r.unsigned_abs() as usize);
            histogram[(r + 4).clamp(0, 8) as usize] += 1;
        }
    }
    (bad, max_abs, histogram)
}

fn save(path: &str, s: &State) {
    s.validate();
    let (bad, max_abs, histogram) = diagnostics(s);
    let (e, guided, io, oo) = s.g.recalc();
    let mut out = format!(
        "{{\n  \"energy\": {e},\n  \"recomputed_energy\": {e},\n  \"io_energy\": {io},\n  \"oo_energy\": {oo},\n  \"guided_energy\": {guided},\n  \"io_weight\": {},\n  \"bad_pairs\": {bad},\n  \"max_abs_residual\": {max_abs},\n  \"residual_histogram_minus4_to_plus4\": {:?},\n  \"edge_count\": 693,\n  \"edges\": [\n",
        s.g.io_weight, histogram
    );
    let mut first = true;
    for u in 0..N {
        for v in u + 1..N {
            if s.g.has(u, v) {
                if !first { out.push_str(",\n"); }
                first = false;
                out.push_str(&format!("    [{}, {}]", u + 1, v + 1));
            }
        }
    }
    out.push_str("\n  ]\n}\n");
    fs::write(path, out).unwrap();
    println!("BEST energy={e} io={io} oo={oo} bad_pairs={bad} max_residual={max_abs} edges=693");
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let seconds = args.get(1).and_then(|x| x.parse().ok()).unwrap_or(120u64);
    let threads = args.get(2).and_then(|x| x.parse().ok()).unwrap_or_else(||
        thread::available_parallelism().map_or(1, usize::from));
    let seed_path = args.get(3).map(String::as_str).unwrap_or("scratch_general_v2_best.json");
    let output_path = args.get(4).map(String::as_str).unwrap_or("scratch_general_v2_best.json");
    let io_output_path = args.get(5).map(String::as_str).unwrap_or("scratch_general_v2_io_best.json");
    let base = load_seed(seed_path, 1).or_else(|| load_seed("scratch_general_best.json", 1));
    if let Some(ref s) = base {
        let (bad, max_abs, _) = diagnostics(s);
        eprintln!("seed={} energy={} io={} oo={} bad={} max={}", seed_path,
            s.g.energy, s.g.io_energy, s.g.oo_energy, bad, max_abs);
    } else { eprintln!("no valid seed; starting from randomized circulants"); }
    let deadline = Instant::now() + Duration::from_secs(seconds);
    let global_best = Arc::new(AtomicI64::new(i64::MAX));
    let best = Arc::new(Mutex::new(base.clone()));
    if let Some(ref s) = base { global_best.store(s.g.energy, Ordering::Relaxed); }
    let io_best = Arc::new(AtomicI64::new(i64::MAX));
    let best_io = Arc::new(Mutex::new(base.clone()));
    if let Some(ref s) = base { io_best.store(s.g.io_energy, Ordering::Relaxed); }
    let stop = Arc::new(AtomicBool::new(false));
    let mut handles = Vec::new();
    for id in 0..threads {
        let (gb, b, ib, bi, st, seed) = (
            global_best.clone(), best.clone(), io_best.clone(), best_io.clone(), stop.clone(), base.clone());
        handles.push(thread::spawn(move || worker(id, deadline, seed, gb, b, ib, bi, st)));
    }
    for h in handles { h.join().unwrap(); }
    let answer = best.lock().unwrap().clone();
    if let Some(ref s) = answer {
        save(output_path, s);
        if s.g.energy == 0 { println!("SOLUTION"); }
    } else { println!("NO_STATE"); }
    let io_answer = best_io.lock().unwrap().clone();
    if let Some(ref s) = io_answer {
        save(io_output_path, s);
    }
}
