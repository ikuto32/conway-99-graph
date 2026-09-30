"""Exact count-table CNF producer. All outputs remain candidates pending review."""
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse,copy,gzip,hashlib,json,platform,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
PRE=B/'20260930_hadamard_count_master_preflight'
GATE=B/'20260930_independent_review/hadamard_count_master_preflight/summary.json'
UNION=B/'20260930_independent_review/hadamard_six_profile_union/summary.json'
PINS={GATE:'5b23e5a188522c669128ec9f79ec8fb975d75e251c15be4ebc0857b96d4876b3',UNION:'6a7b34f7feaf7d9330ce07f4c615f4198e8cdc0c8ac22dd7fb5e673ba59311df',PRE/'summary.json':'f290fc687ac1723354e9b4acf7429de087547f8a422bb4ee7770b2473d62e7bb',PRE/'inventory.json':'546a1c8ecc8a796700161ccdd064627561ea3a609955499cf7f3f07009a2ba80'}

def need(ok,msg):
    if not ok:raise ValueError(msg)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

class Formula:
    def __init__(self,n=0):self.variables=n;self.clauses=[]
    def new(self):self.variables+=1;return self.variables
    def add(self,c):
        need(all(type(x)is int and x and abs(x)<=self.variables for x in c),'literal IDs')
        self.clauses.append(list(c))
    def onehot(self,variables,kind,identity):
        start=len(self.clauses);self.add(variables);prefix=[]
        if len(variables)>1:
            prefix=[self.new() for _ in variables[:-1]];self.add([-variables[0],prefix[0]])
            for i in range(1,len(variables)-1):
                self.add([-variables[i],prefix[i]]);self.add([-prefix[i-1],prefix[i]]);self.add([-variables[i],-prefix[i-1]])
            self.add([-variables[-1],-prefix[-1]])
        return dict(kind=kind,identity=identity,selectors=variables,prefix_variables=prefix,first_clause=start+1,clause_count=len(self.clauses)-start)

def token(x,values):return x if type(x)is bool else values[x]
def relation(out,q,x,r):
    ids=sorted({v for v in [out,q,x,r] if type(v)is not bool});clauses=[]
    for bits in product((False,True),repeat=len(ids)):
        values=dict(zip(ids,bits));expected=token(q,values) or (token(x,values) and token(r,values))
        if values[out]!=expected:clauses.append([-v if values[v] else v for v in ids])
    return clauses

def threshold(formula,variables,bound):
    before=formula.variables;start=len(formula.clauses);states={};records=[]
    for i,x in enumerate(variables,1):
        for j in range(1,min(i,bound+1)+1):
            q=states.get((i-1,j),False);r=True if j==1 else states.get((i-1,j-1),False);out=formula.new();first=len(formula.clauses)
            for clause in relation(out,q,x,r):formula.add(clause)
            states[i,j]=out;records.append(dict(i=i,j=j,id=out,q=q,x=x,r=r,first_clause=first+1,clause_count=len(formula.clauses)-first))
    final=states.get((len(variables),bound+1),False)
    if final is not False:formula.add([-final])
    return dict(input_variables=variables,at_most=bound,states=records,final_threshold=final,first_clause=start+1,clause_count=len(formula.clauses)-start,new_variables=formula.variables-before)

def satisfied(clauses,values):return all(any(values[abs(x)]==(x>0) for x in clause) for clause in clauses)
def assignment_values(assignment,n):
    need(len(assignment)==n and all(type(x)is int and x and abs(x)<=n for x in assignment),'complete signed assignment bounds')
    need(len({abs(x) for x in assignment})==n,'unique complete variable IDs')
    result=[False]*(n+1)
    for x in assignment:result[abs(x)]=x>0
    return result
def threshold_values(values,record):
    for state in record['states']:values[state['id']]=sum(values[x] for x in record['input_variables'][:state['i']])>=state['j']

