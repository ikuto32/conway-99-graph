"""Calibrate the independent box-augmented SAT checker without launching SAT."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import audit_20260930_gram_box_nogood_v1 as box

ROOT,need,digest,key = box.ROOT,box.need,box.digest,box.key


def save(path,data):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(data,stream,indent=2)
        stream.write('\n')


def main():
    out = ROOT/'acceleration/results/20260930_rook_box_checker_controls'
    out.mkdir(parents=True,exist_ok=False)
    base = ROOT/'acceleration/results/20260930_rook_free_internal_sat/instance.cnf'
    model = ROOT/'acceleration/results/20260930_rook_free_internal_sat/model.json'
    gate = ROOT/'acceleration/results/20260930_rook_free_internal_sat/independent_cnf_encoding.json'
    cert = ROOT/'acceleration/results/20260930_rook_gram_box_cut_initial/certificate.json'
    audit = ROOT/'acceleration/results/20260930_rook_gram_box_cut_initial/independent_box_nogood.json'
    assignment = ROOT/'acceleration/results/20260930_rook_lazy_wave01/round_01/solver/model.json'
    prior = ROOT/'acceleration/results/20260930_rook_lazy_wave01/round_01/independent_sat/summary.json'
    checker = ROOT/'acceleration/audit_20260930_rook_box_augmented_sat_v1.py'
    need(digest(audit) == 'd336249f1ccdd91d9f5b8399faee56a8a589ac98d3ab9eb445e22b5ae1e09251','initial box gate')
    prior_record = json.loads(prior.read_bytes())
    need(prior_record['assignment_sha256'] == digest(assignment) and prior_record['status'] == 'INDEPENDENT_AUGMENTED_ROOK_WINDOW_SAT_PASS','previous known-valid SAT fixture')
    certificate = json.loads(cert.read_bytes())
    cuts = [dict(certificate=key(cert),certificate_sha256=digest(cert),audit=key(audit),audit_sha256=digest(audit),clause=certificate['nogood_clause'])]
    cuts_path = out/'ordered_cuts.json'
    save(cuts_path,cuts)
    cnf = out/'instance.cnf'
    with base.open('rb') as source,cnf.open('xb') as target:
        need(source.readline().split() == [b'p',b'cnf',b'30420',b'3689820'],'base header')
        target.write(b'p cnf 30420 3689821\n')
        for block in iter(lambda:source.read(1024*1024),b''):
            target.write(block)
        target.write((' '.join(map(str,certificate['nogood_clause']))+' 0\n').encode('ascii'))
    corrupt = json.loads(assignment.read_bytes())
    corrupt['assignment'] = [-literal if abs(literal) == 1 else literal for literal in corrupt['assignment']]
    bad_assignment = out/'corrupt_assignment.json'
    save(bad_assignment,corrupt)
    bad_cuts = json.loads(json.dumps(cuts))
    bad_cuts[0]['clause'][0] *= -1
    bad_cuts_path = out/'corrupt_ordered_cuts.json'
    save(bad_cuts_path,bad_cuts)
    records = []
    for name,model_assignment,ordered,expect_success in (
        ('positive_known_sat',assignment,cuts_path,True),('corrupt_single_edge',bad_assignment,cuts_path,False),
        ('corrupt_signed_clause',assignment,bad_cuts_path,False)):
        command = [sys.executable,str(checker),'--base-cnf',str(base),'--augmented-cnf',str(cnf),'--model',str(model),
                   '--assignment',str(model_assignment),'--ordered-cuts',str(ordered),'--encoding-audit',str(gate),
                   '--encoding-audit-sha256','a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0','--out',str(out/name)]
        run = subprocess.run(command,cwd=ROOT,capture_output=True)
        (out/(name+'.stdout.log')).write_bytes(run.stdout)
        (out/(name+'.stderr.log')).write_bytes(run.stderr)
        need((run.returncode == 0) == expect_success,'unexpected checker calibration outcome: '+name)
        records.append(dict(case=name,expected_success=expect_success,exit_code=run.returncode,command=command,
                            stdout_sha256=digest(out/(name+'.stdout.log')),stderr_sha256=digest(out/(name+'.stderr.log')),
                            summary=key(out/name/'summary.json') if expect_success else None,
                            summary_null_reason=None if expect_success else 'Deliberately corrupted input rejected before any successful report'))
    report = dict(status='INDEPENDENT_BOX_AUGMENTED_SAT_CHECKER_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
                  positive_complete_sat_artifacts=1,corrupted_artifacts_rejected=2,records=records,
                  inputs_sha256={key(p):digest(p) for p in (Path(__file__),checker,base,model,gate,cert,audit,assignment,prior,cuts_path,cnf,bad_assignment,bad_cuts_path,ROOT/'uv.lock')},
                  solver_launched=False,producer_imported=False,target_resolution=False,external_review=False,
                  scope='Calibration of independently authored full box-augmented SAT artifact checker using one previously verified complete assignment and two corrupted inputs')
    save(out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))


if __name__ == '__main__':
    main()
