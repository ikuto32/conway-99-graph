"""Build only: direct integer model for six-coordinate matching survivors."""
import argparse
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import math
import numpy as np
from scipy.sparse import csc_matrix,save_npz
from tqdm import tqdm
from theory_20260917_partial_matching_moments import digest,save,controls as rook_fixtures

ROOT=Path(__file__).resolve().parents[1]
DOMAIN="acceleration/results/20260917_partial_six_matchings"
FILTER="acceleration/results/20260917_six_coordinate_matching_filter/run01"
MODEL="PARTIAL_K_SIX_COORDINATE_MATCHING_FILTERED_FULL_MOMENT_PHASE1_V1"


class BuildCap(Exception):pass


def assemble(supports,fixed,unknown,tables,deadline,out=None):
    size=len(tables);pairs=list(combinations(range(size),2));p=len(pairs);m=len(unknown)
    pindex={e:i for i,e in enumerate(pairs)};eindex={e:i for i,e in enumerate(unknown)}
    neighbors=[set() for _ in tables]
    for a,b in fixed:neighbors[a].add(b);neighbors[b].add(a)
    offsets=np.cumsum([0]+[len(t) for t in tables]).tolist();n=offsets[-1];hard=size+m
    counts=[1+mask.bit_count()+math.comb(mask.bit_count()+len(neighbors[u]),2)+(mask>>(u+1)).bit_count() for u,t in enumerate(tables) for mask in t]+[1]*(2*p)
    starts=np.r_[np.int64(0),np.cumsum(counts,dtype=np.int64)];nnz=int(starts[-1])
    projection=dict(rows=hard+p,columns=n+2*p,nonzeros=nnz,
        allocated_CSC_bytes=nnz*5+(n+2*p+1)*8,
        projected_CSC_plus_CSR_array_bytes=nnz*10+(n+2*p+1)*8+(hard+p+1)*8,
        meaning="Array-size projection forint8data/int32indices; not measured peak. Python tables/sorting and SciPy conversion overhead additional; no solver memory estimate.")
    if out:save(out/"resource_projection.json",projection)
    assert nnz<2**31 and hard+p<2**31
    indices=np.empty(nnz,dtype=np.int32);values=np.empty(nnz,dtype=np.int8)
    for u,table in enumerate(tqdm(tables,desc="Direct six-coordinate sparse columns",unit="center",disable=out is None)):
        for j,mask in enumerate(table,offsets[u]):
            if j%512==0 and time.monotonic()>=deadline:raise BuildCap("400_SECOND_BUILD_CAP")
            selected=[v for v in range(size) if mask>>v&1]
            assert u not in selected and not neighbors[u]&set(selected)
            full=sorted(neighbors[u]|set(selected))
            entries=[(u,1)]
            for v in selected:
                e=(min(u,v),max(u,v));entries.append((size+eindex[e],1 if u<v else -1))
                if u<v:entries.append((hard+pindex[e],1))
            entries.extend((hard+pindex[e],1) for e in combinations(full,2))
            entries.sort();assert len({r for r,_ in entries})==len(entries)==counts[j]
            a,b=int(starts[j]),int(starts[j+1])
            indices[a:b]=[r for r,_ in entries];values[a:b]=[v for _,v in entries]
        if out:save(out/f"checkpoint_{u:02d}.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),completed_centers=u+1,completed_probability_columns=offsets[u+1],matrix_complete=False,
            limitation="Progress observation only; partialinmemory arrays are not a complete certificate or resumable serialized model"))
    for k in range(2*p):
        indices[int(starts[n+k])]=hard+k%p;values[int(starts[n+k])]=-1 if k<p else 1
    if time.monotonic()>=deadline:raise BuildCap("400_SECOND_BUILD_CAP_BEFORE_CSR")
    matrix=csc_matrix((values,indices,starts),shape=(hard+p,n+2*p)).tocsr()
    rhs=[1]*size+[0]*m+[2-len(supports[a]&supports[b])-int((a,b) in fixed) for a,b in pairs]
    assert matrix.nnz==nnz and set(np.unique(matrix.data))<={-1,1}
    return matrix,rhs,offsets,pairs,projection


