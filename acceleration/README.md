# Rust / CUDA による overlap 探索

2026-09-16 の再開で、既存の E0=0 overlap 探索を高速化した。
99 頂点グラフの構成や一般の非存在証明にはまだ到達していない。
入力は 84 外側頂点上の **完全な overlap 配置**で、168 本の既知の辺を持つ。
同一 fibre 内と未記載の overlap 辺は存在しないと固定し、disjoint support 間の
1,680 変数を後続の補完問題に残す。

その後、ユーザーの指示により構成または一般の非存在証明を目標として再設定した。
現在の進捗は [ゴール継続記録](../docs/GOAL_20260916_PROGRESS.md) を参照。
以下の最初の測定記録にある「96 候補が未検査」は保存時点の情報で、現在は
固定 walk の保存 101 件すべてを独立検証付きで排除済み。可変 compression の
別 walk でも保存 101 件を排除したが、どちらも探索空間全体の排除ではない。

追加実装は `ray_probe.py`（直接 HiGHS ray を利用する厳密証明生成）、
`star_domains.rs` / `star_domains_batch.rs`（完全な局所隣接選択肢の列挙と相互整合性）、
`overlap_neighbors.rs`（合法な辺交換）、`guided_overlap.py`（有限の誘導探索）。
HiGHS ray 用の環境には `requirements.txt` の `highspy` も必要となる。

`guided_two_trade_overlap.py` では、Rust による2段階交換生成、
CUDA による線形残差の候補評価、HiGHS IPM による最適化と完全局所条件の
検査を組み合わせた。評価値は 22.2201 から 7.3321 へ低下し、改善と最良配置の
局所整合性は独立検証済み。ただし最良配置自体も厳密に補完不能と証明されている。
この評価値は完成グラフへの距離や達成率ではない。
手法は [phase-I の定義と検証](../docs/GOAL_20260916_GLOBAL_PHASE1.md)、
[CUDA 入出力](PHASE_GPU_FORMAT.md)、[2段階交換](TWO_TRADE_NEIGHBORS.md) を参照。
既存のハッシュ付きコードは保存し、更新は別名の実装・監査器として追加した。

その後、Rust の3辺・4辺交互サイクル生成と CUDA 評価を組み合わせた
`guided_atomic_overlap.py` を追加した。3回の有限探索に含まれる515件のLPと、
各状態の完全な提案集合を独立検証したが、最良評価値は7.33212201のまま。
詳細は [交互サイクル探索](../docs/GOAL_20260916_ATOMIC_CYCLES.md) を参照。

現在は `matching_phase1_mip.py` により、21組あるマッチングのうち1組全体を
変更するモデルへ拡張した。整数証明を検査する `audit_matching_farkas.py` は、
数値ソルバーを使わず99頂点の隣接関係から制約行列を再構成する。
全21組の診断から8組について、それぞれ残り20組を現最良配置に固定した
全6,040通りの補完不能を独立検証した。重複を除いた和集合は48,313配置で、
部分グラフの条件を満たさない配置も含む。複数組の同時変更は範囲外であり、
これは条件付きの排除で、一般の非存在証明ではない。残る13組は未解決。
導出・再現コマンドは [マッチング全体の継続記録](../docs/GOAL_20260916_MATCHING_MIP.md) にある。

続いて `overlap_matching_neighbors.rs` が同符号マッチング全体を約0.70秒で
列挙し、合法な74,638候補を独立Python列挙でも確認した。組ごとのXを使う
CUDA採点から64件を追加評価し、局所整合性を保った最良値を **7.31624646** に
改善した。改善幅と全84頂点の局所選択肢・整合性は独立検証済みだが、この
固定配置も補完不能であり、目標の完成グラフではない。
新しい種・証拠・次のGPU最適化案は
[全マッチング探索の続報](../docs/GOAL_20260916_WHOLE_MATCHING_SEARCH.md) を参照。

最初の `overlap_cp_gpu.cu` は、候補ごとに補完変数も近似最適化する。
Rust参照実装と独立CPU検査に通過し、73,239候補の500反復をカーネル約42.20秒で
処理した。選択した64件のLPを独立監査し、最良値は **5.94436612** に改善。
最良配置の局所整合性も独立検証済みだが、固定配置自体は補完不能である。
最初の実装は [CUDA再最適化の記録](../docs/GOAL_20260916_CUDA_CP_SEARCH.md)、
仕様は [CP_GPU_INTERFACE.md](CP_GPU_INTERFACE.md) にある。

その後のGPU配置変更版は、同じ512候補の比較でカーネル時間を約2.745倍短縮した。
同符号側の再探索と異符号側の3辺・4辺サイクルへ範囲を広げ、独立検証付きで
正の最良値を **0.06406994** に更新し、数値上ほぼ0の候補2件を整数条件の検査へ進めた。
これらは完成グラフではなく、周辺の9候補を加えた11件でSATの不充足証明を独立検証した。
現在の再開地点と証拠は
[GPU改良と異符号側への継続](../docs/GOAL_20260916_CP_CONTINUATION.md) を参照。

