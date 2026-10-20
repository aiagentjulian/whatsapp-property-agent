# WhatsApp Sales Lab — Autonomous Loop 06

## 结论：NEEDS REVIEW

新版 Sales Brain、Rubric 和 Sales Lab 指南作为本轮起点，未被改写或恢复旧版本。完成一次新 Baseline、一次有针对性的 Candidate 和一次新鲜 Holdout。保留的 Candidate 是一项窄范围的 Knowledge Retrieval 词形修复；结果有一个清楚的真实对话收益，但整体配对分数几乎持平，且有明显未解决问题，不足以宣称销售能力已稳定提升。

## 运行与评分

| | Baseline | Candidate | 变化 |
|---|---:|---:|---:|
| Legacy 加权分（/10） | 7.15 | 7.21 | +0.07（约 +0.7/100） |
| Sales Leadership | 6.9 | 7.1 | +0.2 |
| Appointment Progression | 6.0 | 6.2 | +0.2 |
| Desire / Visualization | 7.5 | 7.5 | 持平 |
| Naturalness | 8.2 | 8.1 | -0.1 |

独立 Judge 在揭盲前对五组 P/Q 配对评分。Candidate 在 2 组更好、1 组略低、1 组明显更低、1 组接近；这组小样本不支持强因果结论。主要配对只比较双方共同的前两次客户回合。详细逐轮记录见 [dialogues.md](dialogues.md)，盲评汇总见 [judge-blind-paired.json](judge-blind-paired.json)。

两边均没有客户同意开始安排 Viewing，也没有正式 Handoff。Candidate 的确发出过 Viewing Invitation，但邀请不等于客户有 Viewing Interest；客户考虑或表示兴趣，也不等于 Appointment Agreement。Holdout 也没有邀请、同意或 Handoff。

## 最有代表性的 Before / After

年轻首置夫妇问周边是否方便购物与日常办事：

**Baseline：** “I don’t have verified details on nearby shops or distances in front of me, so I don’t want to guess. I’ll check the nearby everyday amenities for you.” 结构化结果将一般位置问题转为 Support Request。

**Candidate：** “Pearl Residences is in established Seberang Jaya, with connectivity toward Sunway Carnival Mall, Chai Leng Park and the wider Butterworth/mainland network… when you visit you can judge the routes against your usual routine as well as see how the layout feels for you both.”

客户随后说已知目的地听起来方便，但希望先核对上班路线再考虑到访。这是由 Agent 的具体、经知识支持的区位信息增强了 Viewing Consideration 的证据；客户仍未答应安排，Agent 后续也没有获得预约同意或触发 Handoff。

反例是家庭空间场景：Baseline 把“租屋有点挤”连接到开放式客餐厨空间，并提供低压力看房邀请；Candidate 转而问月供还是首付更担心，没有尝试看房。这个差异不能由词形修复解释，属于模型输出波动，也显示预约判断尚不稳定。

## 诊断与修改

问题来自 Knowledge Retrieval 的常用词归一化：词表能匹配 `shop` 与 `shopping`，但普通客户更自然的 `shops` 没有归一化，导致 Agent 把可回答的一般区位询问当成缺少已验证资料。只增加 `shops` / `shopping` 到 `shop` 的别名，并加一条检索上下文回归测试。没有修改销售流程或添加固定话术。

检查了 `app/agent.py` 的 `SYSTEM_PROMPT` 与 Sales Brain 指引，二者存在宽泛销售建议重叠；但本次证据直接指向词汇检索遗漏，无法把机械提问可靠归因于提示词重复，因此未删改提示词。Holdout 中客户用“area”询问时，系统仍把一般已验证位置与待确认的精确交通细节合并为确认请求，显示检索/支持分流仍有缺口。

Candidate 有一条用 RM0.18/平方尺乘 900 平方尺，得到每月 RM162 维护费的回答，并明确说这不是全部持有成本。计算正确且有边界说明；项目知识同时对运行时计算该金额有谨慎提示，建议后续确认该限制对 Sales Lab 输出的适用范围。未将其记为虚构总成本。

## Holdout

新鲜普通犹豫客户只是在初步了解项目，询问区域和每月成本。独立 Judge 评分 6.33/10，Appointment Progression 4.5/10。Agent 正确说明维护费组成及 clubhouse pay-per-use，也避免编造完整月供；但没有分享已验证的一般区位信息，反而说要确认 area/access。事实与预约同意检查通过，Support Integrity 未通过。由于客户只是刚开始了解，没有强行邀请看房是合理的；核心问题是本可直接回答的支持信息被过度保守地转交确认。

## API 与验证

真实 SalesAgent 运行 24/24 次（Baseline 11、Candidate 11、Holdout 2），均走 `app/agent.py` / `app.sales_lab` 的 GPT-6 Luna、High 推理及真实 OpenAI API。总用量 70,037 输入、36,401 输出，共 106,438 tokens；运行工具未提供美元成本。Customer 与 Judge 由 Codex 原生 Subagent 承担，没有额外 OpenAI API 调用。基线与 Candidate 的真实 API 调用之前都通过真实入口、fake HTTP transport dry-run。

主要样本为 2 组普通意向、3 组普通犹豫，另有 1 组保留 Holdout。由于预算已达上限，没有再尝试第二个修复或候选。

本地验证：Sales Lab 基线及 Candidate fake-transport dry-run 已通过；`app.test_sales_lab_retrieval` 的 5 项测试通过。完整测试套件 `python3 -m unittest discover -s . -t .` 通过（42 项）；`git diff --check` 通过。
