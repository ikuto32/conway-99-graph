"""Fresh exact count-object and native receipt audit; no repository imports."""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import argparse, copy, hashlib, json, platform, re, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
R=B+'count_master_partial_cuts_native_pilot/'
D=B+'count_master_scalar_cuts/'
BASE=B+'hadamard_count_master_cnf/'
OLD=B+'count_master_eight_orbit_cuts/'
EG=B+'independent_review/count_master_partial_cut_cnf/summary.json'
CG=B+'independent_review/count_master_partial_cut_object_calibration/summary.json'
EH='dc1ada9d87d41b5cc6597cd0ff7ce2ed0a06981d8b487dbb797505240f435460'
CH='e381395d2fd8e23e63c3698e44c925390b42faaa2dc55d5960a7338b5fefebbd'
RUN_SHA='0fc8e5e57e9c29886d0e0092aab8f91d94406bca57cd4f2f0d55e2c32a660777'
CHILD_SHA='011b780e141c01c620c1bfc14bf1d6f4c9f1419b873156a93e321af97bbf6464'
CNF=D+'instance.cnf';N=155939;M=705845
RAW=B+'hadamard20_support/six_prism.json'
LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
SPEC='acceleration/audit_20260930_count_master_partial_cut_sat_outcome_spec.md'
CID='C-FIXED-HADAMARD-PARTIAL-CUT-COUNT-CSP-WITNESS'
LIMITS=dict(native_wall_seconds=60,conflicts=1000000,address_space_bytes=4294967296,
    trace_file_bytes=10737418240,kill_grace_seconds=5,outer_guard_seconds=70,
    maximum_research_calls=1,automatic_retry=False,host_reserve_bytes=22548578304,
    ext4_reserve_bytes=11811160064)


def need(ok,label):
    if not ok:raise ValueError(label)
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):
    p=Path(p);return(p if p.is_absolute()else ROOT/p).resolve().relative_to(ROOT).as_posix()
def save(p,v):
    with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def linux(p):
    p=str((ROOT/p).resolve()).replace('\\','/');return '/mnt/'+p[0].lower()+p[2:]


def signed(literals,n):
    need(type(literals)is list and len(literals)==n,'complete signed assignment length')
    v=[None]*(n+1)
    for x in literals:
        need(type(x)is int and 0<abs(x)<=n and v[abs(x)]is None,'unique strictly integer nonzero ID')
        v[abs(x)]=x>0
    need(all(type(x)is bool for x in v[1:]),'every variable assigned')
    return v


def parse_native(text,n):
    statuses=[];literals=[];end=False
    for line in text.splitlines():
        t=line.split()
        if not t or t[0]=='c':continue
        if t[0]=='s':
            need(t==['s','SATISFIABLE'],'native SAT grammar');statuses.append(t[1]);continue
        need(t[0]=='v'and len(t)>1,'native model line grammar')
        for token in t[1:]:
            need(not end,'no model data after final zero')
            if token=='0':end=True
            else:
                need(re.fullmatch(r'-?[1-9][0-9]*',token)is not None,'strict native literal token')
                literals.append(int(token))
    need(statuses==['SATISFIABLE']and end,'exactly one SAT status and terminated model')
    return signed(literals,n)


def truth(clause,v):return any(v[abs(x)]==(x>0)for x in clause)
def clauses(path,v,expected):
    total=0;n=len(v)-1
    with Path(path).open('rb')as stream:
        need(stream.readline()==f'p cnf {n} {expected}\n'.encode(),'exact raw CNF header')
        for line in stream:
            t=line.split();need(t and t[-1]==b'0','one terminated raw clause per line')
            need(all(re.fullmatch(rb'-?[1-9][0-9]*',x)is not None for x in t[:-1]),'strict raw CNF literals')
            row=list(map(int,t[:-1]));need(all(abs(x)<=n for x in row),'raw clause ID bound')
            need(truth(row,v),f'actual clause {total+1} satisfied');total+=1
    need(total==expected,'complete raw clause population');return total


