# 0003. app 设计文档组织:记 why 不复述代码 + 总分结构 + decisions 用 ADR 式

- **Status**: accepted
- **Date**: 2026-08-11

## Context

`od-dev-write-application` 原本只讲 app 的**代码**组织(factory / config / run-record / hub 编排),没讲 app 的**设计文档**怎么组织。实操中复杂 app(如 SR 货币战争)的设计文档散乱:决策日志用 append-only D-NN 大杂烩(混 bug 修 + 诊断 + 决策)、bot 流程散在代码 + strategy、decisions 和游戏玩法文档(docs/game/)混放。

问题:

1. **文档复述代码 / 不复述边界不清**:没原则说「文档记什么、不记什么」→ 要么不写(维护者 / 续开发 AI 不懂设计 why)、要么复述代码(双源漂移)。
2. **decisions 用 append-only D-NN 大杂烩**:一个文件按时间堆,混 bug 修 + 实跑诊断 + 架构决策,粒度杂 → 难查、难维护、bug 修不该算决策。
3. **设计文档和游戏玩法文档(docs/game/)混放**:自动化实现 why 和游戏事实混 → 漂移源混(代码改 vs 游戏版本改)、不懂代码的人读不懂 docs/game/。

用户原则(2026-08-11):app 设计文档该有组织规范;复杂 app 是总分结构;decisions 用 ADR 式(有就写没就不写);流程文本描述不用 Mermaid;踩坑分流(触发选型的进 ADR,纯实现进 commit)。

## Decision Drivers

- **防双源**:文档记 why 不复述代码(行为在代码;why 在文档)。
- **可查可维护**:decisions 用 ADR(一个决策一个文件 + INDEX + Status)比 append-only 大杂烩更易查;有决策才写不强制。
- **总分适配复杂度**:简单 app 单 README,复杂 app 总分(README 总览 + 分文档),不为拆而拆。
- **和游戏玩法文档分界**:app 设计(代码改才改,受众懂代码)vs 游戏玩法(游戏版本改才改,不懂代码能读)—— 各自 docs/ 目录。

## Considered Options

1. **复述代码(文档讲怎么实现)**:双源漂移(代码改文档忘改)(否)。
2. **decisions 用 append-only D-NN 大杂烩**:粒度杂、bug 修混入、难查(否)。
3. **文档记 why + 总分结构 + decisions ADR 式(选中)**:防双源、可查、适配复杂度。
4. **流程用 Mermaid 图**:语法负担 + 渲染依赖,文本描述够(否,用文本)。
5. **踩坑单独立文档类**:没必要,分流到 ADR(触发选型)或 commit(纯实现)即可(否)。

## Decision

选 3(+ 4 用文本 + 5 踩坑分流)。新增 `references/app-design-doc.md` 讲 app 设计文档组织:

- **核心原则**:文档记 why + 代码不直接表达的(架构 overview / 配置语义 / 流程概述),不复述代码。受众 = 懂代码的维护者 / 续开发 AI。
- **decisions 用 ADR 式**:`decisions/` 目录一个决策一个文件 + INDEX + Status,有就写没就不写。踩坑触发选型 / 架构决策的进 ADR;纯实现 bug 修进 commit / insights(不进 ADR);踩坑不单独立类。
- **总分组织**:简单 app 单 README;复杂 app 总分(README 总览 + `decisions/` + architecture/flow/config 按需拆 + `strategy/` 玩法 app 才有[指针 gameplay-automation])。拆判据:内容量大 / 独立更新 / 独立子系统。
- **流程用文本描述**(节点链 / 分支 / 循环 + 指向代码),不用 Mermaid。
- **落点 `docs/develop/<app>/`**,与 `docs/game/<玩法>/`(游戏玩法)分开。

SKILL.md 加「设计文档组织(复杂 app 才需要)」节指针到本 reference。

## Consequences

- **正向**:复杂 app 设计 why 有处记、可查、不漂移;decisions ADR 式干净(只记决策,bug 修进 commit);和游戏玩法文档分界清(各自 docs/ 目录、各自漂移源)。
- **负向**:现有复杂 app(如 CW)的设计文档(decisions append-only D-NN / 散文件)需按本规范重整 —— 这是各项目侧整理(本 ADR 只立规范)。
- **边界**:本 skill 讲通用 app 设计文档;玩法 app 的策略层文档(strategy/)方法论归 gameplay-automation,本 skill 只占位 + 指针。

## Links

- `references/app-design-doc.md`(方法论本体)+ SKILL.md「设计文档组织」节。
- `od-dev-gameplay-automation` gameplay-recording(`docs/game/` 游戏玩法文档,对称)+ SKILL.md「策略」节(strategy/ 方法论)。
- ADR-0008(gameplay-automation):docs/game/ 只放游戏玩法、自动化归 docs/develop/(本 ADR 是其 docs/develop/ 侧的落地)。
