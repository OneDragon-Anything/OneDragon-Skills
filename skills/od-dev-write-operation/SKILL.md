---
name: od-dev-write-operation
description: 当要在一条龙(OneDragon)框架上**新建、修改或调试单个 Operation** 时用 —— 写一个 op(用 `@operation_node` 声明节点、用 `round_by_*` 做画面判定与点击、处理一个画面或一类动作、返回 round 结果),或改/修已有 op 的逻辑与 bug。Use when writing, modifying, or debugging a single Operation on the OneDragon framework — declare nodes via `@operation_node`, detect/click screens via `round_by_*`, handle one screen/action, return round results; includes fixing an op's logic/bugs. 不触发:从零做新玩法(od-dev-gameplay-automation)、搭/改 app 骨架与配置(od-dev-write-application)、**用户反馈的运行失败排查(事后从零重建现场,你没在写那个 op)→ od-dev-debug-automation**。
---

# 写 / 改 / 调试单个 Operation(OneDragon)

OneDragon 的 Operation 是**节点图状态机**:一个 op = 若干 `@operation_node` 节点 + `@node_from` 边。框架每轮截图 → 跑当前节点 → 按其返回的 round 结果沿边找下一节点。**写 op = 把"一类画面 / 一个动作"拆成节点,每节点读屏 → 判定 → 动作 → 返回 round 结果。**

> 全程守「**看(screenshot/OCR)→ 动(click/key)→ 等(sleep)→ 验(再读屏)**」。别凭猜硬写 —— 凭猜只覆盖一种情况、漏另一种,必回归。

## 先认 underlying:自动化开发是探索式(逐画面微循环)

自动化脚本开发 ≠ 普通软件工程,根本区别是**需求不可完备**:面对一个新玩法/新流程,你**不可能一开始就写出完整规格**(分支 / 子状态 / 边缘情况要实机跑才暴露)。工作方式因此是**逐画面的微循环**,不是"规格→实现→交付":

1. **建档先摸大概**(起点):玩法机制 + 主流程经过哪些画面(骨架,不是全集 —— 分支 / 边缘态实机跑才暴露)。
2. **逐画面微循环**(每画面闭环,稳了进下一个):
   - ① **建档该画面**(screen_info area / 模板 + 截图 + doc,按 `od-dev-screen-onboarding`)
   - ② **写该画面的 op**(检测 / 动作,按下面「写一个 op 的主线」)
   - ③ **测试**:`run_operation` 单 op 实操 + 代码测试(fixture / unit 覆盖该画面逻辑 / 分支)
   - ④ **遇预料外 → 补建档 + 补分支**(未建档画面 / 事件 / OCR 误匹配 / 坐标漂移 → 补画面建档 + 补 handler / 分支 / 修 click),循环到**该画面稳定**
   - ⑤ 进下一个画面(多画面按游戏流程顺序推进 = gameplay 层,见 `od-dev-gameplay-automation`)
3. 整体循环到玩法全部画面稳定。

> 这与肉鸽无必然关系 —— **大部分玩法都有分支**(肉鸽只是密)。这是自动化开发的**根本工作方式**,贯穿实现-测试全程。下面所有"为什么 op 要这么写"都由它决定:**op 拆小但别过细**(单跑能定位问题;两头卡判据见「写一个 op 的主线」3)、**决策点多 log 多截图**(一次跑榨取最多信息,因为每次都在暴露建档缺口)、**预料外画面要调研建档**(不是只 ESC)、**调试先读日志**、**重复手动操作建成 op**。

## 写一个 op 的主线(按序)

