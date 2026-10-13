# scripts/ 与 runs/ 可复现链条索引

> 清点时间：本次会话。**本文只读清点，未执行任何脚本**；所有数字直接抄自磁盘上的 JSON/源码原文。
> 时间戳取自文件 mtime（本机本地时间）。引用文献：`docs/STATE.md`（第 56 轮的诚实清单）、`docs/ROADMAP.md`、`docs/findings/001–063`。

## 0. 清点口径与总量

| 项 | 实测 | 说明 |
|---|---|---|
| `scripts/` glob 命中 | **95 项** | = 94 个 `.py` + 1 个 `__pycache__/_bootstrap.cpython-314.pyc` |
| 其中 `step*.py` | **89 个** | = 88 个编号脚本（step1…step88，**无缺号**）+ `step12b_analyse.py` |
| 非 step 脚本 | 5 个 | `_bootstrap.py`、`diag_m2_waterbed.py`、`diag_peak_m2.py`、`diag_asym.py`、`julia_setup.py` |
| `runs/` 文件数 | **204** | = 顶层 79 个（73 `.json` + 6 `.txt`）+ `modelica_work/` 125 个 |
| `runs/` 总体积 | 1,857,461 B = **1.77 MiB** | 见 §4 |
| 脚本写出的 JSON | **72 个** | 由 `(out / "x.json").write_text(...)` 之类语句产生 |
| orchestrator 写出的 JSON | 2 个 | `argue_result.json`（`orchestrator/src/argue.ts:253`）、`witness_audit.json`（`audit.ts:83`） |
| 声明但磁盘不存在的产物 | **1 个** | `runs/rhp_zeros.json`（step33 声明要写，文件不在） |
| 对账 | 72 − 1 + 2 = 73 = 顶层 JSON 数 ✓ | |
| 脚本 mtime 跨度 | 2026-10-12T14:52 → 2026-10-13T01:10 | 全程约 10 小时 18 分 |

**判定口径**（本文所有"在用/失效"结论都按这三条判定，可复核）：

* **在用**：产物被 docs/ **按名**引用，或数字被 finding 正文引用，或位于 STATE §2/§3 六条可宣称主张的依赖链上；
* **失效**：产物被后来的同路径脚本覆盖 / 声明的产物不存在 / 判词被同线后续脚本用同一份数据推翻（finding 明写）；
* **一次性**：只向 stdout 输出，结论一次性写进 finding，不被任何后续脚本或 orchestrator 依赖（仍可复现，但没有下游）。

**对任务前提的一处更正**：step44 并没有被撤回。被撤回/降级的是 Finding 019 的"topology vs value"读法（由 Finding 020 用 step42/43 的 overlap 规则取代），而 step44/45 是**修正** Finding 020 悲观读法的证据（Finding 021：有效维度 4.62）。真正记录在案的撤回是 STATE §5.3 的四条：**037、044 被 055 撤回；038 被 040 撤回；051 被 052 撤回**。step37 确实是死胡同（被 step38 取代），理由见 §2。

---

## 1. 从脚本到论文主张的映射

格式：**脚本 → 算什么 | 读什么 | 写什么 | 支撑哪条结论**。全部脚本默认读 `ecdr/` 包内模块与 `_bootstrap`，只有文件级输入/输出才在表内注明。

### 1.1 阶段 A：L0 证书、机制与任务族（Finding 001–009 的底座）

| 脚本 | 算什么 | 读什么 | 写什么 | 支撑的结论 |
|---|---|---|---|---|
| `step1_certificate.py` | 闭式 M1 不可行性证书的三项独立检查：F1–F3 单调性、闭式 `r*` vs 数值求根、致密网格证伪 | 无文件输入 | stdout | Finding 001；STATE §2 "M1 由精确程序判定"的前提 |
| `step2_escape_ladder.py` | 逃生阶梯：初始机制可证不足 + 另一机制类存在见证 | 无 | stdout | Finding 001/006 的"Design-Space Escape Task"定义 |
| `step3_m2_analysis.py` | 被动 2-DOF 是否能逃生的 Pareto 结构化扫描（差分进化失败后的重做） | 无 | stdout | Finding 001–003 的 M2 段（Finding 009 已降级其中的 Λ₂ 论证） |
| `step4_m2_refine.py` | 同上的加密 Pareto 扫描（把 omega_n1 钉在 omega_n_min，去掉一维） | 无 | `runs/step4_m2_refine.json`（1,186 B，**孤儿**） | Finding 003；产物无下游 |
| `step5_waterbed.py` | 水床不变量：Vieta 闭式 vs 精确物理值、按机制分类的 `(n1/n0 − d1/d0)` | 无 | stdout | Finding 004；`ecdr/l0/invariants.py` 的验证路径 |
| `step6_waterbed_budget.py` | 水床预算作为被动机制的必要条件（floor 0.0073293559887942766 vs M1 最好 0.0064953954734681555、M2 最好 0.01362701266430849） | 无 | `runs/step6_waterbed_budget.json`（434 B，**孤儿**） | Finding 004；产物无下游 |
| `step7_exact_peak.py` | 精确峰值例程 vs 闭式与致密暴力扫描（回归） | 无 | stdout | step12/step15 的"M2 判定用精确峰值"这一说法的依据 |
| `step8_waterbed_exact.py` | 水床预算全走良态 2×2 求解路线（floor 0.0073293559887942766；M1 最好 0.00650817525321487，M2 最好 0.008186671889507752） | 无 | `runs/step8_waterbed_exact.json`（351 B，**孤儿**） | Finding 004 的数值收口 |
| `step9_task_family.py` | 造 11 个带真值标签的逃生任务族，逐机制记录"结论 + 依据类型" | 无 | `runs/task_family.json`（14,581 B，11 个任务） | Finding 006；**被 step12 读取** |
| `step10_thresholds.py` | 两个逃生深度阈值的定位：M1 阈值 `172.23706272343517 Hz`、M2 阈值 `132.42530648581 Hz`（n_examined 44,688，n_peak_feasible 12,182） | 无 | `runs/thresholds.json`（50,184 B） | Finding 006（docs 按名引用 `runs/thresholds.json`） |
| `step11_baseline_smoke.py` | 局部细化基线在单机制上的冒烟 | 无 | stdout | Finding 007 的方法学前置；被 step12 取代 |
| `step12_ablation.py` | 头条消融：11 任务 × 7 arm × 3 seed = **231 episodes**，budget 2500，唯一变量是"放弃信号" | `runs/task_family.json` | `runs/ablation.json`（82,160 B） | Finding 007（自述 "partial support with a serious methodological caveat"） |
| `step12b_analyse.py` | 消融的分层分析（按 depth 分带，隔离"决策质量"与"搜索强度"） | `runs/ablation.json` | stdout | Finding 007 的表格；无产物 |
| `step13_asymptote_check.py` | 高频渐近线是否给 `|T|` 下界（若成立即可证 M2 不可行） | 无 | stdout | 结论：**该路线关闭**（ratio < 1，是上界）→ 见 §2 |
| `step14_l1.py` | L1 阶梯：带宽→∞ 时 L1 复现 L0；L0 不可行 ⇒ L1 不可行 | 无 | stdout | Finding 008 |
| `step15_l1_threshold.py` | 鲁棒性是否移动 L0 阈值：`{"L0": 172.3388671875, "L1 +-5 percent": 203.1005859375, "L1 +-10 percent": 239.7216796875}` | 无 | `runs/l1_threshold.json`（118 B） | Finding 008（**其 239.72 Hz 已被 step56 修正为 258.7646484375**，见 §2） |
| `step16_false_positive_zone.py` | 假阳性区 172.34–239.72 Hz：L0 证书说可行、L1 下一个都活不下来 | 无 | stdout | Finding 008（区间右端被 step56/57 修正为 258.76 Hz） |
| `step17_l1_ablation.py` | L1 消融：6 任务 × 7 arm × 3 seed = **126 episodes**，budget 1500 | 无 | `runs/l1_ablation.json`（40,068 B） | 只有 `docs/CONSENSUS.md` §3.4 引用；**没有任何 finding 引用**（见 §2） |
| `step18_l1_sign_check.py` | 复现 `MechanismProblemL1.evaluate()` 的 `max` 应为 `min` 的符号缺陷并验证修复 | 无 | stdout | `docs/CONSENSUS.md` §3.1；无 finding 编号 |

