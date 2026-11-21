# pet-learning-kit

把一篇英文原文变成一套可读、可听、可练的学习包 —— 这个仓库是第一个成品：《哈利·波特与魔法石》第一章 *The Boy Who Lived*。

为中英对照阅读 + PET（B1）备考而做：逐段译文、CEFR 分级词汇注解、英音朗读、听力题、拼写默写、错题本，全部离线可用。

> ⚠️ **这是一个私有仓库**。仓库内的原文、译文与朗读音频版权归 J.K. Rowling 及出版方所有，仅供个人学习，请勿公开传播。详见 [NOTICE.md](NOTICE.md)。

---

## 内容

### 学习包（根目录 HTML）

| 页面 | 说明 |
|---|---|
| [`index.html`](index.html) | 入口页，四个页面的导览与使用顺序 |
| [`harry-potter-ch1-reader.html`](harry-potter-ch1-reader.html) | **中英对照朗读版**：书页式连续排版，107 段逐段朗读，235 个单词发音，文末 60% 空缺拼写默写 |
| [`harry-potter-ch1-study.html`](harry-potter-ch1-study.html) | **精读讲义**：235 个词条（音标 / CEFR 等级 / 释义 / 例句 / 记忆法）、PET 同义替换 45 组、语法 12 条、写作句型与范文、7 天阅读计划 |
| [`harry-potter-ch1-listening.html`](harry-potter-ch1-listening.html) | **听力练习册**：78 道听力任务 + 13 句听写，三档语速 |
| [`harry-potter-ch1-wrongbook.html`](harry-potter-ch1-wrongbook.html) | **错题本**：默写答错的词自动收集，一次一张卡片反复练 |

### 音频（`audio/`，369 个 mp3）

```
audio/full.mp3            整章 23:29
audio/01–13.mp3           13 个阅读单元
audio/para/001–107.mp3    逐段（朗读版点哪段读哪段）
audio/words/001–235.mp3   235 个词汇发音
audio/dict/01–13.mp3      听写句子
```

### 方法论（`skills/english-reading-kit/`）

整套流程被固化成一个可复用的 agent skill：抓取 → 清洗 → 分段 → 1:1 翻译 → 分级标注 → 考试对齐 → TTS 音频 → 书页式排版 → 练习与打包。

```
skills/english-reading-kit/
├── SKILL.md              触发条件 + 9 步流水线 + 7 条硬规则
├── references/           layout / audio / exam / practice / verify
└── scripts/              make_audio.py · check_pages.py
```

---

## 快速开始

```bash
git clone https://github.com/backyes/pet-learning-kit.git
cd pet-learning-kit

# 直接打开
open index.html

# 手机访问（推荐）：本目录起一个静态服务器，手机连同一 Wi-Fi
python3 -m http.server 8765
# 然后访问 http://<你的局域网IP>:8765/
```

**建议顺序**：朗读版盲读 → 听 0.75× → 回讲义查词 → 做听力题 → 拼写默写 → 错题本复习。

---

## 技术要点

- **排版**：书页式连续正文，译文降级为浅灰注脚，段落播放按钮放在页边（手机上隐藏，改用「点读」模式）。早期版本用卡片 + 独立按钮列，把正文切得很碎，已废弃。
- **音频**：macOS `say` + `ffmpeg` 生成，无需任何 API key。`Daniel`（en-GB）朗读，64 kbps 单声道，四种粒度便于逐句/逐词重听。
- **默写**：每个词遮住约 60% 字母（首尾必露），逐位报错（第几个字母、应为哪个、你写的是哪个）。
- **错题本**：`localStorage` 存 `hp1.wrong.v1`，答对一次消一格，清空即掌握；支持导出/导入。
- **零依赖**：所有页面是单文件 HTML + 相对路径音频，不需要构建、不需要联网。

---

## 检查

仓库自带两个脚本，提交前跑一遍：

```bash
python3 skills/english-reading-kit/scripts/check_pages.py --root . *.html
✓ index.html                    0 audio refs, 0 scripts
✓ harry-potter-ch1-reader.html  236 audio refs, 2 scripts
...
```

检查项：HTML 标签平衡、音频引用是否都存在、锚点是否有目标、内联 JS 是否可解析。

---

## 路线图

- [ ] 第二章（*The Vanishing Glass*）同款讲义
- [ ] 把工具链抽出来，支持任意 URL/PDF 输入
- [ ] 错题本按错误次数排序、支持“已掌握”归档
- [ ] 用公版文本（如 *Alice in Wonderland*）做一个可公开的示例

---

## 许可

- **代码与文档**（`skills/` 下的脚本、模板、本 README）：MIT，见 [LICENSE](LICENSE)。
- **原文、译文、朗读音频**：版权归 J.K. Rowling 及出版方所有，**不在 MIT 许可范围内**，仅供个人学习使用。
