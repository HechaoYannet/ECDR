# reference/ 外部材料索引

清点对象：`D:\\otherProject\\ECDR\\reference\\`（被 `.gitignore:7` 整体忽略）。
清点方式：只读遍历 + `read`/`grep`/`glob`，未修改 `reference/` 内任何字节。
本文只写三件事：**里面是什么**、**本项目实际引用了什么**、**什么与本研究无关**。

---

## 0. 口径对账（先解决数字）

简报给的是"15129 个文件、121MB"。实测复现了这个数字，条件是**排除三个 `.git` 目录**：

| 口径 | 文件数 | 字节 | MiB |
|---|---|---|---|
| `reference/` 含 `.git` | **15217** | 167,185,701 | 159.44 |
| `reference/` 不含 `.git` | **15129** | 127,001,354 | **121.12** |
| 差值（即三个 `.git`） | 88 | 40,184,347 | 38.32 |

所以简报的 15129 / 121MB 是**工作树口径**，本文所有"文件数/体积"若未特别标注均用此口径；讨论 git 溯源时另注明含 `.git` 的数字。

三条关于"里面有什么"的否定性事实，同样重要：

* `reference/` 内 **0 个 `.pdf`、0 个 `.tex`、0 个 `.bib`**（全目录递归统计）。
* `reference/` 内 **0 个 `node_modules`、0 个 `.venv`**。整个目录只有两类内容：三个 git 浅克隆的工作树，加三个 `.git`。
* 因此 `reference/` **不持有任何论文原文**。"某篇论文"在本仓库里只有 README 指针，见 §2.2。

---

## 1. 顶层结构

| 条目 | 类型 | 文件数 | 字节 | MiB | 占 `reference/` |
|---|---|---|---|---|---|
| `reference/cordis/` | git 浅克隆工作树 | 139（不含 `.git`）/ 168（含） | 399,650 / 565,100 | 0.38 / 0.54 | 0.31% |
| `reference/paper/` | git 浅克隆工作树 | **2**（不含 `.git`）/ 31（含） | 2,758 / 34,039 | 0.00 / 0.03 | 0.00% |
| `reference/deepseek-harness/` | git 浅克隆工作树 | 14988（不含 `.git`）/ 15018（含） | 126,598,946 / 166,586,562 | 120.73 / 158.87 | **99.68%** |

三者的克隆时间戳（`git log` 的 committer 时间，+0800）：

| 目录 | remote | 提交 | 克隆时刻 |
|---|---|---|---|
| `cordis/` | `https://github.com/cordiverse/cordis.git` | `c261dd2c13d65b1994adb1cdc10d7dba61542523` | 1791848494 → 2026-10-13 07:41:34 |
| `paper/` | `https://github.com/cordiverse/paper.git` | `0d43a6f18004a7b5bf9662c31aa08c3712d232ec` | 1791848495 → 2026-10-13 07:41:35 |
| `deepseek-harness/` | `https://github.com/deepseek-ai/deepseek-harness.git` | `d743267388641bc76f17c45ce8b4c231aed1d32c` | 1791848501 → 2026-10-13 07:41:41 |

三者都是 **shallow clone depth=1**（各自有 `.git/shallow` 文件，`.git/logs/HEAD` 各只有 1 行、内容为 `clone: from ...`，说明**从未 fetch/pull 过**，工作树 = 该提交的树，未被本地改动）。这对复现很关键：`reference/` 是不可再生的历史快照，删了就没了网络来源以外的凭据。

---

## 2. 逐项识别

### 2.1 `reference/cordis/` — Cordis 元框架源码

**是什么**：npm 包 `cordis` 的上游 monorepo 检出，yarn workspaces，`packageManager: yarn@4.14.1`，MIT。

顶层 `reference/cordis/package.json` 的 `version` 是占位的 `0.0.0`（私有根包 `@root/cordis`）；**真版本在子包里**：

| 路径 | 包名 | 版本 |
|---|---|---|
| `reference/cordis/packages/core/package.json` | `cordis` | **4.0.0-rc.10** |
| `reference/cordis/packages/loader/package.json` | `@cordisjs/plugin-loader` | **1.0.0-rc.7** |
| `reference/cordis/packages/include/package.json` | `@cordisjs/plugin-include` | **1.1.0** |
| `reference/cordis/packages/hmr/package.json` | `@cordisjs/plugin-hmr` | 1.1.0 |
| `reference/cordis/packages/group/package.json` | `@cordisjs/plugin-group` | 1.0.0 |
| `reference/cordis/packages/timer/package.json` | `@cordisjs/plugin-timer` | 1.1.3 |
| `reference/cordis/packages/logger-console/package.json` | `@cordisjs/plugin-logger-console` | 1.0.0 |
| `reference/cordis/packages/utils/package.json` | `@cordisjs/utils` | 1.0.0 |
| `reference/cordis/packages/create/package.json` | `create-cordis` | 0.3.0 |

