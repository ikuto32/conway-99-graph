"""Finite engineering kernel for a fixed-graph restricted three-line census.

V3 exposes engineering controls only. A target census caller/input gate and its
concrete scientific command are deliberately not supplied by this source.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.metadata
import importlib.util
import itertools
import json
import platform
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from command_deadline import CommandDeadline
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
KERNEL = 'acceleration/census_20261003_root_focused_two_line_v1.py'
KERNEL_SHA = 'bbc91ed768a07b302e0e417e8c4415925ef6fac01bd14d78051a56b723419017'
KERNEL_SPEC = 'acceleration/census_20261003_root_focused_two_line_v1_spec.md'
KERNEL_SPEC_SHA = '9b2fcfc0b330b9183a47c0f3888126ef8dfe8a8dbb4d41366c9adf11006cdcc8'
SELF = 'acceleration/census_20261003_root_focused_restricted_three_line_v3.py'
SPEC = 'acceleration/census_20261003_root_focused_restricted_three_line_v3_spec.md'
SOFTWARE = {
    KERNEL: KERNEL_SHA, KERNEL_SPEC: KERNEL_SPEC_SHA,
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'acceleration/native_budget_env_v1/pyproject.toml': '96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782',
    'acceleration/native_budget_env_v1/uv.lock': '54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434',
}
ROLE_SCHEMA = 'FROZEN_ROOT_CN1_CN3_ORIENTED_ROLE_UNIVERSE_V1'
RECORD_SCHEMA = 'FROZEN_ROOT_RESTRICTED_THREE_LINE_ROLE_RECORD_V1'
CHECKPOINT_SCHEMA = 'FROZEN_ROOT_RESTRICTED_THREE_LINE_CHECKPOINT_V1'
MANIFEST_SCHEMA = 'FROZEN_ROOT_RESTRICTED_THREE_LINE_MANIFEST_V1'
CHUNK = 5000
MAX_LINE = 8192


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


def save(path, obj):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n').encode('ascii')


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'JSON', 'duplicate literal object key')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(CheckError('JSON', 'finite JSON values')))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CheckError('JSON', 'literal JSON decoding') from error


def lib():
    need(sha(ROOT / KERNEL) == KERNEL_SHA and sha(ROOT / KERNEL_SPEC) == KERNEL_SPEC_SHA,
         'SOURCE', 'unchanged producer domain/scorer dependency')
    spec = importlib.util.spec_from_file_location('restricted_three_line_old_domain', ROOT / KERNEL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def restricted_domain(engine, n, degree, triples, root):
    base = engine.domain(n, degree, triples, root)
    need(base['lambda_energy'] == 0, 'LAMBDA_DOMAIN', 'every adjacent pair has exactly one common neighbor')
    neighbors = [x for x in range(n) if (base['masks'][root] >> x) & 1]
    neighbor_set = set(neighbors)
    outsiders = [x for x in range(n) if x != root and x not in neighbor_set]
    under = [x for x in outsiders if base['cn'][root][x] == 1]
    over = [x for x in outsiders if base['cn'][root][x] == 3]
    classes = {i: sum(x in neighbor_set for x in triples[i]) for i in base['mutable_labels']}
    need(all(c in (0, 1) for c in classes.values()), 'ROOT_CLASSES', 'lambda1 mutable lines contain at most one root neighbor')
    zero = [i for i in base['mutable_labels'] if classes[i] == 0]
    one = [i for i in base['mutable_labels'] if classes[i] == 1]
    u_roles = sorted((u, i, ix) for u in under for i in zero for ix, x in enumerate(triples[i]) if x == u)
    v_roles = sorted((v, j, jy) for v in over for j in one for jy, x in enumerate(triples[j]) if x == v)
    need(len(one) == 2 * degree * (degree - 1), 'ROOT_CLASSES', 'exact one-neighbor mutable incidence count')
    need(all(sum(t[0] == u for t in u_roles) == degree - 1 for u in under)
         and all(sum(t[0] == v for t in v_roles) == 3 for v in over),
         'ROLE_COUNTS', 'each under/over support has the declared literal incidence choices')
    k_choices = {i: [k for k in zero if k != i] for i in zero}
    per_uv = max(len(zero) - 1, 0) * 3
    total = len(u_roles) * len(v_roles) * per_uv
    universe = dict(schema=ROLE_SCHEMA, root=root, root_neighbors=neighbors,
                    root_outsiders=outsiders, under_vertices=under, over_vertices=over,
                    zero_neighbor_lines=zero, one_neighbor_lines=one,
                    under_incidence_roles=[list(t) for t in u_roles],
                    over_incidence_roles=[list(t) for t in v_roles],
                    proposal_count=total,
                    order='u roles lex(u,i,ix), then v roles lex(v,j,jy), then k zero-neighbor original label excluding i, then kz 0,1,2',
                    orientation='i:u->w; j:v->u; k:w->v',
                    validity_filter_applied=False,
                    role_count_unit='Role-labelled selections before all validity filters; no adjacency/isomorphism collapse',
                    expected_root_residual_delta_if_valid=-2)
    return dict(base=base, universe=universe, u_roles=u_roles, v_roles=v_roles,
                k_choices=k_choices, per_uv=per_uv, total=total)


def decode_role(domain, pid):
    need(type(pid) is int and 0 <= pid < domain['total'], 'PROPOSAL_DOMAIN', 'bounded role-labelled ID')
    uv, within = divmod(pid, domain['per_uv'])
    ua, va = divmod(uv, len(domain['v_roles']))
    ka, kz = divmod(within, 3)
    u, i, ix = domain['u_roles'][ua]
    v, j, jy = domain['v_roles'][va]
    k = domain['k_choices'][i][ka]
    w = domain['base']['triples'][k][kz]
    return dict(u=u, i=i, ix=ix, v=v, j=j, jy=jy, w=w, k=k, kz=kz)


def role_id(domain, i, j, k, ix, jy, kz):
    need(all(type(x) is int for x in (i, j, k, ix, jy, kz)) and all(0 <= x < 3 for x in (ix, jy, kz)),
         'PROPOSAL_DOMAIN', 'typed literal selected positions')
    base = domain['base']
    need(i in base['mutable_labels'] and j in base['mutable_labels'] and k in base['mutable_labels'],
         'FROZEN_UNIVERSE', 'all three selected lines are mutable')
    need(len({i, j, k}) == 3, 'ROLE_UNIVERSE', 'three distinct role-labelled source lines')
    first = (base['triples'][i][ix], i, ix)
    second = (base['triples'][j][jy], j, jy)
    need(first in domain['u_roles'] and second in domain['v_roles'] and k in domain['k_choices'].get(i, []),
         'ROLE_UNIVERSE', 'literal under/over/zero-neighbor role selection')
    return ((domain['u_roles'].index(first) * len(domain['v_roles']) + domain['v_roles'].index(second))
            * domain['per_uv'] + domain['k_choices'][i].index(k) * 3 + kz)


def cycle(engine, base, i, j, k, ix, jy, kz, pid=None):
    need(all(type(x) is int for x in (i, j, k, ix, jy, kz)) and all(0 <= x < 3 for x in (ix, jy, kz)),
         'PROPOSAL_DOMAIN', 'typed source labels/selected positions')
    need(all(x in base['mutable_labels'] for x in (i, j, k)) and len({i, j, k}) == 3,
         'FROZEN_UNIVERSE', 'three distinct mutable literal source lines')
    old = [list(base['triples'][label]) for label in (i, j, k)]
    u, v, w = old[0][ix], old[1][jy], old[2][kz]
    record = dict(schema=RECORD_SCHEMA, proposal_id=pid,
                  role=dict(u=u, i=i, ix=ix, v=v, j=j, jy=jy, w=w, k=k, kz=kz),
                  old_triples=old, new_triples=None, valid=False, invalid_reason=None,
                  conflict_pair=None, toggles=None, changed_root_counts=None,
                  delta_lambda=None, delta_mu=None, new_lambda=None, new_mu=None,
                  new_root_residual=None, root_residual_delta=None,
                  frozen_root_unchanged=None, classification=None, mu_direction=None)
    if len({u, v, w}) != 3:
        record.update(invalid_reason='selected_points_not_distinct', classification='invalid_selection')
        return record
    new = [list(t) for t in old]
    new[0][ix], new[1][jy], new[2][kz] = w, u, v
    record['new_triples'] = new
    if any(len(set(t)) != 3 for t in new):
        record.update(invalid_reason='receiving_triple_duplicate_point', classification='invalid_selection')
        return record
    old_pairs = [tuple(sorted((triple[position], x)))
                 for triple, position in zip(old, (ix, jy, kz))
                 for at, x in enumerate(triple) if at != position]
    new_pairs = [tuple(sorted((triple[position], x)))
                 for triple, position in zip(new, (ix, jy, kz))
                 for at, x in enumerate(triple) if at != position]
    need(len(set(old_pairs)) == 6, 'PAIR_DOMAIN', 'six distinct pairs removed from original linear hypergraph')
    masks = list(base['masks'])
    for a, b in old_pairs:
        masks[a] &= ~(1 << b)
        masks[b] &= ~(1 << a)
    for a, b in new_pairs:
        if (masks[a] >> b) & 1:
            record.update(invalid_reason='new_pair_already_present', conflict_pair=[a, b], classification='invalid_linearity')
            return record
        masks[a] |= 1 << b
        masks[b] |= 1 << a
    toggles = sorted(set(old_pairs) ^ set(new_pairs))
    touched = sorted({x for edge in toggles for x in edge})
    touched_set = set(touched)
    dl = dm = 0
    for a in touched:
        for b in range(base['n']):
            if a == b or (b in touched_set and b < a):
                continue
            common0, common1 = base['cn'][a][b], (masks[a] & masks[b]).bit_count()
            if (base['masks'][a] >> b) & 1:
                dl -= (common0 - 1) ** 2
            else:
                dm -= (common0 - 2) ** 2
            if (masks[a] >> b) & 1:
                dl += (common1 - 1) ** 2
            else:
                dm += (common1 - 2) ** 2
    root = base['root']
    root_counts = [(masks[root] & masks[x]).bit_count() for x in range(base['n'])]
    new_r = sum((root_counts[x] - 2) ** 2 for x in range(base['n'])
                if x != root and not ((masks[root] >> x) & 1))
    changed = [[x, base['cn'][root][x], root_counts[x]] for x in range(base['n'])
               if x != root and base['cn'][root][x] != root_counts[x]]
    need(masks[root] == base['masks'][root] and all(m.bit_count() == 2 * base['degree'] for m in masks),
         'FROZEN_INVARIANT', 'complete graph regularity/root edges preserved')
    dr = new_r - base['root_residual']
    classification = ('valid_lambda_changed' if dl else 'valid_lambda_preserving_root_' +
                      ('down' if dr < 0 else 'up' if dr > 0 else 'equal'))
    record.update(valid=True, toggles=[list(t) for t in toggles], changed_root_counts=changed,
                  delta_lambda=dl, delta_mu=dm, new_lambda=base['lambda_energy'] + dl,
                  new_mu=base['mu_energy'] + dm, new_root_residual=new_r,
                  root_residual_delta=dr, frozen_root_unchanged=True, classification=classification,
                  mu_direction='down' if dm < 0 else 'up' if dm > 0 else 'equal')
    return record


def proposal(engine, domain, pid):
    role = decode_role(domain, pid)
    record = cycle(engine, domain['base'], **{key: role[key] for key in ('i', 'j', 'k', 'ix', 'jy', 'kz')}, pid=pid)
    need(record['role'] == role, 'ROLE_UNIVERSE', 'exact decoder/cycle role agreement')
    if record['valid']:
        expected = sorted([[role['u'], 1, 2], [role['v'], 3, 2]])
        need(record['changed_root_counts'] == expected and record['root_residual_delta'] == -2,
             'ROOT_CUT_INVARIANT', 'valid restricted cycle repairs exactly two unit residuals')
    return record


def record_matrix(engine, base, record):
    need(record.get('valid') is True and type(record.get('toggles')) is list,
         'RECORD_VALIDITY', 'only valid proposals have a candidate graph')
    return engine.masks_from_record(base, record)


def full_control(engine, base, record):
    if not record['valid']:
        return
    changed = [list(t) for t in base['triples']]
    for label, triple in zip((record['role']['i'], record['role']['j'], record['role']['k']), record['new_triples']):
        changed[label] = list(triple)
    fresh = engine.domain(base['n'], base['degree'], changed, base['root'])
    need(fresh['frozen_rows'] == base['frozen_rows'] and fresh['masks'] == record_matrix(engine, base, record),
         'FULL_CONTROL', 'whole literal triples/domain/adjacency independently rebuilt within author controls')
    need((fresh['lambda_energy'], fresh['mu_energy'], fresh['root_residual']) ==
         (record['new_lambda'], record['new_mu'], record['new_root_residual']),
         'FULL_CONTROL', 'full exact pair scoring agrees with changed-row update')


def cache_check(engine, domain):
    base = domain['base']
    fresh = restricted_domain(engine, base['n'], base['degree'], base['triples'], base['root'])
    need(type(base['masks']) is list and len(base['masks']) == base['n']
         and all(type(x) is int and 0 <= x < (1 << base['n']) for x in base['masks'])
         and canonical(base['masks']) == canonical(fresh['base']['masks']), 'ADJ_CACHE', 'complete integer adjacency cache')
    need(type(base['cn']) is list and len(base['cn']) == base['n']
         and all(type(row) is list and len(row) == base['n']
                 and all(type(x) is int and 0 <= x <= 2 * base['degree'] for x in row) for row in base['cn'])
         and canonical(base['cn']) == canonical(fresh['base']['cn']), 'CN_CACHE', 'complete integer common-neighbor cache')
    need(all(type(base[key]) is int and base[key] == fresh['base'][key]
             for key in ('lambda_energy', 'mu_energy', 'root_residual')), 'ENERGY_CACHE', 'all exact baseline components')
    need(canonical(domain['universe']) == canonical(fresh['universe'])
         and all(type(domain[key]) is int and domain[key] == fresh[key] for key in ('total', 'per_uv'))
         and all(canonical(domain[key]) == canonical(fresh[key]) for key in ('u_roles', 'v_roles', 'k_choices')),
         'ROLE_CACHE', 'entire frozen literal role universe and decoder cache')


def record_check(engine, domain, record):
    need(type(record) is dict and type(record.get('proposal_id')) is int,
         'RECORD_ROLE', 'literal object and integer proposal ID')
    expected = proposal(engine, domain, record['proposal_id'])
    need(set(record) == set(expected) and canonical(record['role']) == canonical(expected['role'])
         and record['schema'] == RECORD_SCHEMA, 'RECORD_ROLE', 'exact fixed role/schema fields')
    for stage, keys in [
            ('RECORD_STATUS', ('valid', 'classification', 'invalid_reason', 'mu_direction')),
            ('RECORD_TOPOLOGY', ('old_triples', 'new_triples', 'toggles', 'conflict_pair')),
            ('RECORD_SCORE', ('delta_lambda', 'delta_mu', 'new_lambda', 'new_mu')),
            ('RECORD_ROOT_CUT', ('changed_root_counts', 'new_root_residual', 'root_residual_delta', 'frozen_root_unchanged'))]:
        need(all(canonical(record[k]) == canonical(expected[k]) for k in keys), stage, 'exact literal proposal values')
    full_control(engine, domain['base'], record)


def accumulator():
    return dict(counts=Counter(), mu_counts=Counter(), unique=set(), accepted_unique=set(),
                minimum_root=None, root_best=[], best_pair=None, best=[], zero_ids=[])


def accumulate(a, record):
    a['counts'][record['classification']] += 1
    if not record['valid']:
        return
    key = tuple(tuple(edge) for edge in record['toggles'])
    a['unique'].add(key)
    if record['new_lambda'] == 0:
        a['accepted_unique'].add(key)
        a['mu_counts'][record['mu_direction']] += 1
        if a['minimum_root'] is None or record['new_root_residual'] < a['minimum_root']:
            a['minimum_root'], a['root_best'] = record['new_root_residual'], [record]
        elif record['new_root_residual'] == a['minimum_root']:
            a['root_best'].append(record)
        pair = (record['new_root_residual'], record['new_mu'])
        if a['best_pair'] is None or pair < a['best_pair']:
            a['best_pair'], a['best'] = pair, [record]
        elif pair == a['best_pair']:
            a['best'].append(record)
    if record['new_lambda'] == record['new_mu'] == 0:
        a['zero_ids'].append(record['proposal_id'])


def snapshot(a):
    return dict(counts=dict(sorted(a['counts'].items())), lambda_preserving_mu_directions=dict(sorted(a['mu_counts'].items())),
                unique_valid_neighbor_graphs=len(a['unique']), unique_lambda_preserving_graphs=len(a['accepted_unique']),
                minimum_root_residual=a['minimum_root'], minimum_root_proposal_ids=[r['proposal_id'] for r in a['root_best']],
                minimum_eligible_pair=None if a['best_pair'] is None else list(a['best_pair']),
                minimum_pair_proposal_ids=[r['proposal_id'] for r in a['best']], zero_score_proposal_ids=a['zero_ids'])


def part_types(part):
    need(type(part) is dict and set(part) == {'path','start','end','record_count','raw_bytes','raw_sha256','gzip_bytes','gzip_sha256'}
         and type(part.get('path')) is str and bool(part['path'])
         and all(type(part.get(k)) is int and part[k] >= 0 for k in ('start','end','record_count','raw_bytes','gzip_bytes'))
         and part['end'] - part['start'] == part['record_count'] and part['record_count'] <= CHUNK
         and part['raw_bytes'] <= part['record_count'] * MAX_LINE
         and all(type(part.get(k)) is str and re.fullmatch(r'[0-9a-f]{64}', part[k]) is not None for k in ('raw_sha256','gzip_sha256')),
         'PART_TYPES', 'exact typed part metadata and bounded declared population')


def read_part(part):
    part_types(part)
    path = (ROOT / part['path']).resolve()
    need(path.is_relative_to(ROOT) and path.is_file(), 'PART_PATH', 'existing bounded workspace member')
    need(path.stat().st_size == part['gzip_bytes'] and sha(path) == part['gzip_sha256'], 'PART_HASH', 'compressed exact member')
    digest, byte_count, records = hashlib.sha256(), 0, []
    with gzip.open(path, 'rb') as stream:
        while True:
            raw = stream.readline(MAX_LINE + 1)
            if not raw:
                break
            need(len(raw) <= MAX_LINE and raw.endswith(b'\n'), 'PART_LENGTH', 'bounded full record line')
            byte_count += len(raw)
            need(byte_count <= part['record_count'] * MAX_LINE, 'PART_LENGTH', 'bounded decompressed population')
            digest.update(raw)
            records.append(strict_json(raw))
    need(byte_count == part['raw_bytes'] and digest.hexdigest() == part['raw_sha256']
         and len(records) == part['record_count'], 'PART_HASH', 'whole literal raw part identity')
    need(all(type(r) is dict and type(r.get('proposal_id')) is int for r in records)
         and canonical([r['proposal_id'] for r in records]) == canonical(list(range(part['start'], part['end']))),
         'PART_SEQUENCE', 'complete strictly integer ordered role IDs')
    return records


def enumerate_to(engine, domain, out, deadline, identity, limit=None, resume=None, chunk=CHUNK, progress=True):
    need(type(chunk) is int and 0 < chunk <= CHUNK, 'CHUNK', 'bounded output chunk')
    out.mkdir(parents=True, exist_ok=False)
    start, parts, checkpoints, a = 0, [], [], accumulator()
    if resume is not None:
        need(type(resume) is dict and set(resume) == {'schema','identity','next_proposal_id','parts','aggregate'}
             and type(resume.get('next_proposal_id')) is int and 0 <= resume['next_proposal_id'] <= domain['total']
             and type(resume.get('parts')) is list and type(resume.get('aggregate')) is dict,
             'CHECKPOINT_TYPES', 'exact strictly integer checkpoint header')
        need(resume.get('schema') == CHECKPOINT_SCHEMA and canonical(resume.get('identity')) == canonical(identity),
             'CHECKPOINT_IDENTITY', 'same exact graph/software/universe identity')
        for part in resume['parts']:
            part_types(part)
            need(part['start'] == start and part['end'] == part['start'] + part['record_count'],
                 'PART_SEQUENCE', 'contiguous prefix part coverage')
            for record in read_part(part):
                accumulate(a, record)
            parts.append(part)
            start = part['end']
        need(start == resume['next_proposal_id'] and canonical(snapshot(a)) == canonical(resume['aggregate']),
             'CHECKPOINT_AGGREGATE', 'exact raw prefix aggregate reproduction')
    stop = domain['total'] if limit is None else min(limit, domain['total'])
    need(type(stop) is int and 0 <= start <= stop <= domain['total'], 'CHECKPOINT_IDENTITY', 'bounded literal prefix')
    counter, budget_stop = start, False
    bar = tqdm(total=stop - start, desc='Restricted root three-line roles', unit='role', mininterval=1, disable=not progress)
    while counter < stop:
        if deadline is not None and (deadline.status()['stop_required'] or deadline.status()['remaining_seconds'] <= 20):
            budget_stop = True
            break
        begin = counter
        target = out / f'part_{begin:09d}.jsonl.gz'
        digest, raw_bytes = hashlib.sha256(), 0
        with target.open('xb') as raw_writer:
            with gzip.GzipFile(filename='', fileobj=raw_writer, mode='wb', compresslevel=1, mtime=0) as writer:
                while counter < min(stop, begin + chunk):
                    if (counter - begin) % 100 == 0 and deadline is not None and (
                            deadline.status()['stop_required'] or deadline.status()['remaining_seconds'] <= 20):
                        budget_stop = True
                        break
                    record = proposal(engine, domain, counter)
                    raw = canonical(record)
                    need(len(raw) <= MAX_LINE, 'RECORD_LENGTH', 'bounded canonical proposal record')
                    writer.write(raw)
                    digest.update(raw)
                    raw_bytes += len(raw)
                    accumulate(a, record)
                    counter += 1
                    bar.update(1)
        parts.append(dict(path=target.relative_to(ROOT).as_posix(), start=begin, end=counter,
                          record_count=counter - begin, raw_bytes=raw_bytes, raw_sha256=digest.hexdigest(),
                          gzip_bytes=target.stat().st_size, gzip_sha256=sha(target)))
        cp = out / f'checkpoint_{counter:09d}.json'
        save(cp, dict(schema=CHECKPOINT_SCHEMA, identity=identity, next_proposal_id=counter,
                      parts=parts, aggregate=snapshot(a)))
        checkpoints.append(dict(path=cp.relative_to(ROOT).as_posix(), sha256=sha(cp)))
        if budget_stop:
            break
    bar.close()
    if not checkpoints:
        cp = out / f'checkpoint_{counter:09d}.json'
        save(cp, dict(schema=CHECKPOINT_SCHEMA, identity=identity, next_proposal_id=counter, parts=parts, aggregate=snapshot(a)))
        checkpoints.append(dict(path=cp.relative_to(ROOT).as_posix(), sha256=sha(cp)))
    save(out / 'minimum_pair_ties.json', dict(records=a['best'],
         scope='All lambda-preserving proposals tied at minimum (R_root,E_mu) among this saved role prefix.'))
    save(out / 'minimum_root_ties.json', dict(records=a['root_best'],
         scope='All lambda-preserving proposals tied at minimum R_root among this saved role prefix; mu worsening remains eligible.'))
    selected = min(a['best'], key=lambda r: r['proposal_id']) if a['best'] else None
    if selected is not None:
        base = domain['base']
        (out / 'selected_neighbor.adj').write_bytes(engine.adjacency_bytes(record_matrix(engine, base, selected)))
        triples = [list(t) for t in base['triples']]
        for label, row in zip((selected['role']['i'], selected['role']['j'], selected['role']['k']), selected['new_triples']):
            triples[label] = list(row)
        save(out / 'selected_neighbor_triples.json', dict(n=base['n'], degree=base['degree'], root=base['root'],
             frozen_rows=base['frozen_rows'], mutable_labels=base['mutable_labels'], triples=triples,
             proposal_id=selected['proposal_id'], historical_native_state_written=False))
    manifest = dict(schema=MANIFEST_SCHEMA, identity=identity, universe=domain['universe'],
                    population=domain['total'], completed_proposals=counter, starting_proposal_id=start,
                    proposals_evaluated_this_invocation=counter - start, parts=parts, checkpoints=checkpoints,
                    status='CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK' if counter == domain['total'] else 'UNKNOWN_PREFIX_ONLY',
                    budget_stop=budget_stop, aggregate=snapshot(a), selected_proposal_id=None if selected is None else selected['proposal_id'],
                    baseline=dict(E_lambda=domain['base']['lambda_energy'], E_mu=domain['base']['mu_energy'], R_root=domain['base']['root_residual']),
                    selection_rule='Among valid lambda0 proposals minimize root R, then global E_mu, then role proposal ID; mu worsening remains eligible.',
                    producer='/root/native_driver', independent_approval=False, target_resolution='NONE', historical_native_state_written=False,
                    limitations=['ONE exact role-labelled CN1/CN3 oriented family on one frozen labelled graph only.',
                                 'Not all three-line moves, all root-descent moves, a connected move space, or any target exclusion.',
                                 'Incomplete raw prefix cannot establish absence; exact zero still requires independent full99 integer SRG validation.'])
    save(out / 'manifest.json', manifest)
    return manifest


def fixtures():
    rook = dict(n=9, degree=2, root=0, triples=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]])
    # Doily GQ(2,2): K6 edges are points; perfect matchings are lines.
    points = list(itertools.combinations(range(6), 2))
    def matchings(values):
        if not values:
            yield []
            return
        a = values[0]
        for b in values[1:]:
            for rest in matchings([x for x in values[1:] if x != b]):
                yield [(a, b)] + rest
    rows = [[points.index(edge) for edge in matching] for matching in matchings(list(range(6)))]
    doily = dict(n=15, degree=3, root=0, triples=rows)
    lifted = []
    for at, row in enumerate(rows):
        for sheet in (0, 1):
            lifted.append([2 * point + (sheet ^ int(at == 0 and point == 9)) for point in row])
    return dict(rook9=rook, doily15=doily, doily_two_lift30=dict(n=30, degree=3, root=0, triples=lifted))


def engineering(engine, out, deadline, software, source_commit):
    out.mkdir(parents=True, exist_ok=False)
    results, rejects, coverage, evaluation_calls = {}, [], [], 0
    all_fixtures = fixtures()
    def reject(label, stage, call, value=None):
        need(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'finite control save reserve')
        if value is not None:
            save(out / (label + '_input.json'), value)
        try:
            call()
        except CheckError as error:
            need(error.stage == stage, 'CONTROL', 'precise expected diagnostic ' + label)
            rejects.append(dict(case=label, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error)))
            return
        raise CheckError('CONTROL', 'accepted corrupted control ' + label)
    for name, fixture in all_fixtures.items():
        save(out / (name + '.json'), fixture)
        domain = restricted_domain(engine, **fixture)
        base = domain['base']
        save(out / (name + '_universe.json'), domain['universe'])
        if name == 'rook9':
            need((base['lambda_energy'], base['mu_energy'], base['root_residual']) == (0, 0, 0),
                 'CONTROL', 'known exact rook9 positive; explicitly not a99 certificate')
        elif name == 'doily15':
            need(len(domain['universe']['zero_neighbor_lines']) == 0 and domain['total'] == 0,
                 'CONTROL', 'empty role universe of a known lambda1 doily')
        else:
            need(domain['total'] > 0, 'CONTROL', 'declared lifted fixture has actual under/over incidence roles')
        identity = dict(fixture_path=(out / (name + '.json')).relative_to(ROOT).as_posix(),
                        fixture_sha256=sha(out / (name + '.json')), software=software,
                        universe=domain['universe'], n=fixture['n'], degree=fixture['degree'], root=fixture['root'])
        whole = enumerate_to(engine, domain, out / (name + '_whole'), deadline, identity, chunk=50, progress=False)
        results[name] = whole
        evaluation_calls += whole['proposals_evaluated_this_invocation']
        records = [r for part in whole['parts'] for r in read_part(part)]
        for record in records:
            role = record['role']
            need(role_id(domain, **{k: role[k] for k in ('i','j','k','ix','jy','kz')}) == record['proposal_id'],
                 'CONTROL', 'all exact role decoder/encoder identities')
            record_check(engine, domain, record)
            coverage.append(dict(fixture=name, proposal_id=record['proposal_id'], classification=record['classification']))
        need(canonical(base['triples']) == canonical(fixture['triples']), 'CONTROL', 'all accepted/rejected proposals leave source triples unchanged')
        cache_check(engine, domain)
        for key, stage in [('masks', 'ADJ_CACHE'), ('cn', 'CN_CACHE'), ('lambda_energy', 'ENERGY_CACHE'),
                           ('mu_energy', 'ENERGY_CACHE'), ('root_residual', 'ENERGY_CACHE')]:
            bad = copy.deepcopy(domain)
            if key == 'masks':
                bad['base'][key][0] ^= 1
            elif key == 'cn':
                bad['base'][key][0][1] += 1
            else:
                bad['base'][key] += 1
            reject(name + '_bad_' + key, stage, lambda b=bad: cache_check(engine, b))
        bad = copy.deepcopy(domain)
        bad['universe']['proposal_count'] += 1
        reject(name + '_bad_role_count', 'ROLE_CACHE', lambda: cache_check(engine, bad))
        neighbor = next(x for x in range(base['n']) if (base['masks'][base['root']] >> x) & 1)
        for suffix, at, value in [('boolean_zero', (0,0), False), ('float_zero', (0,0), 0.0),
                                  ('boolean_one', (base['root'],neighbor), True),
                                  ('float_one', (base['root'],neighbor), 1.0)]:
            bad = copy.deepcopy(domain)
            bad['base']['cn'][at[0]][at[1]] = value
            reject(name + '_CN_' + suffix, 'CN_CACHE', lambda b=bad: cache_check(engine, b))
        for suffix, value in [('boolean', False), ('float_equal', float(base['masks'][0]))]:
            bad = copy.deepcopy(domain)
            bad['base']['masks'][0] = value
            reject(name + '_mask_' + suffix, 'ADJ_CACHE', lambda b=bad: cache_check(engine, b))
        prefix = enumerate_to(engine, domain, out / (name + '_prefix17'), deadline, identity, limit=17, chunk=50, progress=False)
        evaluation_calls += prefix['proposals_evaluated_this_invocation']
        checkpoint = strict_json((ROOT / prefix['checkpoints'][-1]['path']).read_bytes())
        resumed = enumerate_to(engine, domain, out / (name + '_resumed'), deadline, identity, resume=checkpoint, chunk=50, progress=False)
        evaluation_calls += resumed['proposals_evaluated_this_invocation']
        resume_records = [r for part in resumed['parts'] for r in read_part(part)]
        need(records == resume_records and whole['aggregate'] == resumed['aggregate'], 'CONTROL', 'full exact whole/prefix/resume equality')
        corrupted = copy.deepcopy(checkpoint)
        corrupted['aggregate']['unique_valid_neighbor_graphs'] += 1
        reject(name + '_checkpoint_aggregate', 'CHECKPOINT_AGGREGATE',
               lambda: enumerate_to(engine, domain, out / (name + '_bad_resume'), deadline, identity, resume=corrupted), corrupted)
        for suffix, value in [('boolean', False), ('float_equal', float(checkpoint['next_proposal_id']))]:
            bad = copy.deepcopy(checkpoint)
            bad['next_proposal_id'] = value
            reject(name + '_checkpoint_ID_' + suffix, 'CHECKPOINT_TYPES',
                   lambda b=bad, s=suffix: enumerate_to(engine, domain, out / (name + '_bad_ID_' + s), deadline, identity, resume=b), bad)
        for suffix, value in [('boolean', False), ('float_equal', float(checkpoint['aggregate']['unique_valid_neighbor_graphs']))]:
            bad = copy.deepcopy(checkpoint)
            bad['aggregate']['unique_valid_neighbor_graphs'] = value
            reject(name + '_checkpoint_count_' + suffix, 'CHECKPOINT_AGGREGATE',
                   lambda b=bad, s=suffix: enumerate_to(engine, domain, out / (name + '_bad_count_' + s), deadline, identity, resume=b), bad)
        for suffix, value in [('boolean_zero', False), ('float_zero', 0.0)]:
            bad = copy.deepcopy(checkpoint)
            bad['identity']['root'] = value
            reject(name + '_checkpoint_identity_' + suffix, 'CHECKPOINT_IDENTITY',
                   lambda b=bad, s=suffix: enumerate_to(engine, domain, out / (name + '_bad_identity_' + s), deadline, identity, resume=b), bad)
        reject(name + '_pid_boolean', 'PROPOSAL_DOMAIN', lambda: decode_role(domain, True))
        reject(name + '_pid_oob', 'PROPOSAL_DOMAIN', lambda: decode_role(domain, domain['total']))
    rook = engine.domain(**all_fixtures['rook9'])
    # This three-cycle shares unselected4/7 across source lines and re-adds removed pairs.
    overlap = cycle(engine, rook, 1, 2, 4, 0, 0, 0)
    need(overlap['valid'] and overlap['new_triples'] == [[1,4,5],[3,7,8],[6,4,7]],
         'CONTROL', 'known valid overlap and removal/re-add cancellation')
    full_control(engine, rook, overlap)
    save(out / 'known_rook_overlap_cycle.json', overlap)
    selected_repeat = cycle(engine, rook, 1, 4, 2, 1, 1, 0)
    need(selected_repeat['invalid_reason'] == 'selected_points_not_distinct', 'CONTROL', 'known selected-point repeat')
    save(out / 'known_selected_repeat.json', selected_repeat)
    collision = cycle(engine, rook, 1, 2, 4, 0, 2, 1)
    need(collision['invalid_reason'] == 'receiving_triple_duplicate_point', 'CONTROL', 'known receiver collision')
    save(out / 'known_receiver_collision.json', collision)
    reject('frozen_line', 'FROZEN_UNIVERSE', lambda: cycle(engine, rook, 0, 1, 2, 0, 0, 0))
    reject('same_line', 'FROZEN_UNIVERSE', lambda: cycle(engine, rook, 1, 1, 2, 0, 0, 0))
    reject('selected_coord_boolean', 'PROPOSAL_DOMAIN', lambda: cycle(engine, rook, 1, 2, 4, True, 0, 0))
    reject('selected_coord_oob', 'PROPOSAL_DOMAIN', lambda: cycle(engine, rook, 1, 2, 4, 3, 0, 0))
    reject('duplicate_json_key', 'JSON', lambda: strict_json(b'{"a":1,"a":2}'))
    reject('nonfinite_json', 'JSON', lambda: strict_json(b'{"a":NaN}'))
    reject('bad_json', 'JSON', lambda: strict_json(b'{'))
    valid_counts = Counter(r['classification'] for result in results.values() for p in result['parts'] for r in read_part(p))
    need(sum(v for k, v in valid_counts.items() if k.startswith('valid_')) > 0,
         'CONTROL', 'restricted positive population must actually exercise valid root-cut repair')
    lifted_domain = restricted_domain(engine, **all_fixtures['doily_two_lift30'])
    valid_record = next(r for p in results['doily_two_lift30']['parts'] for r in read_part(p) if r['valid'])
    def bad_record(label, stage, mutate):
        bad = copy.deepcopy(valid_record)
        mutate(bad)
        reject(label, stage, lambda: record_check(engine, lifted_domain, bad), bad)
    bad_record('record_role_u', 'RECORD_ROLE', lambda r: r['role'].__setitem__('u', r['role']['u'] + 1))
    bad_record('record_boolean_pid', 'RECORD_ROLE', lambda r: r.__setitem__('proposal_id', True))
    bad_record('record_extra_field', 'RECORD_ROLE', lambda r: r.__setitem__('approved', True))
    bad_record('record_valid_flag', 'RECORD_STATUS', lambda r: r.__setitem__('valid', False))
    bad_record('record_classification', 'RECORD_STATUS', lambda r: r.__setitem__('classification', 'WRONG_CLASSIFICATION'))
    bad_record('record_old_triples', 'RECORD_TOPOLOGY', lambda r: r['old_triples'][0].reverse())
    bad_record('record_toggle_omission', 'RECORD_TOPOLOGY', lambda r: r['toggles'].pop())
    bad_record('record_wrong_lambda', 'RECORD_SCORE', lambda r: r.__setitem__('new_lambda', r['new_lambda'] + 1))
    bad_record('record_boolean_score', 'RECORD_SCORE', lambda r: r.__setitem__('new_mu', True))
    bad_record('record_wrong_delta_mu', 'RECORD_SCORE', lambda r: r.__setitem__('delta_mu', r['delta_mu'] + 1))
    bad_record('record_false_minus4', 'RECORD_ROOT_CUT', lambda r: r.__setitem__('root_residual_delta', -4))
    bad_record('record_root_count_omission', 'RECORD_ROOT_CUT', lambda r: r['changed_root_counts'].pop())
    bad_record('record_wrong_root_residual', 'RECORD_ROOT_CUT', lambda r: r.__setitem__('new_root_residual', r['new_root_residual'] + 1))
    bad_record('record_root_frozen_flag', 'RECORD_ROOT_CUT', lambda r: r.__setitem__('frozen_root_unchanged', False))
    original_part = results['doily_two_lift30']['parts'][0]
    for name, key, stage, change in [
            ('part_gzip_hash', 'gzip_sha256', 'PART_HASH', lambda _: '0' * 64),
            ('part_raw_hash', 'raw_sha256', 'PART_HASH', lambda _: '0' * 64),
            ('part_record_count', 'record_count', 'PART_TYPES', lambda x: x + 1)]:
        bad = copy.deepcopy(original_part)
        bad[key] = change(bad[key])
        reject(name, stage, lambda b=bad: read_part(b), bad)
    bad = copy.deepcopy(original_part)
    bad['start'] += 1
    bad['end'] += 1
    reject('part_id_shift', 'PART_SEQUENCE', lambda: read_part(bad), bad)
    for label, key, value in [('part_boolean_start', 'start', False), ('part_float_zero_start', 'start', 0.0),
                              ('part_boolean_count', 'record_count', True),
                              ('part_float_equal_count', 'record_count', float(original_part['record_count'])),
                              ('part_float_equal_rawbytes', 'raw_bytes', float(original_part['raw_bytes']))]:
        bad = copy.deepcopy(original_part)
        bad[key] = value
        reject(label, 'PART_TYPES', lambda b=bad: read_part(b), bad)
    original_records = read_part(original_part)
    for label, value in [('part_boolean_ID_zero', False), ('part_float_ID_zero', 0.0)]:
        records = copy.deepcopy(original_records)
        records[0]['proposal_id'] = value
        raw = b''.join(canonical(r) for r in records)
        target = out / (label + '.jsonl.gz')
        with target.open('xb') as stream:
            with gzip.GzipFile(filename='', fileobj=stream, mode='wb', compresslevel=1, mtime=0) as writer:
                writer.write(raw)
        bad = copy.deepcopy(original_part)
        bad.update(path=target.relative_to(ROOT).as_posix(), gzip_bytes=target.stat().st_size, gzip_sha256=sha(target),
                   raw_bytes=len(raw), raw_sha256=hashlib.sha256(raw).hexdigest())
        reject(label, 'PART_SEQUENCE', lambda b=bad: read_part(b), bad)
    save(out / 'coverage.json', coverage)
    save(out / 'summary.json', dict(status='AUTHOR_RESTRICTED_THREE_LINE_V3_CONTROLS_PENDING_INDEPENDENT_GATE',
         producer='/root/native_driver', verifier=None, verifier_null_reason='Author controls are not independent approval.',
         timestamp=datetime.now(timezone.utc).isoformat(), source_commit=source_commit,
         command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
         tqdm=importlib.metadata.version('tqdm'), software=software, deadline=deadline.status(),
         fixtures=all_fixtures, unique_role_records=len(coverage), recorded_role_evaluation_calls=evaluation_calls,
         extra_generic_cycle_calls=3, whole_split_equal=True, split_equalities=3,
         role_classification_counts=dict(sorted(valid_counts.items())), strict_negative_count=len(rejects),
         strict_negatives=rejects, generic_overlap_removal_readd_control=True,
         mathematical_scope='Generic finite literal controls only; doily and rook are not target99 inputs.',
         actual_target_input_read=False, scientific_census_launched=False,
         independent_approval=False, target_resolution='NONE'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=['controls'])
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--source-commit', required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='New restricted three-line finite engineering controls only; fresh independent checking required')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'PATH', 'workspace output only')
    software = {}
    for path, identity in SOFTWARE.items():
        need(sha(ROOT / path) == identity, 'SOURCE', 'unchanged exact dependency ' + path)
        software[path] = identity
    software[SELF], software[SPEC] = sha(ROOT / SELF), sha(ROOT / SPEC)
    engine = lib()
    engineering(engine, out, deadline, software, args.source_commit)


if __name__ == '__main__':
    main()
