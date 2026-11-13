# od-dev-screen-onboarding · 设计概览(what)

> 给后续维护者的设计存档(不进智能体执行上下文)。记方法论「长什么样」+ 边界 + 当前状态;本次重构动机见「设计动机」。

## 为什么做

建游戏知识库(`docs/game/screens/`)+ 维护 `screen_info` 时,每来一张新画面都要重复「分析 → 验证 → 建档 → 建模」。把这套流程沉淀成 skill,保证后续画面:流程一致、不漏可交互元素、不踩「工具绕路 / 手编 yml」的坑。做成 skill(而非 docs)是因为 skill 触发时自动注入执行上下文(主动),docs 要记得翻(被动)。

## 定位与边界

**管**:拿到截图后的离线分析 + 建档(`docs/game/screens/`)+ 建模可交互元素(模板 + screen_info area)+ 坐标获取 / 模板精准定位(§4.4 视觉直读默认,OpenCV 只管像素级精准;2026-08-31 自 od-dev-ui-region-detect 并入)。

**不管**:
- 运行时识别(框架 screen matching 自己跑);
- gameplay 跨画面流程文档(归 `docs/game/gameplay/`,本 skill 只管单画面;重 app 的玩法建档触发 `od-dev-write-application` §1);
- 整 screen 级 CRUD(增删整个画面,本 skill 只 area 级);
- 任务账本 / 进度结构(od-dev-progress-tracking;本 skill 不内置进度模板);
- **本游戏特定的操作事实**(交互标记约定如「名字旁三角形=可交互」、导航副作用如「传送后朝向继承」)归消费方项目的画面约定 doc,不在本 skill 硬编码(规范 4:具体游戏事实归 doc 不归 skill)。本 skill 只记「这类约定存在、建档前查它」的方法论;例子已匿名化,只留通用结论。

## 结构(2026-11-12 重构后)

开头 7 步 ordered checklist(completion gate,与正文章节一一对齐)→

- **§1 建档前判定**:何时建档(两种触发 + 建档/快修硬判据)/ 跨玩法偏离协议 / 建档规模 / 玩法画面先搜攻略 / 信息源三层(含版本迁移核对)/ 截图获取(手动分解 + 操作时序)/ 随机条件态(钩子捕获判据 + 离线降级)。
- **§2 看画面**:2.1 analyze 客观 / 2.2 视觉大模型主观(纪律:状态推理不可信 / 交互标记 / 朝向盲区 / 开放式枚举 / 交互推进)。
- **§3 验交互**:穷举可交互元素 / 探查纪律(不可逆出口最后 + 状态对比 + 禁干卡)/ 强制探索协议 / click 实锤(同源禁令 + 覆盖测试协议)/ goto_list 落边。
- **§4 建档**:4.1 子态归属四问 / 4.2 screen_info(SCREEN 全建 + AREA 增量 + CRUD 纪律)/ 4.3 id_mark 设计(全套:稳定性定义 / 列表判据 / 选锚流程 / 语料双向验证 / 4 区分场景 / 遮挡子态独立屏)/ 4.4 坐标获取 / 4.5 画面 doc(含选择类画面三要点)。
- **§5 模板建模**:5.1 识别方式决策(5 情形,情形 3 三坑判据行 + 采库指针)/ 5.2 图形按钮截模板 / 5.3 模板资产目录规范。
- **§6 归档与 id_mark 测试**:webp 规范 / 覆盖检查 / crop-OCR 坑 / id_mark 测试。
- **§7 边界 / §8 写完自检**。
- `references/id-mark-test.md`(id_mark 测试方法论)、`practices/template-library.md`(图鉴建库工序)、自带 `convert_to_webp.py`。

## 设计动机(2026-11-12 重构)

