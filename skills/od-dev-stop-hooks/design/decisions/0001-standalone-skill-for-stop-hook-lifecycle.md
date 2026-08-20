# 0001 停机钩子规范独立成 skill(判据归此,手法留各既有落点)

- **状态**:accepted
- **日期**:2026-08-20

## Context

实机开发范式(无模拟环境、无游戏现状先验理解)下,钩子是观察 / 断点基础设施,停机钩子等 AI 现场接手。一次实锤失败:同一个停机钩子(备战槽出现不认识的占用物),同一个 agent 一天内错误处理三次——①视觉模型误读当证据、按误读加了错误守卫;②把停机钩子降级成留证带病跑;③降阈值宽匹配把未知物硬配成「大概是 X」。用户四次纠偏才回到正解(点开确认 + 建档 + 确认钩子)。随后审计项目全部 15 处停机钩子,2 处 flag 无「遇到后做什么」说明。

既有覆盖分散且视角错位:

- `od-dev-debug-automation` §1 四层排查序是**死因排查**视角(谁停的),不回答「它就是自己停的,现在该干什么」。
- `od-dev-write-operation` runtime-craft 钩子节是**作者视角**(怎么埋),接管停机的 agent 往往不是埋钩子的那个、不加载该 skill。
- `od-dev-gameplay-automation` runtime-iteration 只有**分流判据**(停机 vs 采集),不管停机后的处理与钩子生命周期。

## Decision Drivers

1. 消费侧协议必须能被「接管的 agent」在停机现场触达——它没有作者上下文,只看得到 STOPPED + sentinel flag + 截图。
2. 公共 skill 单一源:判据、代码手法、分流判据、建档流程各自归家,新增 skill 不得复述(双源漂移)。
3. 公共仓泛化:不提具体项目钩子名 / 游戏 / 会话细节(三误案例只进 ADR 作论据)。

## Considered Options

- **消费侧协议并入 debug-automation**(否决:那是异常死因场景的 skill,预期触发是不同场景;且生产侧生命周期判据(两分类 / 降级治理 / flag 契约)放不进去,塞进去会腐蚀其「事后排查」边界)。
- **生产侧判据并入 write-operation 钩子节**(否决:消费侧 agent 加载不到该 skill——触发时刻它是「处理停机的 agent」不是「写 op 的 agent」;且该节已承担代码手法,再叠生命周期判据会过长)。
- **只强化既有两处的措辞,不建新 skill**(否决:三误不是「不知道规则」,是压力下的绕过——需要禁令 + 合理化反驳 + red flags 的纠正型内容,散装强化抓不住)。
- **独立 skill + 四邻居单向指针**(采纳)。

## Decision

建 `od-dev-stop-hooks`,只管生命周期判据 + 停机现场处理协议;代码手法留 runtime-craft(其 sentinel 示例补「可执行处理步骤」行 + 指回本 skill 三要素,防双源)、分流留 gameplay-automation、建档留 screen-onboarding、死因排查留 debug-automation(§1 层 3 加移交指针)。名字里的 "stop" 是刻意收窄:防止未来把采集钩子方法论 / 埋钩子手法塞进来(与 harness 层 Stop 事件钩子的歧义由 description 首句消歧)。
