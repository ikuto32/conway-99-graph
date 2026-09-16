# ユーザー指示による停止 — 2026-09-05 11:31 JST

**探索・理論計算は停止済み。ユーザーが明示的に再開を指示するまで起動しない。**
過去の進捗記録や manifest に `RUNNING` が残っていても、本停止指示が優先する。
元の目標は変更していない。目標達成・不存在証明・数学的行き詰まりによる終了とは扱わない。

## 停止確認

- 旧 m03 ordinary 探索 PID 38272 を、起動時刻を照合して停止。
- small5 runner PID 30528 と全子孫プロセスを停止。
- m03 joint supplement runner PID 6268 と全子孫プロセスを停止。
- 把握していた22個のプロセスIDがすべて不在であることを再確認。
- 残っていた4個の Python はエディタの `lsp_server.py`。研究処理ではないため停止していない。
- 処理中の探索スタックは保存されない。完了済み shard / record 単位から再開可能。
  ファイルは削除せず、未監査結果も確定結果と区別して保持した。

E72 の実行設定・完了ファイルSHA・未完了task・停止前manifestのバイト同一
スナップショットは次に保存した。11:34:22 JSTの最終確認も LiveCount=0。

```
scratch_root_e72_stopped_20260905_1131_checkpoint.json
scratch_root_e72_stopped_20260905_1131_restart.md
scratch_root_e72_stopped_20260905_1131_small5_manifest.raw.json
scratch_root_e72_stopped_20260905_1131_m03_manifest.raw.json
```

## 確定済みの位置

詳細な経緯は `scratch_root_theory_priority_progress_20260905.md`。

| 範囲 | 停止時の確定状態 |
| --- | --- |
| E72 全台帳 | 未解決被覆 454,656 |
| E72 source150 | 未解決被覆 32,768 |
| 新規完了 macro (150,1,0) | 96軌道 / 被覆8,192、有限局所CSPの完全排除を独立被覆監査済み。DRAT証明ではない |
| E71 の既存132-macro試験集合 | 59 macro / 被覆26,017,792が残存。E71全層の結果ではない |
| 一様な E0 下界 | 正の下界は未証明 |
| 99頂点グラフ | 未構成。`submission.txt` は存在しない |

E72 台帳:
`scratch_root_e72_complete_coverage_inventory.py/.json/.md`

新規完了 macro の不変証拠:
`scratch_root_e72_source150_small5_joint_primary_m10_complete_audit.json`
SHA-256: `3A54FE7BF6B4E3F2FFEFA97AE2645D3D606AFEF7630823853469CA1AB02543C7`

## 中断した E72 計算

small5 の最後の独立監査済みチェックポイントは21/52 shard、168/400軌道、
局所 UNSAT 被覆13,248。完全 macro として台帳へ計上したのは (1,0) の8,192のみ。
停止直前の producer 出力が増えていれば、別途保存した停止スナップショットを参照し、
未監査出力をこの確定値に混ぜないこと。
停止時の producer-complete は24/52 shard。増分3件は macro (3,3) の
records 48–55、56–63、112–115で、すべて独立監査前のまま保存した。

```
scratch_root_e72_source150_small5_joint_primary_manifest.json
scratch_root_e72_source150_small5_joint_primary_partial_audit.json
scratch_root_e72_source150_small5_joint_primary_runner.py
```

m03 every-depth の80軌道走査は正常終了し、独立被覆監査も再実行済み。
69 UNSAT / 被覆3,648、11 local-SAT / 被覆448、UNKNOWNなし。
local-SAT は実グラフの存在を意味しない。

```
scratch_theory_e72_source150_sync_localpair_everydepth_m03_full.json
scratch_root_e72_source150_m03_everydepth_full_audit.py/.json/.md
```

次段 joint-map の対象IDは `11,36,38,56,57,58,59,63,65,71,74` のみ。
停止直前に record11 の producer が UNSAT / 被覆32を出力したが、
この supplement 結果の独立監査は未実施であり、中央台帳には未計上。
次の record36 の実行中に停止した。

```
scratch_root_e72_source150_m03_joint_supplement_manifest.json
scratch_root_e72_source150_m03_joint_supplement_runner.py
scratch_theory_e72_source150_sync_jointmap_m03_sat_r11.json
```

両 runner は完了ファイルを検査して利用する構造。再開する場合でも、まず停止時の
スナップショット・不変入力ハッシュ・未監査結果を確認する。ここには自動再開の許可はない。

## 理論側の保存内容と限界

- `scratch_theory_uniform_e0_zero_degree_moment_control.py/.json/.md`
  と `_audit.py/.json`: E0=0で平均化された次数第一・第二モーメントと根ラベル
  quota を満たす厳密有理対照。独立監査済み。整数 C やグラフ B の構成ではない。
- `scratch_theory_uniform_compression_rounding.py/.json/.md`
  と `_audit.py/.json/.md`: 整数圧縮行列の二乗トレースの区分線形下界。
  E0=0では tr(C²)>=2772、平均化行列との差の二乗ノルム>=84。
  独立監査済みだが、正の E0 下界・新規低層排除には至っていない。
- `scratch_theory_uniform_e0_zero_one_neighborhood_matching.py/.json`:
  上記一つの対照の N(x)=7K2 局所拡張。producer は正常終了したが、
  **独立監査と説明ノートは未作成**。その停止メモは
  `scratch_theory_uniform_e0_zero_one_neighborhood_STOP_CHECKPOINT.md`。

外部の916個の order-eight classes、208 deletion relations、944 marked-vertex
identities、4,440 marked-pair identities、2,414 coefficient matricesは再生成せず、
既存の `external_conway99_research` を読み取り専用で再利用している。

## 再計画時の方針制約

E72 残存枝は保持する。E71以下の全面列挙へは戻らない。
主目的は層に依存しない強い下界の証明であり、平均化で失われる整数圧縮の
共分散・頂点間や根間の整合性を区別して検討する。
ただし現在はユーザーの再計画待ちであり、追加探索・監査を自動で開始しない。
