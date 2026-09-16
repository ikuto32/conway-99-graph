//! Complete local star domains and reciprocal-edge arc consistency.
//! rustc -O -C target-cpu=native acceleration/star_domains.rs -o acceleration/build/star_domains.exe
//! star_domains INPUT.txt OUTPUT.json [seconds=30] [node_cap=2000000] [domain_cap=20000]
//! INPUT uses C99OVERLAPS1 with exactly one canonical degree-four candidate.
//! An enumeration cap yields INCOMPLETE and disables every exclusion/propagation.
//! An empty complete domain excludes only this fixed overlap assignment.

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

struct Model {
    vertices: Vec<usize>,
    labels: Vec<[usize; 2]>,
    resources: Vec<[usize; 7]>,
    conflicts: Vec<u64>,
    by_symbol: [u64; 14],
    demand: [i8; 14],
    capacity: [i8; 99],
}

impl Model {
    fn new(graph: &Graph, outer: usize) -> Result<Self> {
        let u = outer + 15;
        let mut vertices = Vec::new();
        for v in 0..84 {
            if graph.supports[outer] & graph.supports[v] != 0 {
                continue;
            }
            let mut neighbors = graph.adjacency[u];
            let mut legal = true;
            while neighbors != 0 {
                let w = neighbors.trailing_zeros() as usize;
                neighbors &= neighbors - 1;
                if graph.common(v + 15, w) >= graph.cap(v + 15, w) {
                    legal = false;
                    break;
                }
            }
            if legal {
                vertices.push(v);
            }
        }
        let mut demand = [0; 14];
        for symbol in 0..14 {
            demand[symbol] = graph.cap(u, symbol + 1) - graph.common(u, symbol + 1);
        }
        if demand.iter().sum::<i8>() != 16 || demand.iter().any(|&value| !(0..=2).contains(&value))
        {
            return Err("unexpected local star demand".into());
        }
        let mut capacity = [0; 99];
        for w in 0..99 {
            if w != u {
                capacity[w] = graph.cap(u, w) - graph.common(u, w);
            }
        }
        let mut labels = Vec::new();
        let mut resources = Vec::new();
        let mut conflicts = Vec::new();
        let mut by_symbol = [0; 14];
        for (i, &v) in vertices.iter().enumerate() {
            labels.push(graph.labels[v]);
            for symbol in graph.labels[v] {
                by_symbol[symbol] |= 1u64 << i;
            }
            let mut mask = graph.adjacency[v + 15] | (1u128 << (v + 15));
            let mut required = [0; 7];
            if mask.count_ones() != 7 {
                return Err("unexpected star resource count".into());
            }
            for w in &mut required {
                *w = mask.trailing_zeros() as usize;
                mask &= mask - 1;
            }
            resources.push(required);
            let mut conflict = 0;
            for (j, &w) in vertices.iter().enumerate() {
                if v != w && graph.common(v + 15, w + 15) == graph.cap(v + 15, w + 15) {
                    conflict |= 1u64 << j;
                }
            }
            conflicts.push(conflict);
        }
        Ok(Self {
            vertices,
            labels,
            resources,
            conflicts,
            by_symbol,
            demand,
            capacity,
        })
    }
}

struct Budget {
    start: Instant,
    seconds: f64,
    nodes: u64,
    node_cap: u64,
    domain_cap: usize,
}

#[derive(Clone, Copy)]
enum Cap {
    Nodes,
    Time,
    Domain,
}
impl Cap {
    fn name(self) -> &'static str {
        match self {
            Self::Nodes => "GLOBAL_NODE_CAP",
            Self::Time => "TIME_CAP",
            Self::Domain => "PER_VERTEX_DOMAIN_CAP",
        }
    }
}

struct Domain {
    outer: usize,
    masks: Vec<u128>,
    nodes: u64,
    cap: Option<Cap>,
}

