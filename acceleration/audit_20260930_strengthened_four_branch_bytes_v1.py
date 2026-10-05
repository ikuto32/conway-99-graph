"""Exact base+independently approved equality units+four branch units checker.

No producer imports. This checks byte composition and binds prior semantic
gates; it does not independently reapprove the equality producer's mathematics.
"""
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
    h=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()

def compare(base,composed,variables,base_clauses,equality_count,equality_suffix,branch_suffix):
    need(base.readline()==f'p cnf {variables} {base_clauses}\n'.encode(),'exact originalbase header')
    need(composed.readline()==f'p cnf {variables} {base_clauses+equality_count+4}\n'.encode(),'exact composed header')
    body=0
    for block in iter(lambda:base.read(1<<20),b''):
        need(composed.read(len(block))==block,'complete originalbody unchanged');body+=len(block)
    need(composed.read(len(equality_suffix))==equality_suffix,'exact equality suffix in its required position')
    need(composed.read()==branch_suffix,'exact four branch units and no trailingbytes')
    return body

def controls():
    base=b'p cnf 6 2\n1 -2 0\n3 4 0\n';eq=b'4 0\n5 0\n6 0\n';branch=b'1 0\n-2 0\n3 0\n-4 0\n'
    good=b'p cnf 6 9\n1 -2 0\n3 4 0\n'+eq+branch
    compare(io.BytesIO(base),io.BytesIO(good),6,2,3,eq,branch);rejected=[]
    bad_cases={'wrong_count':good.replace(b'6 9',b'6 8',1),'changed_body':good.replace(b'1 -2',b'1 2',1),
        'reversed_suffixes':b'p cnf 6 9\n1 -2 0\n3 4 0\n'+branch+eq,
        'wrong_equality_literal':good.replace(b'5 0',b'-5 0',1),'missing_equality':good.replace(b'5 0\n',b'',1),
        'changed_branch':good[:-5]+b'4 0\n','extra_bytes':good+b'6 0\n','duplicated_base_header':b'p cnf 6 9\n'+base+eq+branch}
    for name,bad in bad_cases.items():
        try:compare(io.BytesIO(base),io.BytesIO(bad),6,2,3,eq,branch)
        except ValueError:rejected.append(name)
        else:raise ValueError('corrupt composedfile accepted: '+name)
    return dict(positive_complete_composition_passed=True,corruptions_rejected=rejected)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--calibrate',action='store_true')
    for name in ('base','branch-cnf','recipe','coverage-gate','equality-suffix','equality-gate','out'):
        parser.add_argument('--'+name,type=Path,required=name=='out')
    parser.add_argument('--coverage-gate-sha256');parser.add_argument('--equality-gate-sha256');parser.add_argument('--branch')
    args=parser.parse_args();need(not args.out.exists(),'refuse overwrite');bindings={};calibration=controls()
    def bind(path,expected=None):
        value=digest(path);need(expected is None or value==expected,'input hash '+str(path));bindings[key(path)]=value;return Path(path)
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='Independent composed-byte checker authored by /root/eight_domain_audit',controls=calibration,
        producer_imported=False,solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    if args.calibrate:
        report['status']='INDEPENDENT_STRENGTHENED_FOUR_BRANCH_CNF_BYTES_CALIBRATION_PASS'
    else:
        need(all((args.base,args.branch_cnf,args.recipe,args.coverage_gate,args.coverage_gate_sha256,args.equality_suffix,args.equality_gate,args.equality_gate_sha256,args.branch)),'all composition arguments required')
        cover=read(args.coverage_gate,args.coverage_gate_sha256);equal=read(args.equality_gate,args.equality_gate_sha256)
        need(cover['status']=='INDEPENDENT_UNRESTRICTED_FOUR_BRANCH_COVER_PASS','fourbranch coverage gate')
        need(equal['status']=='INDEPENDENT_UNRESTRICTED_PAIR_EQUALITY_UNITS_PASS','independent equality gate')
        need(cover['base_cnf_sha256']==equal['base_cnf_sha256'],'same original base CNF across semantic premises')
        bind(args.base,cover['base_cnf_sha256'])
        need(equal['counts']['units']==4662 and equal['counts']['contradictions']==0 and equal['counts']['duplicates']==0,'approved equality population')
        equality_suffix=bind(args.equality_suffix,equal['inputs_sha256'][key(args.equality_suffix)]).read_bytes()
        recipe=read(args.recipe,cover['inputs_sha256'][key(args.recipe)])
        matches=[row for row in recipe['branches'] if row['branch']==args.branch];need(len(matches)==1,'unique original branch')
        row=matches[0];checked=[entry for entry in cover['checked_branch_recipes'] if entry['branch']==args.branch]
        need(len(checked)==1 and all(checked[0][name]==row[name] for name in ('units','variables','clauses','suffix_sha256'))
             and checked[0]['future_cnf_sha256']==row['cnf_sha256'],'original branch recipe authentication')
        branch_suffix=bind(ROOT/row['suffix'],row['suffix_sha256']).read_bytes()
        need(branch_suffix==b''.join(f'{x} 0\n'.encode() for x in row['units']) and len(row['units'])==4,'four branch literal suffix')
        literals=[]
        for line in equality_suffix.splitlines():
            values=list(map(int,line.split()));need(len(values)==2 and values[1]==0 and 1<=values[0]<=row['variables'],'positive unit suffix shape');literals.append(values[0])
        need(len(literals)==len(set(literals))==4662,'complete distinct equality literals')
        bind(args.branch_cnf)
        with args.base.open('rb') as base,args.branch_cnf.open('rb') as composed:
            compared=compare(base,composed,row['variables'],row['clauses']-4,len(literals),equality_suffix,branch_suffix)
        report.update(status='INDEPENDENT_STRENGTHENED_FOUR_BRANCH_CNF_BYTES_PASS',branch=args.branch,
            base_cnf_sha256=digest(args.base),branch_cnf_sha256=digest(args.branch_cnf),units=row['units'],
            equality_suffix_sha256=digest(args.equality_suffix),equality_units_count=len(literals),
            coverage_gate_sha256=digest(args.coverage_gate),equality_gate_sha256=digest(args.equality_gate),
            original_branch_recipe_sha256=digest(args.recipe),variables=row['variables'],clauses=row['clauses']+len(literals),
            original_base_body_bytes_compared=compared,exact_header=True,original_body_preserved=True,
            exact_equality_suffix_before_branch_suffix=True,
            semantic_composition='The independently approved equality conjunction is entailed by the original baseCNF. Adding it to any checked branch preserves satisfiability. Thus the four strengthened branches retain the independently approved unrestricted cover.',
            semantic_dependencies=[dict(id='C-UNRESTRICTED-PAIR-EQUALITY-UNITS',revision=1,relation='uses_result'),
                                   dict(id='C-UNRESTRICTED-FOUR-BRANCH-COVER',revision=1,relation='coverage')],
            scope='Exact materialization of one base+4662entailedunits+fourbranchunits instance; no solver result.',
            shared_components=['Python standard library hashes and literal bytecomparison',
                'Author produced candidate equality units; their mathematics is approved by the separately authored and hash-bound rootaudit, not selfapproved here.',
                'Prior independently checked fourbranch coverage is reused.'])
    for path in (__file__,ROOT/'uv.lock'):bind(path)
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'stable input bytes')
    report['inputs_sha256']=bindings;report['checker_sha256']=digest(__file__)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=report['status'],sha256=digest(args.out))))

if __name__=='__main__':main()
