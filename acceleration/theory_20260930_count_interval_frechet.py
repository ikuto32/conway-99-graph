"""Cheap complete falsification of a closed-form local interval conjecture."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
PINS={B+'hadamard_count_gram_intervals/signature_intervals.json.gz':'41c4269eb86477069e63900e14296e88734d668a160907f5ce1f0277d2cd230a',B+'hadamard_count_master_preflight/local_signatures.json':'075120017568ecbb0da5369f8e45c0dafd015ae4953681491bab66f04e9fdb45',B+'independent_review/count_gram_intervals/summary.json':'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33'}
def sha(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    for p,h in PINS.items():assert sha(p)==h;pins[p]=h
    for p in (Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml'):pins[p]=sha(p)
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,limit_seconds=30))
    with gzip.open(ROOT/(B+'hadamard_count_gram_intervals/signature_intervals.json.gz'),'rt',encoding='utf8') as f:intervals=json.load(f)
    signatures=json.loads((ROOT/(B+'hadamard_count_master_preflight/local_signatures.json')).read_bytes())['signatures'];bad=[];checked=0
    for sid,(sig,record) in enumerate(zip(signatures,intervals['records'],strict=True)):
        assert sig['index']==record['signature_index']==sid
        for cell,(x,y,f,g) in enumerate(intervals['local_cells']):
            n,m=sig['counts'][3*x+f],sig['counts'][3*y+g];lo=max(0,n+m-3);hi=min(n,m,1 if f==g else2);checked+=1
            if lo!=record['minimum'][cell] or hi!=record['maximum'][cell]:bad.append(dict(signature_index=sid,cell_index=cell,row_counts=[n,m],fibres=[f,g],proposed_minimum=lo,proposed_maximum=hi,actual_minimum=record['minimum'][cell],actual_maximum=record['maximum'][cell]))
        assert time.monotonic()-start<30
    assert checked==818235;save(out/'mismatches.json',dict(records=bad))
    result=dict(status='CANDIDATE_COMPLETE_FRECHET_EQUALITY' if not bad else 'PROPOSED_FRECHET_EQUALITY_COUNTEREXAMPLES',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT).as_posix()) for p in out.iterdir()},checked_cells=checked,mismatching_cells=len(bad),first_counterexample=bad[0] if bad else None,first_counterexample_null_reason='All finite cells agree.' if not bad else None,elapsed_seconds=time.monotonic()-start,native_calls=0,independent_approval=False,target_resolution=False,scope='Proposed exact local scalar extrema formula on the frozen6061 classes; not simultaneous realization or full factor feasibility.')
    save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256')}))
if __name__=='__main__':main()
