"""Independent complete weight60 V2 graph/state/move checking.

No native/producer imports. Prior independently authored RNG and strict error
helpers are disclosed; graph construction, fixed60 scoring, overlap predicate
and persistent first-selection logic are rederived here.
"""
import copy
from itertools import combinations
import json
import math
from pathlib import Path
import audit_20261002_hypergraph_controls_v2 as U
import audit_20261002_hypergraph_weighted_controls_v1 as W

need=U.need
CheckError=U.CheckError
OBJECTIVE='SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2'
KERNEL='LINEAR_TRIPLE_EXCLUSIVE_SWAP_V2'
SCALARS=W.SCALARS
KEYS=('weighted_energy','base_energy','lambda_energy','mu_energy')
RULE='First observed current graph with exact E_lambda0, including invocation initial state; retained across exact weight60 resumes, independent of best F60'
PRISM=[[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]
CUBE=[[1,2,7],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[0,10,11]]


def score(triples,n,degree):
    need((n,degree)in[(99,7),(9,2),(12,2)],'declared target or9/12point engineering domain','DOMAIN')
    need(len(triples)*3==n*degree,'exact labelled triple population','DOMAIN')
    occurrences=[0]*n;adj=[0]*n
    for triple in triples:
        need(len(triple)==3 and all(type(x)is int and 0<=x<n for x in triple)and len(set(triple))==3,'three distinct in-range points','DOMAIN')
        for x in triple:occurrences[x]+=1
        for x,y in combinations(triple,2):
            need(not(adj[x]>>y&1),'linear pair uniqueness','DOMAIN');adj[x]|=1<<y;adj[y]|=1<<x
    need(occurrences==[degree]*n and all(row.bit_count()==2*degree for row in adj),'exact point occurrences and graph degrees','DOMAIN')
    cn=[];el=em=0
    for u in range(n):
        for v in range(u+1,n):
            common=(adj[u]&adj[v]).bit_count();cn.append(common)
            if adj[u]>>v&1:el+=(common-1)**2
            else:em+=(common-2)**2
    return adj,cn,dict(weighted_energy=60*el+em,base_energy=el+em,lambda_energy=el,mu_energy=em)


def parse_state(data):
    try:tokens=data.decode('ascii').split()
    except UnicodeDecodeError:raise CheckError('SYNTAX','ASCII state required')
    at=0
    def take():
        nonlocal at
        need(at<len(tokens),'complete token stream','SYNTAX');v=tokens[at];at+=1;return v
    def field(name):need(take()==name,'ordered '+name,'SYNTAX');return take()
    need(take()=='HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2','new state version','SYNTAX')
    s=dict(objective=field('objective'),lambda_weight=U.natural(field('lambda_weight')))
    need(s['objective']==OBJECTIVE and s['lambda_weight']==60,'fixed60 objective','WEIGHT')
    s['move_kernel']=field('move_kernel');need(s['move_kernel']==KERNEL,'exclusive swap kernel','KERNEL')
    for key in SCALARS:
        raw=field(key);s[key]=float(raw)if key in['t_start','t_end']else U.natural(raw)
    need((s['n'],s['degree'])in[(99,7),(9,2),(12,2)],'exact allowed graph domain','DOMAIN')
    need(all(math.isfinite(s[k])and 0<=s[k]<=1000 for k in['t_start','t_end'])and s['schedule_steps']>0,'finite bounded schedule','SCHEDULE')
    need(all(0<=s[k]<=U.M for k in['seed','mix_steps','schedule_steps','step','admissible','accepted','best_updates'])and s['forced']in[0,1],'uint64 config/counters','COUNTERS')
    need(take()=='rng','RNG tag','SYNTAX');s['rng']=[U.natural(take(),'RNG')for _ in range(4)]
    need(all(0<=v<=U.M for v in s['rng'])and any(s['rng']),'nonzero uint64 RNG','RNG')
    def graph_field(key):
        count=U.natural(field(key));need(count==s['n']*s['degree']//3,'exact '+key+' triple population','DOMAIN')
        return[[U.natural(take())for _ in range(3)]for _ in range(count)]
    s['current']=graph_field('current');s['best']=graph_field('best')
    _,cn,current=score(s['current'],s['n'],s['degree']);_,_,best=score(s['best'],s['n'],s['degree'])
    need(s['weighted_energy']==current['weighted_energy'],'complete fixed60 current score','WEIGHTED')
    need(s['best_weighted_energy']==best['weighted_energy']<=current['weighted_energy'],'complete fixed60 best/order','BEST_WEIGHTED')
    need(all(s[k]==current[k]and s['best_'+k]==best[k]for k in KEYS if k!='weighted_energy'),'complete base/category components','COMPONENT')
    count=U.natural(field('cn'));need(count==len(cn),'CN cache population','CACHE');need([U.natural(take())for _ in range(count)]==cn,'complete CN cache','CACHE')
    found=U.natural(field('first_lambda0'),'FIRST_FLAG');need(found in[0,1],'binary first flag','FIRST_FLAG');s['first']=None
    if found:
        f={k:U.natural(field('first_'+k),'FIRST_COUNTER')for k in['step','admissible','accepted','best_updates']}
        need(take()=='first_rng','first RNG tag','SYNTAX');f['rng']=[U.natural(take(),'FIRST_RNG')for _ in range(4)]
        need(all(0<=v<=U.M for v in f['rng'])and any(f['rng']),'first nonzero uint64 RNG','FIRST_RNG')
        f['current']=graph_field('first_current');f['best']=graph_field('first_best')
        _,_,fc=score(f['current'],s['n'],s['degree']);_,_,fb=score(f['best'],s['n'],s['degree'])
        need(fc['lambda_energy']==0 and fb['weighted_energy']<=fc['weighted_energy'],'lambda0 selected graph and best/order','FIRST_SCORE')
        need(0<=f['best_updates']<=f['accepted']<=f['admissible']<=f['step']and all(0<=f[k]<=s[k]for k in['step','admissible','accepted','best_updates']),'first counters within exact current state','FIRST_COUNTER')
        s['first']=f
    need(s['lambda_energy']!=0 or s['first']is not None,'current lambda0 needs selected snapshot','FIRST_COMPLETENESS')
    need(take()=='END'and at==len(tokens),'exact record END','SYNTAX')
    need(0<=s['best_updates']<=s['accepted']<=s['admissible']<=s['step'],'main counter ordering','COUNTERS')
    return s


def capture(s,completed_step):
    if s['first']is None and s['lambda_energy']==0:
        s['first']={k:copy.deepcopy(s[k])for k in['admissible','accepted','best_updates','rng','current','best']};s['first']['step']=completed_step


def first_state(s):
    need(s['first']is not None,'selected snapshot exists','FIRST_COMPLETENESS');f=s['first'];expected=copy.deepcopy(s)
    for key in['step','admissible','accepted','best_updates','rng','current','best']:expected[key]=copy.deepcopy(f[key])
    expected.update(score(f['current'],s['n'],s['degree'])[2]);expected.update({'best_'+k:v for k,v in score(f['best'],s['n'],s['degree'])[2].items()})
    return expected


def initial(fixture):
    if fixture=='prism9':return copy.deepcopy(PRISM)
    if fixture=='cube12_defect':return copy.deepcopy(CUBE)
    need(fixture in['rook9','target99'],'known declared fixture','INITIAL');return U.initial(9 if fixture=='rook9'else 99)


def config(s,opts):
    need(s['seed']==int(opts['--seed'])and s['mix_steps']==int(opts['--mix-steps'])and s['schedule_steps']==int(opts['--schedule-steps'])and s['t_start']==float(opts['--temperature-start'])and s['t_end']==float(opts['--temperature-end'])and s['forced']==int('--forced'in opts),'exact new seed and schedule config','INITIAL')


def import_initial(s,data,selector,opts):
    need(selector in['current','best'],'explicit current/best import selection','IMPORT');original=W.parse_state(data)
    need(s['current']==s['best']==original[selector],'exact selected weight6 labelled graph','IMPORT')
    need(s['step']==s['admissible']==s['accepted']==s['best_updates']==0,'all old counters reset','IMPORT')
    need(s['rng']==U.seed_words(int(opts['--seed'])),'new RNG seeded independently','IMPORT');config(s,opts)
    expected=None
    if s['lambda_energy']==0:expected={k:copy.deepcopy(s[k])for k in['step','admissible','accepted','best_updates','rng','current','best']}
    need(s['first']==expected,'import initial lambda0 selection','IMPORT')


def replay(s,record=None):
    before=s['rng'][:];size=len(s['current']);ti=U.rng_next(s['rng'])%size;tj=U.rng_next(s['rng'])%(size-1)
    if tj>=ti:tj+=1
    pi=U.rng_next(s['rng'])%3;pj=U.rng_next(s['rng'])%3;t=s['current'][ti][:];q=s['current'][tj][:];x=t[pi];y=q[pj]
    outgoing={tuple(sorted((x,z)))for z in t if z!=x}|{tuple(sorted((y,z)))for z in q if z!=y}
    incoming=[(y,t[(pi+1)%3]),(y,t[(pi+2)%3]),(x,q[(pj+1)%3]),(x,q[(pj+2)%3])]
    adj,_,current=score(s['current'],s['n'],s['degree']);need(all(s[k]==v for k,v in current.items()),'complete score before proposal','REPLAY')
    disjoint=not bool(set(t)&set(q));exclusive=x not in q and y not in t
    absent=all(not(adj[u]>>v&1)for u,v in incoming)
    absent_after=all(u!=v and(not(adj[u]>>v&1)or tuple(sorted((u,v)))in outgoing)for u,v in incoming)
    valid=exclusive and absent_after;pt=t[:];pq=q[:];pt[pi]=y;pq[pj]=x
    fraction=min(1,float(max(0,s['step']-s['mix_steps']))/s['schedule_steps']);temp=s['t_start']+(s['t_end']-s['t_start'])*fraction;mixing=s['step']<s['mix_steps'];delta=0;draw=0;accepted=False;margin=None;first_before=s['first']is not None
    if valid:
        proposal=copy.deepcopy(s['current']);proposal[ti]=pt;proposal[tj]=pq;_,_,proposed=score(proposal,s['n'],s['degree']);delta=proposed['weighted_energy']-current['weighted_energy'];draw=U.rng_next(s['rng']);uniform=(draw>>11)/2**53
        if s['forced']or mixing or delta<=0:accepted=True
        elif temp>0:
            threshold=math.exp(-float(delta)/temp);margin=abs(uniform-threshold);need(margin>U.TOL,'unambiguous probabilistic acceptance','FLOAT');accepted=uniform<threshold
        s['admissible']+=1
        if accepted:
            s['current']=proposal;s.update(proposed);s['accepted']+=1
            if proposed['weighted_energy']<s['best_weighted_energy']:s['best']=copy.deepcopy(proposal);s.update({'best_'+k:v for k,v in proposed.items()});s['best_updates']+=1
    capture(s,s['step']+1)
    expected=dict(trace_schema='HYPERGRAPH_WEIGHT60_MOVE_V2',move_kernel=KERNEL,step=s['step'],ti=ti,tj=tj,pi=pi,pj=pj,old_triples=[t,q],proposed_triples=[pt,pq],disjoint=disjoint,new_pairs_absent=absent,selected_points_exclusive=exclusive,new_pairs_absent_after_old_removal=absent_after,admissible=valid,accepted=accepted,mixing=mixing,objective=OBJECTIVE,lambda_weight=60,delta=delta,weighted_energy_before=current['weighted_energy'],weighted_energy_after=s['weighted_energy'],lambda_energy_before=current['lambda_energy'],mu_energy_before=current['mu_energy'],lambda_energy_after=s['lambda_energy'],mu_energy_after=s['mu_energy'],best_weighted_energy=s['best_weighted_energy'],first_lambda0_before=first_before,first_lambda0_after=s['first']is not None,first_lambda0_step=None if s['first']is None else s['first']['step'],draw=str(draw),rng_before=[str(w)for w in before],rng_after=[str(w)for w in s['rng']])
    if record is not None:
        need(set(record)==set(expected)|{'temperature'},'complete V2 trace fields','REPLAY')
        for k,v in expected.items():need(type(record[k])is type(v)and record[k]==v,'exact trace field '+k,'REPLAY')
        need(type(record['temperature'])in[int,float]and math.isfinite(record['temperature'])and abs(record['temperature']-temp)<=U.TOL,'temperature tolerance','FLOAT')
    s['step']+=1
    # Rejected admissible proposals are checked by untouched complete labelled
    # graph and subsequent native checkpoint equality, not inverse-toggle code.
    return dict(valid=valid,accepted=accepted,delta=delta,margin=margin,overlap=not disjoint,exclusive=exclusive,absence_before=absent,absence_after=absent_after),dict(expected,temperature=temp)


def pair_costs():
    rows=[]
    def components(c,a):return((c-1)**2,0)if a else(0,(c-2)**2)
    for c in range(15):
        for a in range(2):
            changes=[('CN',d,c+d,a)for d in[-1,1]if 0<=c+d<=14]+[('EDGE',1-2*a,c,1-a)]
            for kind,d,nc,na in changes:
                ol,om=components(c,a);nl,nm=components(nc,na);rows.append(dict(kind=kind,c=c,a=a,delta=d,new_c=nc,new_a=na,old_lambda=ol,old_mu=om,new_lambda=nl,new_mu=nm,delta_F=60*(nl-ol)+(nm-om)))
    need(len(rows)==86,'complete pair-cost population','PAIR');return rows


def raw_matrix(data,n):
    try:lines=data.decode('ascii').splitlines()
    except UnicodeDecodeError:raise CheckError('MATRIX','ASCII matrix')
    need(lines and lines[0]==str(n)and len(lines)==n+1 and all(len(line)==n and set(line)<=set('01')for line in lines[1:]),'complete binary matrix syntax/dimensions','MATRIX')
    return[[int(x)for x in line]for line in lines[1:]]


def matrix_matches(matrix,triples,n,degree):
    bits,_,_=score(triples,n,degree);need(matrix==[[int(bits[u]>>v&1)for v in range(n)]for u in range(n)],'matrix equals reconstructed complete labelled graph','MATRIX')


def selection(s,initial,options,value):
    expected=dict(schema='FIRST_LAMBDA0_SELECTION_V1',found=s['first']is not None,selection_rule=RULE,first_step=None if s['first']is None else s['first']['step'],carried_from_resume=('--resume'in options and s['first']is not None and s['first']['step']<=initial['step']),target_resolution=False,independent_approval=False)
    need(value==expected and all(type(value[k])is type(v)for k,v in expected.items()),'exact first-selection metadata','SELECTION')


def calibration(base):
    controls=[]
    for fixture,n,expected in[('rook9',9,(0,0)),('prism9',9,(6,6)),('cube12_defect',12,(6,62)),('target99',99,(6930,12870))]:
        adj,cn,values=score(initial(fixture),n,7 if n==99 else 2);need((values['lambda_energy'],values['mu_energy'])==expected,'exact known component fixture','CONTROL')
        # Different pure scalar row/column matrix multiplication on small fixtures.
        if n<99:
            matrix=[[int(adj[u]>>v&1)for v in range(n)]for u in range(n)];el=em=0
            for u,v in combinations(range(n),2):
                common=sum(matrix[u][w]*matrix[w][v]for w in range(n))
                if matrix[u][v]:el+=(common-1)**2
                else:em+=(common-2)**2
            need((el,em)==expected,'independent scalar square/decomposition control','CONTROL')
    for label in['rook9_positive','prism9_whole','cube12_whole']:
        s=parse_state((base/label/'initial.state').read_bytes())
        if label!='rook9_positive':
            record=json.loads((base/label/'moves.jsonl').read_text().splitlines()[0]);result,_=replay(s,record);need(s['first']['step']==1 and s['lambda_energy']==0,'first completed proposal capture','CONTROL')
            for key in['selected_points_exclusive','new_pairs_absent_after_old_removal','first_lambda0_after','first_lambda0_step','lambda_weight','delta']:
                bad=copy.deepcopy(record);bad[key]=not bad[key]if type(bad[key])is bool else bad[key]+1
                controls.append(dict(mutated=key,label=label,diagnostic=U.reject(lambda:replay(parse_state((base/label/'initial.state').read_bytes()),bad),'REPLAY')))
        else:
            matrix=raw_matrix((base/label/'best.adj').read_bytes(),9);U.matrix_claim(matrix,9,4)
            controls.append(dict(scope=U.reject(lambda:U.matrix_claim(matrix,99,14),'MATRIX')))
            bad=copy.deepcopy(matrix);bad[0][1]=bad[1][0]=0;controls.append(dict(corrupted_rook=U.reject(lambda:U.matrix_claim(bad,9,4),'MATRIX')))
    cube=parse_state((base/'cube12_whole/first_lambda0.state').read_bytes());need(cube['lambda_energy']==0 and cube['mu_energy']==48,'partial lambda0 is not exact graph','CONTROL')
    controls.append(dict(partial_lambda0_rejected=U.reject(lambda:U.matrix_claim(raw_matrix((base/'cube12_whole/first_lambda0.adj').read_bytes(),12),12,4),'MATRIX')))
    need(score(PRISM,9,2)[2]['weighted_energy']==366 and score(CUBE,12,2)[2]['weighted_energy']==422,'fixed60 metrics','CONTROL')
    return controls
