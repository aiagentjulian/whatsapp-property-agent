# Laya 与 Nano-Jev 本地评测报告

日期：2026-10-12（MYT）

基线：当前 Sales Core V2，仓库 commit `44ccc8e`
范围：Pearl Residences / Pearlmont Knowledge；不改正式 Runtime。

## 结论

**建议维持 Sales Core V2。** 这次小样本没有证据支持只上 Laya、只上 Nano-Jev 或两者组合。

- Laya 在 20 项业务决策里答对 7 项（35%），其中下一步动作只对 2/10。它经常把有约束的推荐、未解决事项、未核验投资问题和硬性产品不匹配都压成“直接回答事实”。
- Nano-Jev 的检索排序相对当前关键词检索有小幅收益（Top-3 文件召回 46% 对 35%），Top-1 没有优势（60% 对 60%）。但它在 5 个充分性判断中两次漏掉可回答事实；grounded 6 例中 2 个真实支持事实均被否定。
- 组合测试中过滤器三次都把当前检索器交来的候选全拒绝。这样减少了已知事实回复：洪水措施被省略；投资对话中 RM162/月维护费也被省略。预算/海景场景回复大致相当，仍没有依赖 Nano-Jev 的筛选收益。

## 来源、权重与运行方式

| 模型 | 可复查来源 | 权重与推理 | 许可及已知限制 |
|---|---|---|---|
| Laya | [官方 GitHub](https://github.com/NandhaKishorM/laya)、[官方模型卡](https://huggingface.co/convaiinnovations/laya) | `laya==0.4.6`；`convaiinnovations/laya-typed-decisions`，revision `1a793eb568e6718f15941d08f85432581df534e3`；421M ModernBERT-large，PyTorch 结构化分类头，一次前向；本机 MPS；1024 token | Apache-2.0。官方在其 2,000 项 typed-decision 数据上报告专门微调版 0.766，但通用英文和多语 checkpoint 在该任务接近机会水平；微调版也是通用客服、安全、票据及 agent trace 任务，不是 Pearl 销售专训。 |
| Nano-Jev RAG | [官方 GitHub](https://github.com/shubham10divakar/nano-jev)、[权重模型卡](https://huggingface.co/sdmlai/nano-jev) | `nano-jev==1.0.0`；`sdmlai/nano-jev@v1.0`，实际快照 `ffee345e97797bef0948561461ea54fe558588a0`；33.4M MiniLM-L12 cross-encoder；PyTorch CPU 对 query–passage 作 relevance、sufficient、grounded 分类；512 token | 代码 Apache-2.0，v1.0 权重 MIT，English-only。模型卡说明域外准确率下降、概率会过度自信；只在训练/类似 Wikipedia RAG 文本上报告的指标不是本地项目质量证据。 |

名称核对：另有 [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) 与 [C-Tianyu/NanoJev 权重](https://huggingface.co/C-Tianyu/NanoJev)，是 Qwen3-0.6B、主要面向 Maze/Snake/ViZDoom 决策及 CUDA 服务示例的项目。它不是本次使用的 Nano-Jev RAG 权重，也未被下载或替换进测试。其 GitHub 项目标 MIT；其 Hugging Face 权重卡没有 license 元数据标签。

## 硬件和隔离情况

- Apple M1；8 CPU 核心；7 核 GPU；Metal 3；8 GiB 统一内存。
- 初始可用磁盘 57 GiB；模型缓存检查后仍有 53 GiB 可用。
- Laya safetensors 842,609,220 bytes；Nano-Jev 133,464,836 bytes。没有下载 0.6B 同名游戏模型。
- Python 3.12.13、PyTorch 2.14.1、Transformers 5.19.0。Laya 运行在 MPS；Nano-Jev 运行在 CPU。
- `/tmp/whatsapp-property-agent-laya-nanojev-venv` 独立虚拟环境；HF/uv 缓存在 `/tmp/whatsapp-property-agent-laya-nanojev-cache`。权重未存入 worktree。
- Laya RSS 峰值 1,049,444,352 bytes；MPS driver allocation 2,156,527,616 bytes；`/usr/bin/time` 总峰值 footprint 3,437,205,760 bytes，未报告 swap。Nano-Jev smoke RSS 603,602,944 bytes；多候选评测进程 RSS 峰值 2,051,178,496 bytes。

## Laya 业务判断

样本为 10 条脱敏状态，分别标注当前意图与推荐下一步。标签不包含需要生成的答句，也没有依据具体客户句子硬编码答案。详细结果及概率见 `results.json`。

| 维度 | 命中 | 错误数 | 准确率 |
|---|---:|---:|---:|
| 当前意图 | 5/10 | 5 | 50% |
| 下一步销售动作 | 2/10 | 8 | 20% |
| 合计 | 7/20 | 13 | 35% |

正确样例包括安全/洪水顾虑、客户要求时间、明确的 4 房硬性不匹配、中性回应和维护费事实问题。典型错误包括：把高楼海景与紧预算的取舍识别为事实问题；把未解决的租金资料问题当成已知事实；把对四房不匹配的确认继续导向澄清；以及在客户仅作中性回应时选择直接答事实。

热身后 20 次结构化问题推理中位数 398.69 ms；首次 checkpoint 下载/载入总计约 38 秒；首次模型推理约 1.6 秒。响应快不抵消动作准确度不足的问题。

## Nano-Jev 知识评估

五类知识查询（洪水、海景/预算、投资证据、LPPSA、维护费/会所）。候选文档从 Pearl Knowledge 中选取，标签为应该有帮助的知识文件；指标与当前 `app.knowledge.retrieve()` 的候选排序对比。

| 路由排序 | Nano-Jev | 当前检索器 |
|---|---:|---:|
| Top-1 至少命中一个相关文件 | 3/5 | 3/5 |
| Top-3 至少命中一个相关文件 | 5/5 | 4/5 |
| 所有标注相关路径中，Top-3 召回率 | 46% | 35% |

这只是在 5 个查询上的初步排序改善；top-1 平手、样本小，不足以替换现有检索器。最多 118 passages 的测试，中位数约 132 ms。

| 判断类型 | 命中 | 说明 |
|---|---:|---|
| 回答充分性 | 3/5（60%） | 两个正例都错判为不充分：维护费含 sinking fund；标准户型是否 4 房。三个不充分案例均正确拒答。 |
| Claim groundedness | 4/6（67%） | 四个不受支持的 claim 均判为 no，但两条有直接知识支持的维护费和标准户型 claim 也都判为 no。 |

因此它在这个样本中表现为只会保守拒绝：没有 false positive，但两种正向事实任务的召回率都是 0/2。作为客户回复前的 evidence gate 会漏掉常见、可验证的卖点。

## 完整回复配对

使用三段失败场景：PEA-007 洪水/高压电缆、PEA-008 高层海景与预算、PEA-004 租金/净回报证据。Laya 得出意图和动作提示；Nano-Jev 过滤 Sales Core V2 自身先行检索的候选；当前 Luna 销售 Agent 同时跑 baseline 和新链。6 次 GPT-6 Luna API 请求、无重试。无 WhatsApp、数据库、CRM、Sheets 或人工转接副作用。回复和模型阶段数据在 `results.json`。

| 场景 | Sales Core V2 baseline | Laya → Nano-Jev → Luna | 实际影响 |
|---|---|---|---|
| 洪水与电缆 | 提供已知标高/JPS 防洪措施，避免零风险保证；电缆距离留待核对。 | Nano-Jev 拒绝唯一候选，Luna 只说没有 site-specific 信息，准备核实。 | **退步：**失去可回答的防洪措施。 |
| 高楼海景、预算紧 | 提供 900 平尺、3 房 2 卫布局，并说需按现有高层海景单位与价格作取舍。 | 说明同样的户型，提出按现有供应和价格核实，并问最高预算。 | **接近：**组合的问题更有推进性，但候选筛选没有贡献有效知识。 |
| 投资回报/租金 | 承诺核对带来源/日期的租金与 package，并给 RM0.18 psf、900 平尺 RM162/月持有成本。 | 保证核对租金和价格，但不复述已有的维护费数字。 | **轻微退步：**漏掉与净回报直接相关的已知成本。 |

baseline 的 Luna API 耗时为 8.11、8.71、11.18 秒；组合 Luna 请求为 8.34、11.86、12.47 秒。包含本地阶段后组合端到端中位数 12.90 秒（baseline 中位数 8.71 秒）。三组样本受单次 API 波动影响，不能将这 4.19 秒中位差归因于模型本地推理；组合的额外本地决策中位数约 1.06 秒。Token 合计 baseline 10,268，组合 10,663（+3.8%）。

组合里的 Nano-Jev 候选判断见下表；irrelevant <0.5 才保留：

| 场景 | 现有候选中 Nano-Jev 的最高 `irrelevant` 概率 | 保留结果 |
|---|---:|---|
| 洪水/河流 | 0.964 | 无候选 |
| 高层海景/预算 | 0.696 | 无候选 |
| 投资证据 | 0.977 | 无候选 |

这个行为与充分性测试一致：Nano-Jev 将明显相关的已有知识当作无关材料，并令 Luna 只能依赖系统提示或表达不确定。

## 可复现性和数据边界

- 标注与脱敏输入：`cases.json`。
- 代码：`run_eval.py`；传递依赖锁定：`requirements.lock.txt`。
- 已提交结果只保留标签、分数、路径、计时及三组回复。不保存 passage 原文、模型权重、客户姓名/联系方式、API key、`.env` 或 CRM/WhatsApp 数据。
- 仓库中的历史资料是 simulator fixtures / simulator run transcripts，不是 live WhatsApp 客户对话。测试文本来自实际存档失败模拟运行，已移除运行 ID 及 lead/session 状态，只保留解释业务表现必要的文字。
- 小样本只支持本项目的初筛决定，不代表一般性能结论。没有对真实生产客户发送消息。

执行方式与 license/来源说明见本目录 [`README.md`](README.md)。
