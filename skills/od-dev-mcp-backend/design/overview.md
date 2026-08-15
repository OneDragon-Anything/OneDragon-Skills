# od-dev-mcp-backend · 设计概览(what)

## 为什么做

OneDragon 系列项目(SR / ZZZ / …)各自实现 MCP backend,设计文档在两仓**镜像双源**(实测:design-principles P1-P14 逐字同构、mcp-implementation 两边 105 行仅 4 行项目名差异),靠人工 sync 分支搬运(成本证据:SR 侧专门开「同步 ZZZ backend 演进」分支)。且两边各有对方没有的演进(ZZZ:两类受众/源码盲;SR:per-screen recognizer),不整合则在分叉漂移。方法论(设计原则 / 实现规范 / recognizer 机制)是系列通用 → 抽公共 skill 单源化。

## 定位与边界
- **管**:MCP backend 的**方法论层** —— tool 该不该做(能力边界判定)/ 怎么设计(操作观察分离 / 返回 / docstring / 命名)/ 怎么实现(annotations / Field / 错误兜底)/ recognizer 机制与硬约束 / 改动同步 checklist。
- **不管**:各项目 backend **现状 spec**(具体类名 / 工具表 / 端口 / daemon 接线 / HTTP 路由细节)—— 归各项目 `docs/develop/<game>/backend/`;怎么**用** tool 开发/排查(→ `od-dev-write-operation` / `od-dev-debug-automation`);画面建档本体(→ `od-dev-screen-onboarding`)。

## 构成
- **SKILL.md**:能力边界两问(核心心智)+ 新增能力判定主线(6 步)+ recognizer 何时加 + 必做 checklist + 自检。
- **references/design-principles.md**:设计原则 P1-P14 + 能力分配总表 + 受众分层(源码盲例外)——整合版(见 ADR-0001)。
- **references/implementation.md**:实现落地(annotations 分类表 / Field 选参 / 错误兜底 / docstring 三要素 / 命名 / 同步 checklist)。
- **references/screen-recognizers.md**:per-screen recognizer 机制(契约 / 3 步 / 并发安全纯读 / OCR 缓存 / 错误隔离 / 不稳定字段不硬塞 / 扫描缓存)。

## 泛化映射(从项目 doc → 公共 skill)

- 项目模块名(`sr_od` / `SrContext` / `SrBackendContext`)→ 「项目 backend / 项目 Context / backend 收敛层」;举例时两边并列。
- `sr-od-test` → 「测试仓」;`经 daemon 重启 server` → 「按项目机制重启 server」。
- 系列共享 tool 名(`check_game_window` / `click_game` / `analyze_screen` / `run_operation` 等,两边同名)按规范 3「框架地基级接口名」保留全名。
- 单项目 gitignored 路径引用(设计 spec 在 docs/superpowers/ 下)→ 删除,改指本 skill design/。
- 项目实例(货币战争 recognizers)→ 抽象为模式描述 + 「照项目内最近的同型抄」。

## 落点
- 公共仓 `OneDragon-Skills/skills/od-dev-mcp-backend/`,OneDragon 系列通用。
- 消费方式见仓 `docs/setup/ai_coding.md`(npx skills add 标准安装 / 本地开发 junction)。

## 各仓瘦身(follow-up,等 sync 分支合并后做)

- 两仓 `docs/develop/<game>/backend/` 删 design-principles.md / mcp-implementation.md;SR 另删 screen-recognizers.md(ZZZ 本无)→ 改为指本 skill 的 references。
- 保留各仓:README(总入口,加指 skill 行)/ architecture.md / mcp.md(工具表)/ http.md / entry.md / remote-ssh.md(项目现状 spec)。
- ZZZ 侧实现 screen-recognizer 机制时(公共包契约已就绪),直接按本 skill references 走。

## 当前状态
- **类型**:方法论覆盖型(整合两仓已实操验证的设计文档成公共 skill)→ RED 可省;**GREEN 待做**(下次任一项目新增 MCP tool 时按本 skill 走一遍,观察 gap)。
