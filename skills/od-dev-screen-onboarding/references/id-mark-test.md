# id_mark 准确性测试方法论

> 项目测试仓**应提供** id_mark 准确性测试;若缺,照本方法论建。SKILL.md §6 归档后跑它验本屏,亦可作全 corpus 回归(抓跨屏碰撞 + 改屏后 id_mark 漂移)。

## 测什么

每个**有 id_mark 的 screen** 验两件:

1. **真阳性**:该屏 id_mark 在**自家 fixture** 全命中 —— 自家都认不出 = id_mark 坏 / fixture 非该屏。
2. **无碰撞**:该屏 id_mark **不**在**别屏 fixture** 全命中 —— 两屏 id_mark 互相串 = 撞车,bot 会误识别。

## 怎么写

框架提供 `is_target_screen(ctx, screen, screen_info)`(= "该屏所有 id_mark 全命中?",`get_match_screen_name` 的底层),测试调它:

1. **自动发现 fixture**:glob 测试仓 `screens/<screen>/<state>.webp` → `(screen, state)` 列表(`screen` = 目录名 = `screen_info.screen_name`)。新建档自动进测试,免维护清单。
2. **每张 fixture 参数化**:
   - `get_screen(screen)` 拿 screen_info;**None → skip**(孤儿 fixture,未建 screen_info)。
   - **无 id_mark → skip**(走模糊 top_n,不测 id_mark)。
   - 读 fixture 图。
   - **真阳性**:`assert is_target_screen(ctx, img, screen_info=本屏)`。
   - **无碰撞**:遍历所有别的 id_mark'd screen,收集 `is_target_screen(ctx, img, screen_info=别屏)` 为 True 的;`assert not collisions`。
3. **失败信息说清**:真阳性失败 → "本屏 id_mark 未命中";碰撞 → "本屏被 [X, Y] 撞车 → 加独有 id_mark"。

成本:n 张 fixture = n 次匹配调用(框架内部对全屏比),**线性**;`is_target_screen` 早退(非命中屏只查第一个 id_mark),离线 mock 可接受。

## 约定配合(避免假红)

- **遮挡 id_mark 的子态 → 独立 screen_info**(见 SKILL.md §3.5):有自己 id_mark 的进测试;纯覆盖层无 id_mark 的自动 skip。
- **无 screen_info 的 fixture → skip**:孤儿,该建 screen_info(SKILL.md §3.5 SCREEN 层全建)。

## 何时跑

- **建档归档后**(SKILL.md §6):`pytest -k '<本屏>'` 只测本屏,即装即验。
- **corpus 回归**:全 fixture,抓跨屏碰撞 + id_mark 漂移(改屏后)。

## 不测什么

- **模糊匹配(top_n)**:设计内行为,非 id_mark bug;本测试只测 id_mark(全中)。
- **无 id_mark 的 screen**:不靠 id_mark 识别,跳过。