三个版本号 `4.0.0-rc.10` / `1.0.0-rc.7` / `1.1.0` **与 `orchestrator/package.json` 的锁定值逐字相同**，这是 `reference/cordis` 与本项目唯一有实质关系的版本事实。

核心包 `reference/cordis/packages/core/src/` 共 9 个文件、1891 行（其中非空行 1669 行）。`reference/cordis/.git/index` 记录 **139** 个受跟踪条目（index 头 12 字节为 `DIRC`、version 2、entries 139）。
README 是一个 25 字节的重定向：`reference/cordis/README.md` 内容即 `./packages/core/README.md`。

### 2.2 `reference/paper/` — 论文仓库的检出，**里面没有论文**

**是什么**：`https://github.com/cordiverse/paper` 的浅克隆。工作树**只有 2 个文件**：

| 文件 | 字节 | 内容 |
|---|---|---|
| `reference/paper/README.md` | 2725 | 论文摘要页 + BibTeX |
| `reference/paper/.gitattributes` | 33 | `* text=auto eol=lf` / `*.pdf binary` |

`reference/paper/.git/index` 的条目数是 **2**（`README.md`、`.gitattributes`）——即该提交下就没有 PDF/tex，不是浅克隆漏拉。`.gitattributes` 里的 `*.pdf binary` 只是仓库策略，`reference/` 内 PDF 数为 0（§0）。

可识别的论文标识（全部来自 `reference/paper/README.md`）：

* 标题：**A Programming Paradigm for Spatiotemporal Composability**
* arXiv：**2608.25512**，primaryClass **cs.PL**
* 作者：**Shi, Yifan; Zhang, Wei; Cui, Tianyi**，年份 **2026**
* BibTeX key：`shi2026cordis`（README 内现成，可直接进参考文献）
* 摘要关键词：revertible effects（时间可组合性）、reactive coeffects（空间可组合性）、context paradigm、declarative component loader with configuration reconciliation and HMR、参考实现 Cordis

**结论**：`reference/paper` 是**元数据**，不是全文。任何"论文说……"的表述在本仓库里都只能追溯到这 2725 字节的摘要，追溯不到正文。

### 2.3 `reference/deepseek-harness/` — DeepSeek Harness 完整检出

**是什么**：`https://github.com/deepseek-ai/deepseek-harness` 的浅克隆。根包 `reference/deepseek-harness/package.json`：

```json
{ "name": "@deepseek-ai/dsh-root", "version": "0.2.1-alpha.2",
  "private": true, "packageManager": "pnpm@11.28.5", "license": "MIT",
  "engines": { "node": "^22.19.0 || >=24.0.0" } }
```

工作区声明：`vendor/*`、`packages/*/*`、`native/system`、`apps/*`、`website`。

15 个子目录的体积分布（不含 `.git`）：

| 子目录 | 文件数 | MiB | 说明 |
|---|---|---|---|
| `packages/` | 7076 | 56.30 | 主体：host/lib/client/web 各层包 |
| `docs/` | 692 | 22.33 | 文档与 i18n |
| `.agents/` | 3717 | 17.78 | 架构笔记 `notes/archived/architecture/*.md`（中英双份） |
| `snapshots/` | 1562 | 8.36 | 会话/Web 快照基线（`system-prompt.expected.md`、`ui.expected.md`） |
| `apps/` | 1164 | 8.26 | 应用 |
| `scripts/` | 388 | 4.44 | 构建/校验脚本 |
| `patches/` | 7 | 0.43 | 补丁 |
| `.github/` | 56 | 0.38 | CI |
| `python/` | 47 | 0.34 | Python 侧 |
| `vendor/` | 76 | **0.29** | 内置的 cordis 系包 |
| `benchmarks/` | 45 | 0.27 | |
| `native/` | 79 | 0.17 | |
| `website/` | 32 | 0.16 | |
| `.claude/` | 1 | 0.00 | |

**与 `reference/cordis` 的关键岔口**：`reference/deepseek-harness/vendor/` 里内置了一整套**已改名、已分叉**的 cordis：

