# ADR-0005:待验收态更名 review → pending_review(读侧归一+写侧别名)

- Status: accepted
- Date: 2026-09-11
- Amends: 0004 决策 1 的状态命名——六态语义、流转矩阵、必带字段、文件存在门全部不变,仅 `review` 更名 `pending_review`。0004 其余(多方自记账/账本级锁/双目录/返工熔断)全部延续。

## Context

六态 `todo/doing/wait/review/done/dead` 中唯一用动作名词的 `review`,语义是「已交付待验收」,但裸 token 有两种更自然的误读:顺 `doing`(动作进行中)读成「正在验收中」,按名词读成「评审环节」——都读不出「交付方已完成、等验收方裁决」的方向。机器输出(ready 任务卡 `review@谁`、log 时间线 `review -> done`、mermaid class、raw jsonl)全是裸 token,带不上中文旁注;ready 输出被迫写成 `== review 待验收 ==` 才能读,恰是名字不自明的旁证。用户判读(2026-09-11,在册裁定):「待 review 的状态居然是 review,很容易歧义」。

约束:账本是 append-only 事件流正本,历史事件里大量 `from/to: review` 永久存在且不得改写;更名落地时(货币战争迭代)正有任务停在该态、worker 在飞写入,不允许硬切换。

## Considered Options

- **保留 `review`+文档加注**:否——旁注只能覆盖 SKILL.md 阅读语境,裸 token(命令输出/账本行)永远歧义,根因(名字不编码「谁的动作、停在哪一步」)不动。
- **`delivered`**(过去分词,与 `done` 同语法):次优——语义也自明,但用户裁名 `pending_review` 对缺省读者更直白(不看 ADR 也知道在等什么),且单 token 不破坏命令行手感。
- **`to_review`/`awaiting_review`**:否——与 `pending_review` 同义同长,无增益。

## Decision

1. 状态名 `review` → `pending_review`;六态语义与全部流转不变。
2. **旧账本零迁移**:dag.py 读侧(fold/check/log)经 `normalize_status` 把旧 token `review` 归一为 `pending_review`;`status` 命令对新旧名都收——旧名归一后按规范名落盘并打一行更名提醒;check 对盘上残留旧 token 给信息级警(不计错,不挡通过)。
3. 写侧事件一律落规范名:新账本从第一天起盘上只有 `pending_review`,别名只为读旧账本与兼容在飞 worker 的肌肉记忆。
4. 命名判据沉淀:状态/枚举名必须编码「谁的动作、进行到哪一步」;单独的动作名词做态名默认歧义——`doing`(执行方进行中)自明,`review`(谁的?进行到哪?)不自明,待验类状态用「已完成的交付动作+pending 方向」表达。

## Consequences

- 正:裸 token 自解释,ready/log/mermaid/jsonl 无需旁注;旧账本与在飞 worker 零中断(别名收编,读旧写新都归一);未来收紧为只收规范名时只需删别名表一处。
- 负:①过渡期两种写法并存,派单任务书/编排手册需统一用新名(写旧名合法但会被提醒);②别名归一是 dag.py 的长期维护面,直到宣布旧名退役才可删;③check 的旧名警与写侧归一并存,「盘上无旧 token」成为常态,该警实际只在直改旧档/迁移场景出现。
