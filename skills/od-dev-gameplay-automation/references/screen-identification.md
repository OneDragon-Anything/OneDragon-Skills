# 画面建档深度细则(两套做法:探索期 + 实现期补全)

> ⚠️ **归并进行中(2026-08-09)**:画面建档"做什么"的**操作方法论单一源是 `od-dev-screen-onboarding`**(analyze→视觉大模型→doc→缺口→建模→归档)。本文件只保留 **gameplay 流程视角的画面建档判据速查**(识别优先级 / 每状态建档 / 信息 area / LCS 误匹配),**操作细节不重复**(见 screen-onboarding)。
> **画面建档不分初步/完整档**:每次按完整标准做,探索期标 `进行中` 待实现期补全(详见 SKILL.md 两套做法 + progress-tracking §1)。
> **LCS 误匹配**(运行时 `round_by_ocr` 分派误火)待迁 `od-dev-write-operation`(运行时分派诊断);其「固定位置识别」根因解见 screen-onboarding §3.5。

## 识别优先级(判定"当前在哪个画面")

1. **文字 → OCR**(`analyze_screen` 的 `ocr_texts`,1080p 直出坐标)。OCR 关键词**选画面独有的**,别用会出现在多个画面的子串。
2. **固定 UI 元素 → screen_info**(写 `assets/game_data/screen_info/<screen>.yml`,pc_rect 坐标)。坐标怎么来见 od-dev-screen-onboarding §4.5。
3. **状态/选中/计数 → 视觉大模型 兜底**,但 视觉大模型 的状态推理不可信,只信客观描述;坐标对错用数值对拍 ground truth(别用 视觉大模型 当裁判)。

## 中文关键词 LCS 误匹配(判据 + 修法)

框架 `round_by_ocr` 默认 `lcs_percent=0.5`(LCS 最长公共子序列 / 目标长度 ≥ 阈值)。**中文关键词若与别的画面文字共享 2+ 字子串,就会在 0.5 误匹配** —— 不是"子串包含",是"子序列比例"。

- **症状**:loop 卡在某屏 round_wait 循环、handler 不触发(日志无子 op 执行)、或派发到错误 handler。
- **判据**:卡死 + OCR 明明有关键词但 handler 不跑 → 查 `round_by_ocr` 关键词是否与同屏/邻屏文字共享 2+ 字。
- **修(两档)**:
  1. **快速止血**:该 `round_by_ocr` / `round_by_ocr_and_click` 传 `lcs_percent=0.7~0.9`(真匹配 1.0 不受影响,假匹配 0.5 被杀);或用更长/更独有关键词(如全标题)。
  2. **根因解(推荐)**:**用固定位置识别** —— 关键词只在它**固定的画面位置**识别(screen_info 建 area 圈定该位置,不全文扫),从源头避免与画面其他位置的同类文字冲突。全屏 `round_by_ocr`(loose 全文匹配)天生易冲突;固定位置 screen_info area 检测(bound 到位置)才稳。
- **别只改一个就收工** —— 同 loop 里所有中文关键词都可能踩,逐个审共享子串;长期把派发检测迁到 screen_info area(固定位置)。LCS 误匹配本质 = 全屏匹配撞同类元素;固定位置是根治。

## 建档只写 docs + screen_info,别改原内容

`pc_rect` 占位是**待填**不是坏数据 —— 画面/玩法建档只写 docs/game 的 doc + 新增 area,不动 screen_info 已有内容(详见 `od-dev-screen-onboarding`)。

## 每个状态都建档 + 存 fixture(防回归地基)

早期接触玩法**很多画面没见过** —— 每碰到一个新状态就:① 截代表图存 fixture(项目 test 目录 / `.debug/`);② screen_info 建该画面 area;③ 写针对该 fixture 的测试。

**别凭 1-2 张图写整个流程** —— 一个流程通常有多种状态(不同子界面/事件选项/阶段切换/结算页…),只见过一两种就下结论/写代码,必然漏状态、回归不断。不认识的画面别猜,先 `analyze_screen` + 视觉大模型 看清(取坐标视觉直读,方法论见 od-dev-screen-onboarding §4.5)。

## 建 automation 所需的所有信息 area(不只动作按钮)

画面建档不只建"识别锚点 + 动作按钮 area",还要建**自动化流程要读取的所有信息 area** —— 该屏 bot 做决策 / 存策略状态所需的数据(属性 / 词缀 / 阵营 / 首领 / 数值 / 状态 / 反馈信号)。漏建 → op 没读取 → 策略缺输入。

**判据**:建档时问"该屏 automation 要**读**什么(不只**点**什么)?" 凡是要读的数据,建 area(供 op `round_by_find_area` / OCR 读取);漏了 op 拿不到,策略瞎跑。
