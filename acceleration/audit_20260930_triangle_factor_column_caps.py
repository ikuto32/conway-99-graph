"""Independent complete full36 compact column-cap scope, recipe and byte audit."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_factor_components as premise

ROOT=Path(__file__).resolve().parents[1]
BASE=premise.D
D=ROOT/'acceleration/results/20260930_triangle_factor_column_caps'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_factor_components/summary.json'
GATE_SHA='03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b'
SUMMARY_SHA='21edd0a943f14cd3588fd864660c1e60b27f9ceae9ba25c92d1b00f4c2e9c235'
need,digest,key,save=premise.need,premise.digest,premise.key,premise.save

def templates_from_raw(known,refs):
    templates=[];clauses=[];pairs=[];disjoint=0
    for d,e in combinations(range(60),2):
        common=[r for r in range(12) if known[r][d]==known[r][e]==1]
        need(len(common)<=1,'C0 distinct-pair condition')
        if not common:disjoint+=1;continue
        pairs.append([d,e,common[0]])
        for r in range(12,24):
            for s in range(24,36):
                values=[refs[r][d],refs[r][e],refs[s][d],refs[s][e]]
                need(all(x is False or type(x) is int for x in values),'only variables and forced zeros')
                zeros=[i for i,x in enumerate(values) if x is False]
                number=None
                if not zeros:
                    clause=[-v for v in values];need(len(set(clause))==4,'distinct quartet')
                    clauses.append(clause);number=212580+len(clauses)
                templates.append([d,e,r,s,values,zeros,number])
    need((len(pairs),disjoint,len(templates),len(clauses))==(540,1230,77760,43740),'frozen complete populations')
    return templates,clauses,pairs

def recipe_check(recipe,templates,clauses,pairs):
    need(recipe['templates']==templates,'complete ordered template mapping and every omission')
    need(recipe['C0_intersecting_pairs']==pairs,'all raw C0 intersections')
    need(recipe['base_variables']==61296 and recipe['retained_body_clause_count']==212580,'retained base dimensions')
    need(recipe['emitted_clauses']==len(clauses) and recipe['omitted_zero_tautologies']==len(templates)-len(clauses)==34020,'complete emitted/omitted populations')
    need(recipe['disjoint_C0_pair_count']==1230,'complete disjoint omission population')
    need(recipe['template_format']==['column_d','column_e','C1_row_r','C2_row_s','references_Crd_Cre_Csd_Cse','zero_reference_positions','emitted_absolute_clause_number_or_null'],'template schema')

def scope_check(scope,original,components):
    expected={**original,'schema':'FIXED_TRIANGLE_FULL_FACTOR_TARGET_COLUMN_CAP_SCOPE_V1',
      'original_scope_path':key(premise.base.D/'scope.json'),'original_scope_sha256':digest(premise.base.D/'scope.json'),
      'component_kernel_certificate':key(BASE/'kernel_certificate.json'),'component_kernel_certificate_sha256':digest(BASE/'kernel_certificate.json'),
      'components':components,'component_column_sum':2,'column_pair_overlap_upper_bound':2,'column_pair_count':1770,
      'target_implication':'Every target containing this fixed core can be relabeled to yield this factor with column caps.',
      'abstract_gram_implies_column_caps_claimed':False,'unrestricted_target_coverage':False,'residual_D_included':False,'target_automorphism_assumed':False}
    need(scope==expected,'complete exact extended scope')

def composition(base,suffix,complete):
    head,body=base.split(b'\n',1)
    need(head==b'p cnf 61296 212580','base header')
    need(complete==b'p cnf 61296 256320\n'+body+suffix,'exact complete base plus independently reconstructed suffix')

def mathematical_controls():
    records=[]
    for n in [4,6]:
        masks=[(1<<a)|(1<<b) for a,b in combinations(range(n),2) if b!=(a^1)]
        overlaps=[a&b for a,b in combinations(masks,2)]
        need(all(x.bit_count()<=1 for x in overlaps),'distinct two-subsets have at most one intersection')
        count=0
        for a,b,c in product(overlaps,repeat=3):
            direct=a.bit_count()+b.bit_count()+c.bit_count()<=2
            compact=(a==0) or all(not((b>>r&1) and (c>>s&1)) for r in range(n) for s in range(n))
            need(direct==compact,'complete small three-fibre relation');count+=1
        records.append(dict(coordinates=n,pairs=len(masks),triple_intersection_cases=count))
    for values in product([0,1],repeat=4):need(any(v==0 for v in values)==(sum(values)<4),'complete quartic clause truth table')
    need(0+2+1>2,'duplicate-column counterexample')
    return dict(complete_small_populations=records,quartic_truth_assignments=16,missing_distinctness_counterexample=[0,2,1])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        p=Path(p);value=digest(p);need(expected is None or value==expected,'hash '+str(p));bindings[key(p)]=value;return p
    def read(p,expected=None):return json.loads(bind(p,expected).read_bytes())
    try:
        gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_TRIANGLE_COMPONENT_FACTOR_CNF_ENCODING_PASS','independent base semantic gate')
        for p,value in gate['inputs_sha256'].items():bind(ROOT/p,value)
        summary=read(D/'summary.json',SUMMARY_SHA);manifest=read(D/'manifest.json')
        for p,value in manifest['inputs_sha256'].items():bind(ROOT/p,value)
        for p,record in summary['outputs'].items():need(bind(D/p,record['sha256']).stat().st_size==record['bytes'],'artifact byte length')
        original_scope=read(premise.base.D/'scope.json');original_model=read(premise.base.D/'model.json')
        h,g,columns,known,zeros,entries,refs=premise.base.scope_check(original_model,original_scope)
        components,contrasts=premise.kernel_check(read(BASE/'kernel_certificate.json'),h,g)
        old=read(BASE/'model.json');scope=read(D/'scope.json');model=read(D/'model.json');recipe=read(D/'clause_recipe.json')
        scope_check(scope,original_scope,components)
        templates,clauses,pairs=templates_from_raw(known,refs);recipe_check(recipe,templates,clauses,pairs)
        expected={**old,'schema':'FIXED_TRIANGLE_FULL_FACTOR_COLUMN_CAP_PREFIX_CNF_V1','scope_path':key(D/'scope.json'),'scope_sha256':digest(D/'scope.json'),
          'component_base_model_path':key(BASE/'model.json'),'component_base_model_sha256':digest(BASE/'model.json'),'component_base_cnf_sha256':digest(BASE/'instance.cnf'),
          'retained_component_base_clauses':212580,'column_cap_clauses':clauses,'column_cap_recipe_path':key(D/'clause_recipe.json'),'column_cap_recipe_sha256':digest(D/'clause_recipe.json'),
          'clauses':256320,'column_pair_overlap_upper_bound':2,'abstract_gram_implies_column_caps_claimed':False,'full_target_graph_encoded':False,'solver_calls':0}
        need(model==expected,'entire model exact base plus reconstructed extension')
        for field,p in [('base_cnf',BASE/'instance.cnf'),('base_model',BASE/'model.json'),('scope',D/'scope.json')]:
            need(recipe[field+'_path']==key(p) and recipe[field+'_sha256']==digest(p),'recipe exact '+field+' identity')
        suffix=b''.join((' '.join(map(str,c))+' 0\n').encode() for c in clauses)
        need((D/'column_caps.cnfpart').read_bytes()==suffix,'all independently derived suffix bytes')
        basebytes=(BASE/'instance.cnf').read_bytes();complete=(D/'instance.cnf').read_bytes();composition(basebytes,suffix,complete)
        rejected=[]
        def reject(name,fn):
            try:fn()
            except (ValueError,KeyError,IndexError):rejected.append(name)
            else:raise ValueError('corruption accepted '+name)
        for label in ['missing_template','wrong_reference','missing_zero','wrong_clause_position','wrong_disjoint_count']:
            bad=deepcopy(recipe)
            if label=='missing_template':bad['templates'].pop()
            elif label=='wrong_reference':next(t for t in bad['templates'] if t[6] is not None)[4][0]*=-1
            elif label=='missing_zero':next(t for t in bad['templates'] if t[5])[5]=[]
            elif label=='wrong_clause_position':next(t for t in bad['templates'] if t[6] is not None)[6]+=1
            else:bad['disjoint_C0_pair_count']-=1
            reject(label,lambda:recipe_check(bad,templates,clauses,pairs))
        for label,field,value in [('scope_target_coverage','unrestricted_target_coverage',True),('scope_abstract_implication','abstract_gram_implies_column_caps_claimed',True),('scope_cap','column_pair_overlap_upper_bound',3)]:
            bad=deepcopy(scope);bad[field]=value;reject(label,lambda:scope_check(bad,original_scope,components))
        for label,bad in [('wrong_header',complete.replace(b'61296 256320',b'61296 256319',1)),('lost_suffix_clause',complete[:-5]),('changed_body',complete.replace(b'1 ',b'-1 ',1))]:reject(label,lambda:composition(basebytes,suffix,bad))
        controls={**mathematical_controls(),'corrupt_controls_rejected':rejected};save(args.out/'controls.json',controls)
        packages=[]
        for package in read(D/'artifact_packages.json')['packages']:
            compressed=b''.join(bind(ROOT/part['path'],part['sha256']).read_bytes() for part in package['ordered_parts'])
            need(sha256(compressed).hexdigest()==package['compressed_stream_sha256'],'package compressed stream')
            raw=gzip.decompress(compressed);need(len(raw)==package['raw_bytes'] and sha256(raw).hexdigest()==package['raw_sha256']==digest(ROOT/package['raw_path']),'package exact recovery')
            packages.append(dict(path=package['raw_path'],sha256=package['raw_sha256'],bytes=len(raw)))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_TRIANGLE_FACTOR_COLUMN_CAPS.md']:bind(p)
        need(all(digest(ROOT/p)==value for p,value in bindings.items()),'stable frozen inputs')
        report=dict(status='INDEPENDENT_TRIANGLE_COLUMN_CAP_FACTOR_CNF_ENCODING_PASS',claim_id='C-FIXED-TRIANGLE-FULL-FACTOR-COLUMN-CAP-CNF',claim_revision=1,
          timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',verifier='/root/eight_domain_audit independent full template and byte checker',
          statement='The exact61296variable256320clause formula has exactly the binary36x60 factors of the saved fixed39core Gram with audited margins and all1770 distinct-column overlap bounds<=2. Every target containing that core yields such a factor after the audited C0 column relabelling.',
          dependencies=[dict(id='C-FIXED-TRIANGLE-COMPONENT-STRENGTHENED-CNF',revision=1,relation='encoding_equivalence'),dict(id='C-FIXED-TRIANGLE-FACTOR-COMPONENT-BALANCE',revision=1,relation='uses_result')],
          scope='One exact fixed39core; all C1 and C2 entries free subject to audited zero folds; residual D absent; no unrestricted core coverage.',variables=61296,clauses=256320,primary_entries=1200,retained_base_clauses=212580,new_clauses=43740,template_population=77760,fixedzero_tautologies=34020,column_pairs=1770,controls=controls,packages=packages,
          shared_components=['Frozen independent component-factor gate authenticates the complete preserved base body.','Independent raw-core and Gram constructor plus kernel checker reused with pinned source hashes.','New complete template, metadata and byte checker; no producer imports.'],
          limitations=['Column bounds are additional target-necessary restrictions, not claimed consequences of abstract Gram conditions.','A SAT factor need not extend to residual D or a target.','UNSAT needs a separate complete proof replay and excludes only this fixed-core family.'],solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e),inputs_sha256=bindings));raise

if __name__=='__main__':main()
