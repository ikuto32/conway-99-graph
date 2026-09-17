# 取得と検証

## 2026-09-17以降のロック済み環境

新しいPythonワークフローはルートの `pyproject.toml` と `uv.lock` を使います。
過去の `.venv` と実験コマンドを変更せず、別の無視対象ディレクトリへ構築します。

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv sync --locked --python 3.12 --cache-dir .uv-cache-20260917
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/validate_claims.py --hashes available
uv run --locked --cache-dir .uv-cache-20260917 python -B -m unittest discover -s acceleration -p test_validate_claims.py -v
```

POSIXでは `export UV_PROJECT_ENVIRONMENT=build/research-venv` を設定します。
以下の既存pipコマンドと履歴は当時の再現資料として保持しています。
台帳CIはPUBLIC成果物だけをハッシュ照合し、LOCAL_ONLYや高価な数学的再実行の
省略を明示します。スキーマ検証やCI成功は数学的証明ではありません。

16候補の新しい独立整数検証は、別の未使用出力先を指定して実行できます。

```powershell
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260917_fresh_review.py --run acceleration/results/20260917_fresh_star_shortlist --out build/fresh-star-independent-replay.json
```

この検証器はLP生成コード・従来の整数検証器・数値ライブラリをimportしません。
元の全局所領域の完全性は、別実装の列挙監査と保存されたハッシュ付き入力に依存します。
完全なチェックポイント再開には、後述の大きなローカル成果物も必要です。

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
GitHub Actions では上記の検証、ルートと `acceleration/` の Python 構文チェック、
Rust 実装のビルドと保存済み入力を使う独立検証を実行します。CUDA の保存済み参照値との
比較も含みますが、CI に GPU や数値ソルバーは不要です。

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
2026-09-16 の Rust/CUDA 継続分では、大きな作業用ファイルを含む 92 件、
7,306,900,395 バイトをこの索引に追加しました。小さな生成ログ、ビルド済みバイナリ、
ローカル環境、`acceleration/results/**/work/` の作業用ファイルも公開対象外です。
厳密な再開チェックはこれらのハッシュも参照するため、Git の clone だけでは
停止時チェックポイントの参照ファイル一式は揃いません。
該当ファイルに依存する監査は、元のワークスペースから同じ相対パスへコピーするか、
対応する生成スクリプトと入力を確認して再生成する必要があります。ハッシュ一致も確認してください。
生成に必要な別の大きな入力も省略されている場合があるため、完全な再現には元の成果物が必要です。

整理前のコミットは元のワークスペースのローカルブランチ
`archive/pre-publish-20260916` に保存しています。この約 10 GB の履歴は push していません。
公開先が空だったため、大きなファイルを履歴に含めない公開用の初期コミットを作成しました。
元の履歴を参照するにはローカルで `git show archive/pre-publish-20260916:<path>` を使えます。

既存の研究記録は内容を整形し直していません。`.gitattributes` は研究ファイルの改行変換を
無効にし、ハッシュで参照されるバイト列を保持します。
