# 0024. 合并 od-dev-ui-region-detect 入本 skill(视觉时代独立价值收缩)

- **Status**: accepted
- **Date**: 2026-08-31

## Context

od-dev-ui-region-detect 成文于会话模型无视觉时代(坐标靠 API grounding 委派,故有 grounding
格式表 / 信任层级 / VLM-vs-CV 选型等大篇幅)。2026-08 末常用会话模型具备原生视觉(看图直读绝对
像素坐标,1080p 游戏截图实测可直接消费)后,该 skill 先重写为「视觉优先」并 GREEN 复验通过
(干净上下文子 agent 按 checklist 走完 5 步,9/9 槽坐标对拍 screen_info ≤2px);但用户终审裁定:
视觉直读后独立成 skill 已无必要——幸存价值只有「模板裁剪要 OpenCV 像素级精准定位 + 去背景」,
并入本 skill 做小节即可;密集网格投影峰值法与 `detect_grid.py` 脚本也不再保留(密集槽位建档用
视觉直读坐标)。

## Decision

- **删除** od-dev-ui-region-detect skill 整目录(含 design/ 全部 ADR 与 detect_grid.py;git 历史
  留档)。
- 本 skill 新增 **§4.5「坐标获取:视觉直读默认,OpenCV 只管像素级精准」**:视觉直读默认(无视觉
  派子 agent 使用有视觉大模型)、两条不可信线(空间关系用数值测 / 颜色阈值 CV 采样)、OpenCV
  像素级精准定位(squares 多阈值 / HoughCircles / 轮廓圆度)、mask 去背景、识别方案升级路径
  (ladder)压缩收录。
- §4 的「同源禁令 / 覆盖测试协议」由指针改为正文(原指 ui-region-detect「验证」节)。
- 各协作 skill(gameplay-automation / write-operation / write-application / progress-tracking)的
  路由指针改指本 skill;skills/README.md 索引删行。

## Consequences

- **正向**:少一个 skill(安装套 / 维护 / 互引链都减);坐标方法论与建档流程同文件,§5 采库定位
  不再跨 skill 跳转。
- **负向**:投影峰值法(密集等距槽位批量精确定位)从常驻方法论移除——若未来视觉直读在密集网格
  精度不足,**凭本 ADR 重开**(git 历史有完整方法论文本与 detect_grid.py 实现)。
- **边界**:本仓与他仓历史 ADR 中对 ui-region-detect 的引用按 ADR 不可变约定**不回改**(记录
  当时决策语境);活引用(SKILL 正文 / design overview / 代码注释)同步清理。

## Links

- 被并 skill 的终版状态(视觉优先重写 + ADR-0007 + GREEN 记录)见 git 历史
  `skills/od-dev-ui-region-detect/`(删除前最后提交)。
