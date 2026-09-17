"""Register the independently derived every-root normalization implication."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]


def main():
    lp=ROOT/'CLAIMS.yaml'; snapshot=ROOT/'acceleration/results/20260917_resume/claims_before_root_scaffold.yaml'
    assert not snapshot.exists()
    ledger=yaml.safe_load(lp.read_bytes())
    rp='acceleration/results/20260917_independent_review/root_scaffold.json'
    review=json.loads((ROOT/rp).read_bytes())
    assert review['status']=='INDEPENDENT_ROOT_SCAFFOLD_DERIVATION_AND_CALIBRATION_PASS'
    for path,h in review['inputs_sha256'].items():assert sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    evidence={'root-scaffold-audit':rp,
        'root-scaffold-derivation':'acceleration/results/20260917_independent_review/ROOT_SCAFFOLD_DERIVATION.md',
        'root-scaffold-manifest':'acceleration/results/20260917_root_scaffold/manifest.json',
        'root-scaffold-calibration':'acceleration/results/20260917_root_scaffold/summary.json'}
    for id,path in evidence.items():ledger['artifacts'].append(dict(id=id,path=path,
        sha256=sha256((ROOT/path).read_bytes()).hexdigest(),availability='LOCAL_ONLY',
        retrieval='Workspace relative path; awaiting publication on draft PR1.',unavailable_reason='New local artifact, not yet published.'))
    hashes={a['id']:a['sha256'] for a in ledger['artifacts']}; now=datetime.now(timezone.utc).isoformat()
    scope='Necessary normalization for every hypothetical target and every root; all orderings and orientations of its seven neighborhood matching edges are allowed. Outer adjacencies remain unrestricted by normalization.'
    assert not any(c['id']==review['claim_id'] for c in ledger['claims'])
    ledger['claims'].append(dict(id=review['claim_id'],revision=1,
        statement='For every symmetric binary zero-diagonal 99x99 matrix A satisfying A^2=12I-A+2J, every chosen root and every ordering/orientation of its seven neighborhood matching edges determine a unique labeling of the 84 outside vertices by the nonmatched root-neighbor pairs, yielding the 189 positive root-scaffold edges; this normalization imposes no outer adjacency or nonadjacency and assumes no nontrivial automorphism.',
        kind='mathematical result',basis=['DERIVED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description=scope,unrestricted_target=True,target_resolution='NONE'),
        assumptions=['Symmetry, binary entries, zero diagonal, order99, and the exact target matrix equation.'],
        dependencies=[],evidence=list(evidence),verification=[dict(claim_revision=1,
            verifier='independent_verifier agent',method='independent_derivation',
            command_or_audit=evidence['root-scaffold-derivation']+' and '+rp,timestamp=review['timestamp'],outcome='PASS',
            scope=scope,artifact_hashes={id:hashes[id] for id in evidence},
            shared_components=['Python standard library for finite calibration','Explicit target equation and root-label convention'],
            controls=['Known rook9 graph: all9 roots and72 labeled maps checked using its own srg(9,4,1,2) equation.',
                '42 corrupted matrix/label controls rejected.'],
            limitations=['The universal implication follows from the written proof, not from finite rook9 calibration.'])],
        limitations=['No target existence or nonexistence conclusion.','No novelty or external peer-review claim.',
            'No outer-edge restrictions used by later computational experiments follow merely from this normalization.'],
        created_at=now,updated_at=now,unknowns={'external_source':'Fresh self-contained audit of a standard normalization; no novelty claim.'},
        external_source=None,reproducibility={'manifest':'root-scaffold-manifest'}))
    snapshot.write_bytes(lp.read_bytes());ledger['updated_at']=now
    lp.write_text(yaml.safe_dump(ledger,sort_keys=False,width=110),encoding='utf-8')


if __name__=='__main__':main()
