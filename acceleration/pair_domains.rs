//! Exact full-neighborhood pair constraints over supplied complete star domains.
//! pair_domains CANDIDATE.txt DOMAINS.txt OUTPUT.json [seconds=30] [pair_cap=10000000]
//! The caller must independently establish completeness of all supplied domains.
//! C99DOMAINS1 84, then per vertex: count followed by sorted hexadecimal masks.
//! Graph parser derived unchanged from frozen star_domains.rs.
//! Graph parser parent SHA256: b3637615352c0a5372fe7ed2237f34bc2d5c8773a892ee647c05acb772584d80

use std::collections::VecDeque;
use std::fmt::Write;
use std::fs;
use std::time::Instant;

type Result<T> = std::result::Result<T, String>;

struct Graph {
    adjacency: [u128; 99],
    labels: [[usize; 2]; 84],
    supports: [u8; 84],
}

impl Graph {
    fn read(path: &str) -> Result<Self> {
        let text = fs::read_to_string(path).map_err(|e| e.to_string())?;
        let mut tokens = text.split_whitespace();
        if tokens.next() != Some("C99OVERLAPS1") || tokens.next() != Some("1") {
            return Err("expected C99OVERLAPS1 and exactly one candidate".into());
        }
        let mut graph = Self {
            adjacency: [0; 99],
            labels: [[0; 2]; 84],
            supports: [0; 84],
        };
        for symbol in 0..14 {
            graph.add(0, symbol + 1);
        }
        for symbol in (0..14).step_by(2) {
            graph.add(symbol + 1, symbol + 2);
        }
        let mut outer = 0;
        for a in 0..7 {
            for b in a + 1..7 {
                for s in 0..2 {
                    for t in 0..2 {
                        graph.labels[outer] = [2 * a + s, 2 * b + t];
                        graph.supports[outer] = (1 << a) | (1 << b);
                        for label in graph.labels[outer] {
                            graph.add(outer + 15, label + 1);
                        }
                        outer += 1;
                    }
                }
            }
        }
        for _ in 0..168 {
            let u: usize = tokens
                .next()
                .ok_or("missing edge endpoint")?
                .parse()
                .map_err(|_| "invalid endpoint")?;
            let v: usize = tokens
                .next()
                .ok_or("missing edge endpoint")?
                .parse()
                .map_err(|_| "invalid endpoint")?;
            if !(u < v && v < 84) {
                return Err("endpoints must satisfy 0 <= u < v < 84".into());
            }
            if (graph.supports[u] & graph.supports[v]).count_ones() != 1 {
                return Err("edge is not an overlap edge".into());
            }
            if graph.adjacency[u + 15] & (1u128 << (v + 15)) != 0 {
                return Err("duplicate edge".into());
            }
            graph.add(u + 15, v + 15);
        }
        if tokens.next().is_some() {
            return Err("trailing input".into());
        }
        for u in 0..99 {
            let expected = if u < 15 { 14 } else { 6 };
            if graph.adjacency[u].count_ones() != expected {
                return Err(format!("wrong partial degree at {u}"));
            }
            for v in u + 1..99 {
                if graph.common(u, v) > graph.cap(u, v) {
                    return Err(format!("partial pair cap fails at {u},{v}"));
                }
            }
        }
        for u in 0..84 {
            let mut counts = [0u8; 14];
            let mut neighbors = graph.adjacency[u + 15] >> 15;
            while neighbors != 0 {
                let v = neighbors.trailing_zeros() as usize;
                neighbors &= neighbors - 1;
                for symbol in graph.labels[v] {
                    counts[symbol] += 1;
                }
            }
            for (symbol, count) in counts.iter().enumerate() {
                if graph.supports[u] & (1 << (symbol / 2)) != 0 {
                    if *count != 1 {
                        return Err("own-root quota fails".into());
                    }
                } else if *count > 2 {
                    return Err("foreign-root quota fails".into());
                }
            }
        }
        Ok(graph)
    }
    fn add(&mut self, u: usize, v: usize) {
        self.adjacency[u] |= 1u128 << v;
        self.adjacency[v] |= 1u128 << u;
    }
    fn common(&self, u: usize, v: usize) -> i8 {
        (self.adjacency[u] & self.adjacency[v]).count_ones() as i8
    }
    fn cap(&self, u: usize, v: usize) -> i8 {
        if self.adjacency[u] & (1u128 << v) != 0 {
            1
        } else {
            2
        }
    }
}

