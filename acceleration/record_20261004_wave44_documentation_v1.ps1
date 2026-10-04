$ErrorActionPreference = 'Stop'
function Hash([string]$p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLowerInvariant() }
function Json([string]$p) { Get-Content -LiteralPath $p -Raw | ConvertFrom-Json -AsHashtable -DateKind String }
function SaveJson([string]$p, $value) {
    if (Test-Path -LiteralPath $p) { throw ('Preserve existing output: ' + $p) }
    [IO.File]::WriteAllText((Join-Path (Get-Location) $p), ($value | ConvertTo-Json -Depth 45), [Text.UTF8Encoding]::new($false))
}
$ledgerHash = Hash 'CLAIMS.yaml'
if ($ledgerHash -ne '29b72ee4cd843a56cfd75ab08c6794cac74b497fa0c19bc95506a081c7f2700a') { throw 'Ledger changed; prepare a new cutoff' }
$inputs = [ordered]@{
    'acceleration/results/20261004_registered_eleven_projection01/summary.json' = 'ee'
    'acceleration/results/20261004_registered_eleven_projection_root_actual_acceptance01.json' = '0e27c79773e938438f45145af34adc2721d4257f5b99a8d12c22c7776dc77f6f'
    'acceleration/proposal_20261003_wave44_claim_registry_descriptors_v3.json' = 'da5e279d4e6157d69c73f325d91b73f084cde7761f070956e11f8bd28421f6da'
}
# The exact comparison report is bound by the accepted receipt, rather than an invented hash.
$accept = Json 'acceleration/results/20261004_registered_eleven_projection_root_actual_acceptance01.json'
$inputs['acceleration/results/20261004_registered_eleven_projection01/summary.json'] = $accept.actual_endpoints_sha256['acceleration/results/20261004_registered_eleven_projection01/summary.json']
foreach ($kv in $inputs.GetEnumerator()) { if ((Hash $kv.Key) -ne $kv.Value) { throw ('Input changed: ' + $kv.Key) } }
$r = Json 'acceleration/results/20261004_registered_eleven_projection01/summary.json'
$d = Json 'acceleration/proposal_20261003_wave44_claim_registry_descriptors_v3.json'
if ($r.status -ne 'EXACT_REGISTERED_ELEVEN_MATCHES_INDEPENDENT_COPY' -or $r.claim_records -ne 400 -or
    $r.status_counts.VERIFIED -ne 392 -or $r.status_counts.CANDIDATE -ne 3 -or $r.status_counts.REFUTED -ne 5 -or
    $r.review_state_counts.CLEAR -ne 400 -or $d.records.Count -ne 11) { throw 'Cutoff report mismatch' }
$out = 'acceleration/results/20261004_wave44_documentation01'
if (Test-Path -LiteralPath $out) { throw 'Preserve prior documentation output' }
$null = New-Item -ItemType Directory -Path $out
$asof = [DateTimeOffset]::UtcNow.ToString('o')
$head = git rev-parse HEAD
$processes = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python[0-9.]*|uv|wsl|cadical|highs|g\+\+|clang|cc1|.*solver)\.exe$' })
$scoped = @($processes | Where-Object { $_.CommandLine -and $_.CommandLine -like '*conway-99-graph*' })
$unknown = @($processes | Where-Object { -not $_.CommandLine })
$execution = if ($scoped.Count -eq 0 -and $unknown.Count -eq 0) { 'NO_SCOPED_COMPUTATIONAL_WORKER_OBSERVED' } else { 'UNKNOWN' }
$records = @($d.records | ForEach-Object { [ordered]@{ id=$_.id; revision=$_.revision; statement=$_.original_binding_contract.statement; scope=$_.proposed_schema_scope; binding=$_.binding; primary_independent_report=$_.primary_independent_report } })
$cutoff = [ordered]@{
    schema='WAVE44_FROZEN400_DOCUMENTATION_CHECKPOINT_V1'; timestamp=$asof; source_commit=$head
    ledger='CLAIMS.yaml'; ledger_sha256=$ledgerHash; previous_report='docs/RESEARCH_20261003_FORTYTHIRD_WAVE.md'
    count_source='Actual type-sensitive comparison of all400 ledger records against independently checked registration copy; its accepted report supplies counts. Eleven binding projections retain exact statements.'
    claim_records=$r.claim_records; status_counts=$r.status_counts; review_state_counts=$r.review_state_counts
    new_claims=$records; new_claim_count=$records.Count; target_resolution='UNKNOWN'; external_review='NONE'
    overall_search_coverage='UNKNOWN; no validated denominator'; execution_state=$execution
    process_observation=[ordered]@{timestamp=$asof; scoped_count=$scoped.Count; unknown_count=$unknown.Count; outside_known_count=($processes.Count-$scoped.Count-$unknown.Count); private_argv_omitted=$true}
    input_sha256=$inputs; mathematical_replays=0; new_general_nonexistence_proofs=0
    availability='Existing6054PUBLIC records preserved; new400-cutoff artifacts remain LOCAL_ONLY pending separately checked immutable publication. Four historical MISSING traces remain disclosed.'
    outside_cutoff='Later triple-capped rational certificate, saved-point clique diagnostic/theorem, Gram written results, singleton/pair science and lower28 written theorem are not included in400.'
}
SaveJson ($out+'/checkpoint.json') $cutoff
$table = @('| Claim r1 | Exact recorded topic |', '| --- | --- |')
foreach ($rec in $d.records) { $table += '| '+$rec.id+' | '+$rec.label+' |' }
$body = @"
# Forty-fourth research milestone, 2026-10-04 JST

