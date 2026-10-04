param(
    [Parameter(Mandatory=$true)][string]$Packet,
    [Parameter(Mandatory=$true)][string]$PacketSha256,
    [Parameter(Mandatory=$true)][string]$SourceSha256,
    [Parameter(Mandatory=$true)][string]$SpecSha256,
    [Parameter(Mandatory=$true)][string]$Out,
    [Parameter(Mandatory=$true)][double]$Seconds,
    [Parameter(Mandatory=$true)][string]$Executor
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$TaskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$TaskWatch = [Diagnostics.Stopwatch]::StartNew()
$TaskUtf8 = [Text.UTF8Encoding]::new($false)
$TaskPins = [Collections.Generic.SortedDictionary[string,string]]::new([StringComparer]::Ordinal)
$TaskOutPath = $null
$TaskOutCreated = $false
function Require([bool]$Condition,[string]$Stage) { if (-not $Condition) { throw $Stage } }
function Tick { Require ([double]::IsFinite($Seconds) -and $Seconds -gt 20 -and $Seconds -le 21600 -and $TaskWatch.Elapsed.TotalSeconds -lt ($Seconds-20)) 'SAVE_RESERVE' }
function SafePath([string]$Relative) {
    Require (-not [string]::IsNullOrWhiteSpace($Relative) -and $Relative -notmatch '[:\\]' -and -not [IO.Path]::IsPathRooted($Relative) -and @($Relative.Split('/') | Where-Object { $_ -in @('', '.', '..') }).Count -eq 0) 'INPUT_PATH'
    $Value = [IO.Path]::GetFullPath((Join-Path $TaskRoot $Relative))
    Require ($Value.StartsWith($TaskRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) 'INPUT_PATH'
    $Cursor=$Value
    while ($Cursor -and $Cursor.Length -ge $TaskRoot.Length) {
        if (Test-Path -LiteralPath $Cursor) { Require (((Get-Item -Force -LiteralPath $Cursor).Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) 'LINKED_PATH' }
        $Cursor=[IO.Path]::GetDirectoryName($Cursor)
    }
    return $Value
}
function ReadPinned([string]$Relative,[string]$Expected) {
    Tick
    Require ($Expected -cmatch '^[0-9a-f]{64}$') 'EXPECTED_SHA256'
    $Path=SafePath $Relative; $Item=Get-Item -Force -LiteralPath $Path
    Require (-not $Item.PSIsContainer -and $Item.Length -le 52428800) 'INPUT_FILE_OR_SIZE'
    $Bytes=[IO.File]::ReadAllBytes($Path)
    Require ($Bytes.Length -le 52428800 -and [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant() -ceq $Expected) 'INPUT_SHA256'
    $TaskPins[$Relative]=$Expected; Tick
    return ,$Bytes
}
function JsonObject($Bytes) {
    $Text=[Text.Encoding]::UTF8.GetString($Bytes)
    Require ($Text.TrimStart().StartsWith('{',[StringComparison]::Ordinal)) 'JSON_OBJECT_BASELINE_ONLY'
    return ($Text | ConvertFrom-Json -AsHashtable -DateKind String -Depth 100)
}
function CopyObject($Value) { return ($Value | ConvertTo-Json -Depth 100 -Compress | ConvertFrom-Json -AsHashtable -DateKind String -Depth 100) }
function SaveBytes([string]$Name,[byte[]]$Bytes) {
    Tick; $Path=Join-Path $TaskOutPath $Name; Require (-not (Test-Path -LiteralPath $Path)) 'OUTPUT_EXISTS'
    [IO.File]::WriteAllBytes($Path,$Bytes); Tick
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant()
}
function SaveJson([string]$Name,$Value) { return (SaveBytes $Name ($TaskUtf8.GetBytes(($Value | ConvertTo-Json -Depth 100)+[char]10))) }
try {
    Tick; $TaskOutPath=SafePath $Out
    Require ($TaskOutPath.StartsWith((Join-Path $TaskRoot 'acceleration/results')+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -and -not (Test-Path -LiteralPath $TaskOutPath)) 'FRESH_OUTPUT_ROOT'
    [IO.Directory]::CreateDirectory($TaskOutPath) | Out-Null
    $TaskOutCreated = $true
    ReadPinned 'acceleration/materialize_20261004_nine_bound_mathematical_claims_v1.ps1' $SourceSha256 | Out-Null
    ReadPinned 'acceleration/materialize_20261004_nine_bound_mathematical_claims_v1_spec.md' $SpecSha256 | Out-Null
    Require ($Packet -ceq 'acceleration/proposal_20261004_nine_bound_mathematical_literal_append_v2.json' -and $PacketSha256 -ceq '47bf0eb7189059585078c4d2219d06fac2dc8c5532867f81512c537b6935cf88') 'LITERAL_PACKET'
    $Data=JsonObject (ReadPinned $Packet $PacketSha256)
    Require ($Data.schema -ceq 'NINE_BOUND_MATHEMATICAL_LITERAL_APPEND_SOURCE_ONLY_V2' -and $Data.claims.Count -eq 9) 'PACKET_SHAPE'
    ReadPinned 'acceleration/run_compute_command.py' '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a' | Out-Null
    ReadPinned 'acceleration/command_deadline.py' '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9' | Out-Null
    ReadPinned $Data.validator.path $Data.validator.sha256 | Out-Null
    ReadPinned $Data.schema_definition.path $Data.schema_definition.sha256 | Out-Null
    ReadPinned 'pyproject.toml' '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339' | Out-Null
    ReadPinned 'uv.lock' 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db' | Out-Null
    Require ($Data.baseline.path -ceq 'CLAIMS.yaml' -and $Data.baseline.sha256 -ceq '95e8ffba7f7a8554c0de753495b3aba3a8eae0b8d238aecba81d3f1213db704c') 'BASELINE_IDENTITY'
    $BeforeBytes=ReadPinned $Data.baseline.path $Data.baseline.sha256
    $Ledger=JsonObject $BeforeBytes
    Require ($Ledger.claims.Count -eq 435 -and $Ledger.artifacts.Count -eq 23695 -and $Ledger.updated_at -is [string]) 'BASELINE_COUNTS'
    $Outputs=[ordered]@{'CLAIMS.before.yaml'=(SaveBytes 'CLAIMS.before.yaml' $BeforeBytes)}
    $OldArtifacts=@($Ledger.artifacts)
    $Artifacts=[Collections.Generic.List[object]]::new(); foreach ($Item in $OldArtifacts) { $Artifacts.Add($Item) }
    $Claims=[Collections.Generic.List[object]]::new(); foreach ($Item in $Ledger.claims) { $Claims.Add($Item) }
    $ArtifactIds=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $ClaimIds=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $Existing=[Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
    foreach ($Item in $OldArtifacts) {
        Require ($Item.id -is [string] -and $ArtifactIds.Add($Item.id)) 'OLD_ARTIFACT_IDS'
        if ($Item.availability -cin @('PUBLIC','LOCAL_ONLY')) {
            $Key=$Item.path+[char]0+$Item.sha256
            if (-not $Existing.ContainsKey($Key)) { $Existing.Add($Key,[Collections.Generic.SortedSet[string]]::new([StringComparer]::Ordinal)) }
            $Existing[$Key].Add($Item.id) | Out-Null
        }
    }
    foreach ($Item in $Ledger.claims) { Require ($Item.id -is [string] -and $ClaimIds.Add($Item.id)) 'OLD_CLAIM_IDS' }
    $Paths=[string[]]@($Data.evidence_union.Keys); [Array]::Sort($Paths,[StringComparer]::Ordinal)
    Require ($Paths.Count -eq 115 -and $Data.evidence_identity_count -eq 115) 'EXACT_EVIDENCE_UNION'
    Require (-not ($Paths -contains 'acceleration/results/20261004_fixed17_per_copy_local_sat_native01/proof.drat')) 'OLD_PARTIAL_PROOF_FORBIDDEN'
    $Resolved=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::Ordinal)
    $Rows=[Collections.Generic.List[object]]::new(); $Ordinal=0
    foreach ($PathKey in $Paths) {
        $Identity=@{path=$PathKey;sha256=$Data.evidence_union[$PathKey]}
        Tick; $Ordinal++; Require (-not $Resolved.ContainsKey($Identity.path)) 'DUPLICATE_EVIDENCE_PATH'
        ReadPinned $Identity.path $Identity.sha256 | Out-Null
        $Key=$Identity.path+[char]0+$Identity.sha256; $Reused=$Existing.ContainsKey($Key)
        if ($Reused) { $Id=$Existing[$Key].Min } else {
            $Id=('A-NINE-MATH-20261004-{0:0000}' -f $Ordinal); Require ($ArtifactIds.Add($Id)) 'NEW_ARTIFACT_ID_COLLISION'
            $Artifacts.Add([ordered]@{id=$Id;path=$Identity.path;sha256=$Identity.sha256;availability='LOCAL_ONLY';retrieval=$Identity.path;unavailable_reason='Exact mathematical evidence remains LOCAL_ONLY pending separate publication.'})
        }
        $Resolved.Add($Identity.path,$Id)
        $Rows.Add([ordered]@{ordinal=$Ordinal;path=$Identity.path;sha256=$Identity.sha256;artifact_id=$Id;reused=$Reused})
    }
    foreach ($Item in $Data.claims) {
        Tick; $Claim=CopyObject $Item.claim_core; Require ($ClaimIds.Add($Claim.id)) 'NEW_CLAIM_ID_COLLISION'
        $Claim.evidence=@($Item.evidence_identity_paths | ForEach-Object { $Resolved[$_] })
        $Verification=CopyObject $Item.verification_core; $Hashes=[ordered]@{}
        foreach ($Path in $Item.evidence_identity_paths) { $Hashes[$Resolved[$Path]]=$Item.evidence_identity_sha256[$Path] }
        $Verification.artifact_hashes=$Hashes; $Claim.verification=@($Verification)
        foreach ($Key in @('unknowns','external_source')) { $Claim[$Key]=CopyObject $Item[$Key] }
        if ($null -ne $Item.reproducibility_manifest_path) {
            Require ($Resolved.ContainsKey($Item.reproducibility_manifest_path)) 'REPRODUCIBILITY_IDENTITY'
            $Claim.reproducibility=@{manifest=$Resolved[$Item.reproducibility_manifest_path]}
        } else { $Claim.reproducibility=$null }
        $Claims.Add($Claim)
    }
    $Ledger.claims=$Claims.ToArray(); $Ledger.artifacts=$Artifacts.ToArray(); $Ledger.updated_at=[DateTimeOffset]::UtcNow.ToString('o')
    Require ($Ledger.claims.Count -eq 444) 'CANDIDATE_COUNT'
    $Outputs['CLAIMS.candidate.yaml']=SaveJson 'CLAIMS.candidate.yaml' $Ledger
    $Outputs['evidence_resolution.json']=SaveJson 'evidence_resolution.json' $Rows.ToArray()
    foreach ($Path in @($TaskPins.Keys)) { ReadPinned $Path $TaskPins[$Path] | Out-Null }
    $StatusCounts=[ordered]@{}; $ReviewCounts=[ordered]@{}; $ReuseCount=0
    foreach ($Claim in $Ledger.claims) { if (-not $StatusCounts.Contains($Claim.status)) {$StatusCounts[$Claim.status]=0};$StatusCounts[$Claim.status]++; if (-not $ReviewCounts.Contains($Claim.review_state)) {$ReviewCounts[$Claim.review_state]=0};$ReviewCounts[$Claim.review_state]++ }
    foreach ($Row in $Rows) { if ($Row.reused) {$ReuseCount++} }
    $Summary=[ordered]@{schema='NINE_BOUND_MATHEMATICAL_LITERAL_MATERIALIZATION_V1';timestamp=[DateTimeOffset]::UtcNow.ToString('o');status='CANDIDATE_ADMINISTRATIVE_UNVERIFIED';source_author='/root/checkpoint_audit';actual_executor=$Executor;before_claims=435;candidate_claims=444;before_artifacts=$OldArtifacts.Count;candidate_artifacts=$Artifacts.Count;evidence_identities=115;reused=$ReuseCount;appended=(115-$ReuseCount);candidate_status_counts=$StatusCounts;candidate_review_state_counts=$ReviewCounts;inputs_sha256=$TaskPins;outputs_sha256=$Outputs;elapsed_seconds=$TaskWatch.Elapsed.TotalSeconds;typed_preservation_independently_checked=$false;schema_semantics_checked=$false;live_ledger_mutated=$false;Git_index_mutated=$false;mathematical_replays=0;parser_scope='Frozen JSON-object subset only; native ConvertFrom-Json -AsHashtable -DateKind String. This is not a general YAML parser.';target_resolution='UNKNOWN';availability='LOCAL_ONLY';next_required='Separate Root typed prefix/core/evidence checking and unchanged generic validator; final Root exact installation remains separate.'}
    SaveJson 'summary.json' $Summary | Out-Null; Tick; exit 0
} catch {
    if ($TaskOutCreated -and (Test-Path -LiteralPath $TaskOutPath)) {
        $Failure=[ordered]@{schema='NINE_BOUND_MATHEMATICAL_LITERAL_MATERIALIZATION_V1';status='FAILED_PRESERVED';error=$_.Exception.Message;timestamp=[DateTimeOffset]::UtcNow.ToString('o');inputs_sha256=$TaskPins;elapsed_seconds=$TaskWatch.Elapsed.TotalSeconds;live_ledger_mutated=$false;mathematical_replays=0;target_resolution='UNKNOWN'}
        $FailurePath=Join-Path $TaskOutPath 'failure.json'; if (-not (Test-Path -LiteralPath $FailurePath)) { [IO.File]::WriteAllText($FailurePath,($Failure | ConvertTo-Json -Depth 100)+[char]10,$TaskUtf8) }
    }
    Write-Error $_ -ErrorAction Continue; exit 1
}
