"""Independent exact complete assignment, channel, factor and required Y-cap checker."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gzip
import io
import json
import platform
import subprocess
import sys
import time
import audit_20260930_prism_first_choice_object as prior

base = prior.base
ROOT = base.ROOT
D = ROOT/'acceleration/results/20260930_prism_column_caps_v3'
GATE = ROOT/'acceleration/results/20260930_independent_review/prism_column_caps/summary.json'
GATE_SHA = '5c137eb4b497433d02d99e7b1105c34e06f679b55cd5cbe722b8f265d3f47edf'
PRIOR_CAL = ROOT/'acceleration/results/20260930_independent_review/prism_first_choice_object_calibration/summary.json'
PRIOR_CAL_SHA = '17927bfbc8355b37f45b42c2bcc9e8ed80b3a5c0f2454da8231a9c72a16d3db2'
PRIOR_SOURCE_SHA = 'f4a53b6dac7ed2f59de6216a31f76c532ea96fb63a9dc5f4356c53dc8892f886'
VARIABLES, CLAUSES, BASE_VARIABLES = 247320, 920401, 245880
need, digest, key, read, save = base.need, base.digest, base.key, base.read, base.save


def bind_inputs():
    need(digest(prior.__file__) == PRIOR_SOURCE_SHA, 'frozen independent first-choice wrapper')
    model, derived, bindings = prior.bind_inputs()
    for p, h, status in [(GATE, GATE_SHA, 'INDEPENDENT_SIX_PRISM_COLUMN_CAP_EXTENSION_PASS'),
            (PRIOR_CAL, PRIOR_CAL_SHA, 'INDEPENDENT_SIX_PRISM_FIRST_CHOICE_OBJECT_CALIBRATION_PASS')]:
        need(digest(p) == h, 'exact independent gate identity')
        gate = read(p); need(gate['status'] == status, 'exact independent gate status')
        bindings.update(gate['inputs_sha256']); bindings[key(p)] = h
    extension = read(D/'model.json')
    need(extension['variables'] == VARIABLES and extension['clauses'] == CLAUSES, 'exact augmented dimensions')
    need(extension['outside_column_caps_encoded'] is True and extension['residual_D_encoded'] is False and extension['target_graph_encoded'] is False, 'factor plus required caps only')
    expected = [(245881+(r-12)*60+d, r, d) for r in range(12, 36) for d in range(60)]
    need([(v['id'], v['row'], v['column']) for v in extension['incidence_variables']] == expected, 'all channel IDs and coordinates')
    bindings[key(__file__)] = digest(__file__)
    for p, h in bindings.items(): need(digest(ROOT/p) == h, 'exact bound input '+p)
    return model, extension, derived, bindings


def project(values):
    need(len(values) == VARIABLES+1, 'full augmented assignment dimension')
    return values[:BASE_VARIABLES+1]


def channel_check(values, factor):
    need(len(factor) == 36 and all(len(row) == 60 and all(type(x) is int and x in (0, 1) for x in row) for row in factor), 'strict literal channel factor')
    need(len(values) == VARIABLES+1, 'channel assignment dimension')
    for row in range(12, 36):
        for column in range(60):
            need(values[245881+(row-12)*60+column] == factor[row][column], 'raw factor and channel equality')
    return dict(exact_channel_values_checked=1440, forced_zero_channels_checked=480)


def cap_check(factor):
    need(len(factor) == 36 and all(len(row) == 60 and all(type(x) is int and x in (0, 1) for x in row) for row in factor), 'strict literal cap factor')
    overlaps = []
    for d in range(60):
        for e in range(d+1, 60):
            count = sum(factor[r][d]*factor[r][e] for r in range(36))
            need(count <= 2, 'required raw distinct-column cap violated')
            overlaps.append(count)
    return dict(required=True, column_pairs_checked=1770, maximum_overlap=max(overlaps), overlap_histogram={str(k): overlaps.count(k) for k in range(3)})


def raw_check(factor, gram, c0, components):
    # The reused base checker treats caps as diagnostic. This wrapper explicitly requires them.
    exact = base.raw_check(factor, gram, c0, components)
    return dict(exact_Gram_and_margins=exact['exact_Gram_and_margins'], exact_components=exact['exact_components'], required_column_caps=cap_check(factor))


def native_agreement(values, stream):
    parsed, result = base.native.native_values(stream, VARIABLES)
    need(parsed == values, 'every native and parsed assignment value agrees')
    return result


def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(), inputs_sha256=bindings,
        verifier='/root/structural_attack independent cap-extension object checker', producer_imports=False,
        shared_components=['Frozen independent first-choice decoder/raw six-prism Gram/margin/component validator.',
            'Frozen independent complete native/JSON and clause parsers.', 'New channel equality and mandatory literal Y-column caps.'],
        limitations=['No complete positive research36 factor is known; calibration paths are explicitly separated.',
            'Only the fixed six-prism core is encoded; no arbitrary-core exclusion or residual completion.', 'A factor is not a 99-vertex graph.'],
        target_resolution=False, external_review=False, artifact_availability='LOCAL_ONLY')


def calibrate(args):
    args.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    model, extension, derived, bindings = bind_inputs(); core, gram, columns, c0, components, grouped = derived
    factor = base.balanced_control(columns)
    own_gram = [[sum(x*y for x, y in zip(a, b)) for b in factor] for a in factor]
    generic_factor = base.raw_check(factor, own_gram, c0, components)
    need(own_gram != gram, 'generic fixture is explicitly not a research factor')
    selected = [next(c['id'] for c in choices if c['rows'] == [r for r in range(36) if factor[r][d]]) for d, choices in enumerate(grouped)]
    chosen = set(selected)
    signed = [i if i in chosen else -i for i in range(1, BASE_VARIABLES+1)]
    signed += [245881+(r-12)*60+d if factor[r][d] else -(245881+(r-12)*60+d) for r in range(12, 36) for d in range(60)]
    values = base.common.assignment_values(signed, VARIABLES)
    decoded, selection = prior.decode(project(values), grouped)
    need(decoded == factor and selection == selected, 'independent projected raw choice decode')
    channels = channel_check(values, factor)
    # These are genuine positive cap-only fixtures, not Gram-factor fixtures.
    cap_only = [[int(r in pair) for pair in columns] for r in range(12)]+[[0]*60 for _ in range(24)]
    cap_positive = cap_check(cap_only)
    boundary = [[0]*60 for _ in range(36)]
    for r in range(2): boundary[r][0] = boundary[r][1] = 1
    need(cap_check(boundary)['maximum_overlap'] == 2, 'exact cap boundary positive')
    positive = list(range(1, VARIABLES+1)); fullvalues = base.common.assignment_values(positive, VARIABLES)
    stdout = b'c SYNTHETIC full-size codec; not research SAT\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str, positive[i:i+100]))+(' 0' if i+100 >= VARIABLES else '')+'\n').encode() for i in range(0, VARIABLES, 100))
    native = native_agreement(fullvalues, io.BytesIO(stdout))
    cnf = f'p cnf {VARIABLES} {CLAUSES}\n'.encode()+b''.join((str(i % VARIABLES+1)+' 0\n').encode() for i in range(CLAUSES))
    cnf_result = base.common.check_cnf_stream(io.BytesIO(cnf), fullvalues, VARIABLES, CLAUSES)
    for name, data in [('synthetic_native.stdout.gz', stdout), ('synthetic_fullsize.cnf.gz', cnf)]:
        with gzip.open(args.out/name, 'wb') as stream: stream.write(data)
    save(args.out/'synthetic_generic_factor_channel_control.json', dict(factor=factor, own_gram=own_gram, selected_choice_ids=selected,
        assignment=signed, research_CNF_assignment=False, research_Gram_factor=False, label='Own-Gram factor plus exact normalized primary/channels; base auxiliaries are not research-SAT values.'))
    save(args.out/'synthetic_cap_controls.json', dict(canonical_C0_only=cap_only, exact_boundary=boundary, complete_Gram_factors=False))
    rejected = []
    def reject(label, fn):
        try: fn()
        except (ValueError, KeyError, IndexError, TypeError): rejected.append(label)
        else: raise ValueError('corrupted control accepted '+label)
    for label, var in [('empty_support_channel', 245881), ('positive_channel', next(i for i in range(245881, VARIABLES+1) if values[i]))]:
        bad = values[:]; bad[var] ^= 1
        reject(label, lambda bad=bad: channel_check(bad, factor))
    flipped = 0
    for var in range(245881, VARIABLES+1):
        bad = values[:]; bad[var] ^= 1
        try: channel_check(bad, factor)
        except ValueError: flipped += 1
        else: raise ValueError('one flipped channel accepted')
    need(flipped == 1440, 'every incidence channel is tested')
    bad = values[:]; bad[1] = 0; reject('normalized_choice_false', lambda: prior.decode(project(bad), grouped))
    bad = values[:]; bad[grouped[0][1]['id']] = 1; reject('two_choices_one_column', lambda: prior.decode(project(bad), grouped))
    bad = values[:]; bad[selected[1]] = 0; reject('no_choice_one_column', lambda: prior.decode(project(bad), grouped))
    reject('generic_own_Gram_against_research', lambda: raw_check(factor, gram, c0, components))
    badf = deepcopy(factor); badf[12][0] ^= 1; reject('changed_raw_factor', lambda: base.raw_check(badf, own_gram, c0, components))
    badf = deepcopy(factor); badf[0][0] = bool(badf[0][0]); reject('Boolean_raw_entry', lambda: channel_check(values, badf))
    reject('partial_factor_dimension', lambda: cap_check(factor[:24]))
    badcap = deepcopy(boundary); badcap[2][0] = badcap[2][1] = 1
    reject('isolated_cap_three_is_fatal', lambda: cap_check(badcap))
    reject('missing_assignment', lambda: base.common.assignment_values(positive[:-1], VARIABLES))
    reject('duplicate_assignment', lambda: base.common.assignment_values([1]+positive[:-1], VARIABLES))
    reject('out_of_range_assignment', lambda: base.common.assignment_values(positive[:-1]+[VARIABLES+1], VARIABLES))
    bad = fullvalues[:]; bad[-1] = 0; reject('native_JSON_mismatch_last_channel', lambda: native_agreement(bad, io.BytesIO(stdout)))
    for label, data in [('missing_native_zero', stdout.replace(b'247320 0\n', b'247320\n')), ('duplicate_native_ID', stdout.replace(b'v 1 2 ', b'v 1 1 ', 1)),
            ('missing_native_ID', stdout.replace(b'v 1 2 ', b'v 2 ', 1)), ('wrong_native_status', stdout.replace(b's SATISFIABLE', b's UNSATISFIABLE'))]:
        reject(label, lambda data=data: native_agreement(fullvalues, io.BytesIO(data)))
    for label, data in [('missing_clause', cnf[:cnf.rfind(b'\n', 0, -1)+1]), ('wrong_header', cnf.replace(b'920401', b'920400', 1)),
            ('false_literal', cnf.replace(b'1 0\n', b'-1 0\n', 1)), ('bad_literal', cnf.replace(b'1 0\n', b'247321 0\n', 1))]:
        reject(label, lambda data=data: base.common.check_cnf_stream(io.BytesIO(data), fullvalues, VARIABLES, CLAUSES))
    need(all(digest(ROOT/p) == h for p, h in bindings.items()), 'stable inputs')
    report = {**provenance(bindings), 'status':'INDEPENDENT_SIX_PRISM_COLUMN_CAP_OBJECT_CHECKER_CALIBRATION_PASS',
        'variables':VARIABLES, 'clauses':CLAUSES, 'encoding_gate_sha256':GATE_SHA, 'prior_calibration_sha256':PRIOR_CAL_SHA,
        'generic_factor_with_own_Gram':generic_factor, 'exact_primary_and_channel_control':channels,
        'separate_cap_positive':cap_positive, 'fullsize_codec':dict(native=native, cnf=cnf_result, research_SAT=False),
        'all_flipped_channels_rejected':flipped, 'fresh_corruptions_rejected':rejected,
        'positive_research_factor':None, 'positive_research_factor_null_reason':'No complete research36 positive is known. Generic factor, channels, caps and full-size codec are calibrated separately.',
        'outputs_sha256':{key(p):digest(p) for p in args.out.iterdir() if p.is_file()}, 'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json', report); print(json.dumps(dict(status=report['status'], sha256=digest(args.out/'summary.json'))))


def sat(args):
    args.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    model, extension, derived, bindings = bind_inputs(); core, gram, columns, c0, components, grouped = derived
    values = base.common.assignment_values(read(args.assignment)['assignment'], VARIABLES)
    with args.native_output.open('rb') as stream: native = native_agreement(values, stream)
    with (D/'instance.cnf').open('rb') as stream: cnf = base.common.check_cnf_stream(stream, values, VARIABLES, CLAUSES)
    projected = project(values)
    with (prior.D/'instance.cnf').open('rb') as stream: base_cnf = base.common.check_cnf_stream(stream, projected, BASE_VARIABLES, 874801)
    factor, selected = prior.decode(projected, grouped)
    channels = channel_check(values, factor); exact = raw_check(factor, gram, c0, components)
    if args.decoded:
        obj = read(args.decoded)
        need(obj['factor'] == factor and obj['selected_choice_ids'] == selected and obj['target_graph'] is False, 'independent raw decode agrees')
    save(args.out/'independent_factor.json', dict(factor=factor, selected_choice_ids=selected, core_adjacency=core, target_gram=gram,
        components=components, exact_checks=exact, exact_channels=channels, target_graph=False, encoding_model_sha256=digest(D/'model.json')))
    for p in [args.assignment, args.native_output]+([args.decoded] if args.decoded else []): bindings[key(p)] = digest(p)
    need(all(digest(ROOT/p) == h for p, h in bindings.items()), 'stable inputs')
    report = {**provenance(bindings), 'status':'INDEPENDENT_SIX_PRISM_COLUMN_CAP_FACTOR_OBJECT_PASS',
        'native_assignment':native, 'all_raw_augmented_clauses':cnf, 'all_projected_normalized_base_clauses':base_cnf,
        'exact_channels':channels, **exact, 'independent_factor_sha256':digest(args.out/'independent_factor.json'), 'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json', report); print(json.dumps(dict(status=report['status'], sha256=digest(args.out/'summary.json'))))


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('calibrate'); p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('sat'); p.add_argument('--out', type=Path, required=True); p.add_argument('--assignment', type=Path, required=True)
    p.add_argument('--native-output', type=Path, required=True); p.add_argument('--decoded', type=Path)
    args = ap.parse_args()
    try: (calibrate if args.mode == 'calibrate' else sat)(args)
    except BaseException as error:
        if args.out.exists() and not (args.out/'failure.json').exists(): save(args.out/'failure.json', dict(status='CHECK_FAILED', error=repr(error)))
        raise


if __name__ == '__main__': main()
