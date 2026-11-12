---
name: od-dev-write-application
description: 当要在一条龙(OneDragon)框架上新建、修改或调试一个 Application(应用)时用 —— 把玩法的 Operation 组合成一个可运行的 app(编排设计 + app 类 + factory 注册 + config + GUI + run-record)。Use when creating/modifying/debugging an Application — compose ops into a runnable app. 不触发:写单个 op(od-dev-write-operation)、从零做新玩法(od-dev-gameplay-automation)、用户反馈的运行失败排查(od-dev-debug-automation)。
---

# 写 / 改 / 调试一个 Application(OneDragon)

把一个玩法的若干 Operation 组合成一个**可运行的 Application**(自动注册、有配置 / GUI、能进一条龙批量跑或单独跑)。

`Application` 继承 `Operation`,**写 app 90% = 写 op**(节点图 / `round_by_*` / 画面判定 / 调试)→ 全套规范见 `od-dev-write-operation`,**本 skill 不重复,只讲 app 加的那一层**:

- **`app_id` 身份** + **`AppRunRecord`**(按日 / 周周期重置的运行记录)
- **约定式自动注册**(零手工;`*_factory.py` + `*_const.py` 被框架扫描发现)
- **screen scope**(每 app 独立 screen_info 作用域)
- **生命周期钩子**(`handle_init` / `after_operation_done` 自动更新 run-record + 通知)

**没做完这 4 步不算完成**(改已有 app 走 §4 分诊,轻改可免走全程):

1. ☐ 编排设计:app 目标一句话 + op 清单(缺的 op 先回 `od-dev-write-operation` 走完它的主线)+ hub 骨架 + 分支/循环语义;非纯顺序编排先向用户过设计 → ①
2. ☐ 五件套落地:const / run_record / config(有配置才) / factory / app 节点图 → ②
3. ☐ 端到端验证:重启 MCP server → 注册确认 → `run_standalone_app` 实机从 hub 跑回 hub → ③
4. ☐ 过 §7 自检收口,全过才算完成

## ① 编排设计(纸面,串联已验证的 op)

### 1.1 自底向上:op 先各自验证,再 app 串联

1. **先把 app 要用的 op 各自写完 + `run_operation` 单独验证过**(按 `od-dev-write-operation` 走完它的主线);
2. **再写 app 节点图**(`@operation_node` + `@node_from` 串联;子 op 在节点内 `op.execute()` 调用,其返回结果 = 该节点的一种识别分支,每个结果显式处理 —— `od-dev-write-operation` §3.4);
3. **`run_standalone_app` 端到端跑**(③)。

**别先搭 app 壳再慢慢填 op** —— op 没验证就串联,app 失败时分不清是 op 坏还是串联坏(定位难);op 各自绿了,app 端到端失败就锁在串联 / 状态流转上。

### 1.2 hub 模式(必做)

app **第一个 op = 回到最通用的画面(hub,项目的主界面)→ 从 hub 跑流程 → 最后一个 op = 回 hub**(各项目有标准收尾 op):

- **已知起止态**:单独跑 or 一条龙连跑,都从 hub 起、回 hub 终;
- 一条龙里 app 间**干净衔接**(都在 hub 交接:上一个回 hub = 下一个起点);
- **`op_to_enter_game` 由框架自动**(`need_check_game_win=True` 时,框架在入口前自动插「检测游戏窗口 + 进游戏」节点)—— app 不写"打开游戏"。

### 1.3 编排语义

| 语义 | 写法 |
|---|---|
| 顺序(默认) | `@node_from` 依次串接 |
| 分支 | 子 op 返回结果 = 分支,显式处理每种结果(`od-dev-write-operation` §3.4) |
| 循环 / 重试 | 循环结构选型与实现(`od-dev-write-operation` §3.1) |
| resume(加分项,非必做) | 入口 op 先自检当前态、已在玩法就 skip → crash / 重启 / 手动接管后能从任何态 resume。日常自动化用不上;长流程 / 易崩 / 用户常中途接管的 app 才值得加 |

### 1.4 设计过目(轻量裁决)

编排设计完成后、写代码前:

- **非纯顺序编排**(有分支 / 循环 / 条件跳过 / 碰消耗红线)→ 向用户过一眼:**op 清单 + hub 骨架 + 分支语义**,等确认再进 ②;
- **纯顺序串联的简单 app** 免报,直接落地。

## ② 五件套落地

| 步 | 做什么 | 必做? |
|---|---|---|
| 1 | **const**:定义 `APP_ID` / `APP_NAME` / `DEFAULT_GROUP` / `NEED_NOTIFY` | 必做 |
| 2 | **run_record**:继承 `AppRunRecord`(空壳起步,业务字段后加) | 必做 |
| 3 | **config**:继承 `YamlConfig`(property + setter.update + `xxx_adapter`) | 有配置才 |
| 4 | **factory**:继承 `ApplicationFactory`(`create_application` + `create_run_record`;有 config 再 `create_config`) | 必做 |
| 5 | **app**:继承项目的 Application 子类,`@operation_node` + `@node_from` 编排节点图 | 必做 |
| 6 | **Context 接线**:项目的 Context 实例配置加载里挂 `self.<app>_config` / `_record`(供外部直接访问) | **特殊情况才**(factory 通常够) |
| 7 | **GUI**:setting card interface | 按需 |

