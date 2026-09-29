"""Independent raw99 affine-Gram/Boolean-box cut checker; no producer imports.

The exact full99 encoding gate authenticates the family. This checker recomputes
the entire variable polynomial by changing individual raw matrix entries and
checks an explicit maximizing corner by the literal ordered quadratic sum.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENCODING = ROOT/'acceleration/results/20260930_independent_review/eight_full99_cnf/summary.json'
ENCODING_SHA = 'ecd4adb354a0c8c03589b1446ab511014ea47c7b5bf9ff1d529d34a2d1c79667'
BOX_LEMMA = ROOT/'acceleration/results/20260930_independent_review/target_gram_boolean_box_lemma.json'
BOX_LEMMA_SHA = '72f8dd8a34fdb8dfaef3722fce173e0061c9c21a0b21ef7da7dc979d1668e6b1'
PSD_LEMMA = ROOT/'acceleration/results/20260930_independent_review/target_gram_support_lemma.json'
PSD_LEMMA_SHA = 'e194ca054dfe0596ae2b9ff1070ef59289c7c0401497a63c77eb62e217bd1ac6'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    result = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            result.update(block)
    return result.hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def exact_int(value):
    return type(value) is int


def matrix_ok(graph, n, allowed):
    need(len(graph) == n and all(len(row) == n for row in graph), 'matrix shape')
    need(all(exact_int(x) and x in allowed for row in graph for x in row), 'matrix integer alphabet')
    need(all(graph[u][u] == 0 for u in range(n)), 'zero diagonal')
    need(all(graph[u][v] == graph[v][u] for u,v in combinations(range(n),2)), 'matrix symmetry')


def quadratic(graph, vector):
    return sum(vector[u]*(27*int(u == v)-9*graph[u][v]+1)*vector[v]
               for u in range(len(vector)) for v in range(len(vector)))


def prepare(model, raw):
    known = model['known_adjacency_full99']
    matrix_ok(known,99,(-1,0,1))
    unknown = {(u,v) for u,v in combinations(range(99),2) if known[u][v] == -1}
    mapping = {}
    for row in model['edge_variables']:
        u,v,variable = row['u'],row['v'],row['id']
        need(all(exact_int(x) for x in (u,v,variable)) and (u,v) in unknown, 'mapped free edge')
        need(variable not in mapping, 'duplicate variable')
        mapping[variable] = (u,v)
    need(set(mapping) == set(range(1,2161)) and set(mapping.values()) == unknown and len(unknown) == 2160,
         'complete 2160-variable bijection')
    small = raw['adjacency_full29']
    matrix_ok(small,29,(0,1))
    vertices = raw['full99_vertex_map']
    need(len(vertices) == len(set(vertices)) == 29 and all(exact_int(v) and 0 <= v < 99 for v in vertices), 'raw29 vertex map')
    values = raw['integer_negative_vector']
    need(len(values) == 29 and all(exact_int(v) for v in values), 'raw29 integer vector')
    vector = [0]*99
    position = {v:i for i,v in enumerate(vertices)}
    for i,v in enumerate(vertices):
        vector[v] = values[i]
    for i,j in combinations(range(29),2):
        value = known[vertices[i]][vertices[j]]
        need(value == -1 or value == small[i][j], 'raw29 fixed-family agreement')
    baseline = [[0 if x == -1 else x for x in row] for row in known]
    constant = quadratic(baseline,vector)
    coefficients = {}
    pattern = {}
    for variable,(u,v) in mapping.items():
        # Difference of the two affected ordered matrix summands. No producer
        # edge-expansion function or producer coefficient table is used.
        coefficients[variable] = (vector[u]*(-9)*vector[v] + vector[v]*(-9)*vector[u])
        pattern[variable] = small[position[u]][position[v]] if u in position and v in position else None
        need(pattern[variable] is not None or coefficients[variable] == 0, 'outside-pattern coefficient zero')
    raw_q = quadratic(small,values)
    need(exact_int(raw['quadratic']) and raw_q == raw['quadratic'] < 0, 'raw29 exact negativity')
    completed = [row.copy() for row in baseline]
    for variable,(u,v) in mapping.items():
        completed[u][v] = completed[v][u] = pattern[variable] or 0
    need(quadratic(completed,vector) == raw_q == constant+sum(coefficients[v]*(pattern[v] or 0) for v in mapping),
         'zero-extension and affine expansion')
    return dict(known=known,mapping=mapping,vector=vector,baseline=baseline,constant=constant,
                coefficients=coefficients,pattern=pattern,raw_q=raw_q,vertices=vertices)


def validate(certificate, corner, prepared):
    data = prepared
    vector,mapping = data['vector'],data['mapping']
    need(certificate['schema'] == 'FULL99_TARGET_GRAM_BOOLEAN_BOX_NOGOOD_V1' and certificate['matrix'] == '27I-9A+J', 'definition')
    need(certificate['integer_vector_full99'] == vector and all(exact_int(x) for x in certificate['integer_vector_full99']), 'full99 vector')
    need(certificate['raw29_vertex_map'] == data['vertices'], 'certificate raw map')
    need(exact_int(certificate['affine_constant']) and certificate['affine_constant'] == data['constant'], 'constant')
    need(exact_int(certificate['raw_pattern_quadratic']) and certificate['raw_pattern_quadratic'] == data['raw_q'], 'raw quadratic')
    clause = certificate['nogood_clause']
    need(all(exact_int(x) and x != 0 and abs(x) in mapping for x in clause), 'literal alphabet')
    need(len(clause) == len(set(abs(x) for x in clause)), 'distinct clause variables')
    fixed = {abs(literal): int(literal < 0) for literal in clause}
    need(all(data['pattern'][v] == bit for v,bit in fixed.items()), 'raw pattern falsifies clause')
    coefficients = data['coefficients']
    support = [-v if data['pattern'][v] else v for v in sorted(mapping) if coefficients[v]]
    need(certificate['support_nogood_clause'] == support, 'complete support clause')
    rows = certificate['all2160variable_coefficients']
    need(len(rows) == 2160, '2160 coefficient rows')
    seen = set()
    corner_values = {}
    for row in rows:
        variable = row['variable']
        need(exact_int(variable) and variable in mapping and variable not in seen, 'coefficient-row bijection')
        seen.add(variable)
        coefficient = coefficients[variable]
        pattern = data['pattern'][variable]
        need(row['edge_full99'] == list(mapping[variable]) and all(exact_int(x) for x in row['edge_full99']), 'coefficient edge mapping')
        need(exact_int(row['coefficient']) and row['coefficient'] == coefficient, 'coefficient value')
        need(row['raw_pattern_value'] == pattern and (pattern is None or exact_int(row['raw_pattern_value'])), 'raw bit')
        need((row['raw_pattern_value_null_reason'] is None) == (pattern is not None), 'raw null reason')
        if pattern is None:
            need(isinstance(row['raw_pattern_value_null_reason'],str) and row['raw_pattern_value_null_reason'], 'missing raw null reason')
        need(type(row['free']) is bool and row['free'] == (variable not in fixed), 'free flag')
        need(row['fixed_value'] == fixed.get(variable) and (variable not in fixed or exact_int(row['fixed_value'])), 'fixed bit')
        need((row['fixed_value_null_reason'] is None) == (variable in fixed), 'fixed null reason')
        if variable not in fixed:
            need(isinstance(row['fixed_value_null_reason'],str) and row['fixed_value_null_reason'], 'missing fixed null reason')
        current = pattern or 0
        gain = max(coefficient*0,coefficient*1)-coefficient*current
        need(exact_int(row['maximum_gain_if_freed']) and row['maximum_gain_if_freed'] == gain, 'freeing gain')
        best = fixed[variable] if variable in fixed else (1 if coefficient > 0 else 0)
        need(exact_int(row['maximizing_corner_value']) and row['maximizing_corner_value'] == best, 'row maximizing bit')
        corner_values[variable] = best
    need(seen == set(mapping), 'all variables covered')
    upper = data['constant']+sum(coefficients[v]*fixed[v] if v in fixed else max(coefficients[v]*bit for bit in (0,1)) for v in mapping)
    need(exact_int(certificate['global_boolean_box_upper_bound']) and certificate['global_boolean_box_upper_bound'] == upper < 0,
         'strict negative complete Boolean maximum')
    expected = [row.copy() for row in data['baseline']]
    for variable,(u,v) in mapping.items():
        expected[u][v] = expected[v][u] = corner_values[variable]
    matrix_ok(corner['adjacency_full99'],99,(0,1))
    need(corner['adjacency_full99'] == expected, 'complete maximizing matrix')
    need(corner['all2160edge_values'] == [corner_values[v] for v in range(1,2161)] and all(exact_int(x) for x in corner['all2160edge_values']), 'complete maximizing assignment')
    need(corner['integer_vector_full99'] == vector and all(exact_int(x) for x in corner['integer_vector_full99']), 'corner vector')
    literal_q = quadratic(expected,vector)
    need(exact_int(corner['exact_quadratic']) and corner['exact_quadratic'] == literal_q == upper, 'literal 99x99 corner quadratic')
    need(corner['satisfies_full_SRG_or_family_degrees'] is None and isinstance(corner['satisfies_full_SRG_or_family_degrees_null_reason'],str), 'no feasibility claim for box corner')
    return dict(affine_constant=data['constant'],raw_pattern_quadratic=data['raw_q'],
                exact_boolean_box_upper_bound=upper,maximizing_corner_quadratic=literal_q,
                full99_vector_nonzeros=sum(bool(x) for x in vector),coefficient_rows=2160,
                nonzero_coefficients=sum(bool(x) for x in coefficients.values()),
                support_clause_length=len(support),verified_clause=clause,clause_length=len(clause),
                independently_free_variables=2160-len(fixed),raw_pattern_falsifies_clause=True,
                complete_fixed_and_free_edge_coverage=True,literal_quadratic_ordered_terms=99*99)


def controls(certificate,corner,prepared):
    # Exhaust every ternary fixed/free mask, bit assignment and small coefficient
    # triple; calculate both by literal corner enumeration and separable maxima.
    cases = 0
    for coefficients in product((-2,0,3),repeat=3):
        for specification in product((None,0,1),repeat=3):
            corners = [values for values in product((0,1),repeat=3)
                       if all(bit is None or values[i] == bit for i,bit in enumerate(specification))]
            exact = max(7+sum(c*b for c,b in zip(coefficients,values)) for values in corners)
            proposed = 7+sum(c*bit if bit is not None else max(0,c) for c,bit in zip(coefficients,specification))
            need(exact == proposed,'known exhaustive Boolean box')
            cases += 1
    checked = validate(certificate,corner,prepared)
    rejected = []
    fixed_index = next(i for i,row in enumerate(certificate['all2160variable_coefficients']) if not row['free'])
    nonzero_index = next(i for i,row in enumerate(certificate['all2160variable_coefficients']) if row['coefficient'])
    labels = ('vector','constant','coefficient','missing_variable','edge_map','raw_bit','free_flag','fixed_value',
              'maximizing_row_bit','gain','upper_bound','zero_bound','clause_sign','clause_missing',
              'corner_bit','corner_vector','corner_quadratic','raw_map','support_clause')
    for label in labels:
        bad,wrong_corner = deepcopy(certificate),deepcopy(corner)
        rows = bad['all2160variable_coefficients']
        if label == 'vector': bad['integer_vector_full99'][0] += 1
        elif label == 'constant': bad['affine_constant'] += 1
        elif label == 'coefficient': rows[nonzero_index]['coefficient'] += 1
        elif label == 'missing_variable': rows.pop()
        elif label == 'edge_map': rows[fixed_index]['edge_full99'][0] += 1
        elif label == 'raw_bit': rows[fixed_index]['raw_pattern_value'] ^= 1
        elif label == 'free_flag': rows[fixed_index]['free'] = True
        elif label == 'fixed_value': rows[fixed_index]['fixed_value'] ^= 1
        elif label == 'maximizing_row_bit': rows[fixed_index]['maximizing_corner_value'] ^= 1
        elif label == 'gain': rows[fixed_index]['maximum_gain_if_freed'] += 1
        elif label == 'upper_bound': bad['global_boolean_box_upper_bound'] += 1
        elif label == 'zero_bound': bad['global_boolean_box_upper_bound'] = 0
        elif label == 'clause_sign': bad['nogood_clause'][0] *= -1
        elif label == 'clause_missing': bad['nogood_clause'].pop()
        elif label == 'corner_bit':
            u,v = rows[fixed_index]['edge_full99']
            wrong_corner['adjacency_full99'][u][v] ^= 1
            wrong_corner['adjacency_full99'][v][u] ^= 1
        elif label == 'corner_vector': wrong_corner['integer_vector_full99'][0] += 1
        elif label == 'corner_quadratic': wrong_corner['exact_quadratic'] += 1
        elif label == 'raw_map': bad['raw29_vertex_map'][0] += 1
        else: bad['support_nogood_clause'].pop()
        try:
            validate(bad,wrong_corner,prepared)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError('corruption accepted: '+label)
    return dict(exhaustive_three_variable_boxes=cases,positive_certificate_passed=True,
                deliberately_corrupted_certificates_rejected=rejected),checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path,required=True)
    parser.add_argument('--expected-certificate-sha256',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    need(not args.out.exists(),'refuse overwrite')
    bindings = {}
    def bind(path,expected=None):
        path = Path(path)
        if not path.is_absolute(): path = ROOT/path
        actual = digest(path)
        need(expected is None or actual == expected,'input hash: '+key(path))
        bindings[key(path)] = actual
        return path
    def read(path,expected=None):
        return json.loads(bind(path,expected).read_bytes())
    certificate = read(args.certificate,args.expected_certificate_sha256)
    encoding = read(ENCODING,ENCODING_SHA)
    need(encoding['status'] == 'INDEPENDENT_EIGHT_FULL99_CNF_ENCODING_PASS','encoding gate status')
    lemma = read(BOX_LEMMA,BOX_LEMMA_SHA)
    need(lemma['status'] == 'INDEPENDENT_TARGET_GRAM_BOOLEAN_BOX_LEMMA_PASS','box lemma gate')
    psd = read(PSD_LEMMA,PSD_LEMMA_SHA)
    need(psd['status'] == 'INDEPENDENT_TARGET_GRAM_PSD_SUPPORT_LEMMA_PASS','PSD lemma gate')
    for lemma_report in (lemma,psd):
        if lemma_report.get('written_audit'):
            bind(lemma_report['written_audit'],lemma_report['inputs_sha256'][lemma_report['written_audit']])
    model_path = certificate['encoding_model']
    cnf_path = certificate['base_cnf']
    need(encoding['inputs_sha256'][model_path] == certificate['encoding_model_sha256'] and
         encoding['inputs_sha256'][cnf_path] == certificate['base_cnf_sha256'],'exact encoding identities')
    model = read(model_path,certificate['encoding_model_sha256'])
    bind(cnf_path,certificate['base_cnf_sha256'])
    raw_artifact = read(certificate['raw_artifact'],certificate['raw_artifact_sha256'])
    prior = read(certificate['prior_specific_graph_audit'],certificate['prior_specific_graph_audit_sha256'])
    need(prior['status'] == 'INDEPENDENT_TWO_SPECIFIC_CLOSED29_GRAM_OBSTRUCTIONS_PASS' and
         prior['inputs_sha256'][certificate['raw_artifact']] == certificate['raw_artifact_sha256'],'independent raw29 gate')
    raw = raw_artifact['records'][certificate['raw_record_index']]
    corner = read(certificate['maximizing_corner_path'],certificate['maximizing_corner_sha256'])
    prepared = prepare(model,raw)
    calibration,checked = controls(certificate,corner,prepared)
    clause_path = args.certificate.parent/'nogood.clause'
    tokens = bind(clause_path).read_text(encoding='ascii').split()
    need(list(map(int,tokens)) == checked['verified_clause']+[0],'raw clause bytes semantic identity')
    clarification = args.certificate.parent/'SCOPE_CLARIFICATION.md'
    bind(clarification)
    for path in (__file__,ROOT/'uv.lock',ROOT/'pyproject.toml'):
        bind(path)
    need(all(digest(ROOT/path) == value for path,value in bindings.items()),'input stability at completion')
    report = dict(status='INDEPENDENT_FULL99_GRAM_BOOLEAN_BOX_NOGOOD_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/eight_domain_audit, separate checker author from this cut producer',
        verification_type='Independent artifact checking with a literal 99x99 integer quadratic and complete Boolean coefficient coverage',
        claim_id='C-PARTIAL-K-EIGHT-FULL99-W81-GRAM-BOX-NOGOOD',claim_revision=1,
        recommendation='VERIFIED',kind='mathematical result',basis=['DERIVED','COMPUTED'],
        statement='Every satisfying assignment of the exact recorded full99 eight-coordinate-family CNF satisfies the recorded 44-literal clause. For any Boolean completion of its fixed adjacency entries falsifying that clause, the recorded integer vector has quadratic at most -5868 for 27I-9A+J.',
        scope='One explicit clause within the exact frozen 120-fixed-K/2160-free-edge full99 family; a redundant strengthening of its exact CNF, with no additional graph assumptions.',
        assumptions=['The raw model and base CNF retain the authenticated bytes and the independent encoding-equivalence claim.',
                     'For target interpretation, A is symmetric binary99x99, zero diagonal, satisfying A^2=12I-A+2J.'],
        dependencies=[dict(id='C-TARGET-GRAM-BOOLEAN-BOX-NOGOODS',revision=1,relation='uses_result'),
                      dict(id='C-PARTIAL-K-EIGHT-COORDINATE-FULL99-SAT-ENCODING',revision=1,relation='encoding_equivalence'),
                      dict(id='C-CLOSED29-TWO-SPECIFIC-GRAM-OBSTRUCTIONS',revision=1,relation='derived_from')],
        inputs_sha256=bindings,checker_path=key(__file__),checker_sha256=digest(__file__),
        certificate_sha256=digest(args.certificate),encoding_model_sha256=digest(ROOT/model_path),
        base_cnf_sha256=digest(ROOT/cnf_path),maximizing_corner_sha256=digest(ROOT/certificate['maximizing_corner_path']),
        clause_sha256=digest(clause_path),controls=calibration,**checked,
        proof=['The target diagonal identity gives degree14, so AJ=JA=14J; direct expansion gives G^2=63G for G=27I-9A+J. Hence x^TGx=||Gx||^2/63>=0.',
               'The full known/free matrix is authenticated by the independent exact encoding gate. Setting each free edge to zero gives the independently calculated affine constant.',
               'Each free unordered edge changes exactly two ordered quadratic terms; all2160 such coefficients are checked, including every zero coefficient.',
               'Falsifying the recorded clause fixes its44 values. Each remaining independent Boolean edge is maximized separately; their complete box maximum is -5868, witnessed by the explicit raw99 corner.',
               'Thus no target in this family can falsify the clause. Because the independently audited full99 CNF is equivalent to target graphs in that family, the clause is also entailed by that CNF.'],
        scope_correction=dict(original_certificate_prose_incorrect=True,clarification_path=key(clarification),
             correction='The original wording about a weaker CNF is incorrect for this exact full99 encoding; the numerical certificate is unchanged and its clause is logically redundant.'),
        producer_imported=False,shared_components=['Python standard library exact integers and JSON parser',
            'Previously independently audited and hash-bound exact family/CNF and universal Gram lemma; those prior audits are reused, not rerun here',
            'The raw29 discovery was authored by this verifier, then separately checked by structural_attack; this cut was produced by structural_attack and is independently checked here'],
        limitations=['No claim of minimum clause length or greedy selection optimality.',
                     'The maximizing Boolean corner need not satisfy graph degrees or the CNF; the box is an intentional superset.',
                     'No exclusion of the whole fixed family, closed28 graph, star, or unrestricted target.',
                     'This invocation does not mutate a CNF or run a solver, nor does it replay the prior full CNF audit.'],
        solver_calls=0,cnf_modified=False,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],clause_length=checked['clause_length'],upper_bound=checked['exact_boolean_box_upper_bound'],sha256=digest(args.out))))


if __name__ == '__main__':
    main()
