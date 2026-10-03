"""Independent literal-column counterexamples to792 uniform local mixtures."""
from pathlib import Path
from datetime import datetime, timezone
from itertools import combinations
from collections import Counter, defaultdict
from fractions import Fraction
from math import lcm
import argparse, copy, hashlib, json, sys, time, traceback

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
P = 'acceleration/results/20261001_exact_eight_uniform_gram/'
RAW = B + 'hadamard20_support/six_prism.json'
LOCAL = B + 'hadamard_triplicate_counts/local_triples.json'
MANIFEST = B + 'exact_eight_campaign_preparation/campaign_manifest.json'
GATE = B + 'independent_review/exact_eight_campaign_inventory/summary.json'
FIXTURE = B + 'srg243_residual_fixture/triangle_blocks.json'
PINS = {
    P + 'summary.json': '1b43daf9265afe524d2efb4f10ab0ee7cdf18b255bec47e8826e495db1898344',
    RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    LOCAL: '9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
    MANIFEST: 'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',
    GATE: '555ef430f8a84b8b995c98566decf2c6cb92f9e8de6db1645955c0e48dd0f9ea',
    FIXTURE: '3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
}
INPUTS = {}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    p = Path(path)
    p = p.resolve() if p.is_absolute() else (ROOT / p).resolve()
    need(p.is_relative_to(ROOT), 'contained input')
    rel = p.relative_to(ROOT).as_posix()
    need(not rel.startswith('tools/') and p.name != 'PROMPT.md'
         and not rel.endswith('hadamard_oriented_unknown/process.stdout.log'), 'protected input')
    if rel not in INPUTS:
        with p.open('rb') as stream:
            INPUTS[rel] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return INPUTS[rel]


def read(path):
    digest(path)
    return json.loads((ROOT / path).read_bytes())


def bind(pins):
    for path, expected in pins.items():
        need(digest(path) == expected, 'exact input ' + path)


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, separators=(',', ':'))
        stream.write('\n')


