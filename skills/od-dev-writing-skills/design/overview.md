# od-dev-writing-skills · 设计概览(what)

## 为什么做
项目 skill 部署到不确定的智能体环境(不像 superpowers 自带 plugin、运行时文件环境确定),需要项目特定的自包含 / 落点 / 风格规范。`superpowers:writing-skills` 通用且偏严格 TDD,不含本项目约束(自包含 / 落点 / design-ADR 等);其核心写法**已整合**进本 skill,不外引依赖。不固化项目规范则每次写 skill 易踩红线。

**为什么是 skill 而非 docs**:skill 触发时自动注入执行上下文(主动);docs 要记得翻(被动)。写 skill 的规范本身也该在「要写 skill 时」被主动注入,故做成 skill。

## 4 条硬规范(是什么 + 为什么)
1. **必须有 design/ 文件夹,design 与 ADR 分开;ADR 仅经用户命令创建**(迁移自旧「单 design.md」)。why:design(what)与决策(why)读者 / 生命周期不同,分开防互相污染;ADR 默认不立 = 防智能体自行堆「变更日志式伪 ADR」,日常决策 why 归 overview 动机段 + commit message,用户命令才立(判据与格式见 `../references/design-docs.md` §3.2)。
2. **内容给智能体看(指令式)**:正文是祈使句 + 判据;`description` 只写触发条件(SDO 结论:description 写流程 → 智能体照 description 走、不读正文,故要 pushy 显式列触发场景防漏触发)。**流程类 skill(有固定步骤序的)开头必须带 ordered must-do checklist** —— why:长散文里 must-do 被「判据 / 踩坑」稀释而漏做,结构式 checklist 才防漏(form 见 `../references/writing-craft.md` §1.5)。
3. **自包含(分场景)+ 框架地基级接口名可写进 SKILL.md**。why:引用闭包外的状态在别人机器 / CI / clean checkout 上不存在(skill 是共享 artifact);曾有 CodeRabbit 把外引判成坏链接的误报 incident,故硬门 = target 必须在已提交仓库里。
4. **写方法论,不写具体例子**。why:具体例子会以偏概全 —— 智能体把例子的偶然细节当成必然规则,套到不匹配的新场景。

## 落点
- 根 `skills/`(跨工具源)而非 `.claude/skills/`(工具特定):项目 skill 面向多个 skills 感知工具。
- `od-dev-` 前缀:开发流程类,与工具自带 skill 区分。
- junction 而非 symlink:Windows symlink 需特权,junction 免管理员;junction 不提交(`.claude/` gitignore),每人本地建。
- **不外引写法依赖**:通用写法已整合进 `../references/writing-craft.md`,不 defer 给 superpowers:writing-skills(严格 TDD 立场与本 skill「两类 skill」冲突,见下)。

## 写法来源(已整合 superpowers 核心,无依赖)
- **通用写法**(frontmatter / SDO / token / 结构 / form-to-failure / 例子 / 何时建):已从 superpowers:writing-skills 整合进 [`../references/writing-craft.md`](../references/writing-craft.md),本 skill **不再 defer / 依赖**它。
- **刻意偏离**:superpowers 的 Iron Law(每个 skill 必先 RED baseline)→ 本 skill 弱化为「两类 skill」(方法论覆盖型 RED 可省)。理由 = 外部效度 / 团队工具模型异构(见 `../references/writing-craft.md` §3.1)。
- **本 skill 叠加**(superpowers 没有):design/ + ADR(规范 1)、自包含硬门 + 引用卫生(规范 3)、写法工程指南(writing-craft)。
- **两类 skill**:**纠正型**(改变智能体默认错误)RED 必做;**方法论覆盖型**(整合业界方法论)RED 可省、GREEN 必做。`od-dev-deciding-a-fix` 是方法论型范例(锚定业界 RCA / Impact Analysis / Trade-off Matrix)。

## 自身一致性
本 skill 遵守自己的规范:有 `design/`(design 与 ADR 分开;ADR 仅经用户命令创建,当前无 ADR —— 决策 why 归本文件动机段与 git 历史);SKILL.md 指令式;**不引 skill 目录外的 docs 文件**,写法细则自含在 `references/`(不外引 superpowers:writing-skills);正文是规范 / 判据 / 流程,无具体项目叙事例子。
