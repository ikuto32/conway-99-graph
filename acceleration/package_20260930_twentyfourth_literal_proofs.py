"""Lossless wave24 supplementary transport; no mathematical verification."""
from pathlib import Path
import gzip, hashlib, io, json, sys
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
RECORDS=[
 (B+'hadamard_seven_profile_native_pilot/main/proof.drat','1f2bffea9b59e2a3d17da368468ea5ef8750082fb3d244b4b8f8c07c48f283c6'),
 (B+'eight_count_profile_native_pilot/main/proof.drat','991ee07197c5ce385a7aefc04e64f663b4882b8e83e9772fb66b672874f62106'),
 (B+'hadamard_count_master_native_pilot_v2/main/proof.drat','556660749f70096f4384794d9b9867cfe4608d43122a44e47a0b4ebd956c37a7'),
 (B+'independent_review/hadamard_twohundredfifteen_profile_object_calibration/local_decode_controls.json','6bda307d938dee3a891b00e870260f799dae49a2db88ce9152ef9d556d3081ab'),
]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
 out=ROOT/(B+'twentyfourth_literal_proof_package');out.mkdir(exist_ok=False)
 records=[]
 for index,(name,expected) in enumerate(RECORDS):
  raw=(ROOT/name).read_bytes();assert sha(raw)==expected
  stream=io.BytesIO()
  with gzip.GzipFile(filename='',fileobj=stream,mode='wb',compresslevel=9,mtime=0) as gz:gz.write(raw)
  packed=stream.getvalue();assert len(packed)<10*1024**2 and gzip.decompress(packed)==raw
  dest=out/f'artifact_{index}.gz';dest.write_bytes(packed)
  try:gzip.decompress(packed[:-5]);raise AssertionError('truncated gzip accepted')
  except (EOFError,gzip.BadGzipFile):pass
  damaged=bytearray(packed);damaged[-8]^=1
  try:gzip.decompress(damaged);raise AssertionError('CRC corruption accepted')
  except (EOFError,gzip.BadGzipFile):pass
  records.append(dict(raw_original_path=name,raw_sha256=expected,raw_bytes=len(raw),parts=[dict(index=0,relative_path=dest.name,raw_offset=0,raw_bytes=len(raw),raw_sha256=expected,gzip_bytes=len(packed),gzip_sha256=sha(packed))]))
 result=dict(status='TWENTYFOURTH_SUPPLEMENTARY_BYTE_TRANSPORT_PASS',records=records,inputs_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):sha(Path(__file__).read_bytes())},controls_rejected=['truncated gzip','CRC corruption'],proof_validity_checked=False,originals_preserved=True,scope='Two independently checked literal UNSAT proofs; the SAT count-master trace is incomplete and is NOT an UNSAT certificate; the fourth artifact contains calibration objects only.')
 (out/'package_manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(proofs=len(records),raw_bytes=sum(r['raw_bytes'] for r in records),gzip_bytes=sum(r['parts'][0]['gzip_bytes'] for r in records))))
if __name__=='__main__':main()
