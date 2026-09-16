//! Joint completed-star CSP search. Derived parser from frozen pair_domains.rs.
//! joint_star_dfs CANDIDATE DOMAINS OUTPUT [seconds] [nodes] [pairs] [memory_mib] [ac|search]
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

#[derive(Clone)]
struct Relation { words: usize, supports: Vec<u64> }
#[derive(Clone)]
struct State { active: Vec<Vec<u64>>, counts: Vec<usize> }
#[derive(Clone)]
struct Event { u: usize, v: usize, removed: Vec<usize>, before: usize, after: usize }
enum Outcome { Found(Vec<usize>), Exhausted, Capped(String) }
struct Engine {
    n: usize, sizes: Vec<usize>, neighborhoods: Vec<Vec<u128>>,
    relations: Vec<Option<Relation>>, started: Instant, seconds: f64,
    pair_cap: u64, checks: u64, node_cap: u64, nodes: u64,
    memory_cap: usize, relation_bytes: usize, relations_built: usize,
    branches: u64, contradictions: u64, max_depth: usize,
}
impl State {
    fn new(sizes: &[usize]) -> Self {
        let active = sizes.iter().map(|&size| {
            let mut row = vec![u64::MAX; size.div_ceil(64)];
            if size % 64 != 0 { *row.last_mut().unwrap() = (1u64 << (size % 64))-1; }
            row
        }).collect();
        Self { active, counts: sizes.to_vec() }
    }
    fn ids(&self, u: usize) -> Vec<usize> {
        let mut ids=Vec::new();
        for (word_id,&word) in self.active[u].iter().enumerate() {
            let mut rest=word;
            while rest!=0 { ids.push(word_id*64+rest.trailing_zeros() as usize); rest&=rest-1; }
        }
        ids
    }
    fn choose(&mut self,u:usize,id:usize) {
        self.active[u].fill(0); self.active[u][id/64]=1u64<<(id%64); self.counts[u]=1;
    }
}
impl Engine {
    fn time(&self)->std::result::Result<(),String> {
        if self.started.elapsed().as_secs_f64()>=self.seconds {Err("TIME_CAP".into())} else {Ok(())}
    }
    fn ensure_relation(&mut self,u:usize,v:usize)->std::result::Result<(),String> {
        if self.relations[u*self.n+v].is_some(){return Ok(());}
        self.time()?;
        let (a,b)=(self.sizes[u],self.sizes[v]);
        let required=(a as u64).checked_mul(b as u64).ok_or("PAIR_SIZE_OVERFLOW")?;
        if required>self.pair_cap.saturating_sub(self.checks){return Err("DOMAIN_PAIR_CAP".into());}
        let (aw,bw)=(b.div_ceil(64),a.div_ceil(64));
        let words=a.checked_mul(aw).and_then(|x|b.checked_mul(bw).and_then(|y|x.checked_add(y))).ok_or("RELATION_SIZE_OVERFLOW")?;
        let bytes=words.checked_mul(8).ok_or("RELATION_SIZE_OVERFLOW")?;
        if bytes>self.memory_cap.saturating_sub(self.relation_bytes){return Err("RELATION_MEMORY_CAP".into());}
        let mut left=Relation{words:aw,supports:vec![0;a*aw]};
        let mut right=Relation{words:bw,supports:vec![0;b*bw]};
        for i in 0..a {
            self.time()?;
            let nu=self.neighborhoods[u][i];
            for j in 0..b {
                self.checks+=1;
                let nv=self.neighborhoods[v][j];
                let edge=(nu>>(v+15))&1;
                if edge==((nv>>(u+15))&1) && (nu&nv).count_ones()==2-edge as u32 {
                    left.supports[i*aw+j/64]|=1u64<<(j%64);
                    right.supports[j*bw+i/64]|=1u64<<(i%64);
                }
            }
        }
        self.relations[u*self.n+v]=Some(left);
        self.relations[v*self.n+u]=Some(right);
        self.relation_bytes+=bytes; self.relations_built+=1;
        Ok(())
    }
    fn propagate(&mut self,state:&mut State,changed:Option<usize>,mut events:Option<&mut Vec<Event>>)->std::result::Result<Option<usize>,String> {
        let mut queue=VecDeque::new(); let mut queued=vec![false;self.n*self.n];
        if let Some(v)=changed {
            for u in 0..self.n {if u!=v {queue.push_back((u,v));queued[u*self.n+v]=true;}}
        } else {
            let mut pairs=Vec::new();
            for u in 0..self.n {for v in u+1..self.n {pairs.push((self.sizes[u]*self.sizes[v],u,v));}}
            pairs.sort_unstable();
            for (_,u,v) in pairs {for (a,b) in [(u,v),(v,u)] {queue.push_back((a,b));queued[a*self.n+b]=true;}}
        }
        while let Some((u,v))=queue.pop_front() {
            self.time()?; queued[u*self.n+v]=false;
            if state.counts[u]==0 {return Ok(Some(u));}
            if state.counts[v]==0 {return Ok(Some(v));}
            self.ensure_relation(u,v)?;
            let relation=self.relations[u*self.n+v].as_ref().unwrap();
            let removed:Vec<_>=state.ids(u).into_iter().filter(|&i| {
                !relation.supports[i*relation.words..(i+1)*relation.words].iter().zip(&state.active[v]).any(|(a,b)|a&b!=0)
            }).collect();
            if removed.is_empty(){continue;}
            let before=state.counts[u];
            for &id in &removed {state.active[u][id/64]&=!(1u64<<(id%64));}
            state.counts[u]-=removed.len();
            if let Some(trace)=events.as_mut() {trace.push(Event{u,v,removed,before,after:state.counts[u]});}
            if state.counts[u]==0 {return Ok(Some(u));}
            for w in 0..self.n {if w!=u && !queued[w*self.n+u] {queue.push_back((w,u));queued[w*self.n+u]=true;}}
        }
        Ok(None)
    }
    fn dfs(&mut self,state:State,depth:usize)->Outcome {
        if let Err(reason)=self.time(){return Outcome::Capped(reason);}
        if self.nodes>=self.node_cap{return Outcome::Capped("NODE_CAP".into());}
        self.nodes+=1; self.max_depth=self.max_depth.max(depth);
        let choice=(0..self.n).filter(|&u|state.counts[u]>1).min_by_key(|&u|(state.counts[u],u));
        let Some(u)=choice else {
            if state.counts.iter().any(|&n|n==0){return Outcome::Exhausted;}
            let ids:Vec<_>=(0..self.n).map(|v|state.ids(v)[0]).collect();
            // Defensive leaf check independent of queue scheduling.
            for a in 0..self.n {for b in a+1..self.n {
                if let Err(reason)=self.ensure_relation(a,b){return Outcome::Capped(reason);}
                let rel=self.relations[a*self.n+b].as_ref().unwrap();
                if rel.supports[ids[a]*rel.words+ids[b]/64]&(1u64<<(ids[b]%64))==0 {return Outcome::Exhausted;}
            }}
            return Outcome::Found(ids);
        };
        for id in state.ids(u) {
            if let Err(reason)=self.time(){return Outcome::Capped(reason);}
            if self.nodes>=self.node_cap{return Outcome::Capped("NODE_CAP".into());}
            self.branches+=1;
            let mut child=state.clone();child.choose(u,id);
            match self.propagate(&mut child,Some(u),None) {
                Err(reason)=>return Outcome::Capped(reason),
                Ok(Some(_))=>{self.contradictions+=1;self.nodes+=1;},
                Ok(None)=>match self.dfs(child,depth+1) {
                    Outcome::Found(ids)=>return Outcome::Found(ids),
                    Outcome::Capped(reason)=>return Outcome::Capped(reason),
                    Outcome::Exhausted=>{},
                }
            }
        }
        Outcome::Exhausted
    }
}