fn branch(
    model: &Model,
    chosen: u128,
    eligible: u64,
    remaining: &[i8; 14],
    caps: &[i8; 99],
    selection: &[usize],
    budget: &mut Budget,
    masks: &mut Vec<u128>,
    local_nodes: &mut u64,
) -> std::result::Result<(), Cap> {
    let mut next_remaining = *remaining;
    let mut next_caps = *caps;
    let mut excluded = 0;
    let mut next_chosen = chosen;
    for &i in selection {
        if selection
            .iter()
            .any(|&j| i != j && model.conflicts[i] & (1u64 << j) != 0)
        {
            return Ok(());
        }
        for symbol in model.labels[i] {
            next_remaining[symbol] -= 1;
            if next_remaining[symbol] < 0 {
                return Ok(());
            }
        }
        for &w in &model.resources[i] {
            next_caps[w] -= 1;
            if next_caps[w] < 0 {
                return Ok(());
            }
        }
        excluded |= (1u64 << i) | model.conflicts[i];
        next_chosen |= 1u128 << model.vertices[i];
    }
    visit(
        model,
        next_chosen,
        eligible & !excluded,
        next_remaining,
        next_caps,
        budget,
        masks,
        local_nodes,
    )
}

fn visit(
    model: &Model,
    chosen: u128,
    available: u64,
    remaining: [i8; 14],
    caps: [i8; 99],
    budget: &mut Budget,
    masks: &mut Vec<u128>,
    local_nodes: &mut u64,
) -> std::result::Result<(), Cap> {
    budget.nodes += 1;
    *local_nodes += 1;
    if budget.nodes > budget.node_cap {
        return Err(Cap::Nodes);
    }
    if budget.nodes % 128 == 0 && budget.start.elapsed().as_secs_f64() > budget.seconds {
        return Err(Cap::Time);
    }
    if remaining.iter().all(|&value| value == 0) {
        if masks.len() >= budget.domain_cap {
            return Err(Cap::Domain);
        }
        masks.push(chosen);
        return Ok(());
    }
    let mut eligible = 0;
    let mut rest = available;
    while rest != 0 {
        let i = rest.trailing_zeros() as usize;
        rest &= rest - 1;
        if model.labels[i].iter().all(|&s| remaining[s] > 0)
            && model.resources[i].iter().all(|&w| caps[w] > 0)
        {
            eligible |= 1u64 << i;
        }
    }
    let mut best = (u32::MAX, u32::MAX, usize::MAX);
    for symbol in 0..14 {
        if remaining[symbol] <= 0 {
            continue;
        }
        let count = (eligible & model.by_symbol[symbol]).count_ones();
        if count < remaining[symbol] as u32 {
            return Ok(());
        }
        let candidate = (count - remaining[symbol] as u32, count, symbol);
        if candidate < best {
            best = candidate;
        }
    }
    let symbol = best.2;
    let mut firsts = eligible & model.by_symbol[symbol];
    while firsts != 0 {
        let first = firsts.trailing_zeros() as usize;
        firsts &= firsts - 1;
        if remaining[symbol] == 1 {
            branch(
                model,
                chosen,
                eligible,
                &remaining,
                &caps,
                &[first],
                budget,
                masks,
                local_nodes,
            )?;
        } else {
            let mut seconds = firsts;
            while seconds != 0 {
                let second = seconds.trailing_zeros() as usize;
                seconds &= seconds - 1;
                branch(
                    model,
                    chosen,
                    eligible,
                    &remaining,
                    &caps,
                    &[first, second],
                    budget,
                    masks,
                    local_nodes,
                )?;
            }
        }
    }
    Ok(())
}

fn enumerate(graph: &Graph, outer: usize, budget: &mut Budget) -> Result<Domain> {
    let model = Model::new(graph, outer)?;
    let mut masks = Vec::new();
    let mut nodes = 0;
    let cap = if budget.start.elapsed().as_secs_f64() > budget.seconds {
        Some(Cap::Time)
    } else {
        visit(
            &model,
            0,
            (1u64 << model.vertices.len()) - 1,
            model.demand,
            model.capacity,
            budget,
            &mut masks,
            &mut nodes,
        )
        .err()
    };
    masks.sort_unstable();
    if masks.windows(2).any(|pair| pair[0] == pair[1]) {
        return Err("duplicate enumerated star".into());
    }
    if masks.iter().any(|mask| mask.count_ones() != 8) {
        return Err("enumerated star has wrong degree".into());
    }
    Ok(Domain {
        outer,
        masks,
        nodes,
        cap,
    })
}

