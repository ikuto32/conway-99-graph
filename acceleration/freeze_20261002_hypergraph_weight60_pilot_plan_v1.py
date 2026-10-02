"""Fresh committed exact-gate/resource preflight and fixed weight60 pilot plan.

Metadata only: never launches science, changes the Git index or approves results.
"""
import argparse,hashlib,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
CODE=['acceleration/prepare_20261002_hypergraph_weight60_v2.py',
    'acceleration/hypergraph_weight60_anneal_20261002_v2.cpp',
    'acceleration/prepare_20261002_hypergraph_weight60_v2_spec.md',
    'acceleration/design_20261002_hypergraph_weight60_v2.md',
    'acceleration/plan_20261002_hypergraph_weight60_engineering_v2.json',
    'acceleration/plan_20261002_hypergraph_weight60_correction_v2.json',
    'acceleration/command_deadline.py','acceleration/run_compute_command.py',
    'acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock']
BINARY='acceleration/results/20261002_hypergraph_weight60_build02/hypergraph_weight60_anneal'
BINARY_SHA='6bafa6ccaae4df4bc86369e2a7ae21af8376eff63fb42bbbc98331e11633b446'
BUILD='acceleration/results/20261002_hypergraph_weight60_build02/build_manifest.json'
BUILD_SHA='dbb76b121277e131e8c58e1b5e2b125e90c73233f1e9a25f98bdd9c41aeb0a71'
RAW='acceleration/results/20261002_hypergraph_weighted_pilot02/native/final.state'
RAW_SHA='f4df0eadf3e7c4199c0715ed6c647ea995e41ffe8f972f91889b3a62a10879ad'
RAW_GATE='acceleration/results/20261002_independent_review/hypergraph_weighted_pilot02/summary.json'
RAW_GATE_SHA='6e84a14ccd230801ce9efacdddf99bf90876933ff53997898b367e73c91156f0'
CONTROLS='acceleration/results/20261002_hypergraph_weight60_controls02/controls_manifest.json'
CONTROLS_SHA='92beb153d4d2abc1a93da1ef29d583153c411668916336fe366f41d05525f43f'
OUTER='acceleration/results/20261002_hypergraph_weight60_pilot_supervision01'
RESULT='acceleration/results/20261002_hypergraph_weight60_pilot01'

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=float,required=True)
    p.add_argument('--source-commit',required=True)
    for label in ['gate','saved-gate']:
        p.add_argument('--'+label,required=True);p.add_argument('--'+label+'-sha256',required=True)
    a=p.parse_args();d=CommandDeadline(a.seconds,allocation_reason='Exact committednew weight60V2 finite/savedchecker source/hash closure plus fresh fullyobservable workers/memory/disk andfixed600/550/450 pilotplan; no science launch')
    need(sys.platform.startswith('linux') and os.geteuid()==0,'root Linux metadata observer context required; science remains defaultUID1000')
    need(os.environ.get('GIT_CONFIG_COUNT')=='1' and os.environ.get('GIT_CONFIG_KEY_0')=='safe.directory' and os.environ.get('GIT_CONFIG_VALUE_0')==str(ROOT),'process-local Git safety scope must be this exact workspace only')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();need(head==a.source_commit,'explicit fresh published source HEAD')
    out=a.out.resolve();need(out.is_relative_to(ROOT),'repository plan output');out.mkdir(parents=True,exist_ok=False);pins={};objects={}
    def pin(name,wanted=None):
        need(type(name)is str and not Path(name).is_absolute(),'repository-relative exact input reference')
        need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'not completed within allocated metadata budget')
        if name in pins:
            need(wanted is None or pins[name]==wanted,'consistent repeated identity');return objects.get(name)
        f=(ROOT/name).resolve();need(f.is_relative_to(ROOT) and f.is_file(),'exact committed source/artifact exists '+name)
        raw=f.read_bytes();digest=hashlib.sha256(raw).hexdigest();need(wanted is None or digest==wanted,'exact identity '+name)
        blob=subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)
        need(hashlib.sha256(blob).hexdigest()==digest,'working bytes equal committed bytes '+name)
        pins[name]=digest
        if f.suffix=='.json':objects[name]=json.loads(raw)
        return objects.get(name)
    gate=pin(a.gate,a.gate_sha256);saved=pin(a.saved_gate,a.saved_gate_sha256)
    need(gate['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_ANNEAL_V2_CONTROLS_PASS','new exact overlap-kernel engineering gate')
    need(saved['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_CALIBRATION_PASS','new changed-format saved-object/scalar matrix checker calibration')
    for name in CODE+[BINARY,BUILD]:pin(name,gate['inputs_sha256'][name])
    need(pins[BINARY]==BINARY_SHA and pins[BUILD]==BUILD_SHA,'fixed calibrated binary/build identities')
    for report in [gate,saved]:
        need(type(report.get('inputs_sha256'))is dict and report['inputs_sha256'],'explicit complete gate/checker dependency closure')
        for name,wanted in report['inputs_sha256'].items():pin(name,wanted)
    pin(CONTROLS,CONTROLS_SHA);pin(RAW,RAW_SHA);rawgate=pin(RAW_GATE,RAW_GATE_SHA)
    need(rawgate is not None and rawgate['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_SAVED_OBJECTS_V2_PASS' and rawgate['inputs_sha256'][RAW]==RAW_SHA,'independently checked old graph import source; no execution gate transfer')
    selfkey=Path(__file__).resolve().relative_to(ROOT).as_posix();pin(selfkey);pin('acceleration/freeze_20261002_hypergraph_weight60_pilot_plan_v1_spec.md')
    workers=[];uncertain=[]
    names={'literal_gf3','rooted8_gf3','normalized_gf2','hypergraph_weight60_anneal','hypergraph_weighted_anneal','hypergraph_anneal','cadical','drat-trim'}
    producers=['prepare_20261002_hypergraph_weight60_v2.py research','prepare_20261002_hypergraph_weighted_v1.py research','prepare_20261002_rooted8_gf3_v2.py solve','prepare_20261002_rooted8_normalized_gf2_v2.py solve']
    for proc in Path('/proc').iterdir():
        if not proc.name.isdecimal():continue
        try:
            exe=(proc/'exe').resolve(strict=True);cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode('ascii',errors='replace')
            if exe.name in names or any(name in cmd for name in producers):workers.append(dict(pid=int(proc.name),exe=str(exe),cmdline=cmd))
        except FileNotFoundError:pass
        except PermissionError:uncertain.append(int(proc.name))
    need(not workers and not uncertain,'fresh recognized scientific/proof worker population must be empty and observable')
    mem={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines()) if k in ['MemTotal','MemAvailable']}
    disks={label:shutil.disk_usage(path)._asdict() for label,path in [('host',ROOT),('ext4',Path('/'))]}
    need(mem['MemAvailable']>8*1024**3 and disks['host']['free']>32*1024**3 and disks['ext4']['free']>8*1024**3,'declared fresh RAM/host/ext4 reserves')
    need(not(ROOT/OUTER).exists() and not(ROOT/RESULT).exists(),'fresh fixed scientific output roots')
    cmd=['/usr/bin/python3','acceleration/run_compute_command.py','--seconds','600','--shutdown-reserve-seconds','10',
      '--allocation-reason','One fixed newkernel F60pilot100millionproposals importedbestweight6; prior20million41.9native seconds and57engineeringcalls23.38outer, not a throughput guarantee;550worker450guard445cooperative withreserves.',
      '--success-criterion','Preserve exactcurrent/best andfirstobservedlambda0 rawstate/matrices/RNG/counters; complete100millionproposals or orderlyallocatedtime checkpoint; targetzero requires separatefull99integer SRG check.',
      '--verification-criterion','Differentauthor complete savedobjects andscalar raw99matrix scores/CN/components/identity; firstlambda0 partialonly unlessallmu2; sparse scientific trace gaps explicit; no producerapproval or targetcoverage.',
      '--out',OUTER,'--','/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv','/root/.local/bin/uv','run','--locked','--offline','--project','acceleration/native_budget_env_v1',
      '--cache-dir','build/native-budget-linux-cache','--python','/usr/bin/python3','python',CODE[0],'research',
      '--seconds','550','--allocation-reason','Exactlyone newfixedweight60 seed99032060 graphimport;100mproposals schedule80m T60to.1 mix0;450guard445cooperative2GiBAS1GiBfile, no retries/extensions.',
      '--source-commit',head,'--supervision-out',OUTER,'--out',RESULT,'--native-seconds','450',
      '--binary',BINARY,'--binary-sha256',BINARY_SHA,'--build-manifest',BUILD,'--build-manifest-sha256',BUILD_SHA,
      '--gate',a.gate,'--gate-sha256',a.gate_sha256,'--saved-gate',a.saved_gate,'--saved-gate-sha256',a.saved_gate_sha256,
      '--import-weight6',RAW,'--import-weight6-sha256',RAW_SHA,'--import-select','best','--seed','99032060',
      '--steps','100000000','--mix-steps','0','--schedule-steps','80000000','--temperature-start','60','--temperature-end','0.1',
      '--address-space-bytes','2147483648','--file-bytes','1073741824']
    plan=dict(schema='FROZEN_COMMITTED_WEIGHT60_EXCLUSIVE_KERNEL_PILOT_V1',timestamp=datetime.now(timezone.utc).isoformat(),
      source_commit=head,inputs_sha256=pins,command=cmd,cwd=str(ROOT),objective='SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2',lambda_weight=60,
      move_kernel='LINEAR_TRIPLE_EXCLUSIVE_SWAP_V2',population=dict(scientific_invocations=1,seed=99032060,maximum_proposals=100000000,complete_schedule_proposals=80000000,mix_steps=0,forced=False),
      import_selection=dict(path=RAW,sha256=RAW_SHA,selected='best',oldF6=3801,newF60=7203,lambda_energy=63,mu_energy=3423,ordinaryE=3486,new_rng_and_all_counters_reset=True),
      allocation=dict(outer=600,worker=550,native_guard=450,cooperative=445,address_space_bytes=2*1024**3,file_bytes=1024**3),
      numerical_acceptance='Exactinteger F60andcomponent objectives; bounded temperature/exp/RNG acceptance is heuristic; no floatingcertificate.',
      first_lambda0_rule='First observedCURRENTlambda0,includinginitial; storeits completecurrent/best/config/RNG/counters snapshot separately evenifnotbestF60; partialcriterion only.',
      fresh_preflight=dict(native_workers=workers,permission_uncertain_pids=uncertain,memory_bytes=mem,disks=disks),
      observation_context=dict(uid=os.geteuid(),git_safe_directory=os.environ.get('GIT_CONFIG_VALUE_0'),scientific_uid=1000),
      source_bytes_committed_checked=True,gate_exact_bound=True,savedchecker_exact_bound=True,source_commit_scope='Exactfresh committed sourceandbinary/checker/gates bound; no uncommittedinput exceptions',
      success='Requestedstepscomplete or completecheckpoint atallocatednative deadline; candidatepartiallambda0/rawzero receives independentinteger99matrix checker.',
      falsification='Any source/hash/domain/cache/scorer/selection/independent-validator veto preventspromotion; preserve all rawstates/receipts without retry.',
      limitations=['No newkernel throughput or success probability guarantee.','No connectedmove-space or exhaustivecoverage claim.','F60 is a differentobjective fromF6 orordinaryE.','Savedobjects checkedcompletely; sparse trajectory remains sampled.'],
      overall_search_coverage='UNKNOWN; no validated denominator.',scientific_launched=False,automatic_retry=False,independent_approval=False,target_resolution=False)
    with(out/'plan.json').open('x',encoding='utf8') as f:json.dump(plan,f,indent=2);f.write('\n')
    print(json.dumps(dict(plan=(out/'plan.json').relative_to(ROOT).as_posix(),sha256=hashlib.sha256((out/'plan.json').read_bytes()).hexdigest(),source_commit=head,scientific_launched=False)))

if __name__=='__main__':main()
