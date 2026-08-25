# ADR 索引(od-dev-agent-autonomous-mode)

| ADR | 决策 | 状态 |
|---|---|---|
| [0001](0001-independent-skill-not-domain-or-personal.md) | 独立通用 skill(而非塞领域 skill/个人入口)——分层落位三问:换领域/换协作者/进版本库 | accepted |
| [0002](0002-productive-inventory-four-sources.md) | 盘点产出型四来源+辩护带清单(治确认循环) | accepted |
| [0003](0003-structural-constraints-over-willpower.md) | 结构性约束优先于自觉(元决策:每纪律答「靠什么机制维持」) | accepted |
| [0004](0004-instantiation-rule-skeleton-vs-flesh.md) | 实例化规则:查专属资产→有则填充→无则自建;判据=每条通用条款能答「在这任务里具体是什么/落在哪」 | accepted |
| [0005](0005-worker-liveness-artifact-mtime-hard-interrupt.md) | worker 活性判据=产物 mtime(非注册表态);停滞≥20min+探询未回应→interrupt 强制收账;长批加检查点交付 | accepted |
| [0006](0006-schedule-two-types-self-vs-delegated.md) | schedule 双类型:自执行(判据内化+短时)vs 派 agent(需干净上下文/偏见敏感);深度巡检 2h 派 agent | accepted |
| [0007](0007-three-work-types-by-trigger.md) | 三类工作按触发器分:主线(依赖)/发现轨(周期扫描)/持续流程(健康监控)——不按可并行性合,合了丢触发器 | accepted |
| [0008](0008-three-work-types-definition-moves-to-progress-tracking.md) | 三类工作定义上移 progress-tracking(普适关注框架),autonomous-mode 只留机械化触发器——「该关注什么」vs「没人盯时怎么保证关注到」 | accepted(部分取代 0007 的落位) |
| [0009](0009-reminder-text-user-visible-plain-language.md) | 提醒词=用户可见的持久化文本:大白话+指针化,判据「冷不丁看到能读懂吗」;防看不懂与「放角色不放细节」的防过期互补 | accepted |
