# od-dev-write-application — 设计概览(what)

> 本文件是 **what**(skill 长什么样 / 范围 / 边界 / 构成);重构动机见「设计动机」节。

## 定位(是什么)

OneDragon 框架上「写 / 改 / 调试**一个 Application**」的方法论 skill。把玩法的若干 Operation 组合成可运行的 app(自动注册、有配置/GUI、能进一条龙或单独跑)。

**核心洞察**:Application 继承 Operation → **写 app 90% = 写 op**(→ `od-dev-write-operation`);本 skill 只讲 app 加的那一层。

## 边界(3-粒度拆分)

- op 粒度(单 Operation)→ `od-dev-write-operation`。
- **app 粒度(整个 Application 产品化,含从零做新玩法全程)→ 本 skill**(2026-11-13 用户裁定:原 `od-dev-gameplay-automation` 废弃,其职责并入本 skill——新玩法从零开发也走本 skill 主线;玩法策略调优整块不迁,见「设计动机」策略条)。

判单项归哪层,问:这是「单个 op 的写/改/修」,还是「整个 app / 新玩法的搭/编排/推进」?

## 范围 IN(app 作者完整参考)

- **需求理解**:用户要什么(范围 / 配置 / 规则 / 使用与运行含运行记录设计)、玩法规则(项目建档优先,缺了官方渠道)、requirement.md 产出。
- **流程探索**:四段式骨架(走查透镜 + 编排骨架,定义在本节)、探索范围长短裁定(长流程只摸入口+中断退出链)、手法引用 `od-dev-write-operation` §2、flow.md 产出(每段带现成 op 复用标注)、无实机推演条款。
- **设计**:op 拆分(operation-flow-x.md 系列 + 四形态复用打包)、自底向上串联(复用 op 也要单独跑一次)、节点图按四段式组织、编排语义(顺序 / 分支 / 循环 / 失败处理必须设计 / 中断恢复)、设计过目(轻量裁决,可与开放点合并一轮)。
- **实现件结构**(§4.4:app 类节点图 + 注册件 const / factory + run_record + config,一次写全)+ **约定式自动注册**。
- **Factory + const + 发现规则**(APP_ID / DEFAULT_GROUP / 第三方插件 / zip)。
- **Config**(`YamlConfig` 子类 + adapter + 实例级)+ **GUI**(setting card interface)。
- **run-record**(`AppRunRecord` + 周期重置 + 业务字段按需求文档登记)。
- **端到端验证**:重启 MCP server → 注册确认 → `run_standalone_app`(主界面起止)+ 待实机核对清单核销。
- **修改与调试**:分层分类(op 内部 / 串联层 / 产品化层 / 不在场排查)+ app 特有症状速查。

## 范围 OUT(指针,不重复)

- 单 op 写法(节点图 / `round_by_*` / 画面判定 / 修改调试)→ `od-dev-write-operation`(app 复用同一套;app 节点图与 round 规范全量同守它,本 skill 不复述)。
- 从零做新玩法全程 → 本 skill(原 gameplay-automation 职责已并入)。
- 画面建档 / screen_info area → `od-dev-screen-onboarding`。
- 用户反馈的运行失败排查 → `od-dev-debug-automation`。
- 任务账本 / 进度结构 → `od-dev-progress-tracking`(本 skill 不内置进度模板)。
- app 设计文档组织 → 所在项目文档规范(本 skill 不内置文档方法论)。

## 构成(文件结构)

- `SKILL.md`:§1 需求理解 → §2 流程探索(开头给四段式骨架=走查透镜,后接探索范围长短裁定 + 手法引用 operation §2)→ §3 设计(3.1 op 拆分设计·operation-flow 系列 / 3.2 逐个 op 实现与验证)→ §4 app 实现(4.1 application-flow.md + 编排语义 / 4.2 补 run_record+config 处理方式·周期标记裁定 / 4.3 固定写迭代设计文档 / 4.4 实现 / 4.5 串联验证)→ §5 迭代实现循环(长流程:推进单元轮次 / 标准八步 / 5.3 重新设计编排独立小节·每轮收尾治本重构 / 中断退出链做轻量验证 / 未知项留钩子)→ §6 策略设计(初版不做·随机或固定方案占位·需要时才引入·简单方案起步→配置性·数据取自官方 wiki 或实机;**策略调优整章不写**——实机单环境无条件做 A/B 统计,2026-11-13 用户裁定)→ §7 端到端验收 → §8 GUI(app 完成后再考虑·默认一条龙配置页承载·独立入口问用户)→ §9 MCP 配置工具(通用工具自动暴露·describe 结构与读写验收)→ §10 修改与调试 → §11 必守规则 → §12 边界 → §13 写完自检(completion gate 统一在文末,开头无 checklist)。
- `references/`:
  - `factory-and-discovery.md`:自动发现规则 + Factory + const + 第三方插件 + zip。
  - `config-and-gui.md`:`YamlConfig` + adapter + 实例级 + setting card + interface。
  - `run-record.md`:`AppRunRecord` + 周期重置 + 子类业务字段。
- `design/`:本目录(overview;ADR 如有则入 decisions/,仅经用户命令创建)。

## 设计动机(why)

