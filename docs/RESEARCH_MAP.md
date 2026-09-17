# 研究資料の案内

現在の主張は [ルート台帳](../CLAIMS.yaml) を唯一の入口とします。
[2026-09-17の独立検証](RESEARCH_20260917_FRESH_STAR.md) と
[スキーマ・移行規則](CLAIMS_SCHEMA.md) を追加しました。
下記の外部台帳は固定コミットの履歴であり、新しい再検証として扱いません。

このリポジトリには、既存の研究パッケージと、その後のルート直下の実験・監査記録が共存しています。ファイル名の `scratch_` は研究用の命名であり、削除してよい一時ファイルという意味ではありません。

## 配置

| 場所 | 役割 |
| --- | --- |
| [ACTIVE_RESEARCH.md](../ACTIVE_RESEARCH.md) | 2026-09-05 付の継続記録。固定した部分問題の結果、反例となる緩和解、未解決条件を整理 |
| [STOPPED_BY_USER.md](../STOPPED_BY_USER.md) | 以前の停止時点の引き継ぎ記録 |
| [validate_submission.py](../validate_submission.py) | 1 始まりの `{u, v}` 形式の辺リストを検証する標準ライブラリの CLI |
| [external_conway99_research/](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/README.md) | Wave 205 までの研究パッケージ、主張台帳、独立検証資料 |
| ルートの `scratch_*.py` / `.rs` | 探索、計算、証明係数の生成、独立監査のスクリプト |
| ルートの `scratch_*.md` / `.json` | 計算の要約、制約、候補、失敗記録、検証結果、台帳 |
| `tools/` | 第三者の検証用ツール。サブモジュールは固定されたリビジョンを取得 |
| [local-artifacts.json](local-artifacts.json) | 公開版から除いた大きな外部成果物のサイズ・ハッシュの一覧 |

`ACTIVE_RESEARCH.md` の名前は保存された研究記録の名称です。記載された PID、実行中のワーカー、停止・再開の指示を、そのまま現在の実行状態と解釈しないでください。

## 既存研究アーカイブを読む順序

1. [CONJECTURE.md](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/CONJECTURE.md) で対象と記号を確認する。
2. [STATUS.yaml](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/STATUS.yaml) と [CLAIMS.yaml](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/CLAIMS.yaml) で、保存時点の研究状態と主張の範囲を確認する。
3. [STRUCTURE.md](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/STRUCTURE.md) でグラフが存在すると仮定した場合の構造的帰結を読む。
4. [REPRODUCING.md](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/REPRODUCING.md) と各実験の README で、入力、コマンド、証明・検証の境界を確認する。

アーカイブ内のディレクトリは次のように分かれています。

| ディレクトリ | 内容 |
| --- | --- |
| [code/](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/code/README.md) | 構成探索、SAT 符号化、構造解析 |
| [attempts/](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/attempts/README.md) | 各 Wave の探索・証明案と失敗記録 |
| [verification/](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/verification/README.md) | 独立検証器、校正用の既知のグラフ、監査記録 |
| [candidates/](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/candidates/README.md) | 候補・校正用の証明書。名称だけで対象グラフと判定しない |
| [formal/](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/formal/README.md) | 形式的な証明・証明器の校正資料 |
| [agents/](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/agents/README.md) | 担当別の導出・レビュー・文献調査 |
| [logs/](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/logs/README.md) | 保存対象の実行概要とマニフェスト |

## ルートの実験系列

系列には重なりがあり、番号は数学的な強さや完全性を保証しません。まず同じ接頭辞の `.md` を読み、続いて JSON のスコープ・入力ハッシュ・検証結果を確認してください。

| 接頭辞 | 主な対象 |
| --- | --- |
| `scratch_general_*` | 全体の構成探索、候補、次数・共通隣接数の改善 |
| `scratch_canonical_*` / `scratch_fibre_*` | 根付き正規化、ファイバー、制限した SAT 問題 |
| `scratch_e7*` / `scratch_root_e7*` | 特定の層・ケースの探索と被覆台帳 |
| `scratch_theory_*` | 構造的な必要条件、厳密算術、緩和問題の対照例 |
| `scratch_resume_*` | 再開後の部分隣接構造、圧縮行列、E72 の監査 |
| `scratch_next_*` | 重なり配置の容量矛盾、共分散、再利用する不等式群 |
| `scratch_follow_*` | その後の局所変更・候補生成に関する記録 |

具体的な入り口として、[近傍の独立監査](../scratch_resume_neighborhood_audit.md)、[E72 の保存状態](../scratch_resume_e72_status.md)、[重なり配置の容量矛盾](../scratch_next_overlap_summary.md)、[代替配置の監査結果](../scratch_next_overlap_alternatives_summary.md) があります。いずれも記載された制限条件の範囲で読む必要があります。

## 結果の読み方

- `CANDIDATE` は検証済みの解ではありません。部分グラフや緩和問題の解が含まれます。
- `UNKNOWN`、タイムアウト、候補未発見は、非存在の証明ではありません。
- `UNSAT` は符号化した制約集合についての結果です。問題全体を覆うことと、必要な証明の独立検証は別に確認します。
- `VERIFIED` や監査の `PASS` は、その資料が宣言した範囲の検証です。条件付きの主張を一般の非存在証明へ拡張するものではありません。

研究プロトコルは [AGENTS.md](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/AGENTS.md)、残る証明義務は [OBLIGATIONS.yaml](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/OBLIGATIONS.yaml) に記録されています。本プロジェクトに、検証済みの `srg(99,14,1,2)` または一般の非存在証明はありません。

## パスとバイト列を維持する理由

多くのスクリプトはルートを作業ディレクトリとし、相対パスで別のスクリプトや JSON を読み込みます。既存ファイルを分類用の新ディレクトリへ移動すると、参照・再現コマンド・ハッシュ台帳が壊れます。このため、公開整理は案内資料と Git の保存範囲の整理を中心としています。

また、成果物の一部は改行を含むバイト列全体が SHA-256 で固定されています。[既存の .gitattributes](https://github.com/YesterdaysLemon/conway-99-research/blob/85e705cc6c2a14d123120c93a847e30aaab1789e/.gitattributes) はその保護規則を含みます。JSON の再整形、改行の一括変換、ログの書き換えでも一致しなくなるため、検証対象のファイルを一括整形しないでください。

監査スクリプト自身が既存の JSON レポートを上書きする場合もあります。実行前に出力先と必要入力を確認してください。手軽な動作確認には、[ルートの再現手順](REPRODUCING.md) の軽量チェックを使用できます。大きな外部成果物は通常の clone に含まれず、そのハッシュ一覧だけからデータを復元することはできません。
