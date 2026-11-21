# 结构化数据

从 4 个 HTML 页面反解出来的原始数据，方便你二次加工（做词卡、导入 Anki、重新排版、接别的 TTS）。

## 文件

| 文件 | 内容 |
|---|---|
| `chapter.json` | 全量结构：13 个单元 → 每单元的段落（英/中/音频）与词条（音标/词性/等级/释义/例句/记忆法/音频） |
| `paragraphs.csv` | 107 行，`id,section,audio,en,zh` |
| `vocabulary.csv` | 235 行，`id,word,ipa,pos,level,meaning,example,memory,audio` |
| `audio_manifest.csv` | 369 个音频的路径与字节数 |

## 字段说明

- `id` — 三位数字，**与音频文件名一一对应**：段落 `001` ↔ `audio/para/001.mp3`，词条 `001` ↔ `audio/words/001.mp3`
- `section` — 1–13，对应 13 个阅读单元
- `level` — `a2` / `b1` / `b2` / `c1` / `sy`（sy = 熟词僻义）
- `en_html` — 段落原文，保留了生词高亮的 `<b>` 标签（仅 `chapter.json`）
- `en` — 去掉标签的纯文本，适合送进 TTS 或做检索
- `zh` — 对应的中文译文，与 `en` **严格 1:1**

## 一致性

`paragraphs.csv` 107 行 = 107 个 `audio/para/*.mp3`；
`vocabulary.csv` 235 行 = 235 个 `audio/words/*.mp3`；
13 个 `section` 各对应一个 `audio/NN.mp3`。

校验：

```bash
python3 - <<'PY'
import json
d=json.load(open('chapter.json'))
p=sum(len(s['paragraphs']) for s in d); v=sum(len(s['vocabulary']) for s in d)
print('sections',len(d),'paras',p,'words',v)
PY
```
