# WhatsApp Sales Lab — Autonomous Loop 10

## 结论

- **六张固定买家卡：已建立并通过独立审阅。** 六人分别代表首购情侣、小家庭、Perai 通勤自住买家、轻度浏览者、租金收入投资者、长期持有增值投资者。所有预算与背景均为虚构，且未提供给 SalesAgent。
- **基线：保留的 Sales Brain V3。** 六个有效买家对话中有三次明确同意由销售人员开始安排看房，并正确触发 `APPOINTMENT_HANDOFF`；没有确认具体预约。
- **候选改动：REVERT。** 候选提示改善了轻度浏览者的费用说明，但盲比没有胜过基线：按持久化的结构化动作，基线有 3 次交接，候选有 2 次。家庭买家在基线同意安排周末看房，候选则停在等待平面图；其他配对没有带来新增交接。候选改动已撤回。
- **Holdout：未运行。** 盲比没有证明候选优于基线，因此没有把失败候选带入额外付费测试。

## 方法与有效性

- 使用 Loop 10 的真实 `SalesAgent`（GPT-6 Luna / High）和原有知识检索、结构化输出及 Sales Lab 入口。每个有效试验目录都先用同一入口和 fake HTTP transport 完成 dry run；实际回复来自真实模型 API。
- 六张 persona 卡在基线前冻结。每段基线和候选对话由不同 Customer Simulator 子代理独立模拟；他们只看到自己的 persona 与实际客服回复。盲 Judge 只看到随机标记的 A/B 完整对话及私有 persona 真相，看不到版本映射。
- 一段 Perai 探索对话因我在一轮中直接起草了客户回复，违反独立模拟要求；两次 API 调用保留在账本中，但从配对评估中排除。Perai 的正式基线由新子代理和新 trial 重跑。
- 仅把明确同意开始安排看房计为 agreement；`APPOINTMENT_HANDOFF` 与预约确认分开。没有对任何买家声称预约已确认。
- 商业场景采用实验既有的 **2026-08-14** 假设：适用类别约 RM302k 的 rebate 后基础参考价。它不是 2026 年 10 月促销，也不是全包报价。

## 六位买家的配对结果

| Persona | 基线结果 | 候选结果 | 配对观察 |
|---|---|---|---|
| 首购情侣 | 明确同意销售员检查周末时段并联系；`APPOINTMENT_HANDOFF` | 明确询问两人可看的时段；`APPOINTMENT_HANDOFF` | 两者均达成安排看房同意；都没有确认日期。候选用更少回合连接第三间房与书房/客房用途。 |
| 小家庭 | 先讨论布局和儿童活动空间，随后要求本周末看房；`APPOINTMENT_HANDOFF` | 要求核对家具摆放的平面图，答应等图；未同意看房 | 候选停止在资料跟进；基线完成看房交接。这是基线领先的关键配对。 |
| Perai 通勤自住 | 认可地点，但在决定看房前要求核实其他固定月费；无邀请、同意或交接 | 核实 RM162 维护费并等待其他费用；无邀请、同意或交接 | 两者都没有推动到看房。基线更早直接给出通勤与维护信息；候选对费用跟进更细，但多一回合。 |
| 轻度浏览者 | 得到价格和布局信息后，被询问首付/贷款年限；结束对话 | 得到 RM162 维护费、贷款额需按假设计算，并可自愿再做月供估算；结束对话 | 候选减少资料索取且语气较合适；两者都没有建立看房兴趣或提出邀请。 |
| 租金收入投资者 | 讨论租客适配与持有成本后，同意由销售员核对看房选择并联系；`APPOINTMENT_HANDOFF` | 讨论家庭设施后，同意由销售员查询可用时段并联系；`APPOINTMENT_HANDOFF` | 两者均达成明确看房跟进同意；没有约定日期。候选增加家庭设施关联，但多一回合。 |
| 长期持有增值投资者 | 评估成熟周边、freehold 和路程信息，等待核实路线；无看房邀请/同意/交接 | 评估成熟周边、freehold 和已确认/规划设施，等待核实设施状态；无看房邀请/同意/交接 | 两者均停在买家主动要求的核实信息；没有虚构升值或租金回报。 |

**独立盲审判定：NEEDS REVIEW。** 盲审认为证据混合，不足以证明候选整体更好。复核匿名对话中的动作字段后，A=2 次、B=3 次 `APPOINTMENT_HANDOFF`；版本映射只在盲审结束后揭开，对应基线 3 次、候选 2 次。候选未通过基线门槛，所以按 Loop 10 的保留标准撤回。盲审文本中最初的总体句误写成两组各三次；本报告用原始结构化动作重新计数。

## 完整代表性对话

