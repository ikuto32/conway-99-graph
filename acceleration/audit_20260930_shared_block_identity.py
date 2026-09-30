"""Independent complete finite block rule and raw-domain projection audit."""
from pathlib import Path
from itertools import product, permutations
from datetime import datetime, timezone
import argparse, copy, hashlib, json, platform, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';D=B+'shared_block_identity/'
PINS={D+'summary.json':'0983223571fb4d513917695c46b79b95ef93b04272308e10dad9f1c182bd858f',B+'eight_count_profile_lift/model.json':'a7bd6776b6a5e54857a703bbbdc95fe433a1274e5c592484c0d990fdf4adefa4',B+'eight_count_profile_lift_third/model.json':'0a821d08532ece7d99bc5917a61af8dd0338379ab73a83c3687cbdf5ea480634',I+'eight_count_profile_lift_third/summary.json':'306e86ff14f7be929cd1f0f345b127b8cdf7341ae1e016b51499f2773654aab6',B+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'}
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def check_equal(a,b):need(a==b,'complete exact comparison')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,h=None):
        digest=sha(p);need(h is None or digest==h,'identity '+str(p));need(p not in pins or pins[p]==digest,'consistent pin');pins[str(p)]=digest
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(D+'summary.json')
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in summary[field].items():pin(p,h)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_SHARED_BLOCK_IDENTITY.md','uv.lock','pyproject.toml']:pin(p)
        # Authenticate the earlier independently checked first-profile domain via its registered evidence.
        import yaml
        ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_bytes());first=next(c for c in ledger['claims']if c['id']=='C-FIXED-HADAMARD-EIGHT-COUNT-PROFILE-GRAM-ENCODING')
        need(first['revision']==1 and first['status']=='VERIFIED'and first['review_state']=='CLEAR','first encoding premise')
        artifacts={x['id']:x for x in ledger['artifacts']}
        for aid in first['evidence']:
            art=artifacts[aid];pin(art['path'],art['sha256'])
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,solver_calls=0,limits_seconds=60))
        A=[(0,0,1,1,0,1,0,0,0),(1,0,0,0,0,2,0,0,0)];BB=[(0,1,0,0,0,0,1,1,0),(1,0,0,0,0,0,0,2,0)]
        Ps=[tuple(int(j==p[i])for i in range(3)for j in range(3))for p in permutations(range(3))];pops=[A,BB,A,BB,Ps];target=(1,2,2,2,1,2,2,2,1);identity=(1,0,0,0,1,0,0,0,1)
        check_equal(summary['populations'],[[list(v)for v in p]for p in pops]);check_equal(summary['target'],list(target))
        cases=[];solutions=[]
        for indices in product(range(2),range(2),range(2),range(2),range(6)):
            values=[pops[g][idx]for g,idx in enumerate(indices)];total=tuple(sum(v[j]for v in values)for j in range(9));ok=total==target
            cases.append(dict(choice_indices=list(indices),sum=list(total),meets_target=ok))
            if ok:solutions.append(list(indices))
            x,y=indices[0]+indices[2],indices[1]+indices[3];P=values[-1]
            need(total[2]==2-x+P[2]and total[6]==2-y+P[6]and total[0]==x+y+P[0]and total[4]==P[4],'all exact proof identities')
        need(len(cases)==96 and solutions==[[0,0,0,0,Ps.index(identity)]],'unique conditional solution');check_equal(cases,read(D+'all96.json'));check_equal(solutions[0],summary['unique_solution'])
        raw=read(B+'hadamard20_support/six_prism.json');need([raw['prescribed_Gram36'][12*f+1][12*h+5]for f in range(3)for h in range(3)]==list(target),'literal Gram block')
        instances=[];projection_count=0
        for label,directory in [('first','eight_count_profile_lift'),('third','eight_count_profile_lift_third')]:
            model=read(B+directory+'/model.json');gs=[g for g,x in enumerate(model['domains'])if 1 in x['support']and 5 in x['support']];need(gs==[3,11,13,15,16],'all raw contributor groups');projections=[];retained=[]
            for slot,g in enumerate(gs):
                domain=model['domains'][g];ia,ib=domain['support'].index(1),domain['support'].index(5);rows=[]
                for choice in domain['choices']:
                    words=choice['colour_words'];need(len(words)==3,'three literal columns')
                    values=[sum(int(word[ia]==f and word[ib]==h)for word in words)for f in range(3)for h in range(3)];rows.append(values);projection_count+=1
                need(set(map(tuple,rows))==set(pops[slot]),'complete projection population');want=pops[slot][solutions[0][slot]];retained.append([j for j,row in enumerate(rows)if tuple(row)==want]);projections.append(rows)
            need([len(x)for x in projections]==[48,48,48,48,150]and [len(x)for x in retained]==[36,36,36,36,6],'exact pruning populations')
            instances.append(dict(profile=label,groups=gs,coordinate_pair=[1,5],all_choice_projection_vectors=projections,forced_remaining_choices=retained))
        check_equal(instances,read(D+'raw_instances.json'));need(projection_count==684,'complete raw choices')
        for perm in permutations(range(3)):
            def transport(v):return tuple(v[3*perm[i]+perm[j]]for i in range(3)for j in range(3))
            transported=[[transport(v)for v in pop]for pop in pops];found=[vs for vs in product(*transported)if tuple(sum(v[j]for v in vs)for j in range(9))==target]
            need(len(found)==1 and found[0][-1]==identity,'all six simultaneous relabellings')
        bad=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError,IndexError,TypeError):bad.append(name)
            else:raise ValueError('corrupt control accepted '+name)
        wrong=copy.deepcopy(cases);wrong[1]['meets_target']=True;reject('extra_solution',lambda:check_equal(cases,wrong))
        wrong=copy.deepcopy(instances);wrong[0]['all_choice_projection_vectors'][0][0][0]+=1;reject('projection_entry',lambda:check_equal(instances,wrong))
        wrong=copy.deepcopy(instances);wrong[1]['forced_remaining_choices'][4]=wrong[1]['forced_remaining_choices'][4][:-1];reject('omitted_retained_choice',lambda:check_equal(instances,wrong))
        wrong=copy.deepcopy(instances);wrong[0]['groups'][0]=2;reject('contributor_group',lambda:check_equal(instances,wrong))
        reject('changed_target',lambda:check_equal(list(target),[2]+list(target[1:])))
        reject('incomplete_population',lambda:check_equal(cases,cases[:-1]))
        save(out/'controls.json',dict(rejected=bad,finite_cases=96,raw_projections=684,simultaneous_fibre_relabellings=6,per_profile_local_choices_before=[48,48,48,48,150],per_profile_local_choices_after=[36,36,36,36,6],broader_producer_analysis_reviewed=False))
        need(time.monotonic()-start<60,'audit limit');stamp=datetime.now(timezone.utc).isoformat()
        binding=dict(id='C-FIXED-HADAMARD-FIRST-THIRD-FORCED-BLOCK-IDENTITY',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For the five literal matrix populations A,B,A,B,S3 specified by the frozen shared_block_identity certificate (populations SHA256 bound through summary0983223571fb4d513917695c46b79b95ef93b04272308e10dad9f1c182bd858f), the sum equals2J-I iff all four exceptional matrices are their first listed choices and the permutation is I. At coordinate pair(1,5), the complete domains of the first and third eight-count profiles instantiate this implication, retaining36 of48 choices in each of groups3,11,13,15 and6 of150 choices in group16, in each profile.',scope='Conditional five-population integer matrix identity and two literal raw-domain instantiations; six common fibre relabellings. No profile exclusion or joint feasibility follows.',assumptions=['Exact two-vector A and B populations and the six permutation matrices in the pinned certificate.','Previously checked complete local domains for the first and third literal profiles on this fixed support.'],dependencies=[dict(id='C-FIXED-HADAMARD-EIGHT-COUNT-PROFILE-GRAM-ENCODING',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-THIRD-EIGHT-COUNT-PROFILE-GRAM-ENCODING',revision=1,relation='coverage')],verifier='/root',producer='/root/structural_attack',method='Separate integer entry proof, all96 tuples, all684 raw domain projections, six common fibre maps and changed-artifact controls.',shared_components=['Uses the prior independently checked domain coverage and raw model artifacts, without producer imports.','Python integer arithmetic, JSON, hashing; PyYAML only to resolve earlier registered evidence.'],inputs_sha256=pins,limitations=['Only this necessary block implication is approved; broader proof-core, propagation and LP diagnostics remain outside this review.','No whole-support or target exclusion; target automorphism is not assumed.'],created_at=stamp,updated_at=stamp);save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_SHARED_BLOCK_IDENTITY_PASS',timestamp=stamp,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT))for p in out.iterdir()if p.is_file()},finite_cases=96,raw_projections=684,fibre_relabellings=6,controls_rejected=len(bad),solver_calls=0,shared_components=binding['shared_components'],elapsed_seconds=time.monotonic()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT)),binding_sha256=sha((out/'claim_binding.json').relative_to(ROOT)))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__).relative_to(ROOT))));raise
if __name__=='__main__':main()
