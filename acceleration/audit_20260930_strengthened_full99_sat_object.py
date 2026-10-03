"""Independent strengthened full99 SAT-object wrapper; no producer imports.

Preserves and explicitly reuses the separately authored exact graph/native/CNF
checkers. Composed CNF bytes are checked against independently approved gates.
"""
import argparse
from datetime import datetime,timezone
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_unrestricted_full99_sat_object as unrestricted
import audit_20260930_full99_sat_object as common
import audit_20260930_strengthened_four_branch_bytes_v1 as bytecheck

ROOT=Path(__file__).resolve().parents[1]
need,digest,key,read,save=common.need,common.digest,common.key,common.read,common.save
HELPER_PINS={Path(unrestricted.__file__):'6b78545d53041382e9b134718637998e4d0083175640b70044f60f480bcbc200',
             Path(common.__file__):'65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c',
             Path(bytecheck.__file__):'62d10e4cc6f2b1427b656fae5b200febe8f118ea9e409dfa25d8bc10e921161d'}
OLD_CAL=ROOT/'acceleration/results/20260930_independent_review/unrestricted_full99_sat_object_calibration/summary.json'
OLD_CAL_SHA='1ae229a3a6a3d7dcf9cbc3c1c9a9a924facb2d5c343bbd683f838e27c8362a4f'
RECIPE=ROOT/'acceleration/results/20260930_unrestricted_four_branches/branches.json'
COVER=ROOT/'acceleration/results/20260930_independent_review/unrestricted_four_branch_cover/summary.json'
COVER_SHA='ae44765cab81327f050b27d3ab75e6b952f44d5387a054a38029516e71516d34'
EQUALITY=ROOT/'acceleration/results/20260930_unrestricted_pair_equalities/run01/pair_equalities.units.cnfpart'
EQUAL_GATE=ROOT/'acceleration/results/20260930_independent_review/unrestricted_pair_equalities_v2/summary.json'
EQUAL_GATE_SHA='1ebbff5e7313a97de6ce86aef3a9047ef856aae7ef0e8b1258eec216f1840237'


class Binding:
    def __init__(self):self.hashes={}
    def pin(self,path,expected=None):
        path=Path(path)
        if not path.is_absolute():path=ROOT/path
        observed=digest(path);need(expected is None or observed==expected,'input hash '+key(path));self.hashes[key(path)]=observed
        return path
    def load(self,path,expected=None):return read(self.pin(path,expected))
    def finish(self):
        self.pin(__file__)
        for path,expected in HELPER_PINS.items():self.pin(path,expected)
        self.pin(ROOT/'uv.lock')
        need(all(digest(ROOT/name)==value for name,value in self.hashes.items()),'stable checked artifacts')


