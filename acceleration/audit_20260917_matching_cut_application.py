"""Independent complete identity-cut application check on frozen29 records."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import time
from tqdm import tqdm
import audit_20260917_matching_cut_recheck as proof

ROOT=proof.ROOT
DIR=ROOT/'acceleration/results/20260917_matching_cut_application'

def hits(base,center,mask,literal_sets):
    star={(min(center,v+15),max(center,v+15)) for v in range(84) if mask>>v&1}
    present=base|star
    return [name for name,literals in literal_sets if not literals-present]

def main():
    start=time.perf_counter();bindings={}
    def read(p):
        p=Path(p);bindings[proof.key(p)]=proof.digest(p);d=json.loads(p.read_bytes())
        for f,h in d.get('inputs_sha256',{}).items():
            proof.require(proof.digest(ROOT/f)==h,'bound input changed '+f);bindings[f]=h
        return d
    out=ROOT/'acceleration/results/20260917_independent_review/matching_cut_application.json'
    proof.require(not out.exists(),'preserve audit')
    for p in (__file__,proof.__file__,ROOT/'uv.lock'):bindings[proof.key(p)]=proof.digest(p)
    manifest=read(DIR/'manifest.json');summary=read(DIR/'summary.json')
    proof.require(proof.digest(DIR/'manifest.json')==summary['manifest_sha256'],'manifest identity')
    protocol=read(ROOT/manifest['preregistration']);gate=read(ROOT/manifest['independent_gate']['path'])
    proof.require(proof.digest(ROOT/manifest['independent_gate']['path'])=='3e807d158c7fea05e5a31ec631105fa1733e3ca86ad96549cc46a14dcf3e5fc9' and
                  gate['status']=='INDEPENDENT_POSITIVE_MATCHING_CUTS_PASS','approved exact clauses')
    cuts=[];cut_summary=read(ROOT/'acceleration/results/20260917_matching_cut/summary.json')
    for r in cut_summary['records']:
        name=f"acceleration/results/20260917_matching_cut/vertex_{r['outer_vertex']:02d}_domain_{r['domain_id']}.json"
        d=read(ROOT/name);proof.require(proof.digest(ROOT/name)==gate['inputs_sha256'][name],'clause gate binding')
        cuts.append((name,d['center_full99'],proof.edges(d['cut']['positive_full99_edge_literals']),proof.edges(d['center_star_edges_full99']),proof.edges(d['retained_K_edges_full99'])))
    proof.require(len(cuts)==16 and len({c[1]for c in cuts})==16,'identity centers')
    inventory=[(r['family'],r['proposal_index'])for r in protocol['corpus']]
    proof.require(len(inventory)==len(set(inventory))==29 and inventory==[(r['family'],r['proposal_index'])for r in summary['records']],'frozen29 records')
    checked=[];total_checked=0;total_matching=0
    for item,saved in tqdm(list(zip(protocol['corpus'],summary['records'])),desc='Independent cut application',unit='record'):
        candidate=read(ROOT/item['candidate_path']);domains=read(ROOT/item['original_domains_path']);complete=read(ROOT/item['original_domain_audit_path'])
        raw=read(DIR/saved['path']);proof.require(proof.digest(DIR/saved['path'])==saved['sha256'],'application raw hash')
        proof.require(raw['candidate_path']==item['candidate_path'] and raw['original_domains_path']==item['original_domains_path'],'raw original mapping')
        proof.require(complete['complete_used_domains_verified']is True and complete['status']=='INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and
                      domains['complete_domain_enumeration']is True and [r['outer_vertex']for r in domains['domains']]==list(range(84)),'prior original-domain completeness binding')
        k={(u+15,v+15)for u,v in candidate['overlap_edges_outer_zero_based']};base=proof.scaffold()|k
        proof.require(all(not(star&base) for _,_,_,star,_ in cuts),'other-center coverage premise')
        # All eight required star edges are absent from base. A star at any
        # other center can add at most one of those eight distinct edges.
        # Thus every unlisted center is completely covered without sampling.
        counts=[]
        for row in domains['domains']:
            masks=[int(s,16)for s in row['domain_masks_hex']]
            proof.require(len(masks)==len(set(masks)) and all(0<=m<1<<84 and m.bit_count()==8 for m in masks),'original choice population')
            counts.append(len(masks))
        removal={};per_cut={};direct=0
        for name,center,literals,star,core in cuts:
            u=center-15;ids=[]
            for j,s in enumerate(domains['domains'][u]['domain_masks_hex']):
                direct+=1
                if hits(base,center,int(s,16),[(name,literals)]):
                    ids.append(j);removal.setdefault((u,j),[]).append(name)
            per_cut[name]=ids
        proof.require(counts==raw['per_vertex_original_choices'] and sum(counts)==raw['original_choices']==saved['original_choices'],'population count')
        proof.require(direct==raw['direct_literal_checks']==saved['direct_literal_checks'],'checked scope count')
        for row,(name,center,literals,star,core)in zip(raw['per_cut_results'],cuts):
            proof.require(row['cut_path']==name and row['center_full99']==center and row['matching_original_domain_ids']==per_cut[name] and
                          row['K_prerequisites_match']==(core<=k) and proof.edges(row['missing_K_prerequisite_edges'])==core-k,'per-cut mapping/count')
        raw_removed={(r['outer_vertex'],r['original_domain_id']):r for r in raw['removed_original_choices']}
        proof.require(len(raw_removed)==len(raw['removed_original_choices']) and set(raw_removed)==set(removal),'exact union IDs')
        for (u,j),names in removal.items():
            r=raw_removed[u,j];s=domains['domains'][u]['domain_masks_hex'][j];mask=int(s,16);center=u+15
            proof.require(r['original_mask_hex']==s and r['hit_cut_paths']==sorted(names) and r['direct_literal_containment']is True,'removed choice association')
            star={(min(center,v+15),max(center,v+15))for v in range(84)if mask>>v&1}
            _,hood,forced,free,allowed=proof.permissive(base|star,center)
            witness=r['separate_matching_feasibility']
            proof.require(proof.edges(witness['forced_edges'])==forced and witness['free_vertices']==free and
                          proof.edges(witness['possible_edges'])==allowed and witness['matching_exists']is False,'full permissive graph mismatch')
            proof.require(not proof.perfect_exists(free,allowed),'falsification: removed choice has perfect matching')
            total_matching+=1
        removed_counts=Counter(u for u,j in removal);survivors=[n-removed_counts[u]for u,n in enumerate(counts)]
        clause_hits=sum(map(len,per_cut.values()));hist={str(n):c for n,c in Counter(map(len,removal.values())).items()}
        intersections=[dict(cuts=[a,b],original_ID_pairs=sorted(set((next(c[1]for c in cuts if c[0]==a)-15,j)for j in per_cut[a]) & set((next(c[1]for c in cuts if c[0]==b)-15,j)for j in per_cut[b]))) for a,b in combinations(sorted(per_cut),2)]
        intersections=[r for r in intersections if r['original_ID_pairs']]
        proof.require(raw['hit_multiplicity_histogram']==hist and raw['overlapping_clause_pairs']==intersections and
                      raw['clause_hit_count']==saved['clause_hit_count']==clause_hits and raw['unique_removed_choices']==saved['unique_removed_choices']==len(removal),'union/multiplicity')
        proof.require(raw['per_vertex_survivors']==survivors and raw['surviving_choices']==saved['surviving_choices']==sum(survivors) and
                      raw['empty_domains']==saved['empty_domains']==[u for u,n in enumerate(survivors)if not n] and raw['full_K_exclusion_claimed']is False,'survivors/scope')
        total_checked+=direct;checked.append(dict(family=item['family'],proposal_index=item['proposal_index'],original_choices=sum(counts),removed_ids=sorted(removal),unique_removed=len(removal),clause_hits=clause_hits,surviving_choices=sum(survivors),direct_checks=direct,empty_domains=raw['empty_domains']))
    controls=[]
    sample_name,sample_center,sample_lits,sample_star,sample_core=cuts[0]
    mask=sum(1<<(next(v for v in e if v!=sample_center)-15)for e in sample_star)
    base=proof.scaffold()|sample_core
    proof.require(hits(base,sample_center,mask,[(sample_name,sample_lits)])==[sample_name],'positive hit control');controls.append(dict(name='positive_literal_set',outcome='PASS'))
    proof.require(not hits(base,sample_center,mask&(mask-1),[(sample_name,sample_lits)]),'missing star edge accepted');controls.append(dict(name='deleted_star_literal',outcome='REJECT'))
    removed_core=next(iter(sample_core));proof.require(not hits(base-{removed_core},sample_center,mask,[(sample_name,sample_lits)]),'missing core accepted');controls.append(dict(name='deleted_core_literal',outcome='REJECT'))
    totals={k:sum(r[k]for r in checked)for k in ('original_choices','unique_removed','clause_hits','surviving_choices','direct_checks')}
    for ours,theirs in [('original_choices','original_choices'),('unique_removed','unique_removed_choices'),('clause_hits','clause_hit_count'),('surviving_choices','surviving_choices'),('direct_checks','direct_literal_checks')]:proof.require(totals[ours]==summary[theirs],'total '+ours)
    proof.require(total_matching==summary['matching_feasibility_checks'] and summary['empty_candidate_domains']==[] and not any(r['empty_domains']for r in checked),'matching total/empty domains')
    proof.require(all(proof.digest(ROOT/f)==h for f,h in bindings.items()),'evidence changed')
    result=dict(status='INDEPENDENT_IDENTITY_CUT_APPLICATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],
        command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        claim_id='C-MATCHING-POSITIVE-CUTS-APPLICATION-29',claim_revision=1,recommendation='VERIFIED',
        scope='Exact identity16 clause union on frozen29 original-domain records; named(candidate,outervertex,originalID) units',
        dependency=dict(id='C-MATCHING-POSITIVE-CUTS-16',revision=1,relation='uses_result'),records=checked,totals=totals,
        independent_full_permissive_matching_checks=total_matching,controls=controls,producer_imported=False,
        shared_trusted_components=['Python standard library','tqdm display','prior independently reviewed set-neighborhood/parity helper','hash-bound prior exhaustive original-domain audits'],
        scope_coverage='All choices at16 cut centers checked literally; other68 centers excluded by eight absent distinct required edges and at mostone incident added edge',
        limitations=['No orbit expansion','No entireK exclusion','No domain completeness reenumeration here','No target coverage denominator'],target_resolution='UNKNOWN',elapsed_seconds=time.perf_counter()-start)
    out.open('x',encoding='utf-8').write(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],totals=totals,sha256=proof.digest(out))))

if __name__=='__main__':main()
