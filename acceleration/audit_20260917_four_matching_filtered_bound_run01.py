"""Direct-neighborhood integer support checks on the frozen four-coordinate family."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
import json
import platform
import subprocess
import sys
import audit_20260917_partial_matching as h
import audit_20260917_moment_positive600 as direct

ROOT=h.ROOT;TABLES=ROOT/'acceleration/results/20260917_partial_four_matchings';MODEL=ROOT/'acceleration/results/20260917_four_matching_filtered_moments'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('solve',),required=True);args=ap.parse_args();bindings={};head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    def read(p):
        bindings[h.key(p)]=h.digest(p);data=json.loads(p.read_bytes())
        for f,v in data.get('inputs_sha256',{}).items():h.require(h.digest(ROOT/f)==v,'changed input');bindings[h.key(ROOT/f)]=v
        return data
    for name,pin in [('four_matchings/summary.json','fb21f69b6e5785e0897bccb6965bfea75c171aad2e685b7d60966bc5c8019e73'),('four_matching_filtered_moments.json','472b7f332a99560fd961d7b6a411edd5db619504c21dd6285470f579e0ba2c51'),('four_coordinate_matching_filter/summary.json','6ee0eea6854f8e82e4067f60225f6c897908d5824f5d71c7d4564e21e86738b3')]:
        p=ROOT/'acceleration/results/20260917_independent_review'/name;h.require(h.digest(p)==pin,'prerequisite pin');read(p)
    if args.mode=='transfer':
        D=ROOT/'acceleration/results/20260917_four_matching_transferred_certificate';read(D/'manifest.json');summary=read(D/'summary.json');cert=read(D/'certificate.json');h.require(summary['certificate_sha256']==h.digest(D/'certificate.json'),'transfer certificate binding')
    else:
        D=ROOT/'acceleration/results/20260917_four_matching_filtered_solve2400/run01';read(D/'manifest.json');summary=read(D/'summary.json');cert=read(D/'exact_support_bound.json')['bound'];h.require(h.digest(D/'exact_support_bound.json')=='51d74ca27a16e624bbe898fa7053e2ac9a8ddab4bbd7be5d824e2657dfc371e9','raw certificate pin')
        for f,v in summary['output_sha256'].items():h.require(h.digest(D/f)==v,'solver artifact changed');bindings[h.key(D/f)]=v
        h.require(cert is not None,'no exact support certificate')
    filterreview=read(ROOT/'acceleration/results/20260917_independent_review/four_coordinate_matching_filter/summary.json');modelmeta=read(MODEL/'model.json');primary=read(TABLES/'manifest.json');read(TABLES/'summary.json');labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    B=[set()for _ in range(99)]
    def edge(a,b):B[a].add(b);B[b].add(a)
    for v in range(1,15):edge(0,v)
    for v in range(1,15,2):edge(v,v+1)
    for u,pair in enumerate(labels,15):
        for s in pair:edge(u,s+1)
    for a,b in primary['remaining_fixed_K_edges_outer']:edge(a+15,b+15)
    unknown=list(map(tuple,primary['unknown_edges_outer']));pairs=list(combinations(range(84),2));scale=cert['denominator'];yv=cert['moment_weight_numerators'];qv=cert['reciprocity_weight_numerators']
    h.require(type(scale)is int and scale>0 and len(qv)==1920 and len(yv)==3486 and all(type(v)is int for v in qv+yv)and all(abs(v)<=scale for v in yv),'weight domain')
    y=dict(zip(pairs,yv));q=dict(zip(unknown,qv))
    if args.mode=='transfer':
        old=read(ROOT/'acceleration/results/20260917_two_matching_moments/exact_support_bound.json')['bound'];oldcaps=read(ROOT/'acceleration/results/20260917_two_matching_moments/model.json');oldq=dict(zip(map(tuple,oldcaps['unknown_edges']),old['reciprocity_weight_numerators']))
        h.require(yv==old['moment_weight_numerators']and scale==old['denominator']and all(q[e]==oldq.get(e,0)for e in unknown),'exact transferred weights')
        newedges=[list(e)for e in unknown if e not in oldq];h.require(newedges==cert['added_zero_reciprocity_edges']and len(newedges)==120 and len(oldq)==1800,'transfer scope')
    rhs={e:2-len(B[e[0]+15]&B[e[1]+15]&set(range(1,15)))-int(e[1]+15 in B[e[0]+15])for e in pairs};dot=sum(y[e]*rhs[e]for e in pairs);maxima=[];argmax=[];count=0
    for u in range(84):
        original=read(TABLES/f'domain_{u:02d}.json')['domain_masks_hex'];ids=modelmeta['retained_original_domain_ids'][u];rejected=set(filterreview['records'][u]['rejected_ids']);h.require(ids==[i for i in range(len(original))if i not in rejected],'sound filter complement composition');h.require(len(ids)==len(set(ids))and ids==sorted(ids)and all(0<=i<len(original)for i in ids),'retained IDs');table=[original[i]for i in ids];known={v-15 for v in B[u+15]if v>=15};values=[]
        for text in table:
            chosen=set(h.bits(int(text,16)));h.require(len(known|chosen)==12 and not known&chosen and u not in chosen,'full star');values.append(direct.score(u,chosen,known,y,q))
        maxima.append(max(values));argmax.append(values.index(max(values)));count+=len(values)
    num=dot-sum(maxima);h.require(count==230879 and maxima==cert['center_maxima_numerators']and num==cert['numerator']and (num>0)==cert['strictly_positive'],'exact full support result')
    if args.mode=='transfer':h.require(dot==cert['rhs_dot_numerator']and argmax==cert['maximizing_new_domain_ids']and list(map(list,unknown))==cert['unknown_edge_order']and list(map(list,pairs))==cert['pair_order']and list(rhs.values())==cert['rhs'],'transfer maxima and row identities')
    controls=direct.controls();h.require(num+1!=dot-sum(maxima)and not abs(scale+1)<=scale,'corrupt controls')
    def admissible(y,q,d):return type(d)is int and d>0 and len(y)==3486 and len(q)==1920 and all(type(v)is int for v in y+q)and all(abs(v)<=d for v in y)
    h.require(admissible(yv,qv,scale),'actual weights');bad_y=yv.copy();bad_y[0]=scale+1;bad_q=qv.copy();bad_q[0]=float(bad_q[0]);h.require(not admissible(bad_y,qv,scale)and not admissible(yv,bad_q,scale)and not admissible(yv,qv,0),'weight corruptions accepted')
    removed=sum(len(row['rejected_ids'])for row in filterreview['records']);original_count=sum(row['original_count']for row in filterreview['records']);h.require(removed==59581 and count+removed==original_count==290460,'whole original-domain coverage')
    for p in(__file__,h.__file__,direct.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    h.require(all(h.digest(ROOT/f)==v for f,v in bindings.items()),'changed audit dependency')
    positive=num>0
    report=dict(status='INDEPENDENT_FOUR_COORDINATE_FILTERED_EXACT_SUPPORT_BOUND_PASS',mode=args.mode,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,exact_bound=dict(numerator=num,denominator=scale,reduced=str(Fraction(num,scale)),strictly_positive=positive,rhs_dot_numerator=dot,center_maxima_numerators=maxima,maximizing_filtered_domain_ids=argmax,maximizing_original_domain_ids=[modelmeta['retained_original_domain_ids'][u][j]for u,j in enumerate(argmax)]),checked_choices=count,checked_centers=84,original_choices=original_count,removed_choices=removed,retained_choices=count,filter_complement_identity_checked=True,controls=controls,weight_failure_controls=['out-of-box y rejected','noninteger q rejected','zero denominator rejected','altered claimed numerator rejected'],dependencies=[dict(id='C-PARTIAL-K-FOUR-COORDINATE-DOMAINS',revision=1,relation='coverage'),dict(id='C-PARTIAL-K-FOUR-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER',revision=1,relation='uses_result'),dict(id='C-PARTIAL-K-FOUR-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING',revision=1,relation='uses_result')],method='Direct full99 set neighborhoods and all230879 sound-filtered star columns with original IDs, unbounded Python integer sums. No producer or serialized LP matrix imports. Earlier complete domains, necessary neighborhood matching filter and exact necessary filtered model are freshly hash-bound.',producer_imported=False,solver_feasible_dual_claimed=False,shared_components=['Python standard library','prior independent raw-neighborhood scorer and calibrated rook controls','prior independent complete-domain and necessary-model reviews'],derivation='Any completion produces hard reciprocal simplex stars and zero full-moment residual. Arbitrary signed q and |y|<=D yield residual L1 >= (y*b-sum_center max(M^T*y+R^T*q))/D.',conditional_family_exclusion=positive,claim_id='C-PARTIAL-K-FOUR-COORDINATE-EXCLUSION'if positive else None,claim_id_null_reason=None if positive else 'Nonpositive bound proves no exclusion.',claim_revision=1 if positive else None,scope='Exact144fixedK,1920unknown, bothsame-signcoordinatesrootgroups0and1; everyotherprescribedabsence retained.',limitations=['No unrestricted Conway-99 resolution; no automorphism assumption.','Positive bound excludes only this declared family; nonpositive bound establishes neither feasibility nor exclusion.','No claim that the bound equals the LP optimum.'])
    out=ROOT/f'acceleration/results/20260917_independent_review/four_matching_filtered_run01_bound.json'
    with out.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],num,scale,h.digest(out))
if __name__=='__main__':main()
