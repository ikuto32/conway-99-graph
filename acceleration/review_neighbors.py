"""Independently enumerate and validate every two-edge-trade neighbor on controls.

No generator is imported. The optional temporary Rust harness calls the frozen
wide walk's actual legal_trades function for a second native set comparison.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import time

from audit_certificate import full_graph, require

ROOT = Path(__file__).resolve().parents[1]
LABELS = [(a, b) for a, b in combinations(range(14), 2) if a//2 != b//2]
LABELS.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair))
SUPPORTS = [{s//2 for s in pair} for pair in LABELS]


def signature(edges):
    return tuple(sorted(tuple(pair) for pair in edges))


def independent_neighbors(known):
    adjacency, _ = full_graph({'overlap_edges_outer_zero_based': [list(e) for e in sorted(known)]})
    answers = set()
    examined = 0
    for first, second in combinations(sorted(known), 2):
        if len(set(first+second)) != 4:
            continue
        a, b = first
        c, d = second
        removed = {first, second}
        for matching in (((a, c), (b, d)), ((a, d), (b, c))):
            added = {tuple(sorted(edge)) for edge in matching}
            if added & known or any(len(SUPPORTS[u] & SUPPORTS[v]) != 1 for u, v in added):
                continue
            examined += 1
            changed = {u+15 for u in first+second}
            replacement = {u: adjacency[u].copy() for u in changed}
            for u, v in removed:
                replacement[u+15].remove(v+15)
                replacement[v+15].remove(u+15)
            for u, v in added:
                replacement[u+15].add(v+15)
                replacement[v+15].add(u+15)
            valid = True
            for u in changed:
                for v in range(99):
                    if u == v:
                        continue
                    row_v = replacement[v] if v in replacement else adjacency[v]
                    if len(replacement[u] & row_v) > (1 if v in replacement[u] else 2):
                        valid = False
                        break
                if not valid:
                    break
            if valid:
                answers.add(signature((known-removed)|added))
    return answers, examined


def quota_check(edges):
    adjacency, _ = full_graph({'overlap_edges_outer_zero_based': [list(e) for e in edges]})
    for u in range(84):
        counts = Counter(s for v in adjacency[u+15] if v >= 15 for s in LABELS[v-15])
        for symbol in range(14):
            require(counts[symbol] == 1 if symbol//2 in SUPPORTS[u] else counts[symbol] <= 2,
                    'Generated neighbor violates root-label quota')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'acceleration/results/20260916_neighbors_review.json')
    parser.add_argument('--generator', type=Path, default=ROOT/'acceleration/build/overlap_neighbors.exe')
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior review')
    started = time.perf_counter()
    paths = [ROOT/'scratch_resume_overlap_lift.json'] + [
        ROOT/f'scratch_next_overlap_alternatives_r{i}.json' for i in range(4)] + [ROOT/'scratch_follow_overlap_walk.json']
    controls = [(p.name, json.loads(p.read_bytes())['overlap_edges_outer_zero_based']) for p in paths]
    wide_path = ROOT/'acceleration/results/20260916_wide_walk_2000.json'
    wide = json.loads(wide_path.read_bytes())
    controls += [(f'wide_snapshot_{index}', wide['overlap_candidates'][index]) for index in (15, 37, 100)]
    records = []
    generator_source = ROOT/'acceleration/overlap_neighbors.rs'
    original_generator_hash = sha256(generator_source.read_bytes()).hexdigest()
    wide_source = ROOT/'acceleration/overlap_wide_walk.rs'
    with TemporaryDirectory(prefix='neighbors-review-', dir=args.out.parent) as temporary:
        temporary = Path(temporary)
        harness = temporary/'wide_trade_harness.rs'
        source = wide_source.read_text(encoding='utf-8')
        require(source.count('\nfn main() {') == 1, 'Cannot safely isolate wide-walk entry point')
        # Exact existing function bodies are preserved; only main is renamed.
        harness.write_text(source.replace('\nfn main() {', '\nfn unused_original_main() {') + '''
fn main() {
    let args:Vec<_> = std::env::args().collect();
    let geometry = Geometry::new();
    let graphs = load_candidates(&args[1], &geometry).unwrap();
    let graph = &graphs[0];
    let (_, trades) = legal_trades(graph, &geometry);
    let mut out = String::from("[");
    for (i, trade) in trades.iter().enumerate() {
        if i > 0 { out.push(','); }
        let mut edges:Vec<_> = graph.edges.iter().copied().filter(|e| !trade.removed.contains(e)).collect();
        edges.extend(trade.added);
        edges.sort_unstable();
        append_edges(&mut out, &edges);
    }
    out.push(']');
    fs::write(&args[2], out).unwrap();
}
''', encoding='utf-8')
        harness_exe = temporary/'wide_trade_harness.exe'
        build = subprocess.run(['rustc', '-O', '-A', 'dead_code', str(harness), '-o', str(harness_exe)],
                               text=True, capture_output=True)
        require(build.returncode == 0, f'Could not build comparison harness: {build.stderr}')
        for control_index, (name, listed) in enumerate(controls):
            known = set(map(tuple, listed))
            reference, examined = independent_neighbors(known)
            native_input = temporary/f'input_{control_index}.txt'
            native_input.write_text('C99OVERLAPS1 1\n'+' '.join(str(v) for e in sorted(known) for v in e)+'\n', encoding='ascii')
            all_output = temporary/f'neighbors_{control_index}.json'
            subprocess.run([str(args.generator), str(native_input), str(all_output)], check=True, capture_output=True)
            data = json.loads(all_output.read_bytes())
            candidates = data['overlap_candidates']
            native_set = {signature(edges) for edges in candidates}
            require(len(native_set) == len(candidates) == len(data['trades']) == data['legal_trades'],
                    'Duplicate candidates or incorrect native total')
            require(native_set == reference, 'Native neighbors differ from independent complete enumeration')
            for listed_neighbor, trade in zip(candidates, data['trades']):
                removed, added = map(lambda rows: set(map(tuple, rows)), (trade['removed'], trade['added']))
                require(len(removed) == len(added) == 2 and removed <= known and not added & known,
                        'Invalid trade record')
                require(signature((known-removed)|added) == signature(listed_neighbor), 'Trade and candidate disagree')
                quota_check(signature(listed_neighbor))
            wide_output = temporary/f'wide_neighbors_{control_index}.json'
            subprocess.run([str(harness_exe), str(native_input), str(wide_output)], check=True, capture_output=True)
            wide_candidates = json.loads(wide_output.read_bytes())
            require({signature(edges) for edges in wide_candidates} == native_set
                    and len(wide_candidates) == len(native_set), 'Frozen wide legal_trades set differs')
            sampling = []
            for limit, seed in ((1, 0), (7, 17), (len(native_set)+1, 99)):
                sample_path = temporary/f'sample_{control_index}_{limit}.json'
                subprocess.run([str(args.generator), str(native_input), str(sample_path), str(limit), str(seed)],
                               check=True, capture_output=True)
                sample = json.loads(sample_path.read_bytes())
                sampled_set = {signature(edges) for edges in sample['overlap_candidates']}
                require(len(sampled_set) == len(sample['overlap_candidates']) == min(limit, len(native_set))
                        and sampled_set <= native_set and sample['legal_trades'] == len(native_set),
                        'Invalid reservoir sample membership/count')
                sampling.append({'limit': limit, 'seed': seed, 'returned': len(sampled_set)})
            repeat_path = temporary/f'repeat_{control_index}.json'
            subprocess.run([str(args.generator), str(native_input), str(repeat_path), '7', '17'],
                           check=True, capture_output=True)
            first_sample = json.loads((temporary/f'sample_{control_index}_7.json').read_bytes())
            repeat = json.loads(repeat_path.read_bytes())
            require(first_sample['trades'] == repeat['trades'] and first_sample['overlap_candidates'] == repeat['overlap_candidates'],
                    'Fixed-seed reservoir sample is not deterministic')
            record = {'control': name, 'legal_neighbors': len(native_set), 'support_valid_rewirings_enumerated': examined,
                      'independent_neighbor_set_equal': True, 'wide_legal_trades_set_equal': True,
                      'full99_and_root_quotas_checked_for_every_output': True, 'sampling_controls': sampling,
                      'fixed_seed_reproducible': True}
            records.append(record)
            print(json.dumps(record), flush=True)
    require(sha256(generator_source.read_bytes()).hexdigest() == original_generator_hash, 'Generator source changed during review')
    sources = paths + [wide_path, generator_source, args.generator, wide_source, Path(__file__),
                       ROOT/'acceleration/audit_certificate.py']
    result = {'status': 'INDEPENDENT_COMPLETE_TWO_EDGE_NEIGHBOR_AND_QUOTA_REVIEW_PASS',
              'controls': len(records), 'records': records,
              'full99_graphs_and_root_quotas_checked': sum(row['legal_neighbors'] for row in records),
              'independent_two_edge_enumeration_complete_for_these_controls': True,
              'own_quota_implication': 'Each of the four symbols in an outer support has overlap incidence at most one by full99 pair caps. Four overlap neighbors each contribute one of those symbols, hence all four incidences equal one.',
              'sampling_scope': 'Membership/count and deterministic seed replay checked. Modulo-based PRNG selection is not claimed exactly uniform.',
              'inputs_sha256': {p.resolve().relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in sources},
              'elapsed_seconds': time.perf_counter()-started,
              'scope': 'Complete legal two-edge rewiring comparison for these nine fixed input assignments only. No full graph completion, general state-space coverage, or impossibility claim.'}
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','inputs_sha256')}))


if __name__ == '__main__':
    main()
