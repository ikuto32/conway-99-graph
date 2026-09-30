"""Independent raw-label normalization, exact CNF suffix and domain audit."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_prism_coarse60_bitlift'
D=ROOT/'acceleration/results/20260930_prism_coarse60_bitflip'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_coarse60_bitlift_cnf/summary.json'
GATE_SHA='b82eb3d3c999ae8bdcdbfd246dd28ea9cd6a9dd8d1ce811abc82ee0f3e38d88d'
SUMMARY_SHA='9d74818830b3453194da3025d9e16dbc20ad341a9f2ea3728f8a9c32681d802a'
def need(x,s):
    if not x:raise ValueError(s)
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def suffix_check(base,aug,units):
    need(base.split(b'\n',1)[0]==b'p cnf 5238 85698','base header')
    need(aug==b'p cnf 5238 85704\n'+base.split(b'\n',1)[1]+b''.join(f'{v} 0\n'.encode() for v in units),'exact base body plus six units')

def action_check(action,mask,model,scope,complements):
    labels=[(g,a,b) for g in range(3) for a in range(6) for b in range(2)]
    switched={labels[i]:i for i in range(36)}
    images=[switched[g,a,1-b if mask&(1<<a) else b] for g,a,b in labels]
    need(action['component_flip_mask']==mask and action['row_images']==images,'independent row action')
    need(sorted(images)==list(range(36)),'row bijection')
    c=scope['core_adjacency39'];gram=scope['target_gram36']
    p=[0,1,2]+[i+3 for i in images]
    need(all(c[i][j]==c[p[i]][p[j]] for i in range(39) for j in range(39)),'all raw39 core entries preserved')
    need(all(gram[i][j]==gram[images[i]][images[j]] for i in range(36) for j in range(36)),'all raw Gram entries preserved')
    expected=[]
    for index,domain in enumerate(model['domains']):
        for j,s in enumerate(domain['selectors']):expected.append(domain['selectors'][complements[index][j]] if mask&(1<<domain['component']) else s)
    need(action['selector_images']==expected and sorted(expected)==list(range(1,2449)),'all selector images')
    bits=[-v['variable'] if mask&(1<<v['component']) else v['variable'] for v in model['raw_bits']]
    need(action['raw_bit_literal_images']==bits,'all signed raw bit images')

def prefix_values(domain,prefix,choice):
    vals={s:int(j==choice) for j,s in enumerate(domain['selectors'])}
    for row in prefix['prefixes']:vals[row['variable']]=int(any(vals[s] for s in domain['selectors'][:domain['selectors'].index(row['selector'])+1]))
    return vals
def check_clauses(clauses,values):
    need(all(any(values[abs(v)]==int(v>0) for v in clause) for clause in clauses),'literal prefix clause satisfaction')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(digest(D/'summary.json')==SUMMARY_SHA,'producer summary')
        need(digest(GATE)==GATE_SHA and read(GATE)['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS','base encoding gate')
        prod=read(D/'summary.json');bindings={**prod['inputs_sha256'],**prod['outputs_sha256'],key(D/'summary.json'):SUMMARY_SHA,key(GATE):GATE_SHA}
        for p,h in bindings.items():need(digest(ROOT/p)==h,'input closure '+p)
        model=read(BASE/'model.json');scope=read(BASE/'scope.json');artifact=read(D/'actions64.json');extension=read(D/'extension.json')
        words=scope['columns60'];need(len(words)==60 and len({tuple(w) for w in words})==60,'fixed coarse population')
        expected_bits=[dict(variable=2449+6*d+a,column=d,component=a,fibre=words[d][a]) for d in range(60) for a in range(6)]
        need(model['raw_bits']==expected_bits,'360 direct labels')
        complements=[];global_masks=[];positions=[]
        for index,domain in enumerate(model['domains']):
            a,g=divmod(index,3);pos=[d for d,w in enumerate(words) if w[a]==g];positions.append(pos)
            need((domain['component'],domain['fibre'])==(a,g) and domain['column_positions']==pos and len(pos)==20,'raw domain labels')
            masks=domain['local_masks'];need(len(masks)==136 and len(set(masks))==136 and all(type(m)is int and 0<=m<2**20 and m.bit_count()==10 for m in masks),'binary balanced local domain')
            support=[frozenset(t for t in range(20) if m&(1<<t)) for m in masks]
            lookup={s:j for j,s in enumerate(support)};comp=[lookup[frozenset(range(20))-s] for s in support];complements.append(comp)
            need(all(comp[comp[j]]==j and comp[j]!=j for j in range(136)),'independent complement involution')
            global_masks.append([sum(1<<pos[t] for t in s) for s in support])
        need(artifact['domain_complement_indices']==complements,'all saved complements')
        actions=artifact['actions'];need(len(actions)==64,'action population')
        for mask,a in enumerate(actions):action_check(a,mask,model,scope,complements)
        for x,y in product(range(64),repeat=2):
            z=actions[x^y]
            for field in ['row_images','selector_images']:
                offset=int(field=='selector_images');a=actions[x][field];b=actions[y][field]
                need([a[v-offset] for v in b]==z[field],'complete action composition '+field)
            need([int(v/abs(v))*actions[x]['raw_bit_literal_images'][abs(v)-2449] for v in actions[y]['raw_bit_literal_images']]==z['raw_bit_literal_images'],'signed bit composition')
        coverage=[dict(first_column_bits=[int(bool(m&(1<<a))) for a in range(6)],unique_action=m,normalized_bits=[0]*6) for m in range(64)]
        need(artifact['first_column_coverage']==coverage,'complete first-column coverage')
        units=[-v['variable'] for v in expected_bits if v['column']==0]
        need(extension['appended_unit_literals']==units and units==list(range(-2449,-2455,-1)),'six metadata units')
        for field,name in [('base_cnf','instance.cnf'),('base_model','model.json'),('base_scope','scope.json')]:
            need(extension[field]==key(BASE/name) and extension[field+'_sha256']==digest(BASE/name),'extension raw provenance')
        need((extension['variables'],extension['clauses'],extension['base_clause_count'],extension['group_size'])==(5238,85704,85698,64),'extension dimensions')
        need(extension['base_encoding_gate']==key(GATE) and extension['base_encoding_gate_sha256']==GATE_SHA,'extension gate')
        need(extension['actions']==key(D/'actions64.json') and extension['actions_sha256']==digest(D/'actions64.json'),'extension actions')
        need(extension['first_column_records']==expected_bits[:6],'extension first bits')
        base=(BASE/'instance.cnf').read_bytes();aug=(D/'instance.cnf').read_bytes();suffix_check(base,aug,units)
        need((D/'units.clauses').read_bytes()==b''.join(f'{v} 0\n'.encode() for v in units),'suffix artifact')
        # Independently count all four bit combinations, not the producer bit11-only expression.
        relations=[];seen=set();pairs=0
        for rel in model['Gram_relations']:
            l,r=rel['left_domain'],rel['right_domain'];need(l//3<r//3 and (l,r) not in seen,'unique intercomponent relation');seen.add((l,r))
            region=sum(1<<d for d in set(positions[l])&set(positions[r]));target=1 if l%3==r%3 else 2
            need(region.bit_count()==4*target and rel['target_bit11']==target,'raw relation geometry')
            table=[]
            for x in global_masks[l]:
                row=0
                for j,y in enumerate(global_masks[r]):
                    counts=((region&~x&~y).bit_count(),(region&~x&y).bit_count(),(region&x&~y).bit_count(),(region&x&y).bit_count())
                    if counts==(target,)*4:row|=1<<j
                    # Endpoint flips only permute these four entries.
                    need((counts==(target,)*4)==(counts[2:]+counts[:2]==(target,)*4),'left flip contingency invariance')
                    need((counts==(target,)*4)==((counts[1],counts[0],counts[3],counts[2])==(target,)*4),'right flip contingency invariance')
                    pairs+=1
                table.append(row)
            need(table==[int(s,16) for s in rel['allowed_right_masks_hex']],'raw four-count compatibility table')
            for i in range(136):
                for j in range(136):
                    value=(table[i]>>j)&1
                    need(value==((table[complements[l][i]]>>j)&1)==((table[i]>>complements[r][j])&1),'saved complementary choices preserve relation')
            relations.append(dict(left=l,right=r,pairs=18496,allowed=sum(v.bit_count() for v in table)))
        need(seen=={(3*a+g,3*b+h) for a,b in combinations(range(6),2) for g,h in product(range(3),repeat=2)},'complete135 relation population')
        clauses=[list(map(int,line.split()))[:-1] for line in base.splitlines()[1:]]
        prefix_controls=0
        for index,(domain,prefix) in enumerate(zip(model['domains'],model['exact_one_prefixes'],strict=True)):
            actual=clauses[index*541:(index+1)*541]
            need(len(actual)==541,'actual prefix block size')
            for j in range(136):check_clauses(actual,prefix_values(domain,prefix,j));prefix_controls+=1
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError):rejected.append(label)
            else:raise ValueError('accepted corrupted control '+label)
        for field in ['row_images','selector_images','raw_bit_literal_images']:
            bad=deepcopy(actions[1]);bad[field][0]=actions[0][field][0]
            reject('changed_'+field,lambda bad=bad:action_check(bad,1,model,scope,complements))
        for label,bad in [('missing_unit',aug.rsplit(b'\n',2)[0]+b'\n'),('positive_unit',aug[:-len(b'-2454 0\n')]+b'2454 0\n'),('wrong_header',aug.replace(b'85704',b'85703',1)),('changed_base',aug.replace(b'1 2809',b'2 2809',1))]:
            reject(label,lambda bad=bad:suffix_check(base,bad,units))
        vals=prefix_values(model['domains'][0],model['exact_one_prefixes'][0],0);vals[2809]^=1
        reject('incorrect_prefix_OR',lambda:check_clauses(clauses[:541],vals))
        need(all(((x^e)==(y^e))==(x==y) for x,y,e in product(range(2),repeat=3)),'complete cap equality truth table')
        save(out/'controls.json',dict(actions_checked=64,all_group_compositions=4096,relation_tables=relations,selector_pairs=pairs,prefix_single_choices=prefix_controls,cap_equalities=8,corruptions_rejected=rejected,exploratory_read_failure='Optional model sections print raised KeyError; no research run or result was affected. Actual model keys/clauses were inspected instead.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_PRISM_COARSE60_BITFLIP.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
        now=datetime.now(timezone.utc).isoformat();report=dict(status='INDEPENDENT_SIX_PRISM_COARSE60_BITFLIP_NORMALIZATION_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},verifier='/root/state_literature_audit',method='independent_derivation_and_exact_artifact_check',shared_components=['Python standard library; no producer imports.','Frozen independent base encoding equivalence is a declared dependency.'],variables=5238,clauses=85704,complete_base_clauses=85698,appended_units=units,actions_checked=64,selector_pairs_checked=pairs,prefix_controls=prefix_controls,corruptions_rejected=rejected,artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0,elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',report)
        claim=dict(id='C-SIX-PRISM-COARSE60-COMPONENT-BIT-NORMALIZATION',revision=1,statement='The exact fixed coarse60 six-prism base formula with5238variables85698clauses is satisfiable if and only if its exact six first-column bit-zero unit extension with5238variables85704clauses is satisfiable.',kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='The authenticated fixed60-column six-prism template only.',assumptions=['No nontrivial target automorphism is assumed.'],dependencies=prod['dependencies'],evidence=[dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json'),availability='LOCAL_ONLY')],verifier=report['verifier'],checking_method=report['method'],limitations=['No factor, residual D or target graph is produced.','No arbitrary-template or unrestricted-core coverage.','Auxiliaries are reconstructed, not asserted to permute.'],created_at=now,updated_at=now)
        save(out/'claim_binding.json',claim);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'),binding_sha256=digest(out/'claim_binding.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
