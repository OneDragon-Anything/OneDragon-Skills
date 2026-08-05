# 0004. 区域识别为默认首选(全屏 OCR 降为 fallback)

- **Status**: accepted
- **Date**: 2026-08-05

## Context

`round_by_*` 选型表原本把 `round_by_ocr_and_click` / `round_by_ocr`(全屏 OCR)列在「OCR 找文字并点击 / 只判定」场景的第一行,等于**默认首选全屏 OCR**;「固定位置识别(screen_info area)」框在 OCR 误匹配的「根治」里(出问题才用的 reactive 补救)。

全屏 OCR + LCS 子序列匹配(框架默认 `lcs_percent=0.5`)是**结构性脆弱**:关键词与同屏/邻屏任意相似文字共享 2+ 字子串即 ≥ 0.5 误匹配。把它当默认 = 让 op 作者默认踩一个可避免的坑。

**实战验证**:某 loop-driven 自走棋类玩法用 `round_by_ocr('<4 字关键词>')` 默认 lcs 0.5,把**邻屏共享 2/4 子序列的相似标签**误匹配(LCS = 0.5)→ handler 在错误画面瞎点 → flat loop 卡死(iter63+)。止血(lcs 提到 0.9)治标;**根因是默认选了全屏 OCR,而该元素有固定位置**(本应区域识别)。(具体玩法决策见该玩法的决策日志,本 ADR 不引跨仓 / 本地路径。)

## Decision Drivers

- **结构性规避 > 依赖审查**:全屏 OCR 误匹配是结构性脆弱(换关键词还会撞别的);区域识别对固定位置元素是结构性规避(不全文扫 = 不误匹配)。让作者默认走结构性稳妥的路,而非依赖每次审查 LCS 共享子串。
- **与「坐标进 screen_info」规范一致**:固定位置 UI 的坐标本就该进 screen_info area(`pc_rect`),区域识别顺势用同一 area,单一真相源。
- **泛化**:任何固定位置 UI 元素(按钮 / 标签 / 卡牌区)都该优先区域识别 —— 判据是方法论(位置固定 vs 漂移),不绑具体玩法。

## Considered Options

1. **保持全屏 OCR 默认,误匹配靠关键词审查 + 高 lcs 补救**(原状):pro 是 op 写起来快(不用先建 area);con 是依赖作者每次审查 LCS 共享子串,漏审必踩,全屏扫描结构性易撞。
2. **区域识别为默认首选,全屏 OCR 降为 fallback**(选中):pro 是固定位置元素不全文扫 = 结构性不误匹配,且 area 是坐标单一真相源;con 是固定位置元素要先建 screen_info area(多一步前置建档)。
3. **删除全屏 OCR 行,只留区域识别**:过度 —— 文字位置运行时漂移 / 动态弹出的场景(随机提示等)没有固定 area,全屏 OCR + 高 lcs 是唯一选项。

## Decision

选 **2**。选型判据从「用什么技术(OCR vs area 找图)」改为**「元素在画面上有没有固定位置」**:
- 有固定位置 → 先建 screen_info area,走区域识别(`round_by_find_area` / `round_by_find_and_click_area` / `round_by_click_area`)—— 默认首选习惯。
- 位置漂移 / 动态 → 才用全屏 OCR(`round_by_ocr*`),必带 `lcs_percent=0.7~0.9` + 独有长关键词。

SKILL.md 选型表按位置判据重排(固定位置场景置顶),LCS 误匹配说明从「根治补救」改述为「全屏 fallback 的必带防护」;op 代码硬编码 `Point(x,y)` / `Rect(...)` 做检测/点击也归入「坐标进 area」(检测用 OCR、点击另一处时,点击坐标同样进 area)。

## Consequences

- **正向**:固定位置 UI 默认走区域识别 = 结构性规避误匹配;与「坐标进 screen_info」「要碰的屏先建档」主线一致;坐标单一真相源。
- **负向**:固定位置元素需先建 screen_info area(多一步前置建档;但主线本就要求「要碰的屏先建档」,非新增负担)。
- **follow-up**:GREEN 验证 —— 写 op 时是否对固定位置元素默认区域识别、仅动态文字才全屏 OCR + 高 lcs。

## Links

- SKILL.md「画面判定与点击:`round_by_*` 选型」(位置判据置顶)。
- `references/round-by-helpers.md`(LCS 机制 + 首选区域识别)。
- 相关:[0002](0002-exploratory-spine-op-level-consolidation.md)(主线「要碰的屏先建档」)。
