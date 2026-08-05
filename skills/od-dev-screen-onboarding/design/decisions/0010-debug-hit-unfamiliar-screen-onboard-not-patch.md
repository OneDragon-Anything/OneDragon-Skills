# 0010. 调试撞陌生画面 = 建档信号不是快修信号(description 补被动触发 + 建档/快修硬判据)

- **Status**: accepted
- **Date**: 2026-08-05

## Context

ADR-0001 / 0009 等把方法论锚定在「**主动**拿到一张待建档截图」—— SKILL.md 的 `description` 与正文触发点都是「主动 onboard 一个已知要建的画面」。实战暴露**对称的另一面:更常见的被动场景没被当触发点**:

SR 实战(2026-08-05,货币战争自动化):op 的随机事件(encounter)分发逻辑卡死在一个事件画面上。操作者在「修 handler 解锁」framing 下(且有 loop 紧迫感),**跳过建档、直接猜 ESC / 返回备战 等逃生机制 + 套兜底结构**,被用户点破「算不算你不知道这画面的交互?为什么不去探索建档?」才反应过来。

根因不是「不懂方法论」(本 skill 的「open prompt 探索」「三工具交叉」「未知画面先建档」都写了),而是**「该用它」的信号没被「调试撞陌生画面」这个处境激活** —— `description` / 触发点没覆盖这个被动场景,智能体在「修 bug」framing 下默认跳到猜修,不触发本 skill。

这是**通用方法论 gap**(任何项目调试 op 卡在陌生画面都该先建档),非货币战争 / 模型 / 环境特异。判据是方法论(怎么识别「该建档了」),非具体游戏例子。

注:同命根因也见于「loop 紧迫感 / 自主快修 framing 压过方法论」—— 但那是执行层(智能体自律),非 skill 缺陷;本 ADR 只治 skill 的触发盲区(`description` + 判据)。

## Decision Drivers

- **触发点要覆盖被动场景**:skill 靠 `description` 匹配激活;被动场景不进 `description` → 智能体在 debug framing 下不触发本 skill。
- **把「不该猜」从隐含变显式硬规则**:方法论已写「未知画面先建档」,但没给「调试中怎么判断该停下来建档 vs 继续改」的操作判据 → 智能体缺可机读的刹车点。
- **单源建档方法论**:建档方法论只在本 skill;debug 类 skill 触发「排查 op」时若根因是「op 走到陌生画面」应**转本 skill**,不双写。

## Considered Options

1. **只改 `description` 补被动触发**:智能体撞陌生画面时会触发本 skill,但缺「何时算认知不完整、必须停下建档」的判据 → 仍可能边建边猜。
2. **只加正文判据不改 `description`**:正文有了判据,但 `description` 没覆盖被动触发 → 撞到时根本不激活本 skill,判据看不到。
3. **`description` 补被动触发 + 正文加建档/快修硬判据(选中)**:激活面(被动触发进 `description`)+ 操作刹车点(硬判据)都补,对称。
4. **在 debug 类 skill 里加「撞陌生画面 → 转建档」交叉引用**:会冗余双写;且 debug 类 skill 在消费方项目常是项目专属(非公共 `od-dev-*`),改它跨仓。单源建档方法论在本 skill,靠 `description` 补被动触发就能让智能体在 debug 撞陌生画面时自然转过来 —— cross-ref 作可选增强,不强加(避免双写 + 跨仓依赖)。

## Decision

选 3(+ 视情况选 4 作可选增强,交消费方 harness 决定)。

写进 SKILL.md:

1. **`description` 补被动触发**:与「拿到待建档截图」主动触发并列,加「调试 / 排查 op 卡在不完全认识的画面 / 子屏 / 交互上时用」。SKILL.md 正文不重复 `description`。
2. **正文新增「何时该建档(主动 + 被动两种触发)」节 + 建档/快修硬判据**:你能说出当前画面全部可交互元素 + 各自点后跳哪?不能 / 只能猜 → 先建档(`analyze_screen` + 视觉大模型 open + click 逐元素验证),别在不完整画面认知上猜 escape / 套兜底 / 改 op。

判据复用既有方法论(§1 analyze / §2 open prompt 探索 / §信息源三层对齐),不引入新工具。「能」的判定(`screen_info` `area_list` 已覆盖 + op 代码流转已读清)即 §信息源「对齐判据」的重述 —— 把它从建档时的对齐检查,重述成 debug 时的刹车点。

## Consequences

- **正向**:被动场景被 `description` 激活面覆盖;「该建档了」有可机读刹车点(硬判据),防 debug framing 下猜修。
- **负向**:`description` 变长(多一个触发分支);硬判据「全部可交互元素 + 各自点后跳哪」在元素多的画面执行成本不低,但「说不清」本身就是认知不完整的信号,值得停。
- **边界**:判据的「继续改 op」前提是画面认知已完整(`screen_info` 已覆盖 + 代码流转已读清);若只是 op 有已知占位短路(如某 handler 直返「未开启」),标「待重写」不强制建档(沿用 §信息源「版本迁移核对」的占位短路处理)。
- **未做**:debug 类 skill 的 cross-ref —— 交消费方 harness 判断(若该 debug skill 是项目专属 `sr-od-dev-*`,改它归该仓;公共本 skill 单源足够)。单源 + `description` 补被动触发已让 debug 撞陌生画面时自然转本 skill,cross-ref 仅锦上添花。

## Links

- SKILL.md `description`(被动触发)+ §「何时该建档(主动 + 被动两种触发)」+ 「建档 vs 快修 判据」。
- 相关:[ADR-0001](0001-five-step-flow.md)(五步流,主动触发面;本 ADR 补其被动对称面)、[ADR-0009](0009-open-prompt-cross-tool-exhaustive.md)(探索未知画面怎么探索;本 ADR 补其触发面:debugging 撞陌生画面也要进探索)、[ADR-0003](0003-three-information-sources.md)(信息源三层 —— 判据「画面认知完整」靠它)。
