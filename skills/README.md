# skills/

OneDragon 公共开发类 skill(`od-dev-*`)。每个 skill 一个目录:`SKILL.md`(agent 指令)+ `design/`(设计 + ADR)+ 按需 `references/`。

命名 / 结构 / 硬规范 / 维护流程见根 [AGENTS.md](../AGENTS.md);写作细则见 `od-dev-writing-skills` skill。

## skill 索引

| skill | 用途 |
|---|---|
| `od-dev-gameplay-automation` | 从零开发新玩法自动化(玩法调研 → 画面建档 → 设计 → 实现 → 验证 → 策略 → 探索式迭代);也含策略设计与调优 |
| `od-dev-progress-tracking` | 复杂多步骤开发的任务树进度追踪 + 防 loop / agent 偏离门 |
| `od-dev-pr-review` | 审查/验证一个 open PR 是否可合并(L0 分诊 → L1/L2 总做 → L3/L4 按类型;游戏流程类 L4 live 硬性;框架语义必查项) |
| `od-dev-pr-finishing` | 把已开的 PR 推到完善可合并(checks / CodeRabbit review / 清 unresolved thread / 跨仓 PR 协同) |
| `od-dev-screen-onboarding` | 游戏画面建档(screen_info area / 模板);调试撞陌生画面先建档再改 |
| `od-dev-ui-region-detect` | 从游戏截图检测 / 验证 UI 区域坐标(槽位网格 / 图标按钮 / 卡牌阵列) |
| `od-dev-deciding-a-fix` | bug 已定位后决定怎么修(介入点选型 / 根因挖多深 / 临时 vs 永久 / 多方案横评) |
| `od-dev-debug-automation` | 排查运行中的自动化 bug(用户反馈跑失败的事后法证:分进程找日志 / run_record 判死活 / 节点流转定位 / 识别参数专项) |
| `od-dev-write-application` | 新建 / 修改 / 调试 Application(把 Operation 组合成可运行 app) |
| `od-dev-write-operation` | 新建 / 修改 / 调试单个 Operation |
| `od-dev-writing-agent-instructions` | 编写 AGENTS.md / CLAUDE.md 类 always-on 入口文件(分层 / 取舍 / 反模式) |
| `od-dev-writing-skills` | 创建 / 修改 skill 的写作规范(4 硬规范 / writing-craft / testing;本仓方法论基石) |

## 部分安装说明

skill 间有互引(单一源设计,刻意不复制内容):开发六件套(gameplay-automation / progress-tracking / screen-onboarding / ui-region-detect / write-application / write-operation)存在**文件级**互引(如 framework-pitfalls 只在 write-operation),**建议整套装**;writing-skills / writing-agent-instructions / deciding-a-fix 相对独立,可单装(deciding-a-fix 软引 write-operation / screen-onboarding);PR 对(pr-review / pr-finishing)互相路由,**成对装**(pr-review 软引 screen-onboarding);debug-automation 软引 write-operation / screen-onboarding / deciding-a-fix。