数値ゼロ到達後は、完全局所選択肢の確率分布を使う強化LPとRustの同時選択DFSを追加した。
新LPの整数証明を独立再生し、新しい目的値で **9.067435 → 8.113671 → 6.038934 → 5.374367** への改善を確認した。
最新の起点18481も固定配置としては排除されており、さらに配置を変更する。
強化モデルの [CUDA実装](STAR_PDHG_GPU.md) は保存したCPU反復状態との一致を確認した。
同じ2候補を3回交互に測定した結果、起動・保存込みの速度比は中央値9.43倍だった。
従来の目的値とは異なるため、直接比較しない。現在の起点・証明・再開方法は
[完成条件と強化LP](../docs/GOAL_20260916_STAR_MARGINAL.md) にある。

`star_dual_batch.rs` は固定双対を整数演算で採点し、8,837候補を68.27秒で処理した。
5配置×2双対の独立対照で最小値・最小化マスクを確認済みだが、この採点自体は
候補選択用であり排除証明ではない。強化モデルの新GPU実装に向けたCPU参照と
射影の厳密対照は [測定と設計](STAR_MARGINAL_CP_FEASIBILITY.md) に記録した。

## 実装

- `overlap_cpu.rs`: 依存クレート不要。128-bit 隣接ビット集合による合法な
  2 辺交換の列挙、seed 付き walk、64-bit 整数の必要条件評価。
- `overlap_gpu.cu`: RTX 4090 上で必要条件を候補・カット・128 符号変換ごとに
  並列評価する。評価値には浮動小数点を使わない。入力の整数範囲を検査する。
- `prepare.py`: 保存された証明から CPU/GPU 共通入力を生成する。
  追加証明には独立監査を要求する。
- `verify_scores.py`: Rust と CUDA の全評価値を照合し、Python 参照実装とも比較する。
  `--reference-limit` を指定した場合、Python との比較はその候補数に限る。
- `linear_probe.py`: SciPy/HiGHS で必要な線形補完条件を解き、数値双対解を
  整数係数に丸め、負係数を box bound で補正して厳密な証明を抽出する。
- `audit_certificate.py`: ソルバーや producer を import せず、99 頂点の隣接集合から
  証明の全係数を再構築する標準ライブラリだけの検証器。
- `audit_walk.py`: 全交換と保存 snapshot を独立再生し、次数、block totals、
  label quotas、共通近傍上限を検査する。
- `probe_walk.py`: 条件を通過した snapshot の決定的な有限標本を検査し、
  得られた証明を独立検証する。manifest、全件の score audit、walk audit を照合し、
  同数の別入力や部分照合の結果を取り違えて使わない。

負のカット値は、その完全 overlap 配置の補完不能を示す。
非負の値、局所 walk の終了、数値ソルバーのステータスだけではグラフの存在も
非存在も証明されない。全 E0 配置の網羅性も主張していない。

## ビルドと軽量再現

リポジトリのルートで実行する。Python 3.12 と Rust、GPU 版には CUDA Toolkit と
Visual Studio C++ build tools を用意する。各出力ディレクトリは未使用の名前にする。

```powershell
New-Item -ItemType Directory -Force acceleration/build | Out-Null
rustc -O -C target-cpu=native acceleration/overlap_cpu.rs -o acceleration/build/overlap_cpu.exe
./acceleration/build_gpu.ps1
python -B acceleration/prepare.py --out build/check_controls
acceleration/build/overlap_cpu.exe score build/check_controls/cuts.txt build/check_controls/candidates.txt build/check_controls/cpu.json 1
acceleration/overlap_gpu.exe build/check_controls/cuts.txt build/check_controls/candidates.txt build/check_controls/gpu.json 1
python -B acceleration/verify_scores.py --candidates build/check_controls/candidates.txt --cpu build/check_controls/cpu.json --gpu build/check_controls/gpu.json --out build/check_controls/parity.json
```

Linux の CPU ビルドも通常の `rustc -O ... -o build/overlap_cpu` でよい。
GPU の共通入力は `C99CUTS1`（constant、84×14 alpha、84×84 beta）と
`C99OVERLAPS1`（候補数と各候補168辺）の空白区切りテキスト。
探索は明示した回数で終了し、バックグラウンド常駐処理を起動しない。

```powershell
acceleration/build/overlap_cpu.exe walk build/check_controls/candidate_5.txt build/walk.json 10000 20260916
python -B acceleration/audit_walk.py build/walk.json --out build/walk_audit.json
python -B acceleration/prepare.py --walk build/walk.json --out build/walk_inputs
```

