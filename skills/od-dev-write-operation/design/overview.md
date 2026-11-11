# od-dev-write-operation — 设计概览(what)

> 本文件是 **what**(skill 长什么样 / 范围 / 边界 / 构成)。

## 定位(是什么)

OneDragon 框架上「写 / 改 / 调试**单个 Operation**」的完整方法论 skill。三条主线织在一起:
1. **探索式开发主线**(地基):自动化脚本需求不可完备 → **建档-led 增量**(建档先粗 → 实现 → 测试 → 发现 → 补建档+补分支 → loop)。它决定 op 该怎么写(拆小 / 多log多截图 / 预料外调研建档 / 调试读日志 / 重复建op)。
2. **mechanics**:节点图(`@operation_node` / `@node_from` / 路由 / 自环陷阱)、round 结果语义、`round_by_*` 选型、op 与 reader 内工具(含非节点上下文的无 round 原语)、单 op 测试机制、**循环驱动玩法的 op 结构选型(flat loop vs node-per-op)**、**多目标特征识别范式(区域特征一次提取 + 模板集匹配 + 几何过滤 + 得分仲裁;含模板分辨率下限 / 造型变体失效 / 网格槽位插值补全三条边界与防线)**。
3. **op 粒度规范**:看动等验、识别方式选型、建档前置、OCR 关键词独有、click 时序可靠性(项目相关,见 framework-pitfalls)。

给 coding agent 看,框架通用(不绑具体玩法)。

## 为什么单独成一个 skill(边界)

按**粒度**把"玩法自动化开发"拆成三层,每层一个自洽完整的 skill:

- **op 粒度**(单 Operation)→ 本 skill(`od-dev-write-operation`)。高频:写 / 改 / 修 op。**也是探索式开发 + 框架踩坑的地基**(op 是最具体单元;gameplay-automation 引用本 skill 的 op 级方法论 + framework-pitfalls)。
- **app 粒度**(整个 Application 产品化:factory / config / GUI / run-record / app 级编排)→ `od-dev-write-application`(common)。
- **玩法粒度**(从零做新玩法的全程 pipeline)→ `od-dev-gameplay-automation`(已存在;op 级方法论已迁入本 skill,它瘦成纯生命周期 + 引用本 skill)。

判单项归哪层,问:这是「单个 Operation 的写 / 改 / 修」,还是「整个 app 的搭 / 配 / 编排」,还是「从零做新玩法的全程」?

## 范围 IN(op 作者完整参考)

**探索式主线**(SKILL.md 开篇 + `runtime-craft.md`):建档-led 增量;信息密度论(多 log 多截图根因);调试先读日志 + 补日志;预料外画面调研 + 建档;运行时不确定性预留日志;重复手动建op。

**mechanics**:Operation 结构(`__init__` / `handle_init` / `node_max_retry_times` / `need_check_game_win`);节点图(`@operation_node` / `@node_from` / 路由 / 自环陷阱 / `previous_node`);round 结果语义;`round_by_*` 选型 + LCS 机制;op 与 reader 内工具(`screenshot` / `controller` / `ocr` / 子 op / 非节点上下文无 round 原语);单 op 测试机制(`run_operation` 单跑 / mock 截图 / TDD vs 刻画);**循环驱动玩法的 op 结构选型**(flat loop vs node-per-op)。

**op 粒度规范(织入主线)**:看动等验;每屏定识别方式;建档前置(引 `od-dev-screen-onboarding`);OCR 关键词独有(LCS 坑);click 时序可靠性(项目相关,见 framework-pitfalls)。

**框架踩坑**(single source,`framework-pitfalls.md`):click 与鼠标移动无间隔(项目相关)/ MCP 异步 / ONNX / 配置生效 / 录屏 / GBK 日志。`od-dev-gameplay-automation` 引用本文件。

## 范围 OUT(指针,不重复)

- 从零做新玩法全程 → `od-dev-gameplay-automation`
- app 产品化(factory / config / GUI / run-record / app 级编排)→ `od-dev-write-application`(common;app 节点复用本 skill 的节点图机制,不重复讲)
- 建一张屏的机制(analyze → 视觉大模型 → doc → screen_info area → 存模板)→ `od-dev-screen-onboarding`
- 检测 / 验证 UI 区域坐标(槽位网格 / 图标阵列)→ od-dev-screen-onboarding §4.5
- 非 op 领域的通用调试 / 修复决策 → 所在项目的调试类 skill(如有);通用调试纪律已内联本 skill

## 构成(文件结构)

- `SKILL.md`:compact 核心 —— 探索式主线(开篇)+ 写 op 主线 + round 结果心智 + `round_by_*` 选型 + op 与 reader 内工具 + 必守不变量(含探索式技术)+ 边界 + 自检。框架地基级接口名(`@operation_node` / `@node_from` / `round_by_*` / `controller` / `ocr` ...)。
- `references/`(progressive disclosure):
  - `runtime-craft.md`:探索式开发的 op 级技术(信息密度 / 调试纪律 / 预料外调研 / 运行时不确定性 / 重复建op)—— op 级方法论 single source(gameplay 引用)。
  - `multi-target-recognition.md`:多目标特征识别范式全文(适用判据 / 做法四步 / 网格槽位插值补全 / 边界判据);SKILL.md 只留适用判据 + 指针。
  - `round-by-helpers.md`:`round_by_*` 家族逐个语义 + 何时用哪个 + 关键参数 + LCS 机制 + 非节点上下文无 round 底层原语对照。
  - `node-graph.md`:节点图机制 / 路由规则 / 自环陷阱 / `previous_node` / `handle_init`。
  - `loop-driven-op-structure.md`:循环驱动玩法的 op 结构选型(flat loop vs node-per-op)+ committed-but-verifying + 节点作用域预算(single source;gameplay 引用)。
  - `testing.md`:单 op 测试机制 + TDD / fixture 策略。
  - `framework-pitfalls.md`:框架踩坑完整清单(single source)。
- `design/`:本目录(overview + ADR)。

## 落点

公共仓 `OneDragon-Skills/skills/od-dev-write-operation/`,OneDragon 系列通用(SR/ZZZ 等)。各消费方仓库按其 setup 约定挂载(如 Claude Code junction 进 `.claude/skills/`)。挂载 / 命名 / 路径约定是**所在仓库的 setup**,不在本 skill(见 od-dev-writing-skills)。

## 类型(RED / GREEN)

方法论覆盖型(整合 OneDragon op 开发已成型的实践 + 框架 API + 探索式开发方法论成系统流程)→ RED 可省,**GREEN 必做**(方法见 `od-dev-writing-skills` 的 `references/skill-testing.md`)。

**状态:draft(GREEN-pending,2026-08-04)** —— 结构合规(od-dev-writing-skills 4 硬规范自检过),GREEN utility test 待跑。迁公共仓时已泛化项目专属基础设施为通用说法(如「重启 MCP server」/ 测试仓 / 项目源码路径)。
