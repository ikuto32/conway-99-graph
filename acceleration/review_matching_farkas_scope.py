"""Independent projection arithmetic and conditional matching-family size.

This checker does not establish that every exported matrix row is necessary;
the separate full semantic matrix auditor is required for that conclusion.
"""
import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from audit_certificate import full_graph, require


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--matrix', type=Path, required=True)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior review')
    candidate, matrix, certificate = [json.loads(path.read_bytes()) for path in (args.candidate, args.matrix, args.certificate)]
    require(sha256(args.matrix.read_bytes()).hexdigest() == certificate['matrix_sha256'], 'Certificate matrix hash mismatch')
    adjacency, _ = full_graph(candidate)
    group, matching_class = matrix['root_group'], matrix['matching_class']
    require(type(group) is int and 0 <= group < 7 and matching_class in ('same_0','same_1','cross'), 'Invalid selected matching class')
    labels = [{(s-1)//2:(s-1)%2 for s in adjacency[u+15] if 1 <= s <= 14} for u in range(84)]
    cohort = [u for u in range(84) if group in labels[u] and
              (matching_class == 'cross' or labels[u][group] == int(matching_class[-1]))]
    allowed = {(u,v) for u in cohort for v in cohort if u<v and len(set(labels[u])&set(labels[v])) == 1
               and (matching_class != 'cross' or labels[u][group] != labels[v][group])}
    require(set(map(tuple, matrix['matching_variables'])) == allowed and len(matrix['matching_variables']) == len(allowed),
            'Matrix Y universe differs from full99 label-defined matching class')
    position = {u:i for i,u in enumerate(cohort)}
    possible = [0]*len(cohort)
    for u,v in allowed:
        possible[position[u]] |= 1 << position[v]
        possible[position[v]] |= 1 << position[u]

    @lru_cache(None)
    def count_matchings(mask):
        if not mask:
            return 1
        bit = mask & -mask
        u = bit.bit_length()-1
        others = mask ^ bit
        choices = possible[u] & others
        total = 0
        while choices:
            partner = choices & -choices
            choices ^= partner
            total += count_matchings(others ^ partner)
        return total

    matching_count = count_matchings((1 << len(cohort))-1)
    nx, ny = len(matrix['edge_variables']), len(matrix['matching_variables'])
    box_columns = nx+ny
    require(nx == 1680 and box_columns == certificate['projected_box_columns'] and
            matrix['ncols']-box_columns == certificate['zeroed_slack_columns'] == 5166, 'Projection dimensions differ')
    require(all(value == 0 for value in matrix['col_lower']) and all(value == 1 for value in matrix['col_upper'][:box_columns]),
            'Projected variables do not have [0,1] boxes')
    require(matrix['col_cost'] == [0]*box_columns+[1]*5166, 'Zero objective does not force every slack to zero')
    coefficients = [0]*box_columns
    rhs = 0
    selected_rows = set()
    for row, multiplier in certificate['weighted_rows']:
        require(type(row) is int and 0 <= row < matrix['nrows'] and row not in selected_rows
                and type(multiplier) is int and multiplier != 0, 'Malformed/repeated integer row multiplier')
        selected_rows.add(row)
        bound = matrix['row_lower'][row] if multiplier > 0 else matrix['row_upper'][row]
        require(type(bound) is int, 'Signed multiplier selects an infinite or noninteger row bound')
        rhs += multiplier*bound
        for offset in range(matrix['csr_start'][row], matrix['csr_start'][row+1]):
            column, value = matrix['csr_index'][offset], matrix['csr_value'][offset]
            require(type(column) is int and 0 <= column < matrix['ncols'] and type(value) is int, 'Noninteger CSR entry')
            if column < box_columns:
                coefficients[column] += multiplier*value
    maximum = sum(max(0, value) for value in coefficients)
    require(coefficients == certificate['combined_coefficients'] and rhs == certificate['combined_lower_rhs']
            and maximum == certificate['box_upper_bound'] and rhs-maximum == certificate['contradiction_margin'] > 0,
            'Integer projection arithmetic or strict contradiction differs')
    sources = (args.candidate, args.matrix, args.certificate, Path(__file__), Path(__file__).with_name('audit_certificate.py'))
    result = {'status': 'INDEPENDENT_ZERO_SLACK_ARITHMETIC_AND_FAMILY_SCOPE_REVIEW_PASS',
              'selected_root_group': group, 'selected_matching_class': matching_class,
              'cohort_vertices': cohort, 'allowed_y_edges': len(allowed),
              'all_perfect_matchings_before_partial_caps': matching_count,
              'fixed_other_matching_classes': 20, 'fixed_overlap_edges': 168-len(cohort)//2,
              'weighted_integer_rows': len(selected_rows), 'projected_box_columns': box_columns,
              'zeroed_nonnegative_unit_cost_slacks': 5166,
              'combined_lower_rhs': rhs, 'box_upper_bound': maximum, 'strict_contradiction_margin': rhs-maximum,
              'matrix_row_necessity_independently_established_here': False,
              'producer_or_solver_imported': False,
              'inputs_sha256': {str(path):sha256(path.read_bytes()).hexdigest() for path in sources},
              'scope': 'Arithmetic proves that the exported zero-slack box system is empty. Once the separate semantic auditor establishes every matrix row as necessary, this excludes every completion with the other20 matchings fixed, for every perfect matching of this selected cohort, including the fractional-Y relaxation. It is not a phase-I neighborhood minimum, all legal K, or global E0/Conway nonexistence. The matching count is before partial-cap filtering.'}
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key != 'inputs_sha256'}))


if __name__ == '__main__':
    main()
