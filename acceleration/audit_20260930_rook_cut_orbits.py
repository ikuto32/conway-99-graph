"""Independent signed-clause transport and full finite orbit artifact checker.

No discovery code imported. Exact integer coefficients and matrix permutations
are reconstructed from the raw fixed/free model. The separately checked degree
optimization certificate is an explicitly pinned premise, not recomputed here.
"""
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT/'acceleration/results/20260930_rook_cut_orbits01'
OUT = ROOT/'acceleration/results/20260930_independent_review/rook_cut_orbits'
REVIEW = ROOT/'acceleration/results/20260930_independent_review'
MODEL = ROOT/'acceleration/results/20260930_rook_free_internal_sat/model.json'
BASE = MODEL.with_name('instance.cnf')
MAP_GATE_SHA = '897188e21828d946149dbeee503c1fd61b6946197810a11970b92f2a6bf1b282'
DEGREE_SHA = '8030415e025dd175aaba62879acf72dcffdf08076c435efe023a0e3935c9552d'
bindings = {}


def need(test, message):
    if not test:
        raise ValueError(message)


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def pin(path, expected=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT/path
    name = key(path)
    observed = bindings.setdefault(name, digest(path))
    need(expected is None or observed == expected, 'hash mismatch: '+name)
    return path


def read(path, expected=None):
    return json.loads(pin(path, expected).read_bytes())


def dependencies(report):
    for name, expected in report['inputs_sha256'].items():
        pin(name, expected)


def canonical(clause, n=780):
    need(type(clause) in (tuple, list) and len(clause) > 0, 'nonempty clause')
    need(all(type(x) is int and 1 <= abs(x) <= n for x in clause), 'literal type/range')
    need(len({abs(x) for x in clause}) == len(clause), 'duplicate variable')
    return tuple(sorted(clause, key=lambda x: (abs(x), x)))


def image(clause, variable_map):
    need(sorted(variable_map) == list(range(1, len(variable_map)+1)), 'variable permutation')
    return canonical([variable_map[abs(x)-1] * (1 if x > 0 else -1) for x in clause], len(variable_map))


def specification(model):
    pairs = list(itertools.combinations(range(10, 50), 2))
    need(model['edge_variables'] == [dict(u=u, v=v, id=i+1) for i, (u,v) in enumerate(pairs)], 'canonical780edge coverage')
    edges = [(u+9, v+9) for u,v in pairs]
    matrix = [[0]*59 for _ in range(59)]
    for i,j in itertools.combinations(range(9), 2):
        matrix[i][j] = matrix[j][i] = int(i//3 == j//3 or i%3 == j%3)
    for a in range(50):
        r,c = model['cell_rook_coordinates'][a//10]
        matrix[3*r+c][a+9] = matrix[a+9][3*r+c] = 1
        for b in range(50):
            matrix[a+9][b+9] = model['known_adjacency'][a][b]
    need(all(matrix[i][i] == 0 for i in range(59)), 'zero diagonal')
    need(all(matrix[i][j] == matrix[j][i] and matrix[i][j] in (-1,0,1) for i in range(59) for j in range(59)), 'symmetric specification')
    need({(i,j) for i,j in itertools.combinations(range(59),2) if matrix[i][j] == -1} == set(edges), 'all and only free pairs')
    return matrix, edges


def coefficients(w, matrix, edges):
    need(len(w) == 59 and all(type(x) is int for x in w), 'integer59vector')
    const = sum(w)**2 + 27*sum(x*x for x in w)
    const -= 18*sum(w[i]*w[j] for i,j in itertools.combinations(range(59),2) if matrix[i][j] == 1)
    return const, [-18*w[i]*w[j] for i,j in edges]


def box_bound(const, weights, clause):
    canonical(clause, len(weights))
    fixed = {abs(lit):int(lit < 0) for lit in clause}
    return const + sum(c*fixed[j] if j in fixed else max(0,c) for j,c in enumerate(weights,1))


def population(sources, maps, actual_images, unique):
    expected, origins = {}, {}
    for source in sources:
        for index, mapping in enumerate(maps):
            token = (source['id'],index)
            clause = image(source['clause'],mapping)
            expected[token] = clause
            origins.setdefault(clause,set()).add(token)
    need(len(actual_images) == len(expected), 'attempt population size')
    actual = {}
    for row in actual_images:
        token = (row['source_id'],row['map_index'])
        need(token not in actual and token in expected, 'duplicate/unknown attempt')
        actual[token] = row['unique_clause_id']
    need(set(actual) == set(expected), 'full Cartesian attempt coverage')
    need([r['id'] for r in unique] == list(range(len(unique))), 'unique IDs')
    tuples = [canonical(r['clause']) for r in unique]
    need(len(set(tuples)) == len(tuples) and set(tuples) == set(origins), 'exact unique clause set')
    for token, clause in expected.items():
        need(0 <= actual[token] < len(unique) and tuples[actual[token]] == clause, 'signed literal image differs')
    for row,clause in zip(unique,tuples):
        supplied = [(r['source_id'],r['map_index']) for r in row['origins']]
        need(len(supplied) == len(set(supplied)) and set(supplied) == origins[clause], 'origin population')
        need(list(clause) == row['clause'], 'canonical order')
    return tuples


def controls():
    # A genuine 3-cycle distinguishes image from inverse, unlike involutions.
    need(image([1,-2],[2,3,1]) == (2,-3), 'known 3-cycle forward action')
    need(image([1,-2],[3,1,2]) == (-1,3), 'known inverse action')
    need(box_bound(2,[3,-7],[1,-2]) == -5, 'known negative box')
    sources = [dict(id='s',clause=[1,-2])]
    maps = [[1,2,3],[2,3,1]]
    attempts = [dict(source_id='s',map_index=i,unique_clause_id=i) for i in range(2)]
    unique = [dict(id=i,clause=list(image([1,-2],m)),origins=[dict(source_id='s',map_index=i)]) for i,m in enumerate(maps)]
    need(len(population(sources,maps,attempts,unique)) == 2, 'positive finite orbit')
    cases = []
    def reject(name, operation):
        try:
            operation()
        except (ValueError,KeyError,IndexError):
            cases.append(name)
        else:
            raise ValueError('corruption accepted: '+name)
    reject('duplicate_variable',lambda: canonical([1,-1]))
    reject('nonpermutation_map',lambda: image([1],[1,1]))
    reject('missing_attempt',lambda: population(sources,maps,attempts[:1],unique))
    reject('duplicate_attempt',lambda: population(sources,maps,[attempts[0]]*2,unique))
    for name, field in [('wrong_sign',0),('inverse_instead_of_image',1)]:
        bad = copy.deepcopy(unique)
        bad[1]['clause'] = [2,3] if field == 0 else [-1,3]
        reject(name,lambda: population(sources,maps,attempts,bad))
    reject('missing_unique_clause',lambda: population(sources,maps,attempts,unique[:1]))
    bad = copy.deepcopy(unique); bad[1]['origins'] = []
    reject('missing_origin',lambda: population(sources,maps,attempts,bad))
    return dict(known_three_cycle_and_inverse_distinguished=True,known_negative_box=-5,positive_orbit=True,corruptions_rejected=cases)


def main():
    calibration = controls()
    manifest = read(RUN/'manifest.json'); dependencies(manifest)
    summary = read(RUN/'summary.json')
    for name,expected in summary['output_sha256'].items():
        pin(RUN/name,expected)
    model = read(MODEL)
    matrix, edges = specification(model)
    model_hash, base_hash = digest(MODEL), digest(BASE)
    map_gate = read(REVIEW/'rook_scaffold_relabelings32.json',MAP_GATE_SHA); dependencies(map_gate)
    need(map_gate['status'] == 'INDEPENDENT_ROOK_SCAFFOLD_RELABELINGS32_PASS','map gate')
    transport = read(REVIEW/'scaffold_cut_transport_lemma.json'); dependencies(transport)
    need(transport['status'] == 'INDEPENDENT_FIXED_SCAFFOLD_CUT_TRANSPORT_LEMMA_PASS','transport lemma gate')
    maps_raw = read(ROOT/'acceleration/results/20260930_rook_scaffold_relabeling/accepted_relabelings.json',map_gate['raw_maps_sha256'])['maps']
    need(len(maps_raw) == 32 == len(map_gate['checked_maps']), '32 maps')
    lookup = {pair:j+1 for j,pair in enumerate(edges)}
    degree_set = {(tuple(sorted(row['variables'])),row['value']) for row in model['degree_constraints']}
    need(len(degree_set) == 160, '160 distinct degree constraints')
    variable_maps = []
    for index,raw in enumerate(maps_raw):
        p = raw['full59']
        need(sorted(p) == list(range(59)), 'vertex permutation')
        need(all(matrix[i][j] == matrix[p[i]][p[j]] for i in range(59) for j in range(59)), 'fixed/free specification invariant')
        vm = [lookup[tuple(sorted((p[i],p[j])))] for i,j in edges]
        need(vm == raw['edge_variable_map'] == map_gate['checked_maps'][index]['edge_variable_map'], 'endpoint-to-variable image convention')
        need(p == map_gate['checked_maps'][index]['full59'], 'raw permutation gate binding')
        need({(tuple(sorted(vm[j-1] for j in row['variables'])),row['value']) for row in model['degree_constraints']} == degree_set, 'degree system bijection')
        variable_maps.append(vm)
    need(len({tuple(x) for x in variable_maps}) == 32, '32 distinct maps')
    sources = read(RUN/'source_clauses.json')
    need([s['id'] for s in sources] == ['box_%02d'%i for i in range(10)]+['degree_12'], '11 exact source IDs')
    checkpoint = read(ROOT/'acceleration/results/20260930_rook_box_lazy_wave02/final_checkpoint.json')
    need([{k:s[k] for k in ('certificate','certificate_sha256','audit','audit_sha256','clause')} for s in sources[:10]] == checkpoint['ordered_cuts'], 'all ten approved source box clauses')
    degree_gate = read(REVIEW/'degree_block_gram/summary.json',DEGREE_SHA); dependencies(degree_gate)
    need(degree_gate['status'] == 'INDEPENDENT_DEGREE_BLOCK_GRAM_BOUND_AND_CUT_PASS', 'independent degree proof gate')
    source_checks = []
    transport_checks = []
    for source in sources:
        cert = read(source['certificate'],source['certificate_sha256'])
        audit = read(source['audit'],source['audit_sha256']); dependencies(audit)
        need(source['clause'] == cert['nogood_clause'] == list(canonical(source['clause'])), 'exact source clause')
        need(cert['encoding_model_sha256'] == model_hash and cert['base_cnf_sha256'] == base_hash, 'source family binding')
        w = cert['integer_negative_vector']
        const, weights = coefficients(w,matrix,edges)
        need(const == cert['linear_quadratic_constant'], 'raw source constant')
        if source['kind'] == 'BOOLEAN_BOX':
            need(audit['status'] == 'INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS' and audit['certificate_sha256'] == source['certificate_sha256'], 'source independent box approval')
            need(audit['verified_clause'] == source['clause'], 'box approval exact clause')
            upper = box_bound(const,weights,source['clause'])
            need(upper == cert['global_boolean_box_upper_bound'] == audit['global_boolean_box_upper_bound'] and upper < 0, 'fresh exact independent box maximum')
        else:
            need(source['kind'] == 'DEGREE_BLOCK' and audit['status'] == 'INDEPENDENT_DEGREE_BLOCK12_CUT_BINDING_PASS' and audit['review_state'] == 'CLEAR', 'degree source approval')
            need(degree_gate['cut_package_sha256'] == source['certificate_sha256'] and degree_gate['final_clause'] == source['clause'], 'degree exact package/clause')
            upper = degree_gate['exact_final_upper']
            need(upper == cert['exact_degree_relaxation_maximum'] < 0, 'negative independently checked degree maximum')
        source_checks.append(dict(source_id=source['id'],certificate_sha256=source['certificate_sha256'],audit_sha256=source['audit_sha256'],exact_upper=upper,fresh_box_maximum_recomputed=source['kind']=='BOOLEAN_BOX'))
        for index,(raw,vm) in enumerate(zip(maps_raw,variable_maps)):
            pushed = [0]*59
            for i,v in enumerate(w):
                pushed[raw['full59'][i]] = v
            newconst,newweights = coefficients(pushed,matrix,edges)
            need(newconst == const and all(newweights[vm[j]-1] == weights[j] for j in range(780)), 'exact pushforward polynomial')
            clause = image(source['clause'],vm)
            if source['kind'] == 'BOOLEAN_BOX':
                need(box_bound(newconst,newweights,clause) == upper, 'transported exact Boolean maximum')
            transport_checks.append(dict(source_id=source['id'],map_index=index,exact_upper=upper,all780_coefficients_checked=True,constant_checked=True))
    images = read(RUN/'images.json'); unique = read(RUN/'unique_clauses.json')
    tuples = population(sources,variable_maps,images,unique)
    expected_bytes = ''.join(' '.join(map(str,c))+' 0\n' for c in tuples).encode('ascii')
    need((RUN/'clauses.cnfpart').read_bytes() == expected_bytes, 'exact ordered DIMACS bytes')
    counts = dict(source_clauses=len(sources),maps=len(variable_maps),transport_attempts=len(images),unique_clauses=len(tuples),duplicate_images=len(images)-len(tuples))
    need(all(summary[name] == value for name,value in counts.items()), 'reported counts')
    pin(__file__); pin(ROOT/'uv.lock')
    need(all(digest(ROOT/name) == value for name,value in bindings.items()), 'inputs stable')
    report = dict(status='INDEPENDENT_ROOK_GRAM_CUT_ORBITS_PASS',claim_id='C-ROOK-GRAM-CUT-ORBITS-352',claim_revision=1,
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/state_literature_audit independent checking agent',verification_type='Exact independently reconstructed matrix/edge permutations, fresh Boolean-box maxima, pinned independent degree maximum, all signed Cartesian images and exact DIMACS bytes',
        inputs_sha256=bindings,**counts,source_checks=source_checks,transport_checks=transport_checks,
        base_cnf_sha256=base_hash,encoding_model_sha256=model_hash,clauses_path=key(RUN/'clauses.cnfpart'),clauses_sha256=digest(RUN/'clauses.cnfpart'),
        unique_clauses_path=key(RUN/'unique_clauses.json'),unique_clauses_sha256=digest(RUN/'unique_clauses.json'),
        map_fixed_free_entries_checked=32*59*59,variable_images_checked=32*780,degree_row_images_checked=32*160,
        transported_coefficients_checked=352*780,controls=calibration,
        statement='Every target extension of the exact pinned780edge scaffold satisfies all352 distinct clauses obtained from the exact11 source clauses under all32 supplied checked specification-preserving permutations.',
        scope='Conditional target-extension necessities in one frozen central-factor family; no target automorphism assumption, SAT conclusion, full-family exclusion or unrestricted resolution.',
        derivation=['For arbitrary target extension A and old-to-new permutation p, B[i,j]=A[p(i),p(j)] is another target extension of the same specification.',
                    'Applying the source clause to B gives its same-sign forward edge-image clause on A; no assertion A=B is made.',
                    'Pushing a vector by w_new[p(i)]=w_old[i] preserves the constant and maps every coefficient c_j to c_image(j).',
                    'The degree equation system is permuted bijectively, so its exact maximum is unchanged by the transported fixed pattern.'],
        dependencies=[dict(id='C-FIXED-SCAFFOLD-RELABELING-CUT-TRANSPORT',revision=1,relation='uses_result'),
                      dict(id='C-ROOK-FOUR-FACTOR-SCAFFOLD-RELABELINGS32',revision=1,relation='normalization'),
                      dict(id='C-ROOK-DEGREE-BLOCK-GRAM-CUT-12',revision=1,relation='uses_result')],
        producer_imported=False,shared_components=['Python exact integers and standard library','Pinned independently authored source gates; degree optimization proof is reused, not rerun'],
        limitations=['No exhaustive census of all possible scaffold maps or valid cuts.','Distinct clauses are not disjoint excluded assignment sets. No graph union size or target-wide coverage is claimed.','Degree optimization uses the fully checked prior raw certificate as a pinned premise.'],
        recommendation='VERIFIED',review_state='CLEAR',target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],**counts,sha256=digest(OUT/'summary.json'))))


if __name__ == '__main__':
    main()
