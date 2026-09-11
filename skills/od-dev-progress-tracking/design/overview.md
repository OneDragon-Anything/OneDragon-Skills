# Overview: od-dev-progress-tracking

## 定位

全局进度记录方法论(DAG 任务账本:事件流正本 + 六态状态机 + 图运算 + 脚本校验 + 防偏离门)。适用于任何复杂多步骤开发(多画面/多模块/多阶段,持续多会话/loop/agent),不绑具体项目/玩法/框架。

## 边界

- **只管**:任务图模型(节点字段/状态机/deps-cond 分判)+ 账本存储(事件流 dag.jsonl,状态折叠现算)+ 脚本约定(dag.py)+ 防偏离门(loop 自检)。
- **不管**:各叶子任务的完成判据(归各工件 skill 的「进度模板」节,如 screen-onboarding 的建档判据、write-operation 的节点图判据;本 skill §12 只做映射)。
- **不管**:具体应用的阶段骨架与 module 归属语义(gameplay 侧在该 skill 的 references/progress-tracking.md)。
- **不管**:项目具体事实(画面/流程/数据)。

## 构成

- **SKILL.md**:使用入口 checklist + §1-13(原则/结构/节点模型/状态机/依赖与等待/建任务时机/脚本/恢复/防偏离门/可观测性/边界/叶子映射/涌现任务)。
- **scripts/dag.py(+test_dag.py)**:事件流账本 CLI(add/status/note/dep/ready/list/graph/card/who/check),规范 §7 的实现;迭代目录随首条 add 自动创建。
- **scripts/progress.py(+test_progress.py)**:旧行文法账本 CLI,2026-09-06 起封存——旧迭代目录查历史仍可用,新任务禁用。
- **design/**:设计决策(why):0001 入口定位层(其入口.md 形态已被 0003 修订撤除);0002 两级平铺账本(行文法部分被 0003 取代);0003 DAG 事件流账本(当前形态,含 2026-09-06 修订:撤流水层、撤入口.md);0004 交付-验收记账协议(第六态+多方自记账+文件存在门);0005 待验收态更名 pending_review。

## 关键决策指针

- 为什么事件流正本而非行文法改良/SQLite/YAML、五态状态机怎么裁、幽灵前置禁令与里程碑显式化 → decisions/0003。
- 为什么两级平铺而非递归树、聚合为什么机器算 → decisions/0002(原则延续,载体被 0003 取代)。
- 为什么入口只留定位层 → decisions/0001(其「目标一行文件」形态已被 0003 修订改为「指令文件单一源」,定位层思想保留)。

## 来源

从 `od-dev-gameplay-automation/references/progress-tracking.md` 提取通用部分演化而来;gameplay 专属语义(种子任务模板/module 归属/生长触发)留在该 reference,通用机制以本 skill 为准。
