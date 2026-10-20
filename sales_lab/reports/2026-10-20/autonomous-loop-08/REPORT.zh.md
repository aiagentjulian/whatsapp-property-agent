# WhatsApp Sales Lab — Autonomous Loop 08

## 结论：KEEP 定向地点检索；销售转化仍 NEEDS REVIEW

本轮围绕普通家庭自住客户，完成 2 个改进假设、5 段真实客户模拟旅程、1 次 fresh holdout，以及 1 个单独的预约交接功能场景。Customer Simulator 与 Independent Judge 使用 Codex 原生 subagents；SalesAgent 使用 GPT-6 Luna / High 和现有 OpenAI API。没有触碰 WhatsApp 生产运行、Meta、Google Sheets、Webhook、生产数据库或真实客户。

最终保留一项范围有限的 Knowledge Retrieval 修复：客户同一条消息同时询问地点与价格时，同时提供地点事实和价格资料。家庭配偶判断规则的候选没有显示明确的转化收益，已撤回。没有修改 Sales Brain、SYSTEM_PROMPT、预约规则或 handoff 逻辑。

## 主要发现

1. **混合问题的定向检索会丢地点。** 旧路径对“Where is it and what is the starting price?”进入价格定向检索后提前返回，只提供价格和套餐资料。第一位客户因此要重复询问 area / landmark。新增路由会在问题包含 where、location、area、nearest、landmark、commute 或 nearby 等地点意图时，一并返回 Exact location 与 External connectivity；价格请求仍保留原有定价资料。
2. **回答生活问题有助建立相关性，但不等于预约进展。** 家庭场景中，客户认可 open-plan 与家庭用途，却明确先要和伴侣看户型图。Agent 尊重这项门槛是合理的；两种版本都没有把它转成同意看房。
3. **处理月供顾虑后，具体、低压邀约产生了条件性意愿。** Fresh holdout 客户先说会和伴侣核对贷款。Agent 将 RM162 maintenance 作为总月支出的一部分，承认贷款才是主要月支出，并建议若两人认为数字可接受，可以一起看房。客户随后说若融资数字可行会回来谈看房。Judge 认为邀约很可能让“看房”成为明确下一步，但客户原先的财务条件并未改变；这不是 Agreement to Arrange。
4. **未发现虚构预约。** 真实模拟旅程均未出现客户明确同意开始安排或正式 handoff。只有另一个种子功能场景明确要求安排星期六看房，Agent 才输出 `APPOINTMENT_HANDOFF`。

## 盲评与历史加权比较

Independent Judge 使用 8 项 0–10 评分，并作匿名配对判断。历史加权分按既有映射计算：Discovery 20% + Desire/Visualization 均值 35% + Appointment Progression 35% + Realism 10%。

| 配对 | A 历史加权 | B 历史加权 | Judge 配对结论 | 预约证据 |
|---|---:|---:|---|---|
| 家庭空间、伴侣先看户型图 | 4.00 | 4.38 | B 略优；客户意愿没有可证明变化 | 两边均无 Viewing Agreement / Handoff |
| 价格 + 地点询问 | 2.80 | 5.25 | B 在实用信息与自住判断上更优；A 对地点兴趣略强 | B 客户说布局“reasonable”，不是看房意愿 |
| Fresh affordability holdout | 不适用 | Judge 均分 6.4/10 | KEEP 为有希望的单一 holdout 证据 | 客户条件性表示若贷款可行会回来谈看房；无 Agreement |

这些配对是小样本，客户路径有模拟脚手架，不能把历史分数差视为商业转化提升。Judge 指出家庭配对复用了相同客户措辞；价格地点配对的 B 开场较长，可能略像信息堆叠。Holdout 客户最后的回答也整齐地呼应了 Agent 的条件句，转化归因有限。

### Before / After：家庭空间

**A — 原版检索与销售判断**

客户：Hi, I saw the listing. We’re looking for a bit more room for the family. Is the living area comfortable for everyday family use?

Agent：The living, dining and kitchen are arranged open-plan, so your family can share one connected everyday space. The 900 sq. ft. layout also avoids a long internal corridor, helping make more of the space usable, and there’s an entrance foyer before the living area for a little privacy. A viewing would let you judge how the layout feels for your family.

客户：That sounds promising, but I’m trying to picture it with the kids and a dining table. Do you have a floor plan you can share?

Agent：I’ll check for the approved floor plan and share it if available. That should help you picture how a dining table could fit in the living area with the kids; I don’t want to guess at furniture fit without seeing the plan. （SUPPORT_REQUEST：核实可分享的 approved Type A plan）

客户：Thanks for checking instead of guessing. The open layout sounds useful with the kids, but my partner would prefer to see the layout first before we arrange a viewing. I’ll check with them and get back to you.