struct Event {
    target: usize,
    support: usize,
    required: u8,
    removed: Vec<usize>,
    before: usize,
    after: usize,
}
struct Propagation {
    active: Vec<Vec<bool>>,
    empty: Option<usize>,
    events: Vec<Event>,
}

fn reciprocal_closure(graph: &Graph, domains: &[Domain]) -> Propagation {
    let mut result = Propagation {
        active: domains.iter().map(|d| vec![true; d.masks.len()]).collect(),
        empty: None,
        events: Vec::new(),
    };
    // If a local domain starts empty, no edge propagation is needed or emitted.
    // This explicitly handles a boundary the original Python FIFO deferred.
    if let Some(u) = domains.iter().position(|domain| domain.masks.is_empty()) {
        result.empty = Some(u);
        return result;
    }
    let mut queue: VecDeque<_> = (0..84).collect();
    let mut queued = [true; 84];
    while let Some(v) = queue.pop_front() {
        queued[v] = false;
        let mut union = 0;
        let mut intersection = (1u128 << 84) - 1;
        for (i, &mask) in domains[v].masks.iter().enumerate() {
            if result.active[v][i] {
                union |= mask;
                intersection &= mask;
            }
        }
        for u in 0..84 {
            if graph.supports[u] & graph.supports[v] != 0 {
                continue;
            }
            let required = if intersection & (1u128 << u) != 0 {
                1
            } else if union & (1u128 << u) == 0 {
                0
            } else {
                continue;
            };
            let before = result.active[u].iter().filter(|&&active| active).count();
            let mut removed = Vec::new();
            for (i, &mask) in domains[u].masks.iter().enumerate() {
                if result.active[u][i] && ((mask >> v) & 1) as u8 != required {
                    result.active[u][i] = false;
                    removed.push(i);
                }
            }
            if removed.is_empty() {
                continue;
            }
            let after = before - removed.len();
            result.events.push(Event {
                target: u,
                support: v,
                required,
                removed,
                before,
                after,
            });
            if after == 0 {
                result.empty = Some(u);
                return result;
            }
            if !queued[u] {
                queue.push_back(u);
                queued[u] = true;
            }
        }
    }
    result
}

fn write_propagation(out: &mut String, propagation: &Propagation) {
    let status = if propagation.empty.is_some() {
        "EMPTY_DOMAIN"
    } else {
        "ARC_CONSISTENT_NONEMPTY"
    };
    write!(out, "{{\"status\":\"{status}\",\"empty_vertex\":").unwrap();
    if let Some(u) = propagation.empty {
        write!(out, "{u}").unwrap();
    } else {
        out.push_str("null");
    }
    out.push_str(",\"events\":[");
    for (i, event) in propagation.events.iter().enumerate() {
        if i != 0 {
            out.push(',');
        }
        write!(out, "{{\"target_vertex\":{},\"support_vertex\":{},\"required_edge_value\":{},\"removed_domain_ids\":{:?},\"before_count\":{},\"after_count\":{}}}",
               event.target, event.support, event.required, event.removed, event.before, event.after).unwrap();
    }
    out.push_str("],\"surviving_domain_ids\":[");
    for (u, active) in propagation.active.iter().enumerate() {
        if u != 0 {
            out.push(',');
        }
        let ids: Vec<_> = active
            .iter()
            .enumerate()
            .filter_map(|(i, &value)| value.then_some(i))
            .collect();
        write!(out, "{:?}", ids).unwrap();
    }
    out.push_str("]}");
}

