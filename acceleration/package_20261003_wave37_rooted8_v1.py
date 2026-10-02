"""Lossless publication payload for two frozen unrestricted root8 operator records.

No mathematical checking, claim promotion, or alteration of historical bytes.
The unchanged recovery tool can independently restore this manifest format.
"""
import argparse,gzip,hashlib,json,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
PINS={
 'acceleration/results/20261003_rooted8_unrestricted_extension01/model.json':'b143c129fce1f450b54a397d6d508ecb81a67870c2bafd2e9f50dee0bda83f1a',
 'acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/reconstructed_rows.json':'033778d196dcf7d21f76b2460018944b291c1b34b38602ce9f66c24e198dbd70',
}
AUDIT='acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/summary.json'
AUDIT_SHA='ec5073a22027c512e29dac1d49048a507f272cb8ce1a0a79d2ca1f663f1be974'
CHUNK=8*1024**2

def need(ok,message):
 if not ok:raise ValueError(message)

def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True)
 args=ap.parse_args();out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace payload destination');out.mkdir(parents=True,exist_ok=False)
 deadline=CommandDeadline(args.seconds,allocation_reason='Lossless two-file unrestricted root8 payload; exact frozen bytes, per-part receipts and independent recovery pending')
 def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within allocated budget; completed chunks preserved')
 tick();need(sha(ROOT/AUDIT)==AUDIT_SHA,'exact independent audit identity')
 audit=json.loads((ROOT/AUDIT).read_text(encoding='utf8'))
 recorded=dict(audit['inputs_sha256']);recorded.update({str(Path(AUDIT).parent/p).replace('\\','/'):h for p,h in audit['outputs_sha256'].items()})
 need(all(recorded.get(name)==identity for name,identity in PINS.items()),'raw identity bound by complete independent audit')
 records=[]
 for index,(name,identity) in enumerate(tqdm(PINS.items(),desc='Package fixed unrestricted-root8 bytes',mininterval=1)):
  tick();source=ROOT/name;need(sha(source)==identity,'exact frozen raw identity');parts=[];whole=hashlib.sha256();total=0
  with source.open('rb') as stream:
   for number,block in enumerate(iter(lambda:stream.read(CHUNK),b'')):
    tick();target=out/f'file_{index:02d}_part_{number:03d}.gz'
    with target.open('xb') as writer:
     with gzip.GzipFile(filename='',fileobj=writer,mode='wb',mtime=0,compresslevel=9) as compressed:compressed.write(block)
    need(gzip.decompress(target.read_bytes())==block,'literal recovered chunk bytes')
    parts.append(dict(path=target.relative_to(ROOT).as_posix(),gzip_sha256=sha(target),gzip_bytes=target.stat().st_size,raw_offset=total,raw_sha256=hashlib.sha256(block).hexdigest(),raw_bytes=len(block)))
    total+=len(block);whole.update(block)
  need(total==source.stat().st_size and whole.hexdigest()==identity,'complete original identity')
  record=dict(raw_path=name,raw_sha256=identity,raw_bytes=total,kind='unrestricted_root8_operator_or_independent_reconstruction',parts=parts);records.append(record)
  with (out/f'record_{index:02d}.json').open('x',encoding='utf8',newline='\n') as receipt:json.dump(record,receipt,indent=2);receipt.write('\n')
 manifest=dict(schema='WAVE33_LITERAL_MODELS_LOSSLESS_V1',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_sha256=sha(Path(__file__)),record_count=len(records),raw_bytes=sum(r['raw_bytes'] for r in records),gzip_parts=sum(len(r['parts']) for r in records),gzip_bytes=sum(p['gzip_bytes'] for r in records for p in r['parts']),records=records,mathematical_verification=False,independent_recovery_pending=True,availability='LOCAL_ONLY',originating_audit=dict(path=AUDIT,sha256=AUDIT_SHA),limitations=['Exact byte packaging only; operator necessity has a separate complete independent audit.','No entire historical transitive closure or platform binaries.','Public availability requires a separate immutable publication check.'])
 with (out/'manifest.json').open('x',encoding='utf8',newline='\n') as writer:json.dump(manifest,writer,indent=2);writer.write('\n')
 print(json.dumps({key:manifest[key] for key in ('record_count','raw_bytes','gzip_parts','gzip_bytes')}))

if __name__=='__main__':main()
