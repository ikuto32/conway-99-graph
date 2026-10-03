"""Independent eight-subset coverage and exact marginal exclusion certificates."""
import argparse, copy, gzip, hashlib, json, math, platform, subprocess, sys, time, traceback
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
from tqdm import tqdm
import audit_20260930_hadamard_seven_exception_census as rankcheck

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_eight_exception_census'
RAW=B/'20260930_hadamard20_support/six_prism.json';M=B/'20260930_independent_review/hadamard_few_exception_marginals'
PINS={D/'summary.json':'a65cf171c1a2b2bd45d72bdfe2971dd7ef20179fd02640a34f2158857c815fc2',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',M/'summary.json':'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9',Path(rankcheck.__file__):'464f3331ca73ad4540e3cbebd16e405b760a51de720f7e6f17ba602a68e4b5bf'}
need=rankcheck.need;sha=rankcheck.sha;key=rankcheck.key;read=rankcheck.read;save=rankcheck.save


def category(rank,basis,common):
    if rank==8:return 'EXCLUDED_FULL_COLUMN_RANK',list(range(8))
    forced=[i for i in range(8)if all(v[i]==0 for v in basis)]
    if forced:return 'EXCLUDED_FORCED_BALANCED_GROUP',forced
    if rank==7:
        c=basis[0];need(all(c)and sum(c)==0,'full-support augmented line')
        if any(abs(x)>=2 for x in c):return 'EXCLUDED_ONE_DIMENSIONAL_LARGE_COEFFICIENT',[]
        need(set(c)=={-1,1},'primitive all-sign line')
        if len(common)<2:return 'EXCLUDED_ONE_DIMENSIONAL_SMALL_COMMON_SUPPORT',[]
        return 'RETAINED_ONE_DIMENSIONAL_SIGN_KERNEL',[]
    return 'RETAINED_HIGHER_DIMENSION_KERNEL',[]


def check_record(record,index,ids,H,groups):
    need(record['index']==index and record['groups']==list(ids),'unique lexicographic eight-subset identity')
    matrix=[[r[g]for g in ids]for r in H]
    rank,basis=rankcheck.validate_certificate(matrix,record['certificate'])
    common=[a for a in range(12)if all(a in groups[g]for g in ids)]
    need(common==record['common_coordinates'],'literal eight-way common coordinates')
    expected,forced=category(rank,basis,common)
    need(record['classification']==expected and record['forced_balanced_local_positions']==forced,'exact whole-nullspace classification')
    if rank==7:
        b=record['primitive_Bezout'];need(len(b)==8 and all(type(x)is int for x in b)and sum(x*y for x,y in zip(b,basis[0]))==1,'literal integer-lattice Bezout certificate')
    return rank,expected


def controls(saved):
    checked=0
    for bits in product((0,1),repeat=9):
        a=[list(bits[3*i:3*i+3])for i in range(3)]
        for size in (1,2,3):
            for rows in combinations(range(3),size):
                for cols in combinations(range(3),size):
                    minor=[[a[i][j]for j in cols]for i in rows]
                    need(rankcheck.determinant_mod(minor,1000003)==rankcheck.determinant_expansion(minor)%1000003,'modular checker against independent permutation determinant')
        checked+=1
    full=[[int(i==j)for j in range(8)]for i in range(8)]
    cert=dict(rank=8,minor_rows=list(range(8)),minor_columns=list(range(8)),minor=full,determinant=1,free_columns=[],integer_null_basis=[])
    need(category(*rankcheck.validate_certificate(full,cert),[])==('EXCLUDED_FULL_COLUMN_RANK',list(range(8))),'handwritten full-rank positive')
    cols=[(0,)*6,*[tuple(int(i==j)for i in range(6))for j in range(6)],(1,)*6]
    large=[[1]*8]+[[v[j]for v in cols]for j in range(6)]
    rank,basis=rankcheck.validate_certificate(large,saved['large_coefficient_kernel']);need(category(rank,basis,[])[0]=='EXCLUDED_ONE_DIMENSIONAL_LARGE_COEFFICIENT','large primitive line positive')
    need(sum(x*y for x,y in zip(basis[0],saved['large_coefficient_Bezout']))==1,'large-line primitive certificate')
    cube=list(product((0,1),repeat=3));higher=[[1]*8]+[[v[j]for v in cube]for j in range(3)]
    rank,basis=rankcheck.validate_certificate(higher,saved['retained']);need(category(rank,basis,[])[0]=='RETAINED_HIGHER_DIMENSION_KERNEL','higher-dimensional retention positive')
    cols=[tuple(v)+(0,)for v in cube[:7]]+[(0,0,0,1)];forced=[[1]*8]+[[v[j]for v in cols]for j in range(4)]
    rank,basis=rankcheck.validate_certificate(forced,saved['forced_balanced']);need(category(rank,basis,[])==('EXCLUDED_FORCED_BALANCED_GROUP',[7]),'whole-kernel forced-zero positive')
    cycle=[[1]*8]+[[int(j in(i,(i+1)%8))for j in range(8)]for i in range(8)]
    rank,basis=rankcheck.validate_certificate(cycle,saved['sign_kernel']);need(rank==7,'alternating eight-cycle kernel')
    for common in ([],[0]):need(category(rank,basis,common)[0]=='EXCLUDED_ONE_DIMENSIONAL_SMALL_COMMON_SUPPORT','zero/one common-coordinate exclusion control')
    need(category(rank,basis,[0,1])[0]=='RETAINED_ONE_DIMENSIONAL_SIGN_KERNEL','two common coordinates not overexcluded')
    fibre_patterns=[x for x in product((-1,0,1),repeat=3)if sum(x)==0]
    need(len(fibre_patterns)==7,'all sign-line fibre-sum possibilities')
    local_counts={}
    for common in range(3):
        allowed=[rows for rows in product(fibre_patterns,repeat=common)if all(sum(row[f]for row in rows)==0 for f in range(3))]
        local_counts[common]=len(allowed)
        need(len(allowed)==(7 if common==2 else 1),'coordinate-sum complete small controls')
    for coefficient in(-6,-3,-2,2,3,6):
        allowed=[x for x in product(range(-8,9),repeat=3)if sum(x)==0 and all(coefficient*t>=-1 for t in x)]
        need(allowed==[(0,0,0)],'integer one-sided zero-sum control')
    return dict(binary3x3_determinant_controls=checked,synthetic_rank8=True,synthetic_large_line=True,synthetic_forced_zero=True,synthetic_higher_kernel_retained=True,common_coordinate_controls=local_counts,nonzero_two_common_coordinate_pattern=[[1,-1,0],[-1,1,0]],integer_large_coefficient_controls=6,scope='Synthetic exact matrix/count controls, not full factors.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        actual=sha(p);need(h is None or h==actual,'input identity '+key(p));pins[key(p)]=actual
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(D/'summary.json');marginal=read(M/'summary.json')
        need(producer['status']=='CANDIDATE_COMPLETE_EIGHT_EXCEPTION_CENSUS'and producer['completed']==producer['population']==math.comb(20,8)==125970,'complete census not prefix')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(ROOT/p,h)
        need(marginal['status']=='INDEPENDENT_HADAMARD_FEW_EXCEPTION_MARGINALS_PASS','full-Gram marginal premise')
        mp=M/'independent_marginal_certificates.json';pin(mp,marginal['outputs_sha256'][key(mp)]);matrices=read(mp)['matrices']
        raw=read(RAW);groups=list(dict.fromkeys(tuple(i for i in range(12)if raw['L'][i][d])for d in range(60)))
        need(len(groups)==20 and all(len(g)==6 and all(sum(x in g for x in(a,a+1))==1 for a in range(0,12,2))for g in groups),'actual fixed supports')
        H=[[1]*20]+[[int(a in g)for g in groups]for a in range(12)]
        global_saved=read(D/'global_marginal_matrix.json');need(global_saved['groups']==[list(g)for g in groups]and global_saved['matrix']==H,'literal global marginal matrix')
        global_rank,_=rankcheck.validate_certificate(H,global_saved['global_certificate']);need(global_rank==7,'whole incidence rank7')
        bridge=[]
        for coordinate in range(12):
            incident=[g for g,s in enumerate(groups)if coordinate in s];other=[b for b in range(12)if b not in(coordinate,coordinate^1)]
            expected=[[1]*10]+[[int(b in groups[g])for g in incident]for b in other]
            need(matrices[coordinate]['groups']==incident and matrices[coordinate]['matrix']==expected,'literal prior universal marginal matrix bridge')
            need([H[coordinate+1][g]for g in incident]==[1]*10 and [H[(coordinate^1)+1][g]for g in incident]==[0]*10,'missing self/mate rows are duplicate/zero')
            bridge.append(dict(coordinate=coordinate,incident_groups=incident,rows=[0]+[b+1 for b in other]))
        calibration=controls(read(D/'controls.json'));save(out/'calibration.json',calibration)
        final=read(D/'checkpoint_125970.json');need(final['inputs_sha256']==producer['inputs_sha256']and final['population']==final['completed']==125970,'frozen complete checkpoint')
        need(len(final['chunks'])==63,'63 complete immutable chunks')
        iterator=iter(combinations(range(20),8));completed=0;ranks=Counter();classes=Counter();remaining=[];templates={};chunks=[];commonhist=Counter()
        for ci,chunk in enumerate(tqdm(final['chunks'],desc='Independent eight-subset certificates',mininterval=1)):
            need(chunk['first_index']==completed and chunk['count']==min(2000,125970-completed),'contiguous nonoverlapping chunk range')
            path=ROOT/chunk['path'];pin(path,chunk['sha256']);count=0;cr=Counter();cc=Counter()
            with gzip.open(path,'rt',encoding='utf8')as f:
                for line in f:
                    rec=json.loads(line);ids=next(iterator);rank,category_name=check_record(rec,completed,ids,H,groups)
                    ranks[rank]+=1;classes[category_name]+=1;cr[rank]+=1;cc[category_name]+=1;commonhist[len(rec['common_coordinates'])]+=1;templates.setdefault(category_name,(rec,ids))
                    if category_name.startswith('RETAINED'):remaining.append(rec)
                    completed+=1;count+=1
            need(count==chunk['count'],'exact chunk record count')
            checkpoint=D/f'checkpoint_{completed:05d}.json';cp=read(checkpoint);need(cp['completed']==completed and cp['chunks']==final['chunks'][:ci+1]and cp['inputs_sha256']==final['inputs_sha256'],'every immutable prefix checkpoint')
            chunks.append(dict(path=key(path),sha256=sha(path),first_index=chunk['first_index'],count=count,rank_counts=dict(cr),class_counts=dict(cc)))
        need(next(iterator,None)is None and completed==125970,'complete frozen subset universe no omissions')
        need(producer['rank_counts']=={str(k):v for k,v in sorted(ranks.items())}and producer['class_counts']==dict(classes),'all producer aggregate counts independently derived')
        need(ranks=={5:18,6:7468,7:118484}and classes=={'EXCLUDED_FORCED_BALANCED_GROUP':92723,'EXCLUDED_ONE_DIMENSIONAL_LARGE_COEFFICIENT':28400,'EXCLUDED_ONE_DIMENSIONAL_SMALL_COMMON_SUPPORT':663,'RETAINED_HIGHER_DIMENSION_KERNEL':4184},'exact frozen result population')
        rem=read(D/'remaining_candidates.json');need(rem['records']==remaining and rem['count']==producer['remaining_necessary_subsets']==4184,'all and only retained records')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,IndexError,KeyError,TypeError):rejected.append(name);return
            raise ValueError('accepted corruption '+name)
        for name in('determinant','minor_entry','null_entry','nonprimitive','Bezout','common','classification','missing_basis'):
            rec,ids=templates['EXCLUDED_ONE_DIMENSIONAL_LARGE_COEFFICIENT'];bad=copy.deepcopy(rec);cert=bad['certificate']
            if name=='determinant':cert['determinant']+=1
            elif name=='minor_entry':cert['minor'][0][0]^=1
            elif name=='null_entry':cert['integer_null_basis'][0][0]+=1
            elif name=='nonprimitive':cert['integer_null_basis'][0]=[2*x for x in cert['integer_null_basis'][0]]
            elif name=='Bezout':bad['primitive_Bezout']=[0]*8
            elif name=='common':bad['common_coordinates']=[99]
            elif name=='classification':bad['classification']='RETAINED_HIGHER_DIMENSION_KERNEL'
            else:cert['integer_null_basis']=[]
            reject(name,lambda bad=bad,ids=ids:check_record(bad,bad['index'],ids,H,groups))
        rec,ids=templates['RETAINED_HIGHER_DIMENSION_KERNEL'];bad=copy.deepcopy(rec);bad['certificate']['integer_null_basis'][1]=bad['certificate']['integer_null_basis'][0][:]
        reject('dependent_basis',lambda:check_record(bad,bad['index'],ids,H,groups))
        reject('missing_subset',lambda:need(completed-1==125970,'complete population'))
        calibration['corruptions_rejected']=rejected;save(out/'controls.json',calibration)
        save(out/'marginal_bridge.json',dict(global_matrix=H,global_rank=global_rank,groups=groups,records=bridge))
        save(out/'chunk_checks.json',chunks);save(out/'independent_remaining.json',dict(count=len(remaining),groups=[r['groups']for r in remaining],ranks=[r['certificate']['rank']for r in remaining],scope='Necessary subsets retained only; no factor construction.'))
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_EIGHT_EXCEPTION_CENSUS.md')
        timestamp=datetime.now(timezone.utc).isoformat();statement='Among all125970 eight-element subsets of the20 pinned six-prism Hadamard support groups, the augmented incidence matrix ranks are5 for18,6 for7468,and7 for118484. Every prescribed-Gram binary factor on this fixed support with exactly eight unbalanced triplicate groups must use one of the4184 saved higher-dimensional-kernel subsets:92723 subsets have a forced-zero group coordinate throughout the nullspace,28400 have a primitive rank7 kernel with a coefficient of magnitude at least2,and663 have a full-sign rank7 kernel and at most one common coordinate. The4184 retained subsets are not asserted feasible.'
        binding=dict(id='C-FIXED-HADAMARD-EIGHT-EXCEPTION-KERNEL-CENSUS',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,scope='Complete exact finite octet census and necessary fixed-support full-Gram reduction; no caps or target automorphism premise.',assumptions=['Pinned literal support and full prescribed integer Gram, with aggregate L.','Exactly eight groups have nonzero coordinate/fibre deviations.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION',revision=1,relation='uses_result')],verifier='/root/eight_domain_audit',producer='/root',method='Literal rank minors checked by modular determinant and exact Leibniz bound, every null equation and full basis independence, every Bezout identity, complete population replay and independent integer/common-coordinate derivation.',shared_components=['Prior independently authored seven-census modular certificate checker, explicitly pinned; no producer helper imports.','Raw support and separately checked full-Gram marginal premise; Python exact arithmetic.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p)for p in out.glob('*.json')},limitations=['No retained subset is excluded or constructed.','No full-support/core/unrestricted-target resolution.','No re-execution of producer rank code.'],artifact_availability='LOCAL_ONLY',created_at=timestamp,updated_at=timestamp)
        save(out/'claim_binding.json',binding)
        report=dict(status='INDEPENDENT_HADAMARD_EIGHT_EXCEPTION_CENSUS_PASS',timestamp=timestamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.glob('*.json')},claim_id=binding['id'],claim_revision=1,statement=statement,population=125970,checked_records=completed,checked_chunks=len(chunks),global_rank=global_rank,rank_counts=dict(ranks),class_counts=dict(classes),common_coordinate_histogram=dict(commonhist),retained=4184,excluded_by_necessary_marginals=125970-4184,controls=calibration,elapsed_seconds=time.perf_counter()-start,native_calls=0,target_resolution=False,artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except Exception as e:
        save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise


if __name__=='__main__':main()