以下对话保持当时英文原文。邀请、看房考虑、同意安排、正式交接和已确认预约分别记录。

### 1. 首购情侣

**基线**

1. 客户：Hi, saw the Pearl Residences ad. We’re renting now and starting to look at our first place. What’s the layout like?
2. Agent：Pearl Residences’ Type A is 900 sq ft, with 3 bedrooms, 2 bathrooms and a balcony. There’s a foyer before the open-plan living, dining and kitchen area, plus a small storage area and no long internal corridor. For a first home, the three bedrooms give you flexibility while keeping the shared living space open. It could be useful to see how the layout feels in person—would you like to arrange a viewing?
3. 客户：Thanks, that helps. Do you know roughly how big the bedrooms are? We’re trying to picture whether one could work as a small study later.
4. Agent：I don’t have the exact bedroom dimensions to give you a reliable estimate. The project material says all the bedrooms are designed to fit a queen-size bed, so one could be a usable extra room, but whether it works well as a study depends on the desk and storage you’d want. The show unit would help you judge the proportions in person, too.
5. 客户：That’s fair. Is the show unit open on weekends? We might be able to have a look together.
6. Agent：I don’t have confirmed weekend opening hours for the show unit. Since you might come together, would you like me to ask a salesperson to check whether it’s open on a weekend and contact you to arrange a visit if possible?
7. 客户：Yes, please ask them to check and get back to us if weekend visits are available. We’ll work out a time together.
8. Agent：Thanks — I’ll have a salesperson check whether weekend visits are available and get back to you. If they are, they can coordinate a suitable time with you. **动作：`APPOINTMENT_HANDOFF`。** 周末时段待确认；没有预约日期。

**候选**

1. 客户：Hi, saw the Pearl Residences ad. We’re renting now and starting to look at our first place. What’s the layout like?
2. Agent：Pearl Residences’ Type A is 900 sq.ft., with 3 bedrooms, 2 bathrooms and a balcony. The living, dining and kitchen areas are open-plan, and the entrance foyer gives a little privacy before you reach the main living space. For a first home, the separate bedrooms could give you flexibility as your needs change, without a long internal corridor taking up space. Are you mainly looking for a home to live in yourselves?
3. 客户：Yes, it’d be for us to live in. We’re hoping the third bedroom could work as a study or guest room, but we’re not sure how roomy 900 sq.ft. feels in practice.
4. Agent：That’s fair—900 sq.ft. is easier to judge in person than from a number. Type A has an open-plan living, dining and kitchen area alongside three separate bedrooms, so the third room could stay flexible for a study and occasional guests. The best way to see whether it feels roomy enough for your setup is to view it. Would you like to arrange a viewing?
5. 客户：I think it could help us picture whether the rooms work for us. We’d want to come together—what viewing times are available?
6. Agent：Absolutely—seeing the layout together should help you judge whether the third bedroom works for your study/guest setup. I’ll pass this to a salesperson to check available viewing times for both of you. Nothing is booked until they confirm. **动作：`APPOINTMENT_HANDOFF`。**

### 2. 小家庭：候选停在平面图跟进

**基线**

1. 客户：Hi, we have a young child and our rental is getting a bit tight. Is the 3-bedroom layout practical for a small family?
2. Agent：It could be practical for a small family. The Type A is 900 sq ft with 3 bedrooms and 2 bathrooms, so you could have a separate room for your child while still having space to spend time together in the open-plan living and dining area. The layout also avoids a long corridor and includes a small storage area. I’d recommend viewing it to judge the room sizes and layout for yourselves; exact furniture fit should be checked against the approved plan.
3. 客户：That sounds more workable than what we have now. Is there a place for kids to play in the development?
4. Agent：There’s an approximately 10-acre landscaped facilities deck on Level 9, giving residents a substantial shared outdoor green space. I don’t have verified details on whether there’s a dedicated children’s playground or play equipment, so I’ll check that specifically for you.
5. 客户：A green space could still be useful. Do you know if kids can use it to play, or would that depend on the facilities rules?
6. Agent：The development’s facilities list does include a playground, alongside the roughly 10-acre landscaped Level 9 facilities deck. I can’t confirm whether the playground is on that deck or the specific access and supervision rules; use of the facilities would be subject to the management rules. The green space could still give your family an outdoor area to enjoy together.
7. 客户：That sounds worth seeing for ourselves. Could we visit this weekend?
8. Agent：Yes, I’ll pass your request to our salesperson to coordinate a visit this weekend and confirm an available time with you. It isn’t booked until they confirm. You’ll be able to assess the three-bedroom layout and room sizes in person. **动作：`APPOINTMENT_HANDOFF`。**

**候选**

