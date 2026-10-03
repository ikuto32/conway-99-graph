"""Independent exact matrix/scalar phase audit; no producer imports or ranks."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'acceleration/results'
PINS = {
    ROOT/'acceleration/audit_20260930_balanced_phase_matrix_form.py': 'c1ebde514c1777b64a394763057a4a290e89fb432c9b1432326bd8a698526a33',
    B/'20260930_independent_review/balanced_phase_matrix_form/failure.json': 'cd37a1cbb091c3716a030a059d784894067c61c6fb2df3624e02bf41ffebc282',
    B/'20260930_balanced_phase_matrix_form/summary.json': 'fc54c19db014c6e0c952cddd8692cde96391701156d6a19ae683576b721212b8',
    B/'20260930_balanced_phase_matrix_form/matrix_identity_controls.json': '350af13c8d9593a98c012206a4f18271e6a3a695041822911e9341f9e160294a',
    ROOT/'acceleration/theory_20260930_balanced_phase_matrix_form.py': '3400e354d805e6bca126300652f7dfc1f1ab1aa34d5df7862df4818539a5f376',
    ROOT/'docs/DERIVATION_20260930_BALANCED_PHASE_MATRIX_FORM.md': 'e2a995adfbbe30bb20a79b12a103d57101e13c801882c059bf9ec2be85a7ec43',
    B/'20260930_hadamard20_support/six_prism.json': 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    B/'20260930_independent_review/hadamard_parity_support_cuts_sat/independent_projection.json': 'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',
    B/'20260930_hadamard_f3_phases/phase_system.json': 'aecf80f4f1c7cd29f821cb52ec502b810aa87fc8ff908ea38e2f36a69e416061',
    B/'20260930_independent_review/hadamard_general_f3_phase_necessity/summary.json': '30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
    B/'20260930_independent_review/hadamard_f3_phase_obstruction/summary.json': '0ccca8ba45e0ffa5ff0e1d8d7c051ffcbee3d9d30092fac5df33274d80dea346',
    B/'20260930_independent_review/hadamard_parity_support_cuts_sat/summary.json': '02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a',
    B/'20260930_independent_review/hadamard20_support_v2/summary.json': 'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
    ROOT/'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    ROOT/'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
}

def need(x, reason):
    if not x:
        raise ValueError(reason)

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def key(p):
    return p.resolve().relative_to(ROOT).as_posix()

def read(p):
    return json.loads(p.read_bytes())

def save(p, data):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def mul(a, b):
    return [[sum(x*y for x, y in zip(r, c, strict=True)) for c in zip(*b)] for r in a]

def transpose(a):
    return list(map(list, zip(*a)))

def matrix_value(L, S, T):
    U = [[x*y for x, y in zip(s, t, strict=True)] for s, t in zip(S, T, strict=True)]
    left, right = mul(L, transpose(T)), mul(U, transpose(S))
    return [[(x-y) % 3 for x, y in zip(a, b, strict=True)] for a, b in zip(left, right, strict=True)]

def expected(raw, projection):
    rawL = raw['L']
    need(len(rawL) == 12 and all(len(row) == 60 and set(row) <= {0, 1} for row in rawL), 'binary raw L')
    groups, copies = [], []
    for d in range(60):
        support = [a for a in range(12) if rawL[a][d]]
        need(len(support) == 6, 'six-support')
        if support not in groups:
            groups.append(support)
            copies.append([])
        copies[groups.index(support)].append(d)
    need(len(groups) == 20 and all(len(c) == 3 for c in copies), 'twenty triplicate groups')
    L = [[int(a in group) for group in groups] for a in range(12)]
    incidence = mul(L, transpose(L))
    need(incidence == [[10 if a == b else 0 if a ^ 1 == b else 5 for b in range(12)] for a in range(12)], 'literal support intersections')
    patterns = projection['selected_group_parity_patterns']
    need(len(patterns) == 20 and all(len(p) == 6 and p[0] == 0 and set(p) <= {0,1} and sum(p) == 3 for p in patterns), 'saved all-mixed parity branch')
    S = [[0]*20 for _ in range(12)]
    variables = []
    for g, support in enumerate(groups):
        for i, a in enumerate(support):
            S[a][g] = (-1)**patterns[g][i]
            variables.append((a, g))
    need(all(sum(S[a][g] for a in range(12)) == 0 for g in range(20)), 'signed column balance')
    gram = mul(S, transpose(S))
    need(gram == [[11*int(a == b)+int(a ^ 1 == b)-1 for b in range(12)] for a in range(12)], 'integer signed Gram')
    for a, b in combinations(range(12), 2):
        if a ^ 1 == b:
            continue
        need(sum(S[a][g] != S[b][g] for g in range(20) if L[a][g] and L[b][g]) == 3, 'saved branch disagreements')
    # Independent basis evaluations of generic matrix multiplication.
    rows = [[0]*120 for _ in range(144)]
    columns = [[0]*120 for _ in range(40)]
    for index, (a, g) in enumerate(variables):
        T = [[0]*20 for _ in range(12)]
        T[a][g] = 1
        value = matrix_value(L, S, T)
        for b in range(12):
            for c in range(12):
                rows[12*b+c][index] = value[b][c]
        for j in range(20):
            columns[2*j][index] = sum(T[b][j] for b in range(12)) % 3
            columns[2*j+1][index] = sum(S[b][j]*T[b][j] for b in range(12)) % 3
    # Independently rederive all scalar rows from the relative affine maps.
    scalar = {}
    id_of = {pair:i for i,pair in enumerate(variables)}
    for g, group in enumerate(groups):
        gauge = [0]*120
        gauge[id_of[group[0],g]] = 1
        scalar[('gauge', (), g, None)] = gauge
        for sign in [1, 2]:
            row = [int(j == g and S[a][g] % 3 == sign) for a,j in variables]
            scalar[('local_same_sign_sum', (), g, sign)] = row
    for a,b in combinations(range(12),2):
        if a ^ 1 == b:
            continue
        for parity, name in [(True, 'pair_odd_phase_sum'), (False, 'pair_even_phase_sum')]:
            row = [0]*120
            for g in range(20):
                if L[a][g] and L[b][g] and (S[a][g] != S[b][g]) == parity:
                    row[id_of[b,g]] += 1
                    row[id_of[a,g]] -= S[a][g]*S[b][g]
            scalar[(name,(a,b),None,None)] = [v % 3 for v in row]
    return dict(groups=groups, copies=copies, L=L, S=S, gram=gram, rows=rows, columns=columns, scalar=scalar,
                vector=[p for group in patterns for p in group])

def validate_artifact(artifact, e):
    need(artifact['L12x20'] == e['L'], 'artifact L')
    need(artifact['S12x20'] == e['S'], 'artifact S')
    need(artifact['integer_signed_Gram'] == e['gram'], 'artifact Gram')
    need(len(artifact['phase_matrix_rows']) == 144, 'ordered row count')
    for i,r in enumerate(artifact['phase_matrix_rows']):
        need(r['coordinates'] == [i//12, i%12] and r['coefficients'] == e['rows'][i], 'ordered coefficients')
    need(len(artifact['phase_column_sum_rows']) == 40, 'column sum count')
    for i,r in enumerate(artifact['phase_column_sum_rows']):
        need(r['group'] == i//2 and r['kind'] == ['sum_T','sum_S_times_T'][i%2] and r['coefficients'] == e['columns'][i], 'column sum coefficients')
    need(artifact['degenerate_null_vector'] == e['vector'], 'degenerate vector bytes')

def validate_system(system,e):
    need(system['groups'] == e['groups'], 'system groups')
    seen = set()
    for r in system['rows']:
        kind = r['kind']
        if kind in ['gauge_first_phase_zero', 'column_gauge']:
            kind = 'gauge'
        k = kind, tuple(r.get('coordinates',[])), r.get('group'), r.get('sign')
        need(k not in seen and k in e['scalar'], 'scalar row type/uniqueness '+str(k))
        need(r['coefficients'] == e['scalar'][k], 'scalar coefficient semantics')
        seen.add(k)
    need(seen == set(e['scalar']), 'complete scalar row coverage')
    for a,b in combinations(range(12),2):
        if a ^ 1 == b:
            need(not any(e['rows'][12*a+b]) and not any(e['rows'][12*b+a]), 'matched rows')
            continue
        O = e['scalar']['pair_odd_phase_sum',(a,b),None,None]
        E = e['scalar']['pair_even_phase_sum',(a,b),None,None]
        need(e['rows'][12*a+b] == [(x+y)%3 for x,y in zip(O,E)], 'ordered forward identity')
        need(e['rows'][12*b+a] == [(x-y)%3 for x,y in zip(O,E)], 'ordered reverse identity')
    need(all(not any(e['rows'][13*a]) for a in range(12)), 'diagonal rows')
    need(all(sum(x*y for x,y in zip(row,e['vector'])) % 3 == 0 for row in e['scalar'].values()), 'degenerate scalar solution')
    # Matrix equations have nongauged solutions; gauges are explicitly extra.
    v = [0]*120
    for i,a in enumerate(e['groups'][0]):
        v[i] = e['S'][a][0] % 3
    need(all(sum(x*y for x,y in zip(row,v))%3 == 0 for row in e['rows']+e['columns']), 'nongauged matrix-positive control')
    need(v[0] != 0, 'gauge is not implied')

def controls():
    patterns = [[0]*6]+[list(p) for p in product(range(2),repeat=6) if p[0] == 0 and sum(p) == 3]
    local_cases = shifts = 0
    for p in patterns:
        signs = [1-2*x for x in p]
        for t in product(range(3),repeat=6):
            A = sum(t[i] for i in range(6) if signs[i] == 1)%3
            B = sum(t[i] for i in range(6) if signs[i] == -1)%3
            plain, signed = sum(t)%3, sum(s*x for s,x in zip(signs,t))%3
            need((plain==signed==0) == (A==B==0), 'local invertible equivalence')
            need(A == 2*(plain+signed)%3 and B == 2*(plain-signed)%3, 'inverse coefficient 2')
            for shift in range(3):
                z = [(x-s*shift)%3 for x,s in zip(t,signs)]
                need(sum(z)%3 == plain and sum(s*x for s,x in zip(signs,z))%3 == signed, 'local gauge invariance')
                shifts += 1
            z = [(x-s*t[0])%3 for x,s in zip(t,signs)]
            need(z[0] == 0, 'first coordinate gauge')
            local_cases += 1
        need(sum(p)%3 == 0 and sum(s*x for s,x in zip(signs,p))%3 == 0 and p[0] == 0, 'general degenerate local solution')
    pair_bases = pair_degenerate = 0
    for sign_bits in product(range(2),repeat=10):
        sa = [1-2*x for x in sign_bits[:5]]
        sb = [1-2*x for x in sign_bits[5:]]
        for k in range(10):
            ta,tb = [0]*5,[0]*5
            (ta if k<5 else tb)[k%5] = 1
            O=E=0
            for i in range(5):
                relative = (tb[i]-sb[i]*sa[i]*ta[i])%3
                if sa[i] == sb[i]: E += relative
                else: O += relative
            fwd = sum(tb[i]-sa[i]*sb[i]*ta[i] for i in range(5))%3
            rev = sum(ta[i]-sa[i]*sb[i]*tb[i] for i in range(5))%3
            need(fwd == (O+E)%3 and rev == (O-E)%3, 'all sign/basis pair transformations')
            pair_bases += 1
        ta,tb = sign_bits[:5],sign_bits[5:]
        d = sum(a!=b for a,b in zip(ta,tb))
        r = [tb[i]-sa[i]*sb[i]*ta[i] for i in range(5)]
        need(r == [int(sa[i]!=sb[i]) for i in range(5)], 'exact degenerate relative phase')
        if d in [0,3]:
            need(sum(r)%3 == 0, 'degenerate pair solution')
            pair_degenerate += 1
    for O,E in product(range(3),repeat=2):
        fwd,rev = (O+E)%3,(O-E)%3
        need((fwd==rev==0) == (O==E==0), 'pair equation equivalence')
    need((1+2)%3 == 0 and (1-2)%3 != 0, 'one direction insufficient')
    row_sum_cases = []
    for z in range(11):
        value = 10+5*z-(10-z)
        need(value == 6*z and (value==0) == (z==0), 'integer row-sum implication')
        row_sum_cases.append(dict(z=z,integer_row_sum=value,mod3_row_sum=value%3))
    return dict(local_sign_patterns=11,local_phase_cases=local_cases,gauge_shift_cases=shifts,
                five_group_sign_patterns=1024,pair_basis_cases=pair_bases,degenerate_pair_profiles=pair_degenerate,
                invertible_sum_pairs=9,integer_row_sum_cases=row_sum_cases,
                caution='Finite controls calibrate universal written proof; no global parity enumeration or rank calculation.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    try:
        for p,h in PINS.items(): need(digest(p)==h,'input hash '+key(p))
        raw=read(B/'20260930_hadamard20_support/six_prism.json')
        projection=read(B/'20260930_independent_review/hadamard_parity_support_cuts_sat/independent_projection.json')
        artifact=read(B/'20260930_balanced_phase_matrix_form/matrix_identity_controls.json')
        system=read(B/'20260930_hadamard_f3_phases/phase_system.json')
        e=expected(raw,projection);validate_artifact(artifact,e);validate_system(system,e)
        calibrated=controls();save(out/'controls.json',calibrated)
        rejected=[]
        mutations=[('wrong_L',lambda x:x['L12x20'][0].__setitem__(0,1-x['L12x20'][0][0])),
                   ('wrong_S',lambda x:x['S12x20'][0].__setitem__(0,-x['S12x20'][0][0])),
                   ('wrong_Gram',lambda x:x['integer_signed_Gram'][0].__setitem__(0,9)),
                   ('wrong_ordered_coefficient',lambda x:x['phase_matrix_rows'][2]['coefficients'].__setitem__(0,(x['phase_matrix_rows'][2]['coefficients'][0]+1)%3)),
                   ('missing_ordered_row',lambda x:x['phase_matrix_rows'].pop()),
                   ('wrong_signed_column',lambda x:x['phase_column_sum_rows'][1]['coefficients'].__setitem__(1,(x['phase_column_sum_rows'][1]['coefficients'][1]+1)%3)),
                   ('wrong_degenerate_vector',lambda x:x['degenerate_null_vector'].__setitem__(0,1))]
        for name,change in mutations:
            bad=copy.deepcopy(artifact);change(bad)
            try:validate_artifact(bad,e)
            except ValueError as ex:rejected.append(dict(name=name,rejection=str(ex)))
            else:raise ValueError('accepted corruption '+name)
        for name,change in [('missing_gauge',lambda x:x['rows'].pop(0)),
                            ('wrong_scalar_phase',lambda x:x['rows'][0]['coefficients'].__setitem__(0,2))]:
            bad=copy.deepcopy(system);change(bad)
            try:validate_system(bad,e)
            except ValueError as ex:rejected.append(dict(name=name,rejection=str(ex)))
            else:raise ValueError('accepted scalar corruption '+name)
        # Dropping all-mixed column balance admits S=L, a counterexample to the signed-Gram conclusion.
        unbalanced_gram=mul(e['L'],transpose(e['L']))
        need(unbalanced_gram != e['gram'] and all(sum(row)==60 for row in unbalanced_gram),'all-mixed assumption counterexample')
        save(out/'corruptions.json',dict(rejected=rejected,without_column_balance=dict(S_equals_L=True,all_disagreements_zero=True,integer_row_sums=[sum(row) for row in unbalanced_gram])))
        save(out/'checked_coefficients.json',dict(groups=e['groups'],copies=e['copies'],L=e['L'],S=e['S'],integer_signed_Gram=e['gram'],ordered_matrix_coefficients=e['rows'],column_sum_coefficients=e['columns'],degenerate_vector=e['vector']))
        pins={key(p):h for p,h in PINS.items()}
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_BALANCED_PHASE_MATRIX_FORM.md']:pins[key(p)]=digest(p)
        timestamp=datetime.now(timezone.utc).isoformat()
        manifest=dict(timestamp=timestamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),elapsed_seconds=time.perf_counter()-start,inputs_sha256=pins,solver_calls=0,rank_calculations=0)
        save(out/'manifest.json',manifest)
        evidence={key(p):digest(p) for p in out.iterdir() if p.is_file()}
        claim=dict(id='C-FIXED-HADAMARD-BALANCED-PHASE-MATRIX-FORM',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
                   statement='On the fixed six-prism Hadamard support, for every normalized constant/mixed sign assignment the necessary scalar odd/even phase sums and local sums are equivalent over GF(3) to L T^T=(S entrywise T) S^T and the two column-sum equations, with all20 gauges retained. Every all-mixed parity projection satisfying zero-or-three disagreements has integer S S^T=11I+M-J and all60 disagreements three. For every allowed parity projection the parity-indicator T=(L-S)/2 is a degenerate matrix-and-gauge solution, not a valid mixed coloring when a mixed group exists.',
                   scope='Exact fixed-support conditional algebra; neither universal rank119 nor any family exclusion, full factor or target construction is asserted.',
                   assumptions=['Fixed20 distinct supports from the pinned six_prism L, each repeated three times in the raw60columns.','Normalized constant/mixed local parity patterns; zero-or-three pair disagreements for the signed-Gram and degenerate-solution implications.','Every stated matrix equation is over GF(3), except the signed-Gram identity and its integer row-sum proof.'],
                   dependencies=[dict(id='C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY',revision=1,relation='uses_result'),dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-BALANCED-PARITY-PROJECTION',revision=1,relation='uses_result'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-SAT-WITNESS',revision=1,relation='verification_dependency')],
                   dependency_scope='The actual selected parity witness is a finite coefficient calibration only, not a premise of the universal algebra.',
                   verifier='/root/structural_attack',producer='/root/state_literature_audit',discovery_contributor='/root',method='Independent written derivation, basis-vector matrix multiplication, complete raw coefficient comparison and exact finite controls.',
                   shared_components=['Pinned raw support/parity and earlier reviewed mathematical necessity statements.','Python standard-library exact integer, JSON and combinatorial primitives.','No producer or prior phase-checker code imported.'],
                   artifact_availability='LOCAL_ONLY',availability_reason='Workspace evidence pending parent publication.',external_review=None,external_review_reason='No external review asserted.',
                   limitations=['No universal phase-rank conclusion.','No sufficiency for local distinctness, full Gram, outside caps or residual D.','No factor or graph produced; no solver invoked.','Universal proof is conditional on the extra balanced fixed-support family, not an unrestricted target normalization.'],
                   created_at=timestamp,updated_at=timestamp,inputs_sha256=pins,evidence_sha256=evidence)
        save(out/'claim_binding.json',claim)
        report=dict(status='INDEPENDENT_BALANCED_PHASE_MATRIX_FORM_PASS',timestamp=timestamp,claim_id=claim['id'],claim_revision=1,inputs_sha256=pins,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},integer_Gram_entries=144,ordered_coefficient_rows=144,column_sum_rows=40,gauge_rows=20,phase_variables=120,corruptions_rejected=len(rejected),controls=calibrated,universal_rank119_proved=False,solver_calls=0,rank_calculations=0,scope=claim['scope'])
        save(out/'summary.json',report)
        print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'),claim_binding_sha256=digest(out/'claim_binding.json'))))
    except BaseException as ex:
        save(out/'failure.json',dict(error=repr(ex)))
        raise

if __name__=='__main__':main()
