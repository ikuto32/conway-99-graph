"""Hash-bound editorial impact review; never modifies the authoritative ledger."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import yaml

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_independent_review/automorphism_assumption_editorial'
REPLACEMENTS={
    'No nontrivial target automorphism.':'No nontrivial target automorphism is assumed.',
    'No automorphism of a hypothetical target and no universal rook-containment assumption.':
        'No nontrivial automorphism of a hypothetical target is assumed, and no universal rook-containment assumption is made.'}

# These judgments were formed by reading each original bound audit and its
# stated mathematical mechanism, not by searching only for symmetry keywords.
REASONS={
 'C-TARGET-GRAM-BOOLEAN-BOX-NOGOODS':'The original audit explicitly lists the target matrix identity, a principal fixed/free edge specification and exact Boolean maximization as its hypotheses. The written affine maximum argument quantifies over every Boolean completion and uses no graph automorphism or rook containment premise.',
 'C-ROOK-FOUR-FACTOR-INITIAL-GRAM-BOX-NOGOOD':'The original binding requires exactly the fixed principal scaffold and preservation of that scaffold by an extension. Its strict negative Boolean maximum applies to all completions of the declared fixed values; neither symmetry nor asymmetry is required.',
 'C-ROOK-FOUR-FACTOR-BOX-CUT-COLLECTION01':'The original collection audit authenticates each source clause and its exact Boolean-box bound in the same fixed scaffold. Taking their conjunction requires no target automorphism and asserts no universal occurrence of that scaffold.',
 'C-ROOK-FOUR-FACTOR-BOX-CUT-COLLECTION02':'The original collection audit authenticates each source clause and its exact Boolean-box bound in the same fixed scaffold. Taking their conjunction requires no target automorphism and asserts no universal occurrence of that scaffold.',
 'C-ROOK-GRAM-BOX-WAVE02':'This is a finite artifact/execution claim: saved solver outcomes, checked local assignment, checked negative direction and source clauses. Its scope is the recorded fixed family. An assumption about the automorphism group of a hypothetical target cannot enter those recorded artifact facts.',
 'C-FIXED-SCAFFOLD-RELABELING-CUT-TRANSPORT':'The original proof explicitly defines B[i,j]=A[p(i),p(j)] for arbitrary target A and never asserts A=B. It expressly states that no step requires an automorphism of a hypothetical target. A specification-preserving relabeling is not asserted to preserve an unknown target adjacency.',
 'C-ROOK-FOUR-FACTOR-SCAFFOLD-RELABELINGS32':'The audit compares complete fixed/free specifications, edge-variable images and degree rows for supplied permutations. Its limitations expressly say no nontrivial automorphism of any hypothetical target is assumed or deduced; the maps act on the family of completions.',
 'C-ROOK-DEGREE-BLOCK-GRAM-UPPER-BOUND':'The independently written proof partitions the780 variables and160 degree equations and maximizes an affine Gram quadratic over their Cartesian degree relaxation. It explicitly states that neither an automorphism nor universal rook containment is assumed.',
 'C-ROOK-DEGREE-BLOCK-GRAM-CUT-12':'The original binding assumes only the target identity and induction of this particular fixed scaffold. The checked strict negative degree-relaxation maximum holds for all assignments in its declared scope, regardless of any automorphism group.',
 'C-ROOK-GRAM-CUT-ORBITS-352':'The original audit proves forward signed clause transport on an arbitrary target extension via a different relabeled adjacency B and expressly states that A=B is not asserted. Its fixed-scaffold and source-clause premises impose no target symmetry or asymmetry.',
 'C-INDEPENDENT-SET-MATCHING-CAP-COMPOSITION':'The universal proof expands (A+M)^2 and handles all pair cases using only matching endpoints and independence. It applies to arbitrary finite simple graphs satisfying those explicit hypotheses, with no target or rook graph premise.',
 'C-CLOSED-TWO-NEIGHBORHOOD-GRAM-REDUNDANCY':'The original sum-of-squares proof uses the two center neighborhood equalities, kernels and residual degree at most3. Its statement quantifies over every finite simple graph satisfying those local hypotheses; no symmetry or rook condition enters.',
 'C-CLOSED-TWO-NEIGHBORHOOD-LOWER-GRAM-REDUNDANCY':'The original written Schur-complement proof uses exact center equalities, residual degree bounds and integer/rational matrix identities. Its universal conditional statement and rank/kernel calculation require no automorphism or universal rook containment.',
 'C-CLOSED29-TWO-SPECIFIC-GRAM-OBSTRUCTIONS':'The bound audit checks strict negative integer principal Gram directions for two exact raw29 matrices. Principal positive semidefiniteness follows from the target identity for every target, regardless of symmetry; no larger family or universal containment is asserted.',
 'C-PARTIAL-K-EIGHT-COORDINATE-FULL99-SAT-ENCODING':'The original complete encoding audit quantifies over every adjacency satisfying the recorded fixed present/absent entries. The proof uses99 degree equations, all4851 pair caps, a global equality-of-sums argument and exact Boolean gates. It has no asymmetry condition or target automorphism requirement.',
 'C-ROOK-ORBIT-AUGMENTED-LOCAL59-WITNESS':'The original SAT replay checks all3690172 clauses, the complete assignment and its raw59 graph under the fixed model. Its scope explicitly says no nontrivial automorphism is assumed. Existence of this local assignment makes no claim about any target automorphism group.',
 'C-ROOK-ORBIT-LOCAL59-GRAM-BOX-CUT43':'The original independent audit constructs the exact maximizing Boolean corner for all780 edge variables and proves its quadratic negative. The rule applies to every target extension of the fixed scaffold and uses no symmetry or asymmetry restriction.'}


def need(test,message):
    if not test: raise ValueError(message)


def digest_bytes(raw): return hashlib.sha256(raw).hexdigest()


def digest(path): return digest_bytes(Path(path).read_bytes())


def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()


class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader,node,deep=False):
    loader.flatten_mapping(node);out={}
    for k,v in node.value:
        name=loader.construct_object(k,deep=deep)
        need(name not in out,'duplicate YAML key: '+str(name))
        out[name]=loader.construct_object(v,deep=deep)
    return out


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)


def main():
    ledger_path=ROOT/'CLAIMS.yaml';before=ledger_path.read_bytes()
    ledger=yaml.load(before,Loader=UniqueLoader)
    artifacts={row['id']:row for row in ledger['artifacts']}
    need(len(artifacts)==len(ledger['artifacts']),'unique artifact IDs')
    selected=[c for c in ledger['claims'] if set(c.get('assumptions',[]))&set(REPLACEMENTS)]
    need({c['id'] for c in selected}==set(REASONS),'reviewed exact17claim inventory')
    need(len(selected)==17 and len({c['id'] for c in selected})==17,'exact affected claim population')
    bindings={};records=[]
    def pin(path,expected=None):
        path=Path(path)
        if not path.is_absolute():path=ROOT/path
        actual=digest(path);need(expected is None or expected==actual,'artifact identity '+str(path))
        bindings[key(path)]=actual;return path
    for claim in selected:
        need(claim['status']=='VERIFIED' and claim['review_state']=='CLEAR','current reviewed state')
        verifications=[]
        for verification in claim['verification']:
            need(verification['claim_revision']==claim['revision'] and verification['outcome']=='PASS','existing exact revision check')
            path=ROOT/verification['command_or_audit']
            matching=[(aid,sha) for aid,sha in verification['artifact_hashes'].items() if artifacts[aid]['path']==key(path)]
            need(len(matching)==1,'unique immutable audit binding')
            aid,expected=matching[0];audit=json.loads(pin(path,expected).read_bytes())
            need('PASS' in audit['status'],'original audit successful exact scope')
            # Audit evidence identities are checked, while expensive mathematical
            # computations remain the preserved prior verifications.
            for evidence_id,sha in verification['artifact_hashes'].items():
                evidence=artifacts[evidence_id]
                need(evidence['sha256']==sha,'ledger verification/artifact hash agreement')
                pin(evidence['path'],sha)
            quoted={k:audit[k] for k in ('statement','scope','assumptions','derivation','written_derivation','mathematical_derivation','proof','written_audit') if k in audit}
            for field in ('written_audit','proof'):
                value=audit.get(field)
                if isinstance(value,str) and len(value)<240 and (ROOT/value).is_file():
                    pin(ROOT/value)
            verifications.append(dict(audit_path=key(path),audit_sha256=expected,original_status=audit['status'],original_verification=verification,
                                      actual_hypotheses_and_argument=quoted))
        old=claim['assumptions'];new=[REPLACEMENTS.get(x,x) for x in old]
        need(sum(a!=b for a,b in zip(old,new))==1,'one exact assumption edit per claim')
        records.append(dict(claim_id=claim['id'],reviewed_revision=claim['revision'],
            reviewed_claim_sha256=digest_bytes(json.dumps(claim,sort_keys=True,separators=(',',':')).encode()),
            statement=claim['statement'],scope=claim['scope'],original_assumptions=old,recommended_assumptions=new,
            dependencies=claim['dependencies'],independent_editorial_reason=REASONS[claim['id']],
            bound_original_verifications=verifications,
            finding='The bound original verification establishes its stated scope without any target symmetry or asymmetry premise.',
            retain_prior_verification_for_exact_editorial_change=True,
            permitted_change='Only the indicated assumption wording; statement, mathematical scope, artifacts and hypotheses remain fixed.'))
    # Guard the transformation itself: a missing phrase is not silently guessed;
    # counts and every other byte survive the authorized literal replacements.
    expected_counts={old:before.decode('utf-8').count(old) for old in REPLACEMENTS}
    need(list(expected_counts.values())==[3,14],'three short and fourteen long exact occurrences')
    proposed=before
    for old,new in REPLACEMENTS.items(): proposed=proposed.replace(old.encode(),new.encode())
    roundtrip=proposed
    for old,new in REPLACEMENTS.items(): roundtrip=roundtrip.replace(new.encode(),old.encode())
    # Existing fully-spelled wording could predate the edit, so assess parsed
    # claims instead of relying on a globally reversible text replacement.
    parsed_after=yaml.load(proposed,Loader=UniqueLoader)
    for old,new in zip(ledger['claims'],parsed_after['claims']):
        altered=dict(old)
        altered['assumptions']=[REPLACEMENTS.get(x,x) for x in old.get('assumptions',[])]
        need(altered==new,'no unrelated field changed in candidate editorial patch')
    need(ledger_path.read_bytes()==before,'ledger stable throughout review')
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/'CLAIMS.reviewed.yaml').write_bytes(before)
    for path in (Path(__file__),ROOT/'uv.lock',ROOT/'docs/DERIVATION_20260930_TARGET_GRAM_BOX_NOGOODS.md',
                 ROOT/'docs/DERIVATION_20260930_SCAFFOLD_CUT_TRANSPORT.md',ROOT/'acceleration/audit_20260930_degree_block_gram.md'):
        pin(path)
    report=dict(status='INDEPENDENT_AUTOMORPHISM_ASSUMPTION_EDITORIAL_IMPACT_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),yaml_version=yaml.__version__,
        verifier='/root/state_literature_audit independent editorial impact reviewer',
        verification_type='Exact claim-by-claim comparison with pinned original audit hypotheses and proof mechanisms; no mathematical experiment replay',
        reviewed_ledger_sha256=digest_bytes(before),reviewed_ledger_snapshot=key(OUT/'CLAIMS.reviewed.yaml'),
        reviewed_total_claims=len(ledger['claims']),affected_claims=len(records),phrase_occurrences=expected_counts,
        approved_replacements=REPLACEMENTS,records=records,inputs_sha256=bindings,
        authorization='The exact replacements are supported as editorial clarifications by the original independently checked statements. They do not remove any mathematical premise used in those audits, add a symmetry premise, or assume targets are asymmetric.',
        impact='Original verification records may be retained for these exact corrected statements after attaching this review. A new ledger revision, if created, must be explicitly bound to this editorial review and the preserved original revision/evidence; dependency-revision bookkeeping must remain explicit.',
        rejected_interpretation='Neither ambiguous phrase may be interpreted as asserting that a hypothetical target has trivial automorphism group or lacks nontrivial automorphisms.',
        no_universal_rook_containment='The longer replacement also preserves that a fixed rook scaffold is conditional, never assumed to occur in every target.',
        limitations=['Only these17exact current claim revisions were reviewed.','No producer or audit artifact was rewritten, and no expensive experiment or proof was rerun.','Any broader statement, changed artifact, changed mathematical hypothesis or changed dependency requires a new impact review.','This is an editorial evidence review, not a new resolution or fresh validation of every underlying computation.'],
        ledger_modified=False,solver_launched=False,mathematical_claim_changed=False,target_resolution=False,external_review=False)
    with (OUT/'summary.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    note='''# Editorial assumption impact review

The17 listed claims have ambiguous registry wording: three say `No nontrivial
target automorphism.` and fourteen say `No automorphism of a hypothetical
target and no universal rook-containment assumption.` Neither may be read as
an assumption that a hypothetical target is asymmetric. The original bound
audits establish their exact statements without that premise.

The JSON review identifies every claim/revision, quotes its original audit
hypotheses or proof, gives a separate reason for retaining the prior scope, and
checks the recorded artifact hashes. The archived `CLAIMS.reviewed.yaml` is
only an immutable review input; root `CLAIMS.yaml` remains authoritative.

Approved replacements are the explicit wording in `approved_replacements`.
They clarify that no nontrivial target automorphism is assumed, while keeping
fixed-scaffold conditions and the absence of universal rook containment
unchanged. The reviewer did not modify the ledger. Original mathematical
checks are preserved; this is not a rerun or a new mathematical promotion.

If root assigns new revisions for the editorial changes, bind those revisions
to this review and the preserved prior evidence, and review dependency revision
references explicitly. Other changes are outside this approval.
'''
    (OUT/'review.md').write_text(note,encoding='utf-8')
    print(json.dumps(dict(status=report['status'],affected_claims=len(records),reviewed_ledger_sha256=digest_bytes(before),summary_sha256=digest(OUT/'summary.json'))))


if __name__=='__main__':main()
