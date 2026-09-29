"""Bind disjoint independently checked eight-coordinate tables to claim rev1.

This does not rerun enumeration. It checks exact artifact identities, the
disjoint 84-center union, integer counts, and saved prior-star embeddings.
The separately saved enumeration audits supply completeness evidence.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'PARTIAL_K_EIGHT_SAME_SIGN_COORDINATES_ROOT0123_V1'


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def covered(records):
    vertices = [record['outer_vertex'] for record in records]
    need(len(vertices) == len(set(vertices)) == 84 and set(vertices) == set(range(84)),
         'coverage must be disjoint and exactly all 84 center labels')
    return (sum(record['complete_domain_size'] for record in records),
            sum(record['old_embedded_choices'] for record in records))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--domain-dir', type=Path, required=True)
    parser.add_argument('--audits', type=Path, nargs='+', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), 'refuse overwrite')
    bindings = {}

    def read(path):
        bindings[key(path)] = digest(path)
        return json.loads(Path(path).read_bytes())

    producer = read(args.domain_dir/'summary.json')
    manifest = read(args.domain_dir/'manifest.json')
    need(producer['domain'] == manifest['domain'] == DOMAIN, 'producer scope identity')
    need(producer['complete_all_centers'] and producer['completed_centers'] == 84, 'producer completeness record')
    reports = []
    records = []
    for path in args.audits:
        report = read(path)
        need(report['status'] == 'INDEPENDENT_EIGHT_COORDINATE_SELECTED_DOMAINS_PASS'
             and report['complete_selected_centers'] and report['failure'] is None, 'independent audit did not complete')
        need(report['scope'] == DOMAIN and report['producer_imported'] is False, 'independent audit scope/method')
        for inventory in ('inputs_sha256', 'output_sha256'):
            for source, expected in report[inventory].items():
                need(digest(ROOT/source) == expected, 'audit binding changed: ' + source)
                bindings[source] = expected
        need(report['completed_centers'] == len(report['records'])
             and report['domain_choices'] == sum(row['complete_domain_size'] for row in report['records'])
             and report['old_embedded_choices'] == sum(row['old_embedded_choices'] for row in report['records']),
             'audit population metadata')
        records.extend(report['records'])
        reports.append(dict(path=key(path),sha256=digest(path),centers=report['completed_centers'],
                            domain_choices=report['domain_choices'],old_embedded_choices=report['old_embedded_choices']))
    counts = covered(records)
    need(counts == (producer['complete_domain_choices'],producer['old_choices_located_in_complete_domains']), 'producer/audit total mismatch')
    need(counts == (2290122,879449), 'frozen expected populations differ')
    lookup = {record['outer_vertex']:record for record in producer['domains']}
    need(len(lookup) == len(producer['domains']) == 84, 'producer domain record duplication')
    checked = []
    for record in sorted(records,key=lambda row:row['outer_vertex']):
        u = record['outer_vertex']
        path = args.domain_dir/f'domain_{u:02d}.json'
        raw = read(path)
        need(digest(path) == record['raw_sha256'] == lookup[u]['sha256'], 'raw audited/copied domain mismatch')
        need(record['exact_full99_leaves_checked'] == record['complete_domain_size'] == raw['domain_size'] == lookup[u]['domain_size'], 'per-center leaf counts')
        need(record['old_embedded_choices'] == raw['old_embedded_choices'] == lookup[u]['old_embedded_choices'], 'per-center old embeddings')
        checked.append(dict(outer_vertex=u,raw_path=key(path),raw_sha256=digest(path),
                            domain_size=record['complete_domain_size'],old_embedded_choices=record['old_embedded_choices']))
    # Controls reject overlapping center evidence and a missing center.
    for corrupt in (records[:-1],records+[records[0]],records[:-1]+[records[0]]):
        try:
            covered(corrupt)
        except ValueError:
            pass
        else:
            raise ValueError('coverage corruption accepted')
    for path in (__file__,ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    result = dict(status='INDEPENDENT_EIGHT_COORDINATE_ALL84_BINDING_PASS',
                  claim_id='C-PARTIAL-K-EIGHT-COORDINATE-DOMAINS',claim_revision=1,recommendation='VERIFIED',
                  statement='For each of the 84 outer centers in the explicitly fixed baseline-18481 eight-coordinate family, the saved table contains exactly all degree-14 local center stars satisfying every full-99 common-neighbor upper cap and all 14 exact root-neighbor quotas. The tables contain 2,290,122 center-star choices in total, and all 879,449 six-coordinate choices embed injectively per center with unchanged full center neighborhoods and the recorded original-ID maps.',
                  scope='120 baseline K edges, fixed root scaffold and all recorded other absences remain fixed; only 480 same-sign coordinate edges at root groups 0,1,2,3 plus 1680 disjoint-support edges may vary. No automorphism assumed.',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',
                  verification_type='Independent enumeration and artifact checking combined by exact, disjoint center coverage; no external review',
                  method='Hash-bind the independent old17 and new67 audits, all their inputs/outputs, and byte-identical copied tables; recompute all count totals and require every center exactly once.',
                  centers=84,domain_choices=counts[0],old_embedded_choices=counts[1],records=checked,
                  audits=reports,inputs_sha256=bindings,
                  controls=dict(missing_center_rejected=True,duplicate_center_rejected=True,replacement_duplicate_rejected=True),
                  numerical_settings=None,numerical_settings_null_reason='Exact integers and byte identities only',
                  artifact_availability='LOCAL_ONLY',artifact_availability_reason='This binding records the local artifacts before publication; publication availability must be updated separately.',
                  shared_components=['Python standard library','tqdm','prior independent multiway root-label enumerator','prior independent affected-pair validator'],
                  limitations=['Conditional family only; local domains do not imply global feasibility or exclusion.',
                               'No target-wide coverage measure or graph/nonexistence certificate.',
                               'Historical six-coordinate domain audit reused by hash; fresh checks independently confirm exact embeddings.',
                               'This binding recomputes artifact/coverage facts; it does not itself rerun the saved independent enumerations.'],
                  target_resolution=False,external_review=False)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'],domain_choices=counts[0],sha256=digest(args.out))))


if __name__ == '__main__':
    main()
