# V18 normalized source/AST change proposal, not executed

The complete source is b310e6772f853af3e8faa867c3c60896b27234fe70b3e0c930f5bd46d1123207.
Preserve V17 1ae20114929478bbfbcde7acdc42582453aefe003e76c801bd48353eb2a74e84
and addition text9890ee43b890977480e0e18c658b8969236b51737b2f5d9ff1986d0a3490296c.
No AST comparison, import or execution has occurred.

New top-level nodes only: V18_DESCRIPTOR=dict(literal path/SHA),
V18_EXACT=json.loads(literal eight-ID routing); functions v18_descriptor,
v18_role, v18_report and v18_scope. Main inserts only:
```python
exact_v18 = v18_role(cid, expected, binding)
# One extra Boolean role alternative: or exact_v18
wave43_statement_mapping = v18_report(cid, report_sha, binding, report)
if wave43_statement_mapping is not None:
    need(editorial_statement_mapping is None, 'v18 disjoint exact written metadata adapter')
    editorial_statement_mapping = wave43_statement_mapping
if cid in V18_EXACT:
    original_scope = copy.deepcopy(binding['scope'])
    projected_scope = v18_scope(cid, expected, binding)
    binding = copy.deepcopy(binding)
    binding['scope'] = projected_scope
```

The exact role guard retains producer!=verifier and every inherited alternative.
The new dispatcher follows V17 mapping and precedes inherited checking-identity
validation. The exact scope block follows the unchanged historical normalized
adapter and precedes paths/evidence collection. In-memory binding is copied;
raw binding/report files remain unchanged. Every original statement is explicitly
equal before inherited statement dispatch can be bypassed by the metadata
mapping. Full raw scope and absent original report fields are persisted.

Remove these exact six top-level nodes and five main AST insertion groups,
then require complete ast.dump(include_attributes=False) equality with V17.
The helper checks exact removal shape/name/number and fails on any other edit.
Ordinary routes, mathematical-proof checking, ledger/schema/atomic-write logic,
prior adapters, role exceptions and evidence collection are not rewritten.
This is a proposed future acceptance criterion, not an executed equivalence
claim. Author review and future own controls cannot independently approve V18.

