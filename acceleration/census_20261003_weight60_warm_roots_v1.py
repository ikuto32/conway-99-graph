"""Complete finite root census of two frozen, independently checked raw graphs.

Producer only: no SAT instance, solver invocation, target exclusion or approval.
"""
import argparse,copy,hashlib,itertools,json,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
RAW_PREFIX='acceleration/results/20261002_hypergraph_weight60_pilot01/native/'
PINS={RAW_PREFIX+'best.adj':'818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836',
      RAW_PREFIX+'first_lambda0.adj':'c95eff815f69c6d7c4122c5c0cde96d8c5124ffec892f3d8a4913ad0b1486f21'}
REPORT='acceleration/results/20261003_independent_review/weight60_pilot01/summary.json'
REPORT_SHA='a80ec86298ce13ae8fea44c118ebbe613dd4b55e4387ac49e39ec9b3d4cd40d2'
SPEC='acceleration/census_20261003_weight60_warm_roots_v1_spec.md'

class CensusError(ValueError):pass
def need(ok,stage):
    if not ok:raise CensusError(stage)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')
def encode(rows):return (str(len(rows))+'\n'+'\n'.join(''.join(map(str,row)) for row in rows)+'\n').encode('ascii')
def parse(raw,n,k):
    try:lines=raw.decode('ascii').splitlines()
    except UnicodeDecodeError:raise CensusError('BINARY')
    need(len(lines)==n+1 and lines[0]==str(n) and all(len(line)==n for line in lines[1:]),'SHAPE')
    need(all(set(line)<=set('01') for line in lines[1:]),'BINARY')
    rows=[[int(c) for c in line] for line in lines[1:]]
    need(all(rows[i][i]==0 for i in range(n)),'DIAGONAL')
    need(all(rows[i][j]==rows[j][i] for i in range(n) for j in range(i+1,n)),'SYMMETRY')
    need(all(sum(row)==k for row in rows),'DEGREE')
    return rows
