# 2026-09-16 ユーザー指示による実行終了

予定トークン資源を消費したため、ユーザーの指示で実行を終了した。
新たな探索は、ユーザーから再開の指示を受けてから行う。
99頂点グラフ・一般の非存在証明は未取得であり、目標達成とは扱わない。

## 保存した状態

- 完了済み研究索引：`acceleration/results/20260916_star_guided_round3_checkpoint.json`
- SHA-256：`31fb80b68785901f2ed90f4c301aeac786aa0ae75609872d994f81f6d0b08414`
- 参照数：5,791。現在の起点は18481、強化LPの厳密区間は近似表示で
  `[5.374367028255648, 5.3743670369854]`。この固定配置自体も排除済み。

round3では8,904合法候補を独立列挙し、64件の辺LPを監査した。
1928の元LPだけが厳密誤差基準を超えたため、別ファイルで高精度再計算した。
同じ `1e-7` 基準で厳密ギャップ `1.1155662933177637e-13` を確認した。
元の停止記録・元LP・ログは保存されている。復旧後の30候補を強化LPと
独立整数証明で個別排除したが、最良値の改善はなかった。

## 新しいGPU経路

`rank_fresh_star_pdhg.py` は、保存LPを必要とせず、Rustで生成した元の84星集合から
強化モデルをGPUへ渡す。今回の128候補は、既存の辺LP候補と重複しない。
64候補を従来のGPU上界順で選び、残り64候補を変更箇所・サイクル長ごとに分散した。

保存先：`acceleration/results/20260916_fresh_star_rank_round3`。
`summary.json` のSHA-256は
`18b30d743e4d1f4474a594898a0ecab8eafd2bdc0b6772d23309c1d600927cc8`。
全128候補が500反復を完了し、上限到達はなかった。32候補ずつ4分割した。
Rust処理は1.21秒、行列構築・直列化は32.05秒、GPUプロセス合計は12.47秒。
事前検証後の処理時間は61.87秒で、初期起動と事前検証を含む全体時間ではない。
バイナリ入力は合計3,279,637,076バイト。GPU値は順位付けにだけ使う。

最後の独立監査はPASSし、同ディレクトリの `audit.json` に保存済み。
SHA-256は `7c68e223913274861125549212b70289eaa107b5719c65aa28e7aa2f34eb04ac`。
全128行列・入力対応・候補選抜と3件のCPU対照を検査するが、全候補の局所完全性や
排除を独立証明するものではない。終了時点の成否・ハッシュは
`acceleration/results/20260916_user_requested_stop.json` を正とする。

## 次回の入口（未実行）

新GPU順位から選ぶ16候補の局所独立監査・強化LPは未実施。
次のコマンドは出力を作らない事前検証であり、停止時点では実行していない。

```powershell
.venv/Scripts/python.exe -B acceleration/evaluate_fresh_star_shortlist.py --ranking acceleration/results/20260916_fresh_star_rank_round3/summary.json --ranking-audit acceleration/results/20260916_fresh_star_rank_round3/audit.json --baseline-star-audit acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/audit.json --out acceleration/results/20260916_fresh_star_rank_round3/shortlist --max-candidates 16 --selection union --validate-only
```

再開時に事前検証を通した後で `--validate-only` を外す。出力先が既に存在する場合は
上書きせず内容を確認する。評価後は `build_fresh_star_checkpoint.py` でround3索引と
結合できる。新評価器・作成器の意味検査は38件／25件PASSだが、実データでの
評価・索引作成は未実行。空領域・上限到達・非正の厳密下界は個別に保留する。
