# 0005. click 与鼠标移动无间隔(判拖拽):从项目专属措辞改为泛化条件式提示

- **Status**: accepted
- **Date**: 2026-08-05

## Context

本 skill 原把「`before_screenshot` 每轮移鼠标到角落 → 紧接的 click 被游戏判拖拽落空」作为一条**必守不变量**,措辞**预设了「controller 会在 before_screenshot 移鼠标」**。这条原沿自某项目的内部 bug 记录,连命名也带项目内部编号色彩。

核实框架代码后:`before_screenshot` 的**框架基类是空操作**(`pass`);「截图前移鼠标」是**项目 controller 的覆盖行为**(截图卫生 —— 把光标移到角落避免进画面 / 挡 OCR 区),不是框架公共行为。各项目是否覆盖不一:有的项目覆盖了(会移),有的项目直接用基类空操作(不移)。

两个问题:

1. **项目专属泄漏**:公共 skill 用预设「鼠标会移」的措辞教这条坑,对「不移鼠标的项目」不成立 = 把某项目的 controller 覆盖细节泄漏进了公共 skill(违反公共 skill 泛化约束)。
2. **诱导滥用**:即便在「会移鼠标」的项目里,这条坑也是**间歇**的(多打 `round_by_ocr_and_click` / 过渡按钮 / 结算翻页),多数自动运行 click 正常。原措辞写成必守、配「关键 click 前 mouse_move」自检 → 易诱导每个 op 都铺 mouse_move 缓解(代码污染)。

## Decision Drivers

- 公共 skill 不绑项目专属 controller 行为(基类空操作 vs 项目覆盖)。
- 这条坑的**根因是通用的**:click 与鼠标移动之间没间隔 → 游戏判拖拽。`before_screenshot` 移鼠标只是**其中一个来源**,不是唯一、也不是必然发生。
- 别诱导滥用缓解(多数 click 正常,间歇落空处才加)。

## Considered Options

### A. 泛化条件式提示 + `before_screenshot` 作举例(本决策)

SKILL.md 不再列为必守不变量(删条 + 删自检);`framework-pitfalls.md` 留一条「click 与鼠标移动无间隔 → 判拖拽(通用;举例:截图卫生移鼠标)」:根因通用 + `before_screenshot` 作举例 +「先查你项目 controller 移不移鼠标」+「别滥用,手动测不稳先怀疑人抢鼠标」。

- ✅ 不泄漏项目专属(条件式 + 举例,不预设)。
- ✅ 通用根因对任何点游戏的 OneDragon 项目都成立。
- ✅ 防滥用。

### B. 整条删除

- ❌ 删掉真机制 + 仍有项目在用的缓解依据;未来读者遇间歇落空无 awareness。

### C. 保留原必守措辞

- ❌ 预设「鼠标会移」,对不移鼠标的项目不成立 = 项目专属泄漏 + 诱导滥用。

## Decision

选 **A**:从「必守不变量(预设鼠标会移)」降级为「`framework-pitfalls.md` 的泛化条件式提示(根因通用 + `before_screenshot` 作举例 + 先查你项目)」。SKILL.md 必守不变量条 + 自检条删除;`framework-pitfalls.md` §1 改写为泛化条件式;其它引用(gameplay-automation / runtime-craft / testing / overview / writing-skills 的术语举例)同步去项目专属化。

## Consequences

- **正向**:公共 skill 不再泄漏项目专属 controller 行为;通用根因对所有项目有用;防缓解滥用。
- **代价**:原项目内部命名作废(不属公共);依赖它的引用一并清理。
- **项目侧**:controller 确有此覆盖的项目,其**本地开发文档**(项目 CLAUDE.md / insights)保留针对自己的精确描述;公共 skill 只给泛化判据。两边各归其位。
- **推翻它会碎什么**:退回必守(C)→ 重把项目专属泄漏进公共 + 诱导滥用;整删(B)→ 丢真机制 awareness。

## Links

- 相关 design 章节:`../overview.md`(op 粒度规范 / 框架踩坑清单)
- 落点:`../../references/framework-pitfalls.md` §1
