# 取得と検証

## 最小構成

Python 3.12 と Git を推奨します。提出形式の検証と下記の回帰テストは標準ライブラリだけで動きます。

```sh
git clone --recurse-submodules https://github.com/ikuto32/conway-99-graph.git
cd conway-99-graph
python -B validate_submission.py --self-test
python -B -m unittest discover -s external_conway99_research/verification -p test_check_srg.py -v
```

通常の clone 済みの場合は `git submodule update --init --recursive` を実行してください。
外部研究アーカイブと DRAT checker の上流 URL は `.gitmodules`、固定コミットは親リポジトリの Gitlink に記録しています。
GitHub Actions でも上記の検証とルートの Python 構文チェックを実行します。

候補の提出形式は、頂点番号 1〜99 を用いた `{u, v}` を 1 行ずつ、合計 693 行です。
候補が用意できた場合は次のコマンドで全頂点の次数と全頂点対の共通近傍数を検証できます。

```sh
python -B validate_submission.py path/to/candidate.txt
```

これは入力ファイルを読み取るだけの処理です。本リポジトリに有効な提出候補はありません。

## 任意のソルバー環境

探索や一部の監査スクリプトには追加パッケージが必要です。
`requirements-research.txt` は元のローカル環境で確認した主要パッケージのバージョンを記録しています。
推移的依存を含めた完全な環境ロックではありません。

```sh
python -m venv .venv
# POSIX: source .venv/bin/activate
# PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-research.txt
```

SciPy、CVXPY、pycosat を使う過去の実験には `requirements-optional.txt` を追加で利用してください。
これらの範囲指定は過去の環境との完全一致を保証しません。
一部のスクリプトは `.deps/`、`.ortools/` を import path に加えますが、通常の仮想環境に
同じライブラリをインストールすれば Python の標準の探索先も利用できます。
古いローカル DLL や Python のバージョンが異なるパッケージを混ぜないでください。

スクリプトは相対パスと `scratch_*` モジュール間の import を利用するため、リポジトリの
ルートから実行してください。過去の探索は時間・メモリを多く使う場合があり、監査スクリプトでも
既存の JSON を上書きするものがあります。再計算には別の clone と明示的な出力先を使い、
元の記録を保存してください。

## DRAT checker の Windows 修正

`tools/drat-trim` は上流ソースを固定したサブモジュールです。元の Windows ローカル環境の
互換修正は `tools/patches/drat-trim-windows.patch` に保存しています。
新しい clone のルートから、未適用のサブモジュールに対して一度だけ適用します。

```sh
git -C tools/drat-trim apply --check ../patches/drat-trim-windows.patch
git -C tools/drat-trim apply ../patches/drat-trim-windows.patch
```

Visual Studio の C コンパイラーが利用可能な Developer PowerShell では、ルートから次でビルドできます。

```powershell
cl /O2 /Fe:tools/drat-trim/drat-trim.exe tools/drat-trim/drat-trim.c
```

既存ワークスペースの修正は適用済みです。再適用せず、必要なら
`git -C tools/drat-trim apply --reverse --check ../patches/drat-trim-windows.patch` で確認してください。
Linux では上流の `make -C tools/drat-trim` を利用できます。既存の `scratch_check_drat.py`
は Windows の `drat-trim.exe` パスを想定しているため、Linux では checker を直接呼ぶか
明示的に実行ファイルのパスを変更してください。
checker の再ビルドではバイナリの SHA-256 が変わり得ます。新しい検証記録と過去の記録を区別してください。

## 公開範囲と大きな入力

公開用 `main` にはソース、研究ノート、10 MiB 以下の研究成果物を保持しています。
小さな CNF・証明・圧縮 JSON と既存の研究ログも、検証の参照関係を保つために含めています。
依存パッケージ、キャッシュ、実行ファイル、コンパイル結果、一時ファイル、ダウンロードした
論文の原稿は Git の管理対象から外しています。元のローカルファイルは削除していません。

10 MiB を超える研究成果物は [local-artifacts.json](local-artifacts.json) にパス、サイズ、
SHA-256 を記録しています。これらの本体は GitHub に含まれず、自動ダウンロード先もありません。
該当ファイルに依存する監査は、元のワークスペースから同じ相対パスへコピーするか、
対応する生成スクリプトと入力を確認して再生成する必要があります。ハッシュ一致も確認してください。
生成に必要な別の大きな入力も省略されている場合があるため、完全な再現には元の成果物が必要です。

整理前のコミットは元のワークスペースのローカルブランチ
`archive/pre-publish-20260916` に保存しています。この約 10 GB の履歴は push していません。
公開先が空だったため、大きなファイルを履歴に含めない公開用の初期コミットを作成しました。
元の履歴を参照するにはローカルで `git show archive/pre-publish-20260916:<path>` を使えます。

既存の研究記録は内容を整形し直していません。`.gitattributes` は研究ファイルの改行変換を
無効にし、ハッシュで参照されるバイト列を保持します。