def masks(rows):return [sum(value<<j for j,value in enumerate(row)) for row in rows]
def record(rows,bits,r):
    n=len(rows);neighbors=[i for i in range(n) if rows[r][i]]
    outsiders=[i for i in range(n) if i!=r and not rows[r][i]]
    matching=[[i,j] for i,j in itertools.combinations(neighbors,2) if rows[i][j]]
    degrees={str(i):sum(rows[i][j] for j in neighbors) for i in neighbors}
    outside_records=[];hist={str(c):0 for c in range(len(neighbors)+1)};energy=0
    for v in outsiders:
        common=(bits[r]&bits[v]).bit_count();hist[str(common)]+=1;energy+=(common-2)**2
        outside_records.append(dict(vertex=v,common_neighbor_count=common,
                                    common_neighbors=[w for w in neighbors if rows[v][w]],
                                    cn2_eligible=common==2))
    return dict(root=r,neighbors=neighbors,neighbor_count=len(neighbors),
                neighborhood_matching_edges=matching,neighborhood_internal_degrees=degrees,
                neighborhood_is_perfect_matching=(len(neighbors)%2==0 and len(matching)==len(neighbors)//2 and all(x==1 for x in degrees.values())),
                outside_count=len(outsiders),outsiders=outside_records,
                cn2_eligible_outside_vertices=[v['vertex'] for v in outside_records if v['cn2_eligible']],
                cn2_eligible_count=sum(v['cn2_eligible'] for v in outside_records),
                mu_row_residual=energy,outside_common_neighbor_histogram=hist)
def check_record(rows,rec):
    r=rec['root'];need(type(r)is int and 0<=r<len(rows),'ROOT')
    need(rec==record(rows,masks(rows),r),'SCORE_RECORD')
def rejected(call,stage):
    try:call()
    except CensusError as error:need(str(error)==stage,'WRONG_CONTROL_STAGE');return stage
    raise CensusError('MISSING_CONTROL_VETO')
def calibration(out,actual):
    fixture=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)]
    raw=encode(fixture);save(out/'rook9.json',dict(n=9,k=4,rows=fixture));(out/'rook9.adj').write_bytes(raw)
    parsed=parse(raw,9,4);bits=masks(parsed);controls=[]
    for r in range(9):
        result=record(parsed,bits,r);need(result['mu_row_residual']==0 and result['cn2_eligible_count']==4 and result['neighborhood_is_perfect_matching'],'ROOK9_POSITIVE')
    need(record(parsed,bits,0)['neighbors']==[1,2,3,6] and record(parsed,bits,0)['neighborhood_matching_edges']==[[1,2],[3,6]],'ROOK9_LITERAL')
    save(out/'rook9_all_roots.json',[record(parsed,bits,r) for r in range(9)])
    def matrix_negative(label,rows,n,k,stage):
        name=label+'.adj';data=encode(rows);(out/name).write_bytes(data)
        controls.append(dict(label=label,expected_stage=stage,actual_stage=rejected(lambda:parse(data,n,k),stage),artifact=name))
    diag=copy.deepcopy(parsed);diag[0][0]=1;matrix_negative('rook9_diagonal',diag,9,4,'DIAGONAL')
    asymmetric=copy.deepcopy(parsed);asymmetric[0][1]=0;matrix_negative('rook9_asymmetric',asymmetric,9,4,'SYMMETRY')
    degree=copy.deepcopy(parsed);degree[0][1]=degree[1][0]=0;matrix_negative('rook9_degree',degree,9,4,'DEGREE')
    invalid=raw.replace(b'000',b'200',1);(out/'rook9_binary.adj').write_bytes(invalid)
    controls.append(dict(label='rook9_binary',actual_stage=rejected(lambda:parse(invalid,9,4),'BINARY'),expected_stage='BINARY'))
    controls.append(dict(label='rook9_wrong_target99_scope',actual_stage=rejected(lambda:parse(raw,99,14),'SHAPE'),expected_stage='SHAPE'))
    corrupt_score=record(parsed,bits,0);corrupt_score['mu_row_residual']=1;save(out/'rook9_corrupt_score.json',corrupt_score)
    controls.append(dict(label='rook9_corrupt_score',actual_stage=rejected(lambda:check_record(parsed,corrupt_score),'SCORE_RECORD'),expected_stage='SCORE_RECORD'))
    corrupt_count=record(parsed,bits,0);corrupt_count['outsiders'][0]['common_neighbor_count']=3;save(out/'rook9_corrupt_count.json',corrupt_count)
    controls.append(dict(label='rook9_corrupt_count',actual_stage=rejected(lambda:check_record(parsed,corrupt_count),'SCORE_RECORD'),expected_stage='SCORE_RECORD'))
    target=actual;bad=copy.deepcopy(target);bad[0][0]=1;matrix_negative('actual99_diagonal',bad,99,14,'DIAGONAL')
    v=next(i for i in range(99) if target[0][i]);bad=copy.deepcopy(target);bad[0][v]=bad[v][0]=0;matrix_negative('actual99_degree',bad,99,14,'DEGREE')
    corrupt_target=record(target,masks(target),0);corrupt_target['mu_row_residual']+=1;save(out/'actual99_corrupt_score.json',corrupt_target)
    controls.append(dict(label='actual99_corrupt_score',actual_stage=rejected(lambda:check_record(target,corrupt_target),'SCORE_RECORD'),expected_stage='SCORE_RECORD'))
    controls.append(dict(label='control_harness_wrong_diagnostic',actual_stage=rejected(lambda:rejected(lambda:parse(raw,99,14),'BINARY'),'WRONG_CONTROL_STAGE'),expected_stage='WRONG_CONTROL_STAGE'))
    report=dict(status='PRODUCER_WARM_ROOT_CENSUS_V1_CALIBRATION_COMPLETE',positive_rook_roots=9,negative_controls=controls,independent_approval=False,
                limitations=['Producer-internal finite controls only; separate dense checking path must approve the actual census.','Generic rook9 is not a target99 certificate.'])
    save(out/'summary.json',report);return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=float,required=True)
    a=p.parse_args();d=CommandDeadline(a.seconds,allocation_reason='Frozen two raw99 graphs all198roots exactinteger scaffold census and controls;100worker20reserve; no solver')
    out=a.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_SCOPE');out.mkdir(parents=True,exist_ok=False)
    def tick():need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')
    try:
        tick();need(sha(ROOT/REPORT)==REPORT_SHA,'INDEPENDENT_REPORT_PIN')
        audited=json.loads((ROOT/REPORT).read_text(encoding='utf8'))
        need(audited['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS','INDEPENDENT_REPORT_STATUS')
        rows_by_name={}
        for path,pin in PINS.items():
            need(sha(ROOT/path)==pin and audited['inputs_sha256'][path]==pin,'RAW_PIN');rows_by_name[path]=parse((ROOT/path).read_bytes(),99,14)
        controls=out/'controls';controls.mkdir();cal=calibration(controls,next(iter(rows_by_name.values())));tick()
        graphs=[]
        for label,(path,rows) in zip(['final_best','first_lambda0'],rows_by_name.items()):
            bits=masks(rows);triples=[];triple_checks=0
            for i,j,k in itertools.combinations(range(99),3):
                triple_checks+=1
                if rows[i][j] and rows[i][k] and rows[j][k]:triples.append([i,j,k])
            need(triple_checks==156849,'TRIPLE_COVERAGE');save(out/(label+'_triangles.json'),dict(triple_universe=triple_checks,triangles=triples))
            roots=[]
            with (out/(label+'_roots.jsonl')).open('x',encoding='utf8',newline='\n') as stream:
                for r in tqdm(range(99),desc='Complete '+label+' roots',mininterval=1):
                    tick();entry=record(rows,bits,r);roots.append(entry);stream.write(json.dumps(entry,separators=(',',':'))+'\n');stream.flush()
            minimum=min(x['mu_row_residual'] for x in roots);ties=[x['root'] for x in roots if x['mu_row_residual']==minimum]
            global_mu=sum(x['mu_row_residual'] for x in roots)//2;need(sum(x['mu_row_residual'] for x in roots)==2*global_mu,'ENERGY_PARITY')
            graph=dict(label=label,raw_path=path,raw_sha256=PINS[path],n=99,k=14,root_count=99,triples_checked=triple_checks,triangle_count=len(triples),
                       matching_roots=[x['root'] for x in roots if x['neighborhood_is_perfect_matching']],
                       exact_cn2_outside_counts=[x['cn2_eligible_count'] for x in roots],
                       all84_cn2_eligible_roots=[x['root'] for x in roots if x['cn2_eligible_count']==84],
                       row_mu_residual_histogram={str(v):sum(x['mu_row_residual']==v for x in roots) for v in sorted({x['mu_row_residual'] for x in roots})},
                       global_unordered_mu_energy=global_mu,minimum_mu_row_residual=minimum,minimum_root_ties=ties,selected_root=ties[0],
                       selection_rule='Minimize exact row_mu_residual over all99 labelled roots; retain every tie and select smallest root label.',roots=roots)
            save(out/(label+'_census.json'),graph);graphs.append(graph)
        tick();selection=min((x['minimum_mu_row_residual'],x['label'],x['selected_root']) for x in graphs)
        artifacts={f.relative_to(ROOT).as_posix():dict(sha256=sha(f),bytes=f.stat().st_size) for f in out.rglob('*') if f.is_file()}
        inputs={**PINS,REPORT:REPORT_SHA,Path(__file__).resolve().relative_to(ROOT).as_posix():sha(Path(__file__)),SPEC:sha(ROOT/SPEC)}
        for path in ['acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock']:inputs[path]=sha(ROOT/path)
        summary=dict(status='WARM_SCAFFOLD_ROOT_CENSUS_V1_OUTPUT_PENDING_INDEPENDENT_CHECK',timestamp=datetime.now(timezone.utc).isoformat(),
                     source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
                     inputs_sha256=inputs,artifacts=artifacts,population=dict(raw_graphs=2,labelled_roots_per_graph=99,root_records=198,triple_tests_per_graph=156849),
                     calibration=dict(path=(controls/'summary.json').relative_to(ROOT).as_posix(),sha256=sha(controls/'summary.json'),positive_rook_roots=9,negative_controls=len(cal['negative_controls'])),
                     graph_summaries=[{k:v for k,v in x.items() if k!='roots'} for x in graphs],
                     overall_selected=dict(mu_row_residual=selection[0],graph=selection[1],root=selection[2],tie_rule='lexicographic(residual,graph_label,root_label)'),
                     status_semantics='CANDIDATE producer result; independent denseA squared/root checking required before VERIFIED',independent_approval=False,target_resolution=False,solver_launched=False,
                     limitations=['Complete coverage of exactly2 rawgraphs×99 roots, not hypothetical SRG graphs.','CN2 eligibility alone is not complete scaffold equivalence or an assignment certificate.','No SAT encoding, decoded model, target exclusion, automorphism or graph normalization certificate.','Same author as annealer producer; discovery cannot approve itself.','Overall search coverage: UNKNOWN; no validated denominator.'])
        save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],population=summary['population'],overall_selected=summary['overall_selected'])))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),timestamp=datetime.now(timezone.utc).isoformat(),status='PRODUCER_FAILURE_PRESERVED',independent_approval=False));raise

if __name__=='__main__':main()
