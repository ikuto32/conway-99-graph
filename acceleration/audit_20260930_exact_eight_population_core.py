"""Prepared parameterized independent mathematics; no CLI, no gate, no producer imports.

The eventual campaign wrapper must authenticate the complete population and all
raw inputs before using these functions. This module never approves a campaign.
"""
import hashlib,json
from collections import defaultdict
from copy import deepcopy
from itertools import combinations,product
from pathlib import Path
import audit_20260930_eight_count_profile_lift_third as base
prior=base.prior;shared=base.shared;codec=base.codec;need=codec.need;same=codec.same
HELPER_PINS={Path(base.__file__):'076a6ae8a731bede8075334b8c40e9df480aaed52cc8214aa68bb70ccbda78a1',Path(prior.__file__):base.PINS[Path(prior.__file__)],Path(shared.__file__):base.PINS[Path(shared.__file__)],Path(codec.__file__):base.PINS[Path(codec.__file__)]}
def counts_vector(counts):
    need(len(counts)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in counts),'strict complete count table')
    return bytes(x for row in counts for v in row for x in v)

def derive(raw,p,catalogue=None):
    words,triples,balanced=prior.catalogue() if catalogue is None else catalogue;index=defaultdict(list)
    for i,t in enumerate(triples):index[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
    L=raw['L'];C=raw['core_adjacency'];K=shared.gram_from_core(C,12)
    need(C==[[int((i%12==j%12 and i//12!=j//12)or(i//12==j//12 and i%12^1==j%12))for j in range(36)]for i in range(36)]and K==raw['prescribed_Gram36'],'literal core/Gram')
    supports=[[a for a in range(12)if L[a][d]]for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    columns=[[d for d,s in enumerate(supports)if s==g]for g in groups];pairs=[list(x)for x in combinations(range(12),2)if x[0]^1!=x[1]]
    need(len(groups)==20 and all(len(s)==6 and len(ds)==3 and all(sum(a in s for a in(m,m+1))==1 for m in range(0,12,2))for s,ds in zip(groups,columns)),'literal support triples')
    counts=p['coordinate_group_fibre_counts'];exceptional=[g for g,s in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in s)]
    need(exceptional==p['exceptional_groups']and len(exceptional)==p['exception_count']==8,'exact arbitrary count-table exception list')
    need(len(counts)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in counts),'integer count-table shape')
    need(all(counts[a][g]==[0,0,0]for g,s in enumerate(groups)for a in range(12)if a not in s),'off-support counts vanish')
    deviations=[[[counts[a][g][f]-int(a in groups[g])for g in exceptional]for f in range(3)]for a in range(12)]
    need(deviations==p['coordinate_fibre_deviations'],'raw deviations from literal counts')
    digest=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=deviations),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(digest==p['profile_sha256'] and hashlib.sha256(counts_vector(counts)).hexdigest()==p['full_count_profile_sha256'],'literal profile digest')
    domains=[];ranks=[];nextid=1
    for g,s in enumerate(groups):
        wanted=[counts[a][g]for a in s];signature=tuple(sum(wanted,[]));ids=index.get(signature,[])
        need(ids and ids==p['local_survivor_indices_by_group'][g],'complete raw count class')
        if g in exceptional:
            need(len(ids)>0,'complete nonempty exceptional class');options=[dict(choice_index=j,local_survivor_index=i,word_indices=triples[i],colour_words=[words[w]for w in triples[i]])for j,i in enumerate(ids)];kind='exceptional_sorted_local_triple'
        else:
            need(signature==(1,)*18 and len(ids)==150,'all150 balanced choices');options=deepcopy(balanced);kind='balanced_normalized_triple'
        for option in options:
            option['selector']=nextid;nextid+=1;option['lifted_rows']=[[12*f+a for a,f in zip(s,w)]for w in option['colour_words']]
            need([[sum(w[a]==f for w in option['colour_words'])for f in range(3)]for a in range(6)]==wanted,'literal option counts')
            need(all(len(set(u)&set(v))<=2 for u,v in combinations(option['lifted_rows'],2)),'literal within-triplicate cap')
            need(all(K[a][b]>0 for rows in option['lifted_rows']for a,b in combinations(rows,2)),'every prescribed zero entry absent')
        domains.append(dict(group=g,support=s,columns=columns[g],kind=kind,fixed_counts=wanted,choices=options));ranks.append(dict(group=g,count_signature=list(signature),local_survivor_indices=ids,count=len(ids)))
    margins=[dict(coordinate=a,fibre=f,total=sum(counts[a][g][f]for g in range(20)))for a in range(12)for f in range(3)]
    S=nextid-1;need(all(x['total']==10 for x in margins),'all36 exact margins')
    need(all(K[12*f+a][12*z+b]==0 for a in range(12)for b in range(12)for f,z in product(range(3),repeat=2)if (a==b and f!=z)or a^1==b),'all90 omitted offdiagonal Gram entries zero')
    facts=dict(core_adjacency36=C,prescribed_Gram36=K,L12x60=L,groups=groups,group_columns=columns,coordinate_pairs=pairs,exceptional_groups=exceptional,balanced_groups=[g for g in range(20)if g not in exceptional],coordinate_group_fibre_counts=counts,coordinate_fibre_deviations=deviations,derived_row_margins=margins,selected_profile_sha256=digest,selected_full_count_sha256=p['full_count_profile_sha256'])
    clauses=[];prefixes=[];cells=[];nextvar=nextid
    def append(cs):
        meta=dict(first_clause=len(clauses)+1,clause_count=len(cs));clauses.extend(cs);return meta
    for dom in domains:
        xs=[o['selector']for o in dom['choices']];ps=list(range(nextvar,nextvar+len(xs)-1));nextvar+=len(ps);prefixes.append(dict(group=dom['group'],selectors=xs,prefixes=ps,**append(shared.onehot_clauses(xs,ps))))
    for a,b in pairs:
        incident=[dom for dom in domains if a in dom['support']and b in dom['support']];need(len(incident)==5,'five literal incident supports')
        for f,z in product(range(3),repeat=2):
            contributions=[]
            for dom in incident:
                coeff=[sum(12*f+a in rows and 12*z+b in rows for rows in o['lifted_rows'])for o in dom['choices']];need(set(coeff)<={0,1,2},'integer coefficient range');channels=[]
                for threshold in(1,2):
                    xs=[o['selector']for o,n in zip(dom['choices'],coeff)if n>=threshold];v=nextvar;nextvar+=1;channels.append(dict(threshold=threshold,variable=v,selectors=xs,**append(shared.or_clauses(v,xs))))
                contributions.append(dict(group=dom['group'],coefficients=coeff,channels=channels))
            xs=[c['variable']for g in contributions for c in g['channels']];bound=K[12*f+a][12*z+b];need(bound==(1 if f==z else 2),'actual Gram target')
            cells.append(dict(coordinates=[a,b],fibres=[f,z],bound=bound,group_contributions=contributions,count_inputs=xs,**append(shared.count_clauses(xs,bound))))
    onehot=sum(r['clause_count']for r in prefixes);card=sum(r['clause_count']for r in cells)
    need(nextvar==2*S+5381 and len(clauses)==49*S+60400,'domain-derived complete formula dimensions')
    model=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_WEIGHTED_CNF_V1',variables=nextvar-1,clauses=len(clauses),primary_selectors=S,domains=domains,exact_one_prefix_rows=prefixes,pair_cell_counts=cells,variable_populations=dict(selectors=S,onehot_prefixes=S-20,weighted_threshold_channels=5400),clause_populations=dict(onehot=onehot,channels=len(clauses)-onehot-card,counts=card))
    return facts,model,clauses,dict(records=ranks,all_initial=True,AC_pruning_used=False)

def verify_scope(facts,scope):
    for name,value in facts.items():need(same(scope[name],value),'raw mathematical scope '+name)
    need(scope['within_group_column_caps_encoded'] is True,'local caps required')
    for name in ['cross_group_column_caps_encoded','residual_D_encoded','target_graph','balance_WLOG','orbit_coverage_used','arc_pruning_used']:
        need(scope[name] is False,'literal scope must not expand '+name)
    need(scope['profile_is_additional_assumption'] is True and scope['assumed_target_automorphism'] is None,'literal restricted profile')
    # Provenance/universe/profile-index fields require separate exact outer review.

def verify_formula(raw,profile,scope,actual_model,scope_sha256,raw_cnf_bytes,catalogue=None):
    facts,model,clauses,initial=derive(raw,profile,catalogue)
    verify_scope(facts,scope);model['scope_sha256']=scope_sha256
    need(same(model,actual_model),'every independent model field')
    need(codec.cnf_bytes(clauses,model['variables'])==raw_cnf_bytes,'all exact ordered CNF bytes')
    return dict(facts=facts,model=model,clauses=clauses,initial_domains=initial)

def decode_and_verify(values,model,scope,profile,clauses):
    need(set(values)==set(range(1,model['variables']+1)) and all(type(x)is bool for x in values.values()),'complete Boolean assignment')
    codec.all_clauses(clauses,values);F=[[0]*60 for _ in range(36)];selected=[]
    for dom in model['domains']:
        options=[o for o in dom['choices']if values[o['selector']]];need(len(options)==1,'unique complete local option');o=options[0];selected.append(dict(group=dom['group'],selector=o['selector'],choice_index=o['choice_index']))
        for d,rows in zip(dom['columns'],o['lifted_rows']):
            for r in rows:F[r][d]=1
        need(all(sum(F[r][d]*F[r][e]for r in range(36))<=2 for d,e in combinations(dom['columns'],2)),'mandatory within-triplicate caps')
    actual_counts=[[[sum(F[12*f+a][d]for d in columns)for f in range(3)]for columns in scope['group_columns']]for a in range(12)]
    need(actual_counts==profile['coordinate_group_fibre_counts'],'all720 actual count entries')
    checks=shared.raw_factor(F,scope['core_adjacency36'],12,scope['L12x60']);order,canonical=shared.canonical(F,12)
    return dict(factor=F,selected_choices=selected,coordinate_group_fibre_counts=actual_counts,checks=checks,canonical_column_order=order,canonical_factor=canonical,full_count_profile_sha256=hashlib.sha256(counts_vector(actual_counts)).hexdigest(),cross_group_column_caps_diagnostic_only=True,residual_D=None,target_graph=False)
