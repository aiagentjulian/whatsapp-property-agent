# Sales Lab Loop 05 — 买家价值表达与销售推进

## 结论

**REVERT Candidate 1，保留基线 Sales Brain。** 在三个相同开场场景的匿名配对盲评中，稳定基线为 **7.57/10**，Candidate 1 为 **7.86/10**，提升 **0.29 分/10（2.9 分/100）**。虽然观察到少发无请求的价格核实任务、Product Connection 与 Progression 分项略升，但整体提升低于预设的 **5 分/100** 验收门槛，而且只有三个主要场景。按验收标准撤回候选代码改动，不把温和信号当作通过。候选对话和评分仍完整保留，便于后续复查。

## 做了什么

实验从 `5db0f73` 开始，在 `codex/sales-lab-v1` 建立独立目录。真实 Agent 使用 `app.agent.SalesAgent`、GPT-6 Luna / High、实际 Sales Brain、Knowledge Retrieval、会话历史及结构化决策。Customer 和 Judge 使用 Codex 原生 Subagents，没有额外付费 API；两者分别按 GPT-6 Luna / Low 和 Medium 请求启动，但 Subagent 无法自行确认有效运行配置。主协调器的运行模型配置也未向我暴露。

原基线在三个场景的首轮都创建了 `SUPPORT_REQUEST/PRICING`，尽管客户只说明 dated ~RM302k 起始参考“可能在范围内”，并未要求确认当前价格。Candidate 1 在 Sales Brain 加入一条一般销售判断：把这种认可当作继续讨论房屋适配的起点；只有客户主动要求现价/特定单位或总价，或说明价格阻碍下一步时才发起价格核实。没有加入销售话术或新价格，没有改 Runtime。

## 评分与对话结果

| 场景 | 基线 | Candidate 1 | 观察 |
|---|---:|---:|---|
| 家庭自住 | 7.78 | 7.60 | 两版都把三房连接到一家四口需求；Candidate 1 较直接邀请看房，但客户先要平面图。基线多回应了客户追问的学校位置。 |
| 伴侣居家办公 | 7.60 | 7.95 | Candidate 1 清楚说明独立房间可把视频会议从共用餐桌移开；客户表示这是所需布置，愿先看图则，合适再考虑看房。 |
| 活跃买家 | 7.33 | 8.03 | Candidate 1 将“无长走廊、开放式客餐厨”连接到客户觉得竞品局促的经历；客户愿意比较图则后看房。明确询问现价后，Agent 一并请求核实最新套餐与图则。 |
| **配对均分** | **7.57** | **7.86** | **+0.29/10** |

维度均分：Discovery **7.33 → 7.33**；Product Connection / Buying Desire **8.00 → 8.33**；Sales Progression **7.00 → 7.50**；Natural Conversation **8.50 → 8.50**。Judge 认为整体仍是温和改善。不同候选对话引出了不同客户回合，不能把“更感兴趣”的措辞视作受控因果证据。完整盲评分数、证据和解盲映射见 [`judge-paired.json`](judge-paired.json)。

### 代表性前后对话：活跃买家

**共同客户开场：**“我正在 Seberang Jaya 积极看房，也看过另一个项目，但觉得布局局促。什么会让我值得去看 Pearl Residences？我看到一个约 RM302k 的 dated 起始参考价，可能在预算范围内。”

**基线：**Agent 说明 Type A 约 900 平方英尺、无长内部走廊、开放式客餐厨和小储物空间，推测这可能减少被走廊占用的空间；提出可通过图则或看房比较，但同时主动表示需核实最新单位和套餐价格，结构化动作为 `SUPPORT_REQUEST/PRICING`。客户回应该比较点有用、愿意看，但要求先看图则并确认现价。Agent 请求图则，提到现价核实仍待处理，最后把是否看房留给客户决定。

**Candidate 1：**Agent 用同一组已核实布局特点解释比较价值，说明起始参考价是 dated 且不是现行或全包报价，并邀请客户现场比较；没有主动生成价格 Support Request。客户表示更清楚看到比较点，愿意在图则显示空间利用更好时看房，并要求先发图则和查现价。Agent 随后明确请求批准图则及最新价格/套餐，并说明资料看过后再判断看房是否值得。动作是 `SUPPORT_REQUEST/OTHER`，没有预约或正式 Handoff。

前后完整真实对话见 [`dialogues.md`](dialogues.md)。

## 买家可视化、兴趣与看房判断

两版最有说服力的地方都来自具体需求：家庭各自房间、居家办公不占餐桌、无长走廊对应竞品的局促感。视觉化仍以实用布局为主，没有强烈的日常生活画面；Customer 反应多为认可或有条件看房，不是购房承诺。Candidate 1 没有把邀请算作预约：三组对话都没有 `Appointment Agreement` 或 `Formal Handoff`。候选在更积极邀请的同时接受客户先看图则，不逼客户定时间。

## Holdout

冻结候选后才启用新的早期投资探索 Holdout。Agent 给出有依据的 freehold、RM0.18/平方英尺维护费（含 sinking fund）及预计 Q4 2029 完工信息；明确这些不证明租赁需求或投资回报。客户要求租赁前景证据后，Agent 说明没有已核实的租金可比或租客需求数据，并发起 `SUPPORT_REQUEST/OTHER`。没有随机邀约看房、虚构收益或声称完成核实。Judge 评分 **7.70/10**，认为此时不邀约正确。该单场景 Holdout 只检查候选是否出现明显问题，不是与基线的配对提升证据。完整评估见 [`judge-holdout.json`](judge-holdout.json)。

事实与状态核对：所有约 RM302k 描述都限于日期参考，不声称当前有效或全包；免费产权、维护费和完工时间与 Knowledge 文件一致。任何 Viewing Invitation、客户条件性 Viewing Interest、Appointment Agreement 和 Formal Handoff 均分别记录；本实验没有预约同意或正式 Handoff。

## 预算、验证与 Git

- 完成 **1 轮修复**；**14 / 16** 次真实 SalesAgent API 调用。
- 使用 **64,505 input + 29,095 output = 93,600 tokens**；API 未返回美元成本，未估算费用。
- 稳定代码与候选后的本地验证：`python3 -m unittest app.test_agent app.test_sales_lab app.test_sales_lab_retrieval app.test_runtime`，**27 项通过**；Candidate source 的 fake-transport dry run 也通过。
- 推荐：**REVERT**。候选均分提升 **2.9/100**，未达到至少 **5/100** 的验收条件；已撤回 Sales Brain 候选改动，分数、对话和诊断作为实验记录保留。Buyer Visualization 本身仍有提升空间，本轮没有新增证据支持更强的生活化或投资叙事。
- 无部署、合并、Runtime/生产数据库/Google Sheets/Meta/Webhook 操作。
- Customer 私有模拟资料未纳入 Git。价格测试快照仍只由 Sales Lab 注入。

实验报告、对话和评分已提交并推送至实验分支 `codex/sales-lab-v1`；由于未达验收门槛，候选 Sales Brain 改动已撤回。私有模拟画像未纳入提交。
