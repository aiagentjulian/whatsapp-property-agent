# V2 Lite 知识检索端到端评估

日期：2026-10-13  
分支：codex/v2-lite-knowledge，评估起点 c5b5c67  
A：V2 Lite Prompt + codex/v2-lite-prompt 的原始 Retriever（8c07a83）  
B：同一 Prompt + c5b5c67 的改进 Retriever

## 方法与本地检查

先运行现有 CRM、Runtime、V2 Lite Evaluation、Webhook 测试：**32 passed，0 failed**。先前关于 independent sales judgment 的旧断言已更新为适配 V2 Lite 用语；本次没有修改 Prompt。

A/B 使用相同的 V2 Runtime 代码、GPT-6 Luna / High、知识目录、固定客户消息、画像和预置历史。唯一运行时差异是 retrieve() 函数：A 从 codex/v2-lite-prompt:app/knowledge.py 加载；B 使用评估分支的 Retriever。Prompt 内容及 SHA-256 一致（1ffd1ff885f2e774b61ff06c57ea1ab9bb7bc05ff2a1654d423b8be309453a0d），两分支知识树一致。付费调用前，6 组本地假 Provider 配对检查通过；除 relevant_project_knowledge 外，发送给模型的输入字段逐项相同。

完成 6 个固定用例、12 次真实 Sales Agent API 调用。没有 Customer Simulator、LLM Judge、真实 CRM、WhatsApp 或预约操作。SUPPORT_REQUEST 只写入本地假适配器，返回 status=OPEN, support_result=null，代表等待人工核实，不代表已经核实或完成。

每个用例的固定问题和完整预置历史、模型完整输入、分开提供的核心事实、逐字 Retriever passage（含文件路径/标题/内容）、完整决策、回复、支持请求及假适配器结果、token 和延迟均保存在 [trace.json](trace.json)。以下回复为模型原文。

## 六组配对结果

### 1. 指示价格与月供

历史：客户比较 Seberang Jaya 的 900 平方尺住宅；销售员询问先想了解什么；客户说主要关心月供是否负担得起。问题：“Could you share an indicative price range and a rough loan repayment for a 900 sq ft unit? I have a 30-year loan in mind.”

A、B 都只检索到 02_commercial/financing-and-booking.md 的 Loan-margin references in the FAQ，即不同贷款机构列出的最高贷款比例及不得保证审批的限制；两者均未检索到价格文件。独立提供的单位资料确认 900 平方尺、3 房 2 卫。

- A（SUPPORT_REQUEST，FINANCING）：“I don’t have verified current pricing or loan figures to quote, so I don’t want to guess. I’ll check the indicative price and a rough 30-year repayment estimate for the 900 sq ft unit.”
- B（SUPPORT_REQUEST，PRICING）：“Sure—I’ll check the latest indicative price and a rough 30-year repayment for the 900 sq ft unit. The monthly amount depends on the loan margin and rate, so I don’t want to guess.”
- 两个假请求均为 OPEN，没有返回核实结果。B 把贷款比例/利率假设列为月供估算条件，表达更清楚。

**判定：检索失败（可引用指示起价）+ 动态信息合理待核。** 知识中有 2026-08-14 package 的 “from RM3xxk” 参考和 base-price 结构，Retriever 未交付；如只要求实时有效的精确价格或基于当前单位的月供，索取最新价单及贷款假设是合理的，不把“未直接给实时精确价格”单独算作失败。知识来源本身提醒 package 会变。

### 2. 中文询问附近学校与步行

历史：客户说有两个上学孩子、日常接送忙；销售员表示理解。问题：“请问附近有哪些学校？住户走过去方便吗？”

