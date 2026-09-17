"""Record and execute the frozen September 16 shortlist, without changing it."""
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'acceleration/results/20260917_resume'


def stamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(name, data):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def main():
    command = [sys.executable, '-B', 'acceleration/evaluate_fresh_star_shortlist.py',
        '--ranking', 'acceleration/results/20260916_fresh_star_rank_round3/summary.json',
        '--ranking-audit', 'acceleration/results/20260916_fresh_star_rank_round3/audit.json',
        '--baseline-star-audit', 'acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/audit.json',
        '--out', 'acceleration/results/20260917_fresh_star_shortlist',
        '--max-candidates', '16', '--selection', 'union', '--seconds', '30', '--audit-seconds', '60']
    paths = ['pyproject.toml', 'uv.lock', 'acceleration/run_20260917_fresh_wave.py',
        'acceleration/evaluate_fresh_star_shortlist.py',
        'acceleration/results/20260916_star_guided_round3_checkpoint.json',
        'acceleration/results/20260917_resume/certificate_controls.json',
        'acceleration/results/20260917_resume/shortlist_controls.json',
        'acceleration/results/20260917_resume/checkpoint_controls.json']
    for i, value in enumerate(command):
        if value in ('--ranking', '--ranking-audit', '--baseline-star-audit'):
            paths.append(command[i+1])
    manifest = dict(schema_version=1, created_at=stamp(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        working_tree_additions_explicitly_hashed=True, cwd=str(ROOT), command=command,
        question='Does the previously frozen union-16 shortlist improve the star-marginal bound or survive exact fixed-K exclusion?',
        scope='16 distinct labeled overlap configurations from 128 GPU-ranked members of the saved 8904-member cross-cycle family; no unrestricted coverage.',
        selection='Frozen upper-8/lower-8 union, filled by upper ranking to 16; no post-outcome reselection.',
        success='A strict merit improvement requires exact upper < incumbent exact lower. A target graph requires independent full99 SRG validation.',
        falsification='Exact positive star certificate with independently complete domains excludes only its fixed K.',
        thresholds={'star_LP_seconds':30,'independent_pair_seconds':60,'edge_audit_tolerance':1e-7,
            'strict_improvement':'exact rational strict inequality','certificate_sign':'exact integer gap > 0'},
        limits='One 16-case wave. Frozen native node/domain/time limits and per-subprocess wall cap are recorded by evaluator manifest. Failure remains pending and preserved.',
        python=sys.version, platform=platform.platform(), processor=platform.processor(),
        dependencies={p:importlib.metadata.version(p) for p in ('numpy','scipy','highspy','PyYAML','jsonschema','tqdm')},
        inputs_sha256={p:digest(ROOT/p) for p in paths},
        target_resolution='UNKNOWN', overall_search_coverage='UNKNOWN; no validated denominator',
        independent_review='Separate reviewer receives raw candidate, domain and certificate artifacts; not producer agreement.')
    save('wave_manifest.json', manifest)
    # Keep original saved artifacts immutable; every invocation has a new output.
    for name, cmd in [('preflight',command+['--validate-only']),('evaluation',command)]:
        started=stamp()
        with (OUT/(name+'.txt')).open('x', encoding='utf-8') as log:
            result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=False)
        save(name+'_receipt.json',dict(command=cmd,cwd=str(ROOT),started_at=started,finished_at=stamp(),
            returncode=result.returncode,log_path=(OUT/(name+'.txt')).relative_to(ROOT).as_posix(),
            log_sha256=digest(OUT/(name+'.txt')),mathematical_conclusion_from_exit_code=False))
        print(json.dumps(dict(stage=name,returncode=result.returncode)),flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
