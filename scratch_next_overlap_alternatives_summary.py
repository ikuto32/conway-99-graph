"""Assemble the bounded four-candidate pool without changing its inputs."""
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def main():
    records=[]
    for index in range(4):
        stem=f'scratch_next_overlap_alternatives_r{index}'
        paths={kind:HERE/f'{stem}{suffix}.json' for kind,suffix in
               [('candidate',''),('audit','_audit'),('orbit','_orbit'),('lp','_lp'),
                ('farkas','_farkas'),('farkas_audit','_farkas_audit')]}
        data={kind:json.loads(path.read_bytes()) for kind,path in paths.items()}
        candidate_hash=sha256(paths['candidate'].read_bytes()).hexdigest()
        assert data['candidate']['status'] in ('OPTIMAL','FEASIBLE')
        assert data['audit']['status']=='INDEPENDENT_ALTERNATIVE_OVERLAP_AUDIT_PASS'
        assert data['audit']['input_sha256']==candidate_hash
        assert data['orbit']['input_sha256']==candidate_hash
        assert data['farkas_audit']['status']=='INDEPENDENT_ALTERNATIVE_INTEGER_FARKAS_AUDIT_PASS'
        for name,digest in data['farkas_audit']['inputs_sha256'].items():
            assert sha256((HERE/name).read_bytes()).hexdigest()==digest
        assert data['farkas']['candidate_sha256']==candidate_hash
        assert data['farkas']['combined_rhs']==data['farkas_audit']['combined_rhs']<0
        records.append({'index':index,'candidate_sha256':candidate_hash,
                        'generation_seconds':data['candidate']['elapsed_seconds'],
                        'excluded_preceding_sign_images':data['candidate']['distinct_sign_orbit_assignments_excluded'],
                        'partial_graph_audit':'PASS','original_cut_score':data['audit']['existing_capacity_cut']['score'],
                        'original_sign_orbit_cut_minimum':data['orbit']['minimum_score'],
                        'initial_primal_LP_status':data['lp']['status'],
                        'exact_certificate_rhs':data['farkas']['combined_rhs'],
                        'independent_farkas_audit':'PASS',
                        'certificate_groups':data['farkas_audit']['group_counts'],
                        'certificate_upper_bounds':data['farkas_audit']['upper_bound_count'],
                        'sha256':{path.name:sha256(path.read_bytes()).hexdigest() for path in paths.values()}})
    result={'status':'FOUR_SIGN_DISTINCT_OVERLAP_ALTERNATIVES_INDEPENDENTLY_AUDITED_AND_EXCLUDED',
            'records':records,'generation_time_limit_per_candidate':45,'generation_workers':1,
            'dual_time_limit_per_candidate':30,'same_UNKNOWN_run_extended':False,
            'scope':'Four complete overlap assignments at one saved sharp C, sign-distinct from the original and each other. Each excluded even without disjoint C totals by an independent exact integer capacity audit. No all-C or global E0 exclusion; no graph.'}
    (HERE/'scratch_next_overlap_alternatives_summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'candidate_count':4,
                      'certificate_rhs':[r['exact_certificate_rhs'] for r in records]}))


if __name__=='__main__': main()