| vendor 路径 | 包名 | 版本 | 对比 `reference/cordis` |
|---|---|---|---|
| `vendor/cordis/package.json` | `@deepseek-ai/cordis` | **4.0.5-alpha.1** | vs `cordis@4.0.0-rc.10` |
| `vendor/loader/` | `@deepseek-ai/cordis-plugin-loader` | 1.0.6-alpha.1 | vs `@cordisjs/plugin-loader@1.0.0-rc.7` |
| `vendor/include/` | `@deepseek-ai/cordis-plugin-include` | 1.0.10-alpha.1 | vs `@cordisjs/plugin-include@1.1.0` |
| `vendor/hmr/` | `@deepseek-ai/cordis-plugin-hmr` | 1.0.20-alpha.1 | vs 1.1.0 |
| `vendor/group/` | `@deepseek-ai/cordis-plugin-group` | 1.0.5-alpha.1 | vs 1.0.0 |
| `vendor/timer/` | `@deepseek-ai/cordis-plugin-timer` | 1.1.7-alpha.1 | vs 1.1.3 |
| `vendor/logger-console/` | `@deepseek-ai/cordis-plugin-logger-console` | 1.0.5-alpha.1 | vs 1.0.0 |
| `vendor/cosmokit/` | `@deepseek-ai/cosmokit` | 1.8.6-alpha.1 | — |
| `vendor/schemastery/` | `@deepseek-ai/schemastery` | 3.18.5-alpha.1 | — |

分叉后的 core 明显更大：`vendor/cordis/src/` 9 个文件共 **2696 行**（总行），而 `reference/cordis/packages/core/src/` 是 **1891 行**（总行；非空 1669 行）。**本项目用的是后者（npm 上的 `cordis@4.0.0-rc.10`），不是前者。**

---

## 3. 本项目实际用到了 reference/ 的什么

检索范围：`ecdr/`、`orchestrator/`、`docs/`、`scripts/`、`tools/`、`README.md`，关键词 `cordis`、`cordiverse`、`arXiv`、`2608.25512`、`deepseek`、`DSH`、`reference/`。

### 3.1 引用点 → 被引材料 对照表

| 引用点 | 被引材料 | 引用方式与实际强度 |
|---|---|---|
| `orchestrator/package.json:10` | `cordis` **4.0.0-rc.10** | 精确锁定（无 `^`），运行时依赖 |
| `orchestrator/package.json:8` | `@cordisjs/plugin-include` ^1.1.0 | 依赖 |
| `orchestrator/package.json:9` | `@cordisjs/plugin-loader` ^1.0.0-rc.7 | 依赖 |
| `orchestrator/package-lock.json:60-70` | `registry.npmjs.org/cordis/-/cordis-4.0.0-rc.10.tgz` | **解析来源是 npm registry，不是 `reference/cordis`** |
| `orchestrator/node_modules/cordis/package.json`（实测） | `cordis@4.0.0-rc.10`，只有 `lib/`（无 `src/`） | 实装版本与 `reference/cordis/packages/core` 逐字一致 |
| `orchestrator/smoke.ts:1` | `import { Context, Service } from 'cordis'` | 冒烟 |
| `orchestrator/src/{physics,loop,checker,llm,certificates}.ts:1` | `import { Service, type Context } from 'cordis'` | 5 个服务类 |
| `orchestrator/src/{unitsbound,selfaudit,run,random,demo,audit,argue,derive}.ts:1` | `import type { Context } from 'cordis'` | 插件出口 |
| （合计）`orchestrator/src/` **13/13** 个 `.ts` 均 import `cordis` | 共 1611 行 | 全部编排代码建立在该库上 |
| `orchestrator/src/{physics:6,loop:6,checker:4,llm:4,certificates:3}.ts` | `declare module 'cordis' { interface Context ... }` | 5 处模块增强，把服务注册进 Context |
| `orchestrator/src/certificates.ts:59` | `this.ctx.effect(() => { ... })` | **全仓唯一一处 `ctx.effect()`**，论文 "revertible effects" 的唯一落地点 |
| `orchestrator/src/*.ts` 共 **11** 处 `export const inject = [...]` | cordis 依赖注入 | 对应论文 "reactive coeffects"；声明最多的是 `run.ts:6`（5 个服务：loop/physics/checker/certificates/llm），`argue.ts:9` 为 4 个 |
| `orchestrator/cordis.yml:1-14` | 13 个插件条目 | 由 `@cordisjs/plugin-loader` 读取，对应论文 "declarative component loader" |
| `docs/findings/038-m6-unblocked.md:6` | "the reference is at `reference/` (gitignored)" | 全项目**唯一**记录 `reference/` 存在的地方 |
| `docs/findings/038-m6-unblocked.md:59-60` | `reference/cordis` + `reference/paper` | 显式指名 |
| `docs/findings/038-m6-unblocked.md:62-75` | cordis core 9 文件 + loader 3 文件行数表 | 阅读记录，见 §3.3 |
| `docs/findings/038-m6-unblocked.md:77-83` | 论文的两个概念 | 概念映射：revertible effects→证书撤销；reactive coeffects→域标签 |
| `docs/decisions/001-q4-simulation-and-orchestrator.md:10-13` | `arXiv 2608.25512` + 源检出路径 `D:/otherProject/dsh-win32` | **决策依据**；注意它指向的是仓库**外**的第三方 Windows 发行版，不是 `reference/deepseek-harness` |
| `docs/decisions/001-q4-simulation-and-orchestrator.md:22-24` | Cordis 三个概念（revertible effects / reactive coeffects / loader+HMR） | 逐条对应 ECDR 需求（回跳、冲突核键、机制清单可插拔） |
| `docs/CONSENSUS.md:308` | EngiAI（arXiv 2605.19743） | 仅读摘要页，标注 **[未核实]** |
| `docs/CONSENSUS.md:309` | VeriLoop E2 | 未读到原文/模型卡，抓取失败，**[未核实]** |
| `docs/findings/030-modelica-l2-works.md:18-19` | `omc` OpenModelica **1.27.1**；MSL **`4.1.0+maint.om`**（`exactMatch=true`） | 工具依赖 |
| `ecdr/l2/modelica/run.py:10`、`ecdr/l2/modelica/linearize.py:18` | `IMAGE = "openmodelica/openmodelica:v1.27.1-minimal"` | 工具依赖（Docker 镜像 tag） |
| `ecdr/l2/modelica/smoke/run.mos:1` | 注释即 pin 记录："OpenModelica 1.27.1 (image tag v1.27.1-minimal), MSL 4.1.0+maint.om" | 工具依赖 |
| `ecdr/bench/problem.py:3,53` | BOCoDe（arXiv **2608.15073**） | 接口仿制：`evaluate(x) -> (obj, cons)` |
| `README.md:163` | 仓库树里写 "`reference/` 种子对话原文、已核实的竞争格局" | **指向错误**：这些内容实际在 `docs/reference/`，而仓库根的 `reference/` 是本文清点的三个克隆。同名不同物，写论文时容易引错 |

