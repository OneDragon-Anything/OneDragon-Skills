# 0005. 截图手动分解 op 节点,不靠跑 app/op 中途 capture

- **Status**: accepted
- **Date**: 2026-08-04(形式化;原始踩坑 2026-07-12 起)

## Context
跑 app(`run_standalone_app`)/ 跑单个 op(`run_operation`)中途 `capture` **抓不到中间态** —— op 执行快、且会**自动消费中间画面**(如确认弹窗被 op 自己点掉),sleep 完再 capture 只能看到 op 跑完的结果(如落地入口),抓不到中间弹窗。核实:`run_operation` 跑单个 op 和 `run_standalone_app` 一样自动消费中间画面。

## Decision Drivers
- **抓得到中间态**:op 自动消费中间画面,中途 capture 必错过。
- **复现可重复**:手动分解读 op 代码,按 app 的距离 / 对象复现。
- **人机协作**:边缘状态态靠用户造条件,比智能体盲操作高效。

## Considered Options
1. **跑 app/op 中途 capture**:op 快 + 自动消费中间画面 + 运行慢三重叠加 → 抓不到中间态。
2. **手动分解 op 节点 + 单步 capture**(选中):读 op 代码,每步一个 click/key_tap/drag + capture。
3. **改 op 加 capture 钩子**:改框架代码成本高,不通用。

## Decision
选 2:
- app/op 内部连续动作(传送→move→interact→drag→…→各弹窗)产生的画面,按 op 的 `@operation_node` 节点逻辑**手动分解成单步** —— 读 op 代码,每步一个 `click_game` / `key_tap` / `drag` + `capture`,逐步截图(在 op 会自动点的弹窗处**停下、手动不点、先 capture**)。跑 app / run_operation 只用于「验证流程通」或「到位」,不用于抓中间态画面。
- **手动复现 move 前,先读 app/operation 的 `@operation_node` 链**(move_w press_time?turn_to_angle?interact 哪个对象?),按 app 的距离 / 对象复现;走多了反而错过交互点(角色过头,提示消失)。
- **操作时序**:操作后等动画再 capture。关键 sleep 点:move 后等角色到位(不等紧接 interact 会失效);interact(F)长按(`press_time>0`)非短按 tap。**sleep 建议值**:click ~1s / move ~1s / interact 1-2s / esc ~0.5s / drag ~0.5s。
- **边缘状态态**:依赖「资源消耗 / 时间 / 随机」而非「导航可达」的状态态 → 标「待条件」,别硬刷。处理:① doc 标「待条件」+ 已拍的核心态先归档;② 请用户帮切(用户调游戏状态造条件);③ 后续会话条件出现时补。

> 配套(操作时序、边缘态)在 SKILL.md「截图获取」节;导航/传送副作用、失败排查是游戏事实,归项目 gameplay doc + op 代码。本 ADR 只记「手动分解、不靠中途 capture」这条核心决策。

## Consequences
- **正向**:抓得到中间态;复现按 app 代码有据;边缘态走人机协作不空跑。
- **负向**:手动分解读 op 代码成本高(必要时);依赖用户帮切(非纯自动)。
- **边界**:追尾视角(第三人称过肩)游戏下「看到角色背部 = 正对前方」(仅适用追尾摄像机,勿泛化所有第三人称画面);朝向以 OCR 交互提示 + interact 结果为最终判据(见 [ADR-0004](0004-vision-required.md))。

## Links
- SKILL.md「截图获取:手动分解动作,不靠跑 app 中途」+ 子节(操作时序 / 边缘状态态)。
- 相关:[ADR-0004](0004-vision-required.md)(视觉大模型 不可信边界)、[ADR-0001](0001-five-step-flow.md)(五步流)。