def composed_inputs(args,binding):
    for path,expected in HELPER_PINS.items():binding.pin(path,expected)
    gate=binding.load(args.composition_gate,args.composition_gate_sha256)
    need(gate['status']=='INDEPENDENT_STRENGTHENED_FOUR_BRANCH_COMPOSITION_PASS','complete strengthened composition gate')
    cover=binding.load(COVER,COVER_SHA);equal=binding.load(EQUAL_GATE,EQUAL_GATE_SHA)
    need(cover['status']=='INDEPENDENT_UNRESTRICTED_FOUR_BRANCH_COVER_PASS' and equal['status']=='INDEPENDENT_UNRESTRICTED_PAIR_EQUALITY_UNITS_PASS','semantic prerequisite gates')
    encoding=binding.load(unrestricted.GATE,unrestricted.GATE_SHA)
    need(encoding['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS','original encoding gate')
    binding.pin(unrestricted.CNF,unrestricted.CNF_SHA)
    binding.pin(unrestricted.MODEL,unrestricted.MODEL_SHA)
    binding.pin(unrestricted.SCOPE,unrestricted.SCOPE_SHA)
    binding.pin(unrestricted.NORMALIZATION,unrestricted.NORMALIZATION_SHA)
    recipe=binding.load(RECIPE,cover['inputs_sha256'][key(RECIPE)])
    suffix=binding.pin(EQUALITY,equal['inputs_sha256'][key(EQUALITY)]).read_bytes()
    need(equal['counts']==dict(pair_rows=4851,tautologies=189,units=4662,duplicates=0,contradictions=0,product_terms=285852),'exact approved equality populations')
    need(equal['base_cnf_sha256']==cover['base_cnf_sha256']==unrestricted.CNF_SHA,'semantic gates share original base')
    authenticated=gate['inputs_sha256']
    for path in (COVER,EQUAL_GATE,unrestricted.CNF,unrestricted.MODEL,RECIPE,EQUALITY):
        need(authenticated.get(key(path))==digest(path),'compositiongate exact premise binding '+key(path))
    return gate,recipe,suffix


def validate_composed_branch(gate,recipe,equality_suffix,branch,binding,requested_cnf=None):
    matches=[row for row in gate['branches'] if row['branch']==branch];need(len(matches)==1,'unique branch in composition gate')
    entry=matches[0]
    cnf_path=ROOT/entry['cnf'];need(requested_cnf is None or Path(requested_cnf).resolve()==cnf_path.resolve(),'selected raw CNF path matches gate')
    binding.pin(cnf_path,entry['cnf_sha256'])
    candidates=[row for row in recipe['branches'] if row['branch']==branch];need(len(candidates)==1,'unique original recipe')
    original=candidates[0]
    need(entry['variables']==1186500 and entry['clauses']==4141120 and entry['units']==original['units'],'composed exact counts and branch units')
    branch_suffix=binding.pin(ROOT/original['suffix'],original['suffix_sha256']).read_bytes()
    need(branch_suffix==b''.join(f'{x} 0\n'.encode() for x in original['units']),'exact original4unit suffix')
    with unrestricted.CNF.open('rb') as base,cnf_path.open('rb') as augmented:
        body=bytecheck.compare(base,augmented,1186500,4136454,4662,equality_suffix,branch_suffix)
    return cnf_path,dict(branch=branch,cnf_sha256=digest(cnf_path),variables=1186500,clauses=4141120,
        units=original['units'],equality_units_count=4662,equality_suffix_sha256=digest(EQUALITY),
        base_body_bytes_compared=body,complete_exact_byte_composition=True)


def provenance():
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/eight_domain_audit independent wrapper author; frozen graph/parser helpers authored by /root/state_literature_audit',
        producer_imported=False,shared_components=['Frozen independent unrestricted scope/native parser and generic integerSRG/assignment/CNF primitives explicitly reused.',
            'Separately calibrated exact composition bytechecker, approved root equality audit, and full fourbranch coverage gate.',
            'Python standard library exact integer arithmetic; no solver or structural producer imports.'],
        external_review=False,artifact_availability='LOCAL_ONLY')


