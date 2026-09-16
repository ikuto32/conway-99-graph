# Exact Rust star domains

`star_domains.rs` enumerates every legal choice of eight disjoint-support
neighbors for each of the 84 outer vertices. It enforces root-label equations,
all resource capacities induced by partial pair caps, and conflicts between
chosen neighbors. A domain is represented by a sorted list of hexadecimal
84-bit masks. Necessary reciprocal-edge constraints then remove unsupported
domain values until an empty domain appears or arc consistency is reached.

```powershell
rustc -O -C target-cpu=native acceleration/star_domains.rs -o acceleration/build/star_domains.exe
acceleration/build/star_domains.exe INPUT.txt OUTPUT.json 30 2000000 20000
```

Input is the existing `C99OVERLAPS1` text format, with exactly one complete
overlap assignment. The optional limits are seconds, total recursive nodes
over all 84 vertices, and domain values per vertex. Output includes the complete
domain lists, per-vertex node counts and a deterministic reciprocity deletion
trace. Output files must be new. Invalid partial graphs are rejected before
enumeration.

If any enumeration limit is reached, the entire candidate is `INCOMPLETE` and
no propagation is emitted. A capped domain must never be used to exclude a
candidate. If a complete domain is initially empty, the Rust implementation
returns immediately with zero propagation events. Nonempty arc consistency
would still not certify a mutually consistent graph.

`star_domains_batch.rs` is a separately named derivative and records the frozen
single-candidate source SHA256 in its header. The original remains unchanged.

```powershell
rustc -O -C target-cpu=native acceleration/star_domains_batch.rs -o acceleration/build/star_domains_batch.exe
acceleration/build/star_domains_batch.exe INPUT.txt OUTPUT.json 30 2000000 20000
```

Batch input accepts a positive candidate count. The output `results` list has
the same full payloads as the single-candidate executable, in input order.
All three caps reset independently for each candidate. Each candidate's kernel
timing excludes file parsing and JSON formatting; the outer batch timing also
includes formatting and excludes parsing/file writing.

Controls are saved under `results/20260916_rust_star_domains/`:

- Wide snapshot 15: all 84 domain sets, recursive node counts and the complete
  reciprocal deletion trace match Python exactly; Rust took 0.00291 seconds
  versus 0.251 seconds for Python on this run.
- Wide snapshot 36: every domain set and node count matches Python; two local
  domains are initially empty. Rust took 0.00219 seconds versus 0.214 seconds.
- An independent full-graph ordered-subset enumerator checked 402,282 and
  344,628 search nodes respectively, established complete domain equality and
  replayed every reciprocal deletion.
- Node, time and domain cap controls are independently classified as
  `INCOMPLETE_PRODUCER_NO_EXCLUSION`.
- A batch ordered `[15,36,15]` exactly matches the single payloads except
  timings. With a 23,000-node limit its completion flags are
  `[false,true,false]`, proving that one capped candidate does not consume
  another candidate's budget.

The durable summaries `qa.json` and `batch_qa.json` bind source, native output,
candidate and comparison artifacts by SHA256. These are finite correctness
controls for a necessary-condition filter; they do not solve Conway's problem.
