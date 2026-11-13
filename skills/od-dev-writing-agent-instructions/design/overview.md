# od-dev-writing-agent-instructions · 设计概览

## 定位
指导创建 / 编辑 / 审查 **always-on 入口文件**(AGENTS.md / CLAUDE.md 类,含个人本地 .local 层)。管:内容取舍(砍为默认)、层内归属(共享 vs 个人本地)、指令写法、纯度、改动流程。

## 边界
- **不管 skill**(按需触发那类)→ od-dev-writing-skills(判据互通但不双源:干净读者原则在那边 §1.9,本 skill 引用)。
- **不管工具机制细节**(哪家支持 @import / rules 目录)→ 变体地图只给默认姿势(单源 + 引入),细节查项目对比文档。
- **不管项目专属内容**(构建命令等)→ 各项目自己的入口文件。

## 构成
- SKILL.md:必做 checklist(5 步)+ §1 格式变体 / §2 内容取舍(写入判据 + 删留自检 + 四档分层)/ §3 三层区分 / §4 反模式。
- 依据:agents.md 开放标准 + Anthropic Claude Code memory 官方文档 + SR 项目 harness 的 context_layering / entry_files 实践(泛化)+ 业界实证调研(写入判据的行业共识×项目特有二分、硬约束走 test/hook/permission、上下文自相矛盾反模式)。

## 与 writing-skills 的关系
相邻 artifact、判据互通、核心动作相反:skill 展开(按需加载,token 便宜),入口文件残酷砍(常驻,context rot)。分层判据(multi-step→skill / 强制→hook / 删了不出错→砍)在本 skill §2;写作判据(干净读者/黑话/会话指代)在 writing-skills,引用不复制。

## 状态
- validated(单轮 utility 实测通过:干净 agent 正确运用写入判据/机制承载/自相矛盾三判据做指令取舍与跨层冲突审查)