**最小可跑 = 步 1-5**(无 GUI 也能 run,经一条龙 / `run_standalone_app`)。深度(factory 发现规则 / config + GUI / run-record / 第三方插件 / zip 包)见 `references/` 对应文件。

## ③ 端到端验证

1. **重启 MCP server**(改了任何 Python 代码必做 —— 框架缓存已加载模块与 app 实例,不重启跑的还是旧的);
2. **注册确认**:app 出现在可运行列表(`list_applications` / GUI);不在 → 查发现规则(`references/factory-and-discovery.md`);
3. **`run_standalone_app` 实机端到端**:从 hub 起、回 hub 终;验收 = 编排目标达成(每个 op 依次跑过、分支走对)+ `run_record` 状态落对(一条龙按它判跳过);
4. 要进一条龙的 app(`DEFAULT_GROUP=True`):确认出现在一条龙运行列表;app 间衔接由 hub 起止结构保证(§1.2)。

**mock 快测不设必做**:op 各自的测试在 op 主线 ⑥ 已落盘;app 层只在**编排复杂**(多分支 / 循环 / 条件跳转)时,按「测试只覆盖核心」判据补锁串联结构(fixture 重放整个 app 流程)。

## 4. 修改与调试(先分诊,再动手)

### 4.1 分诊:症状在哪一层

| 症状层 | 去向 |
|---|---|
| 单个 op 内部(节点流转 / 识别 / 读数) | `od-dev-write-operation` §9 修改与调试 |
| 串联层(编排顺序 / 分支路由 / hub 衔接) | 本 skill:回 ① 改编排设计 → 改节点图 |
| 产品化层(config / GUI / 注册 / run-record) | 本 skill:查 ② 对应步 + reference |
| 用户反馈的运行失败(你不在场) | `od-dev-debug-automation` |

### 4.2 app 特有症状速查

| 症状 | 根因方向 | 处置 |
|---|---|---|
| app 跑完首节点即「成功」结束,后续节点全没跑 | 无边节点静默不执行(`@node_from` 串接缺失;**顺序声明 ≠ 顺序执行**) | 补边 |
| 一条龙里 app 间衔接失败 | 首 / 尾 op 没回 hub | 修编排回 hub 模式(§1.2) |
| 一条龙跳过了该 app | `run_record.is_done`(周期内已完成 / 上次状态残留) | 查 run-record(`references/run-record.md`) |
| 改了代码行为没变 | MCP server 缓存 app 实例 | 重启 server 再验 |
| app 不在可运行列表 | 发现规则失败:同目录多个 `_factory.py` / `_const.py`、`APP_ID` 重复、目录位置错 | 查注册(`references/factory-and-discovery.md`) |

## 5. 必守不变量

1. **`APP_ID` 全局唯一**(重复注册被拒);与 run-record 的 app_id 一致。
2. **同一目录一个 `_factory.py` + 一个 `_const.py`**(多个 → 该目录跳过)。
3. **factory 必须实现 `create_application`**;需要 run-record 再 `create_run_record`(不需要的 app 可不实现)。
4. **app 类继承项目的 Application 子类**(项目通常有特化子类,带默认 `op_to_enter_game`),构造传 `app_id` + `run_record`。
5. **改 app 代码后重启 MCP server 生效**(框架缓存 app 实例)。

> app 的节点图与 round 调用同守 `od-dev-write-operation` 全部规范(节点边显式串接 / goto 独占节点 / wait 显式声明 / 图完整性三查),本 skill 不复述。

## 6. 边界(这些去别的 skill)

- 写 / 改 / 调试**单个 Operation** → `od-dev-write-operation`(app 复用它)
- **从零做新玩法全程** → `od-dev-gameplay-automation`(它阶段 6 app 产品化引用本 skill)
- 画面建档 / screen_info area → `od-dev-screen-onboarding`
- 用户反馈的运行失败排查 → `od-dev-debug-automation`

## 7. 写完自检

- [ ] op 清单里的 op 各自 `run_operation` 验证过(自底向上,没先搭壳)?
- [ ] 非纯顺序编排向用户过过设计(op 清单 + hub 骨架 + 分支语义)?
- [ ] `APP_ID` 全局唯一 + 与 run-record app_id 一致;同一目录一个 `_factory.py` + 一个 `_const.py`?
- [ ] factory 实现 `create_application`(需 record 再 `create_run_record`)?app 继承项目的 Application 子类、传 `app_id`(+ 需要时 `run_record`)?
- [ ] 节点图:一个 `is_start_node`;**每个节点都有 `@node_from` 串接**(缺边静默跳过,症状 = 跑完首节点即结束)?**首 op 回 hub、尾 op 回 hub**?
- [ ] 改代码后重启了 MCP server;`run_standalone_app` 实机从 hub 跑回 hub、`run_record` 状态落对?
- [ ] 外部(GUI / 其他 app)要直接访问 app config / record?→ 才需 Context 接线(factory 通常够,默认不接)
