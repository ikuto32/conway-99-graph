"""Arithmetic corruption controls for the standalone integer certificate replay."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import time

import verify_star_marginal_certificate as verifier

ROOT = Path(__file__).resolve().parents[1]
R = ROOT/'acceleration/results'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    verifier.require(not args.out.exists(), 'Fresh QA report required')
    started = time.perf_counter()
    cp = R/'20260916_cp_round9_auto/search/probes/selection_07_index_226_candidate.json'
    dp = R/'20260916_cp_zero_completion/local_226/stars.json'
    pp = dp.with_name('independent_pair_audit.json')
    certp = R/'20260916_star_marginal_pilot/index_226_certificate.json'
    candidate, stars, proof, cert = [json.loads(p.read_bytes()) for p in (cp, dp, pp, certp)]
    bindings = {verifier.key(p): verifier.digest(p) for p in (cp, dp, pp, certp, Path(__file__),
                 ROOT/'acceleration/verify_star_marginal_certificate.py', ROOT/'acceleration/audit_certificate.py')}
    for doc in (proof, cert):
        for path, expected in doc['inputs_sha256'].items():
            verifier.require(verifier.digest(path) == expected, 'Changed positive control input')
            bindings[verifier.key(path)] = expected
    records = []
    def run(name, mutate=lambda c, d: None, accept=False):
        c, d = deepcopy(cert), deepcopy(stars)
        mutate(c, d)
        try:
            result = verifier.verify(candidate, d, proof, c)
        except ValueError as exc:
            verifier.require(not accept, 'Positive control rejected: '+str(exc))
            records.append(dict(name=name, expected='REJECT', observed='REJECT', reason=str(exc)))
        else:
            verifier.require(accept, 'Corrupt certificate accepted: '+name)
            records.append(dict(name=name, expected='PASS', observed='PASS', fixed_K_excluded=result['fixed_K_excluded']))
    run('real_positive_certificate', accept=True)
    def scale_up(c, _d):
        factor = 10**30
        for field in ('integer_scale', 'integer_cap_rhs', 'integer_gap'):
            c[field] = str(int(c[field])*factor)
        for field in ('integer_reciprocity_weights', 'integer_cap_weights', 'integer_vertex_minima'):
            c[field] = [str(int(v)*factor) for v in c[field]]
    run('positive_scaling_10_to_30', scale_up, True)
    def zero(c, _d):
        c.update(integer_scale='1', integer_cap_rhs='0', integer_gap='0', integer_reciprocity_weights=['0']*1680,
                 integer_cap_weights=['0']*3486, integer_vertex_minima=['0']*84, minimizing_domain_ids=[0]*84,
                 exact_phase1_lower_bound=dict(numerator='0', denominator='1', approximate=0), fixed_K_excluded=False,
                 status='EXACT_STAR_MARGINAL_SIMPLEX_DUAL_BOUND')
    run('zero_dual_is_bound_not_exclusion', zero, True)
    mutations = [
        ('negative_cap_weight', lambda c, d: c['integer_cap_weights'].__setitem__(0, '-1')),
        ('reciprocity_outside_box', lambda c, d: c['integer_reciprocity_weights'].__setitem__(0, str(int(c['integer_scale'])+1))),
        ('missing_cap_weight', lambda c, d: c['integer_cap_weights'].pop()),
        ('wrong_minimum', lambda c, d: c['integer_vertex_minima'].__setitem__(0, str(int(c['integer_vertex_minima'][0])+1))),
        ('wrong_minimizer', lambda c, d: c['minimizing_domain_ids'].__setitem__(0, -1)),
        ('wrong_rhs', lambda c, d: c.__setitem__('integer_cap_rhs', str(int(c['integer_cap_rhs'])+1))),
        ('wrong_gap', lambda c, d: c.__setitem__('integer_gap', str(int(c['integer_gap'])+1))),
        ('wrong_exact_lower', lambda c, d: c['exact_phase1_lower_bound'].__setitem__('numerator', str(int(c['exact_phase1_lower_bound']['numerator'])+1))),
        ('wrong_exclusion_flag', lambda c, d: c.__setitem__('fixed_K_excluded', False)),
        ('wrong_projection', lambda c, d: c.__setitem__('projection_convention', 'LARGER_ENDPOINT')),
        ('missing_domain', lambda c, d: d['domains'][0]['domain_masks_hex'].pop()),
        ('duplicate_domain', lambda c, d: d['domains'][0]['domain_masks_hex'].__setitem__(0, d['domains'][0]['domain_masks_hex'][1])),
        ('noninteger_weight', lambda c, d: c['integer_cap_weights'].__setitem__(0, '0.1')),
        ('zero_scale', lambda c, d: c.__setitem__('integer_scale', '0')),
    ]
    for name, mutate in mutations:
        run(name, mutate)
    verifier.require(all(verifier.digest(path) == expected for path, expected in bindings.items()), 'Frozen dependency changed')
    report = dict(status='STAR_MARGINAL_INTEGER_CERTIFICATE_CORRUPTION_CONTROLS_PASS', inputs_sha256=bindings,
                  positive_controls=3, negative_controls=len(mutations), records=records,
                  arithmetic_controls_bypass_hash_guards=True, numerical_solver_calls=0, elapsed_seconds=time.perf_counter()-started)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: report[k] for k in ('status', 'positive_controls', 'negative_controls', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
