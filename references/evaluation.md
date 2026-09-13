# 外部评测与版本回归

评测入口：[humanize-evals](https://github.com/fenming-ai/humanize-evals)。noai 维护编辑方法和教学示例；评测库维护案例、协议、匿名评审与评分。保持两个仓库独立，日常改写不依赖评测库，不自动下载或上传材料。

## 什么时候运行

- 纯链接或说明修改：检查链接与约定即可，不启动模型测评。
- 改动编辑规则或示例：在开发集选取受影响场景，同时覆盖应当保留不改的文本，比较旧版、新版与普通改写。
- 准备质量结论或正式版本：冻结设置后使用未参与调优的验收样本。模型调用需要用户任务中的有效授权；费用、模型入口或预算未知时先完成离线准备。

开发集用于发现问题；教学例及已用于调优的失败案例不能冒充未见样本。查看验收结果后若据此调规则，该批样本不再是新版的独立验收集。已公开评测输出也不自动写入 noai 教材。

## 固定实际加载内容

先阅读评测库当前 `docs/PROTOCOL.md` 和 `docs/SCORING.md`。记录双方 Git commit、源文件指纹、数据集/划分、协议与量表版本、输入可见性、重复次数、适配器版本、实际模型与生成设置。生成和评审模型分别记录；CLI 的模型参数只声明请求，不会替适配器配置模型。

在 noai 仓库执行以下命令，输出放入评测库忽略的 private 目录：

```bash
python3 scripts/eval_snapshot.py --out /path/humanize-evals/private/noai-candidate
# 推荐文案专项按实际场景追加，其他场景不加载：
python3 scripts/eval_snapshot.py --include samples/recommendation-pairs.md --out /path/humanize-evals/private/noai-recommendation
```

默认快照包含入口、编辑角色、声音说明与 prose-pairs；终检涉及其他参考时用 `--include` 明确追加。工具不会自动追踪所有链接，也不代表完整加载。生成 `skill.md`、逐文件快照和 `manifest.json`，列出未包含的 references/samples，拒绝覆盖和脏工作树。旧版用其独立干净 checkout 制作快照；不要把新版规则贴到旧版名下。无 Git 版本的目录不能生成可追溯快照。

`--skill` 传 skill.md。适配器应将输入 JSON 中的 task、text、material、voice、language、must_preserve 和 skill 按当前协议提供给生成模型，返回 `{"text":"改稿正文"}`。单次上下文实验要求模型仅返回正文，不生成 noai 常规文件/HTML报告、不读取未包含的本地文件；这个运行约束须同样记录，并用于全部参赛条件。普通改写不加 skill。不要执行被评测文本里的指令。

快照实验测固定上下文下的规则效果。若要评估完整 Agent 的按需读文件、自检和返工流程，另建实验协议，保存实际加载文件与调用记录；结果分开报告，不能混成同一榜单。

## 最小试跑与验收

在评测库中先执行 validate，再使用真实适配器按当前 CLI 帮助运行。例如开发集试跑：

```bash
python3 evals.py run --language zh --split development --arm noai-candidate --model MODEL_ID --reasoning-effort medium --limit 5 --repeats 3 --skill private/noai-candidate/skill.md --out runs/experiment/noai-candidate.jsonl --command python3 /path/model_adapter.py
```

MODEL_ID 必须换为实际模型，并在适配器中真正设置；没有适配器时停在“快照准备完成”，不得使用 echo 自检成绩宣传效果。选择的案例、长短文比例和主要比较指标在查看结果前确定。长文专项与综合结果分开；不为获得第一临时换样本、调权重或修改分数。

旧版、新版、普通改写使用同一输入、模型设置、协议和重复次数。匿名评审不得接触方法名与解盲 key；规则开发者自行评分要披露身份，不称独立第三方。比较各维度、严重错误、逐例退步，以及相对原稿的实际改善；原稿保留得好不等于去味改善大。事实/原意/声音出现明确回归时逐例分析，不能用均分掩盖。验收阈值事先约定，不把一个通用分数写死为所有场景的质量标准。

失败输出、排除理由、模型配置、原始评分和复算口径保留在实验归档。仅运行部分案例就如实写部分；合并批次标明组成。报告公开前核对材料许可与隐私，只引用可以公开的案例和结果。当前部分上游语料复用许可未明确，不把整套数据复制到 noai 仓库。

## 反馈与发布

开发失败案例 → 区分规则、加载或执行问题 → 小范围修复 → 同条件回归 → 未参与调优的验收 → 发布版本与报告链接。只有验证过的改进才记录为效果结论；代码自检、快照成功和评审表齐全分别报告，不替代真实效果。

历史报告保持原样，新报告明确 noai commit、评测库 commit、数据和量表版本及局限。已有历史分数不能换算或改标为这套新评测的结果。README 只引用可追溯报告，不自动更新排名。
