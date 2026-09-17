"""Independent finite cyclic/sign clause-image and frozen-corpus union audit."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import combinations
import json
import platform
from pathlib import Path
import sys
import time
from tqdm import tqdm
import audit_20260917_matching_cut_recheck as checked

ROOT=checked.ROOT
DIR=ROOT/'acceleration/results/20260917_matching_cut_cyclic'

def main():
    tick=time.perf_counter();bindings={}
    def read(p):
        p=Path(p);bindings[checked.key(p)]=checked.digest(p);d=json.loads(p.read_bytes())
        for f,h in d.get('inputs_sha256',{}).items():
            checked.require(checked.digest(ROOT/f)==h,'bound input '+f);bindings[f]=h
        return d
    out=ROOT/'acceleration/results/20260917_independent_review/matching_cut_cyclic.json';checked.require(not out.exists(),'preserve audit')
    for p in (__file__,checked.__file__,ROOT/'uv.lock'):bindings[checked.key(p)]=checked.digest(p)
    manifest=read(DIR/'manifest.json');summary=read(DIR/'summary.json');maps=read(DIR/'maps.json');bank=read(DIR/'cut_bank.json')
    for name in ('manifest','maps','cut_bank'):checked.require(checked.digest(DIR/(name+'.json'))==summary[name+'_sha256'],'raw identity '+name)
    gate=read(ROOT/manifest['gate']['path']);checked.require(checked.digest(ROOT/manifest['gate']['path'])=='3e807d158c7fea05e5a31ec631105fa1733e3ca86ad96549cc46a14dcf3e5fc9','parent clause independent gate')
    identity=read(ROOT/'acceleration/results/20260917_independent_review/matching_cut_application.json')
    checked.require(identity['status']=='INDEPENDENT_IDENTITY_CUT_APPLICATION_PASS' and checked.digest(ROOT/'acceleration/results/20260917_independent_review/matching_cut_application.json')=='8309785170aa4b2c253ef2f9109d7912035467a95d11ffae1e6a067542cd17d2','identity union audit')
    corpus=read(ROOT/'acceleration/results/20260917_matching_cut/next_application_protocol.json')['corpus']
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    label_lookup={frozenset(p):v for v,p in enumerate(labels,15)}
    def derive(r,m):
        root_images={1+2*g+s:1+2*((g+r)%7)+(s^((m>>((g+r)%7))&1))for g in range(7)for s in range(2)}
        outer_images=[label_lookup[frozenset(root_images[s+1]-1 for s in pair)]for pair in labels]
        return [0]+[root_images[v]for v in range(1,15)]+outer_images
    def image(es,mp):return frozenset(tuple(sorted((mp[u],mp[v])))for u,v in es)
    def valid_map(mp):
        checked.require(len(mp)==99 and set(mp)==set(range(99)) and mp[0]==0,'full99 permutation')
        checked.require(image(checked.scaffold(),mp)==checked.scaffold(),'scaffold preservation')
    mapping={}
    for row in maps['maps']:
        r,m=row['group_shift'],row['target_group_sign_mask'];mp=row['full99_vertex_map']
        checked.require(row['map_id']==128*r+m and mp==derive(r,m),'explicit cyclic/target-sign mapping')
        valid_map(mp);checked.require((r,m)not in mapping,'duplicate coordinate map');mapping[r,m]=mp
    checked.require(set(mapping)=={(r,m)for r in range(7)for m in range(128)} and len({tuple(mp)for mp in mapping.values()})==896,'complete unique896 maps')
    parents=[]
    for p in bank['parent_cut_paths']:
        d=read(ROOT/p);checked.require(checked.digest(ROOT/p)==gate['inputs_sha256'][p],'parent literal binding');parents.append(d)
    checked.require(len(parents)==16,'parent16 inventory')
    expected=defaultdict(list)
    for j,parent in enumerate(parents):
        for (r,m),mp in mapping.items():expected[image(parent['cut']['positive_full99_edge_literals'],mp)].append((j,128*r+m))
    actual={}
    for j,c in enumerate(bank['cuts']):
        literals=frozenset(checked.edges(c['positive_literals']));checked.require(c['cut_id']==j and literals not in actual,'unique bank ID/literals')
        witnesses=sorted((w['parent_cut'],w['map_id'])for w in c['witnesses'])
        checked.require(witnesses==sorted(expected[literals]) and c['rhs']==len(literals)-1,'complete image witnesses')
        for parent_id,map_id in witnesses:
            parent=parents[parent_id];mp=mapping[map_id//128,map_id%128]
            checked.require(c['center_full99']==mp[parent['center_full99']] and
                checked.edges(c['positive_K_prerequisites'])==image(parent['retained_K_edges_full99'],mp) and
                checked.edges(c['selected_star_edges'])==image(parent['center_star_edges_full99'],mp),'core/star image split')
        center=c['center_full99'];star=checked.edges(c['selected_star_edges']);core=checked.edges(c['positive_K_prerequisites'])
        selected={v for e in star for v in e if v!=center}
        checked.require(len(star)==len(selected)==8 and all(center in e for e in star) and core|star==literals and
                        int(c['original_star_mask_hex'],16)==sum(1<<(v-15)for v in selected),'mapped mask identity')
        actual[literals]=c
    checked.require(set(actual)==set(expected) and len(actual)==bank['unique_clauses']==summary['unique_clauses']==14336 and
                    sum(map(len,expected.values()))==bank['generated_images']==summary['generated_clause_images']==14336,'finite image/dedup count')
    byidentity={(r['family'],r['proposal_index']):set(map(tuple,r['removed_ids']))for r in identity['records']}
    records=[]
    for item,saved in tqdm(list(zip(corpus,summary['records'])),desc='Independent cyclic/sign application',unit='record'):
        checked.require((item['family'],item['proposal_index'])==(saved['family'],saved['proposal_index']),'frozen corpus order')
        d=read(DIR/saved['path']);checked.require(checked.digest(DIR/saved['path'])==saved['sha256'],'application identity')
        candidate=read(ROOT/item['candidate_path']);domains=read(ROOT/item['original_domains_path'])
        k={(a+15,b+15)for a,b in candidate['overlap_edges_outer_zero_based']};base=k|checked.scaffold()
        lookup=[{int(s,16):j for j,s in enumerate(row['domain_masks_hex'])}for row in domains['domains']]
        counts=[len(row['domain_masks_hex'])for row in domains['domains']]
        checked.require(len(lookup)==84 and [len(t)for t in lookup]==counts,'original unique ID tables')
        hit=defaultdict(list);matched=[];absent=[]
        # Complete bank scan; all failures are accounted, not only replayed hits.
        for c in bank['cuts']:
            center=c['center_full99'];star=checked.edges(c['selected_star_edges']);literals=checked.edges(c['positive_literals'])
            checked.require(not star&base,'other-center nonhit proof premise')
            missing=literals-base
            # All eight star literals must come from this center's 8-edge
            # original choice. Any additional missing edge makes a hit impossible.
            if missing!=star:continue
            matched.append(c['cut_id']);mask=int(c['original_star_mask_hex'],16);u=center-15
            if mask not in lookup[u]:absent.append(c['cut_id']);continue
            j=lookup[u][mask];hit[u,j].append(c['cut_id'])
        checked.require(matched==d['core_matching_cut_ids'] and absent==d['core_matching_but_star_absent_cut_ids'],'all core/nonhit partitions')
        raw={(r['outer_vertex'],r['original_domain_id']):r for r in d['removed_choices']}
        checked.require(set(raw)==set(hit) and len(raw)==len(d['removed_choices']),'complete union IDs')
        ident=byidentity[item['family'],item['proposal_index']]
        for (u,j),ids in hit.items():
            row=raw[u,j];checked.require(row['hit_unique_cut_ids']==sorted(ids) and row['mask_hex']==domains['domains'][u]['domain_masks_hex'][j] and
                row['covered_by_original16identity']==((u,j)in ident),'hit masks/clause identity')
        n=len(hit);hits=sum(map(len,hit.values()));generated=sum(len(bank['cuts'][i]['witnesses'])for ids in hit.values()for i in ids)
        histogram={str(n):v for n,v in Counter(map(len,hit.values())).items()};pervertex=[sum(u==v for u,j in hit)for v in range(84)]
        vals=dict(original_choices=sum(counts),unique_removed_choices=n,surviving_choices=sum(counts)-n,unique_clause_hits=hits,generated_image_hits=generated,
            original16identity_removed=len(ident),intersection_with_original16identity=len(ident&set(hit)),additional_unique_removed=len(set(hit)-ident),direct_literal_and_witness_checks=hits)
        checked.require(all(d[k]==v for k,v in vals.items()) and all(saved[k]==v for k,v in vals.items()if k in saved),'application counts')
        checked.require(d['unique_choice_hit_multiplicity_histogram']==histogram and d['per_vertex_removed']==pervertex and d['per_vertex_original']==counts and
                        d['empty_domains']==[u for u,n in enumerate(counts)if n==pervertex[u]],'union survivors')
        records.append(dict(family=item['family'],proposal_index=item['proposal_index'],**vals))
    checked.require(len(records)==len(corpus)==29 and all(r['additional_unique_removed']==0 and r['intersection_with_original16identity']==r['unique_removed_choices']for r in records),'finite no-additional result')
    totals={k:sum(r[k]for r in records)for k in ('original_choices','unique_removed_choices','unique_clause_hits','generated_image_hits','additional_unique_removed')}
    checked.require(all(summary[k]==v for k,v in totals.items()),'summary totals')
    controls=[dict(name='identity_coordinate_map',outcome='PASS')];checked.require(derive(0,0)==list(range(99)),'identity control')
    for name in ('duplicate_image','wrong_outer_label','moved_root'):
        mp=derive(0,0)
        if name=='duplicate_image':mp[-1]=mp[-2]
        if name=='wrong_outer_label':mp[15],mp[19]=mp[19],mp[15]
        if name=='moved_root':mp[0],mp[1]=mp[1],mp[0]
        try:valid_map(mp)
        except ValueError as e:controls.append(dict(name=name,outcome='REJECT',reason=str(e)))
        else:raise ValueError('corrupt map accepted')
    checked.require(all(checked.digest(ROOT/f)==h for f,h in bindings.items()),'inputs changed')
    result=dict(status='INDEPENDENT_CYCLIC_SIGN_CUT_APPLICATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],
        command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        claim_id='C-MATCHING-CYCLIC-SIGN-NO-GAIN-29',claim_revision=1,recommendation='VERIFIED',maps=896,parents=16,generated_images=14336,unique_clauses=14336,
        totals=totals,records=records,controls=controls,all_bank_clauses_scanned_for_each_record=True,producer_imported=False,
        dependencies=[dict(id='C-MATCHING-POSITIVE-CUTS-16',revision=1,relation='uses_result'),dict(id='C-MATCHING-POSITIVE-CUTS-APPLICATION-29',revision=1,relation='verification_dependency')],
        derivation='Every full99 bijection preserves the positive scaffold. Applying its inverse to a hypothetical target transfers the approved parent clause; this is relabeling invariance, not an automorphism assumption.',
        shared_trusted_components=['Python standard library','tqdm','prior independent scaffold/edge checker','hash-bound prior independent clauses and identity application'],
        limitations=['Finite896 coordinate maps only, not full root relabeling group','Only frozen29 original-domain corpus','No new wholeK exclusion or target resolution','Matching obstruction not recomputed for every image; independently checked clause transport suffices'],target_resolution='UNKNOWN',elapsed_seconds=time.perf_counter()-tick)
    out.open('x',encoding='utf-8').write(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],totals=totals,sha256=checked.digest(out))))

if __name__=='__main__':main()