fn verify_witness(graph:&Graph,domains:&[Vec<u128>],ids:&[usize])->Result<Vec<(usize,usize)>> {
    if ids.len()!=84{return Err("wrong witness size".into());}
    let mut rows=graph.adjacency;
    for u in 0..84 {
        if ids[u]>=domains[u].len(){return Err("witness domain ID out of range".into());}
        rows[u+15]|=domains[u][ids[u]]<<15;
    }
    for u in 0..99 {
        if rows[u].count_ones()!=14 || rows[u]&(1u128<<u)!=0{return Err("invalid witness degree/loop".into());}
        for v in u+1..99 {
            let edge=(rows[u]>>v)&1;
            if edge!=((rows[v]>>u)&1) || (rows[u]&rows[v]).count_ones()!=2-edge as u32{return Err("invalid full99 witness pair".into());}
        }
    }
    Ok((0..99).flat_map(|u|(u+1..99).filter_map(move |v|if rows[u]&(1u128<<v)!=0{Some((u+1,v+1))}else{None})).collect())
}

fn synthetic(colors:usize)->Engine {
    let n=3;let sizes=vec![colors;n];
    let mut relations=vec![None;n*n];
    for u in 0..n {for v in 0..n {if u!=v {
        relations[u*n+v]=Some(Relation{words:1,supports:(0..colors).map(|i|((1u64<<colors)-1)&!(1u64<<i)).collect()});
    }}}
    Engine{n,sizes,neighborhoods:vec![vec![0;colors];n],relations,started:Instant::now(),seconds:10.0,
        pair_cap:1000,checks:0,node_cap:1000,nodes:0,memory_cap:100000,relation_bytes:0,relations_built:0,
        branches:0,contradictions:0,max_depth:0}
}
fn self_test()->Result<()> {
    let mut results=Vec::new();
    for colors in [2,3] {
        let mut engine=synthetic(colors);let mut state=State::new(&engine.sizes);
        if engine.propagate(&mut state,None,None)?.is_some(){return Err("synthetic root unexpectedly empty".into());}
        let outcome=engine.dfs(state,0);
        let status=match outcome {
            Outcome::Found(ids) if colors==3 && ids==vec![0,1,2]=>"FOUND_SYNTHETIC_ASSIGNMENT",
            Outcome::Exhausted if colors==2=>"EXHAUSTED_SYNTHETIC_CSP",
            _=>return Err("synthetic DFS result wrong".into()),
        };
        if engine.branches==0{return Err("self-test did not branch".into());}
        results.push(format!("{{\"colors\":{colors},\"status\":\"{status}\",\"nodes\":{},\"branches\":{}}}",engine.nodes,engine.branches));
    }
    let mut engine=synthetic(3);engine.node_cap=1;
    if !matches!(engine.dfs(State::new(&engine.sizes),0),Outcome::Capped(ref s) if s=="NODE_CAP"){return Err("node cap control failed".into());}
    let mut engine=synthetic(3);engine.seconds=0.0;
    if !matches!(engine.dfs(State::new(&engine.sizes),0),Outcome::Capped(ref s) if s=="TIME_CAP"){return Err("time cap control failed".into());}
    println!("{{\"status\":\"JOINT_STAR_SYNTHETIC_BRANCH_CONTROLS_PASS\",\"controls\":[{}],\"node_cap_rejected\":true,\"time_cap_rejected\":true,\"conway_witness_claim\":false}}",results.join(","));
    Ok(())
}