### 3.2 零命中：`reference/deepseek-harness` 没有任何引用点

* 全仓 grep `deepseek-harness`：**0 命中**（`ecdr/`、`orchestrator/`、`docs/`、`scripts/`、`tools/`、`README.md`）。
* 全仓 grep `reference/deepseek-harness`：**0 命中**。
* 全仓 grep `\bDSH\b`：**1 命中**，`docs/decisions/001-q4-simulation-and-orchestrator.md:33`（"DSH is Node/TypeScript"），指的是**外部路径 `D:/otherProject/dsh-win32`**（`package.json: version 0.6.0`，`github.com/sjh9714/dsh-win32`，一个 Windows 优先的第三方 DSH 发行版，自带 `cordis.patch.yml`）。
* 全仓 grep `deepseek`：3 命中，全部是 API 端点与模型名（`orchestrator/cordis.yml:7` `model: deepseek-flash`；`orchestrator/src/llm.ts:99,104`），与这个检出无关。

**结论**：`reference/deepseek-harness` 占了 `reference/` 的 99.68% 体积（14988/15129 个工作树文件），被项目**零次引用**。

### 3.3 唯一可验证的口径不一致：finding 038 的"lines"列

`docs/findings/038-m6-unblocked.md:62-72` 给了一张 cordis core 的行数表，并据此写道 "Core is small enough to read in full"。我把这张表与 `reference/cordis/packages/core/src/` 逐文件核对：

| 文件 | finding 038 的 "lines" | 实际总行数 | 实际非空行数 |
|---|---|---|---|
| `fiber.ts` | 455 | 507 | **455** |
| `reflect.ts` | 253 | 283 | **253** |
| `utils.ts` | 250 | 282 | **250** |
| `logger.ts` | 214 | 246 | **214** |
| `registry.ts` | 182 | 214 | **182** |
| `events.ts` | 169 | 194 | **169** |
| `context.ts` | 69 | 78 | **69** |
| `service.ts` | 70 | 80 | **70** |
| `index.ts` | 7 | 7 | **7** |

**9/9 全部等于"非空行数"**；`docs/findings/038:74` 的 loader 三个数（152/118/61）同样等于非空行数（总行数 188/135/69），**3/3 命中**。

