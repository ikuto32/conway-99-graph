"""Exact candidate test of uniform local convex mixtures on all792 count tables."""
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path
from math import lcm
from importlib.metadata import version
import argparse, hashlib, json, platform, subprocess, sys, time
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
RAW = B+'hadamard20_support/six_prism.json'
LOCAL = B+'hadamard_triplicate_counts/local_triples.json'
MANIFEST = B+'exact_eight_campaign_preparation/campaign_manifest.json'
GATE = B+'independent_review/exact_eight_campaign_inventory/summary.json'
FIXTURE = B+'srg243_residual_fixture/triangle_blocks.json'
PINS = {RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
MANIFEST:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',
GATE:'555ef430f8a84b8b995c98566decf2c6cb92f9e8de6db1645955c0e48dd0f9ea',
FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}

def need(x, why):
    if not x: raise ValueError(why)

def digest(p):
    with (ROOT/p).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()

def read(p): return json.loads((ROOT/p).read_bytes())

def save(p, value):
    with p.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, separators=(',', ':')); stream.write('\n')

def gram(n, columns):
    result = [[0]*n for _ in range(n)]
    for col in columns:
        need(len(col)==len(set(col)) and all(type(i) is int and 0<=i<n for i in col), 'binary incidence column')
        for i in col:
            for j in col: result[i][j] += 1
    return result

