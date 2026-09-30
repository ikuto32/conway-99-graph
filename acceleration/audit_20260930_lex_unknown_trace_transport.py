"""Independent complete byte recovery of the two lex UNKNOWN partial traces."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,platform,subprocess,sys,time
import audit_20260930_hadamard_fiftyfour_proof_transport as reader
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';PACK=B/'20260930_direct_cell_lex_unknown_trace_package'
GATES={'standalone':('direct_cell_lex_standalone_unknown','f56257086586c6cad43bcab89da071551ca6d67e30196749827bb10dda280233'),'at_least_seven':('direct_cell_lex_coupled_unknown','dde2093be28b749c4bd27e9be06158cce19d84d65aadb1123bc4cfa4d4191e8a')}
PINS={PACK/'package_manifest.json':'f4ab5f151b82bb57f621de549c6e3b7bb0eedbaa92148a7a3fcf89b65831b028',PACK/'summary.json':'0fba8dc84f55815f9b47ed7e10c9762e6a06739fa49e7380b14261116ad2e677',Path(reader.__file__):'4b6c13e4f18c4f2d55a5d683aac1f9ac60cbfdce08cc2bbcca998573225fa0ee'}
def need(b,m):
    if not b:raise ValueError(m)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,h=None):
        k=key(p)
        if k not in pins:pins[k]=sha(p)
        need(h is None or pins[k]==h,'identity '+k)
    try:
        for p,h in PINS.items():pin(p,h)
        manifest=read(PACK/'package_manifest.json');summary=read(PACK/'summary.json')
        need(manifest['schema']=='DIRECT_CELL_LEX_UNKNOWN_HOST_TRACE_GZIP_PARTS_V1','schema')
        need(manifest['raw_part_bytes']==8388608 and manifest['maximum_gzip_part_bytes']==10485760 and manifest['gzip_parameters']==dict(compresslevel=1,mtime=0,filename=''),'chunk recipe')
        need(manifest['saved_host_transport_complete'] and manifest['host_originals_preserved'] and not manifest['complete_unsat_proof'] and not manifest['proof_validity_checked'],'byte scope only')
        need(manifest['current_ext4_availability']=='MISSING_AT_PINNED_OUTCOME_AUDIT','historical availability scope')
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in summary.get(field,{}).items():pin(ROOT/p,h)
        for p,h in manifest['inputs_sha256'].items():pin(ROOT/p,h)
        need([r['variant']for r in manifest['records']]==list(GATES),'exact stream inventory')
        control=reader.controls(out/'controls');save(out/'controls.json',control);checked=[];allparts=set()
        for record in manifest['records']:
            variant=record['variant'];name,h=GATES[variant];gp=B/'20260930_independent_review'/name/'summary.json';pin(gp,h);gate=read(gp)
            need(gate['status']=='INDEPENDENT_DIRECT_CELL_LEX_UNKNOWN_NATIVE_RUN_AUDIT_PASS' and gate['variant']==variant and gate['interpreted_result']=='UNKNOWN','independent saved outcome')
            trace=gate['partial_trace'];need((record['raw_original_path'],record['raw_sha256'],record['raw_bytes'])==(trace['path'],trace['sha256'],trace['bytes']),'raw stream identity')
            need(not trace['unsat_certificate'] and not record['complete_unsat_proof'] and not record['proof_validity_checked'],'partial traces not proofs')
            need(record['current_ext4_availability']=='MISSING_AT_PINNED_OUTCOME_AUDIT' and not trace['current_ext4']['available'],'original availability report')
            for field in ['run_manifest','run_summary']:pin(ROOT/record[field+'_path'],record[field+'_sha256'])
            native=read(ROOT/record['run_summary_path']);run=read(ROOT/record['run_manifest_path']);need(record['historical_tool_inputs_sha256']==native['inputs_sha256']==run['inputs_sha256'],'historical closure')
            for field in ['historical_tool_inputs_sha256','separate_outcome_availability_pins']:
                for p,h in record[field].items():pin(ROOT/p,h)
            need(record['historical_ext4_source']==trace['original_ext4_path']==native['proof_copy']['linux_source'],'historical ext4 path')
            original=ROOT/record['raw_original_path'];pin(original,trace['sha256'])
            result=reader.checked_stream(dict(record,profile_id=variant),PACK,original);result['variant']=result.pop('profile_id');checked.append(result)
            need(sha(original)==trace['sha256'],'original unchanged after literal comparison')
            for part in record['parts']:
                path=(PACK/part['relative_path']).resolve();need(key(path)not in allparts,'disjoint parts');allparts.add(key(path));pin(path,part['gzip_sha256'])
        raw=sum(r['raw_bytes']for r in checked);gz=sum(r['gzip_bytes']for r in checked);parts=sum(len(r['parts'])for r in checked);maximum=max(p['gzip_bytes']for r in checked for p in r['parts'])
        need((raw,gz,parts,maximum)==(699879424,202568717,84,3074380) and [len(r['parts'])for r in checked]==[34,50],'exact complete totals')
        need((summary['traces'],summary['raw_bytes'],summary['gzip_bytes'],summary['gzip_parts'],summary['largest_gzip_part_bytes'])==(2,raw,gz,parts,maximum),'summary totals')
        need(allparts=={key(p)for variant in GATES for p in(PACK/variant).glob('*.gz')},'complete part inventory')
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_LEX_UNKNOWN_TRACE_TRANSPORT.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        need(time.monotonic()-start<120,'audit limit');save(out/'recovered_identity_records.json',dict(records=checked))
        stamp=datetime.now(timezone.utc).isoformat();limitations=['Saved host partial traces only; neither is a checked complete UNSAT proof.','No fresh ext4 availability claim; original paths were missing at separately pinned observations.','Public availability not yet established; no mathematical exclusion or feasibility statement.'];shared=['Calibrated independent zlib/byte comparator reused; no package producer or restorer imported.','Two earlier independent outcome gates authenticate the retained original identities.']
        binding=dict(id='C-FIXED-HADAMARD-DIRECT-CELL-LEX-UNKNOWN-TRACE-TRANSPORT',revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The exact84 gzip parts losslessly reconstruct both saved lex-normalized direct-cell UNKNOWN host partial traces, totaling699879424 bytes, by complete literal comparison. This is transport verification only.',scope='Two literal host streams and84 parts in the pinned manifest.',assumptions=['Exact two saved host originals and pinned prior outcome/availability reports.'],dependencies=[dict(id='C-FIXED-HADAMARD-DIRECT-CELL-LEX-STANDALONE-NATIVE-UNKNOWN',revision=1,relation='verification_dependency'),dict(id='C-FIXED-HADAMARD-DIRECT-CELL-LEX-AT-LEAST-SEVEN-NATIVE-UNKNOWN',revision=1,relation='verification_dependency')],producer='/root/structural_attack',verifier='/root',method='Independent zlib recovery, complete literal-original comparison, all chunk/stream identities and calibrated corruption controls.',inputs_sha256=pins,shared_components=shared,limitations=limitations,created_at=stamp,updated_at=stamp);save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_LEX_UNKNOWN_TRACE_TRANSPORT_PASS',timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},traces=2,raw_bytes=raw,gzip_bytes=gz,gzip_parts=parts,largest_gzip_part_bytes=maximum,corruptions_rejected=len(control['rejected']),solver_calls=0,DRAT_replays=0,complete_unsat_proof=False,shared_components=shared,limitations=limitations,elapsed_seconds=time.monotonic()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
