// Large-neighbourhood / exhaustive 2-switch search layered on the independently
// checked unrestricted rooted search engine.  This file deliberately includes
// the engine as a module so that its incremental common-neighbour accounting is
// reused without changing the original experiment.
mod engine {
    include!("scratch_general_v2_search.rs");

    fn steepest_2switch(s: &mut State, rng: &mut Rng) -> Option<i64> {
        let before = s.g.energy;
        let mut best_delta = 0i64;
        let mut best: Option<Move> = None;
        let edge_count = s.edges.len();
        for i in 0..edge_count {
            let (a, b) = s.edges[i];
            for j in i + 1..edge_count {
                let (c, d) = s.edges[j];
                if a == c || a == d || b == c || b == d { continue; }
                for new_edges in [[(a, c), (b, d)], [(a, d), (b, c)]] {
                    let Some(mv) = make_move(s, &[(a, b), (c, d)], &new_edges) else { continue; };
                    apply_move(s, &mv);
                    let delta = s.g.energy - before;
                    undo_move(s, &mv);
                    if delta < best_delta || (delta == best_delta && delta < 0 && rng.us(8) == 0) {
                        best_delta = delta;
                        best = Some(mv);
                    }
                }
            }
        }
        if let Some(mv) = best {
            apply_move(s, &mv);
            debug_assert_eq!(s.g.energy, before + best_delta);
            Some(best_delta)
        } else {
            None
        }
    }

    // A much broader sampled 3-switch neighbourhood than the original
    // bad-pair proposal.  It is used both as descent and as a shallow barrier
    // crossing at exhaustive 2-switch local minima.
    fn best_sampled_3switch(
        s: &mut State,
        rng: &mut Rng,
        samples: usize,
        allow_uphill: i64,
    ) -> Option<(Move, i64)> {
        let before = s.g.energy;
        let mut best_delta = i64::MAX;
        let mut best = None;
        for _ in 0..samples {
            let Some(mv) = random_3switch(s, rng) else { continue; };
            apply_move(s, &mv);
            let delta = s.g.energy - before;
            undo_move(s, &mv);
            if delta < best_delta || (delta == best_delta && rng.us(8) == 0) {
                best_delta = delta;
                best = Some(mv);
            }
        }
        best.filter(|_| best_delta <= allow_uphill).map(|mv| (mv, best_delta))
    }

    fn descend(s: &mut State, rng: &mut Rng, deadline: Instant) {
        loop {
            if Instant::now() >= deadline { break; }
            if steepest_2switch(s, rng).is_some() { continue; }
            if let Some((mv, delta)) = best_sampled_3switch(s, rng, 30_000, -1) {
                apply_move(s, &mv);
                debug_assert!(delta < 0);
                continue;
            }
            break;
        }
    }

    pub fn run_lns() {
        let args: Vec<String> = std::env::args().collect();
        let seconds = args.get(1).and_then(|x| x.parse().ok()).unwrap_or(180u64);
        let threads = args.get(2).and_then(|x| x.parse().ok()).unwrap_or_else(||
            thread::available_parallelism().map_or(1, usize::from));
        let seed_path = args.get(3).map(String::as_str).unwrap_or("scratch_general_v2_best.json");
        let output_path = args.get(4).map(String::as_str).unwrap_or("scratch_general_lns_best.json");
        let seed = load_seed(seed_path, 1).expect("valid regular rooted seed");
        eprintln!("seed energy={} io={} oo={}", seed.g.energy, seed.g.io_energy, seed.g.oo_energy);

        let deadline = Instant::now() + Duration::from_secs(seconds);
        let best = Arc::new(Mutex::new(seed.clone()));
        let best_energy = Arc::new(AtomicI64::new(seed.g.energy));
        let stop = Arc::new(AtomicBool::new(false));
        let mut handles = Vec::new();
        for id in 0..threads {
            let base = seed.clone();
            let shared = best.clone();
            let global = best_energy.clone();
            let halt = stop.clone();
            handles.push(thread::spawn(move || {
                let nanos = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64;
                let mut rng = Rng::new(nanos ^ ((id as u64 + 17).wrapping_mul(0x9e37_79b9_7f4a_7c15)));
                let mut round = 0usize;
                while Instant::now() < deadline && !halt.load(Ordering::Relaxed) {
                    let incumbent = shared.lock().unwrap().clone();
                    let mut s = if round == 0 && id == 0 { incumbent } else {
                        let mut q = if rng.us(3) == 0 { base.clone() } else { incumbent };
                        // Ruin between roughly 1% and 12% of the mutable edges.
                        let kicks = 5 + rng.us(56);
                        kick(&mut q, &mut rng, kicks);
                        q
                    };
                    descend(&mut s, &mut rng, deadline);
                    let old = global.fetch_min(s.g.energy, Ordering::Relaxed);
                    if s.g.energy < old {
                        s.validate();
                        *shared.lock().unwrap() = s.clone();
                        eprintln!("worker={id} round={round} BEST={} io={} oo={}",
                            s.g.energy, s.g.io_energy, s.g.oo_energy);
                        if s.g.energy == 0 { halt.store(true, Ordering::Relaxed); }
                    }
                    // Barrier crossing from the local optimum, retaining only
                    // shallow transitions before another exact descent.
                    if Instant::now() < deadline {
                        let mut q = s;
                        if let Some((mv, _)) = best_sampled_3switch(&mut q, &mut rng, 80_000, 12) {
                            apply_move(&mut q, &mv);
                            descend(&mut q, &mut rng, deadline);
                            let old = global.fetch_min(q.g.energy, Ordering::Relaxed);
                            if q.g.energy < old {
                                q.validate();
                                *shared.lock().unwrap() = q.clone();
                                eprintln!("worker={id} round={round} BRIDGE_BEST={} io={} oo={}",
                                    q.g.energy, q.g.io_energy, q.g.oo_energy);
                                if q.g.energy == 0 { halt.store(true, Ordering::Relaxed); }
                            }
                        }
                    }
                    round += 1;
                }
            }));
        }
        for h in handles { h.join().unwrap(); }
        let answer = best.lock().unwrap().clone();
        answer.validate();
        save(output_path, &answer);
        if answer.g.energy == 0 { println!("SOLUTION"); }
    }
}

fn main() { engine::run_lns(); }