所以那不是一个错误，是一个**未声明的单位**：表头只写 "lines"。后果是 core 的规模被低报，1891 总行 vs 1669 非空行（差 222 行、11.7%）。这条值得记，因为它恰好是本项目自己的常设规则要抓的那类东西——"check any two compared columns for algebraic identity"（`docs/STATE.md:251`）。建议把 finding 038 的表头改成 "non-blank lines"。

---

## 4. 论文参考文献候选

分三类，界线是**"我们依赖它运行"还是"我们借它立论"**。项目纪律见 `docs/ROADMAP.md:586`（"Argue from cited authority. The case for certification is structural"）与 `docs/CONSENSUS.md:255-259`（共识 13/14/15）。

### 4.1 甲类：工具依赖（不是思想来源，是运行/编译依赖）

这些必须在方法章节或复现章节**声明版本并哈希**（`docs/findings/003:338-339` 的 integrity rule 6），但**不构成"引用权威"**——它们是被本项目的代码调用的外部实现。

| 外部工具 | 版本 / 标识 | 项目内的落点 | 依赖性质 |
|---|---|---|---|
| **cordis** | `4.0.0-rc.10`（+ `@cordisjs/plugin-loader@1.0.0-rc.7`、`@cordisjs/plugin-include@1.1.0`） | `orchestrator/package.json:8-10`；13/13 个 `src/*.ts` | 编排运行时 |
| **OpenModelica** | `1.27.1`，镜像 `openmodelica/openmodelica:v1.27.1-minimal` | `ecdr/l2/modelica/run.py:10`、`linearize.py:18` | L2 编译器/积分器（独立保真度的来源） |
| **Modelica Standard Library** | `4.1.0+maint.om`，`installPackage(..., exactMatch=true)` | `ecdr/l2/modelica/emit.py:40,130,205`（`Modelica.Mechanics.Translational`、`Modelica.Blocks.*`） | L2 组件库 |
| **DeepSeek API** | `https://api.deepseek.com/chat/completions`；`deepseek-flash`（DeepSeek-V4.1-Flash）、`deepseek-v4-pro` | `orchestrator/cordis.yml:7`、`orchestrator/src/llm.ts:99,104`；`docs/findings/038:12-14` | 被研究的 LLM 本体 |
| **BOCoDe 问题接口** | arXiv `2608.15073`，`evaluate(x) -> (obj, cons)` | `ecdr/bench/problem.py:3,53`、`ecdr/bench/family.py:4-5`、`ecdr/l1/problem.py:1,21` | **协议依赖**（借接口，不借结论） |
| **arXiv API / pypdf** | `tools/arxiv.py`、`tools/fetch_fulltext.py` | 语料获取管线 | 工具链 |

### 4.2 乙类：真正作为技术依据被使用的外部工作（思想来源）

判定标准：项目为其**改变了自己的设计**，而不只是提到它。每条给出"用在哪 → 用来做了什么（具体）"。

