"""Independent raw-support and binary-strip proof of six necessary count cuts."""
from pathlib import Path
from itertools import product
from datetime import datetime, timezone
import argparse, copy, hashlib, json, platform, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'; I=B+'independent_review/'; D=B+'second_count_partial_cut/'
RAW=B+'hadamard20_support/six_prism.json'; MASTER=B+'hadamard_count_master_cnf/model.json'
PROFILE=I+'count_master_eight_orbit_cut_sat_outcome/independent_count_profile.json'
ASSIGN=B+'count_master_eight_orbit_cut_native_pilot/main/parsed_model.json'
FIXTURE=B+'srg243_residual_fixture/triangle_blocks.json'
PINS={D+'summary.json':'75b3fe176b749a24778921253f8ac842d13b05c239f41c50e9b715443a50a0a0',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',MASTER:'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',PROFILE:'7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0',ASSIGN:'40174793158d22cb17a0fff711102e9f3053ab04c9b23ba632d94c2976727189',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',I+'hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888'}

def need(b,m):
    if not b: raise ValueError(m)
def sha(p):
    with (ROOT/p).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def read(p): return json.loads((ROOT/p).read_bytes())
def save(p,o):
    with p.open('x',encoding='utf8',newline='\n') as f: json.dump(o,f,indent=2); f.write('\n')
