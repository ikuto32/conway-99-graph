"""Independent complete integer Farkas checking from raw fixed support domains."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
GATE=B/'20260930_independent_review/hadamard20_support_v2/summary.json'
GH='a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f'
CASES=[('connected_01','2e839fda408da18e3689ffef00de647644375a000d308f4ea306b2cbdfa37e49','20260930_hadamard_support_lp','20260930_hadamard_support_lp_dual_repair/certificate.json',-37617760),('connected_02','bdd3faa4c01f58f67118414251a4bc57e2f42702c6346716ea96ec7bf24565f4','20260930_hadamard_support_remaining_lp/connected_02','20260930_hadamard_support_remaining_lp/connected_02/integer_repaired_certificate.json',-7174717),('connected_03','b2c1c638b8eac68151260dc50012fc48a7c78a594702862af4e08e57179d5ae2','20260930_hadamard_support_remaining_lp/connected_03','20260930_hadamard_support_remaining_lp/connected_03/integer_repaired_certificate.json',-863)]
def need(x,s):
    if not x:raise ValueError(s)
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def gram_from_core(c,coefficient):
    h=len(c);n=h//3;need(h%3==0 and all(len(row)==h and all(type(v)is int and v in (0,1) for v in row) for row in c),'literal raw core')
    nb=[{j for j,v in enumerate(row) if v} for row in c]
    need(all(i not in nb[i] and len(nb[i])==3 and all((j in nb[i])==(i in nb[j]) for j in range(h)) for i in range(h)),'simple symmetric cubic core')
    return [[coefficient*int(i==j)+2-c[i][j]-len(nb[i]&nb[j])-int(i//n==j//n) for j in range(h)] for i in range(h)]

def reconstruct(raw):
    ms=raw['matchings'];need(len(ms)==3 and all(len(m)==12 and sorted(m)==list(range(12)) and all(m[i]!=i and m[m[i]]==i for i in range(12)) for m in ms),'all three perfect matchings')
    c=[[int((i//12==j//12 and ms[i//12][i%12]==j%12) or (i//12!=j//12 and i%12==j%12)) for j in range(36)] for i in range(36)]
    need(c==raw['core_adjacency'],'complete identity-cross core')
    gram=gram_from_core(c,12);need(gram==raw['prescribed_Gram36'],'independent prescribed Gram')
    l=raw['L'];need(len(l)==12 and all(len(row)==60 and sum(row)==30 and all(type(v)is int and v in (0,1) for v in row) for row in l),'binary fixed L and row30')
    coords=[[a for a in range(12) if l[a][y]] for y in range(60)];need(all(len(v)==6 for v in coords) and coords==raw['support_columns'],'all fixed support columns')
    choices=[];rejected=0
    for y,points in enumerate(coords):
        local=[]
        for a in combinations(points,2):
            rest=[v for v in points if v not in a]
            for b in combinations(rest,2):
                parts=[a,b,tuple(v for v in rest if v not in b)]
                selected=tuple(sorted(12*g+v for g,part in enumerate(parts) for v in part))
                if any(gram[i][j]==0 for i,j in combinations(selected,2)):rejected+=1;continue
                colors=[next(g for g,part in enumerate(parts) if v in part) for v in points]
                local.append(dict(fibres_by_sorted_coordinate=colors,rows=list(selected),row_mask_hex=format(sum(1<<i for i in selected),'09x')))
        local.sort(key=lambda o:o['fibres_by_sorted_coordinate'])
        need(local==raw['column_colour_options'][y] and local,'entire independently generated domain')
        choices.append(local)
    pairs=[(i,j) for i in range(36) for j in range(i,36)];rhs=[1]*60+[gram[i][j] for i,j in pairs]
    columns=[];selectors=[]
    for y,options in enumerate(choices):
        for j,option in enumerate(options):
            support=set(option['rows']);columns.append([y]+[60+k for k,(a,b) in enumerate(pairs) if a in support and b in support]);selectors.append([y,j])
    need(all(len(v)==22 and v==sorted(set(v)) for v in columns),'onehot plus21 pair contributions each')
    model=dict(nonnegative_variables=True,columns_nonzero_row_indices=columns,rhs=rhs,selectors=selectors,Gram_row_pairs=[list(p) for p in pairs],variables=len(columns),equations=726,binary_coefficients=True)
    return model,dict(balanced_candidates=5400,zero_Gram_rejections=rejected,retained_choices=len(columns),literal_matrix_nonzeros=sum(map(len,columns)))

def dual(columns,rhs,y):
    need(len(y)==len(rhs) and all(type(v)is int for v in y),'complete integer dual')
    need(all(type(v)is int for v in rhs),'integer RHS')
    need(all(col==sorted(set(col)) and all(type(i)is int and 0<=i<len(rhs) for i in col) for col in columns),'exact binary matrix column format')
    dots=[sum(y[i] for i in col) for col in columns];right=sum(y[i]*b for i,b in enumerate(rhs))
    need(dots and min(dots)>=0,'all independent column dual products nonnegative')
    need(right<0,'strictly negative integer RHS product')
    return dots,right
def matches_model(actual,expected):need(actual==expected,'all exact model fields and coefficients')
def matches_stats(cert,dots,right):
    need(cert['column_dots']==dots and cert['rhs_dot']==right and cert['minimum_column_dot']==min(dots),'all reported certificate products')

def controls():
    columns=[[0,1]];rhs=[0,1];dots,right=dual(columns,rhs,[1,-1]);need(dots==[0] and right==-1,'tiny genuine Farkas positive')
    feasible=0
    for bits in product(range(2),repeat=4):
        cols=[[r for r in range(2) if bits[2*r+j]] for j in range(2)]
        for x in product(range(3),repeat=2):
            b=[sum(x[j] for j,col in enumerate(cols) if r in col) for r in range(2)]
            for y in product(range(-2,3),repeat=2):
                try:dual(cols,b,list(y))
                except ValueError:feasible+=1
                else:raise ValueError('false infeasibility on planted exact positive')
    need(feasible==3600,'complete tiny positive population')
    return dict(valid_infeasible_certificate=dict(columns=columns,rhs=rhs,dual=[1,-1],column_dots=dots,rhs_dot=right),planted_feasible_dual_cases=feasible)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={}
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'artifact pin '+key(p));bindings[key(p)]=value
    def closure(p,h=None):
        pin(p,h);d=read(p)
        for name in ['inputs_sha256','outputs_sha256']:
            for path,value in d.get(name,{}).items():pin(ROOT/path,value)
        return d
    try:
        gate=closure(GATE,GH);need(gate['status']=='INDEPENDENT_HADAMARD20_SUPPORT_AND_PROJECTION_PASS','independent support premise')
        closure(B/'20260930_hadamard_support_lp/summary.json','6635fbf58098292d6510af828bda4e488450c19bc3a6ecdb1c40359c16fe02df')
        closure(B/'20260930_hadamard_support_lp/manifest.json')
        closure(B/'20260930_hadamard_support_lp_dual_repair/summary.json','c38c285f22806526b6be3cca45f368935ce26144de1aad859c1d22d3316059ce')
        closure(B/'20260930_hadamard_support_lp_dual_repair/manifest.json')
        closure(B/'20260930_hadamard_support_remaining_lp/summary.json','e59bdb11ed29df23e787624257150c25854005c24f6e29f644b4cc498727c0fc')
        control=controls();rejected=[];case_records=[];claims=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError):rejected.append(label)
            else:raise ValueError('accepted corrupted control '+label)
        for name,rawsha,folder,certname,target in CASES:
            rawpath=B/'20260930_hadamard20_support'/f'{name}.json';pin(rawpath,rawsha);raw=read(rawpath);expected,counts=reconstruct(raw)
            modelpath=B/folder/'exact_model.json';pin(modelpath);model=read(modelpath);matches_model(model,expected)
            certpath=B/certname;pin(certpath);cert=read(certpath);dots,right=dual(expected['columns_nonzero_row_indices'],expected['rhs'],cert['values']);matches_stats(cert,dots,right);need(right==target,'exact recorded negative bound')
            for label in ['zero_dual','wrong_sign','missing_dual','Boolean_dual']:
                y=cert['values'][:]
                if label=='zero_dual':y=[0]*len(y)
                elif label=='wrong_sign':y=[-v for v in y]
                elif label=='missing_dual':y.pop()
                else:y[0]=bool(y[0])
                reject(name+'_'+label,lambda y=y:dual(expected['columns_nonzero_row_indices'],expected['rhs'],y))
            for label in ['changed_RHS','deleted_column','changed_coefficient']:
                bad=deepcopy(model)
                if label=='changed_RHS':bad['rhs'][0]+=1
                elif label=='deleted_column':bad['columns_nonzero_row_indices'].pop()
                else:bad['columns_nonzero_row_indices'][0].pop()
                reject(name+'_'+label,lambda bad=bad:matches_model(bad,expected))
            badraw=deepcopy(raw);badraw['column_colour_options'][0].pop();reject(name+'_deleted_domain',lambda:reconstruct(badraw))
            bad=deepcopy(cert);bad['column_dots'][0]+=1;reject(name+'_reported_product',lambda:matches_stats(bad,dots,right))
            record=dict(core=name,raw_support_path=key(rawpath),raw_support_sha256=rawsha,model_path=key(modelpath),model_sha256=digest(modelpath),certificate_path=key(certpath),certificate_sha256=digest(certpath),equations=726,variables=len(dots),domain_counts=counts,all_column_dots=dots,minimum_column_dot=min(dots),maximum_column_dot=max(dots),rhs_dot=right,complete_independent_matrix_reconstruction=True)
            save(out/f'{name}_exact_check.json',record);case_records.append(record)
        # Genuine positive system, using only each actual243 column option.
        fp=B/'20260930_srg243_residual_fixture/triangle_blocks.json';pin(fp,'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439')
        pin(B/'20260930_independent_review/srg243_residual_fixture/summary.json','28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e')
        raw243=read(fp);g=gram_from_core(raw243['cubic_core60'],20);f=raw243['factor60x180'];pairs=[(i,j) for i in range(60) for j in range(i,60)]
        positive_columns=[]
        for y in range(180):
            rows={i for i,row in enumerate(f) if row[y]};need(len(rows)==6,'243six selectedrows')
            positive_columns.append([y]+[180+i for i,(a,b) in enumerate(pairs) if {a,b}<=rows])
        positive_rhs=[1]*180+[g[i][j] for i,j in pairs];observed=[0]*2010
        for col in positive_columns:
            for i in col:observed[i]+=1
        need(observed==positive_rhs,'all2010 actual243 primal equations')
        reject('243_zero_dual_not_exclusion',lambda:dual(positive_columns,positive_rhs,[0]*2010))
        bady=[0]*2010;bady[0]=-1;reject('243_negative_primal_row_not_exclusion',lambda:dual(positive_columns,positive_rhs,bady))
        save(out/'known243_positive_system.json',dict(scope='Only180actual known243 column choices, not full coloring domain, not research99',columns=positive_columns,rhs=positive_rhs,primal=[1]*180))
        save(out/'controls.json',dict(**control,known243_positive_equations=2010,known243_variables=180,corruptions_rejected=rejected))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_SUPPORT_FARKAS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();report=dict(status='INDEPENDENT_THREE_FIXED_HADAMARD_SUPPORT_FARKAS_EXCLUSIONS_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},cases=[{k:v for k,v in r.items() if k!='all_column_dots'} for r in case_records],excluded_fixed_supports=3,excluded_cores=0,complete_target_graphs=0,verifier='/root/state_literature_audit',method='independent_exact_domain_matrix_and_integer_certificate_check',shared_components=['Python standard library only; no producer LP, repair, encoding, matrix or solver imports.','Independent support and genuine243 artifact gates explicitly bound.'],recommendation='VERIFIED',review_state='CLEAR',artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0,limitations=['Exactly three saved fixed supports; no whole core or Hadamard family exclusion.','Outside-column caps and residual D omitted from the infeasible relaxation.','Floating results/failed reconstruction are preserved provenance, not mathematical premises.','Unsearched connected01 CNF remains candidate; its full encoding was not audited or promoted.'])
        save(out/'summary.json',report)
        for record in case_records:
            cid='C-FIXED-HADAMARD-'+record['core'].replace('_','').upper()+'-SUPPORT-EXCLUSION'
            claims.append(dict(id=cid,revision=1,statement=f"The exact726-equality nonnegative selector system for the saved {record['core']} coordinate support L and its complete zero-Gram-compatible coloring domains has no solution: the bound integer726-vector has all{record['variables']}column products nonnegative and RHS product{record['rhs_dot']}; therefore no binary prescribed-Gram factor can have this fixed support.",kind='exclusion',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='Only the literal raw support/core and equality system pinned in this record; no core-wide or target-wide exclusion.',assumptions=['No nontrivial target automorphism is assumed.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='verification_dependency'),dict(id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION',revision=1,relation='uses_result'),dict(id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL',revision=1,relation='verification_dependency')],evidence=[dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json'),availability='LOCAL_ONLY'),dict(path=key(out/f"{record['core']}_exact_check.json"),sha256=digest(out/f"{record['core']}_exact_check.json"),availability='LOCAL_ONLY')],exact_scope_hashes={record['raw_support_path']:record['raw_support_sha256'],record['model_path']:record['model_sha256'],record['certificate_path']:record['certificate_sha256']},verifier=report['verifier'],method=report['method'],limitations=report['limitations'],created_at=now,updated_at=now))
        save(out/'claim_bindings.json',dict(claims=claims,ledger_changed=False));print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'),binding_sha256=digest(out/'claim_bindings.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
