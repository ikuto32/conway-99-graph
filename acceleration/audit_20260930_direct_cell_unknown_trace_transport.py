"""Byte transport only: independent reader over two authenticated UNKNOWN traces."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,platform,subprocess,sys,time
import audit_20260930_hadamard_fiftyfour_proof_transport as reader

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';PACK=B/'20260930_direct_cell_unknown_trace_package'
PLAN=ROOT/'docs/AUDIT_20260930_DIRECT_CELL_UNKNOWN_TRACE_TRANSPORT.md'
GATES={
 'standalone':('direct_cell_standalone_unknown_v2','7a97722db1ede1df9f01004af8e00f6ff3503dcdf16618e893bf5d6a70f0b1fd'),
 'at_least_seven':('direct_cell_count_coupled_unknown_v2','677cd12aa5096097311538a894ed0cf885007daa13242a21cf9b7be57215bb95')}
PINS={PACK/'package_manifest.json':'e6e04f78ccd76b2538807da4f20d3063ca10189d4a2562d6ecffc262d39477e9',PACK/'summary.json':'d478edf5cea0edb7471283eeec11f4e09c06394c9feb757225a2c1759fdf70ac',Path(reader.__file__):'4b6c13e4f18c4f2d55a5d683aac1f9ac60cbfdce08cc2bbcca998573225fa0ee',B/'20260930_independent_review/direct_cell_unknown_availability_clarification.json':'322f0166525f982f33ad1443cb449a3f84e202834f2ec661a15810ee5c2c9a19'}

def need(v,m):
 if not v:raise ValueError(m)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
 with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.monotonic()
 def pin(p,h=None):
  p=Path(p);k=key(p)
  if k not in pins:pins[k]=sha(p)
  need(h is None or pins[k]==h,'exact artifact '+k);return pins[k]
 try:
  for p,h in PINS.items():pin(p,h)
  manifest,summary=read(PACK/'package_manifest.json'),read(PACK/'summary.json')
  need(manifest['schema']=='DIRECT_CELL_UNKNOWN_HOST_TRACE_GZIP_PARTS_V1','literal transport schema')
  need(manifest['raw_part_bytes']==8388608 and manifest['maximum_gzip_part_bytes']==10485760 and manifest['gzip_parameters']==dict(compresslevel=1,mtime=0,filename=''),'preregistered chunk/gzip recipe')
  need(manifest['saved_host_transport_complete'] and manifest['host_originals_preserved'] and not manifest['complete_unsat_proof'] and not manifest['proof_validity_checked'],'host-byte-only transport scope')
  need(manifest['current_ext4_availability']=='NOT_CHECKED_BY_PACKAGER','no false original availability assertion')
  need(summary['package_manifest_path']==key(PACK/'package_manifest.json') and summary['package_manifest_sha256']==PINS[PACK/'package_manifest.json'],'summary manifest binding')
  for p,h in manifest['inputs_sha256'].items():pin(ROOT/p,h)
  for p,h in summary.get('outputs_sha256',{}).items():pin(ROOT/p,h)
  need([r['variant']for r in manifest['records']]==list(GATES),'exact ordered two-stream inventory')
  control=reader.controls(out/'controls');save(out/'controls.json',control)
  checked=[];allparts=set();gate_records=[]
  for record in manifest['records']:
   variant=record['variant'];name,h=GATES[variant];gp=B/'20260930_independent_review'/name/'summary.json';pin(gp,h);gate=read(gp)
   need(gate['status']=='INDEPENDENT_DIRECT_CELL_UNKNOWN_NATIVE_RUN_AUDIT_PASS' and gate['variant']==variant and gate['interpreted_result']=='UNKNOWN','separate exact UNKNOWN audit')
   trace=gate['partial_trace'];need((record['raw_original_path'],record['raw_sha256'],record['raw_bytes'])==(trace['path'],trace['sha256'],trace['bytes']),'previously authenticated host identity')
   need(not record['complete_unsat_proof'] and not record['proof_validity_checked'] and not trace['unsat_certificate'] and record['native_outcome']=='UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME','no proof promotion')
   for field in ('run_summary','run_manifest'):pin(ROOT/record[field+'_path'],record[field+'_sha256'])
   native=read(ROOT/record['run_summary_path']);run_manifest=read(ROOT/record['run_manifest_path'])
   need(record['historical_tool_inputs_sha256']==native['inputs_sha256']==run_manifest['inputs_sha256'],'exact historical source/tool closure')
   for p,h in record['historical_tool_inputs_sha256'].items():pin(ROOT/p,h)
   for p,h in record['separate_outcome_availability_pins'].items():pin(ROOT/p,h)
   need(record['historical_ext4_source']==trace['original_ext4_path']==native['proof_copy']['linux_source'],'historical ext4 identity only')
   original=ROOT/record['raw_original_path'];pin(original,trace['sha256'])
   # The separately written zlib helper expects a label named profile_id only;
   # the adapter changes that metadata key, never bytes or hash semantics.
   adapted=dict(record,profile_id=variant);result=reader.checked_stream(adapted,PACK,original);result['variant']=result.pop('profile_id')
   need(sha(original)==trace['sha256'],'original unchanged after literal comparison')
   for part in record['parts']:
    path=(PACK/part['relative_path']).resolve();need(key(path)not in allparts,'no shared part between streams');allparts.add(key(path));pin(path,part['gzip_sha256'])
   checked.append(result);gate_records.append(dict(variant=variant,path=key(gp),sha256=GATES[variant][1]))
  raw=sum(r['raw_bytes']for r in checked);gz=sum(r['gzip_bytes']for r in checked);parts=sum(len(r['parts'])for r in checked);maximum=max(p['gzip_bytes']for r in checked for p in r['parts'])
  need((raw,gz,parts,maximum)==(1148777487,313868314,138,3199631),'complete exact transport totals')
  need((summary['traces'],summary['raw_bytes'],summary['gzip_bytes'],summary['gzip_parts'],summary['largest_gzip_part_bytes'])==(2,raw,gz,parts,maximum),'reported transport totals')
  need([len(r['parts'])for r in checked]==[49,89],'exact per-variant part totals')
  actual={key(p)for variant in GATES for p in (PACK/variant).glob('*.gz')};need(allparts==actual,'complete package part inventory')
  cli=read(PACK/'recovery_cli_receipt.json');pin(PACK/'recovery_cli_receipt.json')
  need(cli['exit_code']==0 and cli['manifest_sha256']==PINS[PACK/'package_manifest.json'] and cli['proof_validity_checked']is False and cli['command'][-1]=='--verify-only','separate helper receipt scope')
  pin(ROOT/'acceleration/recover_20260930_direct_cell_unknown_trace_package.py','d154ee34d8e2540a7f6620d154f1e9d14cba142be8727e10e2f48f0f51e747d2')
  save(out/'recovered_identity_records.json',dict(records=checked))
  for p in [Path(__file__),PLAN,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
  now=datetime.now(timezone.utc).isoformat();limits=['Lossless transport of saved host partial traces only; neither stream is a complete checked UNSAT proof.','Original ext4 files were absent at the independent outcome audit; no current native-original availability asserted.','No public publication, mathematical feasibility/exclusion or target conclusion.']
  shared=['Independent previously calibrated zlib decoder and literal-original comparator reused from the 54-proof transport checker; only its generic transport functions are called.','No package producer/recovery helper imports; Python SHA256 and zlib implementation shared with usual tooling.','Prior independent UNKNOWN outcome gates bind original host identities; no solver or DRAT checker calls.']
  claim=dict(id='C-FIXED-HADAMARD-DIRECT-CELL-UNKNOWN-TRACE-TRANSPORT',revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The exact138 gzip parts losslessly reconstruct the two saved direct-cell UNKNOWN host partial traces, byte for byte, totalling1148777487 raw bytes. This authenticates transport only and supplies no contradiction proof.',scope='Two literal streams/138parts in the pinned manifest.',dependencies=[dict(id='C-FIXED-HADAMARD-DIRECT-CELL-STANDALONE-NATIVE-UNKNOWN',revision=1,relation='verification_dependency'),dict(id='C-FIXED-HADAMARD-DIRECT-CELL-AT-LEAST-SEVEN-NATIVE-UNKNOWN',revision=1,relation='verification_dependency')],verifier='/root/structural_attack',producer='/root/state_literature_audit',method='Complete zlib recovery with every chunk and whole-stream hash/size/order plus literal comparison to authenticated retained originals.',inputs_sha256=pins,shared_components=shared,limitations=limits,artifact_availability='LOCAL_ONLY',created_at=now,updated_at=now)
  save(out/'claim_binding.json',claim)
  report=dict(status='INDEPENDENT_DIRECT_CELL_UNKNOWN_TRACE_TRANSPORT_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},outcome_gates=gate_records,traces=2,raw_bytes=raw,gzip_bytes=gz,gzip_parts=parts,largest_gzip_part_bytes=maximum,literal_original_comparison=True,corruptions_rejected=len(control['rejected']),shared_components=shared,limitations=limits,solver_calls=0,DRAT_replays=0,complete_unsat_proof=False,target_resolution=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
  save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'))))
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
