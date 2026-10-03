"""Independent root-proposed conditional GF2 theorem and raw controls."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def need(ok,msg):
    if not ok:raise ValueError(msg)

def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')

def rank(a):
    rows=len(a);cols=len(a[0])if rows else 0;basis={};pivot_columns=[]
    for j in range(cols):
        raw=sum((a[i][j]%2)<<i for i in range(rows));value=raw;comb=1<<j
        while value:
            top=value.bit_length()-1
            if top not in basis:basis[top]=(value,comb);pivot_columns.append(j);break
            value^=basis[top][0];comb^=basis[top][1]
    for pivot,(value,comb)in basis.items():
        check=0
        for j in range(cols):
            if(comb>>j)&1:check^=sum((a[i][j]%2)<<i for i in range(rows))
        need(check==value and value.bit_length()-1==pivot,'exact column elimination identity')
    return dict(rank=len(basis),pivot_columns=pivot_columns,basis=[dict(pivot=pivot,value=str(value),input_column_combination=str(comb))for pivot,(value,comb)in sorted(basis.items())])

def mixed(c,f):
    return [[(f[i][j]+sum(c[i][k]*f[k][j]for k in range(len(c))))%2 for j in range(len(f[0]))]for i in range(len(c))]

def premise(c,f,claimed=None):
    n=len(c)//3;m=len(f[0]);need(n>0 and len(c)==3*n and len(f)==3*n,'three cells')
    need(all(len(row)==3*n and all(type(x)is int and x in(0,1)for x in row)for row in c),'binary square C')
    need(all(len(row)==m and all(type(x)is int and x in(0,1)for x in row)for row in f),'binary field F')
    for g in range(3):
        need(all(sum(f[i][d]for i in range(g*n,(g+1)*n))%2==0 for d in range(m)),'cell left-kernel parity')
        need(all(sum(c[i][j]for i in range(g*n,(g+1)*n))%2==1 for j in range(3*n)),'required left action')
    certificate=rank(f);need(certificate['rank']==3*n-3,'maximal binary rank')
    if claimed is not None:need(certificate['rank']==claimed,'claimed rank identity')
    h=mixed(c,f);need(rank([a+b for a,b in zip(f,h)])['rank']==certificate['rank'],'column-space consistency consequence')
    return h,certificate

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    fixture=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json';gate=ROOT/'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json'
    need(digest(fixture)=='3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439','fixture identity');need(digest(gate)=='28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e','independent fixture gate')
    raw=json.loads(fixture.read_bytes());c=raw['cubic_core60'];f=raw['factor60x180'];d=raw['residual180x180'];h,certificate=premise(c,f,57)
    fmask=[sum(x<<j for j,x in enumerate(row))for row in f];dmasks=[sum(d[k][j]<<k for k in range(180))for j in range(180)]
    actual=[[(fmask[i]&dmasks[j]).bit_count()%2 for j in range(180)]for i in range(60)];need(actual==h,'actual243 mixed witness')
    lowc=[[0]*12 for _ in range(12)]
    for g in range(3):
        for i in range(4):
            lowc[4*g+i][4*g+(i^1)]=1
            for other in range(3):
                if other!=g:lowc[4*g+i][4*other+i]=1
    u=[int(i%4 in(0,2))for i in range(12)];lowf=[[x]*4 for x in u];lowh=mixed(lowc,lowf)
    need(lowh==[[1]*4 for _ in range(12)] and rank(lowf)['rank']==1 and rank([a+b for a,b in zip(lowf,lowh)])['rank']==2,'exact lower-rank inconsistency')
    need(all(sum(lowf[i][j]for i in range(4*g,4*g+4))==2 for g in range(3)for j in range(4)),'lower control cell margins')
    save(args.out/'raw_controls.json',dict(known243_rank=certificate,known243_mixed_rhs_mod2=h,lower_rank=dict(n=4,C=lowc,F=lowf,H=lowh,rank_F=1,augmented_rank=2,prescribed_Gram_claim=False,target_factor_claim=False)))
    small=0
    for entries in product((0,1),repeat=6):
        a=[list(entries[:3]),list(entries[3:])];columns=[a[0][j]+2*a[1][j]for j in range(3)]
        span={0}
        for col in columns:span|={v^col for v in list(span)}
        need(2**rank(a)['rank']==len(span),'complete tiny rank/span calibration');small+=1
    rejected=[]
    for label in('odd_cell','wrong_left_action','wrong_rank','lower_rank'):
        cc=deepcopy(c);ff=deepcopy(f);claimed=57
        if label=='odd_cell':ff[0][0]^=1
        elif label=='wrong_left_action':cc[0][1]^=1
        elif label=='wrong_rank':claimed=56
        else:cc,ff,claimed=lowc,lowf,None
        try:premise(cc,ff,claimed)
        except ValueError as e:rejected.append(dict(control=label,reason=str(e)))
        else:raise AssertionError(label)
    changed=deepcopy(h);changed[0][0]^=1;need(changed!=actual,'changed mixed RHS rejected');rejected.append(dict(control='changed_mixed_rhs',reason='Actual independently verified D fails the altered equation.'))
    inputs=[Path(__file__),ROOT/'docs/AUDIT_20260930_TRIANGLE_GF2_MAXRANK.md',fixture,gate,ROOT/'uv.lock',ROOT/'pyproject.toml'];now=datetime.now(timezone.utc).isoformat()
    statement='For every GF2 matrix F with three disjoint nonempty n-row cell indicators r_i satisfying r_i^T F=0 and rank(F)=3n-3, and every C satisfying r_i^T C=j^T, there is a GF2 matrix D with FD=2J-(I+C)F.'
    report=dict(status='INDEPENDENT_TRIANGLE_GF2_MAXRANK_MIXED_CONSISTENCY_PASS',claim_id='C-TRIANGLE-GF2-MAXIMAL-RANK-MIXED-CONSISTENCY',claim_revision=1,statement=statement,kind='mathematical result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='Conditional linear solvability over GF2; valid triangle cores supply the left-action premise by symmetry, and valid factors supply even cell-column parity. Full binary rank remains an explicit premise.',assumptions=['The three n-row cells are nonempty and disjoint.','Required action is r_i^T C=j^T; C r_i=j alone requires symmetry to imply it.','No nontrivial target automorphism is assumed.'],dependencies=[dict(id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL',revision=1,relation='verification_dependency')],verifier='/root/state_literature_audit independent derivation of root-proposed lemma',method='independent_derivation_and_artifact_check',written_audit='docs/AUDIT_20260930_TRIANGLE_GF2_MAXRANK.md',controls=dict(known243_binary_rank=57,known243_actual_D_checks=10800,all_two_by_three_binary_matrices=small,negative_controls=rejected,lower_rank_counterexample_augmented_rank=2),shared_components=['Python standard library only; independently approved raw243 fixture; no producer elimination or scoring imports.'],limitations=['No symmetric or zero-diagonal D is established.','Field solvability is not exact integer or binary graph completion; residual degrees and quadratic equations are omitted.','Lower-rank factors are not covered.','Lower-rank countercontrol is not asserted to satisfy a prescribed target Gram.','No novelty, target construction, exclusion or coverage claim.'],created_at=now,updated_at=now,timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256={p.resolve().relative_to(ROOT).as_posix():digest(p)for p in inputs},outputs_sha256={str((args.out/'raw_controls.json').resolve().relative_to(ROOT).as_posix()):digest(args.out/'raw_controls.json')},artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

if __name__=='__main__':main()
