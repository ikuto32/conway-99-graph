"""Independent complete checking of the specified 192 scaffold transports.

No producer imports. Coordinates and primary edge numbering are reconstructed.
"""
import argparse
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'acceleration/results/20260930_two_star_nogood36_anchor_transport/run01'
SOURCE_GATE = ROOT / 'acceleration/results/20260930_independent_review/two_star_empty_domain_cut_v2/summary.json'
SOURCE_HASH = 'e3aae7ba9b776e9382c1790c64f0e76be6f0497912a9e1440e43a7df959ce16c'
ENCODING_GATE = ROOT / 'acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json'
ENCODING_HASH = '2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58'
CERT = ROOT / 'acceleration/results/20260930_two_star_empty_domain_cut/run01/certificate.json'

def need(condition, message):
    if not condition:
        raise ValueError(message)

def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def pairs_hook(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=pairs_hook)

LABELS = [tuple((2*g+a, 2*h+b)) for g in range(7) for h in range(g+1, 7)
          for a in range(2) for b in range(2)]
LABEL_INDEX = {frozenset(label): 15+i for i, label in enumerate(LABELS)}
EDGES = list(itertools.combinations(range(15, 99), 2))
EDGE_INDEX = {frozenset(edge): i+1 for i, edge in enumerate(EDGES)}

