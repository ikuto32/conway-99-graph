"""Candidate exact signed-pair maps and entailed44clause images; no solver."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT/'acceleration/results/20260930_eight_full99_cnf/model.json'
SCOPE = ROOT/'acceleration/results/20260917_partial_eight_matchings/manifest.json'
CERT = ROOT/'acceleration/results/20260930_eight_raw29_gram_cut/certificate.json'
GATE = ROOT/'acceleration/results/20260930_independent_review/eight_full99_w81_gram_cut/summary.json'
GATE_SHA = 'd0b8e269801c7f00b9ec1c04dd504978372c93c4264ae022eeea6d1340fe4fcd'


def need(test,message):
    if not test: raise ValueError(message)


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,obj):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(obj,stream,separators=(',',':')); stream.write('\n')


def canonical(clause,variables=2160):
    need(all(type(x) is int and 1 <= abs(x) <= variables for x in clause),'signed variable range')
    need(len(clause) == len({abs(x) for x in clause}),'distinct clause variables')
    return tuple(sorted(clause,key=lambda x:(abs(x),x)))


def transport(clause,vm):
    need(sorted(vm) == list(range(1,len(vm)+1)),'edge permutation')
    return canonical([vm[abs(lit)-1]*(1 if lit > 0 else -1) for lit in clause],len(vm))


def specification(scope):
    labels = [(2*i+a,2*j+b) for i,j in itertools.combinations(range(7),2) for a in range(2) for b in range(2)]
    fixed = set(map(tuple,scope['remaining_fixed_K_edges_outer']))
    unknown = set(map(tuple,scope['unknown_edges_outer']))
    need(len(fixed)==120 and len(unknown)==2160 and not fixed&unknown,'raw scope universe')
    graph = [[0]*99 for _ in range(99)]
    def put(u,v,value): graph[u][v]=graph[v][u]=value
    for i in range(1,15): put(0,i,1)
    for i in range(7): put(1+2*i,2+2*i,1)
    for u,label in enumerate(labels,15):
        for inner in label: put(u,inner+1,1)
    for u,v in fixed: put(u+15,v+15,1)
    for u,v in unknown: put(u+15,v+15,-1)
    return graph,labels,fixed,unknown


def permutation(group_permutation,mask,labels,lookup):
    inner = [2*group_permutation[i//2]+((i%2)^((mask>>(i//2))&1)) for i in range(14)]
    outer = [lookup[tuple(sorted((inner[a],inner[b])))] for a,b in labels]
    full = [0]+[x+1 for x in inner]+[x+15 for x in outer]
    need(sorted(full) == list(range(99)),'full vertex permutation')
    return full,outer


def full_check(graph,full,edges,edge_lookup):
    need(sorted(full) == list(range(99)),'valid full permutation')
    need(all(graph[u][v] == graph[full[u]][full[v]] for u in range(99) for v in range(99)),'full fixed/free preservation')
    vm = [edge_lookup[tuple(sorted((full[u],full[v])))] for u,v in edges]
    need(sorted(vm) == list(range(1,2161)),'all2160free-edge bijection')
    return vm


def affine(w,graph,edges):
    constant = 27*sum(x*x for x in w)+sum(w)**2
    constant -= 18*sum(w[i]*w[j] for i,j in itertools.combinations(range(99),2) if graph[i][j] == 1)
    coefficients = [-18*w[u]*w[v] for u,v in edges]
    return constant,coefficients


def maximum(constant,coefficients,clause):
    fixed = {abs(lit):int(lit < 0) for lit in clause}
    return constant+sum(c*fixed[j] if j in fixed else max(0,c) for j,c in enumerate(coefficients,1))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(); args.out.mkdir(parents=True,exist_ok=False)
    inputs={}
    def read(path,expected=None):
        path=Path(path)
        if not path.is_absolute(): path=ROOT/path
        observed=digest(path); need(expected is None or observed==expected,'input hash '+str(path))
        inputs[key(path)]=observed
        return json.loads(path.read_bytes())
    scope=read(SCOPE,'a389f457280212fbafcaa556dfe2064c9b1659045475fe4f93a0becb400cb7a2')
    model=read(MODEL,'f2b7a649e74aa476380e14066239a188a2d2122d2ba1cc6e330e9a094d2cc0ee')
    gate=read(GATE,GATE_SHA)
    need(gate['status']=='INDEPENDENT_FULL99_GRAM_BOOLEAN_BOX_NOGOOD_PASS','independent44cut gate')
    for path,expected in gate['inputs_sha256'].items():
        p=ROOT/path; need(digest(p)==expected,'cut gate binding '+path); inputs[key(p)]=expected
    cert=read(CERT,'d08d8bc72221181aba7ce3e73374bf0a04c6c94ab925230890ced2020da9194b')
    clause=canonical(cert['nogood_clause'])
    need(list(clause)==gate['verified_clause'] and len(clause)==44,'exact independently checked44clause')
    graph,labels,fixed,unknown=specification(scope)
    need(graph==model['known_adjacency_full99'] and list(map(list,labels))==model['outer_labels'],'independent raw scope reconstruction')
    edges=[(u+15,v+15) for u,v in sorted(unknown)]
    need(model['edge_variables']==[dict(u=u,v=v,id=i+1) for i,(u,v) in enumerate(edges)],'free edge ordering')
    edge_lookup={edge:i+1 for i,edge in enumerate(edges)}
    lookup={label:i for i,label in enumerate(labels)}
    profiles=Counter()
    for u,v in unknown:
        gs={x//2 for x in labels[u]}&{x//2 for x in labels[v]}
        profiles[(tuple(sorted(gs)),len(set(labels[u])&set(labels[v])))]+=1
    expected={ ((),0):1680, **{((i,),1):120 for i in range(4)} }
    need(dict(profiles)==expected,'release-coordinate profile')
    groups=[list(a+b) for a in itertools.permutations(range(4)) for b in itertools.permutations(range(4,7))]
    need(len(groups)==144,'frozen group population')
    for p in (Path(__file__),Path(__file__).with_suffix('.md'),ROOT/'uv.lock'):
        inputs[key(p)]=digest(p)
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=inputs,
        question='Which proposed signed-pair relabelings preserve every fixed/free entry, and what signed images follow from the checked44clause?',
        scope='Exact eight-coordinate120fixedK/2160free family; no target automorphism assumption.',
        selection='All144 lexicographic group permutations preserving0..3/4..6, each with integer sign mask0..127.',
        group_permutations=groups,proposed_maps=18432,limits=dict(wall_seconds=120),numerical_threshold=None,
        numerical_threshold_null_reason='All decisions exact integer/finite equality.',random_seed=None,random_seed_null_reason='Deterministic complete supplied Cartesian population.',
        success='Every retained map literal full-matrix/edge-bijection pass and every image/Boolean maximum exact; separate independent approval required.',
        failure='Record each first mismatch or exact cap trigger; do not infer whole-family infeasibility.',status='PREREGISTERED_CANDIDATE_PRODUCER',solver_calls=0)
    save(args.out/'manifest.json',manifest)
    # Producer calibration is disclosed and is not independent approval.
    identity=list(range(99)); identity_vm=full_check(graph,identity,edges,edge_lookup)
    need(identity_vm==list(range(1,2161)) and transport(clause,identity_vm)==clause,'identity control')
    need(transport([1,-2],[2,3,1])==(2,-3),'noninvolutory forward action control')
    rejected_controls=[]
    for name,op in [('duplicate_vertex',lambda:full_check(graph,[0]+identity[0:98],edges,edge_lookup)),
                    ('duplicate_variable',lambda:transport([1,2],[1,1])),('repeated_clause_variable',lambda:canonical([1,-1]))]:
        try: op()
        except (ValueError,KeyError): rejected_controls.append(name)
        else: raise ValueError('accepted corrupt control '+name)
    w=cert['integer_vector_full99']; constant,weights=affine(w,graph,edges)
    need(constant==cert['affine_constant'] and maximum(constant,weights,clause)==cert['global_boolean_box_upper_bound']==gate['exact_boolean_box_upper_bound']==-5868,'source raw affine box')
    start=time.monotonic(); accepted=[]; attempted=0; mismatches=Counter(); stopped=False
    with (args.out/'attempts.jsonl').open('x',encoding='utf-8') as attempt_stream:
        for index in tqdm(range(18432),desc='signed-pair proposals',unit='map'):
            if time.monotonic()-start>=120:
                stopped=True; break
            group_index,mask=divmod(index,128); group=groups[group_index]
            full,outer=permutation(group,mask,labels,lookup)
            witness=None
            for u,v in sorted(fixed):
                pu,pv=outer[u],outer[v]
                newvalue=graph[15+pu][15+pv]
                if newvalue!=1:
                    witness=[15+u,15+v,1,15+pu,15+pv,newvalue];break
            if witness is not None:
                record=dict(index=index,accepted=False,first_fixed_edge_violation=witness)
                mismatches['fixed_present_mismatch']+=1
            else:
                try:
                    vm=full_check(graph,full,edges,edge_lookup)
                except (ValueError,KeyError):
                    witness=next([u,v,graph[u][v],full[u],full[v],graph[full[u]][full[v]]] for u in range(99) for v in range(99) if graph[u][v]!=graph[full[u]][full[v]])
                    record=dict(index=index,accepted=False,first_full_matrix_violation=witness)
                    mismatches['other_specification_mismatch']+=1
                else:
                    mapped=transport(clause,vm)
                    pushed=[0]*99
                    for u,x in enumerate(w): pushed[full[u]]=x
                    pushed_const,pushed_weights=affine(pushed,graph,edges)
                    need(pushed_const==constant and all(pushed_weights[vm[j]-1]==weights[j] for j in range(2160)),'pushed raw coefficients')
                    upper=maximum(pushed_const,pushed_weights,mapped)
                    need(upper==-5868,'image box exact maximum')
                    map_id=len(accepted)
                    accepted.append(dict(id=map_id,proposal_index=index,group_permutation=group,sign_mask=mask,full99=full,edge_variable_map=vm,transported_clause=list(mapped),exact_box_upper=upper))
                    record=dict(index=index,accepted=True,accepted_map_id=map_id)
            attempt_stream.write(json.dumps(record,separators=(',',':'))+'\n');attempted+=1
            if attempted%1024==0:
                checkpoint=dict(attempted=attempted,accepted=len(accepted),next_proposal_index=attempted,elapsed_seconds=time.monotonic()-start,status='PRODUCER_RUNNING_OBSERVATION')
                (args.out/'checkpoint.json').write_text(json.dumps(checkpoint)+'\n',encoding='utf-8')
                attempt_stream.flush()
    save(args.out/'accepted_maps.json',accepted)
    unique=[];where={};images=[]
    for rec in accepted:
        c=tuple(rec['transported_clause'])
        if c not in where:
            where[c]=len(unique);unique.append(dict(id=len(unique),clause=list(c),map_ids=[]))
        uid=where[c];unique[uid]['map_ids'].append(rec['id']);images.append(dict(map_id=rec['id'],unique_clause_id=uid))
    save(args.out/'images.json',images);save(args.out/'unique_clauses.json',unique)
    with (args.out/'clauses.cnfpart').open('x',encoding='ascii',newline='\n') as stream:
        for row in unique: stream.write(' '.join(map(str,row['clause']))+' 0\n')
    (args.out/'checkpoint.json').write_text(json.dumps(dict(attempted=attempted,accepted=len(accepted),next_proposal_index=attempted,
        elapsed_seconds=time.monotonic()-start,status='PRODUCER_STOPPED_COMPLETE' if not stopped else 'PRODUCER_STOPPED_CAP'))+'\n',encoding='utf-8')
    outputs={p.name:dict(sha256=digest(p),bytes=p.stat().st_size) for p in sorted(args.out.iterdir()) if p.is_file()}
    report=dict(status='CANDIDATE_EIGHT_SIGNED_PAIR_MAPS_AND_CLAUSE_IMAGES',independent_review_pending=True,
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],command=manifest['command'],working_directory=str(Path.cwd()),
        proposed_population=18432,attempted_proposals=attempted,unattempted_proposals=18432-attempted,accepted_maps=len(accepted),distinct_maps=len({tuple(x['full99']) for x in accepted}),
        rejected_proposals=attempted-len(accepted),rejection_reasons=dict(mismatches),cap_hit=stopped,elapsed_seconds=time.monotonic()-start,
        release_coordinate_profile=[dict(shared_groups=list(g),shared_inner_count=s,unknown_pairs=count) for (g,s),count in sorted(profiles.items())],
        signed_clause_attempts=len(images),unique_clauses=len(unique),duplicate_clause_images=len(images)-len(unique),
        identity_retained=any(x['full99']==identity for x in accepted),source_clause=list(clause),source_clause_length=44,exact_source_and_image_box_upper=-5868,
        inputs_sha256=inputs,outputs=outputs,controls=dict(identity_passed=True,noninvolutory_three_cycle_passed=True,corruptions_rejected=rejected_controls),
        action='Old vertex i maps to full99[i], old variable j maps to edge_variable_map[j-1], literal signs unchanged.',
        proposed_transport_derivation='For arbitrary full99 solution A preserving the specification, B[i,j]=A[p(i),p(j)] is another such target. Applying the verified source clause to B yields its forward signed edge image on A. No equality A=B is required.',
        scope='Only supplied signed-pair label changes preserving the exact fixed/free family; all clauses are intended redundant consequences of the exact full99 CNF.',
        limitations=['All newly produced map and transport claims remain CANDIDATE until separate independent review.','No census of arbitrary99vertex permutations or target automorphisms.','No SAT/UNSAT result, target resolution, graph exclusion union size or performance benefit is established.'],
        producer_imported=False,shared_components=['Python exact integers, standard library and tqdm progress','Raw fixed/free model and independently checked source-cut gate'],solver_calls=0,target_resolution=False)
    save(args.out/'summary.json',report)
    print(json.dumps({k:report[k] for k in ('status','attempted_proposals','accepted_maps','rejected_proposals','unique_clauses','elapsed_seconds','cap_hit')}))


if __name__=='__main__': main()
