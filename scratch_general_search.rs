use std::fs;
use std::sync::{atomic::{AtomicBool, AtomicI64, Ordering}, Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const N: usize = 99;
const O: usize = 15;
const M: usize = 84;

#[derive(Clone)]
struct Rng(u64);
impl Rng {
    fn new(x: u64) -> Self { Self(x | 1) }
    fn u64(&mut self) -> u64 {
        let mut x=self.0; x^=x>>12; x^=x<<25; x^=x>>27; self.0=x;
        x.wrapping_mul(0x2545f4914f6cdd1d)
    }
    fn us(&mut self,n:usize)->usize {(self.u64() as usize)%n}
    fn unit(&mut self)->f64 {((self.u64()>>11) as f64)/(1u64<<53) as f64}
}

#[derive(Clone)]
struct Graph { adj:[[u64;2];N], cn:[[u8;N];N], e:i64 }
impl Graph {
    fn new()->Self { Self{adj:[[0;2];N],cn:[[0;N];N],e:0} }
    fn has(&self,u:usize,v:usize)->bool {self.adj[u][v>>6]&(1u64<<(v&63))!=0}
    fn raw(&mut self,u:usize,v:usize,on:bool) {
        let mv=1u64<<(v&63); let mu=1u64<<(u&63);
        if on {self.adj[u][v>>6]|=mv;self.adj[v][u>>6]|=mu}
        else {self.adj[u][v>>6]&=!mv;self.adj[v][u>>6]&=!mu}
    }
    fn pe(&self,u:usize,v:usize)->i64 {let d=self.cn[u][v] as i64+self.has(u,v) as i64-2;d*d}
    fn ac(&mut self,u:usize,v:usize,d:i8) {
        if u==v{return} let(a,b)=if u<v{(u,v)}else{(v,u)};
        self.e-=self.pe(a,b); let z=self.cn[a][b] as i16+d as i16;
        assert!(z>=0);self.cn[a][b]=z as u8;self.cn[b][a]=z as u8;self.e+=self.pe(a,b);
    }
    fn neigh(&self,u:usize)->[usize;16] {
        let mut a=[usize::MAX;16];let mut k=0;
        for q in 0..2 {let mut x=self.adj[u][q];while x!=0 {let b=x.trailing_zeros() as usize;let v=64*q+b;if v<N{a[k]=v;k+=1}x&=x-1}}
        a
    }
    fn toggle(&mut self,u:usize,v:usize,on:bool) {
        assert!(u!=v && self.has(u,v)!=on);
        if on {
            let nv=self.neigh(v);let nu=self.neigh(u);
            for &w in nv.iter().take_while(|&&x|x!=usize::MAX){self.ac(u,w,1)}
            for &w in nu.iter().take_while(|&&x|x!=usize::MAX){self.ac(v,w,1)}
            let(a,b)=(u.min(v),u.max(v));self.e-=self.pe(a,b);self.raw(u,v,true);self.e+=self.pe(a,b);
        } else {
            let(a,b)=(u.min(v),u.max(v));self.e-=self.pe(a,b);self.raw(u,v,false);self.e+=self.pe(a,b);
            let nv=self.neigh(v);let nu=self.neigh(u);
            for &w in nv.iter().take_while(|&&x|x!=usize::MAX){self.ac(u,w,-1)}
            for &w in nu.iter().take_while(|&&x|x!=usize::MAX){self.ac(v,w,-1)}
        }
    }
    fn init(&mut self) {
        self.e=0;
        for u in 0..N {for v in u+1..N {let c=(self.adj[u][0]&self.adj[v][0]).count_ones()+(self.adj[u][1]&self.adj[v][1]).count_ones();self.cn[u][v]=c as u8;self.cn[v][u]=c as u8;}}
        for u in 0..N {for v in u+1..N {self.e+=self.pe(u,v)}}
    }
    fn recalc(&self)->i64 {
        let mut e=0;for u in 0..N {for v in u+1..N {let c=(self.adj[u][0]&self.adj[v][0]).count_ones()+(self.adj[u][1]&self.adj[v][1]).count_ones();let d=c as i64+self.has(u,v) as i64-2;e+=d*d}}e
    }
}

#[derive(Clone)]
struct State { g:Graph, edges:Vec<(usize,usize)> }

fn add_scaffold(g:&mut Graph) {
    for s in 0..14 {g.raw(0,1+s,true)}
    for i in 0..7 {g.raw(1+2*i,2+2*i,true)}
    let mut x=O;
    for i in 0..7 {for j in i+1..7 {for a in 0..2 {for b in 0..2 {
        g.raw(x,1+2*i+a,true);g.raw(x,1+2*j+b,true);x+=1;
    }}}}
    assert_eq!(x,N);
}
fn canon(a:usize,b:usize)->(usize,usize){(a.min(b),a.max(b))}

fn initial(r:&mut Rng)->State {
    let mut g=Graph::new();add_scaffold(&mut g);let mut es=Vec::with_capacity(504);
    for x in 0..M {for d in 1..=6 {let y=(x+d)%M;if x<y || (y+M-x)%M==d {let e=canon(O+x,O+y);if !g.has(e.0,e.1){g.raw(e.0,e.1,true);es.push(e)}}}}
    // The preceding unique-edge rule is deliberately checked rather than trusted.
    if es.len()!=504 {
        es.clear();g=Graph::new();add_scaffold(&mut g);
        for x in 0..M {for d in 1..=6 {let y=(x+d)%M;let(a,b)=canon(O+x,O+y);if !g.has(a,b){g.raw(a,b,true);es.push((a,b))}}}
    }
    assert_eq!(es.len(),504);
    // Mix the circulant by valid degree-preserving switches before scoring.
    for _ in 0..20000 {
        let i=r.us(es.len());let mut j=r.us(es.len()-1);if j>=i{j+=1}
        let(a,b)=es[i];let(c,d)=es[j];if a==c||a==d||b==c||b==d{continue}
        let (p,q,r1,s)=if r.us(2)==0{(a,c,b,d)}else{(a,d,b,c)};
        if g.has(p,q)||g.has(r1,s){continue}
        g.raw(a,b,false);g.raw(c,d,false);g.raw(p,q,true);g.raw(r1,s,true);
        es[i]=canon(p,q);es[j]=canon(r1,s);
    }
    g.init();State{g,edges:es}
}

#[derive(Copy,Clone)] struct Move{ i:usize,j:usize, old1:(usize,usize),old2:(usize,usize),new1:(usize,usize),new2:(usize,usize) }
fn proposal(s:&State,r:&mut Rng)->Option<Move>{
    for _ in 0..20 {
        let i=r.us(s.edges.len());let mut j=r.us(s.edges.len()-1);if j>=i{j+=1}
        let(a,b)=s.edges[i];let(c,d)=s.edges[j];if a==c||a==d||b==c||b==d{continue}
        let(n1,n2)=if r.us(2)==0{(canon(a,c),canon(b,d))}else{(canon(a,d),canon(b,c))};
        if !s.g.has(n1.0,n1.1)&&!s.g.has(n2.0,n2.1){return Some(Move{i,j,old1:(a,b),old2:(c,d),new1:n1,new2:n2})}
    } None
}
fn apply(s:&mut State,m:Move,keep:bool){
    s.g.toggle(m.old1.0,m.old1.1,false);s.g.toggle(m.old2.0,m.old2.1,false);
    s.g.toggle(m.new1.0,m.new1.1,true);s.g.toggle(m.new2.0,m.new2.1,true);
    if keep{s.edges[m.i]=m.new1;s.edges[m.j]=m.new2}
}
fn undo(s:&mut State,m:Move){
    s.g.toggle(m.new1.0,m.new1.1,false);s.g.toggle(m.new2.0,m.new2.1,false);
    s.g.toggle(m.old1.0,m.old1.1,true);s.g.toggle(m.old2.0,m.old2.1,true);
}

fn worker(id:usize,deadline:Instant,gb:Arc<AtomicI64>,best:Arc<Mutex<Option<State>>>,stop:Arc<AtomicBool>){
    let nanos=SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64;
    let mut r=Rng::new(nanos^((id as u64+1).wrapping_mul(0x9e3779b97f4a7c15)));
    while Instant::now()<deadline && !stop.load(Ordering::Relaxed){
        let mut s=initial(&mut r);let mut lb=s.clone();let mut noimp=0usize;
        for step in 0..2_000_000usize {
            if step&0x3fff==0 && (Instant::now()>=deadline||stop.load(Ordering::Relaxed)){break}
            let Some(m)=proposal(&s,&mut r) else{continue};let old=s.g.e;apply(&mut s,m,false);let de=s.g.e-old;
            let phase=(step%200_000) as f64/200_000.0;
            let temp=6.0*(0.02f64/6.0).powf(phase);
            if de<=0 || r.unit()<(-(de as f64)/temp).exp(){s.edges[m.i]=m.new1;s.edges[m.j]=m.new2;
                if s.g.e<lb.g.e {lb=s.clone();noimp=0;let was=gb.fetch_min(s.g.e,Ordering::Relaxed);if s.g.e<was {
                    let mut z=best.lock().unwrap();if z.as_ref().map_or(true,|q|s.g.e<q.g.e){*z=Some(s.clone())}
                    if s.g.e<was-5 || s.g.e<200 {eprintln!("worker={id} step={step} best={}",s.g.e)}
                    if s.g.e==0{assert_eq!(s.g.recalc(),0);stop.store(true,Ordering::Relaxed);break}
                }}else{noimp+=1}
            }else{undo(&mut s,m);assert_eq!(s.g.e,old);noimp+=1}
            if step>0 && step%200_000==199_999 {assert_eq!(s.g.e,s.g.recalc());s=lb.clone();for _ in 0..8 {if let Some(k)=proposal(&s,&mut r){apply(&mut s,k,true)}}}
            if noimp>700_000{break}
        }
    }
}

fn diagnostics(s:&State)->(usize,usize,usize){
    let mut bad=0;let mut maxr=0;for u in 0..N{assert_eq!((s.g.adj[u][0].count_ones()+s.g.adj[u][1].count_ones()) as usize,14);for v in u+1..N{let r=(s.g.cn[u][v] as i16+s.g.has(u,v) as i16-2).unsigned_abs() as usize;if r>0{bad+=1;maxr=maxr.max(r)}}} (bad,maxr,s.edges.len()+189)
}
fn save(s:&State){
    let(bad,maxr,ec)=diagnostics(s);let re=s.g.recalc();assert_eq!(re,s.g.e);
    let mut out=format!("{{\n  \"energy\": {},\n  \"recomputed_energy\": {},\n  \"bad_pairs\": {},\n  \"max_abs_residual\": {},\n  \"edge_count\": {},\n  \"edges\": [\n",s.g.e,re,bad,maxr,ec);
    let mut first=true;for u in 0..N{for v in u+1..N{if s.g.has(u,v){if !first{out.push_str(",\n")}first=false;out.push_str(&format!("    [{}, {}]",u+1,v+1));}}}out.push_str("\n  ]\n}\n");
    fs::write("scratch_general_best.json",out).unwrap();
    println!("BEST energy={} recomputed={} bad_pairs={} max_residual={} edges={}",s.g.e,re,bad,maxr,ec);
}
fn main(){
    let a:Vec<_>=std::env::args().collect();let sec=a.get(1).and_then(|x|x.parse().ok()).unwrap_or(60u64);let nt=a.get(2).and_then(|x|x.parse().ok()).unwrap_or_else(||thread::available_parallelism().map_or(1,usize::from));
    let deadline=Instant::now()+Duration::from_secs(sec);let gb=Arc::new(AtomicI64::new(i64::MAX));let best=Arc::new(Mutex::new(None));let stop=Arc::new(AtomicBool::new(false));let mut hs=Vec::new();
    for id in 0..nt{let(g,b,s)=(gb.clone(),best.clone(),stop.clone());hs.push(thread::spawn(move||worker(id,deadline,g,b,s)))}for h in hs{h.join().unwrap()}
    if let Some(ref s)=*best.lock().unwrap(){save(s);if s.g.e==0{println!("SOLUTION")}}else{println!("NO_STATE")};
}