Agent：Of course—it makes sense to look at the plan together first. I don’t want to guess about dining-table fit; once the approved Type A plan is confirmed as shareable, I’ll send it over so you and your partner can see whether the open living and dining space works for family meals before deciding about a visit. （REPLY；未邀约、未同意、未交接）

**B — 家庭配偶规则候选（已撤回）**

客户：Hi, I saw the listing. We’re looking for a bit more room for the family. Is the living area comfortable for everyday family use?

Agent：For family use, the Type A is 900 sq. ft. with 3 bedrooms and 2 bathrooms. The living, dining and kitchen areas are open-plan, and the layout avoids a long internal corridor, so the shared space isn’t broken up by a lengthy hallway. Whether it feels comfortable will depend on your family’s needs and furniture, but a viewing would let you judge the proportions in person. Happy to arrange one if you’d like.

客户：That sounds promising, but I’m trying to picture it with the kids and a dining table. Do you have a floor plan you can share?

Agent：I don’t have the floor-plan image to attach here, so I’ll check for the approved Type A plan. What I can confirm is that the entrance foyer leads into an open-plan living, dining and kitchen area, with three bedrooms and a small storage area. I wouldn’t want to guess how a particular dining table fits without the plan—exact furniture fit should be checked against it. （SUPPORT_REQUEST：核实可分享的 approved Type A plan）

客户：Thanks for checking instead of guessing. The open layout sounds useful with the kids, but my partner would prefer to see the layout first before we arrange a viewing. I’ll check with them and get back to you.

Agent：Of course—it makes sense for you both to see the approved layout first, especially to judge the dining-table fit. I’ll share it if it’s confirmed available; then you can decide together whether a viewing would be useful. （REPLY；未进一步邀约、未同意、未交接）

**判断：** B 的户型说明稍具体，但配偶规则没有让客户更愿意开始安排看房。Judge 对 B 略有偏好，但预约进展同为 2/10；该销售规则没有保留。

### Before / After：价格与地点

**A — 旧检索路径（候选前）**

客户：Hi, I saw Pearl Residences advertised. We’re looking for a place to stay ourselves—could you share roughly where it is and the starting price?

Agent：For an eligible category, the starting reference is about RM302k after rebate. That’s based on the base price, not an all-in unit quote. I’ll confirm the exact location for you too. （SUPPORT_REQUEST：核实地点）

客户：Thanks, that gives us a rough idea. Could you share the area or nearest landmark once you’ve confirmed it? We’re trying to work out the commute.

Agent：The area is Seberang Jaya. Project materials reference connectivity toward Sunway Carnival Mall, Chai Leng Park and Butterworth, which may help you orient your commute. I don’t yet have a verified exact address or travel times, so I don’t want to guess.

客户：That helps, thanks. Seberang Jaya might work for us; we’ll check it against our daily commute. Do you have a project brochure or map we can look at?

Agent：I can confirm it’s in Mukim 1, Seberang Jaya, 13700. I don’t have a verified brochure or map link to share right now, so I’ll check whether there’s a shareable one. That should help you compare the location with your commute. （SUPPORT_REQUEST：核实可分享的 brochure/map；自然停止）

**B — 定向地点检索修复**

客户：Hi, I saw Pearl Residences advertised. We’re looking for a place to stay ourselves—could you share roughly where it is and the starting price?

Agent：Pearl Residences is in Seberang Jaya on Penang mainland, with connectivity toward Sunway Carnival Mall. The starting reference is around RM302k after the 14 August package rebate for eligible categories; that’s based on the listed base price, not a guaranteed all-in quote, as parking and add-ons vary. The units are 900 sq. ft. with 3 bedrooms and 2 bathrooms. Does that layout suit what you have in mind for your own stay?

客户：Three bedrooms sounds useful, and 900 sq. ft. could work for us. We’re still comparing the commute and overall costs, though, so I’d want to see the floor plan before deciding if the layout suits us.

Agent：That makes sense—the floor plan should help you judge whether 900 sq. ft. works for you. The concept shows an open-plan living, dining and kitchen area, three bedrooms, two bathrooms, a balcony and a small storage area. For ongoing costs, the stated maintenance is RM0.18 per sq. ft. including sinking fund, or about RM162/month for 900 sq. ft. (excluding utilities and other costs). I’ll get the approved floor plan for you. Where do you usually commute to? That’ll help us assess whether Seberang Jaya suits your route. （SUPPORT_REQUEST：核实 approved Type A floor plan）

客户：Thanks, that’s useful, especially the maintenance estimate. We commute toward George Town a few days a week, so we’ll need to check how the location works for us. The layout concept sounds reasonable, but we’ll wait to see the approved plan before judging the space.

Agent：That’s a sensible commute to check. Seberang Jaya has connectivity toward Butterworth and the wider mainland road network, but I don’t have a verified George Town drive time, so I wouldn’t want to guess. Once you’ve had a chance to review the approved plan, you can judge whether the layout works and test your usual weekday route before deciding on a visit. （REPLY；客户尚未同意看房）

