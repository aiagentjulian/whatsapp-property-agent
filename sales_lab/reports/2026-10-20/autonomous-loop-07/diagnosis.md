# Loop 07 — 诊断与迭代记录

## Baseline

以分支起始版本（Sales Brain V3、SalesAgent 及当前 Knowledge）运行了 5 个短场景，共 24 次真实 SalesAgent 调用。没有客户同意开始安排看房，也没有正式 Appointment Handoff。Baseline 已有一些合适邀约，但通常要等客户先说明更多顾虑；区位场景能在客户询问 commute / amenities 后给出有用地标，并获得“everyday access sounds convenient”的客户反馈。

## Candidate 1 — 精简重复的 System Prompt

**假设：** `app/agent.py` 的 System Prompt 与新版 Sales Brain 重复，精简后可减少机械问答，让模型更有销售判断空间。

**变更：** 将销售行为引导集中交给 Sales Brain，System Prompt 主要保留结构化决策、事实与预约同意边界。以三个匹配场景盲评，Baseline 均分 6.35/10，Candidate 1 为 6.59/10（+0.24）；Appointment Progression 4.97→5.50/10（+0.53）。家庭场景中，客户从“layout might help”推进到“could be worth viewing with my partner”，但仍未同意安排。

**问题：** Couple 场景反复对同一个尚未返回的 approved plan 发出 `SUPPORT_REQUEST`。改动样本只有三组，价格场景无提升；不足以认定稳健。

## Candidate 2 — 避免重复提交待核实事实

**假设：** 在精简版 Prompt 中明确要求不重复已在核实的支持请求，并在等待时使用已验证信息继续对话。

**变更：** 增加该条 System Prompt 指引；五组匹配盲评中，Baseline 均分 6.55/10，Candidate 2 为 6.37/10（−0.18）；Appointment Progression 5.44→5.38/10（−0.06）。Cost 场景中没有重复提交；Couple 与家庭场景的个别客户对具体布局理由表示可考虑看房。

**问题：** Early Exploration 场景在客户只说比较 area 与 monthly cost 时先邀约，客户回答“Maybe later”并要求先给 general area/access。模型当时已有地标资料，但 `retrieve()` 没把区位段落送进 SalesAgent 上下文。整体分数没有提升，且一段重要场景明确退步。

## Candidate 3 — 直接地点问题的 Knowledge 路由

**假设：** 主要场景确认区位事实存在于知识文件，却因普通词项重叠检索失败；显式 location query 应检索 Exact location 与 External connectivity 段落。

**变更：** 在 `app/knowledge.py` 增加地点主题的定向检索测试与路由。候选首轮能给出 Seberang Jaya、Sunway Carnival Mall、Chai Leng Park 与 Butterworth/mainland network；客户明确表示这些地点可帮助比较通勤。

**结果：** 独立盲评在这一单配对中仍偏好 Baseline（7.80 对 6.25/10）。Candidate 3 在客户说“area and monthly cost”后仍较早建议看房；客户指出在整体成本清楚前不会决定是否参观。独立顾客角色与 Judge 都未观察到 Viewing Agreement。检索点修对了事实供给，但未改善销售推进，因而不保留。

## Candidate 4 — 仅保留地点检索，恢复原版 System Prompt

**假设：** Candidate 3 的早邀约可能来自 Prompt 精简；用 Loop 06 原 System Prompt 单独重测地点检索修复。

**结果：** 首轮给出了区位与周边连接，避免 Candidate 2 的“先邀约、再补 location”路径；但第二轮在客户仍比较租房与总成本时已经提到 viewing。匿名 Judge 在该配对中偏好 Baseline（6.25 对 5.00/10）。客户认可地点与 RM162 maintenance 是有帮助的，不过明确说要先了解 overall monthly cost 才决定是否看房。Candidate 4 的独立 Holdout 中，客户认可多用途房间，但仍需成本与 timing 才考虑参观；Agent 尊重了这个门槛，没有把邀请当作同意或触发 Handoff。

## 归因与结论

- 机械/重复问题部分来自模型把已知问题再次送进支持流程；Candidate 2 避免重复请求，但未改善整体销售推进。
- 地点场景的知识上下文确有路由缺口，但局部检索修复在匹配实测中没有带来更好的销售序列；首轮多给事实并不会自动形成购买欲望。
- 主要瓶颈仍是销售节奏判断：有些场景在客户已表达具体用途时可以尝试看房；另一些客户明确以完整成本、时间或伴侣讨论为门槛时，应先回应该门槛。Agent 对“可以看房”的邀请尚未稳定转成客户愿意开始安排。
- 所有真实对话均无 Appointment Agreement、无正式 Handoff，也无确认预约。邀请、客户考虑、同意安排、交由人工分别记录，未混为一谈。
- Candidate 1–4 的 SalesAgent Prompt / Knowledge 修改均未达“稳健且可解释地改善预约推进”的标准，最终全部撤回。保留的仅是无固定新预算/轮数限制、逐事件用量记账、自然结束对话和兼容旧预算的 Sales Lab 基础设施。
