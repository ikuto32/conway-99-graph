"""Extract an integer zero-slack contradiction; independent audit is required.

Signed row multipliers give C*v >= R. All X/Y variables lie in [0,1],
so C*v <= sum(max(C_j,0)). A positive difference contradicts feasibility.
Completion slacks are projected to zero. No solver status is used as proof.
"""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix', type=Path, required=True)
    parser.add_argument('--relaxation', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--scale', type=int, default=1_000_000)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve existing certificate')
    require(0 < args.scale <= 10**12, 'Invalid multiplier scale')
    matrix = json.loads(args.matrix.read_bytes())
    relaxation = json.loads(args.relaxation.read_bytes())
    require(relaxation['matrix_sha256'] == digest(args.matrix), 'LP/matrix binding mismatch')
    nrows, ncols = matrix['nrows'], matrix['ncols']
    boxed = len(matrix['edge_variables']) + len(matrix['matching_variables'])
    require(boxed == 1680 + len(matrix['matching_variables']), 'Unexpected variable support')
    require(matrix['col_lower'][:boxed] == [0]*boxed
            and matrix['col_upper'][:boxed] == [1]*boxed, 'Expected boxed X/Y')
    require(matrix['col_cost'] == [0]*boxed + [1]*(ncols-boxed), 'Unexpected phase-I objective')
    require(matrix['col_lower'][boxed:] == [0]*(ncols-boxed), 'Slacks must be nonnegative')
    duals = relaxation['row_duals']
    require(type(duals) is list and len(duals) == nrows
            and all(type(v) in (int, float) and isfinite(v) for v in duals), 'Missing finite row duals')
    start, indices, values = (matrix[name] for name in ('csr_start', 'csr_index', 'csr_value'))
    require(len(start) == nrows+1 and start[0] == 0 and start[-1] == len(indices) == len(values),
            'Invalid CSR shape')
    require(all(type(v) is int for v in values), 'Coefficients must be exact integers')
    coefficients = [0]*boxed
    rhs = 0
    weighted_rows = []
    dropped_invalid_sign = 0
    for row, value in enumerate(duals):
        weight = round(value*args.scale)
        if weight == 0:
            continue
        bound = matrix['row_lower'][row] if weight > 0 else matrix['row_upper'][row]
        if bound is None:
            dropped_invalid_sign += 1
            continue
        require(type(bound) is int, 'Finite bounds must be exact integers')
        weighted_rows.append([row, weight])
        rhs += weight*bound
        for entry in range(start[row], start[row+1]):
            col = indices[entry]
            require(type(col) is int and 0 <= col < ncols, 'Column index outside matrix')
            if col < boxed:
                coefficients[col] += weight*values[entry]
    box_upper = sum(max(value, 0) for value in coefficients)
    margin = rhs-box_upper
    result = dict(status='INTEGER_ZERO_SLACK_MATCHING_CONTRADICTION_CANDIDATE'
                  if margin > 0 else 'NO_POSITIVE_INTEGER_CONTRADICTION',
                  matrix_path=args.matrix.as_posix(), matrix_sha256=digest(args.matrix),
                  relaxation_path=args.relaxation.as_posix(), relaxation_sha256=digest(args.relaxation),
                  source_sha256=digest(Path(__file__)), multiplier_scale=args.scale,
                  projected_box_columns=boxed, zeroed_slack_columns=ncols-boxed,
                  matrix_rows=nrows, weighted_rows=weighted_rows,
                  invalid_sign_rows_dropped=dropped_invalid_sign,
                  combined_coefficients=coefficients, combined_lower_rhs=rhs,
                  box_upper_bound=box_upper, contradiction_margin=margin,
                  inequality='C*v >= R and 0<=v<=1 imply R <= sum(max(C_j,0)); positive margin contradicts this.',
                  independent_semantic_audit_required=True,
                  scope='Candidate contradiction for zero-slack completion in one whole-matching family with 20 matchings fixed. The matrix must independently be proved necessary for that family. No global nonexistence or complete Conway graph claim.')
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('weighted_rows', 'combined_coefficients')}))


if __name__ == '__main__':
    main()
