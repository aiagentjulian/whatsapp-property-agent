# Sales Lab Loop 04 — 结果

## 结论

**REVERT Candidate 1；保留已验证的稳定 Sales Brain。** 这轮真实 Agent 基线整体表现可靠，但没有达到“修改后提升至少 5 分”的验收线。Candidate 1 的 blind comparison 没证明更好，随后已撤回；仅提交 Sales Lab 测试基础设施、日期明确的测试价格上下文及实验记录，不提交销售行为修改。

实验从 `5b5c61f` 开始，在 `codex/sales-lab-v1` 进行。真实 Sales Agent 使用 `app/agent.py`、实际 Sales Brain、Knowledge Retrieval 和结构化决策，经 GPT-6 Luna / High 推理。Customer Simulator 和 Sales Judge 使用 Codex 原生 Subagents，没有额外 OpenAI API 调用。未触发 WhatsApp Runtime、生产数据库、Google Sheets、Meta、Webhook 或部署。

## 定价测试环境

测试资料来自 `knowledge/project/pearlmont/02_commercial/pricing.md` 与 `sales-package.md`。14 Aug 2026 快照中，Block 1B Podium Blocked Levels 1–4 的 RM328,000 base，匹配 Podium Blocked Levels 1–9 的 8% rebate，计算为 **RM301,760**。它是有日期、特定类别的 base 减 rebate 参考，不是现价、单元总价或包含所有车位/配套的报价；车位与其他组件、最新套餐有效性仍须逐单确认。

此前通用价格问题容易滑向单元筛选或 SUPPORT_REQUEST，是因为现有知识列有 base、rebate、车位结构和准确性限制，却没有清晰的一条可直接表达的匹配类别净额。本轮只把上述可追溯计算加入 Sales Lab 的输入上下文；普通 Runtime 不会传入这份测试资料。真实冒烟调用成功回答 RM301,760，并明确日期与限制，没有触发通用价格支持请求。

## 真实对话评分

Independent Judge 对 5 个基线场景盲于版本来源评分，四项加权均分为 **7.17/10（71.7/100）**。维度权重为 Discovery 20%、Product Connection / Buying Desire 35%、Sales Progression 35%、Natural Conversation 10%。完整证据见 [`judge-baseline-x.json`](judge-baseline-x.json)。

| 场景 | 加权分 / 10 | 客户真实反应与下一步 |
|---|---:|---|
| 家庭自住 | 7.55 | 客户认可孩子各有房间及额外窗户；愿意在总价更清楚后看布局。 |
| 近期购房兴趣 | 7.29 | 客户认可开放空间和储物；若总价合理，愿意再看时间。 |
| 早期探索 | 6.56 | Agent 回答 dated price、再说明月维护费；没有机械邀约。客户仍在比较。 |
| 伴侣居家办公 | 7.42 | 第三间房连接到潜在安静工作空间；客户愿意先看批准图则，再考虑看房。 |
| 首次投资探索 | 7.02 | 给出维护成本、freehold 与预计竣工信息，不编造租金回报；当前费用超出知识范围时请求核实。 |

### 修复尝试 1 — Buyer-specific visualization

基线 Judge 认为需求与功能的连接有效，但“拥有后会怎样”的表达仍偏实用说明；这是真实但有限的假设。Candidate 1 将一条 Sales Brain 原则改为偏好一个简短、基于客户已表达动机的个人用途示例，仍要求有事实支持且不得臆造。

独立盲评比较了家庭与投资场景：同两场景的基线均分 **7.25/10**，候选 **6.94/10**（折算为 100 分制，候选低 3.1 分）；家庭场景基线略优，投资场景因候选较早进入合理的待核实费用支持状态，后续反应不等长，无法证明候选更好。家庭候选确实把主卧与孩子各自的房间说得更具体，但客户意向仍只是在确认总价后再考虑看房。该修改未达到验收标准，已撤回。评分细节见 [`judge-blind-pair-iteration-1.json`](judge-blind-pair-iteration-1.json)。

因此最佳保留版本仍是本轮基线 Sales Brain；它的 7.17/10 与候选同场景盲评不可混为一个测试集的直接全量对比。没有再堆叠提示规则：已有 Sales Brain 已明确要求个性化地连接功能和收益，当前证据没有支持另一项低风险、独立且可能明显提升的提示修改。

## 最终未触碰 Holdout