fn read_domains(path: &str, graph: &Graph) -> Result<Vec<Vec<u128>>> {
    let text = fs::read_to_string(path).map_err(|e| e.to_string())?;
    let mut tokens = text.split_whitespace();
    if tokens.next() != Some("C99DOMAINS1") || tokens.next() != Some("84") {
        return Err("expected C99DOMAINS1 84 header".into());
    }
    let mut domains = Vec::new();
    for u in 0..84 {
        let count: usize = tokens
            .next()
            .ok_or("missing domain count")?
            .parse()
            .map_err(|_| "invalid domain count")?;
        if count == 0 || count > 100_000 {
            return Err(format!("vertex {u}: domain count must be in 1..100000"));
        }
        let mut row = Vec::with_capacity(count);
        for _ in 0..count {
            let word = tokens.next().ok_or("missing hexadecimal mask")?;
            let mask = u128::from_str_radix(
                word.strip_prefix("0x").ok_or("mask must start with 0x")?,
                16,
            )
            .map_err(|_| "invalid hexadecimal mask")?;
            if mask >> 84 != 0 || mask.count_ones() != 8 {
                return Err(format!("vertex {u}: star mask must have eight of 84 bits"));
            }
            if row.last().is_some_and(|previous| *previous >= mask) {
                return Err("domain masks must be strictly sorted and unique".into());
            }
            let mut remaining = mask;
            while remaining != 0 {
                let v = remaining.trailing_zeros() as usize;
                remaining &= remaining - 1;
                if graph.supports[u] & graph.supports[v] != 0 {
                    return Err("star includes a non-disjoint-support edge".into());
                }
            }
            row.push(mask);
        }
        domains.push(row);
    }
    if tokens.next().is_some() {
        return Err("trailing domain input".into());
    }
    Ok(domains)
}

struct Relation {
    words: usize,
    supports: Vec<u64>,
}

#[derive(Clone, Copy)]
enum Cap {
    Time,
    Pairs,
}
impl Cap {
    fn name(self) -> &'static str {
        match self {
            Self::Time => "TIME_CAP",
            Self::Pairs => "DOMAIN_PAIR_CAP",
        }
    }
}

struct Budget {
    started: Instant,
    seconds: f64,
    cap: u64,
    checks: u64,
}
impl Budget {
    fn time(&self) -> std::result::Result<(), Cap> {
        if self.started.elapsed().as_secs_f64() > self.seconds {
            Err(Cap::Time)
        } else {
            Ok(())
        }
    }
}

fn build_relation(
    u: usize,
    v: usize,
    neighborhoods: &[Vec<u128>],
    budget: &mut Budget,
) -> std::result::Result<(Relation, Relation), Cap> {
    budget.time()?;
    let left_count = neighborhoods[u].len();
    let right_count = neighborhoods[v].len();
    let combinations = (left_count as u64) * (right_count as u64);
    // A partial relation cannot be used. This cap test avoids allocating a
    // giant relation that is guaranteed to exceed the remaining pair budget.
    if combinations > budget.cap - budget.checks {
        budget.checks = budget.cap + 1;
        return Err(Cap::Pairs);
    }
    let left_words = right_count.div_ceil(64);
    let right_words = left_count.div_ceil(64);
    let mut left = Relation {
        words: left_words,
        supports: vec![0; left_count * left_words],
    };
    let mut right = Relation {
        words: right_words,
        supports: vec![0; right_count * right_words],
    };
    for (i, &nu) in neighborhoods[u].iter().enumerate() {
        budget.time()?;
        for (j, &nv) in neighborhoods[v].iter().enumerate() {
            budget.checks += 1;
            let edge = (nu >> (v + 15)) & 1;
            if edge == ((nv >> (u + 15)) & 1) && (nu & nv).count_ones() == 2 - edge as u32 {
                left.supports[i * left_words + j / 64] |= 1u64 << (j % 64);
                right.supports[j * right_words + i / 64] |= 1u64 << (i % 64);
            }
        }
    }
    Ok((left, right))
}

