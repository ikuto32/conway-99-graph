"""Independent unrestricted rooted8 marked/product reconstruction and finite calibration."""
import argparse,copy,hashlib,json,math,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261002_rooted8_model_v1 as independent_core
import audit_20261002_rooted5_rigidity_v2 as geometry

ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/results/20261002_rooted7_unrestricted_extension01/model.json'
CONTROL='acceleration/results/20261003_rooted8_unrestricted_precontrols02/'
FORCED='acceleration/results/20261002_rooted5_flag_rigidity/ordered_nonedge_forced5flags.json'
PINS={
 OLD:'9f636889690071f69ad7a103b02abb2f43a5bbc2d2114c87a779da29c0f647a1',
 'acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/summary.json':'e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70',
 'acceleration/results/20261002_rooted7_extension_model/catalogue.json':'a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5',
 'acceleration/results/20261002_independent_review/rooted7_catalogue01/summary.json':'3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758',
 FORCED:'90697d6bbef39e0636bcb4d60109e4a3c6f0458b478428df5b189607b19e1331',
 CONTROL+'summary.json':'22aeed9108a6aaa13e0922ee56909ea270ab2fc3b2f56492e914fee0a1ac7dba',
 CONTROL+'fixture_controls.json':'91252b6d23ad60e4d262e6a71980f6d4ed502bbc80be53b4d9666ce81c521f68',
 CONTROL+'controls.json':'c8c77221c33e94e63f03a4875e65e5adfec8e169caeeb6bfb67a30d22ed1b7db',
 'acceleration/theory_20261003_rooted8_unrestricted_extension_v2.py':'8fbc97fa13296ba4e78a839882419e0b1b1cbfe7c6415486cb444bc749e29796',
 'docs/PROTOCOL_20261003_UNRESTRICTED_ROOTED8_V2.md':'d087151e8fd8a189804231f45c36908e4072459c44c8bbdfe75c0fb7a2fb19bf',
 'docs/DESIGN_20261003_UNRESTRICTED_ROOTED8_V1.md':'d127c9cee6215742d0e80056d0810700a60ee5aefafc0fb1c2f3a99c158faa86',
 'acceleration/audit_20261002_rooted8_model_v1.py':'e8a250075884b3049d4a933441b460da52b8f18468cc13129e4a6ab6bcc0eeba',
 'acceleration/audit_20261002_rooted5_rigidity_v2.py':'b281675c501cbf49116b2c1f6cfd6beb55d0bdf00b0bacc34bf8e9b42660f0ed'}

class AuditError(ValueError):
    def __init__(self,stage,detail=''):self.stage=stage;super().__init__(stage+(': '+detail if detail else ''))
def need(ok,stage,detail=''):
    if not ok:raise AuditError(stage,detail)
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,data):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(data,stream,indent=2);stream.write('\n')
def reject(records,label,expected,call):
    try:call()
    except AuditError as error:
        need(error.stage==expected,'CONTROL_EXACT_STAGE',str(error));records.append({'label':label,'stage':error.stage,'diagnostic':str(error)})
    else:raise AuditError('CONTROL_ACCEPTED',label)

def validate_graph(adj,k,lam,mu):
    n=len(adj)
    need(all(len(row)==n and all(value in (0,1) for value in row) for row in adj),'FIXTURE_BINARY_SHAPE')
    need(all(adj[u][u]==0 and all(adj[u][v]==adj[v][u] for v in range(n)) for u in range(n)),'FIXTURE_SIMPLE_SYMMETRIC')
    need(all(sum(row)==k for row in adj),'FIXTURE_DEGREE')
    need(all(sum(adj[u][w]*adj[v][w] for w in range(n))==(lam if adj[u][v] else mu) for u,v in combinations(range(n),2)),'FIXTURE_EXACT_COMMON_NEIGHBORS')

def fixtures():
    cells=list(combinations(range(5),2))
    # An explicit KG(5,2) labelling matching the saved outer/star convention,
    # constructed via set-disjointness rather than the producer's cycle edges.
    cells=[(0,1),(2,3),(0,4),(1,2),(3,4),(2,4),(1,4),(1,3),(0,3),(0,2)]
    petersen=[[int(set(first).isdisjoint(second)) for second in cells] for first in cells]
    points=[(row,col) for row in range(3) for col in range(3)]
    rook=[[int(a!=b and (a[0]==b[0] or a[1]==b[1])) for b in points] for a in points]
    return [('rook9',rook,4,1,2,36),('petersen10',petersen,3,0,1,60)]

