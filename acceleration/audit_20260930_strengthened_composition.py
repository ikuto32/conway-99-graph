"""Root independent review of exact strengthened branch composition.

No producer or existing byte-checker code is imported. Semantic prerequisites
are explicit previously independently checked results, not rederived here.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import io
import json
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'acceleration/results/20260930_independent_review/strengthened_four_branch_composition'
P = 'acceleration/results/'
PIN = {
 P+'20260930_four_branch_strengthened_preparation/summary.json': '1ce5c5935075b58030f768064507bf6e626f9d6b5026ce6d449ee33f27cc2488',
 P+'20260930_independent_review/unrestricted_full99_cnf/summary.json': '2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58',
 P+'20260930_independent_review/unrestricted_four_branch_cover/summary.json': 'ae44765cab81327f050b27d3ab75e6b952f44d5387a054a38029516e71516d34',
 P+'20260930_independent_review/unrestricted_pair_equalities_v2/summary.json': '1ebbff5e7313a97de6ce86aef3a9047ef856aae7ef0e8b1258eec216f1840237',
 P+'20260930_unrestricted_full99_cnf/instance.cnf': '7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138',
 P+'20260930_unrestricted_full99_cnf/model.json': '77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e',
 P+'20260930_unrestricted_four_branches/branches.json': '2520f51a2a5452f53caa64fe41a17fb2dedf29df989f7af7ceef0d55b2ce318c',
 P+'20260930_unrestricted_pair_equalities/run01/pair_equalities.units.cnfpart': '78b5be7dcbcee5e6593ffd8a047f88228f0383da70d0ebab5261348716466b95',
}
def need(ok, message):
    if not ok:
        raise ValueError(message)
def digest(path):
    with Path(path).open('rb') as stream:
        return sha256(stream.read()).hexdigest()
def compare(source, actual, suffix, base_header, new_header):
    need(source.readline() == base_header, 'base header')
    need(actual.readline() == new_header, 'composed header')
    count = 0
    while True:
        block = source.read(65536)
        if not block:
            break
        need(actual.read(len(block)) == block, 'base body modified')
        count += len(block)
    need(actual.read() == suffix, 'suffix changed, missing, reordered, or extra bytes')
    return count
def main():
    OUT.mkdir(parents=True, exist_ok=False)
    bindings = {}
    def bind(name, expected=None):
        value = digest(ROOT/name)
        need(expected is None or value == expected, 'hash '+name)
        bindings[name] = value
        return ROOT/name
    def read(name, expected=None):
        return json.loads(bind(name, expected).read_bytes())
    for name, expected in PIN.items():
        bind(name, expected)
    prep = read(P+'20260930_four_branch_strengthened_preparation/summary.json')
    recipes = read(prep['recipes'], prep['recipes_sha256'])
    cover = read(P+'20260930_independent_review/unrestricted_four_branch_cover/summary.json')
    eq = read(P+'20260930_independent_review/unrestricted_pair_equalities_v2/summary.json')
    base_gate = read(P+'20260930_independent_review/unrestricted_full99_cnf/summary.json')
    need(base_gate['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS', 'base equivalence')
    need(cover['status']=='INDEPENDENT_UNRESTRICTED_FOUR_BRANCH_COVER_PASS', 'cover')
    need(eq['status']=='INDEPENDENT_UNRESTRICTED_PAIR_EQUALITY_UNITS_PASS', 'entailed equalities')
    base = ROOT/(P+'20260930_unrestricted_full99_cnf/instance.cnf')
    need(eq['base_cnf_sha256']==cover['base_cnf_sha256']==digest(base), 'common premise')
    original = read(P+'20260930_unrestricted_four_branches/branches.json')
    equality = bind(P+'20260930_unrestricted_pair_equalities/run01/pair_equalities.units.cnfpart').read_bytes()
    need(equality == b''.join(f'{v} 0\n'.encode() for v in eq['unit_literals']), 'approved equality order')
    need(len(eq['unit_literals'])==len(set(eq['unit_literals']))==4662, 'equality population')
    expected = {'a0':[44,-1,-2,-3], 'a1_complement':[44,-1,-2,3], 'a1_cross':[44,1,-2,-3], 'a2_crosses':[44,1,2,-3]}
    need(len(prep['branches'])==4 and {x['branch'] for x in prep['branches']}==set(expected), 'exact four branches')
    checked = []
    for entry in prep['branches']:
        name = entry['branch']
        old = [x for x in original['branches'] if x['branch']==name]
        need(len(old)==1 and old[0]['units']==expected[name], 'original branch literals')
        tail = bind(old[0]['suffix'],old[0]['suffix_sha256']).read_bytes()
        need(tail == b''.join(f'{v} 0\n'.encode() for v in expected[name]), 'branch bytes')
        actual = bind(entry['cnf'], entry['cnf_sha256'])
        gate = read(entry['independent_byte_gate']['path'],entry['independent_byte_gate']['sha256'])
        need(gate['status']=='INDEPENDENT_STRENGTHENED_FOUR_BRANCH_CNF_BYTES_PASS' and gate['branch_cnf_sha256']==digest(actual), 'separate byte gate')
        with base.open('rb') as src, actual.open('rb') as dst:
            count = compare(src,dst,equality+tail,b'p cnf 1186500 4136454\n',b'p cnf 1186500 4141120\n')
        checked.append(dict(branch=name,cnf=entry['cnf'],cnf_sha256=digest(actual),variables=1186500,clauses=4141120,units=expected[name],body_bytes_compared=count,independent_byte_gate=entry['independent_byte_gate']['path'],independent_byte_gate_sha256=entry['independent_byte_gate']['sha256']))
    src = b'p cnf 4 1\n1 -2 0\n'; suffix = b'3 0\n4 0\n'; good = b'p cnf 4 3\n1 -2 0\n'+suffix
    compare(io.BytesIO(src),io.BytesIO(good),suffix,b'p cnf 4 1\n',b'p cnf 4 3\n')
    rejected=[]
    bads={'header':good.replace(b'4 3',b'4 2'),'body':good.replace(b'1 -2',b'1 2'),'sign':good.replace(b'3 0',b'-3 0'),'order':good[:-8]+b'4 0\n3 0\n','missing':good[:-4],'extra':good+b'1 0\n'}
    for name,bad in bads.items():
        try:
            compare(io.BytesIO(src),io.BytesIO(bad),suffix,b'p cnf 4 1\n',b'p cnf 4 3\n')
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('corrupted control accepted: '+name)
    bind(Path(__file__).relative_to(ROOT).as_posix());bind('uv.lock')
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'stable artifacts')
    report=dict(status='INDEPENDENT_STRENGTHENED_FOUR_BRANCH_COMPOSITION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),verifier='/root independent composition reviewer',inputs_sha256=bindings,branches=checked,controls=dict(positive_pass=True,rejected=rejected),derivation='Let F be the exact unrestricted CNF and E its independently checked logical consequence of4662units. For each approved branch conjunction B_i, F and B_i entails E, so F and B_i is equivalent to F and E and B_i. The checked fourbranch disjunction therefore retains unrestricted satisfiability equivalence. Exact raw byte comparison verifies these are precisely the four prepared formulas.',shared_components=['Prior independent base equivalence, equality entailment and coverage gates are explicit premises.','This implementation imports no producer or prior bytechecker code. Python standard library hashes and exact byte comparison are trusted.'],limitations=['No SAT or UNSAT result. No performance improvement established.','No reapproval of all prerequisite mathematics; authenticated earlier independent audits are reused.'],target_resolution=False,solver_calls=0,external_review=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],sha256=digest(OUT/'summary.json'))))
if __name__=='__main__':
    main()
