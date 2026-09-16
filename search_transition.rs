use std::sync::{
    atomic::{AtomicBool, AtomicI64, Ordering},
    Arc, Mutex,
};
use std::thread;
use std::time::{Duration, Instant};

const N: usize = 99;
const OUTER0: usize = 15;

#[derive(Clone)]
struct Rng(u64);

impl Rng {
    fn new(seed: u64) -> Self {
        Self(seed | 1)
    }

    fn next_u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x2545_f491_4f6c_dd1d)
    }

    fn usize(&mut self, n: usize) -> usize {
        (self.next_u64() as usize) % n
    }

    fn unit(&mut self) -> f64 {
        ((self.next_u64() >> 11) as f64) * (1.0 / ((1_u64 << 53) as f64))
    }
}

#[derive(Clone)]
struct Block {
    p: usize,
    q: usize,
    perm: [u8; 4],
}

#[derive(Clone)]
struct Graph {
    adj: [[u64; 2]; N],
    common: [[u8; N]; N],
    energy: i64,
}

impl Graph {
    fn empty() -> Self {
        Self {
            adj: [[0; 2]; N],
            common: [[0; N]; N],
            energy: 0,
        }
    }

    fn adjacent(&self, u: usize, v: usize) -> bool {
        ((self.adj[u][v >> 6] >> (v & 63)) & 1) != 0
    }

    fn set_raw(&mut self, u: usize, v: usize, value: bool) {
        let mask_v = 1_u64 << (v & 63);
        let mask_u = 1_u64 << (u & 63);
        if value {
            self.adj[u][v >> 6] |= mask_v;
            self.adj[v][u >> 6] |= mask_u;
        } else {
            self.adj[u][v >> 6] &= !mask_v;
            self.adj[v][u >> 6] &= !mask_u;
        }
    }

    fn pair_energy(&self, u: usize, v: usize) -> i64 {
        let x = self.common[u][v] as i64 + self.adjacent(u, v) as i64 - 2;
        x * x
    }

    fn adjust_common(&mut self, u: usize, v: usize, delta: i8) {
        if u == v {
            return;
        }
        let (a, b) = if u < v { (u, v) } else { (v, u) };
        self.energy -= self.pair_energy(a, b);
        let next = self.common[a][b] as i16 + delta as i16;
        debug_assert!(next >= 0);
        self.common[a][b] = next as u8;
        self.common[b][a] = next as u8;
        self.energy += self.pair_energy(a, b);
    }

    fn for_each_neighbor<F: FnMut(usize)>(&self, u: usize, mut f: F) {
        for word in 0..2 {
            let mut bits = self.adj[u][word];
            while bits != 0 {
                let bit = bits.trailing_zeros() as usize;
                let v = (word << 6) + bit;
                if v < N {
                    f(v);
                }
                bits &= bits - 1;
            }
        }
    }

    fn toggle_edge(&mut self, u: usize, v: usize, add: bool) {
        debug_assert!(u != v);
        debug_assert!(self.adjacent(u, v) != add);
        if add {
            let mut nv = [usize::MAX; 32];
            let mut nu = [usize::MAX; 32];
            let mut cv = 0;
            let mut cu = 0;
            self.for_each_neighbor(v, |w| {
                nv[cv] = w;
                cv += 1;
            });
            self.for_each_neighbor(u, |w| {
                nu[cu] = w;
                cu += 1;
            });
            for &w in &nv[..cv] {
                self.adjust_common(u, w, 1);
            }
            for &w in &nu[..cu] {
                self.adjust_common(v, w, 1);
            }
            self.energy -= self.pair_energy(u.min(v), u.max(v));
            self.set_raw(u, v, true);
            self.energy += self.pair_energy(u.min(v), u.max(v));
        } else {
            self.energy -= self.pair_energy(u.min(v), u.max(v));
            self.set_raw(u, v, false);
            self.energy += self.pair_energy(u.min(v), u.max(v));
            let mut nv = [usize::MAX; 32];
            let mut nu = [usize::MAX; 32];
            let mut cv = 0;
            let mut cu = 0;
            self.for_each_neighbor(v, |w| {
                nv[cv] = w;
                cv += 1;
            });
            self.for_each_neighbor(u, |w| {
                nu[cu] = w;
                cu += 1;
            });
            for &w in &nv[..cv] {
                self.adjust_common(u, w, -1);
            }
            for &w in &nu[..cu] {
                self.adjust_common(v, w, -1);
            }
        }
    }

