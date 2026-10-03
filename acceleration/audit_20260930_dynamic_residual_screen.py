"""Independent literal partial-graph screens and isolated wrapper controls."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_variable_core_residual_screen_calibration'
PRODUCER=ROOT/'acceleration/theory_20260930_variable_core_residual_screen.py'
SUMMARY_SHA='2e4aff27fe39d03cb1f3baac2523e1bdffcba899ec6299eb991689d83bd76789'
POSITIVE_GATE=ROOT/'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json'
POSITIVE_SHA='28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'
def need(ok,message):
    if not ok:raise ValueError(message)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def graph_check(a,k):
    n=len(a);need(all(len(row)==n and all(type(x) is int and x in (0,1) for x in row) for row in a),'binary graph')
    need(all(a[i][i]==0 and sum(a[i])==k for i in range(n)) and all(a[i][j]==a[j][i] for i,j in combinations(range(n),2)),'simple regular graph')
    neighbours=[{j for j,x in enumerate(row) if x} for row in a]
    need(all(len(neighbours[i]&neighbours[j])==(k-2)*int(i==j)-a[i][j]+2 for i in range(n) for j in range(n)),'exact graph identity')

def expected_screen(c,f,degree):
    n=len(c);width=len(f[0]);need(all(len(row)==n and all(type(x) is int and x in (0,1) for x in row) for row in c),'literal core input')
    need(len(f)==n and all(len(row)==width and all(type(x) is int and x in (0,1) for x in row) for row in f),'literal factor input')
    nb=[set() for _ in range(n+width)]
    for a in range(n):
        nb[a].update(b for b,x in enumerate(c[a]) if x)
        for y in range(width):
            if f[a][y]:nb[a].add(n+y);nb[n+y].add(a)
    h=[[2-f[a][y]-len(nb[a]&nb[n+y]) for y in range(width)] for a in range(n)]
    t=[[len(nb[n+y]&nb[n+z]) for z in range(width)] for y in range(width)]
    negative=[dict(coordinate=a,vertex=y,value=h[a][y]) for a in range(n) for y in range(width) if h[a][y]<0]
    excessive=[dict(pair=[y,z],overlap=t[y][z]) for y,z in combinations(range(width),2) if t[y][z]>2]
    allowed=[[] for _ in range(width)];decisions=[]
    for y,z in combinations(range(width),2):
        ny=nb[n+y]|{n+z};nz=nb[n+z]|{n+y}
        forward=[a for a in range(n) if len(nb[a]&ny)+f[a][y]>2]
        reverse=[a for a in range(n) if len(nb[a]&nz)+f[a][z]>2]
        possible=len(ny&nz)+1<=2 and not forward and not reverse
        decisions.append(dict(pair=[y,z],overlap=t[y][z],failed_z_column_at_y=forward,failed_y_column_at_z=reverse,allowed=possible))
        if possible:allowed[y].append(z);allowed[z].append(y)
    degree_shortages=[];bounds=[];shortages=[]
    for y,neighbours in enumerate(allowed):
        if len(neighbours)<degree:degree_shortages.append(dict(vertex=y,allowed_neighbors=neighbours,available=len(neighbours),required=degree))
        for a in range(n):
            ones=[z for z in neighbours if f[a][z]==1];zeros=[z for z in neighbours if f[a][z]==0]
            lo=degree-min(degree,len(zeros));hi=min(degree,len(ones))
            item=dict(vertex=y,coordinate=a,allowed_count=len(neighbours),available_ones=len(ones),lower_for_fixed_degree=lo,upper_for_fixed_degree=hi,required=h[a][y]);bounds.append(item)
            if not lo<=h[a][y]<=hi:shortages.append({**item,'one_neighbors':ones,'zero_neighbors':zeros,'kind':'LOWER_BOUND_EXCEEDS_DEMAND' if h[a][y]<lo else 'UPPER_BOUND_BELOW_DEMAND'})
    return dict(H=h,T=t,allowed_edges_by_vertex=allowed,allowed_pair_decisions=decisions,residual_degree=degree,negative_deficits=negative,excessive_column_overlaps=excessive,degree_shortages=degree_shortages,coordinate_bounds=bounds,coordinate_shortages=shortages,rejection_found=bool(negative or excessive or degree_shortages or shortages))

def screen_check(raw,c,f,degree):
    expected=expected_screen(c,f,degree)
    for field,value in expected.items():need(json.dumps(raw[field],sort_keys=True)==json.dumps(value,sort_keys=True),'complete literal screen field '+field)
    return expected

def factor_check(c,f,m):
    n=3*m;width=m*(m-2)//2
    need(len(c)==n and all(len(row)==n and all(type(x) is int and x in (0,1) for x in row) for row in c),'core dimensions')
    need(len(f)==n and all(len(row)==width and all(type(x) is int and x in (0,1) for x in row) for row in f),'factor dimensions')
    need(all(c[a][a]==0 and all(c[a][b]==c[b][a] for b in range(n)) and all(sum(c[a][m*g:m*(g+1)])==1 for g in range(3)) for a in range(n)),'literal core prerequisites')
    need(all(sum(row)==m-2 for row in f) and all(sum(f[a][d] for a in range(m*g,m*(g+1)))==2 for g in range(3) for d in range(width)),'factor margins')
    full=[[0]*(3+n) for _ in range(3+n)]
    for a,b in combinations(range(3),2):full[a][b]=full[b][a]=1
    for a in range(n):
        full[a//m][3+a]=full[3+a][a//m]=1
        for b in range(n):full[3+a][3+b]=c[a][b]
    nb=[{j for j,x in enumerate(row) if x} for row in full]
    need(all(sum(x*y for x,y in zip(f[a],f[b]))==m*int(a==b)-c[a][b]+2-len(nb[3+a]&nb[3+b]) for a in range(n) for b in range(n)),'all raw factor Gram entries')
    return dict(core_vertices=n,factor_columns=width,Gram_entries=n*n,cell_size=m)

def quota_controls():
    cases=0
    for n in range(7):
        for ones in range(n+1):
            bits=[1]*ones+[0]*(n-ones)
            for degree in range(9):
                actual={sum(bits[i] for i in subset) for subset in combinations(range(n),degree)}
                lo=degree-min(degree,n-ones);hi=min(degree,ones)
                need(actual==set(range(lo,hi+1)),'complete quota subset range');cases+=1
    return dict(parameter_cases=cases,allowed_population_sizes=list(range(7)),degree_values=list(range(9)),includes_degrees_larger_than_population=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        p=Path(p);value=digest(p);need(expected is None or value==expected,'hash '+str(p));bindings[key(p)]=value;return p
    try:
        summary=read(bind(D/'summary.json',SUMMARY_SHA))
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():bind(ROOT/p,h)
        bind(ROOT/'acceleration/theory_20260930_full_srg_validator.py','c0e070aa1ac39e8860b52a7f5e086b3e8da5e01f83d0f4fe76ab1e91c077279b')
        positive_gate=read(bind(POSITIVE_GATE,POSITIVE_SHA));need(positive_gate['status']=='INDEPENDENT_SRG243_NONEMPTY_RESIDUAL_FIXTURE_PASS','independently accepted nonempty generalized control')
        for p,h in positive_gate['inputs_sha256'].items():bind(ROOT/p,h)
        rook=read(D/'rook_triangle_factor_fixture.json');graph_check(rook['full_valid_adjacency'],4);empty=factor_check(rook['core'],rook['factor'],2)
        generic=read(D/'rook_nonempty_residual_fixture.json');graph_check(generic['full_valid_adjacency'],4)
        a=generic['full_valid_adjacency'];x=generic['known_indices'];y=generic['residual_indices']
        need(sorted(x+y)==list(range(9)) and generic['core']==[[a[i][j] for j in x] for i in x] and generic['factor']==[[a[i][j] for j in y] for i in x] and generic['actual_residual_adjacency']==[[a[i][j] for j in y] for i in y],'literal nonempty rook extraction')
        checked=screen_check(generic['screen'],generic['core'],generic['factor'],2)
        need(not checked['rejection_found'] and checked['H']==generic['literal_H'] and checked['T']==generic['literal_T'],'known residual satisfies screen')
        corrupt=[]
        for name in ['H','T','allowed_edges_by_vertex','allowed_pair_decisions','coordinate_bounds','coordinate_shortages']:
            bad=deepcopy(generic['screen'])
            if name in ['H','T']:bad[name][0][0]+=1
            elif name=='allowed_edges_by_vertex':bad[name][0].pop()
            elif name=='allowed_pair_decisions':bad[name][0]['failed_y_column_at_z']=[0]
            elif name=='coordinate_bounds':bad[name][0]['lower_for_fixed_degree']-=1
            else:bad[name].append({'false_shortage':True})
            try:screen_check(bad,generic['core'],generic['factor'],2)
            except ValueError:corrupt.append(name)
            else:raise ValueError('corrupt screen accepted '+name)
        blocks_path=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json';blocks=read(blocks_path)
        large=factor_check(blocks['cubic_core60'],blocks['factor60x180'],20)
        # Isolated execution tests producer behavior; independent expectations above import none of it.
        probe=args.out/'producer_calibration_probe.py'
        probe.write_text("import json,sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(sys.argv[1])/'acceleration'))\nfrom theory_20260930_variable_core_residual_screen import validate_factor,compute_screen\nb=json.loads(Path(sys.argv[2]).read_bytes())\nr={'label':'GENERALIZED243_CALIBRATION_ONLY_NOT_RESEARCH99','validation':validate_factor(b['cubic_core60'],b['factor60x180'],20,research=False),'screen':compute_screen(b['cubic_core60'],b['factor60x180'],16)}\nwith Path(sys.argv[3]).open('x',encoding='utf-8') as f:json.dump(r,f)\n",encoding='utf-8')
        probe_result=args.out/'producer243_probe.json';command=[sys.executable,str(probe),str(ROOT),str(blocks_path),str(probe_result)]
        proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60);(args.out/'producer_probe.stdout.log').write_bytes(proc.stdout);(args.out/'producer_probe.stderr.log').write_bytes(proc.stderr);need(proc.returncode==0,'isolated generalized producer control execution')
        probe_raw=read(probe_result);large_screen=screen_check(probe_raw['screen'],blocks['cubic_core60'],blocks['factor60x180'],16);need(not large_screen['rejection_found'],'real243 residual survives all necessary bounds')
        f=blocks['factor60x180'];d=blocks['residual180x180']
        for v in range(180):
            actual=[z for z in range(180) if d[v][z]];need(len(actual)==16 and set(actual)<=set(large_screen['allowed_edges_by_vertex'][v]),'every actual residual edge retained')
            need(all(sum(f[r][z] for z in actual)==large_screen['H'][r][v] for r in range(60)),'all actual243 residual demands')
        quota=quota_controls();controls_dir=args.out/'malformed_cli_controls';controls_dir.mkdir();cli=[]
        tiny={'core_adjacency':[[0]],'incidence_matrix':[[]],'calibration_only':True}
        for name in ['wrong_gate_hash','wrong_gate_status','unbound_factor','wrong_factor_hash','malformed_factor_shape','Boolean_core','asymmetric_core','wrong_factor_margin']:
            directory=controls_dir/name;directory.mkdir();factor=tiny
            if name in ['Boolean_core','asymmetric_core','wrong_factor_margin']:
                c=[[0]*36 for _ in range(36)]
                for r in range(36):
                    c[r][12*(r//12)+(r%12^1)]=1
                    for g in range(3):
                        if g!=r//12:c[r][12*g+r%12]=1
                if name=='Boolean_core':c[0][0]=False
                elif name=='asymmetric_core':c[0][1]=0
                factor={'core_adjacency':c,'incidence_matrix':[[0]*60 for _ in range(36)],'calibration_only':True}
            fp=directory/'synthetic_factor.json';save(fp,factor)
            gate={'status':'INDEPENDENT_VARIABLE_CORE_FACTOR_SAT_OBJECT_PASS','inputs_sha256':{key(fp):digest(fp)},'_calibration_only':'Artificial gate used only to reach a rejection stage; no actual research approval.'}
            if name=='wrong_gate_status':gate['status']='CALIBRATION_ONLY_NOT_ACCEPTED_FACTOR'
            elif name=='unbound_factor':gate['inputs_sha256']={}
            elif name=='wrong_factor_hash':gate['inputs_sha256'][key(fp)]='0'*64
            gp=directory/'synthetic_gate.json';save(gp,gate);gh='0'*64 if name=='wrong_gate_hash' else digest(gp)
            cmd=[sys.executable,str(PRODUCER),'screen','--factor',str(fp),'--factor-gate',str(gp),'--factor-gate-sha256',gh,'--out',str(directory/'producer_output')]
            result=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30);(directory/'stdout.log').write_bytes(result.stdout);(directory/'stderr.log').write_bytes(result.stderr)
            expected={'wrong_gate_hash':'exact factor audit identity','wrong_gate_status':'actual independently accepted arbitrary-core factor','unbound_factor':'factor bytes bound','wrong_factor_hash':'factor bytes bound','malformed_factor_shape':'core shape','Boolean_core':'core binary entries','asymmetric_core':'core symmetry and diagonal','wrong_factor_margin':'exact factor row margins'}[name]
            need(result.returncode!=0 and expected in result.stderr.decode('utf-8'),'actual CLI rejects intended malformed control '+name)
            need(not (directory/'producer_output/screen.json').exists(),'no completed screen produced by rejected control')
            cli.append(dict(control=name,command=cmd,exit_code=result.returncode,expected_error=expected,stdout_sha256=digest(directory/'stdout.log'),stderr_sha256=digest(directory/'stderr.log')))
        save(args.out/'independent_screen_checks.json',dict(rook=checked,SRG243=large_screen,quota=quota,screen_corruptions_rejected=corrupt,malformed_CLI_controls=cli))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_DYNAMIC_RESIDUAL_SCREEN.md',probe,probe_result]:bind(p)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'stable frozen inputs')
        report=dict(status='INDEPENDENT_DYNAMIC_RESIDUAL_SCREEN_AUDIT_PASS',claim_id='C-DYNAMIC-TRIANGLE-RESIDUAL-SCREEN-NECESSITY',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/eight_domain_audit independent literal partial-adjacency and quota reviewer',recommendation='VERIFIED',review_state='CLEAR',kind='mathematical result',basis=['DERIVED','COMPUTED'],
          statement='For any specified valid triangle39core factor F, every residual60 completion lies in the saved symmetric permitted-edge graph, and every coordinate demand at each vertex lies between max(0,8-(N-p)) and min(8,p). Negative deficits, overlap>2, degree shortages or a demand outside these bounds exclude exactly that supplied factor.',
          dependencies=[dict(id='C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE',revision=1,relation='uses_result')],scope='Necessary local completion bounds for an authenticated supplied factor; no research factor or exclusion produced here.',
          checks=dict(empty_rook_factor=empty,nonempty_rook_pairs=3,nonempty243_factor=large,nonempty243_pairs=16110,nonempty243_coordinate_bounds=10800,all_actual243_residual_edges_retained=True,quota=quota,screen_corruptions_rejected=corrupt,malformed_CLI_controls=cli),
          generalized_producer_probe=dict(command=command,exit_code=proc.returncode,calibration_only=True,research_factor=False),independent_expected_computation_imports_producer=False,
          shared_components=['Independent expectations use literal neighbour-set intersections and explicit edge insertion.','Producer executed only in separately saved black-box calibration/rejection probes.','Imported producer utility transitively loads full_srg_validator; omitted original manifest entry is now explicitly pinned.'],
          gate_trust_boundary='The caller must supply a genuine independent object gate; matching a caller-provided digest does not cryptographically authenticate reviewer identity.',
          evidence_path=key(args.out/'independent_screen_checks.json'),evidence_sha256=digest(args.out/'independent_screen_checks.json'),
          limitations=['No actual36x60research factor exists in these controls.','SRG243 is a different positive-control family with residual degree16.','No local row-domain search, residual SAT instance or complete residual quadratic solve is approved.','Every future claimed obstruction still requires checking its exact admitted factor and raw witness; passing the screen never proves feasibility.'],solver_calls=0,research_screens=0,row_domain_searches=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as error:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(error),inputs_sha256=bindings));raise

if __name__=='__main__':main()
