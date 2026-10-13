"""Finalize and render the Chinese V2 Lite paired-evaluation report."""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from .v2_lite_eval import CRITERIA, SCENARIO_IDS


def cost(usage: dict) -> float:
    details = usage.get("input_tokens_details") or {}
    input_tokens = int(usage.get("input_tokens", 0) or 0)
    cached = int(details.get("cached_tokens", 0) or 0)
    writes = int(details.get("cache_write_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)
    regular = max(0, input_tokens - cached - writes)
    return (regular * 0.10 + cached * 0.01 + writes * 0.125 + output_tokens * 0.50) / 1_000_000


def finalize(report: dict) -> dict:
    roles: dict[str, list[dict]] = {"sales_agent": [], "customer_simulator": [], "blind_evaluator": []}
    latencies: dict[str, list[int]] = {key: [] for key in roles}
    for row in report["dialogues"]:
        for turn in row.get("turns", []):
            if turn.get("openai_usage"):
                roles["sales_agent"].append(turn["openai_usage"])
                if turn.get("agent_latency_ms") is not None:
                    latencies["sales_agent"].append(turn["agent_latency_ms"])
            if turn.get("customer_simulator_usage"):
                roles["customer_simulator"].append(turn["customer_simulator_usage"])
                if turn.get("customer_simulator_latency_ms") is not None:
                    latencies["customer_simulator"].append(turn["customer_simulator_latency_ms"])
        judgement = row.get("judgment") or {}
        if judgement.get("usage"):
            roles["blind_evaluator"].append(judgement["usage"])
            if judgement.get("latency_ms") is not None:
                latencies["blind_evaluator"].append(judgement["latency_ms"])
        # Remove stale diagnostics from the first interrupted judge attempt after its saved transcript
        # was successfully judged during resume.
        if row.get("blind_judgment") == "complete":
            row.pop("error", None)
            row.pop("judgment_error", None)
    role_summary = {}
    in_total = out_total = completed = 0
    completed_cost = 0.0
    for role, usages in roles.items():
        ins = sum(int(u.get("input_tokens", 0) or 0) for u in usages)
        outs = sum(int(u.get("output_tokens", 0) or 0) for u in usages)
        cached = sum(int((u.get("input_tokens_details") or {}).get("cached_tokens", 0) or 0) for u in usages)
        writes = sum(int((u.get("input_tokens_details") or {}).get("cache_write_tokens", 0) or 0) for u in usages)
        role_cost = sum(cost(u) for u in usages)
        completed += len(usages)
        in_total += ins
        out_total += outs
        completed_cost += role_cost
        samples = latencies[role]
        role_summary[role] = {"completed_calls": len(usages), "input_tokens": ins, "cached_input_tokens": cached,
                              "cache_write_input_tokens": writes, "output_tokens": outs,
                              "estimated_completed_call_cost_usd": round(role_cost, 6),
                              "latency_ms_mean": round(statistics.mean(samples)) if samples else None,
                              "latency_ms_median": round(statistics.median(samples)) if samples else None}
    judge_attempts = report.get("usage", {}).get("attempts_by_role", {}).get("blind_evaluator", len(roles["blind_evaluator"]))
    failed = max(0, int(judge_attempts) - len(roles["blind_evaluator"]))
    failed_input_est = int(roles["blind_evaluator"][0].get("input_tokens", 0)) if failed else 0
    failed_output_ceiling = 3000 if failed else 0
    failed_ceiling = (failed_input_est * 0.10 + failed_output_ceiling * 0.50) / 1_000_000
    all_samples = [value for values in latencies.values() for value in values]
    prior = report.get("usage", {})
    report["usage"] = {
        "provider": "OpenAI Responses API", "model": "gpt-6-luna",
        "request_attempts": int(prior.get("request_attempts", completed + failed)),
        "successful_responses_with_usage": completed, "failed_or_incomplete_responses": failed,
        "input_tokens_successful_responses": in_total, "output_tokens_successful_responses": out_total,
        "completed_responses_cost_usd": round(completed_cost, 6),
        "failed_response_usage": "Not retained for the initial incomplete xhigh judge response; estimated separately from the identical retry input and the original 3,000-token output ceiling.",
        "failed_response_input_tokens_estimate": failed_input_est,
        "failed_response_output_tokens_ceiling": failed_output_ceiling,
        "failed_response_cost_ceiling_usd": round(failed_ceiling, 6),
        "estimated_total_cost_range_usd": [round(completed_cost, 6), round(completed_cost + failed_ceiling, 6)],
        "pricing_usd_per_million_tokens": {"input": 0.10, "cached_input": 0.01, "cache_write_input": 0.125, "output": 0.50},
        "pricing_basis": "Standard GPT-6 Luna text pricing; cached reads and cache writes use usage-reported token detail. One failed response is estimated separately.",
        "latency_ms_mean_successful_calls": round(statistics.mean(all_samples)) if all_samples else None,
        "latency_ms_median_successful_calls": round(statistics.median(all_samples)) if all_samples else None,
        "by_role": role_summary,
    }
    report.pop("stop_reason", None)
    report["status"] = "complete" if completed == 104 and len(report["dialogues"]) == 12 else report["status"]
    return report


def evidence_markdown(row: dict) -> list[str]:
    judgment = row["judgment"]
    lines = [f"**盲评：{row['composite_score_1_to_5']}/5**；客户回合 {row['customer_turn_count']}；结束方式：`{row['end_reason']}`。", "",
             "| 维度 | 分数 | 逐轮证据 |", "|---|---:|---|"]
    for key in CRITERIA:
        evidence = str(judgment.get("evidence", {}).get(key, "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {key.replace('_', ' ')} | {judgment['scores'][key]} | {evidence} |")
    if judgment.get("factual_issues"):
        lines += ["", "盲评指出的事实问题："]
        lines.extend(f"- {issue}" for issue in judgment["factual_issues"])
    if judgment.get("overall_note"):
        lines += ["", "盲评摘要：" + judgment["overall_note"]]
    return lines


def render(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# V2 Lite Sales Evaluation：六组盲测报告", "",
        f"运行 ID：`{report['run_id']}`；状态：**{report['status']}**。", "",
        "## 结论", "",
        "**建议暂时保留 main 上的 V2。** V2 Lite 的平均盲评分为 4.479/5，原 V2 为 4.333/5，配对平均差 +0.146 分。Lite 在 6 个场景中 4 胜、1 平、1 负；优势方向一致偏正，但总体差距不大，六个场景不足以证明自然度、理解或销售判断有稳定提升。没有安排第二轮付费评测，也没有修改任一提示词。", "",
        "Lite 在预算场景得分最高，也更好地跟随了设施场景从儿童设施转向户外绿地的关注点；在家庭场景两版都重复等待中的学校/价格信息，在老人入住场景 Lite 漏答了知识中已确认的电梯配置。", "",
        "## 对照设置", "",
        f"- 原 V2：main `{report['git']['main_base']}` 中的 `brain/AGENT.md`。Lite：`codex/v2-lite-prompt` `{report['git']['lite_commit']}`。提交间唯一变更文件为 `brain/AGENT.md`。两臂运行相同的 main V2 `SalesAgent`、系统提示、结构化输出、检索、项目 Knowledge 与模拟运营接口；只在调用中分别注入各自工作简报。",
        "- Sales Agent：GPT-6 Luna / High；Customer Simulator：GPT-6 Luna / Medium；Blind Judge：GPT-6 Luna / Extra High。客户每轮按情境自然回应，可停止或继续；没有最低轮数，最多 12 个客户回合。六组实际各臂为 1–6 轮，未有会话触达上限。",
        "- 盲评收到对话、买家真实背景/需求和项目事实资料，不收到臂名称或提示词身份。评分不奖励更长对话、提前结束或单纯要求看房。没有任何会话请求看房；未生成正式转人工或预约交接。",
        "- 运营使用会话内存储的 fake adapter：SUPPORT_REQUEST 只写入内存并保持 OPEN。没有 WhatsApp、CRM、客户数据库、真实跟进、预约、部署或其他外部操作。",
        "- 六组场景来自既有 V2 评测 fixture：家庭自住、首次购房、预算/月供、设施生活方式、需求可能变化、简短犹豫回复。", "",
        "## 六组结果", "",
        "| 场景 | 原 V2 | V2 Lite | Lite − V2 | 客户回合 V2 / Lite | 简述 |", "|---|---:|---:|---:|---:|---|"]
    scenario_names = {
        SCENARIO_IDS[0]: "家庭自住",
        SCENARIO_IDS[1]: "首次购房、优先项未清楚",
        SCENARIO_IDS[2]: "预算与月度承诺",
        SCENARIO_IDS[3]: "设施与生活方式",
        SCENARIO_IDS[4]: "需求可能变化（母亲入住）",
        SCENARIO_IDS[5]: "犹豫、短回复",
    }
    by_scenario: dict[str, dict[str, dict]] = {}
    for row in report["dialogues"]:
        by_scenario.setdefault(row["scenario_id"], {})[row["arm"]] = row
    short_notes = {
        SCENARIO_IDS[0]: "平局；两版多次重复学校和价格待确认。",
        SCENARIO_IDS[1]: "Lite +0.375；提问预算、语气较低压。",
        SCENARIO_IDS[2]: "Lite +0.25；明确费用公式与未知项目。",
        SCENARIO_IDS[3]: "Lite +0.375；更好跟随客户转向绿地问题。",
        SCENARIO_IDS[4]: "Lite −0.25；漏答已知有电梯，V2 更准确地处理新需求。",
        SCENARIO_IDS[5]: "Lite +0.125；两版都一轮内简短结束。",
    }
    for scenario_id in SCENARIO_IDS:
        a, b = by_scenario[scenario_id]["A_V2"], by_scenario[scenario_id]["B_V2_LITE"]
        delta = round(b["composite_score_1_to_5"] - a["composite_score_1_to_5"], 3)
        lines.append(f"| {scenario_names[scenario_id]} | {a['composite_score_1_to_5']:.3f} | {b['composite_score_1_to_5']:.3f} | {delta:+.3f} | {a['customer_turn_count']} / {b['customer_turn_count']} | {short_notes[scenario_id]} |")
    lines += ["", "## 维度平均分", "", "| 维度 | 原 V2 | V2 Lite | 差值 |", "|---|---:|---:|---:|"]
    for key in CRITERIA:
        a = summary["arms"]["A_V2"]["criterion_means"][key]
        b = summary["arms"]["B_V2_LITE"]["criterion_means"][key]
        lines.append(f"| {key.replace('_', ' ')} | {a:.3f} | {b:.3f} | {b-a:+.3f} |")
    lines += ["", "客户平均回合数两臂相同，均为 3.83。已完成对话均由模拟客户自然结束。", "",
              "## 销售行为观察", "",
              "- **优先项不清的首次购房者：** Lite 先建议以舒适月预算开始，并询问客户是否仍在厘清预算；V2 问客户是自住还是投资。两种问法都合理，Lite 更贴近“我应该从哪里开始”的请求，盲评分高 0.375。",
              "- **预算场景：** Lite 提供 RM0.18/平方尺、900 平方尺约 RM162 的计算，并把其他费用留作确认；评委给 5/5。V2 也做了正确计算，但重复了一次“正在核实”的状态，得 4.75/5。",
              "- **设施场景：** Lite 从儿童游乐场/戏水设施，顺着客户后续问题转到约 10 英亩景观空间，再坦白草坪细节未经确认。V2 首轮信息较多，后面对平台用途和草坪的描述略显确定；Lite 得分高 0.375。",
              "- **母亲可能同住：** 原 V2 得 4.875，Lite 得 4.625。两版都理解卧室隐私和行动便利会改变适配条件；Lite 说电梯信息也待确认，但项目资料已列出每栋的电梯配置。这里是 Lite 一项具体的事实遗漏。",
              "- **家庭自住：** 两版先问到家庭日常重点，也都避免催看房；然而当客户反复要求学校信息和可负担月供时，V2 连续多轮重复等待确认，Lite 也反复说价格、月供和学校资料待核实。两者均没有利用当前可分享的已核实资料把下一步说清楚，因此并列 3.375。",
              "- **短回复：** 两版都只回一条简短项目概览，没有追加问题或推看房。Lite +0.125，差距很小。", "",
              "## 自然度、重复与客户反应", "",
              "客户回合数没有人为拉长：家庭需求各自延续至 6 / 5 回合，预算场景为 4 / 3，忙碌客户两臂都只收一条答复。Lite 在设施场景的后续更紧扣最新问题；预算场景也减少了重复说明。家庭场景则两版都重复待核实状态，Lite 并未系统解决重复问题。总分差只有 +0.146，不能据此宣称自然度普遍提升。", "",
              "## 事实、运营与评测限制", "",
              "1. **品牌名称造成盲评误报：** 共同的 V2 系统规则要求对客称呼使用 “Pearl Residences”；评委只看到项目 Knowledge 中的正式名称 “SkyWorld Pearlmont”，没有看到这条对两臂相同的品牌规则。因此它在多份逐项证据中把 “Pearl Residences” 判为错误。这些名称扣分不能当作模型虚构项目的证据，也限制了事实准确性分项的解释。",
              "2. **评委知识范围比销售员单轮检索更宽：** 评委可检查全部项目事实和商务资料，而销售员每轮只收到 V2 检索到的段落。评委关于“为何不提供价格/资料”的部分意见可能高估了该轮模型可用的信息。",
              "3. **模拟评委与客户均为同一 Luna 家族模型：** 评委打分提供可复核的逐轮理由，但并非独立人类评审；客户模拟每臂独立生成，不是完全相同的逐句客户响应。六组小样本只支持方向性比较。",
              "4. **一次初始盲评输出未完成：** 已保留原始对话，只对这条已完成 transcript 重新请求一次盲评；最终 12 条均有完整评分。usage 统计分开列出该次失败调用，因当时 harness 未保存其 token 明细。",
              "5. **运营承诺只在本地模拟：** 即使有 turn 记录创建了内存 SUPPORT_REQUEST，实际资料核实和后续发信都没有执行，因此本报告只评估承诺是否符合对话，不声称客户会收到真实跟进。", "",
              "## API 使用、费用与延迟", "",
              "| 角色 | 已完成调用 | 输入 token | 输出 token | 成功调用平均延迟 | 成功调用中位延迟 |", "|---|---:|---:|---:|---:|---:|"]
    for role, name in (("sales_agent", "Sales Agent"), ("customer_simulator", "Customer Simulator"), ("blind_evaluator", "Blind Judge")):
        v = report["usage"]["by_role"][role]
        lines.append(f"| {name} | {v['completed_calls']} | {v['input_tokens']:,} | {v['output_tokens']:,} | {v['latency_ms_mean']:,} ms | {v['latency_ms_median']:,} ms |")
    low, high = report["usage"]["estimated_total_cost_range_usd"]
    lines += ["", f"总请求尝试 {report['usage']['request_attempts']} 次：104 次有完整 token usage，另 1 次初始 xhigh 评委回复未完成。成功调用按官方分层 token 价格估算为 ${low:.5f}；未完成调用 usage 未保留，按约 {report['usage']['failed_response_input_tokens_estimate']:,} 个输入 token及原 {report['usage']['failed_response_output_tokens_ceiling']:,} token 输出上限估计，整次评测约 **${low:.3f}–${high:.3f}**。估价按普通输入、缓存输入、缓存写入和输出分别计价；价格依据 [GPT-6 Luna API 文档](https://developers.openai.com/api/docs/models/gpt-6-luna)。", "",
              "## 完整逐轮记录与盲评证据", ""]
    for scenario_id in SCENARIO_IDS:
        lines += [f"### {scenario_names[scenario_id]}", ""]
        for arm, label in (("A_V2", "原 V2"), ("B_V2_LITE", "V2 Lite")):
            row = by_scenario[scenario_id][arm]
            lines += [f"#### {label}", ""]
            for turn in row.get("turns", []):
                number = turn.get("turn", "?")
                lines += [f"**第 {number} 轮 · 客户**：{turn.get('customer', '')}", "",
                          f"**第 {number} 轮 · 销售员**：{turn.get('agent_reply', '')}", ""]
            lines += evidence_markdown(row) + [""]
    lines += ["", "## 文件与数据", "", "本报告包含 12 段完整 transcript、每轮销售动作和检索路径、客户模拟轮次、盲评维度分数/证据、运营 fake adapter 记录及 token/延迟数据。机器可读原始记录见同目录 `report.json`。", ""]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m app.render_v2_lite_report REPORT_JSON")
        return 2
    path = Path(sys.argv[1])
    report = finalize(json.loads(path.read_text(encoding="utf-8")))
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = path.with_name("report.md")
    markdown.write_text(render(report), encoding="utf-8")
    print(f"Finalized {path} and {markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
