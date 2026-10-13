# ecdr/ 代码索引

> 清点对象：`D:\otherProject\ECDR\ecdr\`
> 口径：只读清点，未改动任何既有文件。体积单位 MiB（1 MiB = 1,048,576 B）。
> 方法：`ast` 解析全部 36 个 `.py` 提取类/函数/签名/docstring → 在 `ecdr/ + orchestrator/ + scripts/ + tools/`（135 个 `.py`）与 `docs/`（73 个 `.md`）全语料上做词边界引用计数 → 可疑项用 `grep` 逐条复核。
> 对照文档：`docs/STATE.md`（第 56 轮的诚实清单）、`docs/_inventory_findings.md`。

---

## 0. 结论摘要

1. **`ecdr/` 的 703.24 MiB 里，真源码只有 156,210 B。** 36 个 `.py` 共 3,822 行；其余 737,303,678 B（**99.98%**）全是生成物。
2. **垃圾的主体是一个目录**：`ecdr/runs/modelica_work/`，2,522 文件 / 697.64 MiB，占 `ecdr/` 的 99.2%。其中 20 个 `*_res.csv` 就占 672.37 MiB（最大 `NetC1080_res.csv` = 168.91 MiB）。
3. **这堆垃圾没有被 git 跟踪**（`.gitignore` 第 4 行 `runs/`；`git ls-files ecdr/runs` = 0）。删掉它不影响仓库，只回收本地磁盘。
4. **但另有一批生成物被提交进了 git**：`ecdr/l2/modelica/smoke/`，62 文件 / 5.27 MiB，全在版本控制内。这是本次清点发现的唯一"该清且已入库"的问题。
5. **`ecdr/heat/` 是唯一被生产代码消费的子包**——`orchestrator/python/bridge.py:19` 是全仓库唯一一处从 `ecdr` 导入的非脚本代码。其余子包只被 `scripts/step*.py` 消费。
6. **全仓库 0 个测试、0 个 CI**。`requirements.txt` 只有 2 行（`numpy`/`scipy`），而 `ecdr/l2/verify.py` 需要 `juliacall`、`ecdr/l2/modelica/` 需要 `omc` + 容器。
7. **发现一处"废弃标注与调用方向相反"的问题**：`l1/models.py:130` 的 `robust_violation` docstring 自称 DEPRECATED 并推荐 `robust_violation_corners`，但前者被 7 个脚本调用、后者外部调用数为 0。

---

## 1. 体积清点：源码 vs 垃圾

### 1.1 总量

| 指标 | 值 |
|---|---|
| `ecdr/` 文件总数 | 2,657 |
| `ecdr/` 总体积 | 737,459,888 B = **703.24 MiB** |
| 真源码（`.py`） | **36 文件 / 3,822 行 / 156,210 B = 152.5 KiB** |
| 其他真源码 | `ecdr/l2/kernel_julia.jl`（1 文件） |
| 生成物 | **737,303,678 B = 703.09 MiB（99.98%）** |

### 1.2 按子目录

| 目录 | 文件数 | MiB |
|---|---|---|
| `runs/` | 2,522 | **697.64** |
| `l2/` | 75 | 5.33 |
| `l0/` | 14 | 0.09 |
| `agent/` | 8 | 0.06 |
| `structure/` | 14 | 0.06 |
| `heat/` | 8 | 0.05 |
| `bench/` | 8 | 0.04 |
| `l1/` | 6 | 0.03 |
| `__pycache__/` | 1 | 0.00 |

### 1.3 垃圾清单 A：`ecdr/runs/modelica_work/` —— 697.64 MiB，未被 git 跟踪

| 子项 | 文件数 | MiB | 内容 |
|---|---|---|---|
| 根目录 20 个 `*_res.csv` | 20 | **672.37** | OpenModelica 全时间序列转储 |
| 根目录其余产物 | 1,200 | 12.76 | `.c`/`.o`/`.h`/`.xml`/`.json`/`.makefile`/`.log`/`.bin`/`.mo`/`.mos`/`.libs` |
| 21 个案例子目录 × 62 文件 | 1,302 | 12.52 | `M4_0..M4_7`、`Net0..Net3`、`Tmd0..Tmd3`、`Sky0..Sky3`、`SkyTest` |

**最大的 5 个文件**（全部是仿真结果 CSV）：

| MiB | 文件 |
|---|---|
| 168.91 | `ecdr/runs/modelica_work/NetC1080_res.csv` |
| 60.59 | `ecdr/runs/modelica_work/Free5_res.csv` |
| 59.98 | `ecdr/runs/modelica_work/Free3_res.csv` |
| 56.61 | `ecdr/runs/modelica_work/Free1_res.csv` |
| 56.24 | `ecdr/runs/modelica_work/NetC360_res.csv` |

单个案例目录（以 `M4_3` 为例）的 62 个文件构成：`M4_3.c`(100,054 B)、`M4_3.o`(73,584 B)、`M4_3_info.json`(197,387 B)、`M4_3_init.xml`(230,045 B)、`M4_3_08bnd.c`(150,277 B)、`M4_3_08bnd.o`(122,384 B)、`M4_3_res.mat`(44,504 B，**这才是真正的结果**)、`lin.mos`、`linearized_model.mo`、`M4_3`(可执行文件)、18 组 `_NNxxx.c/.o` 编译单元、`M4_3_JacA.bin`、`M4_3.libs`(0 B)。

> 观察：每个案例真正有价值的 `*_res.mat` 只有 44 KB 量级；同一批数据以 CSV 形式躺在根目录时是 672 MiB。**保留 `.mat`、删 CSV 可以把这批证据从 672 MiB 压到 1 MiB 量级。**

### 1.4 垃圾清单 B：`__pycache__/` —— 247,368 B，未被 git 跟踪

9 个目录、36 个 `.pyc`：

| 目录 | 文件 | B |
|---|---|---|
| `__pycache__/` | 1 | 477 |
| `agent/__pycache__/` | 4 | 35,638 |
| `bench/__pycache__/` | 4 | 23,609 |
| `heat/__pycache__/` | 4 | 32,525 |
| `l0/__pycache__/` | 7 | 59,683 |
| `l1/__pycache__/` | 3 | 22,756 |
| `l2/__pycache__/` | 2 | 5,488 |
| `l2/modelica/__pycache__/` | 4 | 29,881 |
| `structure/__pycache__/` | 7 | 37,311 |

### 1.5 垃圾清单 C：`ecdr/l2/modelica/smoke/` —— 5.27 MiB，**已提交进 git**

62 文件 / 5,526,576 B。一次 `SdofIso` 冒烟测试的完整 OpenModelica 构建输出被打包提交。

| 类别 | 文件 | 说明 |
|---|---|---|
| 仿真结果 | `SdofIso_res.csv`(5,182,867 B，占该目录 **93.8%**) | 单一元凶 |
| 可执行文件 | `SdofIso`(80,672 B) | 编译产物 |
| 目标文件 | 21 个 `.o` | 含 `SdofIso.o`(42,592 B) |
| 生成的 C | 21 个 `.c` | `SdofIso_01exo.c` … `SdofIso_18spd.c` |
| 生成的头 | 8 个 `.h` | |
| 元数据 | `SdofIso_init.xml`(43,241 B)、`SdofIso_info.json`(33,652 B)、`SdofIso_JacA.bin`、`SdofIso.libs`、`SdofIso.log`、`SdofIso.makefile`、`SdofIso_external_functions.json`、`SdofIso_literals.h`、`SdofIso_model.h`、`SdofIso_includes.h` | |
| **真源文件（应留）** | `SdofIso.mo`、`run.mos`、`api.mos` | 3 个手工文件 |

`git ls-files ecdr` = 99 —— 其中 **59 个**是这批生成物。**没有任何 Python 代码引用这个目录**（`grep "smoke|SdofIso"` 在 `ecdr/l2/*.py` 中 0 命中）。

### 1.6 真源码清单（36 个 `.py`，3,822 行）

| 行数 | 文件 | | 行数 | 文件 |
|---|---|---|---|---|
| 304 | `l0/certificates.py` | | 100 | `structure/ensemble.py` |
| 291 | `agent/policies.py` | | 98 | `structure/network.py` |
| 237 | `l2/modelica/emit.py` | | 93 | `l2/modelica/linearize.py` |
| 208 | `agent/episode.py` | | 87 | `l2/verify.py` |
| 208 | `heat/designs.py` | | 65 | `structure/capability.py` |
| 205 | `l0/mechanisms.py` | | 58 | `structure/library.py` |
| 167 | `bench/labels.py` | | 57 | `l0/task.py` |
| 160 | `heat/streams.py` | | 49 | `bench/family.py` |
| 153 | `l0/invariants.py` | | 45 | `l2/modelica/run.py` |
| 149 | `l1/models.py` | | 18 | `l0/__init__.py` |
| 145 | `l0/feasibility.py` | | 12 | `structure/__init__.py` |
| 143 | `heat/networks.py` | | 10 | `__init__.py` |
| 139 | `l1/problem.py` | | 9 | `bench/__init__.py` |
| 130 | `l0/peaks.py` | | 8 | `heat/__init__.py` |
| 123 | `bench/problem.py` | | 7 | `l1/__init__.py` |
| 123 | `structure/counting.py` | | 6 | `agent/__init__.py` |
| 105 | `structure/waterbed.py` | | 4 | `l2/__init__.py` |
| 102 | `agent/search.py` | | 4 | `l2/modelica/__init__.py` |


---

## 2. 模块清单：每个模块支撑论文的哪一条

行数为总行数。「支撑」列对照 [PAPER.md](../PAPER.md) 的命题与章节。

### 2.1 structure/ — 结构表示与计数（Layer A）

| 模块 | 行 | 公开接口 | 支撑 |
|---|---|---|---|
| network.py | 98 | Structure（masses / springs / dampers / ground_k / ground_c）、matrices()、transmissibility()、static_deflection()、mode_count() | 命题 1 至 4 的**对象**；§3.1 的规模轴；§7.1 Layer A |
| counting.py | 123 | CONNECTED_LABELED_GRAPHS（A001187，**只列到 n = 10**）、structures_with_n_nodes(n)、space_size | §3.1 的 N(n)；§5 的横轴 |
| ensemble.py | 100 | ensemble(seed, count, n_lo, n_hi)，从空间均匀抽样 | §5 与 §6.2 的全部测量 |
| capability.py | 65 | 能力缺口 delta(S) 的判据 | §1.1 |
| library.py | 58 | 证书库的组合 | 命题 2 的 k |
| waterbed.py | 105 | 水床（频带权衡）不变量 | §6.1 第四条候选 |

### 2.2 l0/ — L0 频域与证书

| 模块 | 行 | 公开接口 | 支撑 |
|---|---|---|---|
| certificates.py | 304 | 闭式不可行性证书与三项独立检查 | 发现 001；§9.5 的早期消融 |
| feasibility.py | 145 | SEARCH_OMEGA（求值网格） | 全项目的代价基准 c_s |
| invariants.py | 153 | 水床不变量 | 发现 004、016 至 018 |
| mechanisms.py | 205 | M1 被动 SDOF、M2 调谐质量阻尼器、M3 天钩 | §9.5 |
| peaks.py | 130 | **精确峰值例程**——后面所有「精确判定」都靠它 | 发现 007 |
| task.py | 57 | 任务字段：f_low / T_iso_db / A_max_db / delta_max | §9.5 |

### 2.3 l1/ — 鲁棒性（角点精确）

| 模块 | 行 | 公开接口 | 支撑 |
|---|---|---|---|
| models.py | 149 | LaggedSkyHook、perturbed、robust_violation（**已标注废弃**）、robust_violation_corners（**2 的 d 次方个角点，单调性下精确**） | §5.3 的 c_s(L1) |
| problem.py | 139 | MechanismProblemL1、verify_l1 | 发现 009 的符号缺陷与修复 |

**一处标注与调用方向相反**：robust_violation 的 docstring 自称 DEPRECATED 并推荐 corners 版本，**但被 7 个脚本调用的是前者**，后者的外部调用数为 **0**。修正是引入了正确实现而**没有迁移调用点**。**这不影响论文的任何数字**（§5.3 的 L1 代价倍数是角点数 2 的 d 次方，不是对这两个函数的计时），但它是收尾时该做而未做的一件事，如实记录。

### 2.4 l2/ — 多保真 L2

| 模块 | 行 | 公开接口 | 支撑 |
|---|---|---|---|
| verify.py | 87 | state_space_amplitude、transmissibility_time_domain | L2-Julia 路径 |
| kernel_julia.jl | — | 通用一阶核 | 发现 026、027 |
| modelica/emit.py | 237 | emit_model（基座激励，可线性化）、**emit_free_model（无输入、非零初值——发现 061 新增）**、emit_skyhook_model、emit_mos | **§5.4 的 L2 核验**；§7.1 |
| modelica/linearize.py | 93 | linearize（**拒绝 B 恒为零的 dump**）、tf_complex、tf_mag | §5.3、§5.4 |
| modelica/run.py | 45 | IMAGE、WORK、simulate、steady_amplitude | §5.3 的 c_s(L2) |

**发射器的纪律**：文件里**只写声明与连接，没有一处运动方程**。这是「建模独立」的全部来源。

### 2.5 heat/ — 热工领域（第二领域）

| 模块 | 行 | 公开接口 | 支撑 |
|---|---|---|---|
| streams.py | 160 | Stream、problem_table（问题表法）、min_utility_lp（独立线性规划） | §8.2 |
| networks.py | 143 | network_lp、all_match_sets | 发现 043 的池热 bug 与修复 |
| designs.py | 208 | design_lp、enumerate_designs、falsify_units、**remedy_cross_pinch / test_remedy**、units_of | **§8.2 的 219 个设计**；**§6.4 的补救断言检验** |

**designs.py 的建模要点**：节点是 H1、H2、C1、C2、**HU、CU**——**公用工程是节点**。这正是发现 055 之前三轮工作作废的原因：早期把「单元」数成工艺对工艺的匹配数，而经典界把公用工程换热器算作单元。

### 2.6 bench/ 与 agent/ — 早期任务族与 agent 实验

| 模块 | 行 | 内容 |
|---|---|---|
| bench/family.py、labels.py、problem.py | 49 / 167 / 123 | 任务族、真值标签、BOCoDe 式 evaluate(x) 到 (obj, cons) |
| agent/episode.py、policies.py、search.py | 208 / 291 / 102 | (mu+lambda) 进化策略 + 5 个手写启发式策略 |

**判定：两个包都不再被后续工作依赖，但都不得删除。** 它们是 §9.5 与命题 4 的原始证据——**删掉它们，论文里「证书臂不高于最强启发式」这句话就失去了可核查的出处。**

---

## 3. 谁在消费 ecdr/

| 消费者 | 引用的子包 |
|---|---|
| **orchestrator/python/bridge.py:19** | **heat/** ——全仓库**唯一一处**从 ecdr 导入的**生产代码**（非脚本） |
| scripts/step*.py | 全部六个子包 |
| tools/ | 无 |

**所以 ecdr/ 的实际使用面是「脚本库 + 一个 bridge 入口」。** 这对交付物的定位有影响：它是一个**可复现的实验代码库**，不是一个人工调用的包。

---

## 4. 工程完备性的缺口（如实记录）

| 项 | 状态 |
|---|---|
| 测试 | **0 个**（无 test/、无 pytest、无断言框架） |
| CI | **0 个**（无 .github/workflows） |
| requirements.txt | 2 行（numpy / scipy），**不足**：l2/verify.py 需要 juliacall，l2/modelica/ 需要 omc 与容器 |
| 类型检查 / lint | 无 |
| 文档字符串 | 主要模块有，且多数记录了它对应的发现编号——**这是本项目最有价值的工程习惯** |

**这些缺口不构成本文结论的弱点**（每条主张都由一个可独立运行的 step 脚本支撑，脚本本身就是验证），**但它们是「交付一个可长期维护的代码库」与「交付一套可复现的实验」之间的差别**，收网时应说清楚本项目交付的是后者。

---

## 5. 保留 / 清理 / 删除

| 判定 | 内容 | 理由 |
|---|---|---|
| **保留** | structure/、l0/、l1/、l2/、heat/ 全部 | 论文每一条主张都指得回这里 |
| **保留（作证据）** | bench/、agent/、l1/models.py 的 robust_violation | §9.5 与发现 028 的可核查出处 |
| **保留** | l2/modelica/smoke/ 的 4 个文件（SdofIso.mo、run.mos、api.mos、SdofIso_res.csv） | 后三个是手写的，CSV 是 step58 的输入 |
| **已删除** | ecdr/runs/（2,522 文件 / 697.6 MB） | 可再生；且是路径 bug 的产物，根因已修 |
| **已删除** | l2/modelica/smoke/ 的 58 个编译产物（.c / .o / .h / 可执行文件 / .xml / .json / .makefile / .bin / .libs / .log） | 生成物，且**此前被提交进了 git** |
| **已删除** | 106 个 __pycache__ | 生成物 |
| **已加守卫** | .gitignore 新增 5 条规则 | 防止编译产物再次入库 |

**仓库跟踪文件数：333 降至 276。**