def target_from_core(C, n):
    need(len(C) == 3*n and all(len(row) == 3*n for row in C), 'cubic core shape')
    need(all(type(v) is int and v in (0, 1) for row in C for v in row), 'binary cubic core')
    need(all(C[i][i] == 0 and sum(C[i]) == 3 for i in range(3*n)), 'cubic hollow core')
    need(all(C[i][j] == C[j][i] for i in range(3*n) for j in range(3*n)), 'symmetric core')
    neighbors = [{j for j, value in enumerate(row) if value} for row in C]
    return [[n*int(i == j) + 2 - int(i//n == j//n) - C[i][j]
             - len(neighbors[i] & neighbors[j]) for j in range(3*n)] for i in range(3*n)]


def catalogue(checktime):
    # Placement construction, then literal contingency counts, not producer Gram sums.
    words = []
    for zeros in combinations(range(6), 2):
        for ones in combinations([i for i in range(6) if i not in zeros], 2):
            words.append(tuple(0 if i in zeros else 1 if i in ones else 2 for i in range(6)))
    words.sort()
    triples, cap_only_extra, examined = [], None, 0
    for ids in combinations(range(90), 3):
        examined += 1
        if examined % 4096 == 0:
            checktime()
        selected = [words[i] for i in ids]
        if any(sum(a == b for a, b in zip(u, v)) > 2 for u, v in combinations(selected, 2)):
            continue
        valid = True
        for a, b in combinations(range(6), 2):
            frequencies = Counter((w[a], w[b]) for w in selected)
            if any(value > (1 if f == z else 2) for (f, z), value in frequencies.items()):
                valid = False
                if cap_only_extra is None:
                    cap_only_extra = dict(word_indices=list(ids), positions=[a, b],
                                          frequencies=[[f, z, v] for (f, z), v in frequencies.items()])
                break
        if valid:
            triples.append(tuple(ids))
    classes = defaultdict(list)
    for rank, ids in enumerate(triples):
        selected = [words[i] for i in ids]
        signature = tuple(sum(w[a] == f for w in selected) for a in range(6) for f in range(3))
        classes[signature].append(rank)
    need(len(words) == 90 and examined == 117480 and len(triples) == 31110
         and len(classes) == 6061 and cap_only_extra is not None, 'complete local predicate population')
    return words, triples, classes, cap_only_extra


def gram_columns(columns, rows):
    G = [[0]*rows for _ in range(rows)]
    for column in columns:
        need(len(column) == len(set(column)) and all(type(i) is int and 0 <= i < rows for i in column),
             'literal binary column')
        for i in column:
            for j in column:
                G[i][j] += 1
    return G


def profile_domains(record, groups, classes):
    counts = record['raw_representative']['counts']
    need(len(counts) == 12 and all(len(row) == 20 and all(len(v) == 3
         and all(type(x) is int and 0 <= x <= 3 for x in v) for v in row) for row in counts),
         'strict720 integer counts')
    encoded = bytes(x for row in counts for triple in row for x in triple)
    need(len(encoded) == 720 and hashlib.sha256(encoded).hexdigest() == record['full_count_profile_sha256'],
         'literal720 profile identity')
    need(all(counts[a][g] == [0, 0, 0] for g, support in enumerate(groups)
             for a in range(12) if a not in support), 'off-support zero')
    need(all(sum(counts[a][g]) == 3 for g, support in enumerate(groups) for a in support), 'three local columns')
    need(all(sum(counts[a][g][f] for a in groups[g]) == 6 for g in range(20) for f in range(3)), 'group fibre quotas')
    need(all(sum(counts[a][g][f] for g in range(20)) == 10 for a in range(12) for f in range(3)), 'row margins')
    need(sum(any(counts[a][g] != [1, 1, 1] for a in support) for g, support in enumerate(groups)) == 8,
         'exact eight exceptional groups')
    domains = [classes[tuple(counts[a][g][f] for a in support for f in range(3))]
               for g, support in enumerate(groups)]
    need(all(domains), 'complete nonempty initial domains')
    return domains


def verify_difference(result, record, groups, words, triples, classes, G):
    need((result['case_id'], result['case_index'], result['profile_sha256'])
         == (record['case_id'], record['case_index'], record['full_count_profile_sha256']), 'exact case binding')
    domains = profile_domains(record, groups, classes)
    sizes = list(map(len, domains))
    denominator = lcm(*sizes)
    need(result['domain_sizes'] == sizes and type(result['denominator']) is int
         and result['denominator'] == denominator, 'complete sizes and denominator')
    values = result['first_difference']
    need(len(values) == 4 and all(type(v) is int for v in values), 'integer mismatch record')
    i, j, reported, expected = values
    need(0 <= i < 36 and 0 <= j < 36 and not result['exact_uniform_witness'], 'raw mismatch pair')
    mean = Fraction(0)
    parts = []
    for g, (support, ranks) in enumerate(zip(groups, domains)):
        numerator = 0
        if i % 12 in support and j % 12 in support:
            # Every contribution comes from the three actual binary columns of
            # every option; no class-Gram sum, bit-plane product or cached mean.
            for rank in ranks:
                for word_index in triples[rank]:
                    column = {12*f+a for a, f in zip(support, words[word_index])}
                    numerator += int(i in column and j in column)
        mean += Fraction(numerator, len(ranks))
        parts.append(dict(group=g, options=len(ranks), literal_incidence_sum=numerator))
    need(expected == denominator*G[i][j], 'literal target mismatch control')
    need(mean*denominator == reported and mean != G[i][j], 'direct rational nonzero difference')
    return dict(case_id=record['case_id'], case_index=record['case_index'],
                full_count_profile_sha256=record['full_count_profile_sha256'], coordinates=[i, j],
                target=G[i][j], uniform_mean=[mean.numerator, mean.denominator],
                nonzero_residual=[(mean-G[i][j]).numerator, (mean-G[i][j]).denominator],
                common_denominator=denominator, domain_sizes=sizes, literal_group_sums=parts)


def population(records, campaign):
    need(len(records) == len(campaign) == 792, 'complete792 population')
    need([r['case_id'] for r in records] == [r['case_id'] for r in campaign]
         and len({r['case_id'] for r in records}) == 792, 'unique manifest order')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    out = args.out.resolve(); need(out.is_relative_to(ROOT), 'contained output'); out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic(); checks, records_checked = [], []

    def checktime():
        need(time.monotonic()-started < 120, '120-second bounded native-free audit')

    def reject(name, fn):
        try:
            fn()
        except (ValueError, KeyError, TypeError):
            checks.append(name); return
        raise ValueError('accepted corrupt control: ' + name)

    try:
        bind(PINS)
        summary = read(P + 'summary.json'); bind(summary['inputs_sha256']); bind(summary['outputs_sha256'])
        for path in [Path(__file__), Path(__file__).with_name(Path(__file__).stem+'_spec.md')]: digest(path)
        save(out/'manifest.json', dict(created_at=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv],
            cwd=str(ROOT), inputs_sha256=INPUTS.copy(), seconds=120, native_calls=0,
            imports='Python standard library only; no producer, scientific helper or repository checker imported.'))
        raw, local, campaign, gate = read(RAW), read(LOCAL), read(MANIFEST), read(GATE)
        need(gate['status'] == 'INDEPENDENT_EXACT_EIGHT_CAMPAIGN_INVENTORY_PASS', 'authenticated inventory premise')
        C = [[int((i % 12 == j % 12 and i//12 != j//12)
              or (i//12 == j//12 and (i % 12)^1 == j % 12)) for j in range(36)] for i in range(36)]
        need(C == raw['core_adjacency'], 'literal six-prism core')
        G = target_from_core(C, 12); need(G == raw['prescribed_Gram36'], 'core-derived integer target')
        L = raw['L']; need(len(L) == 12 and all(len(row) == 60 for row in L), 'literal support shape')
        supports = [[a for a in range(12) if L[a][d]] for d in range(60)]
        need(supports == raw['support_columns'], 'support from actual matrix')
        groups = []
        for support in supports:
            if support not in groups: groups.append(support)
        need(len(groups) == 20 and supports == groups*3, 'literal20 triplicate groups')
        need(all(len(s) == 6 and all(sum(a in s for a in (m, m+1)) == 1 for m in range(0, 12, 2)) for s in groups),
             'one coordinate per matched pair')
        words, triples, classes, extra = catalogue(checktime)
        need([list(w) for w in words] == local['words'] and [list(t) for t in triples] == local['survivors'],
             'independent complete catalogue equality')
        save(out/'reconstructed_domains.json', [dict(signature=list(k), ranks=v) for k, v in sorted(classes.items())])
        # Genuine243 positive control: reconstruct and verify the entire graph.
        fixture = read(FIXTURE); F, D, A0 = fixture['factor60x180'], fixture['residual180x180'], fixture['core_adjacency63']
        A = [list(row)+[0]*180 for row in A0] + [[0]*243 for _ in range(180)]
        for i in range(60):
            for j in range(180): A[3+i][63+j] = A[63+j][3+i] = F[i][j]
        for i in range(180): A[63+i][63:] = D[i]
        need(len(A) == 243 and all(len(r) == 243 and sum(r) == 22 and all(type(v) is int and v in (0, 1) for v in r) for r in A), 'genuine243 degree')
        masks = [sum(1 << j for j, v in enumerate(row) if v) for row in A]
        need(all(A[i][i] == 0 for i in range(243)) and all(A[i][j] == A[j][i]
             and (masks[i] & masks[j]).bit_count() == (1 if A[i][j] else 2) for i, j in combinations(range(243), 2)),
             'genuine SRG243 literal adjacency identities')
        columns = [[i for i in range(60) if F[i][j]] for j in range(180)]
        actual = gram_columns(columns, 60)
        fixture_G = target_from_core(fixture['cubic_core60'], 20)
        need(actual == fixture_G, 'genuine243 core/factor Gram identity')
        duplicated = gram_columns(columns+columns, 60)
        need(all(Fraction(duplicated[i][j], 2) == fixture_G[i][j] for i in range(60) for j in range(60)), 'duplicate-choice positive mean')
        # The all-balanced relaxation is genuinely a positive uniform mean,
        # despite not being a target graph or integral factor.
        balanced = classes[(1,)*18]; need(len(balanced) == 150, 'complete150 balanced domain')
        balanced_columns = [[12*f+a for a, f in zip(s, words[w])]
                            for s in groups for rank in balanced for w in triples[rank]]
        balanced_sum = gram_columns(balanced_columns, 36)
        need(all(Fraction(balanced_sum[i][j], 150) == G[i][j] for i in range(36) for j in range(36)), 'positive balanced uniform relaxation')
        producer_controls = read(P+'controls.json')
        need(producer_controls['balanced_denominator'] == 150 and producer_controls['balanced_Gram_numerator'] == balanced_sum
             and producer_controls['balanced_group_sizes'] == [150]*20, 'saved balanced positive values')
        records = read(P+'records.json'); cases = campaign['records']; population(records, cases)
        first = verify_difference(records[0], cases[0], groups, words, triples, classes, G)
        bad = copy.deepcopy(records[0]); bad['first_difference'][2] += 1
        reject('altered literal mean', lambda: verify_difference(bad, cases[0], groups, words, triples, classes, G))
        bad = copy.deepcopy(records[0]); bad['first_difference'][3] += bad['denominator']
        reject('altered target', lambda: verify_difference(bad, cases[0], groups, words, triples, classes, G))
        bad = copy.deepcopy(records[0]); bad['denominator'] = 0
        reject('zero denominator', lambda: verify_difference(bad, cases[0], groups, words, triples, classes, G))
        bad = copy.deepcopy(cases[0]); bad['raw_representative']['counts'][0][0][0] ^= 1
        reject('altered720 count table', lambda: verify_difference(records[0], bad, groups, words, triples, classes, G))
        reject('omitted case', lambda: population(records[:-1], cases))
        bad = list(records); bad[-1] = bad[0]
        reject('duplicate case', lambda: population(bad, cases))
        reject('cap-only incomplete predicate', lambda: need(tuple(extra['word_indices']) in triples, 'local Gram bound rejects cap-only extra'))
        corrupt_target = copy.deepcopy(fixture_G); corrupt_target[0][0] += 1
        reject('corrupted genuine243 target', lambda: need(actual == corrupt_target, 'exact positive target'))
        for record, case in zip(records, cases):
            checktime(); records_checked.append(verify_difference(record, case, groups, words, triples, classes, G))
        for k in range(64, 792, 64):
            checkpoint = read(P+f'checkpoint_{k:04d}.json')
            need(checkpoint == dict(records=records[:k], completed=k, pending=792-k), 'authentic immutable progress prefix')
        need(summary['population'] == summary['completed'] == summary['uniform_failures'] == 792
             and summary['uniform_witnesses'] == 0 and summary['native_calls'] == 0, 'exact candidate scope')
        save(out/'literal_counterexamples.json', records_checked)
        save(out/'controls.json', dict(corruptions_rejected=checks, cap_only_extra=extra,
            genuine243_adjacency_entries=243*243, genuine243_Gram_entries=3600,
            balanced_mean_entries=1296, balanced_positive_is_integral_factor=False))
        now = datetime.now(timezone.utc).isoformat()
        shared = ['Python standard library only; no producer or repository scientific imports.',
                  'Pinned literal core/support/count population and prior independently verified complete-domain inventory are common inputs.',
                  'Independent word-placement and literal contingency reconstruction; each reported failure is recomputed from actual option columns with rational arithmetic.']
        limitations = ['Uniform probability1/domain_size within each of20 groups only; arbitrary convex weights and LP feasibility are UNKNOWN.',
                       'One recorded differing entry is independently checked per case; earliest lexicographic position and total differing-entry counts are not approved.',
                       'Producer class-Gram sums and other unexamined entries are authenticated as bytes only, not used as mathematical premises.',
                       'No integral-factor, residualD, whole-support or unrestricted Conway99 exclusion follows.']
        result = dict(status='INDEPENDENT_EXACT_EIGHT_UNIFORM_GRAM_FAILURES_PASS', created_at=now,
            command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256=INPUTS.copy(),
            outputs_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()},
            profiles=792, independent_nonzero_entries=792, complete_local_triples=31110,
            count_classes=6061, reconstructed_group_domains=15840, uniform_witnesses=0,
            arbitrary_convex_feasibility='UNKNOWN', native_calls=0, elapsed_seconds=time.monotonic()-started,
            shared_components=shared, limitations=limitations)
        checktime(); save(out/'summary.json', result)
        binding = dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-UNIFORM-GRAM-MIXTURE-FAILURES', revision=1,
            statement='For each of the792 literal canonical count tables in the authenticated exact-eight scalar/block survivor population, assigning uniform probability to every option in each of its20 complete initial local-triple domains yields a summed expected Gram matrix different from the prescribed integer36x36 Gram matrix.',
            kind='mathematical result', basis=['COMPUTED'], status='VERIFIED', review_state='CLEAR',
            scope='Exactly the pinned792 count tables and uniform groupwise local-option distributions; no assertion about existence of other convex weights.',
            assumptions=['Fixed literal six-prism Hadamard support, prescribed Gram, and the complete local-triple predicate including local Gram upper bounds and within-triplicate caps.'],
            dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS', revision=1, relation='premise'),
                dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS', revision=1, relation='verification_dependency'),
                dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-DOMAIN-INVENTORY', revision=1, relation='uses_result'),
                dict(id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL', revision=1, relation='verification_dependency')],
            verifier='/root/state_literature_audit', producer='/root',
            method='Reconstruct all local triples and literal count domains, then compute one rational nonzero Gram residual per case directly from every local incidence column; independently verify genuine243 and complete balanced-uniform controls.',
            shared_components=shared, limitations=limitations, created_at=now, updated_at=now,
            independent_report=dict(path=(out/'summary.json').relative_to(ROOT).as_posix(), sha256=hashlib.sha256((out/'summary.json').read_bytes()).hexdigest()),
            inputs_sha256=INPUTS.copy(), artifact_availability='LOCAL_ONLY', availability_reason='Immutable public publication not yet confirmed.')
        save(out/'claim_binding.json', binding)
        print(json.dumps(dict(status=result['status'], profiles=792, checked_nonzero_residuals=792, elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as ex:
        save(out/'failure.json', dict(error=repr(ex), traceback=traceback.format_exc(), inputs_sha256=INPUTS,
                                     completed_profiles=len(records_checked), controls_rejected=checks))
        raise


if __name__ == '__main__': main()
