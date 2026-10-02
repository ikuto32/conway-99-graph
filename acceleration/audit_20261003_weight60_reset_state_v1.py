"""Independent dense integer check of one explicit graph-only V2 reset.

No reset producer, native graph implementation, or prior state parser imported.
The serialized V2 format and the native splitmix seed specification are shared.
"""
import argparse
import copy
import hashlib
import itertools
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
MASK = (1 << 64) - 1
SCALARS = ('n degree seed mix_steps schedule_steps t_start t_end forced step '
           'admissible accepted best_updates weighted_energy base_energy '
           'lambda_energy mu_energy best_weighted_energy best_base_energy '
           'best_lambda_energy best_mu_energy').split()
RESET = dict(seed=99032061, mix_steps=0, schedule_steps=80000000,
             t_start=8.0, t_end=0.1, forced=0, step=0, admissible=0,
             accepted=0, best_updates=0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def seeded(seed):
    values = []
    for _ in range(4):
        seed = (seed + 0x9e3779b97f4a7c15) & MASK
        value = ((seed ^ (seed >> 30)) * 0xbf58476d1ce4e5b9) & MASK
        value = ((value ^ (value >> 27)) * 0x94d049bb133111eb) & MASK
        values.append(value ^ (value >> 31))
    return values


def graph(n, degree, triples, deadline):
    need(n in (9, 12, 99) and degree == (7 if n == 99 else 2), 'graph domain')
    need(len(triples) * 3 == n * degree, 'triple population')
    counts = [0] * n
    matrix = [[0] * n for _ in range(n)]
    for triple in triples:
        need(len(triple) == 3 and len(set(triple)) == 3 and
             all(type(v) is int and 0 <= v < n for v in triple), 'triple labels')
        for v in triple:
            counts[v] += 1
        for u, v in itertools.combinations(triple, 2):
            need(matrix[u][v] == 0, 'linear incidence')
            matrix[u][v] = matrix[v][u] = 1
    need(counts == [degree] * n, 'point degrees')
    cn = []
    el = em = mismatches = 0
    for u in range(n):
        need(deadline.status()['remaining_seconds'] > 5, 'shutdown reserve')
        for v in range(n):
            product = sum(matrix[u][w] * matrix[w][v] for w in range(n))
            rhs = ((2 * degree - 2) if u == v else 0) - matrix[u][v] + 2
            mismatches += product != rhs
            if u < v:
                cn.append(product)
                cost = (product - (1 if matrix[u][v] else 2)) ** 2
                if matrix[u][v]:
                    el += cost
                else:
                    em += cost
    return dict(matrix=matrix, cn=cn, lambda_energy=el, mu_energy=em,
                base_energy=el + em, weighted_energy=60 * el + em,
                identity_mismatches=mismatches)


def parse(raw):
    tokens = iter(raw.decode('ascii').split())
    need(next(tokens) == 'HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2', 'state version')
    data = {}
    for tag, value in (('objective', 'SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2'),
                       ('lambda_weight', '60'),
                       ('move_kernel', 'LINEAR_TRIPLE_EXCLUSIVE_SWAP_V2')):
        need(next(tokens) == tag and next(tokens) == value, 'state objective/kernel')
    for tag in SCALARS:
        need(next(tokens) == tag, 'scalar field order')
        data[tag] = float(next(tokens)) if tag in ('t_start', 't_end') else int(next(tokens))
    for tag in ('rng', 'current', 'best', 'cn'):
        need(next(tokens) == tag, 'array field order')
        size = 4 if tag == 'rng' else int(next(tokens))
        need(0 <= size <= 10000, 'bounded field population')
        data[tag] = ([int(next(tokens)) for _ in range(size)] if tag in ('rng', 'cn')
                     else [[int(next(tokens)) for _ in range(3)] for _ in range(size)])
    need(next(tokens) == 'first_lambda0', 'snapshot flag')
    data['first_lambda0'] = int(next(tokens))
    need(data['first_lambda0'] in (0, 1), 'binary snapshot flag')
    if data['first_lambda0']:
        for tag in ('first_step', 'first_admissible', 'first_accepted', 'first_best_updates'):
            need(next(tokens) == tag, 'snapshot counters order')
            data[tag] = int(next(tokens))
        need(next(tokens) == 'first_rng', 'snapshot RNG order')
        data['first_rng'] = [int(next(tokens)) for _ in range(4)]
        for tag in ('first_current', 'first_best'):
            need(next(tokens) == tag, 'snapshot graph order')
            size = int(next(tokens))
            need(0 <= size <= 10000, 'bounded snapshot population')
            data[tag] = [[int(next(tokens)) for _ in range(3)] for _ in range(size)]
    need(next(tokens) == 'END' and next(tokens, None) is None, 'complete exact record')
    return data


def check(data, deadline, reset=False, source=None):
    n, degree = data['n'], data['degree']
    objects = {name: graph(n, degree, data[name], deadline)
               for name in ('current', 'best')}
    need(data['cn'] == objects['current']['cn'], 'complete CN cache')
    for tag in ('lambda_energy', 'mu_energy', 'base_energy', 'weighted_energy'):
        need(data[tag] == objects['current'][tag] and
             data['best_' + tag] == objects['best'][tag], 'exact graph components')
    need(0 <= data['best_updates'] <= data['accepted'] <= data['admissible'] <= data['step']
         and data['best_weighted_energy'] <= data['weighted_energy'], 'ordered main counters')
    need(0 <= data['seed'] <= MASK and all(0 <= v <= MASK for v in data['rng'])
         and any(data['rng']), 'unsigned nonzero RNG')
    if data['first_lambda0']:
        first = {name: graph(n, degree, data['first_' + name], deadline)
                 for name in ('current', 'best')}
        need(first['current']['lambda_energy'] == 0 and
             first['best']['weighted_energy'] <= first['current']['weighted_energy'], 'snapshot graph scores')
        need(0 <= data['first_best_updates'] <= data['first_accepted'] <=
             data['first_admissible'] <= data['first_step'] <= data['step'], 'snapshot counters')
        need(all(data['first_' + tag] <= data[tag] for tag in ('admissible', 'accepted', 'best_updates')),
             'snapshot within current counters')
        need(all(0 <= v <= MASK for v in data['first_rng']) and any(data['first_rng']), 'snapshot RNG')
    need(objects['current']['lambda_energy'] != 0 or data['first_lambda0'], 'lambda0 snapshot completeness')
    if reset:
        need(all(data[tag] == value for tag, value in RESET.items()), 'reset configuration/counters')
        need(data['rng'] == seeded(RESET['seed']), 'exact reset seed expansion')
        need(data['current'] == data['best'] and data['current'] == source['current'], 'graph-only ordered import')
        need(data['first_lambda0'] == (objects['current']['lambda_energy'] == 0), 'initial reset snapshot flag')
        if data['first_lambda0']:
            need(all(data[tag] == 0 for tag in ('first_step', 'first_admissible', 'first_accepted', 'first_best_updates'))
                 and data['first_rng'] == data['rng'] and data['first_current'] == data['current']
                 and data['first_best'] == data['best'], 'exact step-zero snapshot')
    return objects


def calibration(deadline):
    triples = [[3 * r + c for c in range(3)] for r in range(3)]
    triples += [[3 * r + c for r in range(3)] for c in range(3)]
    g = graph(9, 2, triples, deadline)
    need(g['identity_mismatches'] == g['weighted_energy'] == 0, 'known-valid rook SRG')
    data = dict(n=9, degree=2, **RESET, rng=seeded(RESET['seed']), current=triples,
                best=copy.deepcopy(triples), cn=g['cn'], first_lambda0=1,
                first_step=0, first_admissible=0, first_accepted=0, first_best_updates=0,
                first_rng=seeded(RESET['seed']), first_current=copy.deepcopy(triples), first_best=copy.deepcopy(triples))
    for tag in ('lambda_energy', 'mu_energy', 'base_energy', 'weighted_energy'):
        data[tag] = data['best_' + tag] = g[tag]
    check(data, deadline, True, data)
    lines = ['HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2', 'objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2',
             'lambda_weight 60', 'move_kernel LINEAR_TRIPLE_EXCLUSIVE_SWAP_V2']
    lines += [f'{tag} {data[tag]}' for tag in SCALARS]
    lines.append('rng ' + ' '.join(map(str, data['rng'])))
    for tag in ('current', 'best'):
        lines.append(f'{tag} {len(data[tag])}')
        lines.extend(' '.join(map(str, row)) for row in data[tag])
    lines.append(f"cn {len(data['cn'])}")
    lines.extend(map(str, data['cn']))
    lines.append('first_lambda0 1')
    lines.extend(f'{tag} 0' for tag in ('first_step','first_admissible','first_accepted','first_best_updates'))
    lines.append('first_rng ' + ' '.join(map(str, data['first_rng'])))
    for tag in ('first_current', 'first_best'):
        lines.append(f'{tag} {len(data[tag])}')
        lines.extend(' '.join(map(str, row)) for row in data[tag])
    raw = ('\n'.join(lines) + '\nEND\n').encode('ascii')
    need(parse(raw) == data, 'known-valid serialized fixture')
    syntax_controls = [raw + b'extra\n', raw.replace(b'END\n', b''),
                       raw.replace(b'HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2', b'V1'),
                       raw.replace(b'lambda_weight 60', b'lambda_weight 6')]
    for bad in syntax_controls:
        try:
            parse(bad)
        except (ValueError, StopIteration, UnicodeError):
            continue
        raise ValueError('corrupt serialized fixture accepted')
    changes = [lambda x:x['rng'].__setitem__(0,x['rng'][0]^1), lambda x:x.update(seed=99032060),
               lambda x:x.update(step=1), lambda x:x.update(t_start=60), lambda x:x.update(mix_steps=1),
               lambda x:x.update(schedule_steps=1), lambda x:x['cn'].__setitem__(0,x['cn'][0]+1),
               lambda x:x['current'][0].__setitem__(0,x['current'][0][1]),
               lambda x:x.update(weighted_energy=1), lambda x:x.update(first_lambda0=0),
               lambda x:x['first_rng'].__setitem__(0,x['first_rng'][0]^1)]
    for change in changes:
        bad = copy.deepcopy(data)
        change(bad)
        try:
            check(bad, deadline, True, data)
        except (ValueError, IndexError):
            continue
        raise ValueError('corrupt reset accepted')
    return dict(known_valid='srg(9,4,1,2) rook graph, all81 scalar entries',
                positive_controls=2, strict_negative_controls=len(changes) + len(syntax_controls), producer_output_inspected=False,
                limitation='Finite controls cover dense fixture objects and strict complete serialized records; not a general parser proof.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=('calibrate', 'check'))
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    for tag in ('source_state', 'reset_state', 'producer_report', 'calibration'):
        ap.add_argument('--' + tag.replace('_', '-'), type=Path)
        ap.add_argument('--' + tag.replace('_', '-') + '-sha256')
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent dense V2 graph-only reset check;120outer100worker5internalreserve, no search')
    args.out.mkdir(parents=True, exist_ok=False)
    inputs = {Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
              'acceleration/command_deadline.py':sha(ROOT/'acceleration/command_deadline.py')}
    def read(tag):
        path = getattr(args, tag).resolve()
        expected = getattr(args, tag + '_sha256')
        need(path.is_relative_to(ROOT) and sha(path) == expected, 'pinned input ' + tag)
        inputs[path.relative_to(ROOT).as_posix()] = expected
        return path.read_bytes()
    report = dict(timestamp=datetime.now(timezone.utc).isoformat(), verifier='/root',
                  command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
                  source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  inputs_sha256=inputs, target_resolution='NONE',
                  shared_components=['V2 serialized format and native splitmix seed specification; Python integer runtime and command deadline. No producer imports.'])
    if args.mode == 'calibrate':
        report.update(status='INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_CALIBRATION_V1_PASS', controls=calibration(deadline))
    else:
        calibrated = json.loads(read('calibration'))
        need(calibrated['status'] == 'INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_CALIBRATION_V1_PASS'
             and calibrated['inputs_sha256'][Path(__file__).relative_to(ROOT).as_posix()] == inputs[Path(__file__).relative_to(ROOT).as_posix()], 'same frozen calibrated checker')
        source = parse(read('source_state'))
        reset = parse(read('reset_state'))
        producer = json.loads(read('producer_report'))
        check(source, deadline)
        objects = check(reset, deadline, True, source)
        report.update(status='INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_V1_PASS', producer='/root/native_driver',
                      controls=calibrated['controls'], complete_reset_scalar_entries=4 * reset['n']**2,
                      parameters=RESET, graphs_preserved=['current','best','first_current','first_best'],
                      lambda_energy=objects['current']['lambda_energy'], mu_energy=objects['current']['mu_energy'],
                      identity_mismatches=objects['current']['identity_mismatches'],
                      producer_status_recorded=producer.get('status'),
                      limitations=['One exact derivative; graph-only seed/config reset, not RNG trajectory continuation.',
                                   'No discovery, general exclusion, trajectory completeness, or performance claim.'])
    report['deadline'] = deadline.status()
    with (args.out/'summary.json').open('x', encoding='utf8', newline='\n') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status':report['status'], 'report_sha256':sha(args.out/'summary.json')}))


if __name__ == '__main__':
    main()