    fn initialize_common_and_energy(&mut self) {
        for u in 0..N {
            for v in (u + 1)..N {
                let c = (self.adj[u][0] & self.adj[v][0]).count_ones()
                    + (self.adj[u][1] & self.adj[v][1]).count_ones();
                self.common[u][v] = c as u8;
                self.common[v][u] = c as u8;
            }
        }
        self.energy = 0;
        for u in 0..N {
            for v in (u + 1)..N {
                self.energy += self.pair_energy(u, v);
            }
        }
    }

    fn check(&self) -> bool {
        for u in 0..N {
            let d = self.adj[u][0].count_ones() + self.adj[u][1].count_ones();
            if d != 14 {
                return false;
            }
            for v in (u + 1)..N {
                let c = (self.adj[u][0] & self.adj[v][0]).count_ones()
                    + (self.adj[u][1] & self.adj[v][1]).count_ones();
                let target = if self.adjacent(u, v) { 1 } else { 2 };
                if c != target {
                    return false;
                }
            }
        }
        true
    }
}

fn base_pairs() -> Vec<(usize, usize)> {
    let mut pairs = Vec::new();
    for a in 0..7 {
        for b in (a + 1)..7 {
            pairs.push((a, b));
        }
    }
    pairs
}

fn outer(p: usize, state: usize) -> usize {
    OUTER0 + 4 * p + state
}

fn random_blocks(rng: &mut Rng, pairs: &[(usize, usize)]) -> Vec<Block> {
    let mut blocks = Vec::new();
    for p in 0..pairs.len() {
        for q in (p + 1)..pairs.len() {
            let (a, b) = pairs[p];
            let (c, d) = pairs[q];
            if a == c || a == d || b == c || b == d {
                continue;
            }
            let mut perm = [0_u8, 1, 2, 3];
            for i in (1..4).rev() {
                let j = rng.usize(i + 1);
                perm.swap(i, j);
            }
            blocks.push(Block { p, q, perm });
        }
    }
    assert_eq!(blocks.len(), 105);
    blocks
}

fn build_graph(pairs: &[(usize, usize)], blocks: &[Block]) -> Graph {
    let mut g = Graph::empty();
    for s in 0..14 {
        g.set_raw(0, 1 + s, true);
    }
    for group in 0..7 {
        g.set_raw(1 + 2 * group, 1 + 2 * group + 1, true);
    }
    for (p, &(a, b)) in pairs.iter().enumerate() {
        for state in 0..4 {
            let u = outer(p, state);
            let sa = state & 1;
            let sb = (state >> 1) & 1;
            g.set_raw(u, 1 + 2 * a + sa, true);
            g.set_raw(u, 1 + 2 * b + sb, true);
            if state < (state ^ 1) {
                g.set_raw(u, outer(p, state ^ 1), true);
            }
            if state < (state ^ 2) {
                g.set_raw(u, outer(p, state ^ 2), true);
            }
        }
    }
    for block in blocks {
        for s in 0..4 {
            g.set_raw(outer(block.p, s), outer(block.q, block.perm[s] as usize), true);
        }
    }
    g.initialize_common_and_energy();
    g
}

fn apply_swap(g: &mut Graph, block: &Block, a: usize, b: usize) {
    let va = block.perm[a] as usize;
    let vb = block.perm[b] as usize;
    let ua = outer(block.p, a);
    let ub = outer(block.p, b);
    let wa = outer(block.q, va);
    let wb = outer(block.q, vb);
    g.toggle_edge(ua, wa, false);
    g.toggle_edge(ub, wb, false);
    g.toggle_edge(ua, wb, true);
    g.toggle_edge(ub, wa, true);
}

fn print_solution(g: &Graph) {
    println!("SOLUTION_BEGIN");
    for u in 0..N {
        for v in (u + 1)..N {
            if g.adjacent(u, v) {
                println!("{{{}, {}}}", u + 1, v + 1);
            }
        }
    }
    println!("SOLUTION_END");
}

