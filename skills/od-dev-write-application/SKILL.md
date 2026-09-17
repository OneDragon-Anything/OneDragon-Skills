---
name: od-dev-write-application
description: 当要在一条龙(OneDragon)框架上新建、修改或调试一个 Application(应用)时用 —— 把玩法的 Operation 组合成一个可运行的 app(写 app 类 + factory 注册 + config + GUI + run-record + 编排,复杂 app 含设计文档组织)。Use when creating/modifying/debugging an Application — compose ops into a runnable app, incl. design-doc organization for complex apps. 不触发:写单个 op(od-dev-write-operation)、从零做新玩法(od-dev-gameplay-automation)。
---

# 写 / 改 一个 Application(OneDragon)

把一个玩法的若干 Operation 组合成一个**可运行的 Application**(自动注册、有配置 / GUI、能进一条龙批量跑或单独跑)。

## 核心洞察:Application 就是 Operation

`Application` 继承 `Operation`,**复用同一套节点图(`@operation_node` / `@node_from`)、round 机制、截图 / 点击 API**。**写 app 90% = 写 op**(节点图 / `round_by_*` / 画面判定 / 探索式迭代)→ 见 `od-dev-write-operation`,**本 skill 不重复,只讲 app 加的那一层**。

app 在 op 上加的基础设施:
- **`app_id` 身份** + **`AppRunRecord`**(按日 / 周周期重置的运行记录)
- **约定式自动注册**(零手工;`*_factory.py` + `*_const.py` 被框架扫描发现)
- **screen scope**(每 app 独立 screen_info 作用域)
- **生命周期钩子**(`handle_init` / `after_operation_done` 自动更新 run-record + 通知)

## 写一个 app 的标准步骤

| 步 | 做什么 | 必做? |
|---|---|---|
| 1 | **const**:定义 `APP_ID` / `APP_NAME` / `DEFAULT_GROUP` / `NEED_NOTIFY` | 必做 |
| 2 | **run_record**:继承 `AppRunRecord`(空壳起步,业务字段后加) | 必做 |
| 3 | **config**:继承 `YamlConfig`(property + setter.update + `xxx_adapter`) | 有配置才 |
| 4 | **factory**:继承 `ApplicationFactory`(`create_application` + `create_run_record`;有 config 再 `create_config`) | 必做 |
| 5 | **app**:继承项目的 Application 子类,`@operation_node` + `@node_from` 编排节点图 | 必做 |
| 6 | **Context 接线**:项目的 Context 实例配置加载里挂 `self.<app>_config` / `_record`(供外部直接访问) | **特殊情况才**(factory 通常够) |
| 7 | **GUI**:setting card interface | 按需 |

**最小可跑 = 步 1-5**(无 GUI 也能 run,经一条龙 / `run_standalone_app`)。深度(factory 发现规则 / config + GUI / run-record / 第三方插件 / zip 包)见 `references/`。

## 编写顺序:op 先验证,再 app 串联(自底向上)

写 app 逻辑**自底向上**:
1. **先把 app 要用的 op 各自写完 + `run_operation` 单独验证过**(按 `od-dev-write-operation`;每个 op 独立实测 OK)。
2. **再写 app 节点图**(用 `@operation_node` + `@node_from` 把验证过的 op 串联;子 op 经 `round_by_op_result` 调)。
3. **`run_standalone_app` 端到端跑**验 op 串联 / 状态流转 / 入口回 hub + 出口回 hub。

**别先搭 app 壳再慢慢填 op** —— op 没验证就串联,app 失败时分不清是 op 坏还是串联坏(定位难)。op 各自绿了,app 端到端失败就锁在串联 / 状态流转上。

## app 编排:hub 模式(必做)+ resume(加分)

**hub 模式(必做,够日常自动化)**:app **第一个 op = 返回最通用的画面(hub,项目的主界面)→ 从 hub 跑流程 → 最后一个 op = 返回 hub**(各项目有标准收尾 op)。
- 保证**已知起止态**(单独跑 or 一条龙,都从 hub 起、回 hub 终);
- 一条龙里 app 间**干净衔接**(都在 hub 交接:上一个回 hub = 下一个起点)。
- **`op_to_enter_game` 由框架自动**(`need_check_game_win=True` 时,框架在入口前自动插「检测游戏窗口 + 进游戏」节点)—— app 不写"打开游戏"。

**resume(加分项,非必做)**:入口 op 先自检当前态、已在玩法就 skip → crash / 重启 / 手动接管后能从任何态 resume。**日常自动化用不上**;长流程 / 易崩 / 用户常中途接管的 app 才值得加。

