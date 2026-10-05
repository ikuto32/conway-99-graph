"""Independent complete GF(3) kernel enumeration for one saved parity branch."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import audit_20260930_hadamard_parity_phase_batch as independent

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
I=B+'independent_review/'
RUN=B+'hadamard_phase_case01_enumeration_v3/'
CASE=B+'hadamard_parity_phase_batch_pilot/case_01/'
CASE_GATE=I+'hadamard_parity_phase_batch_cases/case_01/summary.json'
RAW=independent.RAW
FIXTURE=B+'srg243_residual_fixture/triangle_blocks.json'
PINS={
    'acceleration/audit_20260930_hadamard_parity_phase_batch.py':'cda0c17f4262050ad7668186845842ede0e7f2a02a324f11a659c8dc4d8fceaf',
    CASE_GATE:'8cf9bf3842fe675973011eb33d6a8909bf64bf2715a8cd9c409858ec593af4f6',
    CASE+'phase_system.json':'c6f31ba77b060ccddefc5274be3a130f3cdaf1d83c612ec507c69f588f80dfe2',
    CASE+'phase_screen.json':'8eebf239cca0bf7aca1f1a8120c2f82494ec2545211031c173948a48e33400dc',
    CASE+'decoded_projection.json':'31c8d00f69c5694121aca82dc99ac103ae9ed769ea00b0a334e87b55c391081e',
    RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
    I+'srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
    independent.NECESSITY_GATE:'30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
}
FROZEN_PRODUCER_PINS={
    RUN+'summary.json':'052938d4c10130850c2bf72b246140abcbdf5992c0b69921dae66da18acad7d9',
    RUN+'enumeration.jsonl':'7fc4d1fa63946037fa9ac8f69421f399e89c8088defb39a88be7687454cc7a0a',
    'acceleration/theory_20260930_hadamard_phase_case01_enumeration_v3.py':'20ac10cc364766b1cb3cb9030e9e4515228595f2e3d48f1b510ded2edf546371',
    'acceleration/theory_20260930_hadamard_phase_case01_enumeration_v3_spec.md':'860f1c21fa26752df645e860f42f8371e0251d13491137fbf979716b4a829632',
}


def need(ok,message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def value_sha(value):
    return hashlib.sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()


def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')


def local_check(signs,phases):
    """Evaluate all three literal columns before inspecting multiplicities."""
    need(len(signs)==len(phases)==6 and all(s in (1,2) for s in signs)
         and all(type(t) is int and t in (0,1,2) for t in phases),'literal local affine domain')
    columns=[[((signs[i]*x)+phases[i])%3 for i in range(6)] for x in range(3)]
    balanced=all(Counter(col)==Counter({0:2,1:2,2:2}) for col in columns)
    actual={str(s):[Counter(phases[i] for i in range(6) if signs[i]==s)[v] for v in range(3)] for s in [1,2]}
    mixed=2 in signs
    expected={'1':[1,1,1],'2':[1,1,1]} if mixed else {'1':[2,2,2],'2':[0,0,0]}
    need(balanced==(actual==expected),'literal balanced columns and multiplicity equivalence')
    if balanced:
        return None
    return dict(rule='mixed_phase_distinctness' if mixed else 'constant_phase_multiplicity',actual=actual,expected=expected)


def local_first(system,phase):
    for g,signs in enumerate(system['signs']):
        fail=local_check(signs,phase[6*g:6*g+6])
        if fail:
            return dict(group=g,**fail)
    return None


def prescribed(core,n):
    need(len(core)==3*n and all(len(row)==3*n for row in core),'core dimension')
    return [[n*(a==b)+2-(a//n==b//n)-core[a][b]
             -sum(core[a][k]*core[k][b] for k in range(3*n)) for b in range(3*n)] for a in range(3*n)]


def factor_checks(F,C,n,L=None):
    need(len(F)==3*n and F and F[0] and all(len(row)==len(F[0]) and all(type(v)is int and v in (0,1) for v in row) for row in F),
         'binary rectangular factor')
    m,width=3*n,len(F[0])
    target=prescribed(C,n)
    gram=[[sum(F[a][d]*F[b][d] for d in range(width)) for b in range(m)] for a in range(m)]
    gram_errors=[dict(rows=[a,b],actual=gram[a][b],expected=target[a][b]) for a in range(m) for b in range(m) if gram[a][b]!=target[a][b]]
    caps=[dict(columns=[d,e],overlap=sum(F[a][d]*F[a][e] for a in range(m))) for d,e in combinations(range(width),2)]
    mixed=[[F[a][d]+sum(C[a][b]*F[b][d] for b in range(m)) for d in range(width)] for a in range(m)]
    margins=all(sum(row)==n-2 for row in F) and all(sum(F[g*n+a][d] for a in range(n))==2 for g in range(3) for d in range(width))
    actualL=[[sum(F[g*n+a][d] for g in range(3)) for d in range(width)] for a in range(n)]
    violations=[x for x in caps if x['overlap']>2]
    mixed_bad=[dict(row=a,column=d,value=mixed[a][d]) for a in range(m) for d in range(width) if mixed[a][d]>2]
    L_ok=L is None or L==actualL
    return dict(Gram_pass=not gram_errors,Gram_mismatches=gram_errors,actual_Gram=gram,margins_pass=margins,raw_L_pass=L_ok,
                all_column_pair_records=caps,cap_violations=violations,mixed_cap_violations=mixed_bad,
                complete_partial_factor_pass=not gram_errors and margins and L_ok and not violations and not mixed_bad)


def literal_factor(raw,system,phase):
    F=[[0]*60 for _ in range(36)]
    for d in range(60):
        support=[a for a in range(12) if raw['L'][a][d]]
        g=system['groups'].index(support)
        ordered=[e for e in range(60) if [a for a in range(12) if raw['L'][a][e]]==support]
        x=ordered.index(d)
        need(len(ordered)==3,'three raw columns with this support')
        for i,a in enumerate(support):
            F[a+12*((system['signs'][g][i]*x+phase[6*g+i])%3)][d]=1
    return F


def pair_failures_literal(system,phase):
    result=[]
    target=[[2-int(x==y) for y in range(3)] for x in range(3)]
    for a,b in combinations(range(12),2):
        if a^1==b:
            continue
        actual=[[0]*3 for _ in range(3)]
        relsigns,relphases=[],[]
        for g,support in enumerate(system['groups']):
            if a not in support or b not in support:
                continue
            i,j=support.index(a),support.index(b)
            sa,sb=system['signs'][g][i],system['signs'][g][j]
            ta,tb=phase[6*g+i],phase[6*g+j]
            # Count actual ordered colors across the three raw group columns;
            # no producer relative-intercept routine is used for these counts.
            for column in range(3):
                actual[(sa*column+ta)%3][(sb*column+tb)%3]+=1
            relsigns.append(sa*sb%3)
            relphases.append((tb-sa*sb*ta)%3)
        if actual!=target:
            result.append(dict(coordinates=[a,b],relative_signs=relsigns,relative_phases=relphases,actual=actual,expected=target))
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    inputs,rejected={},[]
    def pin(path,expected=None):
        path=Path(path);path=(ROOT/path if not path.is_absolute() else path).resolve()
        need(path.is_relative_to(ROOT),'repository artifact');key=path.relative_to(ROOT).as_posix();digest=sha(path)
        need(expected is None or expected==digest,'exact artifact '+key);inputs[key]=digest;return path
    def load(path,expected=None):
        return json.loads(pin(path,expected).read_bytes())
    def reject(label,action):
        try:action()
        except(ValueError,KeyError,TypeError,IndexError):rejected.append(label)
        else:raise ValueError('corruption accepted '+label)
    try:
        need(bool(FROZEN_PRODUCER_PINS),'successful producer artifacts frozen before audit')
        for path,digest in {**PINS,**FROZEN_PRODUCER_PINS}.items():pin(path,digest)
        summary=load(RUN+'summary.json');manifest=load(RUN+'manifest.json')
        for mapping in ('inputs_sha256','outputs_sha256'):
            for path,digest in summary[mapping].items():pin(path,digest)
        need(manifest['inputs_sha256']==summary['inputs_sha256'] and manifest['limits']==dict(seconds=120,expected_vectors=2187,solver_calls=0),'frozen exact bounded protocol')
        gate=load(CASE_GATE);need(gate['status']=='INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_CASE_PASS','prior full actual projection gate')
        for mapping in ('inputs_sha256','outputs_sha256'):
            for path,digest in gate[mapping].items():pin(path,digest)
        raw=load(RAW);projection=load(CASE+'decoded_projection.json')
        _,groups,_=independent.canonical_base(raw,load(independent.OLD_MODEL))
        system=independent.phase_equations(raw,projection,groups)
        need(system==load(CASE+'phase_system.json'),'all independently reconstructed equations and dependencies')
        matrix=[row['coefficients'] for row in system['rows']]
        rank,basis=independent.field_rank_and_kernel(matrix)
        need(rank==113 and len(basis)==7 and len(matrix)==172 and system['mixed_groups']==12 and system['constant_groups']==8,'independent dimensions')
        checked=independent.check_screen(system,load(CASE+'phase_screen.json'))
        need(not checked['exact_exclusion'],'individual-functionals screen really survives')
        certificate=load(RUN+'recomputed_linear_certificate.json')
        need(certificate==load(CASE+'phase_screen.json')['linear_certificate'],'producer basis identity to independently checked complete basis')
        producer_basis=certificate['nullspace_basis']
        need(raw['prescribed_Gram36']==prescribed(raw['core_adjacency'],12),'all1296 target coefficients from raw core')
        # Calibrate literal local columns before the research enumeration.
        local_control_counts={}
        for label,signs in [('mixed',[1,1,1,2,2,2]),('constant',[1]*6)]:
            accepted=sum(local_check(signs,list(t)) is None for t in product(range(3),repeat=6))
            local_control_counts[label]=accepted
        need(local_control_counts==dict(mixed=36,constant=90),'all1458 local phase profiles, with genuine valid controls')
        reject('changed_local_mixed_profile',lambda:need(local_check([1,1,1,2,2,2],[0,0,2,0,1,2]) is None,'invalid mixed phases'))
        reject('changed_local_constant_profile',lambda:need(local_check([1]*6,[0,0,0,1,2,2]) is None,'invalid constant phases'))
        fixture=load(FIXTURE);F,C=fixture['factor60x180'],fixture['cubic_core60']
        good=factor_checks(F,C,20);need(good['complete_partial_factor_pass'],'genuine nonempty SRG243 raw factor positive')
        bad=deepcopy(F);bad[0][0]^=1
        reject('corrupt_generic_factor_bit',lambda:need(factor_checks(bad,C,20)['complete_partial_factor_pass'],'corrupt full Gram'))
        bad=deepcopy(F)
        for row in bad:row[1]=row[0]
        need(any(x['columns']==[0,1] and x['overlap']==6 for x in factor_checks(bad,C,20)['cap_violations']),'explicit duplicated-column cap control')
        bad=deepcopy(F);bad[0][0]=2
        reject('nonbinary_generic_factor',lambda:factor_checks(bad,C,20))
        raw_records=[json.loads(line) for line in pin(RUN+'enumeration.jsonl').read_text(encoding='utf-8').splitlines()]
        need(len(raw_records)==2187,'complete saved population')
        expected_coefficients=list(product(range(3),repeat=7))
        need([r['coefficients'] for r in raw_records]==[list(t) for t in expected_coefficients]
             and [r['index'] for r in raw_records]==list(range(2187)),'all lexicographic producer tuples once, including zero')
        producer_vectors={}
        for record,coefficients in zip(raw_records,expected_coefficients):
            phase=tuple(sum(c*producer_basis[j][i] for j,c in enumerate(coefficients))%3 for i in range(120))
            need(value_sha(list(phase))==record['phase_sha256'],'raw vector identity')
            need(phase not in producer_vectors,'injective producer coefficient parameterization')
            producer_vectors[phase]=record
        independent_vectors=set()
        stages=Counter();failures=Counter();survivors=[]
        with (out/'independent_enumeration.jsonl').open('x',encoding='utf-8',newline='\n') as stream:
            for index,coefficients in enumerate(product(range(3),repeat=7)):
                phase=tuple(sum(c*basis[j][i] for j,c in enumerate(coefficients))%3 for i in range(120))
                need(phase not in independent_vectors and all(sum(a*b for a,b in zip(row,phase))%3==0 for row in matrix),'independent kernel vector and uniqueness')
                independent_vectors.add(phase)
                need(phase in producer_vectors,'independent vector has saved raw record')
                record=producer_vectors[phase];failed=local_first(system,phase);stages['kernel_vectors_enumerated']+=1
                check_record=dict(index=index,independent_coefficients=list(coefficients),phase_sha256=value_sha(list(phase)),producer_index=record['index'])
                if failed:
                    need(record['first_failure']==failed and 'local_survivor_path' not in record,'literal first local failure')
                    failures[failed['rule']]+=1;check_record['first_failure']=failed
                else:
                    stages['local_profile_survivors']+=1
                    witness=load(record['local_survivor_path'],record['local_survivor_sha256'])
                    factor=literal_factor(raw,system,phase)
                    need(witness['phase']==list(phase) and witness['factor']==factor,'every raw surviving factor coordinate')
                    pair_bad=pair_failures_literal(system,phase)
                    factor_result=factor_checks(factor,raw['core_adjacency'],12,raw['L'])
                    need(witness['pair_failures']==pair_bad and witness['factor_checks']==factor_result,'every pair/Gram/margin/cap finding')
                    need((not pair_bad)==factor_result['Gram_pass'],'independent pair and all1296 literal Gram entries agree')
                    stages['complete_pair_Gram_survivors']+=not bool(pair_bad)
                    stages['complete_integer_Gram_factors']+=factor_result['Gram_pass']
                    stages['Gram_and_caps_factors']+=factor_result['complete_partial_factor_pass']
                    if not factor_result['complete_partial_factor_pass']:failures['pair_Gram' if pair_bad else 'column_or_mixed_caps']+=1
                    need(record['first_failure']==(pair_bad[0] if pair_bad else None)
                         and record['Gram_pass']==factor_result['Gram_pass'] and record['full_partial_factor_pass']==factor_result['complete_partial_factor_pass'],'survivor enumeration metadata')
                    survivors.append(dict(producer_index=record['index'],factor_sha256=record['local_survivor_sha256'],Gram_pass=factor_result['Gram_pass'],caps_pass=not factor_result['cap_violations']))
                    check_record.update(local_profile_pass=True,pair_Gram_pass=not pair_bad,complete_partial_factor_pass=factor_result['complete_partial_factor_pass'])
                stream.write(json.dumps(check_record,separators=(',',':'))+'\n')
        need(independent_vectors==set(producer_vectors) and len(independent_vectors)==3**7,'exact complete basis-independent coverage equality')
        for key in ['local_profile_survivors','complete_pair_Gram_survivors','complete_integer_Gram_factors','Gram_and_caps_factors']:stages.setdefault(key,0)
        need(dict(stages)==summary['counts'] and dict(failures)==summary['first_failure_counts'],'all independently counted pipeline outcomes')
        need(summary['complete'] is True and summary['independent_approval'] is False and summary['target_resolution'] is False
             and summary['kernel_dimension']==7 and summary['frozen_universe']==2187,'producer exact declared scope')
        need(summary['candidate_branch_exclusion']==(stages['Gram_and_caps_factors']==0),'candidate conclusion agrees with exact checks')
        need(len(list((ROOT/RUN/'local_survivors').glob('*.json')))==stages['local_profile_survivors'],'all local-survivor artifacts preserved')
        bad=deepcopy(raw_records);bad.pop()
        reject('missing_vector_record',lambda:need(len(bad)==2187,'complete vector population'))
        bad=deepcopy(raw_records);bad[-1]=bad[0]
        reject('duplicated_coefficient_tuple',lambda:need([r['coefficients'] for r in bad]==[list(t) for t in expected_coefficients],'exact tuple census'))
        bad=deepcopy(basis);bad[0][0]=1
        reject('invalid_basis_coordinate',lambda:need(all(sum(x*y for x,y in zip(row,v))%3==0 for row in matrix for v in bad),'all basis products'))
        bad=deepcopy(raw_records[0]);bad['phase_sha256']='0'*64
        reject('changed_raw_vector_hash',lambda:need(bad['phase_sha256']==value_sha([0]*120),'literal zero vector identity'))
        bad=deepcopy(raw_records[0]);bad['first_failure']['group']+=1
        reject('changed_first_failure',lambda:need(bad['first_failure']==local_first(system,[0]*120),'actual first local failure'))
        save(out/'independent_basis.json',dict(rank=rank,nullity=7,basis=basis,method='Descending pivot columns and reverse row selection; independent of producer leftmost RREF.'))
        save(out/'controls.json',dict(local_profiles=1458,local_positive_counts=local_control_counts,generic_positive='Independent raw SRG243 factor, not Conway99 or this fixed support.',corruptions_rejected=rejected))
        save(out/'counts.json',dict(counts=dict(stages),first_failure_counts=dict(failures),local_survivors=survivors,
            covered_population='Every one of3^7 phase vectors in the exact172-by120 homogeneous kernel, including zero.',complete=True))
        timestamp=datetime.now(timezone.utc).isoformat()
        binding=dict(id='C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-CASE01-COMPLETE-PHASE-EXCLUSION',revision=1,
            statement='For the exact saved case01 parity projection, every one of the2187 vectors in its seven-dimensional necessary GF(3) phase kernel violates a local balanced-column phase multiplicity:1611 first fail a mixed-group condition and576 first fail a constant-group condition. Consequently this selected parity assignment has no coordinatewise balanced coloring lift realizing the prescribed full Gram matrix.',
            kind='exclusion',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED' if stages['Gram_and_caps_factors']==0 else 'CANDIDATE',review_state='CLEAR',
            scope='One exact case01 parity assignment on one frozen six-prism Hadamard support; no complete support/core/target exclusion.',
            assumptions=['Coordinatewise balanced support triples are an additional restriction.','The independently checked general phase necessity and within-identical-column gauge apply.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY',revision=1,relation='premise'),
                          dict(id='C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-PROJECTIONS',revision=1,relation='premise')],
            limitations=['Only this exact branch is covered.','This is complete finite phase enumeration, not an UNSAT solver result.','No target automorphism, full99 graph, general nonexistence or literature novelty is asserted.'],
            verifier='/root/eight_domain_audit',checking_method='Independent reverse-pivot kernel, all2187 full vectors and literal affine columns; raw full factor checks for every local survivor.',
            created_at=timestamp,updated_at=timestamp,artifact_availability='LOCAL_ONLY',external_review=False)
        need(stages['local_profile_survivors']==0,'This exact statement requires all2187 local profiles to fail')
        save(out/'claim_binding.json',binding)
        pin(Path(__file__))
        pin('docs/AUDIT_20260930_HADAMARD_CASE01_COMPLETE_PHASE_ENUMERATION.md')
        for version in ['', '_v2']:
            pin('acceleration/theory_20260930_hadamard_phase_case01_enumeration'+version+'.py')
            pin(B+'hadamard_phase_case01_enumeration'+version+'/failure.json')
        for path in ['uv.lock','pyproject.toml']:pin(path)
        save(out/'summary.json',dict(status='INDEPENDENT_HADAMARD_CASE01_COMPLETE_PHASE_ENUMERATION_PASS',timestamp=timestamp,
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=inputs,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},
            counts=dict(stages),first_failure_counts=dict(failures),rank=rank,nullity=7,finite_universe=2187,corruption_controls=len(rejected),
            shared_components=['Frozen independently authored parity-system reconstruction and reverse-pivot linear checker reused with exact pins.','New literal local columns, pair-color histograms, factor products, complete finite enumeration and saved-artifact matching; no producer imports.'],
            verifier='/root/eight_domain_audit',scope=binding['scope'],target_resolution=False,solver_calls=0,artifact_availability='LOCAL_ONLY'))
        print(json.dumps(dict(status='INDEPENDENT_HADAMARD_CASE01_COMPLETE_PHASE_ENUMERATION_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(__file__)))
        raise


if __name__=='__main__':main()
