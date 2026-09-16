//! Heuristic fixed-dual star score; no pruning or exact exclusion.
//! Enumeration copied from frozen star_domains_batch.rs SHA84be679f31ae0fc365dc51a2b05a60d0467fa660c9c72a3572b3681da887c482.
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
    fn read_candidate(tokens: &mut std::str::SplitWhitespace<'_>) -> Result<Self> {
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

const DENOMINATOR: i128 = 1i128 << 40;
struct Dual { beta: Vec<i128>, gamma: Vec<i128>, rhs_constant: i128 }
impl Dual {
    fn read(name:&str, graph:&Graph)->Result<Self> {
        let input=fs::read_to_string(name).map_err(|e|e.to_string())?;
        let mut tokens=input.split_whitespace();
        if tokens.next()!=Some("C99STARDUAL_DYADIC1") || tokens.next()!=Some("1680") || tokens.next()!=Some("3486") || tokens.next()!=Some("1099511627776") {
            return Err("expected C99STARDUAL_DYADIC1 1680 3486 1099511627776".into());
        }
        fn number(tokens:&mut std::str::SplitWhitespace<'_>,low:i128)->Result<i128> {
            let v:i128=tokens.next().ok_or("missing dual value")?.parse().map_err(|_|"invalid dual value")?;
            if v<low || v>DENOMINATOR{return Err("integer dual value outside its box".into());}
            Ok(v)
        }
        let mut beta=vec![0;84*84];let mut gamma=vec![0;84*84];
        for u in 0..84 {for v in u+1..84 {if graph.supports[u]&graph.supports[v]==0 {
            let b=number(&mut tokens,-DENOMINATOR)?;beta[u*84+v]=b;beta[v*84+u]=-b;
        }}}
        let mut rhs_constant=0;
        for u in 0..84 {for v in u+1..84 {
            let g=number(&mut tokens,0)?;gamma[u*84+v]=g;gamma[v*84+u]=g;
            let shared=graph.labels[u].iter().filter(|s|graph.labels[v].contains(s)).count();
            rhs_constant+=(2-shared) as i128*g;
        }}
        if tokens.next().is_some(){return Err("trailing dual tokens".into());}
        Ok(Self{beta,gamma,rhs_constant})
    }
    fn costs(&self,graph:&Graph)->(Vec<i128>,i128) {
        let neighbors:Vec<Vec<usize>>=(0..84).map(|u| {
            let mut bits=graph.adjacency[u+15]>>15;let mut row=Vec::new();
            while bits!=0 {row.push(bits.trailing_zeros() as usize);bits&=bits-1;}
            row
        }).collect();
        let mut rhs=self.rhs_constant;
        for u in 0..84 {
            for &v in &neighbors[u] {if u<v {rhs-=self.gamma[u*84+v];}}
            for i in 0..neighbors[u].len() {for j in i+1..neighbors[u].len() {
                rhs-=self.gamma[neighbors[u][i]*84+neighbors[u][j]];
            }}
        }
        let mut costs=self.beta.clone();
        for u in 0..84 {for v in u+1..84 {if graph.supports[u]&graph.supports[v]==0 {
            let mut edge_cost=self.gamma[u*84+v];
            for &w in &neighbors[u] {edge_cost+=self.gamma[v*84+w];}
            for &w in &neighbors[v] {edge_cost+=self.gamma[u*84+w];}
            // Projection uses the smaller endpoint only. Larger-endpoint
            // star variables retain just the negative reciprocal dual cost.
            costs[u*84+v]+=edge_cost;
        }}}
        (costs,rhs)
    }
}

fn evaluate(graph:&Graph,dual:&Dual,seconds:f64,node_cap:u64,domain_cap:usize)->Result<String> {
    let start=Instant::now();let (costs,rhs)=dual.costs(graph);
    let mut budget=Budget{start,seconds,nodes:0,node_cap,domain_cap};
    let mut counts=Vec::new();let mut minima:Vec<Option<i128>>=Vec::new();
    let mut argmins:Vec<Option<u128>>=Vec::new();let mut cap=None;
    let mut enumeration_seconds=0.0;let mut minimum_seconds=0.0;let mut empty_count=0;
    for u in 0..84 {
        let tick=Instant::now();let domain=enumerate(graph,u,&mut budget)?;
        enumeration_seconds+=tick.elapsed().as_secs_f64();
        debug_assert_eq!(domain.outer,u);
        let _local_nodes=domain.nodes;
        counts.push(domain.masks.len());
        if domain.cap.is_some(){cap=domain.cap;minima.push(None);argmins.push(None);break;}
        let tick=Instant::now();let mut best=i128::MAX;let mut argmin=None;
        for mut mask in domain.masks {
            let original=mask;let mut cost=0;
            while mask!=0 {let v=mask.trailing_zeros() as usize;mask&=mask-1;cost+=costs[u*84+v];}
            if cost<best {best=cost;argmin=Some(original);}
        }
        minimum_seconds+=tick.elapsed().as_secs_f64();
        if argmin.is_none(){empty_count+=1;minima.push(None);}else{minima.push(Some(best));}
        argmins.push(argmin);
    }
    let complete=cap.is_none()&&counts.len()==84;
    let available=complete&&empty_count==0;
    let sum:i128=minima.iter().filter_map(|v|*v).sum();
    let score=if available {format!("{:.17}",(sum-rhs) as f64/DENOMINATOR as f64)}else{"null".into()};
    let score_numerator=if available {(sum-rhs).to_string()}else{"null".into()};
    let status=if !complete {"UNAVAILABLE_INCOMPLETE_DOMAINS"}else if empty_count!=0 {"UNAVAILABLE_EMPTY_DOMAIN"}else{"COMPLETE_HEURISTIC_SCORE"};
    let mut out=format!("{{\"status\":\"{status}\",\"complete_domain_enumeration\":{complete},\"score\":{score},\"score_numerator\":{score_numerator},\"denominator\":{DENOMINATOR},\"weighted_cap_rhs_numerator\":{rhs},\"sum_vertex_minima_numerator\":{},\"local_empty_count\":{empty_count},\"domain_counts\":{:?},\"nodes\":{},\"cap_reason\":{},\"enumeration_seconds\":{enumeration_seconds:.9},\"minimum_scoring_seconds\":{minimum_seconds:.9},\"elapsed_seconds\":{:.9},\"vertex_minimum_numerators\":[",
        if available {sum.to_string()}else{"null".into()},counts,budget.nodes,
        cap.map(|c|format!("\"{}\"",c.name())).unwrap_or("null".into()),start.elapsed().as_secs_f64());
    for (i,v) in minima.iter().enumerate(){if i>0 {out.push(',');}match v{Some(x)=>write!(out,"{x}").unwrap(),None=>out.push_str("null")}}
    out.push_str("],\"minimizing_masks_hex\":[");
    for (i,v) in argmins.iter().enumerate(){if i>0 {out.push(',');}match v{Some(m)=>write!(out,"\"0x{m:x}\"").unwrap(),None=>out.push_str("null")}}
    out.push_str("]}");Ok(out)
}

fn run()->Result<()> {
    let args:Vec<_>=std::env::args().collect();
    if !(4..=7).contains(&args.len()){return Err("usage: star_dual_batch CANDIDATES.txt DUAL.txt OUTPUT.json [seconds_per_candidate=1] [node_cap=2000000] [domain_cap=20000]".into());}
    if std::path::Path::new(&args[3]).exists(){return Err("output exists; preserve prior artifact".into());}
    let seconds:f64=args.get(4).map(|v|v.parse()).transpose().map_err(|_|"bad seconds")?.unwrap_or(1.0);
    let node_cap:u64=args.get(5).map(|v|v.parse()).transpose().map_err(|_|"bad node cap")?.unwrap_or(2000000);
    let domain_cap:usize=args.get(6).map(|v|v.parse()).transpose().map_err(|_|"bad domain cap")?.unwrap_or(20000);
    if !seconds.is_finite()||seconds<=0.0||seconds>3600.0||node_cap==0||domain_cap==0{return Err("finite seconds in(0,3600] and positive caps required".into());}
    let input=fs::read_to_string(&args[1]).map_err(|e|e.to_string())?;let mut tokens=input.split_whitespace();
    if tokens.next()!=Some("C99OVERLAPS1"){return Err("wrong candidates header".into());}
    let count:usize=tokens.next().ok_or("missing candidate count")?.parse().map_err(|_|"bad candidate count")?;
    if count==0||count>100000{return Err("candidate count outside1..100000".into());}
    let mut graphs=Vec::new();
    for i in 0..count {graphs.push(Graph::read_candidate(&mut tokens).map_err(|s|format!("candidate {i}: {s}"))?);}
    if tokens.next().is_some(){return Err("trailing candidate data".into());}
    let dual=Dual::read(&args[2],&graphs[0])?;
    let started=Instant::now();let mut output=String::from("{\"status\":\"HEURISTIC_FIXED_STAR_DUAL_BATCH_FINISHED\",\"results\":[");
    for (i,g) in graphs.iter().enumerate(){if i>0 {output.push(',');}output.push_str(&evaluate(g,&dual,seconds,node_cap,domain_cap)?);}
    write!(output,"],\"candidate_count\":{count},\"caps_reset_per_candidate\":true,\"seconds_per_candidate\":{seconds},\"node_cap\":{node_cap},\"domain_cap\":{domain_cap},\"elapsed_seconds\":{:.9},\"arithmetic\":\"i128 dyadic2^40\",\"scores_are_certificates\":false,\"candidates_pruned\":0,\"scope\":\"Fixed beta/gamma heuristic ranking on each K own freshly enumerated complete star domains. Empty/incomplete domains make scores unavailable. Exact integer ranking arithmetic, no exclusion or certificate claims from this producer.\"}}\n",started.elapsed().as_secs_f64()).unwrap();
    use std::io::Write as IoWrite;
    let mut file=fs::OpenOptions::new().write(true).create_new(true).open(&args[3]).map_err(|e|e.to_string())?;
    file.write_all(output.as_bytes()).map_err(|e|e.to_string())?;
    eprintln!("{count} candidates; {:.6}s evaluation; heuristic scores only",started.elapsed().as_secs_f64());Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("error: {e}");std::process::exit(1);}}

