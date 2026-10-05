"""Compile research sources without execution; authenticate preserved parse failures."""
from pathlib import Path
import hashlib
import json


# These bytes are historical evidence, not runnable tools. Never exempt a pattern
# or every SyntaxError: a new/changed source requires a separate reviewed record.
PRESERVED_FAILURES = {
    'acceleration/theory_20260930_count_interval_frechet.py': {
        'sha256': 'df9cb31a836e8dada21d5e4eb425cfa2fca7b7f40ae62efded76d3f259234850',
        'failure_path': 'acceleration/results/20260930_count_interval_frechet_parse_failure/failure.json',
        'failure_sha256': 'd80c548a7ac24b791b8a812a1a373f44712f4d4e58230abc55cb0c40aa01b9ae',
        'line': 21,
        'message': "expected 'else' after 'if' expression",
    },
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_sources(root, preserved=PRESERVED_FAILURES):
    root = Path(root).resolve()
    files = sorted(root.glob('*.py')) + sorted((root / 'acceleration').glob('*.py'))
    selected = {path.relative_to(root).as_posix(): path for path in files}
    absent = set(preserved) - set(selected)
    if absent:
        raise ValueError(f'Preserved failure source missing from syntax selection: {sorted(absent)}')
    compiled = 0
    observed = []
    for name, path in selected.items():
        data = path.read_bytes()
        expected = preserved.get(name)
        if expected is not None:
            if digest(data) != expected['sha256']:
                raise ValueError(f'Preserved source bytes changed: {name}')
            evidence = (root / expected['failure_path']).read_bytes()
            if digest(evidence) != expected['failure_sha256']:
                raise ValueError(f'Preserved failure receipt changed: {name}')
            receipt = json.loads(evidence)
            if receipt['source_sha256'] != expected['sha256'] or receipt['research_executed'] is not False:
                raise ValueError(f'Invalid preserved parse-failure provenance: {name}')
        try:
            compile(data, name, 'exec')
        except SyntaxError as error:
            if expected is None:
                raise
            if type(error) is not SyntaxError or error.lineno != expected['line'] or error.msg != expected['message']:
                raise ValueError(f'Preserved syntax failure changed: {name}') from error
            observed.append(name)
        else:
            if expected is not None:
                raise ValueError(f'Preserved source unexpectedly compiles: {name}')
            compiled += 1
    return dict(compiled_sources=compiled, authenticated_preserved_failures=observed,
                selected_sources=len(files), source_execution=False)


if __name__ == '__main__':
    print(json.dumps(check_sources(Path(__file__).resolve().parent), indent=2))
