# Sales Lab V1 — 第一轮结果

最终建议：**KEEP（保留在实验分支）**。保留 Sales Lab 基础设施和本轮 Knowledge Retrieval 改善。真实 WhatsApp Runtime 没有被替换或部署。

候选在短场景盲评中平均 **64.83**，基线 **56.00**，改善 **8.83/100**。Holdout **76.5/100，PASS**。这证明本次片段的相关性、项目连接和有用信息有所改善；**没有证明预约转化率提高，也没有产生已确认预约**。

## 实验条件

- 仓库 `aiagentjulian/whatsapp-property-agent`；最新远端基线 `codex/v2-handoff-ack`，提交 `889bb8a`。
- 独立 worktree：`/Users/julianong/Developer/whatsapp-property-agent-sales-lab-v1`；分支 `codex/sales-lab-v1`。
- CLI `0.154.0`，本机 `multi_agent` 已启用；实际使用当前会话原生 Subagent 创建、续用与消息工具。Python 不调用内部 Subagent。
- Customer：`gpt-6-luna / low`；Judge：`gpt-6-luna / medium`。二者复用原生 Codex 子代理，没有另建 API 客户端。
- Coordinator 沿用宿主会话配置，无法通过 Subagent 工具切换自身模型或 reasoning；没有声称已切到 Luna/medium。
- Sales：真实 `app/agent.py::SalesAgent`、现有 OpenAIProvider、`gpt-6-luna / high`，真实 Sales Brain、Knowledge 和结构化决策；没有模型替代或模拟销售回复。
- 每个场景两次实际销售回复；Holdout 三次。客户资料为合成 persona，未注入 SalesAgent。相同开场、相同隐藏动机、相同模型与轮数上限；后续客户回应随真实回复自然分支。
- Judge 只收到 X/Y 匿名对话、客户反应、评分标准与事实 Knowledge。最终解盲：**X = Candidate 1；Y = Baseline**。同一 Judge 进行配对盲评，无法消除全部评估偏差。
- 选择门槛在候选评测前记录：平均提升至少 5 分、单场景不退步超过 10 分、无新增严重事实/Handoff 问题，并通过 Holdout。

## Baseline 问题与诊断

1. Own Stay 的真实开场突然介绍“approximately 55m”泳池，与客户动机无关。检索实际取到了 Pool details、电气资料。
2. Couple/Home Office 只有笼统“可将房间作为办公室”，检索却取了其他设施、防洪，且将 `space` 映射到 SkyPark，没有提供真实布局证据。
3. Investment 在未被问价格时便发起价格 Support；没有主动提供现成的 tenure、maintenance、completion 证据。后续能回答 RM162/月，但仍缺少购入成本参考。
4. 多项问题来自证据选取。现有 Brain 已明确 Guided Selling，本轮没有继续堆 Prompt Rule。

## 一轮针对性改善

只修改 `app/knowledge.py` 的证据供给：

- 过滤广告开场和一般交谈词，避免弱关键词选出随机设施。
- Home Office / floor plan 取真实布局证据；`space` 单词不再自动触发 SkyPark，儿童户外空间仍可取相应证据。
- 明确的价格问题同时提供基础价格结构、额外费用、rebate 适用条件和时效警示；多项问题保留布局与 completion 资料。
- Investment 取 freehold、maintenance 和 expected completion；不生成租金、收益率或升值承诺。

没有新增固定销售剧本，也没有修改 Brain、API 模型、Runtime 服务、Handoff 代码、生产数据库、Sheets、Meta 配置、Webhook 或 Tunnel。候选源代码快照在 `candidate1.patch`，源指纹在各对话 JSON。未执行第二轮销售修复；看过 Holdout 后没有调优销售代码。

## Before / After 证据

完整原文见 [dialogues.md](dialogues.md)，逐轮完整决策和 token usage 见各 JSON。

| 场景 | Before | After |
|---|---|---|
| Own Stay | 无关泳池介绍；价格只说待查 | 去掉泳池；说明历史 base-price reference 和费用限制，同时确认 expected Q4 2029。仍未充分连接“靠近家人”与地点优势 |
| Couple/Home Office | 仅说房间可用作 office，随后重复 900 sqft | 说明 open-plan、减少内部走廊等实际布局；不保证桌子/家具一定放得下 |
| Investment | 开场即价格 Support；后续只有管理费 | 开场给 freehold、Q4 2029、RM162/月 maintenance-only；后续给带限制的 base-price benchmark，拒绝编造租金 comparables/yield |

