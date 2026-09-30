"""Read-only diagnosis of the frozen v2 public-CLI JSON resume mismatch."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import theory_20260930_factor_permutation_annealer_v2 as engine

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/'acceleration/results/20260930_factor_annealer_pilot'
FAILED = ROOT/'acceleration/results/20260930_factor_annealer_cooling'


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def differences(a, b, path='$'):
    if type(a) is not type(b):
        return [dict(path=path, saved_type=type(a).__name__, live_type=type(b).__name__,
                     saved_value=a, live_value=b)]
    if isinstance(a, dict):
        if set(a) != set(b): return [dict(path=path, saved_keys=sorted(a), live_keys=sorted(b))]
        return [item for k in a for item in differences(a[k], b[k], path+'.'+k)]
    if isinstance(a, (list, tuple)):
        if len(a) != len(b): return [dict(path=path, saved_length=len(a), live_length=len(b))]
        return [item for i, (x, y) in enumerate(zip(a, b)) for item in differences(x, y, path+'['+str(i)+']')]
    return [] if a == b else [dict(path=path, saved_value=a, live_value=b)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cases = []; paths = [Path(__file__), Path(engine.__file__), engine.SOURCE, engine.EXE, FAILED/'summary.json']
    for core in ('shift6', 'six_prism'):
        checkpoint = OLD/(core+'_T1')/'checkpoint_00007.json'
        previous = json.loads(checkpoint.read_bytes()); live = engine.problem(engine.core_data(core)[0])
        diff = differences(previous['problem'], live)
        canonical = json.loads(json.dumps(live))
        assert previous['objective_version'] == engine.VERSION
        assert previous['problem'] != live and previous['problem'] == canonical
        assert len(diff) == 180 and all(item['path'].startswith('$.edges[') and item['saved_type'] == 'list' and item['live_type'] == 'tuple' and item['saved_value'] == list(item['live_value']) for item in diff)
        folder = FAILED/(core+'_T0_25'); failure = folder/'failure.json'; paths += [checkpoint, folder/'manifest.json', failure]
        assert json.loads(failure.read_bytes())['error'] == 'resume domain/objective binding'
        assert not list(folder.glob('chunk_*')) and not list(folder.glob('checkpoint_*'))
        cases.append(dict(core=core, checkpoint=key(checkpoint), checkpoint_sha256=digest(checkpoint),
            literal_python_problem_equality=False, objective_version_equal=True,
            JSON_canonical_problem_equality=True, type_only_differences=diff,
            native_chunk_artifacts=0, research_proposals=0,
            limitation='No native transition was run or recalibrated; this is a Python serialization-boundary diagnosis.'))
    report = dict(status='CANDIDATE_PUBLIC_RESUME_JSON_TYPE_MISMATCH_REPRODUCED',
        timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        inputs_sha256={key(p): digest(p) for p in paths}, cases=cases, independent_approval=False,
        exact_issue='Saved JSON edge pairs are lists; live problem() edge pairs are tuples. All360 pair values and every other problem field agree after JSON normalization.',
        affected_scope='Frozen v2 run --resume public Python orchestration; not integer GPU deltas, native split replay, or previously saved objective values.',
        proposed_narrow_fix='In a new version only, compare canonical serialized problem values and add an actual disk-checkpoint public-CLI resume control before research.',
        source_or_checkpoint_modified=False, native_calls=0, solver_calls=0, target_resolution=False)
    save(args.out/'summary.json', report)
    print(json.dumps(dict(status=report['status'], sha256=digest(args.out/'summary.json'))))


if __name__ == '__main__': main()
