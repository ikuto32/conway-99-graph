"""Independent complete enumeration for six sign coordinates at root groups zero, one and two."""
from datetime import datetime,timezone
from itertools import combinations
import json
import platform
import subprocess
import sys
import time
from tqdm import tqdm
import audit_20260917_partial_matching as h
import audit_20260917_affected_star_caps as affected_caps

ROOT=h.ROOT;D=ROOT/'acceleration/results/20260917_partial_six_matchings';O=ROOT/'acceleration/results/20260917_independent_review/six_matchings';OLD=ROOT/'acceleration/results/20260917_partial_four_matchings'
def main():
    O.mkdir(exist_ok=True);bindings={};started=datetime.now(timezone.utc).isoformat();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    def read(p):
        bindings[h.key(p)]=h.digest(p);d=json.loads(p.read_bytes())
        for f,v in d.get('inputs_sha256',{}).items():h.require(h.digest(ROOT/f)==v,'changed input');bindings[h.key(ROOT/f)]=v
        return d
    manifest=read(D/'manifest.json');summary=read(D/'summary.json');oldmanifest=read(OLD/'manifest.json'); originalmanifest=read(h.D/'manifest.json')
    for f,v in summary['output_sha256'].items():h.require(h.digest(D/f)==v,'changed output');bindings[h.key(D/f)]=v
    oldproofpath=ROOT/'acceleration/results/20260917_independent_review/four_matchings/summary.json';h.require(h.digest(oldproofpath)=='fb21f69b6e5785e0897bccb6965bfea75c171aad2e685b7d60966bc5c8019e73','old audit');read(oldproofpath)
    baseline=read(ROOT/next(f for f in originalmanifest['inputs_sha256']if f.endswith('_candidate.json')))
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)];support=[{s//2 for s in p}for p in labels]
    Y=set();affected=[]
    for sign in (0,1,2,3,4,5):
        group=[u for u,p in enumerate(labels)if sign in p];h.require(len(group)==12,'sign coordinate vertices');affected+=group
        Y|={e for e in combinations(group,2)if len(support[e[0]]&support[e[1]])==1}
    affected=sorted(set(affected));K=set(map(tuple,baseline['overlap_edges_outer_zero_based']));removed=K&Y;fixed=K-removed
    unknown=sorted(Y|{e for e in combinations(range(84),2)if not support[e[0]]&support[e[1]]})
    h.require(len(Y)==360 and len(removed)==36 and len(fixed)==132 and len(unknown)==2040 and len(affected)==60,'scope dimensions')
    for name,actual in [('freed_legal_matching_edges_outer',Y),('removed_edges_outer',removed),('remaining_fixed_K_edges_outer',fixed),('unknown_edges_outer',unknown)]:h.require(manifest[name]==sorted(map(list,actual)),'scope identity '+name)
    B=[0]*99
    for v in range(1,15):h.add(B,0,v)
    for v in range(1,15,2):h.add(B,v,v+1)
    for u,pair in enumerate(labels,15):
        for s in pair:h.add(B,u,s+1)
    for u,v in fixed:h.add(B,u+15,v+15)
    h.require(h.valid(B),'fixed partial graph')
    oldfixed=set(map(tuple,oldmanifest['remaining_fixed_K_edges_outer']));h.require(fixed<=oldfixed,'nested fixed graph')
    released=oldfixed-fixed;calibration_tables={u:[int(m,16)for m in read(D/f'domain_{u:02d}.json')['domain_masks_hex']]for u in (0,12,60)};leaf_controls=affected_caps.controls(B,labels,unknown,calibration_tables);leaf_checker=affected_caps.StarValidator(B);deadline=time.monotonic()+900;reports=[];tables=[]
    for u in tqdm(range(84),desc='Independent six-coordinate domains',unit='center'):
        saved=read(D/f'domain_{u:02d}.json');old=read(OLD/f'domain_{u:02d}.json')
        found,nodes,single=h.enumerate_all(B,labels,unknown,u,deadline,5000000)
        actual=[int(v,16)for v in saved['domain_masks_hex']];h.require(len(actual)==len(set(actual))and found==sorted(actual),'complete local set')
        h.require(saved['outer_vertex']==u and saved['domain_size']==len(found)and saved['allowed_single_neighbors']==single and saved['missing_neighbor_count']==14-B[u+15].bit_count(),'domain metadata')
        h.require(all(leaf_checker.check(u,m)for m in found),'full99 exact affected-pair leaves')
        extra=sum(1<<(v if a==u else a)for a,v in released if u in(a,v));position={m:i for i,m in enumerate(actual)}
        mapping=[position.get(int(m,16)|extra)for m in old['domain_masks_hex']]
        h.require(None not in mapping and mapping==saved['old_to_new_domain_ids']and len(mapping)==saved['old_embedded_choices'],'original ID full-neighborhood embedding')
        row=dict(outer_vertex=u,complete_domain_size=len(found),independent_nodes=nodes,direct_full99_leaves=len(found),old_embedded_choices=len(mapping),raw_sha256=h.digest(D/f'domain_{u:02d}.json'))
        reports.append(row);tables.append(found)
        with(O/f'vertex_{u:02d}.json').open('x')as f:json.dump(row,f,indent=2)
    controls=[]
    for u in(0,12,60):
        selected=h.bits(tables[u][0]);pool=sorted(selected+[v for v in h.bits(tables[u][-1])if v not in selected][:12-len(selected)]);need=14-B[u+15].bit_count()
        brute=sorted(sum(1<<v for v in group)for group in combinations(pool,need)if h.direct(B,labels,u,sum(1<<v for v in group)))
        actual,_,_=h.enumerate_all(B,labels,unknown,u,deadline,5000000,set(pool));h.require(brute==actual,'restricted exhaustive fixture');h.require(not h.direct(B,labels,u,0),'corrupt zero star')
        controls.append(dict(center=u,pool=pool,valid=len(brute),subsets=len(list(combinations(pool,need))),corrupt_zero_rejected=True))
    for p in(__file__,h.__file__,affected_caps.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    h.require(all(h.digest(ROOT/f)==v for f,v in bindings.items()),'input changed during check')
    count=sum(map(len,tables));embedded=sum(r['old_embedded_choices']for r in reports);h.require(count==879449==summary['complete_domain_choices']and embedded==290460==summary['all_old_neighborhood_embeddings']==summary['old_choices_located_in_complete_domains'],'population totals')
    result=dict(status='INDEPENDENT_SIX_COORDINATE_DOMAINS_PASS',claim_id='C-PARTIAL-K-SIX-COORDINATE-DOMAINS',claim_revision=1,recommendation='VERIFIED',statement='The frozen tables contain exactly all locally admissible degree14 stars satisfying full99 upper common-neighbor caps and exact14 root quotas in the declared six-coordinate scope; every prior four-coordinate star embeds with identical full outer neighborhood.',started_at=started,completed_at=datetime.now(timezone.utc).isoformat(),source_commit=head,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,records=reports,domain_choices=count,old_embedded_choices=embedded,centers=84,fixed_K_edges=132,freed_matching_edges=360,unknown_edges=2040,affected_centers=60,missing_neighbor_histogram={k:sum(14-B[u+15].bit_count()==k for u in range(84))for k in (8,9,10)},controls=controls,affected_pair_full4851_calibration=leaf_controls,leaf_validation_method='Every full99 cap checked using explicit unchanged-pair proof plus exact recomputation of all changed pairs; fixedB caps verified once. See bound independent helper module docstring.',producer_imported=False,shared_components=['Python standard library','tqdm','prior independent multiway demand-subset enumerator','new exact affected-pair checker calibrated against full4851-pair implementation'],scope='Both same-sign coordinates at rootgroups0,1and2 freed; exactly132 baseline K edges and all other prescribed absences retained. No nontrivial automorphism assumption.',limits=dict(seconds=900,nodes_per_center=5000000),limitations=['Local domains alone do not establish global feasibility or exclusion.','No broader K-family coverage or count asserted.'])
    with(O/'summary.json').open('x')as f:json.dump(result,f,indent=2)
    print(result['status'],count,h.digest(O/'summary.json'))
if __name__=='__main__':main()
