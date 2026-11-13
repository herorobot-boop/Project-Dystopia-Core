# NG 台帳 / 再発防止

Project Dystopia: Genesis Ignition Omega の起動で実際に発生した障害と、
それぞれの恒久対策を記録する。**起動前に必ず読む。**

## 鉄則

1. **実行中に `.sh` を書き換えない。** bash は逐次読み込みするため、
   書き換えると読み込み位置がずれて後段が壊れる。変更は必ず停止後。
2. **GitHub の `git clone` を使わない。** この Pod の git プロトコルは
   148 kB/s まで落ち、クローンがハングしたように見える。
   `https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/<branch>` を
   `curl -fL` で落として `tar -xzf ... --strip-components=1` で展開する。
3. **HuggingFace は速い（342 MiB/s 実測）。** モデル取得は壁にならない。
   GitHub だけが遅い。
4. **モデル取得中は原則中断しない。** 中断コストが高い。
   中断が安いのは apt とクローンだけ。
5. **ログは `/workspace/logs/` に置く。** リポジトリ直下に置くと
   `git status` が汚れる。
6. **`assert` でパッチを書かない。** 1つ外れた瞬間に残り全部が
   未適用のまま終わる。`OK`/`MISS` を出す方式にする。

## 発生済みの障害

| # | 事象 | 原因 | 対策 | 状態 |
|---|---|---|---|---|
| 1 | `apt` が全パッケージ名を正規表現として総当たりし、数百行の `Note, selecting` を吐いた | `c2patool` が jammy に存在せず、apt が正規表現モードにフォールバックして他の引数まで巻き込んだ | apt から外し `install_c2patool_soft()` で GitHub Releases から取得 | 修正済 |
| 2 | `set -e` により Step 1 で即死 | 上記1の行に `|| true` が無かった | パッケージを分離。`c2patool` は関数化し失敗時 `WARN` で続行 | 修正済 |
| 3 | `line 26: uo: command not found` で即終了 | パッチのアンカー `set -e` が `set -euo pipefail` の先頭にヒットし、`uo pipefail` が残置された | `set -uo pipefail` に修復。preflight に `set -euo 健在` 検査を追加 | 修正済 |
| 4 | 24GB 機で `--lowvram --cpu-vae` が選ばれた | 閾値 `-lt 28000` に 24564MB が該当 | `--normalvram` に変更。`--reserve-vram` はこのビルドに無いので付けない | 修正済 |
| 5 | 使わない 14B 重みを 28GB 取得 | tier を見ずに全件取得 | `fetch_missing_assets.py` から 14B ブロックを削除 | 修正済 |
| 6 | パッチが無言で全滅 | `assert` 不一致で `write_text` まで到達せず | `re.subn` + `OK`/`MISS` 方式へ | 修正済 |
| 7 | `git clone` が無応答 | git プロトコルが 148 kB/s まで低下 | tarball 展開方式へ。ComfyUI / Manager / gallery とも実施済 | 回避済 |
| 8 | ComfyUI 本体の依存が入らない | `pip install -r requirements.txt` が `if [ ! -d .git ]` の内側にあり、tarball 先置きでブロックごとスキップされた | `if` の外へ移動 | 修正済 |
| 9 | `tail -30 /workspace/run_*.log` が壊れる | glob が複数ファイルに展開された | `tail -n 40 $(ls -t /workspace/logs/run_*.log \| head -1)` | 運用で回避 |
| 10 | `git commit` が空振り | ステージが空でも実行していた | `git diff --cached --quiet \|\| git commit ...` | 運用で回避 |
| 11 | preflight の `import comfy` が常に NG | `comfy` はパッケージ未 install で cwd 依存 | `cd /workspace/ComfyUI` を挟む | 修正済 |
| 12 | 素の状態から起動すると再びクローンで停止 | 手動回避がスクリプトに反映されていなかった | `fetch_repo()` で tarball 取得。失敗時のみ git clone | 修正済 |
| 13 | Civitai の 401 HTML が `.safetensors` として保存される | `raise_for_status` せず本文を書いていた | ステータス検査を追加 | 修正済 |
| 14 | `extra_model_paths.yaml` が壊れると ComfyUI が起動しない | f-string の三重クォート依存 | 明示文字列＋`yaml.safe_load` 検証 | 修正済 |
| 15 | 停止中の `git clone` を `kill %1` して ComfyUI ツリーが半壊 | 既存ディレクトリへの clone が中断し、custom_nodes が消えた | tarball 展開に統一。退避してから作り直す | 修正済 |
| 16 | 復旧後に genesis が Step 3 で即死 | ガードが `.git` 判定。tarball 復旧した木には `.git` が無く、非空ディレクトリへの clone が失敗 | `fetch_repo()` で中身の有無を判定し tarball 展開 | 修正済 |
| 17 | preflight の追記が無言で空振り | アンカー `if [ $fail -ne 0 ]` が実物と不一致。`replace` の戻りを見ていなかった | アンカー候補を順試しし、不一致なら明示的に MISS を出す | 修正済 |
| 18 | genesis への関数挿入が空振り | アンカー `^set -euo pipefail` が実物と不一致 | shebang 直後を挿入点にする | 修正済 |
| 19 | preflight の `chk` 行が全部 NG、`[: missing ]` | `chk` は第2引数を評価するのに引数を括っていなかった | `chk "ラベル" "コマンド"` で必ず括る。`py_compile` で入れ子引用符を回避 | 修正済 |
| 20 | `chk` の `cd` が後続チェックに漏れる | `eval` を同一シェルで実行していた | `( eval "$2" )` で subshell 化、パスは絶対化 | 修正済 |
| 21 | 退避ディレクトリに Impact-Pack を置き去り | `mv` でツリーごと退避したため | 退避先から `cp -a` で復元 | 修正済 |
| 22 | Civitai 取得が `MissingSchema: '/model-versions/1997816'` | API の `downloadUrl` が空で Web パスにフォールバックしていた | `/api/download/models/{id}` を直接叩く。Content-Type も検査 | 修正済 |
| 23 | Civitai が API 200 でもダウンロード 403 | 対象モデルが早期アクセス扱いでアカウント権限外 | HF の `Comfy-Org/flux1-dev` fp8 へフォールバック | 回避策実装 |
| 24 | `fetch_hf` の引数順を誤り `IsADirectoryError` | シグネチャは `(repo, dest_dir, filename)` | 順序を修正。絶対パスを右辺に置かない | 修正済 |
| 25 | Civitai 失敗でスクリプト全体が停止 | 例外を投げていた | 警告して `return False`。呼び出し側で代替判定 | 修正済 |
| 26 | `fetch_hf` に repo 名を渡して aria2c が URI エラー | 第1引数はフルURL | `resolve/main` 形式のURLを渡す | 修正済 |
| 27 | `qwen_image_edit_2509_fp8.safetensors` が 404 | Comfy-Org の実リポジトリは `_ComfyUI` 付きで、実体は `split_files/` 配下 | HF API でファイル一覧を引いて実パスを解決。推測でURLを書かない | 修正済 |
| 28 | Qwen-Image-Edit のテキストエンコーダと VAE が未取得 | スクリプトに項目自体が無かった | `qwen_2.5_vl_7b` と `qwen_image_vae` を追加 | 修正済 |
| 29 | Civitai が全モデルで 403（API 200 でもDL不可） | 早期アクセス扱いでアカウント権限外。トークンでは回避不能 | HF の `Comfy-Org/flux1-dev` へフォールバック。LoRA はブラウザ手動 | 回避策実装 |
| 30 | Civitai DL が 403 | UA/Referer 無し、または早期アクセス | UA/Referer/トークンを付与。早期アクセスは HF ミラーへ | 回避策実装 |
| 31 | Civitai DL が 404 | `754298` はモデルIDでバージョンIDではなかった | `/api/v1/models/{id}` で versionId を解決してから叩く | 修正済 |
| 32 | DL したファイルが HTML エラー本文 | 検証せず `.safetensors` として保存していた | 先頭が `<` `{` なら破棄。1MB 未満も破棄 | 修正済 |
| 33 | 取得名と参照名が不一致（qwen edit / wan5b / wan vae） | 取得できても必ず失敗 | 保存名を参照側に合わせる | 修正済 |
| 34 | `MS_Nude_Style_Flux_V2` 未取得なのに無条件ロード | 静止画が全滅 | 存在時のみ LoRA を挿す | 修正済 |
| 35 | `--nude` が float なのに menu がフラグで渡す | argparse エラー | `--nude 0.9` に | 修正済 |
| 36 | `CIVITAI_API_TOKEN` を読むが投入は `CIVITAI_TOKEN` | 認証が効かない | 両方読む | 修正済 |
| 37 | menu 6 が未取得の 14B を呼ぶ | 動画の本番が失敗 | 5B 121フレームに変更 | 修正済 |
| 38 | `remove-clothes.safetensors` に Flux 用 LoRA を割当 | Qwen に Flux LoRA は効かない | Qwen-Edit-2509 用ミラーへ差し替え | 修正済 |
| 39 | `run_qwen_image_edit.py` に旧ノード4種と `qwen_vl` | 編集が必ず `node not found` | `UNETLoader`/`CLIPLoader(qwen_image)`/`VAELoader` へ | 修正済 |
| 40 | 同ファイルが `EmptySD3LatentImage`＋denoise 0.85 | 元画像の構図が壊れる | `VAEEncode`＋denoise 1.0 へ | 修正済 |
| 41 | `run_wan_subtle_motion.py` が 14B 用 `WanImageToVideo` と `wan_2.1_vae` / 14B gguf | 5B で latent 不一致、VAE 不在 | `Wan22ImageToVideoLatent`／`wan2.2_vae`／5B safetensors へ | 修正済 |
| 42 | `run_fluxed_up_t2i.py` にトリガーワードが無い | LoRA が発火しない | 先頭に `aidmaNSFWunlock` を付与 | 修正済 |
| 43 | `start_smart_gallery.sh` がポート8000（LLMと衝突）・参照先 `ComfyUI/output` | 起動しても見えない | 8080・`out/raw`・起動判定つきに全面改稿 | 修正済 |
| 44 | メニューからギャラリーを呼べない | 毎回手で叩く必要 | 10番を追加 | 修正済 |
| 45 | Discord通知がどこからも呼ばれない | スマホに届かない | 動画生成直後に呼ぶ | 修正済 |
| 46 | fluxed_up に別モデル（DAC_Fluxed_Style）を割当 | 土台がスタイル寄り | 正規の Fluxed Up 13.1（847101/v3273057/f3157597）へ | 修正済 |
| 47 | Wan リポジトリ名が `Wan_2.2_ComfyUI_Repackaged` | 404 | 実名 `Comfy-Org/Wan-2.2` へ | 修正済 |
| 48 | 編集UNETが 2509 固定 | 2511 の2人一貫性を使えない | 存在する方を自動選択 | 修正済 |
| 49 | ギャラリーが外部リポジトリ名の推測に依存 | 名前が違うと起動不可 | 自前の `gallery_server.py` に置換。外部依存ゼロ | 修正済 |
| 50 | 通知パスが `COMFY_OUT` だが `stash` が先に移動済み | 通知が空振り | `C.RAW` を渡す。`moved` を経由 | 修正済 |
| 51 | `audit_urls.py` が `.sh` を見ない | シェル内URLが監査漏れ | `*.sh` も走査。codeload は除外 | 修正済 |
| 52 | Pod専用コマンドが会話に散在 | 覚えられない | `docs/POD_ONLY.md` に集約 | 修正済 |

## 起動前チェック

`bash scripts/preflight.sh` を通す。NG が1つでもあれば起動しない。
