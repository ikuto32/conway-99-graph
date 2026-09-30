# Independent third literal eight-count-profile proof audit

This wave26 audit preserves the frozen wave25 publication, native outputs and all previous proof reviews. No solver is rerun. Its proposed conclusion concerns only `count_master_third_native_sat_after_six_scalar_cuts`, profile digest `3bc6ebf9444e7a2f15af1ac85c6164119333244ced5d6dbe83a6c6b367e533d5`, on the fixed six-prism Hadamard support.

The independent encoding gate is `306e86ff14f7be929cd1f0f345b127b8cdf7341ae1e016b51499f2773654aab6`; the complete-object calibration gate is `6a1f00d783976bfa63a0f63f9b479829f73bb967731784b355a1e2b0caed0039`. They bind the exact 9,748-variable, 167,416-clause formula and all 2,184 original selectors. The eight exceptional groups are 1, 3, 5, 11, 13, 15, 18 and 19; the remaining twelve groups are balanced. Initial domains include within-group column caps. Cross-group caps, residual D, arc pruning and orbit coverage are absent.

The complete preserved trace has 5,549,451 bytes and SHA256 `17d87b5ef8724d70d7809d8f9cb581afe720272a1633fde261767f90b035340c`. Its native summary is `73dd66bb97da7b9da731586230d24bf56200512f755a81f0e01b7b844e412e1f`. Before replay, the auditor authenticates all gate and raw-input pins, the entire native command, native exit20, exact launched CNF, configured 60-second wall/1M-conflict/4GiB-AS/10GiB-file/70-second outer allocation, historical ext4 placement and immediate copy/hash receipts. Workspace creation and retention intent are recorded separately from unknown future availability. No current ext4 availability is assumed.

The source is a fresh specialization of the frozen second eight-profile proof audit. It reuses the separately authored checker-authentication and subprocess-replay helper from the balanced proof review. The source-authenticated DRAT-trim executable, disclosed Windows timing shim, compiler and runtime remain explicit trusted components. No producer Python is imported, no solver correctness is assumed, and no diverse or formal proof-checker claim is made.

Fresh controls require acceptance of a truth-table checked, non-unit-refutable tiny UNSAT formula with nonempty reasoning; rejection of missing reasoning, a fresh invalid unit and a changed satisfiable input; and rejection of six corrupted native header/status/exit/guard/allocation records. A separate occurrence-list unit propagator checks the actual raw CNF and saves any forcing-clause trail. The research empty-only proof control must agree with that exact calculation. Unit-propagation fixtures distinguish contradictory units, a satisfiable nonunit formula and a non-unit-refutable UNSAT formula. Any saved trail is diagnostic, not a separately approved certificate. Failure of unit propagation implies no SAT conclusion. The full original proof is always replayed.

PASS requires complete original DRAT acceptance and every identity, receipt and control check. The dependency is `C-FIXED-HADAMARD-THIRD-EIGHT-COUNT-PROFILE-GRAM-ENCODING r1`; the proposed result is `C-FIXED-HADAMARD-THIRD-EIGHT-COUNT-PROFILE-EXCLUSION r1`. Only this literal profile is excluded. The verified count witness, all 540 exact scalar interval checks and all 60 separate block witnesses remain valid for their weaker necessary models. No other profile, orbit, whole support or target-graph conclusion follows. Local presence does not establish public availability or external peer review.

Run once using the existing locked environment and a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_third_eight_count_profile_unsat.py --out acceleration/results/20260930_independent_review/third_eight_count_profile_unsat
```
