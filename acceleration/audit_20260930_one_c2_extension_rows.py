"""Independent raw25-to-partial99 reconstruction and all11 complete trees."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_one_c2_row_object as object_check
import audit_20260930_triangle_row29_obstruction as tree

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_one_c2_extension_rows'
SUMMARY_SHA='5881b87e985f4f6ca6d8034230938fff315c3f1a9084b4e232715ebdca139242'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_row_sat_object/summary.json'
GATE_SHA='e4693a9bb52831e26ecdeb350565123df4cac58917a66db4762ea31e161809b1'
HELPER_SHA='109671d882976ab68b350883340f3f0d7437571caa56b01d56a875f7897c4730'
need,digest,key,read,save=object_check.need,object_check.digest,object_check.key,object_check.read,object_check.save

def raw_graph(c):
    g,columns,known,entries,refs,components=object_check.raw.derive_scope()
    checked=object_check.raw.validate(c,g,known,components,columns)
    core=object_check.raw.prior.base.derive()[0]
    a=[[0]*99 for _ in range(99)]
    for i in range(39):
        for j in range(39):a[i][j]=core[i][j]
    for r in range(36):
        for d in range(60):a[3+r][39+d]=a[39+d][3+r]=c[r][d] if r<25 else -1
    for i,j in combinations(range(39,99),2):a[i][j]=a[j][i]=-1
    need(all(a[i][i]==0 for i in range(99)) and all(a[i][j]==a[j][i] for i,j in combinations(range(99),2)),'raw99 diagonal/symmetry')
    need(sum(a[i][j]==-1 for i,j in combinations(range(99),2))==2430,'exact660+1770unknowns')
    need(all(sum(x==1 for x in row)<=14<=sum(x!=0 for x in row) for row in a),'all99degree intervals')
    n=[{j for j,x in enumerate(row) if x==1} for row in a]
    need(all(len(n[i]&n[j])<=2-int(a[i][j]==1) for i,j in combinations(range(99),2)),'all4851knownpair caps')
    return a,checked

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(path,expected=None):
        path=Path(path);v=digest(path);need(expected is None or v==expected,'hash '+str(path));bindings[key(path)]=v;return path
    def load(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    try:
        bind(tree.__file__,HELPER_SHA);gate=load(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_TRIANGLE_ONE_C2_ROW_SAT_OBJECT_PASS','exact independent25row object gate')
        for p,v in gate['inputs_sha256'].items():bind(ROOT/p,v)
        summary=load(D/'summary.json',SUMMARY_SHA)
        for p,v in summary['output_hashes'].items():bind(ROOT/p,v)
        manifest=load(D/'manifest.json')
        for p,v in manifest['inputs_sha256'].items():bind(ROOT/p,v)
        factor_path=ROOT/'acceleration/results/20260930_triangle_one_c2_row_native_pilot/main/decoded_factor.json'
        need(gate['inputs_sha256'][key(factor_path)]==digest(factor_path),'exact producerdecoded object covered by independent gate')
        factor=load(factor_path);a,checked=raw_graph(factor['incidence_matrix']);raw=load(D/'raw99.json')
        need(raw['known_adjacency']==a and raw['Q1']==checked['Q1'] and raw['fixed_C2_row']==factor['incidence_matrix'][24] and raw['fixed_C2_coordinate']==0,'every fixed/free raw99entry and fixed25object')
        need(raw['unknown_C2_entries']==660 and raw['unknown_BB_entries']==1770 and raw['propagated_assignments_used']==0,'no historical propagation premise')
        calibration,_=tree.calibration();save(args.out/'positive_controls.json',calibration)
        rows=[];corrupt=[];rawconstraints=[]
        paths=sorted(D.glob('row_*.json'));need(len(paths)==11,'exact11rowartifact population')
        for vertex,path in zip(range(28,39),paths):
            record=load(path);need(record['vertex']==vertex,'row population/order')
            vv,cs=tree.reconstruct(a,vertex,list(range(3,28)))
            need(vv==list(range(39,99)) and record['variables']==vv and record['constraints']==cs,'all independently reconstructed necessary rowconstraints')
            proof=record['proof'];need(proof['status']=='UNSAT','exact claimed row outcome')
            detail=tree.check_tree(60,cs,proof,record=True);need(detail['sat_leaves']==0,'complete row tree contradictory')
            save(args.out/f'row_{vertex:02d}_complete_tree_check.json',detail)
            detail={k:v for k,v in detail.items() if k!='receipts'}
            mutants={}
            split=next((i for i,n in enumerate(proof['nodes']) if n['status']=='SPLIT'),None)
            if split is not None:
                bad=deepcopy(proof);bad['nodes'][split]['children'].pop();mutants['missing_branch']=bad
            force=next((i for i,n in enumerate(proof['nodes']) if n['forces']),None)
            if force is not None:
                bad=deepcopy(proof);bad['nodes'][force]['forces'][0]['value']^=1;mutants['wrong_force']=bad
            leaf=next(i for i,n in enumerate(proof['nodes']) if n['status']=='CONFLICT')
            bad=deepcopy(proof);bad['nodes'][leaf]['ones']+=1;mutants['false_leaf_counter']=bad
            for name,bad in mutants.items():
                try:tree.check_tree(60,cs,bad)
                except ValueError:corrupt.append(f'row{vertex}_{name}')
                else:raise ValueError('corrupt tree accepted '+name)
            rows.append(dict(vertex=vertex,status='UNSAT',artifact_sha256=digest(path),constraint_counts=dict(Counter(c['kind'] for c in cs)),tree=detail))
            rawconstraints.append(dict(vertex=vertex,variables=vv,constraints=cs))
        need(sum(r['tree']['nodes'] for r in rows)==1037,'actual complete-node population')
        need(summary['attempted_rows']==summary['unsat_rows']==11 and summary['sat_rows']==summary['unknown_rows']==0,'outcome counts')
        for row,outcome in zip(rows,summary['outcomes']):need(row['vertex']==outcome['vertex'] and row['status']==outcome['status'] and row['artifact_sha256']==outcome['sha256'] and row['tree']['nodes']==outcome['nodes'],'producer exact outcome binding')
        bad=deepcopy(factor['incidence_matrix']);bad[24][0]^=1
        try:raw_graph(bad)
        except ValueError:corrupt.append('changed_fixed_C2_bit')
        else:raise ValueError('fixed25corruption accepted')
        save(args.out/'independent_raw99_constraints.json',dict(known_adjacency=a,rows=rawconstraints))
        save(args.out/'corrupted_controls.json',dict(rejected=corrupt))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_ONE_C2_EXTENSION_ROWS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:bind(p)
        need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable artifacts');need(time.monotonic()-start<120,'audit wall cap')
        report=dict(status='INDEPENDENT_FIXED_25_ROW_ELEVEN_EXTENSION_EXCLUSIONS_PASS',claim_id='C-FIXED-25-ROW-TRIANGLE-EXTENSION-EXCLUSION',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit raw25/raw99 reconstruction and independent complete tree replay',kind='exclusion',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
          statement='For the exact independently checked25-row incidence object, none of the eleven remainingC2 rows28..38 admits even the independently reconstructed necessary60-bit row constraints. The11complete contradiction trees contain1037total nodes. Therefore no target graph completes that exact fixed25-row object.',dependencies=[dict(id='C-FIXED-TRIANGLE-ONE-C2-ROW-PROJECTION-CONSTRUCTION',revision=1,relation='uses_result')],scope='One fixedQ1 AND selectedC2coordinate0 incidence row, with all660otherC2 incidences and1770outsideedges unspecified. Not a Q1-only exclusion.',row_population=list(range(28,39)),attempted_rows=11,verified_UNSAT_rows=11,verified_SAT_rows=0,UNKNOWN_rows=0,complete_tree_nodes=1037,rows=rows,raw99_entries_checked=9801,known_pair_caps_checked=4851,integer_Gram_entries_checked=625,controls=calibration,fresh_corruptions_rejected=corrupt,
          shared_components=['Frozen independently authored integer necessary-constraint and complete binary-tree checker reused with source hash109671d8.','Own raw99 reconstruction from independently checked25row input; no producer/search imports.'],limitations=['No sameQ1/differentselectedrow or allQ1 exclusion.','No unrestricted fixedcore containment or target automorphism.','Trees prove only their exact necessary constraint systems.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e)));raise

if __name__=='__main__':main()
