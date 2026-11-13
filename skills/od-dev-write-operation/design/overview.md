# od-dev-write-operation — 设计概览(what)

> 本文件是 **what**(skill 长什么样 / 范围 / 边界 / 构成)。

## 定位(是什么)

OneDragon 框架上「写 / 改 / 调试**单个 Operation**」的方法论 skill。主线是一套**设计先行的六步流程**:op 不是直接写代码,是先把流程摸清成三份设计稿(requirement / screen-flow / nodes),经用户确认后再翻译成节点图代码。

## 主线六步

1. **需求确定**(纸面,不上游戏):从前置来源(用户任务原话 / 玩法文档 / app 编排上下文)收拢目标一句话 + 起终点 + 大致操作 + 放置位置 + 红线 → `requirement.md`。
2. **摸流程**(agent 自主驱动实机走查):沿需求粗线逐跳走——查地图(含逐段查现成 op)只摸未知段、画面核对三分支(未建档建档 / 一致通过 / 漂移纠档)、副作用三档(可逆直接做 / 不可逆问用户 / 消耗前一步停)、变体枚举三分支(会话内走全 / 不可达记未知项 / 消耗型不摸)→ `screen-flow.md` + 沿途建档。
3. **拆节点**(流转 → 节点卡):一次流转一节点;循环驱动先选结构(flat loop vs node-per-op);入口判定归位(首节点判 / 中途靠出口验证);子 op 结果 = 分支;节点卡 = 识别→动作→验证→出口的分支链 → `nodes.md`。
4. **设计确认**(人类裁决点):汇报四件套 → 直接写代码 / 升级正式迭代设计 / 打回。
5. **写代码**(节点卡 → 代码翻译):先过 MCP 可运行单元写法契约(§5.0:构造签名/类名/docstring),再按字段级翻译对照表(round 函数 + until + wait 纪律)。
6. **验证**(三层递进):mock 流程快测抓结构逻辑(无实机,素材 = 探索沿途截图)→ 实机单跑验收(唯一真相源)→ 回归测试落盘锁行为(素材按需挑进测试仓);交付 = 接入 app 编排或作为 MCP 可调单元。

## 关键设计决策(动机段)

- **设计先行、三份稿**:自动化需求不可完备(分支实机才暴露),但"先摸清再写"仍是比"边写边猜"更优的路径;设计稿放 `.debug/temp/operation-explore/`(临时区,寿命=开发期),**事实与设计分离**——画面事实即时进 screen_info/画面 doc(零草稿),设计稿只记编排;代码 docstring + `@node_from` 节点图是设计的持久镜像(修改 op 时的现状反推源)。
- **④人类裁决点**:①②③ agent 全自主,④必须停下汇报裁定——防止 agent 带着未审设计滑进实现;复杂度判据由 agent 给推荐、用户拍板。
- **一次流转一节点**:每节点出口验证转移是纪律,节点内做两次流转 = 第一次流转没验证就做第二步;「弹窗确认链逻辑上是一件事」不构成聚合理由。
- **入口判定归位**:出口验证就是下一节点的入口保证,中途重复判定是白付的开销;防线归出口验证(画面不对修锚,不加中途判定当补丁)。
- **修改分诊**:A 行为不符合设计(bug)→ 调试路径(根因→复现→按层修→防回归,铁律"只有明确复现流程才能修改");B 设计本身要变 → 重走主线(现状核对替代从零摸)。「复现流程」双向:修前验证根因,修后是回归剧本。
- **先实测后测试**:实测验证设计、测试锁定行为;实测大概率改代码,测试先写就是白写(与通用 TDD 相反的理由:mock 锁不住运行时问题)。
- **practices/ 增量扩展**:特定形态 op 的实践(循环驱动/列表网格识别/选择类)独立目录 + SKILL.md 特征触发表——主线保持纯流程,新实践 = 加文档 + 表加一行。
- **op 即 MCP 单元(一档制契约)**:op 除节点图身份外,默认同时是 MCP 可运行单元(agent 经 list/describe/run 探查调用)。「给谁用」写时判不准(今天编排用,明天调试想单跑),与其分档预判,不如全员统一按可传参标准写——JSON 边界友好的参数本身也是更好的接口(传名字不传对象,输入依赖显式、mock 好写);运行时对象参数的框架级 op 走显式豁免(构造 docstring 声明),不做默认后门。约束与注解陷阱经 StarRailOneDragon backend 沙盒实测实证(机制篇 references/mcp-runnable.md)。
- **类 docstring = 使用说明(describe 整段透传)**:远程使用者看不到源码,op 语义对它的唯一来源是 describe 透传的本类 docstring;效果口径「写使用者可感知的状态变化,不写过程动作」(动作+产出,与 requirement.md 三要素同源转写);不做结构化解析——消费者是 agent,读自然语言无障碍,解析只有格式脆弱性没有收益。
- **类名 Op 后缀**:新 op 不带(用户裁定),存量带后缀的保留不迁移,同域混用是接受的过渡态——规则只约束新写法,不追改存量。
- **放置判定归需求阶段**:application 包是域分组(不要求域里有 app,纯给 MCP agent 用的 op 也落此),跨域复用才上顶层 operations 包;位置判定进 requirement.md、随四件套向用户确认——位置是目录结构决策,agent 不自行放行。