fn run() -> Result<()> {
    let args: Vec<_> = std::env::args().collect();
    if !(3..=6).contains(&args.len()) {
        return Err(
            "usage: star_domains INPUT.txt OUTPUT.json [seconds] [node_cap] [domain_cap]".into(),
        );
    }
    if std::path::Path::new(&args[2]).exists() {
        return Err("output exists; preserve previous artifact".into());
    }
    let seconds: f64 = args
        .get(3)
        .map(|v| v.parse())
        .unwrap_or(Ok(30.0))
        .map_err(|_| "invalid seconds")?;
    let node_cap: u64 = args
        .get(4)
        .map(|v| v.parse())
        .unwrap_or(Ok(2_000_000))
        .map_err(|_| "invalid node cap")?;
    let domain_cap: usize = args
        .get(5)
        .map(|v| v.parse())
        .unwrap_or(Ok(20_000))
        .map_err(|_| "invalid domain cap")?;
    if !seconds.is_finite()
        || seconds <= 0.0
        || seconds > 3600.0
        || node_cap == 0
        || domain_cap == 0
    {
        return Err("finite seconds in (0,3600] and positive node/domain caps required".into());
    }
    let graph = Graph::read(&args[1])?;
    let start = Instant::now();
    let mut budget = Budget {
        start,
        seconds,
        nodes: 0,
        node_cap,
        domain_cap,
    };
    let mut domains = Vec::new();
    for outer in 0..84 {
        let domain = enumerate(&graph, outer, &mut budget)?;
        let incomplete = domain.cap.is_some();
        domains.push(domain);
        if incomplete {
            break;
        }
    }
    let enumeration_seconds = start.elapsed().as_secs_f64();
    let complete = domains.len() == 84 && domains.iter().all(|domain| domain.cap.is_none());
    let propagation = if complete {
        Some(reciprocal_closure(&graph, &domains))
    } else {
        None
    };
    let status = match &propagation {
        None => "INCOMPLETE",
        Some(p) if p.empty.is_some() => "COMPLETE_DOMAINS_RECIPROCITY_EMPTY_DOMAIN",
        Some(_) => "COMPLETE_DOMAINS_RECIPROCITY_ARC_CONSISTENT_NONEMPTY",
    };
    let elapsed = start.elapsed().as_secs_f64();
    let mut output = format!("{{\"status\":\"{status}\",\"backend\":\"rust\",\"complete_domain_enumeration\":{complete},\"caps\":{{\"seconds\":{seconds},\"global_nodes\":{node_cap},\"per_vertex_domains\":{domain_cap}}},\"total_nodes\":{},\"enumeration_seconds\":{enumeration_seconds:.9},\"elapsed_seconds\":{elapsed:.9},\"domains\":[", budget.nodes);
    for (i, domain) in domains.iter().enumerate() {
        if i != 0 {
            output.push(',');
        }
        let status = if domain.cap.is_some() {
            "INCOMPLETE"
        } else {
            "COMPLETE"
        };
        write!(
            &mut output,
            "{{\"outer_vertex\":{},\"status\":\"{status}\",\"cap_reason\":",
            domain.outer
        )
        .unwrap();
        if let Some(reason) = domain.cap {
            write!(&mut output, "\"{}\"", reason.name()).unwrap();
        } else {
            output.push_str("null");
        }
        write!(
            &mut output,
            ",\"nodes\":{},\"domain_masks_hex\":[",
            domain.nodes
        )
        .unwrap();
        for (j, mask) in domain.masks.iter().enumerate() {
            if j != 0 {
                output.push(',');
            }
            write!(&mut output, "\"0x{mask:x}\"").unwrap();
        }
        output.push_str("]}");
    }
    output.push(']');
    if let Some(propagation) = propagation {
        output.push_str(",\"propagation\":");
        write_propagation(&mut output, &propagation);
    }
    output.push_str(",\"scope\":\"One fixed complete overlap assignment. Exact complete domains and necessary reciprocal-edge propagation only. An enumeration cap disables exclusions. Nonempty arc consistency is not a graph witness.\"}\n");
    fs::write(&args[2], output).map_err(|e| e.to_string())?;
    eprintln!(
        "{status}: {} vertices, {} nodes, {elapsed:.6} seconds",
        domains.len(),
        budget.nodes
    );
    Ok(())
}

fn main() {
    if let Err(message) = run() {
        eprintln!("error: {message}");
        std::process::exit(1);
    }
}