def catalogue(local):
    mapping=defaultdict(list)
    for rank,choice in enumerate(local['survivors']):
        need(len(choice)==3 and len(set(choice))==3,'three distinct catalogue words')
        words=[local['words'][i]for i in choice]
        need(all(len(w)==6 and sorted(w)==[0,0,1,1,2,2]for w in words),'two entries per fibre')
        need(all(sum(a==b for a,b in zip(words[i],words[j]))<=2 for i in range(3)for j in range(i)),'literal within-group caps')
        signature=tuple(sum(w[pos]==f for w in words)for pos in range(6)for f in range(3))
        mapping[signature].append(rank)
    need(len(local['survivors'])==31110 and len(mapping)==6061,'frozen catalogue populations')
    return mapping


def margins(counts,groups):
    need(len(counts)==12,'twelve coordinates')
    for a,table in enumerate(counts):
        need(len(table)==20,'twenty groups')
        for g,cell in enumerate(table):
            need(len(cell)==3 and all(type(x)is int and 0<=x<=3 for x in cell),'strict bounded counts')
            need(sum(cell)==3*int(a in groups[g]),'support and coordinate quota')
        for f in range(3):
            deviations=[table[g][f]-int(a in groups[g])for g in range(20)]
            need(sum(deviations)==0,'coordinate total fibre quota')
            for b in range(12):need(sum(deviations[g]for g in range(20)if b in groups[g])==0,'every literal support-incidence marginal')
    for g,support in enumerate(groups):
        for f in range(3):need(sum(counts[a][g][f]for a in support)==6,'group fibre quota')


def unique(ids,v):
    selected=[(j,x)for j,x in enumerate(ids)if v[x]];need(len(selected)==1,'one literal selected option');return selected[0]


