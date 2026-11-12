# od-dev-screen-onboarding · 设计概览(what)

> 给后续维护者的设计存档(不进智能体执行上下文)。记方法论「长什么样」+ 边界 + 当前状态。

## 为什么做
建游戏知识库(`docs/game/screens/`)+ 维护 `screen_info` 时,每来一张新画面都要重复「分析 → 建档 → 建模」。把这套流程沉淀成 skill,保证后续画面:流程一致、不漏可交互元素、不踩「工具绕路 / 手编 yml」的坑。做成 skill(而非 docs)是因为 skill 触发时自动注入执行上下文(主动),docs 要记得翻(被动)。

## 定位与边界
**管**:拿到截图后的离线分析 + 建档(`docs/game/screens/`)+ 建模可交互元素(模板 + screen_info area)+ 坐标获取 / 模板精准定位(§4.5 视觉直读默认,OpenCV 只管像素级精准;2026-08-31 自 od-dev-ui-region-detect 并入)。

**不管**:
- 运行时识别(框架 screen matching 自己跑);
- gameplay 跨画面流程文档(归 `docs/game/gameplay/`,本 skill 只管单画面;重 app 的玩法建档触发 gameplay-automation skill);
- 整 screen 级 CRUD(增删整个画面,本 skill 只 area 级);
- **本游戏特定的操作事实(交互标记约定如「名字旁三角形=可交互」、导航副作用如「传送后朝向继承」)归消费方项目的画面约定 doc,不在本 skill 硬编码**(规范 4:具体游戏事实归 doc 不归 skill)。本 skill 只记「这类约定存在、建档前查它」的方法论;例子已匿名化,只留通用结论。

## 方法论构成(what)
1. **五步流**(客观 → 主观 → 建档 → 缺口 → 建模):先客观(analyze,识别器视角)再主观(视觉大模型,人视角)避免只看一方漏信息;缺口分析把「已知 / 未知」显式化;建模放最后(基于缺口,不盲目)。玩法画面在前加「先搜攻略理解机制」前置;无匹配时走兜底画面(loading / 对话)。
2. **工具用法**:MCP 工具直调(`analyze_screen` / `upsert_screen_area` / `delete_screen_area`);area 改动一律走 CRUD 工具(经 `save_screen` 同步独立 yml + `_od_merged.yml` + reload),禁止手编 yml / 手改模板目录。
3. **信息源三层并用**:截图 analyze/视觉大模型 + screen_info `area_list`(全集)+ application/operation 代码(`@operation_node` 链)。代码层 caveat = 版本迁移核对(代码可能落后于游戏版本)。
4. **视觉大模型 必需**:每张建档截图都要视觉大模型 看(OCR 看不见图形 / 布局 / 状态图标 / 模态性 / 朝向);视觉大模型 失败必重试。「描述画面有什么」可信、「判断状态 / 作用」不可信;朝向以 OCR 交互提示 + interact 结果为准。
5. **截图手动分解**:app/op 内部连续动作按 `@operation_node` 节点逻辑手动分解成单步 + 截图;跑 app / run_operation 仅用于验证流程通 / 到位。配套:操作后 sleep 等动画、边缘状态态标「待条件」+ 请用户帮切。
6. **重 app 多子玩法按 app 维度建档**:app 编排进 develop doc、玩法机制进 gameplay doc、跨画面 op 联动 screen 记入口 / develop 记编排。
7. **建档文档 = 稳定的画面参考(事实)**:描述类章节只写画面本身的事实;测试结果 / bug 修复历史 / 开放问题不混入描述章节(归测试仓 / commit-PR / 备注节)。
8. **自包含 webp 工具**:`convert_to_webp.py` 自带在 skill 目录,命令内联 SKILL.md;归档 webp 兼作 mock 测试 fixture。
9. **探索未知画面:开放式提问 + 三工具交叉 + 穷尽自查**:画面未知时视觉大模型单看会以偏概全(显著性漏看非显眼区域 / 非文本状态 + 诱导式问法压制输出);先开放式枚举再收窄,视觉大模型 / OCR / 点击交叉(冲突即信号),穷尽自查后才问用户。补第 4 条的对称面(第 4 条讲「OCR 看不见的要 视觉大模型 补」,本条讲「视觉大模型 也会漏看,要 OCR + 点击补」)。
10. **何时该建档:主动 + 被动两种触发 + 建档/快修硬判据**:`description` 不只「主动拿来截图建档」一个触发面,「调试 / 排查 op 卡在不完全认识的画面」也是(否则 debug framing 下猜修不触发本 skill)。判据:说不出画面全部可交互元素 + 各自点后跳哪 → 先建档别猜修。补第 1 条的触发面对称面(第 1 条锚定主动,本条补被动 + 刹车判据)。
11. **卡住画面协议:判据触发后的强制可执行探索 + 禁干卡**:第 10 条只给触发判据没给执行步骤 —— 状态不清的动态画面(覆盖层 / 不知怎么进来的子屏)要**主动交互把行为摸清**,不能干卡。判据触发 → 5 步强制 checklist(回溯怎么进 → 系统找出口 → 穷举可交互元素逐个交互观察 → 交互前后状态读取对比 → 收尾判据)+「禁干卡」禁令(form-to-failure:明知故犯用禁令 + checklist,非软建议)。补第 10 条的执行体 / 可操作化;画面行为探索 single source 在本 skill(`od-dev-write-operation` runtime-craft 加引用对齐)。
12. **开头 must-do checklist 前置 + 顺序重排**:应用 `od-dev-writing-skills` 的规范(含必做动作序列的 skill 必 checklist)—— 开头 9 步 ordered must-do(进度节点 → analyze → 视觉大模型 → 穷举交互 → screen_info → doc → 归档 → id_mark 测试 → 进度收尾),§1-§6 降级 reference 链回。三处非显然重排:① 穷举交互从 §4 前置到建档前(先摸清全部元素行为再定稿,避免返工);② 进度节点第 1 步(认领)+ 第 9 步(标完成)夹住全程;③ 第 1 步显式 chain od-dev-progress-tracking(深潜建档只加载本 skill 不会自动想起它)。

