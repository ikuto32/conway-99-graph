"""Author engineering controls for the exact V3 metadata-only Git-index omission."""
import argparse
import ast
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from command_deadline import CommandDeadline
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
SOURCE='acceleration/record_20261003_wave38_milestone_v3.py'
SOURCE_SHA='d35693006c44210d83014ebae4c1b8792bf9a1c84ed98d0de8dd654fb32eb0a1'
SPEC='acceleration/record_20261003_wave38_milestone_v3_spec.md'
SPEC_SHA='73a23449e6ad70d23aac1d936efca6f91aaf3aba35c5b4c6e4dc972f41746711'
CAL_SPEC='acceleration/calibrate_20261003_wave38_milestone_v3_v1_spec.md'

def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def need(ok,why):
    if not ok:raise ValueError(why)
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Finite metadata-path controls and full463+404name inventory; expected seconds, no generator/document/index/science execution.');out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False);pins={};rows=[]
    def pin(name,expected=None):
        need(deadline.status()['remaining_seconds']>5,'NOT_COMPLETED_WITHIN_ALLOCATION');value=sha(ROOT/name);need(expected is None or value==expected,'PIN:'+name);pins[name]=value;return value
    try:
        pin(SOURCE,SOURCE_SHA);pin(SPEC,SPEC_SHA);pin(CAL_SPEC);pin(Path(__file__).relative_to(ROOT).as_posix());pin('acceleration/command_deadline.py');pin('acceleration/validate_claims.py');pin('pyproject.toml');pin('uv.lock');ast.parse((ROOT/SOURCE).read_text(encoding='utf8'))
        loader=importlib.util.spec_from_file_location('wave38_v3_author_path_controls',ROOT/SOURCE);p=importlib.util.module_from_spec(loader);loader.loader.exec_module(p)
        pin('CLAIMS.yaml',p.LEDGER);pin(p.IMPACT,p.IMPACT_SHA);pin('.gitattributes','4c5232096640a5308943cb6f18d10402a0528102c5d0e96d09e662a290cad35a');index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip());index=index if index.is_absolute()else ROOT/index;index_before=sha(index);need(index_before==p.HISTORICAL_INDEX_SHA,'INITIAL_LIVE_INDEX')
        positive=[('research_source','acceleration/command_deadline.py','a'*64),('research_doc','docs/REPRODUCING.md','b'*64),('root_ledger','CLAIMS.yaml',p.LEDGER),('root_readme','README.md','c'*64),('attributes','.gitattributes','d'*64),('schema','docs/claims.schema.json','e'*64),('workflow','.github/workflows/claims.yml','f'*64),('historical_index','.git/index',p.HISTORICAL_INDEX_SHA)]
        for label,name,identity in positive:
            got=p.publication_impact_path(name,identity);need(got==(None if label=='historical_index'else name),'POSITIVE_LITERAL:'+label);rows.append(dict(label=label,input=name,outcome='ACCEPTED'if got is not None else'OMITTED_HISTORICAL_ONLY'))
        negative=[('wrong_index_hash','.git/index','0'*64,'HISTORICAL_INDEX_OBSERVATION_HASH'),('missing_index_hash','.git/index',None,'HISTORICAL_INDEX_OBSERVATION_HASH'),('git_config','.git/config','a'*64,'WORKSPACE_RELATIVE_PATH'),('git_private','.git/objects/x','a'*64,'WORKSPACE_RELATIVE_PATH'),('parent_traversal','../CLAIMS.yaml','a'*64,'WORKSPACE_RELATIVE_PATH'),('internal_traversal','docs/../CLAIMS.yaml','a'*64,'WORKSPACE_RELATIVE_PATH'),('absolute_linux','/mnt/c/Users/ikuto/projects/conway-99-graph/docs/REPRODUCING.md','a'*64,'WORKSPACE_RELATIVE_PATH'),('absolute_windows','C:/Users/ikuto/projects/conway-99-graph/docs/REPRODUCING.md','a'*64,'RESEARCH_NAMESPACE'),('outside_linux','/tmp/private','a'*64,'WORKSPACE_RELATIVE_PATH'),('outside_windows','C:/private/file','a'*64,'RESEARCH_NAMESPACE'),('backslash','docs\\x.md','a'*64,'LITERAL_RELATIVE_PATH'),('newline','docs/x\n.md','a'*64,'LITERAL_RELATIVE_PATH'),('nul','docs/x\0.md','a'*64,'LITERAL_RELATIVE_PATH'),('queued_lowword','acceleration/incidence_low_weight_new.py','a'*64,'EXCLUDED_QUEUED_WAVE39'),('queued_neighbor','acceleration/results/new_neighbor_census/run.json','a'*64,'EXCLUDED_QUEUED_WAVE39'),('duplicate_build','acceleration/build/a','a'*64,'EXCLUDED_BUILD_OR_DUPLICATE'),('recovered_copy','acceleration/recovered/a','a'*64,'EXCLUDED_BUILD_OR_DUPLICATE'),('outside_namespace','private/file','a'*64,'RESEARCH_NAMESPACE')]
        for label,name,identity,stage in negative:
            try:p.publication_impact_path(name,identity)
            except ValueError as error:
                need(str(error).startswith(stage+':')and repr(name)in str(error),'EXACT_REJECTION_STAGE:'+label);rows.append(dict(label=label,input=name,outcome='REJECTED',diagnostic=str(error)))
            else:raise ValueError('CORRUPTED_CONTROL_ACCEPTED:'+label)
        ledger=registry.read_ledger(ROOT/'CLAIMS.yaml');need(len(ledger['claims'])==350 and[c['id']for c in ledger['claims'][343:]]==p.IDS,'EXACT_SEVEN_CLAIMS');artifacts={a['id']:a for a in ledger['artifacts']};evidence={e for c in ledger['claims'][343:]for e in c['evidence']};inventory=[]
        for aid in sorted(evidence):
            a=artifacts[aid];need(a['path']is not None,'AVAILABLE_LITERAL_EVIDENCE_PATH');raw=a['path'];need(not raw.startswith(('/', 'C:'))and'\\'not in raw,'NO_UNUSED_ABSOLUTE_ADAPTER');need(p.bounded(raw).is_file(),'ACTUAL_EVIDENCE_FILE:'+raw);inventory.append(dict(origin='seven_claim_evidence',artifact_id=aid,path=raw,expected_sha256=a['sha256'],mapping='UNCHANGED_RELATIVE'))
        need(len(inventory)==463,'EXACT463_EVIDENCE_PATHS');impact=json.loads((ROOT/p.IMPACT).read_bytes());impact_rows=[]
        for raw,identity in impact['inputs_sha256'].items():
            got=p.publication_impact_path(raw,identity)
            if got is not None:need(p.bounded(got).is_file(),'ACTUAL_IMPACT_FILE:'+raw)
            impact_rows.append(dict(origin='independent_impact_input',source_path=raw,publication_path=got,sha256=identity,mapping='OMITTED_HISTORICAL_READONLY_INDEX'if got is None else'UNCHANGED_RELATIVE'))
        need(len(impact_rows)==404 and sum(r['publication_path']is None for r in impact_rows)==1,'EXACT404_WITH_ONE_OMISSION');save(out/'selected_path_inventory.json',dict(evidence=inventory,impact_inputs=impact_rows,absolute_aliases_found=0,namespace_broadened=False));pin((out/'selected_path_inventory.json').relative_to(ROOT).as_posix());need(sha(index)==index_before and sha(ROOT/'CLAIMS.yaml')==p.LEDGER,'LIVE_LEDGER_INDEX_UNCHANGED')
        save(out/'summary.json',dict(status='AUTHOR_WAVE38_V3_HISTORICAL_INDEX_OMISSION_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=SOURCE_SHA,inputs_sha256=pins,controls=rows,positive_controls=8,strict_negative_controls=18,selected_evidence_path_records=463,selected_impact_path_records=404,historical_readonly_index_omissions=1,absolute_artifact_aliases=0,namespace_broadened=False,source_syntax_checked=True,generator_main_called=False,ledger_mutated=False,index_mutated=False,current_documents_mutated=False,attributes_mutated=False,scientific_launched=False,mathematical_replays=0,shared_components=['Producer publication_impact_path/bounded functions tested as author calibration only.','Existing registry YAML reader used only to identify exact current350 selected paths.','Existing deadline helper and Git index path query.'],deadline=deadline.status(),limitations=['Author engineering controls; ROOT review and raw staged/public byte checking remain required.','Names and finite boundary behavior checked; no new mathematical assertion or artifact availability approval.']));print(json.dumps(dict(status='AUTHOR_WAVE38_V3_HISTORICAL_INDEX_OMISSION_CONTROLS_PASS',summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:
        save(out/'failure.json',dict(exception=type(error).__name__,diagnostic=str(error),inputs_sha256=pins,controls=rows,deadline=deadline.status(),generator_main_called=False,scientific_launched=False));raise
if __name__=='__main__':main()
