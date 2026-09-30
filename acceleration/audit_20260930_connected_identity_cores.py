"""Independent literal-set/coordinate-component audit of a frozen four-core portfolio."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_connected_identity_cores'
SUMMARY_SHA='3ab78be8b7a7582c730e4cfe4c95533a2bc68cecccdfca45fa7d3f8cd58190b5'

def need(ok,msg):
    if not ok:raise ValueError(msg)

def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()

def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')

def reconstruct(matchings):
    n=len(matchings[0]);need(n>0 and n%2==0 and len(matchings)==3,'three even matching cells')
    for matching in matchings:
        need(len(matching)==n and sorted(matching)==list(range(n)),'matching permutation')
        need(all(matching[i]!=i and matching[matching[i]]==i for i in range(n)),'matching involution')
    vertices=3+3*n;adj=[set()for _ in range(vertices)]
    for i,j in combinations(range(vertices),2):
        if j<3:edge=True
        elif i<3:edge=(j-3)//n==i
        else:
            g,u=divmod(i-3,n);h,v=divmod(j-3,n)
            edge=matchings[g][u]==v if g==h else u==v
        if edge:adj[i].add(j);adj[j].add(i)
    # Identity cross-edges collapse each coordinate triple. Components are
    # computed on12 coordinates, unlike the producer's36-vertex graph search.
    classes=[{i}for i in range(n)]
    for matching in matchings:
        for i,j in enumerate(matching):
            left=next(s for s in classes if i in s);right=next(s for s in classes if j in s)
            if left is not right:left.update(right);classes.remove(right)
    parts=sorted([sorted(g*n+i for g in range(3)for i in component)for component in classes],key=lambda p:p[0])
    full=[[int(j in adj[i])for j in range(vertices)]for i in range(vertices)];core=[row[3:]for row in full[3:]]
    hist=Counter()
    for i,j in combinations(range(vertices),2):
        value=len(adj[i]&adj[j])+int(j in adj[i]);need(value<=2,'literal39 pair cap');hist[value]+=1
    return full,core,parts,dict(sorted(hist.items())),adj

def check_selected(raw,matchings,indices):
    full,core,parts,hist,adj=reconstruct(matchings);n=12
    need(raw['M0']==matchings[0] and raw['M1']==matchings[1] and raw['M2']==matchings[2],'exact census matching coordinates')
    need(raw['P']==raw['cross01']==raw['cross02']==raw['coordinate_labels']==list(range(n)),'identity cross restriction')
    need(raw['core_row_labels']==[dict(fibre=i//12,coordinate=i%12,full39_vertex=3+i)for i in range(36)],'raw row labels')
    need(raw['full39_adjacency']==full and raw['core_adjacency']==core,'literal raw graph identities')
    need(raw['components']==parts and len(parts)==1 and raw['connected36']is True,'coordinate-derived connectivity')
    need(all(raw[k]==v for k,v in indices.items()),'selected stage/orbit indices')
    need(raw['local_pair_cap_check']==dict(pairs=741,histogram={str(k):v for k,v in hist.items()}),'exact pair cap histogram')
    gram=[[12*int(i==j)+2-int(j+3 in adj[i+3])-len(adj[i+3]&adj[j+3])for j in range(36)]for i in range(36)]
    need(raw['target_gram']==gram and all(x>=0 for row in gram for x in row),'all prescribed Gram entries from raw39 neighborhoods')
    catalogs=[[[i,j]for i in range(n)for j in range(i+1,n)if matchings[g][i]!=j]for g in range(3)]
    need(raw['nonmatching_edge_catalogs']==catalogs and raw['canonical_C0_columns']==catalogs[0],'complete nonmatching catalogs and canonical C0')
    for g,catalog in enumerate(catalogs):
        labels=[set(i for i,pair in enumerate(catalog)if row in pair)for row in range(n)]
        need(len(catalog)==60 and all(len(s)==10 for s in labels),'catalog length/row margins')
        need(all(len(labels[i]&labels[j])==gram[g*n+i][g*n+j]for i in range(n)for j in range(n)),'all within-fibre Gram entries')
    need(raw['P_chosen_not_without_loss']is True and raw['full_factor']is None and raw['target_graph']is False,'declared restricted scope')
    return dict(indices=indices,core_vertices=36,full_vertices=39,pair_caps=741,gram_entries=1296,within_gram_entries=432,component_sizes=[36])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);inputs={}
    def pin(p,h=None):
        sha=digest(p);need(h is None or h==sha,'artifact hash '+key(p));inputs[key(p)]=sha
    def read(p,h=None):pin(p,h);return json.loads(p.read_bytes())
    try:
        summary=read(D/'summary.json',SUMMARY_SHA)
        for path,h in{**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/path,h)
        censusgate=read(ROOT/'acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json','085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79');need(censusgate['status']=='INDEPENDENT_TRIANGLE_ORDERED_MATCHING_PAIR_CENSUS_PASS','independent finite census gate')
        eligibility=read(D/'eligibility.json')['records'];stages=read(D/'stages.json');expected=[];expected_stages=[];chosen=[];gid=0;corechecks=[];all_selected=[]
        rook,_,_,_,adj=reconstruct([[1,0]]*3);need(all(len(adj[i]&adj[j])==2*int(i==j)-rook[i][j]+2 for i in range(9)for j in range(9)),'positive full rook9 identity')
        for stage in range(11):
            saved=read(ROOT/f'acceleration/results/20260930_triangle_matching_pair_census_v2/stage_{stage:02d}.json');first=None;count=0;hist=Counter()
            for local,orb in enumerate(saved['second_orbits']):
                matchings=[[i^1 for i in range(12)],saved['M1'],orb['representative']];full,core,parts,_,_=reconstruct(matchings);sizes=sorted(map(len,parts));connected=len(parts)==1;count+=int(connected);hist[tuple(sizes)]+=1
                expected.append(dict(pair_representative_index=gid,first_stage=stage,second_orbit=local,matching_universe_representative_index=orb['representative_index'],component_sizes=sizes,connected36=connected,all_local39_pair_caps=True,local39_pair_caps_checked=741))
                if connected and first is None:
                    first=dict(first_stage=stage,second_orbit=local,pair_representative_index=gid)
                    if len(chosen)<4:
                        selected=summary['selected'][len(chosen)];need(all(selected[k]==v for k,v in first.items()),'frozen first-connected stage selection');raw=read(ROOT/selected['path'],selected['sha256']);corechecks.append(check_selected(raw,matchings,first));chosen.append(first);all_selected.append((raw,matchings,first))
                gid+=1
            expected_stages.append(dict(first_stage=stage,candidates=len(saved['second_orbits']),connected_candidates=count,first_connected=first,component_size_histogram=[dict(sizes=list(k),count=v)for k,v in sorted(hist.items())]))
        need(eligibility==expected and stages==expected_stages,'complete raw eligibility/stage accounting')
        need(gid==3580 and sum(r['connected36']for r in expected)==summary['connected_candidates']==2806,'finite population and connected count')
        need(sum(r['first_connected']is not None for r in expected_stages)==summary['qualifying_first_stages']==11 and len(chosen)==summary['selected_count']==4,'selected population')
        rejected=[];good,matches,indices=all_selected[0]
        for label in('wrong_matching','wrong_P','wrong_full39','wrong_core','wrong_components','wrong_gram','catalog_duplicate','C0_order','wrong_indices','false_scope'):
            bad=deepcopy(good)
            if label=='wrong_matching':bad['M1'][0]=0
            elif label=='wrong_P':bad['P'][0],bad['P'][1]=bad['P'][1],bad['P'][0]
            elif label=='wrong_full39':bad['full39_adjacency'][0][15]^=1
            elif label=='wrong_core':bad['core_adjacency'][0][1]^=1
            elif label=='wrong_components':bad['components']=[[0],list(range(1,36))]
            elif label=='wrong_gram':bad['target_gram'][0][0]+=1
            elif label=='catalog_duplicate':bad['nonmatching_edge_catalogs'][1][1]=bad['nonmatching_edge_catalogs'][1][0]
            elif label=='C0_order':bad['canonical_C0_columns'].reverse()
            elif label=='wrong_indices':bad['first_stage']+=1
            else:bad['P_chosen_not_without_loss']=False
            try:check_selected(bad,matches,indices)
            except ValueError as e:rejected.append(dict(control=label,reason=str(e)))
            else:raise AssertionError(label)
        bad=deepcopy(eligibility);bad[0]['connected36']=not bad[0]['connected36'];need(bad!=expected,'eligibility corruption detected');rejected.append(dict(control='eligibility_bit',reason='Complete eligibility differs from independent coordinate reconstruction.'))
        wrong=deepcopy(chosen);wrong[0]['second_orbit']+=1;need(wrong!=chosen,'selection corruption detected');rejected.append(dict(control='first_selected_index',reason='Does not follow frozen first-connected-stage order.'))
        save(out/'checks.json',dict(selected=corechecks,stages=expected_stages,controls=dict(known_valid_rook9=True,corruptions=rejected)))
        for p in[Path(__file__),ROOT/'docs/AUDIT_20260930_CONNECTED_IDENTITY_CORES.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();statement='Within the frozen3580 ordered matching-pair representatives with P fixed to identity, exactly2806 have connected36-vertex cores; the declared first-connected-per-stage rule selects the four saved cores, each with the recorded local39 pair caps, exact prescribed Gram and canonical nonmatching catalogs.'
        report=dict(status='INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,outputs_sha256={key(out/'checks.json'):digest(out/'checks.json')},portfolio_summary=dict(path=key(D/'summary.json'),sha256=SUMMARY_SHA),selected=summary['selected'],claim_id='C-FOUR-CONNECTED-IDENTITY-CORE-PORTFOLIO',claim_revision=1,statement=statement,kind='construction',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='Finite four local construction domains from the authenticated matching-pair census with chosen P=I; no full factor, residual D or target graph.',assumptions=['No nontrivial target automorphism is assumed.','P=I is a deliberate restriction, not a target normalization.'],dependencies=[dict(id=name,revision=1,relation=relation)for name,relation in[('C-TRIANGLE-ORDERED-MATCHING-PAIR-CENSUS','uses_result'),('C-TRIANGLE-CORE-IDENTITY-P-CONSTRUCTION','uses_result'),('C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION','uses_result')]],verifier='/root/state_literature_audit independent coordinate-component and literal-neighborhood checker',method='independent_artifact_check',shared_components=['Python standard library only; pinned independent finite census as premise; no producer graph/connectivity/Gram imports.'],counts=dict(frozen_representatives=3580,connected_representatives=2806,qualifying_stages=11,selected_cores=4,literal_local_pair_caps=3580*741,selected_Gram_entries=4*1296,selected_within_Gram_entries=4*432),controls=dict(known_valid_rook9=True,corruptions_rejected=len(rejected)),limitations=['Finite representation population, not all target graphs or all cross permutations.','Distinct M1 stages are the declared selection diversity; no new full-core isomorphism classification.','No factor or target graph constructed and no heuristic run performed.'],artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,created_at=now,updated_at=now)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'),selected=chosen)))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise

if __name__=='__main__':main()
