# V16 engineering V4: corrected source-only review

Reviewer `/root/checkpoint_audit` authored the registrar subject. This review
does not independently approve that subject or execute its checker. Preserve
the earlier V2 and V3 reviews, including V3 review
5815b21d1b4cddc768ead69155bc3783c5a8d23af0417d8416a424041826590f.

The V3 review missed a second absent optional metadata key. ROOT's actual V3
invocation 55ba4723dfc74303a630b61346cdc783 stopped with
`KeyError('original_independent_report_statement_field')` after seven C4
negative controls, before any copied main invocation or live write. The failure
7c0934b625c1d262d34da2da45894a694fbf8870c65189ff282424571ac80e23
and empty-Job terminal
dff80be58d0b0f6a628b49bfb634d4552f22a3c1a68bfc95196a7f44710c0c48
remain evidence. This is an engineering failure, not a mathematical refutation.

Read the complete V4-versus-V3 source diff, complete V4 specification and whole
plan ca9b7acfdf6f825b4845cfe2f17e72a3baa6a3163981f228d8ac59759d52eef7.
V4 source ba6b2a0488dbea628a81562d31396e9d4b838cc3614ea0ef94aabbb830e589a8;
specification 5cf9140dbdcc4ae26e9c0d7523742d02ad447569dd79eb02fd74c54925656337.
Its only source change expands the exact nullable projection set from
`exact_certificate` to that key and
`original_independent_report_statement_field`. It does not relax any other
required key, binding hash, whole original-binding equality or report equality.

Separately parsed the subject's literal V16 metadata configuration from source
text and the two raw JSON bindings, without importing or executing the subject.
Compared the complete configured binding, report and calibration key sets.
The C4 binding 6525dae3734dc6c2f7eabcbd12db994f8c283019176388bb0f540690859225ee
omits only `exact_certificate`. The rank87 binding
dc079188f50e43ac31c9b9707e94a5f6db1fe9644c9b3dbccca4c9e02591a39d
omits only `original_independent_report_statement_field`. Neither original
report nor calibration is missing a configured required key. The nullable
projection therefore matches these exact bytes; it is not a general waiver.

The plan retains supervisor-before-locked-uv execution, 180 seconds outer,
150 worker, 20 shutdown and 20 internal preservation reserve, with fresh output
directories ending in `engineering02` and `supervision02`. It preserves a4f2
ledger and 8bcd index observations and all immutable subject, helper, binding and
runtime pins. The whole protected-copy, AST and typed metadata paths were read
in V2; the V3 and V4 deltas do not alter those paths. No further static veto was
found in this review. Actual finite checks and ROOT's independent interpretation
remain necessary; this document asserts no engineering gate, theorem, target
resolution or availability promotion.
