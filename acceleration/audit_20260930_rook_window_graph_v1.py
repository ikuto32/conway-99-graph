"""Independent direct validator for a frozen-star 59-vertex rook window.

The 59 vertices are rook core 0..8 followed by five external cells of size10.
This never validates a Conway99 target; it checks only the exact local family.
No producer or solver module is imported.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COORDINATES = ((0,0),(1,1),(1,2),(2,1),(2,2))
STAR_HASH = 'da71c5381af0a68f8a7e7dea36535b92cbcfc67d95e3b57d6cc3591dd1dda33f'


def need(condition,message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def fixed_external(star):
    edges = set()
    def insert(a,b):
        edge = tuple(sorted((a,b)))
        need(0 <= edge[0] < edge[1] < 50 and edge not in edges,'fixed edge shape/duplicate')
        edges.add(edge)
    for a,b in star['matching']:
        insert(a,b)
    need(len(star['matching']) == 5 and sorted(v for edge in star['matching'] for v in edge) == list(range(10)),'central matching')
    need(len(star['four_factors']) == 4,'four fixed incidence blocks')
    for cell,record in enumerate(star['four_factors'],1):
        matching = record['partner_matching']
        need(len(matching) == 5 and sorted(v for edge in matching for v in edge) == list(range(10)),'right internal matching')
        for a,b in matching:
            insert(cell*10+a,cell*10+b)
        block = record['incidence_block']
        need(len(block) == 10 and all(len(row) == 10 and all(type(v) is int and v in (0,1) for v in row) for row in block),'binary incidence block')
        need(all(sum(row) == 2 for row in block) and all(sum(block[a][b] for a in range(10)) == 2 for b in range(10)),'fixed two-regular block')
        for a,row in enumerate(block):
            for b,value in enumerate(row):
                if value:
                    insert(a,cell*10+b)
    need(len(edges) == 105,'fixed external edge total')
    return edges


def embed59(external):
    need(len(external) == 50 and all(len(row) == 50 for row in external),'external dimension')
    matrix = [[0]*59 for _ in range(59)]
    for a,b in combinations(range(9),2):
        matrix[a][b] = matrix[b][a] = int(a//3 == b//3 or a%3 == b%3)
    for u in range(50):
        row,column = COORDINATES[u//10]
        core = 3*row+column
        matrix[core][u+9] = matrix[u+9][core] = 1
        for v in range(50):
            matrix[u+9][v+9] = external[u][v]
    return matrix


def validate(matrix,star,require_block_degrees=True):
    need(len(matrix) == 59 and all(len(row) == 59 and all(type(v) is int and v in (0,1) for v in row) for row in matrix),'binary59 matrix')
    need(all(matrix[u][u] == 0 for u in range(59)) and all(matrix[u][v] == matrix[v][u] for u,v in combinations(range(59),2)),'simple undirected59 graph')
    neighbors = [{v for v,value in enumerate(row) if value} for row in matrix]
    need(all(len(row) <= 14 for row in neighbors),'known degree exceeds14')
    need(all(len(neighbors[u]&neighbors[v]) <= 2-matrix[u][v] for u,v in combinations(range(59),2)),'full59 common-neighbor upper cap')
    for a,b in combinations(range(9),2):
        need(matrix[a][b] == int(a//3 == b//3 or a%3 == b%3),'rook core identity')
    for u in range(50):
        row,column = COORDINATES[u//10]
        owner = 3*row+column
        need([matrix[u+9][core] for core in range(9)] == [int(core == owner) for core in range(9)],'external owner-core adjacency')
    fixed = fixed_external(star)
    unknown = {(u,v) for u,v in combinations(range(10,50),2) if u//10 != v//10}
    need(len(unknown) == 600,'unknown edge universe')
    for u,v in combinations(range(50),2):
        if (u,v) not in unknown:
            need(matrix[u+9][v+9] == int((u,v) in fixed),'fixed external edge/absence')
    block_records = []
    for ca,cb in combinations(range(1,5),2):
        target = 1 if (COORDINATES[ca][0] == COORDINATES[cb][0] or COORDINATES[ca][1] == COORDINATES[cb][1]) else 2
        row_degrees = [sum(matrix[9+10*ca+i][9+10*cb+j] for j in range(10)) for i in range(10)]
        column_degrees = [sum(matrix[9+10*ca+i][9+10*cb+j] for i in range(10)) for j in range(10)]
        if require_block_degrees:
            need(row_degrees == [target]*10 and column_degrees == [target]*10,'right-block degree mismatch')
        block_records.append(dict(cells=[ca,cb],required_degree=target,row_degrees=row_degrees,column_degrees=column_degrees))
    return dict(vertices=59,checked_pairs=1711,edge_count=sum(map(len,neighbors))//2,
                maximum_known_degree=max(map(len,neighbors)),required_right_block_degrees_checked=require_block_degrees,
                unknown_edges=600,blocks=block_records,target_graph=False)


def controls(star):
    external = [[0]*50 for _ in range(50)]
    for a,b in fixed_external(star):
        external[a][b] = external[b][a] = 1
    base = embed59(external)
    result = validate(base,star,False)
    rejected = []
    for name in ('loop','asymmetry','extra_owner_core','fixed_edge_deleted','complete_degree_claim'):
        bad = deepcopy(base)
        if name == 'loop':
            bad[0][0] = 1
        elif name == 'asymmetry':
            bad[9][10] = 1-bad[9][10]
        elif name == 'extra_owner_core':
            bad[9][1] = bad[1][9] = 1
        elif name == 'fixed_edge_deleted':
            a,b = sorted(fixed_external(star))[0]
            bad[a+9][b+9] = bad[b+9][a+9] = 0
        try:
            validate(bad,star,name == 'complete_degree_claim')
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('corrupted raw59 control accepted: '+name)
    return dict(positive_fixed_partial59=result,corruptions_rejected=rejected,
                limitation='Positive fixture is the fixed partial59 base. It intentionally does not assert a completed right-block assignment exists.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--star',type=Path,required=True)
    parser.add_argument('--input',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    need(not args.out.exists(),'refuse overwrite')
    need(digest(args.star) == STAR_HASH,'frozen central-star identity')
    star = json.loads(args.star.read_bytes())
    calibration = controls(star)
    bindings = {str(args.star):digest(args.star),str(Path(__file__).relative_to(ROOT)):digest(__file__),'uv.lock':digest(ROOT/'uv.lock')}
    verdict = 'INDEPENDENT_RAW59_CONTROLS_PASS'
    result = None
    if args.input:
        raw = json.loads(args.input.read_bytes())
        bindings[str(args.input)] = digest(args.input)
        if 'adjacency_full59' in raw:
            matrix = raw['adjacency_full59']
        else:
            need('external_adjacency_rows_hex' in raw,'raw graph payload missing')
            rows = [int(value,16) for value in raw['external_adjacency_rows_hex']]
            need(len(rows) == 50 and all(0 <= row < 1 << 50 for row in rows),'raw external rows')
            matrix = embed59([[int(row >> v & 1) for v in range(50)] for row in rows])
        result = validate(matrix,star,True)
        verdict = 'INDEPENDENT_FROZEN_STAR_RAW59_WINDOW_PASS'
    report = dict(status=verdict,timestamp=datetime.now(timezone.utc).isoformat(),
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  inputs_sha256=bindings,controls=calibration,result=result,producer_imported=False,
                  scope='One exact central factor star and five internal matchings; arbitrary four perfect-matching and two bipartite2regular right-cell blocks, embedded with the full rook9 core.',
                  limitations=['A valid59vertex window is necessary only; it does not extend the remaining40externalvertices.',
                               'No target graph, unrestricted exclusion, or universal rook containment claim.'],target_resolution=False)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=verdict,sha256=digest(args.out))))


if __name__ == '__main__':
    main()
