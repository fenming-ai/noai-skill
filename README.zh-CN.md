# noai-skill

[English](README.md) · [简体中文](README.zh-CN.md)

**去掉模板腔，保住原文的声音。**

这是一个以中文为主的编辑 Skill，供能够读取本地文件的 AI 助手使用。先识别当前文字的语感，再判断哪里值得改；改后同时核对信息有没有丢、事实有没有多、声音有没有变。

**暗号：** `noai：文本或文件路径` 直接去味；`noai 检查：材料` 只检查不改。只说 `noai` 且没有明确材料时，先问要处理什么。

## 它解决什么问题

- 不把所有文章改成同一种口语腔：先识别原文视角、温度、节奏与保护点。
- 不按句式直接删：检测信号只是候选，改写必须有收益。
- 不为自然度编经历：数字、限定、因果、立场和独立建议都要回查。
- 不只教“怎么改”：正反示例也说明哪些表达应当保留。
- 不覆盖源文件：文件改写另存新版，并生成可读的 HTML 对照。

文字之外，也提供技术文档、界面文案、架构图标签、代码注释的审阅方向；不会为去味擅自改动代码行为或技术事实。

## 开始使用

```bash
git clone https://github.com/fenming-ai/noai-skill.git
cd noai-skill
```

让助手读取克隆目录里的 `SKILL.md`，再交给它待处理文字。保留完整目录，入口会按需加载参考和示例。不需要安装整套写作团队，也不需要其他私人仓库。本包不安装模型、不调用模型 API。

只检查：

```text
读取 noai-skill/SKILL.md，检查 article.md 的 AI 味。
告诉我具体位置、修改理由和保留理由，先不要修改文件。
```

直接改：

```text
读取 noai-skill/SKILL.md，给 article.md 去 AI 味。
保留事实、条件和原文语气，不增加经历。源文件不动，另存改后稿和 HTML 对照。
```

路径按助手的工作目录调整。主要规则和样例为中文，英文改写效果尚未单独评测。

## 流程与交付

读取原文 → 定语感与修改边界 → 找候选问题 → 裁决改不改 → 回查信息与语感。

检测模式给语感卡和报告，允许零问题。文件改写模式产出 `<文件名>-noai.<扩展名>` 与 `<文件名>-noai-diff.html`；对照样式来自包内 `assets/diff-template.html`。已有语感契约是可选输入，没有也能工作。本包没有自动上传反馈的代码；私人反馈写入共享技能目录前需获得许可。

## 可选脚本与测试

仅运行脚本和测试时需要 Python 3.10+；不需要第三方 Python 包。

```bash
python3 tests/check_text.py examples/input.md
python3 tests/check_text.py examples/input.md --strict
python3 -m unittest discover -s tests -t .
```

脚本只检查部分词语、标点与引号用法，不负责改写，也不能判断作者是不是 AI。普通报告模式完成扫描返回 0，即使发现候选；严格模式有命中返回 1。输入缺失或不可读、规则文件缺失或格式错误返回 1。空文本允许通过。HTML 应先提取正文再扫描。

## 边界

不承诺通过 AI 检测，不公布未经验证的有效率。效果依赖执行模型和原始材料。中立、整齐、专业术语和有效比喻都可能是正确表达，不能为了“人味”硬改。

本地测试覆盖扫描器行为和部分规则约定。教学样例与小规模冷读不代表跨模型稳定性。本包不包含私人会话和外部评测数据集。见[证据边界](references/evidence.md)。


## 中文长文专项评测

6 篇新创作的模拟长文，每篇 1,399—1,632 汉字；6 个 Skill 加普通改写基线，共 **42 份改稿、84 份评分记录**。生成与两组盲评均配置为 **gpt-6-astra / medium**。每组由 3 个独立评审上下文完成，每份改稿获得两组各一次评分。

| 方案 | 均分 / 100 |
|---|---:|
| noai | 100.00 |
| shuorenhua（说人话） | 99.27 |
| Humanizer | 98.75 |
| sepia | 98.33 |
| 普通改写（无 Skill） | 98.02 |
| Humanizer-zh | 97.50 |
| Stop Slop | 96.35 |

noai 本轮均分最高，表现更体现为保住原文声音、避免过度改写。**100 分是当前量表满分，不代表完美：**84 份评分中有 48 份满分。原稿相对成熟，未对不改动的原文另行评分，样本创作、生成和评审也使用同一模型配置。因此，这次六例、单次生成的结果不能证明净去味提升、普遍优势或统计显著性。

[完整报告与方法](docs/evaluations/long-form/README.md) · [下载全文 HTML 对照](docs/evaluations/long-form/comparison.html) · [输入、输出和逐项评分证据](docs/evaluations/long-form/results.json) · [复算成绩](docs/evaluations/long-form/recompute.py)

报告公开全部原创模拟原文及七个方案的改稿；第三方规则包仅列来源、版本与哈希，不重新分发。此前的不同篇幅评测继续保留如下。

## 中文改写对比评测

6 个开发样本、5 个方案，每例每方案生成一次。生成与独立匿名模型评审均配置为 **gpt-6-astra / medium**。

| 排名 | 方案 | 均分 / 100 | 严重错误例数 |
|---:|---|---:|---:|
| 1 | Humanizer | 96.25 | 0/6 |
| 1 | Stop Slop | 96.25 | 0/6 |
| 3 | 普通改写（无 Skill） | 95.83 | 0/6 |
| 3 | noai | 95.83 | 0/6 |
| 5 | Humanizer-zh | 94.17 | 0/6 |

noai 在本轮与普通改写同分。小样本分差不证明显著优势，也不代表跨模型稳定性。

[评测报告与测试方法](docs/evaluations/chinese-rewrite/README.md) · [下载 HTML 报告](docs/evaluations/chinese-rewrite/comparison.html) · [结果数据](docs/evaluations/chinese-rewrite/results.json)

样本全文再分发许可尚未确认，公开报告提供成绩、来源定位与哈希，不分发原文和改写全文。

## 许可与来源

本包原创部分采用 MIT；第三方内容保留对应通知，见 [LICENSE](LICENSE)、[第三方说明](THIRD_PARTY_NOTICES.md) 和 `licenses/`。
