# WhatsApp Sales Lab — Autonomous Loop 09

## 结论

**KEEP（范围有限）：** 当客户表示“如果有 show unit，我愿意安排看看”时，Agent 应确认是否同意让销售人员核实并联系；客户明确同意后，输出 `APPOINTMENT_HANDOFF`，并保留“视 availability 而定”的条件。独立盲评的 focused matched pair 中，基线只承诺稍后更新，候选在客户同意后完成了正式 handoff，没有声称已确认或已预约。

**NEEDS REVIEW（整体销售提升）：** 普通家庭客户的两组匹配比较都出现了真实的 `APPOINTMENT_HANDOFF`，但一个 pair 两边都成功，另一个 pair 的客户路线自然分岔。单次聚焦结果不能证明总体预约转化或说服能力普遍提高。Fresh holdout 因地点不符而自然退出，Agent 没有为了预约硬推看房。

没有修改 `brain/AGENT.md`、检索实现、预约规则或 Runtime。仅在 `app/agent.py` 增加针对条件性看房意愿的窄提示，并为该提示增加一个 prompt-contract regression assertion。

## Customer Simulator 设计与有效性

Loop 09 开始前，独立 Codex reviewer 审核了模拟协议和普通家庭角色，判为 READY。第一条真实基线揭示协议还需要要求实验负责人先检查 persona 卡，并明确阻止“每答完一题就换一个产品问题”的 FAQ 序列。协议因此增加了 persona 完整性检查和反 checklist 规则。Reviewer 指出初稿可能变成提问次数限制；文字改为允许围绕卡片或对话中已经披露的需要自然询问价格、地点等问题，并确认修订后的协议 READY。没有用此协议变化来改写已观察到的客户反应。

共模拟 **8 段旅程：7 段有效、1 段排除**。

| 旅程 | 判断 | 原因 |
|---|---|---|
| 基线 A | 排除 | 私人 persona 只写“有一般预算、会问实际问题”，没有具体主要决策因素；客户随后连续问价格、面积、楼层价格、可售楼层、厨房配置，独立 Judge 认为更像 FAQ 检查，而非这个角色的自然需求对话。保留记录作 simulator artifact，不用作转化证据。 |
| 基线 B | 有效 | 普通首次置业家庭；对三房布局表示认可，询问 show unit，并条件性表示若有单位便愿意安排。 |
| 候选 B | 有效 | 同一冻结 persona、独立 Customer Simulator。自然先问可负担价格，再同意与伴侣安排看房。 |
| Fresh holdout C | 有效 | 独立单身自住买家，因想靠近住在 KL Taman Desa 的母亲而看广告；查明项目在槟城后退出，属真实 fit mismatch。 |
| 基线 C | 有效 | 匹配家庭；客户在看到家庭相关的布局介绍后主动提出安排参观，Agent 完成 handoff。 |
| 候选 C | 有效 | 同一冻结 persona、独立 Customer Simulator；问起起步价后仍明确同意安排，并完成 handoff。 |
| Focused 基线 | 有效，聚焦诊断 | 开场已询问 show unit，因此从 viewing consideration 开始；客户之后表示若有单位愿意参观，Agent 只承诺更新。 |
| Focused 候选 | 有效，聚焦诊断 | 同一冻结 persona 和开场，独立 Customer Simulator；Agent 询问是否同意销售人员查证并联系，客户明确同意，之后输出 handoff。 |

Focused 开场主动问是否有 show unit，是为检查具体的“条件性意愿 → 同意转交”行为；它不证明 Agent 创造了最初的看房兴趣。Reviewer 审核后确认该角色和开场真实，但指出它预先带有 viewing consideration，故只作聚焦诊断。

## 盲评结果

Customer Simulator 与 Judge 均为不同的 Codex subagents；匹配版本使用同一冻结卡片和开场，但各自只看本版本的真实 SalesAgent 对话。Judge 不知道版本身份。固定 handoff 测试没有重跑；以下 `APPOINTMENT_HANDOFF` 均来自真实 SalesAgent 输出，但只记录在隔离 Sales Lab 文件里，没有向真实客户发送消息。

