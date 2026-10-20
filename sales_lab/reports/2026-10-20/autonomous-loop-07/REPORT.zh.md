# WhatsApp Sales Lab — Autonomous Loop 07

## 结论：REVERT SalesAgent 候选；保留 Sales Lab 基础设施

本轮完成一个新 Baseline、四轮有证据的候选测试、三次 Holdout 检查及独立盲评。没有候选达到“更能把普通询盘引导到客户同意开始安排 Viewing”的标准，因此没有保留 SalesAgent Prompt 或 Knowledge 修改。`app/agent.py` 与 `app/knowledge.py` 已恢复到 Loop 06 起始版本；保留的代码改动只包括 Sales Lab 运行限制与用量记录、自然收尾、测试及操作说明。

完整实际逐轮对话见 [`dialogues.md`](dialogues.md)，盲评原始结果见 [`judge_blind.json`](judge_blind.json)，逐轮诊断见 [`diagnosis.md`](diagnosis.md)，后续盲评与最终 Holdout 见 [`judge_addenda.md`](judge_addenda.md)，token 汇总见 [`experiment.json`](experiment.json)。每个阶段的 `ledger.json` / `ledger.jsonl` 保留在本目录及候选子目录中。

## 对比结果

| 阶段 | 配对数 | Baseline 均分 | Candidate 均分 | Appointment Progression | 判断 |
|---|---:|---:|---:|---:|---|
| Candidate 1：精简 System Prompt | 3 | 6.35/10 | 6.59/10 | 4.97→5.50/10 | 小幅上升，但样本少；重复请求同一平面图资料 |
| Candidate 2：加待核实事实防重复指引 | 5 | 6.55/10 | 6.37/10 | 5.44→5.38/10 | 整体无改善；地点探索中早邀约造成明确推迟 |
| Candidate 3：定向区位检索 + Candidate 2 Prompt | 1 | 7.80/10 | 6.25/10 | 单配对偏好 Baseline | 地点资料提前呈现，但客户仍以成本为参观门槛；邀请偏早 |
| Candidate 4：定向区位检索 + Loop 06 原 Prompt | 1 | 6.25/10 | 5.00/10 | 单配对偏好 Baseline | 地址信息更快，但总成本未清楚前已提 Viewing |

Candidate 1/2 的盲评来自同一 Judge、匿名逐场景评价；Candidate 3/4 各由新 Judge 对单一匿名配对复核，评估者绝对分数不可跨组直接比较。配对复用相同客户类型，样本不是独立统计试验。综合证据没有达到稳健改善。

## 有代表性的真实顾客反应

- **Baseline 地点场景：** Agent 在说明 Seberang Jaya、Sunway Carnival Mall、Chai Leng Park 与 Butterworth 网络后，客户说“**The everyday access sounds convenient**”，随后明确提出先核对当前价格再决定是否参观。这个地点理由获得了客户认可，但尚未形成预约同意。
- **Candidate 2 地点场景：** Agent 在未给出客户所问 area/access 资料时先问“**Would you like me to help arrange one?**”客户回答“**Maybe later**”，要求先了解一般区位与 monthly costs，并说“**We can leave the visit for now**”。这是本轮最明确的早邀约负反馈。
- **Candidate 1 家庭场景：** Agent 把额外房间和家庭共享空间联系起来后，客户说“**It could be worth viewing with my partner**”，但仍要先看 approved plan。候选比基线更具体地推动了 viewing consideration，却没有获得同意安排；相邻场景还发生重复平面图支持请求。
- **Final Holdout：** 新婚首置客户认可额外房间可用于家人来访，但表示伴侣担心长期承诺，并要求先了解 timing 和 costs。Agent 给出 RM162/月维护费并标明不含其他费用，承诺核实详情；客户没有答应看房，也没有触发 Handoff。

这些结果显示，贴合生活场景的理由能引发客户本人对空间的认可；但尚无证据证明改动能稳定跨过“我愿意开始安排 Viewing”这一步。Agent 有时也会在客户明确提出成本比较之前先问要不要看房。

## Handoff 与事实检查

74 次真实调用中，没有 `APPOINTMENT_HANDOFF`、客户同意安排的语句或已确认预约；因此没有正式 Human Handoff。仅有 Viewing 邀请或客户表示“可以考虑”均未算同意。已出现的 RM301,760 是按 2026-08-14 的 RM328,000 基准价减 8% 计算，Agent 明确标注为历史、indicative、非当前且非 all-in；RM162 是 900 sq. ft. × RM0.18，Agent 说明这只是 maintenance。没有发现无依据收益或虚构紧迫感。对于周边道路、租金和完整月供，Agent 选择待核实，未捏造数值。

## Sales Lab 运行限制修复

新实验不再受 `LIMIT = 24` 或每段最多三个客户回合限制，也不提供替代的任意限额。新运行 `ledger.jsonl` 追加 `attempt_started`、`attempt_completed` 或 `attempt_failed` 事件，保存可获得的 token usage；保留 `ledger.json` 作为兼容摘要，旧 ledger 中原本记录的 cap 仍然执行。并发锁、失败停止与不自动重试行为保留。新增 `--end-dialogue` 允许在自然终点结束，不必再耗一次 SalesAgent API 调用。真实调用前均通过同一 entrypoint 的 fake HTTP dry-run。

## API 使用

- GPT-6 Luna / High SalesAgent：**74 次已完成调用，0 次失败**。
- 输入：249,259 tokens；输出：118,332 tokens；合计：367,591 tokens（其中可见 reasoning tokens 79,978）。
- Customer Simulator 与 Judge 由 Codex 原生 Subagents 扮演，没有另发 OpenAI API 调用。环境未提供其运行模型身份的独立验证信息。
- API 响应未返回实际账单成本字段，本轮不估算金额。

## 验证与 Git

- `python3 -m unittest discover -s . -t .`：43 项通过。
- 对最终保留的 Sales Lab runner / fake transport dry-run 已验证；候选 SalesAgent 实验的源码指纹和真实调用均随实验数据保存。
- 最终结论：**REVERT** SalesAgent 候选修改；保留 Loop 06 的 SalesAgent / Knowledge 与本轮 Sales Lab 基础设施。未部署、未合并、未触碰 WhatsApp Runtime、Meta、Google Sheets、Webhook 或生产数据。
- 分支：`codex/sales-lab-v1`。没有合并或部署。
