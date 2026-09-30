"""Freeze an explicit metadata-only supplement for independent publication review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20261001_'
OUT = B + 'resume/twentyninth_publication_supplement.json'

def main():
    paths = [
        '.gitattributes', 'CLAIMS.yaml', 'README.md', 'ACTIVE_RESEARCH.md',
        'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md',
        'acceleration/stage_20261001_twentyninth_evidence.py',
        'acceleration/prepare_20261001_twentyninth_stager.py',
        B + 'twentyninth_stager_preparation/summary.json',
        'acceleration/prepare_20261001_twentyninth_catalog_source.py',
        B + 'twentyninth_catalog_source_preparation/summary.json',
        'acceleration/record_20261001_twentyninth_precommit.py',
        B + 'resume/twentyninth_precommit_checks.json',
        B + 'resume/twentyninth_precommit_validation.json',
        B + 'resume/twentyninth_registry.stdout.log',
        B + 'resume/twentyninth_registry.stderr.log',
        B + 'resume/twentyninth_syntax.stdout.log',
        B + 'resume/twentyninth_syntax.stderr.log',
        B + 'resume/twentyeighth_publication_ci_observation.json',
        'acceleration/audit_20261001_twentyninth_publication_metadata.py',
        'acceleration/audit_20261001_twentyninth_publication_metadata_spec.md',
        'acceleration/audit_20261001_twentyninth_publication_metadata_v2.py',
        'acceleration/audit_20261001_twentyninth_publication_metadata_v2_spec.md',
        Path(__file__).relative_to(ROOT).as_posix(), OUT,
    ]
    assert len(paths) == len(set(paths))
    hashes = {}
    for p in paths:
        assert not any(x in p.lower() for x in ('batch03', 'batch04', 'prompt.md', 'hadamard_oriented_unknown'))
        if p == OUT:
            continue  # Identity of the finished manifest is supplied to the auditor.
        q = ROOT / p
        assert q.is_file() and q.stat().st_size <= 10 * 1024**2
        with q.open('rb') as f:
            hashes[p] = hashlib.file_digest(f, 'sha256').hexdigest()
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), paths=sorted(paths),
        inputs_sha256=hashes, scope='Explicit wave29 publication metadata; no mathematical verification or Git mutation.',
        self_hash=None, self_hash_reason='The completed manifest is SHA256-pinned by its independent checking command.')
    with (ROOT / OUT).open('x', encoding='utf8', newline='\n') as f:
        json.dump(result, f, indent=2); f.write('\n')
    print(json.dumps(dict(path=OUT, paths=len(paths), sha256=hashlib.sha256((ROOT / OUT).read_bytes()).hexdigest())))

if __name__ == '__main__':
    main()
