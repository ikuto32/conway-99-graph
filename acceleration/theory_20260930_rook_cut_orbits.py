"""Transport independently valid clauses through independently checked scaffold maps."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
OUT=ROOT/(B+'rook_cut_orbits01')
MAPS=B+'rook_scaffold_relabeling/accepted_relabelings.json'
MAP_GATE=B+'independent_review/rook_scaffold_relabelings32.json'
BOX=B+'rook_box_lazy_wave02/final_checkpoint.json'
BOX_GATE=B+'independent_review/rook_box_collection02.json'
DEGREE=B+'degree_block_gram_bounds/run01/final_cut_certificate.json'
DEGREE_GATE=B+'independent_review/degree_block_gram/cut_claim_binding.json'
GATES={MAP_GATE:'897188e21828d946149dbeee503c1fd61b6946197810a11970b92f2a6bf1b282',BOX_GATE:'ee79e1eb396c5ffd9dc47c3b32a76221e30a514a885e5c472fa4e39af3a5ca67',DEGREE_GATE:'c548e9bcfa8dd506b1696c9ffdce7e141786c7980acd8c62038a417c7323ae1a'}
def h(p):return sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
def transform(clause,mapping):
    assert len(mapping)==780 and sorted(mapping)==list(range(1,781))
    assert clause and all(type(x)is int and 1<=abs(x)<=780 for x in clause)
    assert len({abs(x) for x in clause})==len(clause)
    return sorted([(1 if x>0 else -1)*mapping[abs(x)-1] for x in clause],key=lambda x:(abs(x),x))

def main():
    OUT.mkdir(exist_ok=False)
    bindings={p:h(p) for p in [MAPS,BOX,DEGREE,Path(__file__).relative_to(ROOT).as_posix(),'uv.lock',*GATES]}
    for p,v in GATES.items():
        assert bindings[p]==v
        for name,value in read(p)['inputs_sha256'].items():assert h(name)==value
    assert read(DEGREE_GATE)['recommendation']=='VERIFIED'
    sources=[]
    for index,row in enumerate(read(BOX)['ordered_cuts']):
        assert h(row['certificate'])==row['certificate_sha256'] and h(row['audit'])==row['audit_sha256']
        sources.append(dict(id='box_'+str(index).zfill(2),kind='BOOLEAN_BOX',clause=row['clause'],certificate=row['certificate'],certificate_sha256=row['certificate_sha256'],audit=row['audit'],audit_sha256=row['audit_sha256']))
    d=read(DEGREE);sources.append(dict(id='degree_12',kind='DEGREE_BLOCK',clause=d['nogood_clause'],certificate=DEGREE,certificate_sha256=h(DEGREE),audit=DEGREE_GATE,audit_sha256=h(DEGREE_GATE)))
    maps=read(MAPS)['maps'];assert len(sources)==11 and len(maps)==32
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),inputs_sha256=bindings,
        question='What exact clause orbit follows from eleven independently valid source clauses and the supplied32 specification-preserving maps?',
        scope='Exact frozen780edge family; relabeling-invariant specification, with no automorphism of a target assumed.',selection='Every one of11source clauses under every one of32checked maps, no omissions.',
        action_convention='old graph vertex i maps to pi(i), old edge variable j maps to mapping[j-1]; clause literals keep their signs.',
        deduplication='Sort each clause by absolute variable ID and sign, then compare the entire signed literal tuple. No subsumption or overlap counting.',resource_limit_seconds=30,independent_orbit_check_required_before_SAT=True)
    save(OUT/'manifest.json',manifest);save(OUT/'source_clauses.json',sources)
    identity=list(range(1,781));assert transform([7,-151],identity)==[7,-151]
    swap=identity.copy();swap[6],swap[150]=swap[150],swap[6]
    assert transform([7,-151],swap)==[-7,151]
    try:transform([7,-7],identity)
    except AssertionError:pass
    else:raise AssertionError('duplicate variable control accepted')
    groups={};images=[]
    for source in sources:
        for index,p in enumerate(maps):
            clause=transform(source['clause'],p['edge_variable_map']);key=tuple(clause)
            if key not in groups:groups[key]=dict(id=len(groups),clause=clause,origins=[])
            record=dict(source_id=source['id'],map_index=index,unique_clause_id=groups[key]['id'])
            images.append(record);groups[key]['origins'].append(dict(source_id=source['id'],map_index=index))
    save(OUT/'images.json',images);save(OUT/'unique_clauses.json',list(groups.values()))
    with(OUT/'clauses.cnfpart').open('x',encoding='ascii',newline='\n')as f:
        for row in groups.values():f.write(' '.join(map(str,row['clause']))+' 0\n')
    save(OUT/'summary.json',dict(status='CANDIDATE_SCAFFOLD_TRANSPORTED_CLAUSES',source_clauses=len(sources),maps=len(maps),transport_attempts=len(images),unique_clauses=len(groups),duplicate_images=len(images)-len(groups),clause_lengths=sorted({len(row['clause']) for row in groups.values()}),controls='Identity, sign-preserving swap and invalid repeated variable',independent_review_pending=True,solver_launched=False,target_resolution=False,excluded_assignment_union_size=None,excluded_assignment_union_size_reason='Clause overlap is not counted as graph coverage.',output_sha256={p.name:h(p.relative_to(ROOT)) for p in OUT.iterdir() if p.is_file()}))
    print(json.dumps(dict(transport_attempts=len(images),unique_clauses=len(groups),independent_review_pending=True)))

if __name__=='__main__':main()