fn worker(
    id: usize,
    deadline: Instant,
    stop: Arc<AtomicBool>,
    global_best: Arc<AtomicI64>,
    solution: Arc<Mutex<Option<Graph>>>,
) {
    let pairs = base_pairs();
    let mut rng = Rng::new(
        0x9e37_79b9_7f4a_7c15_u64
            ^ (id as u64).wrapping_mul(0xd1b5_4a32_d192_ed03)
            ^ Instant::now().elapsed().as_nanos() as u64,
    );
    let mut restart = 0_u64;
    while Instant::now() < deadline && !stop.load(Ordering::Relaxed) {
        restart += 1;
        let mut blocks = random_blocks(&mut rng, &pairs);
        let mut g = build_graph(&pairs, &blocks);
        let mut local_best = g.energy;
        let mut stagnant = 0_u64;
        let moves_per_restart = 2_000_000_u64;
        for step in 0..moves_per_restart {
            if (step & 0x3fff) == 0
                && (Instant::now() >= deadline || stop.load(Ordering::Relaxed))
            {
                return;
            }
            let bi = rng.usize(blocks.len());
            let a = rng.usize(4);
            let mut b = rng.usize(3);
            if b >= a {
                b += 1;
            }
            let old = g.energy;
            apply_swap(&mut g, &blocks[bi], a, b);
            let delta = g.energy - old;
            let phase = (step % 200_000) as f64 / 200_000.0;
            let temperature = 7.0 * (1.0 - phase) + 0.12;
            let accept = delta <= 0 || rng.unit() < (-(delta as f64) / temperature).exp();
            if accept {
                blocks[bi].perm.swap(a, b);
                if g.energy < local_best {
                    local_best = g.energy;
                    stagnant = 0;
                    let previous = global_best.fetch_min(g.energy, Ordering::Relaxed);
                    if g.energy < previous {
                        eprintln!(
                            "worker={id} restart={restart} step={step} best_energy={}",
                            g.energy
                        );
                    }
                    if g.energy == 0 {
                        assert!(g.check());
                        *solution.lock().unwrap() = Some(g.clone());
                        stop.store(true, Ordering::Relaxed);
                        return;
                    }
                } else {
                    stagnant += 1;
                }
            } else {
                let va = blocks[bi].perm[a] as usize;
                let vb = blocks[bi].perm[b] as usize;
                let ua = outer(blocks[bi].p, a);
                let ub = outer(blocks[bi].p, b);
                let wa = outer(blocks[bi].q, va);
                let wb = outer(blocks[bi].q, vb);
                g.toggle_edge(ua, wb, false);
                g.toggle_edge(ub, wa, false);
                g.toggle_edge(ua, wa, true);
                g.toggle_edge(ub, wb, true);
                debug_assert_eq!(g.energy, old);
                stagnant += 1;
            }
            if stagnant > 500_000 && phase > 0.8 {
                break;
            }
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let seconds: u64 = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(120);
    let threads: usize = args
        .get(2)
        .and_then(|s| s.parse().ok())
        .unwrap_or_else(|| thread::available_parallelism().map_or(1, usize::from));
    let deadline = Instant::now() + Duration::from_secs(seconds);
    let stop = Arc::new(AtomicBool::new(false));
    let global_best = Arc::new(AtomicI64::new(i64::MAX));
    let solution: Arc<Mutex<Option<Graph>>> = Arc::new(Mutex::new(None));
    let mut handles = Vec::new();
    for id in 0..threads {
        let stop = Arc::clone(&stop);
        let best = Arc::clone(&global_best);
        let solution = Arc::clone(&solution);
        handles.push(thread::spawn(move || worker(id, deadline, stop, best, solution)));
    }
    for handle in handles {
        handle.join().unwrap();
    }
    let guard = solution.lock().unwrap();
    if let Some(g) = guard.as_ref() {
        assert!(g.check());
        print_solution(g);
    } else {
        println!(
            "NO_SOLUTION_IN_RUN best_energy={}",
            global_best.load(Ordering::Relaxed)
        );
    }
}
