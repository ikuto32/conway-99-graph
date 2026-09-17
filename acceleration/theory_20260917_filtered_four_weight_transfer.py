"""Finite exact transfer of ten frozen two-coordinate weights to filtered four domains."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import platform
import subprocess
import sys
import time
import numpy as np
import scipy
from scipy.sparse import load_npz
from tqdm import tqdm

BASE = Path('acceleration/results')
OUT = BASE / '20260917_filtered_four_weight_transfer'


def digest(p): return sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_bytes())
def save(p, x):
    with Path(p).open('x', encoding='utf-8') as f: json.dump(x, f, indent=2); f.write('\n')


def main():
    OUT.mkdir(exist_ok=True)
    assert not any(OUT.iterdir())
    model_path = BASE / '20260917_four_matching_filtered_moments/model.json'
    matrix_path = model_path.with_name('integer_augmented_csr.npz')
    old_path = BASE / '20260917_two_matching_moments/model.json'
    cert_paths = [BASE / '20260917_two_matching_moments/exact_support_bound.json'] + [BASE / f'20260917_two_coordinate_small_certificate/denominator_{d:03}.json' for d in (1,2,4,8,16,32,64,128,256)]
    inputs = [model_path,matrix_path,old_path,*cert_paths,Path(__file__),Path('uv.lock')]
    hashes = {str(p):digest(p) for p in inputs}
    assert digest(matrix_path)=='4ec700a9605d721d4739cd1e79e0ceb950fac56afb2f479d797a84851d76a1db'
    save(OUT/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),inputs_sha256=hashes,
        selection='Exactly original two-coordinate certificate followed by all nine frozen denominator cases, in order; no fitting or retries. Old reciprocity weights mapped by unordered edge and 120 new weights set to zero.',
        scope='Only audited four-coordinate matching-filtered domains; 144 fixed outer edges and prescribed absences, 1920 unknown edges, 230879 surviving stars.',
        criterion='Strictly positive exact support bound is a candidate exclusion pending separate raw-neighborhood checking; all nonpositive cases retained.',
        limits='Ten cases; 60 second elapsed cap checked between cases; no solver.',
        timing_deviation='This cheap filtered-domain transfer was added after the separate 2400-second LP began; it was not part of that LP preflight. Earlier transfer used unfiltered domains.',
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),target_resolution='UNKNOWN'))
    m=read(model_path);old=read(old_path);a=load_npz(matrix_path)
    assert m['row_order']=='84 simplex,1920 reciprocity,3486 moments'
    assert m['pair_order']==old['pair_order'] and len(old['unknown_edges'])==1800
    pcount=m['probability_offsets'][-1];assert pcount==230879
    columns=a[:,:pcount].tocsc()
    max_col_l1=int(np.asarray(abs(columns).sum(axis=0)).max())
    results=[];start=time.monotonic()
    for ci,p in enumerate(tqdm(cert_paths,desc='Filtered four exact transfers',unit='weights')):
        if time.monotonic()-start>60: break
        c=read(p);c=c.get('bound',c);d=int(c['denominator'])
        y=list(map(int,c['moment_weight_numerators']));assert len(y)==3486 and max(map(abs,y))<=d
        qmap={tuple(e):int(q) for e,q in zip(old['unknown_edges'],c['reciprocity_weight_numerators'])}
        q=[qmap.get(tuple(e),0) for e in m['unknown_edges']]
        weights=[0]*84+q+y
        assert max(map(abs,weights))*max_col_l1<2**63
        scores=np.asarray(columns.T@np.array(weights,dtype=np.int64)).ravel()
        maxima=[];argmax=[]
        for u,(lo,hi) in enumerate(zip(m['probability_offsets'],m['probability_offsets'][1:])):
            j=int(np.argmax(scores[lo:hi]));maxima.append(int(scores[lo+j]));argmax.append(m['retained_original_domain_ids'][u][j])
        rhsdot=sum(int(w)*int(b) for w,b in zip(weights,m['rhs']))
        numerator=rhsdot-sum(maxima)
        result=dict(source_certificate=str(p),source_sha256=digest(p),denominator=d,numerator=numerator,strictly_positive=numerator>0,
            rhs_dot_numerator=rhsdot,center_maxima_numerators=maxima,first_argmax_original_ids=argmax,
            moment_weight_numerators=y,reciprocity_weight_numerators=q,checked_columns=pcount,
            max_column_l1=max_col_l1,integer_dot_absolute_bound=max(map(abs,weights))*max_col_l1,
            status='CANDIDATE_EXACT_TRANSFER_RESULT',independent_review_pending=True)
        name=f'case_{ci:02}.json';save(OUT/name,result)
        results.append(dict(case=ci,path=name,sha256=digest(OUT/name),numerator=numerator,denominator=d,positive=numerator>0))
    assert all(digest(p)==h for p,h in hashes.items())
    summary=dict(timestamp=datetime.now(timezone.utc).isoformat(),attempted=len(results),selected=10,completed=len(results),positive=sum(r['positive'] for r in results),records=results,elapsed_seconds=time.monotonic()-start,independent_review_pending=True)
    save(OUT/'summary.json',summary);print(json.dumps(summary))


if __name__=='__main__':main()
