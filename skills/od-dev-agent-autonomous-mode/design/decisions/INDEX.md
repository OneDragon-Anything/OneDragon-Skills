# ADR 索引(od-dev-agent-autonomous-mode)

| ADR | 决策 | 状态 | 日期 |
|---|---|---|---|
| [0001](0001-membership-and-layering.md) | 只收自主推进专属内容(成员判据);操作指令与方法论分层存放(SKILL.md 放开关操作,references/ 按主题放方法论) | accepted | 2026-08-27 |
| [0002](0002-self-contained-reminder-messages.md) | 提醒消息自包含:角色义务全文进消息+统一前缀(消费方式钉进消息本体,抗压缩/防缓存应答);当期细节仍禁入 | accepted | 2026-08-27 |
| [0003](0003-status-split-intervention.md) | 值守干预按子 agent 状态分流:活性只认产物时间;运行中停滞直接中断(消息排队无效),空闲发消息催(立刻开轮) | accepted | 2026-08-27 |
| [0004](0004-inventory-requires-fresh-evidence.md) | 盘点必须重新实扫:记忆不作数,状态结论只从当轮读到的内容下;「扫了 X」是自述不是证据,配套改派发盘点/回顾/审计三处提醒模板 | accepted | 2026-08-27 |
| [0005](0005-zero-candidate-escalates-to-scout-agent.md) | 盘点零候选且有空槽 → 升级派干净上下文找活子 agent:两道保险都是同一双眼睛,第三道换上下文重扫;子 agent 只产候选,派单裁决留在编排者 | accepted | 2026-08-28 |

> 历史:2026-08-27 大重整前的旧 ADR 存档(11 条)因与现状大面积矛盾整体废弃删除;编号从 0001 重新起算。
