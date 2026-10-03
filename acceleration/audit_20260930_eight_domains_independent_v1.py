"""Independently re-enumerate frozen eight-coordinate local-star tables.

No producer module is imported. The reused independent enumerator branches on
whole subsets for the first unsatisfied root label; the producer instead uses
binary include/exclude branching. Every enumerated leaf is checked by mutation
of the full 99-vertex graph using the separately justified affected-pair method.
This establishes only the named local tables, never global feasibility.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback

from tqdm import tqdm
import audit_20260917_partial_matching as enum
import audit_20260917_affected_star_caps as caps

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'acceleration/results/20260917_partial_six_matchings'
BASE = ROOT / 'acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json'
OLD_AUDIT = ROOT / 'acceleration/results/20260917_independent_review/six_matchings/summary.json'
OLD_AUDIT_HASH = '051a57b2fc1b5353a6100b949f86674483cff686c4f797f4f1ad8b037d7f3768'
DOMAIN = 'PARTIAL_K_EIGHT_SAME_SIGN_COORDINATES_ROOT0123_V1'
CALIBRATION_CENTERS = (0, 4, 24, 8, 44, 60)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mask_list(record):
    values = [int(value, 16) for value in record['domain_masks_hex']]
    need(len(values) == len(set(values)), 'duplicate domain mask')
    need(all(0 <= mask < 1 << 84 for mask in values), 'out-of-range domain mask')
    return values


def exact_set(record, expected):
    actual = mask_list(record)
    need(sorted(actual) == expected, 'complete set mismatch')
    need(record['domain_size'] == len(actual), 'declared count mismatch')
    return actual


def build_scope(baseline, manifest):
    labels = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2)
              for s in (0, 1) for t in (0, 1)]
    support = [frozenset(symbol // 2 for symbol in pair) for pair in labels]
    freed = set()
    disjoint = set()
    for u, v in combinations(range(84), 2):
        if support[u].isdisjoint(support[v]):
            disjoint.add((u, v))
        elif len(support[u] & support[v]) == 1 and any(s in labels[v] and s < 8 for s in labels[u]):
            freed.add((u, v))
    raw_edges = baseline['overlap_edges_outer_zero_based']
    fixed_all = set(map(tuple, raw_edges))
    need(len(fixed_all) == len(raw_edges) == 168, 'raw baseline K size/duplicates')
    need(all(0 <= u < v < 84 for u, v in fixed_all), 'raw baseline edge format')
    fixed = fixed_all - freed
    removed = fixed_all & freed
    unknown = sorted(disjoint | freed)
    need((len(fixed), len(removed), len(freed), len(disjoint), len(unknown)) ==
         (120, 48, 480, 1680, 2160), 'scope cardinalities')
    for field, value in [('remaining_fixed_K_edges_outer', fixed),
                         ('removed_edges_outer', removed),
                         ('freed_legal_matching_edges_outer', freed),
                         ('unknown_edges_outer', unknown)]:
        need(manifest[field] == sorted(map(list, value)), 'manifest scope identity: ' + field)
    need(manifest['domain'] == DOMAIN, 'domain identity')
    adjacency = [set() for _ in range(99)]
    edges = [(0, v) for v in range(1, 15)] + [(v, v+1) for v in range(1, 15, 2)]
    edges += [(u+15, symbol+1) for u, pair in enumerate(labels) for symbol in pair]
    edges += [(u+15, v+15) for u, v in fixed]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    rows = [sum(1 << v for v in neighbors) for neighbors in adjacency]
    need(Counter(14 - rows[u+15].bit_count() for u in range(84)) == {10:24, 9:48, 8:12},
         'missing-neighbor histogram')
    validator = caps.StarValidator(rows)
    allowed = [0] * 84
    for u, v in unknown:
        allowed[u] |= 1 << v
        allowed[v] |= 1 << u
    return labels, rows, unknown, fixed, allowed, validator


def controls(rows, labels, unknown, allowed, validator, tables, deadline):
    reports = []
    for u in CALIBRATION_CENTERS:
        good = tables[u][0]
        selected = enum.bits(good)
        need(validator.check(u, good) and enum.direct(rows, labels, u, good), 'positive control')
        outside = enum.bits(allowed[u] & ~good)
        pool = sorted(selected + outside[:2])
        size = 14 - rows[u+15].bit_count()
        brute = sorted(sum(1 << v for v in group) for group in combinations(pool, size)
                       if enum.direct(rows, labels, u, sum(1 << v for v in group)))
        enumerated, nodes, _ = enum.enumerate_all(rows, labels, unknown, u, deadline, 1000000, set(pool))
        need(brute and enumerated == brute, 'restricted brute force disagreement')
        for group in combinations(pool, size):
            mask = sum(1 << v for v in group)
            need(validator.check(u, mask) == enum.direct(rows, labels, u, mask), 'full4851/affected disagreement')
        corruptions = [('missing_edge', good ^ (1 << selected[0])),
                       ('extra_edge', good | (1 << outside[0])),
                       ('empty', 0), ('self_loop', good | (1 << u)),
                       ('outside_84', good | (1 << 84))]
        for name, mask in corruptions:
            need(not validator.check(u, mask), 'corrupted graph accepted: ' + name)
        fixture = {'domain_masks_hex': [hex(x) for x in brute], 'domain_size': len(brute)}
        exact_set(fixture, brute)
        bad_records = [dict(fixture, domain_masks_hex=fixture['domain_masks_hex'] + [hex(brute[0])]),
                       dict(fixture, domain_masks_hex=fixture['domain_masks_hex'][1:]),
                       dict(fixture, domain_size=len(brute)+1)]
        for bad in bad_records:
            try:
                exact_set(bad, brute)
            except ValueError:
                pass
            else:
                raise ValueError('corrupted completeness fixture accepted')
        reports.append(dict(center=u,restricted_pool=pool,
                            subsets_checked=sum(1 for _ in combinations(pool,size)),
                            valid_subsets=len(brute),independent_nodes=nodes,
                            graph_corruptions_rejected=[name for name,_ in corruptions],
                            table_corruptions_rejected=['duplicate','missing','wrong_declared_count']))
    bad = rows.copy()
    bad[0] |= 1
    try:
        caps.StarValidator(bad)
    except ValueError:
        pass
    else:
        raise ValueError('loop in fixed base accepted')
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--domain-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--centers', default='completed', help='completed, all, or comma-separated labels')
    parser.add_argument('--controls-only', action='store_true')
    parser.add_argument('--seconds', type=float, default=1800)
    parser.add_argument('--nodes-per-center', type=int, default=5000000)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    need(not any(args.out.iterdir()), 'refuse to overwrite audit')
    started = stamp()
    start_clock = time.monotonic()
    bindings = {}
    records = []

    def read(path):
        bindings[key(path)] = digest(path)
        return json.loads(Path(path).read_bytes())

    for path in (__file__, enum.__file__, caps.__file__, ROOT/'uv.lock', ROOT/'pyproject.toml'):
        bindings[key(path)] = digest(path)
    manifest = read(args.domain_dir/'manifest.json')
    baseline = read(BASE)
    old_manifest = read(OLD/'manifest.json')
    old_audit = read(OLD_AUDIT)
    need(digest(OLD_AUDIT) == OLD_AUDIT_HASH, 'prior independent six-coordinate audit identity')
    need(old_audit['status'] == 'INDEPENDENT_SIX_COORDINATE_DOMAINS_PASS', 'prior audit outcome')
    labels, rows, unknown, fixed, allowed, validator = build_scope(baseline, manifest)
    old_fixed = set(map(tuple, old_manifest['remaining_fixed_K_edges_outer']))
    need(fixed <= old_fixed and len(old_fixed-fixed) == 12, 'six/eight fixed graph nesting')
    released = old_fixed - fixed
    present = sorted(int(path.stem.split('_')[1]) for path in args.domain_dir.glob('domain_??.json'))
    centers = present if args.centers == 'completed' else list(range(84)) if args.centers == 'all' else [int(x) for x in args.centers.split(',')]
    need(len(centers) == len(set(centers)) and all(0 <= u < 84 for u in centers), 'requested centers')
    need(set(centers) <= set(present), 'requested center table missing')
    need(set(CALIBRATION_CENTERS) <= set(present), 'calibration tables missing')
    selected_artifacts = {u: read(args.domain_dir/f'domain_{u:02d}.json') for u in set(centers)|set(CALIBRATION_CENTERS)}
    tables = {u: mask_list(record) for u, record in selected_artifacts.items()}
    frozen = dict(started_at=started,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  platform=platform.platform(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),
                  inputs_sha256=dict(bindings),question='Exact completeness and local validity of each selected eight-coordinate table',
                  scope=DOMAIN,selection=dict(request=args.centers,selected_centers=centers,available_centers=present),
                  success='Exact full set equality to independent enumeration, all leaves checked, exact old-ID embeddings; every selected center completes',
                  falsification='Any scope mismatch, invalid leaf, missing/extra/duplicate mask, or incorrect old-ID mapping',
                  limits=dict(wall_seconds=args.seconds,nodes_per_center=args.nodes_per_center),
                  numerical_settings=None,numerical_settings_null_reason='Exact integers only; no floating acceptance threshold',
                  prior_audit_replayed=False,prior_audit_scope='Immutable historical evidence reused; actual old masks and embeddings checked here',
                  producer_imported=False,shared_components=['Python standard library','tqdm','prior independent multiway root-label enumerator','prior independent affected-pair checker'],
                  trusted_components=['Python integer operations','SHA256','unchanged-pair proof in affected-pair checker'],
                  controls_only=args.controls_only,target_resolution=False)
    save(args.out/'manifest.json', frozen)
    deadline = start_clock + args.seconds
    status = 'INDEPENDENT_EIGHT_COORDINATE_SELECTED_DOMAINS_PASS'
    failure = None
    calibration = None
    embeddings = 0
    try:
        calibration = controls(rows, labels, unknown, allowed, validator, tables, deadline)
        save(args.out/'controls.json',dict(status='PASS',records=calibration,fixed_base_loop_rejected=True))
        if args.controls_only:
            status = 'INDEPENDENT_EIGHT_COORDINATE_CONTROLS_ONLY_PASS'
        else:
            for u in tqdm(centers, desc='Independent eight-coordinate domain audit',unit='center'):
                need(time.monotonic() < deadline, 'audit wall cap before center')
                begin = time.monotonic()
                saved = selected_artifacts[u]
                found, nodes, singles = enum.enumerate_all(rows,labels,unknown,u,deadline,args.nodes_per_center)
                actual = exact_set(saved, found)
                need(saved['outer_vertex'] == u and saved['domain'] == DOMAIN, 'center/domain metadata')
                need(saved['missing_neighbor_count'] == 14-rows[u+15].bit_count() and saved['allowed_single_neighbors'] == singles, 'domain metadata')
                for index, mask in enumerate(found):
                    if index % 1024 == 0:
                        need(time.monotonic() < deadline, 'audit wall cap during leaf validation')
                    need(mask & ~allowed[u] == 0 and validator.check(u,mask), 'invalid full99 leaf')
                old_path = OLD/f'domain_{u:02d}.json'
                old = read(old_path)
                need(digest(old_path) == old_audit['inputs_sha256'][key(old_path)], 'old table identity')
                extra = sum(1 << (v if a == u else a) for a,v in released if u in (a,v))
                converted = [mask|extra for mask in mask_list(old)]
                positions = {mask:i for i,mask in enumerate(actual)}
                mapping = [positions.get(mask) for mask in converted]
                need(None not in mapping and len(set(mapping)) == len(mapping), 'old embedding membership/injectivity')
                need(mapping == saved['old_to_new_domain_ids'] and len(mapping) == saved['old_embedded_choices'], 'saved old-ID mapping')
                # Center neighborhoods coincide exactly after adding released fixed edges.
                old_center = rows[u+15] | (extra << 15)
                need(all((old_center | (m << 15)) == (rows[u+15] | (n << 15)) for m,n in zip(mask_list(old),converted)), 'unchanged full neighborhood')
                embeddings += len(mapping)
                row = dict(outer_vertex=u,complete_domain_size=len(found),independent_nodes=nodes,
                           exact_full99_leaves_checked=len(found),old_embedded_choices=len(mapping),
                           raw_path=key(args.domain_dir/f'domain_{u:02d}.json'),raw_sha256=digest(args.domain_dir/f'domain_{u:02d}.json'),
                           completed_at=stamp(),elapsed_seconds=time.monotonic()-begin)
                save(args.out/f'vertex_{u:02d}.json',row)
                records.append(row)
                save(args.out/f'checkpoint_{len(records):02d}.json',dict(timestamp=stamp(),records=records,
                     completed_centers=len(records),domain_choices=sum(r['complete_domain_size'] for r in records),
                     complete_selected_centers=len(records)==len(centers)))
        need(all(digest(ROOT/path) == value for path,value in bindings.items()), 'input changed during verification')
    except Exception as exc:
        status = 'INDEPENDENT_EIGHT_COORDINATE_AUDIT_INCOMPLETE_OR_FAILED'
        failure = dict(exception_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    result = dict(status=status,started_at=started,completed_at=stamp(),source_commit=frozen['source_commit'],
                  command=frozen['command'],working_directory=frozen['working_directory'],python=frozen['python'],
                  inputs_sha256=bindings,scope=DOMAIN,scope_statement='Exactly 120 fixed baseline K edges; only 480 root-groups-0-through-3 same-sign coordinate edges and 1680 disjoint-support edges may vary; all other prescribed absences fixed. No automorphism assumption.',
                  statement='For each completed record the saved table is exactly the set of locally admissible degree-14 center stars satisfying all full-99 upper common-neighbor caps and all 14 exact root-neighbor quotas; prior six-coordinate stars embed by their recorded original IDs with identical full center neighborhoods.',
                  requested_centers=centers,records=records,completed_centers=len(records),
                  complete_selected_centers=not args.controls_only and len(records)==len(centers) and failure is None,
                  all_84_domains_complete=not args.controls_only and len(records)==84 and set(centers)==set(range(84)) and failure is None,
                  domain_choices=sum(r['complete_domain_size'] for r in records),old_embedded_choices=embeddings,
                  calibration=calibration,failure=failure,elapsed_seconds=time.monotonic()-start_clock,
                  producer_imported=False,shared_components=frozen['shared_components'],
                  verification_type='Independent re-enumeration and exact artifact checking, not external review',
                  claim_id=None,claim_id_null_reason='Parent researcher must bind exact verified scope to an explicit claim revision; this checker does not promote the ledger',
                  target_resolution=False,limitations=['Only listed completed center tables checked; no claim for unlisted or incomplete centers.',
                  'Local admissibility is necessary but does not establish global feasibility or exclusion.',
                  'Historical six-coordinate audit is hash-bound, not rerun; shared independent checker code disclosed.',
                  'No target-wide coverage denominator exists.'],
                  output_sha256={key(path):digest(path) for path in args.out.iterdir() if path.is_file()})
    save(args.out/'summary.json',result)
    print(json.dumps({field:result[field] for field in ('status','completed_centers','domain_choices','old_embedded_choices','all_84_domains_complete','failure')}))
    return 1 if failure else 0


if __name__ == '__main__':
    sys.exit(main())