def codec_controls(out,binding):
    rejected=[]
    def reject(name,operation):
        try:operation()
        except (ValueError,IndexError,TypeError) as error:rejected.append(dict(case=name,error=str(error)))
        else:raise ValueError('corrupted codec input accepted: '+name)
    base=b'p cnf 6 2\n1 -2 0\n3 4 0\n';eq=b'4 0\n5 0\n6 0\n';branch=b'1 0\n-2 0\n3 0\n4 0\n'
    augmented=b'p cnf 6 9\n1 -2 0\n3 4 0\n'+eq+branch
    signed=[1,-2,3,4,5,6];values=common.assignment_values(signed,6)
    native=b'c SYNTHETIC POSITIVE CONTROL ONLY\ns SATISFIABLE\nv 1 -2 3\nv 4 5 6 0\n'
    parsed,native_record=unrestricted.native_values(io.BytesIO(native),6);need(parsed==values,'tiny nativeJSONagreement')
    bytecheck.compare(io.BytesIO(base),io.BytesIO(augmented),6,2,3,eq,branch)
    tiny_cnf=common.check_cnf_stream(io.BytesIO(augmented),values,6,9)
    for name,bad in [('wrong_header',augmented.replace(b'6 9',b'6 8',1)),
                     ('suffix_order',b'p cnf 6 9\n1 -2 0\n3 4 0\n'+branch+eq),
                     ('branch_literal',augmented[:-4]+b'-4 0\n')]:
        reject(name,lambda bad=bad:bytecheck.compare(io.BytesIO(base),io.BytesIO(bad),6,2,3,eq,branch))
    reject('wrong_assignment_branch_unit',lambda:common.check_cnf_stream(io.BytesIO(augmented),common.assignment_values([-1,-2,3,4,5,6],6),6,9))
    reject('assignment_duplicate',lambda:common.assignment_values([1,-2,3,4,5,5],6))
    reject('assignment_incomplete',lambda:common.assignment_values(signed[:-1],6))
    reject('native_wrong_status',lambda:unrestricted.native_values(io.BytesIO(native.replace(b'SATISFIABLE',b'UNKNOWN')),6))
    reject('native_missing_variable',lambda:unrestricted.native_values(io.BytesIO(native.replace(b'4 5 6',b'4 5')),6))
    reject('native_missing_terminator',lambda:unrestricted.native_values(io.BytesIO(native.replace(b'6 0',b'6')),6))
    old=binding.load(OLD_CAL,OLD_CAL_SHA)
    need(old['status']=='INDEPENDENT_UNRESTRICTED_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS','frozen independent helper calibration')
    native_fixture=binding.pin(ROOT/old['native_controls']['fullsize_fixture'],old['native_controls']['fullsize_fixture_sha256'])
    with gzip.open(native_fixture,'rb') as stream:full,full_native=unrestricted.native_values(stream,1186500)
    signed_full=list(range(-1,-1186501,-1))
    json_values=common.assignment_values(signed_full,1186500);need(full==json_values,'complete1186500nativeJSONagreement')
    assignment_path=out/'synthetic_fullsize_assignment.json.gz'
    assignment_bytes=json.dumps(dict(assignment=signed_full,scope='SYNTHETICCODECCONTROL_NOT_RESEARCH_SAT'),separators=(',',':')).encode()
    with assignment_path.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as zipped:zipped.write(assignment_bytes)
    with gzip.open(assignment_path,'rb') as stream:reloaded=json.load(stream)
    need(common.assignment_values(reloaded['assignment'],1186500)==full,'saved fullsizeJSONreplay')
    class SyntheticCNF:
        def readline(self):return b'p cnf 1186500 4141120\n'
        def __iter__(self):
            for i in range(4141120):yield f'-{i%1186500+1} 0\n'.encode()
    synthetic=common.check_cnf_stream(SyntheticCNF(),full,1186500,4141120)
    return dict(tiny_positive_augmented_cnf=tiny_cnf,tiny_native=native_record,corruptions_rejected=rejected,
        fullsize_native=full_native,fullsize_synthetic_cnf=synthetic,complete_json_native_agreement=True,
        synthetic_assignment=key(assignment_path),synthetic_assignment_sha256=digest(assignment_path),
        synthetic_assignment_uncompressed_sha256=sha256(assignment_bytes).hexdigest(),
        scope='Synthetic parser/codec/positiveCNFcontrols only. The all-negative fullsize model and repeated negative units are NOT the research CNF, NOT solver output, and NOT a99target graph.',
        synthetic_cnf_retrieval='Generate p cnf1186500 4141120 then -(1+i mod1186500) 0 for i=0..4141119, as in the frozen checker.')


