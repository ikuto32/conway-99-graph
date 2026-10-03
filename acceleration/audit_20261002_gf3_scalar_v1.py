"""Independent exact ORIGINAL-row GF3 scalar checker and tiny calibration.

No producer imports, solver execution or packed arithmetic. DIVIDED mode is
an explicitly distinct toy/control operator, never the native original scope.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'docs/AUDIT_20261002_GF3_SCALAR_CHECKING_PROTOCOL.md'
DESIGN=ROOT/'acceleration/design_20261002_rooted8_gf3_v2.md'
DESIGN_SHA='35c8aeb8585adc5f8ad7f778474affe2adb0c2001c53769a11976ed87a2203e2'


def require(ok,message):
    if not ok:raise ValueError(message)


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def literal(row):return json.dumps(row,sort_keys=True,separators=(',',':')).encode('ascii')


def row_data(row,n,mode='original',divisor=None):
    require(mode in ('original','divided'),'GF3_OPERATOR_MODE')
    require(type(row)is dict and type(row.get('terms'))is list and type(row.get('rhs_affine'))is list and len(row['rhs_affine'])==3,'GF3_RAW_ROW_SYNTAX')
    require(all(type(term)is list and len(term)==2 and type(term[0])is int and 0<=term[0]<n and type(term[1])is int for term in row['terms'])and all(type(c)is int for c in row['rhs_affine']),'GF3_RAW_ROW_SYNTAX')
    values=[c for j,c in row['terms']]+row['rhs_affine'];content=math.gcd(*values)or 1
    if divisor is not None:
        require(type(divisor)is int and divisor>0 and all(c%divisor==0 for c in values),'GF3_POSITIVE_DIVIDING_CONTENT');content=divisor
    raw={'terms':[list(term)for term in row['terms']],'rhs_affine':list(row['rhs_affine'])}
    divided={'terms':[[j,c//content]for j,c in row['terms']],'rhs_affine':[c//content for c in row['rhs_affine']]}
    require(all([j,content*c]==term for term,(j,c)in zip(raw['terms'],divided['terms']))and [content*c for c in divided['rhs_affine']]==raw['rhs_affine'],'GF3_INTEGER_CONTENT_ROUNDTRIP')
    return content,(raw if mode=='original'else divided)


def scalar_vectors(model,vectors,mode='original'):
    n=len(model['variables']);require(len(vectors)==3 and all(len(v)==n and all(type(x)is int and x in (0,1,2)for x in v)for v in vectors),'GF3_FULL_TRIT_VECTOR_SYNTAX')
    for row in model['equations']:
        _,raw=row_data(row,n,mode)
        for component,vector in enumerate(vectors):require((sum(c*vector[j]for j,c in raw['terms'])-raw['rhs_affine'][component])%3==0,'GF3_'+mode.upper()+'_PRIMAL_SCALAR_ROW')


def scalar_relation(model,weights,residue,mode='original'):
    n=len(model['variables']);m=len(model['equations'])
    require(type(weights)is list and weights and all(type(term)is list and len(term)==2 and type(term[0])is int and 0<=term[0]<m and type(term[1])is int and term[1]in (1,2)for term in weights),'GF3_ROW_RELATION_SYNTAX')
    indices=[term[0]for term in weights];require(indices==sorted(set(indices))and type(residue)is list and len(residue)==3 and all(type(c)is int and c in (0,1,2)for c in residue)and any(residue),'GF3_ROW_RELATION_SYNTAX')
    lhs=[0]*n;rhs=[0]*3
    for i,weight in weights:
        _,row=row_data(model['equations'][i],n,mode)
        for j,c in row['terms']:lhs[j]+=weight*c
        for component,c in enumerate(row['rhs_affine']):rhs[component]+=weight*c
    require(not any(c%3 for c in lhs)and [c%3 for c in rhs]==residue,'GF3_'+mode.upper()+'_ROW_RELATION_SCALAR')
    return {'lhs_exact_integer_sums':lhs,'rhs_exact_integer_sums':rhs,'rhs_mod3':list(residue),'selected_rows':indices,'weights':weights,'operator_mode':mode}


def sparse_bytes(model,mode='original'):
    n=len(model['variables']);lines=[f'GF3_AFFINE_SPARSE_V1 {n} {len(model["equations"])}\n']
    for row in model['equations']:
        _,raw=row_data(row,n,mode);columns=Counter()
        for j,c in raw['terms']:columns[j]+=c
        terms=[[j,c%3]for j,c in sorted(columns.items())if c%3]
        lines.append(' '.join(map(str,[*[c%3 for c in raw['rhs_affine']],len(terms),*[x for term in terms for x in term]]))+'\n')
    return ''.join(lines).encode('ascii')


def read_sparse(raw):
    try:lines=raw.decode('ascii').splitlines()
    except UnicodeDecodeError:raise ValueError('GF3_SPARSE_SYNTAX')
    require(raw.endswith(b'\n')and lines,'GF3_SPARSE_SYNTAX');header=lines[0].split()
    require(len(header)==3 and header[0]=='GF3_AFFINE_SPARSE_V1' and all(t.isdecimal()for t in header[1:]),'GF3_SPARSE_SYNTAX')
    n,m=map(int,header[1:]);require(n>0 and m>0 and len(lines)==m+1,'GF3_SPARSE_SYNTAX');rows=[]
    for line in lines[1:]:
        tokens=line.split();require(len(tokens)>=4 and all(t.isdecimal()for t in tokens),'GF3_SPARSE_SYNTAX')
        values=list(map(int,tokens));rhs=values[:3];count=values[3];pairs=list(zip(values[4::2],values[5::2]))
        require(all(c<=2 for c in rhs)and count<=n and len(values)==4+2*count and len(pairs)==count and all(j<n and c in (1,2)for j,c in pairs),'GF3_SPARSE_SYNTAX')
        indices=[j for j,c in pairs];require(indices==sorted(set(indices)),'GF3_SPARSE_SYNTAX');rows.append({'terms':[[j,c]for j,c in pairs],'rhs_affine':rhs})
    return {'variables':list(range(n)),'equations':rows}


def read_vectors(directory,n):
    vectors=[]
    for label in ['const','a','b']:
        raw=(Path(directory)/('x_'+label+'.trits')).read_bytes()
        try:lines=raw.decode('ascii').splitlines()
        except UnicodeDecodeError:raise ValueError('GF3_FULL_TRIT_VECTOR_SYNTAX')
        require(len(lines)==2 and raw.endswith(b'\n')and lines[0]==f'GF3_AFFINE_PRIMAL_V1 {n} {label}'and len(lines[1])==n and all(c in '012'for c in lines[1]),'GF3_FULL_TRIT_VECTOR_SYNTAX')
        vectors.append([int(c)for c in lines[1]])
    return vectors


def domains(model,mode='original'):
    n=len(model['variables']);require(n<=6,'GF3_TINY_BRUTE_DOMAIN');rows=[row_data(row,n,mode)[1]for row in model['equations']]
    return [[list(vector)for vector in product((0,1,2),repeat=n)if all((sum(c*vector[j]for j,c in row['terms'])-row['rhs_affine'][component])%3==0 for row in rows)]for component in range(3)]


def fixture():
    return {'variables':[0,1,2,3],'equations':[
        {'terms':[[0,-2],[1,2]],'rhs_affine':[2,2,0]},
        {'terms':[[1,4],[2,8]],'rhs_affine':[4,0,4]},
        {'terms':[[0,-1],[1,2],[2,2]],'rhs_affine':[2,1,1]},
        {'terms':[],'rhs_affine':[0,0,0]},
        {'terms':[[3,1],[3,-1]],'rhs_affine':[0,0,0]},
        {'terms':[[0,1],[0,2]],'rhs_affine':[0,0,0]},
        {'terms':[[3,3],[0,6]],'rhs_affine':[6,6,3]}]}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Independent4variable7row GF3 raw/divided/control domains729component-specificassignments;40worker60outerreserve20,no native/fulloutput')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);negatives=[]
    def reject(label,call,wanted):
        try:call()
        except ValueError as error:require(str(error)==wanted,'GF3_CONTROL_FAILURE_STAGE');negatives.append({'label':label,'diagnostic':str(error)})
        else:raise ValueError('GF3_CORRUPT_CONTROL_ACCEPTED '+label)
    try:
        require(sha(DESIGN)==DESIGN_SHA,'GF3_FROZEN_DESIGN_PIN')
        raw=fixture();known=[[0,1,0,0],[2,0,0,0],[1,1,0,0]];divided_known=[[0,1,0,2],[2,0,0,1],[1,1,0,2]]
        scalar_vectors(raw,known);scalar_vectors(raw,divided_known,'divided')
        original_domains=domains(raw);divided_domains=domains(raw,'divided')
        require([len(d)for d in original_domains]==[9,9,9]and [len(d)for d in divided_domains]==[3,3,3],'GF3_INDEPENDENT_DOMAIN_COUNTS')
        require(all(v in d for v,d in zip(known,original_domains))and all(v in d for v,d in zip(divided_known,divided_domains))and original_domains!=divided_domains,'GF3_KNOWN_FULL_VECTORS')
        sparse=sparse_bytes(raw)
        require(sparse==b'GF3_AFFINE_SPARSE_V1 4 7\n2 2 0 2 0 1 1 2\n1 0 1 2 1 1 2 2\n2 1 1 3 0 2 1 2 2 2\n0 0 0 0\n0 0 0 0\n0 0 0 0\n0 0 0 0\n','GF3_HAND_DERIVED_SPARSE_BYTES')
        scalar_vectors(read_sparse(sparse),known)
        require(sparse.decode().splitlines()[-1]=='0 0 0 0'and sparse_bytes(raw,'divided').decode().splitlines()[-1]!='0 0 0 0','GF3_NONUNIT_CONTENT_SCOPE_CONTROL')
        bad=json.loads(json.dumps(raw));bad['equations'][2]['rhs_affine'][0]=3
        require([len(d)for d in domains(bad)]==[0,9,9],'GF3_KNOWN_INCONSISTENT_DOMAIN')
        raw_weights=[[0,2],[1,1],[2,2]];divided_weights=[[0,1],[1,1],[2,2]]
        raw_relation=scalar_relation(bad,raw_weights,[2,0,0]);divided_relation=scalar_relation(bad,divided_weights,[2,0,0],'divided')
        scalar_relation(bad,[[0,1],[1,2],[2,1]],[1,0,0])
        reject('divided_weights_on_original',lambda:scalar_relation(bad,divided_weights,[2,0,0]),'GF3_ORIGINAL_ROW_RELATION_SCALAR')
        changed=[v[:]for v in known];changed[0][0]=1
        reject('changed_vector_trit',lambda:scalar_vectors(raw,changed),'GF3_ORIGINAL_PRIMAL_SCALAR_ROW')
        changed=json.loads(json.dumps(raw));changed['equations'][0]['terms'][0][1]=-4
        reject('changed_coefficient_magnitude',lambda:scalar_vectors(changed,known),'GF3_ORIGINAL_PRIMAL_SCALAR_ROW')
        changed=json.loads(json.dumps(raw));changed['equations'][0]['terms'][0][1]=2
        reject('changed_coefficient_sign',lambda:scalar_vectors(changed,known),'GF3_ORIGINAL_PRIMAL_SCALAR_ROW')
        changed=json.loads(json.dumps(raw));changed['equations'][0]['rhs_affine'][0]=4
        reject('changed_original_RHS',lambda:scalar_vectors(changed,known),'GF3_ORIGINAL_PRIMAL_SCALAR_ROW')
        reject('changed_relation_weight',lambda:scalar_relation(bad,[[0,1],[1,1],[2,2]],[2,0,0]),'GF3_ORIGINAL_ROW_RELATION_SCALAR')
        reject('changed_relation_residue',lambda:scalar_relation(bad,raw_weights,[1,0,0]),'GF3_ORIGINAL_ROW_RELATION_SCALAR')
        reject('changed_relation_row',lambda:scalar_relation(bad,[[0,2],[1,1]],[2,0,0]),'GF3_ORIGINAL_ROW_RELATION_SCALAR')
        reject('negative_relation_weight',lambda:scalar_relation(bad,[[0,-1],[1,1],[2,2]],[2,0,0]),'GF3_ROW_RELATION_SYNTAX')
        for d in [0,-2,3]:reject('invalid_divisor_'+str(d),lambda d=d:row_data(raw['equations'][0],4,'divided',d),'GF3_POSITIVE_DIVIDING_CONTENT')
        for label,wire in [('coefficient0',b'GF3_AFFINE_SPARSE_V1 4 1\n0 0 0 1 0 0\n'),('coefficient3',b'GF3_AFFINE_SPARSE_V1 4 1\n0 0 0 1 0 3\n'),('negative_sign',b'GF3_AFFINE_SPARSE_V1 4 1\n0 0 0 1 0 -1\n'),('duplicate_column',b'GF3_AFFINE_SPARSE_V1 4 1\n0 0 0 2 0 1 0 2\n'),('column_range',b'GF3_AFFINE_SPARSE_V1 4 1\n0 0 0 1 4 1\n'),('RHSrange',b'GF3_AFFINE_SPARSE_V1 4 1\n3 0 0 0\n')]:reject(label,lambda wire=wire:read_sparse(wire),'GF3_SPARSE_SYNTAX')
        affine_checks=0
        for a,b in product((0,1,2),repeat=2):
            vector=[(known[0][j]+a*known[1][j]+b*known[2][j])%3 for j in range(4)]
            require(all((sum(c*vector[j]for j,c in row['terms'])-(row['rhs_affine'][0]+a*row['rhs_affine'][1]+b*row['rhs_affine'][2]))%3==0 for row in raw['equations']),'GF3_ALL_AFFINE_PARAMETER_CONTROLS');affine_checks+=1
        for x,y in product((0,1,2),repeat=2):
            additive={'variables':[0,1],'equations':[{'terms':[[0,1],[1,1]],'rhs_affine':[(x+y)%3]*3}]}
            multiplicative={'variables':[0],'equations':[{'terms':[[0,x]],'rhs_affine':[(x*y)%3]*3}]}
            scalar_vectors(additive,[[x,y]]*3);scalar_vectors(multiplicative,[[y]]*3)
        rhs_triples_checked=0
        for residues in product((0,1,2),repeat=3):
            scalar_vectors({'variables':[0],'equations':[{'terms':[[0,1]],'rhs_affine':list(residues)}]},[[c]for c in residues]);rhs_triples_checked+=1
        require(rhs_triples_checked==27,'GF3_RHS_POPULATION')
        save(out/'independent_raw_fixture.json',raw);save(out/'independent_inconsistent_fixture.json',bad)
        save(out/'independent_raw_vectors.json',known);save(out/'independent_divided_vectors.json',divided_known)
        save(out/'original_domains.json',original_domains);save(out/'divided_domains.json',divided_domains)
        save(out/'original_relation.json',raw_relation);save(out/'divided_relation.json',divided_relation)
        (out/'original_sparse_rows.txt').write_bytes(sparse);(out/'divided_sparse_rows.txt').write_bytes(sparse_bytes(raw,'divided'))
        for label,vector in zip(['const','a','b'],known):(out/('x_'+label+'.trits')).write_text(f'GF3_AFFINE_PRIMAL_V1 4 {label}\n'+''.join(map(str,vector))+'\n',encoding='ascii',newline='\n')
        require(read_vectors(out,4)==known,'GF3_FULL_VECTOR_WIRE_ROUNDTRIP')
        require(deadline.status()['remaining_seconds']>10,'not completed within allocated budget')
        paths=[Path(__file__),PROTOCOL,DESIGN,ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'uv.lock',ROOT/'pyproject.toml']
        save(out/'summary.json',{'status':'INDEPENDENT_ORIGINAL_GF3_SCALAR_CHECKER_CALIBRATION_V1_PASS','timestamp':datetime.now(timezone.utc).isoformat(),
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python_version':platform.python_version(),
            'verifier':'/root/structural','inputs_sha256':{p.resolve().relative_to(ROOT).as_posix():sha(p)for p in paths},
            'original_domain_sizes':[len(d)for d in original_domains],'divided_domain_sizes':[len(d)for d in divided_domains],
            'original_and_divided_equivalence_claimed':False,'content3_non_equivalence_checked':True,'raw_relation_weights':raw_weights,'divided_relation_weights':divided_weights,
            'positive_scalar_add_product_pair_cases':9,'RHS_triples_scalar_checked':rhs_triples_checked,'component_specific_brute_assignment_tests':729,'affine_parameter_pairs_checked':affine_checks,'negative_controls':negatives,
            'producer_imports':False,'native_execution':False,'full_operator_accessed':False,'rank_claim':False,'target_resolution':False,
            'scope':'Independent scalar checker calibration/fixtures only. Native packed arithmetic, checkpoint/engineering/full outputs remain separately unapproved.',
            'outputs_sha256':{p.resolve().relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()if p.is_file()},'elapsed_seconds':time.monotonic()-started})
    except BaseException as error:
        save(out/'failure.json',{'error':repr(error),'elapsed_seconds':time.monotonic()-started,'outputs_preserved':True,'approval':False});raise


if __name__=='__main__':main()
