# `round_by_*` helper 家族(reference)

> 本 skill(`od-dev-write-operation`)的 situational reference。SKILL.md 给选型表,本文件给逐 helper 语义 + 关键参数,末节给**非节点上下文的无 round 底层原语对照**。

所有 helper 都返回 `OperationRoundResult`(success / wait / retry / fail),直接 `return self.round_by_xxx(...)` 即可。**两个基础参数**: `screen` = 当前截图(图像); `screen_name` / `area_name` = screen_info 的画面名 / 区域名(字符串)。**`screen` 是否必传因 helper 而异**(下文各签名如实呈现;可省 = 不传时自动截新图)。通用参数:`success_wait` / `success_wait_round`(成功后等)、`retry_wait` / `retry_wait_round`(retry 时等)、`pre_delay`(动作前等)、`color_range`(限定文字颜色)、`crop_first`(区域 OCR 先裁再识别)。

## OCR 类(找文字)

### `round_by_ocr_and_click(screen, target_cn, area=None, lcs_percent=0.5, ...)`
OCR 找 `target_cn` 文字 → 点其中心。找不到 → `round_retry`;点失败 → `round_retry`;点到 → `round_success(target_cn)`。
- `area`:限定搜索区域(`ScreenArea`)。**不传 = 全屏搜**(易撞同类文字,见 LCS 坑)。传 area = 固定位置识别,稳。
- `lcs_percent`:子序列匹配阈值,默认 **0.5**(松,易误匹配)。真匹配 1.0 不受提高阈值影响;收紧到 0.7~0.9 杀假匹配。
- `offset`:点击位置偏移。
- `remove_whitespace`:匹配前清空白(应对 OCR 多/少空格)。

### `round_by_ocr(screen, target_cn, area=None, lcs_percent=0.5, ...)`
只判定 `target_cn` 在不在,**不点**。在 → `round_success`;不在 → `round_retry`。用于"等某文字出现再进下一节点"。

### `round_by_ocr_and_click_by_priority(target_cn_list, ignore_cn_list=None, ...)`
按 `target_cn_list` **优先级**找,点第一个命中的。`ignore_cn_list` 防"已领取"误匹配"领取"这类(列出来不实际点)。多目标选一时用它。

## screen_info area 类(找固定 UI)

### `round_by_find_and_click_area(screen=None, screen_name, area_name, until_find_all=None, until_not_find_all=None, ...)`
在 `screen_name` 画面的 `area_name` 区域找(模板 / OCR)→ 点(`screen` 可省,不传自动截新图)。**带后验**:
- `until_find_all=[(screen_name, area_name), ...]`(字符串对):点了之后等这些区域都出现才算 success(没出现 → `round_wait` 继续点)。
- `until_not_find_all=[...]`(同类型):点了之后等这些区域都消失才算 success。
- 适合"点按钮 → 等画面切换"的场景(点完没切换会重试点)。

### `round_by_find_area(screen, screen_name, area_name, ...)`
**只判定** area 在不在(不点;`screen` 此处**必传** —— 先 `self.screenshot()` 再调)。在 → `round_success`;不在 → `round_retry`;区域没配置 → `round_fail`。

> ⚠️ `round_by_find_area` **只检测不点击**。要点必须用 `_and_click` 版或自己 `controller.click`。别拿 find 版当点击用。

### `round_by_click_area(screen_name, area_name, click_left_top=False, ...)`
**不判定,直接点** area 的中心(`click_left_top=True` 点左上角)。area 没配置 → `round_fail`。已知该处可点、不需判定时用它(最快)。

## 导航类

### `round_by_goto_screen(screen_name=None, ...)`
按 screen_info 的 route 从当前画面导航到 `screen_name`:识别当前画面 → 找路径 → 点路径上第一个跳板 area → `round_wait` 等切换 → 循环到目标画面。到 → `round_success`;识别不出当前画面 → `round_retry`;无路径 → `round_fail`。依赖 screen_info 的 screen route 数据。

## OCR 关键词与 LCS 匹配机制(必懂)

框架 OCR 匹配用 **LCS(最长公共子序列)/ 目标长度 ≥ `lcs_percent`**,不是"子串包含"。后果:
- 中文关键词与**别的画面文字共享 2+ 字子序列**就可能 ≥ 0.5 误匹配。例:4 字关键词与别处共享 2 字 → 2/4=0.5 命中。**≤4 字关键词天然高危**(共享 2 字即触默认阈值)。
- 全屏 `round_by_ocr*`(不传 `area`)天生易撞 —— 画面任何位置的同义文字都算。

**首选:固定位置元素用区域识别,不碰全屏 OCR**(SKILL.md 选型判据)。固定位置 → 建 screen_info area → `round_by_find*_area`,或给 `round_by_ocr*` 传 `area`(只在固定位置识别,不全文扫)。

