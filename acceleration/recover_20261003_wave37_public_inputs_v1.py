"""Restore exactly eight package-backed public inputs with the unchanged restorer.

CI byte-recovery engineering only; no solver or mathematical replay. The previous
six-input wrapper remains immutable. All children share this invocation deadline.
"""
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
PACKAGES={
 'acceleration/results/20261002_wave33_model_package01/manifest.json':'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
 'acceleration/results/20261002_wave33_reconstruction_package01/manifest.json':'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
 'acceleration/results/20261003_wave36_coupling_package01/manifest.json':'38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f',
 'acceleration/results/20261003_wave37_rooted8_package01/manifest.json':'ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14'}
RAW={
 'acceleration/results/20261002_rooted7_extension_model/model.json':'21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595',
 'acceleration/results/20261002_rooted8_universal5_product_model02/model.json':'a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b',
 'acceleration/results/20261002_rooted8_universal5_product_model02/extension_rows.json':'012b02939a96f1ccf24778118c9957760652f42a2a3dd52dce65e43c421ab44d',
 'acceleration/results/20261002_rooted8_universal5_product_model02/product_rows.json':'ca205a283ef8ea39db79807444b06544e76fa4cf7b1032ba07d27e95bb3fcb9a',
 'acceleration/results/20261002_independent_review/rooted8_model01/reconstructed_rows.json':'e55bb55fcf1b90d0088d74a2c6a3c600d94674121f828fc40c450b7d58965bbe',
 'acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/srg243_all_primary_coupling_records.json':'447d922b1a0ad28b3b7d459f84b8c02e55da7b9cc8da8615a5e882b6482d4919',
 'acceleration/results/20261003_rooted8_unrestricted_extension01/model.json':'b143c129fce1f450b54a397d6d508ecb81a67870c2bafd2e9f50dee0bda83f1a',
 'acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/reconstructed_rows.json':'033778d196dcf7d21f76b2460018944b291c1b34b38602ce9f66c24e198dbd70'}
