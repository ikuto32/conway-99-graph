"""SOURCE ONLY: full raw geometry and integer matrix checking for F3 swaps.

This new objective/version needs fresh calibrated controls. No producer,
reference scorer, native topology or incremental updater is imported.
The preserved independent three-line core supplies geometry/strict IO only.
"""
from collections import Counter
from dataclasses import dataclass
import hashlib
from itertools import combinations
from pathlib import Path

import numpy as np

import audit_20261003_restricted_three_line_raw_core_v1 as io

SHARED = 'acceleration/audit_20261003_restricted_three_line_raw_core_v1.py'
SHARED_SHA = '98efe2641fe2952857efaa62b7812b0abe7a0f87ce4550bf64544a4ba3ebaa95'
OBJECTIVE = 'SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1'
SCHEMA = 'TERNARY_TWO_LINE_LABELLED_PROPOSAL_V1'
CHECKPOINT_SCHEMA = 'TERNARY_TWO_LINE_CENSUS_CHECKPOINT_V1'
FIELDS = set('schema objective_version proposal_id i j ix jy old_triples new_triples valid invalid_reason conflict_pair removed_pairs added_pairs toggles changed_rows delta_F3 delta_E_lambda delta_E_mu delta_E delta_scalar new_metrics tuple_direction classification'.split())


def authenticate(workspace):
    io.need(io.sha(Path(workspace) / SHARED) == SHARED_SHA, 'SHARED_SOURCE')


def score(adjacency, point_degree):
    n = len(adjacency)
    io.need(io.integer(point_degree) and 3 <= n <= 99 and 0 < 2 * point_degree < n,
            'TERNARY_SCORE_DOMAIN')
    io.need(adjacency.shape == (n, n) and adjacency.dtype == np.dtype('int64')
            and np.all((adjacency == 0) | (adjacency == 1))
            and np.array_equal(adjacency, adjacency.T)
            and np.all(np.diag(adjacency) == 0)
            and np.all(adjacency.sum(axis=1) == 2 * point_degree), 'TERNARY_SCORE_DOMAIN')
    # Exact int64 only. CN<=99, |residual|<=99, <=4851 pair squares;
    # conservative total<48million, all intermediate values<2**63.
    cn = adjacency @ adjacency
    io.need(cn.dtype == np.dtype('int64') and np.all((0 <= cn) & (cn <= n))
            and np.array_equal(cn, cn.T)
            and np.array_equal(np.diag(cn), adjacency.sum(axis=1)), 'INTEGER_PRODUCT')
    u, v = np.triu_indices(n, 1)
    residual = cn[u, v] + adjacency[u, v] - 2
    residues = np.remainder(residual, 3)
    hist = [int(np.count_nonzero(residues == r)) for r in range(3)]
    edges = adjacency[u, v] == 1
    el = int(np.sum(residual[edges] ** 2, dtype=np.int64))
    em = int(np.sum(residual[~edges] ** 2, dtype=np.int64))
    f3 = hist[1] + hist[2]
    weight = 819820 if (n, point_degree) == (99, 7) else n * (n - 1) // 2 * (2 * point_degree) ** 2 + 1
    metrics = dict(F3=f3, E_lambda=el, E_mu=em, E=el + em,
                   scalar_weight=weight, scalar=weight * f3 + el + em,
                   residue_population=hist)
    return metrics, cn


@dataclass(frozen=True)
class Input:
    n: int
    degree: int
    rows: tuple
    adjacency: np.ndarray
    cn: np.ndarray
    metrics: dict
    pairs: tuple
    digest: str

    @property
    def total(self):
        return 9 * len(self.pairs)


def fingerprint(base):
    return hashlib.sha256(io.canonical(dict(n=base.n, degree=base.degree,
        rows=base.rows, metrics=base.metrics, pairs=base.pairs))
        + base.adjacency.tobytes(order='C') + base.cn.tobytes(order='C')).hexdigest()


