# Independent audit: side69 + E0<=73 CNF

Status: **AUDIT_PASS** (`errors = 0`).

- The input header is `818313 / 1624518`; the output header is
  `822182 / 1632236`.
- The complete 30,220,834-byte input CNF body is a byte-identical prefix of
  the output body.  Only the DIMACS header and the appended cardinality
  suffix differ.
- An independent lexicographic reconstruction of the 84 outer labels gives
  21 four-vertex fibres.  Each fibre has four square-side variables and two
  diagonal variables, hence `84 + 42 = 126` E0 variables.  The reconstructed
  side, diagonal, and combined sorted lists exactly match both build metadata
  files.
- Fresh `CardEnc.atmost(..., bound=73, encoding=seqcounter)` reconstruction
  adds 3,869 variables and 7,718 clauses.  Its 153,431-byte DIMACS suffix is
  byte-identical to the actual suffix (SHA-256
  `84C966E05E559526BEDDD62CF9EC2AB696AB25A2D20B37D451482CC441DE3C97`).
- The completed CNF SHA-256 is
  `7FAB56D135701EB8CAE8F7179E337B85E0EC679E571F5BA6D186E93CD50E7923`,
  exactly as recorded in the build metadata.
- The SAT path extracts the graph-edge variables, invokes the direct verifier,
  checks all 99 degrees and all vertex pairs, and rejects a failed check before
  writing a solution artifact.
- This audit did not run or rely on a SAT solver.  An UNSAT answer for this
  search-strengthened CNF is not a formal nonexistence proof: the inherited
  computational E0 exclusions have no DRAT/LRAT certificates.  A SAT answer
  remains acceptable only after the direct 99-vertex verification succeeds.

Full details, including the 21-fibre crosswalk, are in
`scratch_e74_independent_side69_e0le73_audit.json`.