def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);binding=Binding()
    gate,recipe,equality=composed_inputs(args,binding)
    actual=[]
    need({row['branch'] for row in gate['branches']}=={'a0','a1_complement','a1_cross','a2_crosses'} and len(gate['branches'])==4,'allfourresearchbranches')
    for row in gate['branches']:
        _,check=validate_composed_branch(gate,recipe,equality,row['branch'],binding);actual.append(check)
    generic_dir=args.out/'generic_srg_controls';generic_dir.mkdir()
    generic=common.controls(generic_dir)
    codec=codec_controls(args.out,binding)
    model=binding.load(unrestricted.MODEL,unrestricted.MODEL_SHA);scope=binding.load(unrestricted.SCOPE,unrestricted.SCOPE_SHA)
    a,edges,scope_record=unrestricted.unrestricted_scope(model,scope)
    graph=common.decode_model(a,edges,bytearray(1186501))
    try:common.validate_srg(graph,99,14,1,2)
    except ValueError as error:invalid_graph_reason=str(error)
    else:raise ValueError('zeroedge scoped graph incorrectly accepted as target')
    binding.finish();report=provenance()
    report.update(status='INDEPENDENT_STRENGTHENED_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS',inputs_sha256=binding.hashes,
        actual_composed_files_checked=actual,generic_srg_controls=generic,codec_controls=codec,scope_check=scope_record,
        all_free_zero_target_rejection=invalid_graph_reason,composition_gate_sha256=digest(args.composition_gate),
        statement='The separate strengthened SAT-object checking path is calibrated, and allfour materialized base+4662equality+fourbranch CNF byte recipes have been independently compared in full.',
        solver_calls=0,target_resolution=False,limitations=['Calibration is not a researchSAT assignment or graph witness.','No valid99target positive fixture is available; six known smallerSRGs calibrate the exact graph primitive.'])
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))


def check(args):
    started=time.monotonic();args.out.mkdir(parents=True,exist_ok=False);binding=Binding()
    gate,recipe,equality=composed_inputs(args,binding)
    cnf,composition=validate_composed_branch(gate,recipe,equality,args.branch,binding,args.cnf)
    model=binding.load(args.model,unrestricted.MODEL_SHA);scope=binding.load(unrestricted.SCOPE,unrestricted.SCOPE_SHA)
    a,edges,scope_record=unrestricted.unrestricted_scope(model,scope)
    signed=binding.load(args.assignment)['assignment'];values=common.assignment_values(signed,1186500)
    binding.pin(args.native_output)
    with args.native_output.open('rb') as stream:native,native_record=unrestricted.native_values(stream,1186500)
    need(native==values,'every native literal agrees withcompleteJSONassignment')
    with cnf.open('rb') as stream:cnf_record=common.check_cnf_stream(stream,values,1186500,4141120)
    graph=common.decode_model(a,edges,values)
    if args.decoded is not None:need(binding.load(args.decoded)['adjacency_full99']==graph,'supplied graph equals independent decode')
    exact=common.validate_srg(graph,99,14,1,2)
    graph_path=args.out/'independent_adjacency_full99.json';save(graph_path,dict(adjacency_full99=graph,exact_identity='A^2=12I-A+2J',independent_check=exact,external_review=False))
    binding.finish();report=provenance()
    report.update(status='INDEPENDENT_STRENGTHENED_TARGET_GRAPH_PASS_PENDING_EXTERNAL_REVIEW',inputs_sha256=binding.hashes,
        branch=args.branch,composition_check=composition,native_check=native_record,cnf_check=cnf_record,scope_check=scope_record,graph_check=exact,
        graph_path=key(graph_path),graph_sha256=digest(graph_path),target_resolution=True,
        statement='The complete native/JSONassignment satisfies every4141120clause of the exact approved strengthened branch, and its independent99vertex decode satisfies the exacttarget identity overintegers.',
        limitations=['Internally verified candidate resolution only; external mathematical review remains pending.'],elapsed_seconds=time.monotonic()-started)
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],graph_sha256=digest(graph_path),summary_sha256=digest(args.out/'summary.json'))))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    cal=sub.add_parser('calibrate');sat=sub.add_parser('sat')
    for target in (cal,sat):
        target.add_argument('--composition-gate',type=Path,required=True);target.add_argument('--composition-gate-sha256',required=True);target.add_argument('--out',type=Path,required=True)
    for name in ('cnf','model','assignment','native-output'):sat.add_argument('--'+name,type=Path,required=True)
    sat.add_argument('--branch',required=True);sat.add_argument('--decoded',type=Path)
    args=parser.parse_args();(calibrate if args.command=='calibrate' else check)(args)

if __name__=='__main__':main()