1. **先找兄弟 op 抄骨架,别从零**。在 `src/<project>/` 找一个职责相近的已有 op(同类画面 / 同类动作),照它的 `__init__` / `handle_init` / 节点结构写。比从零省一个数量级,也符合项目"先复用现有 Operation"硬约束。
2. **要碰的屏先建档,再写逻辑**。op 依赖的每个画面必须先有 screen_info area / 模板 —— 没建档的屏不写逻辑(坐标 / 关键词会全靠猜)。建档走 `od-dev-screen-onboarding`;坐标检测 / 验证走 od-dev-ui-region-detect。
3. **拆节点**:一节点 = 一类画面 / 一个动作。**粒度判据(两头卡)**:太粗——某方法 if-elif ≥ 3 个不同画面/动作,或单 op 超 ~80 行 → 拆成独立 op(便于 `run_operation` 单跑定位失败步);**太细**——拆出来的 op **单跑没法自验证**(单跑看不出对错,要靠上下游 op 才知道流程对不对)→ 太细,这步(读/点单元素)归 op 内函数 / 节点,别拆成 op。op 粒度 ≈ 一次游戏内导航能覆盖的实测单元(难导航的屏,op 该一次做完,别拆细让每 op 都重导航)。一句话:细到单步(读/点)归 op 内函数,粗到多画面就该拆。
4. **每节点**:读屏 → 判定 → 动作 → **返回 round 结果**(语义见下)。
5. **单 op 实测**:`run_operation '<op_id>'` 单跑通过,再接入主流程。测试机制见 `references/testing.md`。

## round 结果驱动节点图(核心心智)

每节点返回 `round_success` / `round_wait` / `round_retry` / `round_fail`(+ `status` / `data` / `wait`):

| 返回 | 框架行为 |
|---|---|
| `round_success(status)` | 沿 success 边找下一节点;无下一节点 → op 成功结束 |
| `round_fail(status)` | 沿 fail 边找下一节点;无下一节点 → op 失败结束 |
| `round_wait` | **重跑当前节点**(等画面变化 / 等动画) |
| `round_retry` | 累计重试当前节点;超 `node_max_retry_times` → 转 FAIL |

`status` 字符串给 `@node_from(status=...)` 精确路由(多出口节点按状态分流)。完整路由规则 / 自环陷阱 / `previous_node` / `handle_init` 见 `references/node-graph.md`。

## op 进出状态核对:入口识别预期屏 + 出口验证真转移

op 是被上层调度的单元。**尤其出口** —— op 一旦 `round_success` 就交出控制权,若其实没完成(转场 click 没落地),**下个 op 就算有入口验证也只能发现"画面不对",没法替你重做这次转场**(不是它的活、也不知点哪)→ 流程卡错屏。故"验转移 + 没转移就自己 retry 到转移"是 op **不可推卸**的职责。

- **入口(op / 节点开始)**:先识别"在预期屏"再操作。op 被进入时不保证画面就对(上 op 转场没落地 / 意外弹窗 / 错状态调来)→ 起手读屏确认是本 op 该处理的屏(id_mark / 独有关键词),**不在 → round_fail / bail**,别在错屏盲点。例外:首动作用 `round_by_find_and_click_area`(先找 area 再点)= 天然先识别,不重复。
- **出口(转场点击后)**:确认"状态真转移了"才 `round_success`。转场 click 可能没落地(MCP 异步 / 游戏卡 / 判拖拽)→ click 后用**任一可靠转移信号**验:目标屏 id_mark 命中 / 本屏 id_mark 消失 / **刚点的按钮或元素消失**(覆盖层关、面板收起)/ 其他稳定锚变化。**信号没出现 = 没转移 → round_retry / round_wait**(自己 retry 到真转移);出现了 = 真转移 → round_success。子态未必有 id_mark —— 用该次转移能用的任何稳定信号即可(见 od-dev-screen-onboarding §3.5)。

**判据:op 进 = 确认在预期屏;op 出 = 确认真转移了。"做了动作" ≠ "达成结果",没达成别 success。**

> 区别于 per-node「看动等验」节奏(节点内部,非边界契约);节点图下游入口核对是**被动发现**(查出"不对"但替你重做不了)—— 出口自检不能指望下游兜底。屏转移检测可靠(有稳定转移信号:id_mark / 元素消失 / 锚变化),默认守;代价(多一次截图+OCR)远小于错屏卡死。

## 循环驱动玩法:flat loop vs node-per-op(结构判据)

写「**外层 loop 不断跑、每轮重新发现状态再推进**」的玩法(自走棋对局 / 肉鸽一层 / 多阶段流程)时,**先选结构** —— 选错会结构性卡死:

