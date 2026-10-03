"""Independent literal domains, integer Gram scores and saved descent transitions."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import random
import subprocess
import sys
import time
import traceback
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'acceleration/results'
D = B / '20260930_hadamard_all_triple_descent'
RAW = B / '20260930_hadamard20_support/six_prism.json'
LOCAL = B / '20260930_hadamard_triplicate_counts/local_triples.json'
FIX = B / '20260930_srg243_residual_fixture/triangle_blocks.json'
SUMMARY_HASH = '733acd831ce70adc4b4b1e5503f3ee65bf01f5740b1daf3867790b324b812fff'
VERSION = 'FIXED_L_FULL_GRAM_FROBENIUS_SQUARED_V1'
SOURCE_HASH = '5e55ecf6bdad82d29e572737ec96f3e432d8b31175219aa31c92fe082750c3e5'


def need(ok, message):
    if not ok: raise ValueError(message)


def read(p): return json.loads(p.read_bytes())
def key(p): return p.resolve().relative_to(ROOT).as_posix()
def sha(p):
    with p.open('rb') as h: return hashlib.file_digest(h, 'sha256').hexdigest()
def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')
def tuples(value): return tuple(tuples(x) for x in value) if isinstance(value, list) else value


def target(core):
    n = len(core) // 3
    need(len(core) == 3*n and all(len(r) == 3*n for r in core), 'core dimensions')
    need(all(type(core[i][j]) is int and core[i][j] in (0,1) and core[i][j] == core[j][i]
             and (i != j or core[i][j] == 0) for i in range(3*n) for j in range(3*n)), 'simple raw core')
    return [[n*(i == j) + 2 - int(i//n == j//n) - core[i][j]
             - sum(core[i][k]*core[k][j] for k in range(3*n))
             for j in range(3*n)] for i in range(3*n)]


def gram_score(factor, wanted):
    rows = len(wanted); cols = len(factor[0]) if factor else 0
    need(len(factor) == rows and cols > 0 and all(len(r) == cols for r in factor), 'factor dimensions')
    need(all(type(x) is int and x in (0,1) for r in factor for x in r), 'strict binary factor')
    # Whole row intersections use independent Python arbitrary-precision integers.
    masks = [sum(v << d for d,v in enumerate(r)) for r in factor]
    gram = [[(u & v).bit_count() for v in masks] for u in masks]
    score = sum((gram[i][j]-wanted[i][j])**2 for i in range(rows) for j in range(rows))
    return gram, score


def catalog():
    words = [list(w) for w in product(range(3), repeat=6) if sorted(Counter(w).values()) == [2,2,2]]
    need(len(words) == 90, 'ninety balanced words')
    candidates = []
    for triple in combinations(range(90), 3):
        ws = [words[x] for x in triple]
        if any(sum(a == b for a,b in zip(x,y)) > 2 for x,y in combinations(ws,2)): continue
        valid = True
        for a,b in combinations(range(6),2):
            counts = [0]*9
            for w in ws: counts[3*w[a]+w[b]] += 1
            if any(c > (1 if j//3 == j%3 else 2) for j,c in enumerate(counts)):
                valid = False; break
        if valid: candidates.append(list(triple))
    need(len(candidates) == 31110, 'complete local survivor count')
    need(read(LOCAL)['words'] == words and read(LOCAL)['survivors'] == candidates, 'all literal local catalogue entries/order')
    return words, candidates


def geometry(raw):
    L = raw['L']; supports = [tuple(a for a in range(12) if L[a][d]) for d in range(60)]
    groups = sorted(set(supports)); columns = [[d for d,s in enumerate(supports) if s == g] for g in groups]
    need(len(groups) == 20 and all(len(g) == 6 and len(ds) == 3 for g,ds in zip(groups,columns)), 'literal support multiplicities')
    need(all(all(sum(x in g for x in (a,a+1)) == 1 for a in range(0,12,2)) for g in groups), 'one endpoint of every matching pair')
    return groups, columns


def reconstruct(indices, groups, columns, words, triples):
    need(len(indices) == 20 and all(type(i) is int and 0 <= i < 31110 for i in indices), 'twenty exact catalogue indices')
    F = [[0]*60 for _ in range(36)]
    for g,k in enumerate(indices):
        for d,w in zip(columns[g],triples[k]):
            for pos,a in enumerate(groups[g]): F[12*words[w][pos]+a][d] = 1
    return F


def object_check(obj, groups, columns, words, triples, wanted):
    F = reconstruct(obj['local_catalogue_indices'], groups, columns, words, triples)
    need(obj['factor36x60'] == F, 'literal factor equals independently reconstructed catalogue selection')
    gram, score = gram_score(F, wanted)
    need(obj['objective_version'] == VERSION and obj['exact_score'] == score, 'exact objective version/score')
    need(obj['full_Gram'] == gram and obj['row_sums'] == [sum(r) for r in F], 'all1296 Gram entries and row margins')
    # Different checking path for caps: literal scalar products of columns.
    violations = [dict(columns=[d,e],overlap=sum(F[r][d]*F[r][e] for r in range(36)))
                  for d,e in combinations(range(60),2) if sum(F[r][d]*F[r][e] for r in range(36)) > 2]
    need(obj['outside_cap_violations'] == violations, 'all1770 outside-column diagnostics')
    need(obj['full_Gram_valid'] == (score == 0) and obj['all_outside_caps_valid'] == (not violations), 'raw validity flags')
    need(obj['target_graph'] is False and obj['residual_D'] is None, 'no target graph or residual')
    need(all(sum(F[12*f+a][d] for a in range(12)) == 2 for f in range(3) for d in range(60)), 'all180 fibre-column quotas')
    return dict(score=score, column_cap_violations=len(violations), row_sums=obj['row_sums'])


def controls(groups, columns, words, triples, wanted):
    fixture=read(FIX);G=target(fixture['cubic_core60']);F=fixture['factor60x180'];gram,score=gram_score(F,G)
    need(score == 0, 'genuine243 full Gram positive')
    # Independent scalar multiplication also checks the bit-intersection scorer.
    need(gram == [[sum(x*y for x,y in zip(a,b)) for b in F] for a in F], '243 bit/scalar paths agree')
    bad=deepcopy(F);bad[0][0]^=1;need(gram_score(bad,G)[1] > 0, 'changed243 entry nonzero objective')
    ids=list(range(20));synthetic=reconstruct(ids,groups,columns,words,triples);own,_=gram_score(synthetic,wanted)
    need(gram_score(synthetic,own)[1] == 0, 'synthetic own-Gram zero control')
    rejected=[]
    def reject(name, call):
        try: call()
        except (ValueError,TypeError,IndexError): rejected.append(name);return
        raise ValueError('accepted corrupt control '+name)
    for name in ('Boolean','nonbinary','ragged'):
        f=deepcopy(F)
        if name == 'Boolean': f[0][0]=bool(f[0][0])
        elif name == 'nonbinary': f[0][0]=2
        else: f[0].pop()
        reject(name,lambda f=f:gram_score(f,G))
    for name,ids2 in [('bad_catalogue',[31110]+ids[1:]),('short_selection',ids[:-1]),('Boolean_index',[True]+ids[1:])]:
        reject(name,lambda ids2=ids2:reconstruct(ids2,groups,columns,words,triples))
    genuine=read(D/'chain_02/best_factor.json');object_check(genuine,groups,columns,words,triples,wanted)
    for name in ('score','raw_factor','Gram_entry','cap_list','selected_index'):
        o=deepcopy(genuine)
        if name == 'score': o['exact_score']+=1
        elif name == 'raw_factor': o['factor36x60'][0][0]^=1
        elif name == 'Gram_entry': o['full_Gram'][0][0]+=1
        elif name == 'cap_list': o['outside_cap_violations'].pop()
        else: o['local_catalogue_indices'][0]=(o['local_catalogue_indices'][0]+1)%31110
        reject(name,lambda o=o:object_check(o,groups,columns,words,triples,wanted))
    return dict(genuine_positive='SRG243 exact Gram zero, scalar and bit paths agree; not a Conway99 factor.',
                synthetic_positive='Own Gram of an explicit local-catalogue factor, not the prescribed research Gram.',
                changed_genuine_score_positive=True,rejected_corruptions=rejected)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();actual=sha(p);need(h is None or h==actual,'input identity '+key(p));pins[key(p)]=actual
    try:
        pin(D/'summary.json',SUMMARY_HASH);summary=read(D/'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_ALL_TRIPLE_DESCENT.md')
        need(pins['acceleration/theory_20260930_hadamard_all_triple_descent.py'] == SOURCE_HASH,'frozen producer source')
        raw=read(RAW);wanted=target(raw['core_adjacency']);need(wanted==raw['prescribed_Gram36'],'all raw core-derived Gram coefficients')
        groups,columns=geometry(raw);words,triples=catalog();model=read(D/'model.json')
        pairs=list(combinations(range(18),2));upper=[(i,j) for i in range(18) for j in range(i,18)]
        expected_model=dict(groups=[dict(support=list(g),columns=ds,global_rows=[12*f+a for f in range(3) for a in g]) for g,ds in zip(groups,columns)],local_upper_pairs=[list(x) for x in upper],weights=[1 if i==j else 2 for i,j in upper],target=wanted,contributions_path=key(D/'contributions_u8.npy'),contributions_sha256=sha(D/'contributions_u8.npy'),domain_size=31110,group_count=20,objective_version=VERSION)
        need(model == expected_model,'literal whole model')
        contribution=np.load(D/'contributions_u8.npy',allow_pickle=False);need(contribution.shape==(31110,171) and contribution.dtype==np.dtype('uint8'),'saved matrix dimensions/type')
        for k,tri in enumerate(triples):
            rows=[sum(int(words[w][a]==f)<<d for d,w in enumerate(tri)) for f in range(3) for a in range(6)]
            need(contribution[k].tolist()==[(rows[i]&rows[j]).bit_count() for i,j in upper],'all raw local contribution entries')
        calibration=controls(groups,columns,words,triples,wanted);save(out/'controls.json',calibration)
        need(summary['completed_chains']==summary['selected_chains']==4 and summary['unattempted_seeds']==[],'four saved chains')
        results=[];checkpoint_results=[];event_results=[];all_logged_scores=[]
        for chain,report in enumerate(summary['chains']):
            folder=D/f'chain_{chain:02d}';seed=99023000+chain
            need(report['chain']==chain and report['seed']==seed,'fixed chain/seed identity')
            cp_records=report['checkpoints'];need(len(cp_records)==102,'all initial/100sweeps/final checkpoints')
            cps={}
            for p in cp_records:
                pin(ROOT/p['path'],p['sha256']);c=read(ROOT/p['path']);label=Path(p['path']).stem
                need(c['source_sha256']==SOURCE_HASH and c['model_sha256']==pins[key(D/'model.json')],'checkpoint producer/model identity')
                for which in ('current','best'):
                    exact=object_check(c[which],groups,columns,words,triples,wanted)
                    idx='indices' if which=='current' else 'best_indices';sc='score' if which=='current' else 'best_score'
                    need(c[which]['local_catalogue_indices']==c['state'][idx] and exact['score']==c['state'][sc],'checkpoint state/object exact binding')
                random.Random().setstate(tuples(c['state']['rng'])) # schema only, not trajectory RNG replay
                cps[label]=c;checkpoint_results.append(dict(path=p['path'],sha256=p['sha256'],current_score=c['state']['score'],best_score=c['state']['best_score']))
            init=cps['checkpoint_initial']['state'];rng=random.Random(seed);initial=[rng.randrange(31110) for _ in range(20)]
            need(init['indices']==initial and tuples(init['rng'])==rng.getstate(),'actual seed initialization and initial RNG')
            ids=initial[:];best=initial[:];score=gram_score(reconstruct(ids,groups,columns,words,triples),wanted)[1];best_score=score;kicks=0;group_order=[];sweep_start_best=score
            events=[json.loads(line) for line in (folder/'updates.jsonl').read_bytes().splitlines()];need(len(events)==report['updates']==2000,'complete2000 logged update records')
            for j,e in enumerate(events,1):
                if (j-1)%20==0:group_order=[];sweep_start_best=best_score
                g=e['group'];need(type(g)is int and 0<=g<20 and g not in group_order,'one update per group in each sweep');group_order.append(g)
                need(e['update']==j and e['old']==ids[g] and type(e['new'])is int and 0<=e['new']<31110,'exact logged transition')
                ids[g]=e['new'];score=gram_score(reconstruct(ids,groups,columns,words,triples),wanted)[1];need(score==e['score_after_coordinate'],'every logged coordinate score independently recomputed')
                all_logged_scores.append(score)
                if score<best_score:best_score=score;best=ids[:]
                need(e['best_score']==best_score and 1<=e['minimum_ties']<=31110,'logged saved-best score and tie-count range only')
                expected_kick=j%20==0 and best_score!=0 and best_score==sweep_start_best
                need(len(e['kicks'])==(2 if expected_kick else 0),'declared kick stopping rule')
                if expected_kick:
                    need(len({x['group'] for x in e['kicks']})==2,'distinct kicked groups');kicks+=1
                for k in e['kicks']:
                    h=k['group'];need(type(h)is int and 0<=h<20 and k['old']==ids[h] and type(k['new'])is int and 0<=k['new']<31110,'literal kick transition');ids[h]=k['new']
                after=gram_score(reconstruct(ids,groups,columns,words,triples),wanted)[1];need(after==e['score_after_kicks'],'every post-kick exact score');all_logged_scores.append(after)
                if j%20==0:
                    st=cps[f'checkpoint_sweep_{j//20:05d}']['state']
                    expected=dict(seed=seed,indices=ids,best_indices=best,score=after,best_score=best_score,order=group_order,cursor=20,sweeps=j//20,updates=j,options_evaluated=j*31110,kicks=kicks,sweep_start_best=sweep_start_best)
                    need({k:st[k]for k in expected}==expected,'all saved non-RNG sweep state fields derived from complete event stream')
                event_results.append(dict(chain=chain,update=j,coordinate_score=score,after_kicks=after,best_score=best_score,kicked_groups=[k['group']for k in e['kicks']]))
            final=cps['checkpoint_final']['state'];need(final==cps['checkpoint_sweep_00100']['state'],'final checkpoint equals final sweep including RNG')
            raw_best=read(ROOT/report['best_factor_path']);best_result=object_check(raw_best,groups,columns,words,triples,wanted)
            need(raw_best==cps['checkpoint_final']['best'] and best_score==report['best_score']==best_result['score'] and best_result['column_cap_violations']==report['best_outside_cap_violations'],'literal final best artifact')
            need(report['current_score']==final['score'] and report['kicks']==kicks and report['sweeps']==100 and report['stop_reason']=='UPDATE_LIMIT','saved execution counters/scope')
            results.append(dict(chain=chain,seed=seed,logged_updates=len(events),saved_checkpoints=len(cps),best_path=report['best_factor_path'],best_sha256=report['best_factor_sha256'],**best_result))
            print(json.dumps(dict(checked_chain=chain,score=best_result['score'],checkpoints=len(cps))),flush=True)
        need(sum(r['logged_updates']for r in results)==8000 and len(checkpoint_results)==408 and min(r['score']for r in results)==296==summary['best_score'],'complete record counts and global saved best')
        save(out/'checkpoints.json',checkpoint_results);save(out/'events.json',event_results);save(out/'chains.json',results)
        best=min(results,key=lambda x:x['score']);need(best['column_cap_violations']==37 and min(all_logged_scores)==296,'best observed logged score/caps')
        statement='The four pinned saved descent chains with seeds99023000..99023003 contain8000 valid logged catalogue transitions and408 checkpoints whose current and saved-best factors have independently checked exact fixed-L full-Gram Frobenius-squared scores. The smallest saved and logged score is296 at the pinned chain02 best factor, which has37 outside-column overlaps greater than2 and is not a prescribed-Gram factor. Every group uses the complete31110-option local triple catalogue; no exclusion or target construction is established.'
        scope='Finite saved artifacts and all logged transition scores only. Exact move optimality, tie counts, complete intermediate RNG trajectory and248880000 hypothetical candidate evaluations are not independently reproduced.'
        binding=dict(id='C-FIXED-HADAMARD-ALL-TRIPLE-DESCENT-SAVED-OUTCOME',revision=1,statement=statement,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',scope=scope,dependencies=[dict(claim_id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='premise')],inputs_sha256=pins,verifier='eight_domain_audit',method='Own complete catalogue enumeration, Python integer row-bit Gram intersections, literal scalar column diagnostics and all saved raw factors/logged scores; no producer imports.',controls=calibration,limitations=[scope,'Positive energy excludes nothing; full residual graph is absent.'],created=datetime.now(timezone.utc).isoformat(),updated=datetime.now(timezone.utc).isoformat())
        save(out/'claim_binding.json',binding)
        report=dict(status='INDEPENDENT_ALL_TRIPLE_DESCENT_SAVED_ARTIFACTS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.glob('*.json')},statement=statement,scope=scope,chains=results,checked_checkpoints=408,checked_checkpoint_objects=816,checked_logged_updates=8000,checked_logged_coordinate_scores=8000,checked_logged_postkick_scores=8000,checked_contribution_entries=31110*171,catalogue_triples_examined=117480,catalogue_survivors=31110,minimum_logged_score=min(all_logged_scores),objective_version=VERSION,minimum_candidate_evaluations_verified=0,intermediate_rng_replay=False,initial_rng_replay=True,controls=calibration,shared_components=['Python standard-library SHA256, integer arithmetic and random state parser/initialization','NumPy only loads the immutable uint8 array; no NumPy score or delta operations'],elapsed_seconds=time.perf_counter()-start,native_calls=0,discovery_code_imports=False,artifact_availability='LOCAL_ONLY',target_resolution=False)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except Exception as e:
        save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise


if __name__=='__main__':main()
