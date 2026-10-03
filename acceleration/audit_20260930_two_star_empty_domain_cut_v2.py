"""Separate raw-scaffold, complete-pattern, and monotone cap-nogood checker."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_two_star_empty_domain_cut/run01'
OUT=ROOT/'acceleration/results/20260930_independent_review/two_star_empty_domain_cut_v2'
MODEL=ROOT/'acceleration/results/20260930_unrestricted_full99_cnf/model.json'
GATE=ROOT/'acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def rows(a):return [sum(x<<j for j,x in enumerate(row)) for row in a]
def cap(r,i,j):return ((r[i]>>j)&1)+(r[i]&r[j]).bit_count()
def enumerate_patterns(left,right,p,q):
    for e in (0,1):
        if 0<=p-e<=len(left) and 0<=q-e<=len(right):
            for a in combinations(left,p-e):
                for b in combinations(right,q-e):yield (e,a,b)
def verify(c,model):
    labels=sorted([(a,b) for a in range(14) for b in range(a+1,14) if a//2!=b//2],key=lambda x:(x[0]//2,x[1]//2,x[0]%2,x[1]%2))
    a=[[0]*99 for _ in range(99)];partial=[row.copy() for row in a]
    for i,j in combinations(range(99),2):
        if i==0:value=int(j<=14)
        elif j<=14:value=int((i-1)//2==(j-1)//2)
        elif i<=14:value=int(i-1 in labels[j-15])
        else:value=-1
        partial[i][j]=partial[j][i]=value;a[i][j]=a[j][i]=int(value==1)
    need(model['known_adjacency_full99']==partial,'independent complete unrestricted scaffold')
    edges=[dict(id=k,u=i,v=j) for k,(i,j) in enumerate(combinations(range(15,99),2),1)]
    need(model['edge_variables']==edges,'independent3486edge-variable ordering')
    positive=[tuple(pair) for pair in c['known_positive_outer_edges']]
    need(len(positive)==36 and positive==sorted(set(positive)),'exact36 distinct sortedpositiveedges')
    edge_ids={(e['u'],e['v']):e['id'] for e in edges}
    for i,j in positive:
        need((i,j) in edge_ids,'freeouteredge');a[i][j]=a[j][i]=1
    need(c['clause']==[-edge_ids[e] for e in positive],'complete negative-literal clause mapping')
    need(c['known_edge_adjacency']==a and all(type(x) is int for row in c['known_edge_adjacency'] for x in row),'all9801knownpositive entries')
    r=rows(a);need(all(cap(r,i,j)<=2 for i,j in combinations(range(99),2)),'baseknownpositive caps')
    u,v=c['center_vertices'];w=c['shared_neighbor'];z=c['outside_vertex']
    need((u,v,w,z)==(15,59,87,63),'precise frozen vertices')
    nu={i for i in range(99) if a[u][i]};nv={i for i in range(99) if a[v][i]}
    need(len(nu)==len(nv)==14 and v in nu and u in nv and nu&nv=={w},'two saturatedadjacentcenter stars')
    need(c['center_neighbors']==[sorted(nu),sorted(nv)] and z not in nu|nv|{u,v},'complete fixed neighborhoods, outside nonadjacent')
    left=sorted((nu-{v,w})&set(range(15,99)));right=sorted((nv-{u,w})&set(range(15,99)))
    need(len(left)==len(right)==10 and not set(left)&set(right),'two disjoint outerfibres')
    need(left==c['residual_left'] and right==c['residual_right'],'entire residual universes')
    need(not any(a[z][i] for i in [w,*left,*right]),'no prior outeradjacency of outsidevertex into fibres')
    p=2-len(nu&{i for i in range(15) if a[z][i]});q=2-len(nv&{i for i in range(15) if a[z][i]})
    need(c['deficits']==[p,q]==[2,1],'independently counted fixed innercontributions')
    # Every innervertex already has degree14 in the common scaffold; additional
    # adjacency from z to an innervertex is impossible, including fixedzeros.
    need(all(sum(a[i])==14 for i in range(15)),'all innerrows saturated')
    expected=list(enumerate_patterns(left,right,p,q));need(len(expected)==c['pattern_count']==460,'exact complete pattern count')
    raw=c['all_rejections'];need(len(raw)==len(expected),'no missing witnesses')
    pattern_checks=[]
    for pat,record in zip(expected,raw):
        e,lft,rgt=pat
        need(record['pattern']==[e,list(lft),list(rgt)],'complete canonicalpattern stream')
        rr=r.copy()
        for vertex in (([w] if e else [])+list(lft)+list(rgt)):
            rr[z]|=1<<vertex;rr[vertex]|=1<<z
        i,j=record['cap']['pair'];need(0<=i<j<99,'cap pair bounds')
        common=[k for k in range(99) if (rr[i]&rr[j])>>k&1]
        adjacent=(rr[i]>>j)&1;value=len(common)+adjacent
        need(record['cap']['common']==common and record['cap']['adjacent']==adjacent and record['cap']['sum']==value and value>2,'literal raw cap witness')
        pattern_checks.append(dict(pair=[i,j],value=value))
    return dict(positive_outer_edges=36,center_incident_outer_edges=sum(u in e or v in e for e in positive),additional_outer_edges=sum(u not in e and v not in e for e in positive),complete_patterns=460,pair_witnesses=pattern_checks,deficits=[p,q],center_neighbors=[sorted(nu),sorted(nv)])
def main():
    OUT.mkdir(parents=True,exist_ok=False);bindings={}
    def bind(p,expected=None):
        value=digest(p);need(expected is None or value==expected,'input hash');bindings[key(p)]=value;return Path(p)
    certificate=json.loads(bind(D/'certificate.json','1a0c77282656c61675974f29e31e63af075d48c440f57be622630d6fe64abaa4').read_bytes())
    model=json.loads(bind(MODEL,'77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e').read_bytes())
    gate=json.loads(bind(GATE,'2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58').read_bytes());need(gate['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS','independent original encoding gate')
    checked=verify(certificate,model)
    clause=bind(D/'nogood.clause').read_bytes();need(len(clause.splitlines())==1 and [int(x) for x in clause.split()]==certificate['clause']+[0],'raw clause tokens and terminator')
    rejected=[]
    for name in ('missing_pattern','wrong_deficit','wrong_cap','wrong_common','wrong_sign','missing_edge','wrong_center','wrong_outside','extra_fibre'):
        c=deepcopy(certificate)
        if name=='missing_pattern':c['all_rejections'].pop()
        elif name=='wrong_deficit':c['deficits'][0]=1
        elif name=='wrong_cap':c['all_rejections'][0]['cap']['sum']=2
        elif name=='wrong_common':c['all_rejections'][0]['cap']['common'].pop()
        elif name=='wrong_sign':c['clause'][0]*=-1
        elif name=='missing_edge':c['known_positive_outer_edges'].pop()
        elif name=='wrong_center':c['center_vertices'][0]=16
        elif name=='wrong_outside':c['outside_vertex']=64
        else:c['residual_left'].append(90)
        try:verify(c,model)
        except ValueError:rejected.append(name)
        else:raise ValueError('corrupted certificate accepted '+name)
    rook=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)]
    need(all(cap(rows(rook),i,j)==2 for i,j in combinations(range(9),2)),'known rook9 exactpositive cap control')
    k4=[[int(i!=j) for j in range(4)] for i in range(4)];need(cap(rows(k4),0,1)==3,'deliberately invalidK4 control')
    enumeration_controls=0
    for nl,nr in product(range(4),repeat=2):
        left=list(range(nl));right=list(range(nl,nl+nr))
        for p,q in product(range(4),repeat=2):
            brute=[]
            for bits in product((0,1),repeat=1+nl+nr):
                if bits[0]+sum(bits[1:1+nl])==p and bits[0]+sum(bits[1+nl:])==q:
                    brute.append((bits[0],tuple(i for i,x in zip(left,bits[1:1+nl]) if x),tuple(i for i,x in zip(right,bits[1+nl:]) if x)))
            need(set(brute)==set(enumerate_patterns(left,right,p,q)),'independent subset enumeration control');enumeration_controls+=1
    for p in (__file__,ROOT/'uv.lock',D/'manifest.json',D/'summary.json'):bind(p)
    need(all(digest(ROOT/p)==value for p,value in bindings.items()),'stable input bytes')
    report=dict(status='INDEPENDENT_TWO_STAR_EMPTY_DOMAIN_NOGOOD_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),verifier='/root independent raw matrix and finite-domain checker',claim_id='C-UNRESTRICTED-TWO-STAR-POSITIVE-EDGE-NOGOOD36',claim_revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',statement='No target in the unrestricted normalized root scaffold can contain all36 recorded positive outeredges. Equivalently the exact recorded negative36literal clause is entailed by the independently equivalent unrestricted baseCNF.',scope='Exactly one positive-edge configuration:23 edges saturate two centerstars and13 further edges. Not an exclusion of all completions or matchings of the original two stars, nor any full canonicalbranch.',dependencies=[dict(id='C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING',revision=1,relation='encoding_equivalence')],assumptions=['Symmetric binary zero-diagonal target with A^2=12I-A+2J in the independently established root labeling.','The36specified positive edges are retained; no target automorphism is assumed.'],inputs_sha256=bindings,checked=checked,derivation='The retained edges saturate both center rows at degree14, fixing their complete neighborhoods and making z nonadjacent to them. Their neighborhoods intersect only at w. All innerrows are already saturated by the fixed root scaffold. Thus exact common-neighbor counts force z to choose e adjacency to w and subsets of the two disjoint outerfibres of sizes2-e and1-e. These450+10patterns cover every target restriction to the center neighborhood union. Every pattern has a checked pair with adjacency pluscommoncount>2 already from retained/patternpositiveedges; adding other edges only increases this expression. Hence every target omits a retained edge, exactly the36negative-literal disjunction.',controls=dict(known_rook9_pass=True,invalid_K4_rejected=True,subset_enumeration_configurations=enumeration_controls,corrupted_certificates_rejected=rejected),shared_components=['Python standard library exact integers/bit counts, JSON, and combinatorial enumeration.','Raw candidate certificate and original model are shared data; no discovery code or prior domain helper imported.','Pinned full unrestricted encoding equivalence reused only to translate the graph necessity to its CNF variables.'],limitations=['No minimality of the clause asserted.','Original coupled node-capped search remains UNKNOWN; it is not converted to a two-star family exclusion.','No CNF solve, branch exclusion, unrestricted nonexistence, or external review.'],target_resolution=False,solver_calls=0,external_review=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],sha256=digest(OUT/'summary.json'),patterns=460,literals=36)))
if __name__=='__main__':main()