| 外部工作 | 用在哪 | 用来做了什么 |
|---|---|---|
| **CORE** — *Conflict-Oriented Reasoning Elimination for Verifiable Language-Model Search*，arXiv **2609.39069v1**（cs.CL，2026-09-30，Siyu Song 等） | `docs/findings/003:91-161`；被固化为 `docs/findings/003:138-150` 的 **P1–P9 九条规则** | 直接给出证书层的接口形态：三值 verifier `accept \| (reject, C) \| UNKNOWN`（→ **P4**）；sound conflict core（→ **P1**）；exhaustion core 用于"放弃整个机制类"（→ **P2**）；分级 core 生产与"heuristic core 永不进硬缓存"（→ **P9** 超集驱逐）。`docs/CONSENSUS.md:209` 记录 `certificate_pure` 的失败是「CORE 三级纪律的直接实证」——只在有证明处硬剪枝、无软回退，是有害的 |
| **2502.00271** — *Scaling Flaws of Verifier-Guided Search in Mathematical Reasoning*，arXiv **2502.00271v1**（cs.CL，2025-02-01，Fei Yu 等） | `docs/findings/003:55-89`；被 `docs/findings/005` 重估并**未被推翻** | 提供"score 型剪枝在规模上崩坏"的**经验禁令**：coverage gain 在 sample size 32 时为 −3.1/−15.6/−23.9/−32.8；crossover 发生在 sample size **4**；失败中 **77.1%–88.6%** 是 SELECTION 失败。这是本项目"剪枝信号必须是证明而不是分数"的**唯一外部实证依据** |
| **Heuresis** — *Search Strategies for Autonomous AI Research Agents Across Quality, Diversity and Novelty*，arXiv **2606.25198v2**（cs.AI，2026-07-01） | `docs/findings/003:29-53, 167-193`；`docs/findings/003:346-348`（integrity rule 11） | 命名了本项目的问题（"weak because the mechanism is bad" vs "weak because execution is unoptimised"），并给出 Q1 的**否定结果**（3,222 runs，零个 NS 1 "Original"）。项目据此把 Q1 从"生成"改写成"路由 + 清单维护"（`docs/findings/003:198-214`） |
| **AlphaEvolve** — arXiv **2506.13131v1**（cs.AI，2025-06-16） | `docs/findings/003:182-187, 366-367` | 其 evaluation cascade 被一对一到 L0→L1→L2 阶梯的**设计模板**；同时提供"无 discard/restart/abandon 规则"的反面对照 |
| **2608.28639** — *Reward-Oracle MCTS for Formal Theorem Proving: Sample-Efficient Search and the Need for Kernel-Level Proof Auditing*，arXiv **2608.28639v1**（cs.AI，2026-08-11） | `docs/findings/003:325-332, 338-339`（rules 1、2、6）；`docs/findings/057` | 三级审计协议（词法筛查 → 独立重导 → 反事实移除）与 `sorryAx` 案例（Lean 4.9.0 记录、4.15.0 仍复现）直接支撑"pin and hash 整个验证栈"与"reader 必须有可测的东西"这条结论 |
| **2605.19717** — *Physics-in-the-Loop: A Hybrid Agentic Architecture for Validated CAD Engineering Design*，arXiv **2605.19717v1**（cs.CV，2026-05-19） | `docs/findings/003:244, 271-278, 374-377` | 消融形状（禁用单一组件、其余保持、报列联检验；其头条 FEA feedback 59.0% vs 22.2%，Fisher exact p<0.01）；同时提供 "unrecoverable" 这个术语缺口 |
| **2608.21976** — *Closed-loop AI achieves certifiable engineering design*（Yu 等，浙江大学；本地文件无 arXiv 头，按 `docs/findings/003:244` 记为 2608.21976） | `docs/findings/003:243-264` | **竞争边界**：其 certificate 是**拟合代理**（11 个参考项目校准、Spearman 0.717、MAD 3.9、阈值取监管通过项目 90 分位、门禁仅在 **n=1** 上验证）。项目据此禁止无定语使用 "certifiable" |
| **2502.05870** — *Understanding Design Fixation in Generative AI*，arXiv **2502.05870v1**（cs.HC，2025-02-09） | `docs/findings/003:258-261, 371-373` | design fixation 的**已发表仪器**（novelty proportion P_n = unique/(unique+shared)；CLIP 嵌入两两距离 + Mann-Whitney；ChatGPT 67.4% vs Red Dot 78.2%），项目把单位换成"机制类"后复用 |
| **BOCoDe** — arXiv `2608.15073` | `docs/findings/003:357-365` | 除接口外还提供统计排名协议（median best-so-far、Friedman + Iman-Davenport + Nemenyi、Holm Wilcoxon when n<20）。它"**没有 mechanism 轴**"正是本项目的切口 |

### 4.3 丙类：已被明确降级，**不得**作立论依据

| 内容 | 处置出处 | 原文 |
|---|---|---|
| 用 2502.00271 / CORE / Heuresis 的**结论**支撑本方法 | `docs/CONSENSUS.md:277`（撤回表 #5） | 处置：**降级** |
| 文献给出的解空间偏小，启发式因此占优 | `docs/CONSENSUS.md:255`（共识 13） | "不能直接用来支撑本方法" |
| 老旧文献有时限 | `docs/CONSENSUS.md:257`（共识 14） | "不能轻易采信" |
| 论证路线 | `docs/CONSENSUS.md:259`（共识 15） | "应改为**从结构上论证**……而非引用权威结论" |
| 自撰 benchmark 作为优越性证据 | `docs/ROADMAP.md:590`；`docs/STATE.md:203-212` | 禁止 |

**写作含义**：乙类的 8 项在论文里的正确位置是"相关工作 / 我们据此改变了什么"，不是"因为有 X 所以我们成立"。CORE 提供的是**纪律**（三值、sound core、单调缓存），2502.00271 提供的是**禁令**，Heuresis 提供的是**问题命名**——三者都不是本项目命题的真值来源。命题的真值来源是 `docs/ROADMAP.md` 第 4–5 节的结构性论证。

### 4.4 一个分类上的诚实提醒：Cordis 同时属于甲类和乙类

`cordis` 既是工具依赖（§4.1），又被 `docs/decisions/001:22-24` 当成**概念来源**（revertible effects → 撤销；reactive coeffects → 域标签；loader+HMR → 机制清单可插拔）。写参考文献时应拆成两条处理：**软件引用**（`cordis@4.0.0-rc.10`，MIT）与**论文引用**（`arXiv:2608.25512`，BibTeX key `shi2026cordis`）。混在一起会让"工具依赖"看起来像"理论依据"。

