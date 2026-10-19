# Sales Lab V1 — Autonomous Auto-Improve Loop

**结论：KEEP `candidate-r3-live`，适用于实验分支评审。** 本轮对真实 SalesAgent 做了 3 轮定向修复和同条件复测；盲评主场景平均加权分提高 **1.125/10（11.25/100）**，销售推进平均提高 **2/10**。这是客户实际表达的看房兴趣和预算信息，不是 Agent 自报策略。Holdout 为 **6.6/10**，未见明显退步，但也未体现购买欲增强。

## 测试完整性

- SalesAgent 是 `app/agent.py` 的真实实现，使用 `gpt-6-luna / high` OpenAI API；Sales Brain、知识检索及结构化决策均真实加载。
- Customer Simulator 与 Sales Judge 使用 Codex 原生子代理，没有另建付费 API。Judge 对主要对话做匿名盲评；Holdout 在修复完成后单独评估。
- 起初 4 次 pilot 调用未带 Runtime 等价的 pending Support context，已从比较中排除并保留记录，但仍计入预算。修正 harness 后的 baseline、候选和 holdout 均传入 open/resolved Support context；未伪造人工 Support 答复。
- 总预算 **24/24 次真实 SalesAgent 调用**：4 次排除的 pilot、4 次有效 baseline、12 次三轮候选、4 次两个 holdout。API 返回 usage 合计 **130,285 tokens**（82,036 input、48,249 output）；其中有效对比/holdout 为 110,741 tokens。Provider 未返回可验证的美元账单金额，故不估算费用。
- Codex CLI 报告 `multi_agent` stable enabled。当前环境没有在既有主任务里切换主模型/effort 的能力；Sales Agent 模型配置按要求为 Luna/high。此限制不影响 Customer/Judge 使用原生子代理。

## 分数与决策

维度权重为 Discovery 20%、Product Connection / Buying Desire 35%、Sales Progression / Appointment Opportunity 35%、Natural Conversation 10%。独立 Judge 评分均为 0–10；所有分数均有对话证据，详见 judge JSON。

| 集合 | Baseline | 最佳候选 | 变化 | 观察 |
|---|---:|---:|---:|---|
| Genuine Buying Interest | 5.8 | 6.9 | +1.1 | 产生“愿意看房、但先看费用”的明确客户回应；不是预约同意 |
| Early Exploration | 5.7 | 6.9 | +1.15* | 继续轻量回答；客户透露约 RM350,000 预算，但没有看房兴趣 |
| 两个主要场景平均 | 5.75 | 6.875 | **+1.125/10** | 超过 +0.5/10 验收线 |
| Sales Progression 平均 | — | — | **+2/10** | 看房机会 +2；探索场景也得到更有用的预算信号 |
| Fresh final holdout | — | 6.6 | — | 价格异议得到审慎回应；不机械邀约；没有明显退步 |

*独立盲评报告记录的 paired difference 为 +1.15；逐项已四舍五入展示。报告中的平均进步使用 Judge 未舍入的内部加权分。主要结果依据 [judge-r3-paired.json](judge-r3-paired.json) 与 [judge-holdout-final.json](judge-holdout-final.json)。

四项验收均通过：主场景平均提升超过 5 个百分点；Sales Progression 有实际商业推进；没有严重事实或 Handoff 违规；fresh holdout 无明显退步。Holdout 没出现看房邀约是合适的：客户在浏览、要求公平比较，尚无访问意愿。

## 修复记录

1. **Round 1 — 邀请不等于预约/正式交接。** 在 Sales Brain 和系统提示中明确：Viewing invitation 是普通 REPLY；客户愿意看看才是 viewing interest；这两者都不等于 appointment agreement 或正式 handoff。此轮没有改善实际邀约行为；盲评认为一个对话虽披露预算，但缺少有意义的看房推进。
2. **Round 2 — 只在具体购买需求和匹配评估出现时给出低压力下一步。** 买家明确准备购买并在衡量单位/费用时，Agent 可把实地看房作为评估户型的选项，即使仍在确认价格；只浏览/比较者不应自动邀约。真实客户表示户型可能适合且愿意在看费用后看房；Agent 没有虚报预约或触发 handoff。
3. **Round 3 — 把规格明确连到客户说出的需求。** 修复指引要求把已核实特征用简短、实际的个人利益表达出来，不把规格列表留给客户自行推断。盲评显示两个场景均有可解释的客户进展。

候选改动只在 [brain/AGENT.md](../../../../brain/AGENT.md) 和 [app/agent.py](../../../../app/agent.py)；没有固定销售话术或强制状态流程。Harness 修正真实传递 Runtime Support context，避免测试环境与实际决策上下文不一致。

## Before / After 摘录

**Baseline — Genuine Buying Interest，第 2 轮**

> The regular maintenance for the 900 sq ft unit is about RM162 a month; utilities and any pay-per-use clubhouse charges are separate. I need to confirm the latest Type A price and the exact car-park allocation… The loan instalment will depend on the confirmed price…

结论：答复谨慎，但只进入价格/车位待查，没给正在考虑三房买家的看房选项。

**Best Candidate — Genuine Buying Interest，第 1 轮**

> …Maintenance is RM0.18 per sq ft monthly, inclusive of sinking fund… Since you’re hoping to buy, a viewing could help you assess the layout in person. Is this mainly for your own stay or as an investment?

客户回应：“It would be for our own stay. The three-bedroom layout sounds like it could suit us, and I’d be open to viewing it once we understand the price and monthly costs.” Agent 后续记录为 viewing interest，继续先核实价格/车位；没有声称客户已预约，也没有正式 handoff。

完整逐轮真实对话见 [dialogues.md](dialogues.md)。

## 仍待解决

- RM162 可由 900 sq ft × RM0.18 直接计算，但 Agent 在主场景前两轮仍重复表示需要确认；这增加了不必要的等待。Holdout 最终轮已正确直接计算并说明账单面积前提。
- 当前动态 post-rebate package 需要与具体 unit/floor/facing/parking 匹配；没有足够上下文时 Agent 应确认，而非把历史 base price 误当现价。候选对 RM328k–358k 使用了历史/indicative 标签，但仍可能锚定客户预期。接下来的 Support 回复应给出当前 package 后价格与车位配置，才能进一步判断贷款/总成本。
- 本轮停在客户的条件性看房兴趣，没有客户给出日期、预约同意或正式 handoff；没有声称已完成预约。
- 小样本短对话只验证两个主场景和一个 fresh holdout，不能代表所有客户/语言情形。

事实、Viewing / Interest / Agreement / Handoff 和完整轮次依据保存在 [dialogues.md](dialogues.md)、[judge-r3-paired.json](judge-r3-paired.json)、[judge-holdout-final.json](judge-holdout-final.json) 与 [ledger.json](ledger.json)。
