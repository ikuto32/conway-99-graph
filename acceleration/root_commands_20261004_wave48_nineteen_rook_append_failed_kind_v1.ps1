$ErrorActionPreference='Stop'
$TaskWatch=[Diagnostics.Stopwatch]::StartNew()
function TaskHash([string]$Path){if($TaskWatch.Elapsed.TotalSeconds -ge 150){throw 'ADMISSION_RESERVE'};(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
function TaskEq($A,$B,[string]$At){
 if($null -eq $A -or $null -eq $B){if($null -ne $A -or $null -ne $B){throw ('NULL '+$At)};return}
 if($A -is [System.Collections.IDictionary]){if($B -isnot [System.Collections.IDictionary] -or $A.Count -ne $B.Count){throw ('MAP '+$At)};foreach($K in $A.Keys){if(-not $B.Contains($K)){throw ('KEY '+$At)};TaskEq $A[$K] $B[$K] ($At+'.'+$K)};return}
 if($A -is [array]){if($B -isnot [array] -or $A.Count -ne $B.Count){throw ('ARRAY '+$At)};for($I=0;$I -lt $A.Count;$I++){TaskEq $A[$I] $B[$I] ($At+'.'+$I)};return}
 if($A.GetType() -ne $B.GetType() -or $A -cne $B){throw ('SCALAR '+$At)}
}
$TaskPlan='acceleration/plan_20261004_wave48_nineteen_rook_literal_materialization_v1.json'
$TaskPlanSha='8b21c1747114fec07868b932cff81a01a50e329010234aa1df85d047577f12a4'
if((TaskHash $TaskPlan) -cne $TaskPlanSha){throw 'PLAN'}
$TaskP=Get-Content -Raw -LiteralPath $TaskPlan | ConvertFrom-Json -AsHashtable -DateKind String -NoEnumerate
$TaskQ=Get-Content -Raw -LiteralPath $TaskP.packet.path | ConvertFrom-Json -AsHashtable -DateKind String -NoEnumerate
if($TaskP.command_template.Count -ne 36 -or $TaskP.child_argv.Count -ne 20 -or $TaskP.worker_argv.Count -ne 20 -or $TaskP.inputs_sha256.Count -ne 147 -or $TaskQ.claims.Count -ne 19 -or $TaskQ.evidence_union.Count -ne 137){throw 'COUNTS'}
TaskEq $TaskP.command_template[16..35] $TaskP.child_argv 'child';TaskEq $TaskP.child_argv $TaskP.worker_argv 'worker'
$TaskPins=[ordered]@{}
foreach($TaskMap in @($TaskP.inputs_sha256,$TaskP.admission_inputs_sha256,$TaskP.launchers)){foreach($TaskPath in $TaskMap.Keys){if((TaskHash $TaskPath) -cne $TaskMap[$TaskPath]){throw ('PIN '+$TaskPath)};$TaskPins[$TaskPath]=$TaskMap[$TaskPath]}}
$TaskPins[$TaskPlan]=$TaskPlanSha
$TaskGate='acceleration/results/20261004_bound_literal_claims_controls_root_actual_acceptance03.json'
if((TaskHash $TaskGate) -cne '18cef82fb7b97176ffed736bce5a2de3b6d418b757dd3ccca1f1b01e3ad87b61'){throw 'GATE'}
$TaskG=Get-Content -Raw -LiteralPath $TaskGate | ConvertFrom-Json -AsHashtable -DateKind String -NoEnumerate
if($TaskG.result -cne 'PASS_FINITE_ADMINISTRATIVE_CONTROLS_ONLY' -or $TaskG.positive -ne 3 -or $TaskG.negative -ne 19 -or $TaskG.total -ne 22){throw 'QUALIFICATION'}
foreach($TaskSubject in @($TaskP.qualification.source,$TaskP.qualification.checker,$TaskP.qualification.controls_source,$TaskP.qualification.controls_configuration,$TaskP.qualification.controls_plan)){if((TaskHash $TaskSubject.path) -cne $TaskSubject.sha256 -or $TaskG.fresh_inputs_sha256[$TaskSubject.path] -cne $TaskSubject.sha256){throw 'SUBJECT'};$TaskPins[$TaskSubject.path]=$TaskSubject.sha256}
$TaskPins[$TaskGate]=TaskHash $TaskGate
foreach($TaskExtra in @('acceleration/results/20261004_bound_literal_claims_controls03/summary.json','acceleration/results/20261004_bound_literal_claims_controls_supervision03/summary.json','acceleration/check_20261004_bound_literal_claims_v2_spec.md')){$TaskPins[$TaskExtra]=TaskHash $TaskExtra}
$TaskFrozen17Path='acceleration/proposal_20261004_wave48_seventeen_rook_literal_cores_v1.json'
if((TaskHash $TaskFrozen17Path) -cne '86bbe9bb30e90c9f2159bf5cbcbac600f81db37598dcb132796a147191784cc6'){throw 'FIXED17_IDENTITY'}
$TaskFrozen17=Get-Content -Raw -LiteralPath $TaskFrozen17Path|ConvertFrom-Json -AsHashtable -DateKind String -NoEnumerate
for($TaskI=0;$TaskI -lt 17;$TaskI++){TaskEq $TaskQ.claims[$TaskI] $TaskFrozen17.claims[$TaskI] ('fixed17/'+$TaskI)}
$TaskC=Get-Content -Raw -LiteralPath 'acceleration/configuration_20261004_wave48_nineteen_rook_literal_materialization_v1.json'|ConvertFrom-Json -AsHashtable -DateKind String -NoEnumerate
TaskEq $TaskC.worker_inputs_sha256 $TaskP.inputs_sha256 'config-worker-complete147'
TaskEq $TaskC.expected_context $TaskP.expected_context 'config-context'
TaskEq $TaskP.command $TaskP.command_template 'literal-command'
TaskEq $TaskP.supervisor_argv $TaskP.command_template 'literal-supervisor'
if($TaskP.expected_new_claims -ne 19 -or $TaskP.expected_claims_after -ne 486 -or $TaskP.baseline.claims -ne 467 -or $TaskP.expected_evidence_identity_rows -ne 137 -or $TaskP.command[4] -cne '180' -or $TaskP.worker_argv[17] -cne '150'){throw 'SCOPE'}
$TaskRows=@()
foreach($TaskItem in $TaskQ.claims){
 $TaskB=Get-Content -Raw -LiteralPath $TaskItem.binding.path | ConvertFrom-Json -AsHashtable -DateKind String -NoEnumerate
 $TaskR=Get-Content -Raw -LiteralPath $TaskItem.raw_primary_verification.path | ConvertFrom-Json -AsHashtable -DateKind String -NoEnumerate
 $TaskA=Get-Content -Raw -LiteralPath $TaskItem.administrative_acceptance.path | ConvertFrom-Json -AsHashtable -DateKind String -NoEnumerate
 foreach($TaskField in @('id','revision','statement','kind','basis','status','review_state','scope','assumptions','dependencies','limitations','created_at','updated_at')){
 $TaskBindingKey=$TaskField;if($TaskField -ceq 'limitations' -and -not $TaskB.Contains('limitations')){$TaskBindingKey='limits'}
 if(-not $TaskB.Contains($TaskBindingKey)){throw 'MISSING_BINDING_CORE_FIELD'}
 TaskEq $TaskItem.claim_core[$TaskField] $TaskB[$TaskBindingKey] ($TaskItem.claim_core.id+'.'+$TaskField)
 }
 foreach($TaskField in @('statement','scope','assumptions','dependencies')){TaskEq $TaskItem.claim_core[$TaskField] $TaskR[$TaskField] ($TaskItem.claim_core.id+'.report.'+$TaskField)}
 if($TaskB.verifier -cne $TaskItem.verification_core.verifier -or $TaskB.producer -cne $TaskItem.producer -or $TaskB.method -cne $TaskItem.verification_core.method -or $TaskB.verification_timestamp -cne $TaskItem.verification_core.timestamp -or $TaskR.verification_timestamp -cne $TaskItem.verification_core.timestamp -or $TaskR.claim_id -cne $TaskItem.claim_core.id -or $TaskR.claim_revision -ne $TaskItem.claim_core.revision -or $TaskR.result -cne 'PASS' -or $TaskItem.verification_core.outcome -cne 'PASS' -or $TaskItem.verification_core.scope -cne $TaskItem.claim_core.statement -or $TaskItem.verification_core.controls.Count -ne 0 -or $TaskA.claim_id -cne $TaskItem.claim_core.id -or $TaskA.claim_revision -ne $TaskItem.claim_core.revision -or $TaskA.statement -cne $TaskItem.claim_core.statement){throw 'ROLES_SCOPE_TIMES'}
 if($TaskItem.verification_core.claim_revision -ne $TaskItem.claim_core.revision -or $TaskItem.claim_core.status -cne 'VERIFIED' -or $TaskItem.claim_core.review_state -cne 'CLEAR' -or $TaskItem.verification_core.verifier -ceq $TaskItem.producer){throw 'PROMOTION_SCOPE'}
 TaskEq $TaskItem.verification_core.shared_components $TaskB.shared_components 'shared'
 $TaskCanonicalLimits=if($TaskB.Contains('limitations')){$TaskB.limitations}else{$TaskB.limits}
 TaskEq $TaskItem.verification_core.limitations $TaskCanonicalLimits 'limits'
 foreach($TaskPath in $TaskItem.evidence_identity_sha256.Keys){if($TaskQ.evidence_union[$TaskPath] -cne $TaskItem.evidence_identity_sha256[$TaskPath] -or $TaskP.inputs_sha256[$TaskPath] -cne $TaskItem.evidence_identity_sha256[$TaskPath]){throw 'EVIDENCE_UNION'}}
 $TaskRows+=@([ordered]@{id=$TaskItem.claim_core.id;revision=$TaskItem.claim_core.revision;binding=$TaskItem.binding;raw_report=$TaskItem.raw_primary_verification;Root_written_acceptance=$TaskItem.administrative_acceptance;verifier=$TaskItem.verification_core.verifier;verification_timestamp=$TaskItem.verification_core.timestamp;fields_typed_matched=13;evidence_identities=$TaskItem.evidence_identity_count})
}
if((TaskHash 'CLAIMS.yaml') -cne $TaskP.baseline.sha256 -or (git rev-parse HEAD).Trim() -cne $TaskP.expected_context.source_commit -or (TaskHash '.git/index') -cne $TaskP.expected_context.index_sha256){throw 'CONTEXT'}
$TaskPeers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(python.*|uv|kissat|drat-trim|pwsh)\.exe$' -and $_.CommandLine -match 'run_compute_command|materialize_20261004|conway-99-graph/(acceleration|build)' -and $_.ProcessId -ne $PID} | Select-Object ProcessId,Name)
if($TaskPeers.Count){throw 'WORKER'}
$TaskLinux=@(& wsl.exe -d Ubuntu-24.04 --exec bash -lc "pgrep -af '[r]un_compute_command|[c]onway-99-graph/(acceleration|build)'");$TaskLinuxExit=$LASTEXITCODE
if($TaskLinuxExit -ne 1 -or $TaskLinux.Count){throw 'LINUX_WORKER'}
$TaskOs=Get-CimInstance Win32_OperatingSystem;$TaskDisk=Get-PSDrive C;if($TaskOs.FreePhysicalMemory*1024 -lt 4GB -or $TaskDisk.Free -lt 1GB){throw 'RESOURCE'}
$TaskOne='acceleration/results/20261004_wave48_nineteen_rook_append_root_one01.json'
foreach($TaskPath in @($TaskOne,$TaskP.output_directory,$TaskP.supervision_directory)){if(Test-Path -LiteralPath $TaskPath){throw 'OUTPUT_EXISTS'}}
$TaskReceipt=[ordered]@{schema='ROOT_BOUND_LITERAL_NINETEEN_ROOK_APPEND_ONE_V1';timestamp=[DateTimeOffset]::UtcNow.ToString('o');authorizer='/root';executor='/root';authorized_invocations=1;plan=@{path=$TaskPlan;sha256=$TaskPlanSha};qualification=@{path=$TaskGate;sha256=$TaskPins[$TaskGate]};source_commit=$TaskP.expected_context.source_commit;index_sha256=$TaskP.expected_context.index_sha256;ledger_sha256=$TaskP.baseline.sha256;fresh_inputs_sha256=$TaskPins;fresh_small_identities=$TaskPins.Count;supervisor_argv=$TaskP.command_template;child_argv=$TaskP.child_argv;worker_argv=$TaskP.worker_argv;allocation=$TaskP.allocation;claim_projection_rows=$TaskRows;process_observation=@{windows=$TaskPeers;linux_exit=$TaskLinuxExit;linux_rows=$TaskLinux};resources=@{free_ram_bytes=$TaskOs.FreePhysicalMemory*1024;free_disk_bytes=$TaskDisk.Free};review=@('Nineteen exact literal cores (seventeen unchanged r1, b6r2, h1r1) independently matched all13 binding fields, raw statement/scope/assumptions/dependencies and genuine Root written acceptances; verifier roles/times/shared components/limits remain literal.','Whole mathematical papers and independent Native derivations were separately reviewed previously; this admission does not establish proofs by agreement or administrative tests.','Full137 small exact evidence identities plus fixed baseline/software/launchers rehashed, full22 actual controls for unchanged V3copier/V2checker accepted18cef82f. Failed source/run evidence retained.','New artifacts LOCAL_ONLY, old467/23956 prefixes and6054PUBLIC preserved; copier is only candidate preparation. Independent full typed actual prefix/core check and unchanged generic validator are required before separate guarded installation.');automatic_retry=$false;installation_authorized=$false;mathematical_replays=0;target_resolution='UNKNOWN';admission_elapsed_seconds=$TaskWatch.Elapsed.TotalSeconds}
[IO.File]::WriteAllText((Join-Path (Get-Location) $TaskOne),($TaskReceipt | ConvertTo-Json -Depth 70)+[char]10,[Text.UTF8Encoding]::new($false))
$TaskArgs=[string[]]$TaskP.command_template[1..35]
& $TaskP.command_template[0] @TaskArgs
exit $LASTEXITCODE