## 証明の再検証

保存した証明の検査には SciPy、GPU、Rust は不要。

```powershell
python -B acceleration/audit_certificate.py --candidate scratch_follow_overlap_walk.json --certificate acceleration/results/20260916_walk_highs.json --out build/walk_certificate_recheck.json
python -B acceleration/audit_walk.py acceleration/results/20260916_walk_10000.json --out build/walk_recheck.json
```

数値探索を再現する場合は、既存の solver 環境を変更せず、任意の専用 venv に
`pip install -r acceleration/requirements.txt` を行う。

```powershell
.venv/Scripts/python.exe -B acceleration/linear_probe.py --input scratch_follow_overlap_walk.json --out build/walk_highs.json --seconds 30
.venv/Scripts/python.exe -B acceleration/audit_certificate.py --candidate scratch_follow_overlap_walk.json --certificate build/walk_highs.json --out build/walk_highs_audit.json
```

`--seconds` は各 solve の上限。タイムアウトや数値異常を排除証明として扱わない。
新しい環境では別の双対解やステータスになる可能性がある。保存した整数証明の
独立検証が、ソルバーのバージョンに依存しない再現手段になる。

## 今回の測定と研究結果

RTX 4090 / CUDA 13.2、Rust 1.92.0、Python 3.12.10 のローカル測定。

| 処理 | 測定結果 |
| --- | ---: |
| Python、最終101候補の129,280評価 | 231.260秒 |
| Rust、同じ129,280評価 | 0.567秒 |
| CUDA、同じ129,280評価 | 転送込み0.0145秒 |
| Rust、合法交換10,000回 | 3.027秒 |

評価時間はファイル解析を除く。CUDA は context 初期化・メモリ確保も別計測
（最終測定の setup は約0.102秒）。以前の反復測定ではアップロード済み入力を再利用した。
この速度比は評価器のもので、線形計画を含む探索全体の速度比ではない。

既存6候補の3,840値に加え、最終101候補・10カットの **129,280値すべて** が
Python/Rust/CUDA で完全一致した。1万回の全交換、
101 snapshots、386万件の増分共通近傍上限も独立監査済み。

以前640カットを通過して数値異常で止まっていた配置を、新しい整数証明で排除した。
その証明を第6カットとして加えると、101 snapshots 中100が768条件を通る。
そのうち snapshot 1, 34, 67, 100 を検査し、4件すべてに追加の整数証明を得た。

| 配置 | 独立検証済みの結合右辺 |
| --- | ---: |
| 以前の3交換 walk | −107,551 |
| 新 walk snapshot 1 | −136,935 |
| snapshot 34 | −147,698 |
| snapshot 67 | −113,785 |
| snapshot 100 | −124,972 |

すべて1,680変数の結合係数が非負で、負の右辺との矛盾を確認した。
これらは固定した5配置の排除であり、一様な非存在証明ではない。
証拠は `results/20260916_walk_highs*` と `results/20260916_probes/` にある。

5件の新証明は、元の5カットへ追加して **10カット×128符号変換** の集合にした。
最終入力・評価値は `results/20260916_final_bank/` に保存している。
101 snapshots のうち既知の5件を除く96件が1,280条件を通る。
これら96件の線形補完は未検査で、存在の証拠にはならない。
カットの追加は `--extra-certificate` と `--certificate-audit` を対で繰り返して指定する。
対応する証明はエクスポート時にも独立検証される。

保存した最終 bank を使う再検証（実機GPUは不要）:

```powershell
python -B acceleration/verify_scores.py --candidates acceleration/results/20260916_final_bank/candidates.txt --cpu acceleration/results/20260916_final_bank/cpu.json --gpu acceleration/results/20260916_final_bank/gpu.json --out build/final_bank_recheck.json
```

この全件Python照合には数分かかる。入力と証明のハッシュも照合する。
最終チェックポイントと残り96件の index は同ディレクトリの `summary.json` にある。

次の有限標本を検査する場合（新しい出力先を指定する）:

```powershell
.venv/Scripts/python.exe -B acceleration/probe_walk.py --walk acceleration/results/20260916_walk_10000.json --scores acceleration/results/20260916_final_bank/gpu.json --manifest acceleration/results/20260916_final_bank/manifest.json --score-audit acceleration/results/20260916_final_bank/parity.json --walk-audit acceleration/results/20260916_walk_10000_audit.json --out build/next_probes --count 4 --seconds 30
```

次は追加証明をカット集合へ蓄積して候補を選別し、線形補完を通る配置を探す。
単純なランダム walk では廉価なカットを通過しやすく、今回の計算では
線形補完・双対証明抽出が主な計算時間になった。

参照したAPI資料: [NVIDIA CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)、
[SciPy linprog](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html)。
