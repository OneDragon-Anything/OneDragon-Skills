# AGENTS.md

本仓库是 **OneDragon(一条龙)系列游戏自动化项目的公共开发 skill 仓库**。`skills/` 下放开发类 skill,指引 AI 编码 agent 在任何 OneDragon 框架项目(StarRail-OneDragon / ZZZ-OneDragon / …)上做开发。本文件是跨工具单一源(skill 维护的架构 + 硬约束 + 流程)。

## 这是什么

OneDragon 系列项目共用同一套框架(`one_dragon` 公共包:Operation 节点图 / screen_info / controller / YamlConfig …),开发方法论基本一致 → 开发类 skill 抽到本公共仓库,各项目引用同一套。skill 给 AI agent 看(指令 + 判据),不是给人读的说明。

## Skill 命名 / 放哪

- 统一用 `od-` 项目前缀(OneDragon 公共命名空间,防和插件 / 个人 skill 撞名)。
  - 开发类 `od-dev-`:指引 AI 在 OneDragon 项目上开发 / 配置 / 构建(例 `od-dev-write-operation`、`od-dev-writing-skills`)。
  - 使用类 `od-`:指引用 OneDragon 项目做游戏自动化。
- 放根 `skills/<name>/`(跨工具源,提交共享)。
- 各项目消费:clone 本仓库到工作区,按需把 `skills/<name>` **目录联接**(junction)进项目的 `.claude/skills/<name>`(详 `docs/setup/ai_coding.md`)。

## Skill 结构(硬规范)

```
skills/<name>/
├── SKILL.md          # 入口:agent 指令(方法论 + 判据)
├── design/
│   ├── overview.md   # 设计(what):目标 / 范围 / 边界 / 构成
│   └── decisions/    # ADR(why):NNNN-<slug>.md + INDEX.md(arc42 §9)
└── references/       # 按需:被 SKILL.md 引用的情境细节(helper / API 参考)
```

本仓 skill **按 `od-dev-writing-skills` 编写**(4 硬规范 / writing-craft / testing 细则都在它里面);下面是结构 + 4 硬规范摘要。

1. **design/ 与 ADR 分开**:`design/overview.md` 记 what,`design/decisions/NNNN-*.md` 记 why。不写混合 design.md。design/ 不进 agent 执行上下文(SKILL.md 不写「见 design/…」取使用信息)。
2. **内容给 agent 看(指令式)**:SKILL.md = 祈使句 + 判据;frontmatter `description` 只写「何时用」触发,**不总结 workflow**(否则 agent 照 description 行事、不读正文)。
3. **自包含**:引用 target 必须在**已提交仓库**里 —— 禁引 gitignored(`.debug/` / `config/` / `.claude/` / `models`)、个人 local、**memory**。框架地基级接口名(`@operation_node` / `round_by_*` / `controller` / `screen_info` …)可写全名(删了 agent 就不会做的指令);具体代码文件 / 实现行 / 易变文档 → 抽象化。
4. **写方法论,不写具体例子**:SKILL.md + agent 读的辅助文件只写方法 / 原则 / 判据;具体游戏事实(键位 / 坐标 / 流程 / 机制)归项目 doc。design/(含 ADR)可放具体例子作决策论据。

## 框架通用,游戏专属要泛化

本仓库 skill 给**所有** OneDragon 项目用 → 必须框架通用。引用具体项目的游戏模块路径(如某游戏的业务源码目录)要泛化成「项目的游戏业务模块」,不写死某游戏路径。跨项目不成立的内容不进本仓库(归该项目自己的 doc / skill)。

## 创建 / 修改 skill 流程

1. **定位**:这个 skill 管什么、不管什么;和已有 skill(`superpowers:*`、本仓库 `od-dev-*`)重叠的**引用而非重复**。
2. **写 SKILL.md**(frontmatter name+description 触发 + 指令式正文)+ **design/**(overview + ADR)。
3. **自检 4 硬规范**(逐条)+ 通读确认每条指令可执行;**编辑时额外查新增引用是否过规范 3 的门**(已提交 + 不引 memory / gitignored + 稳定 / 可校验)。
4. **junction** `skills/<name>` → 本仓库 `.claude/skills/<name>` 本地验证可触发。
5. **GREEN 验证不可省**(方法:`od-dev-writing-skills` 的 testing reference;方法论型 = clean 工作空间 utility test + 子 agent 干真活 + 观察 gap + 修 + 循环)。
6. 提交 `skills/<name>/`。

## 依赖:superpowers

本仓库 dev skill 叠加在 [superpowers](https://github.com/anthropics/superpowers) 之上(需求探索 / 写计划 / TDD / 调试 / review / 分支收尾全链路方法论),非替代。使用者需同时具备 superpowers。

## 提交流程

- 默认不主动 `git commit / push`(除非明确要求);只提交相关文件、message 聚焦。
- review 关注逻辑错误 / 运行时崩溃 / 死循环 / 资源泄漏,不为风格大改现有内容。
- skill 改动是共享的,大改先经确认。

## 深入

- skill 写作细则(4 硬规范展开 / writing-craft / testing):`od-dev-writing-skills` skill。
- AI 工具接入 / 项目如何消费本仓库:`docs/setup/ai_coding.md`。
