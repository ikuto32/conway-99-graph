"""Freeze committed normalizedGF2 scientific invocation after exact fresh gate.

Read-only preflight/source/hash checks plus a new immutable plan. Never launches
the native solver, edits the index, promotes a result or extends any deadline.
"""
import argparse,hashlib,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
CODE=['acceleration/prepare_20261002_rooted8_normalized_gf2_v2.py','acceleration/rooted8_normalized_gf2_20261002_v2.cpp',
      'acceleration/prepare_20261002_rooted8_normalized_gf2_v2_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py',
      'acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock']
BINARY='acceleration/results/20261002_rooted8_normalized_gf2_build02/normalized_gf2'
BINARY_SHA='8b8baf94b976c815802d90a98d570a2f401a72920ac60c39fd52490b5ef7324e'
BUILD='acceleration/results/20261002_rooted8_normalized_gf2_build02/build_manifest.json'
BUILD_SHA='6bba815232cb4d0962a8b8331cef74ea0a5aefb6abda5e4eff312caceea3fd6c'
GATE='acceleration/results/20261002_independent_review/normalized_gf2_controls01/summary.json'
GATE_SHA='5f9fb0852f86491c628e0ba9ab6bc564f78bc06bfce0a7a0ea4b668241e589a1'
RAW='acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
RAW_SHA='a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'
NORM='acceleration/results/20261002_independent_review/rooted8_row_content01/normalization_manifest.json'
NORM_SHA='47c9f0158084a1cf04b9ce2f84db93ee748e5e3226d759f276090aa50bdfe91c'
ENC='acceleration/results/20261002_independent_review/rooted8_model01/summary.json'
ENC_SHA='e3158fe17f4a83e5231c90f72c912e5ef37cd6ddc3ce6300f0c6861f9d0ffc4e'


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--source-commit',required=True);args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Fresh committed-source/input hash and Linux worker/memory/disk preflight; freeze exact900s invocation, no native solver launch')
    need(sys.platform.startswith('linux'),'fresh preflight inside Linux');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();need(head==args.source_commit,'explicit fresh source HEAD')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'repository plan output');out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,wanted=None,committed=True):
        need(deadline.status()['remaining_seconds']>20 and not deadline.status()['stop_required'],'not completed within allocated budget')
        p=(ROOT/name).resolve();need(p.is_relative_to(ROOT)and p.is_file(),'raw artifact exists');data=p.read_bytes();digest=hashlib.sha256(data).hexdigest();need(wanted is None or digest==wanted,'exact source/artifact hash '+name)
        if committed:need(hashlib.sha256(subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)).hexdigest()==digest,'committed bytes equal working source/artifact '+name)
        pins[name]=digest;return json.loads(data)if p.suffix=='.json'else None
    gate=pin(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_NORMALIZED_GF2_PRIMAL_XOR_CONTROLS_V1_PASS','exact new independent controls gate')
    for name in CODE+[BINARY,BUILD]:pin(name,gate['inputs_sha256'][name])
    need(pins[BINARY]==BINARY_SHA and pins[BUILD]==BUILD_SHA,'fixed native binary/build')
    pin(RAW,RAW_SHA);pin(NORM,NORM_SHA);pin(ENC,ENC_SHA);pin('acceleration/plan_20261002_rooted8_normalized_gf2_v2.json')
    selfkey=Path(__file__).resolve().relative_to(ROOT).as_posix();pin(selfkey)
    workers=[];uncertain=[]
    for proc in Path('/proc').iterdir():
        if not proc.name.isdecimal():continue
        try:
            exe=(proc/'exe').resolve(strict=True)
            if exe.name in ['normalized_gf2','hypergraph_weighted_anneal','hypergraph_anneal','cadical','drat-trim']:
                workers.append(dict(pid=int(proc.name),exe=str(exe),cmdline=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode('ascii',errors='replace')))
        except FileNotFoundError:pass
        except PermissionError:uncertain.append(int(proc.name))
    need(not workers and not uncertain,'fresh scientific native worker population must be empty/observable')
    mem={k:int(v.split()[0])*1024 for k,v in (line.split(':',1)for line in Path('/proc/meminfo').read_text().splitlines())if k in ['MemTotal','MemAvailable']}
    disks={label:shutil.disk_usage(path)._asdict()for label,path in [('host',ROOT),('ext4',Path('/'))]}
    need(mem['MemAvailable']>8*1024**3 and disks['host']['free']>32*1024**3 and disks['ext4']['free']>8*1024**3,'declared fresh memory/disk reserves')
    supervisor='acceleration/results/20261002_rooted8_normalized_gf2_solve_supervision01';result='acceleration/results/20261002_rooted8_normalized_gf2_solve01'
    need(not(ROOT/supervisor).exists()and not(ROOT/result).exists(),'fresh exact scientific output roots')
    command=['/usr/bin/python3','acceleration/run_compute_command.py','--seconds','900','--shutdown-reserve-seconds','10','--allocation-reason',
        'One frozen full normalized23019variable85874row GF2 primal/XOR calculation; prior rawPython255s, no packed runtime guarantee;850worker750native includes preprocessing/checkpoint/hash reserves.',
        '--success-criterion','Complete3binary23019bit primal candidates or complete original-row XOR candidate; exact row-content stream agrees; prefix checkpoints preserved on stop; no rank claim.',
        '--verification-criterion','Different-author full raw integer-content and scalar vector/XOR verification before any literal parity conclusion; UNKNOWN prism-free premise prevents target-level exclusion.',
        '--out',supervisor,'--','/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv','/root/.local/bin/uv','run','--locked','--offline','--project','acceleration/native_budget_env_v1',
        '--cache-dir','build/native-budget-linux-cache','--python','/usr/bin/python3','python',CODE[0],'solve','--seconds','850','--allocation-reason',
        'Independently gated normalized fulloperator exact content/row hashes,3RHS uint64/DAG elimination with750s native guard and completed-prefix checkpoints;20sworker reserve, no retry.',
        '--source-commit',head,'--supervision-out',supervisor,'--out',result,'--native-seconds','750','--binary',BINARY,'--binary-sha256',BINARY_SHA,'--build-manifest',BUILD,'--build-manifest-sha256',BUILD_SHA,
        '--gate',GATE,'--gate-sha256',GATE_SHA,'--address-space-bytes','4294967296','--file-bytes','4294967296']
    plan=dict(schema='FROZEN_COMMITTED_NORMALIZED_GF2_INVOCATION_V1',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,inputs_sha256=pins,command=command,cwd=str(ROOT),
        original_engineering_source_commit='f7834874ad7a9c1ef3ba9daabd09fc18fe24a76a',fresh_preflight=dict(native_workers=workers,permission_uncertain_pids=uncertain,memory_bytes=mem,disks=disks),
        raw_dimensions=dict(columns=23019,rows=85874),allocation=dict(outer=900,worker=850,native_guard=750,cooperative=745,address_space_bytes=4*1024**3,file_bytes=4*1024**3),
        source_bytes_committed_checked=True,gate_exact_bound=True,scope='Normalized literal parity only. No rank/integerfeasibility/graph or unrestricted target claim.',
        next_verification='Different author receives raw23019bit vectors or complete normalized original-row XOR and independently recomputes every literal raw row/content as applicable.',
        scientific_launched=False,automatic_retry=False,independent_approval=False,target_resolution=False,prism_free_premise='UNKNOWN')
    with(out/'plan.json').open('x',encoding='utf8',newline='\n')as f:json.dump(plan,f,indent=2);f.write('\n')
    print(json.dumps(dict(path=(out/'plan.json').relative_to(ROOT).as_posix(),sha256=hashlib.sha256((out/'plan.json').read_bytes()).hexdigest(),source_commit=head,worker_population_empty=True)))


if __name__=='__main__':main()
