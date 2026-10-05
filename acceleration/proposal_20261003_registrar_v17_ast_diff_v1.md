# V17 normalized AST change proposal (not executed)

This source-only record accompanies the complete V17 source1ae20114929478bbfbcde7acdc42582453aefe003e76c801bd48353eb2a74e84
and preserved V16a8e7c2694817970df28ff1ec7be3d8265ba2f6e3ffe3d88798241832426c2026.
No AST restoration test, helper invocation, main-copy projection or registration
has run. The following exact subtraction is the proposed future acceptance
criterion, implemented by the new author helper and requiring separate ROOT
engineering review. Whitespace and source line-ending normalization do not
stand in for executable equivalence.

New normalized top-level node names only:

```text
Assign V17_DESCRIPTOR = dict(path=<literal>, sha256=<literal>)
Assign V17_EXACT = json.loads(<literal three-binding JSON>)
FunctionDef v17_descriptor(cid)
FunctionDef v17_role(cid, expected, binding)
FunctionDef v17_fixed_evidence(cid, record, binding, report)
FunctionDef v17_report(cid, report_sha, binding, report)
```

Their complete source is preserved in the new full registrar and the separate
addition text eef8055a75ba9dc017c37dcc1946280f0b618596bc93ec061d2a1d92dcfd2de3.
They reference only the pinned descriptor0a0717 and three exact frozen bindings,
reports and evidence. All inherited imports, constants and helpers remain.

Four main edits only:

```python
# 1. Insert after inherited exact_v16 role call.
exact_v17 = v17_role(cid, expected, binding)

# 2. Append one name to the inherited role OR; producer!=verifier is preserved.
# Old ending: ... or exact_v15 or exact_v16
# New ending: ... or exact_v15 or exact_v16 or exact_v17

# 3. Insert the exact report call before inherited report checking identity.
wave42_statement_mapping = v17_report(cid, report_sha, binding, report)

# 4. Insert its disjoint dispatcher immediately after the report call.
if wave42_statement_mapping is not None:
    need(editorial_statement_mapping is None, 'v17 disjoint exact metadata adapter')
    editorial_statement_mapping = wave42_statement_mapping
```

Remove exactly these six top-level nodes and four main edits, then compare
`ast.dump(..., include_attributes=False)` for the entire module against V16.
Require every removed name/node/guard shape exactly; reject missing, duplicate
or additional edits. No mathematics or source equivalence result is claimed by
this proposal. New helpers authenticate complete recursively typed original
metadata, exact absent headlines and output-provenance boundaries. Old adapters,
ordinary literal statements and atomic/schema paths are not rewritten.

The new role set contains only rank98, all99roots and energy. Ordinary cf807
stays outside the set. A future protected-copy358->362 test must explicitly
select those three plus the ordinary exactness binding, retain all358 prior
claim/artifact/target records and record the two null-headline mappings only.
That future test is distinct from the author helper's10/170 controls.

Disclosure: Checkpoint authored this registrar proposal, V16, the all-root
diagnostic producer and Wave41 generator. ROOT independently performed the
recorded mathematical checks. Checkpoint's source/author-control work cannot
supply independent engineering approval, mathematical reapproval or target
resolution. Current publication context is ROOT-supplied HEAD63437 and ledger10b;
fresh protected observations and exact input hashes belong to a later command.