| 比较 | Invitation | Viewing consideration | Agreement to arrange | 正式 handoff | 结果 |
|---|---|---|---|---|---|
| 基线 B | Agent 建议看房，但未明确提问 | 有；客户询问 show unit | 条件性：“如果有 show unit，愿意安排” | 否；Agent 仅说等 availability 确认 | 在信息等待处停住 |
| 候选 B | Agent 明确邀请安排 | 有 | 是；客户同意并询问哪几天可看 | 是：`APPOINTMENT_HANDOFF` / `OPERATIONAL_BOOKING` | 有进展；无确认日期 |
| 基线 C | Agent 建议看 show unit | 有 | 是；客户请 Agent 帮忙安排 | 是：`APPOINTMENT_HANDOFF` / `OPERATIONAL_BOOKING` | 成功；无确认日期 |
| 候选 C | Agent 问是否需要协助安排 | 有 | 是；客户想参观并询问价格 | 是：`APPOINTMENT_HANDOFF` / `OPERATIONAL_BOOKING` | 成功；同时回答起步价 |
| Focused 基线 | 客户开场已问 show unit | 是 | 条件性兴趣；客户希望有结果后再看 | 否 | Agent 被动等 availability |
| Focused 候选 | 客户开场已问 show unit | 是 | 是；客户同意销售人员查 availability 并联系 | 是：`APPOINTMENT_HANDOFF` / `OPERATIONAL_BOOKING` | 聚焦假设得到支持；无预约确认 |

Focused 盲评的历史分（Discovery 20 + Desire 35 + Progression 35 + Naturalness 10）：基线 **66/100**，候选 **87/100**。主要差别是客户同意后是否进入正式 handoff，并非更多邀请或已证明的说服提升。该 pair 支持窄范围 KEEP；整体销售提升仍为 NEEDS REVIEW。

候选 B 的盲评也优于基线 B：它回应了新提出的价格问题，并在客户明确同意后转交。两条客户路线自然分岔，所以这不是严格的逐句因果比较。基线 C 与候选 C 两边均 handoff，没有显示候选胜出；候选 C 的家庭画面较泛，基线 C 的布局说明更具体。

Fresh holdout C 没有邀请看房、Agreement 或 handoff；这在此处是正确判断。Agent 第一轮没有直接给出已知地点，创建了地点支持请求；第二轮说清楚 Pearl Residences 位于 Penang Seberang Jaya，指出这不会让客户靠近 KL 的母亲。客户确认不合适并自然结束。这里的第一轮是检索/回答迟缓，不是买家阻碍，也不应计为转化失败。

## 完整代表性对话

### 排除的基线 A：FAQ 型模拟

**Customer:** Hi, I saw the ad for Pearl Residences. Can you share the price range and whether units are still available?

**SalesAgent:** Hi! A starting reference is around RM302k for an eligible Block 1B podium-blocked unit, after the 8% rebate on the listed base price. The exact unit’s total may differ with its car-park allocation and any applicable add-ons. I’ll check which units are currently available and confirm for you.

**Customer:** Okay, thanks—please let me know once you’ve checked. What are the unit sizes like?

**SalesAgent:** Phase 1 units are 900 sq ft, with 3 bedrooms, 2 bathrooms and a balcony. The availability check is still pending; I’ll update you once it’s confirmed.

**Customer:** That sounds like a good size. Does the price vary much by floor or view?

**SalesAgent:** Yes, it varies by floor band and facing. The Block 1B base-price references run from about RM328k for some lower blocked or pylon categories to RM358k for some higher-floor categories—around a RM30k spread. Some higher-floor references include two car parks, and the applicable rebate also depends on the unit category and parking, so the selected-unit total can differ.

**Customer:** Got it, thanks. When you’ve checked, could you let me know which floors and facings are available?

**SalesAgent:** The availability check is still pending. I’ll share the confirmed available floors and facings as soon as it comes back—I don’t want to guess at the current options.

**Customer:** Sure, thanks. Do the units come with any kitchen fittings, or are they mostly bare?

