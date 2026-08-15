---
name: od-dev-writing-agent-instructions
description: 当要创建 / 编辑 / 审查 AI 编码 agent 的 always-on 入口文件(AGENTS.md / CLAUDE.md 类,含个人本地层如 AGENTS.local.md / CLAUDE.local.md),或排查「指令没被遵循 / 上下文臃肿 / 入口文件该放什么」时用。写 / 改 / 审查入口文件、决定一条指令放哪层(always-on / 个人本地 / skill / hook)、入口文件瘦身,都用本 skill —— 即使只加一行也别跳过。英文:author or review AGENTS.md / CLAUDE.md agent instruction files, decide instruction layering, slim a bloated context file。不触发:写 skill 本身(见 od-dev-writing-skills);写项目文档。
---

# 编写 agent 入口文件(AGENTS.md / CLAUDE.md 类 always-on 指令)

入口文件 = 每个会话开头**无条件全文注入**的指令文件。与 skill(按需触发加载)是两类 artifact:**入口文件 token 每 token 都是常驻成本,且塞得越满指令越被忽略(context rot)** —— 所以两者的核心动作相反:skill 鼓励展开写全,入口文件残酷砍。写 skill 的方法论见 `od-dev-writing-skills`(判据大量互通,别双源);本 skill 只管 always-on 入口文件这一层。

## 必做 checklist(编辑入口文件时按序过,缺一不可)

> 没做完这 5 步不算改完。判据 / 细则在后文对应 §,此处只放可勾动作。

1. ☐ **判层**:这条指令该进 always-on 吗?过 §2 删了会出错自检 + 四档分层;多步流程 → skill;强制动作 → hook。放错的先归位再编辑。(必做)
2. ☐ **判层内归属(共享 vs 个人本地)**:团队人人适用 → 共享层(AGENTS.md);个人偏好 / 本机环境 → 个人本地层(.local,不入库)。判据见 §3。(必做)
3. ☐ **写指令本体**:祈使句 + 判据;守干净读者原则(默认读者 = 无会话历史的干净智能体,细则见 od-dev-writing-skills writing-craft §1.9)。(必做)
4. ☐ **纯度自检**:无元信息(维护注释 / TODO / 变更说明)、无 README 复制、无双源(与 docs / skill 重复的内容改指针);单文件 < ~200 行。(必做)
5. ☐ **改动流程合规**:共享层改动先经 owner 确认;大改先分支 / 临时文件试验跑会话观察,确认后再进共享层。(必做)

## §1 格式与变体地图(标准只有一个,变体很多)

- **开放标准 AGENTS.md**:仓库根 markdown,60k+ 项目采用,Codex / Jules / Factory / Aider / goose / opencode / Zed / Warp / VS Code / Devin / Junie 等通读;"README for agents" —— 放构建命令 / 约定 / agent 需要的项目上下文。
- **CLAUDE.md 变体**:Claude Code 读 `CLAUDE.md`,支持 `@path` import(唯一有真 import 的工具);别的工具把 `@xxx` 当纯文本。
- **目录约定**:全局(用户主目录)+ 项目根 + 子目录(部分工具支持嵌套逐层拼接)。放哪层 = 作用域多大。
- **个人本地层**:`AGENTS.local.md` / `CLAUDE.local.md` / 工具忽略名单(.gitignore),不入库,见 §3。
- 各工具 rules 机制差异(import 支持 / 目录自动加载)别背,查项目或公共仓的「AI 工具 rules 机制对比」类文档;**跨工具默认姿势:单一 AGENTS.md 源 + 各工具入口引入 / 回退,不复制正文**。

## §2 内容取舍:砍是默认,留是例外

- **删了会出错吗(否决式自检)**:默认砍;只有「删了这条,agent 会在本项目犯实质错误」才留。整洁不是理由,防错才是。
- **四档分层**(指令该放哪,按序判):
  1. **always-on 入口文件**:每个会话都需要的硬约束 / 项目关键事实(构建命令 / 命令禁区 / 架构落点)。
  2. **skill**:多步流程 / 特定任务方法论 —— 触发时才加载,不占常驻 token。
  3. **hook**:要**强制**的动作(漏了就出事)—— 入口文件是 advisory(context,不是 enforced configuration),agent 可能不遵循;硬拦走工具的 hook 机制(如 PreToolUse)。
  4. **doc(按需引用)**:背景 / 细则 / why —— 入口文件只留一行指针,agent 需要时自己读。
- **何时加**(官方判据,别抢跑):同样错误犯第二次 / code review 抓到 agent 本该知道的 / 同一句纠正打了第二遍 / 新成员也需要 —— 才加;第一次纠正优先走对话,观察是否复发。
- **何时砍**:逐条删了会出错自检;模型已稳定做对的 → 删;过时的(机制改了 / 工具升级了)→ 删或更新。**当代码 review**:定期 prune,出问题时先查入口文件(它是常驻变量)。

## §3 两层区分:共享层 vs 个人本地层(.local)

同一份 always-on 机制里有两层,**判据 = 谁需要它**:

| | 共享层(AGENTS.md) | 个人本地层(AGENTS.local.md / CLAUDE.local.md) |
|---|---|---|
| 入库 | ✅ 提交,团队共享 | ❌ 不入库(gitignore / 工具忽略名单) |
| 该放 | 团队人人适用的约束:构建命令 / 代码规范 / 架构落点 / 提交流程 | 个人偏好(汇报风格 / 语言习惯)、本机环境(特定路径 / 账号 / 并发限制)、个人试验中的约束 |
| 不该放 | 任何「只有我这样工作」的内容 | 团队约定(放了别人看不到 = 事实上不存在) |
| 改动 | 先经 owner 确认,不静默重写 | 个人随意改 |
| 关系 | **源**;个人层不复制正文,只补差异 | 补充,不双源;共享层已有的别复述 |

- **误放症状**:团队其他人按你的 .local 内容协作时会踩坑(他们看不到);或你的个人偏好污染团队(进共享层)。
- **单源纪律**:同一条信息只活在一层;迁移时写进新层**删旧层**(判据:这条该团队人人见吗?是 → 共享;否 → .local)。
- **个人试验场警告**:.local 不入库 = 无法承载「试验 → 晋升回共享层」的团队流程;要试验的共享改动走分支 / 临时文件,不走 .local。

## §4 反模式(高频翻车)

- **臃肿堆积**:把 doc / README 内容复制进入口文件("反正 agent 看得到")—— context rot,越全越没人读。
- **元信息混入**:维护注释 / TODO / 变更记录 / 试验状态写进正文 —— 入口文件只放给 agent 的指令,元信息归 docs / commit message / git history。
- **双源**:同一约束既在入口文件又在 docs / skill 复述 —— 必漂移;入口文件留指针(一行 + 位置),实体在单一源。
- **叙事 / 会话残留**:「我们之前 / 这次开发中」类措辞 —— 违反干净读者原则(见 od-dev-writing-skills writing-craft §1.9)。
- **advice 当 enforcement**:写「绝不许 X」指望拦住 —— advisory 不保证遵循;硬拦走 hook / permissions。
- **永不清理**:只加不减 —— 入口文件是常驻变量,定期 review prune 与代码同级。

## 协作 skill

- 写 / 改 / 审查 **skill**(按需触发那类)→ `od-dev-writing-skills`(4 硬规范 / 干净读者原则 §1.9 / skill 测试方法论)。
- 项目文档(docs/)组织 → 项目自己的文档规范。
- 入口文件 vs skill vs hook 的分层判据本文 §2 已含;工具机制细节查项目「AI 工具 rules 机制对比」类文档。
