"""Read-only eighth-milestone catalog with explicit immutable path allowlists.

Writes only its new output directory. Does not edit the ledger, ignore rules,
existing evidence or Git index. Directory selection is exact, not substring
filtering. Hash verification streams bytes and is not mathematical review.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
LIMIT=10*1024*1024
DIRECTORIES=[
 'acceleration/results/20260930_triangle_matching_pair_census',
 'acceleration/results/20260930_triangle_matching_pair_census_v2',
 'acceleration/results/20260930_independent_review/triangle_matching_pair_census',
 'acceleration/results/20260930_triangle_core_permutation',
 'acceleration/results/20260930_independent_review/triangle_core_paircap_theorem',
 'acceleration/results/20260930_independent_review/triangle_core_permutation_census',
 'acceleration/results/20260930_independent_review/triangle_core_permutation_census_v2',
 'acceleration/results/20260930_triangle39_gram_sos',
 'acceleration/results/20260930_independent_review/triangle39_gram_sos',
 'acceleration/results/20260930_triangle_core_identity',
 'acceleration/results/20260930_independent_review/triangle_core_identity',
 'acceleration/results/20260930_triangle_wave154_row29_obstruction',
 'acceleration/results/20260930_independent_review/triangle_wave154_row29_obstruction',
 'acceleration/results/20260930_eighth_registration',
 'acceleration/results/20260930_identity_corollary_registration',
]
FILES=[
 'acceleration/audit_20260930_triangle_matching_pair_census.py',
 'acceleration/theory_20260930_triangle_matching_pair_census.py',
 'acceleration/theory_20260930_triangle_matching_pair_census_v2.py',
 'acceleration/theory_20260930_triangle_matching_pair_census_spec.md',
 'acceleration/theory_20260930_triangle_census_scope_record.py',
 'acceleration/audit_20260930_triangle_core_permutation.py',
 'acceleration/audit_20260930_triangle_core_permutation_v2.py',
 'acceleration/theory_20260930_triangle_core_permutation.py',
 'acceleration/theory_20260930_triangle_core_permutation_spec.md',
 'acceleration/audit_20260930_triangle39_gram_sos.py',
 'acceleration/theory_20260930_triangle39_gram_sos.py',
 'acceleration/audit_20260930_triangle_core_identity.py',
 'acceleration/theory_20260930_triangle_core_identity.py',
 'acceleration/audit_20260930_triangle_row29_obstruction.py',
 'acceleration/theory_20260930_triangle_row_obstruction.py',
 'acceleration/theory_20260930_triangle_row_obstruction_spec.md',
 'acceleration/register_20260930_eighth_milestone.py',
 'acceleration/register_20260930_identity_corollary.py',
 'docs/AUDIT_20260930_TRIANGLE_MATCHING_PAIR_CENSUS.md',
 'docs/AUDIT_20260930_TRIANGLE_CORE_PERMUTATION_CAPS.md',
 'docs/DERIVATION_20260930_TRIANGLE39_GRAM_SOS.md',
 'docs/DERIVATION_20260930_TRIANGLE_CORE_IDENTITY_CONSTRUCTION.md',
 'docs/AUDIT_20260930_TRIANGLE_ROW29_OBSTRUCTION.md',
 'acceleration/package_20260930_eighth_catalog.py',
]
EXCLUDED_DIRECTORIES=[
 'acceleration/results/20260930_triangle_q1_binary_scout',
 'acceleration/results/20260930_independent_review/triangle_q1_binary_scout',
 'acceleration/results/20260930_triangle_joint_factor_cnf',
 'acceleration/results/20260930_independent_review/triangle_joint_factor_cnf',
 'acceleration/results/20260930_triangle_joint_factor_native_preflight',
 'acceleration/results/20260930_triangle_joint_factor_native_pilot',
 'acceleration/results/20260930_triangle_wave154_proof_core',
]
CLAIMS=[
 'C-TRIANGLE-ORDERED-MATCHING-PAIR-CENSUS',
 'C-TRIANGLE-CORE-PERMUTATION-PAIR-CAP-REDUCTION',
 'C-TRIANGLE-CORE-LABELLED-P-PAIRCAP-CENSUS',
 'C-FIXED-WAVE154-ROW29-EMPTY-DOMAIN',
 'C-TRIANGLE39-UNIVERSAL-GRAM-PSD-REDUNDANCY',
 'C-TRIANGLE-CORE-IDENTITY-P-CONSTRUCTION',
]
MAP_KEYS={'inputs_sha256','input_hashes','output_hashes','artifact_hashes','audit_artifact_hashes','checked_input_bindings'}
HEX=re.compile(r'^[0-9a-f]{64}$')
def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')
def git(*args,input=None):return subprocess.check_output(['git',*args],cwd=ROOT,input=input)
def relative(p):return p.resolve().relative_to(ROOT).as_posix()
def resolve_ref(name,origin,archive=False):
    name=name.replace('\\','/');p=Path(name)
    candidates=[p]if p.is_absolute()else([ROOT/'external_conway99_research'/name]if archive else [ROOT/name,origin.parent/name])
    for p in candidates:
        if p.is_file():
            try:return relative(p)
            except ValueError:return None
    return None

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    ledger_path=ROOT/'CLAIMS.yaml';ledger_bytes=ledger_path.read_bytes();ledger=yaml.safe_load(ledger_bytes)
    claims={c['id']:c for c in ledger['claims']};artifacts={a['id']:a for a in ledger['artifacts']}
    need(all(claims[c]['status']=='VERIFIED'and claims[c]['review_state']=='CLEAR'for c in CLAIMS),'six current verified claims')
    registration=json.loads((ROOT/'acceleration/results/20260930_eighth_registration/summary.json').read_bytes())
    identity=json.loads((ROOT/'acceleration/results/20260930_identity_corollary_registration/summary.json').read_bytes())
    need(registration['new_claim_ids']+identity['new_claim_ids']==CLAIMS,'exact sixth-claim registration population')
    need(identity['ledger_sha256']==hashlib.sha256(ledger_bytes).hexdigest(),'ledger exactly registered before publication changes')
    index_before=git('ls-files','--stage','-z');head=git('rev-parse','HEAD').decode().strip()
    tracked=set(git('ls-files','-z').decode().split('\0'))
    selected=set(FILES)
    for directory in DIRECTORIES:
        path=ROOT/directory;need(path.is_dir(),'allowlisted directory exists '+directory)
        selected.update(relative(p)for p in path.rglob('*')if p.is_file())
    for path in selected:
        need((ROOT/path).is_file(),'explicit file exists '+path)
        need(not any(path==d or path.startswith(d+'/')for d in EXCLUDED_DIRECTORIES),'forbidden next-wave path in selection')
    # check-ignore's return1 means no ignored paths. Capture all, including raw logs.
    ignore_run=subprocess.run(['git','check-ignore','--stdin','-z'],cwd=ROOT,input=('\0'.join(sorted(selected))+'\0').encode(),capture_output=True)
    need(ignore_run.returncode in (0,1),'git ignore inventory')
    ignored=set(ignore_run.stdout.decode().split('\0'))-{''}
    cache={}
    def info(path):
        if path not in cache:
            p=ROOT/path;cache[path]=dict(path=path,sha256=digest(p),bytes=p.stat().st_size)
        return cache[path]
    entries=[]
    for path in sorted(selected):
        item=dict(info(path));item.update(git_state_at_scan='TRACKED'if path in tracked else'IGNORED'if path in ignored else'UNTRACKED_NONIGNORED',
               publication_ready_under_10MiB=item['bytes']<=LIMIT,availability='LOCAL_ONLY'if path not in tracked else'EXISTING_TRACKED_ARTIFACT')
        entries.append(item)
    refs=[];unresolved=[]
    def check(path,expected,origin,field):
        actual=info(path)['sha256'];need(actual==expected,f'referenced hash mismatch {origin}:{field} -> {path}')
        refs.append(dict(origin=origin,field=field,path=path,sha256=actual,bytes=info(path)['bytes'],
                         selection='ALLOWLISTED_PAYLOAD'if path in selected else'EXTERNAL_DEPENDENCY_OR_EXISTING_REPOSITORY_FILE'))
    def walk(obj,origin,field=''):
        if isinstance(obj,dict):
            for key,value in obj.items():
                here=field+'/'+key
                if key in MAP_KEYS and isinstance(value,dict):
                    for name,expected in value.items():
                        if isinstance(expected,str)and HEX.fullmatch(expected):
                            p=resolve_ref(name,ROOT/origin)
                            if p:check(p,expected,origin,here+'/'+name)
                            else:unresolved.append(dict(origin=origin,field=here,name=name,sha256=expected))
                # Immutable external archive source records have their own repo/commit.
                walk(value,origin,here)
            if isinstance(obj.get('path'),str)and isinstance(obj.get('sha256'),str)and HEX.fullmatch(obj['sha256']):
                archived='repository'in obj and 'conway-99-research'in obj['repository']
                p=resolve_ref(obj['path'],ROOT/origin,archive=archived)
                if p:check(p,obj['sha256'],origin,field+'/path')
                else:unresolved.append(dict(origin=origin,field=field+'/path',name=obj['path'],sha256=obj['sha256']))
        elif isinstance(obj,list):
            for i,value in enumerate(obj):walk(value,origin,field+f'/{i}')
    for path in sorted(selected):
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    claims_receipts=[]
    for cid in CLAIMS:
        c=claims[cid];ev=[]
        for aid in c['evidence']:
            a=artifacts[aid];check(a['path'],a['sha256'],'CLAIMS.yaml',cid+'/'+aid);ev.append(dict(id=aid,path=a['path'],sha256=a['sha256']))
            need(a['path']in selected,'new claim evidence outside explicit allowlist '+a['path'])
        claims_receipts.append(dict(id=cid,revision=c['revision'],status=c['status'],review_state=c['review_state'],evidence=ev))
    need(not unresolved,'unresolved exact artifact references: '+json.dumps(unresolved[:5]))
    # New untracked dependencies would be a publication hole: demand an explicit
    # future allowlist edit, never silently import every untracked file.
    outside=sorted({r['path']for r in refs if r['path']not in selected and r['path']not in tracked and not r['path'].startswith('external_conway99_research/')})
    need(not outside,'untracked required dependency absent from explicit allowlist: '+repr(outside))
    large=[e for e in entries if e['bytes']>LIMIT]
    rawlogs=[e for e in entries if e['path']in ignored and e['path'].lower().endswith(('.log','.stdout','.stderr'))]
    report_scope=dict(claim_ids=CLAIMS,claim_records=claims_receipts,ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),
                      ledger_claim_count=len(claims),ledger_current_verified_count=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims.values()),
                      selected_directories=DIRECTORIES,selected_files=FILES,excluded_directories=EXCLUDED_DIRECTORIES,
                      selection_rule='Exact directory trees and exact individual file allowlists only. No substring matching or all-untracked selection.',
                      exclusion_semantics='Only allowlisted paths are candidates; every other path is outside this snapshot, whether or not listed explicitly for emphasis.',
                      root_owned_future_edits=['CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md','eighth checkpoint and publication receipts'],
                      source_commit=head,timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version())
    save(out/'scope.json',report_scope)
    save(out/'catalog.json',dict(entries=entries,total_files=len(entries),total_bytes=sum(e['bytes']for e in entries),
                               git_state_counts=dict(Counter(e['git_state_at_scan']for e in entries)),over10MiB=large,
                               mathematical_reverification_performed=False))
    save(out/'reference_checks.json',dict(status='ALL_RESOLVED_REFERENCED_FILE_HASHES_MATCH',checks=refs,unique_files=len({r['path']for r in refs}),
                                         reference_binding_count=len(refs),unresolved=unresolved,
                                         scope='All path/hash maps and explicit path+sha256 records within selected JSON artifacts, plus evidence records of the exact six selected ledger claims. Existing dependencies are authenticated by their pinned bytes, not recursively re-audited.'))
    save(out/'ignored_raw_logs.json',dict(scope='All files under the exact allowlisted directory trees and explicit file paths, including ignored files.',
                                        ignored_files=[e for e in entries if e['path']in ignored],ignored_raw_logs=rawlogs,
                                        publication_action='No Git ignore or staging changes made; root must explicitly add any ignored selected files.'))
    # All payload paths have hashes. The inventory and final summary are external
    # wrappers rather than self-hashed members of their own payload.
    payload=sorted(selected|{relative(p)for p in out.iterdir()if p.is_file()})
    stage_entries=[dict(info(path))for path in payload]
    stage=dict(paths=payload,entries=stage_entries,count=len(payload),total_bytes=sum(e['bytes']for e in stage_entries),
               policy='Frozen explicit eighth-milestone payload; no Git index mutation.',
               wrapper_paths_to_add_separately=[relative(out/'stage_inventory.json'),relative(out/'summary.json')])
    save(out/'stage_inventory.json',stage)
    # Detect concurrent edits to every selected and referenced input; verify index
    # and ledger unchanged by this inventory task.
    for path,item in cache.items():need(digest(ROOT/path)==item['sha256'],'input changed during inventory '+path)
    need(ledger_path.read_bytes()==ledger_bytes,'ledger changed during inventory')
    need(git('ls-files','--stage','-z')==index_before,'Git index changed during inventory')
    summary=dict(status='EIGHTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'if not large else'EIGHTH_INVENTORY_REQUIRES_LARGE_ARTIFACT_PACKAGING',
                 timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,ledger_sha256=report_scope['ledger_sha256'],
                 claims=CLAIMS,claim_count=6,current_ledger_claims=len(claims),current_verified_claims=report_scope['ledger_current_verified_count'],
                 allowlisted_payload_files=len(entries),allowlisted_payload_bytes=sum(e['bytes']for e in entries),stage_payload_files=len(payload),
                 referenced_file_bindings=len(refs),unique_referenced_files=len({r['path']for r in refs}),
                 ignored_selected_files=len(ignored),ignored_raw_logs=len(rawlogs),files_over10MiB=large,
                 output_hashes={relative(p):digest(p)for p in sorted(out.iterdir())if p.is_file()},
                 git_index_unchanged=True,ledger_unchanged=True,ignore_rules_unchanged=True,target_resolution='UNKNOWN',
                 limitations=['This is byte identity/publication selection checking, not new mathematical verification.',
                              'Claims availability is not changed; root controls public commit and publication.',
                              'The new Q1 scout, joint-factor work and candidate proof-core extraction are outside the exact allowlist.',
                              'Root checkpoint/docs edits made after this scan require a separate final-stage inventory.'])
    save(out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items()if k not in ['output_hashes','limitations','claims','files_over10MiB']}))
    print(json.dumps({'summary_sha256':digest(out/'summary.json'),'stage_inventory_sha256':digest(out/'stage_inventory.json')}))

if __name__=='__main__':main()
