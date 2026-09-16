"""Export audited star-LP duals as deterministic dyadic ranking weights.

This writes no exclusion certificate and does not optimize or clip input weights.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCALE = 1 << 40
CONVENTION = 'X_UV_FROM_SMALLER_CURRENT_OUTER_INDEX;RECIPROCITY_SMALLER_MINUS_LARGER'

def resolve(path):
    p = Path(str(path).replace('\\', '/'))
    return (ROOT / p).resolve() if not p.is_absolute() else p.resolve()

def key(path):
    return resolve(path).relative_to(ROOT).as_posix()

def digest(path):
    return sha256(resolve(path).read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def export(result_path, audit_path, out):
    result_path, audit_path, out = map(resolve, (result_path, audit_path, out))
    require(not out.exists(), 'Preserve output directory')
    bindings = {}
    def bind(path, expected=None):
        name, actual = key(path), digest(path)
        require(expected is None or expected == actual, 'Changed dependency: ' + name)
        require(name not in bindings or bindings[name] == actual, 'Conflicting dependency')
        bindings[name] = actual
        return actual
    bind(__file__)
    bind(result_path)
    bind(audit_path)
    result, audit = [json.loads(p.read_bytes()) for p in (result_path, audit_path)]
    require(audit['status'] == 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS', 'Unaudited baseline')
    for document in (result, audit):
        for path, expected in document['inputs_sha256'].items():
            bind(path, expected)
    require({key(p): h for p,h in audit['inputs_sha256'].items()}.get(key(result_path)) == digest(result_path), 'Audit/result association')
    require(result['projection_convention'] == CONVENTION and result['original_complete_domains_used'] is True and result['pair_pruned_domains_used'] is False, 'Wrong projection/domain scope')
    bind(result['candidate_path'], result['candidate_sha256'])
    quantized = []
    max_error = Fraction(0)
    for name, size, lower in [('numeric_reciprocity_duals', 1680, -1), ('numeric_cap_duals', 3486, 0)]:
        values = result[name]
        require(type(values) is list and len(values) == size, 'Wrong dual length')
        require(all(type(v) in (float, int) and math.isfinite(v) and lower <= v <= 1 for v in values), 'Invalid raw dual box/value')
        integers = [round(Fraction(v) * SCALE) for v in values]
        require(all(lower*SCALE <= v <= SCALE for v in integers), 'Invalid quantized dual box')
        max_error = max(max_error, *(abs(Fraction(q, SCALE)-Fraction(v)) for q,v in zip(integers, values)))
        quantized.extend(integers)
    payload = 'C99STARDUAL_DYADIC1 1680 3486 1099511627776\n' + '\n'.join(map(str, quantized)) + '\n'
    out.mkdir(parents=True)
    weights = out/'dual.txt'
    weights.write_text(payload, encoding='ascii', newline='\n')
    manifest = dict(status='AUDITED_STAR_DUAL_DYADIC_RANKING_WEIGHTS_EXPORTED', inputs_sha256=bindings,
                    baseline_result_path=key(result_path), baseline_result_sha256=digest(result_path),
                    baseline_candidate_path=key(result['candidate_path']), baseline_candidate_sha256=result['candidate_sha256'],
                    dual_path=key(weights), dual_sha256=digest(weights), denominator=SCALE,
                    beta_order='1680 disjoint-support outer pairs u<v, lexicographic',
                    gamma_order='3486 all outer pairs u<v, lexicographic', projection_convention=CONVENTION,
                    rounding='Exact rational interpretation of stored binary float; nearest integer, ties to even; no clipping',
                    maximum_weight_change=float(max_error), certificate_generated=False)
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return manifest

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', required=True)
    p.add_argument('--audit', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    result = export(a.result, a.audit, a.out)
    print(result['status'], result['dual_sha256'])

if __name__ == '__main__':
    main()
