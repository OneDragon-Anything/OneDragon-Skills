# AI 编码助手接入

本仓库(OneDragon-Skills)是公共开发 skill 仓库。本文档是**通用方法论**(工具无关);Claude Code 专属接线在 [claude-code/](claude-code/)([入口文件引入](claude-code/entry-file.md)、[commit trailer](claude-code/commit-trailer.md))。

## 团队源 vs 个人入口

只分两层:

- **团队源 `AGENTS.md`**(仓库根,**提交**):跨工具单一来源 —— skill 维护的命名 / 结构 / 硬约束 / 流程。改它即更新所有已接入工具的行为。
- **个人入口**(各工具自己的入口文件,**不入库**):随便弄,唯一要求是**引用到 `AGENTS.md`**。个人偏好 / 工具特有规则写这里,不进 `AGENTS.md`。

具体工具的入口文件位置 / 引入语法不同 —— Claude Code 的推荐接线见 [entry-file.md](claude-code/entry-file.md)。

## OneDragon 项目如何消费本仓库的 skill

本仓库 skill 给 OneDragon 项目(StarRail-OneDragon / ZZZ-OneDragon / …)用。消费:把本仓库 clone 到工作区(与项目同级),按需把要用的 skill **目录联接**进项目里 AI 工具读 skill 的目录(如 Claude Code 的 `.claude/skills/`):

```powershell
cmd /c mklink /J "<项目>\.claude\skills\od-dev-write-operation" "<workspace>\OneDragon-Skills\skills\od-dev-write-operation"
```

- 每个工具只读自己目录下的 skill —— Claude Code 读项目的 `.claude/skills/`,不读项目根 `skills/`。
- Windows junction(`mklink /J`)免管理员;symlink 需特权 / 开发者模式。
- 只联接用到的 skill(按需),不必整仓联接。

## 在本仓库开发 / 维护 skill

> 先挂载 `od-dev-writing-skills`(本仓自己的 skill)到 `.claude/skills/` —— 编写时它指导你怎么写 skill(4 硬规范 / writing-craft / testing)。

1. 改 `skills/<name>/`(SKILL.md + design/ + 按需 references/),按 `od-dev-writing-skills` + 守 [AGENTS.md](../../AGENTS.md) 的 4 硬规范。
2. junction `skills/<name>` → 本仓库里 AI 工具读 skill 的目录(如 Claude Code 的 `.claude/skills/<name>`,本地不入库),验证可触发。
3. GREEN 验证(不可省):clean 工作空间 + 子 agent 干真活 + 观察 gap + 修 + 循环。
4. 提交 `skills/<name>/`。

## 依赖:superpowers

本仓库 dev skill 叠加在 [superpowers](https://github.com/anthropics/superpowers) 之上(需求探索 / 写计划 / TDD / 调试 / review / 分支收尾全链路方法论),非替代。Claude Code 安装:插件市场搜 `superpowers`,或 `/plugin install superpowers`。

## AI 辅助提交的署名(推荐)

用 AI 编码工具协作时,推荐 commit 消息用 `Co-Authored-By` trailer 标明 AI 参与(透明、可追溯)。靠模型自觉(在个人入口写指引)或 git `prepare-commit-msg` 钩子自动注入(更稳,推荐)。Claude Code 的具体实现见 [commit-trailer.md](claude-code/commit-trailer.md)。

## 相关文档

- [AGENTS.md](../../AGENTS.md) — 统一 skill 维护入口
- [claude-code/](claude-code/) — Claude Code 专属接线
