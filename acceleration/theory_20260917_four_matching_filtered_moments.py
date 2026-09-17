"""Prepare the exact surviving-column moment model; no solver execution."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import numpy as np
from scipy.sparse import load_npz,save_npz,csr_matrix
from tqdm import tqdm
from theory_20260917_partial_matching_moments import digest,save

ROOT=Path(__file__).resolve().parents[1]
FULL="acceleration/results/20260917_four_matching_moments"
FILTER="acceleration/results/20260917_four_coordinate_matching_filter/run01"
MODEL="PARTIAL_K_FOUR_COORDINATE_MATCHING_FILTERED_FULL_MOMENT_PHASE1_V1"


def select(matrix,indices,probability_count):
    assert indices==sorted(set(indices)) and all(0<=i<probability_count for i in indices)
    columns=indices+list(range(probability_count,matrix.shape[1]))
    return matrix[:,columns].tocsr(),columns


def controls():
    toy=csr_matrix(np.array([[1,2,3,-1,1],[4,5,6,0,0]],dtype=np.int64))
    selected,columns=select(toy,[0,2],3)
    assert np.array_equal(selected.toarray(),np.array([[1,3,-1,1],[4,6,0,0]],dtype=np.int64))
    bad=selected.copy();bad.data[0]+=1
    assert (bad!=toy[:,columns]).nnz>0
    rejected=[]
    for ids in ([0,0],[1,0],[-1],[3]):
        try:select(toy,ids,3)
        except AssertionError:rejected.append(ids)
        else:raise AssertionError("Invalid selection accepted")
    return dict(positive_selection="PASS",unchanged_slacks="PASS",corrupt_coefficient="REJECTED",invalid_index_controls=rejected)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();out=args.out;out.mkdir(parents=True,exist_ok=True);assert not any(out.iterdir())
    bindings={}
    def read(name):
        bindings[name]=digest(ROOT/name)
        return json.loads((ROOT/name).read_bytes())
    full=read(FULL+"/model.json");full_manifest=read(FULL+"/build_manifest.json")
    filtering=read(FILTER+"/summary.json");read(FILTER+"/manifest.json")
    assert filtering["original_choices"]==290460 and filtering["surviving_choices"]==230879 and filtering["rejected_choices"]==59581 and filtering["empty_domains"]==0
    original_offsets=full["probability_offsets"];oldn=original_offsets[-1]
    ids_by_center=[];global_ids=[]
    rows={r["outer_vertex"]:r for r in filtering["vertices"]}
    for u in tqdm(range(84),desc="Read exact filter IDs",unit="center"):
        name=f"{FILTER}/vertex_{u:02d}.json";record=read(name)
        assert bindings[name]==rows[u]["sha256"] and record["complete"] and record["outer_vertex"]==u
        count=original_offsets[u+1]-original_offsets[u]
        assert record["original_count"]==count
        kept=record["surviving_ids"];rejected=record["rejected_ids"]
        assert kept==sorted(set(kept)) and set(kept).isdisjoint(rejected) and sorted(kept+rejected)==list(range(count))
        assert kept
        ids_by_center.append(kept);global_ids.extend(original_offsets[u]+j for j in kept)
    assert len(global_ids)==230879
    for name in (FULL+"/integer_augmented_csr.npz",Path(__file__).relative_to(ROOT).as_posix(),"acceleration/theory_20260917_partial_matching_moments.py","uv.lock"):
        bindings[name]=digest(ROOT/name)
    assert bindings[FULL+"/integer_augmented_csr.npz"]==full["matrix_sha256"]
    save(out/"build_manifest.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
        python=platform.python_version(),inputs_sha256=bindings,model=MODEL,scope=full_manifest["scope"],
        selection="Exactly the230879 saved surviving original-domain IDs from complete matching-filter run01;59581 probability columns removed; every5490row and6972slack columns retained unchanged",
        distinct_model="Matching-filtered domain, different feasible relaxation from unfilteredfullmoment model; no objective score comparison",
        solver_preregistration=dict(time_limit_seconds=2400,solver="ipm",threads=1,crossover="off",presolve="HiGHS defaults; adaptive sublimits disclosed"),
        budget_rationale="230879probability columns versus89308in previous605.953s run;2400s is one bounded exploration cap, not a predicted runtime or speed claim",
        solve_gates="Independent matching-filter PASS, independent new filtered-model PASS, and parent RAM/disk resource approval before launch; prepareonly tool has no solver entry point",
        acceptance="Any positive exact support-function bound over all filteredchoices is candidate conditional exclusion only with independently sound removed-choice exclusions and raw-neighborhood bound audit",
        preservation="Never mutate source model/filter/domain files; save exactoriginal-ID map and8MiBcompanion chunks for large artifacts",target_resolution=False))
    start=time.monotonic();save(out/"controls.json",controls())
    A=load_npz(ROOT/FULL/"integer_augmented_csr.npz")
    selected,columns=select(A,global_ids,oldn)
    assert selected.shape==(5490,230879+6972)
    assert (selected[:,-6972:]!=A[:,oldn:]).nnz==0
    save_npz(out/"integer_augmented_csr.npz",selected,compressed=True)
    offsets=np.cumsum([0]+[len(ids) for ids in ids_by_center]).tolist()
    model={k:v for k,v in full.items() if k not in ("model","shape","nonzeros","matrix_sha256","probability_offsets","column_order","costs")}
    model.update(model=MODEL,shape=list(selected.shape),nonzeros=selected.nnz,matrix_sha256=digest(out/"integer_augmented_csr.npz"),
        probability_offsets=offsets,costs=[full["costs"][i] for i in columns],column_order="230879surviving probabilities by center/originalID,all3486negative and3486positive slacks unchanged",
        source_model=FULL+"/model.json",source_model_sha256=bindings[FULL+"/model.json"],
        original_probability_offsets=original_offsets,retained_original_domain_ids=ids_by_center,selected_original_global_columns=columns,
        source_rows_unchanged=True,source_rhs_bounds_unchanged=True,source_slack_columns_unchanged=True)
    save(out/"model.json",model)
    chunks=[]
    for artifact in (out/"integer_augmented_csr.npz",out/"model.json"):
        if artifact.stat().st_size<=10*1024*1024:continue
        parts=[]
        with artifact.open("rb") as source:
            index=0
            while data:=source.read(8*1024*1024):
                name=artifact.name+f".part{index:03d}"
                with (out/name).open("xb") as dest:dest.write(data)
                parts.append(dict(path=name,bytes=len(data),sha256=digest(out/name)));index+=1
        chunks.append(dict(source=artifact.name,source_bytes=artifact.stat().st_size,source_sha256=digest(artifact),source_availability="LOCAL_ONLY",parts=parts,
            recovery="Verify eachpart, concatenate listedorder into freshfile, verify fullbytes/hash"))
    save(out/"chunk_manifest.json",dict(schema_version=1,chunk_bytes=8*1024*1024,artifacts=chunks,publication="Rawlargefiles localonly; hashboundparts are publicationcandidates; no publicationperformed"))
    assert all(digest(ROOT/name)==h for name,h in bindings.items())
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_FILTERED_FOUR_COORDINATE_MOMENT_BUILD",model=MODEL,
        original_probability_choices=oldn,removed_probability_choices=59581,retained_probability_choices=len(global_ids),
        shape=list(selected.shape),nonzeros=selected.nnz,rows_unchanged=True,slacks_unchanged=True,
        elapsed_seconds=time.monotonic()-start,output_sha256={f.name:digest(f) for f in out.iterdir() if f.is_file()},
        solver_launched=False,independent_filter_gate_pending=True,independent_model_gate_pending=True,resource_gate_pending=True,target_resolution=False)
    save(out/"build_summary.json",result)
    print(json.dumps({k:result[k] for k in ("status","shape","nonzeros","elapsed_seconds","solver_launched")}))


if __name__=="__main__":main()