### 1.2 阶段 B：结构空间、g(N) 与证书库（Finding 010–025）

| 脚本 | 算什么 | 读什么 | 写什么 | 支撑的结论 |
|---|---|---|---|---|
| `step19_gN_census.py` | g(N) 普查：I1 模态 `g=32` 恒定（占比 1.0 → 4.970e-10）、I2/I3 占比约 0.14–0.68 持续 | 无 | `runs/census_gN.json`（2,776 B） | Finding 010（文件本身未被按名引用） |
| `step20_library.py` | 库组合论证 + 稀疏（树）空间普查：N=6.4384e10、f=0.5 时只需 **35.906 张证书**，separation **1.793e9** | 无 | `runs/library.json`（1,779 B） | Finding 011；ROADMAP §5.4 的 `k=O(log N/log(1/(1−f)))` |
| `step21_network_verify.py` | 通用网络求值器 vs 手写 L0 机制（不一致则上面一切不可信） | 无 | stdout | Finding 012 的前置 |
| `step22_coverage_ensemble.py` | 覆盖度是 (不变量, 集成, 需求) 三元组的性质：连续界 vs 离散界在两个集成上的覆盖 | 无 | `runs/coverage_ensemble.json`（1,667 B；n_samples 3000，挠度中位数 spread 13.049 vs concentrated 31.167） | Finding 012 |
| `step23_composition.py` | 三条需求轴是否可组合（600 结构；marginals/成对/三轴） | 无 | `runs/composition.json`（970 B；`any_frac=1`：**退化校准**） | Finding 013 —— 正是"退化"这一发现导致 step24 |
| `step24_calibration.py` | 在非退化校准下重测组合：independence_ratio **0.4373101345165974**，product_of_marginals 0.11433533333333333 | 无 | `runs/calibration.json`（2,463 B） | Finding 013 的修正（"走向空集"的校准失败被当场抓住） |
| `step25_structural_features.py` | 结构特征作为独立覆盖来源：按结构特征分区看失败率；并证伪高频渐近线断言 | 无 | `runs/structural_features.json`（1,978 B；base_survival 0.085，grounded 0.072，ungrounded 0.0943，渐近线最坏相对误差 1.6438e-4） | Finding 014 |
| `step26_asymptote_rate.py` | 去掉"asym>0"守卫后重测高频律，得到 `omega*T → g0/m0` | 无 | stdout | Finding 014（改正了 step25 那个"测试不可能失败"的守卫） |
| `step27_independence.py` | 结构切割 vs 性能切割的成对独立性（21 对 × 3 seed） | 无 | `runs/independence.json`（4,140 B） | Finding 015（其"独立性来自结构特征"的处方被 step41/42 推翻） |
| `step28_waterbed.py` | 被动网络水床积分恒为 0 的（错误的）数值路线：max_abs_numeric_W 0.012110969814513808 | 无 | `runs/waterbed.json`（252 B，**孤儿**） | Finding 016；数值路线被 step32 取代 |
| `step29_waterbed_residual.py` | 残差是求积误差还是真违背（加密网格） | 无 | stdout | Finding 016；**其判词被 step30 用同一张表推翻** |
| `step30_waterbed_disagreement.py` | 统计与闭式不符的结构数 | 无 | `runs/waterbed_disagreement.json`（1,345 B，孤儿） | Finding 016 |
| `step31_waterbed_quadcheck.py` | 梯形法错了还是围道论证错了（scipy.quad 独立复核） | 无 | `runs/waterbed_quadcheck.json`（1,554 B，孤儿） | Finding 017 |
| `step32_waterbed_stable.py` | 数值良态的水床积分（直接在 w 上积分 + 解析尾部） | 无 | `runs/waterbed_stable.json`（1,268 B；sdof 1.659e-12；列出 10 个被旧陷阱误伤的结构） | Finding 017；**取代 step28/29/30/31 的数值路线** |
| `step33_rhp_zeros.py` | 围道论证的漏洞：T 的右半平面零点 ⟺ W≠0 | 无 | `runs/rhp_zeros.json` —— **文件不存在** | Finding 017；产物缺失，见 §2 |
| `step34_waterbed_formula.py` | 闭式 `W = pi*Σ_{Re z>0} Re(1/z)` 的首次检验（numpy 伴随矩阵求根） | 无 | `runs/waterbed_formula.json`（226 B，孤儿） | Finding 018；度 8/12 通过、更高阶差 17–33 倍 |
| `step35_waterbed_formula_hp.py` | 高精度系数 + mpmath 求根（系数序错误） | 无 | `runs/waterbed_formula_hp.json`（206 B，孤儿） | Finding 018；被 step38 取代 |
| `step36_waterbed_formula_final.py` | 用多点最小二乘拟合、真实 P 验证（仍在错误链条上） | 无 | `runs/waterbed_formula_final.json`（**与 step38 同路径**） | Finding 018；文件现有内容是 **step38 写的** |
| `step37_diagnose_degree.py` | 单网络诊断：系数次数 2n−1 vs 2n、两套根、真实 `|P(z)|` | 无 | stdout | Finding 018 链条中的诊断；被 step38 判定为又是"系数序传反"，见 §2 |
| `step38_waterbed_formula_final.py` | mpmath 系数序修正后的闭式（numpy roots: 2 个 RHP 根，`|P|/scale=2.7e-07`，`pi*ΣRe(1/z)=1.21109588e-02` 与数值积分 1.2110968083e-02 一致） | 无 | `runs/waterbed_formula_final.json`（272 B；max_rel_diff 7.702e-7；no_rhp_zero_count 85，其 max_W 1.049e-9） | Finding 018 的最终版本 |
| `step39_waterbed_ratio.py` | 比值 `W_formula/W_numeric` 的分布与按次数分解（无残差过滤器会掩盖失败） | 无 | `runs/waterbed_ratio.json`（755 B；compared 24，within_1e-3 11；n=7 median_err 86.15，n=8 median_err 54.63） | Finding 018 的诚实边界（高阶仍不可靠） |
| `step40_certificate_independence.py` | 两张候选证书（payload tie `g0/m0` 与水床 `W`）是否在独立轴上 | 无 | `runs/certificate_independence.json`（1,352 B） | Finding 019 |
| `step41_topology_vs_value.py` | 把两类切割放在一起算 28 对，比较族内与跨族 | 无 | `runs/topology_vs_value.json`（4,031 B） | Finding 019 |
| `step42_overlap_rule.py` | 用受控重叠检验更一般的规则：disjoint_mean **0.9761494252873563** vs shared_mean **1.0** | 无 | `runs/overlap_rule.json`（1,082 B） | Finding 020（topology/value 之分被"重叠"取代） |
| `step43_separation_test.py` | 该分离是否统计上真实（bootstrap）：val_mean 0.8861599586600726，top_mean 1.1338601402831037，差 0.24770018162303103，gap_excludes_zero true | 无 | `runs/separation_test.json`（329 B） | Finding 020 |
| `step44_capability_dimension.py` | 能力空间到底几个独立轴：participation_ratio **4.621301001759276**，leading_share 0.3607668459862495 | 无 | `runs/capability_dimension.json`（1,380 B） | Finding 021（**修正** Finding 020 的悲观读法，未被撤回） |
| `step45_key_pairs.py` | 近零相关是噪声还是真的（bootstrap + 换种子） | 无 | `runs/key_pairs.json`（817 B） | Finding 021 |
| `step46_library_composition.py` | 两张证书在"库"意义下是否可组合（跨规模；fixed 与 calibrated 两种需求） | 无 | `runs/library_composition.json`（1,557 B；calibrated 的 `f_B_conditional` 0.525–0.558，ratio 0.88–0.95） | Finding 022 |
| `step47_rayleigh_bound.py` | 时间尺度族：Rayleigh 试向量 1 给 `omega_1^2 <= Σk_ground/Σm`，与真实最小广义特征值对照（violations **0**，median_tightness 2.729528960711694，rho_bound_vs_n −0.006382630457615112） | 无 | `runs/rayleigh_bound.json`（217 B） | Finding 023（C3 慢证书） |
| `step48_three_certificate.py` | 三张证书联合存活 vs 边缘乘积（mean_ratio **0.391424564428569**；外推修正 3→0.1532、5→0.02347、10→2.157e-4、20→1.821e-8） | 无 | `runs/three_certificate.json`（1,225 B） | Finding 023 |
| `step49_conditionals.py` | 把"比值 <1 好"的读法纠正为条件概率：`f2_given_1` 0.5354–0.5504，`f3_given_12` 0.7596–0.8061 | 无 | `runs/conditionals.json`（1,257 B） | Finding 023（**方向错误**的更正：比值越大越冗余） |
| `step50_fourth_certificate.py` | 第四张证书 C4 fast（无穷范数界），换集成族与校准重复：violations **0**，max_ratio 0.9978306963226589 | 无 | `runs/fourth_certificate.json`（79 B） | Finding 024 |
| `step51_calibration_sweep.py` | 扫单一紧度参数 f，四张证书的边缘都恰为 f：f=0.5 时 survival **0.03125**（rounds_1e10 6.64），f=0.6 时 0.005，f=0.7 时 0 | 无 | `runs/calibration_sweep.json`（10,106 B，含 `Infinity` 字面量，**不是合法 JSON**） | Finding 025；**step80 的 `f=0.65` 出自这条线** |