def lower_factor(adj,kind,orbit,n,k,lam,mu):
    if kind=='delete':return n-7
    if kind=='degree':return sum(k-sum(adj[u]) for u, in orbit)
    return sum((lam if adj[u][v] else mu)-sum(adj[u][w]*adj[v][w] for w in range(7)) for u,v in orbit)

def extensions(seven,eight,lookup,offset,tick,checkpoint,n=99,k=14,lam=1,mu=2):
    # Core independently enumerates EVERY free-deletion isomorphism and checks
    # mark-orbit invariance; it never uses the producer's chosen transport.
    rows,transports,deletions=independent_core.extensions(seven,eight,lookup,offset,tick,checkpoint)
    positions={mask:j for j,mask in enumerate(seven)}
    rows[0]['rhs_affine']=[math.comb(n-2,6),0,0,0]
    for row in rows[1:]:
        adj=geometry.matrix(7,row['parent7mask']);left=lower_factor(adj,row['kind'],row['orbit'],n,k,lam,mu)
        parent=positions[row['parent7mask']]
        row['terms']=[[col,value] for col,value in row['terms'] if col!=parent]
        if left:row['terms'].insert(0,[parent,-left])
        row['rhs_affine']=[0,0,0,0];row['parent_factor']=left
    return rows,transports,deletions

def products(five,six,seven,eight,offset,lookup,forced,origin,bases,tick,checkpoint):
    pairs=[(a,b) for i,a in enumerate(five) for b in five[i:]];position={pair:j for j,pair in enumerate(pairs)}
    terms=[Counter() for _ in pairs];known=[Counter() for _ in pairs];populations={}
    for mask in five:need(independent_core.union_coefficients(5,mask,lookup)==(Counter({(mask,mask):1}),1),'EXACT_ROOT5_COLLISION')
    for h,masks in [(6,six),(7,seven),(8,eight)]:
        populations[h]=0
        for j,mask in enumerate(tqdm(masks,desc='independent unrestricted union'+str(h),mininterval=5)):
            counts,population=independent_core.union_coefficients(h,mask,lookup);populations[h]+=population
            for pair,value in counts.items():
                if h==6:known[position[pair]][mask]+=value
                else:terms[position[pair]][j if h==7 else offset+j]+=value
            if (j+1)%2000==0:checkpoint('products'+str(h),{'completed_classes':j+1,'exact_ordered_pairs':populations[h]})
            tick()
    rows=[]
    for pair,coeff,lower in zip(pairs,terms,known):
        a,b=pair;original=forced[a]*forced[b]*(1 if a==b else 2);collision=forced[a] if a==b else 0
        rhs=[original-collision-sum(value*origin[mask] for mask,value in lower.items())]
        rhs.extend(-sum(value*basis[mask] for mask,value in lower.items()) for basis in bases)
        need(len(rhs)==4,'FULL_CONSTANT_C_A_B_RHS')
        rows.append({'kind':'unrestricted_universal5_ordered_product_upper','rooted5_masks':list(pair),'original_product_rhs':original,'known_root5_collision':collision,'known_root6_coefficients':[[mask,value] for mask,value in sorted(lower.items())],'terms':[[col,value] for col,value in sorted(coeff.items()) if value],'rhs_affine':rhs})
    return rows,populations

def verify(raw,old,eight,extension,product,raw_ext,raw_prod):
    need(raw['format']=='ROOTED8_UNRESTRICTED_EXTENSION_UNIVERSAL5_PRODUCT_MODEL_V1','MODEL_FORMAT')
    need(raw['variables']==old['variables']+[[8,mask] for mask in eight],'MODEL_VARIABLES')
    need(raw_ext==extension,'EXTENSION_COEFFICIENTS_OR_RHS')
    need(raw_prod==product,'PRODUCT_COEFFICIENTS_OR_RHS')
    expected=old['equations']+[{'terms':row['terms'],'rhs_affine':row['rhs_affine']} for row in extension+product]
    need(raw['equations']==expected,'MODEL_COMPLETE_OPERATOR')
    need(raw['inherited_unrestricted_root7_model_sha256']==PINS[OLD] and raw['inherited_prefix']=={'variables':2810,'rows':11769},'UNRESTRICTED_INHERITED_PREFIX')
    need(raw['affine_RHS_coordinate_order']==['constant','c','a','b'] and raw['parameter_domain']==old['parameter_domain'],'FULL_UNRESTRICTED_DOMAIN')

