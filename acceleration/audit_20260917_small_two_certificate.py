"""Independently check all coarse integer certificates by raw-neighborhood sums."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import audit_20260917_partial_matching as h
import audit_20260917_moment_positive600 as direct

ROOT=h.ROOT;D=ROOT/'acceleration/results/20260917_two_coordinate_small_certificate';T=ROOT/'acceleration/results/20260917_partial_two_matchings'
def rounded(n,d,scale):
    f=Fraction(abs(n)*d,scale)+Fraction(1,2)
    return(-1 if n<0 else 1)*(f.numerator//f.denominator)
def validate(c,old,computed):
    d=c['denominator'];h.require(type(d)is int and d>0,'positive denominator')
    y=c['moment_weight_numerators'];q=c['reciprocity_weight_numerators'];scale=old['denominator']
    h.require(y==[max(-d,min(d,rounded(v,d,scale)))for v in old['moment_weight_numerators']]and q==[rounded(v,d,scale)for v in old['reciprocity_weight_numerators']],'deterministic rounding and clipping')
    h.require(all(type(v)is int for v in y+q)and all(abs(v)<=d for v in y),'weight domain')
    h.require(c['moment_rhs_dot_numerator']==computed['dot']and c['center_maxima_numerators']==computed['maxima']and c['first_argmax_original_ids']==computed['argmax'],'direct full-neighborhood maxima')
    num=computed['dot']-sum(computed['maxima']);h.require(num==c['numerator']and c['strictly_positive']==(num>0)and str(Fraction(num,d))==c['exact_value'],'exact bound')
def main():
    bindings={};start=datetime.now(timezone.utc).isoformat();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    def read(p):
        bindings[h.key(p)]=h.digest(p);r=json.loads(p.read_bytes())
        for f,v in r.get('inputs_sha256',{}).items():h.require(h.digest(ROOT/f)==v,'changed input');bindings[h.key(ROOT/f)]=v
        return r
    summary=read(D/'summary.json');h.require(h.digest(D/'summary.json')=='a51ca68a8de3159c727f90a4e258146d71052887e705627c06ee478c655db72c','frozen batch')
    for name,pin in [('two_matching_solve_bound.json','adf254892686dab05f0317b9ecec963b1b98eee8f9f8ccee129b05ebf6145065'),('two_matching_moments.json','5af1f353a70a16fc5f915195b911d782e360ffc0690463936b7a9dea983197ed'),('two_matchings/summary.json','f3d2ba90be5e8c27bc64c2e4941174d36fc3ddfcbc29ce25da872df652383acb')]:
        p=ROOT/'acceleration/results/20260917_independent_review'/name;h.require(h.digest(p)==pin,'independent premise pin');read(p)
    oldpath=ROOT/'acceleration/results/20260917_two_matching_moments/exact_support_bound.json';h.require(h.digest(oldpath)=='708434c9485ba144a62fd4bf7d220dbf672c6fb3ee72a262cfb95e7584b55680','original certificate pin');old=read(oldpath)['bound']
    denominators=[1<<i for i in range(9)];certs=[read(D/f'denominator_{d:03d}.json')for d in denominators]
    h.require([c['denominator']for c in certs]==denominators and summary['attempted']==summary['completed']==9,'frozen batch population')
    primary=read(T/'manifest.json');labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)];known=[set()for _ in range(84)]
    for a,b in primary['remaining_fixed_K_edges_outer']:known[a].add(b);known[b].add(a)
    unknown=list(map(tuple,primary['unknown_edges_outer']));pairs=list(combinations(range(84),2));rhs={e:2-len(set(labels[e[0]])&set(labels[e[1]]))-int(e[1]in known[e[0]])for e in pairs}
    ys=[dict(zip(pairs,c['moment_weight_numerators']))for c in certs];qs=[dict(zip(unknown,c['reciprocity_weight_numerators']))for c in certs]
    calculations=[dict(dot=sum(rhs[e]*y[e]for e in pairs),maxima=[],argmax=[])for y in ys];count=0;maxL1=0
    for u in range(84):
        table=read(T/f'domain_{u:02d}.json')['domain_masks_hex'];values=[[]for _ in certs]
        for mask in table:
            chosen=set(h.bits(int(mask,16)));h.require(len(known[u]|chosen)==12 and not known[u]&chosen,'full neighborhood')
            maxL1=max(maxL1,1+len(chosen)+66+sum(u<v for v in chosen))
            for k in range(9):values[k].append(direct.score(u,chosen,known[u],ys[k],qs[k]))
        count+=len(table)
        for values_,calc in zip(values,calculations):calc['maxima'].append(max(values_));calc['argmax'].append(values_.index(max(values_)))
    h.require(count==89308,'all original local stars')
    for c,calc in zip(certs,calculations):
        validate(c,old,calc);maximum=max(map(abs,c['moment_weight_numerators']+c['reciprocity_weight_numerators']));h.require(c['maximum_column_L1']==maxL1 and c['maximum_weight_magnitude']==maximum and c['integer_product_absolute_bound']==maxL1*maximum,'engineering arithmetic bound')
    controls=[]
    for n,scale,want in[(1,2,1),(-1,2,-1),(3,2,2),(-3,2,-2),(1,3,0),(-1,3,0),(2,3,1),(-2,3,-1),(0,7,0)]:h.require(rounded(n,1,scale)==want,'rounding fixture');controls.append(dict(kind='rounding',n=n,scale=scale,expected=want))
    for name,edit in [('bound',lambda c:c.update(numerator=c['numerator']+1)),('maximum',lambda c:c['center_maxima_numerators'].__setitem__(0,c['center_maxima_numerators'][0]+1)),('argmax',lambda c:c['first_argmax_original_ids'].__setitem__(0,-1)),('moment_weight',lambda c:c['moment_weight_numerators'].__setitem__(0,2)),('reciprocity_weight',lambda c:c['reciprocity_weight_numerators'].__setitem__(0,c['reciprocity_weight_numerators'][0]+1)),('denominator',lambda c:c.update(denominator=0))]:
        bad=deepcopy(certs[0]);edit(bad)
        try:validate(bad,old,calculations[0])
        except ValueError:controls.append(dict(kind='corruption',name=name,outcome='REJECT'))
        else:raise ValueError('corrupt certificate accepted')
    direct.controls()
    records=[dict(denominator=c['denominator'],numerator=c['numerator'],exact_value=c['exact_value'],positive=c['numerator']>0,certificate_sha256=h.digest(D/f"denominator_{c['denominator']:03d}.json"),rhs_dot=calc['dot'],sum_maxima=sum(calc['maxima']),all84_maxima_and_argmax_checked=True)for c,calc in zip(certs,calculations)]
    simple=min((r for r in records if r['positive']),key=lambda r:r['denominator']);strong=max((r for r in records if r['positive']),key=lambda r:Fraction(r['numerator'],r['denominator']))
    h.require(simple['denominator']==summary['simplest_positive']['denominator']and strong['denominator']==summary['strongest_positive']['denominator']and sum(r['positive']for r in records)==summary['positive_count']==9,'selection audit')
    for p in(Path(__file__),Path(h.__file__),Path(direct.__file__),ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    h.require(all(h.digest(ROOT/f)==v for f,v in bindings.items()),'input changed during audit')
    report=dict(status='INDEPENDENT_TWO_COORDINATE_COARSE_CERTIFICATE_BATCH_PASS',claim_id='C-PARTIAL-K-TWO-COORDINATE-EXCLUSION',claim_revision=2,statement_and_scope_changed=False,evidence_relation='Additional exact certificates for the existing conditional exclusion; no new family or target claim.',started_at=start,completed_at=datetime.now(timezone.utc).isoformat(),source_commit=head,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,records=records,selected_simplest=simple,selected_strongest=strong,distinct_original_choices=89308,weight_sets_checked=9,per_weight_set_centers=84,positive_certificates=9,controls=controls,producer_imported=False,method='Exact Fraction rounding ties away from zero; direct raw-neighborhood column sums for every original star and all9 weights; all center maxima and first original argmax IDs checked. No producer or serialized sparse matrix import.',D1=dict(lower_bound=204,rhs_dot=379,sum_center_maxima=175,denominator=1),shared_components=['Python standard library','prior independent raw-neighborhood scorer and rook controls','pinned independent complete-domain/necessary-model reviews'],limitations=['Only exact156fixedK/prescribedabsence/two-root0-sign-coordinate family excluded.','D1 is simplest by the preregistered denominator order, not a claimed globally minimal certificate.','No unrestricted resolution or target-wide coverage percentage.'])
    out=ROOT/'acceleration/results/20260917_independent_review/two_coordinate_small_certificate.json';save=lambda p,d:p.open('x').write(json.dumps(d,indent=2));save(out,report);print(report['status'],h.digest(out))
if __name__=='__main__':main()