def calibrate(deadline):
    fixtures=rook_fixtures();checks=[]
    for fixture in fixtures["records"]:
        tables=[[mask] for mask in fixture["masks"]]
        A,b,_,_,_=assemble(list(map(set,fixture["supports"])),set(map(tuple,fixture["fixed_edges"])),list(map(tuple,fixture["unknown_edges"])),tables,deadline)
        witness=np.r_[np.ones(4,dtype=np.int64),np.zeros(A.shape[1]-4,dtype=np.int64)]
        assert np.array_equal(A@witness,b)
        corrupted=A.copy();nz=int(corrupted.indptr[0]);corrupted.data[nz]+=1
        assert not np.array_equal(corrupted@witness,b)
        wrong=list(b);wrong[-1]+=1;assert not np.array_equal(A@witness,wrong)
        checks.append(dict(root=fixture["root"],fixed_edges=fixture["fixed_edges"],positive="PASS",corrupt_coefficient="REJECTED",corrupt_RHS="REJECTED"))
    return dict(calibration="New directCSC builder on18rook9 exactwitnesses and36corruptions",checks=checks)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();out=args.out;out.mkdir(parents=True,exist_ok=True);assert not any(out.iterdir())
    bindings={}
    def read(name):
        bindings[name]=digest(ROOT/name);return json.loads((ROOT/name).read_bytes())
    domain=read(DOMAIN+"/manifest.json");summary=read(DOMAIN+"/summary.json");filtering=read(FILTER+"/summary.json");read(FILTER+"/manifest.json")
    assert summary["complete_all_centers"] and summary["complete_domain_choices"]==879449
    assert filtering["surviving_choices"]==712721 and filtering["rejected_choices"]==166728 and filtering["empty_domains"]==0
    tables=[];ids_by_center=[];original_counts=[];filter_rows={r["outer_vertex"]:r for r in filtering["vertices"]}
    for u in tqdm(range(84),desc="Bind six-coordinate domains/filter",unit="center"):
        name=f"domain_{u:02d}.json";record=read(DOMAIN+"/"+name)
        assert bindings[DOMAIN+"/"+name]==summary["output_sha256"][name]
        fname=f"{FILTER}/vertex_{u:02d}.json";filt=read(fname)
        assert bindings[fname]==filter_rows[u]["sha256"] and filt["complete"]
        full=[int(s,16) for s in record["domain_masks_hex"]];ids=filt["surviving_ids"]
        assert ids and ids==sorted(set(ids)) and sorted(ids+filt["rejected_ids"])==list(range(len(full)))
        tables.append([full[i] for i in ids]);ids_by_center.append(ids);original_counts.append(len(full))
    assert sum(map(len,tables))==712721 and sum(original_counts)==879449
    for name in (Path(__file__).relative_to(ROOT).as_posix(),"acceleration/theory_20260917_partial_matching_moments.py","uv.lock"):
        bindings[name]=digest(ROOT/name)
    save(out/"build_manifest.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        model=MODEL,scope=domain["scope"],selection="All712721 recorded matching-filter survivors from879449 complete localdomains; no additional pruning",
        construction="Direct perstar integerCSC columns thenCSR, no unfilteredmatrix; original-ID maps preserved",
        build_seconds_cap=400,cap_policy="Check every512columns and phase boundaries; preserve checkpoint/failure records; no LP or automatic retry",
        integer_storage="int8 coefficients exactly +/-1 and32bitindices; no floating arithmetic in model construction",
        resource_projection="Exact nonzero and typedarray bytecount saved before large allocations; Python/conversion overhead not a measured peak",
        controls="New builder calibrates18knownvalidrook9 witnesses plus36coefficient/RHS corruptions",
        solver_configuration=None,solver_configuration_null_reason="NoLPauthorized; independentfilter/model gates and fresh resource decision required",
        interpretation="Necessary conditional model only; positive exact bound requires fresh independent raw-neighborhood audit including all removed choices",target_resolution=False))
    start=time.monotonic();deadline=start+400
    try:
        save(out/"controls.json",calibrate(deadline))
        supports=[{2*a+s,2*b+t} for a,b in combinations(range(7),2) for s in (0,1) for t in (0,1)]
        fixed=set(map(tuple,domain["remaining_fixed_K_edges_outer"]));unknown=list(map(tuple,domain["unknown_edges_outer"]))
        assert len(fixed)==132 and len(unknown)==2040
        A,rhs,offsets,pairs,projection=assemble(supports,fixed,unknown,tables,deadline,out)
        if time.monotonic()>=deadline:raise BuildCap("400_SECOND_BUILD_CAP_BEFORE_SAVE")
        save_npz(out/"integer_augmented_csr.npz",A,compressed=True)
        model=dict(model=MODEL,shape=list(A.shape),nonzeros=A.nnz,matrix_sha256=digest(out/"integer_augmented_csr.npz"),
            coefficient_dtype=str(A.data.dtype),probability_offsets=offsets,retained_original_domain_ids=ids_by_center,
            original_probability_offsets=np.cumsum([0]+original_counts).tolist(),fixed_edges=sorted(fixed),unknown_edges=unknown,pair_order=pairs,supports=[sorted(s) for s in supports],
            rhs=rhs,costs=[0]*offsets[-1]+[1]*(2*len(pairs)),column_lower=0,column_upper=None,column_upper_null_reason="Positive infinity",all_rows_equalities=True,
            row_order="84simplex,2040reciprocity,3486moments",column_order="712721filteredoriginalstar choices bycenter/originalID,3486negative/3486positive slacks")
        save(out/"model.json",model)
        parts_records=[]
        for artifact in (out/"integer_augmented_csr.npz",out/"model.json"):
            if artifact.stat().st_size<=10*1024*1024:continue
            parts=[]
            with artifact.open("rb") as src:
                i=0
                while data:=src.read(8*1024*1024):
                    if time.monotonic()>=deadline:raise BuildCap("400_SECOND_BUILD_CAP_DURING_CHUNKS")
                    name=artifact.name+f".part{i:03d}"
                    with (out/name).open("xb") as dst:dst.write(data)
                    parts.append(dict(path=name,bytes=len(data),sha256=digest(out/name)));i+=1
            parts_records.append(dict(source=artifact.name,source_bytes=artifact.stat().st_size,source_sha256=digest(artifact),source_availability="LOCAL_ONLY",parts=parts))
        save(out/"chunk_manifest.json",dict(schema_version=1,chunk_bytes=8*1024*1024,artifacts=parts_records,recovery="Verify eachpart, concatenate listedorder into freshfile, verify sourcebytes/hash"))
        assert all(digest(ROOT/name)==h for name,h in bindings.items())
        result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_SIX_COORDINATE_FILTERED_MOMENT_BUILD",model=MODEL,
            shape=list(A.shape),nonzeros=A.nnz,original_choices=879449,retained_choices=712721,removed_choices=166728,elapsed_seconds=time.monotonic()-start,
            output_sha256={f.name:digest(f) for f in out.iterdir() if f.is_file()},solver_launched=False,independent_model_review_pending=True,target_resolution=False)
        save(out/"build_summary.json",result);print(json.dumps({k:result[k] for k in ("status","shape","nonzeros","elapsed_seconds","solver_launched")}))
    except BuildCap as error:
        save(out/"build_failure.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),status="INCOMPLETE_BUILD_CAP",reason=str(error),elapsed_seconds=time.monotonic()-start,solver_launched=False,target_resolution=False))
        raise


if __name__=="__main__":main()
