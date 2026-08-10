# 0010. 流程类 skill 开头必须 ordered must-do checklist(规范 2 强化)

- **Status**: accepted
- **Date**: 2026-08-10

## Context
用户反馈:用画面建档类 skill(`od-dev-screen-onboarding`)建一个新画面时,**漏做了三步**(穷举交互验证 / id_mark 测试 / 进度文件更新)—— 这三步 skill 里**都有**(分布在 §4 / §6 末 / 进度模板脚注),但**埋在散文判据里、顺序靠后**(穷举交互在建档之后;测试 / 进度是脚注),不是开头一条可勾的 must-do 序列 → 读着读着跳了。用户原话:「我感觉经常漏」。

根因(观察):**长散文流程类 skill 里,must-do 动作被「判据 / 踩坑 / 方法论」稀释**,agent 读完抓不住「必做哪几步、什么顺序、缺一不可」→ 频繁漏步。判据越详尽,must-do 动作越不显眼(自检观察:「判据越详尽动作越不显眼」)。

这条失败类型 = form-to-failure 表(`references/writing-craft.md` §1.5)第 3 行「漏掉本该有的元素」→ 正确形态是「结构式:模板里 REQUIRED 槽位」。ordered must-do checklist 就是这个形态对「流程类 skill」的具体化 —— 不是拍脑袋,是失败-形态匹配。

## Decision Drivers
- **防漏步**(用户「经常漏」已证实):must-do 不突出 = 结构性漏,靠 agent 自觉不可靠。
- **方法论根基**:form-to-failure「漏元素 → 结构式 REQUIRED 槽位」是业界验证的失败-形态匹配,本条是其在流程类 skill 的落地。
- **保持 4 硬规范招牌清晰**:前 4 条是无条件普适 invariant;这条有适用前提(只流程类)→ 不宜混入「普适 invariant」概念。

## Considered Options
1. **升独立「第 5 条硬规范」**(否):破坏「4 条普适 invariant」招牌;这条条件性(只流程类强制),混进普适 invariant 会稀释概念,且要连锁改多处「4 条」引用(writing-craft 顶部、SKILL.md 开头、overview 标题等)。
2. **放 writing-craft 作 guidance**(否):writing-craft 自声明「定位:guidance(强建议),非硬规范」;用户「经常漏」证明需要**硬性**约束,放 guidance 防漏力度不够。
3. **作为规范 2(指令式)的子条**(选中):逻辑归属正确 —— checklist 前置本质是「指令式」的结构化强化(把 must-do 做成最 crisp 的可勾有序序列),与「祈使句+判据」同属正文形态;保持 4 硬规范招牌不变(还是规范 2 内);条件性清楚标注(只流程类强制,非流程类不强制)。
4. **不加,靠 agent 读全文自觉**(否:已证实漏)。

## Decision
选 3:**流程类 skill(有固定步骤序的:画面建档 / UI 区域检测 / 写 op / 调试等)开头必须带一条 ordered must-do checklist**。形式(SKILL.md 规范 2 新 bullet):
- 编号 + `☐` + 祈使动作 + 一行判据 + 标「必做」;
- 开头再标一句「没做完这 N 步不算完成」(completion gate 前置);
- 每条链回后文详细 §;**判据 / 踩坑 / 方法论留后文,不混进 checklist 主流程**(主流程只放可勾动作 + 一行判据)。

**非流程类 skill(纯方法论 / 参考、无固定步骤序)不强制**(判据:skill 有无固定步骤序 —— 有固定步骤序的才适合 checklist;纯方法论 / 参考无序,强加 checklist 反而生硬)。具体事故(`od-dev-screen-onboarding` 漏三步)不进 SKILL.md 正文(守 ADR-0003 方法论不写例子),只进本 ADR 作证据。

## Consequences
- **正向**:流程类 skill 的 must-do 突出、可勾、有序、显式标「缺一不可」→ 防 agent 读长散文漏步;completion gate 前置让「没做完不算完成」显式可验。
- **负向**:流程类 skill 多维护一条开头 checklist,且要与后文 § 双向链(改后文步骤 → 同步 checklist 项);checklist 与后文判据有重复风险 —— 靠「主流程只放可勾动作 + 一行判据,详判据 / 踩坑留后文」约束(主流程 crisp,细节在后)。
- **边界**:只流程类强制;纯方法论 / 参考 skill 不强制(无固定步骤序)。判据一句话 = skill 有无固定步骤序。

## Links
- SKILL.md 规范 2(新 bullet)+ `references/writing-craft.md` §1.2(指令式 + 判据,补流程类强化)/ §1.5(form-to-failure 表第 3 行「漏元素 → 结构式」的应用)。
- ADR-0003(方法论不写例子 —— 事故细节进 ADR 不进正文);ADR-0009(同类「强化规范 2」决策,格式参照)。
- 后续:`od-dev-screen-onboarding` 按本规范重构(开头加 must-do checklist,把穷举交互 / 测试 / 进度从脚注提进主流程)是另一条 instance 反馈,待后续处理。
