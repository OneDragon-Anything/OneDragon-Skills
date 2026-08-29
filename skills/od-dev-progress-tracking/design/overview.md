# Overview: od-dev-progress-tracking

## 定位

全局进度记录方法论(两级平铺任务账本 + 行文法 + 状态机 + 脚本校验 + 防偏离门)。适用于任何复杂多步骤开发(多画面/多模块/多阶段,持续多会话/loop/agent),不绑具体项目/玩法/框架。

## 边界

- **只管**:账本结构(迭代目录 → app → 模块 → 任务行+缩进子行)+ 状态机 + 依赖字段 + 流水/归档分工 + 脚本约定(progress.py)+ 防偏离门(loop 自检)。
- **不管**:各叶子任务的完成判据(归各工件 skill 的「进度模板」节,如 screen-onboarding 的建档判据、write-operation 的节点图判据)。
- **不管**:具体应用的阶段骨架与模块归属语义(gameplay 侧在该 skill 的 references/progress-tracking.md)。
- **不管**:项目具体事实(画面/流程/数据)。

## 构成

- **SKILL.md**:使用入口 checklist + §1-13(原则/结构/行文法/状态机/依赖与检索/聚合/脚本/恢复/防偏离门/可观测性/边界/叶子映射/涌现任务与流水关系)。
- **scripts/progress.py(+test_progress.py)**:账本写入与结构体检的 CLI(init/write/check/summary/journal),规范 §7 的实现。
- **design/**:设计决策(why):0001 入口定位层;0002 两级平铺替代递归树(含机械聚合/流水文件/脚本校验门的依据)。

## 关键决策指针

- 为什么两级平铺而非递归树、聚合为什么机器算、收件箱为什么废除 → decisions/0002。
- 为什么入口只留定位层 → decisions/0001(注意:其「涉及 app 表」已被 0002 的自动发现取代)。

## 来源

从 `od-dev-gameplay-automation/references/progress-tracking.md` 提取通用部分演化而来;gameplay 专属语义(任务归哪个模块)留在该 reference,文件组织以本 skill 为准。
