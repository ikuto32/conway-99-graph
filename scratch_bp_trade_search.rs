mod engine {
    include!("scratch_general_v2_search.rs");

    use std::collections::HashMap;

    #[derive(Clone, Copy)]
    struct Balance {
        a: [usize; 2],
        b: [usize; 2],
    }

    #[derive(Clone, Copy)]
    struct Trade8 {
        old: [Edge; 8],
        new: [Edge; 8],
        idx: [usize; 8],
    }

    fn label_signature(g: &Graph, a: usize, b: usize) -> u32 {
        let mut code = 0u32;
        let mut place = 1u32;
        for symbol in 0..14 {
            let inner = 1 + symbol;
            let count = g.has(a, inner) as u32 + g.has(b, inner) as u32;
            code += count * place;
            place *= 3;
        }
        code
    }

    // A balance is two distinct pairs of outer labels with the same incidence
    // sum.  Swapping complete 2x2 blocks between two balances preserves every
    // BP row exactly, in both endpoint classes.
    fn balances(g: &Graph) -> Vec<Balance> {
        let mut classes: HashMap<u32, Vec<[usize; 2]>> = HashMap::new();
        for a in O..N {
            for b in a + 1..N {
                classes.entry(label_signature(g, a, b)).or_default().push([a, b]);
            }
        }
        let mut out = Vec::new();
        for pairs in classes.values() {
            for i in 0..pairs.len() {
                for j in i + 1..pairs.len() {
                    let p = pairs[i];
                    let q = pairs[j];
                    if p[0] != q[0] && p[0] != q[1] && p[1] != q[0] && p[1] != q[1] {
                        out.push(Balance { a: p, b: q });
                    }
                }
            }
        }
        out
    }

    fn block(a: [usize; 2], b: [usize; 2]) -> [Edge; 4] {
        [canon(a[0], b[0]), canon(a[0], b[1]),
         canon(a[1], b[0]), canon(a[1], b[1])]
    }

    fn make_trade(s: &State, r: Balance, c: Balance) -> Option<Trade8> {
        let vertices = [r.a[0], r.a[1], r.b[0], r.b[1],
                        c.a[0], c.a[1], c.b[0], c.b[1]];
        for i in 0..8 { for j in 0..i { if vertices[i] == vertices[j] { return None; } } }
        let ac = block(r.a, c.a);
        let bd = block(r.b, c.b);
        let ad = block(r.a, c.b);
        let bc = block(r.b, c.a);
        let diag = ac.iter().chain(bd.iter()).all(|&(u,v)| s.g.has(u,v))
            && ad.iter().chain(bc.iter()).all(|&(u,v)| !s.g.has(u,v));
        let cross = ad.iter().chain(bc.iter()).all(|&(u,v)| s.g.has(u,v))
            && ac.iter().chain(bd.iter()).all(|&(u,v)| !s.g.has(u,v));
        if !diag && !cross { return None; }
        let (old_blocks, new_blocks) = if diag { ((ac,bd),(ad,bc)) } else { ((ad,bc),(ac,bd)) };
        let mut old = [(0,0);8];
        let mut new = [(0,0);8];
        old[..4].copy_from_slice(&old_blocks.0);
        old[4..].copy_from_slice(&old_blocks.1);
        new[..4].copy_from_slice(&new_blocks.0);
        new[4..].copy_from_slice(&new_blocks.1);
        let mut idx = [0usize;8];
        for q in 0..8 { idx[q] = s.edge_id(old[q].0, old[q].1)?; }
        Some(Trade8 { old, new, idx })
    }

    fn apply_trade(s: &mut State, t: &Trade8) {
        for &(u,v) in &t.old { s.g.toggle(u,v,false); }
        for &(u,v) in &t.new { s.g.toggle(u,v,true); }
        for &(u,v) in &t.old {
            s.edge_index[State::map_pos(u,v)] = NONE;
            s.edge_index[State::map_pos(v,u)] = NONE;
        }
        for q in 0..8 {
            let (u,v) = t.new[q];
            s.edges[t.idx[q]] = (u,v);
            s.edge_index[State::map_pos(u,v)] = t.idx[q] as u16;
            s.edge_index[State::map_pos(v,u)] = t.idx[q] as u16;
        }
    }

    fn undo_trade(s: &mut State, t: &Trade8) {
        for &(u,v) in &t.new { s.g.toggle(u,v,false); }
        for &(u,v) in &t.old { s.g.toggle(u,v,true); }
        for &(u,v) in &t.new {
            s.edge_index[State::map_pos(u,v)] = NONE;
            s.edge_index[State::map_pos(v,u)] = NONE;
        }
        for q in 0..8 {
            let (u,v) = t.old[q];
            s.edges[t.idx[q]] = (u,v);
            s.edge_index[State::map_pos(u,v)] = t.idx[q] as u16;
            s.edge_index[State::map_pos(v,u)] = t.idx[q] as u16;
        }
    }

    fn available(s: &State, bs: &[Balance]) -> Vec<Trade8> {
        let mut out = Vec::new();
        for i in 0..bs.len() {
            for j in i + 1..bs.len() {
                if let Some(t) = make_trade(s, bs[i], bs[j]) { out.push(t); }
            }
        }
        out
    }

    fn choose(s: &mut State, moves: &[Trade8], rng: &mut Rng, temp: f64) -> Option<(Trade8,i64)> {
        let before = s.g.energy;
        let mut best = None;
        let mut best_rank = f64::INFINITY;
        let mut best_delta = 0;
        for t in moves {
            apply_trade(s,t);
            let delta = s.g.energy - before;
            undo_trade(s,t);
            let u = rng.unit().clamp(1e-12,1.0-1e-12);
            let rank = delta as f64 - (-(-u.ln()).ln()) * temp.max(0.02);
            if rank < best_rank { best_rank=rank; best=Some(*t); best_delta=delta; }
        }
        best.map(|t|(t,best_delta))
    }

    pub fn run() {
        let args: Vec<String> = std::env::args().collect();
        let seconds = args.get(1).and_then(|x|x.parse().ok()).unwrap_or(180u64);
        let threads = args.get(2).and_then(|x|x.parse().ok()).unwrap_or(8usize);
        let input = args.get(3).map(String::as_str).unwrap_or("scratch_general_cpsat_from_project_best.json");
        let output = args.get(4).map(String::as_str).unwrap_or("scratch_bp_trade_best.json");
        let mut seed = load_seed(input,1).expect("valid 693-edge seed");
        seed.validate();
        assert_eq!(seed.g.io_energy,0,"seed must satisfy exact BP");
        let bs = Arc::new(balances(&seed.g));
        let initial_moves = available(&seed,&bs);
        eprintln!("seed={} io={} balances={} available={}",seed.g.energy,seed.g.io_energy,bs.len(),initial_moves.len());
        let best_value=Arc::new(AtomicI64::new(seed.g.energy));
        let best=Arc::new(Mutex::new(seed.clone()));
        let deadline=Instant::now()+Duration::from_secs(seconds);
        let mut handles=Vec::new();
        for id in 0..threads {
            let mut s=seed.clone(); let bs=bs.clone(); let bv=best_value.clone(); let shared=best.clone();
            handles.push(thread::spawn(move||{
                let nanos=SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64;
                let mut rng=Rng::new(nanos ^ ((id as u64+101)*0x9e37_79b9_7f4a_7c15));
                let mut step=0usize;
                while Instant::now()<deadline {
                    let moves=available(&s,&bs);
                    if moves.is_empty(){break;}
                    let phase=(step%256) as f64/256.0;
                    let temp=40.0*(0.05f64/40.0).powf(phase);
                    let Some((t,delta))=choose(&mut s,&moves,&mut rng,temp) else{break;};
                    if delta<=0 || rng.unit()<(-(delta as f64)/temp).exp(){apply_trade(&mut s,&t);}
                    if step%64==63 && rng.us(3)==0 { s=shared.lock().unwrap().clone(); }
                    let old=bv.fetch_min(s.g.energy,Ordering::Relaxed);
                    if s.g.energy<old {
                        s.validate(); assert_eq!(s.g.io_energy,0);
                        *shared.lock().unwrap()=s.clone();
                        eprintln!("worker={id} step={step} BEST={} moves={}",s.g.energy,moves.len());
                    }
                    step+=1;
                }
                eprintln!("worker={id} stopped step={step} energy={}",s.g.energy);
            }));
        }
        for h in handles {h.join().unwrap();}
        let answer=best.lock().unwrap().clone();
        answer.validate(); assert_eq!(answer.g.io_energy,0);
        save(output,&answer);
    }
}

fn main(){engine::run();}