**两个独立的误匹配高危信号(任一命中 → 必用 area,`lcs` 救不了)**:
1. **关键词在别的屏 / 同屏别处也出现**(作为子序列,甚至全等):典型如某关键词既是要找屏的标题,又是别屏的对局信息 / 描述 / 标签(共现)。**全屏 OCR 无法区分是哪个屏** → 必用 area 的**位置**区分(id_mark area:目标屏关键词在固定 `pc_rect`,别屏的同名文字在别的位置 → 不命中)。
2. **关键词短(≤4 字)且无更独有长形可用**:短词天然易共享子序列(见上)。

⚠️ **`lcs_percent` 收紧不是万能止血** —— 它只杀**低重叠**假匹配(2/4=0.5 这类);对**高重叠 / 全等子序列**(4 字关键词命中别处 4 字全等文字 = LCS 1.0)无能为力,阈值提多高都误匹配。故「关键词可能在别屏全等出现」→ **只有 area 的位置约束根治,`lcs` 档不住**。「多屏共现」因此是比「位置固定吗」更直接的误匹配预测信号:写 `round_by_ocr(keyword)` 前先自查「这词在别的屏 / 同屏别处也会出现吗?」是 → area。

**确需全屏 OCR(fallback:位置漂移 / 动态)时的两档修**:
1. **止血**:传 `lcs_percent=0.7~0.9`,或换更长 / 更独有关键词(完整标题而非两字词)。**前提:先确认该关键词不会在别屏全等 / 高重叠出现**(否则 `lcs` 档不住,见上,只能 area)。
2. **收紧**:能圈出大致区域就传 `area` 缩范围(哪怕不精确),减少撞同屏文字的概率。

判据:同 loop / 同画面里所有中文关键词都要审**共享子串 + 别屏共现**,不只改一个就收工。

## 非节点上下文:无 round 的底层原语(reader / 纯函数层)

reader / 纯函数 / 画面状态判定层**没有 round 上下文**(无 `self.round_*` 路由,只拿 `ctx` + 截图,返回 bool / enum),`round_by_*` 用不了 —— 用它们在 `one_dragon.base.screen.screen_utils` 里的底层原语。**原语与 `round_by_*` 同源同款「固定位置 → screen_info area」纪律**:原语吃 screen_info 档案(area / id_mark 即档案区),全屏 / 短词的 LCS 误匹配纪律(上节)同样适用 —— **不是「自己裁 rect + 裸 OCR / 裸模板」的许可证**。

| 判什么 | 原语(非节点上下文) | round 对应(op 节点内) |
|---|---|---|
| 是不是某画面(id_mark 全中) | `is_target_screen(ctx, screen, screen_name)` → bool | `round_by_goto_screen` 内部链路 |
| 当前是哪个画面 | `get_match_screen_name(ctx, screen)` → 画面名 | 同上 |
| 屏内某 area 在不在(子态判定) | `find_area(ctx, screen, screen_name, area_name)` → `FindAreaResultEnum` | `round_by_find_area` |
| 已持有 ScreenArea 对象(临时区域 / 遍历 `area_list`) | `find_area_in_screen(ctx, screen, area)` | 同上的底层 |
| 某文字在不在 | ⚠️ **优先:固定位置文字建 text area 走上行 `find_area`**(关键词 / 阈值进档案;建 area 方法见 `od-dev-screen-onboarding`);`find_by_ocr(ctx, screen, target_cn, ...)` 裸文本是 last-resort(同 `round_by_ocr` 全屏纪律:必传 `area` 缩范围 + `lcs_percent=0.7~0.9`) | `round_by_ocr`(同纪律) |
| 判定 + 点击 | `find_and_click_area(ctx, screen, screen_name, area_name)` → bool(是否点中) | `round_by_find_and_click_area` |

**判定粒度判据(两级,选对级)**:
- 验「**在不在某画面**」(跨屏区分)→ 画面级 `is_target_screen`:该画面**全部 id_mark 命中**才算,天然抗别屏误匹配。
- 验「**同屏内的子态**」(面板展开 / 收起这类,两子态共享同一批 id_mark,画面级分不出)→ area 级 `find_area` 锚点(area 选**只在目标子态命中**的)。

**纪律**:
- **文字判定优先档案区,裸文本原语是 last-resort**:`find_by_ocr`(裸文本关键词)与全屏 `round_by_ocr*` 同款误匹配面 —— 默认 `lcs_percent=0.5` 且无位置约束,同屏 / 邻屏文字共享 2+ 字子串即命中(机制见上节)。固定位置文字**先建 text area 走 `find_area`**(关键词 / 阈值 / 颜色范围进 screen_info,单一真相源;**建 area 的方法论(upsert_screen_area / pc_rect 定位 / 文本 vs 模板)见 `od-dev-screen-onboarding`,别在 reader 里裸手拼**)。`find_by_ocr` 只在位置真漂移 / 区域定不准时用,且必传 `area` 缩范围 + `lcs_percent=0.7~0.9`。
- op 节点内**别绕开 `round_by_*` 用原语** —— 丢 round 路由 / 重试语义;原语只给非节点上下文。
- `find_area` 返回 `FindAreaResultEnum` 时,`AREA_NO_CONFIG`(区域没配置,先补 screen_info)与 `FALSE`(没命中)是两回事,别混处理。
