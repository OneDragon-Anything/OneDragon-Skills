---
name: od-dev-mcp-backend
description: 当要在一条龙(OneDragon)框架上开发或修改 MCP backend 时用 —— 新增/修改 MCP tool、backend 方法、画面额外识别器(recognizer)、MCP server 设计决策。含「tool 该不该做」的能力边界判定(agent 能力视角)与实现规范。英文:build/modify OneDragon MCP backend, add an MCP tool, design agent-facing tools, add a per-screen recognizer。不触发:用 MCP tool 排查运行 bug(od-dev-debug-automation)、写游戏玩法 op(od-dev-write-operation)。
---

# 开发 OneDragon MCP backend(给 AI 智能体的工具层)

OneDragon 系列项目的 backend:项目 Context 之上的**传输无关**收敛层 + MCP / HTTP 两个适配器并行对外。本 skill 管「给智能体暴露什么能力、怎么设计、怎么实现」;架构现状(具体类名 / 工具表 / 端口)归各项目 backend doc(见各仓 `docs/develop/<game>/backend/`)。

## 必做 checklist(新增 / 修改 MCP tool 时按序过,缺一不可)

> 没做完这 6 步不算改完;判据细则在后文与 references 对应节。

1. ☐ **判定该不该做 tool**:过「能力边界两问」+ P1/P4/P5(智能体自己能做 → 不做;活运行时 / 内存态 / 模型推理 / 配置校验收敛 → 做)。(必做)
2. ☐ **分类**:操作类还是观察类?决定 docstring 首句标注 + `ToolAnnotations`(readOnlyHint / destructiveHint,**camelCase**)。(必做)
3. ☐ **设计返回**:语义化字段 + 定位锚点 + token 预算(response_format / 截断)+ actionable 错误;与 HTTP 对称的能力放 backend 共享层(P11)。(必做)
4. ☐ **写 docstring 三要素**:能做什么(首句标观察/操作)+ 关键约束 / 隐式上下文 + 返回结构。(必做)
5. ☐ **实现落地**:按 `references/implementation.md`(Field description 选参 / 错误兜底不 raise ToolError / 命名前缀分组)。(必做)
6. ☐ **同步收尾**:工具表(mcp.md)+ HTTP 对称评估 + 测试断言 + 重启 server 验证注册 —— 按 implementation 的「改动同步 checklist」逐条。(必做)

## 核心心智:能力边界两问(一切判定的地基)

源码运行前提下,接入的智能体默认能:读源码 / 读运行时文件(日志 / 截图 / 配置)/ 执行命令 / 看图(视觉大模型)/ 改文件。**做不到**(必须经 backend):操作活的游戏运行时(活的 Context 在 server 进程)、读 server 内存态(运行态 / 当前节点)、实时取游戏画面、跑加载的模型(onnx session 在 server,`gpu_executor` 单线程串行)。

→ 推论:**server 给「事实」(领域事实 + 运行时事实),智能体做「决策 + 通用理解」**。server 不替智能体决策(下一步点哪),但给足事实让它能决策。

⚠️ **受众分层**(系列项目共性):消费者分 ①能读源码的技术用户(本地 / 远程 SSH,有 shell)②远程 MCP 纯使用者(**看不到代码**)。对②,凡「读源码才能获得的语义」(app / operation 做什么、效果、消耗)改由 server 主动给(class docstring 经 MCP 字段透传)—— 这不是「为模型弱点补偿」,是该受众客观上没有该通道,语义描述对它是领域事实。原则细节见 `references/design-principles.md` P1 例外 / P9。

## 新增对外能力:判定主线

1. **该不该做 tool?** 智能体自己能做 → 不做;活运行时 / 内存态 / 模型推理 / 配置校验 → 做;高频链式操作可合并进已有 tool → 合并。
2. **操作还是观察?** 操作改状态(进游戏 / 停止 / 改配置),观察只读(窗口 / 截图 / 运行态)。**读写分离**:单 tool 不混两者。
3. **返回设计**:哪些语义化字段?会不会超 token 上限?错误怎么 actionable?要不要锚点(时间戳 / 路径)关联日志 / 截图?
4. **docstring**:能否让智能体一眼选对?隐式上下文显式化没?参数命名无歧义没?
5. **命名**:按资源分组前缀(game 感知 / run 运行 / list·describe 查询 / screen_info CRUD)。
6. **复核**:对照 `references/design-principles.md` 全原则(P1-P14)+ 官方出处(Anthropic《Writing effective tools for AI agents》/ MCP Design Principles)。

## 画面额外识别器(recognizer):`analyze_screen` 精准命中后的领域事实

画面有「该画面特有的结构化事实」要给(如某玩法的备战席阵容 + 经济状态)→ 加 recognizer(子类自动发现、无需注册),**别**让智能体每次截图后自己 OCR 反推。硬约束(必守,详 `references/screen-recognizers.md`):`recognize()` 必须**纯读**(不写 self / 不复用带业务语义可变状态的 reader——并发 analyze 会与 operation 竞争污染)、返回 **JSON 可序列化**、**不稳定字段返 None 不编造**、extras **精简**(计入 tool response token 预算)。

## 边界(这些去别的 skill / 各仓 doc)

- 怎么**用** MCP tool 开发 / 排查 → `od-dev-write-operation`(开发内循环)/ `od-dev-debug-automation`(运行后法证)
- 画面建档本体(screen_info area / 模板)→ `od-dev-screen-onboarding`(recognizer 是建档之上的「额外识别」)
- backend 架构现状 spec(类名 / 工具表 / 端口 / daemon 接线)→ 各项目 backend doc(如 `docs/develop/<game>/backend/`);本 skill 只管跨项目的方法论与规范
- 通用 MCP tool 设计方法论(tool 命名 / schema / token 经济)→ Anthropic 官方 `mcp-server-dev` plugin 的 tool-design.md(装了更好,没装本 skill references 也够用)

## 写完自检

- [ ] 过了能力边界两问(该不该做 tool 有判定依据,不是「感觉有用就加」)?
- [ ] 受众②(源码盲)需要的语义描述给到了(docstring / description 字段)?
- [ ] annotations 标对(camelCase 字段名;观察 readOnlyHint=True / 破坏 destructiveHint=True)?
- [ ] 错误兜底走结构化 error 字段,没透传 opaque traceback?
- [ ] 双适配器消费者都用的能力放 backend 共享层,没写死在 MCP 适配器?
- [ ] recognizer(若加)纯读 + JSON 可序列化 + 不稳定字段不硬塞?
- [ ] 工具表 / 测试 / server 重启验证都同步了(implementation 的 checklist)?
