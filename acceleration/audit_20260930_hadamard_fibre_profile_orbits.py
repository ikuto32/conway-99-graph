"""Independent complete fibre actions and P F Q completion covariance."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,combinations_with_replacement,permutations
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json';SCREEN=B+'hadamard_four_group_local_screen/';PROD=B+'hadamard_fibre_profile_orbits/'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
PROD+'summary.json':'b06060be84e0322323cae1373eff4fccb5d2e7ea38a53d5cf9c3cd204a282da0',
I+'hadamard_four_group_local_screen/summary.json':'ff30d47b012d1661182f1cba066425dd9d5aaccad3754cad4d526b7477725c67',
I+'four_group_ac_calibration/summary.json':'6e53216e9d00ec8990217f80b84c3ed8cc1766d5eaae85c1fc3aead081b4ec6e'}
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v,compact=False):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=None if compact else 2,separators=(',',':') if compact else None);f.write('\n')
def rowmap(tau):
    need(len(tau)==3 and sorted(tau)==[0,1,2],'three distinct fibre labels')
    return [12*tau[f]+a for f in range(3)for a in range(12)]
def invariant(M,p):return all(M[i][j]==M[p[i]][p[j]]for i in range(len(M))for j in range(len(M)))
def local_ok(words,tri):
    ws=[words[i]for i in tri]
    if any(sum(x==y for x,y in zip(a,b))>2 for a,b in combinations(ws,2)):return False
    for a,b in combinations(range(6),2):
        counts=Counter((w[a],w[b])for w in ws)
        if any(n>(1 if f==g else 2)for(f,g),n in counts.items()):return False
    return True
def matrix_gram(F):return [[sum(x*y for x,y in zip(a,b))for b in F]for a in F]
def profile_key(c):return tuple(c['groups']),tuple(tuple(v)for v in c['profile'])
def moved_profile(c,tau):
    inv=[tau.index(f)for f in range(3)]
    return tuple(c['groups']),tuple(tuple(v[inv[f]]for f in range(3))for v in c['profile'])
def fixedpoint(lengths,relations):
    live=[set(range(n))for n in lengths]
    while True:
        new=[{x for x in live[a]if all(relations[a,b][x]&live[b]for b in range(4)if b!=a)}for a in range(4)]
        if new==live:return new
        live=new
def saved_live(c,kind):
    result=[]
    for n,mask in zip(c['domain_sizes'],c[kind]['final_masks']):
        bits=int(mask,16);need(0<=bits<1<<n,'saved fixedpoint mask bounds');result.append({i for i in range(n)if bits>>i&1})
    need([len(x)for x in result]==c[kind]['final_domain_sizes'] and any(not x for x in result)==c[kind]['empty'],'saved fixedpoint metadata')
    return result
def cols_feature(support,tri,words,K):
    cols=[frozenset(12*words[w][a]+coord for a,coord in enumerate(support))for w in tri]
    count=Counter(pair for col in cols for pair in combinations_with_replacement(sorted(col),2))
    need(all(v<=K[i][j]for(i,j),v in count.items()),'individual exact Gram caps')
    return cols,count
def predicates(left,right,K):
    lc,ln=left;rc,rn=right
    gok=all(v+rn.get((a,b),0)<=K[a][b]for(a,b),v in ln.items())
    return gok,gok and all(len(a&b)<=2 for a in lc for b in rc)
def compare_tables(c,features,K):
    relations=[{},{}];total=0
    for r in c['pairs']:
        a,b=r['sides'];l=c['local_survivor_indices'][a];rr=c['local_survivor_indices'][b]
        for rel in relations:rel[a,b]=[set()for _ in l];rel[b,a]=[set()for _ in rr]
        counts=[0,0]
        for i,li in enumerate(l):
            actual=[set(),set()]
            for j,rj in enumerate(rr):
                ok=predicates(features[c['groups'][a],li],features[c['groups'][b],rj],K);total+=1
                for k in range(2):
                    if ok[k]:actual[k].add(j);relations[k][a,b][i].add(j);relations[k][b,a][j].add(i);counts[k]+=1
            for k,field in enumerate(['gram_forward_masks','both_forward_masks']):
                bits=int(r[field][i],16);need(0<=bits<1<<len(rr),'relation mask bounds')
                need(actual[k]=={j for j in range(len(rr))if bits>>j&1},'complete raw pair predicate table')
        need(r['population']==len(l)*len(rr) and counts==[r['gram_compatible'],r['gram_and_caps_compatible']],'pair table counts')
    return relations,total
def covariance_control(C,L,supports,groupcols,words,triples,taus):
    F=[[0]*60 for _ in range(36)]
    for g,ds in enumerate(groupcols):
        tri=triples[(137*g)%len(triples)]
        for d,w in zip(ds,tri):
            for a,c in enumerate(supports[g]):F[12*words[w][a]+c][d]=1
    D=[[int((j-i)%60 in[1,59])for j in range(60)]for i in range(60)]
    def mixed(F,D):return [[sum(F[i][q]*D[q][d]for q in range(60))-(2-F[i][d]-sum(C[i][q]*F[q][d]for q in range(36)))for d in range(60)]for i in range(36)]
    def residual(F,D):return [[sum(D[a][q]*D[q][b]for q in range(60))+sum(F[q][a]*F[q][b]for q in range(36))-(12*int(a==b)-D[a][b]+2)for b in range(60)]for a in range(60)]
    H=mixed(F,D);R=residual(F,D);G=matrix_gram(F);records=[]
    for tau in taus:
        p=rowmap(tau);q=list(range(60))
        for ds in groupcols:
            ordered=sorted(ds,key=lambda d:tuple(tau[next(f for f in range(3)if F[12*f+a][d])]for a in range(12)if L[a][d]))
            for new,old in zip(ds,ordered):q[new]=old
        need(sorted(q)==list(range(60)),'column permutation')
        moved=[[0]*60 for _ in range(36)]
        for old,new in enumerate(p):moved[new]=[F[old][d]for d in q]
        nextD=[[D[a][b]for b in q]for a in q];nextG=matrix_gram(moved);nextH=mixed(moved,nextD);nextR=residual(moved,nextD)
        need(all(nextG[p[a]][p[b]]==G[a][b]for a in range(36)for b in range(36)),'literal Gram covariance')
        need(all(nextH[p[a]][d]==H[a][q[d]]for a in range(36)for d in range(60)),'literal mixed residual covariance')
        need(nextR==[[R[a][b]for b in q]for a in q],'literal residual quadratic covariance')
        records.append(dict(tau=tau,row_map=p,column_new_to_old=q))
    return dict(factor=F,residual_cycle=D,actions=records,scope='Synthetic binary local triples and cycle; neither full Gram nor target feasibility is claimed.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.monotonic();corrupt=[]
    def pin(p,h=None):v=sha(ROOT/p);need(h is None or v==h,'artifact hash '+p);pins[p]=v
    def load(p,h=None):pin(p,h);return json.loads((ROOT/p).read_bytes())
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):corrupt.append(name)
        else:raise ValueError('corruption accepted '+name)
    try:
        for p,h in PINS.items():pin(p,h)
        raw=load(RAW);local=load(LOCAL);producer=load(PROD+'summary.json');maps=load(PROD+'maps.json',producer['outputs_sha256'][PROD+'maps.json'])
        for p,h in producer['inputs_sha256'].items():pin(p,h)
        screen_gate=load(I+'hadamard_four_group_local_screen/summary.json');cal=load(I+'four_group_ac_calibration/summary.json')
        need(screen_gate['status']=='INDEPENDENT_HADAMARD_FOUR_GROUP_LOCAL_PROFILE_SCREEN_PASS' and cal['status'].endswith('_PASS'),'separate screen and controls gates')
        binding=load(I+'hadamard_four_group_local_screen/claim_binding.json','c5a99253b394214fcf834374d1f572851100d89150f7049f75b4e45220a48449')
        need(binding['id']=='C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN' and binding['revision']==1,'scoped screen premise')
        C=raw['core_adjacency'];K=raw['prescribed_Gram36'];L=raw['L'];supports=[];groupcols=[]
        for d in range(60):
            s=tuple(a for a in range(12)if L[a][d])
            if s not in supports:supports.append(s);groupcols.append([])
            groupcols[supports.index(s)].append(d)
        need(len(supports)==20 and all(len(ds)==3 for ds in groupcols),'literal triplicate supports')
        expectedC=[[int((i//12==j//12 and (i%12)^1==j%12) or (i//12!=j//12 and i%12==j%12))for j in range(36)]for i in range(36)]
        need(C==expectedC,'six-prism raw core')
        need(K==[[12*int(i==j)+2-int(i//12==j//12)-C[i][j]-sum(C[i][q]*C[q][j]for q in range(36))for j in range(36)]for i in range(36)],'literal prescribed Gram')
        wordset=set()
        for zero in combinations(range(6),2):
            for one in combinations([i for i in range(6)if i not in zero],2):wordset.add(tuple(0 if i in zero else 1 if i in one else 2 for i in range(6)))
        words=sorted(wordset);need([list(w)for w in words]==local['words'] and len(words)==90,'complete balanced word population')
        triples=[tri for tri in combinations(range(90),3)if local_ok(words,tri)]
        need([list(t)for t in triples]==local['survivors'] and len(triples)==31110,'complete local catalogue from117480 raw triples')
        wi={w:i for i,w in enumerate(words)};ti={t:i for i,t in enumerate(triples)};taus=list(permutations(range(3)));tmaps=[];orders=[]
        for j,tau in enumerate(taus):
            p=rowmap(tau);need(invariant(C,p)and invariant(K,p),'all six fixed-core/Gram actions')
            wm=[wi[tuple(tau[f]for f in w)]for w in words]
            tm=[];sorts=[]
            for t in triples:
                moved=[wm[w]for w in t];sorts.append(sorted(range(3),key=lambda a:moved[a]));tm.append(ti[tuple(sorted(moved))])
            need(sorted(wm)==list(range(90)) and sorted(tm)==list(range(31110)),'complete word/triple bijections')
            need(maps['fibre_actions'][j]==dict(tau=list(tau),rows=p,word_map=wm) and maps['local_triple_maps'][j]==tm,'all saved raw action maps')
            tmaps.append(tm);orders.append(sorts)
        need(tmaps[0]==list(range(31110)),'identity positive control')
        for j,tau in enumerate(taus):
            inv=taus.index(tuple(tau.index(i)for i in range(3)));need(all(tmaps[inv][tmaps[j][i]]==i for i in range(31110)),'all inverse triple maps')
        screen=load(SCREEN+'summary.json');cases=[load(SCREEN+f'case_{i:03d}.json',screen['outputs_sha256'][SCREEN+f'case_{i:03d}.json'])for i in range(108)]
        lookup={profile_key(c):c['case']for c in cases};need(len(lookup)==108,'unique frozen labelled profiles')
        features={};tables=[];live=[];total=0
        for c in tqdm(cases,desc='Independent profile relations',mininterval=1):
            for g,domain in zip(c['groups'],c['local_survivor_indices']):
                for t in domain:
                    if(g,t)not in features:features[g,t]=cols_feature(supports[g],triples[t],words,K)
            rel,count=compare_tables(c,features,K);total+=count;tables.append(rel);fixed=[]
            for j,kind in enumerate(['gram_ac','gram_caps_ac']):
                fp=fixedpoint(c['domain_sizes'],rel[j]);need(fp==saved_live(c,kind),'independent simultaneous AC fixedpoint');fixed.append(fp)
            live.append(fixed)
        orbit_sets={};records=[];entries=0
        for c,rec in zip(cases,maps['case_maps']):
            actions=[lookup[moved_profile(c,tau)]for tau in taus];need(len(set(actions))==6,'free action on labelled profiles');rep=min(actions);j=actions.index(rep);target=cases[rep]
            need(rec['case']==c['case'] and rec['representative']==rep and rec['orbit_actions']==actions and rec['tau']==list(taus[j]),'saved case-to-representative mapping')
            positions=[]
            for side,(domain,tdomain)in enumerate(zip(c['local_survivor_indices'],target['local_survivor_indices'])):
                reverse={t:i for i,t in enumerate(tdomain)};pos=[reverse[tmaps[j][t]]for t in domain]
                need(sorted(pos)==list(range(len(tdomain))) and pos==rec['local_position_maps'][side],'local domain transport bijection');positions.append(pos)
                for k in range(2):need({pos[x]for x in live[c['case']][k][side]}==live[rep][k][side],'AC transport in both models')
            for k in range(2):
                for(a,b),rel in tables[c['case']][k].items():
                    for x,ys in enumerate(rel):
                        need({positions[b][y]for y in ys}==tables[rep][k][a,b][positions[a][x]],'complete pair predicate covariance');entries+=len(c['local_survivor_indices'][b])
            empty=any(not x for x in live[c['case']][1]);need(empty==rec['screen_empty'],'saved screen outcome')
            orbit_sets.setdefault(rep,set()).add(c['case']);records.append(dict(case=c['case'],representative=rep,tau=list(taus[j]),empty=empty))
        orbits=[dict(representative=r,members=sorted(m),screen_empty=any(not x for x in live[r][1]))for r,m in sorted(orbit_sets.items())]
        need(orbits==maps['orbits'] and len(orbits)==18 and all(len(r['members'])==6 for r in orbits),'complete exact finite orbit partition')
        need(sum(o['screen_empty']for o in orbits)==2 and sum(not o['screen_empty']for o in orbits)==16,'two excluded/sixteen unresolved representative orbits')
        control=covariance_control(C,L,supports,groupcols,words,triples,taus)
        reject('repeated_fibre',lambda:rowmap([0,0,2]));reject('outside_fibre',lambda:rowmap([0,1,3]))
        bad=deepcopy(C);bad[0][1]^=1;reject('perturbed_core',lambda:need(invariant(bad,rowmap((1,0,2))),'core invariance'))
        wrong=tmaps[1][:];wrong[0]=wrong[1];reject('nonbijective_triple_map',lambda:need(sorted(wrong)==list(range(31110)),'map bijection'))
        reject('wrong_representative',lambda:need(records[1]['representative']==107,'minimum orbit representative'))
        bad=deepcopy(cases[0]);bad['pairs'][0]['gram_forward_masks'][0]=hex(int(bad['pairs'][0]['gram_forward_masks'][0],16)^1)
        reject('one_flipped_pair_bit',lambda:compare_tables(bad,features,K))
        bad=deepcopy(cases[0]);bad['gram_caps_ac']['final_masks'][0]=hex(int(bad['gram_caps_ac']['final_masks'][0],16)^1)
        reject('changed_final_domain',lambda:need(saved_live(bad,'gram_caps_ac')==live[0][1],'exact fixedpoint'))
        toy={(a,b):[{0,1},{0,1}]for a in range(4)for b in range(4)if a!=b};need(fixedpoint([2]*4,toy)==[{0,1}]*4,'positive complete relation')
        toy[0,1]=[set(),set()];need(fixedpoint([2]*4,toy)==[set()]*4,'empty relation propagation')
        reject('missed_AC_deletion',lambda:need(fixedpoint([2]*4,toy)==[{0,1}]*4,'AC soundness'))
        requireD=control['residual_cycle'];q=control['actions'][-1]['column_new_to_old'];nextD=[[requireD[a][b]for b in q]for a in q]
        reject('unchanged_D_after_column_relabel',lambda:need(nextD==requireD,'must conjugate residual'))
        for p in ['acceleration/audit_20260930_hadamard_fibre_profile_orbits.py','docs/AUDIT_20260930_HADAMARD_FIBRE_PROFILE_ORBITS.md','uv.lock','pyproject.toml']:pin(p)
        save(out/'independent_orbits.json',dict(orbits=orbits,cases=records));save(out/'local_column_orders.json',dict(taus=taus,column_new_to_old=orders),compact=True)
        save(out/'covariance_control.json',control);save(out/'controls.json',dict(corruptions_rejected=corrupt,complete_triples=117480,survivors=31110,inverse_map_checks=6*31110,synthetic_completion_covariance_actions=6))
        now=datetime.now(timezone.utc).isoformat();claim=dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-GLOBAL-FIBRE-NORMALIZATION',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            statement='Global permutations of the three fibre labels, followed by permutations within identical-support column triples, preserve the fixed six-prism prescribed-Gram factor problem, outside-column caps and any residual target completion. The exact108 labelled four-exception profiles form18orbits of size6; the96 nonempty pair-screen outcomes are covered by16representatives, while the12excluded profiles form2orbits.',
            scope='Normalization only of the exactly-four-exception Gram-plus-outside-column-cap family on this literal fixed support. No nonempty screen outcome is asserted feasible.',
            assumptions=['The fixed raw six-prism core and support.','Exactly four unbalanced groups and the separately checked108-profile coverage for Gram plus column caps.','The residual graph, if present, is relabelled rather than assumed invariant.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='uses_result')],
            verifier='/root/eight_domain_audit',producer='/root',method='Independent raw core/Gram and full local catalogue, sparse integer pair predicates, simultaneous set AC, all six action bijections and exact matrix covariance derivation.',
            inputs_sha256=pins,created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY',external_review=False,
            limitations=['No unrestricted target coverage or new exclusion.','No target automorphism or residual symmetry assumed.','No claim that18counts all orbits under any larger group.','Synthetic covariance control is not a research factor.'])
        save(out/'claim_binding.json',claim)
        summary=dict(status='INDEPENDENT_HADAMARD_GLOBAL_FIBRE_PROFILE_NORMALIZATION_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()if p.is_file()},words=90,local_triples=31110,actions=6,profiles=108,orbits=18,excluded_profiles=12,excluded_orbits=2,unresolved_profiles=96,unresolved_orbits=16,
            independently_recomputed_option_pairs=total,directed_pair_covariance_entries=entries,corruptions=len(corrupt),shared_components=['Pinned raw artifacts and independent screen/calibration gates; no producer or previous checker imports.','Python standard arithmetic and tqdm progress only.'],
            target_resolution=False,solver_calls=0,elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],sha256=sha(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(__file__)));raise
if __name__=='__main__':main()
