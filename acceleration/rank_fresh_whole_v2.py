"""Prepare, validate, then (only after independent mapping review) rank a whole-family cohort.

Whole native indices are zero-based rows of the complete same-sign family.
Multiple alternating cycles remain explicit; no cross-extraction label is used.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[_name]='1'
import argparse
from collections import Counter,defaultdict,deque
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import struct
import subprocess
import time

from rank_fresh_star_pdhg import (Binding,CAPS,DOMAIN_EXE,DOMAIN_QA,GPU_EXE,GPU_QA,LIMITS,PINS,
    ROOT,canonical_edges,check_gpu,digest,finite,fits_chunk,inspect_native,key,normalized_bindings,path,
    read_json,require,write_json)

LEGACY_CORE='acceleration/rank_fresh_star_pdhg.py'
OBJECTIVE='ORIGINAL_STAR_SIMPLEX_PDHG_V1'
SCOPE=('Numerical original-star-simplex ranking of128 sampled, previously unevaluated refined-score '
       'members of the audited whole same-sign family. No whole-family star ranking, independent '
       'domain-completeness, graph or exclusion claim. No triangle/pair filtered domains used.')
POLICY=dict(name='64_BEST_REFINED_UPPER_THEN64_ROUND_ROBIN_WHOLE_COORDINATE_CYCLE_SHAPE_V2',
    global_count=64,stratified_count=64,
    eligible_population='Distinct whole-family rows with saved2000-iteration refined old-edge upper scores, excluding recorded previous/current LP graph identities',
    score_order='Ascending(refined_upper,zero_based_whole_family_index)',
    stratum='(root_group,matching_class,sorted changed-edge counts of all alternating cycles)',
    diverse_order='After removing global64, sort buckets lexicographically by stratum; each pass takes one lowest-score unused member per nonempty bucket until64 picked',
    sampling_is_not_exhaustive=True)


def stamp(): return datetime.now(timezone.utc).isoformat()


def geometry(move):
    require(type(move) is dict and type(move.get('root_group')) is int and 0<=move['root_group']<7
            and move.get('matching_class') in ('same_0','same_1'),'Whole same-sign coordinate required')
    removed,added=move.get('removed'),move.get('added')
    def edges(value):
        require(type(value) is list and 2<=len(value)<=6 and all(type(e) is list and len(e)==2 and
                all(type(v) is int for v in e) and 0<=e[0]<e[1]<84 for e in value),'Invalid changed edges')
        require(value==sorted(value) and len(set(map(tuple,value)))==len(value),'Duplicate/unsorted changed edge')
        return set(map(tuple,value))
    old,new=edges(removed),edges(added)
    require(not old&new and len(old)==len(new)==move.get('changed_edges'),'Wrong whole changed-edge count')
    cycles=move.get('alternating_cycles')
    require(type(cycles) is list and cycles,'Missing whole alternating-cycle list')
    seen=set();cycle_old=set();cycle_new=set();sizes=[]
    for cycle in cycles:
        require(type(cycle) is list and 4<=len(cycle)<=12 and len(cycle)%2==0
                and all(type(v) is int and 0<=v<84 for v in cycle),'Bad alternating cycle')
        require(len(set(cycle))==len(cycle) and not seen&set(cycle),'Repeated alternating-cycle vertex')
        seen.update(cycle);sizes.append(len(cycle)//2)
        for j,u in enumerate(cycle):
            edge=tuple(sorted((u,cycle[(j+1)%len(cycle)])))
            (cycle_old if j%2==0 else cycle_new).add(edge)
    require(cycle_old==old and cycle_new==new,'Cycle decomposition does not reproduce removed/added edges')
    return dict(root_group=move['root_group'],matching_class=move['matching_class'],
                changed_edges=len(old),alternating_cycle_sizes=sorted(sizes))


def choose(scores,moves,excluded):
    ordered=sorted((i for i in scores if i not in excluded),key=lambda i:(scores[i],i))
    require(len(ordered)>=128,'Fewer than128 unused refined-score members')
    selected=ordered[:64];roles={i:['global_refined_upper64'] for i in selected}
    buckets=defaultdict(deque)
    for i in ordered[64:]:
        g=geometry(moves[i]);buckets[g['root_group'],g['matching_class'],tuple(g['alternating_cycle_sizes'])].append(i)
    while len(selected)<128:
        changed=False
        for bucket in sorted(buckets):
            if buckets[bucket]:
                i=buckets[bucket].popleft();selected.append(i);roles[i]=['round_robin_coordinate_cycle_shape64'];changed=True
                if len(selected)==128:break
        require(changed,'Diversity bucket exhaustion')
    return selected,roles,ordered


def load_sources(args):
    bindings=Binding();bindings.bind(__file__);bindings.bind(LEGACY_CORE)
    for source,expected in PINS.items(): bindings.bind(source,expected)
    for qfile,status,names in ((DOMAIN_QA,'RUST_BATCH_STAR_DOMAIN_ORDER_PARITY_AND_CAP_RESET_PASS',
                               (DOMAIN_EXE,'acceleration/star_domains_batch.rs')),
                              (GPU_QA,'COLD_STAR_CUDA_BOUNDED_PROTOTYPE_QA_PASS',
                               (GPU_EXE,'acceleration/star_pdhg_gpu.cu','acceleration/export_star_pdhg_binary.py','acceleration/star_marginal_cp_cpu_v2.py'))):
        qa=bindings.document(qfile);require(qa['status']==status,'Missing pinned native/GPU calibration')
        qb=normalized_bindings(qa);require(all(qb.get(n)==PINS[n] for n in names),'Pinned QA association')
    family=bindings.document(args.family);audit=bindings.document(args.family_audit)
    require(family['status']=='COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION' and
            family['selector']=='all' and family['coordinate_count']==14,'Wrong whole family scope')
    require(audit['status']=='INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS'
            and audit['selector']=='all' and audit['final_labeled_edge_set_equality_checked'] is True,'Whole independent audit required')
    ab=normalized_bindings(audit)
    require(ab.get(key(args.family))==bindings.values[key(args.family)],'Whole family/audit mismatch')
    require(len(family['overlap_candidates'])==len(family['moves'])==family['legal_count']==audit['legal_count']==81000,'Whole family row count')
    run=path(args.run)
    search=bindings.document(run/'summary.json');search_audit=bindings.document(run/'audit.json')
    search_manifest=bindings.document(run/'manifest.json');stage=bindings.document(run/'refined_stage.json')
    require(search['status']=='BOUNDED_CP_MATCHING_SEARCH_FINISHED' and search['producer_version']==2
            and search_audit['status']=='INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS'
            and search_audit['audited_producer_version']==2,'Audited whole search required')
    sb=normalized_bindings(search_audit)
    for p in (run/'summary.json',run/'manifest.json',run/'refined_stage.json',path(args.family),path(args.family_audit)):
        require(sb.get(key(p))==bindings.values[key(p)],'Unbound search input '+key(p))
    association=search['family_association']
    require(key(association['native_path'])==key(args.family) and association['native_sha256']==bindings.values[key(args.family)],'Search family row identity mismatch')
    base_path=path(association['initial_path']);bindings.bind(base_path,association['initial_sha256'])
    base=read_json(base_path);base_edges=set(map(tuple,base['overlap_edges_outer_zero_based']))
    require(len(search['records'])==64 and len({r['proposal_index'] for r in search['records']})==64,'Current64 evaluated inventory required')
    excluded_hashes={canonical_edges(base['overlap_edges_outer_zero_based'])}
    current_ids=[]
    for row in search['records']:
        i=row['proposal_index'];require(type(i) is int and 0<=i<81000,'Bad evaluated family row')
        bindings.bind(row['candidate_path'],row['candidate_sha256'])
        graph=read_json(row['candidate_path'])['overlap_edges_outer_zero_based']
        require(graph==family['overlap_candidates'][i],'Evaluated64 graph/index mismatch')
        excluded_hashes.add(canonical_edges(graph));current_ids.append(i)
    previous=search_manifest['previous_candidates']
    for row in previous:
        bindings.bind(row['candidate_path'],row['candidate_sha256'])
        graph=read_json(row['candidate_path'])['overlap_edges_outer_zero_based'];h=canonical_edges(graph)
        require(h==row['overlap_edges_sha256'],'Prior graph identity mismatch');excluded_hashes.add(h)
    gpu=bindings.document(stage['gpu_output_path']);bindings.bind(stage['gpu_output_path'],stage['gpu_output_sha256'])
    require(sb.get(key(stage['gpu_output_path']))==stage['gpu_output_sha256'],'Unbound old-edge refined scores')
    native_ids=stage['proposal_indices']
    require(stage['stage']=='refined' and stage['steps']==2000 and native_ids[0] is None and
            len(native_ids)==len(gpu['results'])==2049 and len(set(native_ids[1:]))==2048,'Wrong refined-score population')
    scores={};positions={};graph_hashes={}
    for position,(i,result) in enumerate(zip(native_ids,gpu['results'])):
        require(result['candidate_index']==position and len(result['checkpoints'])==1,'Old GPU row mismatch')
        cp=result['checkpoints'][0];values=[result['initial']['primal_upper'],cp['last']['primal_upper'],cp['average']['primal_upper']]
        require(cp['iterations']==2000 and all(finite(x) for x in values) and finite(cp['best_upper']) and
                abs(cp['best_upper']-min(values))<1e-10,'Invalid saved refined upper')
        if i is not None:
            require(type(i) is int and 0<=i<81000,'Refined index out of range')
            scores[i]=min(values);positions[i]=position;graph_hashes[i]=canonical_edges(family['overlap_candidates'][i])
    require(len(set(graph_hashes.values()))==len(graph_hashes),'Repeated refined graph')
    excluded={i for i,h in graph_hashes.items() if h in excluded_hashes}
    require(set(current_ids)<=set(scores) and set(current_ids)<=excluded,'Current64 not excluded from available scores')
    selected,roles,ordered=choose(scores,family['moves'],excluded)
    return dict(bindings=bindings,family=family,audit=audit,search=search,search_audit=search_audit,
        stage=stage,scores=scores,positions=positions,graph_hashes=graph_hashes,excluded=excluded,
        current_ids=current_ids,previous_record_count=len(previous),excluded_hashes=excluded_hashes,
        selected=selected,roles=roles,ordered=ordered,base_edges=base_edges)


def request_for(args,c):
    records=[]
    for i in c['selected']:
        g=geometry(c['family']['moves'][i])
        records.append(dict(proposal_index=i,whole_family_index=i,original_native_index=i,
            native_index_convention='ZERO_BASED_COMPLETE_WHOLE_FAMILY_ROW',roles=c['roles'][i],
            refined_upper=c['scores'][i],refined_gpu_result_index=c['positions'][i],
            overlap_edges_sha256=c['graph_hashes'][i],**g))
        prepared=path(args.indices).parent/'prepared_candidates'/f'index_{i}.json'
        raw=prepared_candidate(c['family'],args.family,i,c['bindings'].values[key(args.family)])
        payload=(json.dumps(raw,separators=(',', ':'),allow_nan=False)+'\n').encode()
        records[-1].update(prepared_candidate_path=key(prepared),prepared_candidate_sha256=sha256(payload).hexdigest())
    return dict(status='EXPLICIT_WHOLE_FRESH_STAR_COHORT_REQUEST_V2',created_at=stamp(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        objective_id=OBJECTIVE,source_additions_explicitly_hashed=True,inputs_sha256=dict(c['bindings'].values),
        family_path=key(args.family),family_sha256=digest(args.family),family_audit_path=key(args.family_audit),family_audit_sha256=digest(args.family_audit),
        original_search_path=key(path(args.run)/'summary.json'),search_audit_path=key(path(args.run)/'audit.json'),
        refined_stage_path=key(path(args.run)/'refined_stage.json'),selection_policy=POLICY,
        family_status=c['family']['status'],family_population=81000,refined_scored_population=len(c['scores']),
        eligible_unused_refined_count=len(c['ordered']),excluded_refined_indices=sorted(c['excluded']),
        excluded_current64_indices=sorted(c['current_ids']),bound_previous_candidate_record_count=c['previous_record_count'],
        indices=c['selected'],records=records,iterations=500,requested_count=128,
        future_shortlist_policy='After independent ranking audit only: union8 lowest numerical uppers and8 lowest numerical lowers, fill overlap gaps by upper order to16.',
        native_caps=CAPS,GPU_limits=LIMITS,domain_source='ORIGINAL_NATIVE_DOMAIN_TABLES_NOT_PROPAGATION_SURVIVORS',
        LP_runs=0,native_domain_processes=0,GPU_processes=0,scope=SCOPE)


def prepared_candidate(family,family_path,i,family_sha):
    return dict(status='WHOLE_FAMILY_SELECTED_CANDIDATE_MATERIALIZED_V2',
        overlap_edges_outer_zero_based=family['overlap_candidates'][i],
        family_path=key(family_path),family_sha256=family_sha,proposal_index=i,
        original_native_index=i,native_index_convention='ZERO_BASED_COMPLETE_WHOLE_FAMILY_ROW',
        **geometry(family['moves'][i]))


def validate_request(args,c,request):
    expected=request_for(args,c)
    for field in ('status','objective_id','family_path','family_sha256','family_audit_path','family_audit_sha256',
                  'original_search_path','search_audit_path','refined_stage_path','selection_policy','family_status','family_population',
                  'refined_scored_population','eligible_unused_refined_count','excluded_refined_indices','excluded_current64_indices',
                  'bound_previous_candidate_record_count','indices','records','iterations','requested_count','future_shortlist_policy',
                  'native_caps','GPU_limits','domain_source'):
        require(request.get(field)==expected[field],'Request field/mapping mismatch: '+field)
    rb=normalized_bindings(request)
    require(rb==c['bindings'].values,'Request binding set differs from frozen sources')
    from audit_certificate import full_graph
    for row in request['records']:
        i=row['proposal_index'];move=c['family']['moves'][i]
        actual=set(map(tuple,c['family']['overlap_candidates'][i]));removed=set(map(tuple,move['removed']));added=set(map(tuple,move['added']))
        require(removed<=c['base_edges'] and not added&c['base_edges'] and
                actual==(c['base_edges']-removed)|added,'Selected exact matching replacement identity')
        full_graph(dict(overlap_edges_outer_zero_based=c['family']['overlap_candidates'][i]))
        require(digest(row['prepared_candidate_path'])==row['prepared_candidate_sha256'],
                'Changed prepared raw candidate')
        require(read_json(row['prepared_candidate_path'])==prepared_candidate(c['family'],args.family,i,c['bindings'].values[key(args.family)]),
                'Prepared candidate materialization mismatch')
    require(len({r['overlap_edges_sha256'] for r in request['records']})==128,'Repeated selected graph')


def preflight(args,request_override=None,loaded=None):
    require(args.iterations==500,'This preregistered wave has exactly500 iterations')
    require(not path(args.out).exists(),'Fresh ranking output required')
    c=loaded if loaded is not None else load_sources(args)
    request=request_override if request_override is not None else read_json(args.indices)
    validate_request(args,c,request)
    if request_override is None:c['bindings'].bind(args.indices)
    c['bindings'].recheck()
    return dict(args=args,out=path(args.out),bindings=c['bindings'],family=c['family'],audit=c['audit'],
                request=request,indices=request['indices'],graph_hashes=c['graph_hashes'])


def execution_gate(args,context):
    require(args.mapping_audit is not None,'Independent whole-family mapping review required before native/GPU execution')
    audit=read_json(args.mapping_audit)
    require(audit.get('status')=='INDEPENDENT_WHOLE_FRESH_V2_MAPPING_PASS','Whole-v2 mapping audit not PASS')
    ab=normalized_bindings(audit)
    for source in (args.indices,__file__,LEGACY_CORE,args.family,args.family_audit):
        require(ab.get(key(source))==digest(source),'Mapping review does not bind '+key(source))
    require(audit.get('selected_indices')==context['indices'] and audit.get('GPU_processes')==0,
            'Mapping review selection/state mismatch')
    context['bindings'].document(args.mapping_audit)


# The numerical execute function below is copied from the frozen generic batch
# engine, with whole-family metadata and version changes only. Its model/export
# primitives remain imported and hash-pinned; no original source is modified.

def execute(context):
    args, out, bindings = context['args'], context['out'], context['bindings']
    family, indices = context['family'], context['indices']
    started = time.perf_counter()
    from star_marginal_cp_cpu_v2 import build_model
    from export_star_pdhg_binary import pack_model
    import numpy as np
    import scipy
    out.mkdir(parents=True, exist_ok=False)
    (out / 'candidates').mkdir(); (out / 'domains').mkdir(); (out / 'chunks').mkdir()
    native_input, native_output = out / 'native_input.txt', out / 'native_domains.json'
    with native_input.open('x', encoding='ascii', newline='\n') as f:
        f.write(f'C99OVERLAPS1 {len(indices)}\n')
        for index in indices:
            f.write(' '.join(str(v) for e in family['overlap_candidates'][index] for v in e) + '\n')
    bindings.bind(native_input)
    records = []
    for position, (index, requested) in enumerate(zip(indices, context['request']['records'])):
        candidate_path = out / 'candidates' / f'index_{index}.json'
        candidate = dict(status='AUDITED_FAMILY_CANDIDATE_MATERIALIZED',
            overlap_edges_outer_zero_based=family['overlap_candidates'][index],
            family_path=key(args.family), family_sha256=bindings.values[key(args.family)],
            proposal_index=index, original_native_index=index)
        write_json(candidate_path, candidate)
        records.append(dict(proposal_index=index, original_native_index=index,
            **geometry(family['moves'][index]),
            input_roles=requested['roles'], overlap_edges_sha256=context['graph_hashes'][index],
            candidate_path=key(candidate_path), candidate_sha256=bindings.bind(candidate_path),
            native_result_index=position, domains_path=None, domains_sha256=None,
            status='UNAVAILABLE', unavailable_reason=None, chunk_index=None, binary_candidate_index=None,
            resource_details=None,
            best_lower_numeric=None, best_upper_numeric=None))
    command = [str(path(DOMAIN_EXE)), str(native_input), str(native_output),
               str(CAPS['seconds']), str(CAPS['global_nodes']), str(CAPS['per_vertex_domains'])]
    initial_manifest = dict(status='WHOLE_FRESH_STAR_PDHG_V2_INPUTS_BOUND', objective_id=OBJECTIVE, family_index_convention='ZERO_BASED_COMPLETE_WHOLE_FAMILY_ROW',
        inputs_sha256=dict(bindings.values), family_path=key(args.family), family_sha256=digest(args.family),
        family_audit_path=key(args.family_audit), family_audit_sha256=digest(args.family_audit),
        request_path=key(args.indices), request_sha256=digest(args.indices),
        input_selected_indices=indices, iterations=args.iterations, native_caps=CAPS, GPU_limits=LIMITS,
        native_input_path=key(native_input), native_input_sha256=digest(native_input), native_command=command,
        domain_source='Original native domains; reciprocal survivors never used',
        scores_are_proofs=False, independently_audited_original_domains=False,
        numpy_version=np.__version__, scipy_version=scipy.__version__, scope=SCOPE)
    write_json(out / 'manifest.json', initial_manifest); bindings.bind(out / 'manifest.json')
    tick = time.perf_counter()
    process = subprocess.run(command, capture_output=True, text=True, timeout=len(indices) * CAPS['seconds'] + 120)
    native_wall = time.perf_counter() - tick
    with (out / 'native.log').open('x', encoding='utf-8') as f:
        f.write(process.stdout + process.stderr)
    bindings.bind(out / 'native.log')
    require(process.returncode == 0, 'Native domains failed; preserved artifacts: ' + process.stderr)
    bindings.bind(native_output)
    native = read_json(native_output)
    require(native['candidate_count'] == len(indices) == len(native['results'])
            and native['caps_reset_per_candidate'] is True and finite(native['elapsed_seconds'])
            and native['elapsed_seconds'] >= 0, 'Native batch shape/cap-reset mismatch')
    chunks, cases, chunk_file, chunk_path = [], [], None, None
    totals = dict(count=0, N=0, M=0, nnz=0, bytes=20)
    model_seconds = 0.0

    def flush():
        nonlocal cases, chunk_file, chunk_path, totals
        if not cases:
            return
        chunk_file.seek(8); chunk_file.write(struct.pack('<I', len(cases)))
        chunk_file.close(); chunk_file = None
        chunk_index = len(chunks)
        chunk_manifest_path = chunk_path.parent / 'manifest.json'
        gpu_output = chunk_path.parent / 'gpu.json'
        require(chunk_path.stat().st_size == totals['bytes'], 'Binary byte accounting')
        h = bindings.bind(chunk_path)
        chunk_manifest = dict(status='NATIVE_ORIGINAL_STAR_PDHG_CHUNK_EXPORTED',
            inputs_sha256={name: bindings.values[name] for name in
                [key(out / 'manifest.json'), key(native_output), key(__file__)] + list(PINS)
                + [r[field] for case in cases for r in [records[case['native_result_index']]]
                   for field in ('candidate_path', 'domains_path')]},
            binary_path=key(chunk_path), binary_sha256=h, binary_bytes=totals['bytes'],
            candidate_count=len(cases), checkpoints=[args.iterations], cases=cases,
            chunk_index=chunk_index, aggregate_N=totals['N'], aggregate_M=totals['M'], aggregate_nnz=totals['nnz'],
            original_complete_domains_used=True, pair_pruned_domains_used=False,
            independently_audited_original_domains=False, scope=SCOPE)
        write_json(chunk_manifest_path, chunk_manifest)
        mh = bindings.bind(chunk_manifest_path)
        gpu_command = [str(path(GPU_EXE)), str(chunk_path), str(gpu_output)]
        tick = time.perf_counter()
        run = subprocess.run(gpu_command, capture_output=True, text=True, timeout=max(120, args.iterations * len(cases) * .2))
        gpu_wall = time.perf_counter() - tick
        log = chunk_path.parent / 'gpu.log'
        with log.open('x', encoding='utf-8') as f:
            f.write(run.stdout + run.stderr)
        bindings.bind(log)
        require(run.returncode == 0, 'GPU failed; preserved chunk: ' + run.stderr)
        gh = bindings.bind(gpu_output)
        result = read_json(gpu_output)
        scores = check_gpu(result, cases, args.iterations)
        for position, (case, (lower, upper)) in enumerate(zip(cases, scores)):
            row = records[case['native_result_index']]
            row.update(status='NUMERICALLY_SCORED', unavailable_reason=None,
                chunk_index=chunk_index, binary_candidate_index=position,
                best_lower_numeric=lower, best_upper_numeric=upper)
        chunks.append(dict(chunk_index=chunk_index, proposal_indices=[c['proposal_index'] for c in cases],
            input_path=key(chunk_path), input_sha256=h, manifest_path=key(chunk_manifest_path), manifest_sha256=mh,
            gpu_output_path=key(gpu_output), gpu_output_sha256=gh, gpu_command=gpu_command,
            gpu_process_wall_seconds=gpu_wall, native_elapsed_seconds=result['elapsed_seconds'],
            gpu_iteration_seconds=result['gpu_iteration_seconds']))
        print(json.dumps(dict(chunk_finished=chunk_index, candidates=len(cases), gpu_process_seconds=gpu_wall)), flush=True)
        cases = []; totals = dict(count=0, N=0, M=0, nnz=0, bytes=20)

    for row, document in zip(records, native['results']):
        index = row['proposal_index']
        domains_path = out / 'domains' / f'index_{index}.json'
        write_json(domains_path, document)
        row.update(domains_path=key(domains_path), domains_sha256=bindings.bind(domains_path))
        counts, unavailable = inspect_native(document)
        row.update(domain_counts=counts, complete_domain_enumeration=document['complete_domain_enumeration'],
            native_status=document['status'], native_reciprocity_status=document.get('propagation', {}).get('status'),
            native_caps=CAPS, native_total_nodes=document['total_nodes'])
        if unavailable is None and (max(counts) > LIMITS['domain'] or sum(counts) > LIMITS['N']):
            unavailable = 'UNSUPPORTED_GPU_DOMAIN_OR_VARIABLE_LIMIT'
            row['resource_details'] = dict(max_domain_count=max(counts), total_N=sum(counts),
                max_domain_limit=LIMITS['domain'], total_N_limit=LIMITS['N'])
        if unavailable is not None:
            row['unavailable_reason'] = unavailable
            continue
        tick = time.perf_counter()
        model = build_model(read_json(row['candidate_path']), document['domains'])
        require(model['A'].shape == (5166, sum(counts)) and model['counts'].tolist() == counts, 'Star model association')
        if model['A'].nnz > LIMITS['nnz']:
            row['unavailable_reason'] = 'UNSUPPORTED_GPU_NNZ_LIMIT'
            row['resource_details'] = dict(nnz=int(model['A'].nnz), nnz_limit=LIMITS['nnz'])
            model_seconds += time.perf_counter() - tick
            continue
        payload, metadata = pack_model(model)
        model_seconds += time.perf_counter() - tick
        del model
        require(metadata['M'] == 5166 and metadata['Q'] == 1680 and metadata['blocks'] == 84, 'Export row convention')
        require(fits_chunk(dict(count=0, N=0, M=0, nnz=0, bytes=20), metadata), 'Single model exceeds aggregate limits')
        if not fits_chunk(totals, metadata):
            flush()
        if not cases:
            chunk_dir = out / 'chunks' / f'chunk_{len(chunks):03d}'
            chunk_dir.mkdir()
            chunk_path = chunk_dir / 'input.bin'
            chunk_file = chunk_path.open('xb')
            chunk_file.write(b'C99SCP01' + struct.pack('<3I', 0, 1, args.iterations))
        case = dict(index=len(cases), proposal_index=index, original_native_index=row['original_native_index'],
            native_result_index=row['native_result_index'], candidate_path=row['candidate_path'], candidate_sha256=row['candidate_sha256'],
            domains_path=row['domains_path'], domains_sha256=row['domains_sha256'], domain_counts=counts,
            record_byte_offset=totals['bytes'], record_sha256=sha256(payload).hexdigest(), **metadata)
        chunk_file.write(payload); cases.append(case)
        totals['count'] += 1; totals['N'] += metadata['N']; totals['M'] += metadata['M']
        totals['nnz'] += metadata['nnz']; totals['bytes'] += len(payload)
        del payload
    flush()
    require(all(r['status'] == 'NUMERICALLY_SCORED' or r['unavailable_reason'] is not None for r in records), 'Unfinished candidate')
    bindings.recheck()
    available = [r for r in records if r['status'] == 'NUMERICALLY_SCORED']
    summary = dict(status='NUMERICAL_WHOLE_FRESH_STAR_PDHG_RANKING_FINISHED', producer_version='whole_fresh_v2', objective_id=OBJECTIVE,
        inputs_sha256=bindings.values, manifest_path=key(out / 'manifest.json'), manifest_sha256=digest(out / 'manifest.json'),
        family_path=key(args.family), family_sha256=digest(args.family), family_audit_path=key(args.family_audit), family_audit_sha256=digest(args.family_audit),
        request_path=key(args.indices), request_sha256=digest(args.indices), input_selected_indices=indices,
        native_input_path=key(native_input), native_input_sha256=digest(native_input),
        native_output_path=key(native_output), native_output_sha256=digest(native_output),
        iterations=args.iterations, records=records, chunks=chunks,
        requested_count=len(indices), scored_count=len(available), unavailable_count=len(records)-len(available),
        unavailable_counts=dict(Counter(r['unavailable_reason'] for r in records if r['status'] == 'UNAVAILABLE')),
        ranked_by_lower=[r['proposal_index'] for r in sorted(available, key=lambda r: (r['best_lower_numeric'], r['proposal_index']))],
        ranked_by_upper=[r['proposal_index'] for r in sorted(available, key=lambda r: (r['best_upper_numeric'], r['proposal_index']))],
        ranking_order='Ascending numeric score, then proposal_index; best includes initial and requested last/average only',
        native_process_wall_seconds=native_wall, native_enumeration_seconds=native['elapsed_seconds'],
        model_construction_and_serialization_seconds=model_seconds, elapsed_seconds=time.perf_counter()-started,
        independently_audited_original_domains=False, pair_pruned_domains_used=False, original_complete_domains_used=True,
        numerical_scores_are_proofs=False, candidates_pruned=0, exclusions_claimed=0, LP_runs=0,
        scope=SCOPE)
    write_json(out / 'summary.json', summary)
    print(json.dumps(dict(status=summary['status'], requested=len(indices), scored=len(available),
        unavailable=summary['unavailable_count'], chunks=len(chunks), summary_sha256=digest(out / 'summary.json'))), flush=True)


def argument_parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--family',default='acceleration/results/20260917_same_star_round/family/all.json')
    p.add_argument('--family-audit',default='acceleration/results/20260917_same_star_round/family/independent_audit.json')
    p.add_argument('--run',default='acceleration/results/20260917_same_star_round/search')
    p.add_argument('--indices',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--iterations',type=int,default=500)
    p.add_argument('--report')
    p.add_argument('--mapping-audit')
    modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare',action='store_true')
    modes.add_argument('--validate-only',action='store_true')
    modes.add_argument('--execute',action='store_true')
    return p


def main():
    args=argument_parser().parse_args()
    if args.prepare:
        require(args.iterations==500 and not path(args.indices).exists() and not path(args.out).exists(),
                'Fresh request/ranking outputs and frozen500 iterations required')
        c=load_sources(args)
        request=request_for(args,c)
        candidate_dir=path(args.indices).parent/'prepared_candidates'
        candidate_dir.mkdir(parents=True,exist_ok=False)
        for row in request['records']:
            i=row['proposal_index']
            write_json(row['prepared_candidate_path'],prepared_candidate(c['family'],args.family,i,c['bindings'].values[key(args.family)]))
        validate_request(args,c,request)
        c['bindings'].recheck()
        write_json(args.indices,request)
        report=dict(status='WHOLE_FRESH_V2_REQUEST_PREPARED_NO_COMPUTE',created_at=stamp(),
            source_commit=request['source_commit'],objective_id=OBJECTIVE,request_path=key(args.indices),request_sha256=digest(args.indices),
            selected_indices=request['indices'],selected_count=128,family_population=81000,
            refined_scored_population=request['refined_scored_population'],eligible_unused_refined_count=request['eligible_unused_refined_count'],
            excluded_refined_count=len(request['excluded_refined_indices']),
            native_processes=0,GPU_processes=0,LP_runs=0,independent_mapping_review_pending=True,scope=SCOPE)
        if args.report:write_json(args.report,report)
        print(json.dumps(report));return
    context=preflight(args)
    if args.validate_only:
        report=dict(status='WHOLE_FRESH_V2_PREFLIGHT_PASS',created_at=stamp(),objective_id=OBJECTIVE,
            inputs_sha256=context['bindings'].values,request_path=key(args.indices),request_sha256=digest(args.indices),
            selected_indices=context['indices'],requested_count=128,iterations=500,
            native_processes=0,GPU_processes=0,LP_runs=0,scope=SCOPE)
        if args.report:write_json(args.report,report)
        print(json.dumps({k:v for k,v in report.items() if k!='inputs_sha256'}));return
    execution_gate(args,context)
    execute(context)


if __name__=='__main__':main()