| 结构 | 适用(判据) |
|---|---|
| **flat loop**(每轮:截屏→分类"在哪种状态"→一条优先级阶梯选 handler→`round_wait` 重跑) | **纯帧级、无逻辑单元生命周期**的反应式推进(点空白加速战斗 / 结算翻页) |
| **node-per-op**(一个 op 拥有一个**逻辑单元的完整生命周期**;外层只分类 + 委派) | 流程有**逻辑单元生命周期**(开始→处理→结束)+ 单元内**多阶段** + 需要**单元作用域卡死判据**。满足任一即拆 |

**node-per-op 三件套(缺一退化成 flat loop 的卡死)**:
1. **两条正交问题分开**:外层只回答"我在哪种逻辑单元"(小集合分类,委派);node op 只回答"这单元的哪一步"(单元内多阶段)。塞进同一条优先级阶梯 = 优先级脆弱 / LCS 误匹配噪音的根因。
2. **committed-but-verifying**:node op **拥有**单元生命周期(刻意驱动已知阶段),但**每步重核"还在本单元?"**,被意外弹出(进下一单元 / 意外覆盖层)→ bail 回外层。**不是盲目顺序执行**(丢自愈),是"拥有 + 持续核对"。
3. **节点作用域预算 + 完成检测**:node op 有**自己的 retry 预算 + 完成检测**;N 次没完成 = 判定卡死 → **bail / 降级**(退而求其次 / 跳过),不是无限 retry 烧全局预算。预算按单元算。

> ⚠️ **反模式(必踩,两层都中)**:「点了就 `round_success` / 让 loop 继续」**不验画面真推进** → 点不中(坐标落候选间隙 / LCS 误匹配 / click 没落地)→ 覆盖层不关 / 画面没跳 → loop 反复点同一处 → `round_wait` / 外层 loop 重跑**都不计 retry** → 转到 MAX_ITER(可能数小时)才超时。对 **node op**(如多步单元只做了第 1 步却 success)和 **flat loop 的推进型 handler**(关覆盖层 / 翻页 / 点掉弹窗)都成立。**修法统一(三层完成验证)**:点了之后验画面推进(目标消失 / 覆盖层关 / 画面跳 / 锚变化);验不到 → `round_retry`(计节点预算)兜底退出,别盲目 `round_wait` 重跑。一句话:**「点了」≠「成了」**(op 边界出口同此理,见上节;flat loop 合理场景内的底线详见 `references/loop-driven-op-structure.md`)。

**地基:边界检测先于结构** —— 建 node-per-op 前,**先实地确认"单元开始/结束"有可锁信号**(OCR / 模板);边界不稳先补画面建档(`od-dev-screen-onboarding`)再建结构。完整方法论(flat loop 卡死分析 / committed-but-verifying 伪码 / round 结果映射单元生命周期 / 迁移策略)见 `references/loop-driven-op-structure.md`。

## 画面判定与点击:`round_by_*` 选型

**首选判据:要检测/点击的元素在画面上有固定位置吗?**
- **有固定位置**(每次同屏同坐标,如按钮 / 标签 / 卡牌区)→ **建 screen_info area(`pc_rect`),用区域识别**(建 area 方法论见 `od-dev-screen-onboarding`)。这是**压倒性默认(几乎总是)** —— 坐标进 area = 单一真相源 + 不全文扫 = 不误匹配;**不是出问题才用的补救**。
- **全屏 `round_by_ocr` 是 rare last-resort,不是常规 fallback**:仅当元素位置**真运行时漂移且区域定不准**(随机弹出提示、文字位置不固定)才用,**且必带 `lcs_percent=0.7~0.9`** + 画面独有长关键词(误匹配机制见下)。**对固定位置元素用全屏 = 偷懒**(LCS 默认 0.5 会误匹配,见下)—— 用前自问:这元素位置真漂移到圈不准?不然就是偷懒。

| 场景 | 用 |
|---|---|
| 固定位置:判定在不在 | `round_by_find_area` |
| 固定位置:判定 + 点击 | `round_by_find_and_click_area` |
| 已知该处可点、不需判定,直接点 | `round_by_click_area` |
| 漂移/动态文字:只判定 | `round_by_ocr`(`area` 能定就传;必带高 lcs) |
| 漂移/动态文字:判定 + 点击 | `round_by_ocr_and_click`(`area` 能定就传;必带高 lcs) |
| 多目标按优先级点一个 | `round_by_ocr_and_click_by_priority` |
| 导航到某画面 | `round_by_goto_screen`(按 screen_info route) |

