"""Exact ORIGINAL-row producer and contained packed GF3 primal/relation worker.

No producer mathematics imports or rank claim. New controls/normalization gates
must bind these exact bytes; all scientific outputs remain CANDIDATE until a
different author checks raw integer rows and complete raw trits/row coefficients.
Utility/checkpoint ancestry from the preserved GF2 producer is disclosed; no
producer code is an independent checker. New exact source/build gates required.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import argparse,hashlib,json,os,platform,subprocess,sys,time
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
CPP=ROOT/'acceleration/rooted8_gf3_20261002_v1.cpp'
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
MODEL='acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
MODEL_SHA='a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'
NORM='acceleration/results/20261002_independent_review/rooted8_row_content01/normalization_manifest.json'
NORM_SHA='47c9f0158084a1cf04b9ce2f84db93ee748e5e3226d759f276090aa50bdfe91c'
ENCODING='acceleration/results/20261002_independent_review/rooted8_model01/summary.json'
ENCODING_SHA='e3158fe17f4a83e5231c90f72c912e5ef37cd6ddc3ce6300f0c6861f9d0ffc4e'
COMPILER='/usr/bin/g++'
COMPILER_SHA='1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769'
CODE=[Path(__file__),CPP,SPEC,ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',
      ROOT/'acceleration/native_budget_env_v1/pyproject.toml',ROOT/'acceleration/native_budget_env_v1/uv.lock',
      ROOT/'acceleration/design_20261002_rooted8_gf3_v2.md',ROOT/'acceleration/plan_20261002_rooted8_gf3_v1.json',
      ROOT/'acceleration/plan_20261002_rooted8_gf3_correction_v2.json']


def need(ok,message):
    if not ok:raise ValueError(message)


def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def stamp():return datetime.now(timezone.utc).isoformat()


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')


def tick(deadline):need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>20,'not completed within allocated budget')


def sha(path,deadline):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for block in iter(lambda:f.read(8*1024**2),b''):tick(deadline);h.update(block)
    return h.hexdigest()


def pin(path,wanted,pins,deadline):
    path=Path(path).resolve();need(path.is_relative_to(ROOT)and path.is_file(),'repository raw artifact')
    digest=sha(path,deadline);need(wanted is None or digest==wanted,'exact raw SHA256 '+key(path));pins[key(path)]=digest
    return path


def literal(row):return json.dumps(row,sort_keys=True,separators=(',',':')).encode('ascii')


def normalize(row,n,divisor=None):
    need(type(row)is dict and type(row.get('terms'))is list and type(row.get('rhs_affine'))is list and len(row['rhs_affine'])==3,'literal row shape')
    values=[]
    for term in row['terms']:
        need(type(term)is list and len(term)==2 and type(term[0])is int and 0<=term[0]<n and type(term[1])is int,'literal integer index/coefficient')
        values.append(term[1])
    need(all(type(x)is int for x in row['rhs_affine']),'literal integer affine RHS');values+=row['rhs_affine']
    content=0
    for value in values:
        other=abs(value)
        while other:content,other=other,content%other
    content=content or 1
    if divisor is not None:
        need(type(divisor)is int and divisor>0 and all(x%divisor==0 for x in values),'exact positive dividing content');content=divisor
    result=dict(terms=[[i,c//content]for i,c in row['terms']],rhs_affine=[c//content for c in row['rhs_affine']])
    need(all(c==content*d for (i,c),(j,d)in zip(row['terms'],result['terms'])if i==j)and all(c==content*d for c,d in zip(row['rhs_affine'],result['rhs_affine'])),'literal coefficient normalization roundtrip')
    return content,result


def encode(model,base,deadline,expected=None):
    n=len(model['variables']);rows=model['equations'];need(n>0 and len(rows)>0,'nonempty model')
    text=base/'sparse_rows.txt';stream=base/'normalized_literal_rows.jsonl';records=[];counts=Counter();total=hashlib.sha256()
    with text.open('x',encoding='ascii',newline='\n')as output,stream.open('xb')as normalized:
        output.write('GF3_AFFINE_SPARSE_V1 '+str(n)+' '+str(len(rows))+'\n')
        for index,row in enumerate(tqdm(rows,desc='exact row-content preprocessing',mininterval=5)):
            if index%256==0:tick(deadline)
            g,new=normalize(row,n);counts[g]+=1;raw=dict(terms=row['terms'],rhs_affine=row['rhs_affine']);line=literal(new)+b'\n'
            normalized.write(line);total.update(line)
            coefficients={}
            for j,c in raw['terms']:coefficients[j]=(coefficients.get(j,0)+c)%3
            terms=[(j,c)for j,c in sorted(coefficients.items())if c]
            modularline=' '.join(str(c%3)for c in raw['rhs_affine'])+' '+str(len(terms))+''.join(' '+str(j)+' '+str(c)for j,c in terms)+'\n'
            output.write(modularline)
            record=dict(original_row=index,content=g,raw_literal_sha256=hashlib.sha256(literal(raw)).hexdigest(),normalized_literal_sha256=hashlib.sha256(literal(new)).hexdigest())
            if expected is not None:need(record==expected['records'][index],'independent content/row hash agreement')
            records.append(dict(**record,original_mod3_row_sha256=hashlib.sha256(modularline.encode('ascii')).hexdigest()))
    digest=total.hexdigest()
    if expected is not None:need(digest==expected['normalized_literal_jsonl_sha256']and dict(counts)=={int(k):v for k,v in expected['content_counts'].items()},'independent full normalized row stream/content census')
    manifest=dict(schema='ORIGINAL_LITERAL_GF3_INPUT_CASE_V1',columns=n,rows=len(rows),content_counts=dict(counts),normalized_literal_jsonl_sha256=digest,
        normalized_literal_rows=key(stream),normalized_literal_rows_sha256=sha(stream,deadline),sparse_rows=key(text),sparse_rows_sha256=sha(text,deadline),records=records,
        normalization='Positive gcd of every raw literal term coefficient and three affine RHS coefficients; gcd0 mappedto1. Division/stream checked, but sparse GF3 uses ORIGINAL raw rows including duplicate/sign aggregation modulo3.',
        raw_divided_mod3_equivalent=all(g%3!=0 for g in counts),
        candidate_only=True,independent_approval=False,target_resolution=False,rank_claim=False)
    save(base/'input_case.json',manifest);return text,manifest


def execute(argv,prefix,expected,deadline):
    started=time.monotonic()
    with Path(str(prefix)+'.stdout.log').open('xb')as stdout,Path(str(prefix)+'.stderr.log').open('xb')as stderr:
        process=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr)
        try:
            need(os.getpgid(process.pid)==os.getpgid(0),'worker in enclosing contained group')
            while process.poll()is None:tick(deadline);time.sleep(.05)
        finally:
            if process.poll()is None:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill()
            code=process.wait(timeout=5)
    receipt=dict(timestamp=stamp(),command=argv,cwd=str(ROOT),actual_exit_code=code,expected_exit_codes=expected,wall_seconds=time.monotonic()-started,reaped=True,
        stdout=key(Path(str(prefix)+'.stdout.log')),stderr=key(Path(str(prefix)+'.stderr.log')),child_pid=process.pid,process_group=os.getpgid(0),independent_approval=False)
    for name in ['stdout','stderr']:receipt[name+'_sha256']=sha(ROOT/receipt[name],deadline)
    save(Path(str(prefix)+'.receipt.json'),receipt);need(code in expected,'declared child outcome');return receipt


def native(args,label,inputfile,out,pins,deadline,expected,stop_after=None,resume=None,arithmetic=False):
    digest=sha(inputfile,deadline);allowed=deadline.child_seconds(args.native_seconds,reserve_seconds=40)
    cmd=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s',f'{allowed:.6f}s','/usr/bin/prlimit',f'--as={args.address_space_bytes}:{args.address_space_bytes}',
         f'--fsize={args.file_bytes}:{args.file_bytes}','--core=0:0',str(args.binary.resolve()),'--input',str(inputfile),'--input-sha256',digest,'--out',str(out/label),
         '--seconds',f'{max(.001,allowed-5):.6f}','--checkpoint-every','4096']
    if stop_after is not None:cmd+=['--stop-after-rows',str(stop_after)]
    if resume:pin(resume,None,pins,deadline);cmd+=['--resume',str(resume)]
    if arithmetic:cmd+=['--arithmetic-controls']
    receipt=execute(cmd,out/label,expected,deadline)
    artifacts={key(p):dict(sha256=sha(p,deadline),bytes=p.stat().st_size)for p in sorted((out/label).iterdir())if p.is_file()}
    return dict(label=label,input=key(inputfile),input_sha256=digest,receipt=key(out/(label+'.receipt.json')),receipt_sha256=sha(out/(label+'.receipt.json'),deadline),actual_exit_code=receipt['actual_exit_code'],artifacts=artifacts)


def read_vectors(directory,n):
    result=[]
    for label in ['const','a','b']:
        lines=(directory/('x_'+label+'.trits')).read_text().splitlines()
        need(len(lines)==2 and lines[0]=='GF3_AFFINE_PRIMAL_V1 '+str(n)+' '+label and len(lines[1])==n and set(lines[1])<=set('012'),'exact full ternary primal vector')
        result.append([int(x)for x in lines[1]])
    return result


def scalar_vectors(model,vectors):
    for row in model['equations']:
        normalize(row,len(model['variables']))
        for j in range(3):need(sum(c*vectors[j][i]for i,c in row['terms'])%3==row['rhs_affine'][j]%3,'exact original GF3 primal row')


def scalar_relation(model,path):
    relation=json.loads(path.read_bytes());terms=relation['original_row_coefficients'];indices=[x[0]for x in terms]
    need(terms and all(type(x)is list and len(x)==2 and type(x[0])is int and 0<=x[0]<len(model['equations'])and type(x[1])is int and x[1]in [1,2]for x in terms),'row relation coefficient domain')
    need(indices==sorted(set(indices)),'unique ordered row relation indices')
    need(relation['format']=='ORIGINAL_LITERAL_GF3_ROW_RELATION_CANDIDATE_V1'and relation['matrix_rows']==len(model['equations'])and relation['matrix_columns']==len(model['variables']),'exact original relation scope')
    lhs=[0]*len(model['variables']);rhs=[0]*3
    for i,multiplier in terms:
        row=model['equations'][i];normalize(row,len(lhs))
        for j,c in row['terms']:lhs[j]=(lhs[j]+multiplier*c)%3
        for j,c in enumerate(row['rhs_affine']):rhs[j]=(rhs[j]+multiplier*c)%3
    need(not any(lhs)and rhs==relation['rhs_affine_residue']and any(rhs),'exact original GF3 row relation');return relation


def controls(args,out,pins,deadline):
    import struct
    model=dict(variables=list(range(4)),equations=[dict(terms=[[0,-2],[1,2]],rhs_affine=[2,2,0]),dict(terms=[[1,4],[2,8]],rhs_affine=[4,0,4]),
        dict(terms=[[0,-1],[1,2],[2,2]],rhs_affine=[2,1,1]),dict(terms=[],rhs_affine=[0,0,0]),dict(terms=[[3,1],[3,-1]],rhs_affine=[0,0,0]),
        dict(terms=[[0,1],[0,2]],rhs_affine=[0,0,0]),dict(terms=[[3,3],[0,6]],rhs_affine=[6,6,3])])
    full=json.loads(json.dumps(model));full['equations']+=[dict(terms=[[0,1],[2,1]],rhs_affine=[0,2,1]),dict(terms=[[3,4]],rhs_affine=[0,0,0])]
    divided=dict(variables=model['variables'],equations=[normalize(row,4)[1]for row in model['equations']])
    bad=json.loads(json.dumps(model));bad['equations'][2]['rhs_affine'][0]=3
    large=dict(variables=list(range(130)),equations=[dict(terms=[[{0:0,1:63,2:64,3:129}[i],c]for i,c in row['terms']],rhs_affine=row['rhs_affine'])for row in full['equations']])
    large['equations']+=[dict(terms=[[65,2],[127,1]],rhs_affine=[0,0,0])]
    cases={};runs=[]
    for label,raw in [('singular',model),('fullrank',full),('inconsistent',bad),('multiword',large),('divided_scope_control',divided)]:
        base=out/(label+'_input');base.mkdir();save(base/'raw_model.json',raw);text,case=encode(raw,base,deadline)
        cases[label]=dict(raw_model=key(base/'raw_model.json'),raw_model_sha256=sha(base/'raw_model.json',deadline),input_case=key(base/'input_case.json'),input_case_sha256=sha(base/'input_case.json',deadline),sparse=key(text),sparse_sha256=sha(text,deadline))
        expected=3 if label=='inconsistent'else 0;runs.append(native(args,label+'_whole',text,out,pins,deadline,[expected]))
        if label=='divided_scope_control':continue
        stop=8 if label=='fullrank'else 1 if label=='inconsistent'else 2
        runs.append(native(args,label+'_prefix',text,out,pins,deadline,[4],stop_after=stop));runs.append(native(args,label+'_resume',text,out,pins,deadline,[expected],resume=out/(label+'_prefix/checkpoint.bin')))
        if expected==0:
            scalar_vectors(raw,read_vectors(out/(label+'_whole'),len(raw['variables'])))
            for name in ['const','a','b']:need((out/(label+'_whole')/('x_'+name+'.trits')).read_bytes()==(out/(label+'_resume')/('x_'+name+'.trits')).read_bytes(),'exact whole/resume primal byte identity')
        else:
            scalar_relation(raw,out/(label+'_whole/original_row_relation.json'))
            need((out/(label+'_whole/original_row_relation.json')).read_bytes()==(out/(label+'_resume/original_row_relation.json')).read_bytes(),'exact whole/resume original relation bytes')
    vectors=read_vectors(out/'singular_whole',4);need(vectors==[[0,1,0,0],[2,0,0,0],[1,1,0,0]],'known original singular primals')
    # Divided fixture has three solutions per RHS. Its least-column pivots need
    # not choose the hand-written witness with x2free=0. Exact scalar membership
    # and the explicit raw/content3 contrast are the acceptance conditions.
    divided_vectors=read_vectors(out/'divided_scope_control_whole',4);scalar_vectors(divided,divided_vectors)
    need(vectors!=divided_vectors and cases['singular']['sparse_sha256']!=cases['divided_scope_control']['sparse_sha256'],'content3 raw/divided scope contrast')
    text=ROOT/cases['fullrank']['sparse'];runs.append(native(args,'arithmetic',text,out,pins,deadline,[0],arithmetic=True))
    arithmetic=[json.loads(line)for line in (out/'arithmetic/arithmetic.jsonl').read_text().splitlines()];need(len(arithmetic)==99,'finite arithmetic record population')
    for row in arithmetic:
        if row['kind']=='PACKED_ADD':
            value=(row['a']+row['scale']*row['b'])%3
            for c in range(192):need(((row['one'][c//64]>>(c%64))&1)+2*((row['two'][c//64]>>(c%64))&1)==(value if c in [0,63,64,65,127,128,129]else 0),'finite packed arithmetic value')
        else:need(row['result']==[(a+row['scale']*b)%3 for a,b in zip(row['rhs'],row['other'])],'finite RHS arithmetic value')
    diagnostics={}
    for label,line,message in [('column','0 0 0 1 4 1','sparse ordered column range'),('coefficient','0 0 0 1 0 0','sparse coefficient trit'),('rhs','3 0 0 0','sparse rhs trit'),('duplicate','0 0 0 2 0 1 0 2','sparse ordered column range')]:
        damaged=out/('bad_'+label+'.txt');damaged.write_text('GF3_AFFINE_SPARSE_V1 4 1\n'+line+'\n',encoding='ascii');run='reject_'+label;runs.append(native(args,run,damaged,out,pins,deadline,[2]));diagnostics[run]=message
    original=(out/'fullrank_prefix/checkpoint.bin').read_bytes();position=17+64+32;offsets={}
    for p in range(4):
        present=original[position];position+=1
        if not present:continue
        rhs_at=position;scale_at=position+3;position+=4;origin_at=position;position+=16;count=struct.unpack_from('<Q',original,position)[0];position+=8;deps_at=position;position+=5*count;one_at=position;position+=8;two_at=position;position+=8
        offsets[p]=dict(rhs=rhs_at,scale=scale_at,origin=origin_at,deps=deps_at,count=count,one=one_at,two=two_at)
    mutations=[('hash',17,ord('f')if original[17]!=ord('f')else ord('e'),'checkpoint exact input hash'),('rhs',offsets[0]['rhs'],3,'checkpoint rhs trit'),('origin_scale',offsets[0]['scale'],0,'checkpoint origin scale')]
    for label,at,value,message in mutations:
        cp=bytearray(original);cp[at]=value;changed=out/('bad_checkpoint_'+label+'.bin');changed.write_bytes(cp);run='reject_checkpoint_'+label;runs.append(native(args,run,text,out,pins,deadline,[2],resume=changed));diagnostics[run]=message
    for label,message in [('plane','checkpoint disjoint planes'),('leading','checkpoint leading one'),('padding','checkpoint padding bits'),('dag_weight','checkpoint DAG coefficient')]:
        cp=bytearray(original)
        if label=='plane':cp[offsets[0]['two']]|=1
        elif label=='leading':cp[offsets[0]['one']]&=254;cp[offsets[0]['two']]|=1
        elif label=='padding':cp[offsets[0]['one']]|=128
        else:need(offsets[2]['count']>0,'weighted DAG corrupt control location');cp[offsets[2]['deps']+4]=0
        changed=out/('bad_checkpoint_'+label+'.bin');changed.write_bytes(cp);run='reject_checkpoint_'+label;runs.append(native(args,run,text,out,pins,deadline,[2],resume=changed));diagnostics[run]=message
    for label,message in diagnostics.items():need((out/(label+'.stderr.log')).read_text().splitlines()==[message]and (out/(label+'.stdout.log')).read_bytes()==b'','exact native negative diagnostic')
    negatives=[]
    def reject(label,call,message):
        try:call()
        except ValueError as e:need(type(e)is ValueError and str(e)==message,'exact finite control diagnostic');negatives.append(dict(label=label,diagnostic=str(e)))
        else:raise ValueError('corrupt finite control accepted')
    corrupt=[x[:]for x in vectors];corrupt[0][0]=1;save(out/'corrupt_vector.json',corrupt);reject('corrupt_primal_coordinate',lambda:scalar_vectors(model,corrupt),'exact original GF3 primal row')
    changed_model=json.loads(json.dumps(model));changed_model['equations'][0]['terms'][0][1]=2;save(out/'corrupt_coefficient_model.json',changed_model)
    reject('corrupt_raw_coefficient_sign',lambda:scalar_vectors(changed_model,vectors),'exact original GF3 primal row')
    changed_rhs=json.loads(json.dumps(model));changed_rhs['equations'][0]['rhs_affine'][0]=3;save(out/'corrupt_rhs_model.json',changed_rhs)
    reject('corrupt_raw_affine_RHS',lambda:scalar_vectors(changed_rhs,vectors),'exact original GF3 primal row')
    relation=scalar_relation(bad,out/'inconsistent_whole/original_row_relation.json');changed_relation=json.loads(json.dumps(relation));changed_relation['original_row_coefficients'][0][1]=3-changed_relation['original_row_coefficients'][0][1];save(out/'corrupt_relation_weight.json',changed_relation)
    reject('corrupt_relation_weight',lambda:scalar_relation(bad,out/'corrupt_relation_weight.json'),'exact original GF3 row relation')
    changed_relation=json.loads(json.dumps(relation));changed_relation['rhs_affine_residue'][0]=(changed_relation['rhs_affine_residue'][0]+1)%3;save(out/'corrupt_relation_rhs.json',changed_relation)
    reject('corrupt_relation_rhs',lambda:scalar_relation(bad,out/'corrupt_relation_rhs.json'),'exact original GF3 row relation')
    for label,divisor in [('nondivisor',3),('zero',0),('negative',-2)]:reject('normalization_'+label,lambda:normalize(model['equations'][0],4,divisor),'exact positive dividing content')
    manifest=dict(schema='ORIGINAL_GF3_PRIMAL_RELATION_CONTROLS_V1',timestamp=stamp(),source_commit=args.source_commit,inputs_sha256=pins,runs=runs,cases=cases,
        native_negative_diagnostics=diagnostics,finite_scalar_controls=negatives,whole_resume_primal_bytes_identical=True,whole_resume_original_row_relation_bytes_identical=True,
        arithmetic_records=99,raw_divided_content3_not_equivalent=True,
        producer_only=True,independent_approval=False,target_resolution=False,rank_claim=False,
        required_independent_gate='INDEPENDENT_ORIGINAL_GF3_PRIMAL_RELATION_CONTROLS_V1_PASS')
    save(out/'controls_manifest.json',manifest);return dict(status='ORIGINAL_GF3_PRIMAL_RELATION_CONTROLS_PRODUCED_PENDING_INDEPENDENT_CHECK',manifest=key(out/'controls_manifest.json'),manifest_sha256=sha(out/'controls_manifest.json',deadline),native_calls=len(runs))


def solve(args,out,pins,deadline):
    need(args.gate and args.gate_sha256,'new exact native/front-end controls gate required')
    gate=json.loads(pin(args.gate,args.gate_sha256,pins,deadline).read_bytes());need(gate['status']=='INDEPENDENT_ORIGINAL_GF3_PRIMAL_RELATION_CONTROLS_V1_PASS','new gate status')
    for path in [*CODE,args.binary,args.build_manifest]:need(gate['inputs_sha256'].get(key(path))==pins[key(path)],'new gate exact code/build/binary identity')
    need(args.endpoint_gate and args.endpoint_gate_sha256,'new independent GF3 raw endpoint checker calibration required')
    endpoint=json.loads(pin(args.endpoint_gate,args.endpoint_gate_sha256,pins,deadline).read_bytes());need(endpoint['status']=='INDEPENDENT_GF3_LITERAL_ENDPOINT_CHECKER_CALIBRATION_V1_PASS','new independent endpoint checker status')
    raw=json.loads(pin(ROOT/MODEL,MODEL_SHA,pins,deadline).read_bytes());norm=json.loads(pin(ROOT/NORM,NORM_SHA,pins,deadline).read_bytes())
    encoding=json.loads(pin(ROOT/ENCODING,ENCODING_SHA,pins,deadline).read_bytes());need(encoding['status']=='INDEPENDENT_ROOTED8_MARKED_UNIVERSAL5_PRODUCT_MODEL_PASS'and encoding['inputs_sha256'][MODEL]==MODEL_SHA,'exact conditional necessary encoding identity')
    need(len(raw['variables'])==norm['variables']==23019 and len(raw['equations'])==norm['rows']==85874,'frozen original row universe')
    text,case=encode(raw,out,deadline,norm)
    need(case['raw_divided_mod3_equivalent']and set(case['content_counts'])=={1,2,4},'exact target row contents invertible modulo3')
    save(out/'protocol.json',dict(timestamp=stamp(),source_commit=args.source_commit,inputs_sha256=pins,input_case=key(out/'input_case.json'),input_case_sha256=sha(out/'input_case.json',deadline),
        selection='One exact full ORIGINAL23019-column85874-row operator modulo3; all3affine RHS components at once. No rank claim or graph certificate.',
        success='Three complete ternary vectors satisfy every original literal RHS component modulo3, or a complete original-row coefficient relation has zeroLHS/nonzeroaffineRHS.',
        independent_requirement='Different author checks all257622raw row-component sums for3vectors, or everycolumn/affineRHS of complete selected-original-row relation; exact content/literal encoding also checked; no producer code approval.',
        target_resolution=False,independent_approval=False,rank_claim=False,prism_free_premise='UNKNOWN'))
    row=native(args,'solve',text,out,pins,deadline,[0,3,4])
    result=dict(status='ORIGINAL_LITERAL_GF3_OUTPUT_CANDIDATE_PENDING_INDEPENDENT_CHECK',run=row,inputs_sha256=pins,columns=23019,rows=85874,rank_claim=False,target_resolution=False,independent_approval=False,
        artifact_availability='LOCAL_ONLY',scope='Exact ORIGINAL literal mod3 only; integer feasibility, nonnegativity or graph existence not established. Necessary target interpretation remains conditional on UNKNOWN prism-free premise.')
    if row['actual_exit_code']==0:
        result['primal_vectors']=[dict(label=label,path=key(out/'solve'/('x_'+label+'.trits')),sha256=sha(out/'solve'/('x_'+label+'.trits'),deadline),trits=23019)for label in ['const','a','b']]
    elif row['actual_exit_code']==3:result['coefficient_relation']=dict(path=key(out/'solve/original_row_relation.json'),sha256=sha(out/'solve/original_row_relation.json',deadline),candidate_only=True)
    else:result.update(unfinished_description='not completed within allocated budget',resume_checkpoint=key(out/'solve/checkpoint.bin'),resume_checkpoint_sha256=sha(out/'solve/checkpoint.bin',deadline),automatic_resume=False)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['build','controls','solve']);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--allocation-reason',required=True)
    ap.add_argument('--source-commit',required=True);ap.add_argument('--supervision-out',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--native-seconds',type=float,required=True)
    for name in ['binary','build-manifest','gate']:ap.add_argument('--'+name,type=Path);ap.add_argument('--'+name+'-sha256')
    ap.add_argument('--endpoint-gate',type=Path);ap.add_argument('--endpoint-gate-sha256')
    ap.add_argument('--address-space-bytes',type=int,default=4*1024**3);ap.add_argument('--file-bytes',type=int,default=4*1024**3)
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason);out=args.out.resolve();need(out.is_relative_to(ROOT),'repository output');out.mkdir(parents=True,exist_ok=False);pins={}
    try:
        need(sys.platform.startswith('linux'),'supervisor and native computation inside Linux')
        need(platform.machine()=='x86_64'and sys.byteorder=='little','pinned native-endian checkpoint platform')
        for path in CODE:pin(path,None,pins,deadline)
        outer_path=args.supervision_out.resolve()/'manifest.json';outer=json.loads(pin(outer_path,None,pins,deadline).read_bytes())
        need(outer['source_sha256']==pins['acceleration/run_compute_command.py']and outer['seconds']>=args.seconds+10 and not outer['automatic_retry']and not outer['cumulative_across_commands'],'exact bounded supervisor')
        need(key(Path(__file__))in outer['command']or str(Path(__file__).resolve())in outer['command'],'actual supervised wrapper')
        group=os.getpgid(0);guard=[x.decode()for x in (Path('/proc')/str(group)/'cmdline').read_bytes().split(b'\0')if x]
        need(guard and Path(guard[0]).name=='timeout'and '--signal=KILL'in guard,'observed enclosing Linux group guard')
        save(out/'invocation.json',dict(timestamp=stamp(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=args.source_commit,inputs_sha256=pins,python=platform.python_version(),tqdm_version=__import__('tqdm').__version__,
            supervision=key(outer_path),supervision_sha256=sha(outer_path,deadline),group=group,guard_argv=guard,address_space_bytes=args.address_space_bytes,file_bytes=args.file_bytes,independent_approval=False,target_resolution=False))
        if args.mode=='build':
            need(sha(COMPILER,deadline)==COMPILER_SHA,'exact pinned compiler');version=subprocess.check_output([COMPILER,'--version'],text=True);need(version.startswith('g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0'),'pinned compiler version')
            binary=out/'literal_gf3';allowed=deadline.child_seconds(args.native_seconds,reserve_seconds=25)
            cmd=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s',f'{allowed:.6f}s','/usr/bin/prlimit',f'--as={args.address_space_bytes}:{args.address_space_bytes}',f'--fsize={args.file_bytes}:{args.file_bytes}','--core=0:0',COMPILER,'-std=c++17','-O3','-Wall','-Wextra','-Werror',str(CPP),'-o',str(binary)];execute(cmd,out/'build',[0],deadline)
            manifest=dict(schema='ORIGINAL_GF3_NATIVE_BUILD_V1',source_commit=args.source_commit,inputs_sha256=pins,binary=key(binary),binary_sha256=sha(binary,deadline),compiler=COMPILER,compiler_sha256=COMPILER_SHA,compiler_version=version,
                command=cmd,source_cpp_sha256=pins[key(CPP)],receipt=key(out/'build.receipt.json'),receipt_sha256=sha(out/'build.receipt.json',deadline),independent_approval=False)
            save(out/'build_manifest.json',manifest);result=dict(status='ORIGINAL_GF3_BUILD_PRODUCED_PENDING_INDEPENDENT_CHECK',binary=key(binary),binary_sha256=manifest['binary_sha256'],build_manifest=key(out/'build_manifest.json'),build_manifest_sha256=sha(out/'build_manifest.json',deadline))
        else:
            need(args.binary and args.binary_sha256 and args.build_manifest and args.build_manifest_sha256,'exact binary/build pins');pin(args.binary,args.binary_sha256,pins,deadline)
            build=json.loads(pin(args.build_manifest,args.build_manifest_sha256,pins,deadline).read_bytes());need(build['schema']=='ORIGINAL_GF3_NATIVE_BUILD_V1'and build['source_cpp_sha256']==pins[key(CPP)]and build['binary_sha256']==args.binary_sha256 and build['compiler_sha256']==COMPILER_SHA,'exact new source/compiler/binary binding')
            result=dict(controls=controls,solve=solve)[args.mode](args,out,pins,deadline)
        result.update(timestamp=stamp(),elapsed_seconds=deadline.status()['elapsed_seconds']);save(out/'summary.json',result);print(json.dumps(result),flush=True)
    except BaseException as error:
        save(out/'failure.json',dict(timestamp=stamp(),error=repr(error),inputs_sha256=pins,deadline=deadline.status(),outputs_preserved=True,target_resolution=False,independent_approval=False));raise


if __name__=='__main__':main()
