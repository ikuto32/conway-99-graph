"""Prepare an immutable five-claim registry patch; apply only explicitly.

This registrar consumes independent reviews and checks their artifact bindings.
It performs no scientific verification and never promotes producer agreement.
The default --prepare mode does not write CLAIMS.yaml.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
REV='acceleration/results/20260917_independent_review/'
PINS={
    REV+'rerank_v3_results.json':'be17eb32de607753ca3b7f5972c80a38f58717a235119a78a03e12ccb10a56ed',
    REV+'partial_matching/summary.json':'ed1d5b464466562cff722e45593095ec89c63bda761cfa7f784994abfc308b17',
    REV+'partial_oddsets.json':'d36ba6b7389b1f98075285ab0182b412d3122255c94a2bf069ade3061865e8ff',
    REV+'rerank_v3_calibration_claim_binding.json':'232abf3e4a1d018ebf2fe02bbf97cb1dbb00b47ca4417465dbf26c8eadb7001f',
    REV+'rerank_v3_16_scope.json':'fcb06b8ef67825d8b80e4309b569b8a952ab48026dbed80f1c6ff230bd223a6c',
    REV+'rerank_v3_16_raw.json':'50ceeb88b293f1ee29e23679f6bebba777491010b2c51b92f1d14fdc6bc5d007',
}


def require(ok,message):
    if not ok:raise ValueError(message)


def path(p):
    p=Path(str(p).replace('\\','/'));return (p if p.is_absolute() else ROOT/p).resolve()


def key(p):
    p=path(p);return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()


def digest(p):
    h=sha256()
    with path(p).open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()


def load(p):return json.loads(path(p).read_bytes())


def save(p,d):
    with path(p).open('x',encoding='utf8') as f:f.write(json.dumps(d,indent=2,allow_nan=False)+'\n')


def q(x):return Fraction(int(x['numerator']),int(x['denominator']))


def prepare():
    hashes={}
    def bind(p,h=None):
        k=key(p)
        if k not in hashes:hashes[k]=digest(p)
        require(h is None or hashes[k]==h,'Changed independent evidence: '+k)
        return hashes[k]
    reports=[]
    for p,h in PINS.items():
        bind(p,h);r=load(p)
        for name,expected in r['inputs_sha256'].items():bind(name,expected)
        reports.append(r)
    calibration,partial,odd,calibration_binding,new16,raw16=reports
    require(calibration['status']=='INDEPENDENT_WHOLE_STAR_RERANK_V3_AUDIT_PASS' and calibration['producer_or_native_imported'] is False,
        'Independent reranking review required')
    require(calibration_binding['claim_id']=='C-WHOLE-STAR-RERANK-V3-CALIBRATION' and calibration_binding['claim_revision']==1 and
        calibration_binding['recommendation']=='VERIFIED' and calibration_binding['review_state']=='CLEAR' and
        calibration_binding['statistics']==calibration['calibration_metrics']['statistics'],'Independent calibration claim revision differs')
    require(new16['status']=='INDEPENDENT_WHOLE_STAR_RERANK_V3_SHORTLIST_AUDIT_PASS' and new16['producer_imported'] is False and
        raw16['status']=='THIRD_PATH_EXACT_FIXED_K_STAR_REVIEW_PASS' and new16['records']==raw16['records'] and
        len(new16['selected_indices'])==new16['independent_raw_passes']==16 and new16['domain_choices_checked']==404686 and
        new16['strictly_worse_indices']==new16['selected_indices'] and new16['strictly_better_indices']==[] and
        new16['unseparated_intervals']==[],'Independent new16 exact scope differs')
    require(partial['status']=='INDEPENDENT_PARTIAL_K_DOMAINS_AND_LINEAR_CAPS_PASS' and partial['producer_imported'] is False and
        partial['recommendation']=='VERIFIED' and partial['claim_id']=='C-PARTIAL-K-ONE-COORDINATE-DOMAINS' and partial['claim_revision']==1,
        'Independent partial domain/cap claim binding required')
    require(odd['status']=='INDEPENDENT_PARTIAL_K_SAVED_POINT_ODDSET_DIAGNOSTIC_PASS' and odd['producer_imported'] is False and
        odd['recommendation']=='VERIFIED' and odd['claim_id']=='C-PARTIAL-K-SAVED-POINT-ODDSETS' and odd['claim_revision']==1,
        'Independent saved-point claim binding required')
    metric=calibration['calibration_metrics'];old,new=[metric['statistics'][k] for k in ('iterations500','iterations5000')]
    require(metric['calibration_cases']==16 and metric['total_calibration_pairs']==metric['exact_separated_pairs']==120 and
        metric['ambiguous_exact_pairs']==0 and metric['new_candidates']==0,'Frozen calibration scope differs')
    require(q(old['mean_gap'])==Fraction(10745676638757410733,576460752303423488) and q(new['mean_gap'])==Fraction(169095870021623761,18014398509481984) and
        q(old['median_gap'])==Fraction(1338087308882577117,72057594037927936) and q(new['median_gap'])==Fraction(21100464008006155,2251799813685248),
        'Frozen exact calibration statistics differ')
    require([old['upper_order_disagreements'],new['upper_order_disagreements'],old['lower_order_disagreements'],new['lower_order_disagreements']]==[29,14,24,14] and
        all(s['total_endpoint_violations']==0 and s['endpoint_check_count']==32 for s in (old,new)),'Frozen calibration counts differ')
    require(partial['domain_choices']==54478 and partial['centers']==84 and partial['variable_edges']==1740 and
        partial['freed_matching_edges']==60 and partial['fixed_K_edges']==162 and partial['linear_caps']==3486 and
        [r['outer_vertex'] for r in partial['records']]==list(range(84)) and sum(r['complete_domain_size'] for r in partial['records'])==54478,
        'Frozen complete-domain/cap population differs')
    require(odd['odd_subsets']==2048 and odd['complement_pairs']==1024 and odd['strictly_violated_masks']==[2047] and
        odd['normalized_probabilities']==54478 and odd['matching_edges']==60 and odd['projected_degrees_exactly1'] is False and
        odd['all_matching_reciprocities_exact'] is False and q(odd['maximum_exact_excess'])>0,'Frozen savedpoint diagnostic differs')
    evidence_groups={
        'v3-calibration':{
            'independent':REV+'rerank_v3_results.json',
            'claim-binding':REV+'rerank_v3_calibration_claim_binding.json',
            'manifest':'acceleration/results/20260917_whole_star_rerank_v3/ranking/manifest.json',
            'metrics':'acceleration/results/20260917_whole_star_rerank_v3/ranking/calibration_metrics.json',
            'addendum':'docs/NEXT_20260917_WHOLE_STAR_RERANK_V3_CALIBRATION.md'},
        'partial-coordinate':{
            'independent':REV+'partial_matching/summary.json',
            'independent-manifest':REV+'partial_matching/manifest.json',
            'manifest':'acceleration/results/20260917_partial_matching/manifest.json',
            'caps':'acceleration/results/20260917_partial_matching/linear_caps.json'},
        'partial-oddsets':{
            'independent':REV+'partial_oddsets.json',
            'manifest':'acceleration/results/20260917_partial_matching_oddsets/manifest.json',
            'diagnostic':'acceleration/results/20260917_partial_matching_oddsets/oddset_diagnostic.json',
            'saved-point':'acceleration/results/20260917_partial_matching/numeric_lp.json'},
        'v3-star16':{
            'independent':REV+'rerank_v3_16_scope.json',
            'raw':REV+'rerank_v3_16_raw.json',
            'manifest':'acceleration/results/20260917_whole_star_rerank_v3/shortlist/manifest.json',
            'summary':'acceleration/results/20260917_whole_star_rerank_v3/shortlist/summary.json',
            'checkpoint':'acceleration/results/20260917_whole_star_rerank_v3_checkpoint.json',
            'checkpoint-execution':'acceleration/results/20260917_rerank_v3_checkpoint_execution/receipt.json'},
    }
    artifacts=[]
    for group,files in evidence_groups.items():
        for label,p in files.items():
            artifacts.append(dict(id=group+'-'+label,path=p,sha256=bind(p),availability='LOCAL_ONLY',
                retrieval='Workspace path relative to ikuto32/conway-99-graph; publication must supply this artifact and its referenced run inputs.',
                unavailable_reason='No immutable publication commit is asserted by this prepared patch.'))
    ah={a['id']:a['sha256'] for a in artifacts};now=datetime.now(timezone.utc).isoformat();claims=[]
    def claim(id,statement,kind,basis,scope,assumptions,deps,group,report,shared,controls,limits):
        evidence=[group+'-'+x for x in evidence_groups[group]]
        claims.append(dict(id=id,revision=1,statement=statement,kind=kind,basis=basis,status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),assumptions=assumptions,dependencies=deps,evidence=evidence,
            verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',
                command_or_audit=evidence_groups[group]['independent'],timestamp=report['timestamp'],outcome='PASS',scope=scope,
                artifact_hashes={i:ah[i] for i in evidence},shared_components=shared,controls=controls,limitations=limits)],
            limitations=limits,created_at=now,updated_at=now,unknowns={'external_source':'Current-project result, not an archived imported claim.'},
            external_source=None,reproducibility=dict(manifest=group+'-manifest')))
    claim('C-WHOLE-STAR-RERANK-V3-CALIBRATION',
        'For exactly the16 saved LP-calibration configurations in the frozen128-model cohort, cold5000 versus cold500 PDHG changes the exact mean of saved binary-float endpoint gaps from10745676638757410733/576460752303423488 to169095870021623761/18014398509481984 and their median from1338087308882577117/72057594037927936 to21100464008006155/2251799813685248. Across all120 strictly separated exact-interval pairs, upper-order disagreements decrease29 to14 and lower-order disagreements24 to14, with zero ambiguous exact pairs. Each run has zero violations in32 exact binary-float comparisons against the saved exact interval endpoints.',
        'empirical/engineering result',['COMPUTED'],
        'Only16 named saved calibration cases and their120 unordered pairs under ORIGINAL_STAR_SIMPLEX_PDHG_V1, same model payloads/init and the two specified checkpoint budgets; exact statistics of stored floats.',
        ['The same128 already generated models are reranked; no new candidate count or new model reconstruction is inferred.',
            'Each cold run reports initialization plus its sole requested checkpoint last/average; the500 point is not merged into5000.',
            'Pair order uses ascending score then original row ID; touching/overlapping exact intervals would be ambiguous.'],
        [dict(id='C-WHOLE-FRESH-STAR-16-EXCLUSIONS',revision=1,relation='verification_dependency')],
        'v3-calibration',calibration,calibration['shared_trusted_components'],
        [c['name']+': '+c['outcome'] for c in calibration['metric_controls']]+['Three sampled5000-step independent CPU recurrence controls; not all128 trajectories.'],
        ['No certification of floating-point GPU arithmetic or the numerical optimization values.','No speedup claim, general performance guarantee, graph, or fixed-family exclusion.',
            'Only the16 calibration cases support the reported gap and pair-order improvement; no target-wide progress fraction.'])
    claim(partial['claim_id'],
        'For the frozen baseline18481 partial configuration with root_group0 same_0 matching freed, all84 independently enumerated complete local-star domain tables contain54478 choices in total; its unknown-edge universe is exactly1740 edges (60 permitted edges in that coordinate plus1680 disjoint-label edges), with162 prescribed positive K edges. Every one of the3486 stored linear common-neighbor cap rows equals the exact BE+EB+E derivative row for that same partial graph and prescribed absences.',
        'encoding',['DERIVED','COMPUTED'],partial['scope'],
        ['Only the one named coordinate is freed; the remaining prescribed positive and absent edges are part of the claim.',
            'Local star choices obey the exact degree, root-label quotas and full99 partial common-neighbor caps used by the independent enumeration.',
            'No nontrivial automorphism is assumed.'],
        [dict(id='C-ROOT-SCAFFOLD-NORMALIZATION',revision=1,relation='normalization')],
        'partial-coordinate',partial,['Python standard library','tqdm for progress only; independent enumerator and graph checks import no producer'],
        ['All84 complete domain sets independently enumerated and directly checked on the full99 partial graph.',
            'Restricted pools at centers0 and2 checked by separate220 and495 subset enumerations; corrupt zero mask rejected.'],partial['limitations'])
    excess=odd['maximum_exact_excess']
    claim(odd['claim_id'],
        'For the single saved partial-coordinate floating vector, interpreted as exact binary rationals and normalized independently at each of84 centers, the smaller-endpoint projection onto60 matching edges violates exactly one of all2048 odd-subset inequalities on the12 named coordinate vertices, mask2047. Its maximum exact excess is '+excess['numerator']+'/'+excess['denominator']+'. All1024 complement pairs and their degree-defect identities are checked; the projected degrees are not all exactly1 and matching reciprocity is not exact.',
        'empirical/engineering result',['COMPUTED'],odd['scope'],
        ['Every saved float is interpreted exactly then divided by its exact per-center sum; normalization is part of this diagnostic.',
            'The projection uses the smaller outer endpoint, and both members of every odd-set complement pair are evaluated without numerical tolerance.'],
        [odd['dependency']], 'partial-oddsets',odd,odd['shared_trusted_components'],
        [c['name']+': '+c['outcome'] for c in odd['controls']],odd['limitations'])
    for binding in new16['claim_bindings']:
        require(binding['revision']==1 and binding['recommendation']=='VERIFIED' and binding['indices']==new16['selected_indices'],
            'Independent new16 claim binding differs')
        indices=', '.join(map(str,binding['indices']))
        if binding['id']=='C-RERANK-V3-STAR-16-EXCLUSIONS':
            statement=('For each of the16 labeled whole-family fixedK assignments '+indices+
                ', no srg(99,14,1,2) completes its prescribed present and absent edges: each original-star phase-I lower bound is strictly positive by independent exact arithmetic, using all independently complete original local-star domains.')
            kind='exclusion'
        else:
            require(binding['id']=='C-RERANK-V3-STAR-16-NO-IMPROVEMENT','Unexpected new16 claim ID')
            statement=('For all16 labeled whole-family fixedK assignments '+indices+
                ', the independently exact original-domain STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS lower bound exceeds the incumbent18481 exact upper bound; none improves that same objective.')
            kind='mathematical result'
        claim(binding['id'],statement,kind,['DERIVED','COMPUTED'],binding['scope'],
            ['Fixed labeled assignments, full99 root scaffold and the hash-bound prescribed absent edges.',
                'Original complete star domains, not pair-pruned domains, define the LP; no nontrivial automorphism is assumed.'],
            binding.get('dependencies',[]),'v3-star16',new16,new16['shared_trusted_components'],
            ['Independent raw full99 coefficient and rational interval checks on all16 selected cases;404686 original local choices.',
                'Independent exact certificate replay and full original-domain identity; prior positive/corrupted arithmetic controls are hash-bound.'],
            ['Only these16 fixed configurations are excluded; no exhaustive family or target coverage.',
                'Positive certificates do not identify a graph or a target-wide progress fraction.'])
    bind(__file__);bind('docs/claims.schema.json');bind('acceleration/validate_claims.py');bind('uv.lock')
    ledger=registry.read_ledger(ROOT/'CLAIMS.yaml');merged=merge(ledger,artifacts,claims,now)
    checked=registry.validate(merged,ROOT,load('docs/claims.schema.json'),'none',ledger)
    require(checked['valid'],'Prepared registry patch invalid: '+str(checked['errors']))
    return dict(status='PREPARED_INDEPENDENTLY_REVIEWED_V3_PARTIAL_CLAIM_PATCH',schema_version=1,created_at=now,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable]+sys.argv,
        working_directory=str(ROOT),inputs_sha256=hashes,artifacts=artifacts,claims=claims,ledger_modified=False,
        validated_against_ledger_sha256=digest('CLAIMS.yaml'),validation=checked,
        verification_performed_by_registrar=False,scope='Bookkeeping of five independently reviewed scoped claims only; no target state change')


def merge(ledger,artifacts,claims,now):
    result=deepcopy(ledger);artifact_ids={a['id'] for a in ledger['artifacts']};claim_ids={c['id'] for c in ledger['claims']}
    require(not artifact_ids&{a['id'] for a in artifacts},'Claim patch artifact ID already exists')
    require(not claim_ids&{c['id'] for c in claims},'Claim patch ID already exists')
    result['artifacts'].extend(artifacts);result['claims'].extend(claims);result['updated_at']=now;return result


def main():
    p=argparse.ArgumentParser(description=__doc__);m=p.add_mutually_exclusive_group(required=True)
    m.add_argument('--prepare',action='store_true');m.add_argument('--apply',action='store_true')
    p.add_argument('--patch',required=True);p.add_argument('--expected-ledger-sha256');p.add_argument('--snapshot');p.add_argument('--receipt')
    args=p.parse_args()
    if args.prepare:
        require(not path(args.patch).exists(),'Preserve prepared patch');d=prepare();save(args.patch,d)
        print(json.dumps(dict(status=d['status'],claims=[c['id'] for c in d['claims']],ledger_modified=False,sha256=digest(args.patch))));return
    require(args.expected_ledger_sha256 and args.snapshot and args.receipt,'Explicit current ledger SHA, fresh snapshot and receipt required')
    ledger_path=ROOT/'CLAIMS.yaml';old=ledger_path.read_bytes();require(sha256(old).hexdigest()==args.expected_ledger_sha256,'Concurrent ledger change; review current state')
    require(not path(args.snapshot).exists() and not path(args.receipt).exists(),'Preserve snapshots/receipts')
    d=load(args.patch);require(d['status']=='PREPARED_INDEPENDENTLY_REVIEWED_V3_PARTIAL_CLAIM_PATCH','Wrong patch')
    for name,h in d['inputs_sha256'].items():require(digest(name)==h,'Changed patch evidence: '+name)
    require(d['inputs_sha256'].get(key(__file__))==digest(__file__),'Registrar source changed since preparation')
    previous=registry.read_ledger(ledger_path);now=datetime.now(timezone.utc).isoformat();new=merge(previous,d['artifacts'],d['claims'],now)
    validation=registry.validate(new,ROOT,load('docs/claims.schema.json'),'available',previous)
    require(validation['valid'],'Patch fails validation: '+str(validation['errors']))
    require(ledger_path.read_bytes()==old,'Concurrent ledger write; no modification performed')
    with path(args.snapshot).open('xb') as f:f.write(old)
    ledger_path.write_text(yaml.safe_dump(new,sort_keys=False,width=110),encoding='utf8')
    save(args.receipt,dict(status='INDEPENDENTLY_REVIEWED_V3_PARTIAL_CLAIM_PATCH_APPLIED',created_at=now,
        patch_path=key(args.patch),patch_sha256=digest(args.patch),previous_ledger_sha256=sha256(old).hexdigest(),
        current_ledger_sha256=digest(ledger_path),validation=validation,mathematical_verification_performed=False))
    print(json.dumps(dict(status='CLAIM_PATCH_APPLIED',added_claims=[c['id'] for c in d['claims']],ledger_sha256=digest(ledger_path))))


if __name__=='__main__':main()
