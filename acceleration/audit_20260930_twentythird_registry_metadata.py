"""Independent frozen-cohort registry metadata checks, no execution on import."""
from collections import Counter
from pathlib import Path
import hashlib,json,subprocess
from audit_20260930_sixteenth_checkpoint import read_ledger,require

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
REGISTRARS=['base_results','fiftyfour_proofs','seven_and_coordinates','six_union','seven_normalization']
NEW_IDS=['C-FIXED-HADAMARD-'+suffix for suffix in [
 'SIX-EXCEPTION-PROFILE0000-GRAM-ENCODING',
 'SIX-EXCEPTION-PROFILE0000-EXCLUSION',
 'FIFTYFOUR-SIX-EXCEPTION-GRAM-ENCODINGS',
 'ALL-TRIPLE-DESCENT-SAVED-OUTCOME',
 'EIGHT-EXCEPTION-KERNEL-CENSUS',
 'SEVEN-EXCEPTION-LOCAL-DOMAIN-FILTER',
 'FIFTYFOUR-SIX-EXCEPTION-PROFILE-EXCLUSIONS',
 'SEVEN-EXCEPTION-PAIRWISE-PROFILE-SCREEN',
 'COMPLETE-COORDINATE-MARGINAL-DOMAINS',
 'EXACTLY-SIX-UNBALANCED-GROUPS-EXCLUSION',
 'AT-MOST-SIX-UNBALANCED-GROUPS-EXCLUSION',
 'SEVEN-EXCEPTION-FIBRE-NORMALIZATION',
 'FIFTYFOUR-PROOF-TRANSPORT']]

def audit_chain(load,pin,expected_ledger_sha256):
    additions=[];chain=[];last=None
    for name in REGISTRARS:
        folder=B+'twentythird_'+name+'_registration/';receipt=load(folder+'summary.json')
        before=folder+'CLAIMS.before.yaml';after=folder+'CLAIMS.after.yaml'
        pin(before,receipt['previous_ledger_sha256']);pin(after,receipt['ledger_sha256'])
        old,new=read_ledger(ROOT/before),read_ledger(ROOT/after)
        if last is not None:require((ROOT/before).read_bytes()==last,'contiguous registrar snapshots')
        else:
            prior_path=B+'resume/claims_at_twentysecond_milestone.yaml'
            publication=load(B+'resume/twentysecond_publication_pointer_receipt.json')
            pin(prior_path,publication['previous_ledger_sha256']);prior=read_ledger(ROOT/prior_path)
            require(len(prior['claims'])==len(old['claims'])==216 and prior['claims']==old['claims'],'unchanged published claim population')
            require(receipt['previous_ledger_sha256']==publication['ledger_sha256'],'actual public ledger boundary')
            require(all(prior[k]==old[k] for k in prior if k not in ['updated_at','artifacts']),'only publication metadata changed')
            pa,pb={r['id']:r for r in prior['artifacts']},{r['id']:r for r in old['artifacts']}
            require(set(pa)==set(pb),'same historical artifacts')
            changed={k for k in pa if pa[k]!=pb[k]};promoted=set(publication['new_public_artifact_ids'])
            require(changed==promoted,'exact recorded availability updates')
            for aid in changed:
                require(all(pa[aid].get(k)==pb[aid].get(k) for k in set(pa[aid])|set(pb[aid]) if k not in ['availability','retrieval','unavailable_reason']),'unchanged historical artifact identity')
                require(pa[aid]['availability']=='LOCAL_ONLY' and pb[aid]['availability']=='PUBLIC' and publication['published_commit'] in pb[aid]['retrieval'],'observed public transition')
            require(publication['mathematical_claim_changes']==[] and publication['published_commit']==publication['confirmed_remote_ref'],'publication is not mathematics')
        oc,nc={r['id']:r for r in old['claims']},{r['id']:r for r in new['claims']}
        oa,na={r['id']:r for r in old['artifacts']},{r['id']:r for r in new['artifacts']}
        require(all(nc[k]==v for k,v in oc.items()),'previous claims unchanged')
        require(all(na[k]==v for k,v in oa.items()),'previous artifact records unchanged')
        added=[c['id'] for c in new['claims'] if c['id'] not in oc]
        require(added==receipt['new_claim_ids'] and receipt['registrar_performs_mathematical_verification'] is False and receipt['validation']['valid'] and not receipt['validation']['errors'],'exact schema-validated additions')
        for p,h in receipt['checked_input_bindings'].items():pin(p,h)
        additions.extend(added);last=(ROOT/after).read_bytes();chain.append(dict(name=name,before=receipt['previous_ledger_sha256'],after=receipt['ledger_sha256'],added=added))
    require(additions==NEW_IDS and hashlib.sha256(last).hexdigest()==expected_ledger_sha256,'exact thirteen-claim cutoff')
    require(len(new['claims'])==229 and dict(Counter(c['status'] for c in new['claims']))==dict(VERIFIED=226,CANDIDATE=2,REFUTED=1),'exact final status population')
    claims={c['id']:c for c in new['claims']};artifacts={a['id']:a for a in new['artifacts']}
    for cid in NEW_IDS:
        c=claims[cid]
        require(c['revision']==1 and c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['scope']['target_resolution']=='NONE' and c['scope']['unrestricted_target'] is False,'exact scoped new revision')
        for dependency in c['dependencies']:require(claims[dependency['id']]['revision']==dependency['revision'],'pinned dependency revision')
        for aid in c['evidence']:pin(artifacts[aid]['path'],artifacts[aid]['sha256'])
        for verification in c['verification']:
            require(verification['claim_revision']==1 and verification['outcome']=='PASS','revision-specific checked outcome')
            for aid,h in verification['artifact_hashes'].items():require(artifacts[aid]['sha256']==h,'verification artifact identity')
    return dict(ledger=new,chain=chain,claims=claims,artifacts=artifacts,ledger_bytes=last)
