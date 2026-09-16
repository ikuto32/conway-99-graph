"""Apply a necessary capacity inequality under all seven root sign swaps.

The minimum of these 128 valid inequalities is a sign-invariant rejection
test. Passing is only a relaxation result, never an adjacency certificate.
"""
import argparse
from itertools import combinations
import hashlib
import json
from pathlib import Path

from scratch_next_overlap_cut import evaluate


SUPPORTS = tuple(combinations(range(7), 2))


def sign_permutation(mask):
    if type(mask) is not int or not 0 <= mask < 128:
        raise ValueError('sign mask must be an integer in 0..127')
    return tuple(4*f + 2*(s ^ ((mask >> a) & 1)) + (t ^ ((mask >> b) & 1))
                 for f, (a, b) in enumerate(SUPPORTS)
                 for s in range(2) for t in range(2))


def transform(known, mask):
    permutation = sign_permutation(mask)
    return frozenset(tuple(sorted((permutation[u], permutation[v])))
                     for u, v in known)


def evaluate_orbit(known):
    records = []
    cache = {}
    for mask in range(128):
        transformed = transform(known, mask)
        if transformed not in cache:
            cache[transformed] = evaluate(transformed)
        result = cache[transformed]
        records.append({'flip_mask': mask, 'score': result['score']})
    best = min(records, key=lambda row: row['score'])
    return {
        'status': 'SIGN_ORBIT_CAPACITY_CUT_EVALUATED',
        'tested_sign_masks': 128,
        'distinct_sign_images': len(cache),
        'minimum_score': best['score'],
        'minimizing_flip_mask': best['flip_mask'],
        'excluded_by_sign_orbit_cut': best['score'] < 0,
        'negative_score_count': sum(row['score'] < 0 for row in records),
        'records': records,
        'scope': 'Necessary inequalities for the given E0=0 overlap assignment. Only the 128 root-group sign relabelings are tested; the 5040 group permutations are not included. Passing gives no graph or linear completion witness.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', type=Path,
                        default=Path('scratch_resume_overlap_lift.json'))
    parser.add_argument('--output', type=Path,
                        default=Path('scratch_next_overlap_cut_orbit.json'))
    args = parser.parse_args()
    raw = args.path.read_bytes()
    listed = json.loads(raw)['overlap_edges_outer_zero_based']
    known = frozenset(map(tuple, listed))
    if len(known) != len(listed):
        raise ValueError('duplicate overlap edge')
    evaluate(known)  # Validate endpoints and support type before permutations.
    result = evaluate_orbit(known)
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    for mask in range(128):
        permutation = sign_permutation(mask)
        assert sorted(permutation) == list(range(84))
        assert all(permutation[permutation[u]] == u for u in range(84))
    # XOR permutes the 128 scores of a relabeled input. Check the group law.
    for generator in (1, 2, 4, 8, 16, 32, 64):
        first = sign_permutation(generator)
        for mask in range(128):
            second, composed = sign_permutation(mask), sign_permutation(mask ^ generator)
            assert all(first[second[u]] == composed[u] for u in range(84))
    result['sign_group_composition_checked'] = True
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'records'}))


if __name__ == '__main__':
    main()
