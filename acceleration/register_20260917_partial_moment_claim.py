"""Register the independently reviewed necessary moment encoding only."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import yaml

import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry

ROOT=shared.ROOT
AUDIT='acceleration/results/20260917_independent_review/partial_moments.json'
AUDIT_SHA='1d4d08ecc9e73a00e06d210fa5137e7885e677756dc8f33b016fa3227ddec5e1'
HELPER_SHA='39c5af10d455a8b962daaa35c3160628e486f6ea47ffb4fc576f1d38544f2557'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-ledger-sha256',required=True);p.add_argument('--snapshot',required=True);p.add_argument('--receipt',required=True)
    p.add_argument('--apply',action='store_true',required=True);args=p.parse_args()
    require,digest,path,key=shared.require,shared.digest,shared.path,shared.key
    require(digest(shared.__file__)==HELPER_SHA,'Registry helper changed')
    require(digest(AUDIT)==AUDIT_SHA,'Independent moment review changed');review=shared.load(AUDIT)
    require(review['status']=='INDEPENDENT_PARTIAL_K_FULL_MOMENT_MODEL_PASS' and review['producer_imported'] is False and
        review['claim_id']=='C-PARTIAL-K-FULL-MOMENT-ENCODING' and review['claim_revision']==1 and review['recommendation']=='VERIFIED',
        'Independent claim binding required')
    require(review['shape']==[5310,61450] and review['nonzeros']==4425506 and review['probability_columns']==54478 and
        review['hard_simplex_rows']==84 and review['hard_reciprocity_rows']==1740 and review['soft_moment_equalities']==3486 and
        review['complete_augmented_matrix_and_bounds_checked'] is True,'Recorded exact model differs')
    require(len(review['controls'])==18 and all(c['positive']=='PASS' and c['corrupted_coefficient']=='REJECT' and
        c['corrupted_rhs']=='REJECT' for c in review['controls']),'Independent control coverage differs')
    for name,h in review['inputs_sha256'].items():require(digest(name)==h,'Changed moment evidence: '+name)
    require(not path(args.snapshot).exists() and not path(args.receipt).exists(),'Fresh snapshot and receipt required')
    lp=ROOT/'CLAIMS.yaml';old=lp.read_bytes();require(shared.sha256(old).hexdigest()==args.expected_ledger_sha256,'Concurrent ledger change')
    ledger=registry.read_ledger(lp);now=datetime.now(timezone.utc).isoformat()
    folder='acceleration/results/20260917_partial_matching_moments/'
    evidence={'partial-moment-independent':AUDIT,'partial-moment-manifest':folder+'manifest.json',
        'partial-moment-model':folder+'model.json','partial-moment-integer-csr':folder+'integer_augmented_csr.npz',
        'partial-moment-derivation':folder+'MOMENT_MODEL_DERIVATION.md','partial-moment-numeric-outcome':folder+'numeric_lp.json'}
    artifacts=[dict(id=id,path=name,sha256=digest(name),availability='LOCAL_ONLY',
        retrieval='Workspace relative path; publication must include model and referenced domain artifacts.',
        unavailable_reason='No public retrieval commit is asserted by this new registry entry.') for id,name in evidence.items()]
    hashes={a['id']:a['sha256'] for a in artifacts}
    claim=dict(id=review['claim_id'],revision=1,
        statement=review['statement']+' The checked PARTIAL_K_FULL_CENTER_STAR_MOMENT_PHASE1_V1 augmented integer model has 5,310 rows, 61,450 columns and 4,425,506 nonzeros: 54,478 probability columns, 84 hard simplex rows, 1,740 hard reciprocity rows and 3,486 soft moment equalities.',
        kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description=review['scope'],unrestricted_target=False,target_resolution='NONE'),
        assumptions=['The exact frozen one-freed-coordinate partial configuration and its prescribed absent edges.',
            'Complete local domains from C-PARTIAL-K-ONE-COORDINATE-DOMAINS revision1; no nontrivial automorphism is assumed.'],
        dependencies=[review['dependency']],evidence=list(evidence),verification=[dict(claim_revision=1,verifier='independent_verifier agent',
            method='independent_artifact_check',command_or_audit=AUDIT,timestamp=review['timestamp'],outcome='PASS',scope=review['scope'],
            artifact_hashes=hashes,shared_components=review['shared_trusted_components'],
            controls=['All augmented integer coefficients and bounds reconstructed from complete neighborhoods.',
                '18 positive rooted srg(9,4,1,2) model cases; 18 coefficient corruptions and 18 RHS corruptions rejected.'],
            limitations=review['limitations'])],limitations=review['limitations'],created_at=now,updated_at=now,
        unknowns={'external_source':'Current-project independent encoding review, not a historical import.'},external_source=None,
        reproducibility=dict(manifest='partial-moment-manifest'))
    merged=shared.merge(ledger,artifacts,[claim],now)
    validation=registry.validate(merged,ROOT,shared.load('docs/claims.schema.json'),'available',ledger)
    require(validation['valid'],'Registry validation rejected encoding claim: '+str(validation['errors']))
    require(lp.read_bytes()==old,'Concurrent ledger change; abort before write')
    with path(args.snapshot).open('xb') as f:f.write(old)
    lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf8')
    shared.save(args.receipt,dict(status='INDEPENDENT_PARTIAL_MOMENT_ENCODING_REGISTERED',created_at=now,command=[sys.executable]+sys.argv,
        working_directory=str(ROOT),claim_id=claim['id'],claim_revision=1,independent_review_path=AUDIT,independent_review_sha256=AUDIT_SHA,
        inputs_sha256={key(__file__):digest(__file__),key(shared.__file__):digest(shared.__file__)},
        previous_ledger_sha256=shared.sha256(old).hexdigest(),current_ledger_sha256=digest(lp),validation=validation,
        registrar_performs_mathematical_verification=False,feasibility_claimed=False,exclusion_claimed=False,target_resolution='UNKNOWN'))
    print(json.dumps(dict(status='PARTIAL_MOMENT_ENCODING_REGISTERED',ledger_sha256=digest(lp))))


if __name__=='__main__':main()
