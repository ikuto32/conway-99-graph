"""Bind the preserved metadata failure and subsequent independent SAT replay."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    report_path = 'acceleration/results/20260930_independent_review/rook_orbit_sat_replay_v2/summary.json'
    report = json.loads((ROOT/report_path).read_bytes())
    if report['status'] != 'INDEPENDENT_ORBIT_AUGMENTED_ROOK_WINDOW_SAT_PASS':
        raise ValueError('successful complete SAT replay required')
    paths = [
        'acceleration/audit_20260930_rook_orbit_sat.py',
        'acceleration/audit_20260930_rook_orbit_sat_v2.py',
        'acceleration/results/20260930_independent_review/rook_orbit_sat_calibration/summary.json',
        'acceleration/results/20260930_independent_review/rook_orbit_sat_calibration_v2/summary.json',
        'acceleration/results/20260930_rook_orbit_solver_pilot/independent_sat.log',
        'acceleration/results/20260930_rook_orbit_solver_pilot/summary.json',
        'acceleration/results/20260930_rook_orbit_solver_pilot/main/model.json',
        'acceleration/results/20260930_rook_orbit_solver_pilot/instance.cnf',
        'acceleration/results/20260930_independent_review/rook_cut_orbits/summary.json',
        report_path,report['raw_graph_path'],
        Path(__file__).relative_to(ROOT).as_posix(),'uv.lock']
    record = dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
        inputs_sha256={path:digest(path) for path in paths},
        original_attempt='CHECKER_INPUT_METADATA_ERROR_BEFORE_SAT_VALIDATION',
        original_failure='The exact encoding audit stored Windows backslash paths while the initial checker looked up normalized forward-slash keys.',
        correction='New version normalizes absolute/relative and slash conventions, checks conflicting aliases, and pins exact base/model hashes from the original independent encoding gate.',
        preserved=['Original source and successful finite controls','Original failed invocation/log','Actual solver cleanup exit3221226505','Raw complete SAT assignment'],
        impact='No mathematical orbit cut was invalidated. The first replay established no SAT conclusion. The new replay checks the same saved complete assignment without launching or retrying the solver.',
        corrected_replay='INDEPENDENT_ORBIT_AUGMENTED_ROOK_WINDOW_SAT_PASS',
        clause_checks=report['checked_clauses'],assignment_variables=report['variables'],added_orbit_clauses=report['appended_clauses'],
        raw_local_graph_sha256=report['raw_graph_sha256'],
        solver_launched=False,target_resolution=False,external_review=False,
        statement='A59vertex local witness satisfies the exact pinned base and all352 independently checked orbit clauses; no target completion or family exclusion follows.')
    path = ROOT/'acceleration/results/20260930_independent_review/rook_orbit_sat_replay_v2/correction_record.json'
    with path.open('x',encoding='utf-8') as stream:
        json.dump(record,stream,indent=2); stream.write('\n')
    print(json.dumps(dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path))))


if __name__ == '__main__':
    main()