def gram(C,i,j,n):
    return n*(i==j)-C[i][j]-sum(C[i][k]*C[k][j] for k in range(len(C)))+2-int(i//n==j//n)
def check_instance(rec, f, h, support, C, channels, counts):
    groups=[g for g,s in enumerate(support) if 9 in s and 11 in s]
    need(groups==[1,5,8,18,19], 'all contributors')
    restrictions=[(1,11,h,0),(5,9,f,0),(8,9,f,1),(18,11,h,0),(19,9,f,0)]
    need(rec['coordinates']==[9,11] and rec['fibres']==[f,h], 'literal row identities')
    need(rec['target']==gram(C,12*f+9,12*h+11,12)==2, 'literal target')
    need(rec['groups']==groups and rec['partial_upper']==1 and rec['symmetry_premise_used'] is False, 'scope')
    terms=rec['partial_restrictions']; need(len(terms)==5,'five bounds')
    expected=[]
    for term,(g,c,k,b) in zip(terms,restrictions,strict=True):
        channel=channels[c,g]; values=channel['values']; ids=channel['variables']
        selected=ids[values.index(counts[c][g])]
        escape=[v for v,x in zip(ids,values,strict=True) if x[k]>b]
        exact=dict(group=g,coordinate=c,fibre=k,upper_bound=b,current_count_vector=counts[c][g],current_selected_variable=selected,channel_values=values,channel_variables=ids,escaping_variables=escape)
        need(term==exact,'term exact channel and threshold'); expected+=escape
    need(rec['clause']==expected and len(expected)==25 and len(set(expected))==25,'exact positive escape clause')
    return restrictions,expected

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
    out=args.out.resolve(); out.mkdir(parents=True,exist_ok=False); began=time.monotonic(); pins={}
    def pin(p,h=None):
        digest=sha(p); need(h is None or digest==h,'frozen artifact '+str(p)); pins[str(p)]=digest
    try:
        for p,h in PINS.items(): pin(p,h)
        summary=read(D+'summary.json')
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in summary[field].items(): pin(p,h)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_SECOND_COUNT_PARTIAL_CUT.md','uv.lock','pyproject.toml']: pin(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,solver_calls=0,limits_seconds=120))
        raw=read(RAW); C=raw['core_adjacency']; supports=raw['support_columns']; groups=[]
        for s in supports:
            if s not in groups: groups.append(s)
        need(len(groups)==20 and len(supports)==60,'literal support population')
        need(all([j for j,s in enumerate(supports) if s==g]==[i,i+20,i+40] for i,g in enumerate(groups)), 'three copies each')
        need(all(raw['prescribed_Gram36'][i][j]==gram(C,i,j,12) for i in range(36) for j in range(36)), 'all1296 prescribed entries')
        counts=read(PROFILE)['coordinate_group_fibre_counts']; master=read(MASTER)
        channels={(c['coordinate'],c['group']):c for c in master['count_channels']}
        records=read(D+'ordered_fibre_instances.json')['records']; expected_pairs=[(f,h) for f in range(3) for h in range(3) if f!=h]
        need(len(records)==6,'six separate row pairs'); allclauses=[]; truth_records=[]
        bits=list(product([0,1],repeat=3)); strip_pairs=list(product(bits,repeat=2))
        need(len(strip_pairs)==64 and all(sum(a*b for a,b in zip(x,y))<=min(sum(x),sum(y)) for x,y in strip_pairs),'all64 universal bounds')
        maxima={(u,v):max(sum(a*b for a,b in zip(x,y)) for x,y in strip_pairs if sum(x)==u and sum(y)==v) for u in range(4) for v in range(4)}
        need(all(value==min(k) for k,value in maxima.items()),'all16 attainable maxima')
        for rec,(f,h) in zip(records,expected_pairs,strict=True):
            restrictions,clause=check_instance(rec,f,h,groups,C,channels,counts); allclauses.append(clause)
            domain=[channels[c,g] for g,c,k,b in restrictions]; cases=excluded=0
            localmax=[]
            for g,c,k,b in restrictions:
                vals=[sum(a*z for a,z in zip(x,y)) for x,y in strip_pairs if sum(x if c==9 else y)<=b]
                localmax.append(max(vals))
            need(localmax==[0,0,1,0,0] and sum(localmax)<2,'independent strip maxima')
            for selected in product(*[range(len(ch['values'])) for ch in domain]):
                truevars={ch['variables'][q] for ch,q in zip(domain,selected)}
                actual=bool(truevars.intersection(clause))
                upper=[ch['values'][q][term[2]] for ch,q,term in zip(domain,selected,restrictions)]
                expected=any(u>term[3] for u,term in zip(upper,restrictions))
                need(actual==expected,'complete channel truth equivalence')
                if not actual: need(sum(upper)<=1,'every forbidden region impossible'); excluded+=1
                cases+=1
            need(cases==49000 and excluded==640,'complete local choices'); truth_records.append(dict(fibres=[f,h],cases=cases,excluded_local_choices=excluded,strip_maxima=localmax))
        expected_bytes=''.join(' '.join(map(str,c))+' 0\n' for c in allclauses).encode('ascii')
        need((ROOT/D/'universal_six_bound_cuts.cnfpart').read_bytes()==expected_bytes,'all literal clause bytes')
        cert=read(D+'certificate.json'); original=records[expected_pairs.index((2,1))]
        need(cert['partial_restrictions']==original['partial_restrictions'] and cert['scalar_bound_escape_clause']==original['clause'],'original certificate subset')
        need(cert['cooccurring_columns']==[d for d,s in enumerate(supports) if 9 in s and 11 in s],'all15 contributing columns')
        need(not any(cert[k] for k in ['uses_local_within_caps','uses_cross_group_caps','uses_residual_D','uses_global_countmaster_feasibility']),'no extra inequality premise')
        assignment=read(ASSIGN)['assignment']; need(len(assignment)==155939 and all(type(x)is int and x!=0 for x in assignment) and {abs(x) for x in assignment}==set(range(1,155940)),'complete saved assignment')
        truevars={x for x in assignment if x>0}; failed=[]
        for rec in records:
            value=bool(truevars.intersection(rec['clause'])); need(value==rec['current_witness_satisfies_clause'],'actual witness predicate')
            if not value: failed.append(rec['fibres'])
        need(failed==[[2,1]],'only original pair falsifies old witness')
        controls=[]
        def reject(name,fn):
            try: fn()
            except (ValueError,KeyError,IndexError,TypeError): controls.append(name)
            else: raise ValueError('accepted corruption '+name)
        for key,value in [('target',1),('groups',[1,5,8,18]),('partial_upper',2),('coordinates',[8,11]),('fibres',[2,0]),('symmetry_premise_used',True)]:
            bad=copy.deepcopy(original); bad[key]=value; reject(key,lambda bad=bad:check_instance(bad,2,1,groups,C,channels,counts))
        for key in ['group','coordinate','fibre','upper_bound','current_selected_variable']:
            bad=copy.deepcopy(original); bad['partial_restrictions'][0][key]+=1; reject('term_'+key,lambda bad=bad:check_instance(bad,2,1,groups,C,channels,counts))
        for label,clause in [('remove',original['clause'][:-1]),('negate',[-original['clause'][0],*original['clause'][1:]])]:
            bad=copy.deepcopy(original);bad['clause']=clause;reject(label,lambda bad=bad:check_instance(bad,2,1,groups,C,channels,counts))
        omitted=[]
        for omit in range(5):
            local=[]
            for j,term in enumerate([(1,11,1,0),(5,9,2,0),(8,9,2,1),(18,11,1,0),(19,9,2,0)]):
                bound=3 if j==omit else term[3]
                local.append(max(sum(a*b for a,b in zip(x,y)) for x,y in strip_pairs if sum(x if term[1]==9 else y)<=bound))
            need(sum(local)>=2,'omitted bound admits local target'); omitted.append(dict(omitted=omit,local_maxima=local))
        fixture=read(FIXTURE); FC=fixture['cubic_core60']; F=fixture['factor60x180']
        def genuine(factor):
            need(len(factor)==60 and all(len(r)==180 and all(type(x)is int and x in(0,1) for x in r) for r in factor),'genuine shape/binary')
            need(all(sum(factor[i][d]*factor[j][d] for d in range(180))==gram(FC,i,j,20) for i in range(60) for j in range(60)),'genuine integer Gram')
        genuine(F); bad=copy.deepcopy(F);bad[0][0]^=1;reject('genuine_bit',lambda:genuine(bad))
        need(time.monotonic()-began<120,'audit resource limit')
        save(out/'controls.json',dict(rejected=controls,genuine243_positive=True,binary_strip_cases=64,exact_maxima=[dict(counts=list(k),maximum=v) for k,v in maxima.items()],removed_bound_local_controls=omitted,full_research_factor_positive_available=False))
        save(out/'independent_instances.json',dict(records=truth_records,clauses=allclauses,failed_old_witness_pairs=failed))
        stamp=datetime.now(timezone.utc).isoformat(); cid='C-FIXED-HADAMARD-SIX-PARTIAL-SCALAR-COUNT-CUTS'
        binding=dict(id=cid,revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='Every binary factor on the literal twenty-support six-prism geometry with the prescribed Gram matrix satisfies the six recorded 25-literal count-channel escape clauses. Each clause excludes the five specified bounds on coordinates9,11 for one ordered pair of distinct fibres: their total possible intersection is at most1 although the required entry is2.',scope='Only six literal necessary conditions on this fixed support; a clause excludes a region of count profiles, not all factors. Exact-one count-channel interpretation is a premise for the CNF literals.',assumptions=['Fixed raw support and prescribed integer Gram matrix.','Existing independently checked exactly-one count-channel interpretation; no local-cap or automorphism premise for the overlap bound.'],dependencies=[dict(id='C-FIXED-HADAMARD-COUNT-MASTER-SIX-PROFILE-CUT-ENCODING',revision=1,relation='encoding_equivalence')],verifier='/root',producer='/root/eight_domain_audit',method='Independent raw matrix/support derivation, exhaustive binary strip and channel truth checks, literal suffix reconstruction and adversarial controls.',shared_components=['Only raw source artifacts and Python standard library; no producer imports.','Count-channel meanings are pinned to the earlier independently checked base encoding.'],inputs_sha256=pins,limitations=['No full factor or target graph.','No unrestricted support/core coverage.','49,000 choices per clause are local channel products, not global count-CSP solutions.','No full factor positive fixture is known; positive graph fixture is the separate243 example.'],created_at=stamp,updated_at=stamp)
        save(out/'claim_binding.json',binding)
        report=dict(status='INDEPENDENT_SECOND_COUNT_PARTIAL_SCALAR_CUTS_PASS',timestamp=stamp,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in out.iterdir() if p.is_file()},clauses=6,local_channel_cases=sum(r['cases'] for r in truth_records),solver_calls=0,controls_rejected=len(controls),elapsed_seconds=time.monotonic()-began,shared_components=binding['shared_components'],limitations=binding['limitations'])
        save(out/'summary.json',report); print(json.dumps(dict(status=report['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT)),binding_sha256=sha((out/'claim_binding.json').relative_to(ROOT)))))
    except BaseException as e:
        save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__).relative_to(ROOT)),elapsed_seconds=time.monotonic()-began));raise
if __name__=='__main__': main()
