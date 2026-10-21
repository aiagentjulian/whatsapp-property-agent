# Loop 11 — Appointment Setter Validation（最新分支验证）

## 状态：部分完成，按失败停止

远端最新版本 `083167b` 的 Sales Brain 已完成验证；**六组真实对话未能全部完成**。现有测试 **46 项通过**，六张 Loop 10 persona 的真实入口 fake-transport dry run 均通过。前三组开始真实对话后，家庭组第 3 次 live 调用报 `ValueError`；Sales Lab 将该组 ledger 标记 `stopped=true`。依照实验 fail-stop 约束，没有重试，也没有继续另外三组。

已记录 **9 次 live 尝试**：8 次成功并记录 **32,290 tokens**（输入 24,442、输出 7,848）；1 次失败调用的 token usage 未写入 ledger，因此真实总花费无法从本地记录确认。

| 客户 | 最新版对话结果 | 客户同意安排 Viewing | 正确 Handoff | Tokens（成功调用） |
|---|---|---:|---:|---:|
| 首购情侣 | Agent 回答布局后先问用途；确认 own stay 后介绍卧室并邀请，客户选择周末，Agent 正确输出 `APPOINTMENT_HANDOFF` | 是 | **是** | 11,097 |
| 小家庭 | Agent 回答户型后先问用途；介绍户外设施并提供 weekday/weekend 选择。客户表示周末方便、愿意看房并询问儿童游乐区；下一次 live 调用报 `ValueError`，没有得到 Agent 决策 | 是（客户已表达） | 否，调用失败 | 8,341 + 失败调用用量未知 |
| Perai 通勤自住 | 客户先要求价格和月费；Agent 给出类别起价与 RM162/月维护费并再次提供 weekday/weekend 选择。客户进一步询问基本单位总价；没有选择时间或同意 Handoff | 否 | 否 | 12,852 |
| 轻度浏览者 | 未进行 live 对话；只完成 fake dry run | 未测 | 未测 | 0 |
| 租金收入投资者 | 未进行 live 对话；只完成 fake dry run | 未测 | 未测 | 0 |
| 长期持有投资者 | 未进行 live 对话；只完成 fake dry run | 未测 | 未测 | 0 |

## 检查

- 最新版能在确认用途、呈现一个相关卖点后较早邀请，并明确给出 Weekdays / Weekends；首购情侣展示了从时间偏好到正确 Handoff 的完整路径。
- 家庭组的客户回答已经包含周末偏好和看房意愿，但调用失败，因此不能把它记作 Handoff 成功。
- Perai 客户要求总价后仍未决定看房，未将邀请误计为同意。
- 未修改代码或 Sales Brain。本轮只部分验证；剩余三类客户和家庭组最终交接状态未验证。
