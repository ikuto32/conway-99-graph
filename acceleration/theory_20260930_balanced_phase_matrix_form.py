"""Candidate matrix-form record; exact known-input controls, no solver."""
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
PINS={
 B/'20260930_hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 B/'20260930_independent_review/hadamard_parity_support_cuts_sat/independent_projection.json':'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',
 B/'20260930_hadamard_f3_phases/phase_system.json':'aecf80f4f1c7cd29f821cb52ec502b810aa87fc8ff908ea38e2f36a69e416061',
 B/'20260930_independent_review/hadamard_f3_phase_obstruction/summary.json':'0ccca8ba45e0ffa5ff0e1d8d7c051ffcbee3d9d30092fac5df33274d80dea346',
}
def need(v,msg):
    if not v:raise ValueError(msg)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def plus(a,b,sign=1):return[(x+sign*y)%3 for x,y in zip(a,b,strict=True)]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        for p,d in PINS.items():need(h(p)==d,'input '+key(p))
        raw=read(next(iter(PINS)));projection=read(list(PINS)[1]);system=read(list(PINS)[2]);groups=[]
        for d in range(60):
            s=[a for a in range(12)if raw['L'][a][d]]
            if s not in groups:groups.append(s)
        need(groups==system['groups']and len(groups)==20,'literal group ordering')
        patterns=projection['selected_group_parity_patterns'];L=[[int(a in s)for s in groups]for a in range(12)];S=[[0]*20 for _ in range(12)];ids={}
        for g,s in enumerate(groups):
            need(sum(patterns[g])==3,'all-mixed selected branch')
            for i,a in enumerate(s):S[a][g]=1-2*patterns[g][i];ids[a,g]=6*g+i
        gram=[[sum(S[a][g]*S[b][g]for g in range(20))for b in range(12)]for a in range(12)]
        expect=[[11*int(a==b)+int(a^1==b)-1 for b in range(12)]for a in range(12)]
        need(gram==expect and all(sum(S[a][g]for a in range(12))==0 for g in range(20)),'all integer signed-Gram and column-balance entries')
        matrixrows=[]
        for a in range(12):
            for b in range(12):
                row=[0]*120
                for g in range(20):
                    if L[a][g]and L[b][g]:row[ids[b,g]]=(row[ids[b,g]]+1)%3;row[ids[a,g]]=(row[ids[a,g]]-S[a][g]*S[b][g])%3
                matrixrows.append(dict(coordinates=[a,b],coefficients=row))
        lookup={tuple(r['coordinates']):r['coefficients']for r in matrixrows};bytype={}
        for r in system['rows']:bytype[(r['kind'],tuple(r.get('coordinates',[])),r.get('group'),r.get('sign'))]=r['coefficients']
        for a,b in combinations(range(12),2):
            if a^1==b:need(not any(lookup[a,b])and not any(lookup[b,a]),'matched coefficient identity');continue
            odd=bytype['pair_odd_phase_sum',(a,b),None,None];even=bytype['pair_even_phase_sum',(a,b),None,None]
            need(lookup[a,b]==plus(odd,even)and lookup[b,a]==plus(odd,even,-1),'both ordered matrix equations equal odd+even / odd-even')
        need(all(not any(lookup[a,a])for a in range(12)),'all diagonal equations trivial')
        columns=[]
        for g,s in enumerate(groups):
            plain=[0]*120;signed=[0]*120
            for a in s:plain[ids[a,g]]=1;signed[ids[a,g]]=S[a][g]%3
            even=bytype['local_same_sign_sum',(),g,1];odd=bytype['local_same_sign_sum',(),g,2]
            need(plain==plus(even,odd)and signed==plus(even,odd,-1),'both column sums are exact local row combinations');columns.extend([dict(group=g,kind='sum_T',coefficients=plain),dict(group=g,kind='sum_S_times_T',coefficients=signed)])
        degenerate=[p for row in patterns for p in row];need(all(sum(x*y for x,y in zip(r['coefficients'],degenerate,strict=True))%3==0 for r in system['rows']),'known parity-indicator degenerate null vector')
        need(all(sum(x*y for x,y in zip(r['coefficients'],degenerate,strict=True))%3==0 for r in system['necessary_nonzero_functionals']),'degenerate vector is not a valid mixed coloring')
        corrupt=[]
        wrong=plus(bytype['pair_odd_phase_sum',(0,2),None,None],bytype['pair_even_phase_sum',(0,2),None,None],-1)
        need(wrong!=lookup[0,2],'wrong ordered sign rejected');corrupt.append('wrong_ordered_matrix_sign')
        bad=[r[:]for r in S];bad[0][0]=1 if bad[0][0]==0 else -bad[0][0]
        need([[sum(bad[a][g]*bad[b][g]for g in range(20))for b in range(12)]for a in range(12)]!=expect,'changed signed support rejected');corrupt.append('changed_signed_support')
        save(out/'matrix_identity_controls.json',dict(L12x20=L,S12x20=S,integer_signed_Gram=gram,phase_matrix_rows=matrixrows,phase_column_sum_rows=columns,degenerate_null_vector=degenerate,corruptions_rejected=corrupt))
        pins={key(p):d for p,d in PINS.items()}
        for p in[Path(__file__),ROOT/'docs/DERIVATION_20260930_BALANCED_PHASE_MATRIX_FORM.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=h(p)
        report=dict(status='CANDIDATE_BALANCED_PHASE_MATRIX_FORM_RECORD',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},checked_integer_Gram_entries=144,ordered_phase_coefficient_rows=144,column_sum_coefficient_rows=40,phase_variables=120,universal_rank119_proved=False,new_solver_calls=0,new_rank_calculations=0,independent_approval=False,scope='Candidate written universal algebra plus exact controls on the one checked second parity branch; no general phase-rank collapse or target claim.')
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=h(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
