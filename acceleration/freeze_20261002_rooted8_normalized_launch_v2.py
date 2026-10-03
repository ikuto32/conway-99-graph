"""Freeze normalizedGF2 invocation with committed recoverable raw-input closure.

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
PACKAGE='acceleration/results/20261002_wave33_model_package01/manifest.json'
PACKAGE_SHA='c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145'
RECOVERY='acceleration/results/20261002_independent_review/wave33_model_recovery01/summary.json'
RECOVERY_SHA='b9352a5e5810f20ff9187c06f5e00636f2f3abad2810ed3d7c23df655b76f583'
RAW_BYTES=57414699


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
    # The sole non-Git raw artifact exception is authenticated by a committed
    # lossless package and a separately authored committed full recovery audit.
    # All seventeen package parts are individually checked against Git; the
    # selected model's seven ordered parts additionally bind its exact coverage.
    package=pin(PACKAGE,PACKAGE_SHA);recovery=pin(RECOVERY,RECOVERY_SHA)
    need(package['schema']=='WAVE33_LITERAL_MODELS_LOSSLESS_V1' and package['record_count']==4 and package['gzip_parts']==17,'frozen four-model package dimensions')
    need(recovery['status']=='INDEPENDENT_WAVE33_FOUR_LITERAL_MODELS_RAW_RECOVERY_PASS' and recovery['inputs_sha256'][PACKAGE]==PACKAGE_SHA,'independent exact package recovery')
    need(recovery['originals']==4 and recovery['gzip_parts']==17,'frozen recovery dimensions')
    selected=[r for r in package['records'] if r['raw_path']==RAW]
    checked=[r for r in recovery['records'] if r['path']==RAW]
    need(len(selected)==1 and len(checked)==1,'unique raw model record and independent recovery record')
    record=selected[0];review=checked[0]
    need(record['raw_sha256']==RAW_SHA and record['raw_bytes']==RAW_BYTES and len(record['parts'])==7,'exact selected raw model identity')
    need(review['sha256']==RAW_SHA and review['mathematical_audit_input_hash']==RAW_SHA and review['bytes']==RAW_BYTES and review['parts']==7 and review['literal_byte_comparison'] is True and review['restored_every_byte_matches'] is True,'complete independent raw model byte recovery')
    part_names=set();part_count=0
    for member in package['records']:
        offset=0
        for part in member['parts']:
            name=part['path'];need(name not in part_names,'unique committed package part');part_names.add(name);part_count+=1
            need(part['raw_offset']==offset and part['raw_bytes']>0,'ordered contiguous raw part coverage');offset+=part['raw_bytes']
            need(recovery['inputs_sha256'][name]==part['gzip_sha256'],'independent recovery pins compressed part')
            pin(name,part['gzip_sha256']);need((ROOT/name).stat().st_size==part['gzip_bytes'],'exact compressed part length')
        need(offset==member['raw_bytes'],'complete declared raw member coverage')
    need(part_count==17,'all seventeen committed compressed parts')
    pin(RAW,RAW_SHA,committed=False);need((ROOT/RAW).stat().st_size==RAW_BYTES,'exact local raw model length')
    # Recheck each selected raw segment against its public package descriptor,
    # without decompressing or silently replacing the original raw file.
    with (ROOT/RAW).open('rb') as source:
        for part in record['parts']:
            need(source.tell()==part['raw_offset'],'selected raw segment offset')
            segment=source.read(part['raw_bytes']);need(len(segment)==part['raw_bytes'] and hashlib.sha256(segment).hexdigest()==part['raw_sha256'],'selected raw segment length/hash')
        need(source.read(1)==b'','selected raw model no extra tail')
    raw_recovery=dict(raw_path=RAW,raw_sha256=RAW_SHA,raw_bytes=RAW_BYTES,committed_raw=False,
        sole_uncommitted_input_exception=True,package_manifest=PACKAGE,package_manifest_sha256=PACKAGE_SHA,
        independent_recovery_report=RECOVERY,independent_recovery_report_sha256=RECOVERY_SHA,
        committed_package_parts=17,selected_model_parts=7,selected_raw_segment_hashes_checked=True,
        retrieval='Use the unchanged recovery CLI/argv recorded in the pinned independent recovery report with the committed package; authenticate every compressed and raw part before use.',
        limitation='Source/input authentication only; the recovery report establishes no model mathematics or fresh public network retrieval.')
    pin(NORM,NORM_SHA);pin(ENC,ENC_SHA);pin('acceleration/plan_20261002_rooted8_normalized_gf2_v2.json')
    selfkey=Path(__file__).resolve().relative_to(ROOT).as_posix();pin(selfkey)
    pin('acceleration/freeze_20261002_rooted8_normalized_launch_v2_spec.md')
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
    plan=dict(schema='FROZEN_COMMITTED_NORMALIZED_GF2_INVOCATION_V2',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,inputs_sha256=pins,command=command,cwd=str(ROOT),
        original_engineering_source_commit='f7834874ad7a9c1ef3ba9daabd09fc18fe24a76a',fresh_preflight=dict(native_workers=workers,permission_uncertain_pids=uncertain,memory_bytes=mem,disks=disks),
        raw_dimensions=dict(columns=23019,rows=85874),allocation=dict(outer=900,worker=850,native_guard=750,cooperative=745,address_space_bytes=4*1024**3,file_bytes=4*1024**3),
        source_bytes_committed_checked=True,committed_input_exceptions=[RAW],raw_input_recovery_binding=raw_recovery,gate_exact_bound=True,scope='Normalized literal parity only. No rank/integerfeasibility/graph or unrestricted target claim.',
        next_verification='Different author receives raw23019bit vectors or complete normalized original-row XOR and independently recomputes every literal raw row/content as applicable.',
        scientific_launched=False,automatic_retry=False,independent_approval=False,target_resolution=False,prism_free_premise='UNKNOWN')
    with(out/'plan.json').open('x',encoding='utf8',newline='\n')as f:json.dump(plan,f,indent=2);f.write('\n')
    print(json.dumps(dict(path=(out/'plan.json').relative_to(ROOT).as_posix(),sha256=hashlib.sha256((out/'plan.json').read_bytes()).hexdigest(),source_commit=head,worker_population_empty=True)))


if __name__=='__main__':main()
