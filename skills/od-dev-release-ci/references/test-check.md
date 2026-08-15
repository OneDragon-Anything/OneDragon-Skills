# test-check(测试仓联动)方法论

> OneDragon 项目主仓 + 测试仓分仓:CI 在主仓 PR / push 时 checkout 测试仓跑 pytest。同名分支协议(测试改动只进 PR 同名分支,合主仓后再合测试仓 main)见 od-dev-pr-review §0 / od-dev-pr-finishing §6;本文件管 CI 侧怎么正确检出测试仓。

## 三层 fallback checkout(核心)

按序尝试,`continue-on-error: true` 逐层降级,上一层失败才走下一层:

1. **fork 同名分支**:`repository: PR head owner 的 <game>-od-test`,`ref: PR head 分支` —— 贡献者在**自己 fork 的测试仓**推了同名分支(测试改动随 PR 走);
2. **upstream 同名分支**:`repository: <org>/<game>-od-test`,`ref: PR head 分支` —— 测试改动已推到组织测试仓但 PR 未合(协作中的窗口期);**这层最常被漏**(早期实现只有 fork → main 两层,窗口期会错误地跑旧 main 测试 → 假红);
3. **upstream main**:兜底(该 PR 无测试改动)。

表达式骨架(PR 时取 fork owner,否则组织仓):
`repository: ${{ PR && (head.repo.full_name && format('{0}/<game>-od-test', head.owner) || '<org>/<game>-od-test') || '<org>/<game>-od-test' }}`。

## requires_secrets 双档

- **PR 事件**(尤其 fork)拿不到 secrets → `pytest -m "not requires_secrets"`(跳过推送通知类测试);
- **push main** → 全量跑 + `env:` 注入全部推送渠道 secrets(PUSH_* 系列)。

default 分支推送链(fork PR 合并后 main 的全量验证)是 secrets 测试的唯一 CI 执行点。

## Windows 编码(必守)

`chcp 65001` + `$OutputEncoding/[Console]::Input/OutputEncoding` 三件套 + `PYTHONIOENCODING: utf-8` —— 否则中文输出 / 断言在 CI 日志里乱码,失败排查成本翻倍。

## 失败 notice

失败时输出引导:当前触发事件 + 「fork 测试仓建同名分支改测试」+ 本地复跑命令(`uv run pytest <test-repo>/ -v`)。给贡献者的自助路径,减少 review 往返。