struct Event {
    target: usize,
    support: usize,
    removed: Vec<usize>,
    before: usize,
    after: usize,
}
struct Closure {
    active: Vec<Vec<u64>>,
    events: Vec<Event>,
    empty: Option<usize>,
    cap: Option<Cap>,
    checks: u64,
    relations: usize,
    queue_visits: usize,
    seconds: f64,
}

fn close(graph: &Graph, domains: &[Vec<u128>], seconds: f64, pair_cap: u64) -> Closure {
    let neighborhoods: Vec<Vec<u128>> = domains
        .iter()
        .enumerate()
        .map(|(u, row)| {
            row.iter()
                .map(|mask| graph.adjacency[u + 15] | (mask << 15))
                .collect()
        })
        .collect();
    let mut active: Vec<Vec<u64>> = domains
        .iter()
        .map(|row| {
            let mut words = vec![u64::MAX; row.len().div_ceil(64)];
            if row.len() % 64 != 0 {
                *words.last_mut().unwrap() = (1u64 << (row.len() % 64)) - 1;
            }
            words
        })
        .collect();
    let mut pairs = Vec::new();
    for u in 0..84 {
        for v in u + 1..84 {
            pairs.push((domains[u].len() * domains[v].len(), u, v));
        }
    }
    pairs.sort_unstable();
    let mut queue = VecDeque::new();
    let mut queued = [false; 84 * 84];
    for (_, u, v) in pairs {
        queue.push_back((u, v));
        queue.push_back((v, u));
        queued[u * 84 + v] = true;
        queued[v * 84 + u] = true;
    }
    let mut relations: Vec<Option<Relation>> = (0..84 * 84).map(|_| None).collect();
    let mut budget = Budget {
        started: Instant::now(),
        seconds,
        cap: pair_cap,
        checks: 0,
    };
    let mut events = Vec::new();
    let mut empty = None;
    let mut cap = None;
    let mut relations_built = 0;
    let mut queue_visits = 0;
    while let Some((u, v)) = queue.pop_front() {
        if let Err(reason) = budget.time() {
            cap = Some(reason);
            break;
        }
        queued[u * 84 + v] = false;
        queue_visits += 1;
        if relations[u * 84 + v].is_none() {
            match build_relation(u, v, &neighborhoods, &mut budget) {
                Ok((left, right)) => {
                    relations[u * 84 + v] = Some(left);
                    relations[v * 84 + u] = Some(right);
                    relations_built += 1;
                }
                Err(reason) => {
                    cap = Some(reason);
                    break;
                }
            }
        }
        let relation = relations[u * 84 + v].as_ref().unwrap();
        let mut removed = Vec::new();
        for i in 0..domains[u].len() {
            if active[u][i / 64] & (1u64 << (i % 64)) == 0 {
                continue;
            }
            let supports = &relation.supports[i * relation.words..(i + 1) * relation.words];
            if !supports
                .iter()
                .zip(&active[v])
                .any(|(available, present)| available & present != 0)
            {
                removed.push(i);
            }
        }
        if removed.is_empty() {
            continue;
        }
        let before: usize = active[u]
            .iter()
            .map(|word| word.count_ones() as usize)
            .sum();
        for &i in &removed {
            active[u][i / 64] &= !(1u64 << (i % 64));
        }
        let after = before - removed.len();
        events.push(Event {
            target: u,
            support: v,
            removed,
            before,
            after,
        });
        if after == 0 {
            empty = Some(u);
            break;
        }
        for w in 0..84 {
            if w != u && !queued[w * 84 + u] {
                queue.push_back((w, u));
                queued[w * 84 + u] = true;
            }
        }
    }
    Closure {
        active,
        events,
        empty,
        cap,
        checks: budget.checks,
        relations: relations_built,
        queue_visits,
        seconds: budget.started.elapsed().as_secs_f64(),
    }
}

