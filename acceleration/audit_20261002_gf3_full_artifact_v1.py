"""Independent exact ORIGINAL literal GF3 endpoint checker and calibration.

No producer/packed solver imports. Content normalization is identity evidence;
all primal or relation sums use original signed integer coefficients.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from command_deadline import CommandDeadline
import audit_20261002_gf3_scalar_v1 as S

ROOT=S.ROOT
HELPER_SHA='698eb9bbe8b1ba6a257e8e6226a9e49517e17e966ce64afb11b98d17be08bafa'
CAL=ROOT/'acceleration/results/20261002_independent_review/gf3_scalar_calibration01/summary.json'
CAL_SHA='8948291c910fe4532024ce883fc0a030a3db32a0c5042e226683dbe9ba308632'
PROTOCOL=ROOT/'docs/AUDIT_20261002_GF3_FULL_ARTIFACT_PROTOCOL.md'
MODEL=ROOT/'acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
MODEL_SHA='a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'
CONTROLS=ROOT/'acceleration/results/20261002_rooted8_gf3_controls02/controls_manifest.json'
CONTROLS_SHA='f4e1b7330264015cee18992c08f5a7573ca44468236128a9ad5e00a87f0c4b6a'


def encoded_row(row,n):
    content,raw=S.row_data(row,n);_,divided=S.row_data(row,n,'divided')
    coefficients=Counter()
    for j,c in raw['terms']:coefficients[j]+=c
    terms=[[j,c%3]for j,c in sorted(coefficients.items())if c%3]
    line=(' '.join(map(str,[*[c%3 for c in raw['rhs_affine']],len(terms),*[v for term in terms for v in term]]))+'\n').encode('ascii')
    return content,raw,divided,line


def check_input_case(model,case,pin,tick):
    n=len(model['variables']);m=len(model['equations']);counts=Counter();digest=hashlib.sha256()
    S.require(case['schema']=='ORIGINAL_LITERAL_GF3_INPUT_CASE_V1'and(case['columns'],case['rows'])==(n,m)and len(case['records'])==m,'ENDPOINT_INPUT_DIMENSIONS')
    normalized=pin(case['normalized_literal_rows'],case['normalized_literal_rows_sha256'])
    sparse=pin(case['sparse_rows'],case['sparse_rows_sha256'])
    with normalized.open('rb')as norm,sparse.open('rb')as modular:
        S.require(modular.readline()==f'GF3_AFFINE_SPARSE_V1 {n} {m}\n'.encode('ascii'),'ENDPOINT_SPARSE_HEADER')
        for i,row in enumerate(model['equations']):
            if not i%256:tick()
            g,raw,new,line=encoded_row(row,n);counts[g]+=1
            normalized_line=S.literal(new)+b'\n';digest.update(normalized_line)
            S.require(norm.readline()==normalized_line,'ENDPOINT_NORMALIZED_LITERAL_BYTES')
            S.require(modular.readline()==line,'ENDPOINT_ORIGINAL_MOD3_ROW_BYTES')
            record=dict(original_row=i,content=g,raw_literal_sha256=hashlib.sha256(S.literal(raw)).hexdigest(),normalized_literal_sha256=hashlib.sha256(S.literal(new)).hexdigest(),original_mod3_row_sha256=hashlib.sha256(line).hexdigest())
            S.require(case['records'][i]==record,'ENDPOINT_ORIGINAL_LITERAL_RECORD')
        S.require(norm.read(1)==modular.read(1)==b'','ENDPOINT_STREAM_TRAILING')
    S.require(case['content_counts']=={str(k):v for k,v in counts.items()}and case['normalized_literal_jsonl_sha256']==digest.hexdigest(),'ENDPOINT_FULL_CONTENT_CENSUS')
    S.require(case['raw_divided_mod3_equivalent']==all(g%3!=0 for g in counts),'ENDPOINT_CONTENT3_SCOPE')
    return dict(rows=m,columns=n,content_counts={str(k):v for k,v in counts.items()},normalized_literal_jsonl_sha256=digest.hexdigest(),raw_divided_mod3_equivalent=all(g%3!=0 for g in counts))


def check_primals(model,vectors,tick):
    n=len(model['variables']);S.require(len(vectors)==3 and all(len(v)==n and all(type(c)is int and c in (0,1,2)for c in v)for v in vectors),'ENDPOINT_COMPLETE_TERNARY_VECTORS')
    for i,row in enumerate(model['equations']):
        if not i%256:tick()
        _,raw=S.row_data(row,n)
        for component,vector in enumerate(vectors):
            S.require((sum(c*vector[j]for j,c in raw['terms'])-raw['rhs_affine'][component])%3==0,'ENDPOINT_ORIGINAL_PRIMAL_SCALAR_ROW')
    return dict(complete_vectors=3,scalar_raw_row_component_checks=3*len(model['equations']))


def check_relation(model,relation,tick):
    tick();S.require(relation['format']=='ORIGINAL_LITERAL_GF3_ROW_RELATION_CANDIDATE_V1'and(relation['matrix_rows'],relation['matrix_columns'])==(len(model['equations']),len(model['variables'])),'ENDPOINT_RELATION_DIMENSIONS')
    return S.scalar_relation(model,relation['original_row_coefficients'],relation['rhs_affine_residue'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['calibrate','check']);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    for name in ['summary','input-case','calibration']:ap.add_argument('--'+name,type=Path);ap.add_argument('--'+name+'-sha256')
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Independent GF3 endpoint calibration or all85874 original rows/23019 columns;300outer260worker40reserve, no native solver')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};negatives=[]
    def tick():S.require(not deadline.status()['stop_required'],'ENDPOINT_DEADLINE')
    def pin(path,wanted=None):
        tick();path=Path(path);path=path if path.is_absolute()else ROOT/path;digest=S.sha(path)
        S.require(wanted is None or digest==wanted,'ENDPOINT_INPUT_HASH '+str(path));pins[path.relative_to(ROOT).as_posix()]=digest;return path
    def reject(label,call,wanted):
        try:call()
        except ValueError as error:S.require(str(error)==wanted,'ENDPOINT_CORRUPTION_STAGE '+label);negatives.append(dict(label=label,diagnostic=str(error)))
        else:raise ValueError('ENDPOINT_CORRUPTION_ACCEPTED '+label)
    try:
        for path in [Path(__file__),PROTOCOL,ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(path)
        pin(Path(S.__file__),HELPER_SHA);cal=json.loads(pin(CAL,CAL_SHA).read_bytes());S.require(cal['status']=='INDEPENDENT_ORIGINAL_GF3_SCALAR_CHECKER_CALIBRATION_V1_PASS','ENDPOINT_HELPER_CALIBRATION')
        if args.mode=='calibrate':
            controls=json.loads(pin(CONTROLS,CONTROLS_SHA).read_bytes());reports={}
            for label in ['singular','fullrank','inconsistent','multiword','divided_scope_control']:
                record=controls['cases'][label];model=json.loads(pin(record['raw_model'],record['raw_model_sha256']).read_bytes());case=json.loads(pin(record['input_case'],record['input_case_sha256']).read_bytes())
                report=check_input_case(model,case,pin,tick)
                directory=CONTROLS.parent/(label+'_whole')
                if label=='inconsistent':
                    relation=json.loads(pin(directory/'original_row_relation.json').read_bytes());report['relation']=check_relation(model,relation,tick)
                    changed=deepcopy(relation);changed['original_row_coefficients'][0][1]=3-changed['original_row_coefficients'][0][1]
                    reject('relation_weight',lambda:check_relation(model,changed,tick),'GF3_ORIGINAL_ROW_RELATION_SCALAR')
                    changed=deepcopy(relation);changed['rhs_affine_residue'][0]=(changed['rhs_affine_residue'][0]+1)%3
                    reject('relation_RHS',lambda:check_relation(model,changed,tick),'GF3_ORIGINAL_ROW_RELATION_SCALAR')
                    changed=deepcopy(relation);changed['matrix_columns']+=1
                    reject('relation_dimensions',lambda:check_relation(model,changed,tick),'ENDPOINT_RELATION_DIMENSIONS')
                else:
                    for component in ['const','a','b']:pin(directory/('x_'+component+'.trits'))
                    vectors=S.read_vectors(directory,len(model['variables']));report.update(check_primals(model,vectors,tick))
                reports[label]=report
            record=controls['cases']['fullrank'];model=json.loads((ROOT/record['raw_model']).read_bytes());case=json.loads((ROOT/record['input_case']).read_bytes());vectors=S.read_vectors(CONTROLS.parent/'fullrank_whole',4)
            changed=deepcopy(vectors);changed[0][0]=(changed[0][0]+1)%3
            reject('vector_coordinate',lambda:check_primals(model,changed,tick),'ENDPOINT_ORIGINAL_PRIMAL_SCALAR_ROW')
            changed=deepcopy(vectors);changed[0].pop()
            reject('vector_truncated',lambda:check_primals(model,changed,tick),'ENDPOINT_COMPLETE_TERNARY_VECTORS')
            changed=deepcopy(vectors);changed[0][0]=3
            reject('vector_nontrit',lambda:check_primals(model,changed,tick),'ENDPOINT_COMPLETE_TERNARY_VECTORS')
            changed=deepcopy(model);changed['equations'][0]['terms'][0][1]*=-1
            reject('coefficient_sign',lambda:check_primals(changed,vectors,tick),'ENDPOINT_ORIGINAL_PRIMAL_SCALAR_ROW')
            changed=deepcopy(model);changed['equations'][0]['rhs_affine'][0]+=1
            reject('raw_affine_RHS',lambda:check_primals(changed,vectors,tick),'ENDPOINT_ORIGINAL_PRIMAL_SCALAR_ROW')
            changed=deepcopy(case);changed['records'][0]['content']+=1
            reject('literal_content_record',lambda:check_input_case(model,changed,pin,tick),'ENDPOINT_ORIGINAL_LITERAL_RECORD')
            changed=deepcopy(case);changed['records'].pop()
            reject('missing_raw_row_record',lambda:check_input_case(model,changed,pin,tick),'ENDPOINT_INPUT_DIMENSIONS')
            changed=deepcopy(case);changed['content_counts']['2']+=1
            reject('content_census',lambda:check_input_case(model,changed,pin,tick),'ENDPOINT_FULL_CONTENT_CENSUS')
            changed=deepcopy(case);changed['normalized_literal_jsonl_sha256']='0'*64
            reject('normalized_stream_digest',lambda:check_input_case(model,changed,pin,tick),'ENDPOINT_FULL_CONTENT_CENSUS')
            record=controls['cases']['singular'];raw=json.loads((ROOT/record['raw_model']).read_bytes());rawcase=json.loads((ROOT/record['input_case']).read_bytes());rawvectors=S.read_vectors(CONTROLS.parent/'singular_whole',4)
            reject('raw_primal_on_divided_content3',lambda:check_primals(dict(variables=raw['variables'],equations=[S.row_data(r,4,'divided')[1]for r in raw['equations']]),rawvectors,tick),'ENDPOINT_ORIGINAL_PRIMAL_SCALAR_ROW')
            changed=deepcopy(rawcase);changed['raw_divided_mod3_equivalent']=True
            reject('content3_false_equivalence',lambda:check_input_case(raw,changed,pin,tick),'ENDPOINT_CONTENT3_SCOPE')
            result=dict(status='INDEPENDENT_GF3_LITERAL_ENDPOINT_CHECKER_CALIBRATION_V1_PASS',calibration_cases=reports,negative_controls=negatives,full_scientific_output_inspected=False,scientific_GF3_launched=False,scope='New endpoint original-row checking code exercised on all five tiny/control operators, four complete primal artifact sets and one relation. No full scientific verdict.')
        else:
            S.require(all([args.summary,args.summary_sha256,args.input_case,args.input_case_sha256,args.calibration,args.calibration_sha256]),'ENDPOINT_REQUIRED_PINS')
            calibration=json.loads(pin(args.calibration,args.calibration_sha256).read_bytes())
            S.require(calibration['status']=='INDEPENDENT_GF3_LITERAL_ENDPOINT_CHECKER_CALIBRATION_V1_PASS'and calibration['inputs_sha256'][Path(__file__).resolve().relative_to(ROOT).as_posix()]==S.sha(__file__),'ENDPOINT_EXACT_CHECKER_CALIBRATION')
            model=json.loads(pin(MODEL,MODEL_SHA).read_bytes());S.require(len(model['variables'])==23019 and len(model['equations'])==85874,'ENDPOINT_FROZEN_FULL_DIMENSIONS')
            summary=json.loads(pin(args.summary,args.summary_sha256).read_bytes());case=json.loads(pin(args.input_case,args.input_case_sha256).read_bytes())
            S.require(summary['status']=='ORIGINAL_LITERAL_GF3_OUTPUT_CANDIDATE_PENDING_INDEPENDENT_CHECK','ENDPOINT_PRODUCER_SUMMARY_KIND')
            for path,wanted in summary['inputs_sha256'].items():pin(path,wanted)
            census=check_input_case(model,case,pin,tick);run=summary['run'];pin(run['input'],run['input_sha256'])
            receipt=json.loads(pin(run['receipt'],run['receipt_sha256']).read_bytes());code=run['actual_exit_code']
            S.require(code==receipt['actual_exit_code']and receipt['reaped']is True,'ENDPOINT_RECEIPT_OUTCOME')
            artifact_availability={}
            for path,record in run['artifacts'].items():
                artifact=pin(path,record['sha256']);S.require(artifact.stat().st_size==record['bytes'],'ENDPOINT_ARTIFACT_BYTES')
                artifact_availability[path]=dict(sha256=record['sha256'],bytes=record['bytes'],availability='LOCAL_ONLY',role='Resume state, hash identity only; not mathematical certificate'if artifact.name=='checkpoint.bin'else'Frozen raw output; publication availability tracked separately')
            if code==0:
                descriptors=summary['primal_vectors'];S.require([r['label']for r in descriptors]==['const','a','b'],'ENDPOINT_PRIMAL_POPULATION')
                directories=[]
                for record in descriptors:
                    path=pin(record['path'],record['sha256']);S.require(record['trits']==23019,'ENDPOINT_PRIMAL_DIMENSIONS');directories.append(path.parent)
                S.require(len(set(directories))==1,'ENDPOINT_PRIMAL_DIRECTORY')
                vectors=S.read_vectors(directories[0],23019);literal_result=check_primals(model,vectors,tick)
                changed=deepcopy(vectors);changed[0][0]=(changed[0][0]+1)%3
                reject('full_actual_vector_coordinate',lambda:check_primals(model,changed,tick),'ENDPOINT_ORIGINAL_PRIMAL_SCALAR_ROW')
                result=dict(status='INDEPENDENT_ORIGINAL_LITERAL_GF3_THREE_PRIMALS_V1_PASS',literal_result=literal_result,profile_domain=dict(a=list(range(21)),b=list(range(10)),population=210,unit='conditional rooted-six parameter pairs',literal_mod3_compatible_profiles=210,excluded_profiles=0),primal_vectors=descriptors)
            elif code==3:
                record=summary['coefficient_relation'];relation=json.loads(pin(record['path'],record['sha256']).read_bytes());literal_result=check_relation(model,relation,tick);residue=relation['rhs_affine_residue']
                incompatible=[[a,b]for a in range(21)for b in range(10)if(residue[0]+a*residue[1]+b*residue[2])%3]
                result=dict(status='INDEPENDENT_ORIGINAL_LITERAL_GF3_ROW_RELATION_V1_PASS',literal_result=literal_result,original_row_relation=record,affine_profile_scalar_incompatibilities=incompatible,scope_note='Literal finite-field relation only. Necessary model and conditional profile coverage must be bound separately for any integer exclusion.')
            else:
                S.require(code==4,'ENDPOINT_UNRECOGNIZED_EXIT');result=dict(status='INDEPENDENT_ORIGINAL_LITERAL_GF3_UNFINISHED_OUTPUT_RECORDED',unfinished_description='not completed within allocated budget',mathematical_certificate_checked=False)
            result.update(input_case_census=census,artifact_availability=artifact_availability,negative_controls=negatives,scope='Exact ORIGINAL signed literal operator modulo3 only. No rank, nonnegativity, integer feasibility or graph realization. Unrestricted target does not follow from UNKNOWN global prism absence.')
        result.update(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),verifier='/root/structural',command=[sys.executable,*sys.argv],cwd=str(ROOT),python_version=platform.python_version(),inputs_sha256=pins,shared_components=['Separate independently calibrated scalar helper','command_deadline; no producer imports'],elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),rank_claim=False,target_resolution=False)
        S.save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],sha256=S.sha(out/'summary.json'),summary=str((out/'summary.json').relative_to(ROOT)))))
    except BaseException as error:S.save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,negative_controls=negatives,elapsed_seconds=time.monotonic()-started,outputs_preserved=True));raise


if __name__=='__main__':main()
