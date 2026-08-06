# 0009. flat loop 推进型 handler 完成验证(三层完成验证的最后一块)

- **Status**: accepted
- **Date**: 2026-08-06

## Context

反馈(开发中 5 次 flat-loop 共同模式)指出:flat loop 内「点 UI 推进 overlay / 画面」的 handler,点了就 `round_success` / 让 loop 重跑,**不验画面真推进** → 点不中(坐标落候选间隙 / LCS 误匹配 / click 没落地)→ overlay 不关 / 画面没跳 → loop 反复点同一处 → `round_wait` 不计 retry → 无限到 MAX_ITER(几十~上百 iter 才死)。

现有覆盖**两层**完成验证,缺 flat handler 这层:

- [ADR-0007](0007-op-entry-exit-state-check.md):op **边界**出口验证转移(粒度 = op 边界)。
- [ADR-0003](0003-loop-driven-node-per-op.md) + `loop-driven-op-structure.md`:**node-per-op 的 node op** 完成检测 + 节点预算(粒度 = node op)。
- flat loop 内的 handler(粒度 = loop 内一步,**非 op 边界、非 node op**)**没明确的完成验证判据** —— `loop-driven-op-structure.md` 讲了 flat loop 的卡死缺陷,但解法只指向"迁 node-per-op",没给"若用 flat loop,handler 怎么写不卡死"的底线。

「点 UI 推进」是通用模式(任何此类 handler 都中),非项目 / 模型特异 → 进 skill 正文(规范4 + 通用 RCA,见 writing-craft §3.1)。5 次复发(跨不同 handler / 不同点不中根因)为证,非偶发。

## Decision

补「flat loop 推进型 handler 完成验证」判据,作为三层完成验证(op 边界 / node op / flat handler)的**最后一块**:

- **推进型 handler**(关 overlay / 翻页 / 点掉弹窗 / 点掉提示)点了之后,必须验画面推进(目标消失 / overlay 关 / 画面跳 / 锚变化 —— 任一可靠信号);验不到 → `round_retry`(计当前 flat 节点预算)兜底退出,**别盲目 `round_wait` 重跑**(不计数 → 点不中时无限)。
- **一句话判据**:「点了」≠「成了」,success / 让 loop 继续前验画面变化。与 [ADR-0007](0007-op-entry-exit-state-check.md)(op 边界)、[ADR-0003](0003-loop-driven-node-per-op.md)(node op)同构。

**落点**:`SKILL.md`「循环驱动玩法」节反模式(把 node op + flat handler 两层统一成「点了≠成了」);`loop-driven-op-structure.md` flat loop 缺陷节补"合理适用场景内也要守的底线"小节。

## Decision Drivers

- **同一坑的两面**:flat loop 卡死缺陷(`loop-driven-op-structure.md` §2)讲"**有单元时** handler 完不成也 success → 无限";反馈揭露**无单元的纯推进型场景**点不中也无限 —— 是 `round_wait` 不计 retry 这**同一机制**的两种触发。
- **flat loop 仍有合理适用场景**(纯帧级反应式:点空白加速战斗 / 结算翻页 / 点掉弹窗),不能全禁;但这些场景的推进型 handler 也要守完成验证底线。
- **`round_retry` 能兜底**:flat handler 返回 `round_retry` 计当前节点 `node_max_retry_times`,N 次没推进 = FAIL 退出,不无限烧全局(虽不如 node-per-op 的单元作用域预算精细,但够防死循环)。

## Considered Options

### A. 补 flat handler 完成验证判据(本决策)
- ✅ 堵住 flat loop 合理场景内"点不中 → 无限";三层完成验证闭环,判据统一(「点了≠成了」)。
- ✅ 与现有两层同构,认知负担低。

### B. 不补,判"已被 ADR-0007 + ADR-0003 覆盖"
- 否决:**粒度不同** —— ADR-0007 是 op **边界**(flat handler 不是 op 边界,是 loop 内一步);ADR-0003 是 **node op**(flat loop 不是 node-per-op)。flat handler 这层没覆盖,反馈 5 次跨根因复发为证。

### C. 强制推进型场景也用 node-per-op(禁 flat loop 扛推进)
- 否决:**过度** —— flat loop 对纯帧级反应式(点空白加速 / 翻页)是合理的;"推进型"与"有逻辑单元生命周期"不等价(翻页是推进但无单元生命周期)。已有项目用 flat loop 做这类场景,强制迁移成本不划算;补完成验证判据即可防死循环。

## Consequences

- **正向**:flat loop 合理场景内不再"点不中 → 无限烧 MAX_ITER";三层完成验证闭环,判据统一。
- **代价**:flat loop 推进型 handler 多一次截图 + OCR 验证(与 op 边界出口验证同代价,默认守合理)。
- **与现有立场关系**:**不推翻** [ADR-0003](0003-loop-driven-node-per-op.md)(有单元生命周期 + 多阶段该迁 node-per-op 仍成立);只是 flat loop 合理场景内补底线。
- **推翻它会碎什么**:退回 B → flat loop 合理场景继续点不中无限;退回 C → 过度禁用,简单翻页 / 加速场景被迫上 node-per-op。

## Links

- 落点:`../SKILL.md`「循环驱动玩法」节反模式;`../references/loop-driven-op-structure.md` flat loop 缺陷节("合理适用场景内也要守"小节)
- 相关:[ADR-0007](0007-op-entry-exit-state-check.md)(op 边界出口验证,同构)、[ADR-0003](0003-loop-driven-node-per-op.md)(node op 完成检测,同构;本条是其 flat-loop 侧的底线补全)