## 范围 OUT(指针,不重复)

- 从零做新玩法全程 → `od-dev-write-application`(它引用本 skill 的 practices/loop-driven-op.md 与 references/framework-pitfalls.md)
- app 产品化 → `od-dev-write-application`
- 建一张屏的机制 → `od-dev-screen-onboarding`(②开工前前置加载;建档/纠档手法全归它)
- 修复决策 → `od-dev-deciding-a-fix`;不在场的事后排查 → `od-dev-debug-automation`

## 构成(文件结构)

- `SKILL.md`:六步主线 + 7 最佳实践索引 + 8 必守不变量 + 9 修改与调试 + 10 边界 + 11 自检。
- `practices/`(场景触发,增量扩充):`loop-driven-op.md`(循环驱动实现形态,single source)、`list-grid-recognition.md`、`select-and-proceed.md`。
- `references/`(主线机制深化):`explore-docs-template.md`(三份设计稿模板)、`round-by-helpers.md`(函数细节 + LCS 机制 + 非节点上下文)、`node-graph.md`(节点图机制/自环陷阱)、`framework-pitfalls.md`(框架踩坑 single source)、`testing.md`、`runtime-craft.md`(运行时技术:信息密度/预料外调研/钩子代码手法——与主线⑧⑨章分工:主线留判据,此文件留展开)、`mcp-runnable.md`(op 即 MCP 可运行单元:探查链路/反射机制/注解陷阱实测/验收三连——SKILL.md §5.0 的机制篇)。
- `design/`:本目录。

## 落点

公共仓 `OneDragon-Skills/skills/od-dev-write-operation/`,OneDragon 系列通用(SR/ZZZ 等)。各消费方仓库按其 setup 约定挂载。`.debug/temp/operation-explore/` 为系列通用约定直接写进 SKILL.md(用户裁定)。

## 类型(RED / GREEN)

方法论覆盖型 → RED 可省,**GREEN 必做**:干净上下文给 op 开发任务,验证六步主线被正确触发与执行(方法见 `od-dev-writing-skills` 的 `references/skill-testing.md`;重实机流程类 skill 的验证需适配——回放真实案例 + 纸面章节分段测 + 下一个真实任务现场观察)。

**状态:draft** —— 重构版经独立子 agent 评审,必改项(孤儿 reference 挂点 / 死引用清偿 / 状态节)已修复;§5.0 MCP 契约部分经**裁剪版 GREEN** 实测(干净子 agent 纸面任务走到⑤,七个契约观察点全过:放置判定 / 类名 / 构造签名 / docstring 两段式 / 陷阱规避 / data 返回 / 效果式描述;三条反馈已回灌——新建查重 / 高消耗画面零消耗行 / 参数段位置)。完整六步主线的 GREEN 待下一个真实 op 开发任务现场验证。
