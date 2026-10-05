$ErrorActionPreference = 'Stop'
$taskCwd='C:/Users/ikuto/projects/conway-99-graph'
$taskSource='acceleration/inventory_20261004_wave45_checkpoint_v3.py'
$taskSpec='acceleration/inventory_20261004_wave45_checkpoint_v3_spec.md'
$taskSourceHash=(Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash.ToLowerInvariant()
$taskSpecHash=(Get-FileHash -LiteralPath $taskSpec -Algorithm SHA256).Hash.ToLowerInvariant()
$taskSoftware=[ordered]@{
    $taskSource=$taskSourceHash; $taskSpec=$taskSpecHash
    'acceleration/command_deadline.py'='9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9'
    'acceleration/run_compute_command.py'='593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a'
    'pyproject.toml'='273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'
    'uv.lock'='a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db'
}
$taskLauncher=(Get-Content -LiteralPath acceleration/plan_20261004_fixed17_copy_adjacency_author_controls_root_v1.json -Raw|ConvertFrom-Json -AsHashtable -DateKind String).launcher_byte_pins
$taskPython=$taskCwd+'/build/research-venv/Scripts/python.exe'
$taskUv='C:/Users/ikuto/.local/bin/uv.exe'
$taskContext=[ordered]@{head='adffeee94206e640a2648d050fd8ab2406449517';ledger_sha256='70e5b2a3d904f168dad6ebb814615ba71f331c635bb892019d713277a24d89e2';index_sha256='9e52968786373a8f725bfa2fd4aff4554ed9e050ebceddc1fceb54f389eae192'}
$taskRoutePairs=@(
    @('canonical_nul','PASS'),@('complete_two_manifest','PASS'),@('known_abc_hash','PASS'),@('empty_closed_log_hash','PASS'),@('selected_index_unselected_gitlink','PASS'),@('safe_gitignore','PASS'),
    @('nul_terminator','SELECTED_NUL'),@('nul_duplicate','SELECTED_UNIQUE'),@('nul_order','SELECTED_ORDER'),@('nul_utf8','SELECTED_UTF8'),@('nul_empty','SELECTED_EMPTY'),
    @('parent_path','PATH_SCOPE'),@('git_path','PATH_PRIVATE'),@('environment_path','PATH_PRIVATE'),@('build_path','PATH_PRIVATE'),@('proof_path','PATH_PROOF'),
    @('manifest_count_bool','MANIFEST_COUNT'),@('late_bytes_bool','MANIFEST_BYTES'),@('late_sha_bool','MANIFEST_SHA'),@('late_conflicting_hashes','MANIFEST_SHA'),@('manifest_path_difference','SELECTED_MANIFEST'),
    @('member_hash_mismatch','MEMBER_SHA'),@('raw_blob_mismatch','GIT_BLOB_IDENTITY'),@('member_size_mismatch','MEMBER_BYTES'),@('late_member_bound','MANIFEST_BYTES'),
    @('selected_gitlink','GIT_SELECTED_MODE'),@('selected_unmerged','GIT_SELECTED_STAGE'),@('index_duplicate','GIT_DUPLICATE'),@('missing_member','MEMBER_MISSING'),@('authenticated_json_and_nul_helper','PASS'),@('authenticated_reader_wrong_sha','INPUT_SHA'),@('authenticated_parser_duplicate','JSON_DUPLICATE'),@('reversed_manifest_exact_bijection','PASS'),@('duplicated_manifest_path','MANIFEST_PATH_DUPLICATE')
)
$taskRoutes=@();foreach($taskPair in $taskRoutePairs){$taskRoutes += [ordered]@{index=$taskRoutes.Count;name=$taskPair[0];expected_stage=$taskPair[1];observed_stage=$null;prospective_only=$true}}
if($taskRoutes.Count-ne34){throw 'CONTROL_METADATA_COUNT'}
$taskCalOut='acceleration/results/20261004_wave45_inventory_author_controls03'
$taskCalSup='acceleration/results/20261004_wave45_inventory_author_controls_supervision03'
$taskWorker=@($taskPython,'-B',($taskCwd+'/'+$taskSource),'calibrate','--seconds','150','--out',($taskCwd+'/'+$taskCalOut),'--self-sha256',$taskSourceHash,'--spec-sha256',$taskSpecHash,'--executor','/root')
$taskChild=@($taskUv,'run','--locked','--offline','--cache-dir',($taskCwd+'/build/uv-cache'),'--python',$taskPython)+$taskWorker
$taskReason='New read-only publication identity inventory finite qualification:8 positives/26 precise negatives/34 saved payload/stage rows, known abc and empty-log bytehashes, wrong raw Gitblob identity, late manifest/path/size/type corruption.180outer150inclusiveworker20save20shutdown includes six software/source hashes and final output/direct-pin guards. No real selected443MB payload or Git command is read by calibration.'
$taskSuccess='All8 positives/26 precise negative first stages match literally; save82 nonsummary hashes/83 physical files, including34 payload/stage pairs,eight positive results,five tiny fixtures and controls. Require clean genuine supported593 WindowsJob receipt. Failures preserve partials/no automatic retry.'
$taskVerify='Root independently reads whole source/spec/literal controls and genuine raw calibration. Successful finite qualification applies only to this exact new engineering implementation; actual1947-file inventory needs separate acceptedcal/fresh protected418 context and ONE. No mathematical,remote,staging or availability claim.'
$taskCommand=@($taskPython,'-B',($taskCwd+'/acceleration/run_compute_command.py'),'--seconds','180','--shutdown-reserve-seconds','20','--allocation-reason',$taskReason,'--success-criterion',$taskSuccess,'--verification-criterion',$taskVerify,'--out',($taskCwd+'/'+$taskCalSup),'--')+$taskChild
if($taskCommand.Count-ne38-or$taskChild.Count-ne22-or$taskWorker.Count-ne14){throw 'CAL_VECTOR_COUNT'}
$taskFresh=[ordered]@{source_plan_launcher_pins=$true;source_output_absence=$true;scoped_ownership_resources=$true;unknown_workspace_compute_veto=$true;current_HEAD_ledger_index=$true;save_read_admission=$true}
$taskCal=[ordered]@{
    schema='ROOT_CONCRETE_WAVE45_EXPLICIT_INVENTORY_AUTHOR_CALIBRATION_V3';timestamp=[DateTimeOffset]::UtcNow.ToString('o');status='SOURCE_ONLY'
    source=$taskSource;source_sha256=$taskSourceHash;specification=$taskSpec;specification_sha256=$taskSpecHash;source_author='/root/checkpoint_audit';planned_executor='/root'
    command=$taskCommand;child_argv=$taskChild;worker_argv=$taskWorker;word_counts=[ordered]@{supervisor=38;child=22;worker=14}
    allocation=[ordered]@{outer=180;worker=150;save=20;shutdown=20};allocation_reason=$taskReason;success_criterion=$taskSuccess;verification_criterion=$taskVerify
    cwd=$taskCwd;environment=[ordered]@{UV_PROJECT_ENVIRONMENT='build/research-venv';restore_afterward=$true};inputs_sha256=$taskSoftware;source_software_sha256=$taskSoftware;direct_pin_count=6;launcher_byte_pins=$taskLauncher
    outputs=[ordered]@{worker=$taskCalOut;supervisor=$taskCalSup;required_absent=$true};expected_controls=$taskRoutes;expected_positive=8;expected_negative=26;expected_total=34;expected_nonsummary_hashes=82;expected_physical_files=83
    actual_selected_input_read=$false;mathematical_replays=0;git_calls=0;git_ledger_index_mutations=0;target_resolution='NONE'
    context_expected_from_parent=$taskContext;context_provenance='Root message08:37UTC, not an executor fresh observation';operational_context=$null;fresh_admission_required=$taskFresh
    root_one_authority=$null;dispatch_authorized=$false;automatic_retry=$false;null_reason='Whole source/spec/literal plan review and fresh saved-read admission plus Root ONE still required; no actual calibration exists'
}
$taskCalName='acceleration/plan_20261004_wave45_inventory_author_controls_root_v3.json'
if(Test-Path -LiteralPath $taskCalName){throw 'CAL_PLAN_EXISTS'}
[IO.File]::WriteAllText((Join-Path (Get-Location) $taskCalName),(ConvertTo-Json -InputObject $taskCal -Depth 30)+"`n",[Text.UTF8Encoding]::new($false))
$taskKnown=[ordered]@{};foreach($taskE in $taskSoftware.GetEnumerator()){$taskKnown[$taskE.Key]=$taskE.Value}
$taskKnown['acceleration/results/20261004_wave45_checkpoint_publication_closure05.json']='3f7005fa3491d0a3e38e34413b181abc7e0e1b60305622d887ed4cfbf62f5d26'
$taskKnown['acceleration/results/20261004_wave45_checkpoint_publication_selected01.paths0']='9e28d88e995aeec32608b90078383e7c66cc5705f546763e4ed28ce293634ca1'
$taskKnown['acceleration/results/20261004_wave45_checkpoint_packaging_audit01.json']='36e80ec45e2f81b47de915f132c43c2b19562bedc6b14635d9e8c6ac1ec9ce89'
$taskKnown['acceleration/proposal_20261004_wave45_eighteen_bound_claims_v3.json']='d80ebf22f6d0a9eea28b249568081bc9d1a16df3306aebbf5d2c4bcb268a6411'
$taskKnown['acceleration/results/20261004_registrar_v33_actual_transition01/summary.json']='2797e2021b9335d370d89a56313b9ec33aeae2de34667a38083488e7e9de7ced'
$taskKnown['acceleration/results/20261004_registrar_v33_actual_transition_root_actual_acceptance01.json']='c0ac375df04e7c475a85cd0709d53bc42c779d56c834b4d72c6e3c0671c831b4'
$taskConfig=[ordered]@{
    schema='WAVE45_EXPLICIT_PUBLICATION_INVENTORY_CONFIGURATION_V1';timestamp=[DateTimeOffset]::UtcNow.ToString('o');status='SOURCE_ONLY_NULL_TEMPLATE'
    source=$taskSource;source_sha256=$taskSourceHash;specification=$taskSpec;specification_sha256=$taskSpecHash;inputs_sha256=$taskKnown
    calibration_path=$null;calibration_sha256=$null;root_calibration_acceptance_path=$null;root_calibration_acceptance_sha256=$null;expected_protected_context=$null
    protected_context_required_from_root=$taskContext;frozen_claims=418;new_claims=18;selected_distinct=1947;expected_selected_bytes=442895627;largest_member=16159523;member_cap=52428800
    old_PUBLIC_preserved_premise=6054;new_cutoff_artifact_availability='LOCAL_ONLY';availability_mutation=$false;selection_expansion=$false;physical_cat_file_replay=$false
    null_reason='New actual calibration+Rootacceptance and fresh exact418 HEAD/ledger/index needed before a new concrete config; future422 ledger cannot replace this frozen70e5 identity';dispatch_authorized=$false;automatic_retry=$false;target_resolution='NONE'
}
$taskConfigName='acceleration/proposal_20261004_wave45_inventory_configuration_v3.json'
if(Test-Path -LiteralPath $taskConfigName){throw 'CONFIG_EXISTS'}
[IO.File]::WriteAllText((Join-Path (Get-Location) $taskConfigName),(ConvertTo-Json -InputObject $taskConfig -Depth 30)+"`n",[Text.UTF8Encoding]::new($false))
$taskConfigHash=(Get-FileHash -LiteralPath $taskConfigName -Algorithm SHA256).Hash.ToLowerInvariant()
$taskOut='acceleration/results/20261004_wave45_identity_inventory02'
$taskSup='acceleration/results/20261004_wave45_identity_inventory_supervision02'
$taskFullWorker=@($taskPython,'-B',($taskCwd+'/'+$taskSource),'inventory','--seconds','550','--out',($taskCwd+'/'+$taskOut),'--self-sha256',$taskSourceHash,'--spec-sha256',$taskSpecHash,'--executor','/root','--configuration',($taskCwd+'/'+$taskConfigName),'--configuration-sha256',$taskConfigHash)
$taskFullChild=@($taskUv,'run','--locked','--offline','--cache-dir',($taskCwd+'/build/uv-cache'),'--python',$taskPython)+$taskFullWorker
$taskFullReason='One exact1947-member443MB selected byte inventory, source/config/closure/NUL/calibration authentication and read-only Gitmetadata.600outer550inclusiveworker20save20shutdown permits1947 small-file IO/hash operations with protected/direct closing checks; prior smaller publication inventories justify this uncertainty allowance, not a completion probability. No mathematical imports,private/proof bulk,staging or availability mutation.'
$taskFullSuccess='All1947 current regular safe members have exact declared bytes/SHA256; preserve full member inventory and20 checkpoints (21 nonsummary/22physical), no missing/extra or identity errors; before/after HEAD,index,CLAIMS70e5 equal admitted418 context. Record tracked raw-working Gitblob OID diagnostics separately. Require clean supported593 receipt; any error vetoes staging and stays preserved.'
$taskFullVerify='Root independently reviews complete logical inventory and exact closure/list/418 premise, actual runtime and limitations. SHA identity checks are engineering only; no math,remote or availability approval. No physical cat-file replay claimed; exact selected staged blobs and any appendices require a separate reviewed protocol. New records remainLOCAL_ONLY until genuine commit and proper availability revision.'
$taskFullCommand=@($taskPython,'-B',($taskCwd+'/acceleration/run_compute_command.py'),'--seconds','600','--shutdown-reserve-seconds','20','--allocation-reason',$taskFullReason,'--success-criterion',$taskFullSuccess,'--verification-criterion',$taskFullVerify,'--out',($taskCwd+'/'+$taskSup),'--')+$taskFullChild
if($taskFullCommand.Count-ne42-or$taskFullChild.Count-ne26-or$taskFullWorker.Count-ne18){throw 'FULL_TEMPLATE_VECTOR_COUNT'}
$taskFull=[ordered]@{
    schema='WAVE45_EXPLICIT_PUBLICATION_INVENTORY_SOURCE_ONLY_PLAN_V3';timestamp=[DateTimeOffset]::UtcNow.ToString('o');status='SOURCE_ONLY_NULL_TEMPLATE'
    future_concrete_schema='ROOT_CONCRETE_WAVE45_EXPLICIT_INVENTORY_PLAN_V3';source_author='/root/checkpoint_audit';planned_executor='/root'
    source=$taskSource;source_sha256=$taskSourceHash;specification=$taskSpec;specification_sha256=$taskSpecHash;configuration_path=$taskConfigName;configuration_sha256=$taskConfigHash;inputs_sha256=$taskKnown
    command=$null;child_argv=$null;worker_argv=$null;command_template=$taskFullCommand;child_argv_template=$taskFullChild;worker_argv_template=$taskFullWorker
    word_counts=[ordered]@{supervisor=42;child=26;worker=18};allocation=[ordered]@{outer=600;worker=550;save=20;shutdown=20};allocation_reason=$taskFullReason;success_criterion=$taskFullSuccess;verification_criterion=$taskFullVerify
    cwd=$taskCwd;environment=[ordered]@{UV_PROJECT_ENVIRONMENT='build/research-venv';restore_afterward=$true};launcher_byte_pins=$taskLauncher;outputs=[ordered]@{worker=$taskOut;supervisor=$taskSup;required_absent=$true}
    selected_distinct=1947;selected_bytes=442895627;frozen_claims=418;selected_CLAIMS_sha256='70e5b2a3d904f168dad6ebb814615ba71f331c635bb892019d713277a24d89e2'
    required_calibration_path=$null;required_calibration_sha256=$null;root_calibration_acceptance=$null;operational_context=$null;fresh_admission_required=$taskFresh
    root_one_authority=$null;dispatch_authorized=$false;automatic_retry=$false;target_resolution='NONE';selection_expansion=$false
    null_reason='Frozen null configuration is intentionally nondispatchable; new immutable concrete config/plan follows genuine own34/Root acceptance/current418 admission+ONE. Future ledger422 requires a separately preserved inventory or explicit ledger appendix, not silent replacement'
    source_imports=0;member_hashes_by_preparation=0;Git_ledger_index_mutations=0
}
$taskFullName='acceleration/proposal_20261004_wave45_identity_inventory_full_v3.json'
if(Test-Path -LiteralPath $taskFullName){throw 'FULL_TEMPLATE_EXISTS'}
[IO.File]::WriteAllText((Join-Path (Get-Location) $taskFullName),(ConvertTo-Json -InputObject $taskFull -Depth 30)+"`n",[Text.UTF8Encoding]::new($false))
$taskRows=@();foreach($taskName in @($taskSource,$taskSpec,$taskCalName,$taskConfigName,$taskFullName)){$taskRows += [ordered]@{path=$taskName;sha256=(Get-FileHash -LiteralPath $taskName -Algorithm SHA256).Hash.ToLowerInvariant();bytes=(Get-Item -LiteralPath $taskName).Length}}
[ordered]@{files=$taskRows;calibration_words=[ordered]@{supervisor=38;child=22;worker=14};full_template_words=[ordered]@{supervisor=42;child=26;worker=18};calibration_direct_pins=6;known_full_direct_pins=$taskKnown.Count;controls=34;member_hashes=0;imports=0;mutations=0}|ConvertTo-Json -Depth 8
