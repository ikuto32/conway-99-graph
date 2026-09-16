"""Reproducibility, negative controls, and a saved useful two-trade detour."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from audit_two_trade_proposals import audit, digest, key
from audit_certificate import require

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'acceleration/results/20260916_two_trade_qa'
EXE = ROOT/'acceleration/build/overlap_two_neighbors.exe'


def read(path):
    return json.loads(path.read_bytes())


def save(path, data):
    require(not path.exists(), 'Preserve prior QA artifact')
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')


def run(input_path, output, limit='128', seed='20260922'):
    return subprocess.run([str(EXE),str(input_path),str(output),limit,seed],
                          capture_output=True,text=True,timeout=30)


def main():
    candidate_path = ROOT/'acceleration/results/20260916_coupled_alt/best_candidate.json'
    candidate = read(candidate_path)
    original = read(OUT/'proposals.json')
    repeat_path = OUT/'proposals_repeat.json'
    if not repeat_path.exists():
        require(run(OUT/'input.txt', repeat_path).returncode == 0, 'Repeat run failed')
    repeat = read(repeat_path)
    original_semantics, repeat_semantics = deepcopy(original), deepcopy(repeat)
    original_semantics.pop('elapsed_seconds'); repeat_semantics.pop('elapsed_seconds')
    require(original_semantics == repeat_semantics, 'Same seed did not reproduce the exact sample')
    second_seed = OUT/'proposals_other_seed.json'
    if not second_seed.exists():
        require(run(OUT/'input.txt', second_seed, seed='20260923').returncode == 0, 'Other seed failed')
    other = read(second_seed)
    require(other['trade_paths'] != original['trade_paths'], 'Other seed produced identical paths')
    other_audit = audit(candidate, other)

    native_controls = []
    raw = (OUT/'input.txt').read_text(encoding='ascii').split()
    mutated = {}
    tokens=raw.copy();tokens[2:4]=tokens[4:6];mutated['duplicate_edge']=tokens
    tokens=raw.copy();tokens[3]='84';mutated['out_of_range']=tokens
    tokens=raw.copy();tokens.append('0');mutated['trailing_token']=tokens
    tokens=raw.copy();tokens[1]='2';mutated['wrong_candidate_count']=tokens
    tokens=raw.copy();tokens[2]='-1';mutated['negative_endpoint']=tokens
    for name,tokens in mutated.items():
        path=OUT/(name+'.txt');text=' '.join(tokens)+'\n'
        if path.exists():
            require(path.read_text(encoding='ascii') == text, 'Saved negative input changed')
        else:
            path.write_text(text,encoding='ascii')
        output=OUT/(name+'_must_not_exist.json')
        result=run(path,output)
        require(result.returncode != 0 and not output.exists(), f'Invalid native input accepted: {name}')
        native_controls.append(dict(name=name,rejected=True,message=result.stderr.strip()))
    for name,limit,seed in [('zero_limit','0','0'),('large_limit','4097','0'),('negative_seed','1','-1')]:
        output=OUT/(name+'_must_not_exist.json');result=run(OUT/'input.txt',output,limit,seed)
        require(result.returncode != 0 and not output.exists(), f'Invalid native CLI accepted: {name}')
        native_controls.append(dict(name=name,rejected=True,message=result.stderr.strip()))
    before=digest(OUT/'proposals.json');result=run(OUT/'input.txt',OUT/'proposals.json')
    require(result.returncode != 0 and digest(OUT/'proposals.json') == before, 'Existing output overwritten')
    native_controls.append(dict(name='existing_output',rejected=True,message=result.stderr.strip()))

    audit_controls=[]
    corruptions={}
    broken=deepcopy(original);broken['trade_paths'][0][0]['removed'][0]=[0,1];corruptions['wrong_removed_edge']=broken
    # Independent swaps may legally commute; reversal alone is not corruption.
    reversed_path=deepcopy(original);reversed_path['trade_paths'][0].reverse()
    reverse_control=audit(candidate,reversed_path)
    broken=deepcopy(original);broken['trade_paths'][0].pop();corruptions['truncated_path']=broken
    broken=deepcopy(original);broken['overlap_candidates'][0][0]=[0,1];corruptions['wrong_final_graph']=broken
    broken=deepcopy(original);broken['trade_paths'][1]=deepcopy(broken['trade_paths'][0]);broken['overlap_candidates'][1]=deepcopy(broken['overlap_candidates'][0]);corruptions['duplicate_final']=broken
    broken=deepcopy(original);broken['trade_paths'][0][1]={'removed':deepcopy(broken['trade_paths'][0][0]['added']),'added':deepcopy(broken['trade_paths'][0][0]['removed'])};broken['overlap_candidates'][0]=candidate['overlap_edges_outer_zero_based'];corruptions['backtrack']=broken
    for name,broken in corruptions.items():
        try:
            audit(candidate,broken)
        except ValueError as error:
            audit_controls.append(dict(name=name,rejected=True,message=str(error)))
        else:
            raise ValueError('Audit accepted corruption '+name)

    pilot=ROOT/'acceleration/results/20260916_global_pilot'
    summary=read(pilot/'summary.json')
    first,second=summary['records'][:2]
    require(first['accepted'] and second['accepted'], 'Known detour no longer matches saved trace')
    initial_path=ROOT/first['previous_probe']['candidate_path']
    middle_path=ROOT/first['chosen_probe']['candidate_path']
    final_path=ROOT/second['chosen_probe']['candidate_path']
    for record in (first['previous_probe'],first['chosen_probe'],second['chosen_probe']):
        require(digest(ROOT/record['candidate_path']) == record['candidate_sha256'], 'Saved detour candidate hash mismatch')
    initial,middle,final=map(read,(initial_path,middle_path,final_path))
    path=[{k:r[k] for k in ('removed','added')} for r in (first,second)]
    require(sorted((set(map(tuple,initial['overlap_edges_outer_zero_based']))-set(map(tuple,path[0]['removed'])))|set(map(tuple,path[0]['added']))) == sorted(map(tuple,middle['overlap_edges_outer_zero_based'])), 'Detour intermediate mismatch')
    detour_audit=audit(initial,dict(status='BOUNDED_TWO_TRADE_PROPOSALS',trade_paths=[path],overlap_candidates=[final['overlap_edges_outer_zero_based']],returned_candidates=1,sample_limit=1))
    middle_ac_path=pilot/'accepted_pair_controls/iteration_0000_pair.json'
    final_ac_path=pilot/'accepted_pair_controls/iteration_0001_pair.json'
    middle_ac,final_ac=map(read,(middle_ac_path,final_ac_path))
    require(middle_ac['propagation_status'] == 'EMPTY_DOMAIN' and final_ac['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY', 'Saved detour AC outcomes mismatch')
    detour_sources=[pilot/'summary.json',initial_path,middle_path,final_path,middle_ac_path,final_ac_path]
    detour=dict(status='SAVED_TRACE_TWO_TRADE_DETOUR_REPLAY_PASS',trade_path=path,
                initial_candidate=key(initial_path),intermediate_candidate=key(middle_path),final_candidate=key(final_path),
                initial_numeric_merit=first['previous_probe']['objective'],final_numeric_merit=second['chosen_probe']['objective'],
                intermediate_native_pair_status=middle_ac['propagation_status'],final_native_pair_status=final_ac['propagation_status'],
                independent_partial_graph_replay=detour_audit,inputs_sha256={key(p):digest(p) for p in detour_sources},
                scope='Saved legal detour illustrates why an intermediate pair-AC gate can block a useful two-trade path. Native AC statuses are referenced, not independently replayed here. This path is not asserted present in the random 128-proposal sample.')
    save(OUT/'known_detour.json',detour)
    require(digest(ROOT/'acceleration/overlap_neighbors.rs') == '2c7fa9f6c7f4925135880d78c0e257e56c797615a8e92e50491a19ddd2c8b17d','Frozen one-step source changed')
    sources=[Path(__file__),ROOT/'acceleration/overlap_two_neighbors.rs',EXE,ROOT/'acceleration/audit_two_trade_proposals.py',
             ROOT/'acceleration/audit_certificate.py',candidate_path,OUT/'input.txt',OUT/'proposals.json',OUT/'audit.json',
             repeat_path,second_seed,OUT/'known_detour.json']
    report=dict(status='TWO_TRADE_NATIVE_QA_PASS',inputs_sha256={key(p):digest(p) for p in sources},
                deterministic_same_seed=True,different_seed_distinct=True,returned_candidates=original['returned_candidates'],
                native_seconds=original['elapsed_seconds'],independent_audit=read(OUT/'audit.json'),other_seed_audit=other_audit,
                native_negative_controls=native_controls,audit_negative_controls=audit_controls,
                commuting_swap_reversal_passes=reverse_control['status'] == 'INDEPENDENT_TWO_TRADE_REPLAY_PASS',
                known_detour=key(OUT/'known_detour.json'),scope='Bounded candidate-generation QA only. No AC scan of the new sample and no completion claim.')
    save(OUT/'qa.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs_sha256','independent_audit','other_seed_audit','native_negative_controls','audit_negative_controls')}))


if __name__ == '__main__':
    main()