### 1.3 阶段 C：L2 / Modelica 保真度阶梯（Finding 026–034、060–061）

| 脚本 | 算什么 | 读什么 | 写什么 | 支撑的结论 |
|---|---|---|---|---|
| `step52_l2_verify.py` | L0/L1 vs Julia 积分（L2）的交叉验证：median_rel 2.4686e-6，max_rel **0.0538811800412544** | 无 | `runs/l2_crossvalidation.json`（2,066 B） | Finding 026 |
| `step53_l2_convergence.py` | 那 5.39e-2 的分歧是未收敛瞬态还是真冲突（在共振点 omega=43.4737 上加密周期） | 无 | `runs/l2_convergence.json`（1,410 B，10 行） | Finding 026 |
| `step54_l1_crossvalidation.py` | 从未被仿真的 L1 时滞 sky-hook：闭式 vs 同一组方程的积分 | 无 | `runs/l1_crossvalidation.json`（3,542 B；T_max_rel 9.2207e-7，F_max_rel 1.2362e-6） | Finding 027 |
| `step55_robust_sampling.py` | `robust_violation` 的 12 次随机抽样是不是真的最坏情况（**n_flips = 3**） | 无 | `runs/robust_sampling_check.json`（899 B） | Finding 028 |
| `step56_robust_corners.py` | 用 2^d 角点重算阈值：L0 **172.3388671875**、L1±10% 角点 **258.7646484375**、L1±10% 12 次抽样 239.72；最坏点 = nominal×(1.1, 1.1) = (121.56111009014111, 0.6550561797752809) | 无 | `runs/robust_corners.json`（916 B） | Finding 028（**移走 Finding 008 的阈值**） |
| `step57_l1_labels_corrected.py` | 修正后有多少"鲁棒"标签失效：`total_false_robust = 33`，zone **[172.34, 258.76]**，inside [180, 210, 240] | 无 | `runs/l1_labels_corrected.json`（1,736 B） | Finding 029 |
| `step58_modelica_smoke.py` | 读 Modelica CSV 与 L0 对照（单自由度）：rel_diff **8.306e-6** | `ecdr/l2/modelica/smoke/SdofIso_res.csv` | `runs/modelica_smoke.json`（705 B） | Finding 030 |
| `step59_modelica_ensemble.py` | 通用 emitter 把随机网络发射成 Modelica 再对照 L0 | 无 | `runs/modelica_ensemble.json`（1,609 B，8 行） | Finding 031 |
| `step60_modelica_convergence.py` | 那 3.72 倍的分歧是否未收敛瞬态：40→120→360→1080 周期，ratio 3.7234→1.7246→1.0219→**0.9997756097312523** | 无 | `runs/modelica_convergence.json`（790 B） | Finding 031 |
| `step61_linearize_check.py` | 线性化模型 vs L0；`Position(exact=true)` 陷阱（omc 把 B 留成 0） | `runs/modelica_work/*.mo` | `runs/linearize_check.json`（1,376 B，8 行） | Finding 032 |
| `step62_modelica_skyhook.py` | 时滞 sky-hook 过 Modelica（3 个频率，T 与 F 双列对照） | 无 | `runs/modelica_skyhook.json`（496 B） | Finding 033 |
| `step63_modelica_l1_full.py` | L1 全套 12 项对照走 MSL 组件 + 被动网络集成过线性化 | 无 | `runs/modelica_l1_full.json`（4,624 B；skyhook 12 行、networks 8 行） | Finding 033 |
| `step64_modelica_tmd.py` | TMD 过通用 emitter（4 case × 4 频率 = 16 行，最坏 rel **7.6366e-7**） | 无 | `runs/modelica_tmd.json`（3,558 B） | Finding 034；STATE §4 M2 |
| `step82_m4_ladder.py` | **成本阶梯**：`c_s_L0=1.5090069998404943e-03`、`c_s_L1=6.036027999361977e-03`、`c_s_L2=1.8815941749853664` s；n=10 分离度 L0 9.2957e14 / L1 3.4462e15 / L2 **3.430588e16**；L2 对照 L0 最坏 4.618e-7；agreement [0, 8] | 无 | `runs/m4_ladder.json`（4,722 B） | Finding 060；STATE §3.2 全表 |
| `step83_m4_free_response.py` | C1 对抗 L2 **自由响应**（新 `emit_free_model`，无输入）：峰数 ≤ n、峰频对齐 L0 | 无 | `runs/m4_free_response.json`（2,778 B）；**其 `worst_rel` 最大 0.9614006260899509 的判词无效** | Finding 061（数据被 step84/85 复用，判词被 step84 纠正） |
| `step84_m4_free_fixed.py` | 把指标方向改对，并（无效地）用 L0 传递率峰当固有频率 | `runs/m4_free_response.json` | `runs/m4_free_response_fixed.json`（3,579 B；worst_peak_to_mode 0.06113905724136242；cross_check worst_rel 0.8208231611427141） | 被 step85 取代，见 §2 |
| `step85_m4_l0_free.py` | **同一个程序**在 L0 上做自由响应集成再比 L2：n_violated **0**，worst_l2_to_l0 **9.499950000198741e-05**，l0_ok true，L0 峰 vs 特征值最坏 0.061038259137264336 | `runs/m4_free_response.json` | `runs/m4_l0_free.json`（3,613 B） | Finding 061 = STATE §3.5（"9.50e-05 一致、0 次违背"） |

### 1.4 阶段 D：热域 / M6（Finding 035–048、054–059、063）

