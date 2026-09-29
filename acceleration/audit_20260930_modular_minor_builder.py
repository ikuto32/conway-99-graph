"""Independent minor selection from raw graphs, not producer rank output.

This selection path supplies certificates only; a separate exact determinant
checker must approve every raw minor before it is evidence of exclusion.
"""
from datetime import datetime,timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20260930_modular_rank_screen'

def need(condition,message):
    if not condition:raise ValueError(message)
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,value):
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2);stream.write('\n')

def select_minor(matrix,prime,wanted=46):
    # Full row+column pivoting chooses a nonzero Schur-complement entry each
    # step. Original index lists, rather than transformed matrices, certify
    # which literal square submatrix was selected.
    work=[[x%prime for x in row] for row in matrix]
    n=len(work);rows=list(range(n));cols=list(range(n))
    for k in range(wanted):
        pivot=next(((i,j) for i in range(k,n) for j in range(k,n) if work[i][j]),None)
        need(pivot is not None,'no requested nonzero minor found')
        i,j=pivot
        work[k],work[i]=work[i],work[k];rows[k],rows[i]=rows[i],rows[k]
        for row in work:row[k],row[j]=row[j],row[k]
        cols[k],cols[j]=cols[j],cols[k]
        inverse=pow(work[k][k],prime-2,prime)
        for i in range(k+1,n):
            factor=work[i][k]*inverse%prime
            if factor:
                for j in range(k+1,n):work[i][j]=(work[i][j]-factor*work[k][j])%prime
            work[i][k]=0
    selected_rows,selected_cols=rows[:wanted],cols[:wanted]
    return selected_rows,selected_cols,[[matrix[u][v] for v in selected_cols] for u in selected_rows]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((RUN/'manifest.json').read_bytes());screen=json.loads((RUN/'results.json').read_bytes())
    bindings={key(RUN/name):digest(RUN/name) for name in ('manifest.json','results.json')}
    certificates=[]
    for number,record in enumerate(screen['records']):
        path=ROOT/record['path'];need(digest(path)==record['raw_sha256']==manifest['inputs_sha256'][record['path']],'raw input identity')
        bindings[key(path)]=digest(path);graph=json.loads(path.read_bytes())['adjacency_full59']
        need(len(graph)==59 and all(len(row)==59 and all(type(x) is int and x in (0,1) for x in row) for row in graph),'strict raw59matrix')
        need(all(graph[u][u]==0 and all(graph[u][v]==graph[v][u] for v in range(59)) for u in range(59)),'zero diagonal/symmetry')
        for label,prime,bound in (('A_mod3',3,45),('G_mod2',2,44)):
            matrix=graph if label=='A_mod3' else [[27*int(u==v)-9*graph[u][v]+1 for v in range(59)] for u in range(59)]
            rows,cols,minor=select_minor(matrix,prime)
            certificate=dict(raw_graph=record['path'],raw_graph_sha256=digest(path),matrix=label,prime=prime,
                target_rank_upper_bound=bound,certified_rank_lower_bound_candidate=46,rows_zero_based=rows,columns_zero_based=cols,
                raw_integer_minor=minor,status='CANDIDATE_MINOR_PENDING_SEPARATE_EXACT_DETERMINANT_CHECK')
            output=args.out/f'graph_{number:02d}_{label}.json';save(output,certificate)
            certificates.append(dict(path=key(output),sha256=digest(output),graph_index=number,matrix=label))
    for path in (__file__,ROOT/'uv.lock'):bindings[key(path)]=digest(path)
    save(args.out/'index.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        producer_imported=False,selection='First46full-pivot modular Schur-complement pivots, independently selected from raw matrices',
        certificates=certificates,certificate_count=len(certificates),status='CANDIDATE_MINOR_CERTIFICATES_REQUIRING_EXACT_DETERMINANT_CHECK',
        full_rank_claimed=False,target_resolution=False))
    print(json.dumps(dict(certificates=len(certificates),index_sha256=digest(args.out/'index.json'))))

if __name__=='__main__':main()
