# 取得と検証

## Two-coordinate exact proof: isolated public replay

The frozen independent checker reproduced `469399553/1048576 > 0` using only
Git-bound inputs from public commit `7c5e2bb59580fdae1c0a0eb9beb2513a41ecdad8`.
This repeats that checker; it is not a new derivation or a general nonexistence
proof. All 285 required Git blobs were checked. The earlier commit omitted a
required solver log; that failed availability check remains preserved, and
the exact log is included in this newer commit.

From the repository root, with the locked environment installed, use fresh
destination/output paths:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/prepare_two_coordinate_public_worktree.py --commit 7c5e2bb59580fdae1c0a0eb9beb2513a41ecdad8 --destination build/two-proof-replay --report build/two-proof-extraction.json
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/replay_two_coordinate_moment_checker.py --root build/two-proof-replay --commit 7c5e2bb59580fdae1c0a0eb9beb2513a41ecdad8 --out build/two-proof-check.json --receipt build/two-proof-receipt.json
```

The extractor creates a real detached worktree and verifies exact Git bytes.
The wrapper redirects only the frozen checker's report path, confines research
reads to the checked input closure, and refuses existing output paths. See the
[saved replay receipt](../acceleration/results/20260917_two_coordinate_public_replay/replay_receipt.json)
and [original preparation failure](../acceleration/results/20260917_independent_review/two_public_git_closure_preparation.json).

## Exact one-coordinate certificate: isolated public replay

The conditional family certificate published at commit
`d4f4a926ad075afa7309fb17c776e0de2c18bf7a` was replayed from isolated Git files.
The exact integer result is `590533056/1048576 > 0`. This is repeated execution
of the independent checker, not a new mathematical review. It excludes only
the recorded162-fixed-edge family.

From the research branch containing the replay wrapper, create a fresh detached
worktree at the proof commit and choose new output filenames:

```powershell
git worktree add --detach build/moment-proof-replay d4f4a926ad075afa7309fb17c776e0de2c18bf7a
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python acceleration/replay_positive_moment_checker_v2.py --root build/moment-proof-replay --commit d4f4a926ad075afa7309fb17c776e0de2c18bf7a --out build/moment-proof-check.json --receipt build/moment-proof-receipt.json
```

The wrapper checks the isolated Git top-level and commit, verifies every frozen
runtime input against its committed bytes, and redirects only the checker's
hard-coded report output. Original proof artifacts are not overwritten. It
permits trusted interpreter packages but rejects other data fallback. All115
runtime/seed files were checked and used in the recorded successful replay;
no large LOCAL_ONLY ranking inputs are required for this exact certificate.
The full-domain and encoding reviews remain explicit proof dependencies; the
replay checks their recorded input hashes rather than rerunning those entire
independent derivations.

Recorded evidence: `acceleration/results/20260917_moment_public_replay/`.
The first partial checkout omitted `.gitattributes` and was rejected for nine
newline-only byte differences before arithmetic ran. A later wrapper attempt
rejected Windows' exact-string representation of the Git provenance command;
that failure and old wrapper were retained. The corrected wrapper accepts only
that exact command in list or Windows string form, with corruption controls.
The successful receipt is `replay_receipt_v2.json`; these engineering failures
are not refutations of the mathematical certificate. For selective checkouts,
checkout `.gitattributes` first and disable automatic newline conversion.


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

## 公開コミットだけを使う16候補の隔離再実行

上の直接コマンドには移植上の制約があります。履歴成果物の一部が
`C:/Users/ikuto/projects/conway-99-graph` の絶対パスを入力ハッシュに記録しているため、
別の場所へのcloneではそのまま実行できません。隔離ガード付きの直接実行でも、この
元ワークスペースへの読み取り要求を拒否しました。これはパスの問題であり、数学的反証ではありません。

公開済みコミット `3daebfb05d39aa31afea6fdbb6b80d6b108f1262` から必要なGit blobだけを
抽出し、明示的なパス移送ラッパーで再実行できます。次はリポジトリのルートで実行します。
出力先には未使用の名前を指定してください。既存の監査結果は上書きしません。

```powershell
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/audit_public_replay.py --commit 3daebfb05d39aa31afea6fdbb6b80d6b108f1262 --destination build/public-replay-new --out acceleration/results/public-replay-new
uv run --locked --cache-dir .uv-cache-20260917 python -I acceleration/replay_published_checker.py --root build/public-replay-new --original-root C:/Users/ikuto/projects/conway-99-graph --checker acceleration/audit_20260917_fresh_review.py --relocate --run acceleration/results/20260917_fresh_star_shortlist --report acceleration/results/public-replay-new/fresh16-wrapper.json --checker-out acceleration/results/public-replay-new/fresh16.json
uv run --locked --cache-dir .uv-cache-20260917 python -I acceleration/replay_published_checker.py --root build/public-replay-new --original-root C:/Users/ikuto/projects/conway-99-graph --checker acceleration/audit_20260917_triangle_matching.py --relocate --controls-only --report acceleration/results/public-replay-new/triangle-controls.json --checker-out acceleration/results/public-replay-new/triangle-unused.json
```

ラッパーは上記の元プロジェクトルートだけを抽出先へ移し、成果物のバイト列と数学的検証関数は
変更しません。抽出先・明示した出力先・Python実行環境以外からのファイル読み取りを拒否し、
読み取った入力のSHA-256を記録します。6件のパス移送対照は、正常な移送とパス越境、
別ルート、似た接頭辞の拒否を検査します。ローカルの未公開キャッシュへフォールバックしません。

実行記録では16件すべての厳密有理数チェックが成功し、保存済みの16結果、正常対照1件、
破損対照6件と一致しました。所要時間はこの実行で約57.42秒です。これは既存の独立検証器の
**反復実行**であり、新たな独立数学的導出ではありません。元の全局所領域の列挙完全性は
ハッシュ付き監査に依存し、この再実行では全領域を再列挙していません。

実行時入力の照合対象はfresh16が129パス、baselineが17パス、triangleが99パスです。
これらは重複する集合なので合算しません。関連する環境・入力一覧を含む抽出集合は230パス、
67,052,947バイトで、必要な実行時入力に欠落やハッシュ不一致はありませんでした。
triangleでは入力一覧のハッシュ照合と6件の較正対照だけを実行し、約7,300万部分集合の
完全な数学的監査は再実行していません。baselineの完全な行列監査もこの隔離監査では未実行です。
過去のGPU探索などを含むすべての生成履歴の再現可能性や、新規ネットワークcloneは検証対象外です。

正確な実行済みコマンド、作業ディレクトリ、ソース・出力ハッシュ、失敗した直接実行と
抽出の資源上限到達は、[隔離再実行監査](../acceleration/results/20260917_public_replay/PUBLIC_REPLAY_AUDIT.md)
と[監査receipt](../acceleration/results/20260917_public_replay/replay_receipt.json)を参照してください。

## 第2波の圧縮された大きな入力を復元する

`20260917_same_star_round` の次の3入力には、元バイト列を復元できるgzip同梱物があります。
元JSONやテキストを再整形せず、再実行の前に以下で復元・照合してください。

```powershell
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/restore_compressed_artifacts.py acceleration/results/20260917_same_star_round/compressed_artifacts.json
```

対象は `family/all.json`、`search/coarse_gpu.json`、`search/coarse_input.txt` の3ファイルです。
[圧縮manifest](../acceleration/results/20260917_same_star_round/compressed_artifacts.json)が
圧縮ファイルと復元後のSHA-256・サイズを固定します。圧縮サイズは合計8,212,748バイト、
復元サイズは合計232,062,143バイトです。復元器は圧縮SHA-256、復元後のサイズとSHA-256を
確認してから保存します。既存ファイルが同一なら保持し、異なるバイト列なら上書きせず失敗します。
最大の元ファイルは124,683,908バイトで、復元器はそのバイト列をメモリ上に展開します。

別実装のストリーミングzlib監査でも3件を新しい隔離先へ復元し、元ファイルを参照・上書きせずに
manifestのサイズとSHA-256を確認しました。正常対照1件と、CRC破損・末尾切断・誤ハッシュ・
誤サイズ・余分な末尾・危険なパスを含む拒否対照7件が期待どおりに動作しました。
監査は復元器をimport・実行せず、復元器のソースも別に確認しています。ただし基盤のzlibと
SHA-256実装は共有します。これは厳密なバイト復元の工学的確認であり、数学的主張の検証ではありません。

```powershell
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/audit_compressed_artifacts.py acceleration/results/20260917_same_star_round/compressed_artifacts.json --destination build/compressed-independent-new --out acceleration/results/compressed-independent-new.json
```

この独立監査も未使用の出力先を指定してください。
[実行済み監査receipt](../acceleration/results/20260917_public_replay/compressed_recovery_audit.json)に
正確なコマンド、Python/zlibのバージョン、全入出力ハッシュ、ソース確認結果を保存しています。
この3件のgzip復元は、後述する他の大きなローカル成果物の公開・再現可能性を意味しません。

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
# User stop on 2026-09-17

Research is paused by explicit user instruction. Read
[the latest stop/restart record](STOP_20260917_SIX_COORDINATE.md) before using
any historical launch command below. Documentation maintenance or validation
does not authorize restarting a stopped search. The latest frozen stop
checkpoint is `acceleration/results/20260917_user_requested_stop.json`.
