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
| 4 | 24GB 機で `--lowvram --cpu-vae` が選ばれた | 閾値 `-lt 28000` に 24564MB が該当 | `--highvram --reserve-vram 2.0` に変更 | 修正済 |
| 5 | 使わない 14B 重みを 28GB 取得 | tier を見ずに全件取得 | `fetch_missing_assets.py` から 14B ブロックを削除 | 修正済 |
| 6 | パッチが無言で全滅 | `assert` 不一致で `write_text` まで到達せず | `re.subn` + `OK`/`MISS` 方式へ | 修正済 |
| 7 | `git clone` が無応答 | git プロトコルが 148 kB/s まで低下 | tarball 展開方式へ。ComfyUI / Manager / gallery とも実施済 | 回避済 |
| 8 | ComfyUI 本体の依存が入らない | `pip install -r requirements.txt` が `if [ ! -d .git ]` の内側にあり、tarball 先置きでブロックごとスキップされた | `if` の外へ移動 | **要修正** |
| 9 | `tail -30 /workspace/run_*.log` が `option used in invalid context` | glob が複数ファイルに展開された | `tail -n 40 "$(ls -t /workspace/logs/run_*.log | head -1)"` | 運用で回避 |
| 10 | `git commit` が空振り | ステージが空でも実行していた | `git diff --cached --quiet || git commit ...` | 運用で回避 |

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

## 起動前チェック

`bash scripts/preflight.sh` を通す。NG が1つでもあれば起動しない。