**SalesAgent:** The confirmed spec lists a stainless-steel kitchen sink with tap, plus a washing-machine tap. I can’t confirm whether cabinets or appliances are included from the details I have, so I’ll check rather than describe it as fully fitted.

**Customer:** Okay, good to know. Thanks—I’ll wait for your update on the fittings and unit availability.

### 匹配家庭：基线 B

**Customer:** Hi, saw the Pearl Residences ad. We’re renting a small place now and looking for our first home. The 3 bedrooms caught my eye—would that suit a couple with a young child?

**SalesAgent:** On paper, yes. Pearl Residences’ 900 sq.ft. layout has 3 bedrooms and 2 bathrooms, so you’d have a room for your child and a third room that could stay flexible for a study or guests. Since this is your first home, I’d recommend seeing the layout in person to judge whether the room sizes work for your family.

**Customer:** That sounds like it could work for us. Is there a show unit we can walk through?

**SalesAgent:** Seeing the layout in person should help you judge whether the rooms feel right for your family. I’ll check whether there’s a show unit available to walk through and confirm the arrangements.

**Customer:** Okay, if there’s a show unit, I’d be interested in arranging a time to see it.

**SalesAgent:** That makes sense. The show-unit availability is still being confirmed; if it’s available, seeing the 900 sq.ft. layout should help you judge whether the rooms feel right for your family. Once confirmed, we can arrange a suitable time.

**结局：** 客户表达条件性意愿；没有 `APPOINTMENT_HANDOFF`，对话停在 availability 待确认。

### 匹配家庭：候选 B

**Customer:** Hi, saw the Pearl Residences ad. We’re renting a small place now and looking for our first home. The 3 bedrooms caught my eye—would that suit a couple with a young child?

**SalesAgent:** It could be a practical fit. The Phase 1 homes have 3 bedrooms and 2 bathrooms across 900 sq. ft., so you could have your own room, a room for your child, and keep the third room flexible as your family’s needs change. Seeing the layout in person would help you judge whether the room sizes work for you—would you and your partner like to arrange a viewing?

**Customer:** That layout sounds like it could work for us, especially having a room for our child. Before we arrange a viewing, what’s the price range for the 3-bedroom homes? Around RM302k might be manageable for us.

**SalesAgent:** For an eligible Block 1B podium-blocked unit on Levels 1–4, the listed RM328k base less the 8% package works out to about RM301,760 (roughly RM302k), before any unit-specific car-park or add-on items. That’s close to the budget you mentioned. A viewing would let you and your partner see whether the 900 sq. ft. three-bedroom layout feels comfortable for your family—would you like to arrange one?

**Customer:** That’s close to what we had in mind, and seeing the layout would help us judge the fit. Yes, my partner and I would be interested in arranging a viewing. What days are available?

**SalesAgent:** Great—I’ll pass this to a salesperson to confirm the available days and coordinate a viewing for you and your partner. Seeing the layout should help you judge the room sizes and overall fit for your family. The visit isn’t booked until they confirm the arrangements.

**结构化结果：** `APPOINTMENT_HANDOFF`, `OPERATIONAL_BOOKING`, `appointment_readiness=APPOINTMENT_IN_PROGRESS`。客户同意安排；没有确认日期。

### Fresh holdout：地点不符，合理退出

**Customer:** Hi, I saw the Pearl Residences ad. I’m renting around OUG and thinking about buying somewhere nearer to my mum in Taman Desa. Could you tell me a bit about the project?

**SalesAgent:** A quick overview: Phase 1 homes are 900 sq ft, with 3 bedrooms, 2 bathrooms and a balcony. If you’re buying for your own home, that gives you a three-bedroom layout to consider. Since being closer to your mum is the main reason, I’m checking Pearl Residences’ exact location and access to Taman Desa rather than guessing. Would you be planning to live there yourself?

**Customer:** Yes, I’d be living there myself. Thanks for checking the location and access to Taman Desa—that’s the part I’m trying to understand.

