# V16 independent engineering checker V2: prelaunch static veto

Reviewer /root/checkpoint_audit, author of the registrar subject. This is
engineering source review only, not independent approval of that registrar.
Entire checker and specification read. Checker SHA256
7906ec2afc994cd631fdba1d6414495bfa5d1e4c19e5192709d8c23a6f9210ff;
spec d14c5b7befc3ba9eedca68daa083b037bf0430e0675d403a53725cc1cdbbaec5.
No checker/control/main invocation was performed by this review. Live ledger
and index were not modified; the V16 author's prior helper run is separate.

Static veto before execution: CONFIG_BOUND_TO_RAW builds the comparison with
`{k:b[k] for k in cfg['binding_metadata']}`. The exact C4 binding6525 omits
exact_certificate. V16 source preparation deliberately obtains nullable
metadata through binding.get, so its config contains exact_certificate:null.
The new engineering checker therefore indexes an absent key and raises KeyError
before its protected main copies. Raw property-name inspection confirmed the
absence; no subject/checker function was called to demonstrate it.

Preserve V2 source/spec and use a NEW version. Admit the absence only for this
explicitly declared optional projection, or compare a precise presence map
separately. Required metadata must remain required; the entire original
binding remains hash-bound and subject whole-value equality remains mandatory.
This is metadata interoperability, not mathematical falsification.

The final limitation also describes the ordinary comparison as a ROOT-verifier
report. V2 actually derives that synthetic ordinary copy from e816 N5, whose
verifier is /root/checkpoint_audit. Correct that factual description in the new
version while preserving the old source. No ordinary synthetic claim belongs
in the live ledger or constitutes a theorem check.

No further static gap was found in this reading of exact AST restoration,
the17 own veto paths, report/closure authentication, dependency ordering,
timestamp-limited ordinary comparison, and three final os.replace barriers.
The barrier intercepts the live replacement and preserves actual YAML/index;
whole prior claims/artifacts/target, new literal scopes/dependencies and original
raw headline/combined-method mappings are checked. These observations do not
approve execution, finite control outcomes or mathematics. ROOT must separately
review and execute the changed checker under the supported declared deadline,
preserve any failure, and commission an actual transition audit after eventual
registration. No target-resolution claim follows from bookkeeping.