> ⚠️ **全屏 OCR(`round_by_ocr*` 不传 `area`)= 偷懒 + 误匹配高发,仅 rare last-resort**。框架默认 `lcs_percent=0.5`(子序列匹配):关键词与同屏/邻屏文字**共享 2+ 字子串即 ≥ 0.5 误匹配**(≤4 字短词天然高危)。**写前自查:这关键词在别的屏 / 同屏别处也会出现吗(子序列 / 全等)?是 → 必用 area 位置区分**(id_mark area)—— `lcs` 收紧**救不了全等 / 高重叠子序列**(别处 4 字全等 = LCS 1.0,提多高都误匹配),只有 area 的位置约束能根治。固定位置元素别用全屏;确需全屏(位置真漂移)必带 `lcs_percent=0.7~0.9` + **确认该词不在别屏全等出现** + 独有长关键词。逐 helper 语义 + 关键参数 + LCS 机制见 `references/round-by-helpers.md`。
- **别在 op 代码里硬编码 `Point(x,y)` / `Rect(...)` 做检测/点击**:坐标进 screen_info area(`pc_rect`),与「坐标进 screen_info」规范一致 —— 检测的文字 + 点击目标分离时(检测用 OCR、点的是另一处),点击坐标同样进 area。

## 选择类画面 op:通常 选择→推进;多选重试才需识别选中态

- **通常:选择 → 推进,不必检测选中态**。点选项 → 点推进按钮往前走即可(推进按钮未必叫「确认」)。选中态往往没明显标记、不好认,硬验反而容易判错添乱。**要校准的是"点哪儿能选中"** —— 选项上可能挂着图标、按钮、预览图等子区域,点选项主体 = 选中,但点到子区域可能开详情 / 触发刷新而跑偏;所以**实测**定准选中位置的坐标,存进 screen_info area(见 od-dev-screen-onboarding §3.6)。
- **多选 + 某次点击没选中 → 重试时才需识别选中态**。多选时 click 没落地 → 选不够 / 没法推进 → 流程重试;这时大概率要**先取消原选择再重选**(避免叠加 / 错位),取消前得**识别当前哪些已选中** —— 方法见 od-dev-screen-onboarding §3.6(呈现多样别预设)。

一句话:默认选择→推进,别过度检测;只有多选重试要"取消重选"时,才需识别选中态。

## op 与 reader 内工具

- 截图:`self.screenshot()` 截并存 `self.last_screenshot`;`save_screenshot()` 落盘调试。
- 点击 / 按键:`self.ctx.controller` 的 `click(pos)` / `mouse_move(pos)` / `btn_tap(key)` / `active_window()`。
- OCR:`self.ctx.ocr_service.get_ocr_result_list(image, rect=..., crop_first=...)`(区域 OCR;⚠️ 是 `ocr_service` 不是 `ocr` —— `ctx.ocr` 是裸匹配器无此方法。`crop_first=True` 先裁再识别,与全屏行为可能不一致,分开验)。
- 调子 op:`op = 子Op类(self.ctx)`(构造传 ctx)→ 节点里 `op.execute()` → `self.round_by_op_result(op_result)` 转 round 结果。
- 非节点上下文判定画面 / area(reader / 纯函数层,无 round 上下文):用 `one_dragon.base.screen.screen_utils` 底层原语(`find_area` / `is_target_screen` / `find_and_click_area` 等,与 `round_by_*` 同源同纪律,别手写裁 rect + 裸 OCR;**文字判定同样优先建 text area 走 `find_area`,裸文本 `find_by_ocr` / 全屏是 last-resort;建 area 见 `od-dev-screen-onboarding`**);两级判定粒度 + 完整对照表见 `references/round-by-helpers.md`「非节点上下文」节。op 节点内仍首选 `round_by_*`(带 round 路由)。

## 必守不变量(反复发作的坑 + 探索式开发的技术)