def gadget_controls():
    rows=[];total=0
    for n in range(1,7):
        f=Formula(n);d=f.onehot(list(range(1,n+1)),'control',n);counts=[]
        for bits in product((False,True),repeat=n):
            solutions=0
            for aux in product((False,True),repeat=n-1):
                values=[False,*bits,*aux];solutions+=satisfied(f.clauses,values);total+=1
            need(solutions==int(sum(bits)==1),'onehot full auxiliary truth table');counts.append(solutions)
        rows.append(dict(n=n,variables=f.variables,clauses=f.clauses,solution_counts=counts))
    tested=0;corrupted=0
    for n in range(1,8):
        for bound in range(n+1):
            f=Formula(n);record=threshold(f,list(range(1,n+1)),bound)
            for bits in product((False,True),repeat=n):
                values=[False,*bits]+[False]*(f.variables-n);threshold_values(values,record)
                need(satisfied(f.clauses,values)==(sum(bits)<=bound),'small literal cardinality equivalence');tested+=1
                if record['states']:
                    values[record['states'][0]['id']]^=True
                    gatecount=sum(r['clause_count'] for r in record['states'])
                    need(not satisfied(f.clauses[:gatecount],values),'changed threshold state rejected');corrupted+=1
    # Independently evaluate every local gate input and output truth assignment.
    local=0
    for q,r in product((False,True,1,2),repeat=2):
        for bits in product((False,True),repeat=4):
            values=[False,*bits];expected=values[4]==(token(q,values) or(values[3] and token(r,values)))
            need(satisfied(relation(4,q,3,r),values)==expected,'all local truth-table rows');local+=1
    return dict(onehot_controls=rows,onehot_full_assignments=total,threshold_input_assignments=tested,threshold_corruptions=corrupted,local_gate_rows=local,scope='Gadget truth tables only, no research solver calls.')

def write_cnf(path,formula):
    with path.open('x',encoding='ascii',newline='\n') as f:
        f.write(f'p cnf {formula.variables} {len(formula.clauses)}\n')
        for clause in formula.clauses:f.write(' '.join(map(str,clause))+' 0\n')

def check_cnf(path,values):
    count=0
    with Path(path).open('r',encoding='ascii') as f:
        header=next(f).split();need(header[:2]==['p','cnf'] and int(header[2])==len(values)-1,'actual CNF header variable count')
        for line in f:
            clause=list(map(int,line.split()));need(clause and clause[-1]==0,'actual clause terminator');need(all(x and abs(x)<len(values) for x in clause[:-1]),'actual literal range');need(any(values[abs(x)]==(x>0) for x in clause[:-1]),'actual clause satisfaction');count+=1
        need(count==int(header[3]),'actual clause count')
    return count