Since [wave43](RESEARCH_20261003_FORTYTHIRD_WAVE.md), eleven independently checked claim revisions were registered. The accepted ledger has $($r.claim_records) records: $($r.status_counts.VERIFIED) VERIFIED/CLEAR, $($r.status_counts.CANDIDATE) CANDIDATE/CLEAR and $($r.status_counts.REFUTED) REFUTED/CLEAR. All400 review states are CLEAR. The complete prior389 records and artifact entries were preserved.

**As of:** $asof; source context $head; ledger SHA256 $ledgerHash. The [programmatic checkpoint](../$out/checkpoint.json) retains exact eleven statements, scopes, binding identities and report references. This source context does not contain every new working file.

**Verdict:** target resolution UNKNOWN; no independently validated99-vertex target graph or general nonexistence proof. External review of a resolution: NONE.

**Verified changes:** the [ledger](../CLAIMS.yaml), [eleven-binding descriptor](../acceleration/proposal_20261003_wave44_claim_registry_descriptors_v3.json) and frozen checkpoint supply exact quantifiers and dependency revisions.

$($table -join "`n")

The unrestricted necessary ternary result forces an unbalanced actual-triangle column circuit with at most98 triangles. It does not force a particular minority-sign count, twelve-triangle configuration or a nontrivial automorphism. The two fixed17 rational vectors satisfy all154 moment equations exactly, but neither is an integer allocation or a graph completion. The outside-CN filter checks all9078 labelled point tests, retaining472 of534 original types and removing62. These are overlapping pipeline populations, not additive coverage counts.

The defined local family contains5184 distinct labelled graphs, all independently checked over16 fields and1498176 dense CN entries in41 parts. Its separate written classification proves four isomorphism classes of these edge unions. Arbitrary compatible additional induced edges and occurrence in a target are outside that family census and classification.

**Work completed:** the Saved-BEST finite census independently checks239085 labelled moves. It classifies87230 as invalid linearity,10395 as invalid selection and141460 as valid; every valid move increases F3. The141460 valid labels represent137597 distinct neighboring graphs. Zero residue exports were produced. The adjacency API check covers510 tiny-fixture roles and two declared synthetic99 probes; it is not the479556-role scientific census.

**Best result within this census:** the pinned baseline has F3=2119 and exact integer defect objective E=4258. Its minimum neighbor is F3=2122,E=4264. F3 counts nonzero unordered off-diagonal entries of the integer identity residual reduced modulo3; minimization of this version is the recorded direction. These finite values are not target-wide bounds or evidence that other move families fail. Construction rows do not enumerate all actual graph triangles.

**Verification:** the accepted protected-copy command independently checks all11 new typed records and their10027 distinct evidence identities, preserving prior389 records. The actual registration completed in19.000 seconds. The new [actual comparison](../acceleration/results/20261004_registered_eleven_projection01/summary.json) and [ROOT acceptance](../acceleration/results/20261004_registered_eleven_projection_root_actual_acceptance01.json) compare every400 record, artifact and root field against that accepted copy, normalizing only the root and11 new claim timestamps. Four typed failure controls pass. Invocation7b64ce75c14b4863a48e3a318bfc5e3c completed in13.563 seconds with a clean, reaped, empty Windows Job. This is registration integration, not a fresh replay of every historical proof.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No new general target exclusion is added. Counts of the defined family, fixed neighborhood and type universe measure only those populations. Earlier fixed exclusions and the380/792 branch record are unchanged and are not summed.

**Problems and limitations:** all16625 schema hash-check skips are explicitly disclosed; only two editorial-assumption hashes were checked by that schema invocation. The applicable new mathematical evidence has separate independent records. Schema validity and CI success are not mathematical verification. The invalid null registration V1, vetoed protected-copy V1 and corrected V2 are preserved; these engineering failures are not mathematical refutations. Four historical missing proof traces remain MISSING. Existing6054 PUBLIC entries remain preserved; new cutoff evidence remains LOCAL_ONLY until an immutable publication and separate availability audit succeed.

