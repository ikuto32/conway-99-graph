$ErrorActionPreference='Stop';$TaskWatch=[Diagnostics.Stopwatch]::StartNew()
function TaskHash([string]$Path){if($TaskWatch.Elapsed.TotalSeconds -ge 160){throw 'RESERVE'};(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
$TaskOld='9eec39f07bb726ddbf69c71ac9df59bdf6fe860a31c69d7513b89ddeb05fc2b1'
$TaskNew='32418255444775febd70512bdac6a62e8e3b33de1b540fba03d9a167032faa49'
$TaskHead='155a99539b86206520d8b8cc0f002d66cdc1b3e1';$TaskIndex='b7ff36caa9dc2a0233c77373be7c7bb195fab909ac4d30fdc3cb137f8dba0f2c'
$TaskCandidate='acceleration/results/20261004_wave47_ten_rook_append_candidate01/CLAIMS.candidate.yaml'
$TaskGates=[ordered]@{
 'acceleration/results/20261004_wave47_ten_rook_append_root_actual_acceptance01.json'='29d764a7a3e3977ec6eacf7da0bc01016397697d9c6d1090f1490c4e24f13225'
 'acceleration/results/20261004_wave47_ten_rook_typed_root_actual_acceptance01.json'='e0e825bce74f4a2281fd58efa7f27799fc2c03e962934aca5c25a45968fc4789'
 'acceleration/results/20261004_wave47_ten_rook_generic_root_actual_acceptance01.json'='176e74362d2ad5efe825f4b0920117bb5fe3feefa2602ec28638d5c5c1643f37'
}
$TaskPins=[ordered]@{}
$TaskGateRows=@()
foreach($TaskPath in $TaskGates.Keys){
 if((TaskHash $TaskPath) -cne $TaskGates[$TaskPath]){throw 'GATE'}
 $TaskG=Get-Content -Raw -LiteralPath $TaskPath | ConvertFrom-Json -AsHashtable -DateKind String
 if($TaskG.candidate_sha256 -cne $TaskNew -or $TaskG.source_commit -cne $TaskHead){throw 'GATE_SCOPE'}
 foreach($TaskInput in $TaskG.fresh_inputs_sha256.Keys){if($TaskPins.Contains($TaskInput) -and $TaskPins[$TaskInput] -cne $TaskG.fresh_inputs_sha256[$TaskInput]){throw 'GATE_INPUT_CONFLICT'};$TaskPins[$TaskInput]=$TaskG.fresh_inputs_sha256[$TaskInput]}
 $TaskPins[$TaskPath]=$TaskGates[$TaskPath]
 $TaskGateRows+=@(@{path=$TaskPath;sha256=$TaskGates[$TaskPath];result=$TaskG.result})
}
foreach($TaskPath in $TaskPins.Keys){if((TaskHash $TaskPath) -cne $TaskPins[$TaskPath]){throw ('CLOSING_PIN '+$TaskPath)}}
if((TaskHash 'CLAIMS.yaml') -cne $TaskOld -or (TaskHash $TaskCandidate) -cne $TaskNew -or (git rev-parse HEAD).Trim() -cne $TaskHead -or (TaskHash '.git/index') -cne $TaskIndex){throw 'CONTEXT'}
$TaskOut='acceleration/results/20261004_wave47_ten_rook_exact_installation_root_receipt01.json'
$TaskTemp='acceleration/results/20261004_wave47_ten_rook_exact_installation_temporary01.yaml'
foreach($TaskPath in @($TaskOut,$TaskTemp)){if(Test-Path -LiteralPath $TaskPath){throw 'EXISTING'}}
$TaskRoot=(Get-Location).Path
$TaskBytes=[IO.File]::ReadAllBytes((Join-Path $TaskRoot $TaskCandidate))
[IO.File]::WriteAllBytes((Join-Path $TaskRoot $TaskTemp),$TaskBytes)
if((TaskHash $TaskTemp) -cne $TaskNew -or (TaskHash 'CLAIMS.yaml') -cne $TaskOld){throw 'PRE_REPLACE'}
[IO.File]::Replace((Join-Path $TaskRoot $TaskTemp),(Join-Path $TaskRoot 'CLAIMS.yaml'),$null)
if((TaskHash 'CLAIMS.yaml') -cne $TaskNew -or (git rev-parse HEAD).Trim() -cne $TaskHead -or (TaskHash '.git/index') -cne $TaskIndex){throw 'READBACK'}
$TaskL=Get-Content -Raw -LiteralPath CLAIMS.yaml | ConvertFrom-Json -AsHashtable -DateKind String
$TaskCounts=[ordered]@{VERIFIED=@($TaskL.claims | Where-Object {$_.status -ceq 'VERIFIED'}).Count;CANDIDATE=@($TaskL.claims | Where-Object {$_.status -ceq 'CANDIDATE'}).Count;REFUTED=@($TaskL.claims | Where-Object {$_.status -ceq 'REFUTED'}).Count}
$TaskPublic=@($TaskL.artifacts | Where-Object {$_.availability -ceq 'PUBLIC'}).Count
if($TaskL.claims.Count -ne 467 -or $TaskL.artifacts.Count -ne 23956 -or $TaskPublic -ne 6054 -or $TaskCounts.VERIFIED -ne 458 -or $TaskCounts.CANDIDATE -ne 3 -or $TaskCounts.REFUTED -ne 6 -or @($TaskL.claims | Where-Object {$_.review_state -cne 'CLEAR'}).Count){throw 'INSTALLED_COUNTS'}
$TaskReceipt=[ordered]@{schema='ROOT_TEN_BOUND_LITERAL_EXACT_INSTALLATION_V1';timestamp=[DateTimeOffset]::UtcNow.ToString('o');installer='/root';result='INSTALLED_EXACT_ACCEPTED_CANDIDATE';source_commit=$TaskHead;index_sha256_before=$TaskIndex;index_sha256_after=TaskHash '.git/index';ledger_sha256_before=$TaskOld;ledger_sha256_after=$TaskNew;immutable_before_path='acceleration/results/20261004_wave47_ten_rook_append_candidate01/CLAIMS.before.yaml';installed_candidate_path=$TaskCandidate;claim_records=467;status_counts=$TaskCounts;review_state_counts=@{CLEAR=467};artifact_records=23956;PUBLIC_records=$TaskPublic;new_claims=10;new_artifacts=64;fresh_inputs_sha256=$TaskPins;fresh_small_identities=$TaskPins.Count;gates=$TaskGateRows;operation='Fresh temporary byte copy with hash/precondition guards, File.Replace on CLAIMS.yaml, exact byte/readback/count/index/HEAD checks; temp consumed, immutable predecessor retained.';mathematical_verification_basis='The ten statements have separate genuine independent written Native derivations and exact Root scope acceptance; administration does not verify mathematical proofs.';limitations=@('Only10 accepted exactr1 records appended; entire457/23892 prefixes checked twice through independent typed paths, schema/hashmode none separately passed.','Old mathematical payloads and proofs not replayed; new evidence remainsLOCAL_ONLY, all6054PUBLIC preserved.','No target-level graph or nonexistence proof, external acceptance or publication claim. R226 belongs to a later cutoff.');Git_index_mutations=0;PUBLIC_upgrades=0;mathematical_replays=0;target_resolution='UNKNOWN';overall_search_coverage='UNKNOWN; no validated denominator.';elapsed_seconds=$TaskWatch.Elapsed.TotalSeconds}
[IO.File]::WriteAllText((Join-Path $TaskRoot $TaskOut),($TaskReceipt | ConvertTo-Json -Depth 70)+[char]10,[Text.UTF8Encoding]::new($false))
[ordered]@{receipt=$TaskOut;sha256=TaskHash $TaskOut;ledger_sha256=TaskNew;claim_records=467;status_counts=$TaskCounts;artifact_records=23956;PUBLIC_records=$TaskPublic;fresh_small_identities=$TaskPins.Count} | ConvertTo-Json
