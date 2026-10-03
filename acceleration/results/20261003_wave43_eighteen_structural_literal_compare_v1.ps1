$ErrorActionPreference = 'Stop'
$taskRoot = 'C:/Users/ikuto/projects/conway-99-graph'
Set-Location -LiteralPath $taskRoot
$taskMismatch = [System.Collections.Generic.List[object]]::new()
$taskHashes = [ordered]@{}
function Read-TaskJson([string]$Path) {
    $taskDocument = [System.Text.Json.JsonDocument]::Parse([System.IO.File]::ReadAllText((Join-Path $taskRoot $Path)))
    try { return $taskDocument.RootElement.Clone() } finally { $taskDocument.Dispose() }
}
function Pin-TaskFile([string]$Path, [string]$Expected) {
    $taskActual = (Get-FileHash -LiteralPath (Join-Path $taskRoot $Path) -Algorithm SHA256).Hash.ToLowerInvariant()
    $taskHashes[$Path] = $taskActual
    if ($taskActual -cne $Expected) { $taskMismatch.Add([ordered]@{path=$Path;stage='SHA256';expected=$Expected;actual=$taskActual}) }
}
function Compare-TaskJson($Expected, $Actual, [string]$Path) {
    if ($Expected.ValueKind -ne $Actual.ValueKind) { $taskMismatch.Add([ordered]@{path=$Path;stage='JSON_KIND';expected=$Expected.ValueKind.ToString();actual=$Actual.ValueKind.ToString()}); return }
    switch ($Expected.ValueKind.ToString()) {
        'Object' {
            $taskExpectedKeys = @($Expected.EnumerateObject() | ForEach-Object Name)
            $taskActualKeys = @($Actual.EnumerateObject() | ForEach-Object Name)
            if (($taskExpectedKeys -join "`0") -cne ($taskActualKeys -join "`0")) { $taskMismatch.Add([ordered]@{path=$Path;stage='ORDERED_KEYS';expected=$taskExpectedKeys;actual=$taskActualKeys}); return }
            foreach ($taskKey in $taskExpectedKeys) { Compare-TaskJson $Expected.GetProperty($taskKey) $Actual.GetProperty($taskKey) "$Path.$taskKey" }
        }
        'Array' {
            if ($Expected.GetArrayLength() -ne $Actual.GetArrayLength()) { $taskMismatch.Add([ordered]@{path=$Path;stage='ARRAY_LENGTH';expected=$Expected.GetArrayLength();actual=$Actual.GetArrayLength()}); return }
            for ($taskPosition=0; $taskPosition -lt $Expected.GetArrayLength(); $taskPosition++) { Compare-TaskJson $Expected[$taskPosition] $Actual[$taskPosition] "$Path[$taskPosition]" }
        }
        default {
            if ($Expected.GetRawText() -cne $Actual.GetRawText()) { $taskMismatch.Add([ordered]@{path=$Path;stage='LITERAL_SCALAR';expected=$Expected.GetRawText();actual=$Actual.GetRawText()}) }
        }
    }
}
function Compare-TaskSelected($Selected, $Actual, [string]$Path) {
    foreach ($taskProperty in $Selected.EnumerateObject()) {
        $taskActualValue = [System.Text.Json.JsonElement]::new()
        if (-not $Actual.TryGetProperty($taskProperty.Name, [ref]$taskActualValue)) { $taskMismatch.Add([ordered]@{path="$Path.$($taskProperty.Name)";stage='MISSING_KEY'}); continue }
        Compare-TaskJson $taskProperty.Value $taskActualValue "$Path.$($taskProperty.Name)"
    }
}
$taskDescriptorPath='acceleration/proposal_20261003_wave43_eighteen_written_bindings_v2.json'
$taskPlanPath='acceleration/plan_20261003_wave43_eighteen_written_registration_v2.json'
Pin-TaskFile $taskDescriptorPath '3f29f453813459d18740e5fb70fb7adddf56fed513db84f7598d4e4aeb1b331c'
Pin-TaskFile $taskPlanPath '0bfa921425b939536ef745c22869ce50191fb2e396a885f6f8d87254f05bb65e'
$taskDescriptor=Read-TaskJson $taskDescriptorPath
$taskPlan=Read-TaskJson $taskPlanPath
$taskRows=@($taskDescriptor.GetProperty('records_in_dependency_order').EnumerateArray())
$taskPlanRows=@($taskPlan.GetProperty('bindings_in_dependency_order').EnumerateArray())
$taskSelectedCount=0; $taskBindingFields=0; $taskReportFields=0; $taskReasonFields=0; $taskNullFields=0; $taskTimestampTokens=[System.Collections.Generic.List[object]]::new()
$taskPlanFieldMap=[ordered]@{order='order';id='id';revision='revision';path='binding_path';sha256='binding_sha256';route='route';statement='statement';planned_schema_scope='planned_schema_scope';original_binding_scope='scope';dependencies='dependencies';producer='producer';verifier='verifier';method='method';report='report';report_sha256='report_sha256'}
for ($taskPosition=0; $taskPosition -lt $taskRows.Count; $taskPosition++) {
    $taskRow=$taskRows[$taskPosition]
    $taskBindingPath=$taskRow.GetProperty('binding_path').GetString()
    Pin-TaskFile $taskBindingPath $taskRow.GetProperty('binding_sha256').GetString()
    $taskBinding=Read-TaskJson $taskBindingPath
    $taskReportPath=$taskBinding.GetProperty('report').GetString()
    Pin-TaskFile $taskReportPath $taskBinding.GetProperty('report_sha256').GetString()
    $taskReport=Read-TaskJson $taskReportPath
    foreach ($taskPair in @(@('binding_contract',$taskBinding),@('original_report_contract',$taskReport),@('original_binding_reason_fields',$taskBinding))) {
        $taskFields=$taskRow.GetProperty($taskPair[0]); $taskCount=@($taskFields.EnumerateObject()).Count
        $taskSelectedCount+=$taskCount
        switch ($taskPair[0]) {'binding_contract' {$taskBindingFields+=$taskCount}; 'original_report_contract' {$taskReportFields+=$taskCount}; default {$taskReasonFields+=$taskCount}}
        Compare-TaskSelected $taskFields $taskPair[1] "record[$($taskPosition+1)].$($taskPair[0])"
    }
    $taskNull=$taskRow.GetProperty('explicit_binding_null_fields'); $taskNullFields+=@($taskNull.EnumerateObject()).Count
    Compare-TaskSelected $taskNull $taskBinding "record[$($taskPosition+1)].explicit_binding_null_fields"
    $taskHeadline=$taskRow.GetProperty('original_report_headlines')
    Compare-TaskSelected $taskHeadline.GetProperty('present') $taskReport "record[$($taskPosition+1)].headlines"
    $taskAbsent=@(foreach ($taskName in @('claim_status','review_state','kind','basis')) { $taskValue=[System.Text.Json.JsonElement]::new(); if (-not $taskReport.TryGetProperty($taskName,[ref]$taskValue)) {$taskName} })
    $taskDeclaredAbsent=@($taskHeadline.GetProperty('absent').EnumerateArray() | ForEach-Object GetString)
    if (($taskAbsent -join "`0") -cne ($taskDeclaredAbsent -join "`0") -or $taskHeadline.GetProperty('absences_preserved').ValueKind.ToString() -cne 'True') { $taskMismatch.Add([ordered]@{path="record[$($taskPosition+1)].headlines";stage='ABSENCE_LITERAL';actual=$taskAbsent;expected=$taskDeclaredAbsent}) }
    Compare-TaskJson $taskRow.GetProperty('literal_input_pins') $taskBinding.GetProperty('inputs_sha256') "record[$($taskPosition+1)].literal_input_pins"
    $taskDeclaredInput=$taskRow.GetProperty('declared_input_count')
    if ($taskDeclaredInput.GetRawText() -cne [string]@($taskBinding.GetProperty('inputs_sha256').EnumerateObject()).Count) { $taskMismatch.Add([ordered]@{path="record[$($taskPosition+1)].declared_input_count";stage='COUNT'}) }
    $taskTimestampTokens.Add([ordered]@{binding=$taskBindingPath;literal=$taskBinding.GetProperty('verification_timestamp').GetRawText()})
    foreach ($taskKey in $taskPlanFieldMap.Keys) {
        $taskOriginName=$taskPlanFieldMap[$taskKey]
        $taskOrigin=if ($taskOriginName -cin @('id','revision','statement','scope','dependencies','producer','verifier','method','report','report_sha256')) {$taskBinding.GetProperty($taskOriginName)} else {$taskRow.GetProperty($taskOriginName)}
        Compare-TaskJson $taskOrigin $taskPlanRows[$taskPosition].GetProperty($taskKey) "plan.bindings[$($taskPosition+1)].$taskKey"
    }
}
$taskPython='C:/Users/ikuto/projects/conway-99-graph/build/research-venv/Scripts/python.exe'
$taskExpectedWorker=@($taskPython,'-B','acceleration/register_20261003_bound_claims_v18.py','--out','acceleration/results/20261003_wave43_registration01','--previous-sha256','23ee170c0f7250843ec2852758f0dd7d1324e85647c44e1907a62f062db47da9')
foreach ($taskRow in $taskRows) { $taskExpectedWorker+=@('--binding',$taskRow.GetProperty('binding_path').GetString(),'--binding-sha256',$taskRow.GetProperty('binding_sha256').GetString()) }
$taskExpectedChild=@('C:/Users/ikuto/.local/bin/uv.exe','run','--locked','--offline','--python',$taskPython)+$taskExpectedWorker
$taskWorker=@($taskPlan.GetProperty('worker_argv').EnumerateArray() | ForEach-Object GetString)
$taskChild=@($taskPlan.GetProperty('child_argv').EnumerateArray() | ForEach-Object GetString)
$taskSupervisor=@($taskPlan.GetProperty('supervisor_argv').EnumerateArray() | ForEach-Object GetString)
foreach ($taskPair in @(@('worker',$taskExpectedWorker,$taskWorker),@('child',$taskExpectedChild,$taskChild),@('supervisor_suffix',$taskExpectedChild,$taskSupervisor[16..($taskSupervisor.Count-1)]))) { if (($taskPair[1] -join "`0") -cne ($taskPair[2] -join "`0")) { $taskMismatch.Add([ordered]@{path="plan.$($taskPair[0])";stage='ARGV_LITERAL'}) } }
$taskExpectedPrefix=@($taskPython,'-B','acceleration/run_compute_command.py','--seconds','180','--shutdown-reserve-seconds','30','--allocation-reason',$taskPlan.GetProperty('allocation_reason').GetString(),'--success-criterion',$taskPlan.GetProperty('success_criterion').GetString(),'--verification-criterion',$taskPlan.GetProperty('verification_criterion').GetString(),'--out','acceleration/results/20261003_wave43_registration_supervision01','--')
if (($taskExpectedPrefix -join "`0") -cne ($taskSupervisor[0..15] -join "`0")) {$taskMismatch.Add([ordered]@{path='plan.supervisor_prefix';stage='ARGV_LITERAL'})}
if ($taskRows.Count -ne 18 -or $taskPlanRows.Count -ne 18 -or $taskSelectedCount -ne 693 -or ($taskRows.Count*2+$taskNullFields) -ne 41 -or $taskWorker.Count -ne 79 -or $taskChild.Count -ne 85 -or $taskSupervisor.Count -ne 101) {$taskMismatch.Add([ordered]@{stage='DECLARED_POPULATION'})}
$taskRoutes=@($taskRows | ForEach-Object {$_.GetProperty('route').GetString()})
$taskReport=[ordered]@{
 schema='WAVE43_EIGHTEEN_LITERAL_METADATA_DIFFERENT_AUTHOR_REVIEW_V1'; timestamp=[DateTimeOffset]::UtcNow.ToString('o'); reviewer='/root/structural'; descriptor_author='/root/checkpoint_audit'; outcome=$(if($taskMismatch.Count -eq 0){'PASS'}else{'VETO'});
 scope='Read-only literal metadata comparison. No registrar/source imports, native or mathematical execution, formal proof, protected-copy controls, actual371-to389 transition, ledger/index/Git mutation, or mathematical reapproval.';
 comparisons=[ordered]@{records=$taskRows.Count;binding_contract_fields=$taskBindingFields;report_contract_fields=$taskReportFields;binding_reason_fields=$taskReasonFields;selected_contracts=$taskSelectedCount;headline_groups=$taskRows.Count;explicit_null_fields=$taskNullFields;complete_literal_input_maps=$taskRows.Count;additional_contract_groups=($taskRows.Count*2+$taskNullFields);supervisor_words=$taskSupervisor.Count;child_words=$taskChild.Count;worker_words=$taskWorker.Count;binding_plan_fields=($taskPlanRows.Count*$taskPlanFieldMap.Count);pinned_original_binding_and_report_files=($taskRows.Count*2);route_labels=$taskRoutes};
 mismatch_count=$taskMismatch.Count;mismatches=$taskMismatch.ToArray();literal_original_verification_timestamp_tokens=$taskTimestampTokens.ToArray();inputs_sha256=$taskHashes;
 trust_and_limits=@('System.Text.Json preserves scalar JSON token types and original date-string text; no date parsing or ConvertFrom-Json used for compared values. Nested object keys and arrays are order-sensitive.','Binding/report bytes were SHA-pinned; transitive evidence-map content was compared literally without rehashing bulk mathematical artifacts.','Some underlying discoveries/proofs were authored by Structural. This report approves no underlying discovery, derivation, registrar route implementation or execution.','Plan wording, dependency scope and original no-target conclusions remain subject to ROOT separate review and actual typed impact.'); executed_mathematical_controls=0;native_calls=0;ledger_mutations=0;index_mutations=0;target_resolution='NONE'
}
$taskOutput=Join-Path $taskRoot 'acceleration/results/20261003_wave43_eighteen_structural_literal_review01.json'
if (Test-Path -LiteralPath $taskOutput) {throw 'Exclusive report path already exists'}
[System.IO.File]::WriteAllText($taskOutput,($taskReport|ConvertTo-Json -Depth 30)+"`n",[System.Text.UTF8Encoding]::new($false))
[ordered]@{report=$taskOutput;sha256=(Get-FileHash -LiteralPath $taskOutput -Algorithm SHA256).Hash.ToLowerInvariant();selected=$taskSelectedCount;extras=($taskRows.Count*2+$taskNullFields);mismatches=$taskMismatch.Count;words=@($taskSupervisor.Count,$taskChild.Count,$taskWorker.Count)}|ConvertTo-Json -Depth 5
