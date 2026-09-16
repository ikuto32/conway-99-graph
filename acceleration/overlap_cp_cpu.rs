//! Dependency-free matrix-free phase-I matvec/Chambolle-Pock control.
//! C99CP1 count checkpoint_count, ascending checkpoints,1680X,4326Y,
//! then count complete168-edge K graphs. CLI INPUT OUTPUT [--vectors].
//! Same geometry as full99:840foreign-label rows then3486outer pairs;
//!1680lexicographic disjoint columns. No stored sparse constraint matrix.
//! rustc -O -C target-cpu=native acceleration/overlap_cp_cpu.rs -o acceleration/build/overlap_cp_cpu.exe

use std::fmt::Write as FmtWrite;
use std::io::Write as IoWrite;
use std::{fs,time::Instant};
const N:usize=84;
const Q:usize=840;
const R:usize=4326;
const C:usize=1680;
const NONE:usize=usize::MAX;
struct Geometry {
    labels:[[usize;2];N], supports:[u8;N], columns:Vec<(usize,usize)>,
    col_index:[[usize;N];N], quotas:Vec<(usize,usize)>, quota_index:[[usize;14];N],
    pairs:Vec<(usize,usize)>, pair_index:[[usize;N];N],
}
struct Graph { neighbors:[[usize;4];N], known:[u128;N] }
struct Input { geometry:Geometry, graphs:Vec<Graph>, steps:Vec<usize>, x:Vec<f64>, y:Vec<f64> }
fn number<T:std::str::FromStr>(tokens:&mut std::str::SplitWhitespace<'_>,name:&str)->Result<T,String> {
    tokens.next().ok_or_else(||format!("Missing {name}"))?.parse().map_err(|_|format!("Invalid {name}"))
}
fn geometry()->Geometry {
    let mut g=Geometry{labels:[[0;2];N],supports:[0;N],columns:Vec::new(),col_index:[[NONE;N];N],
        quotas:Vec::new(),quota_index:[[NONE;14];N],pairs:Vec::new(),pair_index:[[NONE;N];N]};
    let mut index=0;
    for a in 0..7 { for b in a+1..7 { for s in 0..2 { for t in 0..2 {
        g.labels[index]=[2*a+s,2*b+t];g.supports[index]=(1<<a)|(1<<b);index+=1;
    }}}}
    for u in 0..N {
        for s in 0..14 { if g.supports[u]&(1<<(s/2))==0 {
            g.quota_index[u][s]=g.quotas.len();g.quotas.push((u,s));
        }}
        for v in u+1..N {
            let p=g.pairs.len()+Q;g.pair_index[u][v]=p;g.pair_index[v][u]=p;g.pairs.push((u,v));
            if g.supports[u]&g.supports[v]==0 {
                let c=g.columns.len();g.col_index[u][v]=c;g.col_index[v][u]=c;g.columns.push((u,v));
            }
        }
    }
    assert_eq!((g.columns.len(),g.quotas.len(),g.pairs.len()),(C,Q,R-Q));g
}
fn put(rows:&mut [u128;99],u:usize,v:usize) {rows[u]|=1u128<<v;rows[v]|=1u128<<u;}
fn read_input(path:&str)->Result<Input,String> {
    let text=fs::read_to_string(path).map_err(|e|e.to_string())?;
    let mut tokens=text.split_whitespace();
    if tokens.next()!=Some("C99CP1") {return Err("Expected C99CP1".into());}
    let count:usize=number(&mut tokens,"candidate count")?;
    let count_steps:usize=number(&mut tokens,"checkpoint count")?;
    if !(1..=100000).contains(&count) || !(1..=32).contains(&count_steps) {return Err("Count outside input limits".into());}
    let mut steps=Vec::new();
    for _ in 0..count_steps {
        let step:usize=number(&mut tokens,"checkpoint")?;
        if !(1..=1000000).contains(&step) || steps.last().is_some_and(|&last|last>=step) {
            return Err("Checkpoints must strictly increase within1..1000000".into());
        }steps.push(step);
    }
    let mut x=Vec::with_capacity(C);let mut y=Vec::with_capacity(R);
    for _ in 0..C {let value:f64=number(&mut tokens,"X")?;
        if !value.is_finite() || !(0.0..=1.0).contains(&value) {return Err("X outside finite[0,1]".into());}x.push(value);
    }
    for i in 0..R {let value:f64=number(&mut tokens,"Y")?;
        if !value.is_finite() || value<if i<Q {-1.0} else {0.0} || value>1.0 {return Err("Y outside finite dual box".into());}y.push(value);
    }
    let g=geometry();let mut graphs=Vec::with_capacity(count);
    for _ in 0..count {
        let mut full=[0u128;99];let mut known=[0u128;N];let mut neighbors=[[0usize;4];N];let mut degrees=[0usize;N];
        for s in 1..15 {put(&mut full,0,s);}for s in (1..15).step_by(2) {put(&mut full,s,s+1);}
        for u in 0..N {for &s in &g.labels[u] {put(&mut full,u+15,s+1);}}
        for _ in 0..168 {
            let u:usize=number(&mut tokens,"edge endpoint")?;let v:usize=number(&mut tokens,"edge endpoint")?;
            if u>=v || v>=N || (g.supports[u]&g.supports[v]).count_ones()!=1 || (known[u]>>v)&1!=0 {
                return Err("Invalid/duplicate overlap edge".into());
            }
            if degrees[u]>=4 || degrees[v]>=4 {return Err("Overlap degree exceeds four".into());}
            neighbors[u][degrees[u]]=v;neighbors[v][degrees[v]]=u;degrees[u]+=1;degrees[v]+=1;
            known[u]|=1u128<<v;known[v]|=1u128<<u;put(&mut full,u+15,v+15);
        }
        if degrees.iter().any(|&d|d!=4) {return Err("Overlap degree must equal four".into());}
        for u in 0..99 {for v in u+1..99 {
            if (full[u]&full[v]).count_ones()>2-((full[u]>>v)&1) as u32 {return Err("Full99 partial pair cap violated".into());}
        }}
        for u in 0..N {for s in 0..14 {if g.supports[u]&(1<<(s/2))!=0 &&
            (full[u+15]&full[s+1]).count_ones()!=2-((full[u+15]>>(s+1))&1) as u32 {return Err("Own-root quota violated".into());}
        }}
        for row in &mut neighbors {row.sort_unstable();}
        graphs.push(Graph{neighbors,known});
    }
    if tokens.next().is_some() {return Err("Trailing input".into());}
    Ok(Input{geometry:g,graphs,steps,x,y})
}
fn xvalue(g:&Geometry,x:&[f64],u:usize,v:usize)->f64 {
    let col=g.col_index[u][v];if col==NONE {0.0} else {x[col]}
}
fn forward(g:&Geometry,k:&Graph,x:&[f64])->Vec<f64> {
    let mut ax=vec![0.0;R];
    for (i,&(u,s)) in g.quotas.iter().enumerate() {
        for v in 0..N {if g.labels[v].contains(&s) {ax[i]+=xvalue(g,x,u,v);}}
    }
    for (i,&(u,v)) in g.pairs.iter().enumerate() {
        let mut value=xvalue(g,x,u,v);
        for &w in &k.neighbors[u] {value+=xvalue(g,x,v,w);}
        for &w in &k.neighbors[v] {value+=xvalue(g,x,u,w);}
        ax[Q+i]=value;
    }ax
}
fn backward(g:&Geometry,k:&Graph,y:&[f64])->Vec<f64> {
    let mut aty=vec![0.0;C];
    for (i,&(u,v)) in g.columns.iter().enumerate() {
        let mut value=0.0;
        for &s in &g.labels[v] {value+=y[g.quota_index[u][s]];}
        for &s in &g.labels[u] {value+=y[g.quota_index[v][s]];}
        value+=y[g.pair_index[u][v]];
        for &w in &k.neighbors[u] {value+=y[g.pair_index[v][w]];}
        for &w in &k.neighbors[v] {value+=y[g.pair_index[u][w]];}
        aty[i]=value;
    }aty
}
fn targets(g:&Geometry,k:&Graph)->Vec<f64> {
    let mut b=vec![0.0;R];
    for (i,&(u,s)) in g.quotas.iter().enumerate() {
        let known=k.neighbors[u].iter().filter(|&&v|g.labels[v].contains(&s)).count();
        b[i]=2.0-known as f64;
    }
    for (i,&(u,v)) in g.pairs.iter().enumerate() {
        let shared=g.labels[u].iter().filter(|s|g.labels[v].contains(s)).count();
        b[Q+i]=2.0-shared as f64-(k.known[u]&k.known[v]).count_ones() as f64-((k.known[u]>>v)&1) as f64;
    }b
}
fn bounds(g:&Geometry,k:&Graph,b:&[f64],x:&[f64],y:&[f64])->(f64,f64) {
    let ax=forward(g,k,x);let aty=backward(g,k,y);
    let primal=ax.iter().zip(b).enumerate().map(|(i,(&a,&target))|if i<Q {(a-target).abs()} else {(a-target).max(0.0)}).sum();
    let dual=-b.iter().zip(y).map(|(a,c)|a*c).sum::<f64>()+aty.iter().map(|&v|v.min(0.0)).sum::<f64>();
    (primal,dual)
}
fn bound_json(out:&mut String,value:(f64,f64)) {
    write!(out,"{{\"primal_upper\":{:?},\"dual_lower\":{:?}}}",value.0,value.1).unwrap();
}
fn run()->Result<(),String> {
    let args:Vec<_>=std::env::args().collect();
    if args.len()<3 || args.len()>4 || (args.len()==4 && args[3]!="--vectors") {return Err("Usage: overlap_cp_cpu INPUT OUTPUT [--vectors]".into());}
    if std::path::Path::new(&args[2]).exists() {return Err("Output already exists".into());}
    let input=read_input(&args[1])?;let vectors=args.len()==4;
    if vectors && input.graphs.len()>64 {return Err("Vectors limited to64candidates".into());}
    let start=Instant::now();let g=&input.geometry;
    let mut out=String::from("{\"status\":\"NUMERICAL_MATRIXFREE_CP_CPU_CONTROL\",\"candidate_count\":");
    write!(&mut out,"{},\"tau\":0.09,\"sigma\":0.09,\"theta\":1,\"quota_rows\":840,\"pair_rows\":3486,\"columns\":1680,\"results\":[",input.graphs.len()).unwrap();
    for (candidate,k) in input.graphs.iter().enumerate() {
        if candidate>0 {out.push(',');}
        let b=targets(g,k);let mut x=input.x.clone();let mut y=input.y.clone();let mut xbar=x.clone();
        let mut xavg=vec![0.0;C];let mut yavg=vec![0.0;R];let initial=bounds(g,k,&b,&x,&y);
        let rowsums=forward(g,k,&vec![1.0;C]);let colsums=backward(g,k,&vec![1.0;R]);
        if rowsums[..Q].iter().any(|&v|v!=8.0) || rowsums[Q..].iter().any(|&v|v>9.0) ||
            colsums.iter().any(|&v|v!=13.0) || rowsums.iter().sum::<f64>()!=21840.0 {return Err("Matrixfree incidence count mismatch".into());}
        write!(&mut out,"{{\"candidate_index\":{candidate},\"initial\":").unwrap();bound_json(&mut out,initial);
        if vectors {
            write!(&mut out,",\"initial_ax\":{:?},\"initial_at_y\":{:?},\"target_b\":{:?},\"row_sums\":{:?},\"column_sums\":{:?}",
                   forward(g,k,&x),backward(g,k,&y),b,rowsums,colsums).unwrap();
        }
        out.push_str(",\"checkpoints\":[");let mut next_checkpoint=0;let mut best_upper=initial.0;let mut best_lower=initial.1;
        for step in 1..=*input.steps.last().unwrap() {
            let ax=forward(g,k,&xbar);
            for i in 0..R {y[i]=(y[i]+0.09*(ax[i]-b[i])).clamp(if i<Q {-1.0} else {0.0},1.0);}
            let aty=backward(g,k,&y);
            for i in 0..C {
                let old=x[i];x[i]=(old-0.09*aty[i]).clamp(0.0,1.0);xbar[i]=2.0*x[i]-old;
                xavg[i]+=(x[i]-xavg[i])/step as f64;
            }
            for i in 0..R {yavg[i]+=(y[i]-yavg[i])/step as f64;}
            if step==input.steps[next_checkpoint] {
                let last=bounds(g,k,&b,&x,&y);let average=bounds(g,k,&b,&xavg,&yavg);
                best_upper=best_upper.min(last.0).min(average.0);best_lower=best_lower.max(last.1).max(average.1);
                if next_checkpoint>0 {out.push(',');}
                write!(&mut out,"{{\"iterations\":{step},\"last\":").unwrap();bound_json(&mut out,last);out.push_str(",\"average\":");bound_json(&mut out,average);
                write!(&mut out,",\"best_upper\":{best_upper:?},\"best_lower\":{best_lower:?}").unwrap();
                if vectors {write!(&mut out,",\"x_last\":{x:?},\"y_last\":{y:?},\"x_average\":{xavg:?},\"y_average\":{yavg:?}").unwrap();}
                out.push('}');next_checkpoint+=1;
                if next_checkpoint==input.steps.len() {break;}
            }
        }out.push_str("]}");
    }
    write!(&mut out,"],\"elapsed_seconds\":{},\"row_order\":\"u-major foreign symbols then lexicographic u<v outer pairs\",\"column_order\":\"lexicographic disjoint-support outer pairs\",\"scope\":\"Independent matrix-free CPU control; all values are numerical diagnostics, not LP optima, exclusion certificates or graph completions. Best bounds include only initial and requested last/average checkpoints.\"}}\n",start.elapsed().as_secs_f64()).unwrap();
    let mut file=fs::OpenOptions::new().write(true).create_new(true).open(&args[2]).map_err(|e|e.to_string())?;
    file.write_all(out.as_bytes()).map_err(|e|e.to_string())?;
    eprintln!("Matrixfree CP CPU {} candidates through step{} in {:.6}s",input.graphs.len(),input.steps.last().unwrap(),start.elapsed().as_secs_f64());Ok(())
}
fn main(){if let Err(error)=run(){eprintln!("{error}");std::process::exit(1);}}