def calibration(old,producer_records,out,tick):
    canon={h:{} for h in range(5,9)}
    def canonical(h,mask):
        if mask not in canon[h]:
            orbit=geometry.orbit(h,mask);minimum=min(orbit)
            for member in orbit:canon[h][member]=minimum
        return canon[h][mask]
    raw_records=[];controls=[];mark_count=product_count=transports=0;prism_children=set();reference=None
    for name,adj,k,lam,mu,expected in fixtures():
        validate_graph(adj,k,lam,mu);n=len(adj);roots=[(u,v) for u in range(n) for v in range(n) if u!=v and not adj[u][v]]
        need(len(roots)==expected,'ALL_FIXTURE_ROOTS')
        for root in roots:
            counts={h:Counter(canonical(h,geometry.bits(adj,(*root,*subset))) for subset in combinations([v for v in range(n) if v not in root],h-2)) for h in range(5,9)}
            seven=sorted(counts[7]);eight=sorted(counts[8]);offset=len(seven)
            rows,tr,deleted=extensions(seven,eight,canon[7],offset,tick,lambda *args:None,n,k,lam,mu)
            vector=Counter({j:counts[7][mask] for j,mask in enumerate(seven)});vector.update({offset+j:counts[8][mask] for j,mask in enumerate(eight)})
            def marked_check(candidate=rows,values=vector):need(all(sum(value*values[col] for col,value in row['terms'])==row['rhs_affine'][0] for row in candidate),'FINITE_MARKED_IDENTITY')
            marked_check();totals=Counter()
            for h in range(5,9):
                for mask,value in counts[h].items():
                    for pair,coefficient in independent_core.union_coefficients(h,mask,canon[5])[0].items():totals[pair]+=coefficient*value
            for a in counts[5]:
                for b in counts[5]:
                    if a<=b:need(totals[a,b]==counts[5][a]*counts[5][b]*(1 if a==b else 2),'FINITE_ORDERED_PRODUCT_IDENTITY')
            record={'fixture':name,'roots':list(root),'counts':{str(h):[[mask,value] for mask,value in sorted(counts[h].items())] for h in range(5,9)},'marked_rows_checked':len(rows),'ordered_product_rows_checked':len(totals)}
            raw_records.append(record);mark_count+=len(rows);product_count+=len(totals);transports+=tr
            if root==roots[0]:
                changed=Counter(vector);changed[offset]+=1
                reject(controls,name+':count','FINITE_MARKED_IDENTITY',lambda:marked_check(values=changed))
                damaged=copy.deepcopy(rows);at,col=next((i,col) for i,row in enumerate(rows[1:],1) for col,value in row['terms'] if col>=offset and vector[col])
                next(term for term in damaged[at]['terms'] if term[0]==col)[1]+=1
                reject(controls,name+':positive_marked_coefficient','FINITE_MARKED_IDENTITY',lambda:marked_check(candidate=damaged))
                first,second=next(pair for pair in totals if pair[0]!=pair[1] and counts[5][pair[0]] and counts[5][pair[1]])
                reject(controls,name+':orientation','FINITE_ORDERED_PRODUCT_IDENTITY',lambda:need(totals[first,second]==counts[5][first]*counts[5][second],'FINITE_ORDERED_PRODUCT_IDENTITY'))
                a=next(iter(counts[5]));reject(controls,name+':collision','FINITE_ORDERED_PRODUCT_IDENTITY',lambda:need(totals[a,a]-counts[5][a]==counts[5][a]**2,'FINITE_ORDERED_PRODUCT_IDENTITY'))
                damaged=copy.deepcopy(adj);u,v=next((u,v) for u,v in combinations(range(n),2) if adj[u][v]);damaged[u][v]=damaged[v][u]=0
                reject(controls,name+':raw_fixture_edge','FIXTURE_DEGREE',lambda:validate_graph(damaged,k,lam,mu))
                if reference is None:reference=(seven,eight,rows,vector)
            if name=='rook9':
                partition=Counter(adj[root[0]][w]+2*adj[root[1]][w] for w in range(n) if w not in root)
                need([partition[p] for p in range(4)]==[1,2,2,2],'ACTUAL_ROOK_PARTITIONS')
                for mask in eight:
                    mat=geometry.matrix(8,mask)
                    if any(all(sum(mat[u][v] for v in chosen)==3 for u in chosen) and sum(all(mat[u][v] for u,v in combinations(triangle,2)) for triangle in combinations(chosen,3))==2 for chosen in combinations(range(8),6)):prism_children.add(mask)
            tick()
    need(raw_records==producer_records,'RAW_PRODUCER_FIXTURE_COUNTS_AND_ROWS')
    need((len(raw_records),mark_count,product_count)==(96,61884,34740),'FINITE_CHECK_POPULATIONS')
    need(prism_children=={14333546,14334680,15404506,15428952},'POSITIVE_PRISM_CONTAINING_SUPPORT')
    damaged=set(prism_children);damaged.pop()
    reject(controls,'omitted_prism_child','FIXTURE_COVERAGE',lambda:need(prism_children<=damaged,'FIXTURE_COVERAGE'))
    five=sorted(int(mask) for mask,value in json.loads((ROOT/FORCED).read_bytes())['flag_counts']);lookup=independent_core.orbit_map(5,five,tick)
    for h,count in ((5,1),(6,12),(7,30),(8,20)):need(independent_core.union_coefficients(h,0,lookup)==(Counter({(0,0):count}),count),'EMPTY_EXACT_UNION_POPULATION')
    profile=old['root6_nonedge_profile_basis'];origin={int(mask):value for mask,value in profile['origin'].items()};bases=[{int(mask):value for mask,value in row.items()} for row in profile['basis']]
    need(len(origin)==567 and len(bases)==3 and [basis[7100] for basis in bases]==[1,0,0],'UNRESTRICTED_C_PRISM_COORDINATE')
    lower=Counter()
    for mask in origin:
        for pair,coefficient in independent_core.union_coefficients(6,mask,lookup)[0].items():lower[pair]-=coefficient*bases[0][mask]
    pair=next(pair for pair,value in sorted(lower.items()) if value);expected=lower[pair]
    reject(controls,'nonzero_c_rhs_omission','C_RHS_REQUIRED',lambda:need(0==expected,'C_RHS_REQUIRED'))
    # A synthetic derivative on real prefix and finite reconstructed rows tests
    # raw equality/prefix/domain checks before a target-sized artifact exists.
    seven,eight,rows,vector=reference;derivative={'format':'ROOTED8_UNRESTRICTED_EXTENSION_UNIVERSAL5_PRODUCT_MODEL_V1','variables':old['variables']+[[8,mask] for mask in eight],'equations':old['equations']+[{'terms':row['terms'],'rhs_affine':row['rhs_affine']} for row in rows],'inherited_unrestricted_root7_model_sha256':PINS[OLD],'inherited_prefix':{'variables':2810,'rows':11769},'affine_RHS_coordinate_order':['constant','c','a','b'],'parameter_domain':old['parameter_domain']}
    verify(derivative,old,eight,rows,[],rows,[])
    damaged=copy.deepcopy(derivative);damaged['equations'][0]['rhs_affine'][0]+=1
    reject(controls,'copied_prefix_rhs','MODEL_COMPLETE_OPERATOR',lambda:verify(damaged,old,eight,rows,[],rows,[]))
    damaged=copy.deepcopy(derivative);damaged['variables'][0][1]+=1
    reject(controls,'copied_prefix_variable','MODEL_VARIABLES',lambda:verify(damaged,old,eight,rows,[],rows,[]))
    damaged=copy.deepcopy(derivative);damaged['affine_RHS_coordinate_order']=['constant','a','b']
    reject(controls,'dropped_c_coordinate','FULL_UNRESTRICTED_DOMAIN',lambda:verify(damaged,old,eight,rows,[],rows,[]))
    save(out/'independent_fixture_counts.json',raw_records)
    return {'actual_ordered_nonedge_roots':96,'rook_roots':36,'petersen_roots':60,'marked_row_calculations':mark_count,'ordered_product_row_calculations':product_count,'all_lower_isomorphism_checks':transports,'positive_prism_containing_order8_masks':sorted(prism_children),'nonzero_c_rhs_witness':{'rooted5_masks':list(pair),'exact_coefficient':expected},'strict_controls':controls,'synthetic_derivative_is_calibration_only':True,'full_catalogue_or_operator_checked':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('calibration','full'));ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--artifact-dir',type=Path);ap.add_argument('--producer-summary-sha256');ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');ap.add_argument('--catalogue-audit',type=Path);ap.add_argument('--catalogue-audit-sha256');args=ap.parse_args()
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent unrestricted root8 finite/newrow reconstruction; calibration100 or full260 seconds,20/40 reserve')
    reserve=20 if args.mode=='calibration' else 40;out=args.out.resolve();need(out.is_relative_to(ROOT),'BOUNDED_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={};stage='pins'
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>reserve,'DEADLINE','not completed within the allocated budget')
    def pin(name,expected=None):
        tick();name=Path(name).as_posix();actual=digest(ROOT/name);need(expected is None or actual==expected,'INPUT_PIN',name);pins[name]=actual;return actual
    def read(name):return json.loads((ROOT/name).read_bytes())
    def checkpoint(part,value):save(out/(part+'_'+str(value.get('completed_child_classes',value.get('completed_classes')))+'.json'),{'timestamp':datetime.now(timezone.utc).isoformat(),'progress':value,'deadline':deadline.status(),'target_resolution':False})
    try:
        for name,identity in PINS.items():pin(name,identity)
        for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml',CONTROL+'manifest.json','acceleration/results/20261003_rooted8_unrestricted_precontrols_supervisor02/summary.json']:
            pin(name)
        supervisor=read('acceleration/results/20261003_rooted8_unrestricted_precontrols_supervisor02/summary.json')
        need(supervisor['command_exit_code']==0 and supervisor['cleanup']['reaped'] is True and supervisor['cleanup']['job_active_zero_observed'] is True,'PRODUCER_PRECONTROLS_TERMINAL')
        old=read(OLD);seven=[row[1] for row in old['variables'] if len(row)==2 and row[0]==7]
        need(len(old['variables'])==2810 and len(old['equations'])==11769 and len(seven)==2770,'UNRESTRICTED_PREFIX_DIMENSIONS')
        need(seven==read('acceleration/results/20261002_rooted7_extension_model/catalogue.json')['complete_locally_admissible_masks'],'COMPLETE_UNRESTRICTED_PARENT_UNIVERSE')
        stage='finite_controls';controls=calibration(old,read(CONTROL+'fixture_controls.json'),out,tick)
        report={'timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','producer':'/root/structural','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'controls':controls,'target_resolution':False,'new_exclusions':0,'graph_realizability_asserted':False,'shared_components':['Pinned previous independently checked matrix/free-label orbit/DSU and all-isomorphism transport helpers, plus distinct overlap/private-set union helper; no producer imports.','Python exact integers, gzip/SHA256, uv locked environment and supported deadline/Job supervisor.'],'limitations':['Finite calibration checks all saved small-graph roots and exact negative controls; it does not establish the new full target operator or catalogue.','No target automorphism, prism-free premise, uniform secondary profile, optimizer result, graph construction or exclusion asserted.']}
        if args.mode=='calibration':report['status']='INDEPENDENT_UNRESTRICTED_ROOTED8_V1_PREOUTPUT_CALIBRATION_PASS'
        else:
            need(all((args.artifact_dir,args.producer_summary_sha256,args.calibration,args.calibration_sha256,args.catalogue_audit,args.catalogue_audit_sha256)),'FULL_EXACT_ARGUMENTS')
            pin(args.calibration,args.calibration_sha256);cal=read(args.calibration)
            need(cal['status']=='INDEPENDENT_UNRESTRICTED_ROOTED8_V1_PREOUTPUT_CALIBRATION_PASS' and cal['inputs_sha256'][Path(__file__).relative_to(ROOT).as_posix()]==pins[Path(__file__).relative_to(ROOT).as_posix()],'APPLICABLE_PREOUTPUT_CALIBRATION')
            directory=args.artifact_dir.as_posix().rstrip('/')+'/';pin(directory+'summary.json',args.producer_summary_sha256);summary=read(directory+'summary.json')
            for name,identity in summary['outputs_sha256'].items():pin(directory+name,identity)
            pin(args.catalogue_audit,args.catalogue_audit_sha256);coverage=read(args.catalogue_audit)
            need(coverage['status']=='INDEPENDENT_COMPLETE_UNRESTRICTED_ROOTED8_CATALOGUE_PASS' and coverage['inputs_sha256'][directory+'catalogue.json']==pins[directory+'catalogue.json'],'COMPLETE_INDEPENDENT_CATALOGUE_COVERAGE')
            catalog=read(directory+'catalogue.json');eight=catalog['complete_locally_admissible_masks'];offset=2810
            need(catalog['base_complete_root7_masks']==seven and catalog['prism_filter_applied'] is False,'FULL_PARENT_NO_PRISM_FILTER')
            profile=old['root6_nonedge_profile_basis'];origin={int(mask):value for mask,value in profile['origin'].items()};bases=[{int(mask):value for mask,value in row.items()} for row in profile['basis']]
            forced={mask:value[0] for mask,value in read(FORCED)['flag_counts']};need(len(forced)==87 and all(value[1]==1 for mask,value in read(FORCED)['flag_counts']),'EXACT_UNIVERSAL5_COUNTS')
            five=sorted(forced);six=sorted(origin);stage='orbit_maps';map5=independent_core.orbit_map(5,five,tick);map7=independent_core.orbit_map(7,seven,tick)
            stage='every_marked_transport';ext,tr,deleted=extensions(seven,eight,map7,offset,tick,checkpoint)
            stage='full_three_basis_products';prod,population=products(five,six,seven,eight,offset,map5,forced,origin,bases,tick,checkpoint)
            raw=read(directory+'model.json');raw_ext=read(directory+'extension_rows.json');raw_prod=read(directory+'product_rows.json');stage='raw_equality';verify(raw,old,eight,ext,prod,raw_ext,raw_prod)
            rejected=[]
            for label,which,mutate,diagnostic in [
                ('extension_coefficient','extension',lambda rows:rows[0]['terms'][0].__setitem__(1,2),'EXTENSION_COEFFICIENTS_OR_RHS'),
                ('extension_rhs','extension',lambda rows:rows[0]['rhs_affine'].__setitem__(0,rows[0]['rhs_affine'][0]+1),'EXTENSION_COEFFICIENTS_OR_RHS'),
                ('product_c_rhs','product',lambda rows:next(row for row in rows if row['rhs_affine'][1]).get('rhs_affine').__setitem__(1,0),'PRODUCT_COEFFICIENTS_OR_RHS'),
                ('product_collision','product',lambda rows:next(row for row in rows if row['known_root5_collision']).__setitem__('known_root5_collision',0),'PRODUCT_COEFFICIENTS_OR_RHS'),
                ('product_omission','product',lambda rows:rows.pop(),'PRODUCT_COEFFICIENTS_OR_RHS')]:
                damaged=copy.deepcopy(raw_ext if which=='extension' else raw_prod);mutate(damaged)
                reject(rejected,label,diagnostic,lambda:verify(raw,old,eight,ext,prod,damaged if which=='extension' else raw_ext,damaged if which=='product' else raw_prod))
            save(out/'reconstructed_rows.json',{'variables':raw['variables'],'extensions':ext,'products':prod,'every_lower_isomorphism_checks':tr,'free_deletions_checked':deleted,'ordered_union_pair_populations':population})
            report.update(status='INDEPENDENT_UNRESTRICTED_ROOTED8_MARKED_UNIVERSAL5_PRODUCT_MODEL_PASS',variables=len(raw['variables']),rows=len(raw['equations']),nonzeros=sum(len(row['terms']) for row in raw['equations']),inherited_rows=11769,marked_extension_rows=len(ext),upper_pair_product_rows=len(prod),every_lower_isomorphism_checks=tr,free_deletions_checked=deleted,ordered_union_pair_populations=population,raw_corruption_controls=rejected,outputs_sha256={'reconstructed_rows.json':digest(out/'reconstructed_rows.json')},statement='Every saved integer coefficient and constant,c,a,b right side of the frozen unrestricted rooted8 operator is a necessary local count equation at each ordered nonedge of a hypothetical srg(99,14,1,2), retaining the full2810-variable11769-row prefix and all651 primary rooted6 profiles, with secondary profiles varying by their actual pairs and without any prism-free or target-automorphism assumption.',scope='Complete unrestricted necessary localcount encoding only; count feasibility is not graph realization and no optimizer/certificate outcome is checked.')
            report['limitations'][0]='Complete new row operator independently reconstructed; pinned rooted5/rooted6/rooted7 results and separate catalogue coverage are reused, not re-proved.'
        report.update(elapsed_seconds=time.monotonic()-start,deadline=deadline.status());save(out/'summary.json',report)
        print(json.dumps({'status':report['status'],'sha256':digest(out/'summary.json'),'elapsed_seconds':report['elapsed_seconds'],'strict_controls':len(controls['strict_controls'])}))
    except BaseException as error:
        save(out/'failure.json',{'stage':stage,'error':repr(error),'timestamp':datetime.now(timezone.utc).isoformat(),'inputs_sha256':pins,'elapsed_seconds':time.monotonic()-start,'target_resolution':False});raise

if __name__=='__main__':main()
