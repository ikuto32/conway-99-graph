"""Independent exact pair packet checker; no producer imports or work on import."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import stat
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_fixed17_dual_gram_pairs_v2.py'
SPEC = 'acceleration/audit_20261004_fixed17_dual_gram_pairs_v2_spec.md'
PRODUCER = 'acceleration/diagnose_20261004_fixed17_dual_gram_pairs_v1.py'
PRODUCER_SPEC = 'acceleration/diagnose_20261004_fixed17_dual_gram_pairs_v1_spec.md'
SOFTWARE = {
    PRODUCER: '079435a1ddf24ed19144dc103abd5e40954724bffacc8f708742418125e83373',
    PRODUCER_SPEC: '455767765eb2e01c800648a458dd56175642e6fd8786302aa55ba592154cc23d',
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'acceleration/run_compute_command_v2.py': '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}
DATA_ROOT = 'acceleration/results/20261004_fixed17_dual_gram_singletons01/'
DATA = {
    DATA_ROOT+'summary.json': 'e6d60171fb6d2d8b22e7d1eac02d68972de805ecb56329e77d75a199cb4f4be9',
    DATA_ROOT+'parsed_input.json': 'fa363f43b1e3de238c330b0b9caaf4e2c61dd8e1f7dc7044d3817b02b3b246b5',
    DATA_ROOT+'singletons.json': 'feed0822248d1e956246f27f31c16970757dd518fba9695d13e9d71f39c13026',
    DATA_ROOT+'upper_inverse_certificate.json': '22a7bcd7f178382d7a8893a8acc5f960ba69ac5e2509c2b6175c7ae22cf3c4e5',
    DATA_ROOT+'lower_inverse_certificate.json': 'f7c98ab5da93ded447730ccdd39aeb247fd51930c6e472d0cebc89231b29703b',
}
ROWS = ((0,1,2),(0,3,4),(0,5,6),(1,7,9),(1,8,10),(15,11,14),
        (16,12,13),(2,15,16),(3,7,11),(4,8,12),(5,9,13),(6,10,14))
FIELDS = ('proposal_id','i','j','left_mask','right_mask','intersection',
    'upper_left_diagonal','upper_right_diagonal','upper_cross_0','upper_cross_1',
    'lower_left_diagonal','lower_right_diagonal','lower_cross_0','lower_cross_1',
    'upper_bits','lower_bits','cn_bits','combined_bits','classification')
CLASSES = ('incompatible','forced_nonadjacent','forced_adjacent','either')
COUNTS = (*CLASSES,'cn_incompatible','additional_gram_incompatible',
          'upper_incompatible','lower_incompatible','equal_type_pairs','distinct_type_pairs')
CAL_STATUS = 'INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_PRODUCER_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS'
AUTHOR_STATUS = 'FIXED17_DUAL_GRAM_PAIR_V1_AUTHOR_CONTROLS_PASS'
AUTHOR_COUNTS = dict(positive=10,negative=41,total=51)
OWN_COUNTS = dict(positive=13,negative=58,total=71)

class Veto(ValueError):
    def __init__(self, stage):
        super().__init__(stage)
        self.stage = stage

def need(ok, stage):
    if not ok:
        raise Veto(stage)

def same(a,b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if type(a) is list:
        return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b

def q(value):
    need(type(value) is str,'RATIONAL_TYPE')
    try:
        result=Fraction(value)
    except (ValueError,ZeroDivisionError):
        raise Veto('RATIONAL_CANONICAL') from None
    need(str(result)==value,'RATIONAL_CANONICAL')
    return result

def decode(raw):
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,'JSON_DUPLICATE')
            result[key]=value
        return result
    def constant(_):
        raise Veto('JSON_CONSTANT')
    try:
        return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
    except (json.JSONDecodeError,UnicodeDecodeError):
        raise Veto('JSON_SYNTAX') from None

class Budget:
    def __init__(self,seconds):
        self.deadline=CommandDeadline(seconds,allocation_reason=
            'Independent direct Fraction pair/whole-prefix checks; all I/O shares one deadline')
    def tick(self):
        s=self.deadline.status()
        need(not s['stop_required'] and s['remaining_seconds']>20,'SAVE_RESERVE')

def safe(name,existing=True):
    p=Path(name)
    p=p if p.is_absolute() else ROOT/p
    need(p.resolve().is_relative_to(ROOT),'PATH_SCOPE')
    for part in (p,*p.parents):
        if part==ROOT.parent:
            break
        if part.exists():
            flags=getattr(part.lstat(),'st_file_attributes',0)
            need(not part.is_symlink() and not(flags & stat.FILE_ATTRIBUTE_REPARSE_POINT),'PATH_REPARSE')
    if existing:
        need(p.is_file(),'INPUT_FILE')
    return p

class Reader:
    def __init__(self,budget):
        self.budget=budget
        self.pins={}
    def read(self,name,expected,parse=True):
        self.budget.tick()
        p=safe(name)
        need(type(expected) is str and len(expected)==64,'HASH_SCHEMA')
        need(p.stat().st_size<=64*1024*1024,'INPUT_SIZE')
        h=hashlib.sha256()
        chunks=[]
        with p.open('rb') as f:
            while True:
                self.budget.tick()
                block=f.read(1024*1024)
                if not block:
                    break
                h.update(block)
                if parse:
                    chunks.append(block)
        digest=h.hexdigest()
        need(digest==expected,'INPUT_HASH')
        key=p.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key]==digest,'PIN_CONFLICT')
        self.pins[key]=digest
        self.budget.tick()
        return decode(b''.join(chunks)) if parse else None
    def closing(self):
        for p,h in list(self.pins.items()):
            self.read(p,h,False)

def save(path,value,budget):
    budget.tick()
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False)
        f.write('\n')
    budget.tick()

def inventory(base,budget):
    found=set()
    for p in base.rglob('*'):
        budget.tick()
        if p.is_dir():
            safe(p,False)
        else:
            safe(p)
            found.add(p.relative_to(base).as_posix())
    return found

def packet(reader,path,identity):
    summary=reader.read(path,identity)
    base=safe(path).parent
    outputs=summary.get('outputs_sha256')
    need(type(outputs) is dict and all(type(k) is str and type(v) is str for k,v in outputs.items()),'OUTPUT_MAP')
    need('summary.json' not in outputs and inventory(base,reader.budget)==set(outputs)|{'summary.json'},'OUTPUT_POPULATION')
    for name,digest in outputs.items():
        target=base/name
        need(target.resolve().is_relative_to(base) and target!=base,'OUTPUT_PATH')
        reader.read(target,digest,False)
    return summary,base

def inverse(payload,name,n):
    need(type(payload) is dict and payload.get('schema')=='EXACT_DUAL_GRAM_INVERSE_LDL_CERTIFICATE_V1','INVERSE_SCHEMA')
    need(payload.get('gram')==name,'INVERSE_GRAM')
    need(type(payload.get('dimension')) is int and payload['dimension']==n,'INVERSE_DIMENSION')
    a=payload.get('inverse')
    need(type(a) is list and len(a)==n and all(type(row) is list and len(row)==n for row in a),'INVERSE_SHAPE')
    matrix=[[q(x) for x in row] for row in a]
    need(all(matrix[i][j]==matrix[j][i] for i in range(n) for j in range(n)),'INVERSE_SYMMETRY')
    return matrix

def masks(raw,n,count):
    need(type(raw) is list and len(raw)==count,'MASK_POPULATION')
    need(all(type(x) is int for x in raw),'MASK_INTEGER')
    need(all(0<=x<2**n for x in raw),'MASK_RANGE')
    need(len(set(raw))==count,'MASK_DISTINCT')
    need(raw==sorted(raw),'MASK_ORDER')
    return raw

def bilinear(x,a,y):
    return sum((x[i]*a[i][j]*y[j] for i in range(len(x)) for j in range(len(y))),Fraction())

def scaled(a):
    denominator=math.lcm(*(x.denominator for row in a for x in row))
    return denominator,[[int(x*denominator) for x in row] for row in a]

class Oracle:
    """Rational b=1/9-t products; never calls producer integer context or record."""
    def __init__(self,ordered,upper,lower,budget=None):
        self.masks=ordered
        self.upper=upper
        self.lower=lower
        self.n=len(upper)
        self.d,self.N=scaled(upper)
        self.e,self.P=scaled(lower)
        supports=[{j for j in range(self.n) if m & (1<<j)} for m in ordered]
        self.t=[[int(k in support) for k in range(self.n)] for support in supports]
        self.b=[[Fraction(1,9)-x for x in row] for row in self.t]
        self.ub=[]
        self.lt=[]
        for b,t in zip(self.b,self.t):
            if budget:
                budget.tick()
            self.ub.append([sum((upper[i][j]*b[j] for j in range(self.n)),Fraction()) for i in range(self.n)])
            self.lt.append([sum((lower[i][j]*t[j] for j in range(self.n)),Fraction()) for i in range(self.n)])
        self.qu=[sum((a*b for a,b in zip(x,y)),Fraction()) for x,y in zip(self.b,self.ub)]
        self.ql=[sum((a*b for a,b in zip(x,y)),Fraction()) for x,y in zip(self.t,self.lt)]
    def expected(self,pid,i,j):
        ul=Fraction(28,9)-self.qu[i]
        ur=Fraction(28,9)-self.qu[j]
        ll=4-self.ql[i]
        lr=4-self.ql[j]
        ux=sum((a*b for a,b in zip(self.b[i],self.ub[j])),Fraction())
        lx=sum((a*b for a,b in zip(self.t[i],self.lt[j])),Fraction())
        uc=[Fraction(1,9)-a-ux for a in (0,1)]
        lc=[a-lx for a in (0,1)]
        upper=[a for a in (0,1) if ul>=0 and ur>=0 and uc[a]**2<=ul*ur]
        lower=[a for a in (0,1) if ll>=0 and lr>=0 and lc[a]**2<=ll*lr]
        left={k for k in range(self.n) if self.masks[i] & (1<<k)}
        right={k for k in range(self.n) if self.masks[j] & (1<<k)}
        overlap=len(left.intersection(right))
        cn=[a for a in (0,1) if overlap<=(2 if a==0 else 1)]
        joint=[a for a in (0,1) if a in upper and a in lower and a in cn]
        labels={():CLASSES[0],(0,):CLASSES[1],(1,):CLASSES[2],(0,1):CLASSES[3]}
        def numerator(value,scale):
            f=value*scale
            need(f.denominator==1,'ORACLE_SCALE')
            return f.numerator
        return dict(proposal_id=pid,i=i,j=j,left_mask=self.masks[i],right_mask=self.masks[j],intersection=overlap,
            upper_left_diagonal=numerator(ul,81*self.d),upper_right_diagonal=numerator(ur,81*self.d),
            upper_cross_0=numerator(uc[0],81*self.d),upper_cross_1=numerator(uc[1],81*self.d),
            lower_left_diagonal=numerator(ll,self.e),lower_right_diagonal=numerator(lr,self.e),
            lower_cross_0=numerator(lc[0],self.e),lower_cross_1=numerator(lc[1],self.e),
            upper_bits=upper,lower_bits=lower,cn_bits=cn,combined_bits=joint,classification=labels[tuple(joint)])
    def records(self,budget=None):
        pid=0
        for i,j in itertools.combinations_with_replacement(range(len(self.masks)),2):
            if budget:
                budget.tick()
            yield self.expected(pid,i,j)
            pid+=1

def check_record(raw,wanted):
    need(type(raw) is dict and set(raw)==set(FIELDS),'RECORD_KEYS')
    need(all(type(raw[k]) is int for k in FIELDS[:14]),'RECORD_INTEGER')
    need(all(type(raw[k]) is list and all(type(a) is int and a in (0,1) for a in raw[k]) for k in FIELDS[14:18]),'RECORD_BITS')
    need(type(raw['classification']) is str,'RECORD_CLASS_TYPE')
    need(same(raw,wanted),'RECORD_IDENTITY')

def empty_counts():
    return dict.fromkeys(COUNTS,0)

def count_record(counts,row):
    counts[row['classification']]+=1
    for key,test in [('cn_incompatible',not row['cn_bits']),
                     ('additional_gram_incompatible',bool(row['cn_bits']) and not row['combined_bits']),
                     ('upper_incompatible',not row['upper_bits']),('lower_incompatible',not row['lower_bits']),
                     ('equal_type_pairs',row['i']==row['j']),('distinct_type_pairs',row['i']!=row['j'])]:
        counts[key]+=int(test)

def check_part(raw,index,start,stop,wanted):
    need(type(raw) is dict and set(raw)=={'schema','part_index','start','stop','count','records'},'PART_KEYS')
    need(all(type(raw[k]) is int for k in ('part_index','start','stop','count')),'PART_INTEGER')
    need(raw['schema']=='DUAL_GRAM_PAIR_PART_V1' and raw['part_index']==index and raw['start']==start and
         raw['stop']==stop and raw['count']==stop-start,'PART_BOUNDARY')
    need(type(raw['records']) is list and len(raw['records'])==len(wanted),'PART_RECORD_POPULATION')
    for row,expected in zip(raw['records'],wanted):
        check_record(row,expected)

def checkpoint(stop,population,index,counts,identities):
    return dict(schema='DUAL_GRAM_PAIR_CHECKPOINT_V1',next_proposal_id=stop,total_pair_population=population,
                part_index=index,cumulative_counts=dict(counts),input_identity_sha256=identities)

def check_checkpoint(raw,wanted):
    need(type(raw) is dict and set(raw)==set(wanted),'CHECKPOINT_KEYS')
    need(all(type(raw[k]) is int for k in ('next_proposal_id','total_pair_population','part_index')),'CHECKPOINT_INTEGER')
    need(type(raw['cumulative_counts']) is dict and all(type(x) is int for x in raw['cumulative_counts'].values()),'CHECKPOINT_COUNT_INTEGER')
    need(same(raw,wanted),'CHECKPOINT_IDENTITY')

def stream(reader,base,outputs,oracle,identities,part_size):
    n=len(oracle.masks)
    population=n*(n+1)//2
    expected=iter(oracle.records(reader.budget))
    counts=empty_counts()
    parts=0
    for start in range(0,population,part_size):
        stop=min(start+part_size,population)
        wanted=[next(expected) for _ in range(stop-start)]
        name='part_%03d.json'%parts
        check_part(reader.read(base/name,outputs[name]),parts,start,stop,wanted)
        for row in wanted:
            count_record(counts,row)
        name='checkpoint_%03d.json'%parts
        check_checkpoint(reader.read(base/name,outputs[name]),checkpoint(stop,population,parts,counts,identities))
        parts+=1
        print(json.dumps(dict(complete_pair_records=stop,total=population,parts_checked=parts)),flush=True)
    need(next(expected,None) is None,'STREAM_EXHAUSTION')
    return dict(complete_pair_records=population,part_count=parts,checkpoint_count=parts,counts=counts,
                ordering='i increasing0..count-1; j increasing i..count-1',equal_type_means_two_distinct_external_vertices=True)

def singleton_gate(raw,expected):
    need(type(raw) is dict and raw.get('status')=='INDEPENDENT_FIXED17_DUAL_GRAM_SINGLETON_V1_COMPLETE_PASS' and
         raw.get('producer')=='/root/structural' and raw.get('verifier')=='/root/checkpoint_audit' and
         raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE' and
         type(raw.get('implementation_version')) is int and raw['implementation_version']==1,'SINGLETON_GATE_HEADER')
    need(type(raw.get('inputs_sha256')) is dict and all(raw['inputs_sha256'].get(p)==h for p,h in expected.items()),'SINGLETON_GATE_DIRECT_PINS')
    required=dict(complete_type_records=472,upper_pass=472,lower_pass=472,combined_pass=472,
                  pairs_enumerated=0,future_unordered_pairs_including_equal_types=111628)
    need(type(raw.get('outcome')) is dict and all(type(raw['outcome'].get(k)) is int and raw['outcome'][k]==v for k,v in required.items()),'SINGLETON_GATE_COUNTS')

def author_header(raw,software):
    need(type(raw) is dict and raw.get('status')==AUTHOR_STATUS and type(raw.get('implementation_version')) is int and
         raw['implementation_version']==1 and same(raw.get('source_software'),software) and
         raw.get('actual_target_input_read') is False and type(raw.get('outcome')) is dict and
         same(raw['outcome'].get('controls'),AUTHOR_COUNTS),'CALIBRATION_HEADER')

def options(words):
    need(type(words) is list and len(words)%2==0,'ARGV_PAIRS')
    result={}
    for key,value in zip(words[::2],words[1::2]):
        need(type(key) is str and key.startswith('--') and key not in result and type(value) is str,'ARGV_OPTION')
        result[key]=value
    return result

def runtime(plan,manifest,terminal,summary,mode):
    command=plan.get('command')
    child=plan.get('child_argv')
    worker=plan.get('worker_argv')
    need(type(command) is list and type(child) is list and type(worker) is list and '--' in command,'RUNTIME_PLAN')
    cut=command.index('--')
    need(same(command[cut+1:],child) and same(child[8:],worker),'RUNTIME_SUFFIX')
    need(len(worker)==(12 if mode=='calibrate' else 20) and worker[1]=='-B' and
         safe(worker[2])==ROOT/PRODUCER and worker[3]==mode,'RUNTIME_WORKER')
    need(safe(command[2])==ROOT/'acceleration/run_compute_command_v2.py','RUNTIME_SUPERVISOR')
    outer=options(command[3:cut])
    args=options(worker[4:])
    need(args['--self-sha256']==SOFTWARE[PRODUCER] and args['--spec-sha256']==SOFTWARE[PRODUCER_SPEC],'RUNTIME_SOURCE')
    need(same(manifest.get('command'),child) and manifest.get('source_sha256')==SOFTWARE['acceleration/run_compute_command_v2.py'] and
         manifest.get('runtime_scope')=='LOCAL_WINDOWS_SUSPENDED_JOB_V1' and Path(manifest.get('cwd','')).resolve()==ROOT,'RUNTIME_MANIFEST')
    for name,value in [('seconds',outer['--seconds']),('shutdown_reserve_seconds',outer['--shutdown-reserve-seconds'])]:
        actual=manifest.get(name)
        need(type(actual) in (int,float) and math.isfinite(actual) and actual==float(value),'RUNTIME_ALLOCATION')
    need(type(terminal.get('command_exit_code')) is int and terminal['command_exit_code']==0 and
         terminal.get('error') is None and terminal.get('deadline_reached') is False,'RUNTIME_EXIT')
    cleanup=terminal.get('cleanup')
    need(type(cleanup) is dict and type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code']==0 and
         all(cleanup.get(k) is True for k in ('created_suspended','resumed','reaped','job_active_zero_observed')) and
         cleanup.get('cleanup_errors')==[],'RUNTIME_CLEANUP')
    need(type(manifest.get('invocation_id')) is str and bool(manifest['invocation_id']) and
         terminal.get('invocation_id')==manifest['invocation_id'],'RUNTIME_INVOCATION')
    elapsed=terminal.get('elapsed_seconds')
    need(type(elapsed) in (int,float) and math.isfinite(elapsed) and 0<=elapsed<=manifest['seconds'],'RUNTIME_ELAPSED')
    need(same(summary.get('command'),worker[2:]) and Path(summary.get('cwd','')).resolve()==ROOT,'RUNTIME_SUMMARY_COMMAND')
    state=summary.get('deadline')
    need(type(state) is dict and state.get('stop_required') is False and type(state.get('remaining_seconds')) in (int,float) and
         math.isfinite(state['remaining_seconds']) and state['remaining_seconds']>20,'RUNTIME_WORKER_DEADLINE')
    return args

def scaled_packet(oracle,h,identities):
    n=oracle.n
    r=[[int(9*x) for x in row] for row in oracle.b]
    def whole(value):
        need(value.denominator==1,'ORACLE_SCALE')
        return value.numerator
    return dict(schema='DUAL_GRAM_PAIR_SCALED_INPUT_V1',dimension=n,ordered_masks=oracle.masks,
        induced_adjacency=h,upper_denominator=oracle.d,upper_numerator=oracle.N,
        lower_denominator=oracle.e,lower_numerator=oracle.P,upper_vectors_r=r,
        upper_products_Nr=[[whole(9*oracle.d*x) for x in row] for row in oracle.ub],
        lower_vectors=oracle.t,lower_products_Pt=[[whole(oracle.e*x) for x in row] for row in oracle.lt],
        upper_diagonals=[whole(81*oracle.d*(Fraction(28,9)-x)) for x in oracle.qu],
        lower_diagonals=[whole(oracle.e*(4-x)) for x in oracle.ql],input_identity_sha256=identities,
        inverse_generation_calls=0,original_inverse_identities_authenticated_by_gate=True)

def check_scaled(raw,wanted):
    need(type(raw) is dict and set(raw)==set(wanted),'SCALED_KEYS')
    need(same(raw,wanted),'SCALED_IDENTITY')

def identity_products(h,upper,lower,budget=None):
    n=len(h)
    grams=[[[Fraction(3*int(i==j)-h[i][j])+Fraction(1,9) for j in range(n)] for i in range(n)],
           [[Fraction(4*int(i==j)+h[i][j]) for j in range(n)] for i in range(n)]]
    for gram,submitted in zip(grams,(upper,lower)):
        for i in range(n):
            if budget:
                budget.tick()
            for j in range(n):
                left=sum((gram[i][k]*submitted[k][j] for k in range(n)),Fraction())
                right=sum((submitted[i][k]*gram[k][j] for k in range(n)),Fraction())
                need(left==int(i==j),'INVERSE_LEFT_IDENTITY')
                need(right==int(i==j),'INVERSE_RIGHT_IDENTITY')

def own_header(raw,software):
    need(type(raw) is dict and raw.get('status')==CAL_STATUS and raw.get('mode')=='calibrate' and
         type(raw.get('implementation_version')) is int and raw['implementation_version']==2 and
         raw.get('producer')=='/root/structural' and raw.get('verifier')=='/root/native_driver' and
         raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE' and
         raw.get('actual_target_input_read') is False and same(raw.get('source_software'),software) and
         type(raw.get('outcome')) is dict and same(raw['outcome'].get('controls'),OWN_COUNTS),'OWN_CALIBRATION_HEADER')

def fixture(name,n,ordered):
    if name=='triangle':
        upper=[[Fraction(int(i==j),4)+Fraction(1,6) for j in range(n)] for i in range(n)]
        lower=[[Fraction(int(i==j),3)-Fraction(1,18) for j in range(n)] for i in range(n)]
        h=[[int(i!=j) for j in range(n)] for i in range(n)]
    else:
        upper=[[Fraction(int(i==j),3)-Fraction(1,3*(27+n)) for j in range(n)] for i in range(n)]
        lower=[[Fraction(int(i==j),4) for j in range(n)] for i in range(n)]
        h=[[0]*n for _ in range(n)]
    def wire(matrix,label):
        return dict(schema='EXACT_DUAL_GRAM_INVERSE_LDL_CERTIFICATE_V1',gram=label,
                    dimension=n,inverse=[[str(x) for x in row] for row in matrix])
    return dict(upper=wire(upper,'upper'),lower=wire(lower,'lower'),masks=ordered),Oracle(ordered,upper,lower),h

def author_routes(stream_check):
    p2,o2,h2=fixture('empty',2,[0,1,2,3])
    p3,o3,h3=fixture('triangle',3,[0,1,2,7])
    p17,o17,h17=fixture('empty',17,[0,1,65536])
    up,lp=p2['upper'],p2['lower']
    baseline=o2.expected(0,0,0)
    def grid(raw,pristine,h):
        need(same(raw,pristine),'GRID_FIXTURE')
        n=len(h)
        ui=inverse(raw['upper'],'upper',n)
        li=inverse(raw['lower'],'lower',n)
        identity_products(h,ui,li)
        o=Oracle(masks(raw['masks'],n,len(pristine['masks'])),ui,li)
        for row in o.records():
            need(len(row)==19,'GRID_FIELDS')
        first=o.expected(0,0,0)
        if n==2:
            need([first[k] for k in FIELDS[6:14]]==[21870,21870,729,-6318,16,16,0,4],'HAND_EMPTY2')
        if n==3:
            need([first[k] for k in FIELDS[6:14]]==[2997,2997,81,-891,72,72,0,18],'HAND_TRIANGLE')
    def boundary(raw,wanted):
        left,right,c0,c1=raw
        bits=[]
        for a,c in enumerate((c0,c1)):
            if left>=0 and right>=0 and left*right-c*c>=0:
                bits.append(a)
        need(bits==wanted,'BOUNDARY')
    gate=dict(status='INDEPENDENT_FIXED17_DUAL_GRAM_SINGLETON_V1_COMPLETE_PASS',
        producer='/root/structural',verifier='/root/checkpoint_audit',method='independent_artifact_check',
        target_resolution='NONE',implementation_version=1,inputs_sha256={'synthetic':'pin'},
        outcome=dict(complete_type_records=472,upper_pass=472,lower_pass=472,combined_pass=472,
                     pairs_enumerated=0,future_unordered_pairs_including_equal_types=111628))
    cal=dict(status=AUTHOR_STATUS,implementation_version=1,source_software={'synthetic':'pin'},
             actual_target_input_read=False,outcome=dict(controls=AUTHOR_COUNTS))
    tiny=list(o2.records())
    counts=empty_counts()
    for rec in tiny:
        count_record(counts,rec)
    result=dict(complete_pair_records=10,part_count=4,checkpoint_count=4,counts=counts,
        ordering='i increasing0..count-1; j increasing i..count-1',equal_type_means_two_distinct_external_vertices=True)
    part=dict(schema='DUAL_GRAM_PAIR_PART_V1',part_index=0,start=0,stop=3,count=3,records=tiny[:3])
    c3=empty_counts()
    for rec in tiny[:3]:
        count_record(c3,rec)
    cp=checkpoint(3,10,0,c3,{'input':'synthetic'})
    cases=[]
    def add(name,stage,payload,fn):
        cases.append((name,stage,copy.deepcopy(payload),fn))
    add('positive_upper_scaled','PASS',up,lambda p: inverse(p,'upper',2))
    add('positive_lower_scaled','PASS',lp,lambda p: inverse(p,'lower',2))
    add('positive_full_empty2_grid','PASS',p2,lambda p:grid(p,p2,h2))
    add('positive_full_triangle_grid','PASS',p3,lambda p:grid(p,p3,h3))
    add('positive_full17_last_grid','PASS',p17,lambda p:grid(p,p17,h17))
    add('positive_upper_boundary','PASS',[1,1,1,-1],lambda p:boundary(p,[0,1]))
    add('positive_lower_boundary','PASS',[0,0,0,1],lambda p:boundary(p,[0]))
    add('positive_gate','PASS',gate,lambda p:singleton_gate(p,{'synthetic':'pin'}))
    add('positive_calibration_header','PASS',cal,lambda p:author_header(p,{'synthetic':'pin'}))
    add('positive_stream','PASS',result,lambda p:stream_check(p,o2,result))
    add('rational_bool','RATIONAL_TYPE',True,q)
    add('rational_alias','RATIONAL_CANONICAL','2/2',q)
    for name,key,value,stage in [
        ('inverse_schema','schema','wrong','INVERSE_SCHEMA'),('inverse_gram','gram','lower','INVERSE_GRAM'),
        ('inverse_dimension_bool','dimension',True,'INVERSE_DIMENSION'),('inverse_dimension_wrong','dimension',3,'INVERSE_DIMENSION'),
        ('inverse_shape','inverse',[['1']],'INVERSE_SHAPE')]:
        p=copy.deepcopy(up);p[key]=value
        add(name,stage,p,lambda p:inverse(p,'upper',2))
    for name,i,j,value,stage in [('inverse_entry_bool',0,0,False,'RATIONAL_TYPE'),
        ('inverse_asymmetric',0,1,'0','INVERSE_SYMMETRY'),('inverse_last_bool',1,1,True,'RATIONAL_TYPE')]:
        p=copy.deepcopy(up);p['inverse'][i][j]=value
        add(name,stage,p,lambda p:inverse(p,'upper',2))
    for name,value,stage in [('mask_bool',[False,1,2,3],'MASK_INTEGER'),
        ('mask_float',[0.0,1,2,3],'MASK_INTEGER'),('mask_negative',[-1,1,2,3],'MASK_RANGE'),
        ('mask_high',[0,1,2,4],'MASK_RANGE'),('mask_duplicate',[0,1,1,3],'MASK_DISTINCT'),
        ('mask_order',[0,2,1,3],'MASK_ORDER'),('mask_short',[0,1,2],'MASK_POPULATION')]:
        add(name,stage,value,lambda p:masks(p,2,4))
    for name,key,value,stage in [('record_keys','extra',1,'RECORD_KEYS'),
        ('record_integer_bool','i',False,'RECORD_INTEGER'),('record_index_wrong','proposal_id',1,'RECORD_IDENTITY'),
        ('record_bits_bool','cn_bits',[False,1],'RECORD_BITS'),('record_combined_wrong','combined_bits',[],'RECORD_IDENTITY'),
        ('record_cross_wrong','upper_cross_0',baseline['upper_cross_0']+1,'RECORD_IDENTITY'),
        ('record_class_wrong','classification','incompatible','RECORD_IDENTITY')]:
        p=copy.deepcopy(baseline);p[key]=value
        add(name,stage,p,lambda p:check_record(p,baseline))
    for name,key,value in [('gate_bool_version','implementation_version',True),('gate_method','method','independent_derivation'),
        ('gate_verifier','verifier','/root/structural'),('gate_status','status','CANDIDATE')]:
        p=copy.deepcopy(gate);p[key]=value
        add(name,'SINGLETON_GATE_HEADER',p,lambda p:singleton_gate(p,{'synthetic':'pin'}))
    p=copy.deepcopy(gate);p['inputs_sha256']['synthetic']='wrong'
    add('gate_pin','SINGLETON_GATE_DIRECT_PINS',p,lambda p:singleton_gate(p,{'synthetic':'pin'}))
    for name,key,value in [('gate_bool_outcome','pairs_enumerated',False),('gate_incomplete_outcome','complete_type_records',471)]:
        p=copy.deepcopy(gate);p['outcome'][key]=value
        add(name,'SINGLETON_GATE_COUNTS',p,lambda p:singleton_gate(p,{'synthetic':'pin'}))
    add('json_duplicate','JSON_DUPLICATE','{"x":0,"x":1}',decode)
    add('json_constant','JSON_CONSTANT','{"x":NaN}',decode)
    for name,key,value,stage in [('part_bool_count','count',True,'PART_INTEGER'),
        ('part_boundary','stop',4,'PART_BOUNDARY'),('part_drop_record','records',tiny[:2],'PART_RECORD_POPULATION')]:
        p=copy.deepcopy(part);p[key]=value
        add(name,stage,p,lambda p:check_part(p,0,0,3,tiny[:3]))
    for name,key,value,stage in [('checkpoint_bool_next','next_proposal_id',True,'CHECKPOINT_INTEGER'),
        ('checkpoint_bool_count','cumulative_counts',{**cp['cumulative_counts'],'either':True},'CHECKPOINT_COUNT_INTEGER'),
        ('checkpoint_identity','input_identity_sha256',{'input':'wrong'},'CHECKPOINT_IDENTITY')]:
        p=copy.deepcopy(cp);p[key]=value
        add(name,stage,p,lambda p:check_checkpoint(p,cp))
    p=copy.deepcopy(cal);p['implementation_version']=True
    add('calibration_bool_version','CALIBRATION_HEADER',p,lambda p:author_header(p,{'synthetic':'pin'}))
    p=copy.deepcopy(cal);p['outcome']['controls']['positive']=True
    add('calibration_bool_count','CALIBRATION_HEADER',p,lambda p:author_header(p,{'synthetic':'pin'}))
    need(len(cases)==51,'AUTHOR_ROUTE_POPULATION')
    return cases

def synthetic_runtime():
    py=(ROOT/'build/research-venv/Scripts/python.exe').as_posix()
    sup=(ROOT/'acceleration/run_compute_command_v2.py').as_posix()
    worker=[py,'-B',(ROOT/PRODUCER).as_posix(),'calibrate','--seconds','100','--out','synthetic',
            '--self-sha256',SOFTWARE[PRODUCER],'--spec-sha256',SOFTWARE[PRODUCER_SPEC]]
    child=['uv','run','--locked','--offline','--cache-dir','cache','--python',py,*worker]
    command=[py,'-B',sup,'--seconds','120','--shutdown-reserve-seconds','20','--',*child]
    plan=dict(command=command,child_argv=child,worker_argv=worker)
    manifest=dict(command=child,source_sha256=SOFTWARE['acceleration/run_compute_command_v2.py'],
        runtime_scope='LOCAL_WINDOWS_SUSPENDED_JOB_V1',cwd=str(ROOT),seconds=120.0,shutdown_reserve_seconds=20.0,invocation_id='synthetic')
    terminal=dict(command_exit_code=0,error=None,deadline_reached=False,invocation_id='synthetic',elapsed_seconds=1.0,
        cleanup=dict(actual_exit_code=0,created_suspended=True,resumed=True,reaped=True,job_active_zero_observed=True,cleanup_errors=[]))
    summary=dict(command=worker[2:],cwd=str(ROOT),deadline=dict(stop_required=False,remaining_seconds=99.0))
    return dict(plan=plan,manifest=manifest,terminal=terminal,summary=summary)

def calibrate(out,budget,software):
    reader=Reader(budget)
    _,o,h=fixture('empty',2,[0,1,2,3])
    tiny=out/'synthetic_stream'
    tiny.mkdir()
    records=list(o.records(budget))
    counts=empty_counts()
    local_outputs={}
    for index,start in enumerate(range(0,10,3)):
        stop=min(start+3,10)
        part=dict(schema='DUAL_GRAM_PAIR_PART_V1',part_index=index,start=start,stop=stop,count=stop-start,records=records[start:stop])
        for row in records[start:stop]:
            count_record(counts,row)
        for name,value in [('part_%03d.json'%index,part),('checkpoint_%03d.json'%index,checkpoint(stop,10,index,counts,{'input':'synthetic'}))]:
            save(tiny/name,value,budget)
            local_outputs[name]=hashlib.sha256((tiny/name).read_bytes()).hexdigest()
    def stream_control(raw,oracle,wanted):
        result=stream(reader,tiny,local_outputs,oracle,{'input':'synthetic'},3)
        need(same(raw,wanted) and same(result,wanted),'STREAM_REFERENCE')
    cases=author_routes(stream_control)
    conflict=dict(upper=[['243/128']],lower=[['9/4']],masks=[1])
    def conflict_check(p):
        c=Oracle(p['masks'],[[q(x) for x in row] for row in p['upper']],[[q(x) for x in row] for row in p['lower']])
        row=c.expected(0,0,0)
        need(row['upper_bits']==[0] and row['lower_bits']==[1] and row['cn_bits']==[0,1] and
             row['combined_bits']==[] and row['classification']=='incompatible','SAME_BIT_CONFLICT')
    own=dict(status=CAL_STATUS,mode='calibrate',implementation_version=2,producer='/root/structural',
        verifier='/root/native_driver',method='independent_artifact_check',target_resolution='NONE',
        actual_target_input_read=False,source_software={'synthetic':'pin'},outcome=dict(controls=OWN_COUNTS))
    cases.extend([('positive_same_bit_conflict','PASS',conflict,conflict_check),
                  ('positive_own_qualification','PASS',own,lambda p:own_header(p,{'synthetic':'pin'}))])
    late=records[-1]
    for name,key,value,stage in [('late_mask_bool','left_mask',True,'RECORD_INTEGER'),
        ('late_lower_cross','lower_cross_1',late['lower_cross_1']+1,'RECORD_IDENTITY'),
        ('late_upper_diagonal','upper_left_diagonal',-1,'RECORD_IDENTITY')]:
        p=copy.deepcopy(late);p[key]=value
        cases.append((name,stage,p,lambda p:check_record(p,late)))
    sc=scaled_packet(o,h,{'synthetic':'pin'})
    for name,change in [('scaled_numerator',lambda p:p['upper_numerator'][1].__setitem__(1,p['upper_numerator'][1][1]+1)),
        ('scaled_last_vector',lambda p:p['upper_vectors_r'][-1].__setitem__(-1,0)),
        ('scaled_denominator_bool',lambda p:p.__setitem__('upper_denominator',True))]:
        p=copy.deepcopy(sc);change(p)
        cases.append((name,'SCALED_IDENTITY',p,lambda p:check_scaled(p,sc)))
    rt=synthetic_runtime()
    def run_runtime(p):
        runtime(p['plan'],p['manifest'],p['terminal'],p['summary'],'calibrate')
    cases.append(('positive_runtime','PASS',copy.deepcopy(rt),run_runtime))
    for name,change,stage in [
        ('runtime_exit_bool',lambda p:p['terminal'].__setitem__('command_exit_code',False),'RUNTIME_EXIT'),
        ('runtime_source_wrong',lambda p:p['manifest'].__setitem__('source_sha256','wrong'),'RUNTIME_MANIFEST'),
        ('runtime_live_job',lambda p:p['terminal']['cleanup'].__setitem__('job_active_zero_observed',False),'RUNTIME_CLEANUP'),
        ('runtime_invocation_wrong',lambda p:p['terminal'].__setitem__('invocation_id','other'),'RUNTIME_INVOCATION'),
        ('runtime_elapsed_inf',lambda p:p['terminal'].__setitem__('elapsed_seconds','inf'),'RUNTIME_ELAPSED'),
        ('runtime_command_wrong',lambda p:p['summary'].__setitem__('command',p['summary']['command'][1:]),'RUNTIME_SUMMARY_COMMAND')]:
        p=copy.deepcopy(rt);change(p)
        cases.append((name,stage,p,run_runtime))
    for name,change in [('own_missing_pin',lambda p:p.__setitem__('source_software',{})),
                       ('own_bool_version',lambda p:p.__setitem__('implementation_version',True)),
                       ('own_bool_count',lambda p:p['outcome']['controls'].__setitem__('positive',True))]:
        p=copy.deepcopy(own);change(p)
        cases.append((name,'OWN_CALIBRATION_HEADER',p,lambda p:own_header(p,{'synthetic':'pin'})))
    # Exercise the ACTUAL full-mode identity_products helper, not a parallel predicate.
    # Right-only first-coordinate failure deliberately uses a nonsymmetric helper
    # argument; the public inverse parser would separately reject its asymmetry.
    for name,right in [('inverse_left_corrupt',False),('inverse_right_corrupt',True)]:
        p=dict(h=h,upper=[[str(x) for x in row] for row in o.upper],
               lower=[[str(x) for x in row] for row in o.lower])
        row,column=(0,1) if right else (0,0)
        p['upper'][row][column]=str(q(p['upper'][row][column])+1)
        def product_control(p):
            ui=[[q(x) for x in row] for row in p['upper']]
            li=[[q(x) for x in row] for row in p['lower']]
            identity_products(p['h'],ui,li,budget)
        cases.append((name,'INVERSE_RIGHT_IDENTITY' if right else 'INVERSE_LEFT_IDENTITY',p,product_control))
    need(len(cases)==71 and sum(stage=='PASS' for _,stage,_,_ in cases)==13,'OWN_ROUTE_POPULATION')
    rows=[]
    for name,expected,payload,function in cases:
        budget.tick()
        save(out/('control_'+name+'.json'),payload,budget)
        actual='PASS'
        try:
            function(copy.deepcopy(payload))
        except Veto as exc:
            actual=exc.stage
        rows.append(dict(name=name,expected_stage=expected,actual_stage=actual))
        need(expected==actual,'OWN_CONTROL_STAGE:'+name)
    save(out/'controls.json',rows,budget)
    return dict(controls=OWN_COUNTS,fraction_fixture_pairs=26,durable_stream_records=10,
                same_adjacency_bit_conflict_exercised=True,actual_target_input_read=False)


def map_rehash(reader,identities):
    need(type(identities) is dict,'INPUT_MAP')
    for name,digest in identities.items():
        reader.read(name,digest,False)


def qualify_own(reader,path,digest,software):
    # Snapshot source applicability before pinning the calibration summary itself.
    source_snapshot=dict(software)
    summary,base=packet(reader,path,digest)
    own_header(summary,source_snapshot)
    need(same(summary.get('inputs_sha256'),source_snapshot),'OWN_CALIBRATION_INPUT_MAP')
    names={'control_'+name+'.json' for name in control_names()}
    names.add('controls.json')
    names.update('synthetic_stream/'+kind+'_%03d.json'%i for i in range(4) for kind in ('part','checkpoint'))
    need(set(summary['outputs_sha256'])==names,'OWN_CALIBRATION_OUTPUT_POPULATION')
    rows=reader.read(base/'controls.json',summary['outputs_sha256']['controls.json'])
    need(type(rows) is list and len(rows)==OWN_COUNTS['total'],'OWN_CALIBRATION_CONTROL_POPULATION')
    expected=control_names()
    need([row.get('name') for row in rows]==expected and all(
        type(row) is dict and set(row)=={'name','expected_stage','actual_stage'} and
        type(row['expected_stage']) is str and row['expected_stage']==row['actual_stage'] for row in rows),
        'OWN_CALIBRATION_CONTROL_ROWS')
    need(sum(row['expected_stage']=='PASS' for row in rows)==OWN_COUNTS['positive'],'OWN_CALIBRATION_CONTROL_COUNTS')
    map_rehash(reader,summary['inputs_sha256'])
    return summary


def control_names():
    # Public order of freshly qualified control payloads; no evaluation or I/O here.
    names=[name for name,_,_,_ in author_routes(lambda *_:None)]
    names+=['positive_same_bit_conflict','positive_own_qualification',
        'late_mask_bool','late_lower_cross','late_upper_diagonal',
        'scaled_numerator','scaled_last_vector','scaled_denominator_bool','positive_runtime',
        'runtime_exit_bool','runtime_source_wrong','runtime_live_job','runtime_invocation_wrong',
        'runtime_elapsed_inf','runtime_command_wrong','own_missing_pin','own_bool_version','own_bool_count',
        'inverse_left_corrupt','inverse_right_corrupt']
    need(len(names)==OWN_COUNTS['total'] and len(set(names))==len(names),'OWN_CONTROL_NAMES')
    return names


def producer_packet(reader,args,mode):
    plan=reader.read(args.producer_plan,args.producer_plan_sha256)
    summary,base=packet(reader,args.producer_summary,args.producer_summary_sha256)
    manifest=reader.read(args.producer_manifest,args.producer_manifest_sha256)
    terminal=reader.read(args.producer_terminal,args.producer_terminal_sha256)
    flags=runtime(plan,manifest,terminal,summary,mode)
    need(safe(flags['--out'],False)==base,'RUNTIME_OUTPUT_ROOT')
    need(summary.get('producer')=='/root/structural' and summary.get('target_resolution')=='NONE' and
         summary.get('independent_approval') is False and summary.get('automatic_retry') is False and
         type(summary.get('LP_calls')) is int and summary['LP_calls']==0 and
         type(summary.get('inverse_generation_calls')) is int and summary['inverse_generation_calls']==0,
         'PRODUCER_SCOPE')
    need(summary.get('complete_ancestor_closure_rehashed') is False and
         summary.get('conditional_fixed_induced17_only') is True,'PRODUCER_LIMITATIONS')
    return summary,base,flags


def producer_controls(reader,args,out):
    summary,base,_=producer_packet(reader,args,'calibrate')
    source={PRODUCER:SOFTWARE[PRODUCER],PRODUCER_SPEC:SOFTWARE[PRODUCER_SPEC]}
    author_header(summary,source)
    need(same(summary.get('inputs_sha256'),source) and summary.get('pairs_launched') is False,'AUTHOR_CALIBRATION_INPUT_MAP')
    need(same(summary['outcome'],dict(controls=AUTHOR_COUNTS,complete_fraction_reference_pairs=26,
        synthetic_stream_pairs=10,actual_target_input_read=False)),'AUTHOR_CALIBRATION_OUTCOME')
    outputs=summary['outputs_sha256']
    _,oracle,_=fixture('empty',2,[0,1,2,3])
    def replay_stream(raw,o,wanted):
        result=stream(reader,base/'synthetic_stream',
            {name.removeprefix('synthetic_stream/'):h for name,h in outputs.items() if name.startswith('synthetic_stream/')},
            o,{'input':'synthetic'},3)
        need(same(raw,wanted) and same(result,wanted),'STREAM_REFERENCE')
    routes=author_routes(replay_stream)
    expected_names={name+'.json' for name,_,_,_ in routes}|{'controls.json'}
    expected_names.update('synthetic_stream/'+kind+'_%03d.json'%i for i in range(4) for kind in ('part','checkpoint'))
    need(set(outputs)==expected_names and len(outputs)==60,'AUTHOR_OUTPUT_POPULATION')
    rows=reader.read(base/'controls.json',outputs['controls.json'])
    need(type(rows) is list and len(rows)==51,'AUTHOR_CONTROL_POPULATION')
    checked=[]
    for row,(name,stage,pristine,function) in zip(rows,routes):
        reader.budget.tick()
        need(same(row,dict(name=name,expected_stage=stage,actual_stage=stage)),'AUTHOR_CONTROL_ROW')
        actual_payload=reader.read(base/(name+'.json'),outputs[name+'.json'])
        need(same(actual_payload,pristine),'AUTHOR_CONTROL_PAYLOAD')
        actual='PASS'
        try:
            function(copy.deepcopy(actual_payload))
        except Veto as exc:
            actual=exc.stage
        need(actual==stage,'AUTHOR_INDEPENDENT_STAGE:'+name)
        checked.append(dict(name=name,producer_expected_stage=stage,producer_actual_stage=row['actual_stage'],independent_actual_stage=actual))
    save(out/'producer_control_stage_pairs.json',checked,reader.budget)
    map_rehash(reader,summary['inputs_sha256'])
    return dict(complete_author_controls=AUTHOR_COUNTS,complete_independent_stage_pairs=51,
        full_fraction_fixture_pairs=26,complete_durable_stream_records=10,complete_parts=4,
        complete_checkpoints=4,complete_raw_physical_files=61,actual_target_input_read=False)


def controls_gate(raw,software):
    need(type(raw) is dict and raw.get('status')==CONTROLS_STATUS and raw.get('mode')=='controls' and
         type(raw.get('implementation_version')) is int and raw['implementation_version']==2 and
         raw.get('producer')=='/root/structural' and raw.get('verifier')=='/root/native_driver' and
         raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE' and
         raw.get('actual_target_input_read') is False and same(raw.get('source_software'),software),
         'INDEPENDENT_CONTROLS_HEADER')
    expected=dict(complete_author_controls=AUTHOR_COUNTS,complete_independent_stage_pairs=51,
        full_fraction_fixture_pairs=26,complete_durable_stream_records=10,complete_parts=4,
        complete_checkpoints=4,complete_raw_physical_files=61,actual_target_input_read=False)
    need(same(raw.get('outcome'),expected),'INDEPENDENT_CONTROLS_OUTCOME')


def full(reader,args,out,software):
    controls,controls_base=packet(reader,args.producer_controls,args.producer_controls_sha256)
    controls_gate(controls,software)
    map_rehash(reader,controls.get('inputs_sha256'))
    need(set(controls['outputs_sha256'])=={'producer_control_stage_pairs.json'},'INDEPENDENT_CONTROLS_OUTPUTS')
    summary,base,flags=producer_packet(reader,args,'pairs')
    source={PRODUCER:SOFTWARE[PRODUCER],PRODUCER_SPEC:SOFTWARE[PRODUCER_SPEC]}
    need(summary.get('status')=='CANDIDATE_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE' and
         type(summary.get('implementation_version')) is int and summary['implementation_version']==1 and
         same(summary.get('source_software'),source) and summary.get('actual_target_input_read') is True and
         summary.get('pairs_launched') is True,'SCIENTIFIC_HEADER')
    gate=reader.read(flags['--singleton-gate'],flags['--singleton-gate-sha256'])
    singleton_gate(gate,DATA)
    map_rehash(reader,gate['inputs_sha256'])
    cal,cal_base=packet(reader,flags['--calibration'],flags['--calibration-sha256'])
    author_header(cal,source)
    # The producer's exact author calibration is the previously independently replayed one.
    cal_key=safe(flags['--calibration']).relative_to(ROOT).as_posix()
    need(controls['inputs_sha256'].get(cal_key)==flags['--calibration-sha256'],'SCIENTIFIC_AUTHOR_CALIBRATION_BINDING')
    raw={p:reader.read(p,h) for p,h in DATA.items()}
    decoded=raw[DATA_ROOT+'parsed_input.json']
    need(type(decoded) is dict and decoded.get('schema')=='FIXED17_DUAL_GRAM_PARSED_INPUT_V1' and
         same(decoded.get('support_vertices'),list(range(17))),'FIXED_INPUT_HEADER')
    h=[[0]*17 for _ in range(17)]
    for triple in ROWS:
        for i,j in itertools.combinations(triple,2):
            h[i][j]=h[j][i]=1
    need(same(decoded.get('induced_adjacency'),h),'FIXED_INPUT_ALL289')
    ordered=masks(decoded.get('ordered_masks'),17,472)
    upper=inverse(raw[DATA_ROOT+'upper_inverse_certificate.json'],'upper',17)
    lower=inverse(raw[DATA_ROOT+'lower_inverse_certificate.json'],'lower',17)
    identity_products(h,upper,lower,reader.budget)
    oracle=Oracle(ordered,upper,lower,reader.budget)
    old=raw[DATA_ROOT+'singletons.json']
    need(type(old) is list and len(old)==472,'SINGLETON_POPULATION')
    for i,row in enumerate(old):
        reader.budget.tick()
        need(type(row) is dict and type(row.get('index')) is int and row['index']==i and
             type(row.get('mask')) is int and row['mask']==ordered[i],'SINGLETON_COORDINATES')
        need(q(row.get('upper_margin'))==Fraction(28,9)-oracle.qu[i] and
             q(row.get('lower_margin'))==4-oracle.ql[i],'SINGLETON_RATIONAL_ADAPTER')
    # Path strings are preserved exactly as producer Path arguments serialize them.
    identities={**DATA,str(Path(flags['--singleton-gate'])):flags['--singleton-gate-sha256']}
    expected_inputs={**source,**identities,str(Path(flags['--calibration'])):flags['--calibration-sha256']}
    need(same(summary.get('inputs_sha256'),expected_inputs),'SCIENTIFIC_INPUT_MAP')
    outputs=summary['outputs_sha256']
    expected_outputs={'scaled_input.json'}|{kind+'_%03d.json'%i for i in range(23) for kind in ('part','checkpoint')}
    need(set(outputs)==expected_outputs and len(outputs)==47,'SCIENTIFIC_OUTPUT_POPULATION')
    check_scaled(reader.read(base/'scaled_input.json',outputs['scaled_input.json']),scaled_packet(oracle,h,identities))
    aggregate=stream(reader,base,outputs,oracle,identities,5000)
    need(aggregate['complete_pair_records']==111628 and aggregate['part_count']==23 and
         aggregate['checkpoint_count']==23 and aggregate['counts']['equal_type_pairs']==472 and
         aggregate['counts']['distinct_type_pairs']==111156,'SCIENTIFIC_COMPLETE_POPULATION')
    need(same(summary.get('outcome'),aggregate),'SCIENTIFIC_AGGREGATE')
    save(out/'independent_aggregate.json',aggregate,reader.budget)
    map_rehash(reader,summary['inputs_sha256'])
    return dict(complete_pair_records=111628,complete_record_fields=19,complete_parts=23,complete_checkpoints=23,
        final_part_records=1628,complete_scaled_type_vectors=472,complete_induced_adjacency_entries=289,
        complete_submitted_inverse_product_entries=1156,inverse_products_include_left_and_right=True,
        equal_types_are_distinct_external_vertices=True,same_adjacency_bit_required=True,
        complete_raw_physical_files=48,aggregate=aggregate,actual_target_input_read=True)


def output_hashes(out,budget):
    result={}
    for name in sorted(inventory(out,budget)):
        p=out/name
        h=hashlib.sha256()
        with p.open('rb') as f:
            while True:
                budget.tick()
                block=f.read(1024*1024)
                if not block:
                    break
                h.update(block)
        result[name]=h.hexdigest()
        budget.tick()
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=['calibrate','controls','full'])
    ap.add_argument('--seconds',required=True,type=float)
    ap.add_argument('--out',required=True)
    ap.add_argument('--self-sha256',required=True)
    ap.add_argument('--spec-sha256',required=True)
    for name in ('calibration','producer-plan','producer-summary','producer-manifest','producer-terminal','producer-controls'):
        ap.add_argument('--'+name)
        ap.add_argument('--'+name+'-sha256')
    args=ap.parse_args()
    budget=Budget(args.seconds)
    reader=Reader(budget)
    out=safe(args.out,False)
    need(out.resolve().is_relative_to(ROOT/'acceleration/results/20261004_independent_review'),'OUTPUT_SCOPE')
    need(not out.exists(),'OUTPUT_EXISTS')
    out.mkdir(parents=True)
    software={**SOFTWARE,SELF:args.self_sha256,SPEC:args.spec_sha256}
    try:
        for p,h in software.items():
            reader.read(p,h,False)
        if args.mode=='calibrate':
            result=calibrate(out,budget,software)
            status=CAL_STATUS
        else:
            required=['calibration','producer_plan','producer_summary','producer_manifest','producer_terminal']
            if args.mode=='full':
                required.append('producer_controls')
            need(all(getattr(args,k) is not None and getattr(args,k+'_sha256') is not None for k in required),'ENDPOINT_ARGUMENTS')
            qualify_own(reader,args.calibration,args.calibration_sha256,software)
            if args.mode=='controls':
                result=producer_controls(reader,args,out)
                status=CONTROLS_STATUS
            else:
                result=full(reader,args,out,software)
                status=FULL_STATUS
        reader.closing()
        outputs=output_hashes(out,budget)
        report=dict(status=status,implementation_version=2,mode=args.mode,timestamp=datetime.now(timezone.utc).isoformat(),
            producer='/root/structural',verifier='/root/native_driver',checker_author='/root/native_driver',
            method='independent_artifact_check',target_resolution='NONE',source_software=software,
            outcome=result,inputs_sha256=dict(reader.pins),outputs_sha256=outputs,command=sys.argv,
            actual_target_input_read=args.mode=='full',LP_calls=0,inverse_generation_calls=0,
            LDL_factor_generation_calls=0,mathematical_model_generation_calls=0,automatic_retry=False,
            ledger_index_mutations=0,complete_ancestor_evidence_closure_rehashed=False,
            shared_components=['Python Fraction/json/SHA, literal coordinate and field contracts, command_deadline and SUP2',
                'Known analytic empty-H/K3 fixtures shared with producer; no producer algorithms imported',
                'Positive-definite submitted inverse qualification is inherited explicitly from genuine independent singleton gate; both inverse products are independently rechecked'],
            limitations='Conditional fixed induced17/ordered472 necessary pair tests only. Equal types mean distinct outside vertices. No integer/graph completion, target exclusion, maximal-clique census or small-type unit-multiplicity cut. Twenty-second reserve is guarded intent, not hard-real-time proof.',
            deadline=budget.deadline.status())
        save(out/'summary.json',report,budget)
        reader.closing()
        budget.tick()
        return 0
    except BaseException as exc:
        try:
            with (out/'failure.json').open('x',encoding='utf8') as f:
                json.dump(dict(status='FAILED_OR_NOT_COMPLETED_WITH_ALLOCATED_BUDGET',
                    stage=getattr(exc,'stage',type(exc).__name__),reason=str(exc),deadline=budget.deadline.status(),
                    target_resolution='NONE',provisional_summary_is_not_a_gate=True,automatic_retry=False,
                    pending_suffix_saved=False),f,indent=2,allow_nan=False)
                f.write('\n')
        except OSError:
            pass
        raise


if __name__=='__main__':
    raise SystemExit(main())
