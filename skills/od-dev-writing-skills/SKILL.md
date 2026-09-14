---
name: od-dev-writing-skills
description: 当要创建 skill、编辑/修改 skill、写 SKILL.md、用户要求编写或修改 skill 的 ADR(design/decisions/ 下的决策记录)、问 skill 带哪些文件/内容怎么写,或开发中用某 skill 发现 gap 想写规范反馈(交迭代方处理)时用。英文:create/author/edit a skill、write SKILL.md、write/edit a skill ADR (architecture decision record) when the user asks、skill structure、or write structured feedback on a skill gap。仅创建/修改 skill、用户命令的 ADR 或写其反馈时用;纯使用已有 skill 不触发。
---

# 创建/修改项目 skill

创建或改 skill 时,下面 4 条硬规范必须满足。**skill 的命名 / 放哪 / 挂载方式是所在仓库的约定**(见该仓库 AGENTS.md / setup);本 skill 只管**怎么写好一个 skill 的内容**。

## 硬规范

> **这 4 条是 skill 的不变量(invariant),不只新建时查**。每次**编辑**(哪怕只改一行)都要保持;**新增的任何引用都要过规范 3 的门**(已提交 + 稳定 / 可校验;不引 memory / gitignored)。新建 = 全套满足;编辑 = 至少不破坏 + 新增项满足。

### 1. 必须有 design/ 文件夹,design 与 ADR 分开;ADR 仅经用户命令创建
每个 skill 目录下要有 `design/` 文件夹,把**设计(what)**和**决策(why)**分成两类文件:`design/overview.md`(+ 按关注点拆的 `<concern>.md`)记「系统 / 方法论长什么样、目标、边界」;`design/decisions/NNNN-<slug>.md`(**ADR**,一决策一文件)记「为什么这么选」。不写混合的 design.md。
- **目的**:后续修改者(人或智能体)知道当初为什么这么定,避免盲目改动破坏原意。design 和 decision 读者 / 生命周期不同(前者随系统演进,后者 immutable 只 supersede)→ **分开不混写**。
- **ADR 仅经用户命令创建(默认不立)**:智能体**不得自行新建 ADR**。日常决策 why 的默认归宿 = `design/overview.md` 动机段 + commit message(考古走 git 历史)。认为某决策够格立 ADR → **向用户提议,用户明确要求才建**;用户命令建 ADR 时按 `references/design-docs.md` 的格式写。`decisions/` 目录有第一条 ADR 才建,不建空架子。
- **ADR 格式**:按 arc42 §9(Status / Context / Considered Options / Decision / Consequences;详见 `references/design-docs.md`)。
- **提议门槛(治「奢侈」)**:只对**架构级 / 难逆 / 有实质备选**的决策提议立 ADR;调参 / 笔误 / 局部重构 → commit message 即可,不必提议。**内容补录("XX 成文")/ 结构整理(拆文件挪章节)/ 规范套用(执行既有写作规范)= 变更日志,连提议都不必**(反面清单见 design-docs.md §3.2);自检问句:「半年后有人能从这条学到『为什么不能那样做』吗?」答不上=不提议。
- **边界:`design/` 全是给后续维护者的存档,不进智能体执行上下文** —— SKILL.md **不应写「见 design/...」让智能体去读它获取使用信息**(命令 / 参数 / 接口);使用信息内联 SKILL.md,或放 `references/` 等会被引用的辅助文件。design/ 只记「为什么这么设计」(决策 / 踩坑论据)。
- **细则**:目录结构 / ADR 全套模板 / 写作方法论(何时写、缩放、design vs ADR 内容归属)见 `references/design-docs.md`(锚定 arc42 + ADR/MADR 业界方法论,不自己发明)。