### 4.5 附：项目真正持有的文献语料在 `docs/literature/`，不在 `reference/`

`reference/` 里 0 篇论文。项目实际持有的语料是 `docs/literature/`（受 git 跟踪，共 39 个文件 / 2086 KiB）：

* `docs/literature/arxiv/`：**24 个查询 JSON** + 1 个 `_index.json`；每个查询 JSON 含 `query` 与 `hits[]`（`id/title/abstract/published/authors/categories/url/pdf/comment`）。其中 `C2_fundamental_limits_vibration_isolation.json` 的 `hits` 为 **0**（空结果，是一个诚实保留的空查询）。
* `docs/literature/fulltext/`：**13 个 `.txt`**，去重后 **10 篇**唯一论文（`2608.21976.txt` 与 `2608.21976v1.txt` 逐字节相同，均 66550 B；`2502.00271`、`2609.39069` 各有 `.clean` 派生版）。
* `docs/literature/digest-core-vs-verifier-scaling.md`（10138 B）。

10 篇全文清单：2502.00271、2502.05870、2506.13131、2605.19717、2606.13473（MaxProof）、2606.25198、2608.15073、2608.21976、2608.28639、2609.39069。
**`docs/findings/003:3` 写的是 "9 full texts read in depth"**；第 10 篇（MaxProof，2606.13473）是 `docs/findings/005` 之后补入的，finding 003 的表头未随后更新。

### 4.6 缺原文的引用：必须在投稿前补齐或删除

| 被引 | 项目内的依据 | 状态 |
|---|---|---|
| **SimulCost**（ICML 2026） | `docs/decisions/001:43`、`docs/findings/003:257`、`docs/findings/006:127` | **本地无语料、无 arXiv 号**，只有名字。而它承载的是"成本模型必须与平台无关的解析成本对齐"这一实质要求 |
| **EngiAI**（arXiv 2605.19743） | `docs/CONSENSUS.md:308` | 仅摘要页，自标 **[未核实]** |
| **VeriLoop E2** | `docs/CONSENSUS.md:309` | 未读到原文/模型卡（抓取失败），自标 **[未核实]** |
| **Physics-in-the-Loop（IJCAI 2026）** | `docs/findings/003:244` | 与 arXiv 2605.19717 并列出现，是否同一工作的会议版**未说明** |
| **论文 2608.25512 正文** | `docs/findings/038:60`、`docs/decisions/001:11` | 只有 README 摘要（§2.2）；`reference/` 内无 PDF |

---

## 5. 与本研究无关的部分 / 可清理项

### 5.1 明确无关：`reference/deepseek-harness/`

判据（三条同时成立）：

1. **零引用**：`deepseek-harness`、`reference/deepseek-harness` 在 `ecdr/`、`orchestrator/`、`docs/`、`scripts/`、`tools/`、`README.md` 中命中数均为 **0**（§3.2）。
2. **不是决策记录指向的那个检出**：`docs/decisions/001:13` 指的是 `D:/otherProject/dsh-win32`（`version 0.6.0`，第三方 `github.com/sjh9714/dsh-win32`），**不是** `reference/deepseek-harness`（`@deepseek-ai/dsh-root@0.2.1-alpha.2`）。两者是不同仓库、不同版本线。
3. **体量占绝对多数**：121.12 MiB 中的 120.73 MiB（**99.68%**），15129 个工作树文件中的 14988 个。

**处置建议**：

* **默认删除**（或移出交付物）。保留它不增加任何可核验的引用。
* **若只为一个理由保留**：留 `reference/deepseek-harness/vendor/{cordis,loader,include,hmr,group,timer,logger-console,cosmokit,schemastery}/`（**76 个文件 / 0.29 MiB**），因为它是 `cordis@4.0.0-rc.10` 与 `@deepseek-ai/cordis@4.0.5-alpha.1` 之间**唯一可在本地做的版本对照**。其余 14912 个文件可弃。
* **注意一条诚实的保留**：`docs/CONSENSUS.md:243-247`（共识 8–10）讨论 "LLM + harness" 的定位，与这个检出的主题相邻。但**没有任何文档以路径形式引用它**，所以"相邻"不构成保留理由；若要保留这个理由，应当先把它写进文档。

### 5.2 计算得到的开销：三个 `.git` 目录

88 个文件 / 38.32 MiB，其中 `reference/deepseek-harness/.git` 一个就占 38.14 MiB（对它自己是纯开销，对 `cordis`/`paper` 则是**唯一的溯源凭据**——两者合计仅 0.19 MiB）。