- A 检索结果为空。核心销售证据另行提供项目规划内 25 层、SK/SMK、预计与 Phase 1 同步完成等信息，但没有步行通道 passage。回复：“目前确认的资料显示，项目规划内有一所25层学校，规划涵盖SK和SMK，预计与第一期同步完成；学校不在住宅塔楼正前方。至于周边其他学校名单，以及住户能否直接步行前往、具体路线，我还没有核实资料，不想误导你，我先确认一下。”
- B 检索 01_facts/location-and-connectivity.md 的 Nearby school connection，内容确认 Ground Floor / Level 9 podium 连接及有盖步道。回复：“目前能确认的是，项目内规划一所涵盖 SK 和 SMK、由教育部管理的学校，预计与 Phase 1 同步完成。规划从 Ground Floor 和 Level 9 podium 连接，并设有有盖走道，住户步行接送会比较方便。附近其他学校的名称和实际步行距离，我目前没有核实资料，不想乱报；我先帮您确认。”
- 两者都为周边学校名单/距离创建 OTHER 假请求，结果 OPEN。现有知识没有列出周边学校清单及实际距离，核实请求合理。B 直接回答步行通道；A 将已存在的步行信息当成未核实。

**判定：A 检索失败；B 有实质改善。** “步行更方便”是基于有盖通道的有限判断，不是承诺学校录取或距离。

### 3. 长者、升降机与布局

历史：客户说行动较慢的母亲可能同住；销售员询问日常需要；客户说母亲能走路，但楼梯和长距离困难。问题询问升降机配置以及布局是否适合。

- A 只检索 01_facts/unit-and-layout.md 的 Layout and room arrangement，未检索升降机信息。回复：“I don’t have confirmed details on the lift arrangement, so I’ll check the lift access and route to the units. The layout information shows no long internal corridor, which may mean less walking inside the home, but we’d need to check the actual plan and access route before judging if it suits your mum.”
- B 检索上述布局 passage，以及 01_facts/building-and-access.md 的 Phase 1 Building Structure 和 01_facts/overview.md 的 Phase 1。回复：“Each Phase 1 block has 4 passenger lifts and 1 Bomba lift. The unit layout avoids a long internal corridor, which may help reduce walking inside, but I can’t confirm the lift locations, route to the unit or exact accessibility from the information I have. I’ll verify those details against the approved plans before advising whether it may suit your mum.”
- 两边均发 TECHNICAL 假请求，询问实际升降机位置、路线和无障碍细节；结果 OPEN。这些细节在现有知识中确实没有。

**判定：A 检索失败；B 正确补足已验证升降机数量，并对未验证的路线/无障碍情况谨慎请求核实。** B 同时重复提供升降机事实（overview 与 building 两段），存在少量重复，但没有造成回复重复。

### 4. 四房需求与已验证单位

问题：“We need four bedrooms. Do you have any 4-bedroom layout?” 无预置历史。独立提供的标准单位事实为 900 平方尺、3 房 2 卫；两边也检索到 01_facts/unit-and-layout.md 的 Layout and room arrangement，其中说明三间卧室。

- A：“No, sorry—Pearl Residences Phase 1 only offers a 3-bedroom, 2-bathroom layout (900 sq. ft.), so there isn’t a 4-bedroom option. If four bedrooms are essential, this project probably won’t be the right fit.”
- B：“Pearl Residences Phase 1 doesn’t have a 4-bedroom layout; all units are 3 bedrooms and 2 bathrooms. If four bedrooms are essential, it may not be the right fit for you.”

两边均直接回答，没有不实改造暗示或多余支持请求。

**判定：两边通过；B 更简洁。**

### 5. 水灾、高压电缆与安全

历史：客户在地图上看到河流和电线；销售员说会查证。问题：“I am concerned about flooding and nearby high-voltage pylons. What verified flood mitigation or pylon safety information is available?”