### 2. 内容给智能体看(指令式)
SKILL.md 是**智能体要执行的指令与判据**,不是给人读的说明文档。给"哪个"智能体:**默认读者 = 无会话历史的干净智能体**(读不到你的会话/项目当下状态,只读得到 skill 文本)—— 每句都要脱离当前会话可理解,细则(禁会话指代/禁依赖当下状态/自检法)见 `references/writing-craft.md` §1.9。
- 祈使句 + 判据(「先 X 再 Y」「若 Z 则 W」),不要叙述文档腔。
- **指令写意图,不写实现**:删掉工具名/命令智能体还能照做 → 是实现示例,删(至多括号示例);删了就不会做(细节承载项目约定)→ 是指令本体,留;术语换大白话信息不丢就换(细则见 `references/writing-craft.md` §1.12)。
- **多项内容(≥3 个并列项/步骤/枚举)用 markdown 列表逐项一行**,别长句塞顿号/嵌套①②③(细则见 `references/writing-craft.md` §1.10)。
- **指令性枚举(流程步骤/路由分诊表/检查清单)分支完备**:步骤消费的外部状态写全合法取值的处理、路由表带「未命中」去向、检查项带「不过」出口;参考性列表(知识查阅,不匹配无害)不受此条约束(细则见 `references/writing-craft.md` §1.11)。
- **流程类 skill(有固定步骤序:画面建档 / UI 区域检测 / 写 op / 调试等)开头必须带一条 ordered must-do checklist**:编号 + `☐` + 祈使动作 + 一行判据 + 标「必做」,开头再标一句「没做完这 N 步不算完成」(completion gate 前置);每条链回后文详细 §。**判据 / 踩坑 / 方法论留后文,不混进 checklist 主流程**(主流程只放可勾动作 + 一行判据)。理由:长散文里 must-do 被「判据 / 踩坑」稀释,agent 抓不住「必做哪几步、什么序、缺一不可」→ 频繁漏步;结构式 checklist 才防漏(form-to-failure「漏元素 → 结构式 REQUIRED 槽位」,见 `references/writing-craft.md` §1.5)。**非流程类(纯方法论 / 参考、无固定步骤序)不强制**。
- frontmatter 的 `description` 是**调用主触发器**(Anthropic 官方:primary mechanism):**以触发为主 + 可带一句 purpose,不写 workflow / 执行步骤**(范围关键词 —— 碰什么组件 / 接口 / 制品 / 扁平列举的动作 —— 属触发上下文,不禁)—— 否则智能体照 description 行事、不读正文。**要 pushy 防 under-trigger**(显式列场景 +「凡是 X 都用,即使没明说」;Claude 倾向漏触发)。详 `references/writing-craft.md` §1.3。
- **写法细则**(frontmatter 全规则 / 触发词覆盖 / token 效率 / 正文结构 / form-to-failure / 拆分 / 重构)见 `references/writing-craft.md`。

