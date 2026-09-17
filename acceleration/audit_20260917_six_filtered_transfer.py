"""All-column integer raw-neighborhood check of transferred four-family weights."""
from datetime import datetime,timezone
from itertools import combinations
from fractions import Fraction
import json,sys,subprocess,platform
from tqdm import tqdm
import audit_20260917_partial_matching as h
import audit_20260917_moment_positive600 as direct
ROOT=h.ROOT;OUT=ROOT/'acceleration/results/20260917_independent_review';D=ROOT/'acceleration/results/20260917_six_filtered_transferred_certificate';TABLES=ROOT/'acceleration/results/20260917_partial_six_matchings'
def main():
    bindings={}
    def read(p):bindings[h.key(p)]=h.digest(p);return json.loads(p.read_bytes())
    modelgate=read(OUT/'six_filtered_moments.json');filtergate=read(OUT/'six_coordinate_matching_filter/summary.json')
    h.require(h.digest(OUT/'six_filtered_moments.json')=='f27467b03a34fe3ea3adec4e537585e71d5697f4e63562cdd43d7e6822c8f3e7'and h.digest(OUT/'six_coordinate_matching_filter/summary.json')=='05d4284f04fb5c84491394695c6f56a3e5517302ae95c1885b27592cfed78a7f','gates')
    recovered={r['raw_path']:ROOT/r['recovered_path']for r in filtergate['lossless_gzip_recovery']}
    recovered.update({f'acceleration/results/20260917_six_filtered_moments/{r["source"]}':ROOT/r['recovered_path']for r in modelgate['chunk_recovery']})
    manifest=read(D/'manifest.json');summary=read(D/'summary.json');cert=read(D/'certificate.json')
    h.require(summary['certificate_sha256']==h.digest(D/'certificate.json'),'certificate binding')
    for record in(modelgate,filtergate,manifest):
        for f,v in record['inputs_sha256'].items():h.require(h.digest(recovered.get(f,ROOT/f))==v,'dependency changed');bindings[f]=v
    primary=read(TABLES/'manifest.json');fixed=set(map(tuple,primary['remaining_fixed_K_edges_outer']));edges=list(map(tuple,primary['unknown_edges_outer']));pairs=list(combinations(range(84),2))
    labels=[{2*a+s,2*b+t}for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    known=[set()for _ in range(84)]
    for a,b in fixed:known[a].add(b);known[b].add(a)
    yv=cert['moment_weight_numerators'];qv=cert['reciprocity_weight_numerators'];scale=cert['denominator']
    def valid(y,q,d):return type(d)is int and d>0 and len(y)==3486 and len(q)==2040 and all(type(v)is int for v in y+q)and all(abs(v)<=d for v in y)
    h.require(valid(yv,qv,scale),'weights');y=dict(zip(pairs,yv));q=dict(zip(edges,qv))
    old=read(ROOT/'acceleration/results/20260917_four_matching_filtered_solve2400/run01/exact_support_bound.json')['bound'];oldmeta=read(ROOT/'acceleration/results/20260917_four_matching_filtered_moments/model.json');oldq=dict(zip(map(tuple,oldmeta['unknown_edges']),old['reciprocity_weight_numerators']))
    added=[list(e)for e in edges if e not in oldq]
    h.require(yv==old['moment_weight_numerators']and scale==old['denominator']and all(q[e]==oldq.get(e,0)for e in edges)and len(added)==120 and added==cert['added_zero_reciprocity_edges'],'transfer mapping')
    rhs=[2-len(labels[a]&labels[b])-int((a,b)in fixed)for a,b in pairs];dot=sum(v*w for v,w in zip(rhs,yv));maxima=[];argfiltered=[];argoriginal=[];count=0
    for u in tqdm(range(84),desc='Independent six transferred bound',unit='center'):
        raw=read(TABLES/f'domain_{u:02d}.json')['domain_masks_hex'];reject=set(filtergate['records'][u]['rejected_ids']);ids=[i for i in range(len(raw))if i not in reject]
        h.require(ids==cert['retained_original_domain_ids'][u],'exact filtered identities')
        values=[]
        for i in ids:
            chosen=set(h.bits(int(raw[i],16)));h.require(len(known[u]|chosen)==12 and not known[u]&chosen,'raw full neighborhood');values.append(direct.score(u,chosen,known[u],y,q))
        maximum=max(values);j=values.index(maximum);maxima.append(maximum);argfiltered.append(j);argoriginal.append(ids[j]);count+=len(values)
    numerator=dot-sum(maxima)
    h.require(count==712721 and maxima==cert['center_maxima_numerators']and argfiltered==cert['maximizing_filtered_domain_ids']and argoriginal==cert['maximizing_original_domain_ids']and dot==cert['rhs_dot_numerator']and numerator==cert['numerator']==-2378749843,'complete exact arithmetic')
    h.require(rhs==cert['rhs']and list(map(list,edges))==cert['unknown_edge_order']and list(map(list,pairs))==cert['pair_order']and cert['strictly_positive']is False,'row identities/interpretation')
    controls=direct.controls();bad=yv[:];bad[0]=scale+1;badq=qv[:];badq[0]=float(badq[0]);h.require(not valid(bad,qv,scale)and not valid(yv,badq,scale)and not valid(yv,qv,0)and numerator+1!=dot-sum(maxima),'negative controls')
    for p in(__file__,h.__file__,direct.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    h.require(all(h.digest(recovered.get(f,ROOT/f))==v for f,v in bindings.items()),'end identity')
    report=dict(status='INDEPENDENT_SIX_COORDINATE_FILTERED_TRANSFER_BOUND_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,checked_columns=count,checked_centers=84,exact_bound=dict(numerator=numerator,denominator=scale,reduced=str(Fraction(numerator,scale)),strictly_positive=False,rhs_dot_numerator=dot,center_maxima_numerators=maxima,maximizing_filtered_domain_ids=argfiltered,maximizing_original_domain_ids=argoriginal),controls=controls,corrupted_weights_and_numerator_rejected=True,producer_imported=False,serialized_matrix_used_for_arithmetic=False,method='All raw full-neighborhood integer column scores and 84 maxima; direct transfer checked edge-by-edge with120 new zero q weights.',scope=primary['scope'],shared_components=['Python standard library','tqdm','prior independent raw-neighborhood score and rook controls','pinned independent domains/filter/encoding evidence'],limitations=['Negative support bound is weaker than trivial zero and proves neither feasibility nor exclusion.','No target resolution or proof about every possible choice of weights.'])
    p=OUT/'six_filtered_transfer.json'
    with p.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],h.digest(p))
if __name__=='__main__':main()
