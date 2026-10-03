"""Independent exact compact-prefix equivalence and all template audit."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_one_c2_row_cnf as original

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_one_c2_compact'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_row_cnf/summary.json'
GATE_SHA='661062b1fbdf0d9e076082867b44353509fb892d9946dc142d1c70b91f59558d'
SUMMARY_SHA='c16b08a1835ba33e1f08b7db312a4d1e61eb0b2e284879bdbb2ec146aa78df35'
need,digest,key,save=original.need,original.digest,original.key,original.save

def controls():
    cases=0
    for n in [4,6]:
        pairs=[(1<<a)|(1<<b) for a,b in combinations(range(n),2) if b!=(a^1)]
        for a,b in combinations(pairs,2):
            q=(a&b).bit_count();need(q<=1,'distinct two-subset overlap')
            for k,x,y in product([0,1],repeat=3):
                literal=all(not(k and x and y and (a>>r&1) and (b>>r&1)) for r in range(n))
                need(literal==(k+q+x*y<=2),'small bitset capacity equivalence');cases+=1
    for values in product([False,True],repeat=4):need(any(not x for x in values)==(not all(values)),'fourliteral truth relation')
    need(not(0+2+1<=2),'missing distinctness creates genuine counterexample')
    return dict(bitset_cases=cases,fourliteral_assignments=16,missing_distinctness_counterexample=dict(C0_overlap=0,C1_overlap=2,y_product=1,original_accepts=False,unguarded_omission_accepts=True))

def expected_templates(known,refs):
    templates=[];clauses=[];pair_counts=[0,0]
    for d,e in combinations(range(60),2):
        overlap=[r for r in range(12) if known[r][d] and known[r][e]];need(len(overlap)<=1,'canonical distinct C0 pairs');pair_counts[len(overlap)]+=1
        if not overlap:continue
        for r in range(12,24):
            coordinates=[[r,d],[r,e],[24,d],[24,e]];values=[refs[a][b] for a,b in coordinates]
            need(all(x is False or type(x) is int for x in values),'only variable or forcedzero')
            zeros=[p for p,x in zip(coordinates,values) if x is False]
            record=dict(C0_common_endpoint=overlap[0],column_pair=[d,e],C1_row=r,coordinates=coordinates,references=values)
            if zeros:record.update(action='OMIT_TAUTOLOGY_FIXED_ZERO',zero_coordinates=zeros,clause=None,clause_null_reason='At least one negated fixed-zero literal is true.')
            else:
                clause=[-v for v in values];need(len(set(clause))==4,'four distinct literals');clauses.append(clause)
                record.update(action='EMIT',zero_coordinates=[],clause=clause,first_clause=77721+len(clauses),clause_count=1)
            templates.append(record)
    need(pair_counts==[1230,540] and len(templates)==6480 and len(clauses)==3645,'complete frozen template universe')
    return templates,clauses

def recipe_check(recipe,templates,clauses):
    need(recipe['candidate_clauses']==templates,'every emitted/omitted clause mapping')
    need(recipe['retained_body_clause_count']==77721 and recipe['retained_maximum_variable']==22379,'prefix boundary')
    need(recipe['intersecting_C0_column_pairs']==540 and recipe['full_pair_row_universe']==6480 and recipe['emitted_count']==3645 and recipe['omitted_fixed_zero_tautologies']==2835 and recipe['disjoint_C0_column_pair_count']==1230,'exact population counts')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(path,expected=None):
        path=Path(path);value=digest(path);need(expected is None or value==expected,'hash '+str(path));bindings[key(path)]=value;return path
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    try:
        gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_TRIANGLE_ONE_C2_ROW_CNF_ENCODING_PASS','original independent gate')
        for p,v in gate['inputs_sha256'].items():bind(ROOT/p,v)
        summary=read(D/'summary.json',SUMMARY_SHA);manifest=read(D/'manifest.json')
        for p,v in manifest['inputs_sha256'].items():bind(ROOT/p,v)
        for p,r in summary['outputs'].items():need(bind(D/p,r['sha256']).stat().st_size==r['bytes'],'frozen output length')
        old=read(original.D/'model.json');scope=read(original.D/'scope.json');g,cols,known,entries,refs,comp=original.scope_check(old,scope)
        model=read(D/'model.json');recipe=read(D/'replacement_recipe.json');templates,clauses=expected_templates(known,refs);recipe_check(recipe,templates,clauses)
        kept=old['counter_rows'][:487];products=[p for p in old['product_variables'] if p['kind']=='row_gram']
        need(len(kept)==487 and len(products)==3200 and old['counter_rows'][487]['kind']=='column_pair_overlap','exact prefix equation/product populations')
        need(max(r['first_clause']+r['clause_count']-1 for r in kept)==77721,'last complete prefix clause')
        prefixvars=set(e['id'] for e in entries)|set(p['id'] for p in products)
        for r in kept:prefixvars.update(x for x in r['inputs'] if type(x) is int);prefixvars.update(s[2] for s in r['states'] if type(s[2]) is int)
        need(prefixvars==set(range(1,22380)),'all and only retained variables')
        expected=dict(old);expected.update(schema='TRIANGLE_ONE_C2_ROW_COMPACT_PREFIX_CNF_V1',product_variables=products,counter_rows=kept,compact_clauses=clauses,variables=22379,clauses=81366,retained_original_clause_count=77721,original_model_path=key(original.D/'model.json'),original_model_sha256=digest(original.D/'model.json'),replacement_recipe_path=key(D/'replacement_recipe.json'),replacement_recipe_sha256=digest(D/'replacement_recipe.json'),equivalence_review='PENDING_INDEPENDENT_REVIEW',solver_calls=0)
        need(model==expected,'complete new model versus independently reconstructed prefix/suffix')
        need(recipe['base_cnf_path']==key(original.D/'instance.cnf') and recipe['base_cnf_sha256']==digest(original.D/'instance.cnf') and recipe['base_model_sha256']==digest(original.D/'model.json') and recipe['scope_path']==key(original.D/'scope.json') and recipe['scope_sha256']==digest(original.D/'scope.json'),'recipe exact original identities')
        with (original.D/'instance.cnf').open('rb') as before,(D/'instance.cnf').open('rb') as after:
            need(before.readline()==b'p cnf 74814 256151\n' and after.readline()==b'p cnf 22379 81366\n','exact headers')
            for _ in range(77721):need(before.readline()==after.readline(),'exact original prefix bytes')
            for clause in clauses:need(after.readline()==(' '.join(map(str,clause))+' 0\n').encode(),'every independently reconstructed suffix byte')
            need(after.read()==b'','no extra compact clauses')
        corrupt=[]
        for name in ['missing_template','wrong_literal','missing_zero_reason','prefix_boundary','wrong_omission_count']:
            bad=deepcopy(recipe)
            if name=='missing_template':bad['candidate_clauses'].pop()
            elif name=='wrong_literal':next(r for r in bad['candidate_clauses'] if r['action']=='EMIT')['clause'][0]*=-1
            elif name=='missing_zero_reason':next(r for r in bad['candidate_clauses'] if r['action'].startswith('OMIT'))['zero_coordinates']=[]
            elif name=='prefix_boundary':bad['retained_body_clause_count']-=1
            else:bad['omitted_fixed_zero_tautologies']-=1
            try:recipe_check(bad,templates,clauses)
            except ValueError:corrupt.append(name)
            else:raise ValueError('corrupted compact recipe accepted '+name)
        calibration={**controls(),'corrupted_recipes_rejected':corrupt};save(args.out/'controls.json',calibration)
        packages=[]
        for p in read(D/'artifact_packages.json')['packages']:
            compressed=b''.join(bind(ROOT/part['path'],part['sha256']).read_bytes() for part in p['ordered_parts']);need(sha256(compressed).hexdigest()==p['compressed_stream_sha256'],'gzip stream')
            recovered=gzip.decompress(compressed);need(len(recovered)==p['raw_bytes'] and sha256(recovered).hexdigest()==p['raw_sha256']==digest(ROOT/p['raw_path']),'exact package recovery');packages.append(dict(path=p['raw_path'],sha256=p['raw_sha256'],bytes=len(recovered)))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_TRIANGLE_ONE_C2_COMPACT.md']:bind(p)
        need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable frozen artifacts')
        report=dict(status='INDEPENDENT_TRIANGLE_ONE_C2_COMPACT_EQUIVALENCE_PASS',claim_id='C-FIXED-TRIANGLE-ONE-C2-COMPACT-CNF-EQUIVALENCE',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit independent prefix and complete fourliteral-universe checker',kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
          statement='The exact22379variable81366clause compact formula has precisely the same primary incidence solutions as the audited original25row target projection. Every original model restricts to it, and every compact model extends uniquely over the removed original product/threshold auxiliaries.',dependencies=[dict(id='C-FIXED-TRIANGLE-ONE-C2-ROW-TARGET-PROJECTION-CNF',revision=1,relation='encoding_equivalence')],scope='Same explicit25row fixed-core target-necessary problem; no new target coverage.',variables=22379,clauses=81366,retained_clauses=77721,retained_counter_rows=487,retained_products=3200,primary_entries=650,template_population=6480,emitted_fourliteral_clauses=3645,omitted_fixedzero_tautologies=2835,disjoint_pairs_automatically_bounded=1230,controls=calibration,package_checks=packages,
          shared_components=['Frozen independent original full-clause gate and scope constructor used as explicit premises.','New direct fourliteral template/byte checker; no producer imports.'],limitations=['Clause count reduction is not a solver performance guarantee.','No additional SAT solve or larger object is claimed.'],solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e)));raise

if __name__=='__main__':main()
