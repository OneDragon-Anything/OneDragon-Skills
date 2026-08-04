# Claude Code：接入团队 AGENTS.md

> [ai_coding.md](../ai_coding.md)「团队源 vs 个人入口」在 Claude Code 上的具体接线。思路通用,下面是 Claude Code 的落地。

## 推荐:用 `@` 引入 AGENTS.md

1. 创建 `.claude/CLAUDE.md`(`.claude/` 不入库,各自建)。
2. 用 `@` 引入团队源:`@../AGENTS.md`。
3. 后续在 `@` **下方**补充个人内容(Claude 特有规则 / 个人偏好)。

`.claude/CLAUDE.md` 形如:

```markdown
@../AGENTS.md

（下方写个人 / 工具特有的补充）
```

> Claude Code 启动时自动加载 `.claude/CLAUDE.md`,`@../AGENTS.md` 会把团队源完整引入,无需额外配置。个人偏好另写仓库根 `CLAUDE.local.md`(gitignore,加载在 `CLAUDE.md` 之后)。

## 其他工具

支持引入语法(`@` / `@import` 等)的工具同理;只读固定入口且无引入语法的,用**硬链接**镜像 `AGENTS.md`,将来支持引入时改回。

## 相关文档

- [ai_coding.md](../ai_coding.md) — 通用方法论(团队源 vs 个人入口)
- [AGENTS.md](../../AGENTS.md) — 团队源
