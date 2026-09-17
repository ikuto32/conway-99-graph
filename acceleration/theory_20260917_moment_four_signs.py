"""Preregistered four-sign diagnostic of arbitrary frozen moment weights."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from scipy.sparse import load_npz
from theory_20260917_partial_matching_moments import digest,save,exact_bound

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"acceleration/results/20260917_partial_matching_moments"
OUT=ROOT/"acceleration/results/20260917_partial_matching_moment_four_signs"


def main():
    OUT.mkdir(exist_ok=True)
    assert not any(OUT.iterdir())
    inputs={str(p.relative_to(ROOT)).replace("\\","/"):digest(p) for p in (SRC/"model.json",SRC/"numeric_lp.json",SRC/"integer_augmented_csr.npz",Path(__file__),ROOT/"acceleration/theory_20260917_partial_matching_moments.py",ROOT/"uv.lock")}
    save(OUT/"manifest.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),inputs_sha256=inputs,
        selection="All four independent signs of reciprocity q and moment y from preserved60-second raw weights",
        cases=[[1,1],[-1,1],[1,-1],[-1,-1]],criterion="Strictly positive exact bound only; save every case; no solver feasibility assumption"))
    model=json.loads((SRC/"model.json").read_bytes());raw=json.loads((SRC/"numeric_lp.json").read_bytes())
    A=load_npz(SRC/"integer_augmented_csr.npz");n=model["probability_offsets"][-1]
    weights=np.array(raw["row_dual"],dtype=float)
    records=[]
    for qs,ys in ((1,1),(-1,1),(1,-1),(-1,-1)):
        w=weights.copy();w[84:1824]*=qs;w[1824:]*=ys
        bound=exact_bound(A[84:1824,:n],A[1824:,:n],np.array(model["rhs"][1824:],dtype=np.int64),model["probability_offsets"],w)
        name=f"q_{qs}_y_{ys}.json"
        save(OUT/name,bound)
        records.append(dict(q_sign=qs,y_sign=ys,path=name,sha256=digest(OUT/name),numerator=bound["numerator"],denominator=bound["denominator"],approximate=bound["approximate"],strictly_positive=bound["strictly_positive"]))
    save(OUT/"summary.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),records=records,any_strictly_positive=any(r["strictly_positive"] for r in records),independent_verification=False,target_resolution=False))
    print(json.dumps(records))


if __name__=="__main__":
    main()
