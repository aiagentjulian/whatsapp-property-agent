# Sales Lab V1 Auto-Improve Loop 02

**结论：KEEP `candidate-r2-live`。** 两轮修复后，开发场景盲评均分从 6.53/10 提高到 7.10/10（+5.7/100）。最终保留候选在全新价格顾虑 holdout 上为 6.8/10，对照原版为 5.9/10；Judge 认为客户更愿意继续考虑布局，且 Agent 提出了相关、可选的看房邀请。该客户仍未确认预约。没有事实、压力或 Handoff 违规。

## 执行和成本

- 真实 SalesAgent：使用 `app/agent.py`、Sales Brain、Knowledge Retrieval、结构化决策及待处理 Support 上下文，通过现有 OpenAI API 使用 GPT-6 Luna / High。
- Codex 原生 Customer Simulator 与独立 Judge 使用 Subagents，没有额外 OpenAI API 调用。
- 共 18 次真实 Agent 调用，预算上限 24；72,190 输入 token、40,457 输出 token、112,647 总 token。Provider 未返回费用金额，因此不推算成本。逐调用明细见 `ledger.json`、汇总见 `usage.json`。
- 没有运行旧版 Simulator、生产 Runtime、数据库、Sheets、Meta、Webhook 或部署操作。
- 复用了 Loop 01 的 candidate-r3 两组对话作为 genuine-interest 与 early-exploration 起始对照；补做了一组 fresh own-stay baseline。没有重跑能说明充分的旧场景。

## 迭代记录

**Baseline / 起始版本。** 盲评起始三组均分为 6.53/10。家庭需求连接表现最好，但邀请通常泛化；有的对话会漏掉可计算的 RM162 月维护费；销售推进容易落在“等价格确认”上。

**修复 1 — 未保留。** 在 `brain/AGENT.md` 加入将特性转成日常画面、按看房收益解释邀请等指导。真实复测里，家庭对话增加了空间描述，但没有显示更强购买欲；真有购买意向的路径失去原版取得的条件性看房兴趣，探索型路径也失去 RM350,000 预算信息。Judge 均分从 6.50 降到 5.96（−5.4/100），因此用第二轮针对性改写覆盖了该版本，没有保留为最终 Agent。

**修复 2 — 保留。** 用一条更有条件判断的指导代替上述两条：先将一个已表达需求连接到相关、可验证的实用益处；客户明确回应适配时，再判断看房能否帮助其决策；邀请时同时回应客户顾虑，不等完整 Budget/Profile；纯价格探索或尚无 plausible fit 时不机械邀约。保留已知部分费用直接计算、未知部分单独说明的做法。它不规定话术或阶段流程。

## 主场景盲评

| 场景 | Judge 观察 |
| --- | --- |
| 家庭自住 / 孩子需要独立房间 | 候选把三房与孩子独立房间直接连接，客户说“layout … promising”，并表示理解价格后愿意看看布局。原版仅获正面适配反馈，没有看房兴趣。属于真实的条件性推进，不是预约。 |
| 明确购买意向 / own stay | 候选邀请看房后，客户说明想先确认价格、费用及约 RM450,000 预算。Agent 尊重成本前提并提供已知维护费，不把条件意向误记为预约；但该对话没有复现对照版本的明确条件性看房兴趣。Judge 指出这是与预算发现之间的真实取舍。 |
| 初步价格探索 | 候选没有推看房；在客户给出 RM350,000 目标后，提供带明确限定的基价加最低停车附加费算术参考，并强调不能视为某套单位的确认全包价。Judge 认为有助于比较，但仍有历史参考价锚定风险。 |

完整轮次、结构化输出与客户反应保存在本目录的 `baseline-r0-*.json`、`candidate-r1-*`、`candidate-r2-*` 和 `customer-*.json`。完整逐字回复请查看这些文件；独立评分证据在 `judge-round1-loop02.json` 与 `judge-round2-loop02.json`。

代表性前后：

- 对照原版（家庭场景）：“If you’d like, I can also arrange a viewing.” 客户没有表达要看房。
- 候选（家庭场景）：“If the layout looks promising, a viewing could help you assess the room arrangement in person.” 客户回答：“I’d be open to seeing the layout, but we’d like to understand the current price and any other regular charges first.” 这是看房兴趣的条件表达；没有同意预约或完成交接。
- 候选面对早期探索客户时没有邀约，继续核实客户所问价格，保留了销售判断而不是追求邀约数量。

## 最终 holdout（修复结束后才运行）

新客户比较 Seberang Jaya 公寓，觉得项目偏贵。原版解释价格构成并等核价；客户说布局可能适合，但要求先比较完整费用。候选给出有来源且带条件的历史价格/附加项目说明，并建议同面积及停车配置进行比较。客户随后表示，若总价可承受，布局值得深入了解。Agent 解释当前单价仍待核实，并提出“optional viewing; nothing is booked”。Judge 加权分数 6.8 对 5.9，认为这带来轻微积极的推进提升。

该信号只是有条件地愿意进一步看布局，不是明确接受现场看房；没有预约协议，也没有正式 Handoff。全包单价与停车配置仍未确认。holdout 的匿名盲评见 `judge-final-holdout-loop02.json`；不得将这组结果理解为预约转化已被验证。

## 事实与 Handoff

Judge 未发现新事实错误。RM328k–RM358k 是历史基价参考，并明确不等于当前全包价；RM162/月维护费按 RM0.18 × 900 sq ft 计算；其他收费、停车配置及现行 package 均保持待核实。逐段区分看房邀请、客户条件性兴趣、预约同意与正式 Handoff。18 次调用中均没有约定日期/时间或真实人工交接。

## 最终建议

**KEEP** 第二轮候选。它达到本轮可接受的开发集提升幅度，解释得清楚的销售推进有所增加，并在新 holdout 上没有明显退步。它没有解决当前价目未确认导致客户延迟决定的问题；也有一个场景在预算发现和看房兴趣之间出现取舍。以后应以已核实的当前 unit-level price/package 与真实销售结果复核，不应把本轮小样本视为实际预约转化证明。
