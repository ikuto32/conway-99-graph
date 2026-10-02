"""Independent full replay with exact negative native diagnostic calibration v2."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'acceleration/results/20261002_hypergraph_controls01/controls_manifest.json'
MANIFEST_SHA = '11236e7a6eb1e3fccd7d08504e215eb8a6bccc10965c8ba2c358e5e3d1863ee0'
M = (1 << 64) - 1
TOL = 1e-12
SCALARS = ('n','degree','seed','mix_steps','schedule_steps','t_start','t_end','forced',
           'step','admissible','accepted','best_updates','energy','best_energy')
INTEGER = re.compile(r'-?(0|[1-9][0-9]*)\Z')


class CheckError(ValueError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(stage + ': ' + message)


def need(value, message, stage='REPLAY'):
    if not value: raise CheckError(stage, message)


def natural(value, stage='SYNTAX'):
    need(INTEGER.fullmatch(value) is not None, 'exact integer token', stage)
    return int(value)


def graph(triples, n, degree):
    need((n, degree) in [(99,7),(9,2)], 'declared graph domain', 'DOMAIN')
    need(len(triples)*3 == n*degree, 'triple population', 'DOMAIN')
    adj = [set() for _ in range(n)]; counts = [0]*n
    for row in triples:
        need(len(row)==3 and all(type(x) is int and 0<=x<n for x in row) and len(set(row))==3,
             'triple range/distinctness', 'DOMAIN')
        for x in row: counts[x] += 1
        for x,y in combinations(row,2):
            need(y not in adj[x], 'linear pair uniqueness', 'DOMAIN')
            adj[x].add(y); adj[y].add(x)
    need(counts == [degree]*n and all(len(row)==2*degree for row in adj), 'regular occurrences/adjacency', 'DOMAIN')
    cn = [len(adj[u] & adj[v]) for u in range(n) for v in range(u+1,n)]
    energy = sum((common + int(v in adj[u]) - 2)**2
                 for common,(u,v) in zip(cn,combinations(range(n),2)))
    return adj,cn,energy


def parse_state(data):
    tokens = data.decode('ascii').split(); at=0
    def take():
        nonlocal at
        need(at<len(tokens), 'complete token stream', 'SYNTAX')
        item=tokens[at]; at+=1; return item
    def field(name):
        need(take()==name, 'ordered field '+name, 'SYNTAX'); return take()
    need(take()=='HYPERGRAPH_ANNEAL_STATE_V1', 'state version', 'SYNTAX')
    s={}
    for name in SCALARS:
        raw=field(name)
        s[name]=float(raw) if name in ['t_start','t_end'] else natural(raw)
    need((s['n'],s['degree']) in [(99,7),(9,2)], 'exact target or control domain', 'DOMAIN')
    need(all(math.isfinite(s[k]) and 0<=s[k]<=1000 for k in ['t_start','t_end']) and s['schedule_steps']>0,
         'bounded temperature schedule', 'SCHEDULE')
    need(all(0<=s[k]<=M for k in ['seed','mix_steps','schedule_steps','step','admissible','accepted','best_updates']) and s['forced'] in [0,1],
         'uint64 counters/config', 'COUNTERS')
    need(take()=='rng', 'RNG tag', 'SYNTAX'); s['rng']=[natural(take(),'RNG') for _ in range(4)]
    need(all(0<=x<=M for x in s['rng']) and any(s['rng']), 'nonzero uint64 RNG', 'RNG')
    for name in ['current','best']:
        count=natural(field(name)); need(count==s['n']*s['degree']//3, name+' triple count', 'DOMAIN')
        s[name]=[[natural(take()) for _ in range(3)] for _ in range(count)]
    a,cn,e=graph(s['current'],s['n'],s['degree'])
    _,_,be=graph(s['best'],s['n'],s['degree'])
    need(e==s['energy'], 'exact current score', 'ENERGY')
    need(be==s['best_energy'] and be<=e, 'exact best score/order', 'BEST_ENERGY')
    count=natural(field('cn')); need(count==len(cn), 'cache population', 'CACHE')
    need([natural(take()) for _ in range(count)]==cn, 'all exact common-neighbor cache entries', 'CACHE')
    need(take()=='END' and at==len(tokens), 'exact record end', 'SYNTAX')
    need(0<=s['best_updates']<=s['accepted']<=s['admissible']<=s['step'], 'counter order', 'COUNTERS')
    return s


def rot(value, count): return ((value << count) | (value >> (64-count))) & M


def seed_words(seed):
    words=[]
    for _ in range(4):
        seed=(seed+0x9e3779b97f4a7c15)&M; z=seed
        z=((z^(z>>30))*0xbf58476d1ce4e5b9)&M
        z=((z^(z>>27))*0x94d049bb133111eb)&M
        words.append(z^(z>>31))
    return words


def rng_next(words):
    result=(rot((words[1]*5)&M,7)*9)&M; t=(words[1]<<17)&M
    words[2]^=words[0]; words[3]^=words[1]; words[1]^=words[2]; words[0]^=words[3]
    words[2]^=t; words[3]=rot(words[3],45)
    return result


def initial(n):
    if n==9: return [[3*x,3*x+1,3*x+2] for x in range(3)]+[[x,x+3,x+6] for x in range(3)]
    return [[x,x+33,x+66] for x in range(33)]+[[x,(x+1)%99,(x+4)%99] for x in range(99)]+[[x,(x+7)%99,(x+18)%99] for x in range(99)]


def replay(s, record):
    before=s['rng'][:]; size=len(s['current'])
    ti=rng_next(s['rng'])%size; tj=rng_next(s['rng'])%(size-1)
    if tj>=ti:tj+=1
    pi=rng_next(s['rng'])%3; pj=rng_next(s['rng'])%3
    t=s['current'][ti][:]; q=s['current'][tj][:]
    x=t[pi]; y=q[pj]; a=t[(pi+1)%3]; b=t[(pi+2)%3]; c=q[(pj+1)%3]; d=q[(pj+2)%3]
    adj,_,old=graph(s['current'],s['n'],s['degree'])
    need(old==s['energy'], 'rebuild current score before every proposal')
    disjoint=not bool(set(t)&set(q)); absent=all(v not in adj[u] for u,v in [(y,a),(y,b),(x,c),(x,d)])
    valid=disjoint and absent; pt=t[:];pq=q[:];pt[pi]=y;pq[pj]=x
    elapsed=max(0,s['step']-s['mix_steps']); fraction=min(1.0,float(elapsed)/float(s['schedule_steps']))
    temp=s['t_start']+(s['t_end']-s['t_start'])*fraction
    mixing=s['step']<s['mix_steps']; draw=0;delta=0;accepted=False;margin=None
    if valid:
        proposal=[row[:] for row in s['current']];proposal[ti]=pt;proposal[tj]=pq
        _,_,score=graph(proposal,s['n'],s['degree']);delta=score-old;draw=rng_next(s['rng'])
        uniform=(draw>>11)/2**53
        if s['forced'] or mixing or delta<=0:accepted=True
        elif temp>0:
            threshold=math.exp(-float(delta)/temp);margin=abs(uniform-threshold)
            need(margin>TOL, 'unambiguous floating acceptance margin', 'FLOAT')
            accepted=uniform<threshold
        s['admissible']+=1
        if accepted:
            s['current']=proposal;s['energy']=score;s['accepted']+=1
            if score<s['best_energy']:
                s['best']=copy.deepcopy(proposal);s['best_energy']=score;s['best_updates']+=1
    expected=dict(step=s['step'],ti=ti,tj=tj,pi=pi,pj=pj,old_triples=[t,q],proposed_triples=[pt,pq],
        disjoint=disjoint,new_pairs_absent=absent,admissible=valid,accepted=accepted,mixing=mixing,
        delta=delta,energy_before=old,energy_after=s['energy'],best_energy=s['best_energy'],draw=str(draw),
        rng_before=[str(w) for w in before],rng_after=[str(w) for w in s['rng']])
    need(set(record)==set(expected)|{'temperature'}, 'exact raw trace fields')
    for name,value in expected.items():
        need(type(record[name]) is type(value) and record[name]==value, 'raw transition '+name)
    need(type(record['temperature']) in [int,float] and math.isfinite(record['temperature']) and abs(temp-record['temperature'])<=TOL,
         'temperature numeric tolerance', 'FLOAT')
    s['step']+=1
    return valid,accepted,delta,margin


def matrix_claim(adj,n,k):
    need(len(adj)==n and all(len(r)==n for r in adj), 'exact matrix dimensions', 'MATRIX')
    need(all(type(x) is int and x in [0,1] for row in adj for x in row), 'binary entries', 'MATRIX')
    need(all(adj[u][u]==0 and sum(adj[u])==k for u in range(n)), 'diagonal/degree', 'MATRIX')
    for u in range(n):
        for v in range(n):
            need(adj[u][v]==adj[v][u], 'symmetry', 'MATRIX')
            squared=sum(adj[u][w]*adj[w][v] for w in range(n))
            need(squared==(k-2 if u==v else 0)-adj[u][v]+2, 'complete exact integer SRG identity', 'MATRIX')


def reject(call, stage):
    try:call()
    except CheckError as error:
        need(error.stage==stage, 'expected diagnostic '+stage+' versus '+error.stage, 'CONTROL')
        return str(error)
    raise CheckError('CONTROL','corrupted control was accepted')


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')


def run(args):
    started=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Full finite adjacency-set/RNG replay of frozen14 controls;20seconds shutdown reserve')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};checked=[];controls=[]
    def tick():need(deadline.status()['remaining_seconds']>20 and not deadline.status()['stop_required'], 'not completed within the allocated budget','DEADLINE')
    def path(name):
        p=(ROOT/name).resolve();need(p.is_relative_to(ROOT) and p.is_file(), 'local repository artifact','IDENTITY');return p
    def pin(name,wanted=None,size=None):
        p=path(name);tick();digest=hashlib.sha256(p.read_bytes()).hexdigest()
        need(wanted is None or digest==wanted,'hash '+name,'IDENTITY');need(size is None or p.stat().st_size==size,'size '+name,'IDENTITY')
        need(name not in pins or pins[name]==digest,'same artifact pin','IDENTITY');pins[name]=digest;return p
    def read(name):return json.loads(path(name).read_bytes())
    def linux(name):return '/mnt/c/'+str((ROOT/name).resolve())[3:].replace('\\','/')
    try:
        pin(MANIFEST,MANIFEST_SHA);manifest=read(MANIFEST)
        need(manifest['schema']=='HYPERGRAPH_ANNEAL_CONTROLS_V1' and manifest['objective']=='SRG_SQUARED_PAIR_RESIDUAL_V1'
             and manifest['target_resolution'] is False and manifest['independent_approval'] is False,'finite raw unapproved manifest','RECEIPT')
        for name,digest in manifest['inputs_sha256'].items():pin(name,digest)
        for source in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:
            pin(source.relative_to(ROOT).as_posix())
        build_name='acceleration/results/20261002_hypergraph_build01/build_manifest.json';build=read(build_name)
        need(build['schema']=='HYPERGRAPH_ANNEAL_NATIVE_BUILD_V1' and build['source_cpp_sha256']==pins['acceleration/hypergraph_anneal_20261002_v1.cpp']
             and build['binary_sha256']==pins[build['binary_path']] and build['compiler_sha256']=='1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769',
             'exact native build/source/compiler pins','RECEIPT')
        pin(build['receipt'],build['receipt_sha256']);br=read(build['receipt'])
        need(br['command']==build['command'] and br['actual_exit_code']==0 and br['reaped'] is True and build['command'][1:6]==['-std=c++17','-O3','-Wall','-Wextra','-Werror'],
             'successful exact native compilation receipt','RECEIPT')
        for name in ['stdout','stderr']:pin(br[name],br[name+'_sha256'])
        outer=manifest['supervision'];pin(outer['path'],outer['sha256']);sm=read(outer['path'])
        ss_name=str(Path(outer['path']).parent/'summary.json').replace('\\','/');pin(ss_name);ss=read(ss_name)
        need(sm['invocation_id']==ss['invocation_id']==outer['invocation_id'] and sm['seconds']==outer['outer_seconds']==300 and outer['producer_seconds']==270
             and sm['cumulative_across_commands'] is False and sm['automatic_retry'] is False,'same fixed contained invocation','RECEIPT')
        need(ss['command_exit_code']==0 and ss['cleanup']['reaped'] is True and ss['cleanup']['job_active_zero_observed'] is True
             and ss['cleanup']['process_group_live_pids']==[] and ss['cleanup']['cleanup_errors']==[], 'actual enclosing Linux cleanup observation','RECEIPT')
        need(outer['guard_argv'][:2]==['/usr/bin/timeout','--signal=KILL'] and outer['guard_argv'][3:6]==['/root/.local/bin/uv','run','--locked'],
             'Linux enclosing GNU timeout/locked runner','RECEIPT')
        runs=manifest['runs'];labels=[r['label'] for r in runs]
        expected=['rook9_positive','rook9_forced','target99_forced','target99_greedy','target99_anneal','target99_mixed','resume_whole','resume_first','resume_second',
                  'reject_energy','reject_best_energy','reject_cn','reject_duplicate_triple','reject_zero_rng']
        need(labels==expected and len(set(labels))==14,'complete frozen14-call population','POPULATION')
        successes={};traces={};all_checkpoints=0;full_proposals=0;valid_proposals=0;minimum_margin=None
        for row in tqdm(runs,desc='independent finite control replay',unit='call'):
            tick();label=row['label'];pin(row['receipt'],row['receipt_sha256']);receipt=read(row['receipt'])
            native_out=str(Path(MANIFEST).parent/label).replace('\\','/')
            command=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s','60.000000s','/usr/bin/prlimit',
                     '--as=2147483648:2147483648','--fsize=1073741824:1073741824','--core=0:0',linux(build['binary_path']),
                     '--out',linux(native_out),'--seconds','55.000000',*row['options']]
            expected_exit=2 if label.startswith('reject_') else 0
            need(receipt['command']==command and receipt['cwd']==linux('') and receipt['actual_exit_code']==row['actual_exit_code']==expected_exit
                 and receipt['expected_exit_code']==expected_exit and receipt['reaped'] is True and receipt['process_group']==outer['group']
                 and receipt['independent_approval'] is False, 'exact contained native receipt/options','RECEIPT')
            for channel in ['stdout','stderr']:pin(receipt[channel],receipt[channel+'_sha256'])
            for name,descriptor in row['artifacts'].items():pin(name,descriptor['sha256'],descriptor['bytes'])
            actual_files={p.relative_to(ROOT).as_posix() for p in path(row['receipt']).parent.joinpath(label).iterdir() if p.is_file()}
            need(actual_files==set(row['artifacts']), 'complete saved per-call artifact inventory','POPULATION')
            if expected_exit:
                need(row['artifacts']=={} and path(receipt['stderr']).stat().st_size>0,'producer rejected corrupt checkpoint before outputs','RECEIPT')
                diagnostics={'reject_energy':'checkpoint exact current/best scores',
                             'reject_best_energy':'checkpoint exact current/best scores',
                             'reject_cn':'checkpoint exact CN cache',
                             'reject_duplicate_triple':'linear hypergraph pair multiplicity',
                             'reject_zero_rng':'nonzero RNG state'}
                need(path(receipt['stderr']).read_text().splitlines()==[diagnostics[label]] and path(receipt['stdout']).read_bytes()==b'',
                     'exact producer rejection diagnostic; unrelated exit2 does not calibrate', 'CONTROL')
                continue
            base=ROOT/native_out;initial_data=(base/'initial.state').read_bytes();s=parse_state(initial_data);start=copy.deepcopy(s)
            options=row['options'];opts={};at=0
            while at<len(options):
                key=options[at];at+=1
                if key=='--forced':opts[key]=True;continue
                need(at<len(options),'raw option value','SYNTAX');opts[key]=options[at];at+=1
            steps=int(opts['--steps']);need(int(opts['--trace-max'])==steps,'every control proposal fully traced','POPULATION')
            if '--resume' in opts:
                need(initial_data==(ROOT/str(Path(MANIFEST).parent/'resume_first/final.state')).read_bytes(), 'resume raw initial byte identity','RESUME')
            else:
                need(s['step']==s['admissible']==s['accepted']==s['best_updates']==0 and s['current']==s['best']==initial(s['n'])
                     and s['rng']==seed_words(int(opts['--seed'])),'independent fixture and initial RNG','INITIAL')
                need(s['seed']==int(opts['--seed']) and s['mix_steps']==int(opts['--mix-steps']) and s['schedule_steps']==int(opts['--schedule-steps'])
                     and s['t_start']==float(opts['--temperature-start']) and s['t_end']==float(opts['--temperature-end']) and s['forced']==int('--forced' in opts),'initial exact configuration','INITIAL')
            snapshots={}
            for file in sorted(base.glob('checkpoint_*.state')):
                snap=parse_state(file.read_bytes());need(file.name=='checkpoint_'+str(snap['step'])+'.state', 'checkpoint label/step','CHECKPOINT')
                need(snap['step'] not in snapshots,'unique checkpointstep','CHECKPOINT');snapshots[snap['step']]=snap
            records=[json.loads(line) for line in (base/'moves.jsonl').read_text().splitlines()]
            need(len(records)==steps,'full raw trace cardinality','POPULATION');traces[label]=records
            for index,record in enumerate(records):
                if index%128==0:tick()
                valid,accepted,delta,margin=replay(s,record);valid_proposals+=int(valid);full_proposals+=1
                if margin is not None:minimum_margin=margin if minimum_margin is None else min(minimum_margin,margin)
                if s['step'] in snapshots:need(s==snapshots.pop(s['step']),'every full saved checkpoint matches replay','CHECKPOINT');all_checkpoints+=1
            need(not snapshots,'no unreplayed checkpoint','CHECKPOINT')
            final=parse_state((base/'final.state').read_bytes());need(final==s,'complete final state matches independent replay','CHECKPOINT')
            adj,_,_=graph(s['best'],s['n'],s['degree']);matrix=[[int(v in adj[u]) for v in range(s['n'])] for u in range(s['n'])]
            text=(base/'best.adj').read_text().splitlines();need(text==[str(s['n'])]+[''.join(map(str,r)) for r in matrix],'raw full best adjacency exact','MATRIX')
            result=json.loads((base/'result.json').read_bytes())
            facts=dict(objective='SRG_SQUARED_PAIR_RESIDUAL_V1',n=s['n'],point_degree=s['degree'],triple_count=len(s['current']),initial_energy=start['energy'],
                       current_energy=s['energy'],best_energy=s['best_energy'],starting_step=start['step'],ending_step=s['step'],proposals_this_invocation=steps,
                       admissible_total=s['admissible'],accepted_total=s['accepted'],best_updates_total=s['best_updates'],stop_reason='REQUESTED_STEPS_COMPLETE',
                       target_resolution=False,independent_approval=False)
            need({k:v for k,v in result.items() if k!='elapsed_seconds'}==facts and 0<=result['elapsed_seconds']<=receipt['wall_seconds'], 'raw result exactly replayed','RESULT')
            if label=='rook9_positive':
                matrix_claim(matrix,9,4);need(matrix==[[int(u!=v and (u//3==v//3 or u%3==v%3)) for v in range(9)] for u in range(9)], 'independent rook grid adjacency','CONTROL')
                controls.append({'positive':'exact srg(9,4,1,2) all81 integer identities','rejected_99_scope':reject(lambda:matrix_claim(matrix,99,14),'MATRIX')})
                corrupt=copy.deepcopy(matrix);corrupt[0][1]=corrupt[1][0]=0
                controls.append({'corrupted_rook_edge':reject(lambda:matrix_claim(corrupt,9,4),'MATRIX')})
            if s['n']==99:need(s['best_energy']>0,'finite targetcontrols did not create a resolution','RESULT')
            successes[label]=dict(initial=start,final=final)
            checked.append(dict(label=label,full_trace_proposals=steps,admissible_proposals_recomputed=sum(r['admissible'] for r in records),initial_energy=start['energy'],
                                current_energy=s['energy'],best_energy=s['best_energy'],ending_step=s['step'],receipt_sha256=row['receipt_sha256']))
        corruption_stages={'energy':'ENERGY','best_energy':'BEST_ENERGY','cn':'CACHE','duplicate_triple':'DOMAIN','zero_rng':'RNG'}
        need([r['type'] for r in manifest['corruptions']]==list(corruption_stages),'five exact corrupted controls','POPULATION')
        for item in manifest['corruptions']:
            p=pin(item['path'],item['sha256']);need(item['expected_exit_code']==2,'declared malformed rejection','CONTROL')
            controls.append({'raw_corruption':item['type'],'diagnostic':reject(lambda:parse_state(p.read_bytes()),corruption_stages[item['type']])})
        original=traces['target99_greedy'][0];initial_state=successes['target99_greedy']['initial']
        for field in ['delta','energy_after','rng_after','accepted']:
            bad=copy.deepcopy(original)
            if field=='rng_after':bad[field][0]=str(int(bad[field][0])^1)
            elif field=='accepted':bad[field]=not bad[field]
            else:bad[field]+=1
            controls.append({'mutated_trace_field':field,'diagnostic':reject(lambda:replay(copy.deepcopy(initial_state),bad),'REPLAY')})
        control_root=ROOT/Path(MANIFEST).parent
        need((control_root/'resume_whole/final.state').read_bytes()==(control_root/'resume_second/final.state').read_bytes(), 'whole/split raw final byte identity','RESUME')
        need(traces['resume_whole']==traces['resume_first']+traces['resume_second'], 'whole/split complete trace identity','RESUME')
        save(out/'checked_controls.json',{'runs':checked,'checking_controls':controls,'all_saved_intermediate_checkpoints':all_checkpoints,
                                         'full_proposals':full_proposals,'admissible_proposals_full_rescored':valid_proposals,'minimum_probabilistic_decision_margin':minimum_margin})
        source_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
        summary=dict(status='INDEPENDENT_HYPERGRAPH_ANNEAL_V1_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source_commit,
            producer_source_commit=manifest['source_commit'],verifier='/root/checkpoint_audit',producer='/root/native_driver',claim_revision=None,
            claim_revision_null_reason='Finite engineering gate; no mathematical research claim promotion.',scope='Fourteen frozen native engineering calls only; nine complete successful trajectories and five rejected corrupt checkpoints.',
            inputs_sha256=pins,outputs_sha256={'checked_controls.json':hashlib.sha256((out/'checked_controls.json').read_bytes()).hexdigest()},
            native_calls_observed=14,new_native_calls=0,successful_calls_completely_replayed=9,rejected_corrupt_calls=5,full_proposals=full_proposals,
            admissible_proposals_full_rescored=valid_proposals,all_saved_intermediate_checkpoints=all_checkpoints,independent_calibrated_controls=len(controls),
            numerical_acceptance=dict(energies_deltas_counts_rng_cache='EXACT_INTEGERS',temperature_absolute_tolerance=TOL,required_probabilistic_margin=TOL,
                                      actual_minimum_probabilistic_margin=minimum_margin),
            comparison='Adjacency-set complete graph rescoring versus producer incremental toggles/bitset cache; independently expanded exact RNG.',
            shared_trusted_components=['Python integer/set arithmetic and JSON','SHA-256','Python libm for heuristic exp only','uv runtime','policy supervisor/deadline'],
            limitations=['Finite engineering controls are not general trajectory or performance guarantees.','No independent compiler reconstruction; exact saved build/receipt identities checked.',
                         'Probabilistic acceptance is heuristic; exact energy is not a graph certificate unless complete target validator passes.',
                         'No scientific search, exhaustive coverage, target exclusion, or mathematical resolution.','Historical cleanup observations do not assert a currently running process.'],
            target_resolution=False,overall_search_coverage='UNKNOWN; no validated denominator.',tool_versions={'python':platform.python_version(),'platform':platform.platform()},
            exact_argv=sys.argv,working_directory=str(ROOT),elapsed_seconds=time.monotonic()-started,deadline=deadline.status())
        save(out/'summary.json',summary);print(json.dumps({k:summary[k] for k in ['status','full_proposals','admissible_proposals_full_rescored','all_saved_intermediate_checkpoints','elapsed_seconds']}))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),status='INDEPENDENT_CHECK_FAILED',error=repr(error),inputs_sha256=pins,
            completed_calls=checked,controls=controls,elapsed_seconds=time.monotonic()-started,target_resolution=False));raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True)
    run(parser.parse_args())