| 脚本 | 算什么 | 读什么 | 写什么 | 支撑的结论 |
|---|---|---|---|---|
| `step65_heat_min_utility.py` | 最小热公用工程两条独立路线（问题表 vs 运输 LP），12 行 diff 全 0 | 无 | `runs/heat_min_utility.json`（1,912 B；教科书 4 流 dt_min=10 时 Q_H 142.5、Q_C 150.0、pinch 105.0） | Finding 035 |
| `step66_heat_ecdr_question.py` | 在非自造领域跑 ECDR 形状：证书 Q_H_min vs 枚举最优网络（4-stream：证书 142.5、枚举 15 个网络、Q*=128.25、certificate_rules_out true；3x2：63 个网络、Q*=0） | 无 | `runs/heat_ecdr_question.json`（1,022 B） | Finding 035/036 |
| `step67_heat_min_units.py` | U ≥ N−1 是否 sound：4-stream（N=5）min_units_attaining **2**、`sound: false` | 无 | `runs/heat_min_units.json`（1,003 B） | Finding 037 → **被 Finding 055 撤回**（单位计数不同，见 §2） |
| `step68_llm_scenarios.py` | 生成 6 个随机流集 + 真值（model 从未见过真值） | 无 | `runs/llm_scenarios.json`（3,114 B，6 个场景 R1…，首例 Q_H_min 142） | Finding 041/042；**orchestrator `--random` 读它**（`random.ts:35`） |
| `step69_pool_heat_check.py` | 模型的反驳成立吗：`network_lp` 让池热流向未匹配的流股，报出 142.5 而任何这样的网络至少 150.0 | 无 | stdout | Finding 043（**我的检查器错了，模型的反对是对的**） |
| `step70_network_model_validated.py` | 修正后的网络模型在**两个**工况都验证：all-matches 三例全等（142.5/60.0/0.0）、按单位数最优 {1:232.5, 2:150.0, 3:142.5, 4:142.5}、fewest_units_attaining **3**、`counterexample_Q_H 150.0 = agent_floor 150.0` | 无 | `runs/network_model_validated.json`（496 B） | Finding 044（模型修正是对的；其**计数解释被 055 撤回**） |
| `step71_witness_truth.py` | 4 个声称见证的真值（W1 真值 150.0 不合格、W2 142.5 合格、W3 332.5 不合格、W4 142.5 合格） | 无 | `runs/witness_truth.json`（991 B） | Finding 045 的 ground truth；agent 侧产物是 `runs/witness_audit.json`（77,418 B，orchestrator `--audit` 写） |
| `step72_units_bound.py` | 给 agent 8 个已解实例 + 1 个留出实例（**答案未知**的界） | 无 | `runs/units_bound.json`（6,367 B；train 8 行，test 1 行：dt_min 10、Q_H_min 609、min_units 3） | Finding 048；**orchestrator `--unitsbound` 读它**（`unitsbound.ts:28`）；产物未被 docs 按名引用 |
| `step78_utility_units.py` | 3 单位网络之争 + "公用工程换热器算不算一个 unit"：N=**6**、N−1=**5**；3 个 match + 2 个公用工程换热器 = 7 units，4 个 match + 2 = 8 | 无 | `runs/utility_units.json`（679 B） | Finding 055 |
| `step79_design_units.py` | 把公用工程建成节点（N=6：H1,H2,C1,C2,HU,CU）并枚举 219 个设计：最少 **5 units** 达到 Q_H_min 142.5；by_units {4:150.0, 5:142.5, …} | 无 | `runs/design_units.json`（367 B） | Finding 056（**经典 U_min = N−1 从未被推翻**） |
| `step81_m5_named_remedy.py` | M5：证书点名的补救（"a cross-pinch exchanger"）照做能否构造出可行结构：pinch_shifted 105.0、Q_H_min 142.5、four_unit_designs_attaining **0**、spanning_matches ["H1-C1"]、`M5_holds: true` | 无 | `runs/m5_named_remedy.json`（183 B） | Finding 059；STATE §3.6 |

### 1.5 阶段 E：成本轴、交叉点与命题 4（Finding 049–053、058）

| 脚本 | 算什么 | 读什么 | 写什么 | 支撑的结论 |
|---|---|---|---|---|
| `step73_crossing_measured.py` | 在真实代码路径上测 Prop 2 的三个常数：`c_s 9.164e-04`（min 8.912e-4 / max 1.0219e-3）、`c_v 3.97515e-08`（批量 200,000 次）、`c_p 1.00000761e-06`、阈值 `(c_p+c_v)/c_s = 1.1346127481892362e-03`、`first_crossing_n = 1`；g(N) 1/4/32/602/23,170/1,705,522/238,720,034/64,383,610,994/33,941,788,348,786/35,323,849,620,845,554 | 无 | `runs/crossing_measured.json`（985 B） | **Finding 049 §7.4 逐字引用这些数字**；结论是"条件 1 几乎无内容"（任何排除 1 个结构的谓词都过） |
| `step74_two_routes.py` | 三条路线放同一条秒轴上（route B/C/A）：c_s 1.044865750009194e-3、c_v 5.348899998352863e-08、c_p 9.414499800186604e-07、阈值 9.522170479733253e-4、M=100、cost_sampling 0.10448657500091939 恒定；C1 的 fraction 0.125 → 1.132379410210005e-16 | 无 | `runs/two_routes.json`（1,878 B） | Finding 050（C1 落到 ROADMAP §5.4 第 1 行"永无交叉；装饰品"） |
| `step75_library_cost.py` | 四张证书的**检查成本差几个数量级**，且按顺序只施加于幸存者：c_v modal 4.575e-8 / statics 8.0392e-6 / slow 4.5375e-7 / fast 9.581e-6；applied_to 400→201→86→18；`library_total 0.0024131000391207635` vs `enumeration_total 0.8693939600023441`；survivors 6 | 无 | `runs/library_cost.json`（849 B） | Finding 051（其"证书路线是 Θ(N)"的读法**在下一轮被 052 撤回**） |
| `step76_three_procedures.py` | 三种程序在同一被排除集合上：cert/heur/enum，`cert_over_heur 8.3097e-05` 恒定、`cert_over_enum 3.99953` 恒定（g=4 时）→ scaling 段 3.9995 → 3.39378e13 | 无 | `runs/three_procedures.json`（3,529 B） | Finding 052（**051 测的是启发式，不是证书**） |
| `step77_proposition4.py` | 命题 4：三种程序排除**同一个** C（`pruning_identical: true`），成本分别 c_p+c_v / g·c_v_apply / g·c_s；`constant_cs_over_cvapply = 44154.95313655758`；八个规模逐行 `sep_enum = predicted_sep_enum`（n=10：g 33,941,788,348,786，cert 0.0021527536499975717 s，heur 1,654,661.9395488366 s，enum 73,061,520,397.62436 s，sep 3.393863501181697e13）；`formula_holds: true` | 无 | `runs/proposition4.json`（2,316 B） | Finding 053；STATE §2 Prop 4"八个规模上精确" |
| `step80_curve_b.py` | 补上从未建过的曲线 **(b)**：hybrid 成本 = k(c_p+c_v) + remainder·c_s，f=0.65，k = 4/7/10/14/19/24/30/37；三臂指数 `exponent_a 1.0`、`exponent_b 0.05507407923312987`、`exponent_c 0.05965716302820119`；ratio_ab 6.4（n=3）→ **9.295749900222514e14**（n=10） | 无 | `runs/curve_b.json`（1,618 B） | Finding 058；STATE §3.1 全表（三条臂 + 交叉点位置） |

### 1.6 阶段 F：M1 收口（Finding 062）

| 脚本 | 算什么 | 读什么 | 写什么 | 支撑的结论 |
|---|---|---|---|---|
| `step86_m1_growth.py` | 逐规模均匀采样（**PER_N = 400**，n=3…8）测各证书覆盖：tau_slow 6365.555731290864、tau_fast 119792.05323087271、C3_survives/C4_survives true；判据是"coverage > 0.05"（**该判据不能失败**） | 无 | `runs/m1_growth.json`（118,600 B，最大的 JSON） | Finding 062 的第一次测量；判词被 step87/88 取代 |
| `step87_m1_trend.py` | 用**指数**而不是阈值：n=3…12，1000 样本/规模；modal 1.0→0.0（n≥4 恒为 0）、slow 0.5→0.637、fast 0.5→0.027；alpha modal −12.286614343781055、slow **+0.1448002737230628**（se 0.011398652426744113）、fast **−2.1326541948067796**（se 0.009108933396537249）；tau_slow 6409.459472300427、tau_fast 120340.54460497841 | 无 | `runs/m1_trend.json`（976 B） | Finding 062；STATE §3.4 |
| `step88_m1_verdict.py` | 只读 m1_trend，给每个指数解释与 M1 判决：modal `g_unbounded: false`，slow/fast `true` | `runs/m1_trend.json` | `runs/m1_verdict.json`（672 B） | Finding 062；STATE §4 M1 SATISFIED |

---

## 2. 失效、被取代与一次性脚本

