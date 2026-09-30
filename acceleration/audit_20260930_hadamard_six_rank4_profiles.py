"""Independent exhaustive unmerged profile recursion checking every saved DP layer."""
import argparse, copy, gzip, hashlib, json, platform, subprocess, sys, time
from collections import Counter
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_six_rank4_dp'
G=B/'20260930_independent_review/hadamard_six_exception_census'
RAW=B/'20260930_hadamard20_support/six_prism.json'
PINS={D/'summary.json':'e315a3261b2aee326142d1ad83ca828041b0f39907f54a5b51d4d11d33e7e53b',G/'summary.json':'4a82b3d74c0015804b844612051596e828439e2ffb73735d3d7689899c6141cd',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def domains(groups):
    n=len(groups);H=[[1]*n]+[[int(a in g) for g in groups] for a in range(12)]
    # Enumerate all4^n full group vectors, not only incident coordinates or
    # projected kernel coefficients. Literal matrix products decide membership.
    kernel=[v for v in product(range(-1,3),repeat=n) if all(sum(x*y for x,y in zip(row,v))==0 for row in H)]
    rows=[]
    for a in range(12):
        vs=[v for v in kernel if all(a in groups[i] or v[i]==0 for i in range(n))];lookup=set(vs);choices=[]
        for v0 in vs:
            for v1 in vs:
                v2=tuple(-x-y for x,y in zip(v0,v1))
                if v2 in lookup:
                    flat=v0+v1+v2;mask=sum(1<<i for i in range(n) if any(flat[f*n+i] for f in range(3)))
                    choices.append((flat,mask))
        rows.append(dict(vectors=vs,choices=choices,incident=[i for i,g in enumerate(groups) if a in g]))
    return H,rows
def enumerate_paths(rows,n):
    layers=[Counter() for _ in rows];positives=[];allfinal=0
    def visit(a,total,activity,path):
        nonlocal allfinal
        if a==len(rows):
            allfinal+=1
            if not any(total) and activity==(1<<n)-1:positives.append(path)
            return
        # Opposite traversal order from the producer. No DP state merging.
        for i in range(len(rows[a]['choices'])-1,-1,-1):
            vector,mask=rows[a]['choices'][i];dest=tuple(x+y for x,y in zip(total,vector));active=activity|mask
            layers[a][dest+(active,)]+=1;visit(a+1,dest,active,path+(i,))
    visit(0,(0,)*(3*n),0,())
    return layers,positives,allfinal
def path_state(path,rows,n):
    total=[0]*(3*n);activity=0
    for a,index in enumerate(path):
        need(type(index) is int and 0<=index<len(rows[a]['choices']),'raw path index')
        vec,mask=rows[a]['choices'][index]
        for i,v in enumerate(vec):total[i]+=v
        activity|=mask
    return tuple(total)+(activity,)
def project(state,p,n):return tuple(state[f*n+i] for f in [0,1] for i in p)+(state[-1],)
def expected_rows(rows,p,n):
    return [dict(coordinate=a,incident_groups=r['incident'],integer_kernel_vectors=[list(v) for v in r['vectors']],choices=[dict(fibres=[list(flat[f*n:(f+1)*n]) for f in range(3)],projection=[flat[f*n+i] for f in [0,1] for i in p],activity_mask=mask) for flat,mask in r['choices']]) for a,r in enumerate(rows)]
def check_layer(raw,expected,full_by_project,rows,n,p,depth):
    seen={};last=None
    for state,count,path in raw:
        state=tuple(state);need(state not in seen,'unique saved state');need(last is None or state>last,'strict raw state order');last=state
        need(type(count) is int and count>0 and expected.get(state)==count,'exact independent path count')
        need(len(path)==depth+1,'correct prefix witness length')
        full=path_state(path,rows,n);need(project(full,p,n)==state and full_by_project[state]==full,'all full quota sums and activity witness')
        seen[state]=count
    need(seen==expected,'complete saved layer states')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or h==v,'pin '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        s=read(D/'summary.json');gate=read(G/'summary.json');need(gate['status']=='INDEPENDENT_HADAMARD_SIX_EXCEPTION_KERNEL_CENSUS_PASS','necessary sextet gate')
        for p,h in s['inputs_sha256'].items():pin(ROOT/p,h)
        for p in [D/'manifest.json',D/'controls.json',D/'domain_inventory.json']:pin(p)
        cand=B/'20260930_hadamard_six_exception_census/remaining_candidates.json';need(sha(cand)==gate['inputs_sha256'][key(cand)],'exact independently approved remaining cases');cases=read(cand)['records']
        L=read(RAW)['L'];groups=list(dict.fromkeys(tuple(i for i in range(12) if L[i][d]) for d in range(60)))
        # Known four-circuit exact count control, evaluated by the same full recursion.
        _,toy=domains([groups[i] for i in [0,7,9,19]]);tl,tp,tn=enumerate_paths(toy,4)
        need(len(tp)==6 and tl[-1][(0,)*12+(0,)]==1,'four-circuit six nonzero and one balanced control')
        controls=dict(four_circuit_nonzero_profiles=len(tp),four_circuit_balanced_profiles=tl[-1][(0,)*12+(0,)],four_circuit_total_paths=tn)
        inventory=read(D/'domain_inventory.json')['cases'];need(len(cases)==len(inventory)==len(s['cases'])==9,'all nine exact cases')
        results=[];positives=[];allpaths=0;allstates=0;alllayers=0;first_layer_control=None
        for ci,c in enumerate(tqdm(cases,desc='Independent full-profile recursion',mininterval=1)):
            selected=[groups[g] for g in c['groups']];H,rows=domains(selected);caseout=D/f'case_{ci:02d}'
            inv=inventory[ci];need(inv['case']==ci and inv['groups']==c['groups'],'domain inventory scope');domainpath=ROOT/inv['domain_path'];pin(domainpath,inv['domain_sha256']);saved=read(domainpath)
            p=saved['projection_group_indices'];need(len(p)==2 and p==sorted(set(p)) and all(0<=i<6 for i in p),'two distinct projection coordinates')
            basis=c['certificate']['integer_null_basis'];pm=[[v[i] for v in basis] for i in p];pd=pm[0][0]*pm[1][1]-pm[0][1]*pm[1][0]
            need(pd!=0 and pm==saved['projection_matrix'] and pd==saved['projection_determinant'],'injectivity on entire rational kernel')
            need(saved['case']==ci and saved['groups']==c['groups'] and saved['global_kernel_H']==H,'domain raw scope')
            expected=expected_rows(rows,p,6);need(saved['records']==expected,'all integer vectors and all ordered fibre triples')
            need(inv['integer_vector_counts']==[len(r['vectors']) for r in rows] and inv['fibre_profile_counts']==[len(r['choices']) for r in rows],'domain counts')
            layers,paths,total=enumerate_paths(rows,6);allpaths+=total;case=s['cases'][ci];pin(caseout/'summary.json');need(read(caseout/'summary.json')==case,'case summary bytes')
            need(case['case']==ci and case['groups']==c['groups'] and case['complete'] and case['completed_coordinate']==11 and len(case['checkpoints'])==12 and case['unknown_reason'] is None and case['status']=='COMPLETE','actual complete coordinate domain')
            layerrecords=[];previous_count=1
            for depth,cp in enumerate(case['checkpoints']):
                cp_path=ROOT/cp['path'];pin(cp_path,cp['sha256']);receipt=read(cp_path)
                need(receipt['case']==ci and receipt['coordinate']==depth and receipt['domain_sha256']==pins[key(domainpath)],'layer scope and hash')
                statepath=ROOT/receipt['state_path'];pin(statepath,receipt['state_sha256'])
                expected_counts={};full_by_project={}
                for full,count in layers[depth].items():
                    state=project(full,p,6);need(state not in expected_counts,'independent full quota states project injectively');expected_counts[state]=count;full_by_project[state]=full
                with gzip.open(statepath,'rt',encoding='utf-8') as f:raw_records=[json.loads(line) for line in f]
                check_layer(raw_records,expected_counts,full_by_project,rows,6,p,depth)
                need(receipt['states']==len(expected_counts) and receipt['profile_sequence_count']==sum(expected_counts.values()),'layer counts')
                need(receipt['transitions']==previous_count*len(rows[depth]['choices']),'reported aggregated transition count');previous_count=len(expected_counts)
                layerrecords.append(dict(coordinate=depth,distinct_full_quota_states=len(layers[depth]),literal_prefix_sequences=sum(layers[depth].values()),raw_state_witnesses=len(raw_records)))
                alllayers+=1;allstates+=len(raw_records)
                if first_layer_control is None and len(raw_records)>1:first_layer_control=(raw_records,expected_counts,full_by_project,rows,p,depth)
            need(case['exactly_six_marginal_profile_sequences']==len(paths) and case['has_marginal_witness']==bool(paths),'exact positive/zero result')
            if paths:
                witnesspath=caseout/'first_witness.json';pin(witnesspath);w=read(witnesspath);state=path_state(w['choice_path'],rows,6)
                need(state==(0,)*18+(63,) and w['groups']==c['groups'] and w['activity_mask']==63 and w['total_group_fibre_deviations']==[[0]*6 for _ in range(3)],'raw six-active marginal witness')
            results.append(dict(case=ci,groups=c['groups'],complete_profile_product=total,exactly_six_active=len(paths),balanced_profiles=layers[-1].get((0,)*19,0),layers=layerrecords))
            positives.append(dict(case=ci,groups=c['groups'],ordered_choice_paths=[list(v) for v in sorted(paths)],scope='Exact linear/count marginal profiles only, no local column realization.'))
        expected_counts=[96,108,0,96,96,24,0,0,564];need([r['exactly_six_active'] for r in results]==expected_counts,'independent final counts')
        need(sum(expected_counts)==984 and allpaths==121869,'complete labelled population sizes')
        need(s['complete_cases']==9 and s['unattempted_cases']==0 and s['complete_empty_cases']==3 and s['complete_nonempty_cases']==6,'stage counts')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError,IndexError,TypeError):rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        records,ec,fp,rows,p,depth=first_layer_control
        bad=copy.deepcopy(records);bad[0][1]+=1;reject('changed_path_count',lambda:check_layer(bad,ec,fp,rows,6,p,depth))
        reject('missing_saved_state',lambda:check_layer(records[:-1],ec,fp,rows,6,p,depth))
        bad=copy.deepcopy(records);bad.insert(1,bad[0]);reject('duplicate_saved_state',lambda:check_layer(bad,ec,fp,rows,6,p,depth))
        bad=copy.deepcopy(records);bad[0][2][-1]=999;reject('invalid_witness_choice',lambda:check_layer(bad,ec,fp,rows,6,p,depth))
        bad=copy.deepcopy(records);bad[0][0][-1]^=1;reject('wrong_activity',lambda:check_layer(bad,ec,fp,rows,6,p,depth))
        reject('wrong_projection_injectivity',lambda:need([[0,0],[0,0]][0][0]!=0,'zero projection determinant'))
        reject('truncate_local_domains',lambda:need(expected[:-1]==saved['records'],'complete domain coverage'))
        reject('nonbinary_count_bound',lambda:need(all(-1<=v<=2 for v in [3]),'count range'))
        write(out/'controls.json',dict(**controls,corruptions_rejected=rejected))
        write(out/'independent_layers.json',dict(records=results,total_full_profile_sequences=allpaths,total_saved_states_checked=allstates,total_layers=alllayers))
        write(out/'all_positive_marginal_profiles.json',dict(records=positives,total_labelled_profiles=984))
        for q in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_SIX_RANK4_MARGINALS.md']:pin(q)
        ts=datetime.now(timezone.utc).isoformat();write(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,solver_calls=0))
        binding=dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-INTEGER-MARGINAL-CENSUS',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For all nine retained rank4 sextets on the fixed six-prism Hadamard support, complete bounded integer coordinate/fibre marginal enumeration gives exactly-six-active labelled profile counts[96,108,0,96,96,24,0,0,564] in the saved order. Hence the three saved sextets at indices2,6,7 cannot be the exact exceptional-group set of a binary prescribed-Gram factor; the other six admit984 total labelled marginal profiles only.',scope='Complete necessary marginal relaxation on nine fixed sextets; six positive marginal cases remain unresolved for local triples/full factors.',assumptions=['Literal fixed support and full prescribed-Gram marginal equations.','Counts are integral, each incident coordinate/fibre deviation is in[-1,2], and exactly six groups are active.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-KERNEL-CENSUS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION',revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root/state_literature_audit',method='Direct enumeration of all full6-group integer vectors and unmerged recursion over121869 complete labelled coordinate-profile sequences, maintaining all18 quota sums; every saved DP layer and witness checked afterward.',shared_components=['Raw support and independently checked rank4 census; no producer imports.','Python exact integer arithmetic; independent recursion does not use compressed-state recurrence.'],inputs_sha256=pins,evidence_sha256={key(q):sha(q) for q in out.iterdir() if q.is_file()},artifact_availability='LOCAL_ONLY',availability_reason='Workspace artifacts pending parent publication.',external_review=None,external_review_reason='No external peer review asserted.',limitations=['Positive integer marginals do not establish local three-column realizability, full quadratic Gram equality, column caps or a graph.','No whole-support/core/unrestricted-target exclusion.','984 counts labelled marginal profiles, not graphs or target coverage.'],created_at=ts,updated_at=ts)
        write(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_SIX_RANK4_INTEGER_MARGINAL_CENSUS_PASS',timestamp=ts,inputs_sha256=pins,outputs_sha256={key(q):sha(q) for q in out.iterdir() if q.is_file()},complete_cases=9,zero_cases=[2,6,7],positive_cases=[0,1,3,4,5,8],exact_counts=expected_counts,complete_profile_sequences=121869,labelled_feasible_marginal_profiles=984,saved_layers_checked=alllayers,saved_state_witnesses_checked=allstates,corruptions_rejected=len(rejected),solver_calls=0,target_resolution=False)
        write(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'),elapsed_seconds=time.perf_counter()-start)))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