1. 客户：Hi, we have a young child and our rental is getting a bit tight. Is the 3-bedroom layout practical for a small family?
2. Agent：It could be a practical fit for a small family. Type A is 900 sq ft with 3 bedrooms and 2 bathrooms; the living, dining and kitchen are open-plan, and the layout avoids a long internal corridor and includes a small storage area. The third bedroom also gives you flexibility as your child grows. A viewing would help you judge whether the space feels comfortable for your family—would you like to arrange one?
3. 客户：That sounds more practical than where we are now. I’m still wondering if there’d be enough room for our child to play once we’ve got the usual furniture in. Do you have a floor plan I could look at first?
4. Agent：The approved Type A floor plan would be the best way to judge how much play space remains with your usual furniture. I don’t have the drawing to share in this chat, but I can check with the team for it. Exact furniture fit will depend on how you arrange the space.
5. 客户：Yes, please check and send it over if you can. Seeing the layout would help us picture where the play space might be. Thanks.
6. Agent：Thanks — I’ll share the approved Type A plan when it comes through. It should help you compare the living/dining area with your usual furniture and judge the potential play space more realistically.
7. 客户：Okay, thanks. I’ll take a look when you have it. **结束：等待平面图；没有看房同意或交接。**

### 3. 轻度浏览者：候选费用回答更合适，但没有看房进展

**基线**

1. 客户：Hey, your Pearl Residences ad came up. Just browsing for now — what’s the starting price and what’s the main appeal?
2. Agent：For an eligible Block 1B podium-blocked unit, the starting base-after-rebate reference is about RM302k; that isn’t an all-in unit quote, as parking and add-ons can vary. The clearest practical appeal is the 900 sq ft layout with 3 bedrooms, 2 bathrooms and a balcony—there’s flexibility for family, guests or a work-from-home space. Are you browsing mainly for your own stay or as an investment?
3. 客户：Probably own stay, but I’m only browsing. The layout sounds practical—does that RM302k apply to many units, or just a specific one? I’d need to understand the monthly commitment too.
4. Agent：The ~RM302k is a category-level base-after-rebate reference for eligible Block 1B podium-blocked units on levels 1–4, not just one specific unit. I can’t confirm how many qualifying units are available. Monthly instalments depend on the loan amount, tenure and bank rate—roughly how much would you put down, and what loan tenure would you consider?
5. 客户：I haven’t worked those out—I was just trying to get a rough feel for the price. I’ll leave it there for now, thanks. **结束：客户仍在浏览；没有看房邀请或交接。**

**候选**

1. 客户：Hey, your Pearl Residences ad came up. Just browsing for now — what’s the starting price and what’s the main appeal?
2. Agent：As a starting reference, it’s about RM302k after the documented rebate on an eligible category’s base price; the selected unit’s car-park and other costs can change the total. The main appeal is a practical 900 sq ft layout with 3 bedrooms, 2 bathrooms and a balcony—one room could be useful as a guest or work space, if that suits you. Are you browsing for your own stay or mainly as an investment?
3. 客户：More own stay, if anything — I’m not planning a move right now. Three bedrooms at that price is more space than I expected, but I’d be careful about the monthly commitment on one income.
4. Agent：That’s a sensible thing to weigh on one income. For the 900 sq ft unit, maintenance is RM0.18 per sq ft inclusive of sinking fund—about RM162 a month. The loan instalment is separate and depends on your financing, so I wouldn’t guess at it. The three bedrooms give you flexibility if your needs change, and there’s no need to rush while you’re not planning a move. If you later want to explore affordability, I can work through an indicative instalment using your preferred down payment and tenure.
5. 客户：Thanks, that’s useful to know. Three bedrooms sounds practical, but I’m not looking to move at the moment, so no instalment estimate needed for now. I’ll keep the ad in mind. **结束：客户没有近期搬家计划；没有看房邀请或交接。**

### 4. 租金收入投资者：两版均交接

**基线**

