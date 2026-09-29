"""Independent exact all-column audit of the eight-coordinate filtered LP.

Expected columns come from raw full neighborhoods, never a producer builder.
SciPy is used only for exact sparse deserialization and CSR-to-CSC conversion.
Requires separately authenticated complete-domain and matching-filter gates.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback

import numpy as np
import scipy
from scipy.sparse import load_npz
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_AUDIT = ROOT/'acceleration/results/20260930_independent_review/eight_domains_claim_binding.json'
DOMAIN_AUDIT_HASH = '170871c99ed16a160bf1403e4f6443275ca00c3a6ce68775fb56ba5f02783302'
TABLES = ROOT/'acceleration/results/20260930_eight_domains/run01'
RAW_BASE = ROOT/'acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json'


def need(value,message):
    if not value:
        raise ValueError(message)


def digest(path):
    value = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            value.update(block)
    return value.hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')


def stamp():
    return datetime.now(timezone.utc).isoformat()


def expected_column(u,mask,known,edge_index,pair_index,size):
    selected = {v for v in range(size) if mask >> v & 1}
    need(mask >= 0 and mask < 1 << size and u not in selected and not known[u]&selected,
         'raw star shape')
    full = known[u]|selected
    hard = size+len(edge_index)
    expected = {u:1}
    for v in selected:
        edge = (min(u,v),max(u,v))
        need(edge in edge_index,'chosen unknown edge missing')
        expected[size+edge_index[edge]] = 1 if u < v else -1
        if u < v:
            expected[hard+pair_index[edge]] = 1
    for a,b in combinations(sorted(full),2):
        row = hard+pair_index[(a,b)]
        need(row not in expected,'moment row collision')
        expected[row] = 1
    return expected


def compare_column(indices,data,expected):
    observed = dict(zip(map(int,indices),map(int,data)))
    need(len(indices) == len(observed) == len(expected) and observed == expected,'integer column mismatch')


def calibration():
    """Fresh rook9 adjacency and eighteen exact one-hot induced witnesses."""
    adjacency = [[int(a != b and (a//3 == b//3 or a%3 == b%3)) for b in range(9)] for a in range(9)]
    need(all(sum(row) == 4 for row in adjacency),'rook degree')
    need(all(sum(adjacency[a][w]*adjacency[b][w] for w in range(9)) == 2-adjacency[a][b]
             for a,b in combinations(range(9),2)),'rook exact identity')
    records = []
    for root in range(9):
        inner = [v for v in range(9) if adjacency[root][v]]
        outer = [v for v in range(9) if v != root and v not in inner]
        pairs = list(combinations(range(4),2))
        actual_edges = [edge for edge in pairs if adjacency[outer[edge[0]]][outer[edge[1]]]]
        for fixed_count in (0,1):
            fixed = set(actual_edges[:fixed_count])
            unknown = [edge for edge in pairs if edge not in fixed]
            known = [set() for _ in outer]
            for a,b in fixed:
                known[a].add(b)
                known[b].add(a)
            masks = [sum(1 << v for v in range(4) if adjacency[outer[u]][outer[v]] and v not in known[u]) for u in range(4)]
            edge_index = {edge:i for i,edge in enumerate(unknown)}
            pair_index = {edge:i for i,edge in enumerate(pairs)}
            hard = 4+len(unknown)
            matrix = np.zeros((hard+6,4),dtype=np.int64)
            for u,mask in enumerate(masks):
                column = expected_column(u,mask,known,edge_index,pair_index,4)
                indices = sorted(column)
                values = [column[row] for row in indices]
                compare_column(indices,values,column)
                corrupt = list(values)
                corrupt[0] += 1
                try:
                    compare_column(indices,corrupt,column)
                except ValueError:
                    pass
                else:
                    raise ValueError('altered column accepted')
                for row,value in column.items():
                    matrix[row,u] = value
            rhs = [1]*4+[0]*len(unknown)+[2-int((a,b) in fixed)-sum(adjacency[outer[a]][r]*adjacency[outer[b]][r] for r in inner)
                                                        for a,b in pairs]
            need(np.array_equal(matrix.sum(axis=1),rhs),'rook one-hot equality')
            bad = matrix.copy()
            bad[0,0] += 1
            wrong = rhs.copy()
            wrong[-1] += 1
            need(not np.array_equal(bad.sum(axis=1),rhs) and not np.array_equal(matrix.sum(axis=1),wrong), 'rook corruption controls')
            records.append(dict(root=root,fixed_edges=fixed_count,positive_one_hot='PASS',
                                all_four_column_corruptions='REJECT',coefficient_corruption='REJECT',rhs_corruption='REJECT'))
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir',type=Path,required=True)
    parser.add_argument('--filter-audit',type=Path,required=True)
    parser.add_argument('--filter-audit-sha256',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=1800)
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    need(not any(args.out.iterdir()),'refuse overwrite')
    started = stamp()
    start = time.monotonic()
    deadline = start+args.seconds
    bindings = {}

    def read(path):
        bindings[key(path)] = digest(path)
        return json.loads(Path(path).read_bytes())

    controls = calibration()
    save(args.out/'controls.json',dict(status='INDEPENDENT_ROOK9_CONTROLS_PASS',records=controls))
    need(digest(DOMAIN_AUDIT) == DOMAIN_AUDIT_HASH,'independent domain gate hash')
    need(digest(args.filter_audit) == args.filter_audit_sha256,'independent filter gate hash')
    domain_audit = read(DOMAIN_AUDIT)
    filter_audit = read(args.filter_audit)
    need(domain_audit['status'] == 'INDEPENDENT_EIGHT_COORDINATE_ALL84_BINDING_PASS','domain gate status')
    need(filter_audit['status'] == 'INDEPENDENT_EIGHT_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS','filter gate status')
    need(filter_audit['producer_imported'] is False,'filter separation record')
    primary = read(TABLES/'manifest.json')
    baseline = read(RAW_BASE)
    manifest = read(args.model_dir/'build_manifest.json')
    summary = read(args.model_dir/'build_summary.json')
    meta = read(args.model_dir/'model.json')
    read(args.model_dir/'controls.json')
    for source,value in manifest['inputs_sha256'].items():
        need(digest(ROOT/source) == value,'model input changed: '+source)
        bindings[source] = value
    for name,value in summary['output_sha256'].items():
        need(digest(args.model_dir/name) == value,'model output changed: '+name)
        bindings[key(args.model_dir/name)] = value
    # Raw domain scope is independently reconstructed; the larger sound filter
    # audit is consumed by its exact pinned report and exact table identities.
    labels = sorted([(a,b) for a in range(14) for b in range(a+1,14) if a//2 != b//2],
                    key=lambda pair:(pair[0]//2,pair[1]//2,pair[0]%2,pair[1]%2))
    support = [{a//2,b//2} for a,b in labels]
    pairs = list(combinations(range(84),2))
    freed = {edge for edge in pairs if len(support[edge[0]]&support[edge[1]]) == 1 and
             any(s < 8 and s in labels[edge[1]] for s in labels[edge[0]])}
    fixed = set(map(tuple,baseline['overlap_edges_outer_zero_based']))-freed
    unknown = sorted(freed|{edge for edge in pairs if support[edge[0]].isdisjoint(support[edge[1]])})
    need(len(fixed) == 120 and len(unknown) == 2160 and len(freed) == 480,'scope counts')
    need(primary['remaining_fixed_K_edges_outer'] == sorted(map(list,fixed))
         and primary['unknown_edges_outer'] == list(map(list,unknown)),'fixed scope identity')
    known = [set() for _ in range(84)]
    for a,b in fixed:
        known[a].add(b)
        known[b].add(a)
    edge_index = {edge:i for i,edge in enumerate(unknown)}
    pair_index = {edge:i for i,edge in enumerate(pairs)}
    domain_records = {record['outer_vertex']:record for record in domain_audit['records']}
    filtered = {record['outer_vertex']:record for record in filter_audit['records']}
    need(len(filtered) == len(filter_audit['records']) == 84 and set(filtered) == set(range(84)), 'filter center coverage')
    tables = []
    retained = []
    original_offsets = [0]
    offsets = [0]
    for u in range(84):
        path = TABLES/f'domain_{u:02d}.json'
        table = read(path)
        need(digest(path) == domain_records[u]['raw_sha256'], 'independently complete table binding')
        need(key(path) in filter_audit['inputs_sha256'] and digest(path) == filter_audit['inputs_sha256'][key(path)], 'independent filter table binding')
        raw_masks = [int(mask,16) for mask in table['domain_masks_hex']]
        row = filtered[u]
        need(row['original_count'] == len(raw_masks) == domain_records[u]['domain_size'], 'original population')
        rejected = set(row['rejected_ids'])
        need(len(rejected) == len(row['rejected_ids']) == row['rejected_count']
             and all(type(i) is int and 0 <= i < len(raw_masks) for i in rejected), 'rejected ID identity')
        ids = [i for i in range(len(raw_masks)) if i not in rejected]
        need(len(ids) == row['surviving_count'] and ids,'nonempty survivor count')
        retained.append(ids)
        tables.append([raw_masks[i] for i in ids])
        original_offsets.append(original_offsets[-1]+len(raw_masks))
        offsets.append(offsets[-1]+len(ids))
    n = offsets[-1]
    hard = 84+len(unknown)
    need(original_offsets[-1] == 2290122 == domain_audit['domain_choices'],'complete population total')
    need(meta['retained_original_domain_ids'] == retained and meta['original_probability_offsets'] == original_offsets
         and meta['probability_offsets'] == offsets,'exact original IDs/offsets')
    need(meta['supports'] == list(map(list,labels)) and meta['fixed_edges'] == sorted(map(list,fixed))
         and meta['unknown_edges'] == list(map(list,unknown)) and meta['pair_order'] == list(map(list,pairs)), 'model ordering/scope')
    expected_nnz = sum(1+mask.bit_count()+66+(mask>>(u+1)).bit_count() for u,table in enumerate(tables) for mask in table)+6972
    need(tuple(meta['shape']) == (5730,n+6972) and meta['nonzeros'] == expected_nnz, 'shape/nonzero projection')
    need(summary['original_choices'] == original_offsets[-1] and summary['retained_choices'] == n
         and summary['removed_choices'] == original_offsets[-1]-n,'build counts')
    for path in (__file__,ROOT/'uv.lock',ROOT/'pyproject.toml'):
        bindings[key(path)] = digest(path)
    frozen = dict(started_at=started,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  numpy=np.__version__,scipy=scipy.__version__,inputs_sha256=dict(bindings),
                  question='Does the complete saved exact integer LP equal the independently derived necessary filtered moment encoding?',
                  scope=primary['scope'],selection='Every retained original-ID probability column and every slack, with every bound/cost/RHS checked',
                  criterion='Exact integer equality; reject any extra/missing coefficient, mismapped ID, or altered coefficient/RHS/bound',
                  limits=dict(wall_seconds=args.seconds),shape=[5730,n+6972],projected_nonzeros=expected_nnz,
                  array_projection_bytes=dict(two_csr_csc_values_indices=10*expected_nnz,
                     both_index_pointer_upper_bound=8*((n+6973)+5731)),
                  projection_limitation='Typed-array estimate only; Python table metadata, decompression, and conversion temporary memory are additional. Not measured peak.',
                  numerical_settings='Exact integer arithmetic; no numerical acceptance tolerance',producer_imported=False,solver_launched=False)
    save(args.out/'manifest.json',frozen)
    need(time.monotonic() < deadline,'wall cap before sparse load')
    matrix_path = args.model_dir/'integer_augmented_csr.npz'
    need(digest(matrix_path) == meta['matrix_sha256'],'matrix hash')
    actual = load_npz(matrix_path)
    need(actual.format == 'csr' and actual.has_canonical_format and np.issubdtype(actual.dtype,np.integer)
         and actual.shape == (5730,n+6972) and actual.nnz == expected_nnz,'exact canonical CSR storage')
    need(set(map(int,np.unique(actual.data))) == {-1,1},'coefficient values')
    columns = actual.tocsc()
    need(columns.has_canonical_format,'converted columns canonical')
    checked = 0
    reports = []
    for u,table in enumerate(tqdm(tables,desc='Independent eight-coordinate LP columns',unit='center')):
        for j,mask in enumerate(table,offsets[u]):
            if j%512 == 0:
                need(time.monotonic() < deadline,'wall cap during full column audit')
            need(len(known[u])+mask.bit_count() == 12,'full outer neighborhood size')
            expected = expected_column(u,mask,known,edge_index,pair_index,84)
            begin,end = int(columns.indptr[j]),int(columns.indptr[j+1])
            compare_column(columns.indices[begin:end],columns.data[begin:end],expected)
            checked += len(expected)
        row = dict(outer_vertex=u,probability_columns_checked=len(table),cumulative_columns=offsets[u+1],
                   cumulative_nonzeros_checked=checked,completed_at=stamp())
        reports.append(row)
        save(args.out/f'center_{u:02d}.json',row)
    for k in range(6972):
        begin,end = int(columns.indptr[n+k]),int(columns.indptr[n+k+1])
        compare_column(columns.indices[begin:end],columns.data[begin:end],{hard+k%3486:-1 if k<3486 else 1})
        checked += 1
    rhs = [1]*84+[0]*2160+[2-len(set(labels[a])&set(labels[b]))-int((a,b) in fixed) for a,b in pairs]
    need(meta['rhs'] == rhs and meta['costs'] == [0]*n+[1]*6972 and meta['column_lower'] == 0
         and meta['column_upper'] is None and meta['all_rows_equalities'] is True,'objective, bounds, and RHS')
    need(checked == expected_nnz,'all coefficients checked')
    # Check public byte-parts by direct sequential comparison to the audited raw
    # bytes. This proves concatenation identity without using the producer's
    # recovery routine. No second full in-memory copy is made.
    chunks = read(args.model_dir/'chunk_manifest.json')
    chunk_records = []
    for artifact in chunks['artifacts']:
        need(Path(artifact['source']).name == artifact['source'],'confined chunk source')
        path = args.model_dir/artifact['source']
        total = 0
        joined = sha256()
        with path.open('rb') as raw_stream:
            for part in artifact['parts']:
                need(Path(part['path']).name == part['path'],'confined part')
                part_path = args.model_dir/part['path']
                block = part_path.read_bytes()
                need(len(block) == part['bytes'] and sha256(block).hexdigest() == part['sha256']
                     and raw_stream.read(len(block)) == block,'chunk bytes/hash')
                bindings[key(part_path)] = part['sha256']
                joined.update(block)
                total += len(block)
            need(raw_stream.read(1) == b'','extra raw source bytes')
        need(total == artifact['source_bytes'] and joined.hexdigest() == artifact['source_sha256'] == digest(path),'chunk union identity')
        chunk_records.append(dict(source=key(path),bytes=total,parts=len(artifact['parts']),sha256=joined.hexdigest()))
    need(all(digest(ROOT/path) == value for path,value in bindings.items()),'input stability')
    report = dict(status='INDEPENDENT_EIGHT_COORDINATE_FILTERED_FULL_MOMENT_MODEL_PASS',
                  claim_id='C-PARTIAL-K-EIGHT-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING',claim_revision=1,recommendation='VERIFIED',
                  statement='Every SRG completion in the recorded eight-coordinate 120-fixed-K-edge family induces a zero-objective feasible point of the exact saved matching-filtered full-neighborhood moment LP. No converse is asserted.',
                  started_at=started,completed_at=stamp(),source_commit=frozen['source_commit'],command=frozen['command'],
                  working_directory=frozen['working_directory'],python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent exact column reconstruction and mathematical necessity derivation',
                  inputs_sha256=bindings,shape=list(actual.shape),nonzeros=checked,objective=meta['model'],
                  original_probability_columns=original_offsets[-1],retained_original_probability_columns=n,
                  removed_original_probability_columns=original_offsets[-1]-n,hard_simplex_rows=84,hard_reciprocity_rows=2160,
                  soft_moment_rows=3486,slack_columns=6972,records=reports,controls=controls,
                  all_raw_neighborhood_columns_checked=True,all_bounds_costs_rows_slacks_checked=True,chunk_identity_checks=chunk_records,
                  derivation='A completion selects one complete-domain star at each center; the sound necessary matching filter preserves it. The selected one-hot point satisfies each simplex and reciprocity row. At outer pair(a,b), summing full-neighborhood pair incidences counts all common outer neighbors; the smaller-endpoint chosen-edge term counts unknown adjacency once. The SRG identity gives common_outer+A_unknown=2-common_inner-B_fixed. All moment slacks can therefore be zero. Nonnegative slacks have unit costs, so this point has objective zero.',
                  dependencies=[dict(id='C-PARTIAL-K-EIGHT-COORDINATE-DOMAINS',revision=1,relation='coverage'),
                                dict(id='C-PARTIAL-K-EIGHT-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER',revision=1,relation='uses_result')],
                  scope=primary['scope'],producer_imported=False,
                  shared_components=['Python standard library','NumPy/SciPy exact sparse storage and format conversion','tqdm','separately authenticated independent domain/filter reports'],
                  limitations=['Necessary conditional relaxation only; no feasibility, positive bound, or family exclusion established here.',
                               'No converse from LP feasibility to a graph.',
                               'Sparse deserialization and conversion trust NumPy/SciPy; no independent NPZ decoder implemented.',
                               'Model-audit checkpoints record completed checks, not a serialized recursive or solver state.'],
                  elapsed_seconds=time.monotonic()-start,artifact_availability='LOCAL_ONLY',
                  artifact_availability_reason='Local artifact check before publication; chunk identities checked separately',
                  target_resolution=False,external_review=False,solver_launched=False)
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],shape=report['shape'],nonzeros=checked,sha256=digest(args.out/'summary.json'))))


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        # Preserve a failed attempt without converting a resource interruption
        # or missing gate into a mathematical refutation.
        if '--out' in sys.argv:
            destination = Path(sys.argv[sys.argv.index('--out')+1])
            destination.mkdir(parents=True,exist_ok=True)
            failure_path = destination/'failure.json'
            if not failure_path.exists():
                save(failure_path,dict(status='INCOMPLETE_OR_FAILED_MODEL_AUDIT',timestamp=stamp(),
                     exception_type=type(error).__name__,reason=str(error),traceback=traceback.format_exc(),
                     command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
                     auditor_sha256=digest(__file__),target_resolution=False,
                     limitation='Completed center receipts, if any, do not establish full encoding verification.'))
        raise
