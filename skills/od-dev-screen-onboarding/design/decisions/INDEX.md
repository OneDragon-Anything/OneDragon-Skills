# ADR 索引

| NNNN | 标题 | 状态 | 日期 |
|------|------|------|------|
| [0001](0001-five-step-flow.md) | 五步流:客观→主观→建档→缺口→建模 | accepted | 2026-08-04 |
| [0002](0002-mcp-direct-call-crud-over-handedit.md) | MCP 直调 + area CRUD 工具 > 手编 yml / HTTP 脚本 | accepted | 2026-08-04 |
| [0003](0003-three-information-sources.md) | 信息源三层并用:截图 + screen_info + 代码(含版本迁移核对) | accepted | 2026-08-04 |
| [0004](0004-vision-required.md) | 视觉大模型 必需,不只靠 MCP(含 视觉大模型 不可信边界) | accepted | 2026-08-04 |
| [0005](0005-manual-decomposition-screenshots.md) | 截图手动分解 op 节点,不靠跑 app/op 中途 capture | accepted | 2026-08-04 |
| [0006](0006-heavy-app-dimension-onboarding.md) | 重 app 多子玩法按 app 维度建档 | accepted | 2026-08-04 |
| [0007](0007-doc-stable-facts-only.md) | 建档文档只写画面事实,过程产物不进描述章节 | accepted | 2026-08-04 |
| [0008](0008-bundled-webp-tool-inline.md) | 自包含:webp 转换工具内联进 SKILL.md | accepted | 2026-08-04 |
| [0009](0009-open-prompt-cross-tool-exhaustive.md) | 探索未知画面:open prompt + 三工具交叉 + 穷尽自查(防 视觉大模型 以偏概全) | accepted | 2026-08-04 |
| [0010](0010-debug-hit-unfamiliar-screen-onboard-not-patch.md) | 调试撞陌生画面 = 建档信号不是快修信号(description 补被动触发 + 建档/快修硬判据) | accepted | 2026-08-05 |
| [0011](0011-harvest-catalog-reusable-script-position-align.md) | 采图鉴模板库:脚本持久化为可复用工具 + 标签图标按空间位置对齐(非行索引) | accepted | 2026-08-06 |
| [0012](0012-stuck-screen-forced-exploration-protocol.md) | 卡住画面协议:判据触发后的强制可执行探索 + 禁干卡(补 ADR-0010 执行体) | accepted | 2026-08-06 |
| [0013](0013-exhaustive-interaction-survey-irreversible-exit-last.md) | 认知层穷尽探查画面所有可交互元素 + 探查顺序(不可逆出口最后) | accepted | 2026-08-07 |
| [0014](0014-exhaust-vlm-iterate-open-on-failure.md) | 视觉大模型交互流程:画面不重复 + 让它提需求 + 交互失败迭代 + 穷尽才升级 | accepted | 2026-08-07 |
| [0015](0015-mustdo-checklist-prefixed-reordering.md) | 开头 must-do checklist 前置 + 顺序重排(穷举交互前置 / 进度节点 chain 进主流程) | accepted | 2026-08-10 |
| [0016](0016-cross-mode-drift-navigate-back.md) | 跨玩法偏离协议:认知完整但非目标玩法 → 导航回目标(别停;卡住协议并列分支) | accepted | 2026-08-11 |
| [0017](0017-random-state-passive-hook-and-pause.md) | 随机/条件态:被动钩子捕获 + 触发停当场建档(非请用户帮切) | accepted | 2026-08-11 |
| [0018](0018-area-complete-not-interaction-verified.md) | area 齐 ≠ 交互验证完:逐个交互验证从 §4 方法论提升进进度模板硬完成判据 | accepted | 2026-08-11 |
| [0019](0019-interactive-area-click-verify.md) | 交互类 area 必须 click 实锤(视觉定位再准也不证可点性;展示图与真按钮无差别) | accepted | 2026-08-16 |
| [0020](0020-post-stop-frame-gone-offline-degraded-path.md) | 停机后画面已流转的离线降级路径(先判画面态合法性;非法→修前置门不建档;原图直喂不裁剪) | accepted | 2026-08-16 |
| [0021](0021-substate-modeling-ownership-four-questions.md) | 子态建模归属四问判据(独立屏 vs 父屏 area;遮挡三段式含换锚权衡;正交一票否决) | accepted | 2026-08-17 |
| [0022](0022-template-asset-directory-convention.md) | 模板资产目录规范(模板根/<玩法>/<类型>;禁源码包藏资产/同名双库/先散放后迁;生成器产物标来源) | accepted | 2026-08-17 |
| [0023](0023-idmark-candidate-vision-prior-runtime-verdict.md) | id_mark 选锚流程:视觉枚举候选 + 跨帧验稳定(内容位一票否决)+ 运行时匹配定谳 | accepted | 2026-08-29 |

> 日期为 ADR **形式化日**(按 od-dev-writing-skills 重构 + 迁公共仓时回溯记录);原始决策 / 踩坑发生日见各 ADR 的 Context。
