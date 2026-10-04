"""SOURCE ONLY: exact F3/E census of every labelled two-line exclusive swap.

No frozen root, lambda-zero restriction, stochastic engine or target caller.
Fresh finite controls and independent checking are required before execution.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/census_20261003_ternary_two_line_v1.py'
SPEC = 'acceleration/census_20261003_ternary_two_line_v1_spec.md'
STRUCTURE = 'acceleration/census_20261003_weight60_two_line_v2.py'
STRUCTURE_SHA = 'c98fc050e6c99ab4cce045052230cd648d080041ec7bbf22d9d2be0f3729c149'
STRUCTURE_SPEC = 'acceleration/census_20261003_weight60_two_line_v2_spec.md'
STRUCTURE_SPEC_SHA = 'cb42cdc0c6d34349382eb0abcdb2c5d9d19ccbfd4abbaa7d056e46863f39dad6'
IO = 'acceleration/census_20261003_root_focused_restricted_three_line_v3.py'
IO_SHA = '493aeace43b91c755c2c038db0ab71fd61f4acbcf62d7a717b07894fb7f0f41e'
IO_SPEC = 'acceleration/census_20261003_root_focused_restricted_three_line_v3_spec.md'
IO_SPEC_SHA = 'e2dcded34b2deb6f5eb0c326353487bb741e5b22eae9447d5216902982bc0164'
REFERENCE = 'acceleration/theory_20261003_hypergraph_ternary_residue_reference_v1.py'
REFERENCE_SHA = '692ecf18fc0e8c3df95c8f8609953b7c971692b5b77cdc10d8707954aa47baca'
OBJECTIVE = 'SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1'
RECORD_SCHEMA = 'TERNARY_TWO_LINE_LABELLED_PROPOSAL_V1'
CHECKPOINT_SCHEMA = 'TERNARY_TWO_LINE_CENSUS_CHECKPOINT_V1'
MANIFEST_SCHEMA = 'TERNARY_TWO_LINE_CENSUS_MANIFEST_V1'
CHUNK = 5000
MAX_LINE = 8192
PAPERS = {
    'docs/DESIGN_20261003_HYPERGRAPH_TERNARY_RESIDUE_SEARCH_V1.md': '2484f9828a8d8eaa2e79b17672917140fe3f024646355f74a77db106025fc7ad',
    'docs/CANDIDATE_20261003_TERNARY_DEGREE14_EXACTNESS_V1.md': '274ce3fb355f69068bec254782f9f7d72c5b28e7e0dd53ca655c292dd6361582',
    'acceleration/audit_20261003_ternary_degree14_exactness_v1.md': '9f34fc4842379b026eb01430b25edb0a4911ddac713b9dae05f15b2bc9336d24',
    'docs/CANDIDATE_20261003_TERNARY_RESIDUE_ENERGY_BOUNDS_V1.md': '82f92749d30949fe0dcdcfcf3aab15256f90c31bfcbb1208350397870a123392',
    'acceleration/audit_20261003_ternary_residue_energy_bounds_v1.md': 'c2ebce87570a6b0828e1ea3feb66121bab6a16f6d14e2d0e6b9d39fc3c2393bf',
}


class CheckError(ValueError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(stage + ': ' + message)


def need(ok, stage, message):
    if not ok:
        raise CheckError(stage, message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def lib():
    pins = {STRUCTURE: STRUCTURE_SHA, STRUCTURE_SPEC: STRUCTURE_SPEC_SHA,
            IO: IO_SHA, IO_SPEC: IO_SPEC_SHA, REFERENCE: REFERENCE_SHA, **PAPERS}
    for path, identity in pins.items():
        need(sha(ROOT / path) == identity, 'SOURCE', 'exact preserved source/paper:' + path)
    structure = module(STRUCTURE, 'unchanged_all_line_structure')
    io = module(IO, 'unchanged_strict_record_io')
    reference = module(REFERENCE, 'author_scalar_ternary_reference')
    return structure, io, reference, pins


def weight(n, graph_degree):
    return 819820 if (n, graph_degree) == (99, 14) else n * (n - 1) // 2 * graph_degree * graph_degree + 1


def cost(common, adjacent):
    need(type(common) is int and common >= 0 and type(adjacent) is int and adjacent in (0, 1),
         'PAIR_COST', 'exact integer CN and binary adjacency')
    residual = common + adjacent - 2
    return int(residual % 3 != 0), residual * residual if adjacent else 0, residual * residual if not adjacent else 0, residual % 3


def score(masks, point_degree):
    need(type(masks) is list and 3 <= len(masks) <= 99 and type(point_degree) is int
         and 0 < 2 * point_degree < len(masks), 'SCORE_DOMAIN', 'complete typed finite regular domain')
    n = len(masks)
    need(all(type(m) is int and m >= 0 and m.bit_count() == 2 * point_degree for m in masks),
         'SCORE_DOMAIN', 'exact integer regular adjacency masks')
    f3 = lam = mu = 0
    hist = [0, 0, 0]
    cn = [[0] * n for _ in range(n)]
    for u in range(n):
        need(not ((masks[u] >> u) & 1) and masks[u] < (1 << n), 'SCORE_DOMAIN', 'binary zero diagonal bounded rows')
        for v in range(u + 1, n):
            adjacent = (masks[u] >> v) & 1
            need(adjacent == ((masks[v] >> u) & 1), 'SCORE_DOMAIN', 'symmetric literal adjacency')
            common = (masks[u] & masks[v]).bit_count()
            cn[u][v] = cn[v][u] = common
            f, a, b, residue = cost(common, adjacent)
            f3 += f
            lam += a
            mu += b
            hist[residue] += 1
    metrics = dict(F3=f3, E_lambda=lam, E_mu=mu, E=lam + mu,
                   scalar_weight=weight(n, 2 * point_degree), scalar=weight(n, 2 * point_degree) * f3 + lam + mu,
                   residue_population=hist)
    score_necessity(n, point_degree, metrics)
    return metrics, cn


def score_necessity(n, point_degree, metrics):
    need(all(type(metrics[k]) is int and metrics[k] >= 0 for k in
             ['F3', 'E_lambda', 'E_mu', 'E', 'scalar_weight', 'scalar'])
         and type(metrics['residue_population']) is list and len(metrics['residue_population']) == 3
         and all(type(x) is int and x >= 0 for x in metrics['residue_population'])
         and metrics['E'] == metrics['E_lambda'] + metrics['E_mu']
         and sum(metrics['residue_population']) == n * (n - 1) // 2
         and metrics['F3'] == sum(metrics['residue_population'][1:])
         and metrics['scalar_weight'] == weight(n, 2 * point_degree)
         and metrics['scalar'] == metrics['scalar_weight'] * metrics['F3'] + metrics['E'],
         'SCORE_NECESSITY', 'typed integer score components and literal pair population')
    if (n, point_degree) == (99, 7):
        f3, energy, hist = metrics['F3'], metrics['E'], metrics['residue_population']
        need(f3 <= energy <= 28 * f3 and (hist[1] - hist[2]) % 3 == 0,
             'TARGET_SCORE_NECESSITY', 'exact complete degree14 residue-energy necessary checks')
        need(metrics['scalar'] <= 3977766639, 'TARGET_SCORE_NECESSITY', 'recorded conservative scalar bound')


def domain(structure, n, point_degree, triples):
    need(type(n) is int and 3 <= n <= 99 and type(point_degree) is int and 0 < 2 * point_degree < n,
         'DOMAIN', 'simple regular linear triple domain')
    # The reused all-line helper computes an unused row0 diagnostic; it never
    # freezes row0, filters lambda, or restricts its all-line pair population.
    base = structure.domain(n, point_degree, triples, 0)
    metrics, cn = score(base['masks'], point_degree)
    base.update(metrics=metrics, cn=cn)
    need(base['total'] == len(triples) * (len(triples) - 1) // 2 * 9,
         'UNIVERSE', 'every literal line pair, including every root-incident line')
    if (n, point_degree) == (99, 7):
        need(len(triples) == 231 and base['total'] == 239085, 'UNIVERSE', 'exact target-domain labelled population')
    return base


def proposal(structure, base, pid):
    old = structure.proposal(base, pid)
    record = dict(schema=RECORD_SCHEMA, objective_version=OBJECTIVE, proposal_id=pid,
        i=old['i'], j=old['j'], ix=old['ix'], jy=old['jy'], old_triples=old['old_triples'], new_triples=old['new_triples'],
        valid=old['valid'], invalid_reason=old['invalid_reason'], conflict_pair=old['conflict_pair'],
        removed_pairs=None, added_pairs=None, toggles=None, changed_rows=None, delta_F3=None, delta_E_lambda=None,
        delta_E_mu=None, delta_E=None, delta_scalar=None, new_metrics=None, tuple_direction=None,
        classification=old['classification'] if not old['valid'] else None)
    if not old['valid']:
        return record
    i, j, ix, jy = (old[k] for k in ('i', 'j', 'ix', 'jy'))
    first, second = base['triples'][i], base['triples'][j]
    x, y = first[ix], second[jy]
    aa = [v for at, v in enumerate(first) if at != ix]
    bb = [v for at, v in enumerate(second) if at != jy]
    removed = [sorted((x, v)) for v in aa] + [sorted((y, v)) for v in bb]
    added = [sorted((y, v)) for v in aa] + [sorted((x, v)) for v in bb]
    masks = structure.masks_from_record(base, old)
    touched = sorted({v for edge in old['toggles'] for v in edge})
    touched_set = set(touched)
    delta_f3 = delta_lam = delta_mu = 0
    hist = base['metrics']['residue_population'][:]
    for u in touched:
        for v in range(base['n']):
            if u == v or (v in touched_set and v < u):
                continue
            before = cost(base['cn'][u][v], (base['masks'][u] >> v) & 1)
            after = cost((masks[u] & masks[v]).bit_count(), (masks[u] >> v) & 1)
            delta_f3 += after[0] - before[0]
            delta_lam += after[1] - before[1]
            delta_mu += after[2] - before[2]
            hist[before[3]] -= 1
            hist[after[3]] += 1
    need(delta_lam == old['delta_lambda'] and delta_mu == old['delta_mu'], 'CATEGORY_DELTA', 'complete category switches agree with disclosed structural scorer')
    metrics = dict(F3=base['metrics']['F3'] + delta_f3,
        E_lambda=base['metrics']['E_lambda'] + delta_lam, E_mu=base['metrics']['E_mu'] + delta_mu,
        E=base['metrics']['E'] + delta_lam + delta_mu, scalar_weight=base['metrics']['scalar_weight'],
        scalar=base['metrics']['scalar'] + base['metrics']['scalar_weight'] * delta_f3 + delta_lam + delta_mu,
        residue_population=hist)
    score_necessity(base['n'], base['degree'], metrics)
    pair = (metrics['F3'], metrics['E'])
    original = (base['metrics']['F3'], base['metrics']['E'])
    direction = 'down' if pair < original else 'up' if pair > original else 'equal'
    need((metrics['scalar'] < base['metrics']['scalar']) == (direction == 'down')
         and (metrics['scalar'] == base['metrics']['scalar']) == (direction == 'equal'), 'OBJECTIVE_ORDER', 'exact scalar and tuple order agree')
    record.update(removed_pairs=removed, added_pairs=added, toggles=old['toggles'], changed_rows=touched,
        delta_F3=delta_f3, delta_E_lambda=delta_lam, delta_E_mu=delta_mu, delta_E=delta_lam + delta_mu,
        delta_scalar=metrics['scalar'] - base['metrics']['scalar'], new_metrics=metrics,
        tuple_direction=direction, classification='valid_F3_' + ('down' if delta_f3 < 0 else 'up' if delta_f3 > 0 else 'equal'))
    return record


def candidate(structure, base, record):
    need(type(record) is dict and record.get('valid') is True, 'RECORD_VALIDITY', 'only literal valid records have a graph')
    masks = structure.masks_from_record(base, record)
    triples = [row[:] for row in base['triples']]
    triples[record['i']], triples[record['j']] = [row[:] for row in record['new_triples']]
    return masks, triples


def cache_check(structure, io, base):
    fresh = domain(structure, base['n'], base['degree'], base['triples'])
    for key, stage in [('masks', 'ADJ_CACHE'), ('cn', 'CN_CACHE'), ('metrics', 'SCORE_CACHE'), ('pairs', 'UNIVERSE_CACHE'), ('total', 'UNIVERSE_CACHE')]:
        need(io.canonical(fresh[key]) == io.canonical(base[key]), stage, 'complete strictly typed cache:' + key)


def record_check(structure, io, base, record):
    need(type(record) is dict and type(record.get('proposal_id')) is int and 0 <= record['proposal_id'] < base['total'],
         'RECORD_ID', 'literal integer labelled ID')
    expected = proposal(structure, base, record['proposal_id'])
    need(set(record) == set(expected) and record.get('schema') == RECORD_SCHEMA and record.get('objective_version') == OBJECTIVE,
         'RECORD_SCHEMA', 'closed changed-objective schema')
    topology = ['i', 'j', 'ix', 'jy', 'old_triples', 'new_triples', 'valid', 'invalid_reason', 'conflict_pair',
                'removed_pairs', 'added_pairs', 'toggles', 'changed_rows']
    need(all(io.canonical(record[k]) == io.canonical(expected[k]) for k in topology), 'RECORD_TOPOLOGY', 'exact typed swap and net cancellations')
    need(io.canonical(record) == io.canonical(expected), 'RECORD_SCORE', 'all exact residues, components, categories and tuple comparison')


def accumulator():
    return dict(counts=Counter(), tuple_directions=Counter(), unique=set(), best_pair=None, best=[], best_f3=None, f3_best=[], residue_zero=[])


def accumulate(a, record):
    a['counts'][record['classification']] += 1
    if not record['valid']:
        return
    a['tuple_directions'][record['tuple_direction']] += 1
    a['unique'].add(tuple(tuple(e) for e in record['toggles']))
    metrics = record['new_metrics']
    pair = (metrics['F3'], metrics['E'])
    if a['best_pair'] is None or pair < a['best_pair']:
        a['best_pair'], a['best'] = pair, [record]
    elif pair == a['best_pair']:
        a['best'].append(record)
    if a['best_f3'] is None or metrics['F3'] < a['best_f3']:
        a['best_f3'], a['f3_best'] = metrics['F3'], [record]
    elif metrics['F3'] == a['best_f3']:
        a['f3_best'].append(record)
    if metrics['F3'] == 0:
        a['residue_zero'].append(record)


def snapshot(a):
    return dict(counts=dict(sorted(a['counts'].items())), tuple_directions=dict(sorted(a['tuple_directions'].items())),
        unique_valid_neighbor_graphs=len(a['unique']), minimum_pair=None if a['best_pair'] is None else list(a['best_pair']),
        minimum_pair_proposal_ids=[r['proposal_id'] for r in a['best']], minimum_F3=a['best_f3'],
        minimum_F3_proposal_ids=[r['proposal_id'] for r in a['f3_best']], residue_zero_proposal_ids=[r['proposal_id'] for r in a['residue_zero']])


def enumerate_to(structure, io, base, out, deadline, identity, limit=None, resume=None, chunk=CHUNK, progress=True):
    need(type(chunk) is int and 0 < chunk <= CHUNK, 'CHUNK', 'bounded raw part population')
    out.mkdir(parents=True, exist_ok=False)
    start, parts, checkpoints, a = 0, [], [], accumulator()
    if resume is not None:
        need(type(resume) is dict and set(resume) == {'schema', 'identity', 'next_proposal_id', 'parts', 'aggregate'}
             and type(resume.get('next_proposal_id')) is int and type(resume.get('parts')) is list
             and type(resume.get('aggregate')) is dict, 'CHECKPOINT_TYPES', 'strict typed prefix header')
        need(resume.get('schema') == CHECKPOINT_SCHEMA and io.canonical(resume['identity']) == io.canonical(identity),
             'CHECKPOINT_IDENTITY', 'same exact graph, objective and software')
        for part in resume['parts']:
            io.part_types(part)
            need(part['start'] == start, 'PART_SEQUENCE', 'contiguous prefix')
            for record in io.read_part(part):
                record_check(structure, io, base, record)
                accumulate(a, record)
            parts.append(part)
            start = part['end']
        need(start == resume['next_proposal_id'] and io.canonical(snapshot(a)) == io.canonical(resume['aggregate']),
             'CHECKPOINT_AGGREGATE', 'full literal prefix aggregate reproduction')
    need(limit is None or (type(limit) is int and limit >= 0), 'CHECKPOINT_TYPES', 'exact integer prefix request')
    stop = base['total'] if limit is None else min(limit, base['total'])
    need(type(stop) is int and 0 <= start <= stop <= base['total'], 'CHECKPOINT_TYPES', 'bounded exact integer prefix')
    counter, budget_stop = start, False
    bar = tqdm(total=stop - start, desc='Exact ternary two-line proposals', unit='proposal', mininterval=1, disable=not progress)
    while counter < stop:
        if deadline is not None and (deadline.status()['stop_required'] or deadline.status()['remaining_seconds'] <= 20):
            budget_stop = True
            break
        begin = counter
        target = out / f'part_{begin:09d}.jsonl.gz'
        digest, raw_bytes = hashlib.sha256(), 0
        with target.open('xb') as file:
            with gzip.GzipFile(filename='', fileobj=file, mode='wb', compresslevel=1, mtime=0) as writer:
                while counter < min(stop, begin + chunk):
                    if (counter - begin) % 100 == 0 and deadline is not None and (deadline.status()['stop_required'] or deadline.status()['remaining_seconds'] <= 20):
                        budget_stop = True
                        break
                    record = proposal(structure, base, counter)
                    raw = io.canonical(record)
                    need(len(raw) <= MAX_LINE, 'RECORD_LENGTH', 'bounded complete canonical record')
                    writer.write(raw)
                    digest.update(raw)
                    raw_bytes += len(raw)
                    accumulate(a, record)
                    counter += 1
                    bar.update(1)
        parts.append(dict(path=target.relative_to(ROOT).as_posix(), start=begin, end=counter, record_count=counter - begin,
            raw_bytes=raw_bytes, raw_sha256=digest.hexdigest(), gzip_bytes=target.stat().st_size, gzip_sha256=sha(target)))
        cp = out / f'checkpoint_{counter:09d}.json'
        io.save(cp, dict(schema=CHECKPOINT_SCHEMA, identity=identity, next_proposal_id=counter, parts=parts, aggregate=snapshot(a)))
        checkpoints.append(dict(path=cp.relative_to(ROOT).as_posix(), sha256=sha(cp)))
        if budget_stop:
            break
    bar.close()
    if not checkpoints:
        cp = out / f'checkpoint_{counter:09d}.json'
        io.save(cp, dict(schema=CHECKPOINT_SCHEMA, identity=identity, next_proposal_id=counter, parts=parts, aggregate=snapshot(a)))
        checkpoints.append(dict(path=cp.relative_to(ROOT).as_posix(), sha256=sha(cp)))
    io.save(out / 'minimum_F3_ties.json', dict(records=a['f3_best'], scope='All labelled minimumF3 ties in this saved prefix.'))
    io.save(out / 'minimum_pair_ties.json', dict(records=a['best'], scope='All labelled minimum(F3,E) ties in this saved prefix.'))
    selected = min(a['best'], key=lambda r: r['proposal_id']) if a['best'] else None
    if selected is not None:
        masks, triples = candidate(structure, base, selected)
        (out / 'selected_neighbor.adj').write_bytes(structure.adjacency_bytes(masks))
        io.save(out / 'selected_neighbor_triples.json', dict(n=base['n'], point_degree=base['degree'], ordered_triples=triples,
            proposal_id=selected['proposal_id'], objective_version=OBJECTIVE, historical_native_state_written=False))
    zeros = []
    by_matrix = {}
    if base['metrics']['F3'] == 0:
        by_matrix[sha_bytes(structure.adjacency_bytes(base['masks']))] = (None, base['masks'], base['triples'])
    for record in a['residue_zero']:
        masks, triples = candidate(structure, base, record)
        identity_sha = sha_bytes(structure.adjacency_bytes(masks))
        if identity_sha not in by_matrix:
            by_matrix[identity_sha] = (record['proposal_id'], masks, triples)
    if by_matrix:
        zero_out = out / 'residue_zero_objects'
        zero_out.mkdir()
        for at, (identity_sha, (pid, masks, triples)) in enumerate(sorted(by_matrix.items())):
            path = zero_out / f'object_{at:06d}.adj'
            path.write_bytes(structure.adjacency_bytes(masks))
            rows = zero_out / f'object_{at:06d}.triples.json'
            io.save(rows, dict(n=base['n'], point_degree=base['degree'], ordered_triples=triples, proposal_id=pid))
            zeros.append(dict(adjacency_path=path.relative_to(ROOT).as_posix(), adjacency_sha256=identity_sha,
                triples_path=rows.relative_to(ROOT).as_posix(), triples_sha256=sha(rows), proposal_id=pid,
                target99_domain=(base['n'], base['degree']) == (99, 7), independent_full_SRG_validation_pending=True))
    manifest = dict(schema=MANIFEST_SCHEMA, identity=identity, objective_version=OBJECTIVE, population=base['total'],
        completed_proposals=counter, starting_proposal_id=start, proposals_evaluated_this_invocation=counter - start,
        parts=parts, checkpoints=checkpoints, aggregate=snapshot(a), baseline_metrics=base['metrics'],
        status='CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK' if counter == base['total'] else 'UNKNOWN_PREFIX_ONLY',
        budget_stop=budget_stop, selection_rule='Every valid proposal eligible; minimize exact(F3,E), then proposalID.',
        selected_proposal_id=None if selected is None else selected['proposal_id'], residue_zero_objects=zeros,
        producer='/root/native_driver', independent_approval=False, target_resolution='NONE', historical_native_state_written=False,
        limitations=['One exact graph/all labelled two-line proposals only; no graph-space, ergodicity or target exclusion.',
                    'No frozen root, lambda0 acceptance or stochastic search exists in this kernel.',
                    'Generic fixture residue zero is not a target99 certificate; any actual99 zero needs independent fullintegerSRG validation.'])
    io.save(out / 'manifest.json', manifest)
    return manifest


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def fixtures():
    return dict(
        rook9=dict(n=9, point_degree=2, triples=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]),
        prism9=dict(n=9, point_degree=2, triples=[[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]),
        cube12=dict(n=12, point_degree=2, triples=[[0,1,2],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[7,10,11]]))


def engineering(structure, io, reference, out, deadline, software, source_commit):
    out.mkdir(parents=True, exist_ok=False)
    results, negatives, record_count, calls, valid_count = {}, [], 0, 0, 0
    branch = Counter()
    def reject(label, stage, call, artifact):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'finite control preservation reserve')
        io.save(out / (label + '.json'), artifact)
        try:
            call()
        except (CheckError, structure.CheckError, io.CheckError) as error:
            need(error.stage == stage, 'CONTROL', 'exact rejection diagnostic:' + label)
            negatives.append(dict(case=label, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error)))
            return
        raise CheckError('CONTROL', 'accepted corrupted control:' + label)
    for name, fixture in fixtures().items():
        io.save(out / (name + '.json'), fixture)
        base = domain(structure, **fixture)
        need(base['total'] == (252 if name == 'cube12' else 135), 'CONTROL', 'complete canonical i<j fixture population')
        matrix = [[(row >> j) & 1 for j in range(base['n'])] for row in base['masks']]
        oracle = reference.complete_score(matrix, 2 * base['degree'])
        need(io.canonical(base['metrics']) == io.canonical(dict(F3=oracle['f3'], E_lambda=oracle['e_lambda'], E_mu=oracle['e_mu'],
            E=oracle['ordinary_energy'], scalar_weight=oracle['scalar_weight'], scalar=oracle['scalar_score'], residue_population=oracle['residue_population'])),
            'CONTROL', 'full direct author-reference scalar score')
        if name == 'rook9':
            need(base['metrics']['F3'] == base['metrics']['E'] == 0, 'CONTROL', 'known rook9 exact genericSRG positive, not99certificate')
        if name == 'prism9':
            need(base['metrics']['E_lambda'] > 0, 'CONTROL', 'positive-lambda graph is admitted to complete domain')
        identity = dict(fixture=name, software=software, n=base['n'], point_degree=base['degree'], total=base['total'], objective_version=OBJECTIVE)
        whole = enumerate_to(structure, io, base, out / (name + '_whole'), deadline, identity, chunk=50, progress=False)
        prefix = enumerate_to(structure, io, base, out / (name + '_prefix17'), deadline, identity, limit=17, chunk=50, progress=False)
        checkpoint = io.strict_json((ROOT / prefix['checkpoints'][-1]['path']).read_bytes())
        resumed = enumerate_to(structure, io, base, out / (name + '_resumed'), deadline, identity, resume=checkpoint, chunk=50, progress=False)
        records = [r for part in whole['parts'] for r in io.read_part(part)]
        replay = [r for part in resumed['parts'] for r in io.read_part(part)]
        need(io.canonical(records) == io.canonical(replay) and io.canonical(whole['aggregate']) == io.canonical(resumed['aggregate']),
             'CONTROL', 'exact complete whole-versus-split records and aggregate')
        for record in records:
            record_check(structure, io, base, record)
            raw_move = reference.exclusive_swap(base['n'], base['degree'], base['triples'],
                record['i'], record['j'], record['ix'], record['jy'])
            need(raw_move['valid'] is record['valid'], 'CONTROL', 'all labels match disclosed raw pair-occupancy reference')
            if not record['valid']:
                continue
            valid_count += 1
            masks, triples = candidate(structure, base, record)
            fresh = domain(structure, base['n'], base['degree'], triples)
            need(io.canonical(fresh['metrics']) == io.canonical(record['new_metrics']), 'CONTROL', 'full rescoring of every valid label')
            next_matrix = [[(row >> j) & 1 for j in range(base['n'])] for row in masks]
            need(io.canonical(next_matrix) == io.canonical(raw_move['adjacency']), 'CONTROL', 'complete raw reference candidate matrix')
            oracle = reference.complete_score(next_matrix, 2 * base['degree'])
            need(record['new_metrics']['F3'] == oracle['f3'] and record['new_metrics']['E'] == oracle['ordinary_energy'],
                 'CONTROL', 'complete direct scalar ternary/energy product')
            reverse = proposal(structure, fresh, record['proposal_id'])
            need(reverse['valid'] is True, 'CONTROL', 'every valid exclusive swap has a valid inverse')
            returned, _ = candidate(structure, fresh, reverse)
            need(returned == base['masks'], 'CONTROL', 'every valid exclusive swap exact inverse')
            overlap = bool(set(record['old_triples'][0]) & set(record['old_triples'][1]))
            branch['valid_overlap' if overlap else 'valid_disjoint'] += 1
            branch['moves_row0' if masks[0] != base['masks'][0] else 'retains_row0'] += 1
            branch['candidate_positive_lambda' if fresh['metrics']['E_lambda'] else 'candidate_lambda_zero'] += 1
        record_count += len(records)
        calls += whole['proposals_evaluated_this_invocation'] + prefix['proposals_evaluated_this_invocation'] + resumed['proposals_evaluated_this_invocation']
        results[name] = whole
        for key, stage in [('masks', 'ADJ_CACHE'), ('cn', 'CN_CACHE'), ('metrics', 'SCORE_CACHE'), ('pairs', 'UNIVERSE_CACHE'), ('total', 'UNIVERSE_CACHE')]:
            bad = copy.deepcopy(base)
            if key == 'masks': bad[key][0] = float(bad[key][0])
            elif key == 'cn': bad[key][0][0] = False
            elif key == 'metrics': bad[key]['F3'] = float(bad[key]['F3'])
            elif key == 'pairs': bad[key][0] = [True, 1]
            else: bad[key] = float(bad[key])
            reject(name + '_bad_' + key, stage, lambda b=bad: cache_check(structure, io, b), dict(cache_key=key, corrupted_value=bad[key]))
        chosen = next(r for r in records if r['valid'])
        for key in ['delta_F3', 'delta_E', 'delta_E_lambda', 'delta_E_mu', 'delta_scalar']:
            bad = copy.deepcopy(chosen)
            bad[key] += 1
            reject(name + '_record_' + key, 'RECORD_SCORE', lambda b=bad: record_check(structure, io, base, b), bad)
        for key in ['F3', 'E', 'scalar', 'residue_population']:
            bad = copy.deepcopy(chosen)
            if key == 'residue_population': bad['new_metrics'][key][1] += 1
            else: bad['new_metrics'][key] = float(bad['new_metrics'][key])
            reject(name + '_metric_' + key, 'RECORD_SCORE', lambda b=bad: record_check(structure, io, base, b), bad)
        bad = copy.deepcopy(chosen)
        bad['proposal_id'] = True
        reject(name + '_boolean_record_ID', 'RECORD_ID', lambda b=bad: record_check(structure, io, base, b), bad)
        bad = copy.deepcopy(chosen)
        bad['proposal_id'] = float(bad['proposal_id'])
        reject(name + '_float_record_ID', 'RECORD_ID', lambda b=bad: record_check(structure, io, base, b), bad)
        for key, replacement, stage in [
                ('schema', 'OLD_OBJECTIVE_RECORD', 'RECORD_SCHEMA'),
                ('objective_version', 'SRG_ROOT_LOCAL_PAIR_RESIDUAL_V1', 'RECORD_SCHEMA'),
                ('tuple_direction', 'wrong', 'RECORD_SCORE'),
                ('classification', 'valid_lambda_preserving', 'RECORD_SCORE')]:
            bad = copy.deepcopy(chosen)
            bad[key] = replacement
            reject(name + '_wrong_' + key, stage, lambda b=bad: record_check(structure, io, base, b), bad)
        bad = copy.deepcopy(chosen)
        bad['toggles'][0][0] = float(bad['toggles'][0][0])
        reject(name + '_float_toggle', 'RECORD_TOPOLOGY', lambda b=bad: record_check(structure, io, base, b), bad)
        bad = copy.deepcopy(next(r for r in records if not r['valid']))
        bad['new_metrics'] = copy.deepcopy(base['metrics'])
        reject(name + '_forged_invalid_score', 'RECORD_SCORE', lambda b=bad: record_check(structure, io, base, b), bad)

        empty = enumerate_to(structure, io, base, out / (name + '_empty'), deadline, identity, limit=0, progress=False)
        empty_cp = io.strict_json((ROOT / empty['checkpoints'][-1]['path']).read_bytes())
        cp_cases = []
        for suffix, value in [('boolean', False), ('float', 0.0)]:
            bad = copy.deepcopy(empty_cp)
            bad['next_proposal_id'] = value
            cp_cases.append(('empty_' + suffix + '_next', 'CHECKPOINT_TYPES', bad))
        for suffix, value in [('boolean', True), ('float', float(base['n']))]:
            bad = copy.deepcopy(checkpoint)
            bad['identity']['n'] = value
            cp_cases.append((suffix + '_identity_n', 'CHECKPOINT_IDENTITY', bad))
        for suffix, value in [('boolean', False), ('float', 0.0)]:
            bad = copy.deepcopy(empty_cp)
            bad['aggregate']['counts']['invalid_selection'] = value
            cp_cases.append(('empty_' + suffix + '_count', 'CHECKPOINT_AGGREGATE', bad))
        bad = copy.deepcopy(empty_cp)
        bad['extra'] = True
        cp_cases.append(('extra_header', 'CHECKPOINT_TYPES', bad))
        bad = copy.deepcopy(empty_cp)
        bad['schema'] = 'OLD_ROOT_CHECKPOINT'
        cp_cases.append(('wrong_schema', 'CHECKPOINT_IDENTITY', bad))
        bad = copy.deepcopy(checkpoint)
        bad['next_proposal_id'] += 1
        cp_cases.append(('wrong_next', 'CHECKPOINT_AGGREGATE', bad))
        bad = copy.deepcopy(checkpoint)
        bad['aggregate']['minimum_F3'] = float(bad['aggregate']['minimum_F3'])
        cp_cases.append(('float_best_F3', 'CHECKPOINT_AGGREGATE', bad))
        for label, stage, bad in cp_cases:
            reject(name + '_checkpoint_' + label, stage,
                lambda b=bad, tag=label: enumerate_to(structure, io, base, out / (name + '_negative_cp_' + tag),
                    deadline, identity, resume=b, progress=False), bad)
        for suffix, value in [('boolean', False), ('float', 0.0)]:
            reject(name + '_limit_' + suffix, 'CHECKPOINT_TYPES',
                lambda v=value, tag=suffix: enumerate_to(structure, io, base, out / (name + '_negative_limit_' + tag),
                    deadline, identity, limit=v, progress=False), dict(limit=value))

        part = checkpoint['parts'][0]
        for label, key, value, stage in [
                ('boolean_start', 'start', False, 'PART_TYPES'),
                ('float_start', 'start', 0.0, 'PART_TYPES'),
                ('wrong_record_count', 'record_count', part['record_count'] + 1, 'PART_TYPES'),
                ('gzip_hash', 'gzip_sha256', '0' * 64, 'PART_HASH'),
                ('raw_hash', 'raw_sha256', '0' * 64, 'PART_HASH'),
                ('gzip_bytes', 'gzip_bytes', part['gzip_bytes'] + 1, 'PART_HASH'),
                ('raw_bytes', 'raw_bytes', part['raw_bytes'] + 1, 'PART_HASH'),
                ('outside_path', 'path', '../ternary-outside-workspace.gz', 'PART_PATH')]:
            bad = copy.deepcopy(part)
            bad[key] = value
            reject(name + '_part_' + label, stage, lambda b=bad: io.read_part(b), bad)
        bad = copy.deepcopy(part)
        bad['start'] += 1
        bad['end'] += 1
        reject(name + '_part_shifted_IDs', 'PART_SEQUENCE', lambda b=bad: io.read_part(b), bad)
        original_raw_records = io.read_part(part)
        for suffix, value in [('boolean', False), ('float', 0.0)]:
            bad_records = copy.deepcopy(original_raw_records)
            bad_records[0]['proposal_id'] = value
            bad = corrupted_part(io, out, name + '_part_' + suffix + '_ID', part, bad_records)
            reject(name + '_part_' + suffix + '_ID', 'PART_SEQUENCE', lambda b=bad: io.read_part(b), bad)
        bad_records = copy.deepcopy(original_raw_records)
        chosen_at = next(at for at, r in enumerate(bad_records) if r['valid'])
        bad_records[chosen_at]['delta_F3'] += 1
        bad = corrupted_part(io, out, name + '_part_forged_score', part, bad_records)
        forged_cp = copy.deepcopy(checkpoint)
        forged_cp['parts'][0] = bad
        reject(name + '_part_forged_score', 'RECORD_SCORE',
            lambda b=forged_cp: enumerate_to(structure, io, base, out / (name + '_negative_forged_record'),
                deadline, identity, resume=b, progress=False), forged_cp)
    need(record_count == 522 and calls == 1044 and all(branch[k] > 0 for k in ['valid_overlap', 'valid_disjoint', 'moves_row0', 'candidate_positive_lambda']),
         'CONTROL', 'complete fixture count and unrestricted move/domain branches')
    # Signed-residue controls are arithmetic fixtures, not graph existence claims.
    for residual in [-2, -1, 0, 1, 2, 3, 6, 12]:
        common = residual + 2
        observed = cost(common, 0)
        need(observed[0] == int(residual % 3 != 0) and observed[2] == residual * residual and observed[3] == residual % 3,
             'CONTROL', 'normalized signed residue/cost arithmetic')
    for label, common, adjacent in [('boolean_common_zero', False, 0), ('boolean_common_one', True, 0),
            ('float_common_zero', 0.0, 0), ('float_common_one', 1.0, 0), ('negative_common', -1, 0),
            ('boolean_adj_zero', 0, False), ('boolean_adj_one', 0, True), ('float_adj_zero', 0, 0.0),
            ('float_adj_one', 0, 1.0), ('nonbinary_adj', 0, 2)]:
        reject('pair_cost_' + label, 'PAIR_COST', lambda c=common, a=adjacent: cost(c, a), dict(common=common, adjacent=adjacent))
    rook = fixtures()['rook9']
    for label, n, degree, rows, stage in [
            ('boolean_n', True, 2, rook['triples'], 'DOMAIN'),
            ('boolean_degree', 9, True, rook['triples'], 'DOMAIN'),
            ('wrong_degree', 9, 3, rook['triples'], 'DEGREE')]:
        reject('domain_' + label, stage, lambda a=n, d=degree, t=rows: domain(structure, a, d, t),
            dict(n=n, point_degree=degree, triples=rows))
    for label, stage, mutation in [
            ('boolean_vertex', 'DOMAIN', lambda t: t[0].__setitem__(0, False)),
            ('duplicate_vertex', 'DOMAIN', lambda t: t[0].__setitem__(1, t[0][0])),
            ('duplicate_triple', 'DOMAIN', lambda t: t.__setitem__(1, t[0][:])),
            ('repeated_pair', 'LINEARITY', lambda t: t.__setitem__(1, [0, 1, 3]))]:
        rows = copy.deepcopy(rook['triples'])
        mutation(rows)
        reject('domain_' + label, stage, lambda t=rows: domain(structure, 9, 2, t), dict(n=9, point_degree=2, triples=rows))
    for label, raw in [('duplicate_key', b'{"a":0,"a":1}'), ('nonfinite', b'{"a":NaN}'), ('invalid_utf8', b'\xff')]:
        reject('json_' + label, 'JSON', lambda b=raw: io.strict_json(b), dict(raw_hex=raw.hex()))
    rook_base = domain(structure, **rook)
    invalid = next(proposal(structure, rook_base, pid) for pid in range(rook_base['total'])
                   if not proposal(structure, rook_base, pid)['valid'])
    reject('invalid_record_has_no_candidate', 'RECORD_VALIDITY', lambda: candidate(structure, rook_base, invalid), invalid)
    masks = [float(x) for x in rook_base['masks']]
    reject('score_float_masks', 'SCORE_DOMAIN', lambda: score(masks, 2), dict(masks=masks, point_degree=2))
    need(len(negatives) == 160, 'CONTROL', 'exact predeclared three-fixture plus global negative population')
    io.save(out / 'summary.json', dict(status='AUTHOR_TERNARY_TWO_LINE_V1_CONTROLS_PENDING_INDEPENDENT_GATE',
        producer='/root/native_driver', timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv],
        cwd=str(ROOT), source_reference_commit=source_commit, python=platform.python_version(), tqdm=importlib.metadata.version('tqdm'),
        software=software, unique_fixture_labels=record_count, streamed_proposal_evaluation_calls=calls, valid_fixture_labels=valid_count,
        fixture_manifests=results, whole_prefix_resume_equalities=3, branch_counts=dict(branch),
        strict_negatives=negatives, strict_negative_count=len(negatives), signed_residue_arithmetic_cases=8,
        actual99graph_read=False, scientific_census_launched=False, stochastic_engine_launched=False,
        independent_approval=False, target_resolution='NONE', deadline=deadline.status()))


def corrupted_part(io, out, label, part, records):
    raw = b''.join(io.canonical(r) for r in records)
    target = out / (label + '.jsonl.gz')
    with target.open('xb') as stream:
        with gzip.GzipFile(filename='', fileobj=stream, mode='wb', compresslevel=1, mtime=0) as writer:
            writer.write(raw)
    bad = copy.deepcopy(part)
    bad.update(path=target.relative_to(ROOT).as_posix(), raw_bytes=len(raw), raw_sha256=sha_bytes(raw),
        gzip_bytes=target.stat().st_size, gzip_sha256=sha(target))
    return bad


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['controls'])
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='New ternary two-line finite controls only; complete input/source hashes/setup/children and saving share this invocation; no science or automatic retry')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'PATH', 'fresh bounded output')
    structure, io, reference, pins = lib()
    for path, identity in io.SOFTWARE.items():
        need(sha(ROOT / path) == identity, 'SOURCE', 'exact runtime/shared helper closure:' + path)
        pins[path] = identity
    pins[SELF], pins[SPEC] = sha(ROOT / SELF), sha(ROOT / SPEC)
    try:
        engineering(structure, io, reference, out, deadline, pins, args.source_commit)
    except BaseException as error:
        out.mkdir(parents=True, exist_ok=True)
        io.save(out / 'failure.json', dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(),
            preserved_partial_artifacts=True, target_resolution='NONE', independent_approval=False))
        raise


if __name__ == '__main__':
    main()