**Execution state:** $execution, observed at $asof with $($scoped.Count) scoped and $($unknown.Count) unclassified recognized computational processes. This observation does not assert global machine idleness or future execution. Completed receipts establish their own past commands only. The historical [user stop](../STOPPED_BY_USER.md) is preserved; the current explicit request authorizes resumed research under the [per-command policy](COMPUTE_POLICY.md).

**Next experiment:** independently replay the complete111628 exact dual-Gram/CN pair records for the fixed17/all472 universe, then test an integer count relaxation including only justified restrictions. The pair producer has completed, but its result remains CANDIDATE pending that separate check. Later triple-capped rational and singleton certificates and new written Gram/lower28 results remain outside the400-record cutoff until their bindings are registered; they are not silently included in these totals.

**References:** source context $head; [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3); [actual registration](../acceleration/results/20261004_wave44_claim_registration01/summary.json); [accepted protected copy](../acceleration/results/20261004_independent_review/registrar_v20_eleven_copy02/summary.json). Publication does not imply external acceptance of a target resolution.
"@
$milestone='docs/RESEARCH_20261004_FORTYFOURTH_WAVE.md'
if (Test-Path -LiteralPath $milestone) { throw 'Preserve existing milestone' }
[IO.File]::WriteAllText((Join-Path (Get-Location) $milestone),$body+"`n",[Text.UTF8Encoding]::new($false))
$docs=@('README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md')
$documentRecords=@()
foreach ($p in $docs) {
    $link=if ($p.StartsWith('docs/')) {'RESEARCH_20261004_FORTYFOURTH_WAVE.md'} else {'docs/RESEARCH_20261004_FORTYFOURTH_WAVE.md'}
    $prefix=@"
# Latest verified continuation checkpoint — wave44, 2026-10-04 JST

The [forty-fourth milestone]($link) freezes400 claims:392 VERIFIED/CLEAR,
3 CANDIDATE/CLEAR and5 REFUTED/CLEAR. Eleven additions cover two exact fixed17
rational moment witnesses, necessary CN/type constraints, one5184-label local
family and its four classes, an unrestricted necessary circuit bound98,
one239085-label saved-neighborhood census and finite adjacency API controls.
None resolves the target. Overall search coverage: UNKNOWN; no validated
denominator. Later independently reviewed results remain outside this cutoff.
All6054 earlier PUBLIC entries are preserved; new cutoff evidence remains
LOCAL_ONLY pending immutable confirmation. Use the linked checkpoint for the
separate target, verification and execution states. Historical text follows
byte for byte.

"@
    $absolute=Join-Path (Get-Location) $p
    $old=[IO.File]::ReadAllBytes($absolute)
    $before=Hash $p
    $snapshot=$out+'/'+$p.Replace('/','_')+'.before'
    [IO.File]::WriteAllBytes((Join-Path (Get-Location) $snapshot),$old)
    $prefixBytes=[Text.UTF8Encoding]::new($false).GetBytes($prefix+"`n")
    $stream=[IO.MemoryStream]::new()
    $stream.Write($prefixBytes,0,$prefixBytes.Length)
    $stream.Write($old,0,$old.Length)
    [IO.File]::WriteAllBytes($absolute,$stream.ToArray())
    $stream.Dispose()
    $new=[IO.File]::ReadAllBytes($absolute)
    if ($new.Length -ne $old.Length+$prefixBytes.Length) {throw 'Document byte length mismatch'}
    for ($i=0;$i -lt $old.Length;$i++) {if ($new[$i+$prefixBytes.Length] -ne $old[$i]) {throw 'Historical suffix changed'}}
    $documentRecords += [ordered]@{path=$p;before_sha256=$before;after_sha256=(Hash $p);historical_suffix_bytes_preserved=$true;prefix_bytes=$prefixBytes.Length;before_snapshot=$snapshot}
}
if ((Hash 'CLAIMS.yaml') -ne $ledgerHash -or (git rev-parse HEAD) -ne $head) {throw 'Closing protected state changed'}
SaveJson ($out+'/documentation_receipt.json') ([ordered]@{schema='WAVE44_DOCUMENTATION_RECEIPT_V1';timestamp=[DateTimeOffset]::UtcNow.ToString('o');command=@('powershell','-File','acceleration/record_20261004_wave44_documentation_v1.ps1');source_sha256=(Hash 'acceleration/record_20261004_wave44_documentation_v1.ps1');checkpoint_sha256=(Hash ($out+'/checkpoint.json'));milestone=$milestone;milestone_sha256=(Hash $milestone);documents=$documentRecords;ledger_unchanged=$true;mathematical_replays=0;availability_promotions=0;limitations='Editorial checkpoint derived from accepted ledger integration report and eleven literal bindings; no fresh mathematical verification or publication.'})
[ordered]@{checkpoint=($out+'/checkpoint.json');milestone=$milestone;claim_records=$r.claim_records;status_counts=$r.status_counts;execution_state=$execution;historical_suffixes_preserved=4;ledger_unchanged=$true} | ConvertTo-Json -Depth 8