- **正文序改为流程序**:原 362 行是历史生长序(checklist 顺序与正文 § 顺序对不上、无序号章与 §3.5/§3.6/§4.5 半级编号混杂)→ 重排为 checklist↔§1-§8 一一对齐(2026-11-12 用户裁定,对齐 write-operation/write-application 改造基准)。
- **删除全部进度内容**(零指针):checklist 步 1/9 与「进度模板」节整删 —— 任务账本单一源在 od-dev-progress-tracking;单画面建档不属「复杂多步开发」不该强制建账本;上层流程(od-dev-write-application,原 gameplay-automation)自带账本纪律。外部 3 处表述同步(progress-tracking overview / SKILL 路由表「9步→7步」、gameplay-automation「进度判据它管→建档判据它管」)。
- **id_mark 全部留正文**:id_mark 是建档主线必经(每次建档都定)+ gotcha 集(LCS 撞车 / 遮挡双向配合的触发条件 agent 认不出),按 writing-skills「核心但长留正文 / gotchas 不进 references / 重构时别误伤」(2026-11-12 用户裁定)。
- **随机态判据留正文压缩**(23→~15 行):判据 / 三种错法 / 珍贵性 / 钩子捕获分派是建档工作流的分支本体;钩子**代码实现**归 write-operation runtime-craft(判据 vs 实现分层,经对抗评审确认归属)。
- **两个撞画面协议各归其位**(对抗评审裁定,置信度高):跨玩法偏离 → §1 分诊(使用时机=进 skill 第一问);卡住协议 → §3 验交互(它是穷举交互的探索细则,使用时机=执行中;原 §4→协议 的跨章回引降级为章内整合,「不可逆出口最后」升格章级探查纪律)。
- **采库深水拆 practices**(对抗评审裁定,分层条件):三个坑(混来源 conf 崩 / 行索引错位 / 中文路径)的触发条件+后果**留在 §5.1 判据行**(不可恢复的静默风险防在正文);工序细则(图鉴优先 / 采全判据 / 脚本持久化 / 对齐实现)下沉 `practices/template-library.md`(漏了显性可恢复);指针双保险(行内 + 索引)。
- **外部 9 处锚引用一次清偿**:§4.5→§4.4 ×5、§3.5→§4.3 ×3、§4→§3 ×1(含 SR 项目 docs 一处)+ description 自引。
- **mock 断言方法归位**:原 §6 的「写断言前先读 node 返回类型」是 op 测试方法 → 挪 write-operation `references/testing.md` §2。
- **三处重复规则收敛**:「不可逆出口最后」「每张截图视觉大模型看」「area 齐 ≠ 行为」各收敛到主线一处。

## 落点

- 公共仓 `OneDragon-Skills/skills/od-dev-screen-onboarding/`(`SKILL.md` + `references/` + `practices/` + `design/` + 自带 `convert_to_webp.py`),OneDragon 系列通用(SR / ZZZ 等)。各消费方仓库按其 setup 约定挂载。
- 公共仓开发类前缀 `od-dev-`(通用);消费方项目内可另有项目专属 skill(如 SR 的 `sr-od-dev-*`)。

## 当前状态

- **GREEN 状态:draft**(重构后待 utility test:干净子 agent 拿新截图按本 skill 建档,观察 gap 再修 —— 重点观察项:①agent 在滑动场景(单模板→库)会不会跟 §5.1 行内指针读 practice;②§1 判定章的阅读动线)。本 skill 是**方法论覆盖型**,RED 可省、GREEN 必做(方法见 `od-dev-writing-skills/references/skill-testing.md`)。

## 已知 todo(非架构决策,不配 ADR)

- 批量同屏改动(多个 area pc_rect 修正)用 MCP 客户端串行脚本(1 turn)比 N 次直调(同屏 save 写竞争需串行)高效;「直调 > 脚本」对批量场景待放宽说明。
- 各类画面(战斗 / 养成 / 日常)的典型元素清单(反哺视觉大模型预设提问)。
- 更多形状(非圆形)图形按钮的 CV 判据。

## 自身一致性

遵守 od-dev-writing-skills 4 条硬规范:有 `design/`(design 与 ADR 分开);SKILL.md 指令式 + 判据;自包含(不引 memory / gitignored 依赖,自带 `convert_to_webp.py`);写方法论不写具体游戏事实(具体 app / 场景例子不进 skill 正文;项目特定操作事实归消费方项目 doc)。
