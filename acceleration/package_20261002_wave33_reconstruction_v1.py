"""Lossless publication payload for the independent full row reconstruction.

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
 'acceleration/results/20261002_independent_review/rooted8_model01/reconstructed_rows.json':'e55bb55fcf1b90d0088d74a2c6a3c600d94674121f828fc40c450b7d58965bbe',
}
CHUNK=8*1024**2

def need(ok,message):
 if not ok:raise ValueError(message)

def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True)
 args=ap.parse_args();out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace payload destination');out.mkdir(parents=True,exist_ok=False)
 deadline=CommandDeadline(args.seconds,allocation_reason='Lossless independent reconstruction payload; exact frozen bytes, per-part receipts and independent recovery pending')
 def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within allocated budget; completed chunks preserved')
 records=[]
 for index,(name,identity) in enumerate(tqdm(PINS.items(),desc='Package fixed model bytes',mininterval=1)):
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
  record=dict(raw_path=name,raw_sha256=identity,raw_bytes=total,kind='literal_structural_model',parts=parts);records.append(record)
  with (out/f'record_{index:02d}.json').open('x',encoding='utf8',newline='\n') as receipt:json.dump(record,receipt,indent=2);receipt.write('\n')
 manifest=dict(schema='WAVE33_INDEPENDENT_RECONSTRUCTION_LOSSLESS_V1',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_sha256=sha(Path(__file__)),record_count=len(records),raw_bytes=sum(r['raw_bytes'] for r in records),gzip_parts=sum(len(r['parts']) for r in records),gzip_bytes=sum(p['gzip_bytes'] for r in records for p in r['parts']),records=records,mathematical_verification=False,independent_recovery_pending=True,availability='LOCAL_ONLY',limitations=['Exact byte packaging only; model mathematics needs its own independent audit.','No entire historical transitive closure or platform binaries.','Public availability requires a separate immutable publication check.'])
 with (out/'manifest.json').open('x',encoding='utf8',newline='\n') as writer:json.dump(manifest,writer,indent=2);writer.write('\n')
 print(json.dumps({key:manifest[key] for key in ('record_count','raw_bytes','gzip_parts','gzip_bytes')}))

if __name__=='__main__':main()
