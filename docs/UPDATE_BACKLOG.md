# アップデート対応リスト

思い付いた改善をここに積む。実装は計画が安定してから。

## 保留中

| # | 案件 | 条件 | 難度 |
|---|---|---|---|
| 1 | 4人以上の群衆を1枚で | Qwen-Imageで5人以上が安定するLoRA or 上位モデルが出たら | 高 |
| 2 | 720p動画を常用 | Wan 14B GGUF Q5 + ComfyUI-GGUF 導入。VRAM 16GB級で720p可の報告あり | 中 |
| 3 | 動画の拡大 | 生成後にReal-ESRGAN等で拡大。フレーム数分の処理時間 | 中 |
| 4 | 参照画像を10枚投入 | FLUX.2 Klein 9B の multi-reference。NSFW実績が薄いので検証要 | 高 |
| 5 | ネットワークボリューム | 3回連続で起動成功したら導入判断。月7ドル前後 | 低 |
| 6 | Civitai直取得 | トークン実値設定 + civitai.red 対応 | 低 |
| 7 | 表情4型の自動配分 | roll_cast の表情をプロンプトへ自動注入 | 低 |
| 8 | 手のYOLO補正 | Impact-Pack + SAM2。手だけdenoise 0.45 | 中 |

## 完了済み

- 2人被写体 → compose（Qwen Edit 多参照）
- 動きの小ささ → wan14b_i2v（--motion）
- 群衆 → gen_crowd（Qwen-Image）
- 認証 → 全HF公開・トークン不要