**SalesAgent:** Thanks, that’s helpful. Pearl Residences is in Seberang Jaya, Seberang Perai, Penang. If you mean the Taman Desa near OUG in KL, it wouldn’t bring you closer to your mum, so based on your main reason for buying, I don’t think this is a good location fit. I’d rather be upfront than suggest otherwise.

**Customer:** Oh, I didn’t realise it was in Penang. My mum’s in Taman Desa, so that won’t really fit what I’m looking for. Thanks for checking.

### Focused pair：条件性 show-unit 意愿

**共同开场 — Customer:** Hi, we saw the Pearl Residences ad. We’re renting a small place and looking for our first home with our young child. The three-bedroom layout caught our eye—do you have a show unit we could walk through?

**基线 — SalesAgent:** That sounds like a sensible first home to explore for your family. Type A is 900 sq ft with 3 bedrooms and 2 bathrooms; the open-plan living and dining area gives you a shared family space, while the bedrooms keep sleeping space separate. I’ll check whether a show unit is available to walk through.

**基线 — Customer:** That sounds promising, especially having three bedrooms for our little one. If a show unit is available, we’d be interested in seeing how the rooms feel in person. Let us know what you find out?

**基线 — SalesAgent:** Absolutely—I’m still waiting for confirmation about the show unit, so I can’t confirm a walk-through just yet. If it’s available, seeing the three bedrooms and open living and dining area in person should help you picture how the layout could work for your family. I’ll update you once I have confirmation.

**候选 — SalesAgent:** A walk-through would help you see whether the 900 sq. ft., three-bedroom, two-bathroom layout feels right for your family. I can’t confirm show-unit availability from the information I have. Would you like a salesperson to check and contact you to arrange a visit if one is available?

**候选 — Customer:** Yes, please ask them to check if there’s a show unit and contact us. Seeing how the rooms feel in person would help us decide.

**候选 — SalesAgent:** Absolutely—I’ll ask a salesperson to check whether a show unit is available and contact you to arrange a walk-through if possible. Seeing the rooms and living space in person should help you judge how the layout feels for your family.

**候选结构化结果：** `APPOINTMENT_HANDOFF`, `OPERATIONAL_BOOKING`, `appointment_readiness=APPOINTMENT_IN_PROGRESS`。show-unit availability 与参观安排都保留条件，没有声称已确认。

## API、验证与限制

- 真实 SalesAgent：GPT-6 Luna / High；本轮 **21 次真实 API 调用，21 次完成、0 次失败**。每一种待测源码版本、每个独立 Sales Lab run-dir 均先用同一真实 entrypoint 和 fake HTTP transport 做过 dry-run。Customer Simulator 与 Judge 的 subagent 调用不计入 SalesAgent API 使用量。
- API usage：输入 **77,759 tokens**，输出 **31,018 tokens**，合计 **108,777 tokens**。API usage 没有返回 cost 字段，因此不估算费用。
- `python3 -m unittest discover -s . -t .`：**45 项通过**。测试中的预期 argparse 拒绝用例会打印错误用法，但整套测试退出成功。
- 价格对话只使用 Sales Lab 的 2026-08-14 假设：RM328,000 × 92% = RM301,760，作为约 RM302k 的合资格类别税后返利前价参考，不是单位 all-in 报价，也不是 2026-10 的现行优惠。候选 B 的算术与限定语正确。
- 没有调用 WhatsApp/Meta、Sheets、生产数据库、部署、真实销售人员或用户数据。所有 handoff 只是隔离实验记录，不会触达他人。

## 文件与 Git

- 改进：`sales_lab/customer_simulator.md`、`sales_lab/README.md`、`app/agent.py`、`app/test_runtime.py`。
- 每轮逐条对话、结构化决策、source hash 与 token ledger 保存在本目录的 `baseline/`、`candidate-b/`、`baseline-c/`、`candidate-c/`、`focused-baseline/` 和 `focused-candidate/`。
- 保留原来 Loop 04–06 的所有未跟踪/私有文件；未加入暂存。
- 本实验没有证明整体销售转化提升；只支持在明确条件性意愿下先征求 follow-up 同意、再正式 handoff 的窄规则。
