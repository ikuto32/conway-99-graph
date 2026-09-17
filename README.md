# Conway 99-graph research

強正則グラフ `srg(99,14,1,2)` の構成・非存在証明を調べたコード、実験記録、独立検証資料の研究アーカイブです。

**このプロジェクトでは、条件を満たす 99 頂点グラフも、一般の非存在証明も得られていません。** 限定条件下の排除、部分グラフ、緩和問題の解、探索のタイムアウトは、問題全体の解決を意味しません。

## 対象

求めるのは、次の条件をすべて満たす単純無向グラフです。

- 頂点数は 99、各頂点の次数は 14。
- 隣接する 2 頂点の共通隣接頂点はちょうど 1 個。
- 隣接しない 2 頂点の共通隣接頂点はちょうど 2 個。

隣接行列 `A` による同値な条件は `A² = 12I − A + 2J` です。定義と正規化の詳細は [CONJECTURE.md](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/CONJECTURE.md) にあります。

## 最初に読む資料

2026-09-17 に研究を再開しました。現在の主張台帳は
[CLAIMS.yaml](CLAIMS.yaml)、最新の完了済み検証は
[16候補の独立監査](docs/RESEARCH_20260917_FRESH_STAR.md) です。
16件すべての固定配置を排除しましたが、最良の強化LP値の改善はなく、
問題全体は未解決です。旧台帳・停止資料は履歴として保持しています。

| 資料 | 内容 |
| --- | --- |
| [研究資料の案内](docs/RESEARCH_MAP.md) | ディレクトリ、実験系列、検証資料の読み方 |
| [再現手順](docs/REPRODUCING.md) | 環境構築、軽量チェック、外部成果物の制約 |
| [Rust / CUDA による再開](acceleration/README.md) | 2026-09-16 の高速化、実測値、追加の厳密排除証明 |
| [再設定したゴールの進捗](docs/GOAL_20260916_PROGRESS.md) | 現在の目標、完全検証済みの有限排除、局所条件と誘導探索 |
| [マッチング全体の最適化と排除証明](docs/GOAL_20260916_MATCHING_MIP.md) | 1組全体の変更を扱うモデルと、独立した整数計算による条件付き排除 |
| [全マッチング探索の続報](docs/GOAL_20260916_WHOLE_MATCHING_SEARCH.md) | Rust完全候補生成、CUDA採点、独立検証済みの最良値改善 |
| [CUDAによる候補ごとの再最適化](docs/GOAL_20260916_CUDA_CP_SEARCH.md) | 最初のGPU反復最適化、独立検証付きで5.944366まで改善 |
| [GPU改良と異符号側への継続](docs/GOAL_20260916_CP_CONTINUATION.md) | GPU処理の高速化、異符号サイクル、数値ゼロ候補への到達 |
| [停止・再開記録](docs/STOP_20260916_FRESH_STAR.md) | ユーザー指示で実行終了。最新索引、128候補のGPU採点、未実施の次回作業 |
| [完成条件と強化LP](docs/GOAL_20260916_STAR_MARGINAL.md) | 固定配置の独立排除、新目的値5.374367への改善 |
| [強化モデルのCUDA実装](acceleration/STAR_PDHG_GPU.md) | CPUとの一致検査と、同一入力による中央値9.43倍の速度比較 |
| [再開時チェックポイント監査](docs/RESUME_20260916_CHECKPOINT.md) | 保存済み E72 と overlap 探索の状態 |
| [ACTIVE_RESEARCH.md](ACTIVE_RESEARCH.md) | 現在の継続地点と保存された研究履歴 |
| [既存研究アーカイブ](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/README.md) | Wave 205 までの詳細な研究記録 |
| [現在の主張台帳](CLAIMS.yaml) | 現プロジェクトの主張、厳密な範囲、独立検証、成果物の公開状態 |
| [台帳のスキーマと移行規則](docs/CLAIMS_SCHEMA.md) | 旧台帳を変更しない移行、CI、検証状態の意味 |
| [保存された外部台帳](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/CLAIMS.yaml) | 固定コミットの歴史資料。現在の再検証ではない |

`ACTIVE_RESEARCH.md` や [STOPPED_BY_USER.md](STOPPED_BY_USER.md) にある「実行中」、PID、停止・再開の記述は保存時点の履歴です。現在のプロセス状態を示すものではありません。文献調査の日付も各記録の時点を示し、現在の世界全体の研究状況についての主張ではありません。

## 取得と軽量チェック

Git と Python を用意し、以下をリポジトリのルートで実行します。環境構築例は Python 3.12 を使用します。

```powershell
git clone --recurse-submodules https://github.com/ikuto32/conway-99-graph.git
cd conway-99-graph
python -B validate_submission.py --self-test
python -B external_conway99_research/verification/check_srg.py external_conway99_research/verification/fixtures/rook-3x3.srg.json --vertices 9 --degree 4 --lambda 1 --mu 2
python -B -m unittest discover -s external_conway99_research/verification -p "test_check_srg.py" -v
```

この 3 つのチェックは Python 標準ライブラリで動作します。提出形式のパーサー、既知の 9 頂点グラフ、検証器の回帰テストを確認するもので、99 頂点グラフの存在・非存在を証明するものではありません。

探索用ライブラリが必要な場合は、任意の仮想環境を作成します。

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-research.txt
```

macOS / Linux では `python3.12 -m venv .venv` と `.venv/bin/python` を使用してください。個別実験には追加のソルバーや依存関係が必要な場合があります。詳細は [再現手順](docs/REPRODUCING.md) と各実験の README を参照してください。

## 公開範囲と保存方針

この公開版は、研究資料を読み、選択した検証を再現するための**部分アーカイブ**です。すべての探索・証明を単独で再実行できる完全な成果物一式ではありません。

- 既存スクリプトの相対パスと成果物のハッシュを保つため、`scratch_*` や研究アーカイブの配置を維持しています。
- 小さな CNF・証明を含む研究成果物を保存し、10 MiB を超える外部成果物は [local-artifacts.json](docs/local-artifacts.json) にパス・サイズ・SHA-256 を記録しています。列挙された外部成果物の実体はローカル保存で、通常の clone には含まれません。
- 依存ライブラリのキャッシュとビルド済みバイナリは公開対象から除外しています。既存の小さなアーカイブログは保存し、新たに生成される実行ログは Git の追跡対象から除外します。
- 停止時チェックポイントは、非公開のログ・バイナリ・作業用ファイルもハッシュで参照しています。完全な再開には元のワークスペースの保存資料も必要です。
- 整理前の履歴は元の作業環境のローカルブランチ `archive/pre-publish-20260916` に保存しています。このブランチは通常の clone では取得できません。

入力・証明ファイルが不足する検証は実行できません。成果物の欠落を、検証成功や不成立の根拠として扱わないでください。

## ライセンスと出典

`external_conway99_research/` のソフトウェアには [MIT License](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/LICENSE)、同アーカイブの文章・データには [CC BY 4.0](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/LICENSE-CONTENT.md) の記載があります。著作権表示と出典をそのまま保持しています。`tools/` などの第三者コードには各プロジェクトのライセンスが適用されます。これらの表示が、その他すべてのルート資料に一括で適用されるとは限りません。
