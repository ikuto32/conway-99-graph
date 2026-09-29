# Editorial assumption impact review

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
