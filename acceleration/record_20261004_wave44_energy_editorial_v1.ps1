$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$milestoneRel = 'docs/RESEARCH_20261004_FORTYFOURTH_WAVE.md'
$milestonePath = Join-Path $repoRoot $milestoneRel
$snapshotRootRel = 'acceleration/results/20261004_wave44_energy_definition_editorial01'
$snapshotRoot = Join-Path $repoRoot $snapshotRootRel
if (Test-Path -LiteralPath $snapshotRoot) { throw 'Editorial output already exists' }
$before = [IO.File]::ReadAllBytes($milestonePath)
$beforeSha = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($before)).ToLowerInvariant()
if ($beforeSha -ne 'c4897f14f36e3585340676d3cc670373e3f0319a0799ebfc85c7c17895ca359c') { throw 'Unexpected milestone before bytes' }
$codec = [Text.UTF8Encoding]::new($false, $true)
$text = $codec.GetString($before)
$anchor = 'F3 counts nonzero unordered off-diagonal entries of the integer identity residual reduced modulo3; minimization of this version is the recorded direction.'
$replacement = $anchor + ' Here R=A²+A−12I−2J and E=Σ_{i<j}R_ij², as defined by the pinned adjacency-switch kernel specification.'
if (($text.Split($anchor).Length - 1) -ne 1) { throw 'Editorial anchor is not unique' }
$after = $codec.GetBytes($text.Replace($anchor, $replacement))
[IO.Directory]::CreateDirectory($snapshotRoot) | Out-Null
$beforeRel = $snapshotRootRel + '/RESEARCH_20261004_FORTYFOURTH_WAVE.md.before'
$snapshot = [IO.File]::Open((Join-Path $repoRoot $beforeRel), [IO.FileMode]::CreateNew)
try { $snapshot.Write($before) } finally { $snapshot.Dispose() }
[IO.File]::WriteAllBytes($milestonePath, $after)
$afterSha = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($after)).ToLowerInvariant()
$specRel = 'acceleration/adjacency_ternary_switch_kernel_20261003_v1_spec.md'
$specSha = (Get-FileHash -LiteralPath (Join-Path $repoRoot $specRel) -Algorithm SHA256).Hash.ToLowerInvariant()
if ($specSha -ne '1b5844c669be85b420d33626c144f078ec15c66259c921c6e2b29a433709dc8c') { throw 'Kernel specification changed' }
$receipt = [ordered]@{
    schema = 'WAVE44_ENERGY_DEFINITION_EDITORIAL_RECEIPT_V1'
    timestamp = [DateTimeOffset]::UtcNow.ToString('o')
    author = '/root/structural'
    authorization = 'ROOT explicit reversible editorial instruction; no new mathematical scope or status'
    source = 'acceleration/record_20261004_wave44_energy_editorial_v1.ps1'
    source_sha256 = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
    milestone = $milestoneRel
    before_snapshot = $beforeRel
    before_sha256 = $beforeSha
    after_sha256 = $afterSha
    before_bytes = $before.Length
    after_bytes = $after.Length
    exact_inserted_text = $replacement.Substring($anchor.Length)
    definition_source = [ordered]@{path=$specRel;sha256=$specSha}
    other_bytes_preserved = ($codec.GetString($after).Replace($replacement, $anchor) -ceq $text)
    as_of_and_cutoff_unchanged = $true
    historical_pair_candidate_at_cutoff_unchanged = $true
    prior_documentation_receipt_unchanged = 'acceleration/results/20261004_wave44_documentation01/documentation_receipt.json'
    mathematical_replays = 0
    ledger_index_git_mutations = 0
    availability_promotions = 0
}
if (-not $receipt.other_bytes_preserved) { throw 'Editorial inverse check failed' }
$receiptBytes = $codec.GetBytes(($receipt | ConvertTo-Json -Depth 12) + "`n")
$receiptPath = Join-Path $snapshotRoot 'receipt.json'
$receiptStream = [IO.File]::Open($receiptPath, [IO.FileMode]::CreateNew)
try { $receiptStream.Write($receiptBytes) } finally { $receiptStream.Dispose() }
$receipt | ConvertTo-Json -Depth 12
