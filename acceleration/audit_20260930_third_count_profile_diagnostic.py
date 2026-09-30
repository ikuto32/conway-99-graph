"""Separate exact Cartesian review of third-profile scalar/Gram-block diagnostics."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
import audit_20260930_second_count_scalar_obstruction as helper

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
D=B+'third_count_profile_gram_diagnostic/';PROFILE=I+'count_master_partial_cut_sat_outcome/independent_count_profile.json'
RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
PLAN='docs/AUDIT_20260930_THIRD_COUNT_DIAGNOSTIC_PLAN.md'
FIXTURE=B+'srg243_residual_fixture/triangle_blocks.json'
PINS={PROFILE:'03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e',I+'count_master_partial_cut_sat_outcome/summary.json':'736ccbcda81ee34c21ede2a80253d5b224fabb96a2e83d0a2c1c76dba435d071',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439','acceleration/audit_20260930_second_count_scalar_obstruction.py':'6918af881f589f16080796b4d583c472c763d0bfb0341083a4cf7a7982b5db13'}
need=helper.need;sha=helper.sha;write=helper.write


def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p):
    raw=(ROOT/p).read_bytes();return json.loads(gzip.decompress(raw)if p.endswith('.gz')else raw)


def check_pair(q,pi,a,b,groups,ranks,words,triples,G):
    need(q['coordinates']==[a,b]and q['pair_index']==pi,'complete pair identity')
    gs=[g for g,s in enumerate(groups)if a in s and b in s];need(len(gs)==5,'five raw incident groups')
    matrices=[];rankmaps=[]
    for g,gr in zip(gs,q['group_records'],strict=True):
        ia,ib=groups[g].index(a),groups[g].index(b)
        mapping={rank:tuple(sum(words[w][ia]==f and words[w][ib]==h for w in triples[rank])for f,h in product(range(3),repeat=2))for rank in ranks[g]}
        classes=defaultdict(list)
        for rank,m in mapping.items():classes[m].append(rank)
        values=sorted(classes)
        need(gr['group']==g and gr['local_positions']==[ia,ib]and gr['full_local_indices']==ranks[g],'complete unpruned contributing class')
        need(gr['matrices']==[list(m)for m in values]and gr['realizing_local_indices']==[classes[m]for m in values],'all literal local matrices and rank fibres')
        matrices.append(values);rankmaps.append(mapping)
    target=tuple(G[12*f+a][12*h+b]for f,h in product(range(3),repeat=2));need(q['target']==list(target),'raw-core target block')
    need(len(q['scalar_intervals'])==9,'nine scalar cells')
    for cell,row in enumerate(q['scalar_intervals']):
        need(row['coordinates']==[a,b]and row['fibres']==list(divmod(cell,3)),'scalar ordering')
        helper.scalar_check(row,gs,[{rank:m[cell]for rank,m in rs.items()}for rs in rankmaps],target[cell])
    layers=q['DP_layers'];need(len(layers)==6,'all exact prefix layers');prefixproducts=0;lastproduct=0
    for depth in range(6):
        # Complete independent Cartesian enumeration, with no producer DP reuse.
        actual,number=helper.cartesian(matrices[:depth],target);prefixproducts+=number
        need(layers[depth]['states']==[list(s)for s in sorted(actual)],'complete Cartesian prefix state set')
        if depth==0:
            need(layers[0]['predecessors']==[None]and layers[0]['option_indices']==[None]and layers[0]['attempted_transitions']==layers[0]['oversized_transitions']==0,'initial state metadata')
        else:
            expected_attempts=len(layers[depth-1]['states'])*len(matrices[depth-1])
            oversized=sum(any(x+y>bound for x,y,bound in zip(s,m,target))for s in layers[depth-1]['states']for m in matrices[depth-1])
            need(layers[depth]['attempted_transitions']==expected_attempts and layers[depth]['oversized_transitions']==oversized,'exact transition bookkeeping')
            for state,previous,index in zip(layers[depth]['states'],layers[depth]['predecessors'],layers[depth]['option_indices'],strict=True):
                need(type(previous)is int and 0<=previous<len(layers[depth-1]['states'])and type(index)is int and 0<=index<len(matrices[depth-1]),'bounded predecessor indices')
                need(state==[x+y for x,y in zip(layers[depth-1]['states'][previous],matrices[depth-1][index])],'literal predecessor realization')
        if depth==5:lastproduct=number;feasible=target in actual
    need(q['feasible']==feasible,'complete literal block verdict')
    if feasible:
        need(len(q['witness'])==5,'five chosen raw local options');summed=[0]*9
        for g,w,rs,values in zip(gs,q['witness'],rankmaps,matrices,strict=True):
            need(w['group']==g and tuple(w['matrix'])==rs[w['local_survivor_index']]==values[w['matrix_index']],'actual complete witness choice')
            summed=[x+y for x,y in zip(summed,w['matrix'])]
        need(summed==list(target),'raw witness sums to prescribed block')
    else:need(q['witness']is None,'no false witness for failed block')
    return dict(pair_index=pi,coordinates=[a,b],feasible=feasible,support_sizes=list(map(len,matrices)),
        complete_block_products=lastproduct,complete_prefix_products=prefixproducts,
        scalar_failures=sum(not r['passes']for r in q['scalar_intervals']))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--producer-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        digest=sha(ROOT/p);need(h is None or digest==h,'frozen artifact '+p);pins[p]=digest
    try:
        for p,h in PINS.items():pin(p,h)
        pin(D+'summary.json',args.producer_summary_sha256);producer=load(D+'summary.json')
        need(producer['status']=='CANDIDATE_THIRD_COUNT_PROFILE_EXACT_DIAGNOSTIC_COMPLETE'and producer['pairs_completed']==60,'completed producer population')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(p,h)
        for p in [key(__file__),PLAN,'uv.lock','pyproject.toml']:pin(p)
        controls=helper.controls(load(FIXTURE));words,triples=helper.catalogue();local=load(LOCAL)
        need([list(w)for w in words]==local['words']and [list(t)for t in triples]==local['survivors'],'complete separate117480-triple reconstruction')
        raw=load(RAW);profile=load(PROFILE);need(profile['profile_sha256']==producer['profile_sha256']=='3bc6ebf9444e7a2f15af1ac85c6164119333244ced5d6dbe83a6c6b367e533d5','exact third literal profile')
        groups=[]
        for d in range(60):
            s=[a for a in range(12)if raw['L'][a][d]]
            if s not in groups:groups.append(s)
        counts=profile['coordinate_group_fibre_counts'];classes=defaultdict(list)
        for rank,t in enumerate(triples):classes[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(rank)
        ranks=[classes[tuple(v for a in s for v in counts[a][g])]for g,s in enumerate(groups)]
        initial=load(D+'initial_domain_ranks.json');need(ranks==profile['local_survivor_indices_by_group']==initial['local_survivor_indices_by_group']and groups==initial['groups'],'every exact initial domain')
        need(len(groups)==20 and all(ranks),'all20 domains nonempty')
        C=raw['core_adjacency'];G=[[12*(i==j)-C[i][j]+2-int(i//12==j//12)-sum(C[i][k]*C[k][j]for k in range(36))for j in range(36)]for i in range(36)]
        need(G==raw['prescribed_Gram36'],'literal core target')
        reports=[];intervals=[];pairs=[q for q in combinations(range(12),2)if q[0]//2!=q[1]//2]
        for pi,(a,b)in enumerate(pairs):
            q=load(D+f'pair_{pi:02d}.json.gz');reports.append(check_pair(q,pi,a,b,groups,ranks,words,triples,G));intervals.extend(q['scalar_intervals'])
            need(time.perf_counter()-start<120,'120-second audit allocation')
        saved=load(D+'all540_intervals.json');failed=[r for r in intervals if not r['passes']]
        need(len(intervals)==540 and intervals==saved['records']and failed==saved['violations'],'all exact scalar records')
        need(producer['failed_scalar_cells']==len(failed)and producer['infeasible_pairs']==sum(not r['feasible']for r in reports),'actual producer finite outcome counts')
        fresh=[]
        original=load(D+'pair_00.json.gz')
        for label in ['domain_omission','matrix_entry','state_omission','transition_count','false_verdict','raw_witness']:
            q=deepcopy(original)
            if label=='domain_omission':q['group_records'][0]['full_local_indices'].pop()
            elif label=='matrix_entry':q['group_records'][0]['matrices'][0][0]+=1
            elif label=='state_omission':q['DP_layers'][1]['states'].pop()
            elif label=='transition_count':q['DP_layers'][1]['attempted_transitions']+=1
            elif label=='false_verdict':q['feasible']=not q['feasible']
            elif q['witness']:q['witness'][0]['matrix'][0]+=1
            else:q['witness']=[]
            try:check_pair(q,0,*pairs[0],groups,ranks,words,triples,G)
            except(ValueError,KeyError,TypeError,IndexError):fresh.append(label)
            else:raise ValueError('corrupt artifact accepted '+label)
        controls['fresh_artifact_corruptions']=fresh;write(out/'controls.json',controls)
        write(out/'independent_block_records.json',dict(records=reports,complete_Cartesian_products=sum(r['complete_block_products']for r in reports),complete_prefix_products=sum(r['complete_prefix_products']for r in reports)))
        write(out/'independent_initial_domains.json',dict(groups=groups,local_survivor_indices_by_group=ranks))
        write(out/'independent_scalar_records.json',dict(records=intervals,violations=failed))
        shared=['Frozen separately authored second-profile checker literal catalogue/Cartesian-product/positive-control functions are reused and hash-pinned. No producer code or merged-state DP is imported.', 'The count-CSP witness and complete catalogue are exact pinned premises; all profile-specific ranks, contributions, intervals, state sets and witnesses are rechecked.']
        statement=f'The exact third count profile has {len(failed)} failed scalar cells among540 and {sum(not r["feasible"]for r in reports)} failed separate Gram blocks among60 in its complete within-triplicate-cap local domains. These are independent necessary projections, not simultaneous factor choices.'
        summary=dict(status='INDEPENDENT_THIRD_COUNT_PROFILE_GRAM_DIAGNOSTIC_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,
            outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},profile_sha256=profile['profile_sha256'],
            local_triples_examined=117480,local_survivors=31110,initial_domain_sizes=list(map(len,ranks)),
            scalar_cells=540,failed_scalar_cells=len(failed),blocks=60,infeasible_blocks=sum(not r['feasible']for r in reports),
            feasible_blocks=sum(r['feasible']for r in reports),complete_Cartesian_products=sum(r['complete_block_products']for r in reports),
            complete_prefix_products=sum(r['complete_prefix_products']for r in reports),controls=controls,scope=statement,
            shared_components=shared,solver_calls=0,native_calls=0,full_factor=False,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        write(out/'summary.json',summary)
        write(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-THIRD-COUNT-SEPARATE-GRAM-PROJECTIONS',revision=1,status='VERIFIED',review_state='CLEAR',kind='finite_check',basis=['COMPUTED'],statement=statement,
            dependencies=[dict(id='C-FIXED-HADAMARD-PARTIAL-CUT-COUNT-CSP-WITNESS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage')],
            verifier='/root/structural_attack',producer='/root/eight_domain_audit',report=key(out/'summary.json'),report_sha256=sha(out/'summary.json'),
            shared_components=shared,limitations=['Literal third count profile only. Passing separate blocks does not imply joint choices, full Gram, cross-group column caps, residual D or target graph.']))
        print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as error:write(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start));raise


if __name__=='__main__':main()
