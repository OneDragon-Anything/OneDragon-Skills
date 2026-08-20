# od-dev-stop-hooks · 设计概览(what)

> 本目录是给后续维护者的设计存档,**不进智能体执行上下文**(SKILL.md 不写「见 design/」取使用信息)。

## 为什么做

OneDragon 系列项目是**实机开发范式**:没有模拟环境、对游戏当前状态无先验理解 → 实机是唯一测试环境,埋在运行代码里的钩子(观察 / 留证 / 停机)就是定位问题与捕获状态的基础设施——开发、调试、定位 bug、捕获随机态都靠它,有些还要停机等 AI 现场接手。停机钩子由此获得两个此前无家可归的规范面:

- **消费侧(停机现场处理协议)**:接管停机的 agent 往往不是埋钩子的那个(新会话 / 别的任务中途接手),它看到的只有 STOPPED 状态 + sentinel flag + 存证截图。实锤失败(见 [ADR-0003](decisions/0003-downgrade-requires-evidence-and-user-approval.md) 的三误案例)表明:进度压力 + 状态必然未知 + 无法离线验证,会把 agent 推向各种**绕过变形**(降级带病跑 / 降阈值硬配 / 单源归因),每个都在烧「不可按需复现的实机证据」。
- **生产侧(钩子生命周期判据)**:一次项目级审计(15 处停机钩子,仅 12 处 flag 合格)暴露钩子编写缺契约——flag 缺「可执行处理步骤」、常驻兜底钩子被按临时钩子草率写(见 [ADR-0002](decisions/0002-hook-taxonomy-temporary-vs-resident.md))。

既有覆盖是**作者视角**的(`od-dev-write-operation` runtime-craft 讲埋钩子手法)和**死因排查视角**的(`od-dev-debug-automation` §1 讲谁停的),都没有回答「它就是自己停的,现在该干什么」与「钩子整个生命周期该怎么管」。

## 定位与边界

- **管**:停机钩子(含其降级为留证的形态)的**生命周期判据**(两分类 / flag 三要素 / 降级治理)+ **停机现场处理协议**(预期触发后接管者怎么走)。
- **不管**(指针出去,防双源):
  - 埋钩子的**代码手法**(方案选择 / 前置门实现 / sentinel 写入代码)→ `od-dev-write-operation` runtime-craft「钩子触发停 bot 留画面」;
  - **停机 vs 采集的分流判据** → `od-dev-gameplay-automation` runtime-iteration「随机态钩子分流判据」;
  - **现场建档流程**(含停机后画面已流转降级路径)→ `od-dev-screen-onboarding`;
  - **死因排查**(不知道谁停的)→ `od-dev-debug-automation` §1;两 skill 互为对侧(预期触发场景 vs 异常死因场景),§1 层 3 有移交指针。
- **消歧**:本 skill 的 "stop hook" 指游戏自动化运行时代码里埋的停机钩子,与 AI 工具 harness 层的 Stop / SubagentStop 事件钩子无关。

## 构成

| SKILL.md 节 | 内容 | 防的失败 |
|---|---|---|
| §0 必做清单 | 停机现场 5 步 ordered checklist | 压力下漏步(判归属 / 读 flag / 处理 / 闭环 / 自查) |
| §1 停机现场处理协议 | 归属判别 / 禁绕过清单 + red flags / 类型默认流程 / 证据保全 | 绕过变形(CW 三误的抽象) |
| §2 生命周期判据 | 两分类 / flag 三要素 / 降级治理 / 埋前前置与分层 | 兜底被按临时写、flag 裸、agent 自行降级 |
| §3 审计 | 停入口调用点检查表 | 项目钩子存量质量漂移 |

**form-to-failure 选择**:禁绕过清单用「禁令 + 合理化反驳 + red flags」形态(压力下明知故犯型),不用软建议——软建议会被「先跑起来要紧」谈判掉。

## 与相邻 skill 的接线(单向指针,均已在落点侧同步)

- `od-dev-write-operation` runtime-craft 钩子节:sentinel 示例补「可执行处理步骤」行 + 指向本 skill 三要素契约与两分类。
- `od-dev-debug-automation` §1 层 3:查明 flag 写入者是活钩子 → 移交本 skill 现场协议;description 补移交句。
- `od-dev-gameplay-automation` runtime-iteration 分流判据:停机钩子句补本 skill 指针。

## 当前状态

- **类型**:**纠正型**(改变 agent「进度压力下绕过停机钩子」的默认行为;判据部分含方法论覆盖)。RED(baseline)= 一次项目实锤失败实录(同一天三次错误处理同一停机钩子,用户四次纠偏;见 ADR-0003),已是天然 baseline,无需补跑。
- **GREEN 验证**:pressure test(干净代理 + 3 重压力选择题 + 抓合理化原话),场景:未知物品触发 / 识别可疑 / flag 裸数字 / 兜底型触发 / 触发捕获。状态见下方更新记录。

<!-- GREEN 记录(最近在前):
- 2026-08-20 首轮 GREEN 过(双干净代理,默认路由):
  - pressure test 5 场景全对(未知物品+遥测沉没成本+同伴 agent 劝降阈值→照 flag 走;视觉模型单源归因→交叉验证三分支;凌晨裸 flag→grep 写入者+类型默认流程+补要素;兜底型第 5 次触发→只删 flag 改移除条件不删钩;三度阻断+用户催→只提案不自行降级),代理自述按「禁绕过清单+生命周期判据」两轴排除全部「先跑起来要紧」选项——三误变体(降阈值/降级/单源)在压力下全被拒。
  - 触发捕获:干净代理在 13 个挂载 skill 中首序选本 skill(flag 自证预期停→直入协议),次序正确指到 screen-onboarding(建档)/debug-automation(证据不符回退)/write-operation(删钩子);无 flag 场景正确先 debug-automation §1 判死因——description 触发面与两 skill 移交边界实测成立。
-->
