# Pearl Residences: Laya / Nano-Jev 本地评测

这是隔离的研究工具和结果。没有改动 WhatsApp Runtime；模型权重、虚拟环境和缓存都不在 Git 仓库中。

## 项目与模型核实

| 项目 | 本次使用版本 | 权重 / 方式 | 许可证 | 任务适配 |
|---|---|---|---|---|
| [Laya](https://github.com/NandhaKishorM/laya) | Python `laya==0.4.6`；`convaiinnovations/laya-typed-decisions`，revision `1a793eb568e6718f15941d08f85432581df534e3` | 421M 参数 ModernBERT-large encoder + 分类决策头；PyTorch 一次前向输出 choice/score/yes-no，不生成文本；1024 token；本机 MPS 可运行 | 项目及 Hugging Face 权重 Apache-2.0 | 结构化决策和客户服务是相邻任务，但官方说明销售任务仍需领域微调。本次零样本判断不够好。 |
| [Nano-Jev: RAG variant](https://github.com/shubham10divakar/nano-jev) | Python `nano-jev==1.0.0`；`sdmlai/nano-jev` tag `v1.0`，本地缓存快照 `ffee345e97797bef0948561461ea54fe558588a0` | 33.4M 参数 MiniLM-L12 cross-encoder；逐个给问题与 passage 打 relevance / sufficient / grounded 概率；512 token；PyTorch CPU 可运行 | 代码 Apache-2.0；v1.0 权重 MIT。未使用 v0.1（其训练底模 MS MARCO 有非商业用途限制）。 | 恰好面向 RAG 判断；但模型卡限制在英语及类 Wikipedia 文本。本地 Pearl 知识域外测试显示正向事实漏判严重。 |

“Nano-Jev / NanoJev”存在同名歧义。本次选的是 README 明确支持 `relevance`、`sufficient`、`grounded` 的 33M RAG 项目。另有 [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev)，其 Hugging Face 卡为 Qwen3-0.6B，训练和公开评测集中在 Maze、Snake、ViZDoom 等游戏任务，提供 CUDA 服务示例；不是把它当作 RAG 模型替换使用。该项目仓库列 MIT 许可证，但 Hugging Face 卡未给出权重许可证标签，因此本次未下载或测试。

公开基准只用于确定 checkpoint 与运行方式，不视为 Pearl 销售质量证据。Laya 官方模型卡称通用 checkpoint 在其 typed-decision 基准接近随机，较好的 0.766 来自专门微调的 checkpoint；Nano-Jev 官方卡也报告未见数据集准确率明显下降。本报告只依据本地样本作结论。

## 本机与隔离安装

- Apple M1，8 个 CPU 核心、7 核 GPU、Metal 3、8 GiB 统一内存。
- 测试开始时磁盘可用 57 GiB；测试后 53 GiB。
- 下载权重：Laya 842,609,220 bytes；Nano-Jev 133,464,836 bytes。
- Python 3.12.13；PyTorch 2.14.1；Transformers 5.19.0。Laya 用 MPS，Nano-Jev 用 CPU。
- 隔离虚拟环境：`/tmp/whatsapp-property-agent-laya-nanojev-venv`；HF / uv 缓存：`/tmp/whatsapp-property-agent-laya-nanojev-cache`。安装和权重总占用约 2.3 GiB。
- Laya 进程 RSS 峰值约 1.05 GiB，MPS driver allocation 约 2.16 GiB；`/usr/bin/time` 报告的总峰值 footprint 约 3.44 GiB。Nano-Jev 单次 smoke RSS 约 0.60 GiB。采样时无 swap。

## 评测方法与结果

仓库保存的是 simulator fixtures 和 simulator run transcripts，不是 live WhatsApp 客户对话。评测使用实际存档失败运行中的买家消息与上下文，移除了 lead/session 标识和运行记录，只保留脱敏文本、对话状态与可复查知识路径。没有针对具体句子编写生成式答案；标注衡量意图类别、下一步、支持证据和遗漏。代码及标注见 [`cases.json`](cases.json)。

### Laya：意图和下一步

10 个对话状态、每项各判断 intent 和 next move，共 20 个有标注决策。Laya 命中 **7/20（35%）**：intent **5/10**，next move **2/10**。常见误判是把未验证的投资回报、预算/视野取舍、未解决事项和硬性户型不匹配一概判成“直接回答知识问题”；有 8/10 个 next move 标签判错。过载和中性回应两项处理正确。概率信心也低：样本 choice confidence 约 0.01–0.26。

热启动推理中位数约 399 ms；首次载入约 38 秒，首次推理约 1.6 秒。模型有速度优势，但在这个业务上的决策准确度不足以驱动销售阶段、意图或问题路由。

### Nano-Jev：候选相关性、充分性与事实支持

用 5 个问题、59–118 个 passage 候选/题，按知识文件路径标注相关材料，并与当前检索器排序作对比：

| 指标 | Nano-Jev | 当前 Sales Core V2 检索 |
|---|---:|---:|
| Top-1 含至少一个标注相关文件 | 3/5（60%） | 3/5（60%） |
| Top-3 含至少一个标注相关文件 | 5/5（100%） | 4/5（80%） |
| Top-3 标注相关路径召回率 | 46% | 35% |

这组样本只显示小幅排序收益；Nano-Jev 的 top-1 没有优于现有检索。逐候选批量判断中位数约 132 ms。按当前候选流程筛 1–2 条 passage 用时约 117–259 ms。

充分性判断 **3/5（60%）**；两条已有明确资料的正向问题（维护费、户型）都被判“不充分”。Grounded 判断 **4/6（67%）**；所有 4 条不受支持的断言都判对，但 **2/2 条有资料支持的正向事实均被错判为不支持**。模型可以阻挡夸大说法，却也会抑制普通、可证实的销售回答；按当前阈值不能作为资料过滤闸门。

### 小规模完整回复：Laya → Nano-Jev → Luna 对照 Sales Core V2

在 3 个真实失败场景上做了 3 组配对、共 6 次 GPT-6 Luna API 请求（没有 WhatsApp、CRM、Sheets、人工转接或 provider 重试）。新链只把当前 Sales Core V2 已检索出的候选 passage 交给 Nano-Jev；低于 0.5 的 irrelevance 概率才予保留。Nano-Jev 三次都拒绝了全部候选：洪水/高压电缆、预算与高楼海景、租金回报/价格包。

- **洪水/电缆：回退损失。** 基线用知识说明标高、JPS 与防洪控制，并明确不保证零风险；组合链因没有保留 passage，只能说无法确认，遗漏已有支持的防洪措施。
- **预算/海景：质量接近。** 两者均说明要核对当前单位与价格。组合回复问了最高预算，推进稍自然；但没有 Nano-Jev 的任何有效资料支持，靠 Luna 原有提示完成。
- **投资核算：组合回复少给了一条已知事实。** 基线给出 RM0.18/平方尺及 900 平方尺对应 RM162/月；组合回复只承诺核对租金和 package，遗漏 maintenance 输入。

小样本盲测不是可靠总体质量估计；逐条审阅没有看到组合回复产生新的不实项目事实，但出现两个重要事实遗漏。6 次回复共计 10,268 对 10,663 tokens（组合多 3.8%）。Luna API 响应中位数约 8.71 s 对 11.86 s；加本地 Laya 和 Nano-Jev 后，组合全链中位数约 12.90 s。差异主要有 API 单次波动，但本地组件本身再增加约 1 秒。

**实际建议：维持现有 Sales Core V2。** 暂不单独采用 Laya、Nano-Jev 或组合。Laya 当前零样本决策精度不够；Nano-Jev v1.0 过度拒绝已支持的事实；组合样本没有稳定质量提升，并在防洪事实和持有成本上发生遗漏。

## 重跑

需 Python 3.12+ 和网络仅用于首次下载模型。依赖及所有传递依赖记录在 [`requirements.lock.txt`](requirements.lock.txt)。权重缓存应保持在仓库外。以下命令跑本地决策与检索，不会调用 Luna：

```sh
uv venv --python 3.12 /tmp/whatsapp-property-agent-laya-nanojev-venv
uv pip install --python /tmp/whatsapp-property-agent-laya-nanojev-venv/bin/python -r research/laya-nanojev/requirements.lock.txt
PYTHONPATH=. HF_HOME=/tmp/whatsapp-property-agent-laya-nanojev-cache/hf LAYA_REVISION=reviewed \
  /tmp/whatsapp-property-agent-laya-nanojev-venv/bin/python research/laya-nanojev/run_eval.py \
  --phase local --output /tmp/laya-nanojev-results.json
```

如需重新执行 Luna A/B，把私有 `.env` 路径作为 `--env-file` 传入 `--phase combo`。该路径不会复制或写入结果文件；组合阶段会对三个场景各运行一次当前 baseline 和一次新链。结果 JSON 应写到 `/tmp`，不要提交 `.env`、API 输出中的客户资料或模型缓存。
