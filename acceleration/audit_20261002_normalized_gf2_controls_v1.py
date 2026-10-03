"""Independent scalar, brute-domain and binary-checkpoint engineering audit.

No native/producer mathematics imports or solver execution. Finite controls
approve tested source/build/input behavior only, never rank or target coverage.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time

from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20261002_rooted8_normalized_gf2_controls01'
MANIFEST=BASE/'controls_manifest.json'
MANIFEST_SHA='00f3fccb582133180583c48f1502c5dbc0f980324a92d295a3b1cd41ff601bf8'
PLAN=ROOT/'acceleration/plan_20261002_rooted8_normalized_gf2_v2.json'
PLAN_SHA='2b4b89b137fe221e4a0f41797ed37a6bba800ae7a5ad26365603a60997c4198b'
NORMALIZATION=ROOT/'acceleration/results/20261002_independent_review/rooted8_row_content01/normalization_manifest.json'
NORMALIZATION_SHA='47c9f0158084a1cf04b9ce2f84db93ee748e5e3226d759f276090aa50bdfe91c'


def require(ok, diagnostic):
    if not ok:raise ValueError(diagnostic)


def dump(path, data):
    with path.open('x',encoding='utf8',newline='\n') as stream:
        json.dump(data,stream,indent=2);stream.write('\n')


def key(path):return path.resolve().relative_to(ROOT).as_posix()


def digest(data):return hashlib.sha256(data).hexdigest()


def canonical(row):return json.dumps(row,sort_keys=True,separators=(',',':')).encode('ascii')


def normalized(row, n, divisor=None):
    require(type(row)is dict and type(row.get('terms'))is list and type(row.get('rhs_affine'))is list and len(row['rhs_affine'])==3,'RAW_ROW_SYNTAX')
    require(all(type(t)is list and len(t)==2 and type(t[0])is int and 0<=t[0]<n and type(t[1])is int for t in row['terms']),'RAW_ROW_SYNTAX')
    require(all(type(c)is int for c in row['rhs_affine']),'RAW_ROW_SYNTAX')
    values=[t[1] for t in row['terms']]+row['rhs_affine']
    g=math.gcd(*values) or 1
    if divisor is not None:
        require(type(divisor)is int and divisor>0 and all(c%divisor==0 for c in values),'NORMALIZATION_DIVISOR')
        g=divisor
    result={'terms':[[j,c//g]for j,c in row['terms']],'rhs_affine':[c//g for c in row['rhs_affine']]}
    require(all([j,g*c]==t for t,(j,c)in zip(row['terms'],result['terms'])) and [g*c for c in result['rhs_affine']]==row['rhs_affine'],'NORMALIZATION_ROUNDTRIP')
    return g,result


def read_sparse(raw):
    require(raw.endswith(b'\n'),'SPARSE_INPUT_SYNTAX')
    try:lines=raw.decode('ascii').splitlines()
    except UnicodeDecodeError:raise ValueError('SPARSE_INPUT_SYNTAX')
    header=lines[0].split()
    require(len(header)==3 and header[0]=='GF2_AFFINE_SPARSE_V1' and all(x.isdecimal() for x in header[1:]),'SPARSE_INPUT_SYNTAX')
    n,m=map(int,header[1:]);require(n>0 and m>0 and len(lines)==m+1,'SPARSE_INPUT_SYNTAX');rows=[]
    for line in lines[1:]:
        tokens=line.split();require(len(tokens)>=2 and all(t.isdecimal() for t in tokens),'SPARSE_INPUT_SYNTAX')
        mask,count,*indices=map(int,tokens)
        require(mask<=7 and count<=n and len(indices)==count and indices==sorted(set(indices)) and all(j<n for j in indices),'SPARSE_INPUT_SYNTAX')
        rows.append((mask,indices))
    return n,rows


def parity_rows(model):
    n=len(model['variables']);rows=[]
    for row in model['equations']:
        _,z=normalized(row,n);left=[0]*n
        for j,c in z['terms']:left[j]=(left[j]+c)%2
        rows.append((sum((c%2)<<j for j,c in enumerate(z['rhs_affine'])),[j for j,c in enumerate(left)if c]))
    return rows


def read_vectors(directory,n):
    vectors=[]
    for label in ['const','a','b']:
        raw=(directory/('x_'+label+'.bits')).read_bytes();lines=raw.decode('ascii').splitlines()
        require(len(lines)==2 and raw.endswith(b'\n') and lines[0]==f'GF2_AFFINE_PRIMAL_V1 {n} {label}' and len(lines[1])==n and all(c in '01' for c in lines[1]),'PRIMAL_SYNTAX')
        vectors.append([int(c)for c in lines[1]])
    return vectors


def check_vectors(model,vectors):
    n=len(model['variables']);require(len(vectors)==3 and all(len(v)==n and all(type(x)is int and x in (0,1)for x in v)for v in vectors),'PRIMAL_SYNTAX')
    for row in model['equations']:
        _,z=normalized(row,n)
        for t,v in enumerate(vectors):require((sum(c*v[j] for j,c in z['terms'])-z['rhs_affine'][t])%2==0,'PRIMAL_SCALAR_ROW')


def check_relation(model,relation):
    n=len(model['variables']);m=len(model['equations']);indices=relation['original_row_indices']
    require(relation['format']=='NORMALIZED_LITERAL_GF2_ROW_XOR_CANDIDATE_V1' and relation['matrix_rows']==m and relation['matrix_columns']==n and type(indices)is list and indices and all(type(i)is int and 0<=i<m for i in indices) and indices==sorted(set(indices)),'XOR_SYNTAX')
    lhs=[0]*n;rhs=[0]*3
    for i in indices:
        _,z=normalized(model['equations'][i],n)
        for j,c in z['terms']:lhs[j]+=c
        for j,c in enumerate(z['rhs_affine']):rhs[j]+=c
    observed=sum((c%2)<<j for j,c in enumerate(rhs))
    require(not any(c%2 for c in lhs) and observed==relation['rhs_affine_mask'] and observed!=0,'XOR_SCALAR_ROW')
    return {'original_rows':indices,'lhs_exact_integer_sums':lhs,'rhs_exact_integer_sums':rhs,'rhs_mod2_mask':observed}


def brute(rows,n,component):
    return [list(v)for v in product((0,1),repeat=n) if all(sum(v[j]for j in indices)%2==(mask>>component&1)for mask,indices in rows)]


def checkpoint(raw,input_hash,rows,n):
    require(raw[:17]==b'GF2_PRIMAL_CP_V2\n' and raw[17:81].decode('ascii')==input_hash,'CHECKPOINT_INPUT_IDENTITY')
    offset=81
    def u64():
        nonlocal offset
        require(offset+8<=len(raw),'CHECKPOINT_SYNTAX');value=struct.unpack_from('<Q',raw,offset)[0];offset+=8;return value
    cn,m,words,processed=[u64()for _ in range(4)]
    require((cn,m,words)==(n,len(rows),(n+63)//64) and processed<=m,'CHECKPOINT_DIMENSIONS')
    cells={}
    for p in range(n):
        require(offset<len(raw),'CHECKPOINT_SYNTAX');present=raw[offset];offset+=1;require(present in (0,1),'CHECKPOINT_SYNTAX')
        if present:
            require(offset<len(raw),'CHECKPOINT_SYNTAX');rhs=raw[offset];offset+=1
            origin,order,count=[u64()for _ in range(3)];deps=[u64()for _ in range(count)]
            packed=sum(u64()<<(64*w)for w in range(words))
            require(rhs<=7 and origin<processed and order<n and len(deps)<=n and packed>>n==0 and packed&(1<<p) and packed% (1<<p)==0,'CHECKPOINT_SYNTAX')
            cells[p]={'rhs':rhs,'origin':origin,'order':order,'dependencies':deps,'packed':packed}
    require(offset==len(raw),'CHECKPOINT_SYNTAX')
    insertion=sorted(cells,key=lambda p:cells[p]['order']);require([cells[p]['order']for p in insertion]==list(range(len(cells))),'CHECKPOINT_DAG')
    for p in insertion:
        cell=cells[p];mask,indices=rows[cell['origin']];bits=sum(1<<j for j in indices)
        for d in cell['dependencies']:
            require(d in cells and cells[d]['order']<cell['order'],'CHECKPOINT_DAG');bits^=cells[d]['packed'];mask^=cells[d]['rhs']
        require(bits==cell['packed'] and mask==cell['rhs'],'CHECKPOINT_RAW_BASIS')
    basis_rows=[(cells[p]['rhs'],[j for j in range(n)if cells[p]['packed']>>j&1])for p in insertion]
    for t in range(3):require(brute(rows[:processed],n,t)==brute(basis_rows,n,t),'CHECKPOINT_PREFIX_DOMAIN')
    return {'processed_rows':processed,'basis_entries':len(cells),'basis_scalar_DAG_checked':True,'all_three_prefix_domains_exhausted':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Independent eight5row native controls, four-variable brute domains, little-endian DAG checkpoints and full85874row gcd identity;260worker/300outer with40reserve')
    start=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(path,wanted=None):
        path=Path(path);path=path if path.is_absolute()else ROOT/path
        require(path.resolve().is_relative_to(ROOT) and path.is_file(),'RAW_ARTIFACT_AVAILABILITY')
        require(deadline.status()['remaining_seconds']>20,'not completed within allocated budget')
        value=digest(path.read_bytes());require(wanted is None or value==wanted,'ARTIFACT_SHA256 '+key(path));pins[key(path)]=value;return path
    negatives=[]
    def rejected(label,call,wanted):
        try:call()
        except ValueError as error:require(str(error)==wanted,'NEGATIVE_STAGE_MISMATCH');negatives.append({'label':label,'diagnostic':str(error)})
        else:raise ValueError('NEGATIVE_ACCEPTED '+label)
    try:
        manifest=json.loads(pin(MANIFEST,MANIFEST_SHA).read_bytes());plan=json.loads(pin(PLAN,PLAN_SHA).read_bytes())
        for path,wanted in manifest['inputs_sha256'].items():pin(path,wanted)
        for path,wanted in plan['source_hashes'].items():pin(path,wanted)
        build=json.loads((ROOT/'acceleration/results/20261002_rooted8_normalized_gf2_build02/build_manifest.json').read_bytes())
        for path,wanted in build['inputs_sha256'].items():pin(path,wanted)
        build_receipt=json.loads(pin(build['receipt'],build['receipt_sha256']).read_bytes())
        require(build_receipt['actual_exit_code']==0 and build_receipt['reaped'] and build['source_cpp_sha256']==plan['source_hashes']['acceleration/rooted8_normalized_gf2_20261002_v2.cpp'],'SOURCE_BUILD_BINDING')
        for name in ['stdout','stderr']:pin(build_receipt[name],build_receipt[name+'_sha256'])
        model0={'variables':list(range(4)),'equations':[{'terms':[[0,-2],[1,2]],'rhs_affine':[2,2,0]},{'terms':[[1,4],[2,4]],'rhs_affine':[4,0,4]},{'terms':[[0,1],[2,1]],'rhs_affine':[0,1,1]},{'terms':[],'rhs_affine':[0,0,0]},{'terms':[[0,2],[0,-2]],'rhs_affine':[0,0,0]}]}
        models={};domains={}
        for label in ['feasible','inconsistent']:
            base=BASE/(label+'_input');raw=json.loads(pin(base/'raw_model.json').read_bytes())
            expected=json.loads(json.dumps(model0))
            if label=='inconsistent':expected['equations'][2]['rhs_affine'][0]=1
            require(raw==expected,'INDEPENDENT_FIXTURE_DEFINITION');models[label]=raw
            case=json.loads(pin(manifest[label+'_case'],manifest[label+'_case_sha256']).read_bytes());rows=parity_rows(raw)
            normalized_bytes=b'';records=[];counts=Counter();sparse=f'GF2_AFFINE_SPARSE_V1 4 5\n'.encode('ascii')
            for i,row in enumerate(raw['equations']):
                g,z=normalized(row,4);counts[g]+=1;normalized_bytes+=canonical(z)+b'\n'
                mask,indices=rows[i];line=(str(mask)+' '+str(len(indices))+''.join(' '+str(j)for j in indices)+'\n').encode('ascii');sparse+=line
                records.append({'original_row':i,'content':g,'raw_literal_sha256':digest(canonical(row)),'normalized_literal_sha256':digest(canonical(z)),'parity_row_sha256':digest(line)})
            require(case['records']==records and case['content_counts']=={str(k):v for k,v in counts.items()},'TINY_NORMALIZATION_RECORDS')
            require(pin(case['normalized_literal_rows'],case['normalized_literal_rows_sha256']).read_bytes()==normalized_bytes and digest(normalized_bytes)==case['normalized_literal_jsonl_sha256'],'TINY_NORMALIZED_STREAM')
            require(pin(case['sparse_rows'],case['sparse_rows_sha256']).read_bytes()==sparse and read_sparse(sparse)==(4,rows),'TINY_PARITY_STREAM')
            domains[label]=[brute(rows,4,j)for j in range(3)]
        require(all(len(d)==4 for d in domains['feasible']) and [len(d)for d in domains['inconsistent']]==[0,4,4],'BRUTE_FORCE_FIXTURE_DOMAINS')
        checkpoint_reports=[];receipts=[]
        labels=['feasible_whole','feasible_prefix','feasible_resume','inconsistent_whole','inconsistent_prefix','inconsistent_resume','reject_column','reject_checkpoint_hash']
        codes=[0,4,0,3,4,3,2,2];require([r['label']for r in manifest['runs']]==labels,'EXACT_EIGHT_POPULATION')
        for run,code in zip(manifest['runs'],codes):
            pin(run['input'],run['input_sha256']);receipt=json.loads(pin(run['receipt'],run['receipt_sha256']).read_bytes())
            require(receipt['actual_exit_code']==run['actual_exit_code']==code and receipt['reaped'] and receipt['expected_exit_codes']==[code],'NATIVE_RECEIPT_OUTCOME')
            for name in ['stdout','stderr']:pin(receipt[name],receipt[name+'_sha256'])
            for path,record in run['artifacts'].items():require(pin(path,record['sha256']).stat().st_size==record['bytes'],'NATIVE_ARTIFACT_BYTES')
            argv=receipt['command'];require(argv[:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s'] and argv[5:9]==['/usr/bin/prlimit','--as=4294967296:4294967296','--fsize=4294967296:4294967296','--core=0:0'],'NATIVE_CONTAINMENT_VECTOR')
            require(argv[9].endswith('/'+build['binary']) and argv[argv.index('--input-sha256')+1]==run['input_sha256'],'NATIVE_SOURCE_INPUT_BINDING')
            label=run['label'];stdout=(ROOT/receipt['stdout']).read_bytes();stderr=(ROOT/receipt['stderr']).read_bytes()
            if code==2:
                wanted={'reject_column':b'sparse ordered column range\n','reject_checkpoint_hash':b'checkpoint exact input hash\n'}[label]
                require(stderr==wanted and stdout==b'' and not run['artifacts'],'STRICT_NATIVE_REJECTION_STAGE')
            else:
                require(stderr==b'','NATIVE_UNEXPECTED_STDERR')
                inputlabel=label.split('_')[0];rows=parity_rows(models[inputlabel]);cp=BASE/label/'checkpoint.bin'
                report=checkpoint(cp.read_bytes(),run['input_sha256'],rows,4);report['label']=label;checkpoint_reports.append(report)
                if code==0:
                    vectors=read_vectors(BASE/label,4);check_vectors(models[inputlabel],vectors)
                    require(all(v in d for v,d in zip(vectors,domains[inputlabel])),'FULL_BINARY_DOMAIN_MEMBERSHIP')
                    require((BASE/label/'row_residuals.bin').read_bytes()==bytes(5),'FULL_RESIDUAL_BYTES')
                if code==3:
                    relation=json.loads((BASE/label/'xor_original_row_indices.json').read_bytes());witness=check_relation(models[inputlabel],relation)
                    require(witness['original_rows']==[0,1,2] and witness['rhs_mod2_mask']==1,'HAND_DERIVED_XOR')
            receipts.append({'label':label,'exit_code':code,'strict_stage_checked':True})
        for label in ['const','a','b']:require((BASE/'feasible_whole'/('x_'+label+'.bits')).read_bytes()==(BASE/'feasible_resume'/('x_'+label+'.bits')).read_bytes(),'WHOLE_RESUME_PRIMAL_BYTES')
        require((BASE/'inconsistent_whole/xor_original_row_indices.json').read_bytes()==(BASE/'inconsistent_resume/xor_original_row_indices.json').read_bytes(),'WHOLE_RESUME_XOR_BYTES')
        vectors=read_vectors(BASE/'feasible_whole',4)
        rejected('corrupt_primal',lambda:check_vectors(models['feasible'],json.loads(pin(BASE/'corrupt_vector.json').read_bytes())),'PRIMAL_SCALAR_ROW')
        for label in ['coefficient','rhs']:rejected('corrupt_raw_'+label,lambda label=label:check_vectors(json.loads(pin(BASE/('corrupt_'+label+'_model.json')).read_bytes()),vectors),'PRIMAL_SCALAR_ROW')
        for label in ['indices','mask']:rejected('corrupt_XOR_'+label,lambda label=label:check_relation(models['inconsistent'],json.loads(pin(BASE/('corrupt_relation_'+label+'.json')).read_bytes())),'XOR_SCALAR_ROW')
        for divisor in [3,0,-2]:rejected('bad_divisor_'+str(divisor),lambda divisor=divisor:normalized(model0['equations'][0],4,divisor),'NORMALIZATION_DIVISOR')
        good_sparse=(BASE/'feasible_input/sparse_rows.txt').read_bytes()
        for label,raw in [('column_range',b'GF2_AFFINE_SPARSE_V1 4 1\n0 1 4\n'),('duplicate_column',b'GF2_AFFINE_SPARSE_V1 4 1\n0 2 1 1\n'),('mask_range',b'GF2_AFFINE_SPARSE_V1 4 1\n8 0\n'),('extra_tail',good_sparse+b'garbage\n')]:rejected(label,lambda raw=raw:read_sparse(raw),'SPARSE_INPUT_SYNTAX')
        raw_cp=(BASE/'wrong_input_checkpoint.bin').read_bytes()
        rejected('wrong_checkpoint_input_hash',lambda:checkpoint(raw_cp,digest(good_sparse),parity_rows(models['feasible']),4),'CHECKPOINT_INPUT_IDENTITY')
        normal=json.loads(pin(NORMALIZATION,NORMALIZATION_SHA).read_bytes());full=json.loads(pin(normal['model'],normal['model_sha256']).read_bytes())
        require(len(full['variables'])==normal['variables']==23019 and len(full['equations'])==normal['rows']==85874,'FULL_FROZEN_UNIVERSE')
        stream=hashlib.sha256();counts=Counter()
        for i,row in enumerate(full['equations']):
            if i%1024==0:require(deadline.status()['remaining_seconds']>20,'not completed within allocated budget')
            g,z=normalized(row,23019);counts[g]+=1;literal={'terms':row['terms'],'rhs_affine':row['rhs_affine']}
            require(normal['records'][i]=={'original_row':i,'content':g,'raw_literal_sha256':digest(canonical(literal)),'normalized_literal_sha256':digest(canonical(z))},'FULL_MATH_GCD_RECORD')
            stream.update(canonical(z)+b'\n')
        require(stream.hexdigest()==normal['normalized_literal_jsonl_sha256'] and {str(k):v for k,v in counts.items()}==normal['content_counts'],'FULL_MATH_GCD_STREAM')
        pin(__file__);pin(ROOT/'pyproject.toml');pin(ROOT/'uv.lock')
        dump(out/'summary.json',{'status':'INDEPENDENT_NORMALIZED_GF2_PRIMAL_XOR_CONTROLS_V1_PASS','timestamp':datetime.now(timezone.utc).isoformat(),
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python_version':platform.python_version(),
            'verifier':'/root/structural','producer':'/root/native_driver','method':'Independent math.gcd integer rows and scalar sums; all16four-bit assignments eachRHS; source-reviewed uint64 DAG producer, binary little-endian checkpoints reconstructed against raw rows; no producer imports or native execution.',
            'shared_trusted_components':['command_deadline.py','run_compute_command.py','Python standard library and pinned environment'],'inputs_sha256':pins,
            'native_receipts_checked':receipts,'checkpoint_reports':checkpoint_reports,'brute_force_domains':domains,'negative_controls':negatives,
            'full_normalization_rows_checked':85874,'normalized_stream_sha256':stream.hexdigest(),'normalization_content_counts':dict(counts),
            'source_review':{'cpp_least_pivot_forward_elimination':True,'DAG_original_row_parity_expansion':True,'descending_free_zero_backsubstitution':True,'cooperative_completed_prefix_checkpoint':True,'wrapper_exact_new_gate_required':True},
            'scope':'Finite engineering controls plus exact full row-content identity. No full native solve, rank, graph feasibility, catalogue/model necessity or target-wide exclusion approval.',
            'rank_claim':False,'target_resolution':False,'elapsed_seconds':time.monotonic()-start})
    except BaseException as error:
        dump(out/'failure.json',{'error':repr(error),'inputs_sha256':pins,'elapsed_seconds':time.monotonic()-start,'outputs_preserved':True,'gate_approved':False});raise


if __name__=='__main__':main()