1. **MCP click/key 异步**:立即返回但 ~1s 才落地;操作后 `sleep ~1.5s` 再验(数字对齐 framework-pitfalls 坑 2),否则截到点击前画面。
2. **调试先读日志,不够就补日志**:bot 卡住 / op 失败 → 先读 MCP server 日志(项目 `.debug/` 下;实际 OCR / 走到哪个节点 / 决策状态),别盲点坐标。日志解释不了 → 在决策点补日志(OCR 摘要 + 点击坐标 + 分支结果)+ `save_screenshot()` 存图。**改前先形成假设、一次只改一个变量、定位根因才修**(别连续换补丁碰运气;详 `references/runtime-craft.md` 调试纪律)。
3. **画面操作以点击为主,禁用键盘 ESC,其余按键尽量不用**:op 里不写 `controller.esc()` / `btn_tap('esc')` —— 关闭、返回、退出、跳过一律 screen_info 建档 + 坐标点击;其余键盘输入(移动/交互键)默认不用,确无点击替代时注释声明键名与原因(留待点击替代后移除)。理由:**前向兼容手机模拟器端**——模拟器无键盘,一切画面操作靠点击,今天多按一个键就是明天多一处适配返工。预料外画面先调研"上一步代码点了什么 → 落到哪个 UI 元素 → 游戏对该元素的交互",**用该画面自己的关闭/返回控件**(建档后 click 避开误触元素);找不到可见控件就报告现场等裁决,不许顺手按 ESC。
4. **多样本核实**:验证 OCR / 读取器跨多样本看统计分布,别凭一张图 / 单次推断下结论(量级参考:每个画面状态 1-2 张典型 fixture,见 `references/testing.md`)。
5. **决策点多 log 多截图(信息密度论)**:探索式开发里每次实跑都在暴露建档缺口,要从一次跑榨取**最多信息**(OCR 到啥 / 评估了啥 / 点了哪 / 结果 / 关键分支截图),而非跑一次只找一个坑。**判据:实跑后看日志能复盘每个决策点发生了什么**;做不到 = 日志不够,补。验证通过后逐步去掉减开销。详 `references/runtime-craft.md`。
6. **重复手动操作 → 尽早建成 op**:开发/测试中同一手动操作做了 2+ 次(导航序列 / 退出对局多页 / 进玩法入口)→ 建成 op(`run_operation` 一键调),别每次手动点 N 个按钮。

> 框架级踩坑完整清单(拖拽误判 / MCP 异步 / ONNX 并发 / 配置生效 / 录屏 / GBK 日志 / LCS 误匹配 / 瞬态残影假阳 / 阈值灰区假 MISS 等)见 `references/framework-pitfalls.md`(single source;od-dev-gameplay-automation 也引用它)。

## 边界(这些去别的 skill)

- 从零做新玩法全程 → `od-dev-gameplay-automation`
- app 产品化(factory / config / GUI / run-record / app 编排)→ `od-dev-write-application`
- 建一张屏的机制 → `od-dev-screen-onboarding`
- 修复决策(已定位后怎么修:介入点选型 / 根因挖多深 / 临时 vs 永久 / 多方案横评)→ `od-dev-deciding-a-fix`
- 用户反馈的运行失败排查(你不在场,从零重建现场:找对进程日志 / run_record 判死活 / 数重复记录)→ `od-dev-debug-automation`;**「run 被莫名停掉 / 提前停止 / status 显示人工结束 / sentinel flag 删了又生」的死因排查也走它(§1「run 被停→判死因」四层序——即使是开发中自己埋的钩子干的)**;op 内调试纪律见本文「必守不变量」+ `references/runtime-craft.md`

## 写完自检

