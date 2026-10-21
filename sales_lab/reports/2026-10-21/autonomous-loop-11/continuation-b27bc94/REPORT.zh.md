# Loop 11 — Appointment Setter Validation

## 执行摘要

在 `codex/sales-lab-v1` 最新提交 `b27bc94` 上完成验证。自动测试 **47 项通过**；新增 `ValueError` 诊断测试单独通过，确认失败原因写入 ledger 且不会重试。随后在全新目录完成剩余四组真实 SalesAgent 对话，使用冻结的 Loop 10 personas、GPT-6 Luna / High SalesAgent 和独立 Customer Simulator。未修改 Sales Brain 或增加销售规则；没有发送真实 WhatsApp 消息，也没有部署。

六组共记录 **19 次成功 API 调用、79,166 tokens**；旧小家庭失败调用的 token 用量不可得，故总实际用量至少为此数。该旧失败账本保留原状，未重置或重试。续跑四组账本记录 11 次调用、46,876 tokens，均成功。

| 固定客户 | 对话结果 | 愿意开始安排 Viewing | Handoff 结果 |
|---|---|---:|---|
| 首购情侣 | 回答布局与用途后较早邀请；客户选择周末 | 是，明确选择周末 | 是，`APPOINTMENT_HANDOFF` |
| 小家庭 | 首次运行回答户型；客户表示周末愿意看并问儿童户外设施，下一次调用报 `ValueError`。新目录完整重跑：答复约 10 英亩户外绿地，说明不能确认具体设施，并核对周末时段 | 是，明确选择周末 | 是，`APPOINTMENT_HANDOFF`；旧失败记录仍保留 |
| Perai 通勤自住 | 询问价格/月费后收到回答和 weekday/weekend 邀请，继续询问单位总价；没有选择时间 | 否，尚未接受邀请 | 否；未误判邀请为同意 |
| 轻度浏览者 | 表示只是浏览、价格超预期且暂不愿看房；Agent 继续回答月费和贷款估算问题，客户决定暂时继续浏览 | 否，明确暂缓 | 否；自然结束，未强推 |
| 租金收入投资者 | 先回答月费和预计完工时间；客户确认周末合适并同意查询示范单位及周末时段 | 是，明确同意开始查询 | 是，`APPOINTMENT_HANDOFF`，转人工确认两项并跟进 |
| 长期持有增值投资者 | 客户表示愿意周末看房，但先询问产权和距离；Agent 不猜测，转人工确认事实及可用周末时段 | 有条件愿意，等待事实确认 | 是，`MANDATORY_HANDOFF`（`HIGH_RISK_FACTUAL_UNCERTAINTY`）；交接内容含周末看房跟进，但动作码不是 `APPOINTMENT_HANDOFF` |

## 结论

简化 Sales Brain 在 3 组取得明确的周末看房意愿并正确进入 `APPOINTMENT_HANDOFF`；长期持有组给出有条件的周末意愿，并因产权/距离未知而正确转人工核实，但使用的是 `MANDATORY_HANDOFF`。轻度浏览者和 Perai 客户未同意，系统没有把邀请当作预约。对话总体没有出现问卷式连续追问；租金投资者多问一轮与其问题相关的事实后取得同意。Loop 11 验证完成，旧失败的原始调用成本仍不可得。