未用于修复的价格异议场景得到 **6.71/10（67.1/100）**。Agent 解释 dated RM301,760 计算与可能的车位/配套费用，再针对客户明确要求的“当前标准车位总价和适用组件”请求核实。客户没有表达看房兴趣，Judge 认为到第二轮仍不邀请看房是恰当的：当前总价仍是客户唯一明确的判断门槛。没有预约同意或正式 Handoff，也没有现价或总价虚构。完整盲评见 [`judge-holdout-iteration-1.json`](judge-holdout-iteration-1.json)。

## 销售判断与遗留问题

看房机会判断总体符合目标：近期买家、家庭和居家办公客户收到与布局相关的邀请；他们只表达有条件的 Viewing Interest，没有同意日期/时间，Agent 也没有误报 Appointment Agreement 或 Formal Handoff。早期比较、仍需了解投资成本和价格异议客户没有被机械邀约。

主要限制仍是购买欲望表达多为实用层面的空间/成本说明；投资知识没有已验证租赁需求或回报数据。数个首轮回复偏密，RM301,760 的明确数字即使注明日期，仍可能锚定客户预期。当前套餐、标准车位总价、额外费用和具体房间尺寸需要真实 Support 结果才能继续推进；测试没有伪造这些信息。

完整真实逐轮对话、结构化动作、客户反应和支持/看房状态见 [`dialogues.md`](dialogues.md)。

## API 与验证

- 真实 SalesAgent 调用：**18 / 24**；无失败重试。
- 使用量：**80,485 input tokens + 38,679 output tokens = 119,164 tokens**。OpenAI 响应未提供美元成本，故不估算费用。
- 实际真实推理均为 GPT-6 Luna / High。Customer/Judge 没有额外付费 API 调用。
- 最终基线版本本地验证：`python3 -m unittest app.test_agent app.test_sales_lab app.test_sales_lab_retrieval app.test_runtime`，**27 tests passed**；`git diff --check` 通过。
- 独立测试覆盖可选 Sales Lab 上下文与普通 `SalesAgent` 调用隔离；最终未提交 Customer 私有画像文件。

## Git

已验证的 Sales Lab 基础设施和实验结果已提交并推送到 `codex/sales-lab-v1`，主实现提交为 `82cb936`。没有提交 Sales Brain 候选修改或 Customer 私有画像。

## 自主续跑：修复尝试 2

按后续执行要求，在同一 24 次预算内继续测试了另一项方向：宽泛价格咨询只检索 base/package 概要；只有停车位、总价、包含项目等具体问题才加载组件明细。Sales Brain 没有改动。本次真实 SalesAgent 在相同早期探索开场下跑了两轮，Customer 与 Judge 使用 Codex Subagents。

盲评将候选标为 U、稳定基线标为 V：候选 **6.62/10**，基线 **6.87/10**。基线首轮准确说明 RM328,000 对应 Block 1B Podium Blocked Levels 1–4，再给出日期限定的 RM301,760 计算，并用已验证的 RM162 月维护费帮助客户比较。候选首轮没有说出该金额所依据的单位类别；客户追问后，Agent 正确澄清类别及 rebate 适用范围，并为现行套餐/停车费用建立了合适的价格核实请求。该请求不是正式人工 Handoff。两段对话都没有 Viewing Invitation、Viewing Interest、Appointment Agreement 或 Formal Handoff；客户仍在早期比较，盲评认为不邀约是正确判断。客户第二轮反应不同，不能据此推断单一回复造成了兴趣差异。

候选没有创造更多购买动机，也没有改善销售推进；稳定基线在完整对话质量上略好。因此已撤回 `app/knowledge.py` 与对应测试的候选修改，并在原始稳定代码上重新运行 27 项本地测试，全部通过。逐轮候选记录见 [`candidate2-early_exploration.json`](candidate2-early_exploration.json)，独立评分见 [`judge-blind-pair-uv.json`](judge-blind-pair-uv.json)。第二次修复尝试未通过，没有提交销售行为或检索变更。

续跑后累计真实 SalesAgent **20 / 24 次**，**88,470 input + 42,167 output = 130,637 tokens**；API 未提供美元费用。保持原稳定版本的总体基线 **7.17/10**，没有证据证明候选达到要求的 5 分提升，最终建议仍为 **REVERT 候选，保留稳定版本**。剩余 4 次预算未消耗：当前证据没有显示一个不同、具体且有依据的改动方向能在这有限样本中提高销售判断；继续盲目改提示只会增大过拟合风险。
