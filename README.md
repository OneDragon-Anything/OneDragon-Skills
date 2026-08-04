# OneDragon-Skills

OneDragon(一条龙)系列游戏自动化项目的**公共开发 skill 仓库**。

`skills/` 下的开发类 skill 指引 AI 编码 agent 在任何 OneDragon 框架项目(StarRail-OneDragon / ZZZ-OneDragon / …)上做开发 —— 这系列项目共用同一套框架(`one_dragon` 公共包:Operation 节点图 / screen_info / controller / YamlConfig …),开发方法论一致,故 skill 抽到本公共仓库,各项目引用同一套。

## 里面有什么

- `skills/<name>/`:开发类 skill(`od-dev-*`)。每个 = `SKILL.md`(agent 指令)+ `design/`(设计 + ADR)+ 按需 `references/`。
- `AGENTS.md`:跨工具单一源 —— skill 维护的架构 / 硬约束 / 流程(always-on)。
- `docs/setup/`:AI 工具接入 + 项目如何消费本仓库。

## 项目如何消费(把 skill 接进某个 OneDragon 项目)

把本仓库 clone 到工作区,按需把要用的 skill **目录联接**(junction)进项目的 `.claude/skills/`:

```powershell
cmd /c mklink /J "<项目>\.claude\skills\od-dev-write-operation" "<workspace>\OneDragon-Skills\skills\od-dev-write-operation"
```

(Windows junction 免管理员;symlink 需特权。每个工具只读自己 `.claude/skills/`。)详 `docs/setup/ai_coding.md`。

## 如何开发 / 维护 skill

先读 [AGENTS.md](AGENTS.md)(命名 / 结构 / 4 硬规范 / 流程),写作细则见 `od-dev-writing-skills` skill。本仓库 dev skill 叠加在 [superpowers](https://github.com/anthropics/superpowers) 之上,非替代。