def package(path):
    target=path.with_name(path.name+'.gz')
    with path.open('rb') as source,target.open('xb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=9) as out:
            for block in iter(lambda:source.read(1048576),b''):out.write(block)
    need(target.stat().st_size<10*1024**2,'public compressed payload limit')
    h=hashlib.sha256();n=0
    with gzip.open(target,'rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block);n+=len(block)
    need(n==path.stat().st_size and h.hexdigest()==sha(path),'whole gzip byte recovery')
    return dict(raw_path=key(path),raw_sha256=sha(path),raw_bytes=n,gzip_path=key(target),gzip_sha256=sha(target),gzip_bytes=target.stat().st_size,recovery_identity=True)

def decode(assignment,model_path,variant='baseline'):
    model=read(model_path);v=model['variants'][variant];values=assignment_values(assignment,v['variables']);checked=check_cnf(ROOT/v['cnf_path'],values)
    coordinates=[];selected=[]
    for d in model['coordinate_domains']:
        chosen=[i for i,x in enumerate(d['selectors']) if values[x]];need(len(chosen)==1,'one coordinate choice');i=chosen[0];coordinates.append(d['count_tables'][i]);selected.append(d['selectors'][i])
    groups=[];local=[];ranks=[]
    for d in model['group_domains']:
        chosen=[i for i,x in enumerate(d['selectors']) if values[x]];need(len(chosen)==1,'one group signature');i=chosen[0];sid=d['signature_indices'][i];signature=model['local_signatures'][sid]
        actual=[v for a in d['support'] for v in coordinates[a][d['group']]]
        need(actual==signature['counts'],'literal incidence agreement');need(all(sum(actual[3*j+f] for j in range(6))==6 for f in range(3)),'group/fibre quota')
        groups.append(d['selectors'][i]);local.append(signature['local_survivor_indices']);ranks.append(sid)
    for a,counts in enumerate(coordinates):
        for f in range(3):
            delta=[counts[g][f]-int(a in model['groups'][g]) for g in range(20)]
            need(sum(delta)==0 and all(sum(delta[g] for g in range(20) if b in model['groups'][g])==0 for b in range(12)),'literal complete summed-Gram marginal')
    exceptional=[g for g,support in enumerate(model['groups']) if any(coordinates[a][g]!=[1,1,1] for a in support)]
    if variant=='at_least_seven':need(len(exceptional)>=7,'literal exception bound')
    deviations=[[[coordinates[a][g][f]-int(a in model['groups'][g]) for g in exceptional] for f in range(3)] for a in range(12)]
    profile=dict(groups=exceptional,deviations=deviations)
    return dict(variant=variant,selected_coordinate_selector_ids=selected,selected_group_selector_ids=groups,selected_global_signature_indices=ranks,coordinate_group_fibre_counts=coordinates,exceptional_groups=exceptional,exception_count=len(exceptional),coordinate_fibre_deviations=deviations,profile_sha256=hashlib.sha256(json.dumps(profile,sort_keys=True,separators=(',',':')).encode()).hexdigest(),local_survivor_indices_by_group=local,actual_cnf_clauses_checked=checked,full_factor=False,target_graph=False,residual_D=None,all_cross_group_column_caps_checked=False,model_sha256=sha(model_path))

def build(out):
    start=time.monotonic();pins={}
    for p,h in PINS.items():need(sha(p)==h,'frozen gate/input '+key(p));pins[key(p)]=h
    gate=read(GATE);need(gate['status']=='INDEPENDENT_COUNT_MASTER_PREFLIGHT_REVIEW_PASS','independent preflight gate')
    for p,h in read(PRE/'summary.json')['outputs_sha256'].items():need(sha(ROOT/p)==h,'preflight output');pins[p]=h
    inventory=read(PRE/'inventory.json')
    for p,h in inventory['inputs_sha256'].items():need(sha(ROOT/p)==h,'preflight raw input');pins[p]=h
    for p in (Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml'):pins[key(p)]=sha(p)
    need(gate['inputs_sha256'][key(PRE/'inventory.json')]==PINS[PRE/'inventory.json'],'gate directly binds table inventory')
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,limits=dict(seconds=120,estimated_memory_bytes=1024**3,native_calls=0)))
    save(out/'gadget_controls.json',gadget_controls())
    f=Formula();coordinates=[];groups=[];channels=[];signatures=read(PRE/'local_signatures.json')['signatures']
    for rec in inventory['coordinate_records']:
        path=ROOT/rec['path'];need(sha(path)==rec['sha256'],'raw complete coordinate domain');raw=read(path);ids=[f.new() for _ in raw['ordered_three_fibre_choices']]
        coordinates.append(dict(coordinate=raw['coordinate'],selectors=ids,incident_groups=raw['incident_groups'],count_tables=[c['full20_count_signature'] for c in raw['ordered_three_fibre_choices']]))
    for d in inventory['group_domains']:groups.append(dict(group=d['group'],support=d['support'],signature_indices=d['signature_indices'],selectors=[f.new() for _ in d['signature_indices']]))
    for d in inventory['channel_domains']:channels.append(dict(coordinate=d['coordinate'],group=d['group'],values=d['values'],variables=[f.new() for _ in d['values']]))
    primary=f.variables;domains=[]
    for d in coordinates:domains.append(f.onehot(d['selectors'],'coordinate',d['coordinate']))
    for d in groups:domains.append(f.onehot(d['selectors'],'group',d['group']))
    for d in channels:domains.append(f.onehot(d['variables'],'channel',[d['coordinate'],d['group']]))
    onehot_end=len(f.clauses);lookup={(d['coordinate'],d['group'],tuple(value)):x for d in channels for value,x in zip(d['values'],d['variables'])}
    for d in coordinates:
        for x,counts in zip(d['selectors'],d['count_tables']):
            for g in d['incident_groups']:f.add([-x,lookup[d['coordinate'],g,tuple(counts[g])]])
    coordinate_end=len(f.clauses)
    for d in groups:
        for x,sid in zip(d['selectors'],d['signature_indices']):
            sig=signatures[sid]['counts']
            for j,a in enumerate(d['support']):f.add([-x,lookup[a,d['group'],tuple(sig[3*j:3*j+3])]])
    base_n=f.variables;base_c=len(f.clauses);need((base_n,base_c)==(155750,704454)==(inventory['estimated_variables'],inventory['estimated_clauses']),'frozen base count prediction')
    write_cnf(out/'baseline.cnf',f)
    balanced=[]
    for d in groups:
        ids=[x for x,sid in zip(d['selectors'],d['signature_indices']) if signatures[sid]['counts']==[1]*18];need(len(ids)==1,'unique balanced signature');balanced+=ids
    extension=threshold(f,balanced,13);need(extension['new_variables']==189 and extension['clause_count']==1379,'twenty by fourteen exact threshold counts');write_cnf(out/'at_least_seven.cnf',f)
    with (out/'extension.cnfpart').open('x',encoding='ascii',newline='\n') as stream:
        for clause in f.clauses[base_c:]:stream.write(' '.join(map(str,clause))+' 0\n')
    save(out/'extension.json',dict(schema='COUNT_MASTER_AT_LEAST_SEVEN_EXTENSION_V1',base_variables=base_n,base_clauses=base_c,variables=f.variables,clauses=len(f.clauses),balanced_selector_ids=balanced,threshold=extension,necessity_gate_path=key(UNION),necessity_gate_sha256=PINS[UNION],necessary_scope='Only potential fixed-support full-Gram factors with all outside-column overlap caps; not entailed by baseline count CSP.',new_activity_variables=0))
    model=dict(schema='ARBITRARY_EXCEPTION_COUNT_MASTER_CNF_V1',groups=inventory['groups'],coordinate_domains=coordinates,group_domains=groups,count_channels=channels,local_signatures=signatures,one_hot_domains=domains,primary_variables=primary,clause_sections=dict(onehots=[1,onehot_end],coordinate_implications=[onehot_end+1,coordinate_end],group_implications=[coordinate_end+1,base_c]),variants=dict(baseline=dict(variables=base_n,clauses=base_c,cnf_path=key(out/'baseline.cnf'),cnf_sha256=sha(out/'baseline.cnf')),at_least_seven=dict(variables=f.variables,clauses=len(f.clauses),cnf_path=key(out/'at_least_seven.cnf'),cnf_sha256=sha(out/'at_least_seven.cnf'))),extension=extension,inputs_sha256=pins,scope=inventory['scope'],full_factor=False,target_graph=False)
    save(out/'model.json',model)
    save(out/'scope.json',dict(schema='ARBITRARY_EXCEPTION_COUNT_MASTER_SCOPE_V1',groups=inventory['groups'],baseline='Joint complete coordinate marginal profiles, local count-signature tables and exact incidence agreement; any number of exceptional groups.',extension='At least seven exceptional groups, as a separately justified necessary condition for potential fixed-support full-Gram factors with all outside-column caps.',preflight_gate_path=key(GATE),preflight_gate_sha256=PINS[GATE],extension_necessity_gate_path=key(UNION),extension_necessity_gate_sha256=PINS[UNION],within_group_caps_inherited=True,cross_group_caps_encoded=False,full_Gram_encoded=False,residual_D_encoded=False,target_automorphism_assumed=False,inputs_sha256=pins))
    control_records=[]
    for control in read(PRE/'controls.json')['positive_count_profiles']:
        values=[False]*(f.variables+1)
        for d,i in zip(coordinates,control['coordinate_choice_indices']):values[d['selectors'][i]]=True
        for d,sid in zip(groups,control['group_signature_indices']):values[d['selectors'][d['signature_indices'].index(sid)]]=True
        for d in channels:values[d['variables'][d['values'].index(control['counts'][d['coordinate']][d['group']])]]=True
        for d in domains:
            seen=False
            for x,s in zip(d['selectors'],d['prefix_variables']):seen=seen or values[x];values[s]=seen
        need(satisfied(f.clauses[:base_c],values),'literal full baseline control')
        signed=[i if values[i] else -i for i in range(1,base_n+1)];name=control['name'];save(out/(name+'_assignment.json'),dict(assignment=signed,count_only_control=True))
        decoded=decode(signed,out/'model.json');save(out/(name+'_counts.json'),decoded)
        threshold_values(values,extension);need(not satisfied(f.clauses,values) and values[extension['final_threshold']],'positive baseline fails additional bound')
        corruptions=[]
        for label,x in [('selector',coordinates[0]['selectors'][0]),('prefix',domains[0]['prefix_variables'][0]),('channel',channels[0]['variables'][0])]:
            bad=values.copy();bad[x]^=True;need(not satisfied(f.clauses[:base_c],bad),'single corrupted base bit rejected');corruptions.append(label)
        for label,bad in [('missing',signed[:-1]),('duplicate',signed[:-1]+[signed[0]])]:
            try:assignment_values(bad,base_n)
            except ValueError:corruptions.append(label)
            else:raise ValueError('assignment corruption accepted')
        control_records.append(dict(name=name,baseline_all_clauses_pass=True,exception_count=decoded['exception_count'],extension_rejected=True,corruptions_rejected=corruptions,full_factor=False))
    save(out/'full_count_controls.json',dict(records=control_records,scope='Constructed count-CSP SAT assignments only; neither asserts a full-Gram factor.'))
    packages=[package(out/name) for name in ['baseline.cnf','at_least_seven.cnf','model.json']];save(out/'packages.json',dict(records=packages))
    need(time.monotonic()-start<120,'120-second cooperative build allocation')
    summary=dict(status='CANDIDATE_COUNT_MASTER_AND_AT_LEAST_SEVEN_CNF_BUILT',inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},baseline_variables=base_n,baseline_clauses=base_c,augmented_variables=f.variables,augmented_clauses=len(f.clauses),coordinate_choices=2226,group_choices=74798,count_channels=927,onehot_domains=len(domains),added_threshold_variables=189,added_clauses=len(f.clauses)-base_c,elapsed_seconds=time.monotonic()-start,native_calls=0,solver_calls=0,independent_approval=False,target_resolution=False,artifact_availability='LOCAL_ONLY',scope='Count-table relaxation only, arbitrary exceptions in baseline. Additional at-least-seven family consequence in separate formula; full Gram and cross-group caps omitted.')
    save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['inputs_sha256','outputs_sha256']}))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True);p=sub.add_parser('build');p.add_argument('--out',type=Path,required=True);p=sub.add_parser('decode');p.add_argument('--model',type=Path,required=True);p.add_argument('--variant',choices=['baseline','at_least_seven'],default='baseline');p.add_argument('--assignment',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        if args.mode=='build':build(out)
        else:save(out/'decoded_count_profile.json',decode(read(args.assignment)['assignment'],args.model,args.variant))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),target_resolution=False));raise
if __name__=='__main__':main()