### 2.1 明确失效（判词被后续脚本用同一份数据推翻）

| 脚本 | 判定 | 理由（可核查） |
|---|---|---|
| `step15_l1_threshold.py` | **结论失效** | 它给出 L1±10% 阈值 239.7216796875 Hz；step56 用 2^d 角点重算得 **258.7646484375 Hz**（`runs/robust_corners.json` 的 `thresholds` 三个值并列），Finding 028 明写"修正后的阈值是 258.76 Hz；任何后来引用 239.72 Hz 的结论都受影响"。`runs/l1_threshold.json` 本身没有任何文档按名引用 |
| `step16_false_positive_zone.py` | **区间失效** | 假阳性区右端 239.72 → **258.76**（`runs/l1_labels_corrected.json` 的 `zone: [172.34, 258.76]`，`inside: [180, 210, 240]`） |
| `step28_waterbed.py` | **数值路线失效** | 用 Vandermonde 拟合取前两个系数，n 增大时舍入被无界放大；其 `max_abs_numeric_W 0.012110969814513808` 是计算错误。step32 换成直接在 w 上积分 + 解析尾部（`sdof 1.6591171486662228e-12`）。产物 `runs/waterbed.json` 无文档引用 |
| `step29_waterbed_residual.py` | **判词失效** | 它打印"残差是求积误差、加密会缩小"，而**它自己的表**显示 W 在 100× 加密下稳定到 1e-12；step30 的 docstring 明写"判词写在读数字之前"。Finding 016 记录在案 |
| `step33_rhp_zeros.py` | **产物缺失** | 声明写 `runs/rhp_zeros.json`，磁盘上**不存在**该文件（73 个顶层 JSON 中唯一缺失的一项） |
| `step34/35` | **失效** | 度 8/12 通过，更高阶差 17–33 倍；`|P(z)|/max|coef| = 2.1e+93` 说明 numpy 伴随矩阵求根不适用于这种系数跨度（step35 的自述） |
| `step36_waterbed_formula_final.py` | **被 step38 覆盖** | 与 step38 写**同一个路径** `runs/waterbed_formula_final.json`；文件的现有内容是 step38 的（字段 `max_root_residual 1.5903358327047895e+114`、`verified 88`、`median_rel_diff 4.172831635448838e-07`）。step38 自述列出 step36 的三处"让检验无法失败"的错误 |
| `step37_diagnose_degree.py` | **死胡同** | 它是"numpy 系数降序 vs mpmath 升序"这条错误链上的诊断：step35/36/37 都把系数按升序传给 mpmath，于是求根器解的是反转多项式，而"验证"又拿同一个反转多项式在自己的根上求值——自洽且无意义（step38 自述）。无产物 |
| `step83_m4_free_response.py` | **判词失效（数据保留）** | 其 `worst_rel` 最大 0.9614006260899509 来自"把每个 L0 模态找最近的峰、取最坏"，**未被激励的模态被记成巨大失配**（step84 自述"这个指标是反的"）。它保存的 `peak_freqs` 仍是 step84/85 的输入，所以是"数据在用、判词废弃" |
| `step84_m4_free_fixed.py` | **被 step85 取代** | 它的 L0 交叉校验用**传递率的幅值峰**当固有频率，而基座激励的传递函数有零点、反共振会吃掉极点（step85 自述"那是无效的"）；它打印的"agree to within 8.21e-01"里 **8.21e-01 就是分歧本身**（STATE §5.2 第 8 条）。产物 `runs/m4_free_response_fixed.json` 无文档引用 |
| `step86_m1_growth.py` | **判词被取代（数据在用）** | 判据是"每个 n 的 coverage > 0.05"：C4 的覆盖 0.50→0.0875 明明在衰减却通过了（STATE §5.2 第 9 条；step87 自述"instance nine"）。`runs/m1_growth.json` 仍被 Finding 062 引用 |
| `step17_l1_ablation.py` | **无下游** | 产物 `runs/l1_ablation.json` 只被 `docs/CONSENSUS.md` §3.4 引用；**不存在 findings/009 的对应文档**（CONSENSUS §2.1 明写"仓库中不存在 findings/009"，L1 消融跑完但没有形成结论文档） |
| `step67_heat_min_units.py` | **结论被撤回** | STATE §5.3：Finding 037 被 055 撤回——它把"matches"与经典 N−1 中的 N（含公用工程、含公用工程换热器）当成同一个量。其 `sound: false`（N=5、min_units_attaining 2）不成立：step79 用 N=6 枚举 219 个设计得到最少 5 units = N−1 |
| `step70_network_model_validated.py` | **计数解释被撤回** | 同上：Finding 044 的 `fewest_units_attaining: 3` 与 `sound` 类结论被 055 撤回；但它的**模型修正**（`counterexample_Q_H 150.0 = agent_floor 150.0`、all-matches 三例全等）仍然成立并被 step71/78/79 依赖 |

### 2.2 结论被同线后续修正（非正式撤回）

| 脚本 | 修正者 | 说明 |
|---|---|---|
| `step23_composition.py` | `step24_calibration.py` | `runs/composition.json` 的 `any_frac = 1`（全部失败）是退化校准；step24 在非退化窗口重测得 independence_ratio 0.4373 |
| `step25_structural_features.py` | `step26_asymptote_rate.py` | step25 只在 `asym > 0`（有 payload 接地）的结构上测渐近线，等于把最可能反例排除掉；step26 去掉守卫后得到 `omega*T → g0/m0` |
| `step27_independence.py`（Finding 015 的处方） | `step40/41/42/43`（Finding 019/020） | "独立性来自结构特征"被推翻：`g0/m0` 与 `W` 都是结构量，比值 0.6066；step42 的受控重叠实验显示 disjoint 0.976 vs shared 1.0，即**拓扑/取值的标签本身不解释什么** |
| `step44_capability_dimension.py` | —— | **未被撤回**。它正是修正 Finding 020 悲观读法的证据（participation_ratio 4.62、leading_share 0.361）；任务描述里把它列为"被 finding 撤回"与事实不符 |
| `step36…step39` 整条水床闭式线 | `step38`+`step39` | step39 用比值分布给出诚实边界：compared 24、within_1e-3 只有 11；n=7 的中位相对误差 86.15、n=8 为 54.63 —— 高阶多项式求根仍不可靠，闭式只在低阶被验证 |

### 2.3 一次性但有效（无下游依赖，结论一次性写进 finding）

| 脚本 | 产物 | 为什么算"一次性" |
|---|---|---|
| `step1_certificate.py` | 无 | 只有 Finding 001 引用；验证对象是 `ecdr/l0` 的闭式证书 |
| `step2_escape_ladder.py`、`step3_m2_analysis.py` | 无 | Finding 001–003 的 M2 段；Finding 009 已把其中的 Λ₂ 论证降级 |
| `step5/6/7/8` | `step6_waterbed_budget.json`、`step8_waterbed_exact.json` | 验证 Finding 004 引用的 `ecdr/l0/invariants.py`、`ecdr/l0/peaks.py`；两个 JSON 没有任何文档按名引用 |
| `step11_baseline_smoke.py` | 无 | 基线冒烟，被 step12 的正式消融取代 |
| `step13_asymptote_check.py` | 无 | **有价的否定**：渐近线是上界不是下界 ⇒ 该证明路线关闭 |
| `step18_l1_sign_check.py`、`step21_network_verify.py`、`step26_asymptote_rate.py`、`step29_waterbed_residual.py`、`step69_pool_heat_check.py` | 无 | 每个都是"某条结论能不能成立"的单次判定，结论进入 finding 后没有下游脚本依赖 |
| `step12b_analyse.py` | 无 | 消融的分析器；主指标（逃生率）被 Finding 007 自证混淆 |
| `diag_m2_waterbed.py`、`diag_peak_m2.py`、`diag_asym.py` | 无 | 临时探针，mtime 分别 2026-10-12T15:18 / 15:32（夹在 step4/step5/step6 之间） |
| `julia_setup.py`、`_bootstrap.py` | 无 | 环境/路径准备，被所有脚本 import |
| `step72_units_bound.py` | `runs/units_bound.json` | **产物孤儿**：全库 docs 无一处按名引用 `units_bound.json`；它只作为 orchestrator `--unitsbound` 的输入（`unitsbound.ts:28`），而 Findings 054 的产物是 `runs/unitsbound_reasoning.txt` |

