"""Freeze one predeclared full99 linear-triple heuristic pilot; no solver launch."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GATE='acceleration/results/20261002_independent_review/hypergraph_controls02/summary.json'
GATE_SHA='81aa0427d80d66b45ae48d47cea98c02de02bc4ae096d5a0bcc688d6df2bacb3'
BUILD='acceleration/results/20261002_hypergraph_build01/build_manifest.json'
BUILD_SHA='555fc69cedfabd76e5c0ffb23bba55e12a366a476320d550ce48771128708bb4'


def main():
    out=ROOT/'acceleration/results/20261002_hypergraph_pilot_plan01'
    out.mkdir(parents=True,exist_ok=False)
    gate_raw=(ROOT/GATE).read_bytes();build_raw=(ROOT/BUILD).read_bytes()
    if hashlib.sha256(gate_raw).hexdigest()!=GATE_SHA or hashlib.sha256(build_raw).hexdigest()!=BUILD_SHA:
        raise ValueError('Exact independent controls and native build required')
    gate=json.loads(gate_raw);build=json.loads(build_raw)
    if gate['status']!='INDEPENDENT_HYPERGRAPH_ANNEAL_V1_CONTROLS_PASS':raise ValueError('Exact independent gate status')
    inputs=build['inputs_sha256']|{GATE:GATE_SHA,BUILD:BUILD_SHA,build['binary_path']:build['binary_sha256']}
    for name,expected in inputs.items():
        actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if actual!=expected:raise ValueError('Exact frozen source/binary identity '+name)
    plan=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        question='Can one predeclared unrestricted linear-triple trade chain produce an exact target graph or a lower independently checkable residual in this new domain?',
        domain='99 labelled points;231 linear triples;pointdegree7, hence14-regular simple point graph. No fixed triangle core, support or target automorphism.',
        selection='One fresh chain, seed99032010, with10000 mixing proposals. No best-of-unrecorded-run selection.',
        objective=dict(id='SRG_SQUARED_PAIR_RESIDUAL_V1',definition='sum over i<j of (common_neighbors(i,j)+A[i,j]-2)^2',
            arithmetic='Exact integers',direction='Minimize to0',limits='Positive scores are heuristic guidance and not certificates; no comparison with other objective versions.'),
        configuration=dict(steps=20000000,seed=99032010,mix_steps=10000,schedule_steps=15000000,
            temperature_start=20.0,temperature_end=0.1,native_seconds=180.0,producer_seconds=270.0,outer_seconds=300.0,
            address_space_bytes=2147483648,file_bytes=1073741824,checkpoint_seconds=15,verify_every=100000),
        success='Save exact current/best/RNG checkpoints and full best adjacency. Only E0 plus independent full99 SRG validation can be a candidate positive resolution.',
        falsification='An independent domain/cache/score or full matrix mismatch vetoes promotion. No timeout or positive residual excludes a graph.',
        independent_verification='Complete independent saved-object scoring and all saved checkpoint checks; full99 graph validator for E0. Sparse scientific trace is not complete trajectory verification.',
        numerical_acceptance='E exactly0 for target candidate; floating Metropolis acceptance guides search only.',
        stopping='20million proposals or native cooperative allocation, whichever first; preserve checkpoints and report incomplete work if allocated budget is reached.',
        resource_rationale='Finite controls gave full99 states and complete score/move replay;180s is a first throughput/quality pilot, with90s worker reserve and30s outer reserve. No inherited solver/build stopping cap.',
        review='Command shorter than1800s; inspect saved checkpoint/resource state during execution and reassess on significant evidence.',
        limitations=['No move-space connectivity, ergodicity or exhaustive coverage claim.','No calibrated success probability.','Initial cyclic construction is a starting point only; target symmetries are not imposed.'],
        inputs_sha256=inputs,target_resolution=False,status='FROZEN_CANDIDATE_SCIENTIFIC_PROTOCOL')
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(status=plan['status'],path=str(out/'plan.json'),sha256=hashlib.sha256((out/'plan.json').read_bytes()).hexdigest())))


if __name__=='__main__':main()
