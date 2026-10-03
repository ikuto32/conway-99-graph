"""One-time observed resources, not a reservation or future availability claim."""
import ctypes
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
class MemoryStatus(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(k,ctypes.c_ulonglong) for k in ['total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','avail_extended']]

def main():
    state=MemoryStatus();state.length=ctypes.sizeof(state)
    assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state))
    command=['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.free,memory.used','--format=csv,noheader,nounits']
    raw=subprocess.check_output(command,text=True).strip();rows=raw.splitlines();assert len(rows)==1
    name,driver,total,free,used=[x.strip() for x in rows[0].split(',')]
    observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),gpu_query=command,gpu_query_output=raw,
        gpu=name,gpu_driver=driver,gpu_total_mib=int(total),gpu_free_mib=int(free),gpu_used_mib=int(used),
        host_total_bytes=state.total_phys,host_free_bytes=state.avail_phys,disk_free_bytes=shutil.disk_usage(ROOT).free,
        observation_method='NVIDIA management query, Windows GlobalMemoryStatusEx, and disk_usage; no memory allocation or reservation.',
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    p=ROOT/'acceleration/results/20260930_resume/eight_gpu_resource_preflight.json'
    with p.open('x',encoding='utf-8') as f:json.dump(observation,f,indent=2)
    print(json.dumps(observation))

if __name__=='__main__':main()
