"""Exact set-based reference for every CUDA initial-pair-support flag.

Tests the complete pilot domains, a singleton-domain control, a repeated batch
candidate, and an empty-domain control. Reduced-domain controls test mechanics
only and do not represent complete-domain claims.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct
import subprocess
from tempfile import TemporaryDirectory
import time

from audit_certificate import full_graph, require

ROOT = Path(__file__).resolve().parents[1]


def reference(domains):
    flags = []
    unsupported = [[0]*84 for _ in range(84)]
    surviving = [0]*84
    # Python set membership/intersection is independent of CUDA's bit packing.
    for u in range(84):
        choices = [[[], []] for _ in range(84)]
        for v, neighbors in enumerate(domains):
            for right in neighbors:
                choices[v][int(u+15 in right)].append(right)
        for left in domains[u]:
            row = []
            for v in range(84):
                if u == v:
                    row.append('1')
                    continue
                adjacent = int(v+15 in left)
                allowed = any(len(left & right) == 2-adjacent for right in choices[v][adjacent])
                row.append('1' if allowed else '0')
                if not allowed:
                    unsupported[u][v] += 1
            flags.append(''.join(row))
            surviving[u] += all(bit == '1' for bit in row)
    return flags, unsupported, surviving


def binary_input(candidates):
    output = bytearray(b'C99PAIR1'+struct.pack('<I', len(candidates)))
    for candidate in candidates:
        output.extend(struct.pack('<84I', *map(len, candidate)))
        for domains in candidate:
            for row in domains:
                value = sum(1 << v for v in row)
                output.extend(struct.pack('<QQ', value & ((1 << 64)-1), value >> 64))
    return bytes(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', type=Path, default=ROOT/'acceleration/results/20260916_guided_pilot')
    parser.add_argument('--out', type=Path, default=ROOT/'acceleration/results/20260916_star_pair_gpu')
    parser.add_argument('--gpu', type=Path, default=ROOT/'acceleration/build/star_pair_gpu.exe')
    args = parser.parse_args()
    require(not args.out.exists(), 'QA output directory must be new')
    args.out.mkdir(parents=True)
    started = time.perf_counter()
    candidate_path, domains_path, audit_path = [args.pilot/name for name in
        ('best_candidate.json', 'best_domains_python.json', 'best_domains_audit.json')]
    candidate, domains, domain_audit = [json.loads(path.read_bytes()) for path in (candidate_path, domains_path, audit_path)]
    require(domains['complete_domain_enumeration'] is True and domain_audit['complete_domain_enumeration_verified'] is True,
            'Pilot domains need complete independent audit')
    for name, expected in domain_audit['inputs_sha256'].items():
        path = Path(name)
        require(sha256(path.read_bytes()).hexdigest() == expected, 'Independent domain audit input changed')
    require(domains['candidate_sha256'] == sha256(candidate_path.read_bytes()).hexdigest(), 'Candidate domain binding differs')
    require([row['outer_vertex'] for row in domains['domains']] == list(range(84)), 'Domain vertex order')
    adjacency, unknown = full_graph(candidate)
    full = []
    for u, record in enumerate(domains['domains']):
        stars = []
        for text in record['domain_masks_hex']:
            mask = int(text, 16)
            require(mask >= 0 and mask >> 84 == 0 and mask.bit_count() == 8, 'Invalid star mask')
            chosen = {v+15 for v in range(84) if mask >> v & 1}
            require(all(tuple(sorted((u+15, v))) in unknown for v in chosen), 'Star edge outside disjoint domain')
            neighbors = adjacency[u+15] | chosen
            require(len(neighbors) == 14, 'Not a complete degree14 star')
            stars.append(frozenset(neighbors))
        full.append(stars)
    small = [rows[:1] for rows in full]
    empty = [[] for _ in range(84)]
    candidates = [full, small, full, empty]
    binary = args.out/'input.bin'
    binary.write_bytes(binary_input(candidates))
    output = args.out/'gpu.json'
    process = subprocess.run([str(args.gpu), str(binary), str(output), '--flags'], text=True, capture_output=True, check=True)
    print(process.stdout.strip(), flush=True)
    gpu = json.loads(output.read_bytes())
    require(gpu['candidate_count'] == 4 and len(gpu['results']) == 4, 'GPU batch dimensions')
    reference_started = time.perf_counter()
    expectations = [reference(full), reference(small)]
    expectations += [expectations[0], reference(empty)]
    python_seconds = time.perf_counter()-reference_started
    reports = []
    flags_checked = 0
    for index, (candidate_domains, expected, result) in enumerate(zip(candidates, expectations, gpu['results'])):
        flags, unsupported, surviving = expected
        require(result['candidate_index'] == index and result['domain_counts'] == list(map(len, candidate_domains)),
                'Incorrect candidate offsets or domain counts')
        require(result['support_rows_bits'] == flags, f'GPU/Python support mismatch for candidate {index}')
        require(result['unsupported_domain_counts_by_pair'] == unsupported, 'Unsupported per-pair summary mismatch')
        require(result['initial_pair_supported_domain_counts'] == surviving
                and result['per_vertex_initial_supported_domains'] == surviving, 'Per-vertex all83 support mismatch')
        require(result['total_initial_pair_supported_domains'] == sum(surviving)
                and result['vertices_with_initial_pair_supported_domain'] == sum(v > 0 for v in surviving)
                and result['total_unsupported_relations'] == sum(map(sum, unsupported)), 'Aggregated support summary mismatch')
        flags_checked += len(flags)*83
        reports.append({'candidate_index': index, 'domains': len(flags),
                        'vertices_with_initial_support': sum(v > 0 for v in surviving),
                        'initial_pair_supported_domains': sum(surviving),
                        'unsupported_domain_relations': sum(map(sum, unsupported))})
    malformed = []
    with TemporaryDirectory(prefix='bad-pair-', dir=args.out) as temporary:
        temporary = Path(temporary)
        good = binary.read_bytes()
        versions = {'wrong_header': b'BADPAIR1'+good[8:], 'truncated': good[:-1],
                    'trailing': good+b'\x00', 'zero_candidates': b'C99PAIR1'+struct.pack('<I', 0)}
        row_start = 12+84*4
        invalid_degree = bytearray(good)
        invalid_degree[row_start:row_start+16] = b'\x00'*16
        versions['invalid_degree'] = bytes(invalid_degree)
        for name, content in versions.items():
            path = temporary/f'{name}.bin'
            path.write_bytes(content)
            test = subprocess.run([str(args.gpu), str(path), str(temporary/f'{name}.json')], text=True, capture_output=True)
            require(test.returncode != 0, f'Malformed binary accepted: {name}')
            malformed.append({'case': name, 'rejected': True, 'message': test.stderr.strip()})
    sources = [Path(__file__), ROOT/'acceleration/star_pair_gpu.cu', ROOT/'acceleration/build_star_pair_gpu.ps1',
               args.gpu, candidate_path, domains_path, audit_path, binary, output,
               ROOT/'acceleration/audit_certificate.py']
    report = {'status': 'ALL_CUDA_INITIAL_PAIR_SUPPORT_FLAGS_MATCH_INDEPENDENT_PYTHON_SETS',
              'complete_pilot_domains': sum(map(len, full)), 'batch_candidates': 4,
              'candidate_controls': ['complete_pilot', 'one_domain_per_vertex_subset', 'complete_pilot_repeat', 'empty_domains'],
              'all_nonself_support_flags_checked': flags_checked, 'records': reports,
              'malformed_input_controls': malformed,
              'python_set_reference_seconds': python_seconds, 'cuda_transfer_and_kernel_seconds': gpu['elapsed_seconds'],
              'cuda_kernel_seconds': gpu['kernel_seconds'], 'elapsed_seconds': time.perf_counter()-started,
              'inputs_sha256': {path.resolve().relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in sources},
              'scope': 'Every initial support flag and aggregate matched exact independent Python set compatibility on these four controls. Full original domains used for the pilot; subset controls test mechanics only. This is a score backend, not AC propagation, a completion witness or a global exclusion.'}
    (args.out/'review.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'inputs_sha256'}))


if __name__ == '__main__':
    main()
