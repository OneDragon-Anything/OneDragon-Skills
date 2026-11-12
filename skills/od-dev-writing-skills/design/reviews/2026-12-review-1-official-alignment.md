# 独立评审报告 1:对标 Anthropic 官方实践(2026-12)

> 评审对象:SKILL.md 旧版重写初稿 + 旧 references(writing-craft 尚未拆迁)。评审者为无前提独立子 agent,基准为 Anthropic 官方三源(best practices / skill-creator / agentskills.io)。报告原文存档,处置见 design/overview.md 台账。

## 高

### H1. 引用链超过一层深,违反两份官方基准的明确推荐,且与自采纳的「部分读取」机制自相矛盾
- 问题:references 之间互引形成二层链(skill-testing / skill-feedback / design-docs → writing-craft)。官方:"Keep references one level deep from SKILL.md"。被指向的 writing-craft §3.1 位于该文件 199-204 行,恰在 100 行预览窗口之外。
- 处置:随 writing-craft 拆迁自动解决——拆迁后 references 只指 SKILL.md(总是全文加载)。

## 中

### M1. 自设「pushy 防漏触发」两要素,自身 description 只满足一半
- 处置:已补 pushy 强化句(不含 superpowers,见 M2 裁定)。

### M2. description 负向路由缺 superpowers:writing-skills,且无生态限定词
- 处置:**用户裁定不处理**(不考虑与 superpowers 的重叠);报告附注的英文触发词对齐同样未做。

### M3. §7 总装 checklist 末步不是自验证步(名实不符)
- 处置:已加第 8 步「回头核对 1-7 步结果」+ 实测回灌后重过自检的回路。

### M4. 「完工自检」7 项检查全部没有「不过」出口
- 处置:已补总出口行。

### M5. SKILL.md 正文多处长句嵌套塞多项,违反自设「≥3 并列项用列表」
- 处置:三处已拆列表。

### M6. 「4 硬规范」实体在 SKILL.md 中悬空,下游引用断链
- 处置:随拆迁解决(框架已溶解,旧引用全部清偿,合规定义改为「过 §7 完工自检」)。

### M7. 测试制度与官方「evaluations first」顺序相反;触发质量验证缺负例
- 处置:轻量采纳——测试场景(任务+负例)留档 evals/TESTS.md;挂载验证正负例双查;eval-first 顺序不翻转(§1 需求确认已吸收其精神,知情裁定)。

### M8. 「When to Use」信息归属内部直接矛盾
- 处置:已补划界句(触发语义归 description;正文该节管已加载后的适用性判断)。

### M9. 例子政策整体与官方「具体例子最有效」推荐相抵,且三处口径漂移
- 处置:SKILL.md §4.1 改为「方法可泛化,细节可具体」;AGENTS.md 同步;writing-craft 部分随拆迁消化。

## 低

- L1 writing-craft 转述官方上限错误(共 1024)→ 随拆迁消失,SKILL.md 表述本就正确。
- L2 「agent/智能体」混用 → SKILL.md 侧已统一 agent;references 侧在评审 2 处置。
- L3 RCA、SDO 缩写首现无解释 → RCA 已加「(根因分析)」;SDO 随 overview 重写消失。
- L4 SKILL.md token 规模超 5000 建议(待确认)→ 知情保留(低频 dev skill,行数合规 <500)。
- L5 「wc -w」Unix 命令 → 随拆迁消失。
- L6 skill-testing 写死 SendMessage → 已通用化。
- L7 驳回 skills-ref 校验器的理由与仓库消费方式(npx skills add)矛盾 → 理由已修正(overview 台账)。
- L8 「Anthropic Goldilocks」出处归因存疑 → 随拆迁消失。
- L9 跨模型「保证」是未验证假设 → overview 措辞已降格为「预判」。
- L10 引用存在性校验缺位 → 维持已记录的 follow-up 计划。
