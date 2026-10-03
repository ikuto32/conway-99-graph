"""Independent raw selected-parity lift domain/matrix and zero-row exclusion."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys
import audit_20260930_balanced_lift_lp as helper
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';D=B+'hadamard_parity_lift_cnf/';O=B+'hadamard_parity_lift_obstruction/'
PINS={D+'exact_model.json':'dc9534f38c2bf2cb6c7f24c027c7a0ef15e8a5282e3b1c83d87ed5679555fbbd',D+'scope.json':'c7b232d8d6cf53bc7c7c0fb062191e25f88f2e0b531c98c21c0175335c79077c',O+'certificate.json':'e54b0676ed2796e2eb03930e066be8a4503553023746ad41b2c4df25700634e9'}
def h(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(v,s):
    if not v:raise ValueError(s)
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};corrupt=[]
    def pin(p,digest=None):
        v=h(ROOT/p);need(digest is None or v==digest,'artifact '+p);pins[p]=v;return ROOT/p
    def load(p,digest=None):return json.loads(pin(p,digest).read_bytes())
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,IndexError,TypeError):corrupt.append(name)
        else:raise ValueError('corruption accepted '+name)
    try:
        for p,digest in {**helper.PINS,**PINS}.items():pin(p,digest)
        gate=load(helper.GATE);need(gate['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_SAT_OBJECT_PASS','exact selected parity input gate')
        for p,digest in gate['outputs_sha256'].items():pin(p,digest)
        projection=load(I+'hadamard_balanced_parity_sat_v2/independent_projection.json');raw=load(helper.RAW)
        fullcols,fullrhs,_,_=helper.matrix(raw,projection,True);helper.primal(fullcols,fullrhs,[Fraction(1,150)]*3000)
        helper.primal([[0],[0]],[1],[Fraction(1,3),Fraction(2,3)]);helper.dual([[0,1]],[0,1],[1,-1])
        reject('uniform_bad_denominator',lambda:helper.primal(fullcols,fullrhs,[Fraction(1,149)]*3000))
        reject('positive_dual_rhs',lambda:helper.dual([[0,1]],[0,1],[-1,1]))
        reject('nonnegative_primal_violation',lambda:helper.primal([[0],[0]],[1],[-1,2]))
        cols,rhs,selectors,domains=helper.matrix(raw,projection);model=load(D+'exact_model.json');scope=load(D+'scope.json');catalog=helper.triples()
        need(model['variables']==312 and model['equations']==560 and model['binary_coefficients'] is True and model['nonnegative_variables'] is True,'continuous exact model domain')
        need(model['columns_nonzero_row_indices']==cols and model['rhs']==rhs,'every reconstructed matrix coefficient')
        need(model['selectors']==[[r['group'],r['choice']] for r in selectors],'complete selector order')
        need(model['scope_sha256']==PINS[D+'scope.json'],'model scope hash')
        need(scope['raw_support_sha256']==helper.PINS[helper.RAW] and scope['L']==raw['L'] and scope['matchings']==raw['matchings'] and scope['core_adjacency']==raw['core_adjacency'] and scope['target_gram36']==raw['prescribed_Gram36'],'fixed raw geometry')
        pin(scope['parity_projection'],scope['parity_projection_sha256']);need(gate['inputs_sha256'][scope['parity_projection']]==scope['parity_projection_sha256'],'producer scope exact verified parity artifact')
        need(scope['selected_pattern_indices']==projection['selected_pattern_indices'] and scope['one_fixed_parity_branch'] and not scope['all_balanced_branches_covered'] and not scope['arbitrary_fixedL_factors_covered'] and not scope['residual_D_encoded'],'narrow branch scope flags')
        need(len(scope['domains'])==20,'complete raw group domains')
        offsets=[0]
        for ds in domains:offsets.append(offsets[-1]+len(ds))
        for g,(saved,choices) in enumerate(zip(scope['domains'],domains)):
            support=projection['group_records'][g]['support'];rawcols=[d for d in range(60) if [i for i in range(12) if raw['L'][i][d]]==support]
            need(saved['group']==g and saved['support_coordinates']==support and saved['raw_columns']==rawcols and saved['selected_parity_pattern']==projection['selected_group_parity_patterns'][g],'raw group identity')
            need(len(saved['choices'])==len(choices),'exhaustive filtered choices')
            for j,(item,choice) in enumerate(zip(saved['choices'],choices)):
                rows=[sorted(support[i]+12*w[i] for i in range(6)) for w in choice['words']]
                need(item['selector']==offsets[g]+j+1 and item['choice_index']==j and item['balanced_triple_index']==catalog.index(choice),'exact local selector mapping')
                need(item['word_indices']==choice['word_indices'] and item['color_words']==choice['words'] and item['lifted_rows']==rows,'every literal local triple')
                need([int(mask,16) for mask in item['lifted_masks_hex']]==[sum(1<<r for r in rs) for rs in rows],'every raw incidence mask')
        rowpairs=[list(p) for p in combinations(range(36),2) if (p[0]%12)//2!=(p[1]%12)//2]
        rowmeta=[]
        for row in range(560):
            inputs=[j+1 for j,col in enumerate(cols) if row in col]
            expected=dict(kind='group_exactone',group=row,inputs=inputs,target=rhs[row]) if row<20 else dict(kind='gram_count',rows=rowpairs[row-20],target=rhs[row],inputs=inputs)
            need(model['row_metadata'][row]==expected,'complete row metadata');rowmeta.append(expected)
        zero=[row for row,m in enumerate(rowmeta) if not m['inputs'] and rhs[row]!=0]
        need(zero==[139,215,399,445,539,555],'exact six empty target rows')
        weights=[-int(r==zero[0]) for r in range(560)];dots,right=helper.dual(cols,rhs,weights)
        need(dots==[0]*312 and right==-1,'literal one-row Farkas certificate')
        # Raw matrices are checked again through actual pair occurrence, not sparse membership.
        raw_zeros=[]
        for row in zero:
            a,b=rowpairs[row-20];occurrences=[]
            for group in scope['domains']:
                for item in group['choices']:occurrences.append(sum(a in rs and b in rs for rs in item['lifted_rows']))
            need(occurrences==[0]*312 and raw['prescribed_Gram36'][a][b]==1,'literal312 raw-column zero products')
            raw_zeros.append(dict(row=row,rows=[a,b],required=1,coefficients=occurrences))
        produced=load(O+'certificate.json')
        # Entire producer certificate is pinned; its schema is retained alongside
        # our independently constructed literal certificate, without trusting it.
        reject('actual_dual_sign',lambda:helper.dual(cols,rhs,[-v for v in weights]))
        badcols=deepcopy(cols);badcols[0]=sorted(set(badcols[0]+[zero[0]]));reject('invented_zero_row_coefficient',lambda:helper.dual(badcols,rhs,weights))
        badrhs=rhs.copy();badrhs[zero[0]]=0;reject('zeroed_required_rhs',lambda:helper.dual(cols,badrhs,weights))
        badscope=deepcopy(scope);badscope['domains'][0]['choices'][0]['color_words'][0][0]^=1
        reject('corrupt_domain_word',lambda:need(badscope['domains'][0]['choices'][0]['color_words']==domains[0][0]['words'],'corrupt word refused'))
        badmodel=deepcopy(model);badmodel['columns_nonzero_row_indices'][0]=badcols[0]
        reject('corrupt_sparse_matrix',lambda:need(badmodel['columns_nonzero_row_indices']==cols,'corrupt matrix refused'))
        fail=load(D+'failure.json');need(fail['mathematical_exclusion'] is False,'failed partial builder was not mathematical proof')
        save(out/'independent_matrix.json',dict(columns_nonzero_row_indices=cols,rhs=rhs,selectors=selectors,domain_sizes=list(map(len,domains)),row_metadata=rowmeta))
        save(out/'zero_row_certificate.json',dict(weights=weights,column_products=dots,rhs_product=right,all_empty_rows=raw_zeros))
        for p in ['acceleration/audit_20260930_balanced_lift_zero_rows.py','acceleration/audit_20260930_balanced_lift_lp.py','docs/AUDIT_20260930_BALANCED_LIFT_LP.md','uv.lock','pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();claim=dict(id='C-FIXED-HADAMARD-SIX-PRISM-FIRST-PARITY-LIFT-EXCLUSION',revision=1,statement='The exact312-variable560-equation nonnegative Gram-selector system for the first independently checked parity assignment on the saved six-prism Hadamard support is infeasible: rows139,215,399,445,539,555 have zero coefficients and right-hand side1. The vector with only y139=-1 has all312column products0 and RHS product-1.',kind='exclusion',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='Only this one fully specified selected-parity colouring branch on one fixed support. No other parity assignment, unbalanced factor, whole support, core or Conway99 exclusion.',assumptions=['Balanced local triples and the exact authenticated selected20parity patterns.','No target automorphism is assumed.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-NONCYCLIC-PARITY-PROJECTION-WITNESS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-BALANCED-PARITY-PROJECTION',revision=1,relation='uses_result')],created_at=now,updated_at=now,limitations=['No LP or SAT solver result is required.','Integrality, between-group column caps and residualD are omitted from the already impossible continuous relaxation.','The producer partial-CNF assertion failure is preserved but is not the proof.'])
        summary=dict(status='INDEPENDENT_SELECTED_PARITY_LIFT_ZERO_ROW_EXCLUSION_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():h(p) for p in out.glob('*.json')},counts=dict(variables=312,equations=560,nonzeros=sum(map(len,cols)),mixed_groups=16,constant_groups=4,zero_rows=6,positive_uniform_control_variables=3000,positive_uniform_control_rows=560),claim=claim,corruptions=corrupt,verifier='/root/eight_domain_audit',method='independent_complete_domain_matrix_and_literal_zero_row_check',shared_components=['Own independently authored pending LP checker helper reused for direct word-generation, sparse mapping and exact products; no producer imports.','Source was prepared before outcome and its never-executed LP mode is not used; native/LP solver is not called.'],artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0)
        save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],sha256=h(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc)));raise
if __name__=='__main__':main()
