"""Independent integer/full99 controls for the fixed-dual native ranker.

Complete domain sets are reused only through saved independent enumeration
proofs, exact input hashes, frozen native mask equality, and byte-identical
enumeration source. This control audit makes no new candidate exclusion claim.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time
from audit_phase1 import graph_rows

ROOT = Path(__file__).resolve().parents[1]
SCALE = 1 << 40

def resolve(p):
    return (ROOT / str(p).replace('\\', '/')).resolve()

def key(p):
    return resolve(p).relative_to(ROOT).as_posix()

def digest(p):
    return sha256(resolve(p).read_bytes()).hexdigest()

def require(ok, msg):
    if not ok:
        raise ValueError(msg)

def reference(candidate, domains, beta, gamma):
    edges, rows, _ = graph_rows(candidate)
    caps = rows[840:]
    require(len(caps) == 3486, 'Missing full99 cap rows')
    costs = [0]*1680
    for row, weight in zip(caps, gamma):
        for edge in row['terms']:
            costs[edge] += weight
    index = {tuple(e): i for i, e in enumerate(edges)}
    minima, minimizers = [], []
    for u, masks in enumerate(domains):
        values = []
        for mask in masks:
            value = 0
            for v in range(84):
                if mask >> v & 1:
                    e = index[tuple(sorted((u, v)))]
                    value += beta[e] + costs[e] if u < v else -beta[e]
            values.append(value)
        minimum = min(values)
        minima.append(minimum)
        minimizers.append(masks[values.index(minimum)])
    rhs = sum(row['target']*w for row,w in zip(caps, gamma))
    return minima, minimizers, rhs

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory', required=True)
    a = p.parse_args()
    directory = resolve(a.directory)
    report_path = directory/'audit.json'
    require(not report_path.exists(), 'Preserve previous QA')
    started, bindings = time.perf_counter(), {}
    def bind(p, expected=None):
        actual = digest(p)
        require(expected is None or actual == expected, 'Changed file: '+key(p))
        bindings[key(p)] = actual
        return actual
    native = ROOT/'acceleration/build/star_dual_batch.exe'
    source = ROOT/'acceleration/star_dual_batch.rs'
    parent = ROOT/'acceleration/star_domains_batch.rs'
    for path in (native, source, parent, __file__, ROOT/'acceleration/audit_phase1.py', ROOT/'acceleration/audit_certificate.py'):
        bind(path)
    parent_text, new_text = parent.read_text(), source.read_text()
    frozen_part = parent_text.split('type Result<T> =', 1)[1].split('\nstruct Event {', 1)[0].strip()
    copied_part = new_text.split('type Result<T> =', 1)[1].split('\nconst DENOMINATOR:', 1)[0].strip()
    require(frozen_part == copied_part, 'Enumeration/graph parser changed from frozen parent')
    bind(parent, '84be679f31ae0fc365dc51a2b05a60d0467fa660c9c72a3572b3681da887c482')
    controls_path = directory/'controls.json'
    controls = json.loads(controls_path.read_bytes()); bind(controls_path)
    candidates_path = directory/'candidates.txt'; bind(candidates_path)
    old_path = directory/'frozen_domains.json'; bind(old_path)
    old = json.loads(old_path.read_bytes())['results']
    candidates, domain_sets, associations = [], [], []
    for c, frozen in zip(controls, old):
        for field in ('candidate', 'domains', 'pair_audit'):
            bind(c[field+'_path'], c[field+'_sha256'])
        proof = json.loads(resolve(c['pair_audit_path']).read_bytes())
        require(proof['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and proof['complete_used_domains_verified'], 'Missing independent domain proof')
        for path, h in proof['inputs_sha256'].items():
            bind(path, h)
        pb = {key(path): h for path,h in proof['inputs_sha256'].items()}
        require(pb.get(key(c['domains_path'])) == c['domains_sha256'], 'Domain proof table association')
        candidate = json.loads(resolve(c['candidate_path']).read_bytes())
        bound_candidates = []
        for path in pb:
            if path.endswith('_candidate.json') or path.endswith('/best_candidate.json'):
                other = json.loads(resolve(path).read_bytes())
                if sorted(other.get('overlap_edges_outer_zero_based', [])) == sorted(candidate['overlap_edges_outer_zero_based']):
                    bound_candidates.append(path)
        require(len(bound_candidates) == 1, 'Missing/ambiguous independently bound graph identity')
        associations.append(dict(candidate_path=key(c['candidate_path']), proof_candidate_path=bound_candidates[0], exact_canonical_edge_identity=True))
        stars = json.loads(resolve(c['domains_path']).read_bytes())
        require(stars['complete_domain_enumeration'] is True and frozen['complete_domain_enumeration'] is True, 'Incomplete domain control')
        require([d['outer_vertex'] for d in stars['domains']] == list(range(84)), 'Wrong domain row order')
        sets = [[int(m,16) for m in row['domain_masks_hex']] for row in stars['domains']]
        require(sets == [[int(m,16) for m in row['domain_masks_hex']] for row in frozen['domains']], 'Frozen native full mask set parity')
        require([r['outer_vertex'] for r in proof['independently_reenumerated_domains']] == list(range(84)), 'Incomplete independent enumeration coverage')
        require([len(d) for d in sets] == [r['domain_size'] for r in proof['independently_reenumerated_domains']], 'Independent domain sizes differ')
        candidates.append(candidate); domain_sets.append(sets)
    require(len(candidates) == len(old) == 5, 'Expected5 controls')
    expected_tokens = ['C99OVERLAPS1', '5'] + [str(v) for c in candidates for e in sorted(c['overlap_edges_outer_zero_based']) for v in e]
    require(candidates_path.read_text().split() == expected_tokens, 'Candidate batch/order mismatch')
    weights_path = directory/'baseline_weights/dual.txt'; bind(weights_path)
    wm_path = directory/'baseline_weights/manifest.json'; bind(wm_path)
    wm = json.loads(wm_path.read_bytes())
    for path,h in wm['inputs_sha256'].items():
        bind(path,h)
    baseline = json.loads(resolve(wm['baseline_result_path']).read_bytes())
    tokens = weights_path.read_text().split()
    require(tokens[:4] == ['C99STARDUAL_DYADIC1','1680','3486',str(SCALE)], 'Wrong integer input format')
    weights = list(map(int,tokens[4:]))
    require(weights == [round(Fraction(v)*SCALE) for field in ('numeric_reciprocity_duals','numeric_cap_duals') for v in baseline[field]], 'Dyadic export differs')
    dyadic_path = directory/'pattern_weights.txt'
    pattern = [(((i*17+3)%17)-8)*(SCALE//8) for i in range(1680)] + [((i*7+2)%9)*(SCALE//8) for i in range(3486)]
    # Nonconstant signs and supports exercise both endpoint orientations.
    pattern[:1680] = [(((i*7+3)%17)-8)*(SCALE//8) for i in range(1680)]
    dyadic_path.write_text('C99STARDUAL_DYADIC1 1680 3486 '+str(SCALE)+'\n'+'\n'.join(map(str,pattern))+'\n', encoding='ascii')
    bind(dyadic_path)
    def run(input_path, dual_path, output, extra=()):
        return subprocess.run([str(native),str(input_path),str(dual_path),str(output),*map(str,extra)],capture_output=True,text=True,timeout=30)
    pattern_out = directory/'pattern_scores.json'
    done = run(candidates_path,dyadic_path,pattern_out)
    require(done.returncode == 0, done.stderr)
    checks = []
    for label, values, out in [('baseline',weights,directory/'baseline_scores.json'),('pattern',pattern,pattern_out)]:
        bind(out)
        native_result = json.loads(out.read_bytes())
        require(native_result['candidate_count'] == 5 and len(native_result['results']) == 5, 'Wrong result count')
        scores = []
        for candidate, domains, actual in zip(candidates,domain_sets,native_result['results']):
            minima, minimizers, rhs = reference(candidate,domains,values[:1680],values[1680:])
            require(actual['status'] == 'COMPLETE_HEURISTIC_SCORE' and actual['complete_domain_enumeration'], 'Unexpected unavailable control')
            require(actual['domain_counts'] == list(map(len,domains)), 'Native domain sizes differ')
            require(actual['vertex_minimum_numerators'] == minima, 'Wrong exact star minima')
            require([int(m,16) for m in actual['minimizing_masks_hex']] == minimizers, 'Wrong exact minimizing masks/tie order')
            require(actual['weighted_cap_rhs_numerator'] == rhs and actual['sum_vertex_minima_numerator'] == sum(minima), 'Wrong weighted RHS/min sum')
            require(actual['score_numerator'] == sum(minima)-rhs and actual['denominator'] == SCALE, 'Wrong exact score')
            scores.append(actual['score'])
        checks.append(dict(label=label,scores=scores,native_seconds=native_result['elapsed_seconds'],exact_minima_checked=420,full99_caps_checked=17430))
    negative = []
    negative_dir = directory/'negative_controls'; negative_dir.mkdir()
    base_input = candidates_path.read_text(); base_dual = weights_path.read_text()
    cases = [('bad_count',base_input.replace('C99OVERLAPS1 5','C99OVERLAPS1 0',1),base_dual,()),
             ('trailing_candidate',base_input+' 0',base_dual,()),
             ('missing_dual',base_input,' '.join(tokens[:-1]),()),
             ('trailing_dual',base_input,base_dual+' 0',()),
             ('nan_dual',base_input,' '.join(tokens[:4]+['NaN']+tokens[5:]),()),
             ('outside_beta',base_input,' '.join(tokens[:4]+[str(SCALE+1)]+tokens[5:]),()),
             ('negative_gamma',base_input,' '.join(tokens[:1684]+['-1']+tokens[1685:]),()),
             ('nonfinite_seconds',base_input,base_dual,('NaN',)),('zero_node_cap',base_input,base_dual,(1,0))]
    invalid_edges = base_input.split(); invalid_edges[2] = '84'
    cases.append(('invalid_edge',' '.join(invalid_edges),base_dual,()))
    for name, ci, di, args in cases:
        cp,dp,op = [negative_dir/(name+s) for s in ('.candidates','.dual','.output')]
        cp.write_text(ci);dp.write_text(di)
        r = run(cp,dp,op,args)
        require(r.returncode != 0 and not op.exists(), 'Negative control accepted: '+name)
        bind(cp);bind(dp)
        negative.append(dict(name=name,rejected=True,output_created=False))
    keep = negative_dir/'existing.output'; keep.write_text('preserve')
    r = run(candidates_path,weights_path,keep)
    require(r.returncode != 0 and keep.read_text() == 'preserve', 'Existing output changed')
    negative.append(dict(name='existing_output',rejected=True,output_preserved=True))
    caps = []
    for label,args in [('node',(1,1,20000)),('domain',(1,2000000,1)),('time',(1e-12,2000000,20000))]:
        out = directory/(label+'_cap.json')
        r = run(candidates_path,weights_path,out,args)
        require(r.returncode == 0,r.stderr)
        result = json.loads(out.read_bytes());bind(out)
        require(result['caps_reset_per_candidate'] and len(result['results']) == 5, 'Missing independent cap resets')
        require(all(v['status']=='UNAVAILABLE_INCOMPLETE_DOMAINS' and v['score'] is None and v['score_numerator'] is None and not v['complete_domain_enumeration'] for v in result['results']), 'Capped candidate got score')
        caps.append(dict(kind=label,candidates=5,all_scores_unavailable=True))
    report = dict(status='INDEPENDENT_FULL99_INTEGER_STAR_DUAL_CONTROLS_PASS',inputs_sha256=bindings,
                  exact_arithmetic='integer2^40; two dual vectors,5 real K,840 vertex minima',
                  complete_domain_set_identity=True,complete_enumeration_source_byte_identity=True,
                  independent_saved_full99_domain_proofs_reused=5,candidate_domain_associations=associations,checks=checks,negative_controls=negative,
                  cap_controls=caps,baseline_quantized_score=checks[0]['scores'][0],
                  baseline_original_numeric_dual=baseline['numeric_simplex_dual_lower'],
                  elapsed_seconds=time.perf_counter()-started,exclusions_claimed=0,
                  scope='Scorer correctness on10 real controls and strict CLI/cap behavior. Full future batch scores remain ranking data; no independent completeness replay or exclusion certificate for every future K.')
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(report['status'], 'seconds',round(report['elapsed_seconds'],3), 'SHA',digest(report_path))

if __name__ == '__main__':
    main()
