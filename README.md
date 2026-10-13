# ECDR — 能力缺口认证

> **交付物**：[PAPER.md](PAPER.md)（论文）· [docs/STATE.md](docs/STATE.md)（项目状态清单）· [docs/ROADMAP.md](docs/ROADMAP.md)（研究纲领）· [docs/CONSENSUS.md](docs/CONSENSUS.md)（早期共识报告）

## 一句话

**对未被检查的成员，确定性否定无法通过观察获得。** 因此证书与搜索的关系不是快慢，而是**能否得出结论**。

## 核心主张

给设计对象 S =（组件清单, 连接拓扑, 边界关系）与能力缺口 delta(S) > epsilon，本项目的**证书**是对一类结构的陈述，携带

1. 一份**可被第三方检查的可靠性论证**（独立于促成它的那次搜索）；
2. 一个**适用域标签**，使它可撤销而非闸门；
3. 一个**增长慢于族规模**的代价。

## 四条命题

| | 命题 | 状态 |
|---|---|---|
| **1** | 确定性否定的查询下界：只靠求值需与族规模同阶的次数 | **已证** |
| **2** | 代价定理：证书更便宜当且仅当 g(N) 超过 (c_p + c_v) / c_s | **已证** |
| **3** | 概率区制的划界：**抽样足够的区制里没有交叉** | **已证** |
| **4** | **启发式不是替代品**：读同一判词者剪枝相同、标度与枚举一致 | **已证且已测** |

## 关键数字

| 量 | 值 |
|---|---|
| 设计空间规模轴 | 3.2e+01 至 3.5e+16（规模 3 至 10） |
| 三臂指数（仅求值 / 混合 / 仅证书） | **1.0000 / 0.0551 / 0.0597** |
| 分离度 | 规模 3 时的 6.4 → 规模 10 时的 **9.3e+14** |
| 代价阶梯 L0 / L1 / L2 | 1.509e-03 / 6.036e-03 / **1.8816 s（1247 倍）** |
| L2 处的分离度 | **3.431e+16** |
| L2 与 L0 用同一程序测得的一致度 | **9.50e-05** |

## 仓库结构

    ecdr/            核心库
      structure/     结构表示、计数、系综、能力
      l0/            L0 频域、证书、不变量、峰值
      l1/            L1 鲁棒性（角点精确）
      l2/            L2：Julia 时域、Modelica 发射 / 线性化 / 运行
      heat/          热工领域：问题表、网络线性规划、设计枚举
      bench/ agent/  任务族与早期 agent 实验
    scripts/         可独立复现的步骤脚本（step1 至 step88）
    runs/            运行产物（JSON）
    docs/
      ROADMAP.md     研究纲领（含里程碑与证伪条件）
      STATE.md       诚实清单：已证 / 已测 / 失败 / 不主张
      CONSENSUS.md   早期共识报告（发现 001 至 008 时期）
      findings/      62 份发现文档
    orchestrator/    Cordis 编排器（TypeScript）+ Python 物理桥
    PAPER.md         论文

## 复现

    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt
    .venv\Scripts\python.exe scripts\step77_proposition4.py     # 命题 4
    .venv\Scripts\python.exe scripts\step80_curve_b.py          # 三臂曲线
    .venv\Scripts\python.exe scripts\step82_m4_ladder.py        # 代价阶梯（需 Docker）
    .venv\Scripts\python.exe scripts\step88_m1_verdict.py       # 规模普查

编排器：

    cd orchestrator
    npm install
    node node_modules/cordis/bin.js --argue

**依赖**：Python 3.14、NumPy、SciPy、Docker（镜像 openmodelica/openmodelica:v1.27.1-minimal）、Node 24。

## 纪律

* 振动是**首个领域**而非主题。
* **不训练任何模型**，包括验证器。
* 证书是**带适用域、可撤销的置信度算子**，不是判决。
* **不从引用权威立论**——论证是结构性的。
* 不在小到够不着交点的设计空间上报结果。

## 这份工作里最该被读的部分

[docs/STATE.md](docs/STATE.md) 与论文第 9 节记录了：**十次判决不可能因为该检验存在的理由而失败**（其中五次算术完全正确）、**三次装置被外部阅读推翻而每次外部都是对的**、以及**四份被撤回的结论**。

**十次错误全部由计算产生，而抓住它们的从来不是更多的计算。**

## 状态

里程碑 M1 至 M5 完成，**M6 未完成**——编排器能跑、管线是真的，但环里的证书是作者的、场景里的证书是教科书算法、而那里的一致性检验是循环的。论文第 10.2 节精确陈述了这个缺口。