### 2.4 产物存在但没有任何文档按名引用（25 个）

按名在 docs/ 里搜不到的 JSON：`task_family.json`、`census_gN.json`、`library.json`、`coverage_ensemble.json`、`composition.json`、`calibration.json`、`structural_features.json`、`independence.json`、`crossing_measured.json`、`llm_scenarios.json`、`witness_truth.json`、`units_bound.json`、`modelica_smoke.json`、`waterbed.json`、`waterbed_stable.json`、`waterbed_disagreement.json`、`waterbed_quadcheck.json`、`waterbed_formula.json`、`waterbed_formula_hp.json`、`waterbed_formula_final.json`、`step4_m2_refine.json`、`step6_waterbed_budget.json`、`step8_waterbed_exact.json`、`l1_threshold.json`、`m4_free_response_fixed.json`。

其中三类要分开看，不能一律当垃圾：

1. **内容在用、只是没写文件名**：`census_gN.json`（Finding 010 的 N 表）、`library.json`（Finding 011 的 35.9 张证书）、`crossing_measured.json`（Finding 049 §7.4 逐字引用 9.164e-04 / 3.975e-08 / 1.000e-06 / 1.135e-03）、`task_family.json`（step12 的输入）、`llm_scenarios.json` 与 `units_bound.json`（orchestrator 的输入）、`witness_truth.json`（Finding 045 的真值表）、`modelica_smoke.json`（Finding 030 的 8.31e-6）。
2. **真·中间产物**：`waterbed*.json`（7 个）里只有 `waterbed_ratio.json` 被 Finding 018 引用。
3. **失效链条的遗留**：`step4_m2_refine.json`、`step6/step8_*.json`、`l1_threshold.json`、`m4_free_response_fixed.json`。

---

## 3. runs/ 里论文会引用的关键数据（数字抄自文件）

| JSON | 生成脚本 | 里面最关键的数字 | 引用它的 finding |
|---|---|---|---|
| `crossing_measured.json` | `step73_crossing_measured.py` | `c_s 9.164e-04`（min 8.912e-4 / max 1.0219e-3）、`c_v 3.97515e-08`（batch 200,000）、`c_p 1.00000761e-06`、`threshold (c_p+c_v)/c_s = 1.1346127481892362e-03`、`first_crossing_n 1`；g(N) 十行：1 / 4 / 32 / 602 / 23,170 / 1,705,522 / 238,720,034 / 64,383,610,994 / 33,941,788,348,786 / 35,323,849,620,845,554 | Finding 049 §7.4（按数字引用，未写文件名） |
| `two_routes.json` | `step74_two_routes.py` | route B 成本恒定 `9.94938980002189e-07 s`；route C `4.179463000036776e-03 s`（g=4 恒定）；route A `0.10448657500091939 s`（M=100，δ=0.01）；C1 的 fraction 从 `0.125` 掉到 `1.132379410210005e-16` | Finding 050 |
| `library_cost.json` | `step75_library_cost.py` | `c_v`：modal 4.575e-08、statics 8.0392e-06、slow 4.5375e-07、fast 9.581e-06（相差 **209 倍**）；顺序施加 400→201→86→18；`library_total 0.0024131000391207635` vs `enumeration_total 0.8693939600023441`（360 倍）；survivors 6 / n 400 | Finding 051（下一轮被部分撤回） |
| `three_procedures.json` | `step76_three_procedures.py` | `cert_over_heur 8.309670243145872e-05`、`cert_over_enum 3.999530758610542`（g=4 时在 n=3…10 全部恒定）；scaling 段 sep 3.9995 → `3.3937806625804633e13`（n=10，g 33,941,788,348,786） | Finding 052 |
| `proposition4.json` | `step77_proposition4.py` | `pruning_identical: true`；`c_s 0.0021525536499975716`、`c_v_apply 4.8749992856755854e-08`、`c_p 2e-07`、`constant_cs_over_cvapply 44154.95313655758`；`formula_holds: true`；n=10 行：g 33,941,788,348,786、cert 0.0021527536499975717 s、heur 1,654,661.9395488366 s、enum 73,061,520,397.62436 s、`sep_enum 3.393863501181697e13 = predicted_sep_enum` | Finding 053；STATE §2 Prop 4 |
| `curve_b.json` | `step80_curve_b.py` | `exponent_a 1.0`、`exponent_b 0.05507407923312987`、`exponent_c 0.05965716302820119`；f=0.65，k = 4/7/10/14/19/24/30/37；a(n=10) `76045183463756.3 s`、b(n=10) `0.08180639999999999 s`、c(n=10) `0.07965359999999999 s`；`ratio_ab` 6.4 → `9.295749900222514e14` | Finding 058；STATE §3.1 |
| `m4_ladder.json` | `step82_m4_ladder.py` | `c_s_L0 1.5090069998404943e-03`、`c_s_L1 6.036027999361977e-03`、`c_s_L2 1.8815941749853664`（L2 是 L0 的 **1247 倍**）；n=10 `sep_L0 9.295749900222514e14`、`sep_L1 3.4462292313020055e15`、`sep_L2 3.430587825843005e16`；8 行 L2 对照 L0 最坏 `4.6183658014454945e-07`；`agreement [0, 8]` | Finding 060；STATE §3.2 |
| `m1_trend.json` | `step87_m1_trend.py` | n=3…12：modal 1.0→0.0（n≥4 恒 0）、slow 0.5→**0.637**、fast 0.5→**0.027**；`tau_slow 6409.459472300427`、`tau_fast 120340.54460497841`；`alpha` modal −12.286614343781055 / slow **+0.1448002737230628**（se 0.0114）/ fast **−2.1326541948067796**（se 0.00911） | Finding 062；STATE §3.4 |
| `m1_verdict.json` | `step88_m1_verdict.py` | `modal: g_unbounded false`（coverage 1.0→0.0）；`slow/fast: true`；`unbounded: ["slow","fast"]` | Finding 062；STATE §4（M1 SATISFIED） |
| `m1_growth.json` | `step86_m1_growth.py` | n=3…8 的原始抽样（**每规模 400 个** slow_vals/fast_vals，实测长度 400）；`tau_slow 6365.555731290864`、`tau_fast 119792.05323087271`；`C3_survives/C4_survives true`（**用的是 0.05 阈值判据**） | Finding 062 |
| `network_model_validated.json` | `step70_network_model_validated.py` | all-matches 三例 `142.5/142.5`、`60.0/60.0`、`0.0/0.0`；`counterexample_Q_H 150.0`、`agent_floor 150.0`（**两者相等 = 模型的反驳成立**）；`best_by_units {1: 232.5, 2: 150.0, 3: 142.5, 4: 142.5}`；`fewest_units_attaining 3`（该计数解释被 055 撤回） | Finding 044（已被 055 部分撤回） |
| `design_units.json` | `step79_design_units.py` | `Q_H_min 142.5`、`N 6`、`designs 219`、`by_units {4: 150.0, 5: 142.5, 6: 142.5, 7: 142.5, 8: 142.5}`、`fewest_attaining {units: 5, process: [[0,2],[0,3],[1,2]], heaters: [3], coolers: [1], Q_H: 142.5}` | Finding 056（**经典 U_min = N−1 = 5 成立**） |
| `utility_units.json` | `step78_utility_units.py` | `N 6`、`N_minus_1 5`、`Q_C_min 150.0`；3 match + 2 公用工程换热器 = `total_units 7`；4 match + 2 = `8` | Finding 055 |
| `m5_named_remedy.json` | `step81_m5_named_remedy.py` | `pinch_shifted 105.0`、`Q_H_min 142.5`、`four_unit_designs_attaining 0`、`named "a cross-pinch exchanger"`、`spanning_matches ["H1-C1"]`、`M5_holds true` | Finding 059；STATE §3.6 |
| `census_gN.json` | `step19_gN_census.py` | `g_I1 = 32` 在 n_max=3…8 **恒定**（占比 1.0 → `4.970208956279592e-10`，speedup → 1.0000000005）；I3 占比稳定在 0.44–0.65 | Finding 010 |
| `library.json` | `step20_library.py` | N=64,383,610,994、f=0.5 时 `certificates_needed 35.90597444238762`、`separation 1793116939.2800004`；f=0.001 时 24,875.68 张、separation 2.588e6；树空间占比 0.44–0.645 | Finding 011 |
| `calibration_sweep.json` | `step51_calibration_sweep.py` | 原始族：f=0.5 → `survival 0.03125`（rounds_1e10 6.64）、f=0.6 → 0.005、f=0.7 → 0；新族 f=0.5 → 0.03375 / 6.79。**step80 的 f=0.65 就取自这条线**；文件含 `Infinity` 字面量，`json.load` 之外的工具解析会失败 | Finding 025、058 |
| `three_certificate.json` / `conditionals.json` / `fourth_certificate.json` / `rayleigh_bound.json` | `step48 / step49 / step50 / step47` | 三证书 `mean_ratio 0.391424564428569`，外推修正 3→0.1532、5→0.02347、10→2.157e-4、20→1.821e-8；条件概率 `f2_given_1` 0.5354–0.5504、`f3_given_12` 0.7596–0.8061；C4 `fast_bound_violations 0`、max_ratio 0.9978306963226589；C3 `violations 0`、median_tightness 2.729528960711694、rho_bound_vs_n −0.00638 | Finding 023/024 |
| `thresholds.json` | `step10_thresholds.py` | `M1_threshold_hz 172.23706272343517`、`M2_threshold_hz 132.42530648581`、`n_examined 44688`、`n_peak_feasible 12182`、`T_iso 0.1`、`m2_threshold_curve` 400 点 | Finding 006 |
| `robust_corners.json` / `l1_labels_corrected.json` | `step56` / `step57` | 三阈值并列 `172.3388671875 / 258.7646484375 / 239.72`；最坏点 = nominal(110.51010008194646, 0.595505617977528) × 1.1 = (121.56111009014111, 0.6550561797752809)；`total_false_robust 33`、zone [172.34, 258.76] | Finding 028/029 |
| `l1_crossvalidation.json` / `modelica_l1_full.json` / `modelica_tmd.json` | `step54` / `step63` / `step64` | L1 闭式 vs 同方程积分：T_max_rel 9.2207e-7、F_max_rel 1.2362e-6；MSL 组件路线 12 项 + 8 网络；TMD 16 行最坏 rel 7.6366e-7 | Finding 027/033/034 |
| `m4_free_response.json` / `m4_l0_free.json` | `step83` / `step85` | 8 个结构的 L2 峰数 ≤ n；step85 的**有效**结论：`n_violated 0`、`worst_l2_to_l0 9.499950000198741e-05`、`l0_ok true` | Finding 061；STATE §3.5 |
| `heat_min_utility.json` / `heat_ecdr_question.json` | `step65` / `step66` | 12 行 `Q_H_table == Q_H_lp`（diff 全 0）；教科书 4 流 dt_min=10：Q_H 142.5、Q_C 150.0、pinch 105.0；ECDR 形状：4-stream 证书 142.5 / 15 个网络 / Q* 128.25 / `certificate_rules_out true`，3x2 证书 0.0 / 63 个网络 / Q* 0.0 | Finding 035/036 |
| `heat_min_units.json` | `step67_heat_min_units.py` | N=5、`min_units_attaining 2`、`sound false`（三例）——**这是被撤回的结论**，保留它是为了记录撤回 | Finding 037（被 055 撤回） |
| `witness_truth.json` | `step71_witness_truth.py` | W1 `true_Q_H 150.0`（q* 142.5，不合格，untouched ["C2"]，duty_floor 150.0）；W2 142.5 合格；W3 `332.5` 不合格（duty_floor 262.5）；W4 142.5 合格 | Finding 045 的真值；agent 侧是 `witness_audit.json` |

