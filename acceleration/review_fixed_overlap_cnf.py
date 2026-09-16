"""Small semantic corruption controls; no solver and no graph witness output."""
import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from audit_fixed_overlap_cnf import audit, resolve, require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    require(not args.out.exists(),'Fresh controls directory required')
    positive = audit(args.manifest)
    original = json.loads(args.manifest.read_bytes())
    args.out.mkdir(parents=True)
    cases = []
    def reject(name,change):
        data = copy.deepcopy(original)
        change(data)
        path = args.out/(name+'.json')
        path.write_text(json.dumps(data,allow_nan=False)+'\n',encoding='utf-8')
        try:
            audit(path)
        except ValueError as exc:
            cases.append(dict(name=name,rejected=True,reason=str(exc),path=str(path),sha256=digest(path)))
        else:
            raise AssertionError('Corruption accepted: '+name)
    reject('identity_map',lambda d:d.update(current_to_legacy_vertices=list(range(84))))
    reject('wrong_inverse',lambda d:d['legacy_to_current_vertices'].__setitem__(2,2))
    reject('wrong_exact_label',lambda d:d['current_labels'].__setitem__(0,[0,4]))
    reject('missing_unit',lambda d:d['fixed_units'].pop())
    reject('duplicate_unit',lambda d:d['fixed_units'].__setitem__(1,d['fixed_units'][0]))
    reject('wrong_literal_sign',lambda d:d['fixed_units'][0].update(literal=-d['fixed_units'][0]['literal']))
    reject('wrong_current_edge',lambda d:d['fixed_units'][0].update(current_edge=[0,4]))
    reject('wrong_legacy_variable',lambda d:d['fixed_units'][0].update(variable=3486))
    reject('free_contains_fixed',lambda d:d['free_edge_variables'].__setitem__(0,d['fixed_units'][0]['variable']))
    reject('wrong_moved_count',lambda d:d.update(moved_coordinate_indices=0))
    reject('symmetry_claim',lambda d:d.update(no_symmetry_branch_added=False))
    reject('wrong_output_count',lambda d:d.update(output_clauses=d['output_clauses']+1))
    # Rebind bytes deliberately: rejection must detect an extra constraint,
    # not merely a stale hash. The added disjoint edge is an unsafe symmetry
    # restriction for a fixed labeled K.
    original_cnf = resolve(original['cnf_path']).read_bytes()
    header,body = original_cnf.split(b'\n',1)
    altered = args.out/'extra_symmetry.cnf'
    altered.write_bytes(b'p cnf 817278 1624309\n'+body+f"{original['free_edge_variables'][0]} 0\n".encode('ascii'))
    reject('extra_symmetry_bound_bytes',lambda d:d.update(cnf_path=str(altered.resolve()),cnf_sha256=digest(altered)))
    # Exercise producer refusal before creating the requested output root.
    candidate = json.loads(resolve(original['candidate_path']).read_bytes())
    candidate['overlap_edges_outer_zero_based'][1] = candidate['overlap_edges_outer_zero_based'][0]
    bad = args.out/'duplicate_candidate.json'
    bad.write_text(json.dumps(candidate)+'\n',encoding='utf-8')
    rejected_output = args.out/'must_not_exist'
    proc = subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('fixed_overlap_cnf.py')),
                           '--candidate',str(bad),'--out',str(rejected_output)],capture_output=True,text=True)
    require(proc.returncode != 0 and not rejected_output.exists(),'Invalid producer input mutated output')
    cases.append(dict(name='duplicate_candidate_prewrite',rejected=True,returncode=proc.returncode,output_created=False))
    before = digest(args.manifest)
    proc = subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('fixed_overlap_cnf.py')),
                           '--candidate',original['candidate_path'],'--out',str(args.manifest.parent)],capture_output=True,text=True)
    require(proc.returncode != 0 and digest(args.manifest) == before,'Existing output not preserved')
    cases.append(dict(name='existing_output_preserved',rejected=True,returncode=proc.returncode))
    sources = [args.manifest,Path(__file__),Path(__file__).with_name('fixed_overlap_cnf.py'),Path(__file__).with_name('audit_fixed_overlap_cnf.py')]
    report = dict(status='FIXED_OVERLAP_CNF_MAPPING_AND_NEGATIVE_CONTROLS_PASS',
                  positive_status=positive['status'],negative_controls=len(cases),all_negative_controls_rejected=True,
                  cases=cases,inputs_sha256={str(p):digest(p) for p in sources},
                  solver_runs=0,witness_created=False,known_lp_excluded_control=original['known_lp_excluded_control'],
                  scope='Mapping/restriction and parser controls only; no SAT status or new exclusion claim.')
    with (args.out/'report.json').open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('cases','inputs_sha256')}))


if __name__ == '__main__':
    main()
