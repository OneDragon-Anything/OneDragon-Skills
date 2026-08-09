# 框架级踩坑(op 作者视角,reference)

> 本 skill(`od-dev-write-operation`)的 situational reference。这些是 op 里反复发作的 **one_dragon 公共框架**行为,遇过就守;SR/ZZZ 等 OneDragon 系列共有。SKILL.md 列了最频发的;本文件给完整 + 缓解。
> **单源**:本文件是框架踩坑清单的唯一源;`od-dev-gameplay-automation` 也引用它(不重复维护)。

## 1. click 与鼠标移动无间隔 → 被游戏判拖拽(通用;举例:截图卫生移鼠标)

游戏会把「按键按下期间 / 刚 click 后没间隔的鼠标移动」判成拖拽 → click 落不到目标。间歇发生,多打 `round_by_ocr_and_click` / 过渡按钮 / 结算翻页这类。

- **通用根因**:click 和鼠标移动挨得太近(移动发生在 click 过程中,或 click 后立刻移动),游戏分不清单击还是拖拽。
- **举例(常见来源之一)**:有的项目 controller 在 `before_screenshot` 把光标移到角落(截图卫生,避免光标进画面 / 挡 OCR 区)。这类项目里 op 截图后紧接 click(target),光标从角落移动到目标的过程 =「click 过程中移动」→ 判拖拽。**先查你项目**:controller 的 `before_screenshot` 移不移鼠标?(框架基类是空操作,有项目覆盖移鼠标才会这么触发。)
- **缓解**:关键 click 前 `mouse_move(target)` 再 `click`(click 时光标已到位、零移动,不被判拖拽);或 click 后留间隔再移鼠标。
- **别滥用**:多数自动运行 click 正常,只在观察到间歇落空处加,别每个 op 都铺。
- 手动测 click 不稳,先怀疑你自己在抢鼠标,别急着归框架 bug 铺防御。

## 2. MCP click / key 异步

`click_game` / `key_tap` 立即返回,但 ~1s 后才落地。操作后**必须 `sleep`(~1.5s)再读屏验证**,否则截到点击前画面 → 误判还在原画面 → 乱导航 / 乱重试。坐标用 screen_info 精确值,别凭目测。

## 3. ONNX session 异步走 `gpu_executor`

OCR / 检测等 ONNX session 的异步调用必须经 `one_dragon.utils.gpu_executor.submit`,**别并发直调多个 session**(撞 GPU 资源 / 报错)。

## 4. 配置改了不自动生效

MCP server 启动时把配置(当前实例 / 账号 / 各 yml)读进内存缓存,运行时不再重读文件。故 **GUI 改配置 / 手改 yml / 改 op 代码,server 都不自动跟随** —— **重启 MCP server 即生效**(各项目有自己的重启方式;客户端**无需**重连)。只有改 MCP 自身元信息(instructions / tool 描述 / 增减 method)才需客户端重连 MCP。遇"改了配置 / 代码但行为没变",先想这条。

## 5. 录屏走 MCP 后端

录 bot 实战用 `record_screen` MCP tool(Session 1 后端,observe 不占跑道,可与 bot run 并行)。**别从服务会话(Session 0)Bash 起 ffmpeg** —— BitBlt 录不到交互桌面。`mode='start'` → 跑 bot → `mode='stop'`。

## 6. server 日志默认 GBK → mojibake 不可读

server 的 Python stdout 用 Windows locale(GBK)写 → 进 UTF-8 文件变乱码(op 名 / OCR 全 mojibake,无法"读日志"诊断)。**MCP server 入口起手** `sys.stdout/stderr.reconfigure(encoding='utf-8')`。日志不可读 = 无法用"读日志"方法论,优先修。验证:MCP server 日志(项目 `.debug/` 下)按 utf-8 能解码 + Read 工具显示正常中文。

## 7. 中文关键词 LCS 误匹配(`round_by_ocr` 默认 lcs_percent=0.5)

框架 `round_by_ocr` 默认 `lcs_percent=0.5`(LCS 最长公共子序列 / 目标长度 ≥ 阈值)。**中文关键词若与别的画面文字共享 2+ 字子串,就会在 0.5 误匹配** —— 不是"子串包含",是"子序列比例"。

- **症状**:loop 卡在某屏 `round_wait` 循环、handler 不触发(日志无子 op 执行)、或派发到错误 handler。
- **判据**:卡死 + OCR 明明有关键词但 handler 不跑 → 查 `round_by_ocr` 关键词是否与同屏 / 邻屏文字共享 2+ 字。
- **修(两档)**:
  1. **快速止血**:该 `round_by_ocr` / `round_by_ocr_and_click` 传 `lcs_percent=0.7~0.9`(真匹配 1.0 不受影响,假匹配 0.5 被杀);或用更长 / 更独有关键词(如全标题)。
  2. **根因解(推荐)**:**固定位置识别** —— 关键词只在它**固定的画面位置**识别(screen_info 建 area 圈定该位置,不全文扫),从源头避免冲突。全屏 `round_by_ocr`(loose 全文)天生易冲突;固定位置 area 检测才稳(画面建档见 od-dev-screen-onboarding §3.5)。
- **别只改一个就收工** —— 同 loop 里所有中文关键词都可能踩,逐个审共享子串;长期把派发检测迁到固定位置 screen_info area。