def compare(total, target, denominator):
    need(type(denominator) is int and denominator>0, 'positive integral denominator')
    need(len(total)==len(target) and all(len(r)==len(total) for r in total+target), 'square Gram arrays')
    failed = [(i,j,total[i][j],denominator*target[i][j]) for i in range(len(target)) for j in range(len(target)) if total[i][j]!=denominator*target[i][j]]
    return dict(exact_uniform_witness=not failed, differing_entries=len(failed), first_difference=list(failed[0]) if failed else None)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out', required=True); args=ap.parse_args()
    out=(ROOT/args.out).resolve(); need(out.is_relative_to(ROOT) and not out.exists(), 'fresh contained output'); out.mkdir(parents=True)
    began=time.monotonic(); hashes={}; outputs={}; records=[]
    def checktime(): need(time.monotonic()-began<120, 'declared120-second calculation limit')
    def emit(name,obj):
        p=out/name; save(p,obj); outputs[p.relative_to(ROOT).as_posix()]=digest(p)
    try:
        for p,pin in PINS.items(): need(digest(p)==pin, 'input identity '+p); hashes[p]=pin
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:
            hashes[p.relative_to(ROOT).as_posix()]=digest(p)
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        emit('manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=hashes,python=platform.python_version(),tqdm=version('tqdm'),seconds=120,seed=None,seed_null_reason='Deterministic integer calculation.',floating_point=False,scope='Uniform local convex mixtures only; all792 literal count profiles.'))
        raw=read(RAW); cat=read(LOCAL); campaign=read(MANIFEST); gate=read(GATE)
        need(campaign['universe_size']==len(campaign['records'])==792, 'full frozen792 universe')
        need(gate['status'].startswith('INDEPENDENT_') and gate['status'].endswith('_PASS'), 'independent domain inventory')
        C=raw['core_adjacency']; G=[[12*(i==j)-C[i][j]+2-sum(C[i][k]*C[k][j] for k in range(36))-(i//12==j//12) for j in range(36)] for i in range(36)]
        need(G==raw['prescribed_Gram36'], 'integer core-derived Gram')
        supports=raw['support_columns'][:20]; need(all(raw['support_columns'][g+20*k]==supports[g] for g in range(20) for k in range(3)), 'triplicate group supports')
        words=cat['words']; triples=cat['survivors']; classes=defaultdict(list)
        need(len(words)==90 and len(triples)==31110, 'raw local catalogue')
        for ti,tri in enumerate(triples):
            sig=tuple(sum(words[w][a]==f for w in tri) for a in range(6) for f in range(3)); classes[sig].append(ti)
        need(len(classes)==6061, 'complete count classes')
        sums={}
        for sig,ids in tqdm(classes.items(),desc='Exact local uniform sums',mininterval=1):
            checktime(); sums[sig]=gram(18, [[3*a+words[w][a] for a in range(6)] for ti in ids for w in triples[ti]])
        emit('local_class_sums.json', [dict(signature=list(sig),domain_indices=ids,integer_Gram_sum=sums[sig]) for sig,ids in classes.items()])
        def mixture(signatures):
            sizes=[len(classes[sig]) for sig in signatures]; den=lcm(*sizes); total=[[0]*36 for _ in range(36)]
            for g,(sig,size) in enumerate(zip(signatures,sizes,strict=True)):
                mapping=[12*f+a for a in supports[g] for f in range(3)]; factor=den//size
                for i,row in enumerate(sums[sig]):
                    for j,value in enumerate(row): total[mapping[i]][mapping[j]]+=factor*value
            return den,total,sizes
        F=read(FIXTURE)['factor60x180']; actual=gram(60,[[i for i in range(60) if F[i][j]] for j in range(180)])
        doubled=[[2*x for x in row] for row in actual]
        need(compare(doubled,actual,2)['exact_uniform_witness'], 'genuine243 duplicated-option mean')
        bad=[r[:] for r in actual]; bad[0][0]+=1
        need(not compare(doubled,bad,2)['exact_uniform_witness'], 'changed actual target rejected')
        controls=['genuine243 exact mean','changed genuine243 target rejected']
        for denominator in [0,-1,0.5,True]:
            try: compare(doubled,actual,denominator)
            except ValueError: controls.append('invalid denominator rejected:'+str(denominator))
            else: raise AssertionError('bad denominator accepted')
        balanced=(1,)*18; need(len(classes[balanced])==150,'balanced150 domain')
        den,total,sizes=mixture([balanced]*20); need(compare(total,G,den)['exact_uniform_witness'], 'complete balanced uniform relaxation')
        emit('controls.json',dict(controls=controls,balanced_denominator=den,balanced_Gram_numerator=total,balanced_group_sizes=sizes,genuine_fixture_entries=3600,scope='Valid relaxation controls, not a Conway99 graph.'))
        for record in tqdm(campaign['records'],desc='Uniform rational Gram test792',mininterval=1):
            checktime(); counts=record['raw_representative']['counts']
            raw720=bytes(x for row in counts for group in row for x in group)
            need(len(raw720)==720 and hashlib.sha256(raw720).hexdigest()==record['full_count_profile_sha256'], 'literal720 profile identity')
            sigs=[tuple(counts[a][g][f] for a in supports[g] for f in range(3)) for g in range(20)]
            den,total,sizes=mixture(sigs); verdict=compare(total,G,den)
            r=dict(case_id=record['case_id'],case_index=record['case_index'],profile_sha256=record['full_count_profile_sha256'],denominator=den,domain_sizes=sizes,**verdict)
            records.append(r)
            if verdict['exact_uniform_witness']: emit('witness_%04d.json'%record['case_index'],dict(**r,integer_Gram_numerator=total))
            if len(records)%64==0: emit('checkpoint_%04d.json'%len(records),dict(records=records[:],completed=len(records),pending=792-len(records)))
        emit('records.json',records)
        summary=dict(status='CANDIDATE_EXACT_EIGHT_UNIFORM_GRAM_DIAGNOSTIC',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=hashes,outputs_sha256=outputs.copy(),population=792,completed=len(records),uniform_witnesses=sum(r['exact_uniform_witness'] for r in records),uniform_failures=sum(not r['exact_uniform_witness'] for r in records),domain_class_population=len(classes),denominator_counts=dict(Counter(r['denominator'] for r in records)),elapsed_seconds=time.monotonic()-began,native_calls=0,independent_approval=False,target_resolution='UNKNOWN',limitations=['Uniform weights only: failure does not imply LP infeasibility.','Rational convex mixtures are not integral factors or target graphs.','Neither a whole-support nor unrestricted exclusion follows.'])
        emit('summary.json',summary); print(json.dumps({k:summary[k] for k in ['population','completed','uniform_witnesses','uniform_failures','elapsed_seconds']})); print(digest(out/'summary.json'))
    except BaseException as ex:
        emit('failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),error=repr(ex),completed=len(records),inputs_sha256=hashes)); raise

if __name__=='__main__': main()
