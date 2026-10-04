param(
    [Parameter(Mandatory=$true)][string]$Configuration,
    [Parameter(Mandatory=$true)][string]$ConfigurationSha256,
    [Parameter(Mandatory=$true)][string]$Out,
    [Parameter(Mandatory=$true)][double]$Seconds
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$TaskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$TaskWatch = [Diagnostics.Stopwatch]::StartNew()
$TaskUtf8 = [Text.UTF8Encoding]::new($false)
$TaskRows = [Collections.Generic.List[object]]::new()
$TaskOutPath = $null

function Require([bool]$Condition, [string]$Stage) {
    if (-not $Condition) { throw $Stage }
}
function Tick {
    Require ([double]::IsFinite($Seconds) -and $Seconds -gt 20 -and $Seconds -le 21600) 'ALLOCATION'
    Require ($TaskWatch.Elapsed.TotalSeconds -lt ($Seconds - 20)) 'SAVE_RESERVE'
}
function SafePath([string]$Relative) {
    Require (-not [string]::IsNullOrWhiteSpace($Relative) -and $Relative -notmatch '[:\\]' -and
        -not [IO.Path]::IsPathRooted($Relative) -and
        @($Relative.Split('/') | Where-Object { $_ -in @('', '.', '..') }).Count -eq 0) 'INPUT_PATH'
    $Value = [IO.Path]::GetFullPath((Join-Path $TaskRoot $Relative))
    Require ($Value.StartsWith($TaskRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) 'INPUT_PATH'
    $Cursor = $Value
    while ($Cursor -and $Cursor.Length -ge $TaskRoot.Length) {
        if (Test-Path -LiteralPath $Cursor) {
            Require (((Get-Item -Force -LiteralPath $Cursor).Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) 'LINKED_PATH'
        }
        $Cursor = [IO.Path]::GetDirectoryName($Cursor)
    }
    return $Value
}
function Stat([string]$Path) {
    $Item = Get-Item -Force -LiteralPath $Path
    Require (-not $Item.PSIsContainer -and ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) 'INPUT_FILE'
    return [ordered]@{ bytes=[long]$Item.Length; last_write_utc_ticks=$Item.LastWriteTimeUtc.Ticks; creation_utc_ticks=$Item.CreationTimeUtc.Ticks }
}
function SameStat($Left, $Right) {
    return $Left.bytes -eq $Right.bytes -and $Left.last_write_utc_ticks -eq $Right.last_write_utc_ticks -and
        $Left.creation_utc_ticks -eq $Right.creation_utc_ticks
}
function SnapshotJson([string]$Relative, [string]$Expected) {
    Tick
    Require ($Expected -cmatch '^[0-9a-f]{64}$') 'EXPECTED_SHA256'
    $Path = SafePath $Relative
    $Before = Stat $Path
    Require ($Before.bytes -le 1048576) 'METADATA_SIZE'
    $Bytes = [IO.File]::ReadAllBytes($Path)
    Require ([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant() -ceq $Expected) 'METADATA_SHA256'
    Require (SameStat $Before (Stat $Path)) 'METADATA_CHANGED'
    Tick
    return ([Text.Encoding]::UTF8.GetString($Bytes) | ConvertFrom-Json -AsHashtable -DateKind String)
}
function Save([string]$Name, $Value) {
    Tick
    $Path = Join-Path $TaskOutPath $Name
    Require (-not (Test-Path -LiteralPath $Path)) 'OUTPUT_EXISTS'
    [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 60) + [char]10, $TaskUtf8)
    Tick
}

try {
    Tick
    $TaskOutPath = SafePath $Out
    Require ($TaskOutPath.StartsWith((Join-Path $TaskRoot 'acceleration/results') + [IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase) -and -not (Test-Path -LiteralPath $TaskOutPath)) 'OUTPUT_ROOT'
    [IO.Directory]::CreateDirectory($TaskOutPath) | Out-Null
    $Config = SnapshotJson $Configuration $ConfigurationSha256
    Require ($Config.schema -ceq 'PER_COPY_LOCAL_SAT_CLOSED_IDENTITY_SEAL_CONFIGURATION_V2') 'CONFIGURATION'
    $NativePath = SafePath $Config.native_root
    $ExpectedNames = @('linux_cleanup_observations.jsonl','manifest.json','progress.jsonl','proof.drat','reviews.jsonl','stderr.log','stdout.log','summary.json')
    $Names = @((Get-ChildItem -Force -LiteralPath $NativePath).Name)
    [Array]::Sort($Names, [StringComparer]::Ordinal)
    Require (($Names -join [char]0) -ceq ($ExpectedNames -join [char]0)) 'NATIVE_FILE_POPULATION'
    $Terminal = SnapshotJson ($Config.native_root + '/summary.json') $Config.native_terminal_sha256
    $Manifest = SnapshotJson ($Config.native_root + '/manifest.json') $Config.native_manifest_sha256
    Require ($Terminal.invocation_id -ceq $Config.native_invocation_id -and $Manifest.invocation_id -ceq $Config.native_invocation_id) 'INVOCATION'
    Require ($Manifest.runtime_scope -ceq 'LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2' -and
        $Manifest.source_sha256 -ceq '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17') 'NATIVE_SUPERVISOR'
    Require ($Terminal.stop_reason -ceq 'COMMAND_EXITED' -and
        ($Terminal.command_exit_code -is [int] -or $Terminal.command_exit_code -is [long]) -and
        $null -eq $Terminal.error -and $Terminal.deadline_reached -is [bool] -and -not $Terminal.deadline_reached -and
        $Terminal.hard_limit_observed -is [bool] -and $Terminal.hard_limit_observed) 'CLOSED_PROTOCOL'
    Require ($Terminal.cleanup.reaped -is [bool] -and $Terminal.cleanup.reaped -and
        $Terminal.cleanup.job_active_zero_observed -is [bool] -and $Terminal.cleanup.job_active_zero_observed -and
        $Terminal.cleanup.process_group_live_pids.Count -eq 0 -and $Terminal.cleanup.cleanup_errors.Count -eq 0) 'CLEAN_ORIGINAL_GROUP'
    Require ($Terminal.status -in @('COMMAND_COMPLETED_VERIFICATION_PENDING','NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')) 'SUPERVISOR_STATUS'
    $Expected = [Collections.Generic.SortedDictionary[string,object]]::new([StringComparer]::Ordinal)
    foreach ($Name in $Config.immutable_inputs_sha256.Keys) { $Expected.Add($Name, $Config.immutable_inputs_sha256[$Name]) }
    Require (-not $Expected.ContainsKey($Configuration)) 'CONFIGURATION_ALIAS'
    $Expected.Add($Configuration, $ConfigurationSha256)
    foreach ($Name in $ExpectedNames) {
        $Relative = $Config.native_root + '/' + $Name
        Require (-not $Expected.ContainsKey($Relative)) 'NATIVE_INPUT_ALIAS'
        $Expected.Add($Relative, $null)
    }
    $Expected[$Config.native_root + '/manifest.json'] = $Config.native_manifest_sha256
    $Expected[$Config.native_root + '/summary.json'] = $Config.native_terminal_sha256
    foreach ($Relative in $Expected.Keys) {
        Tick
        $Path = SafePath $Relative
        $Before = Stat $Path
        # Standard cmdlet streams every byte, including a multi-gigabyte proof.
        # This atomic cmdlet has no per-block worker tick; the external Job deadline remains authoritative.
        $Digest = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        $After = Stat $Path
        Require (SameStat $Before $After) 'CHANGED_DURING_HASH'
        if ($null -ne $Expected[$Relative]) { Require ($Digest -ceq $Expected[$Relative]) 'EXPECTED_IDENTITY' }
        $Row = [ordered]@{ path=$Relative; sha256=$Digest; before=$Before; after=$After; availability='LOCAL_ONLY' }
        $TaskRows.Add($Row)
        [IO.File]::AppendAllText((Join-Path $TaskOutPath 'checkpoint.jsonl'), ($Row | ConvertTo-Json -Depth 12 -Compress) + [char]10, $TaskUtf8)
        Tick
    }
    foreach ($Row in $TaskRows) { Require (SameStat $Row.after (Stat (SafePath $Row.path))) 'CHANGED_AT_CLOSE'; Tick }
    $ClosingNames = @((Get-ChildItem -Force -LiteralPath $NativePath).Name)
    [Array]::Sort($ClosingNames, [StringComparer]::Ordinal)
    Require (($ClosingNames -join [char]0) -ceq ($ExpectedNames -join [char]0)) 'NATIVE_FILE_POPULATION_AT_CLOSE'
    $TotalBytes = [long]0
    foreach ($Row in $TaskRows) { $TotalBytes += [long]$Row.before.bytes }
    Save 'summary.json' ([ordered]@{
        schema='PER_COPY_LOCAL_SAT_CLOSED_IDENTITY_SEAL_V2'; timestamp=[DateTimeOffset]::UtcNow.ToString('o'); status='IDENTITY_SEAL_COMPLETE';
        native_invocation_id=$Config.native_invocation_id; native_terminal=$Terminal; native_manifest=$Manifest; native_physical_files=8;
        sealed_file_count=$TaskRows.Count; artifacts=$TaskRows.ToArray(); elapsed_seconds=$TaskWatch.Elapsed.TotalSeconds;
        bytes=$TotalBytes;
        original_protocol_exit=$Terminal.command_exit_code; proof_verified=$false; SAT_object_checked=$false; mathematical_replays=0;
        target_resolution='UNKNOWN'; availability='LOCAL_ONLY'; actual_executor='See external Windows593 supervisor receipt';
        limitations=@('Identity-only seal of closed bytes and genuine terminal metadata. No SAT/UNSAT correctness or exclusion is asserted.',
            'Stable size/time observations are not an adversarial concurrency guarantee; proof is hashed once through standard Get-FileHash.',
            'Atomic hash/serialization can cross worker reserve; actual external contained clean terminal is required. No automatic proof or assignment replay.')
    })
    Tick
    exit 0
} catch {
    if ($null -ne $TaskOutPath -and (Test-Path -LiteralPath $TaskOutPath)) {
        $Failure = [ordered]@{ schema='PER_COPY_LOCAL_SAT_CLOSED_IDENTITY_SEAL_V2'; status='FAILED_PRESERVED'; error=$_.Exception.Message;
            timestamp=[DateTimeOffset]::UtcNow.ToString('o'); completed_files=$TaskRows.ToArray(); elapsed_seconds=$TaskWatch.Elapsed.TotalSeconds;
            proof_verified=$false; SAT_object_checked=$false; mathematical_replays=0; target_resolution='UNKNOWN' }
        $FailurePath = Join-Path $TaskOutPath 'failure.json'
        if (-not (Test-Path -LiteralPath $FailurePath)) { [IO.File]::WriteAllText($FailurePath, ($Failure | ConvertTo-Json -Depth 30) + [char]10, $TaskUtf8) }
    }
    Write-Error $_ -ErrorAction Continue
    exit 1
}
