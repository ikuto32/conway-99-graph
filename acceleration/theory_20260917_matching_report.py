"""Summarize the saved pilot without treating the producer as independent review."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'acceleration/results/20260917_theory/matching_baseline18481'


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def save(name, obj):
    with (OUT/name).open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def main():
    pair_path = ROOT/'acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/pairs.json'
    summary = json.loads((OUT/'summary.json').read_bytes())
    pairs = json.loads(pair_path.read_bytes())
    initial, after_pair, unique, after_both = 0, 0, 0, 0
    reasons = Counter()
    compact = None
    for row in summary['vertices']:
        u = row['outer_vertex']
        surviving_pair = set(pairs['surviving_domain_ids'][u])
        initial += row['original_choices']
        after_pair += len(surviving_pair)
        unique += len(surviving_pair & set(row['removed_domain_ids']))
        after_both += len(surviving_pair & set(row['survivor_domain_ids']))
        raw = json.loads(Path(row['output_path']).read_bytes())
        for r in raw['results']:
            if r['matching_count']:
                continue
            nodes = r['unmatched_vertices_full99']
            degree = Counter(v for e in r['allowed_edges_full99'] for v in e)
            isolated = [v for v in nodes if degree[v] == 0]
            reasons['isolated_free_vertex' if isolated else 'no_isolated_free_vertex'] += 1
            if compact is None and isolated and r['domain_id'] in surviving_pair:
                compact = dict(outer_vertex=u, domain_id=r['domain_id'], mask_hex=r['mask_hex'],
                    isolated_unmatched_full99_vertex=isolated[0],
                    original_pair_ac_surviving=True, raw_record=r,
                    raw_path=row['output_path'], raw_sha256=row['output_sha256'])
    save('comparison.json', dict(status='CANDIDATE_DESCRIPTIVE_COMPARISON',
        created_at=datetime.now(timezone.utc).isoformat(),
        summary_sha256=digest(OUT/'summary.json'), pair_path=str(pair_path), pair_sha256=digest(pair_path),
        original_choices=initial, existing_pair_ac_survivor_choices=after_pair,
        matching_rejected_choices_among_pair_ac_survivors=unique,
        survive_both_without_further_propagation=after_both,
        rejected_matching_graph_classification=dict(reasons),
        compact_strict_strengthening_witness=compact,
        independent_verification=False,
        limitations='No new propagation or global completion. The matching filter is a necessary relaxation, and counts alone do not exclude K.'))
    command = 'uv run --frozen --offline python -B acceleration/theory_20260917_triangle_matching.py --candidate acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json --domains acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/stars.json --domain-audit acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/independent_pair_audit.json --out acceleration/results/20260917_theory/matching_baseline18481 --seconds 300'
    save('execution_receipt.json', dict(schema_version=1, created_at=datetime.now(timezone.utc).isoformat(),
        source_commit=json.loads((OUT/'manifest.json').read_bytes())['source_commit'],
        working_directory=str(ROOT), command=command,
        environment={'UV_CACHE_DIR': str(ROOT/'.uv-cache-20260917'),
                     'UV_PROJECT_ENVIRONMENT': None,
                     'UV_PROJECT_ENVIRONMENT_reason': 'Not set during successful producer execution; uv used preexisting default .venv.'},
        execution_result={'returncode':0, 'elapsed_compute_seconds':summary['elapsed_seconds'],
                          'terminal_tool_chunk_id':'68b201', 'created_outputs':84},
        preflight_failures=[
            {'command':command.replace(' --offline',''), 'environment':{'UV_CACHE_DIR':None},
             'exitcode':1, 'reason':'Default UV cache failed to initialize, Windows error183; producer did not execute.',
             'tool_chunk_id':'b49375'},
            {'command':command.replace(' --offline',''), 'environment':{'UV_CACHE_DIR':str(ROOT/'.uv-cache-theory')},
             'exitcode':1, 'reason':'Cache lacked jsonschema-specifications==2025.9.1 and sandbox socket access blocked download, error10013; producer did not execute.',
             'tool_chunk_id':'cbd302'}],
        logs={'availability':'MISSING','path':None,
              'reason':'Terminal output was returned by tool but not redirected to a repository log; failure text and tool chunk IDs preserved above.'},
        deviation={'recorded_manifest_command_omitted':['--offline','UV_CACHE_DIR'],
                   'correct_actual_command_recorded_here':True,
                   'default_environment_sync':'uv reported Installed9 packages in66ms in existing .venv; no new environment directory created. Root instructed future work to use established build/research-venv after run had finished.',
                   'past_environment_contents_before_sync':None,
                   'past_environment_contents_reason':'No pre-sync environment inventory was recorded; no assertion of byte-identical historical environment.'},
        producer_source_sha256=digest(ROOT/'acceleration/theory_20260917_triangle_matching.py'),
        run_environment_versions={'python':sys.version, 'tqdm':version('tqdm'),
            'uv':subprocess.check_output(['uv','--version'],text=True).strip(),
            'platform':platform.platform()},
        output_sha256={p.name:digest(p) for p in (OUT/'manifest.json', OUT/'controls.json', OUT/'summary.json', OUT/'comparison.json')},
        result='CANDIDATE; independent verification pending',
        artifact_availability='LOCAL_ONLY', retrieval='Shared repository working tree; publication and immutable commit binding managed by root.'))


if __name__ == '__main__':
    main()
