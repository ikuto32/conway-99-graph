"""Rank an explicit audited cross-cycle cohort with cold star-simplex PDHG.

This producer uses native ORIGINAL star domains, not propagation survivors.
Native completeness and floating scores are recorded claims, never exclusions.
The later selected-candidate auditor must independently re-enumerate all84
domains and match their exact masks before an exact star-LP certificate is used.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[_name] = '1'
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'acceleration/audit_certificate.py': '22d3e334930f734890216f18cfc8335c0a5c046f142a72e5a30beca6be9f1c9d',
    'acceleration/star_marginal_cp_cpu_v2.py': '6a2823692dfb0baab9b0fdb011f84c6fdda82361d9af01433260020cb19ae65d',
    'acceleration/export_star_pdhg_binary.py': 'dd1ba00013e03cdaeb6f2c2ef20cf8ba0fc2a4e2f83f94ecdffd3720c16e740f',
    'acceleration/star_domains_batch.rs': '84be679f31ae0fc365dc51a2b05a60d0467fa660c9c72a3572b3681da887c482',
    'acceleration/build/star_domains_batch.exe': '6f14259f98cf47c2ffa11a7ea0b609cc494f710937468ad11ee318f2b35ae3dd',
    'acceleration/star_pdhg_gpu.cu': '79593e296a4fba29882fb04b7e7dd88091dbc7f218135b6db2ba79c0b49002e8',
    'acceleration/build/star_pdhg_gpu.exe': '9dc3ea92ca53a6ebc8dd3715f5a0586ef00b18d5c8c8b7bd4e61cb6c2ae11075',
    'acceleration/build_star_pdhg_gpu.ps1': 'ca2b9f7117601b2e5d8e67fbfdab84d1604bf1a0b56fee36f021204a0895772b',
    'acceleration/STAR_PDHG_GPU_PROTOCOL.md': 'debbbb003c649bd895d4d9164512ad778b908452e4e53b50aa3f34b02d8ae96c',
    'acceleration/results/20260916_rust_star_domains/batch_qa.json': '7edcab3f2731a41e377f8392afb705015214f6a8cd6834faec4fd9802be9eb59',
    'acceleration/results/20260916_star_cuda_controls/summary.json': '54aac067fb73fc8ed1ced3db1768c447d68f2538760431ec58df58af0d7bf020',
}
DOMAIN_QA = 'acceleration/results/20260916_rust_star_domains/batch_qa.json'
GPU_QA = 'acceleration/results/20260916_star_cuda_controls/summary.json'
DOMAIN_EXE = 'acceleration/build/star_domains_batch.exe'
GPU_EXE = 'acceleration/build/star_pdhg_gpu.exe'
CAPS = dict(seconds=1.0, global_nodes=2000000, per_vertex_domains=20000)
LIMITS = dict(chunk_count=32, N=100000, M=20000, blocks=128, domain=8192,
              nnz=8000000, total_N=2000000, total_M=1000000,
              total_nnz=64000000, binary_bytes=2**31)
SCOPE = ('Numerical ranking of this explicit sampled cohort only. All scores use '
         'the original native domains; no independent domain-completeness, LP, '
         'exclusion, graph-construction or full-family ranking claim. Capped, '
         'empty and unsupported cases remain unavailable records.')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def path(value):
    result = (ROOT / str(value).replace('\\', '/')).resolve()
    result.relative_to(ROOT)
    return result


def key(value):
    return path(value).relative_to(ROOT).as_posix()


def digest(value):
    h = sha256()
    with path(value).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        require(name not in result, 'Repeated JSON key: ' + name)
        result[name] = value
    return result


def read_json(value):
    def bad_constant(token):
        raise ValueError('Nonfinite JSON constant: ' + token)
    return json.loads(path(value).read_bytes(), object_pairs_hook=unique_object,
                      parse_constant=bad_constant)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def canonical_edges(edges):
    require(type(edges) is list and len(edges) == 168 and all(
        type(e) is list and len(e) == 2 and all(type(v) is int for v in e)
        and 0 <= e[0] < e[1] < 84 for e in edges), 'Invalid overlap edge list')
    require(edges == sorted(edges) and len(set(map(tuple, edges))) == 168,
            'Noncanonical overlap edge list')
    return sha256(json.dumps(edges, separators=(',', ':')).encode('utf-8')).hexdigest()


class Binding:
    def __init__(self):
        self.values = {}

    def bind(self, filename, expected=None):
        name = key(filename)
        require(expected is None or (type(expected) is str and len(expected) == 64
                and all(c in '0123456789abcdef' for c in expected)), 'Invalid SHA256: ' + name)
        actual = digest(name)
        require(expected is None or actual == expected, 'Changed bound input: ' + name)
        require(name not in self.values or self.values[name] == actual, 'Conflicting binding: ' + name)
        self.values[name] = actual
        return actual

    def document(self, filename):
        self.bind(filename)
        data = read_json(filename)
        require(type(data) is dict, 'Expected object: ' + key(filename))
        normalized = set()
        for name, expected in data.get('inputs_sha256', {}).items():
            require(key(name) not in normalized, 'Repeated normalized binding: ' + key(name))
            normalized.add(key(name))
            self.bind(name, expected)
        return data

    def recheck(self):
        for name, expected in self.values.items():
            require(digest(name) == expected, 'Input changed during work: ' + name)


def normalized_bindings(data):
    return {key(name): value for name, value in data['inputs_sha256'].items()}


def preflight(args):
    require(type(args.iterations) is int and 1 <= args.iterations <= 20000,
            'Iterations must be in1..20000')
    out = path(args.out)
    require(not out.exists(), 'Fresh output directory required')
    bindings = Binding()
    bindings.bind(__file__)
    for name, expected in PINS.items():
        bindings.bind(name, expected)
    native_qa = bindings.document(DOMAIN_QA)
    gpu_qa = bindings.document(GPU_QA)
    require(native_qa['status'] == 'RUST_BATCH_STAR_DOMAIN_ORDER_PARITY_AND_CAP_RESET_PASS', 'Missing native QA')
    require(gpu_qa['status'] == 'COLD_STAR_CUDA_BOUNDED_PROTOTYPE_QA_PASS', 'Missing GPU QA')
    for qa, names in ((native_qa, (DOMAIN_EXE, 'acceleration/star_domains_batch.rs')),
                      (gpu_qa, (GPU_EXE, 'acceleration/star_pdhg_gpu.cu',
                                'acceleration/export_star_pdhg_binary.py',
                                'acceleration/star_marginal_cp_cpu_v2.py'))):
        qb = normalized_bindings(qa)
        require(all(qb.get(name) == PINS[name] for name in names), 'QA/source association')
    family = bindings.document(args.family)
    audit = bindings.document(args.family_audit)
    request = bindings.document(args.indices)
    require(family['status'] == 'COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION'
            and family['selector'] == 'cross_3_4' and family['cycle_sizes'] == [3, 4], 'Wrong family scope')
    require(audit['status'] == 'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS', 'Missing cross-family audit')
    ab = normalized_bindings(audit)
    require(ab.get(key(args.family)) == bindings.values[key(args.family)], 'Family/audit association')
    bindings.bind(family['candidate_path'], family['candidate_sha256'])
    require(ab.get(key(family['candidate_path'])) == family['candidate_sha256'], 'Family base/audit association')
    require(request['status'] == 'EXPLICIT_FRESH_STAR_COHORT_REQUEST', 'Wrong request status')
    rb = normalized_bindings(request)
    for field, value in (('family', args.family), ('family_audit', args.family_audit)):
        require(key(request[field + '_path']) == key(value)
                and request[field + '_sha256'] == bindings.values[key(value)]
                and rb.get(key(value)) == bindings.values[key(value)], 'Request/' + field + ' association')
    require(type(request['selection_policy']) is dict and type(request['selection_policy'].get('name')) is str
            and request['selection_policy']['name'], 'Missing explicit sampling policy')
    indices = request['indices']
    require(type(indices) is list and 1 <= len(indices) <= 256
            and all(type(i) is int for i in indices) and len(set(indices)) == len(indices), 'Unique explicit indices1..256 required')
    candidates, moves = family['overlap_candidates'], family['moves']
    count = family['legal_count']
    require(type(count) is int and 0 < count == len(candidates) == len(moves)
            == len(family['original_native_indices']) == audit['legal_count'], 'Family count mismatch')
    require(all(0 <= i < count for i in indices), 'Requested index out of range')
    graph_hashes = [canonical_edges(edges) for edges in candidates]
    require(len(set(graph_hashes)) == count, 'Duplicate exact family graph')
    require(type(request['records']) is list and len(request['records']) == len(indices), 'Request record count')
    from audit_certificate import full_graph
    full_graph(read_json(family['candidate_path']))
    for index, row in zip(indices, request['records']):
        move = moves[index]
        require(type(row) is dict and type(row.get('proposal_index')) is int
                and row['proposal_index'] == index, 'Request record/order mismatch')
        require(type(row.get('roles')) is list and row['roles'] and all(type(s) is str and s for s in row['roles'])
                and len(row['roles']) == len(set(row['roles'])), 'Request roles')
        require(finite(row.get('refined_upper')), 'Nonfinite requested refined upper')
        require(move['matching_class'] == 'cross' and move['cycle_size'] in (3, 4)
                and type(row.get('root_group')) is int and row['root_group'] == move['root_group']
                and type(row.get('cycle_size')) is int and row['cycle_size'] == move['cycle_size'], 'Request geometry metadata')
        require(type(row.get('original_native_index')) is int
                and row['original_native_index'] == family['original_native_indices'][index] == move['original_native_index'], 'Original native index association')
        require(row['overlap_edges_sha256'] == graph_hashes[index], 'Request exact graph association')
        full_graph(dict(overlap_edges_outer_zero_based=candidates[index]))
    bindings.recheck()
    return dict(args=args, out=out, bindings=bindings, family=family, audit=audit,
                request=request, indices=indices, graph_hashes=graph_hashes)


def write_json(filename, value):
    with path(filename).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, separators=(',', ':'), allow_nan=False)
        f.write('\n')


def inspect_native(document, expected_caps=CAPS):
    """Validate the native schema; completeness remains a native claim."""
    require(document.get('backend') == 'rust' and document.get('caps') == expected_caps, 'Native backend/caps mismatch')
    complete = document.get('complete_domain_enumeration')
    require(type(complete) is bool and type(document.get('total_nodes')) is int
            and document['total_nodes'] >= 0, 'Native completeness/node type')
    require(all(finite(document.get(k)) and document[k] >= 0 for k in ('enumeration_seconds', 'elapsed_seconds')), 'Native timing')
    rows = document['domains']
    require(type(rows) is list and 1 <= len(rows) <= 84
            and [r['outer_vertex'] for r in rows] == list(range(len(rows))), 'Native domain row order')
    caps = []
    counts = []
    for row in rows:
        require(type(row['outer_vertex']) is int and type(row['nodes']) is int and row['nodes'] >= 0, 'Native row metadata')
        require(type(row['domain_masks_hex']) is list, 'Native mask list')
        masks = []
        for value in row['domain_masks_hex']:
            require(type(value) is str and value.startswith('0x'), 'Native mask encoding')
            mask = int(value, 16)
            require(value == hex(mask) and 0 <= mask < 1 << 84 and mask.bit_count() == 8
                    and not (mask >> row['outer_vertex'] & 1), 'Native mask format')
            masks.append(mask)
        require(masks == sorted(set(masks)), 'Native masks not sorted/unique')
        require(row['status'] in ('COMPLETE', 'INCOMPLETE'), 'Unknown native row status')
        if row['status'] == 'COMPLETE':
            require(row['cap_reason'] is None, 'Complete row with cap')
        else:
            require(row['cap_reason'] in ('TIME_CAP', 'GLOBAL_NODE_CAP', 'PER_VERTEX_DOMAIN_CAP'), 'Unknown native cap')
            caps.append(row['cap_reason'])
        counts.append(len(masks))
    if complete:
        require(len(rows) == 84 and not caps, 'Incomplete rows declared complete')
        propagation = document.get('propagation', {})
        require(propagation.get('status') in ('EMPTY_DOMAIN', 'ARC_CONSISTENT_NONEMPTY'), 'Native reciprocal status')
        expected = 'COMPLETE_DOMAINS_RECIPROCITY_' + propagation['status']
        require(document['status'] == expected, 'Native status/propagation mismatch')
    else:
        require(document['status'] == 'INCOMPLETE' and len(caps) == 1
                and rows[-1]['status'] == 'INCOMPLETE' and 'propagation' not in document,
                'Incomplete native result propagated')
    reason = 'INCOMPLETE_NATIVE_DOMAINS' if not complete else 'EMPTY_ORIGINAL_DOMAIN' if not all(counts) else None
    return counts, reason


def fits_chunk(totals, metadata):
    return (totals['count'] + 1 <= LIMITS['chunk_count']
            and totals['N'] + metadata['N'] <= LIMITS['total_N']
            and totals['M'] + metadata['M'] <= LIMITS['total_M']
            and totals['nnz'] + metadata['nnz'] <= LIMITS['total_nnz']
            and totals['bytes'] + metadata['byte_length'] <= LIMITS['binary_bytes'])


def check_gpu(document, cases, iterations):
    require(document['status'] == 'NUMERICAL_COLD_STAR_PDHG_BATCH_FINISHED'
            and document['candidate_count'] == len(cases) == len(document['results'])
            and document['eta'] == .9 and document['theta'] == 1 and document['float_type'] == 'float64'
            and document['numerical_scores_are_proofs'] is False
            and document['initialization'] == 'uniform_per_simplex_probability_zero_dual'
            and document['best_scope'] == 'initial_and_requested_checkpoint_last_and_average'
            and document['scalar_metrics_computed_on_host'] is True, 'GPU result header/scope')
    for name in ('parse_seconds', 'gpu_iteration_seconds', 'checkpoint_transfer_and_metrics_seconds', 'elapsed_seconds'):
        require(finite(document[name]) and document[name] >= 0, 'GPU timing invalid')
    scores = []
    for position, (result, case) in enumerate(zip(document['results'], cases)):
        require(type(result['candidate_index']) is int and result['candidate_index'] == position
                and result['n_variables'] == case['N'] and result['n_rows'] == case['M']
                and result['n_equalities'] == case['Q'] and result['domain_counts'] == case['domain_counts'], 'GPU candidate/model association')
        checkpoints = result['checkpoints']
        require(len(checkpoints) == 1 and type(checkpoints[0]['iterations']) is int
                and checkpoints[0]['iterations'] == iterations, 'GPU checkpoint association')
        cp = checkpoints[0]
        values = [result['initial'], cp['last'], cp['average']]
        for value in values:
            require(all(finite(value[k]) for k in ('primal_upper_numeric', 'dual_lower_numeric', 'numeric_gap')), 'Nonfinite GPU scalar')
            require(value['primal_upper_numeric'] >= -1e-10
                    and value['dual_lower_numeric'] <= value['primal_upper_numeric'] + 1e-7,
                    'GPU primal/dual numerical sanity')
            require(abs(value['numeric_gap'] - (value['primal_upper_numeric'] - value['dual_lower_numeric'])) <= 1e-8,
                    'GPU scalar gap arithmetic')
        upper = min(v['primal_upper_numeric'] for v in values)
        lower = max(v['dual_lower_numeric'] for v in values)
        require(finite(cp['best_upper_numeric']) and finite(cp['best_lower_numeric'])
                and cp['best_upper_numeric'] == upper and cp['best_lower_numeric'] == lower
                and lower <= upper + 1e-7, 'GPU best/checkpoint scope')
        scores.append((lower, upper))
    return scores


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
            proposal_index=index, original_native_index=family['original_native_indices'][index])
        write_json(candidate_path, candidate)
        records.append(dict(proposal_index=index, original_native_index=family['original_native_indices'][index],
            root_group=family['moves'][index]['root_group'], cycle_size=family['moves'][index]['cycle_size'],
            input_roles=requested['roles'], overlap_edges_sha256=context['graph_hashes'][index],
            candidate_path=key(candidate_path), candidate_sha256=bindings.bind(candidate_path),
            native_result_index=position, domains_path=None, domains_sha256=None,
            status='UNAVAILABLE', unavailable_reason=None, chunk_index=None, binary_candidate_index=None,
            resource_details=None,
            best_lower_numeric=None, best_upper_numeric=None))
    command = [str(path(DOMAIN_EXE)), str(native_input), str(native_output),
               str(CAPS['seconds']), str(CAPS['global_nodes']), str(CAPS['per_vertex_domains'])]
    initial_manifest = dict(status='FRESH_STAR_PDHG_RANKING_INPUTS_BOUND',
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
    summary = dict(status='NUMERICAL_FRESH_STAR_PDHG_RANKING_FINISHED', producer_version='fresh1',
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', required=True)
    parser.add_argument('--family-audit', required=True)
    parser.add_argument('--indices', required=True, help='Bound EXPLICIT_FRESH_STAR_COHORT_REQUEST JSON')
    parser.add_argument('--out', required=True)
    parser.add_argument('--iterations', type=int, default=500)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    context = preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='FRESH_STAR_PDHG_PREFLIGHT_PASS',
            input_selected_indices=context['indices'], requested_count=len(context['indices']),
            input_binding_count=len(context['bindings'].values), iterations=args.iterations,
            outputs_written=0, native_processes=0, GPU_processes=0, LP_runs=0, scope=SCOPE)))
        return
    execute(context)


if __name__ == '__main__':
    main()