**判断：** B 一开始就解决了地点和价格问题，随后将户型及维护费连到客户的自住与月支出考虑。客户具体认可三房、900 sq. ft. 和维护费，但仍以批准户型、通勤和总成本作为决定门槛；没有邀请或 agreement。此处保留的只是针对检索遗漏的修复，不代表客户已准备参观。

### Fresh holdout：条件性看房意愿

客户：Hi, I came across Pearl Residences. We’re considering a place for our own stay, but still comparing locations and budget. What area is it in, and roughly where do prices start?

Agent：Pearl Residences is in Seberang Jaya on Penang Mainland, with connectivity toward Sunway Carnival Mall and Chai Leng Park. The starting reference is about RM302k after the 8% rebate for an eligible podium-block category, based on the 14 Aug 2026 package; it’s a base-price reference, not a guaranteed all-in quote for a selected unit. For own stay, the standard Type A offers 900 sq ft, 3 bedrooms, 2 bathrooms and a balcony.

客户：Thanks, that gives us a useful starting point. Seberang Jaya could work for us, and that price is in the range we’re exploring, though we’d need to understand the monthly costs before judging affordability. Is there an estimated maintenance fee?

Agent：The maintenance fee is RM0.18 per sq ft per month, inclusive of the sinking fund. For the 900 sq ft Type A, that works out to about RM162 a month—a useful baseline for your own-stay budget before factoring in financing. Selected clubhouse facilities are pay-per-use.

客户：That’s helpful, thanks. We’re comparing a few places, and the loan payment will be the main monthly cost for us. I’ll check the numbers with my partner and get back to you if it looks workable.

Agent：That makes sense—the loan instalment is the key figure to check. The estimated RM162 maintenance fee gives you one part of the monthly cost, but not the full financing picture. If the numbers work for you both, I’d recommend viewing together so you can see whether the home feels right for your own stay before comparing further. There’s no need to decide on the spot.

客户：Thanks, that’s fair. We’ll check the financing with my partner first, and if the numbers look manageable, we’ll get back to you about a viewing.

**结果：** 这是 Agent 邀约后客户本人提出的条件性后续意愿，未同意开始安排看房。Judge 认为低压邀约可能帮助客户把参观看作下一步，但贷款可负担性仍是客户自己的先决条件。没有 Handoff。

## Appointment Handoff 功能测试

另设客户明确说：“My partner and I have reviewed the project details together. We would like to start arranging a viewing this Saturday afternoon. Please pass our request to your salesperson to confirm a time.”

- 真实 SalesAgent 判定：`APPOINTMENT_HANDOFF`；`appointment_readiness=APPOINTMENT_IN_PROGRESS`；原因 `OPERATIONAL_BOOKING`。
- 决策通过隔离的 `Runtime.process_inbound` 路径及现有就绪状态校验；状态变为 `owner=HUMAN`、`ai_session_status=ENDED`，记录 1 个 `APPOINTMENT_HANDOFF`。
- 面向客户的交接文本表示团队会跟进确认可用时间；没有宣称已订好。
- 功能测试使用临时 SQLite 与不发送模式，没有触达 Meta 或客户。

此种子功能测试只证明明确同意后的识别与交接链路可用，不代表 Agent 说服了模拟客户。

## API 与验证

- 自然客户旅程：5 段；真实 SalesAgent 调用 15 次。另有预约 handoff 种子功能调用 1 次；共 **16 次**真实 API 调用，16 次完成，0 次失败。
- 用量合计：输入 **57,389 tokens**；输出 **24,752 tokens**；总计 **82,141 tokens**，其中可见 reasoning **16,844 tokens**。
- API 返回未提供实际收费字段；没有估算费用。
- 最新完整回归：`python3 -m unittest discover -s . -t .`，**45 项通过**。包括混合价格与地点检索、地点查询和 handoff 状态测试。
- 对真实 SalesAgent 调用前使用同一 runner 的 fake transport dry-run。真实 handoff 功能测试额外把真实 Agent 决策通过临时数据库的应用 Runtime 校验。

## 文件与 Git

- 保留改动：`app/knowledge.py` 定向地点检索；`app/test_sales_lab_retrieval.py` 两个回归测试；本报告及 loop 08 的逐轮 ledger / 对话 JSON。
- 已撤回：配偶一起看房的单条 Sales Judgment 候选；盲评没有证明其带来更多预约意愿。
- 现有用户的私有未跟踪文件未加入暂存。API 实验记录均在 `sales_lab/reports/2026-10-20/autonomous-loop-08/`。
- 最终判断：**KEEP 定向地点检索；NEEDS REVIEW 商业转化提升**。独立评估与 holdout 支持更完整、贴合买家需求的引导，但自然旅程无一达到客户 Agreement to Arrange。没有改动预约交接逻辑。
