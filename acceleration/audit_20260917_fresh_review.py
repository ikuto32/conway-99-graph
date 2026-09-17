"""Third checking path for fixed-K star bounds; stdlib only, no project imports.

The known adjacency is rebuilt as a dense matrix. Cap coefficients are obtained
from the entry formula for (B+E)^2+(B+E), where E is one unknown edge.
Completeness is a separately disclosed dependency on the bound domain audit.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '7518ebcec78589fe7f8b068ee7a1dd87e8bf8d42'


def check(ok, message):
    if not ok:
        raise ValueError(message)


def path(p):
    p = Path(str(p).replace('\\', '/'))
    return p if p.is_absolute() else ROOT / p


def key(p):
    return path(p).resolve().relative_to(ROOT).as_posix()


def digest(p):
    return sha256(path(p).read_bytes()).hexdigest()


def integer(s):
    check(type(s) is str and re.fullmatch(r'-?(0|[1-9][0-9]*)', s), 'noncanonical integer')
    return int(s)


def rational(d):
    return Fraction(integer(d['numerator']), integer(d['denominator']))


def exact(q):
    return {'numerator': str(q.numerator), 'denominator': str(q.denominator), 'approximate': float(q)}


def model(candidate):
    labels = [(2*a+s, 2*b+t) for a in range(7) for b in range(a+1, 7)
              for s in range(2) for t in range(2)]
    B = [[0]*99 for _ in range(99)]
    def put(u, v):
        check(u != v and B[u][v] == 0, 'repeated/self edge')
        B[u][v] = B[v][u] = 1
    for s in range(1, 15):
        put(0, s)
    for s in range(1, 15, 2):
        put(s, s+1)
    for u, lab in enumerate(labels, 15):
        for s in lab:
            put(u, s+1)
    overlap = candidate['overlap_edges_outer_zero_based']
    check(type(overlap) is list and len(overlap) == 168, 'overlap count')
    for edge in overlap:
        check(type(edge) is list and len(edge) == 2 and all(type(x) is int for x in edge), 'edge format')
        u, v = edge
        check(0 <= u < v < 84, 'edge range')
        check(len({s//2 for s in labels[u]} & {s//2 for s in labels[v]}) == 1, 'overlap scope')
        put(u+15, v+15)
    check([sum(row) for row in B] == [14]*15+[6]*84, 'partial degrees')
    C = [[sum(x*y for x, y in zip(B[u], B[v])) for v in range(99)] for u in range(99)]
    check(all(C[u][v] <= 2-B[u][v] for u, v in combinations(range(99), 2)), 'partial graph cap')
    pairs = list(combinations(range(84), 2))
    unknown = [(u, v) for u, v in pairs if not {s//2 for s in labels[u]} & {s//2 for s in labels[v]}]
    check(len(unknown) == 1680, 'unknown universe')
    lookup = {e: i for i, e in enumerate(unknown)}
    caps = []
    # For an unknown edge pq, E_ab+[BE+EB]_ab is exactly the
    # off-diagonal change in B^2+B when just pq is switched on.
    for a, b in pairs:
        terms = []
        A, Z = a+15, b+15
        for i, (p, q) in enumerate(unknown):
            P, Q = p+15, q+15
            coefficient = int((a, b) == (p, q))
            coefficient += (B[A][P] if Z == Q else 0) + (B[A][Q] if Z == P else 0)
            coefficient += (B[Q][Z] if A == P else 0) + (B[P][Z] if A == Q else 0)
            if coefficient:
                terms.append((i, coefficient))
        caps.append((2-B[A][Z]-C[A][Z], terms))
    return B, unknown, lookup, caps


def verify(data, prepared=None, with_primal=True):
    candidate, domains, proof, cert, numeric, audit = data
    B, edges, lookup, caps = prepared or model(candidate)
    check(proof['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and
          proof['complete_used_domains_verified'] is True, 'complete prior audit required')
    check(domains['complete_domain_enumeration'] is True and
          [r['outer_vertex'] for r in domains['domains']] == list(range(84)), 'domain inventory')
    check(cert['projection_convention'] == 'X_UV_FROM_SMALLER_CURRENT_OUTER_INDEX;RECIPROCITY_SMALLER_MINUS_LARGER' and
          cert['domain_scope'] == 'ALL_ORIGINAL_COMPLETE_DOMAINS', 'scope convention')
    scale = integer(cert['integer_scale'])
    beta = list(map(integer, cert['integer_reciprocity_weights']))
    gamma = list(map(integer, cert['integer_cap_weights']))
    check(scale > 0 and len(beta) == 1680 and len(gamma) == 3486, 'dual dimensions/scale')
    check(all(-scale <= b <= scale for b in beta) and all(0 <= g <= scale for g in gamma), 'dual boxes')
    costs = [0]*1680
    for g, (_, terms) in zip(gamma, caps):
        for i, coefficient in terms:
            costs[i] += g*coefficient
    mincost, argmin, tables = [], [], []
    for u, row in enumerate(domains['domains']):
        masks = [int(s, 16) for s in row['domain_masks_hex']]
        check(row['status'] == 'COMPLETE' and len(masks) > 0 and len(set(masks)) == len(masks), 'bad domain')
        check(len(masks) == proof['independently_reenumerated_domains'][u]['domain_size'], 'completeness count')
        local = []
        table = []
        for mask in masks:
            check(mask >= 0 and mask < 1 << 84 and mask.bit_count() == 8, 'mask range/cardinality')
            selected = [v for v in range(84) if mask >> v & 1]
            check(all(tuple(sorted((u, v))) in lookup for v in selected), 'mask edge universe')
            check(all(sum(B[u+15][w]*B[s][w] for w in range(99)) +
                      sum(B[s][v+15] for v in selected) == 2-B[u+15][s]
                      for s in range(1, 15)), 'root quota')
            local.append(sum((beta[lookup[u, v]]+costs[lookup[u, v]]) if u < v else
                             -beta[lookup[v, u]] for v in selected))
            table.append(selected)
        mincost.append(min(local)); argmin.append(local.index(min(local))); tables.append(table)
    rhs = sum(g*b for g, (b, _) in zip(gamma, caps))
    gap = sum(mincost)-rhs
    lower = Fraction(gap, scale)
    check(mincost == list(map(integer, cert['integer_vertex_minima'])), 'claimed minima')
    check(argmin == cert['minimizing_domain_ids'], 'claimed minimizers')
    check(rhs == integer(cert['integer_cap_rhs']) and gap == integer(cert['integer_gap']), 'rhs/gap')
    check(lower == rational(cert['exact_phase1_lower_bound']), 'exact bound')
    check(cert['fixed_K_excluded'] is (gap > 0), 'exclusion flag')
    check(cert['status'] == ('EXACT_STAR_MARGINAL_SIMPLEX_DUAL_CONTRADICTION' if gap > 0 else
                            'EXACT_STAR_MARGINAL_SIMPLEX_DUAL_BOUND'), 'status')
    result = dict(exact_lower=exact(lower), fixed_K_excluded=gap > 0,
                  domain_choices_checked=sum(map(len, tables)), complete_domain_sets_reenumerated_here=False,
                  domain_completeness_dependency='Hash-bound prior independent exhaustive audit; source reviewed')
    if with_primal:
        check(len(numeric['numeric_probabilities']) == sum(map(len, tables)), 'probability dimensions')
        values = iter(map(Fraction, numeric['numeric_probabilities']))
        M = [[Fraction(0) for _ in range(84)] for _ in range(84)]
        for u, table in enumerate(tables):
            ps = [next(values) for _ in table]
            total = sum(ps)
            check(total > 0 and min(ps) >= 0, 'probability simplex')
            for selected, p in zip(table, ps):
                for v in selected:
                    M[u][v] += p/total
        x = [M[u][v] for u, v in edges]
        upper = sum(abs(M[u][v]-M[v][u]) for u, v in edges)
        upper += sum(max(Fraction(0), sum(x[i]*c for i, c in terms)-b) for b, terms in caps)
        check(lower == rational(audit['exact_dual_lower']) and upper == rational(audit['exact_primal_upper']), 'audit interval')
        check(lower <= upper, 'weak duality')
        result['exact_upper'] = exact(upper)
    return result


def read_case(directory, bindings):
    directory = path(directory)
    def read(p):
        bindings[key(p)] = digest(p)
        return json.loads(path(p).read_bytes())
    numeric = read(directory/'phase1.json')
    names = [numeric[f'{s}_path'] for s in ('candidate', 'domains', 'domain_audit')]
    docs = [read(p) for p in names]
    cert, audit = read(directory/'integer_certificate.json'), read(directory/'audit.json')
    for doc in (*docs[1:], cert, numeric, audit):
        for p, h in doc.get('inputs_sha256', {}).items():
            check(digest(p) == h, 'changed input: '+str(p))
            bindings[key(p)] = h
    for doc, required in ((docs[2], names[:2]), (cert, names)):
        mapped = {key(p): h for p, h in doc['inputs_sha256'].items()}
        check(all(mapped.get(key(p)) == digest(p) for p in required), 'unbound domain/certificate')
    return (*docs, cert, numeric, audit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    check(not args.out.exists(), 'preserve prior report')
    started = time.perf_counter()
    bindings = {key(__file__): digest(__file__), 'uv.lock': digest('uv.lock')}
    control = read_case('acceleration/results/20260916_star_guided_round3/recovered_star_shortlist/index_521', bindings)
    prepared = model(control[0])
    records = [{'name': 'historical_positive_with_exact_primal', 'outcome': 'PASS', **verify(control, prepared)}]
    mutations = [
        ('wrong_gap', lambda d: d[3].__setitem__('integer_gap', str(int(d[3]['integer_gap'])+1))),
        ('negative_cap_weight', lambda d: d[3]['integer_cap_weights'].__setitem__(0, '-1')),
        ('missing_domain', lambda d: d[1]['domains'][0]['domain_masks_hex'].pop()),
        ('repeated_domain', lambda d: d[1]['domains'][0]['domain_masks_hex'].__setitem__(0, d[1]['domains'][0]['domain_masks_hex'][1])),
        ('wrong_projection', lambda d: d[3].__setitem__('projection_convention', 'LARGER_ENDPOINT')),
        ('wrong_exclusion', lambda d: d[3].__setitem__('fixed_K_excluded', False)),
    ]
    for name, mutate in mutations:
        changed = deepcopy(control); mutate(changed)
        try:
            verify(changed, prepared, with_primal=False)
        except ValueError as e:
            records.append(dict(name=name, outcome='REJECT', reason=str(e)))
        else:
            raise ValueError('corrupted control accepted: '+name)
    print(json.dumps(dict(event='CONTROLS_PASS', positive=1, corrupted=6)), flush=True)
    outcomes = []
    if args.run:
        summary_path = args.run/'summary.json'
        summary = json.loads(path(summary_path).read_bytes())
        bindings[key(summary_path)] = digest(summary_path)
        for row in summary['records']:
            if not row['audited']:
                outcomes.append(dict(proposal_index=row['proposal_index'], result='SKIPPED_NO_AUDITED_CERTIFICATE'))
                continue
            directory = args.run/f"index_{row['proposal_index']}"
            data = read_case(directory, bindings)
            checked = verify(data)
            check(rational(checked['exact_lower']) == rational(row['exact_lower']) and
                  rational(checked['exact_upper']) == rational(row['exact_upper']), 'summary bounds')
            outcomes.append(dict(proposal_index=row['proposal_index'], result='INDEPENDENT_RAW_CHECK_PASS', **checked))
            print(json.dumps(dict(event='CASE_CHECKED', index=row['proposal_index'], lower=checked['exact_lower']['approximate'])), flush=True)
    check(all(digest(p) == h for p, h in bindings.items()), 'input changed during checking')
    report = dict(status='THIRD_PATH_EXACT_FIXED_K_STAR_REVIEW_PASS', source_commit=SOURCE,
                  timestamp=datetime.now(timezone.utc).isoformat(), verifier='independent_verifier agent; separate stdlib implementation',
                  command=' '.join(sys.argv), working_directory=str(Path.cwd()), python=platform.python_version(),
                  shared_trusted_components=['Python standard library', 'raw candidate/domain/certificate artifacts',
                      'hash-bound original-domain completeness audit (not rerun by this checker)'],
                  project_imports=[], numerical_solver_calls=0, controls=records, records=outcomes,
                  inputs_sha256=bindings, elapsed_seconds=time.perf_counter()-started,
                  target_resolution=False, scope='Only enumerated fixed complete overlap assignments; no unrestricted coverage',
                  limitations=['Raw arithmetic and matrix reconstruction independently checked; full original domain enumeration relies on prior independent auditor whose source was reviewed.',
                               'No nontrivial automorphism assumed by the fixed-K implication.',
                               'This report is evidence, not a claim-ledger promotion; bind to exact claim revision separately.'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status=report['status'], cases=len(outcomes), seconds=report['elapsed_seconds'])))


if __name__ == '__main__':
    main()