fn run() -> Result<()> {
    let args: Vec<_> = std::env::args().collect();
    if !(4..=6).contains(&args.len()) {
        return Err(
            "usage: pair_domains CANDIDATE.txt DOMAINS.txt OUTPUT.json [seconds] [pair_cap]".into(),
        );
    }
    if std::path::Path::new(&args[3]).exists() {
        return Err("output exists; preserve previous artifact".into());
    }
    let seconds: f64 = args
        .get(4)
        .map(|v| v.parse())
        .unwrap_or(Ok(30.0))
        .map_err(|_| "invalid seconds")?;
    let pair_cap: u64 = args
        .get(5)
        .map(|v| v.parse())
        .unwrap_or(Ok(10_000_000))
        .map_err(|_| "invalid pair cap")?;
    if !seconds.is_finite()
        || !(0.0 < seconds && seconds <= 3600.0)
        || pair_cap == 0
        || pair_cap > 1_000_000_000
    {
        return Err("seconds must be finite in (0,3600], pair cap in 1..1000000000".into());
    }
    let graph = Graph::read(&args[1])?;
    let domains = read_domains(&args[2], &graph)?;
    let closure = close(&graph, &domains, seconds, pair_cap);
    let status = if closure.cap.is_some() {
        "INCOMPLETE"
    } else if closure.empty.is_some() {
        "EMPTY_DOMAIN"
    } else {
        "ARC_CONSISTENT_NONEMPTY"
    };
    let mut output = format!("{{\"status\":\"EXACT_PAIR_DOMAIN_{status}\",\"backend\":\"rust\",\"complete_initial_domains_audited\":false,\"caps\":{{\"seconds\":{seconds},\"domain_pairs\":{pair_cap}}},\"propagation_status\":\"{status}\",\"cap_reason\":");
    if let Some(reason) = closure.cap {
        write!(&mut output, "\"{}\"", reason.name()).unwrap();
    } else {
        output.push_str("null");
    }
    output.push_str(",\"empty_vertex\":");
    if let Some(u) = closure.empty {
        write!(&mut output, "{u}").unwrap();
    } else {
        output.push_str("null");
    }
    output.push_str(",\"events\":[");
    for (i, event) in closure.events.iter().enumerate() {
        if i != 0 {
            output.push(',');
        }
        write!(&mut output, "{{\"target_vertex\":{},\"support_vertex\":{},\"removed_domain_ids\":{:?},\"before_count\":{},\"after_count\":{}}}",
               event.target, event.support, event.removed, event.before, event.after).unwrap();
    }
    output.push_str("],\"surviving_domain_ids\":[");
    for u in 0..84 {
        if u != 0 {
            output.push(',');
        }
        let ids: Vec<_> = (0..domains[u].len())
            .filter(|i| closure.active[u][i / 64] & (1u64 << (i % 64)) != 0)
            .collect();
        write!(&mut output, "{:?}", ids).unwrap();
    }
    write!(&mut output, "],\"domain_pairs_evaluated\":{},\"vertex_pair_relations_built\":{},\"queue_visits\":{},\"elapsed_seconds\":{:.9},", closure.checks, closure.relations, closure.queue_visits, closure.seconds).unwrap();
    output.push_str("\"scope\":\"Exact reciprocal adjacency and completed-neighborhood intersection constraints, conditional on supplied star domains. Complete input domains must be independently established before exclusion. A cap gives no exclusion; nonempty arc consistency is not a global graph witness.\"}\n");
    fs::write(&args[3], output).map_err(|e| e.to_string())?;
    eprintln!(
        "{status}: {} relations, {} domain pairs, {} events, {:.6} seconds",
        closure.relations,
        closure.checks,
        closure.events.len(),
        closure.seconds
    );
    Ok(())
}

fn main() {
    if let Err(message) = run() {
        eprintln!("error: {message}");
        std::process::exit(1);
    }
}
