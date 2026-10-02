"""Independent GF3 finite native controls, original rows and weighted checkpoints.

Imports only the separately authored/calibrated scalar checker and deadline.
Does not execute or import the producer, and does not approve a full model run.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time

from command_deadline import CommandDeadline
import audit_20261002_gf3_scalar_v1 as S

ROOT=S.ROOT
BASE=ROOT/'acceleration/results/20261002_rooted8_gf3_controls02'
MANIFEST=BASE/'controls_manifest.json'
MANIFEST_SHA='f4e1b7330264015cee18992c08f5a7573ca44468236128a9ad5e00a87f0c4b6a'
CAL=ROOT/'acceleration/results/20261002_independent_review/gf3_scalar_calibration01/summary.json'
CAL_SHA='8948291c910fe4532024ce883fc0a030a3db32a0c5042e226683dbe9ba308632'
HELPER_SHA='698eb9bbe8b1ba6a257e8e6226a9e49517e17e966ce64afb11b98d17be08bafa'
PROTOCOL=ROOT/'docs/AUDIT_20261002_GF3_NATIVE_CONTROLS_PROTOCOL.md'
NEG={
    'reject_column':'sparse ordered column range',
    'reject_coefficient':'sparse coefficient trit',
    'reject_rhs':'sparse rhs trit',
    'reject_duplicate':'sparse ordered column range',
    'reject_checkpoint_hash':'checkpoint exact input hash',
    'reject_checkpoint_rhs':'checkpoint rhs trit',
    'reject_checkpoint_origin_scale':'checkpoint origin scale',
    'reject_checkpoint_plane':'checkpoint disjoint planes',
    'reject_checkpoint_leading':'checkpoint leading one',
    'reject_checkpoint_padding':'checkpoint padding bits',
    'reject_checkpoint_dag_weight':'checkpoint DAG coefficient'}


def dense_row(row,n):
    _,raw=S.row_data(row,n);lhs=[0]*n
    for j,c in raw['terms']:lhs[j]=(lhs[j]+c)%3
    return lhs,[c%3 for c in raw['rhs_affine']]


def checkpoint(raw,model,input_sha):
    """Unpack without producer helpers; rederive every saved weighted basis row."""
    n=len(model['variables']);m=len(model['equations']);pos=0;locations={}
    def take(length):
        nonlocal pos
        S.require(pos+length<=len(raw),'CP_TRUNCATION');chunk=raw[pos:pos+length];pos+=length;return chunk
    def uint64():return struct.unpack('<Q',take(8))[0]
    S.require(take(17)==b'GF3_PRIMAL_CP_V1\n','CP_MAGIC')
    S.require(take(64)==input_sha.encode('ascii'),'CP_HASH')
    dimensions=[uint64()for _ in range(4)];cn,cm,words,processed=dimensions
    S.require((cn,cm,words)==(n,m,(n+63)//64)and processed<=m,'CP_DIMENSIONS')
    bases={}
    for p in range(n):
        present=take(1)[0];S.require(present in (0,1),'CP_PRESENCE')
        if not present:continue
        rhs=list(take(3));S.require(all(c in (0,1,2)for c in rhs),'CP_RHS')
        scale=take(1)[0];S.require(scale in (1,2),'CP_ORIGIN_SCALE')
        origin,order,depcount=[uint64()for _ in range(3)]
        S.require(origin<processed and order<n and depcount<=n,'CP_ORIGIN_ORDER')
        deps=[];dep_offsets=[]
        for _ in range(depcount):
            j=struct.unpack('<I',take(4))[0];dep_offsets.append(pos);weight=take(1)[0]
            S.require(j<n and weight in (1,2),'CP_DAG_WEIGHT');deps.append([j,weight])
        S.require([j for j,w in deps]==sorted(set(j for j,w in deps)),'CP_DAG_ORDER')
        one_offset=pos;one=[uint64()for _ in range(words)];two=[uint64()for _ in range(words)]
        S.require(not any(a&b for a,b in zip(one,two)),'CP_PLANES')
        vector=[((one[j//64]>>(j%64))&1)+2*((two[j//64]>>(j%64))&1)for j in range(words*64)]
        S.require(not any(vector[n:]),'CP_PADDING')
        S.require(vector[p]==1 and not any(vector[:p]),'CP_LEADING')
        bases[p]={'lhs':vector[:n],'rhs':rhs,'origin':origin,'order':order,'scale':scale,'deps':deps}
        locations[p]={'one_offset':one_offset,'dep_offsets':dep_offsets}
    S.require(pos==len(raw),'CP_TRAILING')
    order=sorted(bases,key=lambda p:bases[p]['order'])
    S.require([bases[p]['order']for p in order]==list(range(len(order))),'CP_ORDER_BIJECTION')
    for p in order:
        b=bases[p];lhs,rhs=dense_row(model['equations'][b['origin']],n)
        lhs=[b['scale']*v%3 for v in lhs];rhs=[b['scale']*v%3 for v in rhs]
        for q,w in b['deps']:
            S.require(q in bases and bases[q]['order']<b['order'],'CP_DAG_PRECEDENCE')
            lhs=[(v+w*z)%3 for v,z in zip(lhs,bases[q]['lhs'])]
            rhs=[(v+w*z)%3 for v,z in zip(rhs,bases[q]['rhs'])]
        S.require(lhs==b['lhs']and rhs==b['rhs'],'CP_RAW_DAG_IDENTITY')
    # Reverse inclusion: every completed original row belongs to saved row space.
    for row in model['equations'][:processed]:
        lhs,rhs=dense_row(row,n)
        for p in sorted(bases):
            w=lhs[p]
            if w:
                lhs=[(v-w*z)%3 for v,z in zip(lhs,bases[p]['lhs'])]
                rhs=[(v-w*z)%3 for v,z in zip(rhs,bases[p]['rhs'])]
        S.require(not any(lhs)and not any(rhs),'CP_PREFIX_ROWSPACE')
    if n<=6:
        original={'variables':list(range(n)),'equations':model['equations'][:processed]}
        basis_model={'variables':list(range(n)),'equations':[{'terms':[[j,c]for j,c in enumerate(b['lhs'])if c],'rhs_affine':b['rhs']}for b in bases.values()]}
        S.require(S.domains(original)==S.domains(basis_model),'CP_EXHAUSTIVE_PREFIX_DOMAIN')
    return {'processed':processed,'basis_rows':len(bases),'n':n,'m':m},locations


def fixtures():
    singular=S.fixture();full=deepcopy(singular)
    full['equations'] += [dict(terms=[[0,1],[2,1]],rhs_affine=[0,2,1]),dict(terms=[[3,4]],rhs_affine=[0,0,0])]
    bad=deepcopy(singular);bad['equations'][2]['rhs_affine'][0]=3
    mapping={0:0,1:63,2:64,3:129}
    multi={'variables':list(range(130)),'equations':[dict(terms=[[mapping[j],c]for j,c in r['terms']],rhs_affine=r['rhs_affine'][:])for r in full['equations']]}
    multi['equations'].append(dict(terms=[[65,2],[127,1]],rhs_affine=[0,0,0]))
    divided={'variables':list(range(4)),'equations':[S.row_data(r,4,'divided')[1]for r in singular['equations']]}
    return dict(singular=singular,fullrank=full,inconsistent=bad,multiword=multi,divided_scope_control=divided)


def audit_case(model,case,pin):
    n=len(model['variables']);m=len(model['equations']);records=[];stream=b'';counts=Counter()
    sparse=S.sparse_bytes(model);lines=sparse.splitlines(keepends=True)
    for index,row in enumerate(model['equations']):
        g,raw=S.row_data(row,n);_,divided=S.row_data(row,n,'divided');counts[g]+=1
        stream+=S.literal(divided)+b'\n'
        records.append(dict(original_row=index,content=g,raw_literal_sha256=hashlib.sha256(S.literal(raw)).hexdigest(),normalized_literal_sha256=hashlib.sha256(S.literal(divided)).hexdigest(),original_mod3_row_sha256=hashlib.sha256(lines[index+1]).hexdigest()))
    S.require(case['schema']=='ORIGINAL_LITERAL_GF3_INPUT_CASE_V1'and(case['columns'],case['rows'])==(n,m),'CASE_DIMENSIONS')
    S.require(case['records']==records and case['content_counts']=={str(k):v for k,v in counts.items()},'CASE_FULL_LITERAL_RECORDS')
    S.require(pin(case['normalized_literal_rows'],case['normalized_literal_rows_sha256']).read_bytes()==stream,'CASE_NORMALIZED_FULL_BYTES')
    S.require(case['normalized_literal_jsonl_sha256']==hashlib.sha256(stream).hexdigest(),'CASE_NORMALIZED_HASH')
    S.require(pin(case['sparse_rows'],case['sparse_rows_sha256']).read_bytes()==sparse,'CASE_ORIGINAL_MOD3_FULL_BYTES')
    S.require(case['raw_divided_mod3_equivalent']==all(g%3 for g in counts),'CASE_NONUNIT_SCOPE')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='25 finite native calls,99 arithmetic records,13 tiny weighted checkpoints;300outer260worker40reserve;no scientific solver')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};checks=[];negatives=[]
    def pin(path,wanted=None):
        S.require(not deadline.status()['stop_required'],'AUDIT_DEADLINE');path=Path(path);path=path if path.is_absolute()else ROOT/path
        digest=S.sha(path);S.require(wanted is None or digest==wanted,'AUDIT_INPUT_HASH '+str(path));pins[path.relative_to(ROOT).as_posix()]=digest;return path
    def reject(label,call,wanted):
        try:call()
        except ValueError as error:S.require(str(error)==wanted,'AUDIT_NEGATIVE_STAGE '+label);negatives.append(dict(label=label,diagnostic=str(error)))
        else:raise ValueError('AUDIT_CORRUPT_ACCEPTED '+label)
    try:
        pin(Path(S.__file__),HELPER_SHA);cal=json.loads(pin(CAL,CAL_SHA).read_bytes());S.require(cal['status']=='INDEPENDENT_ORIGINAL_GF3_SCALAR_CHECKER_CALIBRATION_V1_PASS','SCALAR_CALIBRATION')
        for path in [Path(__file__),PROTOCOL,ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(path)
        manifest=json.loads(pin(MANIFEST,MANIFEST_SHA).read_bytes())
        for path,wanted in manifest['inputs_sha256'].items():pin(path,wanted)
        models=fixtures();case_reports={}
        S.require(set(manifest['cases'])==set(models),'CASE_POPULATION')
        for name,record in manifest['cases'].items():
            actual=json.loads(pin(record['raw_model'],record['raw_model_sha256']).read_bytes());expected=models[name]
            S.require(actual==expected,'HAND_FIXTURE '+name)
            case=json.loads(pin(record['input_case'],record['input_case_sha256']).read_bytes());audit_case(expected,case,pin)
            pin(record['sparse'],record['sparse_sha256'])
            domain=S.domains(expected)if len(expected['variables'])<=6 else None
            if domain is not None:
                sizes=[len(d)for d in domain];S.require(sizes==({'singular':[9,9,9],'fullrank':[1,1,1],'inconsistent':[0,9,9],'divided_scope_control':[3,3,3]}[name]),'BRUTE_FIXTURE_DOMAIN')
            case_reports[name]=dict(columns=len(expected['variables']),rows=len(expected['equations']),domain_sizes=None if domain is None else [len(d)for d in domain])
        # Raw and divided content3 toy have explicitly different solution sets.
        S.require(S.domains(models['singular'])!=S.domains(models['divided_scope_control']),'CONTENT3_NON_EQUIVALENCE')
        labels=[name+'_'+phase for name in ['singular','fullrank','inconsistent','multiword']for phase in ['whole','prefix','resume']]+['divided_scope_control_whole','arithmetic']+list(NEG)
        S.require([r['label']for r in manifest['runs']]==labels,'NATIVE_25_FROZEN_POPULATION')
        cp_reports=[];primal_count=0;relation_count=0
        for run in manifest['runs']:
            label=run['label'];inputpath=pin(run['input'],run['input_sha256']);receipt=json.loads(pin(run['receipt'],run['receipt_sha256']).read_bytes())
            expected=2 if label in NEG else 4 if label.endswith('_prefix') else 3 if label.startswith('inconsistent_')else 0
            S.require(run['actual_exit_code']==receipt['actual_exit_code']==expected and receipt['reaped']is True,'NATIVE_RECEIPT_RESULT')
            cmd=receipt['command'];S.require(cmd[:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s']and cmd[5]=='/usr/bin/prlimit'and cmd[6:9]==['--as=4294967296:4294967296','--fsize=4294967296:4294967296','--core=0:0'],'NATIVE_GUARD_VECTOR')
            S.require(cmd[9].endswith('/acceleration/results/20261002_rooted8_gf3_build02/literal_gf3')and cmd[cmd.index('--input-sha256')+1]==run['input_sha256'],'NATIVE_BINARY_INPUT_ID')
            stdout=pin(receipt['stdout'],receipt['stdout_sha256']).read_bytes();stderr=pin(receipt['stderr'],receipt['stderr_sha256']).read_bytes()
            for path,record in run['artifacts'].items():S.require(pin(path,record['sha256']).stat().st_size==record['bytes'],'NATIVE_ARTIFACT_SIZE')
            directory=BASE/label
            if label in NEG:
                S.require(stdout==b''and stderr==(NEG[label]+'\n').encode('ascii'),'NATIVE_EXACT_REJECT_STAGE')
                if label.startswith('reject_checkpoint_'):
                    cp=Path(cmd[cmd.index('--resume')+1]);cp=ROOT/cp.as_posix().split('/conway-99-graph/')[1]
                    wanted={'hash':'CP_HASH','rhs':'CP_RHS','origin_scale':'CP_ORIGIN_SCALE','plane':'CP_PLANES','leading':'CP_LEADING','padding':'CP_PADDING','dag_weight':'CP_DAG_WEIGHT'}[label[len('reject_checkpoint_'):]]
                    reject(label,lambda cp=cp:checkpoint(pin(cp).read_bytes(),models['fullrank'],manifest['cases']['fullrank']['sparse_sha256']),wanted)
                else:reject(label,lambda: S.read_sparse(inputpath.read_bytes()),'GF3_SPARSE_SYNTAX')
                continue
            S.require(stderr==b'','NATIVE_POSITIVE_STDERR')
            if label=='arithmetic':continue
            name=label.rsplit('_',1)[0];model=models[name];n=len(model['variables']);cpraw=(directory/'checkpoint.bin').read_bytes()
            report,_=checkpoint(cpraw,model,run['input_sha256']);cp_reports.append(dict(label=label,**report))
            if label.endswith('_prefix'):
                S.require(report['processed']=={'singular':2,'fullrank':8,'inconsistent':1,'multiword':2}[name],'NATIVE_PREFIX_BOUNDARY');continue
            if expected==0:
                vectors=S.read_vectors(directory,n);S.scalar_vectors(model,vectors);primal_count+=1
                if n<=6:S.require(all(v in d for v,d in zip(vectors,S.domains(model))),'NATIVE_PRIMAL_DOMAIN')
                S.require((directory/'row_residuals.bin').read_bytes()==bytes(3*len(model['equations'])),'NATIVE_FULL_ZERO_RESIDUAL_BYTES')
                if label.endswith('_resume'):
                    for component in ['const','a','b']:S.require((directory/('x_'+component+'.trits')).read_bytes()==(BASE/(name+'_whole')/('x_'+component+'.trits')).read_bytes(),'WHOLE_RESUME_FULL_PRIMAL_BYTES')
            else:
                rel=json.loads((directory/'original_row_relation.json').read_bytes());S.require(rel['format']=='ORIGINAL_LITERAL_GF3_ROW_RELATION_CANDIDATE_V1'and(rel['matrix_rows'],rel['matrix_columns'])==(7,4),'RELATION_DIMENSIONS')
                S.scalar_relation(model,rel['original_row_coefficients'],rel['rhs_affine_residue']);relation_count+=1
                if label.endswith('_resume'):S.require((directory/'original_row_relation.json').read_bytes()==(BASE/'inconsistent_whole/original_row_relation.json').read_bytes(),'WHOLE_RESUME_FULL_RELATION_BYTES')
        # Every arithmetic record, every physical bit including padding, with full tuple coverage.
        arithmetic=[json.loads(line)for line in pin(BASE/'arithmetic/arithmetic.jsonl').read_bytes().splitlines()];seen=set()
        for row in arithmetic:
            if row['kind']=='PACKED_ADD':
                key=(row['kind'],row['a'],row['b'],row['scale']);S.require(key not in seen,'ARITH_DUPLICATE');seen.add(key)
                S.require(row['n']==130 and len(row['one'])==len(row['two'])==3 and all(type(v)is int and 0<=v<2**64 for v in row['one']+row['two']),'ARITH_WIRE')
                S.require(not any(a&b for a,b in zip(row['one'],row['two'])),'ARITH_PLANES')
                for j in range(192):
                    trit=((row['one'][j//64]>>(j%64))&1)+2*((row['two'][j//64]>>(j%64))&1)
                    S.require(trit==((row['a']+row['scale']*row['b'])%3 if j in [0,63,64,65,127,128,129]else 0),'ARITH_SCALAR_PACKED_BIT')
            else:
                S.require(row['kind']=='RHS_ADD'and row['other']==[2,1,2],'ARITH_RHS_WIRE');key=(row['kind'],*row['rhs'],row['scale']);S.require(key not in seen,'ARITH_DUPLICATE');seen.add(key)
                S.require(row['result']==[(a+row['scale']*b)%3 for a,b in zip(row['rhs'],row['other'])],'ARITH_SCALAR_RHS')
        wanted={('PACKED_ADD',a,b,s)for a,b,s in product(range(3),range(3),(1,2))}|{('RHS_ADD',a,b,c,s)for a,b,c,s in product(range(3),repeat=4)}
        S.require(seen==wanted and len(arithmetic)==99,'ARITH_COMPLETE_99_POPULATION')
        # Independent corruption must pass syntax and fail at mathematical identity.
        cpraw=bytearray((BASE/'fullrank_prefix/checkpoint.bin').read_bytes());_,loc=checkpoint(bytes(cpraw),models['fullrank'],manifest['cases']['fullrank']['sparse_sha256'])
        changed=bytearray(cpraw);offset=loc[0]['one_offset'];value=struct.unpack_from('<Q',changed,offset)[0];struct.pack_into('<Q',changed,offset,value^(1<<3))
        reject('valid_syntax_wrong_basis_bit',lambda:checkpoint(bytes(changed),models['fullrank'],manifest['cases']['fullrank']['sparse_sha256']),'CP_RAW_DAG_IDENTITY')
        changed=bytearray(cpraw);offset=next(v for data in loc.values()for v in data['dep_offsets']);changed[offset]=3-changed[offset]
        reject('valid_syntax_wrong_DAG_weight',lambda:checkpoint(bytes(changed),models['fullrank'],manifest['cases']['fullrank']['sparse_sha256']),'CP_RAW_DAG_IDENTITY')
        changed=bytearray(cpraw);struct.pack_into('<Q',changed,17+64+3*8,9)
        reject('valid_syntax_false_processed_prefix',lambda:checkpoint(bytes(changed),models['fullrank'],manifest['cases']['fullrank']['sparse_sha256']),'CP_PREFIX_ROWSPACE')
        known=S.read_vectors(BASE/'fullrank_whole',4)
        for filename,scope in [('corrupt_vector.json','vector'),('corrupt_coefficient_model.json','model'),('corrupt_rhs_model.json','model')]:
            artifact=json.loads(pin(BASE/filename).read_bytes())
            reject(filename,lambda a=artifact,s=scope:S.scalar_vectors(models['fullrank']if s=='vector'else a,a if s=='vector'else known),'GF3_ORIGINAL_PRIMAL_SCALAR_ROW')
        for filename in ['corrupt_relation_weight.json','corrupt_relation_rhs.json']:
            artifact=json.loads(pin(BASE/filename).read_bytes());reject(filename,lambda a=artifact:S.scalar_relation(models['inconsistent'],a['original_row_coefficients'],a['rhs_affine_residue']),'GF3_ORIGINAL_ROW_RELATION_SCALAR')
        for divisor in [3,0,-2]:reject('invalid_divisor_'+str(divisor),lambda d=divisor:S.row_data(models['singular']['equations'][0],4,divisor=d),'GF3_POSITIVE_DIVIDING_CONTENT')
        # The original failed wrapper is immutable evidence; approve no old gate.
        old=ROOT/'acceleration/results/20261002_rooted8_gf3_controls01';failure=json.loads(pin(old/'failure.json').read_bytes())
        S.require(failure['error']=="ValueError('known divided scope control primals')",'OLD_FAILURE_REASON')
        for path,wanted_sha in failure['inputs_sha256'].items():pin(path,wanted_sha)
        receipts=sorted(old.glob('*.receipt.json'));S.require(len(receipts)==13,'OLD_ACTUAL_RECEIPT_POPULATION')
        for path in receipts:pin(path)
        oldvectors=S.read_vectors(old/'divided_scope_control_whole',4);S.scalar_vectors(models['divided_scope_control'],oldvectors)
        S.require(all(v in d for v,d in zip(oldvectors,S.domains(models['divided_scope_control']))),'OLD_VALID_NONUNIQUE_DIVIDED_MEMBERSHIP')
        S.require(oldvectors!=[[0,1,0,2],[2,0,0,1],[1,1,0,2]],'OLD_PARTICULAR_EXPECTATION_FALSIFIED')
        for label in ['const','a','b']:pin(old/'divided_scope_control_whole'/('x_'+label+'.trits'))
        result=dict(status='INDEPENDENT_ORIGINAL_GF3_PRIMAL_RELATION_CONTROLS_V1_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),verifier='/root/structural',command=[sys.executable,*sys.argv],cwd=str(ROOT),python_version=platform.python_version(),inputs_sha256=pins,
            native_calls_checked=25,positive_complete_vector_artifact_sets=primal_count,complete_original_row_relation_artifacts=relation_count,weighted_checkpoint_artifacts_checked=len(cp_reports),checkpoint_reports=cp_reports,arithmetic_records_scalar_checked=99,negative_controls=negatives,cases=case_reports,
            original_signed_integer_rows_checked=True,packed_planes_checked_all_bits=True,weighted_checkpoint_DAG_and_complete_prefix_rowspace_checked=True,whole_resume_bytes_checked=True,
            old_v1_failure=dict(actual_receipts=13,reason=failure['error'],divided_vectors_exactly_valid=True,arbitrary_particular_vector_expectation_refuted=True,old_gate_approved=False),
            scope='Finite frozen controls only. No producer imports or native solver execution. Tiny domain exhaustion and exact scalar raw-row/certificate/weighted-DAG checks; no full operator rank, graph or exclusion claim.',
            shared_components=['Previously independently calibrated scalar checker','command_deadline; raw file formats and frozen artifacts only'],elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),rank_claim=False,target_resolution=False,scientific_GF3_launched=False)
        S.save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary=str((out/'summary.json').relative_to(ROOT)),sha256=S.sha(out/'summary.json'))))
    except BaseException as error:
        S.save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),error=repr(error),inputs_sha256=pins,negative_controls=negatives,elapsed_seconds=time.monotonic()-started,outputs_preserved=True));raise


if __name__=='__main__':main()
