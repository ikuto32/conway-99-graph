"""Direct integer matrix falsification tests and current-incumbent raw check."""
import argparse
from datetime import datetime, timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import random
import sys
import time

import audit_20260917_fresh_review as third


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    third.check(not args.out.exists(), 'preserve evidence')
    started = time.perf_counter()
    bindings = {third.key(__file__): third.digest(__file__), third.key(third.__file__): third.digest(third.__file__),
                'uv.lock': third.digest('uv.lock')}
    directory = 'acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481'
    data = third.read_case(directory, bindings)
    prepared = third.model(data[0])
    checked = third.verify(data, prepared)
    B, edges, _, caps = prepared
    rng = random.Random(20260917)
    assignments = [dict(name='all_zero', values=[0]*1680), dict(name='all_one', values=[1]*1680),
                   dict(name='seeded_binary', values=[rng.randrange(2) for _ in edges]),
                   dict(name='seeded_sparse', values=[int(rng.randrange(13) == 0) for _ in edges])]
    controls = []
    for assignment in assignments:
        values = assignment['values']
        A = [row[:] for row in B]
        X = [[0]*99 for _ in range(99)]
        for (u, v), value in zip(edges, values):
            A[u+15][v+15] = A[v+15][u+15] = value
            X[u+15][v+15] = X[v+15][u+15] = value
        for (u, v), (rhs, terms) in zip(combinations(range(84), 2), caps):
            a, b = u+15, v+15
            full = sum(A[a][w]*A[w][b] for w in range(99))+A[a][b]
            quadratic = sum(X[a][w]*X[w][b] for w in range(99))
            linear = sum(values[i]*coefficient for i, coefficient in terms)
            third.check(full == (2-rhs)+linear+quadratic, 'matrix residual identity')
            third.check(quadratic >= 0, 'nonnegative omitted product')
        controls.append(dict(name=assignment['name'], exact_pair_identities_checked=3486, result='PASS'))
    third.check(all(third.digest(f) == h for f, h in bindings.items()), 'source/input changed')
    report = dict(status='INCUMBENT_RAW_AND_MATRIX_IDENTITY_AUDIT_PASS',
                  timestamp=datetime.now(timezone.utc).isoformat(), source_commit=third.SOURCE,
                  claim_binding={'id': 'C-STAR-BASELINE-18481', 'revision': 1,
                    'statement_checked': 'The exact original-star phase-I interval for this fixed index18481 overlap assignment is the recorded interval; its positive lower bound excludes this fixed assignment only.'},
                  verifier='independent_verifier agent', command=' '.join(sys.argv), working_directory=str(Path.cwd()),
                  python=platform.python_version(), inputs_sha256=bindings, baseline=checked,
                  matrix_controls=controls, random_seed=20260917,
                  trusted_shared_code=['audit_20260917_fresh_review.py (new independent checker)',
                      'Python standard library', 'hash-bound historical complete original-domain audit'],
                  domain_completeness_reenumerated_here=False, matrix_control_scope='4 assignments x 3486 identities; algebraic proof separately written, sampled assignments do not establish universality',
                  elapsed_seconds=time.perf_counter()-started, general_nonexistence_proved=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status=report['status'], baseline=checked['exact_lower']['approximate'], controls=len(controls))))


if __name__ == '__main__':
    main()