- A 检索 01_facts/risks-and-sensitive-faq.md 的 High-Tension Cable / Pylon：Block 1B 电缆约 120 ft / 36 m，资料称最低要求 20 m，并提醒不能泛化到其他塔楼/单位；没有检索到水灾段落。回复说明 Block 1B 的范围，并称尚无已核实的水灾措施，发 TECHNICAL 请求。假结果 OPEN。
- B 错误检索 01_facts/location-and-connectivity.md 的 Nearby school connection，与安全问题无关；未检索水灾或电缆 passage。回复：“I don’t have verified details on the flood mitigation or high-voltage pylon safety to share yet. I’ll request confirmed information on both so I can answer accurately.” 发 TECHNICAL 假请求，结果 OPEN。

**判定：两边都有检索失败；B 更严重。** 水灾措施和电缆资料都存在于 Knowledge，但未全部交付。B 的 nearby 词扩展把 “nearby high-voltage pylons” 错误导向学校 passage，继而让模型错误地以为两项信息都不存在。A 至少交付了适用范围有限的电缆事实。

### 6. 管理费、月度总额与 RM162

历史：客户想先算经常性支出再决定看房；销售员说明管理费是其中一项，月供取决于价格及贷款条件。问题：“For 900 sq ft, does RM0.18 per sq ft mean RM162 a month? What other regular monthly ownership costs should I plan for?”

A、B 都检索到 01_facts/maintenance-and-management.md 的 Maintenance Fee：RM0.18/平方尺、含 sinking fund；如果换算标准 900 平方尺，要说明这是按费率计算的估值并待最新项目确认。核心销售证据还包括 pay-per-use clubhouse 角度，但检索结果没有提供该费用关系的完整事实 passage。

- A：“Yes—at the stated rate, 900 sq ft × RM0.18 = RM162/month, inclusive of sinking fund. Treat that as an estimate, subject to latest project confirmation. Beyond that, budget for your loan instalment and usage-based utilities and internet; I don’t have confirmed figures for any other Pearl Residences charges, so I’ll verify those rather than guess.”
- B：“Yes—900 sq. ft. × RM0.18 works out to an estimated RM162 a month, with the sinking fund included, subject to the latest project confirmation. I don’t have verified details on any other regular charges, so I’ll confirm those rather than guess.”
- 两边均创建 OTHER 假请求核实其他经常性费用，结果 OPEN。

**判定：RM162 回答正确；其他项目费用资料不足，核实请求可接受。** A 将水电和网络列为一般预算项目，但这些不是本次交付的项目事实。两边都没清楚说明 pay-per-use club facilities 是按使用付费，而非固定管理费包含项目；详细解释 passage 未被检索，属于小范围检索遗漏。固定物业费用、具体水电网金额在现有输入中没有可靠依据，不应编造。

## 用量和成本

| Arm | API 调用 | 输入 tokens | 输出 tokens | 平均延迟 | 中位延迟 | SUPPORT_REQUEST | 估算成本 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A 原始 Retriever | 6 | 12,532 | 6,189 | 9.44 秒 | 9.24 秒 | 5 | US$0.004661 |
| B 改进 Retriever | 6 | 12,981 | 6,144 | 9.30 秒 | 10.01 秒 | 5 | US$0.004694 |
| 总计 | 12 | 25,513 | 12,333 | — | — | 10 | **US$0.009355（约 US$0.01）** |

成本按 API 返回的 token 计数估算，并单独计算缓存写入、缓存读取及输出；费率取 [OpenAI GPT-6 Luna 模型定价](https://developers.openai.com/api/docs/models/gpt-6-luna)。未发生缓存读取。所有调用均完成；无重试、Customer Simulator 或 Judge 调用。

## 结论

**暂不建议整体替换。** 改进 Retriever 在中文学校接送和长者升降机问题上确实交付了原始版本缺少的事实；两边在四房及 RM162 问题上结果相近。但组合水灾/电缆查询暴露了明显的 nearby→学校误匹配，并丢失已有的水灾与电缆事实；价格用例两边也都未取到可谨慎引用的指示起价。一次小样本评估不足以证明整体替换更好，当前证据显示改进是混合的。

本次依用户要求只评估，没有改 Retriever、Sales Prompt、生产环境、部署或分支合并。
