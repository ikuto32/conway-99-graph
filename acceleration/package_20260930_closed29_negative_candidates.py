"""Package two saved exact negative29vertex artifacts; does not approve them."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20260930_closed29_extension_screen/run01'
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def main():
    summary_path=RUN/'summary.json'
    assert digest(summary_path)=='db3ed028a6b36bdde8ef94f8d378cfa561524d535653ea0459e45cccd9c31bae'
    records=[];bindings={key(summary_path):digest(summary_path)}
    for filename,assignment_index in [('case_11_w_71.json',0),('case_11_w_81.json',6)]:
        path=RUN/'pairs'/filename;record=json.loads(path.read_bytes());assignment=record['assignments'][assignment_index]
        assert assignment['pair_cap_failure'] is None
        rows=[int(row,16) for row in assignment['adjacency_rows_hex']]
        A=[[int(row>>j&1) for j in range(29)] for row in rows]
        negatives=[row for row in assignment['gram_screens'] if row['exact_negative'] is not None]
        assert len(negatives)==1
        negative=negatives[0];assert negative['matrix']=='27I-9A+J'
        z=negative['exact_negative']['vector'];q=negative['exact_negative']['quadratic']
        assert q==sum(z[i]*(27*int(i==j)-9*A[i][j]+1)*z[j] for i in range(29) for j in range(29))<0
        records.append(dict(case_index=record['case_index'],center=record['center'],original_id=record['original_id'],outer_extra_vertex=record['outer_extra_vertex'],
                            full99_vertex_map=record['full99_vertex_map'],adjacency_full29=A,integer_negative_vector=z,quadratic=q,
                            matrix=negative['matrix'],source_pair=key(path),source_pair_sha256=digest(path),assignment_index=assignment_index,
                            chosen_outer_edges_to_w=assignment['chosen_outer_edges_to_w'],
                            remaining_surviving_assignments_for_same_pair=record['surviving_guidance_assignments'],
                            scope='Only this specific induced29vertex adjacency cannot extend to a target if the exact negative certificate is independently validated; the saved closed28 graph and star are not excluded.'))
        bindings[key(path)]=digest(path)
    for p in (Path(__file__),ROOT/'uv.lock'):bindings[key(p)]=digest(p)
    report=dict(status='CANDIDATE_EXACT_NEGATIVE29_ARTIFACTS_PENDING_INDEPENDENT_REVIEW',timestamp=datetime.now(timezone.utc).isoformat(),
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
                inputs_sha256=bindings,records=records,packaged_raw29_candidates=2,producer_literal_recalculation_only=True,
                independent_verification=None,independent_verification_null_reason='A discovery agent cannot approve its own candidate',
                whole_closed28_graphs_excluded=0,whole_stars_excluded=0,target_resolution=False)
    path=RUN/'negative_candidates.json'
    with path.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(sha256=digest(path),records=[{k:r[k] for k in ('case_index','outer_extra_vertex','quadratic','remaining_surviving_assignments_for_same_pair')} for r in records])))


if __name__=='__main__':main()