**一个必须写进论文脚注的观察**：同一个 `c_s`（一次结构评估的秒数）在五个产物里是**五个不同的数**——`crossing_measured 9.164e-04`、`two_routes 1.044865750009194e-03`、`m4_ladder c_s_L0 1.5090069998404943e-03`、`proposition4/three_procedures 2.1525536499975716e-03 / 2.2356870500079822e-03`、`library_cost 2.1734849000058605e-03`（跨度 2.4 倍）。它们是在不同网格/不同批次上现测的墙钟时间。**指数（1.0000 / 0.0551 / 0.0597）与分离度对这一点不敏感，绝对秒数敏感**——引用绝对成本时必须写明是哪一次运行。

---

## 4. runs/ 里的中间产物与垃圾（体积实测）

| 路径 | 文件数 | 体积 | 是什么 | 处置建议 |
|---|---|---|---|---|
| `runs/modelica_work/` | 125 | 697,900 B = **0.67 MiB** | step61 的工作目录：`Lin1*`、`Lin2*` 两套 OpenModelica 线性化编译产物（`.c`/`.o`/`.h`/`.makefile`/`.mat`/`.bin`/`_init.xml`/`_info.json`）、`iface.mos`/`lin.mos`/`lin2.mos`、`linearized_model.mo`、`linearized_model_exact.mo` | 可删可重建；`linearized_model*.mo` 是 step61 的输入，删了要重跑 step61 |
| `ecdr/runs/modelica_work/` | **2,522** | 731,607,040 B ≈ **697.64 MiB** | 真正的体积大头，**不在 runs/ 下**：`Free0…` 等 21 个子目录，是 step82/83/85 的 L2 路径（emit + `omc` 线性化 + 编译）留下的编译中间件 | 这是仓库里最大的可再生垃圾（占 `ecdr/` 的 737.46 MB 中的 99.2%）；一次 L2 重建即可全部重生成 |
| `ecdr/l2/modelica/` | 70 | 5.32 MiB | emitter/linearize/run 三个模块 + `smoke/`（step58 读的 `SdofIso_res.csv` 在这里） | `smoke/` 是 step58 的输入，必须保留 |
| `runs/unitsbound_reasoning.txt` | 1 | 571,591 B | orchestrator `--unitsbound` 的原始推理（`unitsbound.ts:117`） | Finding 054 的唯一证据，**不要删** |
| `runs/selfaudit_reasoning.txt` | 1 | 83,407 B | orchestrator `--selfaudit` 的原始推理（`selfaudit.ts:146`） | Finding 046/047 的证据 |
| `runs/witness_audit.json` | 1 | 77,418 B | orchestrator `--audit`（`audit.ts:83`）；Finding 045 自述"gitignored" | Finding 045 的证据 |
| `runs/argue_log.txt/2/3/4.txt` | 4 | 767 / 1,015 / 1,036 / **3,502** B | `--argue` 的运行日志（外部重定向捕获）；`argue_log4.txt` 被 Finding 063 按名引用 | 只 `argue_log4.txt` 有引用，前三个是过程性 |
| 大 JSON | 4 | `m1_growth.json` 118,600 B、`ablation.json` 82,160 B、`thresholds.json` 50,184 B、`l1_ablation.json` 40,068 B | 逐样本/逐曲线原始数据 | `m1_growth.json` 与 `thresholds.json` 被 finding 引用；`ablation.json`/`l1_ablation.json` 只被 CONSENSUS 引用 |
| `runs/` 顶层其余 JSON | 73 个合计约 1.05 MiB | — | 见 §3 | — |

**一句话**：`runs/` 本身只有 1.77 MiB，真正的垃圾在 `ecdr/runs/modelica_work/`（697.64 MiB，2,522 个文件，可再生）。

---

## 5. "跑一遍就能重建全部结论"的最短脚本序列

以下按依赖顺序排列。**每一步只列必须的**；括号里写它为什么必须在前面。全部命令按仓库现有写法用 `.venv\Scripts\python.exe`（findings 里的写法）。