## 落点
- 公共仓 `OneDragon-Skills/skills/od-dev-screen-onboarding/`(`SKILL.md` + `design/` + 自带 `convert_to_webp.py`),OneDragon 系列通用(SR / ZZZ 等)。各消费方仓库按其 setup 约定挂载(如 Claude Code junction 进 `.claude/skills/`)。
- 公共仓开发类前缀 `od-dev-`(通用);消费方项目内可另有项目专属 skill(如 SR 的 `sr-od-dev-*`)。挂载 / 命名 / 路径约定是**所在仓库的 setup**,不在本 skill(见 od-dev-writing-skills)。

## 当前状态
- **GREEN 状态:draft**(待 utility test:干净上下文子 agent 拿一张新截图按本 skill 建档,观察 gap 再修)。按 od-dev-writing-skills「两类 skill」,本 skill 是**方法论覆盖型**(整合画面建档方法论),RED 可省、GREEN 必做(方法见 `od-dev-writing-skills/references/skill-testing.md`)。

## 已知 todo(非架构决策,不配 ADR)
- 批量同屏改动(多个 area pc_rect 修正)用 MCP 客户端串行脚本(1 turn)比 N 次直调(同屏 save 写竞争需串行)高效;「直调 > 脚本」对批量场景待放宽说明。
- 各类画面(战斗 / 养成 / 日常)的典型元素清单(反哺 视觉大模型 预设提问)。
- 更多形状(非圆形)图形按钮的 CV 判据。
- screen_info 缺口的常见模式。

## 自身一致性
遵守 od-dev-writing-skills 4 条硬规范:有 `design/`(design 与 ADR 分开);SKILL.md 指令式 + 判据;自包含(不引 memory / gitignored 依赖,自带 `convert_to_webp.py`);写方法论不写具体游戏事实(具体 app / 场景例子不进 skill 正文;项目特定操作事实归消费方项目 doc)。
