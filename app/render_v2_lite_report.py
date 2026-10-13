"""Render a Chinese Phase 3 mission-led evaluation report."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .v2_lite_eval import CRITERIA


def render(report: dict) -> str:
    arms = report.get("summary", {}).get("arms", {})
    git = report.get("git", {})
    manifest = git.get("runtime_comparison", {})
    lines = [
        "# WhatsApp Property Agent — Phase 3 销售判断评测", "",
        f"运行：`{report.get('run_id')}` · 状态：**{report.get('status')}** · main `{git.get('main_base')}` · Lite `{git.get('lite_commit')}`。", "",
        "## 结论", "",
        report.get("recommendation", "待结合逐轮证据审阅后决定。"), "",
        "本报告比较两个完整运行时；盲评分仅作辅助。采纳结论还应依据逐轮对话、可用事实、重复表现及明确拒绝后的行为。", "",
        "## 对照与边界", "",
        "| 项目 | 原 V2（main） | V2 Lite（实验分支） |", "|---|---|---|",
        f"| commit | `{manifest.get('A_V2', {}).get('runtime_commit', git.get('main_base'))}` | `{manifest.get('B_V2_LITE', {}).get('runtime_commit', git.get('lite_commit'))}` |",
        f"| System Prompt SHA-256 | `{manifest.get('A_V2', {}).get('system_prompt_sha256', '')}` | `{manifest.get('B_V2_LITE', {}).get('system_prompt_sha256', '')}` |",
        f"| Sales Brain SHA-256 | `{manifest.get('A_V2', {}).get('brain_sha256', '')}` | `{manifest.get('B_V2_LITE', {}).get('brain_sha256', '')}` |",
        f"| Agent runtime SHA-256 | `{manifest.get('A_V2', {}).get('agent_py_sha256', '')}` | `{manifest.get('B_V2_LITE', {}).get('agent_py_sha256', '')}` |",
        f"| Retriever SHA-256 | `{manifest.get('A_V2', {}).get('knowledge_py_sha256', '')}` | `{manifest.get('B_V2_LITE', {}).get('knowledge_py_sha256', '')}` |", "",
        "Prompt-only comparison was not assumed: each arm loaded its own system prompt, Brain, agent module, retriever, schema, and Knowledge files from its isolated worktree. Runtime differences include `app/agent.py`, `app/knowledge.py`, and `brain/AGENT.md`; the Knowledge files themselves have identical paths and SHA-256 hashes across arms. Full Git path list and per-file hashes are in `report.json`. Customer-facing project alias **Pearl Residences** is authorized; formal identity is SkyWorld Pearlmont.", "",
        "销售员为 GPT-6 Luna / High；模拟客户为 GPT-6 Luna / Medium；盲评为 GPT-6 Luna / Extra High。客户可自然继续或结束，没有最低轮数；未要求达到看房或交接。所有运营请求只经过内存 fake adapter。没有 WhatsApp、CRM、客户数据库、真实预约、真实转人工、合并或部署。", "",
        "## 人工逐轮审阅", "",
        report.get("human_review", {}).get("summary", "待完成人工审阅。"), "",
    ]
    for note in report.get("human_review", {}).get("findings", []):
        lines.append(f"- {note}")
    setup_note = report.get("evaluation_input_snapshot", {}).get("review_note")
    if setup_note:
        lines += ["", "**场景设置缺陷：** " + setup_note,
                  "已付费 transcript 保持原样。测试夹具已修正供以后使用，本次未再次付费运行。"]
        correction = report.get("evaluation_input_snapshot", {}).get("post_run_correction")
        if correction:
            lines += ["", "修正后的未来场景预置内容：", "", f"> {correction}", ""]
    lines += ["",
        "## 八组配对结果", "",
        "| 情境 | 原 V2 | V2 Lite | Lite − V2 | 回合数 V2 / Lite |", "|---|---:|---:|---:|---:|",
    ]
    labels = {
        "P3-family-four-bedroom-budget": "六口之家、四房要求与后续预算",
        "E05-layout-four-bedrooms": "四房明确不可妥协",
        "P3-too-expensive-ambiguous": "“太贵”原因不明（预置报价污染）",
        "E02-first-home-unsure": "首次购房、优先项不清",
        "P3-short-oh-okay": "简短中性回复及对话历史",
        "P3-pricing-rebates-maintenance": "价格、优惠、管理费与月供",
        "E30-ready-but-no-pressure": "逐渐产生看房兴趣",
        "P3-explicit-no-contact": "明确要求停止联系（运营动作不可比）",
    }
    by_pair = {}
    for row in report.get("dialogues", []):
        by_pair.setdefault(row["scenario_id"], {})[row["arm"]] = row
    for scenario_id, label in labels.items():
        pair = by_pair.get(scenario_id, {})
        a, b = pair.get("A_V2", {}), pair.get("B_V2_LITE", {})
        av, bv = a.get("composite_score_1_to_5"), b.get("composite_score_1_to_5")
        delta = f"{bv-av:+.3f}" if isinstance(av, (int, float)) and isinstance(bv, (int, float)) else "—"
        lines.append(f"| {label} | {av if av is not None else '—'} | {bv if bv is not None else '—'} | {delta} | {a.get('customer_turn_count', '—')} / {b.get('customer_turn_count', '—')} |")
    lines += ["", "价格污染组的初始报价来自测试夹具，不是任一被测 agent 的生成内容；该组分数保留作审计记录，但不用于结论。明确拒绝组一臂只记录内部 handoff，另一臂发出未验证承诺，因此评分差不代表有效退出联系能力比较。", ""]
    lines += ["", "## 评分摘要", "", "| 维度 | 原 V2 | V2 Lite |", "|---|---:|---:|"]
    for criterion in CRITERIA:
        a = arms.get("A_V2", {}).get("criterion_means", {}).get(criterion)
        b = arms.get("B_V2_LITE", {}).get("criterion_means", {}).get(criterion)
        lines.append(f"| {criterion} | {a if a is not None else '—'} | {b if b is not None else '—'} |")
    lines += ["", f"完整配对差值均值：{report.get('summary', {}).get('paired_mean_B_minus_A', '—')}；这些分数是方向性证据，不单独决定采用。", "",
              "## 逐轮记录", ""]
    for scenario_id, label in labels.items():
        lines += [f"### {label}", ""]
        scenario_input = report.get("evaluation_input_snapshot", {}).get("scenarios", {}).get(scenario_id, {})
        if scenario_input.get("seeded_history"):
            lines += ["**两臂共同的夹具预置历史（非被测 agent 生成）：**", ""]
            for message in scenario_input["seeded_history"]:
                speaker = "客户" if message.get("direction") == "INBOUND" else "销售员"
                lines.append(f"- {speaker}：{message.get('body', '')}")
            lines.append("")
        for arm, title in (("A_V2", "原 V2"), ("B_V2_LITE", "V2 Lite")):
            row = by_pair.get(scenario_id, {}).get(arm)
            if row is None:
                continue
            lines += [f"#### {title} · {row.get('customer_turn_count')} 个客户回合 · {row.get('end_reason')}", ""]
            for turn in row.get("turns", []):
                lines += [f"**客户（第 {turn.get('turn')} 轮）**：{turn.get('customer', '')}", "",
                          f"**销售员**：{turn.get('agent_reply', '')}", "",
                          f"动作：`{turn.get('action')}` · 销售动作：`{turn.get('sales_move')}` · 客户信号：`{turn.get('buyer_signal')}`。", ""]
                if turn.get("retrieved_knowledge_passages"):
                    lines += ["本轮检索段落：", ""]
                    for passage in turn["retrieved_knowledge_passages"]:
                        lines += [f"- `{passage.get('path')}` · {passage.get('heading', '')}: {passage.get('text', passage.get('content', ''))}"]
                    lines.append("")
                if turn.get("support_request"):
                    lines += ["SUPPORT_REQUEST fake adapter 结果：", "", "```json", json.dumps(turn["support_request"], ensure_ascii=False, indent=2), "```", ""]
            handoffs = row.get("operations", {}).get("handoffs", [])
            if handoffs:
                lines += ["内部 handoff fake adapter 记录（未产生真实交接）：", "", "```json",
                          json.dumps(handoffs, ensure_ascii=False, indent=2), "```", ""]
            judgement = row.get("judgment", {})
            if judgement:
                lines += [f"盲评综合分：{row.get('composite_score_1_to_5')} / 5。", ""]
                for key in CRITERIA:
                    evidence = judgement.get("evidence", {}).get(key, "")
                    lines.append(f"- **{key} {judgement.get('scores', {}).get(key)}**：{evidence}")
                for issue in judgement.get("factual_issues", []):
                    lines.append(f"- 事实问题：{issue}")
                if judgement.get("overall_note"):
                    lines += ["", f"盲评摘要：{judgement['overall_note']}"]
                lines.append("")
    usage = report.get("usage", {})
    lines += ["## API 使用", "", f"尝试 {usage.get('request_attempts', '—')} 次；成功调用 {usage.get('successful_calls', usage.get('successful_responses_with_usage', '—'))} 次；输入 {usage.get('input_tokens', usage.get('input_tokens_successful_responses', '—'))} tokens（缓存 {usage.get('cached_input_tokens', '—')}，写入缓存 {usage.get('cache_write_input_tokens', '—')}）；输出 {usage.get('output_tokens', usage.get('output_tokens_successful_responses', '—'))} tokens；估算费用 USD {usage.get('estimated_cost_usd', '—')}。价格依据 [GPT-6 Luna API 定价](https://developers.openai.com/api/docs/models/gpt-6-luna)，按 usage 返回的缓存 token 分类估算。", ""]
    for role, row in usage.get("by_role", {}).items():
        lines.append(f"- {role}: {row.get('calls', row.get('completed_calls', '—'))} calls, {row.get('input_tokens', 0)} input / {row.get('output_tokens', 0)} output tokens, mean latency {row.get('latency_ms_mean', '—')} ms.")
    lines += ["", "## 局限", "", "模拟客户和盲评与销售员同属 Luna 模型家族，模拟客户在每臂独立生成，不保证逐句完全相同。报告保存了每轮实际提供给模型的上下文与完整 Knowledge 文件哈希；需要人工逐轮检查盲评分是否将未传入模型的事实误判为回复遗漏。一次小样本不能证明普遍表现。", "",
              ]
    for limitation in report.get("paid_run_limitations", []):
        lines.append(f"- {limitation}")
    lines += ["", "机器可读报告和完整可用事实见同目录 `report.json`。"]
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m app.render_v2_lite_report REPORT_JSON")
        return 2
    path = Path(sys.argv[1])
    report = json.loads(path.read_text(encoding="utf-8"))
    markdown = path.with_name("report.md")
    markdown.write_text(render(report), encoding="utf-8")
    print(f"Rendered {markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
