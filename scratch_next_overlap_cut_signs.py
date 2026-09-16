"""Check the indexing sensitivity of a necessary cut on isomorphic lifts.

All tested inputs are root-label permutations of an already excluded K.
This does not generate a new graph candidate or test global existence.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json

from scratch_next_overlap_cut import evaluate


def main():
    path = Path('scratch_resume_overlap_lift.json')
    raw = path.read_bytes()
    original = set(map(tuple, json.loads(raw)['overlap_edges_outer_zero_based']))
    supports = list(combinations(range(7), 2))
    records = []
    for flip_mask in [0]+[1 << g for g in range(7)]:
        permutation = []
        for f, (a, b) in enumerate(supports):
            for s in range(2):
                for t in range(2):
                    permutation.append(4*f+2*(s ^ ((flip_mask >> a)&1))+(t ^ ((flip_mask >> b)&1)))
        assert sorted(permutation) == list(range(84))
        assert all(permutation[permutation[x]] == x for x in range(84))
        transformed = {tuple(sorted((permutation[u], permutation[v]))) for u, v in original}
        assert len(transformed) == 168
        result = evaluate(transformed)
        records.append({'flip_mask': flip_mask, 'score': result['score'],
                        'rejected_by_one_fixed_cut': result['excluded_by_this_cut']})
    assert records[0]['score'] == -807
    result = {'status': 'CUT_SIGN_RELABELING_EVALUATION_COMPLETE',
              'input_sha256': hashlib.sha256(raw).hexdigest(),
              'tested_isomorphic_lifts': len(records),
              'rejected_by_one_fixed_cut': sum(r['rejected_by_one_fixed_cut'] for r in records),
              'records': records,
              'scope': 'Every input is isomorphic to the excluded overlap graph. A nonnegative single-cut score is not a completion witness. For search, sign-conjugates of the fixed inequality remain valid and can be applied when useful.'}
    Path('scratch_next_overlap_cut_signs.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
