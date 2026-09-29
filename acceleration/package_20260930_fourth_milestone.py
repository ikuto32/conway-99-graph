"""Preserve exact public gzip companions for oversized completed raw artifacts."""
from datetime import datetime,timezone
from hashlib import sha256
import gzip,json
from pathlib import Path
import shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/'
RAW=[BASE+x for x in ['20260930_eight_full99_cnf/clauses.body','20260930_eight_full99_cnf/instance.cnf','20260930_eight_full99_cnf/model.json',
    '20260930_rook_box_checker_controls/instance.cnf','20260930_rook_box_lazy_wave02/round_01/instance.cnf',
    '20260930_rook_box_lazy_wave02/round_02/instance.cnf','20260930_rook_orbit_solver_pilot/instance.cnf']]
def digest(p):
    h=sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    entries=[];ignore=[]
    for name in RAW:
        raw=ROOT/name;packed=raw.with_name(raw.name+'.gz');expected=digest(raw)
        if not packed.exists():
            with raw.open('rb') as src,packed.open('xb') as dst:
                with gzip.GzipFile(filename='',mode='wb',fileobj=dst,mtime=0,compresslevel=6) as z:shutil.copyfileobj(src,z,1048576)
        h=sha256();size=0
        with gzip.open(packed,'rb') as f:
            for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
        assert h.hexdigest()==expected and size==raw.stat().st_size
        assert packed.stat().st_size<=10*1024*1024
        entries.append(dict(raw=name,sha256=expected,bytes=size,availability='LOCAL_ONLY',
            public_companion=packed.relative_to(ROOT).as_posix(),gzip_sha256=digest(packed),gzip_bytes=packed.stat().st_size,
            recovery='Decompress the exact gzip companion and verify the raw SHA256.',independent_raw_reconstruction=True))
        ignore.append('/'+name)
    gitignore=ROOT/'.gitignore';old=gitignore.read_text();new=[s for s in ignore if s not in old.splitlines()]
    with gitignore.open('a',encoding='utf-8',newline='\n') as f:f.write('\n# Fourth resumed milestone; oversized raw originals have exact gzip companions.\n'+'\n'.join(new)+'\n')
    record=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=digest(Path(__file__)),
        status='EXACT_GZIP_RECONSTRUCTION_CHECKED',mathematical_verification=False,entries=entries)
    with (ROOT/(BASE+'20260930_resume/fourth_artifact_catalog.json')).open('x',encoding='utf-8',newline='\n') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps({'raw_originals':len(entries),'public_companion_bytes':sum(e['gzip_bytes'] for e in entries)}))
if __name__=='__main__':main()
