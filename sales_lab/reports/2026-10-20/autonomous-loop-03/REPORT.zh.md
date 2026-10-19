# Sales Lab Loop 03 — 最终报告

**结论：REVERT 销售 Brain 候选；保留并提交 18 次预算控制、测试和报告。** 本轮没有达到“真实销售能力改善”的验收线。最好的完整三场景候选仍低于已验证的 Loop02 版本，Holdout 也暴露了过早建议看房的问题。`brain/AGENT.md` 已恢复到 Loop02 的稳定版本。

## 执行与评分

共完成 3 轮针对性修复尝试。Round 1、2 各跑了 Own Stay、Genuine Interest 和 Early Exploration 的两轮对话；Round 3 聚焦 Own Stay 的两轮对话。最后使用新建、未用于修复的价格顾虑 Holdout，对 Loop02 稳定版本和 Round 3 候选各跑两轮。Judge 在评分完成后才收到版本映射。

沿用原四维评分权重：Effective Discovery 20%、Product Connection / Buying Desire 35%、Sales Progression / Appointment Opportunity 35%、Natural Conversation 10%。可视化/欲望、销售指导和对话真实感另行评分，不混入原权重。独立校准将 Loop02 家庭对话的可视化从 8 分下调到 6.5–7 分：房型与需求相关、客户表示可能合适，并不等于生动的生活场景或强购买欲望；邀请看房也不能单独算作客户兴趣。

| 版本 | Own Stay | Genuine Interest | Early Exploration | 三场景均分 |
|---|---:|---:|---:|---:|
| Loop02 已验证稳定版 | 6.78 | 6.44 | 6.63 | **6.62 / 10** |
| Loop03 Round 1 | 6.61 | 6.22 | 6.29 | **6.37 / 10** |
| Loop03 Round 2 | 6.24 | 6.47 | 6.54 | **6.42 / 10** |
| Loop03 Round 3（仅 Own Stay） | 6.53 | — | — | 不可作三场景均分 |

Round 1、2 的完整候选均低于稳定版；最佳完整候选 Round 2 仍低 0.20 分。Round 3 的 Own Stay 比 Round 2 提高 0.29 分，但仍比稳定版低 0.25 分。变化都很小，远未达到要求的实质改善。

## 修复尝试与真实对话

**Round 1** 调整了“生活化呈现”的许可措辞，允许在有根据时描述现实可能性，同时明确禁止编造事实或日常习惯。盲评发现 Sales Brain 开头仍然限制“想象房间用途”，与后文允许条件式呈现相冲突。客户对三个场景的反应总体有帮助，但没有形成稳定的购买欲望或看房推进。

**Round 2** 删除了这处矛盾。结果没有扩大可视化或购买欲望。Own Stay 客户说布局“could suit us”，随后明确要求完整月费再决定下一步；不邀约符合客户设下的边界。Genuine Interest 候选先问自住还是投资，得到有效目的信息，但随后仍只处理价格与费用，没有产生更具体的产品吸引力。Early Exploration 候选没有追问预算、没有硬邀约，并正确说明价格与停车配置尚未匹配。

**Round 3** 对明确需求更直接地连接房间用途与家庭需要。候选回复：“With three bedrooms, your child can have a separate room, and there’s another bedroom for your household’s needs.” 客户回应布局“does sound promising”，说明家庭用途表达带来有限的具体价值；但 Judge 认为第二间卧室仍泛泛而谈，没有形成具体生活画面。客户仍先询问其他费用和停车成本。Round 3 没有充分对三场景复测，因此不能据此声称整体改善。

对照稳定版的家庭对话，稳定版说：“One bedroom can be your child’s separate room”并在首轮建议看房，客户明确回复：“I’d be open to seeing the layout,” 但要求先确认价格和其他费用。Round 3 的客户只说布局听起来 promising，并没有表达看房意向。这个差异不能全归因于 Agent 文案，因为模拟客户两版本的实际回复不同；但真实对话证据也没有显示新候选更强。

## Holdout

同一个新价格顾虑场景下，Round 3 候选的首次回复解释价格组成、提到父母的布局适配，并说：“I’d recommend viewing it while you compare.” 客户随即表示希望先看到具体单位价格及包含项目，再决定是否安排看房。Judge 将该邀请判为过早；候选第二轮接受客户顺序，承诺先给确认后的价格。

Loop02 稳定版没有先邀约，而是承认价格需要合理、说明布局可能更适合日常生活，并承诺查明单位价格与包含项目。客户明确说拿到总价后再判断值不值得看。Holdout 评分为稳定版 **6.74/10**、Round 3 候选 **6.57/10**。候选对价值的解释稍具体，客户信心有所增加；但邀请先于客户要求的价格明细，自然度和推进评分下降。没有任何版本获得预约同意或完成正式 Handoff。

## 事实、Handoff 与限制

三轮主要场景的 900 平方英尺、3 房 2 卫及 RM162 维护费计算均符合 Knowledge；历史基础价有注明非当前总价，未确认费用保持待核实。Holdout 候选没有作无障碍承诺，并明确房型信息不能证明无障碍配置。Judge 提醒 RM10,000 upgrade package 与其他当前优惠应继续分清楚；没有发现严重事实错误。

所有对话都清楚区分邀请、客户看房兴趣、预约同意与正式 Handoff。Holdout 候选在客户明确先要价格后恢复了正确顺序；没有虚构预约、客户同意或人工交接。

本轮模拟客户对不同版本的实际回答有差异，属于小样本对话判断，不能推断转化率变化。三轮候选均没有证明客户更想购买或到访；剩余问题是把已知需求变成具体但不过度假设的生活价值，并判断何时推荐看房而不越过客户明确的价格条件。

## API 与复现

- 真实 SalesAgent 推理：**18/18 次**，GPT-6 Luna / High；没有为 Customer 或 Judge 调用付费 API。
- 可得 Usage：输入 70,744 tokens、输出 32,782 tokens、合计 **103,526 tokens**（其中报告的 reasoning tokens 为 22,140）。本次没有可用的美元成本明细。
- 每个候选版本均先通过 Sales Lab 的真实入口及 fake HTTP transport 验证；`app.test_sales_lab`、`app.test_sales_lab_retrieval`、`app.test_runtime` 共 26 项通过，`git diff --check` 通过。
- 逐轮对话、Judge 证据、客户反应、盲评映射、Usage 和预算账本均保存在本目录。客户隐藏动机没有写入 Agent 输入。

## 最终处置

**REVERT** Loop03 的 `brain/AGENT.md` 销售行为修改，保留 Loop02 稳定版本。**保留**本轮为遵守 18 次上限加入的 `--api-limit`、测试、README 更新及实验报告。当前没有理由将 Loop03 销售 Brain 改动推入分支。
