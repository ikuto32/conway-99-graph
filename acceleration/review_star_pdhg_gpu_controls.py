"""Independent simplex KKT and negative CLI controls for frozen cold-star CUDA."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='79593e296a4fba29882fb04b7e7dd88091dbc7f218135b6db2ba79c0b49002e8'
BINARY_SHA='9dc3ea92ca53a6ebc8dd3715f5a0586ef00b18d5c8c8b7bd4e61cb6c2ae11075'

def path(p):return (ROOT/str(p).replace('\\','/')).resolve()
def key(p):return path(p).relative_to(ROOT).as_posix()
def digest(p):return sha256(path(p).read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)

def tiny_oracle(z):
    z=list(map(Fraction,z))
    for mask in range(1,1<<len(z)):
        active=[i for i in range(len(z)) if mask>>i&1]
        theta=(sum(z[i] for i in active)-1)/len(active)
        if all((z[i]>theta)==bool(mask>>i&1) for i in range(len(z))):return [float(max(Fraction(0),v-theta)) for v in z]
    raise ValueError('No exact projection support')

def sparse_record(N,block_sizes):
    # A=[1,0,...,0], one inequality, useful for shape/cap-only controls.
    offsets=[0]
    for n in block_sizes:offsets.append(offsets[-1]+n)
    require(offsets[-1]==N,'Bad synthetic offsets')
    return (struct.pack('<5I',N,1,0,len(block_sizes),1)+struct.pack('<'+'I'*len(offsets),*offsets)+
            struct.pack('<3I',0,1,0)+struct.pack('<d',1.)+
            struct.pack('<'+'I'*(N+1),0,*([1]*N))+struct.pack('<I2d',0,1.,0.))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tiny-input',required=True);p.add_argument('--projection-output',required=True)
    p.add_argument('--gpu-source',required=True);p.add_argument('--gpu-binary',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();out=path(a.out)
    require(not out.exists(),'Fresh controls output required')
    require(digest(a.gpu_source)==SOURCE_SHA and digest(a.gpu_binary)==BINARY_SHA,'Frozen CUDA changed')
    bindings={key(p):digest(p) for p in (__file__,a.tiny_input,a.projection_output,a.gpu_source,a.gpu_binary)}
    projection=json.loads(path(a.projection_output).read_bytes())
    require(projection['status']=='NUMERICAL_SIMPLEX_PROJECTION_SELF_TEST_FINISHED' and projection['numerical_scores_are_proofs'] is False,'Wrong projection status')
    require([r['size'] for r in projection['cases']]==[3,1,2,1053,2049,8192],'Missing size controls')
    projection_checks=[]
    for record in projection['cases']:
        z,q=record['input'],record['projected'];n=record['size']
        require(len(z)==len(q)==n and all(type(v) in (int,float) and math.isfinite(v) for v in z+q) and all(v>=0 for v in q),'Malformed projection vectors')
        active=[i for i,v in enumerate(q) if v>0];require(active,'No active probability')
        theta=(math.fsum(z[i] for i in active)-1)/len(active)
        error=max(abs(math.fsum(q)-1),max(abs(q[i]-max(z[i]-theta,0)) for i in range(n)))
        require(error<=2e-12,'Projection KKT residual exceeds declared2e-12')
        exact_error=max(abs(v-w) for v,w in zip(q,tiny_oracle(z))) if n<=3 else None
        require(exact_error is None or exact_error<=2e-13,'Tiny exact simplex oracle mismatch')
        if record['name']=='extreme_negative_tail':require(q==[1.,0.,0.],'Extreme negative-tail regression')
        projection_checks.append(dict(name=record['name'],size=n,active_count=len(active),KKT_max_error=error,tiny_exact_oracle_error=exact_error))
    base=path(a.tiny_input).read_bytes();require(base[:8]==b'C99SCP01','Bad tiny input')
    count,nchecks=struct.unpack_from('<2I',base,8);require(count==4 and nchecks==3,'Unexpected tiny geometry')
    record_start=16+4*nchecks
    N,M,Q,B,nnz=struct.unpack_from('<5I',base,record_start)
    offsets=record_start+20;ar=offsets+4*(B+1);ai=ar+4*(M+1);av=ai+4*nnz
    tr=av+8*nnz;ti=tr+4*(N+1);tv=ti+4*nnz;targets=tv+8*nnz;record_end=targets+8*M
    first=base[record_start:record_end]
    def mutated(offset,fmt,value):
        data=bytearray(base);struct.pack_into(fmt,data,offset,value);return bytes(data)
    cases=[('bad_magic',b'WRONGMAG'+base[8:],()),('zero_count',mutated(8,'<I',0),()),('count257',mutated(8,'<I',257),()),
           ('zero_checkpoints',mutated(12,'<I',0),()),('checkpoints17',mutated(12,'<I',17),()),
           ('zero_iteration',mutated(16,'<I',0),()),('iteration20001',mutated(16,'<I',20001),()),('duplicate_checkpoint',mutated(20,'<I',1),()),
           ('zero_N',mutated(record_start,'<I',0),()),('M20001',mutated(record_start+4,'<I',20001),()),('Q_outside_M',mutated(record_start+8,'<I',M+1),()),
           ('zero_blocks',mutated(record_start+12,'<I',0),()),('oversized_nnz',mutated(record_start+16,'<I',8000001),()),
           ('offset_start',mutated(offsets,'<I',1),()),('empty_simplex',mutated(offsets+4,'<I',0),()),('offset_end',mutated(offsets+4*B,'<I',N-1),()),
           ('csr_start',mutated(ar,'<I',1),()),('csr_end',mutated(ar+4*M,'<I',nnz-1),()),('csr_nonmonotonic',mutated(ar+8,'<I',0),()),
           ('csr_index_range',mutated(ai,'<I',N),()),('csr_duplicate_index',mutated(ai+4,'<I',0),()),
           ('zero_coefficient',mutated(av,'<d',0.),()),('nan_coefficient',mutated(av,'<d',float('nan')),()),('inf_coefficient',mutated(av,'<d',float('inf')),()),
           ('wrong_transpose',mutated(tv,'<d',.125),()),('nan_target',mutated(targets,'<d',float('nan')),()),('oversized_target',mutated(targets,'<d',1e291),()),
           ('trailing_bytes',base+b'x',()),('truncated_tail',base[:-1],()),('truncated_header',base[:10],()),
           ('unknown_option',base,('--unknown-option',)),
           ('vectors_count17',b'C99SCP01'+struct.pack('<5I',17,3,1,2,10)+first*17,('--vectors',)),
           ('domain8193',b'C99SCP01'+struct.pack('<3I',1,1,1)+sparse_record(8193,[8193]),())]
    wrong_order=bytearray(base);struct.pack_into('<2I',wrong_order,ai,1,0);cases.append(('csr_unsorted',bytes(wrong_order),()))
    excessive=bytearray(base);struct.pack_into('<d',excessive,av,1e291);struct.pack_into('<d',excessive,tv,1e291);cases.append(('row_magnitude_cap',bytes(excessive),()))
    large=sparse_record(100000,[8192]*12+[1696])
    cases.append(('vector_entry_cap',b'C99SCP01'+struct.pack('<2I',5,16)+struct.pack('<16I',*range(1,17))+large*5,('--vectors',)))
    out.mkdir(parents=True);results=[]
    for name,data,extra in cases:
        inp=out/(name+'.bin');target=out/(name+'.json');inp.write_bytes(data)
        require(digest(a.gpu_binary)==BINARY_SHA and digest(a.gpu_source)==SOURCE_SHA,'CUDA changed during controls')
        result=subprocess.run([str(path(a.gpu_binary)),str(inp),str(target),*extra],capture_output=True,text=True,timeout=15)
        require(result.returncode!=0 and not target.exists(),'Invalid input accepted: '+name)
        bindings[key(inp)]=digest(inp)
        results.append(dict(name=name,rejected=True,exit_code=result.returncode,output_created=False,error=result.stderr.strip()))
    kept=out/'existing_output.txt';kept.write_text('KEEP\n',encoding='ascii');prior=digest(kept)
    result=subprocess.run([str(path(a.gpu_binary)),str(path(a.tiny_input)),str(kept)],capture_output=True,text=True,timeout=15)
    require(result.returncode!=0 and digest(kept)==prior,'Existing output overwritten')
    results.append(dict(name='existing_output',rejected=True,exit_code=result.returncode,output_preserved=True,error=result.stderr.strip()))
    report=dict(status='INDEPENDENT_COLD_STAR_CUDA_PROJECTION_AND_CLI_CONTROLS_PASS',inputs_sha256=bindings,
                projection_checks=projection_checks,negative_controls=results,negative_control_count=len(results),
                all_negative_controls_rejected=True,untested_large_file_limits=['2GiB input','aggregate64million nonzeros'],
                scope='Independent simplex KKT/exact tiny support checks and CLI rejection/preservation controls. No99graph or infeasibility claim. Invalid cases are parsed before native CUDA initialization by source review.')
    dump_path=out/'report.json'
    with dump_path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=report['status'],negatives=len(results),max_KKT=max(r['KKT_max_error'] for r in projection_checks),report_sha256=digest(dump_path))))

if __name__=='__main__':main()
