"""Independent scalar replay of NEW normalized full-model native artifacts.

No native producer imports or native execution. Reuses the independently
authored finite-control scalar checker, with its exact source hash disclosed.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from command_deadline import CommandDeadline
import audit_20261002_normalized_gf2_controls_v1 as independent

ROOT=independent.ROOT
MODEL='acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
MODEL_SHA='a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'
NORM='acceleration/results/20261002_independent_review/rooted8_row_content01/normalization_manifest.json'
NORM_SHA='47c9f0158084a1cf04b9ce2f84db93ee748e5e3226d759f276090aa50bdfe91c'
GATE='acceleration/results/20261002_independent_review/normalized_gf2_controls01/summary.json'
GATE_SHA='5f9fb0852f86491c628e0ba9ab6bc564f78bc06bfce0a7a0ea4b668241e589a1'
HELPER_SHA='675e393b8ba1cb20b78565b40cb6a478c96dc01e4a6b50de51f5272fb19bc3f0'
PROTOCOL=ROOT/'docs/AUDIT_20261002_NORMALIZED_GF2_FULL_ARTIFACT_PROTOCOL.md'


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary',type=Path,required=True);parser.add_argument('--summary-sha256',required=True)
    parser.add_argument('--input-case-sha256',required=True);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Complete85874math.gcd literal/parity roundtrips and3scalarfullvector passes or full23019column original-row XOR;260worker/300outer,no native solver')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};controls=[]
    def pin(path,wanted=None):
        path=Path(path);path=path if path.is_absolute()else ROOT/path
        need(path.resolve().is_relative_to(ROOT)and path.is_file(),'RAW_ARTIFACT_AVAILABILITY')
        need(deadline.status()['remaining_seconds']>20,'not completed within allocated budget')
        observed=independent.digest(path.read_bytes());need(wanted is None or observed==wanted,'ARTIFACT_SHA256 '+independent.key(path));pins[independent.key(path)]=observed;return path
    def rejected(label,call,wanted):
        try:call()
        except ValueError as error:need(str(error)==wanted,'CONTROL_DIAGNOSTIC_STAGE');controls.append({'label':label,'diagnostic':str(error)})
        else:raise ValueError('CORRUPTED_CONTROL_ACCEPTED '+label)
    try:
        pin(Path(independent.__file__),HELPER_SHA);pin(PROTOCOL);pin(__file__);pin(ROOT/'pyproject.toml');pin(ROOT/'uv.lock')
        gate=json.loads(pin(GATE,GATE_SHA).read_bytes());need(gate['status']=='INDEPENDENT_NORMALIZED_GF2_PRIMAL_XOR_CONTROLS_V1_PASS','ENGINEERING_GATE_STATUS')
        summary=json.loads(pin(args.summary,args.summary_sha256).read_bytes());run=summary['run'];code=run['actual_exit_code']
        need(summary['columns']==23019 and summary['rows']==85874 and code in (0,3,4),'EXACT_FROZEN_OUTPUT_UNIVERSE')
        for path,wanted in summary['inputs_sha256'].items():
            if path in gate['inputs_sha256']:need(wanted==gate['inputs_sha256'][path],'NEW_GATE_SOURCE_INPUT_BINDING')
            pin(path,wanted)
        receipt=json.loads(pin(run['receipt'],run['receipt_sha256']).read_bytes());need(receipt['actual_exit_code']==code and receipt['reaped'],'NATIVE_COMPLETED_RECEIPT')
        for name in ['stdout','stderr']:pin(receipt[name],receipt[name+'_sha256'])
        for path,record in run['artifacts'].items():need(pin(path,record['sha256']).stat().st_size==record['bytes'],'COMPLETE_NATIVE_ARTIFACT_SIZE')
        need((ROOT/receipt['stderr']).read_bytes()==b'','NATIVE_UNEXPECTED_STDERR')
        model=json.loads(pin(MODEL,MODEL_SHA).read_bytes());norm=json.loads(pin(NORM,NORM_SHA).read_bytes())
        case=json.loads(pin(args.summary.resolve().parent/'input_case.json',args.input_case_sha256).read_bytes())
        need(len(model['variables'])==case['columns']==norm['variables']==23019 and len(model['equations'])==case['rows']==norm['rows']==85874,'INPUT_CASE_COMPLETE_UNIVERSE')
        tiny={'variables':[0],'equations':[{'terms':[[0,2]],'rhs_affine':[2,0,0]},{'terms':[[0,4]],'rhs_affine':[4,0,0]}]}
        independent.check_vectors(tiny,[[1],[0],[0]])
        rejected('tiny_flipped_vector',lambda:independent.check_vectors(tiny,[[0],[0],[0]]),'PRIMAL_SCALAR_ROW')
        bad=json.loads(json.dumps(tiny));bad['equations'][0]['rhs_affine'][0]=4
        rejected('tiny_changed_RHS',lambda:independent.check_vectors(bad,[[1],[0],[0]]),'PRIMAL_SCALAR_ROW')
        bad=json.loads(json.dumps(tiny));bad['equations'][0]['terms'][0][1]=0
        rejected('tiny_changed_coefficient',lambda:independent.check_vectors(bad,[[1],[0],[0]]),'PRIMAL_SCALAR_ROW')
        inconsistent={'variables':[0],'equations':[{'terms':[[0,2]],'rhs_affine':[0,0,0]},{'terms':[[0,1]],'rhs_affine':[1,0,0]}]}
        relation={'format':'NORMALIZED_LITERAL_GF2_ROW_XOR_CANDIDATE_V1','matrix_rows':2,'matrix_columns':1,'original_row_indices':[0,1],'rhs_affine_mask':1}
        independent.check_relation(inconsistent,relation)
        rejected('tiny_changed_XORmask',lambda:independent.check_relation(inconsistent,dict(relation,rhs_affine_mask=2)),'XOR_SCALAR_ROW')
        parity_path=pin(case['sparse_rows'],case['sparse_rows_sha256']);need(independent.key(parity_path)==run['input'] and case['sparse_rows_sha256']==run['input_sha256'],'ACTUAL_NATIVE_INPUT_CASE_BINDING')
        normalized_path=pin(case['normalized_literal_rows'],case['normalized_literal_rows_sha256'])
        normalized_hash=hashlib.sha256();sparse_hash=hashlib.sha256();counts=Counter();first_nonzero_parity_column=None
        with normalized_path.open('rb')as normalized_stream,parity_path.open('rb')as sparse_stream:
            header=b'GF2_AFFINE_SPARSE_V1 23019 85874\n';need(sparse_stream.readline()==header,'PARITY_INPUT_HEADER');sparse_hash.update(header)
            for i,row in enumerate(model['equations']):
                if i%1024==0:need(deadline.status()['remaining_seconds']>20,'not completed within allocated budget')
                g,z=independent.normalized(row,23019);counts[g]+=1
                raw={'terms':row['terms'],'rhs_affine':row['rhs_affine']};encoded=independent.canonical(z)+b'\n';normalized_hash.update(encoded)
                need(normalized_stream.readline()==encoded,'EVERY_NORMALIZED_LITERAL_BYTE')
                coefficients=Counter()
                for j,c in z['terms']:coefficients[j]+=c
                indices=sorted(j for j,c in coefficients.items()if c%2);mask=sum((c%2)<<j for j,c in enumerate(z['rhs_affine']))
                if indices and first_nonzero_parity_column is None:first_nonzero_parity_column=indices[0]
                line=(str(mask)+' '+str(len(indices))+''.join(' '+str(j)for j in indices)+'\n').encode('ascii');sparse_hash.update(line)
                need(sparse_stream.readline()==line,'EVERY_PARITY_INPUT_BYTE')
                record={'original_row':i,'content':g,'raw_literal_sha256':independent.digest(independent.canonical(raw)),'normalized_literal_sha256':independent.digest(independent.canonical(z))}
                need(norm['records'][i]==record and case['records'][i]==dict(record,parity_row_sha256=independent.digest(line)),'EVERY_CONTENT_ROW_RECORD')
            need(normalized_stream.read()==sparse_stream.read()==b'','EXACT_INPUT_STREAM_END')
        need(normalized_hash.hexdigest()==norm['normalized_literal_jsonl_sha256']==case['normalized_literal_jsonl_sha256'] and sparse_hash.hexdigest()==run['input_sha256'],'COMPLETE_NORMALIZATION_PARITY_HASH')
        need({str(k):v for k,v in counts.items()}==case['content_counts']==norm['content_counts'],'COMPLETE_CONTENT_CENSUS')
        result={}
        directory=ROOT/Path(next(iter(run['artifacts']))).parent if run['artifacts']else None
        if code==0:
            vectors=independent.read_vectors(directory,23019);independent.check_vectors(model,vectors)
            need((directory/'row_residuals.bin').read_bytes()==bytes(85874),'ALL_NATIVE_RESIDUAL_BYTES')
            need(first_nonzero_parity_column is not None,'ACTUAL_COORDINATE_CONTROL_COLUMN')
            corrupt=[list(v)for v in vectors];corrupt[0][first_nonzero_parity_column]^=1
            rejected('actual_full_vector_coordinate_flip',lambda:independent.check_vectors(model,corrupt),'PRIMAL_SCALAR_ROW')
            result={'status':'INDEPENDENT_NORMALIZED_GF2_THREE_FULL_PRIMALS_PASS','three_vectors_each_raw_rows_checked':85874,
                'full_scalar_row_component_checks':3*85874,'actual_corrupt_column':first_nonzero_parity_column,
                'literal_mod2_consistency':True,'integer_nonnegative_feasibility':None,'integer_nonnegative_feasibility_null_reason':'Modulo2 solutions certify only literal parity consistency.',
                'profile_parity_population':{'all210_integer_profiles_mod2_consistent':True,'selection':'a0..20,b0..9; all4parity combinations induced by threeaffine vectors'},'primal_hashes':{label:independent.digest((directory/('x_'+label+'.bits')).read_bytes())for label in ['const','a','b']}}
        elif code==3:
            relation=json.loads((directory/'xor_original_row_indices.json').read_bytes());diagnostics=independent.check_relation(model,relation)
            rejected('actual_XOR_affine_mask_flip',lambda:independent.check_relation(model,dict(relation,rhs_affine_mask=relation['rhs_affine_mask']^1)),'XOR_SCALAR_ROW')
            mask=relation['rhs_affine_mask'];outcomes=[{'a':a,'b':b,'relation_rhs_mod2':((mask&1)+((mask>>1)&1)*a+((mask>>2)&1)*b)%2}for a in range(21)for b in range(10)]
            independent.dump(out/'all210_relation_outcomes.json',outcomes);independent.dump(out/'full_XOR_integer_diagnostics.json',diagnostics)
            result={'status':'INDEPENDENT_NORMALIZED_LITERAL_GF2_ORIGINAL_ROW_XOR_PASS','full_original_columns_checked':23019,'selected_original_rows_checked':len(relation['original_row_indices']),
                'rhs_affine_mask':mask,'literal_profile_points_excluded':sum(r['relation_rhs_mod2']for r in outcomes),'frozen_integer_profile_population':210,
                'claim_scope':'One exact original-row relation excludes only listed literal profile points; necessary graph interpretation remains conditional on UNKNOWN prismabsence and prior independent root8 encoding coverage.',
                'complete_modular_restrictions':False,'xor_witness_sha256':independent.digest((directory/'xor_original_row_indices.json').read_bytes())}
        else:
            result={'status':'INCOMPLETE_NORMALIZED_NATIVE_ARTIFACT_INPUT_IDENTITY_CHECKED','unfinished_description':'not completed within allocated budget',
                'unmet_requirements':['No complete3vectors or original-row XOR supplied; no modular consistency/exclusion check possible.'],'resume_checkpoint':summary.get('resume_checkpoint'),
                'automatic_resume':False}
        result.update({'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python_version':platform.python_version(),'inputs_sha256':pins,'controls':controls,
            'verifier':'/root/structural','producer':'/root/native_driver','checking_method':'Independent math.gcd content/byte/hash reconstruction then raw integer scalar sums; no producer imports, native execution or packed arithmetic.',
            'shared_trusted_components':['Independent finite-control scalar helper pinned675e393b...bc3f0','command_deadline.py','run_compute_command.py','Python standard library/locked environment','Raw model produced by structural, with separate complete encoding/catalogue audit by checkpoint_audit'],
            'rows_normalization_checked':85874,'normalized_stream_sha256':normalized_hash.hexdigest(),'sparse_stream_sha256':sparse_hash.hexdigest(),
            'rank_claim':False,'target_resolution':False,'external_review':None,'external_review_null_reason':'Internal independent artifact check only.','elapsed_seconds':time.monotonic()-started})
        independent.dump(out/'summary.json',result)
    except BaseException as error:
        independent.dump(out/'failure.json',{'error':repr(error),'inputs_sha256':pins,'elapsed_seconds':time.monotonic()-started,'outputs_preserved':True,'approval':False});raise


if __name__=='__main__':main()
