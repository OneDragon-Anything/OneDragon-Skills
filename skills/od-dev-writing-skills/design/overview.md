# od-dev-writing-skills · 设计概览(what + why)

## 为什么做

项目 skill 部署到不确定的智能体环境,需要项目特定的自包含 / 落点 / 风格规范;不固化则每次写 skill 易踩红线。做成 skill 而非 docs:skill 触发时自动注入执行上下文(主动),docs 要记得翻(被动)。

## 现行结构(2026-12 推倒重写)

SKILL.md 七节主流程,细则全内联:

1. **先对齐**(需求确认:四问 / 对话提取 / 该不该建——源 Anthropic skill-creator 的 Capture Intent + Interview);
2. **产出物形态**(目录树含 scripts / assets / evals + 加载语义 + 拆分判据 + 章节序号 + 长文件目录);
3. **SKILL.md 怎么写**(3.1 frontmatter 触发器工程 / 3.2 结构层 / 3.3 句子层 / 3.4 gotchas·计划先行);
4. **内容边界**(方法可泛化细节可具体 / 数值归属 / 引用三分 + 接口名两问 + 防过时四档 + 引用清偿);
5. **design 档案**(why 三层归宿 / overview 最小清单 / ADR 提议判据含伪 ADR 反面清单);
6. **测试验证**(单轮定性实测 + 两类制度 + RCA + evals 留档);
7. **总装**(7 步 checklist + 第 8 步自验证 + 完工自检 8 项含清晰度扫描)。

references 只留「特定环节配套物」:`design-docs.md`(ADR 配套格式)、`skill-testing.md`(测试细则)、`skill-feedback.md`(反馈格式)。

## 为什么推倒重写(决策记录)

- 旧结构 = 「SKILL.md 4 硬规范 + writing-craft 213 行细则库」:两者是「摘要-全文」双源(必漂移),且 writing-craft 是 18 个主题按加入时间堆积(五个维度混杂,§1.1 主次颠倒 / §1.9 杂项抽屉 / §1.13 按到货批次打包)。
- 新原则:**细则按消费时机归位**——动笔必需的归位内联 SKILL.md,特定环节配套物(格式模板 / 测试细则)才留 references。与 Anthropic skill-creator 一致(主流程全内联,references 放 schemas 类配套物);官方无「进阶技艺库」形态,该定位经用户质询后否定。
- 「4 硬规范」框架溶解进 §3/§4/§5,自检职能由 §7 完工清单承接(清单比抽象规范好过)。

## 立场与裁定台账(维护者视角)

- **写法来源与血缘**:本 skill 以 `superpowers:writing-skills` 为基底做的**特殊改进适配**——初版整合其通用核心(frontmatter / 触发词覆盖 / token 效率 / 结构模板 / form-to-failure / 何时建),适配点 = 本仓特有约束(自包含三分引用 / design+ADR 维护者档案 / 一条龙生态落点)+ 刻意偏离其 Iron Law(RED 制度,见下条);2026-12 推倒重写时再整合 Anthropic 官方实践(Capture Intent / degrees of freedom / 高价值形态 / 部分读取新知)。全部内容内联,无外引依赖。
- **Iron Law 不采纳**(每 skill 必先 RED baseline):按两类分法,方法论覆盖型 RED 可省(单一 baseline 外部效度不足 / 模型异构);GREEN 实测两类都不可省。
- **测试制度**:单轮子 agent 定性实测,不做量化基建(skill 低频修改,养不起);测试场景(任务 + 负例问法)留档 `evals/TESTS.md` 重测复用;挂载验证正负例双查;「eval-first」顺序不翻转——§1 需求确认已吸收其精神(知情裁定)。
- **引用深度**:官方「one level deep」不立规。早期理由(消费环境可定向读取)被独立评审证伪(与自采纳的部分读取机制矛盾);拆迁后 references 只指 SKILL.md(它总是全文加载,无部分读取风险),矛盾由结构消除。
- **约束校准**:采纳 degrees of freedom 的任务定档 + 默认偏松倾向;不引入三档术语(本仓纯指令型 skill 用不上中自由档);不做按模型调优(无多模型测试资源;跨模型可用性由「不为特定模型调档 + RCA 过滤」**预判**——此为未验证假设,视实际跨模型使用修正)。
- **frontmatter**:可选字段 compatibility 硬依赖才写;license / metadata / allowed-tools 不用(内部仓无分发场景,author / version 归 git,跨工具不绑 allowed-tools);skills-ref 校验器未引入——理由修正:本仓消费走 `npx skills add` 标准安装器,frontmatter 不合规会被整条跳过,故提交前按 §3.1 / §7 完工自检人工核对兜底(不上校验器)。
- **独立评审 1(2026-12,对标官方,20 项)**:报告存 [`reviews/2026-12-review-1-official-alignment.md`](reviews/2026-12-review-1-official-alignment.md)。M2(superpowers 兄弟外路由 + 生态限定词)用户裁定不处理;M1 pushy 句做了最小补(不含 superpowers);其余全部采纳或随拆迁自动解决(H1 嵌套引用 / M6 4 硬规范死标记 / M9 口径漂移 / L1 / L5 / L6 / L8)。
- **独立评审 2(2026-12,大改终态复审,20 项)**:报告存 [`reviews/2026-12-review-2-final-state.md`](reviews/2026-12-review-2-final-state.md)。全部处置:H1(GREEN 术语链断裂 / 口径冲突→§6 补定义、testing 改引用式)、H2(description 漏测试场景→已补)、H3(仓内兄弟 agent-instructions 单向路由→已回指;与 superpowers 豁免不同性质:仓内互指 + 对方已路由过来,如不应加可撤)、H4(references 编号违反「从 1 起」+ 自检失实→两文件重编号、deciding-a-fix 引用清偿)、M1-M9(双源消除 / 缩写补解释 / 一条龙本仓定义 / 白话化 / README 重写 / 评审存档)、L1-L7 全部小修。
- **checklist 触发**:内容直判(含「有顺序、漏任一步不算完成」的必做序列 → 必须 checklist;跳过条件写进步骤内),删「流程类 / 非流程类」中间标签;GREEN「谁跑」条款维持原文(被委派子 agent 按规范字面自行编排 utility test 属合法解读,实测记录支持)。
- **例子政策**:旧「写方法论,不写具体例子」修正为「方法可泛化,细节可具体」——指令本体的具体(步骤 / 命令 / 模板 / 脚本)直接写,叙事佐证归 design 动机段;仓库 AGENTS.md 已同步口径。

## 落点

- 根 `skills/`(跨工具源);`od-dev-` 前缀;junction 挂载(见仓库 AGENTS.md)。
- 自检(扫描范围 = SKILL.md + references/*.md + design):章节序号全部从 1 起 ✓(评审 2 修正后重扫);references 三文件均 <100 行,无需目录 ✓;术语统一 agent / 合理化 ✓。

## 状态

- **draft(GREEN-pending)**:推倒重写 + 独立评审修复 + references 拆迁完成;待按 §6 起干净子 agent 实测一轮(场景将记入 `evals/TESTS.md`)。
