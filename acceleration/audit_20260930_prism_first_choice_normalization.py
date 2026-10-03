"""Independent complete relabelling action, coverage and exact one-unit CNF audit."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import permutations,product
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import time
import audit_20260930_prism_all_columns as base

ROOT=base.ROOT;D=ROOT/'acceleration/results/20260930_prism_first_choice_normalization'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json'
GATE_SHA='07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3'
need,digest,key,save=base.need,base.digest,base.key,base.save

def ah(values):return hashlib.sha256(json.dumps(values,separators=(',',':')).encode('ascii')).hexdigest()

def map_action(record,derived,model):
    h,k,components,labels,universe=derived
    p,e=record['component_permutation'],record['component_bit_flips']
    need(len(p)==len(e)==6 and p[:2]==[0,1]and sorted(p[2:])==[2,3,4,5]and e[:2]==[0,0]and all(type(v)is int and v in(0,1)for v in e),'explicit signed subgroup element')
    coordinate=[None]*12
    for a in range(6):
        images=[2*p[a],2*p[a]+1]
        if e[a]:images.reverse()
        coordinate[2*a:2*a+2]=images
    rowmap=[12*(r//12)+coordinate[r%12]for r in range(36)]
    fullmap=list(range(3))+[3+r for r in rowmap]
    need(record['coordinate_map']==coordinate and record['row_map']==rowmap,'explicit map convention old vertex to new vertex')
    need(sorted(fullmap)==list(range(39)),'full39 permutation')
    need(all(h[a][b]==h[fullmap[a]][fullmap[b]]for a,b in product(range(39),repeat=2)),'every raw39 edge preserved')
    need(all(k[a][b]==k[rowmap[a]][rowmap[b]]for a,b in product(range(36),repeat=2)),'every Gram entry preserved')
    index={tuple(pair):d for d,pair in enumerate(labels)}
    colmap=[index[tuple(sorted(coordinate[r]for r in pair))]for pair in labels]
    need(record['canonical_C0_column_map']==colmap and colmap[0]==0 and sorted(colmap)==list(range(60)),'canonical C0 old-to-new map')
    choices=model['choices'];lookup={(x['column'],tuple(x['rows'])):x['id']for x in choices}
    primary=[lookup[colmap[x['column']],tuple(sorted(rowmap[r]for r in x['rows']))]for x in choices]
    need(sorted(primary)==list(range(1,5761))and record['first_column_choice_map']==primary[:96],'full primary bijection and first-column restriction')
    need(record['primary_choice_map_sha256']==ah(primary),'bound whole primary map')
    return coordinate,rowmap,colmap,primary

def check_transports(raw,actions,choices):
    records=raw['transports'];need(len(records)==96 and sorted(r['source_choice_id']for r in records)==list(range(1,97)),'all96 distinct first-column sources')
    for record in records:
        source=record['source_choice_id'];need(type(source)is int and record['target_choice_id']==1,'exact normalized target')
        group_id=record['group_id'];need(type(group_id)is int and 0<=group_id<384,'valid group index')
        _,rows,columns,primary=actions[group_id]
        need(record['row_map']==rows and record['column_map']==columns and record['primary_choice_map']==primary,'raw transport equals full independently reconstructed group action')
        need(primary[source-1]==1 and columns[choices[source-1]['column']]==0,'source maps to choice1')
        need(sorted(rows[r]for r in choices[source-1]['rows'])==choices[0]['rows'],'literal first support transport')

def recipe_check(recipe):
    need(recipe['schema']=='SIX_PRISM_FIRST_CHOICE_NORMALIZATION_V1','recipe schema')
    need(recipe['variables']==245880 and recipe['clauses']==874801 and recipe['base_clauses']==874800,'exact dimensions')
    need(recipe['base_cnf']==key(base.D/'instance.cnf')and recipe['base_cnf_sha256']==digest(base.D/'instance.cnf'),'exact CNF premise')
    need(recipe['base_model']==key(base.D/'model.json')and recipe['base_model_sha256']==digest(base.D/'model.json'),'exact model premise')
    need(recipe['unit_clauses']==[[1]]and recipe['normalized_column']==0 and recipe['normalized_C0_pair']==[0,2]and recipe['normalized_choice_id']==1,'one positive first-choice unit')
    for field in ['target_automorphism_assumed','literal_auxiliary_permutation_claimed','residual_D_encoded','target_graph_encoded']:need(recipe[field]is False,'scope limitation '+field)

def byte_check(old,new):
    head,body=old.split(b'\n',1);need(head==b'p cnf 245880 874800','base header')
    need(new==b'p cnf 245880 874801\n'+body+b'1 0\n','byte-identical base body and exact sole unit')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        value=digest(p);need(expected is None or value==expected,'hash '+str(p));bindings[key(p)]=value;return p
    def read(p,expected=None):return json.loads(bind(p,expected).read_bytes())
    try:
        gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_SIX_PRISM_ALL_COLUMNS_CNF_ENCODING_PASS','base equation equivalence gate')
        for p,sha in gate['inputs_sha256'].items():bind(ROOT/p,sha)
        summary=read(D/'summary.json','0e916dce1fa9e011a30fe37eafbe0fe20ce3b7b5b97cc27bd305e4155466132e');manifest=read(D/'manifest.json')
        for source in [summary,manifest]:
            for p,sha in source['inputs_sha256'].items():bind(ROOT/p,sha)
        for p,record in summary['outputs'].items():need(bind(ROOT/p,record['sha256']).stat().st_size==record['bytes'],'output length')
        model=read(base.D/'model.json');derived=base.derive();equations=base.scope_check(model,derived)
        need(model['choices'][0]==dict(id=1,column=0,rows=[0,2,16,18,32,34]),'actual first-choice convention')
        raw=read(D/'group_actions.json');records=raw['actions']
        need(len(records)==384 and[r['group_id']for r in records]==list(range(384)),'384 distinct indexed actions')
        expected={(tuple([0,1,*p]),tuple([0,0,*e]))for p in permutations(range(2,6))for e in product((0,1),repeat=4)}
        observed={(tuple(r['component_permutation']),tuple(r['component_bit_flips']))for r in records}
        need(observed==expected,'complete explicit finite subgroup population')
        actions=[];equation_set={(frozenset(inputs),bound)for inputs,bound,_ in equations};need(len(equation_set)==540,'540 distinct abstract equations')
        for record in records:
            action=map_action(record,derived,model);actions.append(action);primary=action[3]
            images={(frozenset(primary[v-1]for v in inputs),bound)for inputs,bound,_ in equations}
            need(images==equation_set,'all540 equation images, including reverse coverage')
        coordinates={tuple(action[0]):i for i,action in enumerate(actions)}
        need(len(coordinates)==384 and tuple(range(12))in coordinates,'identity and distinct action population')
        inverse=[]
        for a in actions:
            inverse.append(coordinates[tuple(a[0].index(i)for i in range(12))])
            for b in actions:need(tuple(a[0][b[0][i]]for i in range(12))in coordinates,'complete group composition closure')
        need(raw['inverse_group_ids']==inverse and raw['full_group_order']==384,'exact inverse metadata')
        orbit=sorted({a[3][0]for a in actions});stabilizers=[i for i,a in enumerate(actions)if a[3][0]==1]
        need(orbit==raw['orbit_choice_ids']==list(range(1,97))and stabilizers==raw['stabilizer_of_choice1_group_ids']and len(stabilizers)==4,'complete orbit and stabilizer')
        transports=read(D/'coverage_transports.json');check_transports(transports,actions,model['choices'])
        recipe=read(D/'model.json');recipe_check(recipe)
        old=(base.D/'instance.cnf').read_bytes();new=(D/'instance.cnf').read_bytes();byte_check(old,new)
        rejected=[]
        def reject(label,fn):
            try:fn()
            except(ValueError,IndexError,KeyError):rejected.append(label)
            else:raise ValueError('accepted corruption '+label)
        for label in ['wrong_row_direction','duplicate_component','missing_flip','wrong_column','wrong_primary_hash']:
            bad=deepcopy(records[1])
            if label=='wrong_row_direction':bad['row_map'][4],bad['row_map'][5]=bad['row_map'][5],bad['row_map'][4]
            elif label=='duplicate_component':bad['component_permutation'][2]=bad['component_permutation'][3]
            elif label=='missing_flip':bad['component_bit_flips']=bad['component_bit_flips'][:-1]
            elif label=='wrong_column':bad['canonical_C0_column_map'][0]=1
            else:bad['primary_choice_map_sha256']='0'*64
            reject(label,lambda:map_action(bad,derived,model))
        for label in ['missing_source','wrong_transport_row','wrong_transport_variable','wrong_target']:
            bad=deepcopy(transports)
            if label=='missing_source':bad['transports'].pop()
            elif label=='wrong_transport_row':bad['transports'][1]['row_map'][4]^=1
            elif label=='wrong_transport_variable':bad['transports'][1]['primary_choice_map'][0]=0
            else:bad['transports'][0]['target_choice_id']=2
            reject(label,lambda:check_transports(bad,actions,model['choices']))
        for label,field,value in [('wrong_unit','unit_clauses',[[-1]]),('wrong_choice','unit_clauses',[[2]]),('wrong_base_hash','base_model_sha256','0'*64),('automorphism_premise','target_automorphism_assumed',True),('auxiliary_map_claim','literal_auxiliary_permutation_claimed',True)]:
            bad=deepcopy(recipe);bad[field]=value;reject(label,lambda:recipe_check(bad))
        for label,bad in [('missing_unit',new[:-4]),('negative_unit',new[:-4]+b'-1 0\n'),('wrong_header',new.replace(b'245880 874801',b'245880 874800',1)),('changed_base_byte',new.replace(b' 0\n',b' 1\n',1))]:reject(label,lambda:byte_check(old,bad))
        save(args.out/'controls.json',dict(identity_action_checked=True,complete_positive_transports=96,corrupted_controls_rejected=rejected))
        packages=[]
        for package in read(D/'artifact_packages.json')['packages']:
            data=b''.join(bind(ROOT/p['path'],p['sha256']).read_bytes()for p in package['ordered_parts'])
            need(hashlib.sha256(data).hexdigest()==package['compressed_stream_sha256'],'gzip stream');original=gzip.decompress(data)
            need(len(original)==package['raw_bytes']and hashlib.sha256(original).hexdigest()==package['raw_sha256']==digest(ROOT/package['raw_path']),'exact package recovery')
            packages.append(dict(path=package['raw_path'],sha256=package['raw_sha256'],bytes=len(original)))
        for p in[Path(__file__),ROOT/'docs/AUDIT_20260930_PRISM_FIRST_CHOICE_NORMALIZATION.md']:bind(p)
        need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),'stable inputs')
        report=dict(status='INDEPENDENT_SIX_PRISM_FIRST_CHOICE_NORMALIZATION_PASS',claim_id='C-SIX-PRISM-FIRST-CHOICE-NORMALIZATION-CNF',claim_revision=1,
          timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/state_literature_audit independent finite-action and exact-byte checker',recommendation='VERIFIED',review_state='CLEAR',kind='encoding',basis=['DERIVED','COMPUTED'],
          statement='For the frozen complete six-prism column-factor CNF, requiring primary choice1 in canonical C0 column{0,2} preserves satisfiability; the saved245880variable874801clause formula is exactly the base plus that unit. The explicit384relabellings form the stated group, act transitively on all96 first-column choices, and have a4element choice1 stabilizer.',
          scope='One fixed six-prism abstract Gram-factor family; finite specified relabelling group, not full automorphism-group census.',
          assumptions=['No nontrivial factor or target automorphism is assumed.','Canonical C0 and exact base prefix-counter semantics are the independently checked premises.'],
          dependencies=[dict(id='C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF',revision=1,relation='encoding_equivalence')],
          group_order=384,group_compositions=147456,primary_images_checked=384*5760,equation_images_checked=384*540,coverage_transports=96,orbit_size=96,stabilizer_size=4,variables=245880,clauses=874801,
          controls_rejected=rejected,packages=packages,derivation='docs/AUDIT_20260930_PRISM_FIRST_CHOICE_NORMALIZATION.md',
          shared_components=['Frozen own independent raw39/domain/equation constructor, pinned through base gate.','Python exact integer/finite-set arithmetic; no producer imports.'],
          limitations=['No literal permutation of prefix auxiliaries claimed; they have unique recomputed extensions.','Column caps and residual D remain omitted.','No factor or target graph is constructed.','No complete UNSAT proof or unrestricted target exclusion is checked.'],solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as error:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(error),inputs_sha256=bindings));raise
if __name__=='__main__':main()
