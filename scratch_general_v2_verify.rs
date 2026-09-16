use std::collections::HashSet;
use std::env;
use std::fs;

const N: usize = 99;

fn parse_edges(text: &str) -> Result<Vec<(usize, usize)>, String> {
    let key = text.find("\"edges\"").ok_or("missing JSON edges key")?;
    let bytes = text[key..].as_bytes();
    let mut nums = Vec::new();
    let mut p = 0usize;
    while p < bytes.len() && bytes[p] != b'[' { p += 1; }
    if p == bytes.len() { return Err("missing edges array".into()); }
    let mut depth = 0i32;
    while p < bytes.len() {
        if bytes[p] == b'[' { depth += 1; p += 1; }
        else if bytes[p] == b']' {
            depth -= 1;
            p += 1;
            if depth == 0 { break; }
        } else if bytes[p].is_ascii_digit() {
            let mut x = 0usize;
            while p < bytes.len() && bytes[p].is_ascii_digit() {
                x = x.checked_mul(10).and_then(|z| z.checked_add((bytes[p] - b'0') as usize))
                    .ok_or("integer overflow")?;
                p += 1;
            }
            nums.push(x);
        } else { p += 1; }
    }
    if nums.len() % 2 != 0 { return Err("odd number of endpoints".into()); }
    Ok(nums.chunks_exact(2).map(|q| (q[0], q[1])).collect())
}

fn main() -> Result<(), String> {
    let path = env::args().nth(1).unwrap_or_else(|| "scratch_general_v2_best.json".into());
    let text = fs::read_to_string(&path).map_err(|e| format!("read {path}: {e}"))?;
    let edges = parse_edges(&text)?;
    let mut seen = HashSet::new();
    let mut adj = [0u128; N];
    for (line, &(a, b)) in edges.iter().enumerate() {
        if !(1..=N).contains(&a) || !(1..=N).contains(&b) {
            return Err(format!("edge {} endpoint out of range: [{a},{b}]", line + 1));
        }
        if a == b { return Err(format!("self-loop at edge {}", line + 1)); }
        let (u, v) = if a < b { (a - 1, b - 1) } else { (b - 1, a - 1) };
        if !seen.insert((u, v)) { return Err(format!("duplicate edge [{a},{b}]")); }
        adj[u] |= 1u128 << v;
        adj[v] |= 1u128 << u;
    }
    let degrees: Vec<u32> = adj.iter().map(|x| x.count_ones()).collect();
    let degree_bad = degrees.iter().filter(|&&d| d != 14).count();
    let mut energy = 0i64;
    let mut io_energy = 0i64;
    let mut oo_energy = 0i64;
    let mut bad_pairs = 0usize;
    let mut adjacent_bad = 0usize;
    let mut nonadjacent_bad = 0usize;
    let mut max_abs = 0i64;
    let mut hist = [0usize; 13]; // residual -6..6, clamped
    for u in 0..N {
        for v in u + 1..N {
            let common = (adj[u] & adj[v]).count_ones() as i64;
            let is_edge = ((adj[u] >> v) & 1) as i64;
            let residual = common + is_edge - 2;
            let p = residual * residual;
            energy += p;
            if u < 15 && v >= 15 { io_energy += p; }
            if u >= 15 { oo_energy += p; }
            if residual != 0 {
                bad_pairs += 1;
                if is_edge != 0 { adjacent_bad += 1; } else { nonadjacent_bad += 1; }
            }
            max_abs = max_abs.max(residual.abs());
            hist[(residual + 6).clamp(0, 12) as usize] += 1;
        }
    }
    println!("file={path}");
    println!("edges={} unique={} degree_bad={} degree_min={} degree_max={}",
        edges.len(), seen.len(), degree_bad,
        degrees.iter().min().copied().unwrap_or(0), degrees.iter().max().copied().unwrap_or(0));
    println!("energy={energy} io_energy={io_energy} oo_energy={oo_energy}");
    println!("bad_pairs={bad_pairs} adjacent_bad={adjacent_bad} nonadjacent_bad={nonadjacent_bad} max_abs_residual={max_abs}");
    println!("residual_histogram_minus6_to_plus6={hist:?}");
    let valid = edges.len() == 693 && seen.len() == 693 && degree_bad == 0 && energy == 0;
    println!("valid_srg_99_14_1_2={valid}");
    if valid { Ok(()) } else { std::process::exit(2) }
}
