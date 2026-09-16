"""Sequential bounded positive-control probes, one CP-SAT worker at a time."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys


def main():
    records = []
    input_sha = hashlib.sha256(Path('scratch_resume_integral_compression.json').read_bytes()).hexdigest()
    repair_path = Path('scratch_resume_uniform_fibre_incidence_repair_checkpoint.json')
    invalid = set(json.loads(repair_path.read_text())['invalid_source_indices']) if repair_path.exists() else set()
    for fi in range(21):
        path = Path(f'scratch_resume_uniform_fibre_incidence_f{fi}_q16.json')
        old = json.loads(path.read_text()) if path.exists() else None
        reuse = (old is not None and old.get('input_sha256') == input_sha
                 and old.get('source_index') == fi and old.get('q16_required') is True
                 and (fi not in invalid or old.get('model_version') == 2))
        if not reuse:
            done = subprocess.run([sys.executable, '-B', 'scratch_resume_uniform_fibre_incidence.py',
                                   '--source', str(fi), '--seconds', '15', '--q16'],
                                  capture_output=True, text=True)
            if done.returncode:
                raise RuntimeError(done.stderr)
        item = json.loads(path.read_text())
        record = {'source_index': fi, 'status': item['status'], 'reused': reuse,
                  'elapsed_seconds': item['elapsed_seconds'],
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        records.append(record)
        manifest = {'status': 'COMPLETE' if fi == 20 else 'PARTIAL',
                    'input_sha256': input_sha,
                    'scope': 'Independent local fibre controls, not simultaneous incidence or adjacency.',
                    'records': records}
        Path('scratch_resume_uniform_fibre_incidence_all.json').write_text(json.dumps(manifest, indent=2)+'\n')
        print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
