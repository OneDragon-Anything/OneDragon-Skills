# AI 编码助手接入

本仓库(OneDragon-Skills)是公共开发 skill 仓库。本文档是**通用方法论**(工具无关);Claude Code 专属接线在 [claude-code/](claude-code/)([入口文件引入](claude-code/entry-file.md)、[commit trailer](claude-code/commit-trailer.md))。

## 团队源 vs 个人入口

只分两层:

- **团队源 `AGENTS.md`**(仓库根,**提交**):跨工具单一来源 —— skill 维护的命名 / 结构 / 硬约束 / 流程。改它即更新所有已接入工具的行为。
- **个人入口**(各工具自己的入口文件,**不入库**):随便弄,唯一要求是**引用到 `AGENTS.md`**。个人偏好 / 工具特有规则写这里,不进 `AGENTS.md`。

具体工具的入口文件位置 / 引入语法不同 —— Claude Code 的推荐接线见 [entry-file.md](claude-code/entry-file.md)。

## 项目如何消费本仓库的 skill

### 标准安装(推荐)

[skills CLI](https://github.com/justjavac/skills)(agent-skills 开放生态,支持 Claude Code / Codex / Cursor / OpenCode 等 70+ agent):

```powershell
npx skills add OneDragon-Anything/OneDragon-Skills                    # 交互式:选 skill + 选 agent
npx skills add OneDragon-Anything/OneDragon-Skills -l                 # 只列出本仓可用 skill
npx skills add OneDragon-Anything/OneDragon-Skills -a claude-code -y  # 非交互指定 agent
```

- 装进**所选 agent 自己的 skills 目录**(项目级 `./<agent>/skills/`,默认 symlink 便于 `npx skills update`;`-g` 装全局 `~/<agent>/skills/`;`--copy` 改复制)。常见落点:Claude Code `.claude/skills/`、跨工具通用位 `.agents/skills/`(`-a universal`;DSH 等工具也扫它)。
- 更新 / 卸载:`npx skills update` / `npx skills remove`。

### 手动 junction(本地开发 / 维护本仓时用)

把本仓 clone 到工作区,按需把 skill **目录联接**进项目里 AI 工具读 skill 的目录 —— 直接指向本仓 clone,改一处全工具生效:

```powershell
cmd /c mklink /J "<项目>\.claude\skills\od-dev-write-operation" "<workspace>\OneDragon-Skills\skills\od-dev-write-operation"
```

- Windows junction(`mklink /J`)免管理员;symlink 需特权 / 开发者模式;只联接用到的 skill,不必整仓联接。

## 目录结构是安装器兼容的硬约束

`skills/<name>/SKILL.md`(flat,一层)是 agent-skills 开放标准的发现结构,`npx skills add` 按此扫描本仓。维护时保持:

- skill 一律放 `skills/<name>/`,**别按类目再嵌一层** —— 标准虽也支持 `skills/<category>/<name>/` 目录布局,本仓统一用 flat,避免两套布局混用。
- 目录名与 frontmatter `name` 一致;frontmatter 必填 `name` + `description`(格式细则见 `od-dev-writing-skills`)。
- `design/` / `references/` 等辅助目录随 skill 目录整体安装,不受影响;仓根其他文件(AGENTS.md / docs/)不参与 skill 发现。

## 在本仓库开发 / 维护 skill

> 先挂载 `od-dev-writing-skills`(本仓自己的 skill)到 `.claude/skills/` —— 编写时它指导你怎么写 skill(编写全流程 / testing)。

1. 改 `skills/<name>/`(SKILL.md + design/ + 按需 references/),按 `od-dev-writing-skills` 走(含守 [AGENTS.md](../../AGENTS.md) 的本仓约定)。
2. junction `skills/<name>` → 本仓库里 AI 工具读 skill 的目录(如 Claude Code 的 `.claude/skills/<name>`,本地不入库),验证可触发。
3. GREEN 验证(不可省):clean 工作空间 + 子 agent 干真活 + 观察 gap + 修 + 循环。
4. 提交 `skills/<name>/`。

## AI 辅助提交的署名(推荐)

用 AI 编码工具协作时,推荐 commit 消息用 `Co-Authored-By` trailer 标明 AI 参与(透明、可追溯)。靠模型自觉(在个人入口写指引)或 git `prepare-commit-msg` 钩子自动注入(更稳,推荐)。Claude Code 的具体实现见 [commit-trailer.md](claude-code/commit-trailer.md)。

## 相关文档

- [AGENTS.md](../../AGENTS.md) — 统一 skill 维护入口
- [claude-code/](claude-code/) — Claude Code 专属接线
