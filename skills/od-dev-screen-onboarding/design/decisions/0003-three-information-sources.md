# 0003. 信息源三层并用:截图 + screen_info + 代码(含版本迁移核对)

- **Status**: accepted
- **Date**: 2026-08-04(形式化;原始踩坑 2026-07-11 起)

## Context
两个观察:
1. onboard 某基础画面(大世界类)时 doc 漏写左上角菜单按钮 —— 该画面的 screen_info yml 的 `area_list` 本有此 area,但它是纯坐标(无 text / template)不参与 analyze 匹配,**只看截图就漏了**;同期 onboard 另一画面(邮件类)靠读其 screen_info yml 的 `area_list` + app 的 `@operation_node` 链快速理清跳转。
2. 代码层 caveat:onboard 某多 tab 商店画面发现只剩单一 tab,原本的另两个 tab 没了 —— 但对应 op 代码还在点这俩 tab(死代码)。搜官方更新说明:**后续版本移除了这俩 tab**。app 层有占位短路直返「未开启」(config 默认开但不调 op,故无运行错误)。

## Decision Drivers
- **不漏元素**:截图只覆盖「当前帧看得到」的;screen_info 才是该画面全部已建模元素全集(含当前帧未显示的子态 area);代码补画面跳转 / 状态流转。
- **不假设代码 = 当前游戏**:代码可能落后于游戏版本(死代码 / 占位短路)。

## Considered Options
1. **只看截图 analyze/视觉大模型**:漏 screen_info 已建模但当前帧未显示的子态 area。
2. **截图 + screen_info + 代码三层并读**(选中):全集对齐 + 流转理清。
3. **只读代码**:漏画面视觉细节 / OCR 文本。

## Decision
选 2。建档前并读三层:
1. **截图** → `analyze_screen`(客观 area / OCR)+ 视觉大模型(主观布局 / 状态图标)。
2. **screen_info**(`assets/game_data/screen_info/<screen_id>.yml` 的 `area_list`)→ 该画面**全部已建模元素**,含当前帧未显示的子态 area(如弹窗按钮)。每个 area 的 `text` / `template_id` / `pc_rect` / `goto_list` / `pc_alt` / `gamepad_key` 直接说明它是啥、点后跳哪、PC 端怎么点。**analyze 只返回当前帧命中的 area,screen_info 才是全集**。
3. **application/operation 代码**(`src/<project>/application/<app_id>/`)→ `@operation_node` 链 = 画面跳转与状态流转;`round_by_find_and_click_area` / `round_by_goto_screen` 调用 = 在哪画面点哪 area。

**对齐判据**:doc 的「可交互元素」「状态流转」要与 screen_info `area_list` + 代码**逐条对齐** —— screen_info 有、doc 无 = 建档漏,补上。截图没显示的子态 area,先按 screen_info + 代码记入流转、标「待现场快照」。

**版本迁移核对(代码层 caveat,老 app / 大版本更新后必查)**:游戏版本更新会改画面 / UI / 流程。判据:**建档前核对 op 代码假设的画面元素(tab / 按钮 / 流程)在当前游戏版本还在吗** —— 不假设「代码 = 当前游戏」。发现不符:① doc 记版本差异 + 标「代码与当前版本不符」;② 搜官方更新说明确认改动版本;③ app 层若有占位短路(如 `handle_xxx` 直返「未开启」)说明已知情,标「待重写」。教训:上面那个商店 op 基于旧版本 tab(后续版本移除),靠用户观察 + 搜官方说明才发现 —— 代码默认有效是建档盲区。

## Consequences
- **正向**:不漏元素;doc 与 screen_info / 代码对齐;版本漂移能被发现。
- **负向**:三层并读花时间 → 按需:通用流程(大世界 / 菜单 / 任务 / 背包 / 战斗 等基础 UI)代码层可轻读;玩法画面三层全读。
- **边界**:代码层落后由「版本迁移核对」兜底(本 ADR Context #2)。

## Links
- SKILL.md「信息源:理解画面三层并用」。
- 相关:[ADR-0004](0004-vision-required.md)(视觉大模型 也是信息源之一)、[ADR-0001](0001-five-step-flow.md)(五步流)。
