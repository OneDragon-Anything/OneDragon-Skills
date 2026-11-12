# AGENTS.md

本仓库是 **OneDragon(一条龙)系列游戏自动化项目的公共开发 skill 仓库**。`skills/` 下放开发类 skill,指引 AI 编码 agent 在任何 OneDragon 框架项目(StarRail-OneDragon / ZZZ-OneDragon / …)上做开发。本文件是跨工具单一源(skill 维护的架构 + 硬约束 + 流程)。

## 这是什么

OneDragon 系列项目共用同一套框架(`one_dragon` 公共包:Operation 节点图 / screen_info / controller / YamlConfig …),开发方法论基本一致 → 开发类 skill 抽到本公共仓库,各项目引用同一套。skill 给 AI agent 看(指令 + 判据),不是给人读的说明。

## Skill 命名 / 放哪

- 统一用 `od-` 项目前缀(OneDragon 公共命名空间,防和插件 / 个人 skill 撞名)。
  - 开发类 `od-dev-`:指引 AI 在 OneDragon 项目上开发 / 配置 / 构建(例 `od-dev-write-operation`、`od-dev-writing-skills`)。
  - 使用类 `od-`:指引用 OneDragon 项目做游戏自动化。
- 放根 `skills/<name>/`(跨工具源,提交共享)。**保持 flat 一层,目录名 = frontmatter `name`**:`skills/<name>/SKILL.md` 是 agent-skills 开放标准的发现结构(`npx skills add` 按此扫描安装),按类目加嵌套层 / 目录名与 name 不一致会破坏安装器兼容(细则与消费方式见 `docs/setup/ai_coding.md`)。
- 各项目消费:`npx skills add OneDragon-Anything/OneDragon-Skills`(标准 CLI);本地开发 / 维护本仓时用 junction 直接指本仓 clone(见 `docs/setup/ai_coding.md`)。

## Skill 结构(硬规范)

```
skills/<name>/
├── SKILL.md          # 入口:agent 指令(方法论 + 判据)
├── design/
│   ├── overview.md   # 设计(what):目标 / 范围 / 边界 / 构成
│   └── decisions/    # ADR(why,仅经用户命令创建,默认无):NNNN-<slug>.md + INDEX.md(arc42 §9)
└── references/       # 按需:被 SKILL.md 引用的情境细节(helper / API 参考)
```

本仓 skill **按 `od-dev-writing-skills` 编写**(七节主流程:需求对齐 → 产出物形态 → SKILL.md 写法 → 内容边界 → design 档案 → 测试验证 → 总装自检)。**完整判据与细则单一源在 `od-dev-writing-skills`**(此处不复制摘要,摘要会漂移);写 / 改 skill 时按其 §7 完工自检逐条对照。

## 框架通用,游戏专属要泛化

本仓库 skill 给**所有** OneDragon 项目用 → 必须框架通用。引用具体项目的游戏模块路径(如某游戏的业务源码目录)要泛化成「项目的游戏业务模块」,不写死某游戏路径。跨项目不成立的内容不进本仓库(归该项目自己的 doc / skill)。

## 创建 / 修改 skill 流程

写 skill 的完整流程(需求确认 / 定位 / 写 SKILL.md + design / 完工自检 / 实测 / 挂载验证)单一源在 `od-dev-writing-skills` 的 §7「创建/修改流程」,照它做;此处只列本仓特有步骤:

1. 按 `od-dev-writing-skills` 的创建/修改流程完成 skill 本体(ADR 仅经用户命令创建;仅当用户命令加 / 改 ADR 且该 skill 有 `design/decisions/` 时,先复查 INDEX 防撞号 / 重提已否)。
2. junction `skills/<name>` → 本仓里所用 AI 工具读 skill 的目录(如 `.claude/skills/<name>`,本地不入库),验证可触发。
3. 提交 `skills/<name>/`。

## 提交流程

- 默认不主动 `git commit / push`(除非明确要求);只提交相关文件、message 聚焦。
- review 关注逻辑错误 / 运行时崩溃 / 死循环 / 资源泄漏,不为风格大改现有内容。
- skill 改动是共享的,大改先经确认。

## 深入

- skill 写作细则(编写全流程 / testing):`od-dev-writing-skills` skill。
- AI 工具接入 / 项目如何消费本仓库:`docs/setup/ai_coding.md`。