- **需求理解与流程探索是两个独立大步骤**(2026-11-13 用户裁定,不可合并成一节):§1 搞清「用户要什么 + 玩法规则」(先读项目建档,缺了去官方渠道调研);§2 实机按四段式只读走查(真实消耗逐次授权)。原「主线比 op 短、没有摸流程对应物」的假设(2026-11-12)被实践推翻——app 需求常先于 op 清单存在,缺这两步会让拆解与编排失据。**所有 app 走同一流程,不分轻重档**(2026-11-13 用户裁定,推翻本日初稿的轻重分级尝试)。
- **全文档平实表述**(2026-11-13 用户裁定,违反过干净读者原则返工):不依赖内部缩语——「落盘 / 快过 / 纸面 / 落对」类词全改平实说法;内部惯用名(op)保留但首次出现给定义;hub 一词整删,统一叫「主界面」(定义 = 进入游戏后停留的第一个画面);「五件套」一词随 §4 拆为「初步实现 / 产品化」两章后不再使用;判据句子展开写全,不压缩。
- **四段式骨架取代主界面起止单句**(2026-11-13 用户给定,后经用户裁定前移至 §2):①导航段(**简单档**=统一回主界面再前往;**精细档**=入口识别在导航路径上则从当前位置继续)/②玩法段/③领奖兑换环节(按玩法裁定有无)/④返回段——原「首 op 回主界面、尾 op 回主界面」一句话不足以指导新 app 的流程组织。**定义放 §2 摸流程处**(2026-11-13 用户裁定):四段式首先是走查的透镜——先知道要摸什么,才有编排骨架;编排落法引用在 §4.1。导航精细档与编排语义表的中断恢复行同源(前者是导航段形态,后者是入口自检跳态,共用同一适用判据)。
- **§4 一章承载「实现到能运行」**(2026-11-13 用户两轮裁定):app 本质也是 operation——op 全部实现后写 application-flow.md(app 级编排设计稿,对标 op 的 nodes.md,含失败处理语义与 run_record/config 处理方式),然后**节点图与注册件一次写齐**(const / factory / run_record / config 按 requirement.md 与节点图一次落地,不留空壳——不注册就无法运行验证),串联验证(重启 server + 注册确认 + run_standalone_app 主界面起止),迭代设计文档沉淀探索产物;§7 端到端验收做产品化行为(周期标记语义 / 一条龙 / 通知 / 待实机核对核销)。曾拆「初步实现 / 产品化」两章的版本把注册件放在验证之后,验证无从运行,作废。
- **失败处理入编排语义**(2026-11-13 用户裁定):子 op 失败后停下还是继续,必须在编排设计时显式裁定并写进设计,禁止运行时即兴——月度 / 批量型 app 静默继续会吞掉真实失败(如兑换缺口)。
- **开头 checklist 删除,completion gate 统一归文末自检**(2026-11-13 用户裁定):同一判据不在开头清单与文末自检两处维护。
- **读数类需求走画面识别 extras 通道**(2026-11-13 用户方向裁定):§3.1 op 拆解判据收录「动作类 → op / 读数类 → ScreenRecognizer → analyze extras」;op 侧正文章节后续批次补进 `od-dev-write-operation`(本 skill 先自含指针)。
- **设计过目取轻量档(3.4)**:对齐 op 侧「agent 自主推进后必有裁决」的哲学,但编排设计通常直接来自用户需求 —— 折中为「非纯顺序编排才报,纯顺序串联免报」(2026-11-12 用户裁定)。
- **假画面回放测试不设必做**:op 各自测试已在 op 侧主线落盘;app = 已验证 op 的串联,强制三层验证性价比低 —— 编排复杂(多分支 / 循环 / 条件跳转)时按「测试只覆盖核心」判据补锁串联结构(2026-11-12 用户裁定)。
- **删除「进度模板」节**(2026-11-12 用户裁定):任务账本单一源在 `od-dev-progress-tracking`,曾内置的进度模板满是账本内部术语且与正文重复 —— 职责归位,整节删。
- **删除「设计文档组织」节 + `app-design-doc.md`**(2026-11-12 用户裁定):文档组织归所在项目文档规范(各项目有自己的双层文档流 / ADR 体系),公共 skill 不内置完整目录方法论;后续(2026-11-13)§4.3 为「迭代设计文档怎么落」内联了**最小骨架兜底**(项目规范没细说时照此搭),与该裁定不冲突——骨架是兜底不是替代。
- **新增修改与调试章**:description 一直承诺「修改或调试」,正文曾只有新建路径;app 特有症状(跑完首节点即结束 / 一条龙跳过 / 改码没变 / 不在列表)原本散落各处,聚成分类表 + 症状速查。
- **必守规则收敛**:原 7 条里 4 条是 op 层规范复述,与「不重复 write-operation」的定位自相矛盾 —— 收敛为一句指针,app 层 5 条留正文。

## 落点

公共仓 `OneDragon-Skills/skills/od-dev-write-application/`,OneDragon 系列通用(SR / ZZZ 等)。各消费方仓库按其 setup 约定挂载。

## 类型(RED / GREEN)

方法论覆盖型(整合 OneDragon app 开发已成型的实践 + 框架 API 成系统流程)→ RED 可省,**GREEN 必做**。

**状态:draft(2026-11-13 合并重构后:§1-§6 经三个场景两代版本实测通过 + gap 回灌,见 evals/TESTS.md;§7-§9(端到端验收 / GUI / MCP 配置工具)待首个真实 app 实装走通后补验;两轮独立子 agent 评审(阻断+应修)已全部修复)**。参考来源:SR 现有 app(world_patrol / sim_universe / trailblaze_power / currency_war)+ 框架 `Application` / `ApplicationFactory` / `AppRunRecord` / `YamlConfig` API + 原 od-dev-gameplay-automation(已废弃并入)。迁公共仓时已泛化项目专属(SrApplication/ZApplication/BackToNormalWorldPlus/大世界/src 路径)为通用说法。
