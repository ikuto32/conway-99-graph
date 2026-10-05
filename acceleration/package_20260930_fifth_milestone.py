"""Check recovery of unrestricted raw inputs and record local/public separation."""
from datetime import datetime,timezone
from hashlib import sha256
import gzip,io,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_unrestricted_full99_cnf'
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def main():
    entries=[]
    for name in ['instance.cnf','model.json']:
        raw=D/name;parts=sorted(D.glob(name+'.gz.part*'));assert parts
        compressed=b''.join(p.read_bytes() for p in parts)
        digest=sha256();size=0;body=sha256()
        with gzip.GzipFile(fileobj=io.BytesIO(compressed),mode='rb') as stream:
            if name=='instance.cnf':
                header=stream.readline();assert header==b'p cnf 1186500 4136454\n';digest.update(header);size+=len(header)
            for chunk in iter(lambda:stream.read(1048576),b''):
                digest.update(chunk);size+=len(chunk)
                if name=='instance.cnf':body.update(chunk)
        assert digest.hexdigest()==h(raw) and size==raw.stat().st_size
        entries.append({'raw':raw.relative_to(ROOT).as_posix(),'sha256':h(raw),'bytes':size,'availability':'LOCAL_ONLY',
            'recovery':'Concatenate these ordered gzip parts, decompress, and check raw SHA256.',
            'gzip_sha256':sha256(compressed).hexdigest(),'parts':[{'path':p.relative_to(ROOT).as_posix(),'sha256':h(p),'bytes':p.stat().st_size} for p in parts]})
        if name=='instance.cnf':
            assert body.hexdigest()==h(D/'clauses.body')
            entries.append({'raw':(D/'clauses.body').relative_to(ROOT).as_posix(),'sha256':body.hexdigest(),'bytes':(D/'clauses.body').stat().st_size,
                'availability':'LOCAL_ONLY','recovery':'Remove exactly the first LF-terminated DIMACS header line from the recovered instance.cnf; all remaining bytes equal this intermediate body.'})
    with (ROOT/'.gitignore').open('a',encoding='utf-8',newline='\n') as f:
        f.write('\n# Fifth resumed milestone; unrestricted raw originals recover from checked parts.\n')
        f.write('\n'.join('/'+e['raw'] for e in entries)+'\n')
    p=ROOT/'acceleration/results/20260930_resume/fifth_artifact_catalog.json'
    record={'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'source_sha256':h(Path(__file__)),'entries':entries,
        'status':'EXACT_PART_RECONSTRUCTION_CHECKED','mathematical_verification':False}
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps({'raw_originals':len(entries),'reconstruction':'PASS'}))
if __name__=='__main__':main()