1. 客户：Hi, I saw the Pearl Residences ad. I’m looking at a rental property — what makes this location and unit type practical for tenants?
2. Agent：For tenants, the Type A’s 900 sq. ft., 3 bedrooms, 2 bathrooms and balcony could suit a family or offer flexibility for sharers. Seberang Jaya is an established urban area, with connectivity toward Sunway Carnival Mall, Chai Leng Park and the Butterworth/mainland network. For your holding costs, the RM0.18 psf maintenance fee works out to about RM162 a month, including sinking fund. Phase 1 is expected to complete in Q4 2029, so it wouldn’t be an immediate rental option; actual rental demand and rates would still need checking. Are you mainly considering family tenants or shared occupancy?
3. 客户：Probably families, given the three bedrooms. The RM162 monthly maintenance figure is useful, and the 2029 completion timing helps set expectations. What other recurring costs should I factor in while it’s rented—or between tenants?
4. Agent：Aside from the RM162/month maintenance fee, which includes the sinking fund, owners commonly budget for assessment tax and parcel rent/quit rent where applicable, insurance, utilities and upkeep during vacancy, plus letting or management fees if using an agent. The applicable Pearl-specific charges and amounts aren’t verified here, so I’ll check rather than guess.
5. 客户：That’s a useful list. I’d want the verified Pearl-specific charges before I compare the numbers, but I don’t need them to decide whether it’s worth a closer look. Since completion is some way off, is there a show unit or a way to visit the area and assess the layout and surroundings?
6. Agent：The Type A layout is 900 sq. ft. with three bedrooms, two bathrooms and an open-plan living, dining and kitchen area, so you could judge how it might work for a family. You can also get a feel for Seberang Jaya and its nearby hubs. I’ll check the show-unit and visit options. Would you like a salesperson to contact you to arrange a visit if one is available?
7. 客户：Yes, please have a salesperson contact me if a show-unit or area visit can be arranged. I’d like to hear what’s available before settling on a date.
8. Agent：Thanks — I’ll have a salesperson check whether a show-unit or area visit can be arranged and contact you with the available options. No date is booked yet, so you can decide after hearing what’s possible. **动作：`APPOINTMENT_HANDOFF`。**

**候选**

1. 客户：Hi, I saw the Pearl Residences ad. I’m looking at a rental property — what makes this location and unit type practical for tenants?
2. Agent：For a rental property, the practical points are the established Seberang Jaya setting, with connectivity toward Sunway Carnival Mall, Chai Leng Park and the wider Butterworth/mainland network. The 900 sq.ft. layout has 3 bedrooms, 2 bathrooms and a balcony, giving flexibility for a family or shared household without assuming a particular tenant demand. The maintenance fee is RM162 a month, inclusive of sinking fund. One timing point: Phase 1 is expected to complete in Q4 2029, so this is a future rental play rather than immediate income. Are you mainly considering family tenants or a shared household?
3. 客户：Probably families, though I’d want to keep the unit flexible. Q4 2029 is quite a wait, so I’m weighing the carrying costs before completion too. Besides the RM162 maintenance fee, are there any other regular costs I should factor in?
4. Agent：The RM162/month maintenance fee is the only recurring property charge I can verify here, and it includes the sinking fund. I don’t have verified details on any other charges, especially during construction, so I’ll check rather than guess. That should help you assess the carrying costs for a future family-rental plan.
5. 客户：Yes, please check the other charges when you can. For a family tenant, I’d also be interested in what facilities residents can use.
6. Agent：For a family household, the listed facilities include a playground, jogging track, outdoor fitness area, open lawn, surau and kindergarten space, plus a BBQ pit, terrace garden and viewing deck. The clubhouse is pay-per-use. The final facilities schedule is the best reference for exact access and inclusions. I don’t have a confirmed update on other recurring or pre-completion charges yet, so I won’t guess.
7. 客户：The playground and kindergarten space could matter to families. I’d be open to seeing the show unit and getting a feel for the area. What viewing times are available?
8. Agent：That makes sense—the show unit would let you judge how the layout could work for a family tenant, and get a feel for the area yourself. I can’t confirm the current show-unit availability or viewing times. Would you like a salesperson to check and contact you to arrange a visit if possible?
9. 客户：Yes, please have a salesperson check the available viewing times and contact me. I’m flexible, but nothing is booked yet.
10. Agent：Sure—I’ll pass this to a salesperson to check the available viewing times and contact you to arrange a visit if possible. Nothing is booked yet. **动作：`APPOINTMENT_HANDOFF`。**

## API 用量与验证

| 试验组 | 真实 API 调用 | 输入 tokens | 输出 tokens | 总 tokens |
|---|---:|---:|---:|---:|
| 基线（含被排除的 Perai 探索试验） | 21 | 75,964 | 37,758 | 113,722 |
| 候选 | 20 | 74,958 | 29,878 | 104,836 |
| **合计** | **41** | **150,922** | **67,636** | **218,558** |

所有已登记请求均已完成，两个账本均未进入停止状态。单次调用的 token 数以 Sales Lab `ledger.json` / `ledger.jsonl` 中真实模型 usage 为准。未把 fake dry-run 计入真实 API 调用。

回归测试：`python3 -m unittest discover -v` — **45 tests passed**。

## Git 结果

- 最终 Brain：已恢复到 Loop 09 的稳定版本；候选提示没有保留。
- Loop 10 保留内容：六张经批准的合成 persona、完整基线/候选 transcript 与 usage ledger、匿名配对材料及本报告。
- 不合并、不部署、不触及生产 WhatsApp、Meta、Sheets、数据库或真实客户数据。