### 3. 自包含:分场景(独立发布 vs 项目内)
- **硬门(所有引用,不分场景)**:引用的 target 必须**在已提交的仓库里**。gitignored 内容(`.debug/` / `config/` / `.claude/` / `models` 等)、个人 local 文件、**memory**(个人本地、不跨人共享)→ **一律禁止引用** —— 引用闭包外的状态 = 在别人机器 / CI / clean checkout 上不存在(skill 是共享 artifact,不能依赖某人的私有状态)。**范围**:门管 skill **依赖**的内容(facts / helper 脚本 / 引用的 doc,**含 design/ 内**);**不管运行时操作的产物**(日志 / 截图 / 存档 —— skill 执行时生成、本不在仓库,如读 `.debug/` 日志诊断、存截图建档,这类合法)。引用「过时」风险 + 4 档应对谱(吸收 / 校验 / 运行时读 / 抽象)见 `references/design-docs.md` §引用卫生;反向义务同节 §5.3:**删除/改名被引用的实体时,全仓扫描引用点同步清偿,防死标记**。
- **可引用其它 skill**(写**完整标识符含命名空间**,如「按 superpowers:receiving-code-review 的方法」):用完整标识符,避免裸名解析不到。
- **兄弟项目模块 / skill 名(操作目标 vs 叙事示例)**:skill 指令 agent 去**读 / 用**别的 application / skill(如「找兄弟骨架:本仓库已有的同构 application / skill(写全名)」)→ **规范 3 允许**(稳定运行时资产,写全名,可留 SKILL.md);作**叙事示例**(「项目 X 里我们…」)→ **规范 4 抽象**。判据同接口名两问:删了这名 agent 还会做吗(会 = 示例 → 抽象;不会 = 指令 → 留)。
- **引用 skill 目录外的文件,分场景**:
  - **独立发布 skill**(跨项目用):**禁止**外引(发布不含,目标环境可能不存在)。知识内联进 SKILL.md 或 skill 目录内辅助文件。
  - **项目内 dev skill**(放项目 `skills/`,跟项目走、不独立发布)可引:**runtime 资产路径**(skill 要去读/写的**操作对象**:screen_info / application 源码 / docs/game 等,本项目必有、稳定)+ **skill 目录内自带工具 / 辅助文件**(自包含,随 skill 走,如归档脚本 `convert_to_webp.py`)。**不可引**:**具体代码文件 / 实现行 / 易变文档**(如某 devtools 模块 L640、「详见某 README」)—— 抽象化,不点具体位置。
  - 判据(**分场景,非「所有路径都不写」**):**「skill 要读写的稳定操作对象 / 自带工具」可引**;**「只为佐证某约定的具体代码/文档位置(易变)」抽象化**。
  - **有一类具体名可以写:框架地基级、几乎不改名的接口名**。有些 skill(debug / 排查 bug / 迁移)的指令本身就是「在本项目代码里搜某个名 / 调某个接口」,比如要搜 `@operation_node` 装饰器看节点流转、要调 `save_screenshot` 截图、要提醒画面识别工具的结论会骗你 —— 这些名是**指令的一部分**(不是顺带举例),删了智能体就不会做了;且是框架地基级接口(整个节点系统就靠 `@operation_node`,改它等于重写框架,几乎不会发生)。这类名属上面「skill 要读写的稳定操作对象」,**可以写进 SKILL.md**。判一个名能不能写,问两点:
    1. **删掉它,智能体还能照做吗?** —— 删了照样能做(名只是举例住在哪)→ 删(理由进 commit message 或 design 动机段);删了就不会做了(名 = 指令本身)→ 看第 2 点。
    2. **它会不会经常变?** —— 框架地基级、几乎不改名 → 可以写;容易变的(某测试 API、具体行号)→ 删,别写进正文。
  - **能写就写全名,别改成模糊说法**。可写进 SKILL.md 的接口名直接写完整名字(如「本项目用 `@operation_node` 装饰器声明节点流转」)—— 万一以后代码改名,全局一搜这名就发现 SKILL.md 这行也得跟着改,**改没改一目了然**。**别**反过来模糊成「节点声明装饰器」:代码改名后这种说法不报错、却已指错地方,谁都不会发现 —— 看着抽象好像更稳,其实更危险。

### 4. 写方法论,不写具体例子(限 SKILL.md 与智能体读的辅助文件)
写**方法、原则、判据**(怎么判断、怎么选),不要写「某个具体场景/项目的做法」。**具体游戏事实(键位/坐标/具体流程/机制)归 doc 不归 skill**;skill 只记方法论(分工见 doc_organization)。(注:框架接口名不归本条管 —— 那是规范 3「skill 要读写的稳定操作对象」,看规范 3 判据;本条只管具体游戏事实 / 项目例子。)
- **适用范围**:SKILL.md 正文 + skill 目录内会被智能体读取的辅助文件(这些注入智能体执行上下文)。
- **design/(含 ADR)不在此列**:它是给后续维护者的设计记录,可以有具体例子/踩坑作为决策论据。
- 理由:具体例子会以偏概全 —— 智能体把例子的偶然细节当成必然规则,套到不匹配的新场景。
- 抽象成判据:「在 X 条件下选 A,在 Y 条件下选 B」,而非「项目 P 里我们用了 A」。
- 不得不具体的,**仅限纯语法/字段名**(如 frontmatter 的 `name`+`description`、命令必填参数),给最小可用形式;「为什么选 A」「项目里遇过 X」这类划到 design/(overview 动机段;ADR 仅用户命令才有)。