候选价格原话包含：`That isn’t a confirmed current all-in range`。RM328k–RM358k 是提供的 Block 1B 基础价格参考，不是全项目最高最低价、不是当前 post-rebate 报价，也不是已确认总价。相关费用和最新适用 package 仍需核实。

## Judge 分数与理由

维度顺序：Effective Discovery 20%、Product Connection & Buying Desire 35%、Sales Progression 35%、Natural Conversation 10%。每维 0–10，总分 0–100。逐项证据在 `judge-blind.json`。

| 场景 | Baseline 四维 | Candidate 四维 | Baseline 总分 | Candidate 总分 | 差值 |
|---|---|---|---:|---:|---:|
| Own Stay | 8 / 4 / 3 / 8 | 8 / 6 / 4 / 8 | 48.5 | 59 | +10.5 |
| Couple/Home Office | 8 / 6 / 4 / 8 | 8 / 8 / 4 / 8 | 59 | 66 | +7 |
| Investment | 7 / 6 / 5 / 8 | 8 / 8 / 5 / 8 | 60.5 | 69.5 | +9 |
| 平均 | | | **56.00** | **64.83** | **+8.83** |

Judge 认为主要进步是具体、相关且有事实根据的项目连接。发展场景中客户均选择等确认价格/图纸/租金证据，不能为了分数强推 Appointment；三个场景均无已同意看房。两版本的事实准确性与 Handoff 合规均 PASS。

评测期间发现并修正两处评测问题：最初入口把 SUPPORT_REQUEST 错作自动终点，现已允许客户自然继续；从原始 `889bb8a` 源码快照补完受影响的 Baseline 投资片段，不虚构支持结果。Judge 初稿的加权计算也经程序重算。早期评分仅保留作历史记录 `judge-preliminary.json`，**最终结论只用修正后的完整片段与评分**。

## Holdout：价格顾虑 / Appointment Opportunity

Holdout 从未用于销售修复。客户喜欢 freehold、三房，但担心预算；后来说明约 RM420,000 all-in、第三房未来可作 nursery。

Agent 将三房和 nursery 需求连接，保留批准图纸/尺寸的事实限制；客户表达条件性看房兴趣后，Agent 回复：

> If it’s close to RM420,000, we can then arrange a viewing so you can judge whether the third bedroom works for your nursery plans.

最终客户只同意在价格接近预算时再讨论看房。最终决策是 `REPLY`、`appointment_readiness=EMERGING`，没有 APPOINTMENT_HANDOFF、预约日期或确认 booking。查看意愿先由客户提出，**不能称作 Agent 主动创造了看房机会**。

Judge：8 / 8 / 7 / 8，**76.5/100**；有用且低压力的条件性推进，事实/Handoff 均 PASS。它仍容易停在“待核实后继续”；本轮不能证明 Agent 已全面解决主动邀约问题。没有实际执行人工 Handoff，因此生产交接执行链不属于这份销售能力结果。

## 验证、预算和费用

- 同一 operator CLI 先执行 fake HTTP transport，走真实 SalesAgent → Brain/Retrieval → OpenAIProvider 请求格式 → 结构化响应解析 → 状态/报告路径，通过后再 live。候选源变化后重新 dry run。
- **39 项本地测试通过**，覆盖已有 Runtime/Webhook/CRM、检索相关性、多项问题证据、24 次上限、失败即停止、fake transport 和 pending Support 继续对话。另有 `git diff --check` 通过。
- 真实 API：Baseline 6、Candidate 6、Holdout 3，共 **15/24**；无自动重试、无额度失败。剩余预算未使用。
- Input **46,446**、output **24,464**，total **70,910 tokens**；output 内含 reasoning **16,493**，不重复加总。
- API 未返回货币账单费用，未猜测美元成本。详细原始 usage 和调用预算见 `usage.json` / `ledger.json`。Customer/Judge 使用 Codex 会话额度，未另外调用付费 OpenAI API。

保留本轮合格检索改善和可重复实验入口；样本很小、客户为合成、对话自然分支，分数是定性证据，不是销售转化率的统计结论。