def fixed_input(n, degree, rows):
    adjacency = io.geometry(n, degree, rows, 0)
    metrics, cn = score(adjacency, degree)
    adjacency.setflags(write=False); cn.setflags(write=False)
    values = dict(n=n, degree=degree, rows=tuple(tuple(row) for row in rows),
                  adjacency=adjacency, cn=cn, metrics=metrics,
                  pairs=tuple(combinations(range(len(rows)), 2)))
    provisional = Input(**values, digest='')
    return Input(**values, digest=fingerprint(provisional))


def unchanged(base):
    io.need(not base.adjacency.flags.writeable and not base.cn.flags.writeable
            and fingerprint(base) == base.digest, 'BASE_IMMUTABILITY')


def expected_record(base, pid):
    io.need(io.integer(pid) and 0 <= pid < base.total, 'RECORD_ID')
    i, j = base.pairs[pid // 9]
    ix, jy = divmod(pid % 9, 3)
    first, second = base.rows[i], base.rows[j]
    x, y = first[ix], second[jy]
    record = dict(schema=SCHEMA, objective_version=OBJECTIVE, proposal_id=pid,
        i=i, j=j, ix=ix, jy=jy, old_triples=[list(first), list(second)],
        new_triples=None, valid=False, invalid_reason=None, conflict_pair=None,
        removed_pairs=None, added_pairs=None, toggles=None, changed_rows=None,
        delta_F3=None, delta_E_lambda=None, delta_E_mu=None, delta_E=None,
        delta_scalar=None, new_metrics=None, tuple_direction=None, classification=None)
    if x in second or y in first:
        record.update(invalid_reason='selected_point_not_exclusive', classification='invalid_selection')
        return record, None, None
    rows = [list(row) for row in base.rows]
    rows[i][ix], rows[j][jy] = y, x
    record['new_triples'] = [rows[i][:], rows[j][:]]
    aa = [v for k, v in enumerate(first) if k != ix]
    bb = [v for k, v in enumerate(second) if k != jy]
    removed = [sorted((x, v)) for v in aa] + [sorted((y, v)) for v in bb]
    added = [sorted((y, v)) for v in aa] + [sorted((x, v)) for v in bb]
    # Full final pair multiset, independent of producer bitset removal/addition.
    occupancy = Counter(tuple(sorted(pair)) for row in rows for pair in combinations(row, 2))
    conflicts = {pair for pair, count in occupancy.items() if count > 1}
    if conflicts:
        # Exclusivity guarantees these four added pairs are distinct. Every
        # new conflict is one of them; their declared order binds the diagnostic.
        io.need(len({tuple(pair) for pair in added}) == 4, 'EXCLUSIVE_ADDED_DISTINCT')
        conflict = next((pair for pair in added if tuple(pair) in conflicts), None)
        io.need(conflict is not None, 'CONFLICT_COVERAGE')
        record.update(invalid_reason='new_pair_already_present',
                      conflict_pair=conflict, classification='invalid_linearity')
        return record, None, None
    adjacency = io.geometry(base.n, base.degree, rows, 0)
    metrics, cn = score(adjacency, base.degree)
    u, v = np.triu_indices(base.n, 1)
    changed_edges = adjacency[u, v] != base.adjacency[u, v]
    toggles = [[int(a), int(b)] for a, b in zip(u[changed_edges], v[changed_edges])]
    changed_rows = [int(u) for u in np.flatnonzero(np.any(adjacency != base.adjacency, axis=1))]
    before = (base.metrics['F3'], base.metrics['E'])
    after = (metrics['F3'], metrics['E'])
    df3 = metrics['F3'] - base.metrics['F3']
    record.update(valid=True, removed_pairs=removed, added_pairs=added,
        toggles=toggles, changed_rows=changed_rows, delta_F3=df3,
        delta_E_lambda=metrics['E_lambda'] - base.metrics['E_lambda'],
        delta_E_mu=metrics['E_mu'] - base.metrics['E_mu'],
        delta_E=metrics['E'] - base.metrics['E'],
        delta_scalar=metrics['scalar'] - base.metrics['scalar'], new_metrics=metrics,
        tuple_direction='down' if after < before else 'up' if after > before else 'equal',
        classification='valid_F3_' + ('down' if df3 < 0 else 'up' if df3 > 0 else 'equal'))
    return record, adjacency, cn


def check_record(base, pid, raw):
    io.need(type(raw) is dict and set(raw) == FIELDS and raw.get('schema') == SCHEMA
            and raw.get('objective_version') == OBJECTIVE, 'RECORD_SCHEMA')
    io.need(io.integer(raw.get('proposal_id')) and raw['proposal_id'] == pid, 'RECORD_ID')
    expected, adjacency, cn = expected_record(base, pid)
    io.need(io.same(raw, expected), 'RECORD_CONTENT', 'all24 fields through full raw reconstruction')
    return expected, adjacency, cn


class Aggregate:
    def __init__(self):
        self.counts = Counter(); self.directions = Counter(); self.unique = set()
        self.minimum_pair = None; self.pair_ties = []
        self.minimum_f3 = None; self.f3_ties = []; self.zero_records = []

    def add(self, record):
        self.counts[record['classification']] += 1
        if record['valid'] is False:
            return
        self.directions[record['tuple_direction']] += 1
        self.unique.add(tuple(tuple(pair) for pair in record['toggles']))
        metrics = record['new_metrics']; pair = (metrics['F3'], metrics['E'])
        if self.minimum_pair is None or pair < self.minimum_pair:
            self.minimum_pair = pair; self.pair_ties = [record]
        elif pair == self.minimum_pair:
            self.pair_ties.append(record)
        if self.minimum_f3 is None or metrics['F3'] < self.minimum_f3:
            self.minimum_f3 = metrics['F3']; self.f3_ties = [record]
        elif metrics['F3'] == self.minimum_f3:
            self.f3_ties.append(record)
        if metrics['F3'] == 0:
            self.zero_records.append(record)

    def snapshot(self):
        return dict(counts=dict(sorted(self.counts.items())),
            tuple_directions=dict(sorted(self.directions.items())),
            unique_valid_neighbor_graphs=len(self.unique),
            minimum_pair=None if self.minimum_pair is None else list(self.minimum_pair),
            minimum_pair_proposal_ids=[r['proposal_id'] for r in self.pair_ties],
            minimum_F3=self.minimum_f3,
            minimum_F3_proposal_ids=[r['proposal_id'] for r in self.f3_ties],
            residue_zero_proposal_ids=[r['proposal_id'] for r in self.zero_records])


def checkpoint(raw, identity, parts, end, aggregate):
    io.need(type(raw) is dict and set(raw) == {'schema', 'identity', 'next_proposal_id', 'parts', 'aggregate'}
            and io.integer(raw.get('next_proposal_id')) and type(raw.get('parts')) is list
            and type(raw.get('aggregate')) is dict, 'CHECKPOINT_TYPES')
    io.need(raw.get('schema') == CHECKPOINT_SCHEMA and io.same(raw.get('identity'), identity), 'CHECKPOINT_IDENTITY')
    io.need(raw['next_proposal_id'] == end and io.same(raw['parts'], parts), 'CHECKPOINT_PREFIX')
    io.need(io.same(raw['aggregate'], aggregate), 'CHECKPOINT_AGGREGATE')


def full_integer_target(adjacency):
    io.need(adjacency.shape == (99, 99) and adjacency.dtype == np.dtype('int64')
            and np.all((adjacency == 0) | (adjacency == 1))
            and np.array_equal(adjacency, adjacency.T) and np.all(np.diag(adjacency) == 0), 'TARGET_DOMAIN')
    difference = adjacency @ adjacency - (12 * np.eye(99, dtype=np.int64) - adjacency + 2)
    return dict(all9801_integer_identity_entries_checked=True,
        degree14=bool(np.all(adjacency.sum(axis=1) == 14)),
        identity_mismatches=int(np.count_nonzero(difference)),
        is_target=bool(np.all(difference == 0) and np.all(adjacency.sum(axis=1) == 14)))