def known(u, v):
    if u == v:
        return 0
    u, v = sorted((u, v))
    if u == 0:
        return int(v < 15)
    if v < 15:
        return int((u-1)//2 == (v-1)//2)
    if u < 15:
        return int(u-1 in LABELS[v-15])
    return -1

def audit_records(records, clause):
    expected_symbols = set()
    for first in itertools.permutations((0, 1)):
        for second in itertools.permutations((2, 3)):
            for tail in itertools.permutations((4, 5, 6)):
                target_groups = first + second + tail
                for signs in itertools.product((0, 1), repeat=3):
                    symbols = tuple(2*target_groups[g] + (b ^ (signs[g-4] if g >= 4 else 0))
                                    for g in range(7) for b in range(2))
                    expected_symbols.add(symbols)
    need(len(expected_symbols) == 192 and len(records) == 192, 'complete finite population cardinality')
    seen_symbols, images, maps = set(), [], set()
    for number, rec in enumerate(records):
        need(rec['id'] == number, 'ordered record IDs')
        symbols = tuple(rec['symbol_map'])
        need(symbols in expected_symbols and symbols not in seen_symbols, 'unique in-population symbol map')
        seen_symbols.add(symbols)
        need(rec['group_permutation'] == [symbols[2*g]//2 for g in range(7)], 'group metadata')
        mask = sum((symbols[2*g] % 2) << (g-4) for g in range(4, 7))
        need(rec['tail_sign_mask'] == mask, 'tail sign metadata')
        vertex_map = [0] + [s+1 for s in symbols]
        vertex_map.extend(LABEL_INDEX[frozenset(symbols[s] for s in label)] for label in LABELS)
        need(rec['full99'] == vertex_map, 'full reconstructed vertex transport')
        need(set(vertex_map) == set(range(99)) and vertex_map[15] == 15 and vertex_map[59] == 59,
             'vertex bijection and fixed ordered anchor')
        for u in range(99):
            for v in range(99):
                need(known(u, v) == known(vertex_map[u], vertex_map[v]), 'preserve complete scaffold')
        edge_map = [0] + [EDGE_INDEX[frozenset((vertex_map[u], vertex_map[v]))] for u, v in EDGES]
        need(rec['edge_variable_map'] == edge_map, 'complete primary edge transport')
        need(set(edge_map[1:]) == set(range(1, 3487)), 'edge bijection')
        image = [(-1 if literal < 0 else 1)*edge_map[abs(literal)] for literal in clause]
        canonical = sorted(image, key=abs)
        need(rec['transported_clause'] == image and rec['canonical_clause'] == canonical,
             'signed literal and canonical image')
        images.append(tuple(canonical))
        maps.add(tuple(vertex_map))
    need(seen_symbols == expected_symbols, 'exhaustive specified symbol population')
    need(len(maps) == 192 and len(set(images)) == 192, 'distinct maps and clause images')
    return images

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    need(digest(SOURCE_GATE) == SOURCE_HASH and digest(ENCODING_GATE) == ENCODING_HASH, 'pinned independent gates')
    gate = read(SOURCE_GATE)
    need(gate['status'] == 'INDEPENDENT_TWO_STAR_EMPTY_DOMAIN_NOGOOD_PASS', 'source status')
    inputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in
              [SOURCE_GATE, ENCODING_GATE, CERT, Path(__file__).resolve(), ROOT/'uv.lock', ROOT/'pyproject.toml']}
    for name, expected in gate['inputs_sha256'].items():
        need(digest(ROOT/name) == expected, 'source gate bound input '+name)
        inputs[name] = expected
    for path in sorted(RUN.iterdir()):
        if path.is_file():
            inputs[path.relative_to(ROOT).as_posix()] = digest(path)
    summary = read(RUN/'summary.json')
    for name, expected in summary['artifact_hashes'].items():
        need(digest(RUN/name) == expected, 'producer artifact identity '+name)
    need(gzip.decompress((RUN/'maps.json.gz').read_bytes()) == (RUN/'maps.json').read_bytes(), 'exact compressed recovery')
    records = read(RUN/'maps.json')['records']
    clause = read(CERT)['clause']
    need(len(clause) == 36 and len(set(clause)) == 36 and all(x < 0 for x in clause), 'source clause')
    images = audit_records(records, clause)
    uniques = read(RUN/'unique_clauses.json')
    need(len(uniques) == 192, 'unique table length')
    for i, row in enumerate(uniques):
        need(row == {'id': i, 'clause': list(images[i]), 'map_ids': [i]}, 'complete dedup incidence')
        need(records[i]['unique_clause_id'] == i, 'record to unique incidence')
    suffix = (RUN/'clauses.cnfpart').read_bytes()
    expected_suffix = ''.join(' '.join(map(str, row))+' 0\n' for row in images).encode('ascii')
    need(suffix == expected_suffix, 'all exact suffix bytes')
    need(tuple(sorted(clause, key=abs)) in images, 'identity source included')
    need(summary['generated_maps'] == 192 and summary['unique_signed_clauses'] == 192
         and summary['duplicate_clause_images'] == 0, 'claimed stage counts')
    # The raw data are positive controls; independent signed truth tables test direction and sign.
    signed_checks = 0
    permutation = [0, 3, 1, 2]
    for signs in itertools.product((-1, 1), repeat=3):
        for values in itertools.product((0, 1), repeat=3):
            original = [0]+list(values)
            moved = [0]*4
            for i in range(1, 4):
                moved[permutation[i]] = original[i]
            a = any(original[i+1] == (signs[i] > 0) for i in range(3))
            b = any(moved[permutation[i+1]] == (signs[i] > 0) for i in range(3))
            need(a == b, 'signed forward transport truth table')
            signed_checks += 1
    rejected = []
    mutations = [
        ('missing_map', lambda x: x.pop()),
        ('duplicate_symbol_map', lambda x: x[1].update(symbol_map=x[0]['symbol_map'])),
        ('wrong_group_metadata', lambda x: x[0]['group_permutation'].__setitem__(0, 2)),
        ('wrong_tail_mask', lambda x: x[0].update(tail_sign_mask=8)),
        ('wrong_root_image', lambda x: x[0]['full99'].__setitem__(0, 1)),
        ('wrong_outer_image', lambda x: x[0]['full99'].__setitem__(16, 17)),
        ('wrong_edge_image', lambda x: x[0]['edge_variable_map'].__setitem__(1, 2)),
        ('wrong_literal_sign', lambda x: x[0]['transported_clause'].__setitem__(0, -x[0]['transported_clause'][0])),
        ('omitted_canonical_literal', lambda x: x[0]['canonical_clause'].pop()),
    ]
    for name, mutate in mutations:
        corrupted = copy.deepcopy(records)
        mutate(corrupted)
        try:
            audit_records(corrupted, clause)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError('accepted corruption '+name)
    report = {
        'status': 'INDEPENDENT_NOGOOD36_ANCHOR_TRANSPORT_PASS',
        'claim_id': 'C-UNRESTRICTED-NOGOOD36-ANCHOR-TRANSPORT192', 'claim_revision': 1,
        'recommendation': 'VERIFIED', 'kind': 'mathematical result', 'basis': ['DERIVED', 'COMPUTED'],
        'statement': 'All 192 specified ordered-anchor-fixing scaffold relabelings transport the verified 36-literal nogood to 192 distinct clauses entailed by every normalized unrestricted target and its exact unrestricted CNF.',
        'scope': 'Exactly group permutations S2 x S2 x S3 and sign flips on groups 4,5,6; ordered anchor vertices15,59 fixed. No target automorphism assumption or full relabeling-group census.',
        'dependencies': [
            {'id': 'C-UNRESTRICTED-TWO-STAR-POSITIVE-EDGE-NOGOOD36', 'revision': 1, 'relation': 'uses_result'},
            {'id': 'C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING', 'revision': 1, 'relation': 'encoding_equivalence'},
        ],
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'python': platform.python_version(),
        'verifier': '/root independent checker, not transport producer',
        'verification_type': 'complete independent artifact checking and derivation; no producer code imported',
        'inputs_sha256': inputs,
        'checks': {'specified_maps': 192, 'distinct_maps': 192, 'unique_clauses': 192,
                   'scaffold_entries_checked': 192*99*99, 'primary_images_checked': 192*3486,
                   'signed_literals_checked': 192*36, 'signed_truth_table_assignments': signed_checks,
                   'corruptions_rejected': rejected, 'exact_gzip_recovery': True},
        'derivation': [
            'The exhaustive product enumeration has 2!*2!*3!*2^3=192 distinct symbol maps. All records coincide with this set.',
            'Every map preserves all known/free scaffold entries and bijects all outer primary edges, so relabeling maps the normalized target family bijectively onto itself.',
            'For any normalized target A, apply the inverse vertex map. The source clause holds there; transporting each signed edge literal forward gives the recorded image clause holding in A.',
            'The audited unrestricted encoding equivalence therefore entails each clause for every satisfying CNF assignment. No permutation of auxiliary variables is needed.',
        ],
        'limitations': ['No new target graph, unrestricted exclusion, or search coverage fraction.',
                        'No CNF was augmented or solved in this audit.',
                        'The 192 clause count measures this finite image population, not new independently excluded graph classes.'],
        'elapsed_seconds': time.monotonic()-start,
    }
    path = out/'summary.json'
    path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': report['status'], 'sha256': digest(path), 'elapsed_seconds': report['elapsed_seconds']}))

if __name__ == '__main__':
    main()
