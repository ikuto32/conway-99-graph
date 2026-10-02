"""Bind the preserved scientific draft to committed sources and new exact gates."""
import argparse,copy,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DRAFT='acceleration/plan_20261002_hypergraph_weighted_pilot_v1.json'
DRAFT_SHA='ad464cc2954ab2dcbd35939f3efefe5ead8a45bb04f41593d034413562bf8463'
GATE='acceleration/results/20261002_independent_review/hypergraph_weighted_controls01/summary.json'
GATE_SHA='464a90e4093194ac59c4bdba3c19da661f7eabde52806307b37dbd33a7249f57'
CHECK='acceleration/results/20261002_independent_review/hypergraph_weighted_saved_calibration02/summary.json'
CHECK_SHA='503a9a55d02823f2016e5a7053f6644f0c11d9b0981ef28368f854777a2e5d2c'
BUILD='acceleration/results/20261002_hypergraph_weighted_build01/build_manifest.json'

def need(ok,message):
 if not ok:raise ValueError(message)

def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--source-commit',required=True)
 args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
 def load(name,expected=None):
  identity=sha(ROOT/name);need(expected is None or identity==expected,'exact pinned planning input');pins[name]=identity;return json.loads((ROOT/name).read_bytes())
 plan=copy.deepcopy(load(DRAFT,DRAFT_SHA));gate=load(GATE,GATE_SHA);calibration=load(CHECK,CHECK_SHA);build=load(BUILD)
 need(gate['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_ANNEAL_V1_CONTROLS_PASS' and calibration['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_SAVED_OBJECTS_V2_CALIBRATION_PASS','new independent exact gate statuses')
 need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==args.source_commit,'actual source commit')
 needed=['acceleration/hypergraph_weighted_anneal_20261002_v1.cpp','acceleration/prepare_20261002_hypergraph_weighted_v1.py','acceleration/prepare_20261002_hypergraph_weighted_v1_spec.md',build['binary_path'],BUILD,'acceleration/audit_20261002_hypergraph_weighted_saved_objects_v2.py','acceleration/audit_20261002_hypergraph_weighted_saved_objects_v2_spec.md',CHECK]
 for name in needed:
  pins[name]=sha(ROOT/name);blob=subprocess.check_output(['git','show',args.source_commit+':'+name],cwd=ROOT);need(hashlib.sha256(blob).hexdigest()==pins[name],'committed actual scientific/checker bytes')
 for name in needed[:5]:need(gate['inputs_sha256'][name]==pins[name],'engine gate binds exact committed bytes')
 need(sha(ROOT/plan['import']['path'])==plan['import']['sha256'],'independently checked starting state')
 pins[plan['import']['path']]=plan['import']['sha256']
 plan.update(schema='HYPERGRAPH_WEIGHTED_SCIENTIFIC_FROZEN_V1',status='FROZEN_ONE_SEED_WITH_NEW_ENGINE_AND_SAVED_OBJECT_GATES',source_commit=args.source_commit,source_commit_null_reason=None,gate=dict(path=GATE,sha256=GATE_SHA),gate_null_reason=None,saved_object_gate=dict(path=CHECK,sha256=CHECK_SHA,checker='acceleration/audit_20261002_hypergraph_weighted_saved_objects_v2.py'),build=dict(path=BUILD,sha256=pins[BUILD],binary=build['binary_path'],binary_sha256=build['binary_sha256']),timestamp=datetime.now(timezone.utc).isoformat(),input_hashes=pins,preserved_draft=dict(path=DRAFT,sha256=DRAFT_SHA),freeze=dict(source=Path(__file__).relative_to(ROOT).as_posix(),source_sha256=sha(Path(__file__)),command=[sys.executable,*sys.argv],cwd=str(ROOT)),independent_approval_scope='Exact finite engine and saved-object controls only; no approval of a future scientific outcome.',scientific_launched=False)
 with (out/'plan.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(plan,stream,indent=2);stream.write('\n')
 print(json.dumps(dict(plan=(out/'plan.json').relative_to(ROOT).as_posix(),sha256=sha(out/'plan.json'),source_commit=args.source_commit)))

if __name__=='__main__':main()
