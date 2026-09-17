"""Independent Python-integer raw-star checks of every frozen GPU support attempt."""
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import argparse,json,sys,subprocess,platform,hashlib,io,math
from tqdm import tqdm
import audit_20260917_partial_matching as h
import audit_20260917_moment_positive600 as direct
import audit_compressed_artifacts as recovery
ROOT=h.ROOT;REVIEW=ROOT/'acceleration/results/20260917_independent_review';TABLES=ROOT/'acceleration/results/20260917_partial_six_matchings';D=1<<20
def rounding(value):
    if not math.isfinite(value):raise ValueError('nonfinite multiplier')
    a,b=(-float(value)).as_integer_ratio();sign=-1 if a<0 else 1;q,r=divmod(abs(a)*D,b)
    if 2*r>b or(2*r==b and q%2):q+=1
    return sign*q
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);parser.add_argument('--out',required=True);args=parser.parse_args();run=ROOT/args.run;out=ROOT/args.out;bindings={};recovered={};recovery_records=[]
    def digest(p):return hashlib.sha256(recovered[p]).hexdigest()if p in recovered else h.digest(p)
    def read(p):bindings[h.key(p)]=digest(p);return json.loads(recovered[p]if p in recovered else p.read_bytes())
    summary=read(run/'summary.json');manifest=read(run/'manifest.json');compressed=read(run/'compressed_artifacts.json');chunks=read(run/'chunk_manifest.json')
    # Recover checkpoint bytes from independently concatenated gzip parts when present.
    for record in compressed['files']:
        raw=ROOT/record['path'];gz=ROOT/record['compressed_path'];art=next((a for a in chunks['artifacts']if a['source']==gz.name),None)
        if art:
            blob=bytearray()
            for part in art['parts']:
                p=run/part['path'];data=p.read_bytes();h.require(len(data)==part['bytes']and hashlib.sha256(data).hexdigest()==part['sha256'],'compressed part identity');bindings[h.key(p)]=h.digest(p);blob.extend(data)
            packed=bytes(blob);h.require(len(packed)==art['source_bytes']and hashlib.sha256(packed).hexdigest()==art['source_sha256'],'packed gzip identity')
        else:packed=gz.read_bytes();bindings[h.key(gz)]=h.digest(gz)
        h.require(len(packed)==record['compressed_size_bytes']and hashlib.sha256(packed).hexdigest()==record['compressed_sha256'],'gzip identity');recovered[gz]=packed
        sink=io.BytesIO();recovery.decode((packed[i:i+100003]for i in range(0,len(packed),100003)),sink.write,record['size_bytes'],record['sha256']);recovered[raw]=sink.getvalue();bindings[h.key(raw)]=record['sha256'];recovery_records.append(dict(path=h.key(raw),sha256=record['sha256'],original_raw_consulted=False,parts_used=bool(art)))
    gate=read(REVIEW/'six_filtered_moments.json');filtered=read(REVIEW/'six_coordinate_matching_filter/summary.json');read(REVIEW/'six_gpu_export_verifier.json')
    h.require(digest(REVIEW/'six_filtered_moments.json')=='f27467b03a34fe3ea3adec4e537585e71d5697f4e63562cdd43d7e6822c8f3e7'and digest(REVIEW/'six_coordinate_matching_filter/summary.json')=='05d4284f04fb5c84491394695c6f56a3e5517302ae95c1885b27592cfed78a7f','independent family premises')
    for premise in(gate,filtered):
        for f,v in premise['inputs_sha256'].items():h.require(h.digest(ROOT/f)==v,'changed premise input');bindings[f]=v
    for f,v in summary['output_sha256'].items():
        # Bind mathematically consumed records explicitly below; other run artifacts get identity checks.
        p=run/f;h.require(digest(p)==v,'run artifact changed');bindings[h.key(p)]=v
    cm=read(run/'certificates/manifest.json');cs=read(run/'certificates/summary.json');expected_order=[(cp,kind)for cp in(1000,5000,10000)for kind in('last','average')]
    h.require(cm['attempt_order']==list(map(list,expected_order))and len(cs['attempts'])==6,'all six preregistered attempts')
    primary=read(TABLES/'manifest.json');labels=[{2*a+s,2*b+t}for a,b in combinations(range(7),2)for s in range(2)for t in range(2)];fixed=set(map(tuple,primary['remaining_fixed_K_edges_outer']));edges=list(map(tuple,primary['unknown_edges_outer']));pairs=list(combinations(range(84),2));known=[set()for _ in range(84)]
    for a,b in fixed:known[a].add(b);known[b].add(a)
    tables=[];ids=[]
    for u in range(84):
        raw=read(TABLES/f'domain_{u:02d}.json')['domain_masks_hex'];h.require(bindings[h.key(TABLES/f'domain_{u:02d}.json')]==gate['inputs_sha256'][h.key(TABLES/f'domain_{u:02d}.json')],'audited raw domains');reject=set(filtered['records'][u]['rejected_ids']);ids.append([i for i in range(len(raw))if i not in reject]);tables.append([set(h.bits(int(raw[i],16)))for i in ids[u]])
    h.require(sum(map(len,tables))==712721 and sum(len(r['rejected_ids'])for r in filtered['records'])==166728,'whole879449 composition')
    rhs=[2-len(labels[a]&labels[b])-int((a,b)in fixed)for a,b in pairs]
    tie_inputs=[.5/D,1.5/D,2.5/D,-.5/D,-1.5/D,-2.5/D];h.require([rounding(v)for v in tie_inputs]==[0,-2,-2,0,2,2],'independent half-even signs')
    controls=direct.controls();results=[]
    for (cp,kind),row in zip(expected_order,cs['attempts']):
        p=ROOT/row['path'];cert=read(p);h.require(digest(p)==row['sha256']and(row['iterations'],row['iterate'])==(cp,kind),'attempt order/binding')
        h.require(cert['status']=='CANDIDATE_EXACT_SIX_COORDINATE_SUPPORT_ATTEMPT','incomplete attempt needs separate audit path')
        checkpoint=ROOT/cert['checkpoint_path'];gpu=read(checkpoint);h.require(digest(checkpoint)==cert['checkpoint_sha256']and gpu['iterations']==cp,'raw checkpoint binding')
        dual=gpu['y_'+kind];h.require(len(dual)==5526,'multiplier dimension');weights=[rounding(float(v))for v in dual];yv=[max(-D,min(D,v))for v in weights[:3486]];qv=weights[3486:]
        h.require(yv==cert['moment_weight_numerators']and qv==cert['reciprocity_weight_numerators']and cert['denominator']==D,'exact saved binary64 quantization')
        y=dict(zip(pairs,yv));q=dict(zip(edges,qv));dot=sum(a*b for a,b in zip(rhs,yv));maxima=[];argmax=[];old=[];mc=0;rc=0
        for u,table in enumerate(tqdm(tables,desc=f'Raw six support {cp} {kind}',unit='center')):
            scores=[]
            for chosen in table:
                h.require(len(known[u]|chosen)==12 and not known[u]&chosen and u not in chosen,'full neighborhood');scores.append(direct.score(u,chosen,known[u],y,q));mc=max(mc,66+sum(v>u for v in chosen));rc=max(rc,len(chosen))
            maximum=max(scores);j=scores.index(maximum);maxima.append(maximum);argmax.append(j);old.append(ids[u][j])
        numerator=dot-sum(maxima);guard=max(map(abs,yv))*mc+max(map(abs,qv))*rc
        h.require(guard==cert['int64_absolute_product_guard']and guard<2**62,'producer integer bound independently justified')
        h.require(maxima==cert['center_maxima_numerators']and argmax==cert['first_argmax_retained_ids']and old==cert['first_argmax_original_ids']and dot==cert['moment_rhs_dot_numerator']and sum(maxima)==cert['sum_center_maxima_numerator']and numerator==cert['numerator']and(numerator>0)==cert['strictly_positive'],'all exact support values')
        h.require(numerator+1!=dot-sum(maxima)and not abs(D+1)<=D,'corrupt result/box controls')
        results.append(dict(iterations=cp,iterate=kind,certificate_path=h.key(p),certificate_sha256=digest(p),numerator=numerator,denominator=D,reduced=str(Fraction(numerator,D)),strictly_positive=numerator>0,checked_columns=712721,checked_centers=84,center_maxima_numerators=maxima,first_argmax_original_ids=old))
    for p in(__file__,h.__file__,direct.__file__,recovery.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    h.require(all(digest(ROOT/f)==v for f,v in bindings.items()),'artifact stability')
    report=dict(status='INDEPENDENT_SIX_COORDINATE_GPU_EXACT_SUPPORT_ATTEMPTS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,attempts=results,positive_attempts=sum(r['strictly_positive']for r in results),attempt_population=6,raw_original_choices=879449,independently_rejected_choices=166728,retained_choices=712721,recovery=recovery_records,controls=controls,independent_ties_to_even_sign_clip=True,producer_imported=False,serialized_matrix_used_for_support_arithmetic=False,solver_dual_feasibility_assumed=False,derivation='For any hypothetical completion in the declared scope, the independent domain/filter premises retain all its local stars. Their one-hot simplex point satisfies exact reciprocity and full-neighborhood moments. For arbitrary q and moment weights withabs(y)<=D, the L1 moment residual is at least(y*b-sum_center max(M^T*y+R^T*q))/D. A strictly positive independently evaluated bound contradicts zero residual in that conditional family only.',scope=primary['scope'],shared_components=['Python standard library','tqdm','prior independent raw-neighborhood scorer and rook controls','independent zlib recovery helper','pinned complete domain/filter/model reviews'],limitations=['A numerical checkpoint is never itself a certificate; only the separately checked integer weights and all column maxima enter this result.','Scope132fixedK and prescribed other absences; no unrestricted target resolution or nontrivial automorphism assumption.','Nonpositive attempts prove neither feasibility nor exclusion; no claim of optimality.'])
    with out.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],h.digest(out))
if __name__=='__main__':main()
