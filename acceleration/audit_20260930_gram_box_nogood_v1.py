"""Independent exact Boolean-box Gram cut checker; never imports producer code."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys

import audit_20260930_gram_nogood_v1 as support

ROOT = support.ROOT
need,digest,key = support.need,support.digest,support.key


def audit_certificate(certificate,graph,mapping):
    need(certificate['cut_kind'] == 'GRAM_BOOLEAN_BOX_MAXIMUM' and certificate['matrix'] == '27I-9A+J','exact box-cut definition')
    vector = certificate['integer_negative_vector']
    need(len(vector) == 59 and all(type(x) is int for x in vector),'exact integer vector')
    current = support.direct_quadratic(graph,vector)
    need(type(certificate['quadratic_value_at_parent_graph']) is int and current == certificate['quadratic_value_at_parent_graph'] < 0,'exact parent quadratic')
    zero_graph = [row.copy() for row in graph]
    for u,v in mapping.values():
        zero_graph[u][v] = zero_graph[v][u] = 0
    constant = support.direct_quadratic(zero_graph,vector)
    need(type(certificate['linear_quadratic_constant']) is int and certificate['linear_quadratic_constant'] == constant,'exact fixed polynomial constant')
    coefficients = {variable:-18*vector[u]*vector[v] for variable,(u,v) in mapping.items()}
    rows = certificate['variable_coefficients_and_free_choices']
    need(all(type(row['variable']) is int and type(row['coefficient']) is int and type(row['value_in_rejected_graph']) is int
             and type(row['maximum_gain_if_freed']) is int and type(row['free']) is bool for row in rows),'typed coefficient/free-decision records')
    need(len(rows) == len({row['variable'] for row in rows}) and {row['variable'] for row in rows} == {v for v,c in coefficients.items() if c},'all and only nonzero coefficients')
    fixed = {}
    gains = 0
    for row in rows:
        variable = row['variable']
        u,v = mapping[variable]
        coefficient = coefficients[variable]
        value = graph[u][v]
        need(row['edge_full59'] == [u,v] and row['coefficient'] == coefficient and row['value_in_rejected_graph'] == value,'independent coefficient/edge/current-value check')
        # Enumerate this one bit independently instead of trusting a sign/gain
        # shortcut. This also establishes the exact gain, not only an upper bound.
        gain = max(coefficient*bit for bit in (0,1))-coefficient*value
        need(row['maximum_gain_if_freed'] == gain,'exact one-bit free gain')
        if row['free']:
            gains += gain
        else:
            fixed[variable] = value
    # Construct an actual maximizing Boolean corner of the entire780bit box,
    # including every omitted zero-coefficient variable. This graph need not
    # satisfy the weaker local constraints: the larger box gives a safe bound.
    corner = [row.copy() for row in zero_graph]
    maximizing_values = {}
    for variable,(u,v) in mapping.items():
        maximizing_values[variable] = fixed.get(variable,int(coefficients[variable] > 0))
        corner[u][v] = corner[v][u] = maximizing_values[variable]
    upper = support.direct_quadratic(corner,vector)
    polynomial_maximum = constant+sum(coefficients[v]*maximizing_values[v] for v in mapping)
    need(upper == polynomial_maximum == current+gains,'three independent box maximum evaluations')
    need(type(certificate['global_boolean_box_upper_bound']) is int and upper == certificate['global_boolean_box_upper_bound'] < 0,'strictly negative exact full-box maximum')
    expected_clause = [-variable if value else variable for variable,value in sorted(fixed.items())]
    clause = certificate['nogood_clause']
    need(all(type(literal) is int and literal != 0 for literal in clause)
         and len(clause) == len({abs(x) for x in clause}) == certificate['nogood_clause_length'] == len(expected_clause)
         and sorted(clause) == sorted(expected_clause),'exact opposite signed fixed-value clause')
    need(certificate['parent_clause_length'] == len(rows) and len(clause) <= len(rows),'parent support population')
    need(all(coefficients[variable] == 0 for variable in mapping if variable not in {row['variable'] for row in rows}),'complete zero-coefficient coverage')
    return dict(verified_clause=clause,clause_length=len(clause),parent_clause_length=len(rows),
                vector_support_size=sum(x != 0 for x in vector),quadratic_value_at_parent_graph=current,
                linear_quadratic_constant=constant,global_boolean_box_upper_bound=upper,
                checked_edge_variables=len(mapping),fixed_nonzero_variables=len(fixed),
                freed_nonzero_variables=len(rows)-len(fixed),zero_coefficient_variables=len(mapping)-len(rows),
                all_unlisted_variables_maximized=True,corner_direct_quadratic=upper,
                maximizing_corner_values=[maximizing_values[v] for v in sorted(mapping)],
                fixed_values=[dict(variable=v,value=value) for v,value in sorted(fixed.items())],
                target_cut_necessity='For all780Boolean edge assignments preserving the listed fixed values, the full principal quadratic is at most this attained negative box maximum. Any target extension must change at least one listed value.')


def controls(certificate,graph,mapping):
    need(support.product_basis((27,-9,1),(27,-9,1)) == (1701,-567,63),'target exact PSD relation')
    # Exhaustive small independent calibration of the separable box maximum.
    small_cases = 0
    for coefficients in product((-2,0,3),repeat=3):
        for mask in product((False,True),repeat=3):
            for values in product((0,1),repeat=3):
                fixed = {i:values[i] for i in range(3) if mask[i]}
                exact = max(-5+sum(c*x for c,x in zip(coefficients,bits))
                            for bits in product((0,1),repeat=3) if all(bits[i] == value for i,value in fixed.items()))
                formula = -5+sum(c*fixed[i] if i in fixed else max(0,c) for i,c in enumerate(coefficients))
                need(exact == formula,'exhaustive small-box calibration')
                small_cases += 1
    checked = audit_certificate(certificate,graph,mapping)
    rejected = []
    for name in ('wrong_bound','nonnegative_bound','wrong_constant','wrong_coefficient','wrong_gain','wrong_fixed_value',
                 'wrong_edge','missing_nonzero_coefficient','wrong_free_flag','removed_fixed_literal','wrong_literal_sign','wrong_parent_value'):
        bad = deepcopy(certificate)
        if name == 'wrong_bound': bad['global_boolean_box_upper_bound'] -= 1
        elif name == 'nonnegative_bound': bad['global_boolean_box_upper_bound'] = 0
        elif name == 'wrong_constant': bad['linear_quadratic_constant'] += 1
        elif name == 'wrong_coefficient': bad['variable_coefficients_and_free_choices'][0]['coefficient'] += 1
        elif name == 'wrong_gain': bad['variable_coefficients_and_free_choices'][0]['maximum_gain_if_freed'] += 1
        elif name == 'wrong_fixed_value': bad['variable_coefficients_and_free_choices'][0]['value_in_rejected_graph'] ^= 1
        elif name == 'wrong_edge': bad['variable_coefficients_and_free_choices'][0]['edge_full59'][0] += 1
        elif name == 'missing_nonzero_coefficient': bad['variable_coefficients_and_free_choices'].pop()
        elif name == 'wrong_free_flag': bad['variable_coefficients_and_free_choices'][0]['free'] ^= True
        elif name == 'removed_fixed_literal':
            if not bad['nogood_clause']:
                continue
            bad['nogood_clause'].pop()
            bad['nogood_clause_length'] -= 1
        elif name == 'wrong_literal_sign':
            if not bad['nogood_clause']:
                continue
            bad['nogood_clause'][0] *= -1
        else: bad['quadratic_value_at_parent_graph'] -= 1
        try:
            audit_certificate(bad,graph,mapping)
        except (ValueError,KeyError):
            rejected.append(name)
        else:
            raise ValueError('corrupt box certificate accepted: '+name)
    # Strictness at zero is mathematically essential. Calibrate an actual
    # zero upper-bound box directly, rather than just corrupting metadata.
    need(max(-1+bit for bit in (0,1)) == 0 and not(max(-1+bit for bit in (0,1)) < 0),'zero bound must not certify a cut')
    return dict(exhaustive_three_bit_boxes=small_cases,known_certificate_passed=True,
                corruption_cases_rejected=rejected,zero_boundary_not_a_cut=True),checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('graph','certificate','model','cnf','encoding-audit','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--encoding-audit-sha256',required=True)
    parser.add_argument('--expected-certificate-sha256')
    parser.add_argument('--clause',type=Path)
    parser.add_argument('--claim-id')
    args = parser.parse_args()
    need(not args.out.exists(),'refuse overwrite')
    bindings = {}
    def read(path,expected=None):
        observed = digest(path)
        need(expected is None or expected == observed,'artifact hash mismatch: '+str(path))
        bindings[key(path)] = observed
        return json.loads(Path(path).read_bytes())
    gate = read(args.encoding_audit,args.encoding_audit_sha256)
    need(gate['status'] == 'INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS','independent780edge encoding')
    authenticated = {key(ROOT/name):value for name,value in gate['inputs_sha256'].items()}
    for path in (args.model,args.cnf):
        need(digest(path) == authenticated[key(path)],'exact authenticated base model/CNF')
        bindings[key(path)] = digest(path)
    model = read(args.model)
    star = read(support.STAR)
    graph = read(args.graph)['adjacency_full59']
    graph_check = support.window.validate_candidate(graph,star,True)
    certificate = read(args.certificate,args.expected_certificate_sha256)
    need(certificate['graph_sha256'] == digest(args.graph) and certificate['encoding_model_sha256'] == digest(args.model)
         and certificate['base_cnf_sha256'] == digest(args.cnf),'certificate family/graph identity')
    mapping = support.reconstruct_mapping(model)
    for u in range(50):
        for v in range(u+1,50):
            if model['known_adjacency'][u][v] != -1:
                need(graph[u+9][v+9] == model['known_adjacency'][u][v],'fixed graph/model agreement')
    parent = read(ROOT/certificate['parent_certificate'],certificate['parent_certificate_sha256'])
    parent_audit = read(ROOT/certificate['parent_independent_audit'],certificate['parent_independent_audit_sha256'])
    need(parent_audit['status'] == 'INDEPENDENT_TARGET_GRAM_NOGOOD_PASS' and parent_audit['certificate_sha256'] == certificate['parent_certificate_sha256'],'parent support audit')
    for name,expected in parent_audit['inputs_sha256'].items():
        need(digest(ROOT/name) == expected,'parent audit input changed: '+name)
        bindings[key(ROOT/name)] = expected
    need(parent['integer_negative_vector'] == certificate['integer_negative_vector'] and parent['graph_sha256'] == certificate['graph_sha256']
         and parent['encoding_model_sha256'] == certificate['encoding_model_sha256'] and parent['base_cnf_sha256'] == certificate['base_cnf_sha256'],'same parent vector and family')
    parent_checked = support.audit_certificate(parent,graph,mapping)
    calibration,checked = controls(certificate,graph,mapping)
    need(set(checked['verified_clause']) <= set(parent_checked['verified_clause']),'new clause must be a subset of parent literals')
    if args.clause:
        values = list(map(int,args.clause.read_text(encoding='ascii').split()))
        need(values and values[-1] == 0 and values[:-1] == checked['verified_clause'],'raw box clause identity')
        bindings[key(args.clause)] = digest(args.clause)
    for path in (__file__,support.__file__,support.window.__file__,support.window.symbolic.__file__,support.window.graphcheck.__file__,ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    need(all(digest(ROOT/name) == value for name,value in bindings.items()),'stable inputs')
    report = dict(status='INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS',claim_id=args.claim_id,claim_revision=1 if args.claim_id else None,
                  claim_id_null_reason=None if args.claim_id else 'Registrar must bind this reusable result to a precise scoped claim',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='Independent checker authored by /root/eight_domain_audit; invocation provenance is the recorded command',
                  verification_type='Raw integer59quadratic at explicit Boolean maximizing corner, all780edge coefficients and independent exhaustive small-box/corruption controls',
                  checker_path=key(__file__),checker_sha256=digest(__file__),inputs_sha256=bindings,
                  encoding_audit_sha256=digest(args.encoding_audit),base_cnf_sha256=digest(args.cnf),
                  encoding_model_sha256=digest(args.model),graph_sha256=digest(args.graph),certificate_sha256=digest(args.certificate),
                  **checked,controls=calibration,raw_local_graph_check=graph_check,
                  statement='Every target extension of this exact frozen central-factor family satisfies the listed clause: fixing only its listed values makes the principal Gram quadratic strictly negative even at its exact maximum over every other Boolean edge.',
                  derivation=['The already independently derived target matrix G=27I-9A+J is positive semidefinite.',
                              'On a fixed principal graph its quadratic is c+sum(d_e*t_e), with d_e=-18*w_u*w_v.',
                              'For fixed edge-value subset F, the maximum over all remaining independent bits is c+sum_F(d_e*a_e)+sum_notF(max(0,d_e)).',
                              'This maximum is attained at the explicitly checked Boolean corner. A strictly negative maximum rules out every target completion preserving F, so their opposite-value clause is necessary.'],
                  dependencies=[dict(id='C-TARGET-GRAM-BOOLEAN-BOX-NOGOODS',revision=1,relation='uses_result'),
                                dict(id='C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING',revision=1,relation='encoding_equivalence')],
                  producer_imported=False,shared_components=['Earlier independent support Gram checker and raw59 validator','Python exact integers'],
                  limitations=['The box maximizes over a superset of locally feasible assignments, so it is safe but may be weak.',
                               'No globally shortest-clause or minimum-support assertion.',
                               'No full fixed-star, unrestricted nonexistence, target construction, or external review.',
                               'The cut is necessary for target extensions, not implied by the weaker local CNF.'],
                  recommendation='VERIFIED',target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],clause_length=checked['clause_length'],box_upper_bound=checked['global_boolean_box_upper_bound'],sha256=digest(args.out))))


if __name__ == '__main__':
    main()
