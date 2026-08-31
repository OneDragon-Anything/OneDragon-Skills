# od-dev-write-application — 设计概览(what)

> 本文件是 **what**(skill 长什么样 / 范围 / 边界 / 构成)。**why** 见 `decisions/`。

## 定位(是什么)

OneDragon 框架上「写 / 改 / 调试**一个 Application**」的方法论 skill。把玩法的若干 Operation 组合成可运行的 app(自动注册、有配置/GUI、能进一条龙或单独跑)。

**核心洞察**:Application 继承 Operation → **写 app 90% = 写 op**(→ `od-dev-write-operation`);本 skill 只讲 app 加的那一层。

## 边界(3-粒度拆分)

- op 粒度(单 Operation)→ `od-dev-write-operation`。
- **app 粒度(整个 Application 产品化)→ 本 skill**。
- 玩法粒度(从零做新玩法全程)→ `od-dev-gameplay-automation`。

判单项归哪层,问:这是「单个 op 的写/改/修」,还是「整个 app 的搭/配/编排」,还是「从零做新玩法的全程」?

## 范围 IN(app 作者完整参考)

- **5 文件结构**(const / run_record / config / factory / app)+ **约定式自动注册**。
- **Factory + const + 发现规则**(APP_ID / DEFAULT_GROUP / 第三方插件 / zip)。
- **Config**(`YamlConfig` 子类 + adapter + 实例级)+ **GUI**(setting card interface)。
- **编排**:hub 模式(必做)+ resume(加分);`op_to_enter_game` 框架自动。
- **编写顺序**:op 先验证再 app 串联(自底向上)。
- **run-record**(`AppRunRecord` + 周期重置 + 业务字段)。

## 范围 OUT(指针,不重复)

- 单 op 写法(节点图 / `round_by_*` / 画面判定 / 探索式迭代)→ `od-dev-write-operation`(app 复用同一套)。
- 从零做新玩法全程 → `od-dev-gameplay-automation`(它阶段 6 app 产品化引用本 skill)。
- 画面建档 / screen_info area → `od-dev-screen-onboarding`。
- 检测 / 验证 UI 区域坐标 → od-dev-screen-onboarding §4.5。

## 构成(文件结构)

- `SKILL.md`:compact 核心 —— 开篇洞察(Application=Operation)+ 标准步骤 + 编写顺序 + 编排(hub/resume)+ 必守不变量 + 边界 + 自检。
- `references/`(progressive disclosure):
  - `factory-and-discovery.md`:自动发现规则 + Factory + const + 第三方插件 + zip。
  - `config-and-gui.md`:`YamlConfig` + adapter + 实例级 + setting card + interface。
  - `run-record.md`:`AppRunRecord` + 周期重置 + 子类业务字段。
- `design/`:本目录(overview + ADR)。

## 落点

公共仓 `OneDragon-Skills/skills/od-dev-write-application/`,OneDragon 系列通用(SR / ZZZ 等)。各消费方仓库按其 setup 约定挂载。SR/ZZZ 的项目内 app skill(若有)后续迁移指向本 common skill。

## 类型(RED / GREEN)

方法论覆盖型(整合 OneDragon app 开发已成型的实践 + 框架 API 成系统流程)→ RED 可省,**GREEN 必做**。

**状态:draft(GREEN-pending,2026-08-05)**。参考来源:SR 现有 app(world_patrol / sim_universe / trailblaze_power / currency_war)+ ZZZ `zzz-od-dev-plugin` skill + 框架 `Application` / `ApplicationFactory` / `AppRunRecord` / `YamlConfig` API。迁公共仓时已泛化项目专属(SrApplication/ZApplication/BackToNormalWorldPlus/大世界/src 路径)为通用说法。
