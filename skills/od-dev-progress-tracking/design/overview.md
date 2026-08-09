# Overview: od-dev-progress-tracking

## 定位

全局进度记录方法论(任务树状态机 + 防偏离门)。适用于任何复杂多步骤开发(多画面/多模块/多阶段,持续多会话/loop/agent),不绑具体项目/玩法/框架。

## 边界

- **只管**:任务树结构(嵌套节点 + 状态机 + 聚合)+ 防偏离门(loop 自检)+ 事件长尾收件箱。
- **不管**:各叶子任务的完成判据(归各工件 skill 的「进度模板」节,如 screen-onboarding 的①建档判据、write-operation 的节点图判据)。
- **不管**:具体应用的阶段骨架(如 gameplay-automation 的 5 阶段实例化,在该 skill 的 reference 里)。
- **不管**:项目具体事实(画面/流程/数据)。

## 构成

- **SKILL.md**:§1-9 总纲(原则/任务树/状态机/聚合/树操作/防偏离门/边界)+ §10 叶子→skill 模版映射 + §11 事件长尾。
- **design/**:设计决策(why standalone、为什么从 gameplay-automation 提取)。

## 来源

从 `od-dev-gameplay-automation/references/progress-tracking.md` 提取通用部分(§1-9 + §11 + §12 → 本 skill §1-9 + §10 + §11)。gameplay 专属的分纲(原§10,5 阶段骨架)保留在 gameplay-automation。