- [ ] 碰到的屏都建了档(screen_info area / 模板),检测/点击坐标进 area、不是凭猜 / 硬编码 `Point(x,y)`?
- [ ] op 粒度两头卡——太粗(if-elif ≥ 3 画面/动作、超 ~80 行)拆开;太细(单跑没法自验证、读/点单步)归 op 内函数不拆 op?能 `run_operation` 单跑定位失败步?
- [ ] 固定位置元素用区域识别(`round_by_find*_area`);全屏 OCR 只在位置真漂移 / 区域定不准时 last-resort(带高 lcs + 独有关键词),不是常规 fallback?
- [ ] 全文零 ESC 键输入(`esc()` / `btn_tap('esc')` 均无);其余键盘输入已最小化(确需用有注释声明);关闭/返回/退出走建档坐标控件?
- [ ] 用 `round_by_ocr*` 全屏前自查过:**这关键词在别的屏 / 同屏别处也会出现吗(子序列 / 全等)**?是 → 用 area 位置区分(`lcs` 收紧救不了全等 / 高重叠子序列,见上)?
- [ ] 决策点有日志 + 存图,卡了能复盘(信息密度)?
- [ ] 单 op `run_operation` 实测通过再接入?
- [ ] 循环驱动玩法选了正确结构(flat loop / node-per-op)?node op 有完成检测 + 节点预算,不会"完成不了也 `round_success`"假完成;flat loop 推进型 handler 也点了验推进、没推进 `round_retry` 兜底(三层都守「点了≠成了」)?

## 进度模板(本 skill 任务怎么算完成)

> 配合 `od-dev-progress-tracking`(账本状态机 + 状态词 + §12 叶子表 + §2 两级结构)+ `od-dev-gameplay-automation/references/progress-tracking.md`(模块归属语义,op 任务挂所属画面域的流程账本内)。本 skill 负责 **op 类任务**(画面子任务②op / ③run_op / ④代码测试)的完成判据 + 防跑偏点。状态用 progress-tracking 状态词。
>
> ⚠️ **编号体系声明**:下表的 ②op / ③run_op / ④代码测试 沿用 `od-dev-gameplay-automation` **做法二**的画面子任务编号,与本文上方「逐画面微循环」的 ①-⑤(①建档 ②写op ③测试 ④补分支 ⑤进下一个)**是两套体系,数字含义不同,勿混用**;跨体系对进度时以账本任务行为准,别按数字想当然。
>
> ⚠️ **一个画面的 op 工作 = 多步任务(任务行+缩进子行),不是单行叶子**:一个画面常有**多个 op**(读信息 op / 动作 op / 不同子态 op),按 progress-tracking §2「≥2 子步骤 → 缩进子任务行」→ **在流程账本建画面 op 任务行,每个 op 一个缩进子行**(行经 progress.py write 写入)。下表给的是**单个 op 级别**的叶子判据(op 编写② / run_op③ / 测试④ 是单个 op 的三步,全过 = 该 op 闭环);多 op 画面的任务行聚合所有子行状态。单 op 画面可直接用下表三行作子任务,或作合法聚合行(带判据指针)。

| 单 op 叶子(→progress-tracking §11) | 已过判据(指本 skill) | 特有防跑偏点 |
|---|---|---|
| op 编写② | §写一个op主线:节点图 + round 结果语义 + §op进出状态核对(入口识别预期屏 + 出口验真转移) | op 粒度两头卡(§主线3:太粗 if-elif≥3 画面/动作拆、超~80行拆;太细单跑没法自验证归 op 内函数);"做了动作"≠"达成结果",出口没验真转移别 success |
| run_op 实测③ | §主线5 + §写完自检:`run_operation '<op_id>'` 单 op 实测通过再接入主流程 | **代码写完 ≠ 过,必须 run_op 单 op 实测**(最易跳过的一步) |
| 代码测试④ | `references/testing.md`:fixture + unit 覆盖该画面逻辑/分支 | 写 mock 断言前先读 node 返回类型语义(§round结果驱动节点图:`round_success`/`round_fail`/`round_wait`/`round_retry` 路由不同、判法不同),别照搬别的 app |

- **状态记录**:单个 op 的 ②op / ③run_op / ④测试 各一叶子,用 progress-tracking 状态词;该 op 三者全过 = **该 op 闭环**(合法聚合行,行文法见 od-dev-progress-tracking §3,行经 progress.py write 写入)。**多 op 画面**:op 目录聚合所有 op 子节点全过 = 画面级 op 工作(**≠ 画面闭环**;画面闭环还需 ①建档 + ②-⑤ 全过 + 罕见态 + 假绿,见做法二分纲 §1.2 画面闭环判据)。
- **跑偏信号(本 skill)**:op 卡住没先读日志就盲改坐标;ESC 键输入(§必守3 禁令)或预料外画面没调研就动手;循环驱动玩法没选结构(flat loop / node-per-op)就写。
