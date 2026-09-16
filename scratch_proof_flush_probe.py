"""Probe C stdio flushing for PySAT proof streams (diagnostic only)."""

import ctypes
import json

import pysat.solvers as solver_module
from pysat.solvers import Solver


def snapshot(handle):
    handle.seek(0)
    data = handle.read()
    return {"bytes": len(data), "tail": data[-32:].decode("ascii", errors="replace")}


solver = Solver(
    name="glucose4",
    bootstrap_with=[[1, 2], [1, -2], [-1, 2], [-1, -2]],
    with_proof=True,
)
answer = solver.solve()
engine = solver.solver
result = {"answer": answer, "after_solve": snapshot(engine.prfile)}
result["ucrt_fflush"] = ctypes.CDLL("ucrtbase.dll").fflush(None)
result["after_ucrt_fflush"] = snapshot(engine.prfile)
solver_module.pysolvers.glucose41_del(engine.glucose)
engine.glucose = None
result["after_delete"] = snapshot(engine.prfile)
result["ucrt_fflush_after_delete"] = ctypes.CDLL("ucrtbase.dll").fflush(None)
result["after_final_fflush"] = snapshot(engine.prfile)
print(json.dumps(result))