* 若 `reference/` 随交付物发布：删 `deepseek-harness/.git`，**留** `cordis/.git` 与 `paper/.git`（保留提交哈希与 remote 的可验证性）。
* 若 `reference/` 不随交付物发布：三者的 `.git` 都可删，但需先把两个提交哈希抄进文档（本文 §1 已抄）。

### 5.3 不是"无关"而是"缺失"：`reference/paper/`

它只有 2 个文件、0.00 MiB。它的问题不是多余，而是**内容不在**（§2.2）。处置不是清理，是**在交付物里改成正式引用**：`arXiv:2608.25512`（cs.PL），BibTeX 直接取 `reference/paper/README.md` 中已有的 `shi2026cordis`，并在正文里明确"本文引用的是 arXiv 预印本，未能核对全文"（若在投稿前仍未下载全文）。

### 5.4 `README.md:163` 的路径歧义（应修，属文档而非 reference/）

`README.md:163` 把 `reference/` 描述为"种子对话原文、已核实的竞争格局"，那实际是 `docs/reference/` 的内容（`competitive-landscape.md`、`seed-conversation.md`、`seed-conversation.messages.json`、`seed-conversation.raw.html.gz`）。仓库根的 `reference/` 是本文清点的三个克隆。两个 `reference/` 同名不同物，且其中一个被 gitignore——这是最容易在写作时引错的地方。

---

## 6. 交付物排除清单（一句话版）

| 条目 | 页数/体积 | 是否进交付物 |
|---|---|---|
| `reference/cordis/` | 139 文件 / 0.38 MiB | **排除**文件，但引用其版本 `cordis@4.0.0-rc.10` 与提交 `c261dd2` |
| `reference/paper/` | 2 文件 / 0.00 MiB | **排除**文件，引用 `arXiv:2608.25512` + `shi2026cordis` |
| `reference/deepseek-harness/` | 14988 文件 / 120.73 MiB | **排除**（§5.1） |
| 三个 `.git` | 88 文件 / 38.32 MiB | **排除**，哈希抄进 §1 后即可 |
| `docs/literature/` | 39 文件 / 2.09 MiB | **保留**（受 git 跟踪，是真正的引用凭据） |

---

## 7. 本文数字的复现方式

本文没有生成脚本（任务约束是"只读 + 只写一个 Markdown 文件"），因此在这里给出所用方法与可复现代码，供后续固化成 `scripts/` 下的一步。

* **文件数与体积**：递归 `readdirSync` + `statSync`，对 `.git` 做一次跳过/不跳过的对照（这一步同时解释了 15129 与 15217 的差）：
  ```js
  function walk(dir, skipGit) {
    let files = 0, bytes = 0; const stack = [dir]
    while (stack.length) {
      const d = stack.pop()
      for (const e of fs.readdirSync(d, { withFileTypes: true })) {
        if (skipGit && e.name === '.git') continue
        const p = path.join(d, e.name)
        if (e.isDirectory()) stack.push(p)
        else { files++; bytes += fs.statSync(p).size }
      }
    }
    return { files, bytes }
  }
  ```
* **版本与标识**：`read` 读取 `package.json` / `README.md` / `.git/config` / `.git/logs/HEAD` / `.git/shallow` / `.git/packed-refs`；`reference/paper/.git/index` 以前 12 字节（`DIRC` + version + 条目数）与 ASCII 串判读受跟踪文件，得 2 个。
* **引用点**：`grep` 工具在 `ecdr/`、`orchestrator/`、`docs/`、`scripts/`、`tools/`、`README.md` 上搜索 `cordis`、`cordiverse`、`arXiv`、`2608\.25512`、`deepseek`、`\bDSH\b`、`reference/`、`OpenModelica`、`Modelica`、`\bMSL\b`、`deepseek-harness`、`dsh-win32`。
* **行数口径（§3.3）**：对同一文件分别算 `split("\n").length - 1`（总行）、`filter(l => l.trim()).length`（非空行）、以及去 `/* */` 与 `^\s*//` 后的非空行数；只有**非空行**在 12/12 个文件上与 finding 038 的表一致。

**本索引中未复现、依赖项目自身记录的数字**（按本项目惯例应显式标注）：finding 038 中 `deepseek-v4-pro` 未测；`docs/CONSENSUS.md` §8 已列出的全部 [未核实] 项；`docs/findings/003` 引述 Heuresis / CORE / 2502.00271 的数字——这些数字我在 10 篇本地全文中**未逐条回核**，本文只转述它们被引用这件事本身。
