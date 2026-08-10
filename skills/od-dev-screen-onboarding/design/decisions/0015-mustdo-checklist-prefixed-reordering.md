# 0015. 开头 must-do checklist 前置 + 顺序重排(穷举交互前置 / 进度节点 chain 进主流程)

- **Status**: accepted
- **Date**: 2026-08-10

## Context

`od-dev-writing-skills` [ADR-0010](../../../../od-dev-writing-skills/design/decisions/0010-procedural-skill-mustdo-checklist.md) 落地了通用规范:**流程类 skill 开头必须带一条 ordered must-do checklist**(form-to-failure「漏元素 → 结构式 REQUIRED 槽位」)。本 skill 是该规范的 instance 应用 —— 事故就是 ADR-0010 Context 记的那次:建一个新画面时**漏做三步**(穷举交互验证 / id_mark 测试 / 进度文件更新),这三步 skill 里**都有**(§4 / §6 末 / 进度模板脚注),但**埋在散文判据里、顺序靠后**,不是开头可勾的必做序列 → 读着读着跳了。用户原话「我感觉经常漏」。

本 ADR 不重复 ADR-0010 的 general 决策(为何要 checklist),只记**本 skill 特有的三处顺序 / 结构决策**(checklist 通用规范没覆盖、且非显然、有被否备选的部分):

1. **穷举交互验证从 §4(缺口分析)前置到建档(doc / screen_info 定稿)之前**。
2. **进度节点操作(第 1 步认领 + 第 9 步标完成)夹住整个 checklist**,而非留在末尾「进度模板」脚注。
3. **第 1 步显式 chain 到 od-dev-progress-tracking skill**(同 §5 chain od-dev-ui-region-detect 的模式)。

## Decision Drivers

- **防漏步**(用户「经常漏」已证实,见 ADR-0010):这三步都因「埋深 / 顺序靠后」被漏过,必须进主流程。
- **先摸清再定稿,避免返工**:穷举交互前置 = 先把「全部可交互元素 + 各自行为」摸清,再写 doc / 定 screen_info。否则基于不完整认知定稿,建完发现漏元素 / 漏行为要返工。
- **深潜建档只加载本 skill,不会想起 progress-tracking**(用户洞察):任务执行时上下文只注入被调用的 skill;建档深潜不会自动加载 progress-tracking → 进度节点漏记。故 checklist 第 1 步显式 route 过去,不靠 agent 记起(与 §5 「坐标怎么找 → 见 od-dev-ui-region-detect skill」同一 chain 模式:某步骤的子纪律在另一 skill → 该步骤显式 route)。

## Considered Options

**穷举交互验证的位置**:
1. **前置到建档前(选中)**:先摸清全部元素行为再定稿 doc / screen_info,避免返工。
2. **留 §4(建档之后)**(否):原结构 —— 建完档才发现漏元素 / 行为认知不全要回改 doc,且 §4 混在「缺口分析」散文里被跳过(已证实漏)。顺序反了。
3. **只在卡住协议里(否)**:卡住协议是「状态不清动态画面」的强制探索;常规建档也该穷举交互,不止卡住时。

**进度节点的位置**:
1. **第 1 步(认领)+ 第 9 步(标完成)夹住 checklist(选中)**:进度节点贯穿始终,夹住主流程防漏记;第 1 步显式 chain progress-tracking 解决「深潜不加载它」问题。
2. **留末尾「进度模板」脚注(否)**:原结构 —— 已证实漏(脚注不突出);且不解决「想不到去 invoke progress-tracking」问题。
3. **不进 checklist,靠 progress-tracking skill 自己触发(否)**:深潜建档只加载 screen-onboarding,不会触发 progress-tracking;两 skill 各管一段,screen-onboarding 不 route 过去就断链。

**id_mark 测试的位置**:
1. **进 checklist 第 8 步(选中)**:归档后强制验,失败不算完。
2. **留 §6 末脚注(否)**:已证实漏。

## Decision

SKILL.md 开头(frontmatter 后、`## 何时该建档` 前)插入「## 必做流程」节:9 步 ordered must-do checklist(编号 + `☐` + 祈使动作 + 一行判据 + 链回 § + 标「必做」),开头标「没做完这 9 步不算建档完成」。

9 步顺序(关键 = 三处重排):
1. 进度节点第一件 → 见 od-dev-progress-tracking skill(建/认领 + 标进行中)。
2. `analyze_screen`(§1)。
3. 视觉大模型看截图(§2)。
4. **穷举交互验证(前置)**—— §4 / 卡住画面协议。
5. 建 screen_info(SCREEN 层 entry + id_mark / AREA 层增量)—— §3.5。
6. 建 screen doc(只写画面事实)—— §3。
7. 归档 fixture —— §6。
8. 跑 id_mark 准确性测试过 —— §6 末。
9. 进度节点收尾(标 `已过`)。

**§1-§6 降级为 reference**:checklist 链回 §X,正文判据 / 踩坑 / 方法论**不删、不搬进 checklist**(主流程只放可勾动作 + 一行判据)。§ 编号不变,保持链回稳定。

## Consequences

- **正向**:9 步可勾有序 + 「缺一不可」显式 + 进度节点夹住全程 → 防 agent 读长散文漏步(穷举交互 / id_mark 测试 / 进度记录这三步不再靠自觉);穷举交互前置避免建完档返工;显式 chain progress-tracking 解决深潜断链。
- **负向**:checklist 与 §1-§6 / 「收尾判据」/「进度模板」节有内容重叠 —— 靠「主流程只放动作 + 一行判据,详判据 / 踩坑留 §」约束(checklist crisp,细节在后);改 § 步骤要同步 checklist 对应项(双向链维护成本)。
- **边界**:checklist 是「确认该建档后」的执行体;「该不该建档」(主动 / 被动触发 + 建档/快修硬判据)仍是前置 gate(见「何时该建档」节,不进 checklist)。重 app 多子玩法维度的建档另走「建档规模」节,本 checklist 是单画面 / 独立 app 常规流程。

## Links

- 通用规范:`od-dev-writing-skills` [ADR-0010](../../../../od-dev-writing-skills/design/decisions/0010-procedural-skill-mustdo-checklist.md)(流程类 skill 必 checklist)+ `references/writing-craft.md` §1.5 / §1.2。
- 本 skill 相关:ADR-0013(穷举交互 + 不可逆出口最后,checklist 第 4 步的详化方法论)、ADR-0012(卡住画面协议强制探索)、ADR-0010(本 skill,调试撞陌生画面触发)。
- chain 模式参照:§5 「坐标怎么找 → 见 od-dev-ui-region-detect skill」(本 ADR 第 1 步 chain progress-tracking 同模式)。
