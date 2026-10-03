"""Independent exact four-branch byte-materialization checker; no producer imports."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import io
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def need(value,message):
    if not value:raise ValueError(message)
def digest(path):
    with Path(path).open('rb') as stream:
        h=sha256()
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
        return h.hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()

def compare(base,branch,variables,clauses,suffix):
    need(base.readline()==f'p cnf {variables} {clauses}\n'.encode(),'exact base header')
    need(branch.readline()==f'p cnf {variables} {clauses+4}\n'.encode(),'exact branch header')
    body_bytes=0
    for block in iter(lambda:base.read(1<<20),b''):
        need(branch.read(len(block))==block,'complete base body preserved verbatim');body_bytes+=len(block)
    need(branch.read()==suffix,'exact complete suffix and no extra bytes')
    return body_bytes

def controls():
    base=b'p cnf 4 2\n1 -2 0\n3 4 0\n';suffix=b'1 0\n-2 0\n3 0\n-4 0\n'
    good=b'p cnf 4 6\n1 -2 0\n3 4 0\n'+suffix
    compare(io.BytesIO(base),io.BytesIO(good),4,2,suffix);rejected=[]
    cases={'wrong_header':good.replace(b'4 6',b'4 5',1),'duplicated_base_header':b'p cnf 4 6\n'+base+suffix,
           'changed_body':good.replace(b'1 -2',b'1 2',1),'missing_unit':good[:-5],
           'wrong_unit_sign':good[:-5]+b'4 0\n','extra_bytes':good+b'1 0\n'}
    for name,bad in cases.items():
        try:compare(io.BytesIO(base),io.BytesIO(bad),4,2,suffix)
        except ValueError:rejected.append(name)
        else:raise ValueError('corrupted branch accepted: '+name)
    return dict(positive_exact_recipe_passed=True,corruptions_rejected=rejected)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--calibrate',action='store_true')
    for name in ('base','branch-cnf','recipe','coverage-gate','out'):parser.add_argument('--'+name,type=Path,required=name=='out')
    parser.add_argument('--coverage-gate-sha256');parser.add_argument('--branch');args=parser.parse_args()
    need(not args.out.exists(),'refuse overwrite');calibration=controls();bindings={}
    def bind(path,expected=None):
        value=digest(path);need(expected is None or value==expected,'input identity '+str(path));bindings[key(path)]=value;return Path(path)
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='Independently authored byte checker by /root/eight_domain_audit',controls=calibration,producer_imported=False,
        scope='Exact file materialization only; no solver result or mathematical conclusion beyond the hash-bound existing coverage gate.',
        solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    if args.calibrate:
        report['status']='INDEPENDENT_FOUR_BRANCH_CNF_BYTES_CALIBRATION_PASS'
    else:
        need(all((args.base,args.branch_cnf,args.recipe,args.coverage_gate,args.coverage_gate_sha256,args.branch)),'all research-check arguments required')
        gate=json.loads(bind(args.coverage_gate,args.coverage_gate_sha256).read_bytes())
        need(gate['status']=='INDEPENDENT_UNRESTRICTED_FOUR_BRANCH_COVER_PASS','complete independent coverage gate')
        bind(args.base,gate['base_cnf_sha256']);recipe=json.loads(bind(args.recipe,gate['inputs_sha256'][key(args.recipe)]).read_bytes())
        matches=[row for row in recipe['branches'] if row['branch']==args.branch];need(len(matches)==1,'unique branch recipe')
        row=matches[0];checked=[x for x in gate['checked_branch_recipes'] if x['branch']==args.branch]
        need(len(checked)==1 and all(checked[0][name]==row[name] for name in ('units','variables','clauses','suffix_sha256'))
             and checked[0]['future_cnf_sha256']==row['cnf_sha256'],'gate binds exact selected recipe')
        suffix=bind(ROOT/row['suffix'],row['suffix_sha256']).read_bytes()
        need(suffix==b''.join(f'{x} 0\n'.encode() for x in row['units']) and len(row['units'])==4,'exact four literals')
        bind(args.branch_cnf,row['cnf_sha256'])
        with args.base.open('rb') as base,args.branch_cnf.open('rb') as branch:
            count=compare(base,branch,row['variables'],row['clauses']-4,suffix)
        report.update(status='INDEPENDENT_FOUR_BRANCH_CNF_BYTES_PASS',branch=args.branch,units=row['units'],
            base_cnf_sha256=digest(args.base),branch_cnf_sha256=digest(args.branch_cnf),coverage_gate_sha256=digest(args.coverage_gate),
            recipe_sha256=digest(args.recipe),variables=row['variables'],clauses=row['clauses'],base_body_bytes_compared=count,
            exact_header_replacement=True,base_body_preserved=True,exact_suffix=True)
    for path in (__file__,ROOT/'uv.lock'):bind(path)
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'input stability')
    report['inputs_sha256']=bindings;report['checker_sha256']=digest(__file__)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=report['status'],sha256=digest(args.out))))

if __name__=='__main__':main()
