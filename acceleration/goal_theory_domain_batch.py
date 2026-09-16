"""Bounded complete-domain and independent-audit batch over saved star survivors."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    summary_path = args.out/'summary.json'
    if summary_path.exists():
        raise FileExistsError(summary_path)
    args.out.mkdir(parents=True,exist_ok=True)
    walk_path = Path('acceleration/results/20260916_wide_walk_2000.json')
    selection_path = Path('acceleration/results/20260916_goal_theory_wide_stars100_audit.json')
    selection = read(selection_path)
    for name,expected in selection['inputs_sha256'].items():
        if digest(Path(name)) != expected:
            raise ValueError('Changed selection evidence: '+name)
    if selection['status'] != 'INDEPENDENT_NONLINEAR_VERTEX_STAR_AUDIT_PASS':
        raise ValueError('Selection is not independently audited')
    walk = read(walk_path)
    indices = selection['all_local_stars_feasible_snapshot_indices']
    producer = Path('acceleration/goal_theory_star_domains.py')
    auditor = Path('acceleration/audit_goal_theory_domains.py')
    started = time.perf_counter()
    records = []
    for index in indices:
        if index in (15,100):
            candidate = Path(f'acceleration/results/20260916_wide_probes/candidate_{index}.json')
            domain = Path(f'acceleration/results/20260916_goal_theory_domains_wide{index}.json')
            checked = domain.with_name(domain.stem+'_audit.json')
        else:
            candidate = args.out/f'candidate_{index}.json'
            domain = args.out/f'candidate_{index}_domains.json'
            checked = args.out/f'candidate_{index}_audit.json'
            if not candidate.exists():
                document = dict(overlap_edges_outer_zero_based=walk['overlap_candidates'][index],
                                source_walk=str(walk_path),source_sha256=digest(walk_path),snapshot_index=index)
                with candidate.open('x',encoding='utf-8') as stream:
                    stream.write(json.dumps(document,indent=2)+'\n')
        if read(candidate)['overlap_edges_outer_zero_based'] != walk['overlap_candidates'][index]:
            raise ValueError('Wrong candidate snapshot')
        if not domain.exists():
            subprocess.run([sys.executable,str(producer),'--candidate',str(candidate),'--out',str(domain),
                            '--seconds','30','--node-cap','2000000','--domain-cap','20000'],check=True,capture_output=True)
        if not checked.exists():
            subprocess.run([sys.executable,str(auditor),'--candidate',str(candidate),'--domains',str(domain),
                            '--out',str(checked),'--seconds','30'],check=True,capture_output=True)
        certificate, audit = read(domain),read(checked)
        for mapping in (certificate['inputs_sha256'],audit['inputs_sha256']):
            for name,expected in mapping.items():
                if digest(Path(name)) != expected:
                    raise ValueError('Changed candidate evidence: '+name)
        if certificate['candidate_sha256'] != digest(candidate):
            raise ValueError('Candidate domain binding failed')
        complete = audit['complete_domain_enumeration_verified']
        status = audit.get('propagation_status','INCOMPLETE') if complete else 'INCOMPLETE'
        row = dict(snapshot_index=index,status=status,complete_domains_independently_verified=complete,
                   initial_domain_sizes=[len(r['domain_masks_hex']) for r in certificate['domains']],
                   total_domain_values=sum(len(r['domain_masks_hex']) for r in certificate['domains']),
                   producer_nodes=certificate['total_nodes'],audit_nodes=audit.get('independent_search_nodes'),
                   enumeration_seconds=certificate['enumeration_seconds'],audit_seconds=audit['elapsed_seconds'],
                   empty_vertex=certificate.get('propagation',{}).get('empty_vertex'),
                   deletion_events=len(certificate.get('propagation',{}).get('events',[])),
                   inputs_sha256={str(p):digest(p) for p in (candidate,domain,checked)})
        records.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in ('inputs_sha256','initial_domain_sizes')}),flush=True)
    result = dict(status='BOUNDED_COMPLETE_DOMAIN_BATCH_AUDIT_COMPLETED',snapshots=len(records),
                  status_histogram=dict(Counter(r['status'] for r in records)),records=records,
                  inputs_sha256={str(p):digest(p) for p in (walk_path,selection_path,producer,auditor,Path(__file__))},
                  elapsed_seconds=time.perf_counter()-started,
                  scope='Exactly the saved all-local-stars-pass variable-compression sample. Complete local domains and checked reciprocity deletions concern each fixed K only; no uniform E0 or Conway proof.')
    with summary_path.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'records'}))


if __name__ == '__main__':
    main()
