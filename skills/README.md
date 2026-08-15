# skills/

OneDragon 公共开发类 skill(`od-dev-*`)。每个 skill 一个目录:`SKILL.md`(agent 指令)+ `design/`(设计 + ADR)+ 按需 `references/`。

命名 / 结构 / 硬规范 / 维护流程见根 [AGENTS.md](../AGENTS.md);写作细则见 `od-dev-writing-skills` skill。

## skill 索引

| skill | 用途 |
|---|---|
| `od-dev-gameplay-automation` | 从零开发新玩法自动化(玩法调研 → 画面建档 → 设计 → 实现 → 验证 → 策略 → 探索式迭代);也含策略设计与调优 |
| `od-dev-progress-tracking` | 复杂多步骤开发的任务树进度追踪 + 防 loop / agent 偏离门 |
| `od-dev-screen-onboarding` | 游戏画面建档(screen_info area / 模板);调试撞陌生画面先建档再改 |
| `od-dev-ui-region-detect` | 从游戏截图检测 / 验证 UI 区域坐标(槽位网格 / 图标按钮 / 卡牌阵列) |
| `od-dev-write-application` | 新建 / 修改 / 调试 Application(把 Operation 组合成可运行 app) |
| `od-dev-write-operation` | 新建 / 修改 / 调试单个 Operation |
| `od-dev-writing-agent-instructions` | 编写 AGENTS.md / CLAUDE.md 类 always-on 入口文件(分层 / 取舍 / 反模式) |
| `od-dev-writing-skills` | 创建 / 修改 skill 的写作规范(4 硬规范 / writing-craft / testing;本仓方法论基石) |
