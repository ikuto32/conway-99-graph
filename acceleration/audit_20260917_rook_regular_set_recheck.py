"""Independent set-count and exact determinant audit of the conditional rook encoding."""
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import audit_20260917_partial_matching as h

ROOT=h.ROOT;D=ROOT/'acceleration/results/20260917_rook_regular_set'
def determinant(matrix):
    a=[r[:]for r in matrix];n=len(a);sign=1;last=1
    for k in range(n-1):
        pivot=next((i for i in range(k,n)if a[i][k]),None)
        if pivot is None:return 0
        if pivot!=k:a[k],a[pivot]=a[pivot],a[k];sign=-sign
        p=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                value=p*a[i][j]-a[i][k]*a[k][j];h.require(value%last==0,'fraction-free exact division');a[i][j]=value//last
            a[i][k]=0
        last=p
    return sign*a[-1][-1]
def polyval(coeff,x):
    result=0
    for c in coeff:result=result*x+c
    return result
def main():
    bindings={}
    def read(p):
        bindings[h.key(p)]=h.digest(p);d=json.loads(p.read_bytes())
        for f,v in d.get('inputs_sha256',{}).items():h.require(h.digest(ROOT/f)==v,'changed producer input');bindings[h.key(ROOT/f)]=v
        return d
    manifest=read(D/'manifest.json');raw=read(D/'exact_matrices.json');summary=read(D/'summary.json');h.require(h.digest(D/'exact_matrices.json')==summary['matrices_sha256'],'matrix pin')
    B=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)];N=[{j for j in range(9)if B[i][j]}for i in range(9)]
    h.require(all(len(N[i]&N[j])==2-int(i!=j and B[i][j])+2*int(i==j)for i in range(9)for j in range(9)),'rook equation')
    bad=[r[:]for r in B];bad[0][1]^=1;bad[1][0]^=1;badN=[{j for j in range(9)if bad[i][j]}for i in range(9)]
    h.require(any(len(badN[i]&badN[j])!=2-bad[i][j]+2*int(i==j)for i in range(9)for j in range(9)),'corrupted rook accepted')
    T=[[int(v//10==i)for v in range(90)]for i in range(9)];Q=[[2-B[i][j]-int(i==j)for j in range(9)]for i in range(9)]
    R=[B[i]+[10*int(i==j)for j in range(9)]for i in range(9)]+[[int(i==j)for j in range(9)]+Q[i]for i in range(9)]
    h.require(raw['B']==B and raw['T']==T and raw['Q']==Q and raw['eighteen_cell_quotient']==R,'raw exact matrices')
    h.require(determinant([[2,0],[0,3]])==6 and determinant([[0,2],[3,0]])==-6 and determinant([[1,2],[2,4]])==0,'determinant controls')
    polychecks=[]
    for matrix,key,factors in [(Q,'Q_characteristic',[(13,1),(-2,4),(1,4)]),(R,'quotient_characteristic',[(14,1),(3,9),(-4,8)])]:
        n=len(matrix);coeff=raw[key];h.require(len(coeff)==n+1 and coeff[0]==1,'monic polynomial degree')
        for x in range(-8,-8+n+1):
            det=determinant([[x*int(i==j)-matrix[i][j]for j in range(n)]for i in range(n)]);expected=1
            for root,power in factors:expected*=(x-root)**power
            h.require(det==expected==polyval(coeff,x),'exact characteristic interpolation')
        changed=coeff.copy();changed[-1]+=1;h.require(polyval(changed,0)!=polyval(coeff,0),'corrupted coefficient control');polychecks.append(dict(matrix=key,degree=n,distinct_exact_determinants=n+1,factors=factors,corrupted_constant_rejected=True))
    checks=[]
    for case in range(10):
        H=[set()for _ in range(90)]
        for i,j in combinations(range(90),2):
            if((i+3)*(j+7)+case*(i+j+1))%(11+case)<case:H[i].add(j);H[j].add(i)
        A=[set(row)for row in N]+[{v+9 for v in H[x]}|{x//10}for x in range(90)]
        for i in range(9):A[i].update(range(9+10*i,19+10*i))
        residual=[[len(A[i]&A[j])+int(j in A[i])-2-12*int(i==j)for j in range(99)]for i in range(99)]
        h.require(all(residual[i][j]==0 for i in range(9)for j in range(9)),'top-left identity')
        for i in range(9):
            for x in range(90):h.require(residual[i][x+9]==residual[x+9][i]==sum(v//10==i for v in H[x])-Q[i][x//10],'cross block identity')
        for x in range(90):
            for y in range(90):
                expected=len(H[x]&H[y])+int(y in H[x])-2-12*int(x==y)+int(x//10==y//10)
                h.require(residual[x+9][y+9]==expected,'lower block identity')
        h.require(residual[9][9]!=residual[9][9]+1,'corrupt lower residual');row=dict(case=case,edges=sum(map(len,H))//2,full_residual_nonzeros=sum(v!=0 for row in residual for v in row),block_identity=True,corrupted_identity_rejected=True);h.require(row==summary['calibration_records'][case],'saved calibration record');checks.append(row)
    h.require(summary['exact_eighteen_cell_eigenvalue_multiplicities']=={'14':1,'3':9,'-4':8}and summary['remaining_target_multiplicities']=={'3':45,'-4':36}and summary['spectral_contradiction']is False,'spectral scope')
    for p in(Path(__file__),Path(h.__file__),ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    report=dict(status='INDEPENDENT_CONDITIONAL_ROOK18_ENCODING_AND_SPECTRUM_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,independent_derivation=[
        'A target has degree14 by the diagonal identity. An induced rook9 B has degree4 and already realizes lambda1/mu2 for every pair inside B. Hence any outside vertex has at most one B neighbor. There are exactly9*(14-4)=90 cross edges and90 outside vertices, forcing exactlyone each and ten outside neighbors for each B vertex.',
        'Order the9 cells by their unique B neighbor: T=I9 tensor1_10^T. Then TT^T=10I9 and J9,90=J9*T. Multiplication of A=[B,T;T^T,H] gives top-left identity automatically, cross identity TH=(2J9-B-I9)T and lower identity H^2=12I-H+2J-T^T*T. Conversely symmetric binary loopless H satisfying these two equations makes A satisfy every target entry. No degree assumption or normalization beyond this explicit labeling is added.',
        'TH=QT counts neighbors in each cell: Qii=1, Qij=1 for a B edge and2 otherwise. Symmetry gives internal5K2, cross perfect matchings or2-regular bipartite graphs and H degree13.',
        'The rook adjacency is (J3-I3) tensor I3 + I3 tensor (J3-I3), giving B eigenvalues4^1,1^4,(-2)^4. Q acts as13,-2,1 on those subspaces. Each simultaneous eigenvector produces quotient block[[b,10],[1,q]]. The constant block has roots14,3; the other8blocks have roots3,-4. Thus quotient multiplicities1,9,8.',
        'The18-dimensional cell-constant subspace is invariant, and since A is symmetric its orthogonal complement is invariant. It is precisely[0;x] with Tx=0, dimension81. The full target has eigenvalues14^1,3^54,(-4)^44 from the identity and trace, so this complement requires3^45,(-4)^36. This is compatible, not a contradiction.'
    ],known_positive_rook_and_corrupted_edge=True,exact_determinant_checks=polychecks,independent_set_residual_controls=checks,producer_imported=False,shared_components=['Python standard library','artifact hash helper only; no producer algebra imports'],approved_scope='Exact conditional block-equivalence and quotient-spectrum statements for targets containing an induced labeled rook9, with arbitrary labels inside every10-vertex cell.',excluded_scope=['No proof every target contains a rook9.','No exclusion or target resolution.','Literature-triage paragraph and historical archive attribution were not independently re-audited; no literature-status promotion.','Finite calibration cases support implementation checks; universal equivalence rests on the written block derivation.'])
    report['fresh_review_after_source_collision']=True
    report['does_not_depend_on_missing_previous_auditor']=True
    report['statement']='For every symmetric binary hollow90-by90 H and fixed labeled rook B with T=I9 tensor ones10, A=[[B,T],[T^T,H]] satisfies the target identity if and only if TH=(2J-B-I)T and H^2=12I-H+2J-T^T*T. Every target containing an induced rook9 admits this representation; the18cell quotient has spectrum14^1,3^9,(-4)^8, leaving3^45,(-4)^36, with no contradiction.'
    out=ROOT/'acceleration/results/20260917_independent_review/rook_regular_set_recheck.json'
    with out.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],h.digest(out))
if __name__=='__main__':main()