### 阶段 0：L0 证书与判定例程（约 1 分钟，无产物）

    .venv\Scripts\python.exe scripts\step1_certificate.py     # M1 闭式证书三项检查
    .venv\Scripts\python.exe scripts\step7_exact_peak.py      # 精确峰值例程（后面所有"精确判定"都靠它）
    .venv\Scripts\python.exe scripts\step14_l1.py             # L1 复现 L0 + 证书上移
    .venv\Scripts\python.exe scripts\step21_network_verify.py # 通用网络求值器 == 手写 L0 机制

### 阶段 1：结构空间与 g(N)（证书库的规模依据）

    .venv\Scripts\python.exe scripts\step19_gN_census.py      -> runs/census_gN.json
    .venv\Scripts\python.exe scripts\step20_library.py        -> runs/library.json
    .venv\Scripts\python.exe scripts\step22_coverage_ensemble.py  -> runs/coverage_ensemble.json
    .venv\Scripts\python.exe scripts\step23_composition.py    -> runs/composition.json
    .venv\Scripts\python.exe scripts\step24_calibration.py    -> runs/calibration.json
    .venv\Scripts\python.exe scripts\step25_structural_features.py -> runs/structural_features.json
    .venv\Scripts\python.exe scripts\step26_asymptote_rate.py # 修正 step25 的守卫

### 阶段 2：四张证书与库的组合（step80 的 f=0.65 出处）

    .venv\Scripts\python.exe scripts\step47_rayleigh_bound.py -> runs/rayleigh_bound.json   # C3
    .venv\Scripts\python.exe scripts\step50_fourth_certificate.py -> runs/fourth_certificate.json # C4
    .venv\Scripts\python.exe scripts\step48_three_certificate.py -> runs/three_certificate.json
    .venv\Scripts\python.exe scripts\step49_conditionals.py   -> runs/conditionals.json
    .venv\Scripts\python.exe scripts\step46_library_composition.py -> runs/library_composition.json
    .venv\Scripts\python.exe scripts\step51_calibration_sweep.py -> runs/calibration_sweep.json

（`step40/41/42/43/44/45` 与 `step27` 只在论文要写"证书为什么必须沿不同轴"时才需要；它们记录的是失败与修正，不进入最终数字。）

### 阶段 3：成本轴与命题 4（STATE §2 Prop 2/4、§3.1）

    .venv\Scripts\python.exe scripts\step73_crossing_measured.py -> runs/crossing_measured.json  # c_s/c_v/c_p + 阈值
    .venv\Scripts\python.exe scripts\step74_two_routes.py        -> runs/two_routes.json          # 三路线同轴
    .venv\Scripts\python.exe scripts\step75_library_cost.py      -> runs/library_cost.json        # c_v 不是一个数
    .venv\Scripts\python.exe scripts\step76_three_procedures.py  -> runs/three_procedures.json    # 三种程序
    .venv\Scripts\python.exe scripts\step77_proposition4.py      -> runs/proposition4.json        # Prop 4 八规模
    .venv\Scripts\python.exe scripts\step80_curve_b.py           -> runs/curve_b.json             # 三臂指数 + 交叉点

（`step80` 只依赖 `library` 线的常数 f=0.65 与 c_s/c_p/c_v，**不读**前面任何 JSON —— 所以它是重建链条里最便宜的一环，也是 STATE §3.1 的全部证据。）

### 阶段 4：保真度阶梯 M4（STATE §3.2、§3.5）

    .venv\Scripts\python.exe scripts\step54_l1_crossvalidation.py  -> runs/l1_crossvalidation.json  # L1 闭式确认
    .venv\Scripts\python.exe scripts\step58_modelica_smoke.py      -> runs/modelica_smoke.json      # 需要 ecdr/l2/modelica/smoke/SdofIso_res.csv
    .venv\Scripts\python.exe scripts\step63_modelica_l1_full.py    -> runs/modelica_l1_full.json
    .venv\Scripts\python.exe scripts\step64_modelica_tmd.py        -> runs/modelica_tmd.json
    .venv\Scripts\python.exe scripts\step82_m4_ladder.py           -> runs/m4_ladder.json           # c_s(L0/L1/L2) + 三档分离度
    .venv\Scripts\python.exe scripts\step83_m4_free_response.py    -> runs/m4_free_response.json    # 自由响应（峰数据）
    .venv\Scripts\python.exe scripts\step85_m4_l0_free.py          -> runs/m4_l0_free.json          # 同一程序在 L0 上复测（读 step83 的输出）

（`step82` 会调用 `omc` 并在 `ecdr/runs/modelica_work/` 下重建那 697 MiB；这是整条链最慢、最占空间的一步。`step55/56/57` 只在要复现 Finding 028/029 的阈值修正时跑；`step84` 已被 step85 取代，不必跑。）

### 阶段 5：M1 收口（STATE §3.4、§4 M1）

    .venv\Scripts\python.exe scripts\step86_m1_growth.py  -> runs/m1_growth.json   # PER_N=400，n=3..8（旧判据，保留作对照）
    .venv\Scripts\python.exe scripts\step87_m1_trend.py   -> runs/m1_trend.json    # n=3..12，指数
    .venv\Scripts\python.exe scripts\step88_m1_verdict.py -> runs/m1_verdict.json  # 读 m1_trend，出判决

### 阶段 6：热域与 M5（STATE §3.6、§7）

    .venv\Scripts\python.exe scripts\step65_heat_min_utility.py  -> runs/heat_min_utility.json
    .venv\Scripts\python.exe scripts\step66_heat_ecdr_question.py -> runs/heat_ecdr_question.json
    .venv\Scripts\python.exe scripts\step69_pool_heat_check.py   # 模型的反驳成立（无产物）
    .venv\Scripts\python.exe scripts\step70_network_model_validated.py -> runs/network_model_validated.json
    .venv\Scripts\python.exe scripts\step78_utility_units.py     -> runs/utility_units.json
    .venv\Scripts\python.exe scripts\step79_design_units.py      -> runs/design_units.json       # 最少 5 units（step81 的前提）
    .venv\Scripts\python.exe scripts\step81_m5_named_remedy.py   -> runs/m5_named_remedy.json

    # 可选，M6 的 agent 侧（需要 LLM key，见 orchestrator/src/llm.ts:81）
    .venv\Scripts\python.exe scripts\step68_llm_scenarios.py  -> runs/llm_scenarios.json
    cd orchestrator && node node_modules/cordis/bin.js --random
    cd orchestrator && node node_modules/cordis/bin.js --audit
    cd orchestrator && node node_modules/cordis/bin.js --argue

### 5.1 如果只要 STATE 六条"可宣称"主张

最小集合是 **20 个脚本**：

    step1, step7, step47, step48, step49, step50, step51,      # 证书库与 f
    step19, step20,                                            # g(N) 与库规模
    step73, step74, step76, step77, step80,                    # 成本轴、三种程序、Prop 4、三臂
    step54, step63, step82, step83, step85,                    # 保真度阶梯 + 自由响应
    step87, step88                                             # M1 的 g(N) -> infinity

（共 20 个；`step86` 只在要展示"旧判据为什么不能失败"时才加。）

---

## 6. 这份索引自身的边界

1. **没有执行任何脚本**。"在用/失效"是**引用关系 + 源码自述**的判定，不是实测；每一步的实际耗时未测。
2. **墙钟数字不可跨运行比较**：§3 末尾的 `c_s` 五值差异就是证据。重建后指数应重现，绝对秒数不会。
3. **时间戳来自文件 mtime**，不是 git 提交时间；`.git` 里有 281 个对象但没有逐脚本的提交时间对照表。
4. **`runs/calibration_sweep.json` 含 `Infinity` 字面量**（Python `json.dumps` 允许），标准 JSON 解析器会失败——用 Python 的 `json.load` 读，不要用别的语言直接 parse。
5. **产物按名引用 ≠ 内容被引用**：§2.4 已把两者分开列；写论文时如果引用 `crossing_measured.json` 或 `census_gN.json` 的数字，引用源应是 Finding 049 / 010，而不是"某脚本的输出文件"。