## 创建/修改流程
1. **定位 + 复查过往 design**:这个 skill 管什么、不管什么。和已有 skill(`superpowers:*`、所在仓库已有的 skill)重叠的,**引用而非重复**。**编辑前,先读该 skill 的 `design/overview.md`(及相关 concern 文档)**,防改出与既有设计矛盾的。**仅当用户命令加 / 改 ADR**:先读该 skill `design/decisions/`(有则读 INDEX + 相关 ADR):① 下一个编号照 INDEX 接着排(无 ADR 则从 0001 起,防撞号);② 有无相关决策已覆盖(别重复决策 / 别改出矛盾的);③ 有无相关被否备选(别重提已否方案)。
2. **写 SKILL.md**:frontmatter(name + description,description 只写触发)+ 指令式正文(方法论)。
3. **写 design/**:`overview.md`(定位 / 边界 / 构成;决策 why 默认写进动机段)。`decisions/` ADR **仅用户命令时**才建才写(按 `references/design-docs.md` 格式),默认不动。
4. **自检 4 条硬规范**(**打开本 skill 原文逐条对照,禁凭记忆复述**——记忆会自动跳过你刚违反过的项,带着会话语境检查自己的无语境产物=盲区自洽;新建和编辑都要做)+ 通读正文确认每条指令可执行。自检第 2 条(干净读者)的具体扫描面:①**隐喻/自造复合词**(行业通用术语可用;自造词首次出现必须给定义——判例:「三池/互喂/冒泡/收账」直接进 skill,干净读者全不懂);②**会话语境词**(「今晚/我们/这次讨论定的」);③**未定义缩写**(项目批次号/内部代号在 SKILL.md 正文出现即违规)。**编辑时额外查**:① 新增的引用是否过规范 3 的门(已提交 + 不引 memory / gitignored + 稳定 / 可校验);② **改 / 加 ADR(用户命令)时,复查过该 skill 过往 ADR 了吗**(编号没撞 / 没重复已有决策 / 没改出矛盾 / 没重提已否备选;没有 ADR 则从 0001 起);③ **新增文本的语境污染**——编辑者天然带着会话语境写增量,比新建更容易夹黑话。
5. **挂载到 AI 工具读 skill 的目录**(如 Claude Code 的 `.claude/skills/`),验证 skill 可被触发。
6. 提交(见所在仓库提交流程)。

## skill 改进反馈(开发中迭代)
skill 在真实开发中会暴露 gap。开发中发现可优化点 → 写条**规范反馈**(观察 + RCA + 方法论级拟改),让迭代方据此优化。**反馈怎么写、写什么**见 `references/skill-feedback.md`;反馈的处理流程(谁改 / 怎么改 / 改哪 / 怎么验)归各消费方 harness(取决于本地有无 skill 源仓 / 挂载方式)。

## SKILL.md 写法(细则)
frontmatter(`name` 仅字母数字连字符 / `description` 只写触发条件句(如「当…时用」/「Use when…」)、**绝不总结 workflow**)/ 触发词覆盖(keyword 覆盖、命名)/ token 效率 / 正文结构 / **form-to-failure**(按失败类型选指令形态)/ 拆分(progressive disclosure)/ 编写中重构 / 例子与反模式 / 何时建 —— **细则见 `references/writing-craft.md`**(锚定 Anthropic context engineering + lost-in-the-middle + Diátaxis)。SKILL.md 保持 compact、情境细节进 references/(just-in-time)、定期重构不无脑追加。

## 两类 skill:RED 必要性不同,GREEN 始终必做
本 skill **不照搬**「写 skill = 严格 TDD、每个 skill 必须先 RED baseline」(superpowers 的 Iron Law)。按 skill 的**内容依据**分两类:
- **纠正型**:改变智能体默认会做错的行为,内容依据是"baseline 暴露的 failure" → RED(baseline)必做,再写最小纠正。
- **方法论覆盖型**:整合业界已验证的方法论成系统流程,内容依据是方法论本身 → **RED 可省**(团队工具 / 模型异构,单一 baseline 外部效度不足 —— 你本地看到的失败可能只是你模型的弱点,或别人环境的失败你根本没看到);但写完必须 GREEN 验证(跑 application 场景,确认用了 skill 的智能体决策 / 产出更系统)。

无论哪类,**GREEN 验证不可省**(方法见 `references/skill-testing.md`:方法论型 = utility test 干净工作空间 + 可交互子 agent + 你扮用户只答所问 + 观察 gap + 修 + 循环;纠正型 = pressure test);差异只在 RED 是否必须。
判断属于哪类:问"这条规范的依据,是'智能体默认会做错所以纠正',还是'业界方法论本来就该这么做'?"。前者纠正型,后者方法论型。`od-dev-deciding-a-fix` 是方法论型(锚定 RCA / Impact Analysis 等)。理由见 `references/writing-craft.md` §3.1。