fn run()->Result<()> {
    let args:Vec<_>=std::env::args().collect();
    if args.len()==2 && args[1]=="--self-test"{return self_test();}
    if !(4..=9).contains(&args.len()){return Err("usage: joint_star_dfs CANDIDATE DOMAINS OUTPUT [seconds=30] [nodes=100000] [pairs=500000000] [memory_mib=256] [ac|search=ac]".into());}
    if std::path::Path::new(&args[3]).exists(){return Err("output exists".into());}
    let seconds:f64=args.get(4).map(|s|s.parse()).transpose().map_err(|_|"bad seconds")?.unwrap_or(30.0);
    let node_cap:u64=args.get(5).map(|s|s.parse()).transpose().map_err(|_|"bad node cap")?.unwrap_or(100000);
    let pair_cap:u64=args.get(6).map(|s|s.parse()).transpose().map_err(|_|"bad pair cap")?.unwrap_or(500000000);
    let memory_mib:usize=args.get(7).map(|s|s.parse()).transpose().map_err(|_|"bad memory cap")?.unwrap_or(256);
    let mode=args.get(8).map(String::as_str).unwrap_or("ac");
    if !seconds.is_finite()||seconds<=0.0||node_cap==0||pair_cap==0||memory_mib==0||memory_mib>65536||!matches!(mode,"ac"|"search"){return Err("invalid mode/budgets".into());}
    let graph=Graph::read(&args[1])?;let domains=read_domains(&args[2],&graph)?;
    // Check every domain's completed root-label equations directly. Domains
    // need not be declared complete here; completeness is an external proof gate.
    for u in 0..84 {for &mask in &domains[u] {
        let nu=graph.adjacency[u+15]|(mask<<15);
        for s in 1..15 {
            let edge=(nu>>s)&1;
            if (nu&graph.adjacency[s]).count_ones()!=2-edge as u32{return Err("invalid star root-label equation".into());}
        }
    }}
    let neighborhoods=domains.iter().enumerate().map(|(u,row)|row.iter().map(|m|graph.adjacency[u+15]|(m<<15)).collect()).collect();
    let sizes:Vec<_>=domains.iter().map(Vec::len).collect();
    let mut engine=Engine{n:84,sizes:sizes.clone(),neighborhoods,relations:vec![None;84*84],started:Instant::now(),seconds,
        pair_cap,checks:0,node_cap,nodes:0,memory_cap:memory_mib*1024*1024,relation_bytes:0,relations_built:0,
        branches:0,contradictions:0,max_depth:0};
    let mut root=State::new(&sizes);let mut events=Vec::new();
    let root_result=engine.propagate(&mut root,None,Some(&mut events));
    let (ac_status,empty,mut cap_reason)=match &root_result {Ok(Some(v))=>("EMPTY_DOMAIN",Some(*v),None),Ok(None)=>("ARC_CONSISTENT_NONEMPTY",None,None),Err(s)=>("INCOMPLETE",None,Some(s.clone()))};
    let mut assignment=None;let mut edges=None;
    let status=if cap_reason.is_some(){"UNKNOWN"}else if empty.is_some(){"UNSAT_CLAIM_UNVERIFIED"}else if mode=="ac"{"AC_NONEMPTY_NO_SEARCH"}else{
        match engine.dfs(root.clone(),0) {
            Outcome::Found(ids)=>{edges=Some(verify_witness(&graph,&domains,&ids)?);assignment=Some(ids);"SAT_NATIVE_VERIFIED_WITNESS"},
            Outcome::Exhausted=>"UNSAT_CLAIM_UNVERIFIED",
            Outcome::Capped(s)=>{cap_reason=Some(s);"UNKNOWN"},
        }
    };
    let mut out=format!("{{\"status\":\"{status}\",\"mode\":\"{mode}\",\"cap_reason\":{},\"seconds_limit\":{seconds},\"node_cap\":{node_cap},\"pair_cap\":{pair_cap},\"relation_memory_mib_cap\":{memory_mib},\"nodes\":{},\"branches\":{},\"contradictions\":{},\"maximum_depth\":{},\"domain_pairs_evaluated\":{},\"vertex_pair_relations_built\":{},\"relation_bytes\":{},\"elapsed_seconds\":{:.9},\"root_ac\":{{\"propagation_status\":\"{ac_status}\",\"empty_vertex\":{},\"events\":[",
        cap_reason.as_ref().map(|s|format!("\"{s}\"")).unwrap_or("null".into()),engine.nodes,engine.branches,engine.contradictions,engine.max_depth,
        engine.checks,engine.relations_built,engine.relation_bytes,engine.started.elapsed().as_secs_f64(),empty.map(|v|v.to_string()).unwrap_or("null".into()));
    for (i,e) in events.iter().enumerate(){if i>0{out.push(',');}write!(out,"{{\"target_vertex\":{},\"support_vertex\":{},\"removed_domain_ids\":{:?},\"before_count\":{},\"after_count\":{}}}",e.u,e.v,e.removed,e.before,e.after).unwrap();}
    out.push_str("],\"surviving_domain_ids\":[");
    for u in 0..84 {if u>0{out.push(',');}write!(out,"{:?}",root.ids(u)).unwrap();}
    out.push_str("]},\"selected_domain_ids\":");
    if let Some(ids)=assignment{write!(out,"{:?}",ids).unwrap();}else{out.push_str("null");}
    out.push_str(",\"edges_one_based\":");
    if let Some(pairs)=edges {out.push('[');for (i,(u,v)) in pairs.iter().enumerate(){if i>0{out.push(',');}write!(out,"[{u},{v}]").unwrap();}out.push(']');}else{out.push_str("null");}
    out.push_str(",\"independent_exclusion_proved\":false,\"scope\":\"One supplied star-domain CSP for one fixed K. Domain completeness and prior pruning require independent input audits. UNSAT is a native search claim only. Caps are UNKNOWN. A native witness requires separate full99 verification.\"}\n");
    use std::io::Write as IoWrite;
    let mut file=fs::OpenOptions::new().create_new(true).write(true).open(&args[3]).map_err(|e|e.to_string())?;
    file.write_all(out.as_bytes()).map_err(|e|e.to_string())?;
    println!("{status}: {} nodes, {} branches, {:.6}s",engine.nodes,engine.branches,engine.started.elapsed().as_secs_f64());
    Ok(())
}
fn main(){if let Err(error)=run(){eprintln!("{error}");std::process::exit(1);}}

