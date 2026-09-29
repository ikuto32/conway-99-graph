"""Independent component-kernel, overflow and complete suffix audit."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_joint_factor_cnf as base

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_factor_components'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_joint_factor_cnf/summary.json'
GATE_SHA='5a6ebade41cf1ab35796ca5d5ce3840c23b624ab06d0ed5a4ff327327ea2b97f'
need,digest,key,save=base.need,base.digest,base.key,base.save
SUMMARY_SHA='d88a594b3b01b27f2b7713e22157ba07e0c8a7bf385cec4372d5ef750439eb73'

def components_from_raw(h):
    adj=[{b for b in range(36) if h[3+a][3+b]} for a in range(36)]
    need(all(len(row)==3 for row in adj),'raw cubic core')
    reach=[set([i]) for i in range(36)]
    for a in range(36):
        changed=True
        while changed:
            old=set(reach[a])
            for b in old:reach[a].update(adj[b])
            changed=old!=reach[a]
    components=sorted({tuple(sorted(s)) for s in reach})
    need(len(components)==3 and all(len(c)==12 for c in components),'three12components')
    need(sorted(x for c in components for x in c)==list(range(36)),'component partition')
    need(all(sum(x//12==f for x in c)==4 for c in components for f in range(3)),'four rows per fibre in each component')
    return adj,list(map(list,components))

def kernel_check(certificate,h,g):
    adj,components=components_from_raw(h)
    need(certificate['adjacency_core_rows']==[sorted(s) for s in adj],'exact raw cubic adjacency')
    need(certificate['components']==components and certificate['target_gram_rows']==g,'exact partition and Gram')
    need(certificate['column_total']==6 and certificate['entailed_component_column_total']==2,'six total gives2per component')
    expected=[]
    for index in [1,2]:
        v=[int(a in components[0])-int(a in components[index]) for a in range(36)]
        image=[sum(g[a][b]*v[b] for b in range(36)) for a in range(36)]
        need(image==[0]*36,'literal exact Gram kernel')
        expected.append(dict(vector=v,exact_Kv=image,exact_quadratic=sum(v[a]*image[a] for a in range(36))))
    need(certificate['contrast_certificates']==expected,'complete exact contrast certificates')
    return components,expected

def overflow(c,q,components,columns):
    need(sorted(q)==list(range(60)) and all(type(x) is int for x in q),'labelled Q1 permutation')
    rows=[r[:] for r in c]+[[int(a in columns[q[d]]) for d in range(60)] for a in range(12)]
    found=[]
    for i,comp in enumerate(components):
        for d in range(60):
            support=[r for r in comp if r<24 and rows[r][d]]
            if len(support)>2:found.append(dict(component=i,column=d,known_incidence_rows=support,count=len(support)))
    return rows,found

def diagnostic_check(record,q,c0,components,columns,g,known):
    need(record['Q1']==q,'exact input factor permutation')
    rows,expected=overflow(c0,q,components,columns)
    base.factor_check(rows,[row[:24] for row in g[:24]],known[:24])
    need(record['violations']==expected and record['overflow_count']==len(expected),'every exact overflow and total')
    need(record['status']=='CANDIDATE_COMPONENT_OVERFLOW' and expected,'positive overflow witness')
    return rows,expected

def verify_composition(basebytes,suffix,complete):
    head,body=basebytes.split(b'\n',1)
    need(head==b'p cnf 58860 203748','exact original base header')
    need(complete==b'p cnf 61296 212580\n'+body+suffix,'complete exact header/basebody/suffix bytes')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(path,expected=None):
        path=Path(path);v=digest(path);need(expected is None or v==expected,'artifact hash '+str(path));bindings[key(path)]=v;return path
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    try:
        gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_TRIANGLE_JOINT_FACTOR_CNF_ENCODING_PASS','base independent gate')
        for p,v in gate['inputs_sha256'].items():bind(ROOT/p,v)
        summary=read(D/'summary.json',SUMMARY_SHA);manifest=read(D/'manifest.json')
        for p,v in manifest['inputs_sha256'].items():bind(ROOT/p,v)
        for p,entry in summary['outputs'].items():need(bind(D/p,entry['sha256']).stat().st_size==entry['bytes'],'recorded artifact bytes')
        original=read(base.D/'model.json');scope=read(base.D/'scope.json');model=read(D/'model.json')
        h,g,columns,known,zeros,entries,refs=base.scope_check(original,scope)
        certificate=read(D/'kernel_certificate.json');components,contrasts=kernel_check(certificate,h,g)
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,IndexError,KeyError):rejected.append(label)
            else:raise ValueError('corruption accepted '+label)
        for label in ['kernel_vector','Gram_entry','component_partition','raw_edge','column_total']:
            bad=deepcopy(certificate)
            if label=='kernel_vector':bad['contrast_certificates'][0]['vector'][0]+=1
            elif label=='Gram_entry':bad['target_gram_rows'][0][0]+=1
            elif label=='component_partition':bad['components'][0][0]=bad['components'][1][0]
            elif label=='raw_edge':bad['adjacency_core_rows'][0].pop()
            else:bad['column_total']=9
            reject(label,lambda:kernel_check(bad,h,g))
        diagnostic=read(D/'five_Q1_diagnostic.json');need(len(diagnostic)==5,'exact five-factor population')
        inputs=[('external_conway99_research/attempts/wave151-triangle-root-factor/exact-results.json','exact_partial_factor'),('external_conway99_research/attempts/wave154-triangle-factor-portfolio/exact-results.json','second_exact_Q1_representative')]+[(f'acceleration/results/20260930_triangle_q1_binary_scout/factor_{i:02d}.json',None) for i in range(3)]
        checked=[]
        for record,(path,nested) in zip(diagnostic,inputs):
            need(record['factor_input']==path,'frozen factor population/order')
            raw=read(ROOT/path,record['factor_sha256']);q=(raw[nested] if nested else raw)['Q1']
            rows,violations=diagnostic_check(record,q,known[:12],components,columns,g,known)
            checked.append(dict(factor_input=path,factor_sha256=digest(ROOT/path),Q1=q,raw_incidence_24=rows,overflow_count=len(violations),violations=violations))
        need([r['overflow_count'] for r in checked]==summary['five_Q1_overflow_counts']==[3,1,1,1,1],'exact overflow counts')
        for label in ['overflow_count','overflow_row','overflow_column','missing_overflow','wrong_Q1']:
            bad=deepcopy(diagnostic[0]);q=checked[0]['Q1']
            if label=='overflow_count':bad['overflow_count']+=1
            elif label=='overflow_row':bad['violations'][0]['known_incidence_rows'][0]=0
            elif label=='overflow_column':bad['violations'][0]['column']=0
            elif label=='missing_overflow':bad['violations'].pop()
            else:bad['Q1'][0],bad['Q1'][1]=bad['Q1'][1],bad['Q1'][0]
            reject(label,lambda:diagnostic_check(bad,q,known[:12],components,columns,g,known))
        rows=read(D/'appended_rows.json')
        changed={'schema','counter_rows','variables','clauses'}
        extra={'base_model_path','base_model_sha256','base_cnf_sha256','component_kernel_certificate','component_kernel_certificate_sha256','appended_component_counters'}
        need(set(model)==set(original)|extra,'exact strengthened model keys')
        for name,value in original.items():
            if name not in changed:need(model[name]==value,'unchanged base model field '+name)
        need(model['schema']=='FIXED_TRIANGLE_JOINT_BINARY_FACTOR_COMPONENT_PREFIX_CNF_V1','component model schema')
        need(model['counter_rows']==original['counter_rows']+rows and len(rows)==model['appended_component_counters']==180,'exact base+180counter model')
        need(model['base_model_path']==key(base.D/'model.json') and model['base_model_sha256']==digest(base.D/'model.json') and model['base_cnf_sha256']==digest(base.D/'instance.cnf'),'base identity metadata')
        need(model['component_kernel_certificate']==key(D/'kernel_certificate.json') and model['component_kernel_certificate_sha256']==digest(D/'kernel_certificate.json'),'kernel certificate metadata')
        basebytes=(base.D/'instance.cnf').read_bytes();suffix=(D/'component_equalities.cnfpart').read_bytes();complete=(D/'instance.cnf').read_bytes()
        verify_composition(basebytes,suffix,complete)
        reject('changed_header',lambda:verify_composition(basebytes,suffix,complete.replace(b'61296 212580',b'61296 212579',1)))
        reject('missing_suffix_clause',lambda:verify_composition(basebytes,suffix,complete[:-5]))
        reject('changed_base_body',lambda:verify_composition(basebytes.replace(b'1 ',b'-1 ',1),suffix,complete))
        calibration=base.gates.controls()
        with io.BytesIO(suffix) as stream:
            cursor=base.gates.ClauseCursor(stream,61296);cursor.count=203748;audit=base.gates.GateAudit(cursor,58860);index=0
            for ci,component in enumerate(components):
                for d in range(60):
                    constant=sum(refs[r][d] is True for r in component);terms=[refs[r][d] for r in component if type(refs[r][d]) is int]
                    annotation=dict(kind='component_column_margin',component=ci,column=d,raw_component_rows=component,constant=constant,original_bound=2)
                    audit.counter(rows[index],terms,2-constant,True,annotation);index+=1
            need(stream.read()==b'','all suffix bytes consumed')
        need(cursor.count==model['clauses']==summary['clauses']==212580 and audit.top==model['variables']==summary['variables']==61296,'exact augmented counts')
        need(cursor.count-203748==summary['appended_clauses']==8832 and audit.top-58860==summary['new_variables']==2436,'exact suffix counts')
        packages=[]
        for p in read(D/'artifact_packages.json')['packages']:
            rawparts=b''.join(bind(ROOT/part['path'],part['sha256']).read_bytes() for part in p['ordered_parts'])
            need(sha256(rawparts).hexdigest()==p['compressed_stream_sha256'],'gzip stream identity')
            recovered=gzip.decompress(rawparts)
            need(len(recovered)==p['raw_bytes'] and sha256(recovered).hexdigest()==p['raw_sha256']==digest(ROOT/p['raw_path']),'exact recovered artifacts')
            packages.append(dict(path=p['raw_path'],sha256=p['raw_sha256'],bytes=len(recovered)))
        save(args.out/'independent_kernel_and_overflow.json',dict(components=components,contrasts=contrasts,checked_factors=checked))
        save(args.out/'controls.json',dict(kernel_overflow_composition_corruptions_rejected=rejected,threshold=calibration))
        for path in [Path(__file__),ROOT/'docs/AUDIT_20260930_TRIANGLE_FACTOR_COMPONENTS.md']:bind(path)
        need(all(digest(ROOT/p)==v for p,v in bindings.items()),'input stability')
        need(time.monotonic()-start<180,'audit wall cap')
        report=dict(status='INDEPENDENT_TRIANGLE_COMPONENT_FACTOR_CNF_ENCODING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),verifier='/root/eight_domain_audit independent component implication and suffix checker',inputs_sha256=bindings,
          claim_records=[dict(id='C-FIXED-TRIANGLE-FACTOR-COMPONENT-BALANCE',revision=1,statement='Every real36x60 factor of the exact fixed core Gram with six total per column has sum2 on each of its three saved row components in every column.',kind='mathematical result',dependencies=[dict(id='C-FIXED-TRIANGLE-JOINT-BINARY-FACTOR-CNF-ENCODING',revision=1,relation='uses_result')]),dict(id='C-FIXED-TRIANGLE-COMPONENT-STRENGTHENED-CNF',revision=1,statement='The exact61296variable212580clause augmented formula has precisely the same primary incidence solutions as the audited base factor CNF.',kind='encoding',dependencies=[dict(id='C-FIXED-TRIANGLE-FACTOR-COMPONENT-BALANCE',revision=1,relation='uses_result'),dict(id='C-FIXED-TRIANGLE-JOINT-BINARY-FACTOR-CNF-ENCODING',revision=1,relation='encoding_equivalence')]),dict(id='C-FIVE-FIXED-TRIANGLE-Q1-COMPONENT-OVERFLOW-EXCLUSIONS',revision=1,statement='None of the five exact saved24row C0+C1 factors extends by a nonnegative C2 to the fixed36row target Gram and column conditions, as witnessed by complete recorded overflow populations3,1,1,1,1.',kind='exclusion',dependencies=[dict(id='C-FIXED-TRIANGLE-FACTOR-COMPONENT-BALANCE',revision=1,relation='uses_result')])],
          recommendation='VERIFIED',review_state='CLEAR',basis=['DERIVED','COMPUTED'],scope='One fixed39core Gram; no unrestricted target coverage, no residual D; five specific Q1 choices only.',components=components,component_equations=180,variables=audit.top,clauses=cursor.count,new_variables=2436,appended_clauses=8832,checked_factor_count=5,overflow_counts=[3,1,1,1,1],
          controls_path=key(args.out/'controls.json'),controls_sha256=digest(args.out/'controls.json'),raw_certificate_path=key(args.out/'independent_kernel_and_overflow.json'),raw_certificate_sha256=digest(args.out/'independent_kernel_and_overflow.json'),package_checks=packages,
          shared_components=['Previously frozen independently authored raw-core Gram builder and factor validator reused.','Frozen independent GateAudit helper reused; complete new suffix reconstructed.','Exact base byte identity plus its independent encoding gate used as a declared premise.','No producer imports.'],
          limitations=['This is not a census of Q1 factors.','No target automorphism or fixed-core containment is assumed.','No SAT/UNSAT solver result is supplied by this audit.'],solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:
        save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e),inputs_sha256=bindings));raise

if __name__=='__main__':main()
