"""Small exact reusable matrix rule; candidate evidence only."""
import argparse,hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
    if not x:raise ValueError(m)
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        s=sha(p);need(h is None or s==h,'identity');pins[key(p)]=s
    try:
        root=B/'20260930_first_third_proof_obstructions';pin(root/'summary.json','018b134a4f6682e177ba4c95cb98a77036e4a05c42735608cd07dc53af2f1951');prior=json.loads((root/'summary.json').read_bytes())
        A=[(0,0,1,1,0,1,0,0,0),(1,0,0,0,0,2,0,0,0)];BB=[(0,1,0,0,0,0,1,1,0),(1,0,0,0,0,0,0,2,0)]
        perm=[]
        for p in itertools.permutations(range(3)):perm.append(tuple(int(p[i]==j) for i in range(3) for j in range(3)))
        populations=[A,BB,A,BB,perm];target=(1,2,2,2,1,2,2,2,1);identity=(1,0,0,0,1,0,0,0,1);instances=[]
        for name,directory in [('first','20260930_eight_count_profile_lift'),('third','20260930_eight_count_profile_lift_third')]:
            p=B/directory/'model.json';pin(p,prior['inputs_sha256'][key(p)]);m=json.loads(p.read_bytes());groups=[g for g,d in enumerate(m['domains']) if 1 in d['support'] and 5 in d['support']];need(groups==[3,11,13,15,16],'literal groups');projection=[]
            for i,g in enumerate(groups):
                d=m['domains'][g];a=d['support'].index(1);b=d['support'].index(5);vals=[]
                for c in d['choices']:
                    v=[0]*9
                    for w in c['colour_words']:v[3*w[a]+w[b]]+=1
                    vals.append(tuple(v))
                need(set(vals)==set(populations[i]),'exact complete raw projection population');projection.append(vals)
            instances.append(dict(profile=name,groups=groups,coordinate_pair=[1,5],all_choice_projection_vectors=projection,forced_remaining_choices=[[j for j,v in enumerate(vals) if v==(A[0] if i in [0,2] else BB[0] if i in [1,3] else identity)] for i,vals in enumerate(projection)]))
        records=[];success=[]
        for choices in itertools.product(*[range(len(p)) for p in populations]):
            vectors=[populations[i][j] for i,j in enumerate(choices)];summed=tuple(map(sum,zip(*vectors)));r=dict(choice_indices=choices,sum=summed,meets_target=summed==target);records.append(r)
            if r['meets_target']:success.append(choices)
        need(len(records)==96 and success==[(0,0,0,0,perm.index(identity))],'unique exact block solution')
        controls=[]
        corrupted=[list(p) for p in populations];corrupted[0]=[A[1]]
        need(not any(tuple(map(sum,zip(*choice)))==target for choice in itertools.product(*corrupted)),'removed required vector gives no solution');controls.append('required-vector omission rejected')
        badtarget=list(target);badtarget[0]+=1;need(sum(badtarget)!=15,'wrong total target rejected');controls.append('wrong target total rejected')
        covariance=0
        for f in itertools.permutations(range(3)):
            def transport(v):
                out=[0]*9
                for i in range(3):
                    for j in range(3):out[3*f[i]+f[j]]=v[3*i+j]
                return tuple(out)
            ps=[[transport(v) for v in p] for p in populations];solutions=[choice for choice in itertools.product(*ps) if tuple(map(sum,zip(*choice)))==target];need(len(solutions)==1 and solutions[0][-1]==identity,'all six common fibre relabellings');covariance+=1
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:pin(p)
        save(out/'all96.json',records);save(out/'raw_instances.json',instances);save(out/'controls.json',dict(negative_controls=controls,fibre_maps=covariance))
        proof='The (1,1) cell receives no exceptional contribution, forcing P11=1. A3 permutation fixing1 is I or the0/2 swap. Write x as the number of second A choices and y as the number of second B choices. If P swaps0/2, cells(0,2) and(2,0) give x=y=1; cell(0,0) instead gives x+y=1, contradiction. Thus P=I. Then cells(0,2),(2,0) give x=y=0, so every exceptional choice is its first matrix.'
        save(out/'summary.json',dict(status='CANDIDATE_SHARED_BLOCK_IDENTITY_RULE',inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},populations=populations,target=target,unique_solution=success[0],combinations=96,proof=proof,scope='General five-population block implication; literal first/third profiles instantiate it. No exclusion or joint feasibility claim.',native_sat_calls=0,independent_approval=False));print(sha(out/'summary.json'))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
