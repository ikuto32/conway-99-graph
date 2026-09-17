"""Independent exact integer-scaled savedpoint odd-set diagnostic."""
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import time
import audit_20260917_partial_matching as prior

ROOT=prior.ROOT
D=ROOT/'acceleration/results/20260917_partial_matching_oddsets'
def q(x):return Fraction(int(x['numerator']),int(x['denominator']))
def exact(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator),approximate=float(x))

def main():
    tick=time.perf_counter();bindings={}
    def read(p):
        p=Path(p);bindings[prior.key(p)]=prior.digest(p);d=json.loads(p.read_bytes())
        for f,h in d.get('inputs_sha256',{}).items():prior.require(prior.digest(ROOT/f)==h,'bound input changed');bindings[f]=h
        return d
    out=ROOT/'acceleration/results/20260917_independent_review/partial_oddsets.json';prior.require(not out.exists(),'preserve evidence')
    for p in (__file__,prior.__file__,ROOT/'uv.lock'):bindings[prior.key(p)]=prior.digest(p)
    manifest=read(D/'manifest.json');saved=read(D/'oddset_diagnostic.json');primary=read(prior.D/'manifest.json');numeric=read(prior.D/'numeric_lp.json')
    proof=read(ROOT/'acceleration/results/20260917_independent_review/partial_matching/summary.json')
    prior.require(proof['status']=='INDEPENDENT_PARTIAL_K_DOMAINS_AND_LINEAR_CAPS_PASS'and prior.digest(ROOT/'acceleration/results/20260917_independent_review/partial_matching/summary.json')=='ed1d5b464466562cff722e45593095ec89c63bda761cfa7f784994abfc308b17','independent domains dependency')
    tables=[read(prior.D/f'domain_{u:02d}.json')['domain_masks_hex']for u in range(84)]
    tables=[[int(s,16)for s in t]for t in tables];values=numeric['numeric_probabilities'];prior.require(len(values)==sum(map(len,tables))==54478,'savedpoint inventory')
    offset=0;marginal=[];sums=[]
    for u,table in enumerate(tables):
        raw=values[offset:offset+len(table)];offset+=len(table)
        ratios=[v.as_integer_ratio()for v in raw];scale=max(d for n,d in ratios)
        prior.require(all(n>=0 and scale%d==0 for n,d in ratios),'binary ratios/nonnegative coordinates')
        integers=[n*(scale//d)for n,d in ratios];total=sum(integers);prior.require(total>0,'positive simplex sum')
        original_sum=Fraction(total,scale);sums.append(original_sum)
        accum=[0]*84
        for mask,w in zip(table,integers):
            while mask:
                bit=mask&-mask;mask-=bit;accum[bit.bit_length()-1]+=w
        marginal.append([Fraction(v,total)for v in accum])
        record=saved['per_center_normalizations'][u]
        prior.require(record['outer_vertex']==u and q(record['exact_binary_input_sum'])==original_sum and q(record['deviation_from1'])==original_sum-1,'exact normalization record')
    affected=primary['affected_outer_vertices'];Y=list(map(tuple,primary['freed_legal_matching_edges_outer']))
    weights={(u,v):marginal[u][v]for u,v in Y}
    prior.require(affected==saved['affected_outer_vertices']and len(Y)==60,'freed-coordinate universe')
    prior.require(all(sum(marginal[u][v]for v in affected if (min(u,v),max(u,v))in weights)==1 for u in affected),'own normalized matching degrees')
    for r,(u,v)in zip(saved['matching_edge_marginals'],Y):
        prior.require(r['edge']==[u,v]and q(r['smaller_endpoint'])==marginal[u][v]and q(r['larger_endpoint'])==marginal[v][u]and q(r['exact_difference'])==marginal[u][v]-marginal[v][u],'edge projection/reciprocity')
    degrees={u:sum(w for e,w in weights.items()if u in e)for u in affected}
    for r,u in zip(saved['projected_degrees'],affected):prior.require(r['outer_vertex']==u and q(r['degree'])==degrees[u]and q(r['defect'])==degrees[u]-1,'projected degree')
    rows={r['mask']:r for r in saved['odd_subsets']};excess={}
    # Different finite-universe enumeration: explicit combinations by size.
    for size in range(1,12,2):
        for positions in combinations(range(12),size):
            mask=sum(1<<i for i in positions);selected={affected[i]for i in positions}
            weight=sum((w for (u,v),w in weights.items()if {u,v}<=selected),Fraction())
            value=weight-Fraction(size-1,2);excess[mask]=value;r=rows[mask]
            prior.require(r['outer_vertices']==sorted(selected)and r['size']==size and r['bound']==(size-1)//2 and q(r['exact_internal_weight'])==weight and
                          q(r['exact_excess'])==value and r['violated']==(value>0),'odd-set exact record')
    prior.require(set(excess)==set(rows)and len(rows)==len(saved['odd_subsets'])==saved['odd_subset_count']==2048,'complete odd subsets')
    pair_records={tuple(r['masks']):r for r in saved['complement_pairs']}
    expected_pairs={(m,4095^m)for m in excess if m<(4095^m)}
    prior.require(set(pair_records)==expected_pairs and len(pair_records)==saved['complement_pair_count']==1024,'complete complement pairs')
    for m,c in expected_pairs:
        r=pair_records[m,c];difference=excess[m]-excess[c]
        degree_difference=sum((degrees[u]-1)*(1 if m>>i&1 else -1)for i,u in enumerate(affected))/2
        prior.require(difference==degree_difference==q(r['exact_excess_difference'])and r['violated_members']==[s for s in (m,c)if excess[s]>0]and
                      r['exact_equivalence_at_saved_projection']==(difference==0),'complement identity with degree defects')
    violations=[m for m in sorted(excess)if excess[m]>0];maximum=max(excess.values())
    prior.require(len(violations)==saved['violated_subsets']and maximum==q(saved['maximum_excess'])and saved['maximum_excess_mask']==next(m for m in sorted(excess)if excess[m]==maximum),'strict violation summary')
    prior.require(saved['projected_degrees_exactly1']==all(d==1 for d in degrees.values())and saved['all_matching_reciprocities_exact']==all(marginal[u][v]==marginal[v][u]for u,v in Y),'diagnostic nonfeasibility flags')
    # Exact controls: an integral matching satisfies every odd inequality;
    # two fractional3cycles produce the familiar strict half violation.
    pair_matching={(2*i,2*i+1):Fraction(1)for i in range(6)}
    for mask in rows:
        prior.require(sum(w for (u,v),w in pair_matching.items()if mask>>u&1 and mask>>v&1)<=(mask.bit_count()-1)//2,'positive matching control')
    fractional={(0,1):Fraction(1,2),(0,2):Fraction(1,2),(1,2):Fraction(1,2)}
    prior.require(sum(fractional.values())-1==Fraction(1,2),'fractional triangle control')
    prior.require(all(prior.digest(ROOT/f)==h for f,h in bindings.items()),'inputs changed')
    report=dict(status='INDEPENDENT_PARTIAL_K_SAVED_POINT_ODDSET_DIAGNOSTIC_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],
        command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        claim_id='C-PARTIAL-K-SAVED-POINT-ODDSETS',claim_revision=1,recommendation='VERIFIED',
        normalized_probabilities=54478,centers=84,matching_edges=60,odd_subsets=2048,complement_pairs=1024,strictly_violated_masks=violations,
        maximum_exact_excess=exact(maximum),projected_degrees_exactly1=saved['projected_degrees_exactly1'],all_matching_reciprocities_exact=saved['all_matching_reciprocities_exact'],
        dependency=dict(id='C-PARTIAL-K-ONE-COORDINATE-DOMAINS',revision=1,relation='verification_dependency'),
        controls=[dict(name='integral_matching_all2048',outcome='PASS'),dict(name='fractional_triangle_half_violation',outcome='REJECT_ODDSET')],
        producer_imported=False,shared_trusted_components=['Python standard library','earlier independent artifact helpers'],
        scope='Exact rational interpretation and perstar normalization of this saved floating vector; smaller-endpoint matching projection; no numerical tolerance',
        limitations=['Not an exact feasible LP point or structural matching obstruction','A tiny exact savedpoint violation does not establish any positive lower bound','No family exclusion','StrengthenedV2solver run not covered by this audit'],target_resolution='UNKNOWN',elapsed_seconds=time.perf_counter()-tick)
    out.open('x',encoding='utf8').write(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],violations=violations,max_display=float(maximum),sha256=prior.digest(out))))

if __name__=='__main__':main()
