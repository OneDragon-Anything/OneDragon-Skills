# skills/

OneDragon 公共开发类 skill(`od-dev-*`)。每个 skill 一个目录:`SKILL.md`(agent 指令)+ `design/`(设计 + ADR)+ 按需 `references/`。

命名 / 结构 / 4 硬规范 / 维护流程见根 [AGENTS.md](../AGENTS.md);写作细则见 `od-dev-writing-skills` skill。

## 迁移备注(skeleton 阶段)

本仓库为**骨架初始化**,skill 内容尚未迁入。计划从 StarRail-OneDragon 仓库迁入现有开发类 skill 并**改名 `sr-od-dev-*` → `od-dev-*`**(公共仓库用通用 `od-` 前缀),同时**泛化 SR 专属引用**(如具体游戏业务模块路径)为框架通用表述。迁移是独立后续步骤。

迁入清单(待办):

- `sr-od-dev-skill-guide` → `od-dev-writing-skills`(skill 写作规范,本仓库的方法论基石)✅ 已迁入
- `sr-od-dev-write-operation` → `od-dev-write-operation`(写 / 改单个 Operation)✅ 已迁入
- `sr-od-dev-gameplay-automation` → `od-dev-gameplay-automation`(从零开发新玩法自动化 pipeline)✅ 已迁入
- `sr-od-dev-screen-onboarding` → `od-dev-screen-onboarding`(画面建档)✅ 已迁入
- `sr-od-dev-ui-region-detect` → `od-dev-ui-region-detect`(UI 区域坐标检测)
- `sr-od-dev-debug-automation` → `od-dev-debug-automation`(自动化调试)
- `sr-od-dev-deciding-a-fix` → `od-dev-deciding-a-fix`(修复决策)
- `sr-od-dev-pr-review` / `sr-od-dev-pr-finishing` → `od-dev-pr-review` / `od-dev-pr-finishing`(PR 审查 / 收尾)

> 迁移后需逐个核对:SR 专属路径 / 例子是否已泛化;frontmatter `name` 改 `od-` 前缀;skill 间交叉引用从 `sr-od-dev-*` 改 `od-dev-*`。