def decode(model,v,raw,mapping,minimum=7):
    groups=[]
    for d in range(60):
        support=[a for a in range(12)if raw['L'][a][d]]
        if support not in groups:groups.append(support)
    need(groups==model['groups']and len(groups)==20,'groups rederived from literal L columns')
    counts=[[[0]*3 for _ in range(20)]for _ in range(12)];gs=[];sids=[];witnesses=[]
    for g,domain in enumerate(model['group_domains']):
        need(domain['group']==g and domain['support']==groups[g],'ordered group map')
        i,selector=unique(domain['selectors'],v);sid=domain['signature_indices'][i]
        signature=model['local_signatures'][sid];flat=signature['counts'];ranks=mapping[tuple(flat)]
        need(signature['index']==sid and ranks==signature['local_survivor_indices']and len(ranks)==signature['count'],'actual selected signature class and every local witness')
        for pos,a in enumerate(groups[g]):counts[a][g]=flat[3*pos:3*pos+3]
        gs.append(selector);sids.append(sid);witnesses.append(ranks)
    margins(counts,groups)
    cs=[]
    for a,domain in enumerate(model['coordinate_domains']):
        need(domain['coordinate']==a,'coordinate order');i,selector=unique(domain['selectors'],v)
        need(domain['count_tables'][i]==counts[a],'independently reconstructed counts equal coordinate choice');cs.append(selector)
    for channel in model['count_channels']:
        i,_=unique(channel['variables'],v)
        need(channel['values'][i]==counts[channel['coordinate']][channel['group']],'raw count/channel equality')
    exc=[g for g,s in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in s)]
    need(len(exc)>=minimum,'required exception bound')
    deviations=[[[counts[a][g][f]-int(a in groups[g])for g in exc]for f in range(3)]for a in range(12)]
    digest=hashlib.sha256(json.dumps(dict(groups=exc,deviations=deviations),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(variant='at_least_seven'if minimum else'baseline',selected_coordinate_selector_ids=cs,
        selected_group_selector_ids=gs,selected_global_signature_indices=sids,
        coordinate_group_fibre_counts=counts,exceptional_groups=exc,exception_count=len(exc),
        coordinate_fibre_deviations=deviations,profile_sha256=digest,
        local_survivor_indices_by_group=witnesses,full_factor=False,target_graph=False,
        residual_D=None,all_cross_group_column_caps_checked=False)


def cuts(profile,v,excluded,scalar):
    counts=profile['coordinate_group_fibre_counts'];old=[];fresh=[]
    for record in excluded:
        differs=counts!=record['coordinate_group_fibre_counts']
        need(differs==truth(record['clause'],v),'whole-profile cut means literal table differs');old.append(differs)
    for record in scalar:
        escape=any(counts[q['coordinate']][q['group']][q['fibre']]>q['upper_bound']for q in record['partial_restrictions'])
        need(escape==truth(record['clause'],v),'scalar clause equals some raw count escaping bounds');fresh.append(escape)
    need(len(old)==len(fresh)==6 and all(old+fresh),'all six old and six new cuts satisfied')
    return dict(old_profile_cuts=old,scalar_cuts=fresh)


def envelopes(profile,raw,groups):
    C=raw['core_adjacency'];G=[[12*int(i==j)-C[i][j]+2-int(i//12==j//12)-sum(C[i][k]*C[k][j]for k in range(36))for j in range(36)]for i in range(36)]
    need(G==raw['prescribed_Gram36'],'Gram target independently reconstructed from core')
    count=profile['coordinate_group_fibre_counts'];records=[]
    for a in range(12):
        for b in range(a+1,12):
            common=[g for g,s in enumerate(groups)if a in s and b in s]
            if not common:continue
            need(len(common)==5,'five contributions per nonmatching coordinate pair')
            for f in range(3):
                for h in range(3):
                    upper=sum(min(count[a][g][f],count[b][g][h])for g in common);target=G[12*f+a][12*h+b]
                    records.append(dict(coordinates=[a,b],fibres=[f,h],upper=upper,target=target,passes=upper>=target))
    need(len(records)==540,'all scalar envelope diagnostics')
    return dict(records=records,failed=[r for r in records if not r['passes']],full_Gram_realization=False)


def receipt(run,text,workspace):
    r=run['receipt'];need(r['actual_exit_code']==10 and not r['outer_windows_guard_expired']and r['outer_windows_guard_seconds']==70,'actual native SAT and bounded return')
    expected=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/timeout','--signal=TERM','--kill-after=5s','60s','/usr/bin/prlimit','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0',linux('build/research-cadical195/source/build/cadical'),'--no-binary','-c','1000000',linux(CNF),workspace+'/proof.drat']
    need(r['command']==expected,'exact authenticated solver/input/resources/output command')
    need(run['research_calls']==1 and run['automatic_retry']is False and run['interpreted_result']=='SAT_RAW_UNCHECKED','honest single-run interpretation')
    need([x for x in text.splitlines()if x.startswith('s ')]==['s SATISFIABLE'],'single SAT status')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e'in text and '\nc exit 10\n'in text,'saved solver version and exit')
    def one(pattern):
        found=re.findall(pattern,text,re.M);need(len(found)==1,'one complete native statistic');return found[0]
    stats=dict(conflicts=int(one(r'^c conflicts:\s+(\d+)\s')),cpu_seconds=float(one(r'^c total process time since initialization:\s+([\d.]+)\s+seconds')),
        native_wall_seconds=float(one(r'^c total real time since initialization:\s+([\d.]+)\s+seconds')),
        native_max_rss_mb=float(one(r'^c maximum resident set size of process:\s+([\d.]+)\s+MB')),wrapped_wall_seconds=r['wall_seconds'])
    need(stats['conflicts']<LIMITS['conflicts']and stats['native_wall_seconds']<60 and r['wall_seconds']<70,'observed SAT before budgets')
    return stats


def calibrate(out,model,raw,mapping,actual,v,run,text,workspace):
    rejected=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):rejected.append(label);return
        raise ValueError('corruption accepted '+label)
    need(parse_native('c synthetic\ns SATISFIABLE\nv 1 -2 0\n',2)==[None,True,False],'tiny codec positive')
    for name,a in [('missing',[1]),('duplicate',[1,1]),('zero',[1,0]),('range',[1,3]),('boolean',[1,True])]:reject('signed_'+name,lambda a=a:signed(a,2))
    for name,s in [('status','s UNSATISFIABLE\nv 1 -2 0\n'),('missing','s SATISFIABLE\nv 1 0\n'),('repeat','s SATISFIABLE\nv 1 1 0\n'),('tail','s SATISFIABLE\nv 1 0 -2\n'),('unfinished','s SATISFIABLE\nv 1 -2\n'),('token','s SATISFIABLE\nv 1 true 0\n')]:reject('native_'+name,lambda s=s:parse_native(s,2))
    tiny=out/'tiny.cnf';tiny.write_bytes(b'p cnf 2 2\n1 0\n-2 0\n');clauses(tiny,[None,True,False],2)
    for name,data in [('header',b'p cnf 3 2\n1 0\n-2 0\n'),('missing',b'p cnf 2 2\n1 0\n'),('false',b'p cnf 2 2\n-1 0\n-2 0\n'),('range',b'p cnf 2 2\n1 0\n3 0\n'),('unterminated',b'p cnf 2 2\n1 0\n-2\n')]:
        p=out/('bad_'+name+'.cnf');p.write_bytes(data);reject('cnf_'+name,lambda p=p:clauses(p,[None,True,False],2))
    positives=[]
    for label in ['all_balanced_counts','rank4_00_profile_0000']:
        path=BASE+label+'_assignment.json';a=read(path)['assignment'];q=signed(a,155750)
        clauses(ROOT/(BASE+'baseline.cnf'),q,704454);result=decode(model,q,raw,mapping,0)
        positives.append(dict(path=path,sha256=sha(ROOT/path),exception_count=result['exception_count'],clauses=704454))
    need(sorted(p['exception_count']for p in positives)==[0,6],'independent authentic baseline positives')
    for label,id_ in [('coordinate',actual['selected_coordinate_selector_ids'][0]),('group',actual['selected_group_selector_ids'][0]),('channel',model['count_channels'][0]['variables'][0]),('prefix',model['one_hot_domains'][0]['prefix_variables'][0])]:
        q=v.copy();q[id_]=not q[id_];reject('full_assignment_'+label,lambda q=q:clauses(ROOT/CNF,q,M))
    for label in ['count','deviation','digest','exception_count','factor']:
        q=copy.deepcopy(actual)
        if label=='count':q['coordinate_group_fibre_counts'][0][0][0]+=1
        elif label=='deviation':q['coordinate_fibre_deviations'][0][0][0]+=1
        elif label=='digest':q['profile_sha256']='0'*64
        elif label=='exception_count':q['exception_count']+=1
        else:q['full_factor']=True
        reject('raw_'+label,lambda q=q:need(q==actual,'exact independently reconstructed profile'))
    q=copy.deepcopy(actual['coordinate_group_fibre_counts']);q[0][0][0]+=1;q[0][0][1]-=1
    reject('direct_marginal_corruption',lambda:margins(q,model['groups']))
    for label in ['exit','guard','wall','conflicts','input','binary','research_count','status']:
        q=copy.deepcopy(run);t=text
        if label=='exit':q['receipt']['actual_exit_code']=20
        elif label=='guard':q['receipt']['outer_windows_guard_expired']=True
        elif label=='wall':q['receipt']['command'][7]='600s'
        elif label=='conflicts':q['receipt']['command'][15]='100'
        elif label=='input':q['receipt']['command'][16]='wrong.cnf'
        elif label=='binary':q['receipt']['command'][12]='wrong_solver'
        elif label=='research_count':q['research_calls']=2
        else:t=t.replace('s SATISFIABLE','s UNSATISFIABLE')
        reject('receipt_'+label,lambda q=q,t=t:receipt(q,t,workspace))
    return dict(status='FRESH_COUNT_OBJECT_AND_RECEIPT_CONTROLS_PASS',rejected=rejected,positive_baseline_count_objects=positives,
        tiny_native_and_CNF_positive=True,actual_strengthened_assignment_positive=True,full_factor_positive=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,h=None):
        p=key(p)
        if p not in pins:pins[p]=sha(ROOT/p)
        need(h is None or pins[p]==h,'immutable identity '+p);return p
    def streams(rec):
        for s in ['stdout','stderr']:pin(rec[s],rec[s+'_sha256'])
    try:
        pin(R+'summary.json',RUN_SHA);pin(R+'independent_object/summary.json',CHILD_SHA)
        pin(EG,EH);pin(CG,CH)
        run=read(R+'summary.json');child=read(R+'independent_object/summary.json')
        need(read(EG)['status']=='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_CNF_PASS','independent encoding premise')
        need(read(CG)['status']=='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_OBJECT_CALIBRATION_PASS','frozen calibration premise')
        for report in [read(EG),read(CG),run,child]:
            for p,h in {**report.get('inputs_sha256',{}),**report.get('outputs_sha256',{})}.items():pin(p,h)
        for p in [__file__,SPEC,'uv.lock','pyproject.toml','CLAIMS.yaml']:pin(p)
        need(read(R+'manifest.json')['limits']==LIMITS and read(R+'manifest.json')['mode']=='RESEARCH','exact declared native limits')
        workspace=read(R+'workspace.json');w=workspace['path']
        need(w.startswith('/tmp/conway99-count-partial-cuts-')and '\n'not in w and workspace['creation_observed']is True and workspace['future_availability']=='UNKNOWN','honest workspace observation')
        text=(ROOT/(R+'main/solver.stdout.log')).read_text(encoding='ascii');stats=receipt(run,text,w)
        need(read(R+'main/solver.receipt.json')==run['receipt'],'same actual return receipt');streams(run['receipt'])
        launch=read(R+'main/launch.json');need(launch['command']==run['receipt']['command']and launch['cnf_sha256']==pin_digest(CNF,pins),'same exact launch input')
        transfer=run['proof_copy'];pin(R+'main/proof.drat',transfer['sha256'])
        need((ROOT/(R+'main/proof.drat')).stat().st_size==transfer['bytes']and transfer['bytes']<=LIMITS['trace_file_bytes'],'saved SAT trace bytes and size limit')
        need(transfer['linux_source']==w+'/proof.drat','historical trace source')
        for name in ['native_hash_receipt','copy_receipt']:
            rec=transfer[name];streams(rec);need(rec['actual_exit_code']==0 and not rec['outer_windows_guard_expired'],'historical transfer completed')
        hashtext=(ROOT/transfer['native_hash_receipt']['stdout']).read_text().split()
        need(hashtext==[transfer['sha256'],transfer['linux_source']],'historical ext4 SHA equals current host')
        need(transfer['native_hash_receipt']['command'][-2:]==['/usr/bin/sha256sum',w+'/proof.drat'],'targeted historical hash command')
        need(transfer['copy_receipt']['command'][-4:]==['/usr/bin/cp','--',w+'/proof.drat',linux(R+'main/proof.drat')],'exact immediate host-copy command')
        for label in ['processes_before','fresh_process_observation']:
            rec=run[label];streams(rec)
            need(rec['command']==['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'],'targeted saved process query')
            need(rec['actual_exit_code']==1 and not rec['outer_windows_guard_expired']and len((ROOT/rec['stdout']).read_text().strip().splitlines())<=1,'saved no matching named process; no present process assertion')
        object_rec=run['independent_object_receipt'];streams(object_rec)
        need(object_rec==read(R+'independent_object_command.receipt.json')and object_rec['actual_exit_code']==0 and not object_rec['outer_windows_guard_expired'],'separately saved child execution')
        v=signed(read(R+'main/parsed_model.json')['assignment'],N);need(v==parse_native(text,N),'entire native/JSON assignment equality')
        checked=clauses(ROOT/CNF,v,M);model=read(BASE+'model.json');raw=read(RAW);mapping=catalogue(read(LOCAL))
        profile=decode(model,v,raw,mapping)
        need(profile==read(R+'independent_object/independent_count_profile.json'),'saved child equals new independent raw reconstruction')
        excluded=read(OLD+'excluded_profiles.json')['records'];scalar=read(D+'model.json')['scalar_clause_records']
        cut_result=cuts(profile,v,excluded,scalar);diagnostic=envelopes(profile,raw,model['groups'])
        need(cut_result==read(R+'independent_object/independent_cut_avoidance.json'),'all independent raw cut truths match')
        saved_diag=read(R+'independent_object/universal_upper_envelopes.json')
        need(diagnostic['records']==saved_diag['records']and diagnostic['failed']==saved_diag['failed'],'all540 independently reconstructed envelopes')
        controls=calibrate(out,model,raw,mapping,profile,v,run,text,w)
        save(out/'controls.json',controls);save(out/'independent_count_profile.json',profile)
        save(out/'independent_cut_truths.json',cut_result);save(out/'universal_upper_envelopes.json',diagnostic)
        need(child['status']=='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_SAT_OBJECT_PASS'and child['actual_clauses_checked']==M,'child metadata consistent only after fresh complete check')
        need(time.monotonic()-start<180,'bounded180second verification')
        statement=f'The pinned {N}-variable {M}-clause at-least-seven count formula with six whole-profile and six scalar necessary cuts is satisfiable. The complete saved assignment decodes to count profile {profile["profile_sha256"]} with {profile["exception_count"]} exceptional groups and passes all 540 universal upper-envelope diagnostics. This is a count-relaxation witness, not a Gram factor, cross-column completion or target graph.'
        report=dict(status='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_SAT_OUTCOME_PASS',claim_id=CID,revision=1,
            timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],python=platform.python_version(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},
            variables_checked=N,actual_clauses_checked=checked,profile_sha256=profile['profile_sha256'],
            independent_count_profile_sha256=sha(out/'independent_count_profile.json'),exception_count=profile['exception_count'],
            exceptional_groups=profile['exceptional_groups'],all_twelve_cuts_satisfied=True,universal_upper_bounds_checked=540,
            upper_bound_failures=len(diagnostic['failed']),native_statistics=stats,configured_limits=LIMITS,
            saved_SAT_trace=dict(bytes=transfer['bytes'],sha256=transfer['sha256'],proof_validity_checked=False,
                current_ext4_availability='NOT_QUERIED',historical_transfer_authenticated=True),
            rejected_corruptions=len(controls['rejected']),scope=statement,
            shared_components=['Fresh standard-library-only parsing, literal clause evaluator, catalogue-signature grouping and count decoder; no repository checker/producer imports.',
                'Frozen complete local catalogue and authenticated model mappings are earlier independent premises. Encoding semantics are not reproved by this outcome check.'],
            solver_calls=0,full_factor=False,target_resolution=False,elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',report)
        depids=['C-FIXED-HADAMARD-SIX-PARTIAL-SCALAR-COUNT-CUTS','C-FIXED-HADAMARD-COUNT-MASTER-SIX-PROFILE-CUT-ENCODING']
        ledger=(ROOT/'CLAIMS.yaml').read_text(encoding='utf8')
        for cid in depids:need('- id: '+cid+'\n  revision: 1\n'in ledger,'actual ledger dependency ID/revision')
        save(out/'claim_binding.json',dict(claim_id=CID,revision=1,statement=statement,status='VERIFIED',review_state='CLEAR',
            dependencies=[dict(id=cid,revision=1,relation='encoding_equivalence'if i==0 else'uses_result')for i,cid in enumerate(depids)],
            independent_verification=dict(report=key(out/'summary.json'),sha256=sha(out/'summary.json'),verifier='structural_attack',method='Fresh complete native/JSON/raw-clause and raw-count audit with corruptions'),
            evidence=dict(assignment=R+'main/parsed_model.json',assignment_sha256=pins[R+'main/parsed_model.json'],
                independent_count_profile=key(out/'independent_count_profile.json'),independent_count_profile_sha256=sha(out/'independent_count_profile.json'),encoding_gate=EG,encoding_gate_sha256=EH),
            limitations=['No full Gram realization, cross-group column-cap compatibility, residual D, target construction, exclusion or novel-family coverage.'],
            shared_components=report['shared_components']))
        print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,source_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-start));raise


def pin_digest(path,pins):
    need(path in pins,'CNF bound by immutable gate/run');return pins[path]


if __name__=='__main__':main()
