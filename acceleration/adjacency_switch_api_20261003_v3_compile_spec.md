# Adjacency switch API harness V3 compiler correction

SOURCE_ONLY preparation by `/root/structural`. No compiler, native API, fixture,
census or scientific invocation is authorized or performed by this correction.
No existing finite gate transfers to these new bytes. ROOT reviews the new source
and the separately prepared Native build wrapper/plan before any ONE build.

The frozen V2 build invocation `172fc4e8e2f441ca8315df7c0d11eb86` compiled the
census binary but its API compiler returned1. The V2 API line171 called the
unqualified local `quoted` helper on mutable `std::string observed`.
Argument-dependent lookup also finds `std::quoted`; its mutable-string overload
is a better match than the local const-reference overload, so the selected
`std::_Quoted_string` cannot be added to the JSON string. This is a C++ overload
failure, not a mathematical failure. All V2 source/build/partial-binary/receipt
bytes are preserved. No API binary or native API execution is inferred.

## Exact new source and complete allowed difference

- `acceleration/probe_20261003_adjacency_ternary_switch_api_v3.cpp`:
  `9008e9f26826e3fa518f3e5c554babeba7d9f2baed49470a6eb4a894c761a6dc`.
- `acceleration/diff_20261003_adjacency_switch_api_v2_v3.txt`:
  `009e4c8d25473f024151d498729e9a30d3407c6fbfd51a25abdfb03a7b74383e`.

The complete physical source change renames the local `quoted` function to
`json_quoted` and every call to that helper. There are eleven changed identifier
occurrences: one definition and ten calls. No fixture, validation order, getter,
transaction, cache, reverse probe, snapshot, deadline, record, JSON byte grammar
or output schema changes. The escaping function body is byte-identical.
The renamed helper has no `std` overload and so avoids this ADL name collision.
The API source retains its V2 kernel include and exact kernel SHA metadata.
Raw logical V1 schemas remain unchanged; physical V3 filename/hash identify
changed execution. Compilation success is still unobserved here.

Unchanged frozen dependencies:

- Pure V2 kernel `adjacency_ternary_switch_kernel_20261003_v2.cpp`:
  `ce35a195796266753cc123064e34a9bf0a9bda1880932576010089031bccba47`.
- V2 census driver `census_20261003_adjacency_ternary_switch_v2.cpp`:
  `5b3c170a817716a4e1e0ceaab90edcaa8a62c7e91c053ea927369a4d748e10fd`.
- V2 API source:
  `0831d566cbd8189ba211b9ae3051ecd5da9530a35b8445f3b582e8d3419a117f`.
- Original unchanged API semantic specification
  `probe_20261003_adjacency_ternary_switch_api_v1_spec.md`:
  `93f742b4757c499a2288c664f387a14c54b9f07165a91899284b86b06638be58`.
- Prior V2 joint compiler specification
  `adjacency_switch_cpp_20261003_v2_compile_spec.md`:
  `ad558d8757464cc0c5b0640b0281496f10ea7e445eb0a6711c9d94decd710d7e`.

## Preserved genuine V2 failure evidence

Under `acceleration/results/20261003_adjacency_switch_native_build02`:

- `api.stderr.log`: `9ee640ad36479d1564bfc5a94440709be77d20d17abb208ef075b441e8663d31`.
- `api.receipt.json`: `bd06da7437e8038fbf26da69c67b7b90dd0dac9c687f36f36fd75a0e47553c1e`.
- `failure.json`: `66d3e3a291db39f1ddaf691b97e606d8bd78130a19a5db45ad1af5edbcc35bfd`.

The receipt records compiler exit1 after0.407127056 seconds, childPID413,
original Linux process group400, euid1000 and reapedtrue. That compiler receipt
itself makes no group-empty claim; the separately preserved containing Native
supervisor terminal supplies its observed bounded cleanup. No Windows Job claim
is made for that Linux process group. The census partial binary remains build
evidence only and was never run by this correction.

All later build/API control receipts and verifiers must pin this new V3 API
source and this specification explicitly. The actual getter interface remains
510 tiny labelled roles, two synthetic99 probes and twelve direct negative
calls; these counts are planned coverage, not results. Authentic API cache,
rollback, rejected-copy and reverse observations require a separately authorized
native fixture command and distinct complete independent replay. No silent
oldgate, automatic retry, ledger/index/Git mutation or target conclusion.

Preparation used text editing and small source/receipt hashes only. An initial
text-edit guard expected ten identifier occurrences and correctly stopped before
writing because there are eleven including the definition; the guard was
corrected after inspection. This was no compiler/native/control invocation.