> 节点图 / `round_by_*` / 画面判定 / 探索式迭代怎么写 → `od-dev-write-operation`(app 复用同一套,本 skill 不重复)。

## 必守不变量

- **`APP_ID` 全局唯一**(重复注册被拒);与 run-record 的 app_id 一致。
- **同一目录一个 `_factory.py` + 一个 `_const.py`**(多个 → 该目录跳过)。
- **factory 必须实现 `create_application`**;需要 run-record 再 `create_run_record`。
- **app 类继承项目的 Application 子类**(框架基类 `Application`;项目通常有特化子类,带默认 `op_to_enter_game`),构造传 `app_id` + `run_record`。
- **节点图一个 `is_start_node=True`**;复用 write-operation 的节点图 / round 机制。
- **改 app 代码后重启 MCP server 生效**(框架缓存 app 实例,同改配置)。

## 边界(去别的 skill)

- 写 / 改 / 调试**单个 Operation** → `od-dev-write-operation`(app 复用它)。
- **从零做新玩法全程** → `od-dev-gameplay-automation`(它阶段 6 app 产品化引用本 skill)。
- 画面建档 / screen_info area → `od-dev-screen-onboarding`。
- 检测 / 验证 UI 区域坐标 → od-dev-screen-onboarding §4.5。

## 写完自检

- [ ] `APP_ID` 全局唯一 + 与 run-record app_id 一致?
- [ ] 同一目录一个 `_factory.py` + 一个 `_const.py`?
- [ ] factory 实现 `create_application`(需 record 再 `create_run_record`)?
- [ ] app 继承项目的 Application 子类,传 `app_id` + `run_record`?
- [ ] 节点图:一个 `is_start_node`;**第一个 op 回 hub;最后一个 op 回 hub**?
- [ ] 外部(GUI / 其他 app)要直接访问 app config/record?→ 才需 Context 接线(factory 通常够,默认不接)
- [ ] 改完代码重启 MCP server?

## 设计文档组织(复杂 app 才需要)

复杂 app(多 op / 分支 / 循环 / 策略 / 多子系统)该有设计文档,记**设计 why + 架构 overview**(不复述代码)。简单 app 代码自解释不必写。**总分结构**(README 总览 + 按需拆)。落 `docs/develop/<app>/`(与 `docs/game/<玩法>/` 游戏玩法分开)。详见 `references/app-design-doc.md`。

## 进度模板(本 skill 任务怎么算完成)

> 配合 `od-dev-progress-tracking`(DAG 账本 + 五态状态机) + `od-dev-gameplay-automation`(module 归属语义,其 references/progress-tracking.md)。本 skill 负责 **app 编排任务**(module=流程,所有画面闭环后)的完成判据 + 防跑偏点。**位置与前置**:app 编排=一个任务,deps=各画面闭环任务(画面建档判据→`od-dev-screen-onboarding`,op 判据→`od-dev-write-operation`)。
>
> ⚠️ **app 编排 = 一个多步任务,不是单步叶子**:app 编排有**多步**(§标准步骤步1-5:const / run_record / config / factory / app + hub模式 + 自检)→ **一个任务承载**(module=流程,deps 引用各画面闭环任务),步进用 note 记,步1-5 全过才标 done(criteria 带产物指针;多步任务纪律见 od-dev-progress-tracking §12)。下表给的是 app 编排**整体的完成判据**(各子步骤的判据在 §标准步骤)。

| 任务 | 形态 | 已过判据(指本 skill) | 特有防跑偏点 |
|---|---|---|---|
| app 编排/factory/config/GUI | **多步任务**(步1-5) | §标准步骤 最小可跑(步1-5:const/run_record/config/factory/app)+ §hub模式 + §写完自检全过 | **自底向上**:op 先各自 `run_operation` 验证过再串联(§编写顺序);别先搭 app 壳再慢慢填 op(op 没验证就串联,失败时分不清 op 坏还是串联坏) |

- **状态记录**:app 编排是**做法二**的非叶子任务(所有画面闭环后建,deps 引用它们);**完整闭环**还要做法二出口 `run_standalone_app` 端到端跑通(独立任务,deps 引用 app 编排任务)。五步步进用任务 note 记。
- **跑偏信号(本 skill)**:先搭壳再填 op;首/尾 op 没回 hub(§hub模式必做);改 app 代码没重启 MCP server(框架缓存 app 实例)。
