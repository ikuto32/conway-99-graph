"""Independent exact trace primitives; no annealer producer imports or popcount delta."""
from itertools import combinations
from pathlib import Path
import math

MASK=(1<<64)-1
def need(ok,message):
    if not ok:raise ValueError(message)

def read_input(path):
    words=Path(path).read_text().split();position=0
    def take(convert=str):
        nonlocal position
        need(position<len(words),'truncated native input');value=convert(words[position]);position+=1;return value
    need(take()=='FACTOR_PERMUTATION_V1','native input version')
    n,chains,steps,mode=take(int),take(int),take(int),take(int);temperature=take(float);m=n*(n-2)//2
    need(4<=n<=20 and n%2==0 and 1<=chains<=256 and 0<=steps<=1024 and mode in(0,1),'native dimension/mode bounds')
    need(math.isfinite(temperature)and 0<=temperature<=1e6,'finite temperature')
    target=[[take(int)for _ in range(3*n)]for _ in range(3*n)]
    edges=[[[take(int),take(int)]for _ in range(m)]for _ in range(3)]
    states=[]
    for _ in range(chains):
        rng,proposals=take(int),take(int)
        current=[list(range(m))]+[[take(int)for _ in range(m)]for _ in range(2)]
        best=[list(range(m))]+[[take(int)for _ in range(m)]for _ in range(2)]
        need(1<=rng<=MASK and proposals>=0,'state header')
        need(all(sorted(p)==list(range(m))for p in current+best),'state permutations')
        states.append(dict(rng=rng,proposals=proposals,current=current,best=best))
    need(position==len(words),'trailing native input')
    return dict(n=n,m=m,chains=chains,steps=steps,mode=mode,temperature=temperature,target=target,edges=edges,states=states)

def bind_core(problem,core):
    n,m=problem['n'],problem['m'];need(len(core)==3*n and all(len(r)==3*n for r in core),'raw core dimensions')
    need(all(type(x)is int and x in(0,1)for row in core for x in row),'literal core bits')
    need(all(core[r][r]==0 and sum(core[r])==3 for r in range(3*n)),'simple cubic core')
    need(all(core[r][s]==core[s][r]for r,s in combinations(range(3*n),2)),'symmetric core')
    need(all(sum(core[r][g*n:g*n+n])==1 for r in range(3*n)for g in range(3)),'three matching blocks')
    for g in range(3):
        expected=[list(p)for p in combinations(range(n),2)if not core[g*n+p[0]][g*n+p[1]]]
        need(problem['edges'][g]==expected,'complete ordered nonmatching catalogue')
    need(all(core[i][j]==int(j==(i^1))for i in range(n)for j in range(n)),'canonical first matching')
    need(all(core[i][g*n+j]==int(i==j)for g in(1,2)for i in range(n)for j in range(n)),'canonical root-cross matchings')
    target=[[n*int(r==s)-core[r][s]-sum(core[r][t]*core[t][s]for t in range(3*n))+2-int(r//n==s//n)for s in range(3*n)]for r in range(3*n)]
    need(problem['target']==target,'every raw target coefficient from core')

def exact_score(problem,permutations):
    n,m=problem['n'],problem['m'];edges=problem['edges'];target=problem['target'];scores=[]
    need(all(sorted(p)==list(range(m))for p in permutations),'score domain permutations')
    for g,h in combinations(range(3),2):
        counts=[[0]*n for _ in range(n)]
        for d in range(m):
            for r in edges[g][permutations[g][d]]:
                for s in edges[h][permutations[h][d]]:counts[r][s]+=1
        scores.append(sum((counts[r][s]-target[g*n+r][h*n+s])**2 for r in range(n)for s in range(n)))
    return sum(scores),scores

def factor(problem,permutations):
    n,m=problem['n'],problem['m'];f=[[0]*m for _ in range(3*n)]
    for g in range(3):
        for d,index in enumerate(permutations[g]):
            for r in problem['edges'][g][index]:f[g*n+r][d]=1
    return f

def next_rng(state):
    state^=state>>12;state^=(state<<25)&MASK;state^=state>>27
    return state,(state*2685821657736338717)&MASK

def proposal(state,m):
    state,g=next_rng(state);state,a=next_rng(state);state,b=next_rng(state);state,u=next_rng(state)
    g=1+g%2;a%=m;b%=m-1
    if b>=a:b+=1
    # The C++ decimal denominator rounds to 2**53 in binary64.
    return state,g,a,b,((u>>11)+1)/float(1<<53)

def audit_chain(problem,initial,output):
    m=problem['m'];rng=initial['rng'];current=[r[:]for r in initial['current']];best=[r[:]for r in initial['best']]
    score,_=exact_score(problem,current);best_score,_=exact_score(problem,best);need(best_score<=score,'initial best no worse than current')
    trace=output['trace'];need(len(trace)==problem['steps'],'complete proposal trace');minimum_margin=None;accepted=0
    boundaries={63:0,127:0}
    for step,entry in enumerate(trace):
        need(len(entry)==7 and all(type(v)is int for v in entry),'literal trace row')
        rng,g,a,b,u=proposal(rng,m);need(entry[:3]==[g,a,b],'independent RNG/proposal replay')
        proposed=[r[:]for r in current];proposed[g][a],proposed[g][b]=proposed[g][b],proposed[g][a]
        new_score,_=exact_score(problem,proposed);delta=new_score-score;need(entry[3]==delta,'exact full-score proposal delta')
        if problem['mode']==0 or delta<=0:yes=True
        elif problem['temperature']==0:yes=False
        else:
            threshold=math.exp(-delta/problem['temperature']);margin=abs(u-threshold)
            minimum_margin=margin if minimum_margin is None else min(minimum_margin,margin)
            need(margin>1e-12,'acceptance too near floating threshold for this finite parity audit');yes=u<threshold
        need(entry[4]==int(yes),'finite saved acceptance rule')
        if yes:
            accepted+=1;current=proposed;score=new_score
            if score<best_score:best_score=score;best=[r[:]for r in current]
        need(entry[5:]==[score,best_score],'saved exact current/best scores')
        for boundary in boundaries:
            if min(a,b)<=boundary<max(a,b):boundaries[boundary]+=1
    need(int(output['rng'])==rng and output['proposals']==initial['proposals']+len(trace),'resumable RNG/proposal counter')
    need(output['permutations']==current[1:]and output['best_permutations']==best[1:],'complete final/current best permutation states')
    need(output['score']==score and output['best_score']==best_score,'final score identities')
    return dict(proposals=len(trace),accepted=accepted,final_score=score,best_score=best_score,minimum_positive_temperature_acceptance_margin=minimum_margin,
      minimum_margin_null_reason='No positive-delta positive-temperature acceptance decision.'if minimum_margin is None else None,
      word_boundary_crossings=boundaries,final_factor=factor(problem,current),best_factor=factor(problem,best))
