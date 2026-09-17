"""Calibration for independent whole-family ranking matrix builder."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from audit_20260917_whole_fresh_ranking import path, digest, key, compare_model, parse_binary, require
from audit_20260917_ranking_model import build_model


def main():
    out = path('acceleration/results/20260917_independent_review/whole_ranking_model_controls.json')
    require(not out.exists(), 'preserve prior controls')
    sources = [__file__, 'acceleration/audit_20260917_ranking_model.py', 'acceleration/audit_20260917_whole_fresh_ranking.py',
               'acceleration/review_star_pdhg_gpu.py', 'acceleration/results/20260916_fresh_star_rank_round3/summary.json']
    summary = json.loads(path(sources[-1]).read_bytes())
    row = next(r for r in summary['records'] if r['status'] == 'NUMERICALLY_SCORED')
    chunk = summary['chunks'][row['chunk_index']]
    sources += [row['candidate_path'],row['domains_path'],chunk['input_path']]
    candidate = json.loads(path(row['candidate_path']).read_bytes())
    domains = json.loads(path(row['domains_path']).read_bytes())
    _,models = parse_binary(chunk['input_path']); parsed = models[row['binary_candidate_index']]
    model = build_model(candidate, domains['domains'])
    controls = [dict(name='historical_exact_full_serialized_model',outcome='PASS',array_entries=compare_model(model,parsed))]
    for name in ('one_matrix_coefficient','one_rhs','one_offset'):
        bad = {k:v.copy() for k,v in model.items()}
        if name == 'one_matrix_coefficient': bad['A'].data[0] += 1
        if name == 'one_rhs': bad['b'][-1] += 1
        if name == 'one_offset': bad['offsets'][1] += 1
        try: compare_model(bad,parsed)
        except ValueError as e: controls.append(dict(name=name,outcome='REJECT',reason=str(e)))
        else: raise ValueError('corruption accepted '+name)
    bad_domains = deepcopy(domains['domains']); bad_domains[0]['domain_masks_hex'][0] = '0'
    try: build_model(candidate,bad_domains)
    except ValueError as e: controls.append(dict(name='zero_domain_mask',outcome='REJECT',reason=str(e)))
    else: raise ValueError('zero mask accepted')
    result = dict(status='INDEPENDENT_WHOLE_RANKING_MODEL_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        inputs_sha256={key(f):digest(f) for f in sources},command=[sys.executable]+sys.argv,
        candidate_index=row['proposal_index'],controls=controls,
        scope='Independent dense derivative model matches one historical serialized model; three matrix/schema corruptions and malformed domain rejected. No original-domain completeness or new ranking claim.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],controls=len(controls),sha256=digest(out))))


if __name__ == '__main__': main()
