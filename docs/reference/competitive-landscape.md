# 相关工作与竞争格局 / Competitive Landscape

> 建立于 2026-10-12。以下条目均已**在线核实存在**（经本机代理 127.0.0.1:7897 访问官方来源），摘要为官方页面原文摘录。
> 本文档支撑种子对话第一节的核心判断：**"生成设计 → 物理仿真 → 发现失败 → LLM 修复 → 再仿真" 已不足以构成新颖性。**

## 一、直接相关工作

### 1. Physics-in-the-Loop: A Hybrid Agentic Architecture for Validated CAD Engineering Design ⚠️ 最危险
- **会议**：IJCAI 2026（AI4Tech track），pp. 6417–6425
- **作者**：Elias Berger, Muhammad Usama, Jan Mehlstäubl, Bernhard Saske, Kristin Paetzold-Byhain
- **链接**：<https://www.ijcai.org/proceedings/2026/714> · DOI: 10.24963/ijcai.2026/714
- **摘要原文要点**："LLMs can generate CAD, yet lack physical comprehension required for reliable engineering design. Instead of attempting to implicitly learn physical laws from data, we propose a Hybrid Agentic-Physical Architecture that embeds **validated knowledge-based engineering tools directly into the decision-making loop** of autonomous AI agents. In this framework, engineering design is formulated as a **closed-loop, sequential decision-making process guided by explicit physical verification**. Based on a load case, dedicated agents iteratively **plan, generate, evaluate, and revise** engineering designs using knowledge-based tools as a feedback signal. We introduce a **benchmark dataset and metrics** for assessing functional validity in generative CAD. … 4.2x increase in structural complexity and improving compile rate by 3.5%."
- **对我们的含义**：闭环 + 物理验证 + 迭代修订 + benchmark + 指标，**整套叙事已被占据**。不能把"把物理验证嵌入设计闭环"当贡献。
- **可能的差异点（待实证）**：其动作空间是 plan/generate/evaluate/revise，失败信号是"合不合规 / 能否编译 / 结构复杂度"；**没有**处理"当前机制类别根本不可行、必须更换解决机制"。指标是功能有效性，不是**设计空间逃逸**。
- **必须核实**：它的 failure signal 是否已包含"不可行性"判定？它的 action space 是否已隐含机制切换？

### 2. APOLLO: Automated LLM and Lean Collaboration for Advanced Formal Reasoning —— 方法论来源
- **会议**：NeurIPS 2025；arXiv:2505.05758
- **作者**：Azim Ospanov, Farzan Farnia, Roozbeh Mohit
- **链接**：<https://proceedings.neurips.cc/paper_files/paper/2025/hash/3b77109ad4dd4ba82d07cacd4b24207e-Abstract-Conference.html> · <https://arxiv.org/abs/2505.05758>
- **摘要原文要点**："A formal verification system can check whether a formal proof is correct or not almost instantaneously… The usual approach … is to prompt the LLM many times (up to several thousands) until one of the generated proofs passes. … APOLLO (Automated PrOof repair via LLM and Lean cOllaboration), a modular, model-agnostic agentic framework … The LLM generates proofs for theorems, a set of agents analyze the proofs, fix the syntax errors, **identify the mistakes in the proofs using Lean, isolate failing sub-lemmas**, …"
- **对我们的含义**：这是"验证器闭环 → 失败定位 → 子问题分解 → 修复"的原型。ECDR 要回答的是它在**开放工程设计空间**中的对应物：物理验证器只说"该设计不满足约束"，**不告诉你该换哪一类机制**。数学证明中目标命题不变、被重构的是证明结构；工程设计中**被重构的是问题分解与机制本身**。

### 3. MCP-SIM: A self-correcting multi-agent LLM framework for language-based physics simulation and explanation
- **会议**：npj Artificial Intelligence (2026)，article s44387-025-00057-z
- **链接**：<https://www.nature.com/articles/s44387-025-00057-z>
- **摘要要点**：多智能体 LLM 框架，从自然语言构建物理仿真并给出解释；检索片段含 "Despite promising results, several limitations remain…"
- **对我们的含义**：证明"自动构建仿真 + 诊断**数值**错误 + 迭代修复"本身已不新颖。**数值错误诊断 ≠ 工程设计机制诊断**，这是必须划清且可以量化的界线。

### 4. SimulCost: A Cost-Aware Benchmark and Toolkit for Automating Physics Simulations with LLMs
- **会议**：ICML 2026 Poster
- **链接**：<https://icml.cc/virtual/2026/poster/60755>
- **摘要原文**："Evaluating LLM agents for scientific tasks has focused on token costs while ignoring **tool-use costs like simulation time and experimental resources**. As a result, metrics like pass@k become impractical under realistic budget constraints. … we introduce SimulCost, the first benchmark targeting **cost-sensitive parameter tuning in physics simulations**. … spanning 2,947 single-round (initial guess) and 1,931 multi-round (adjustment by trial-and-error) tasks across 13 simulators from fluid dynamics, solid mechanics, and plasma physics. Each simulator's cost is **analytically defined and platform-independent**. Frontier LLMs achieve 46–65% success rates in single-round mode, dropping to 35–55% under high accuracy requirements…"
- **对我们的含义**：**仿真预算必须计入评价**这件事已有 benchmark 在做。成本核算是**实验设定**，不是贡献；且要与其口径兼容。注意它是 *parameter tuning* 任务 —— 恰好是 ECDR 声称要超越的那一层。

## 二、必须补检索的方向（尚未核实）

种子对话提到 **LLM-AutoSciLab**（2026，闭环科学发现 + 用竞争假设选择信息量更高的实验）。这是 ECDR 第二支柱（**可证伪的失败诊断**）最接近的已有工作：
- 若它已做到"竞争假设 → 主动实验 → 更新置信度"，则**诊断部分本身不是贡献**。
- 差异化必须落在：**实验的结果作用于"允许继续探索的设计空间与问题分解结构"**，而不仅是作用于对物理机制的认知。
- 检索线索：术语可能是 competitive hypotheses / information-gain experiment selection / self-driving lab。

其他待检索：
- design-space escape / mechanism switching / **infeasibility certification** in LLM engineering design agents
- LLM agent + topology optimization（强基线来源）
- "paradigm shift" / "design fixation" in AI design（心理学侧的可引证基础）
- Bayesian optimization with variable/expanding search space（算法侧最直接的对手）

## 三、精读清单（按优先级）

| # | 论文 | 为什么必须读 | 状态 |
|---|---|---|---|
| 1 | Physics-in-the-Loop (IJCAI 2026) | 决定 novelty 边界：其 action space 与 failure signal 究竟多细 | 待精读 |
| 2 | LLM-AutoSciLab (2026) | 决定"可证伪诊断"能否仍算贡献 | 待定位原文 |
| 3 | APOLLO (NeurIPS 2025) | 方法论原型；看它如何定义"分解"与"修复" | 摘要已读，正文待读 |
| 4 | MCP-SIM (npj AI 2026) | 划清"数值失败" vs "机制失败" | 待精读 |
| 5 | SimulCost (ICML 2026) | 对齐成本核算口径 | 摘要已读，正文待读 |

## 四、对我们的三条硬约束（由以上推出）

1. **不能**把"物理在环"、"闭环修订"、"成本感知"、"假设竞争 + 主动实验"中的任何一条单独当贡献 —— 全部已有先行工作。
2. **必须**证明差异发生在 **失败证据 → 设计空间/问题分解结构的改写** 这一步，并且这一步**可被独立测量**。
3. **必须**让强基线拿到**同一套设计算子与机制集合**，否则无法排除"新方法只是选项更多"。
