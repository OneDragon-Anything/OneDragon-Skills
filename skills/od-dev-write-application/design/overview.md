# od-dev-write-application — 设计概览(what)

> 本文件是 **what**(skill 长什么样 / 范围 / 边界 / 构成);重构动机见「设计动机」节。

## 定位(是什么)

OneDragon 框架上「写 / 改 / 调试**一个 Application**」的方法论 skill。把玩法的若干 Operation 组合成可运行的 app(自动注册、有配置/GUI、能进一条龙或单独跑)。

**核心洞察**:Application 继承 Operation → **写 app 90% = 写 op**(→ `od-dev-write-operation`);本 skill 只讲 app 加的那一层。

## 边界(3-粒度拆分)

- op 粒度(单 Operation)→ `od-dev-write-operation`。
- **app 粒度(整个 Application 产品化)→ 本 skill**。
- 玩法粒度(从零做新玩法全程)→ `od-dev-gameplay-automation`。

判单项归哪层,问:这是「单个 op 的写/改/修」,还是「整个 app 的搭/配/编排」,还是「从零做新玩法的全程」?

## 范围 IN(app 作者完整参考)

- **编排设计**:自底向上(op 先各自验证再串联)/ hub 模式 / 编排语义(顺序 / 分支 / 循环 / resume)/ 设计过目(轻量裁决:非纯顺序编排向用户过设计)。
- **5 文件结构**(const / run_record / config / factory / app)+ **约定式自动注册**。
- **Factory + const + 发现规则**(APP_ID / DEFAULT_GROUP / 第三方插件 / zip)。
- **Config**(`YamlConfig` 子类 + adapter + 实例级)+ **GUI**(setting card interface)。
- **run-record**(`AppRunRecord` + 周期重置 + 业务字段)。
- **端到端验证**:重启 MCP server → 注册确认 → `run_standalone_app`(hub→hub)。
- **修改与调试**:分层分诊(op 内部 / 串联层 / 产品化层 / 不在场排查)+ app 特有症状速查。

## 范围 OUT(指针,不重复)

- 单 op 写法(节点图 / `round_by_*` / 画面判定 / 修改调试)→ `od-dev-write-operation`(app 复用同一套;app 节点图与 round 规范全量同守它,本 skill 不复述)。
- 从零做新玩法全程 → `od-dev-gameplay-automation`(它阶段 6 app 产品化引用本 skill)。
- 画面建档 / screen_info area → `od-dev-screen-onboarding`。
- 用户反馈的运行失败排查 → `od-dev-debug-automation`。
- 任务账本 / 进度结构 → `od-dev-progress-tracking`(本 skill 不内置进度模板)。
- app 设计文档组织 → 所在项目文档规范(本 skill 不内置文档方法论)。

## 构成(文件结构)

- `SKILL.md`:开头 4 步 checklist(completion gate)→ ①编排设计(1.1 自底向上 / 1.2 hub 模式 / 1.3 编排语义 / 1.4 设计过目)→ ②五件套 → ③端到端验证 → §4 修改与调试(分诊 + 症状速查)→ §5 必守不变量 → §6 边界 → §7 写完自检。
- `references/`:
  - `factory-and-discovery.md`:自动发现规则 + Factory + const + 第三方插件 + zip。
  - `config-and-gui.md`:`YamlConfig` + adapter + 实例级 + setting card + interface。
  - `run-record.md`:`AppRunRecord` + 周期重置 + 子类业务字段。
- `design/`:本目录(overview + ADR)。

## 设计动机(why)

- **主线比 op 短(3 步主线 vs op 六步)**:app 的复杂度不在画面流转(被 op 层消化),在编排语义 + 产品化接线 —— 没有「摸流程」与三份设计稿的对应物,编排设计一页纸(①)。
- **设计过目取轻量档(1.4)**:对齐 op ④「agent 自主推进后必有裁决」的哲学,但编排设计通常直接来自用户需求 —— 折中为「非纯顺序编排才报,纯顺序串联免报」(2026-11-12 用户裁定)。
- **mock 快测不设必做**:op 各自测试已在 op 主线 ⑥ 落盘;app = 已验证 op 的串联,强制三层验证性价比低 —— 编排复杂(多分支 / 循环 / 条件跳转)时按「测试只覆盖核心」判据补锁串联结构(2026-11-12 用户裁定)。
- **删除「进度模板」节**(2026-11-12 用户裁定):任务账本单一源在 `od-dev-progress-tracking`,曾内置的进度模板满是账本内部术语且与正文重复 —— 职责归位,整节删。
- **删除「设计文档组织」节 + `app-design-doc.md`**(2026-11-12 用户裁定):文档组织归所在项目文档规范(各项目有自己的双层文档流 / ADR 体系),公共 skill 内置目录结构必然冲突;app 特有判据信息量小,不足撑一个 reference。
- **新增修改与调试章**:description 一直承诺「修改或调试」,正文曾只有新建路径;app 特有症状(跑完首节点即结束 / 一条龙跳过 / 改码没变 / 不在列表)原本散落各处,聚成分诊表 + 症状速查。
- **不变量收敛**:原 7 条里 4 条是 op 层规范复述,与「不重复 write-operation」的定位自相矛盾 —— 收敛为一句指针,app 层 5 条留正文。

## 落点

公共仓 `OneDragon-Skills/skills/od-dev-write-application/`,OneDragon 系列通用(SR / ZZZ 等)。各消费方仓库按其 setup 约定挂载。

## 类型(RED / GREEN)

方法论覆盖型(整合 OneDragon app 开发已成型的实践 + 框架 API 成系统流程)→ RED 可省,**GREEN 必做**。

**状态:draft(2026-11-12 重构后待 GREEN;上一版也是 draft 未测)**。参考来源:SR 现有 app(world_patrol / sim_universe / trailblaze_power / currency_war)+ ZZZ `zzz-od-dev-plugin` skill + 框架 `Application` / `ApplicationFactory` / `AppRunRecord` / `YamlConfig` API。迁公共仓时已泛化项目专属(SrApplication/ZApplication/BackToNormalWorldPlus/大世界/src 路径)为通用说法。