RESTORER='acceleration/recover_20261001_twentyninth_raw_artifacts.py'
RESTORER_SHA='d55e458b2fb980691f416ca346782ba371bf713c80b8ecb055c5240f794a5730'
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):
 with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def population(manifests):
 records=[r for m in manifests for r in m['records']]
 need(len(manifests)==4 and [len(m['records']) for m in manifests]==[4,1,1,2],'exact four-package member counts')
 need(len(records)==8 and len({r['raw_path'] for r in records})==8,'exact eight distinct raw inputs')
 need({r['raw_path']:r['raw_sha256'] for r in records}==RAW,'exact eight raw identities')
 need(sum(r['raw_bytes'] for r in records)==367261301,'exact eight raw byte count')
 need(sum(len(r['parts']) for r in records)==48 and sum(p['gzip_bytes'] for r in records for p in r['parts'])==11723542,'exact48compressed-part byte population')
 return records
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--destination-dir',type=Path,default=ROOT);a=ap.parse_args()
 started=time.monotonic();d=CommandDeadline(a.seconds,allocation_reason='Exactly eight package-backed inputs from4pinned manifests;367,261,301raw bytes48parts,shared deadline20reserve; CI byte recovery only')
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};receipts=[]
 def tick():need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'not completed within the allocated budget')
 def pin(p,h=None):
  tick();v=sha(ROOT/p);need(h is None or v==h,'exact input hash '+p);pins[p]=v
 try:
  pin(RESTORER,RESTORER_SHA)
  for p in [Path(__file__).resolve().relative_to(ROOT).as_posix(),'acceleration/recover_20261003_wave37_public_inputs_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pin(p)
  manifests=[]
  for name,h in PACKAGES.items():pin(name,h);manifests.append(json.loads((ROOT/name).read_bytes()))
  records=population(manifests);controls=[]
  for label,message,mutate in [('missing_member','exact four-package member counts',lambda m:m[0]['records'].pop()),('duplicate_raw','exact eight distinct raw inputs',lambda m:m[2]['records'][0].update(raw_path=m[1]['records'][0]['raw_path'])),('wrong_raw_hash','exact eight raw identities',lambda m:m[2]['records'][0].update(raw_sha256='0'*64)),('wrong_raw_size','exact eight raw byte count',lambda m:m[2]['records'][0].update(raw_bytes=1))]:
   bad=copy.deepcopy(manifests);mutate(bad)
   try:population(bad)
   except ValueError as e:need(str(e)==message,'exact population corruption failure');controls.append({'name':label,'diagnostic':str(e)})
   else:raise ValueError('corrupted input population accepted')
  destination=a.destination_dir.resolve();commands=[]
  for index,(name,h) in enumerate(PACKAGES.items()):
   tick();cmd=[sys.executable,'-B',str(ROOT/RESTORER),'--manifest',str(ROOT/name),'--manifest-sha256',h,'--destination-dir',str(destination),'--receipt',str(out/f'recovery_{index:02d}.json')];commands.append(cmd)
   with (out/f'recovery_{index:02d}.stdout.log').open('xb') as stdout,(out/f'recovery_{index:02d}.stderr.log').open('xb') as stderr:result=subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr,check=False,timeout=max(1,d.status()['remaining_seconds']-20))
   need(result.returncode==0,'unchanged complete recovery child exit zero');r=json.loads((out/f'recovery_{index:02d}.json').read_bytes());need(r['status']=='TWENTYNINTH_RAW_ARTIFACT_RECOVERY_PASS','unchanged exact byte recovery receipt');receipts.append(r)
  need(sum(r['originals'] for r in receipts)==8 and sum(r['raw_bytes'] for r in receipts)==367261301,'complete eight recovered input receipts')
  checked=[]
  for record in records:
   tick();target=destination/record['raw_path'];need(target.is_file() and target.stat().st_size==record['raw_bytes'] and sha(target)==record['raw_sha256'],'complete eight destination hash/size checks')
   checked.append({'path':record['raw_path'],'sha256':record['raw_sha256'],'bytes':record['raw_bytes'],'destination':str(target)})
  report={'status':'WAVE37_EIGHT_PUBLIC_INPUTS_RECOVERED','timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'raw_inputs':8,'raw_bytes':367261301,'gzip_parts':48,'gzip_bytes':11723542,'records':checked,'child_commands':commands,'child_action_counts':[r['action_counts'] for r in receipts],'destination':str(destination),'controls':controls,'mathematical_verification':False,'public_availability_established':False,'original_overwrites':False,'receipts':[str(out/f'recovery_{i:02d}.json') for i in range(4)],'shared_components':['Unchanged pinned historical raw recovery CLI with complete part/whole hashes and nonoverwrite checks; Python gzip/SHA256; shared invocation deadline/supported supervisor.'],'limitations':['CI byte recovery only; independent mathematical audit remains separate.','Existing destination files are identity-checked, never replaced. Clean destination must be asserted by its caller when a clean recovery is claimed.','Source wrapper does not assert public retrieval/availability or replay any proof.'],'elapsed_seconds':time.monotonic()-started,'deadline':d.status()}
  with (out/'summary.json').open('x',encoding='utf8',newline='\n') as s:json.dump(report,s,indent=2,sort_keys=True);s.write('\n')
  print(json.dumps({'status':report['status'],'raw_inputs':8,'raw_bytes':367261301,'elapsed_seconds':report['elapsed_seconds']}),flush=True)
 except BaseException as e:
  with (out/'failure.json').open('x',encoding='utf8',newline='\n') as s:json.dump({'error':repr(e),'inputs_sha256':pins,'completed_packages':len(receipts),'elapsed_seconds':time.monotonic()-started,'original_overwrites':False,'mathematical_verification':False},s,indent=2);s.write('\n')
  raise
if __name__=='__main__':main()
