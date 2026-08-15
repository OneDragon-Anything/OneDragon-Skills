# 0001. 以 ZZZ 为提炼基准 + SR 落后点台账

- **Status**: accepted
- **Date**: 2026-08-15

## Context

两仓 build-release / test-check 同族分叉。逐项对比(2026-08-15):ZZZ 13 个 workflow(含 mirrorchyan×2 / SignPath / CNB / 运营类),SR 4 个;ZZZ build-release 为多 job 分解(version→build→sign→release,335 行),SR 为单 job 巨石(460 行,逻辑内联);test-check ZZZ 三层 fallback(fork→upstream 同名→upstream main)+ requires_secrets 双档,SR 两层 + 无双档。

## Decision Drivers

- **一侧显著领先且经过生产验证**(ZZZ 多轮正式发布含签名 / 分发)。
- **组织级同构**:产品形态 / 组织 release 仓 / 测试仓协议全一致 → 方法论可平移。
- **差距是演进滞后,不是有意分叉** → 台账化,朝基准收敛。

## Considered Options

1. **各写各的,不提炼**:同族体系持续分叉,SR 侧每次踩 ZZZ 踩过的坑(如两层 fallback 的窗口期假红)。
2. **以 SR 为基准**:落后版做基准,方向反了。
3. **以 ZZZ 为基准 + SR 差距台账**(选中):领先版为准绳;差距显式列出,SR 跟进时逐项补。

## Decision

选 3。**SR 落后点台账**(跟进 backlog,以本 skill 各节为准绳):

| # | 差距 | SR 跟进动作(参照节) |
|---|---|---|
| 1 | 单 job 巨石,无 version/build/sign/release 分解 | 拆 job + outputs 传递(build-release.md「job 分解」) |
| 2 | 无 PR label `build` 触发 + concurrency | 触发三模式(build-release.md「触发与全局」) |
| 3 | 条件布尔式散在多处 `if` | 收敛 CREATE_RELEASE env |
| 4 | pyinstaller 裸调(非 uv run),Python 未钉 patch | build 环境钉死 |
| 5 | 版本不写版本源文件 | version job + 写 version.py |
| 6 | 产物组装内联 PowerShell(非脚本化) | tools/ci/prepare_release_assets.py 同型 |
| 7 | 无代码签名 | SignPath job + owner 门控 + release 署名 |
| 8 | 无分发(mirrorchyan / CNB) | distribution.md |
| 9 | test-check 两层 fallback(缺 upstream 同名分支层) | 三层 fallback(test-check.md) |
| 10 | 无 requires_secrets 双档 | PR `-m not requires_secrets` + main 全量 |

## Consequences

- **正向**:SR 侧跟进有了逐项准绳(且 test-check 两层 fallback 是**正在产生假红风险的缺口**,优先补);新项目(后续游戏)接 CI 有完整路径。
- **负向**:台账需要随 SR 实际跟进更新(跟进完删行);skill 内容从 YAML 反推,部分 why 靠推断,GREEN 验证时校准。
- **follow-up**:SR 逐项跟进(建议顺序:test-check 两层→三层(低风险)→ 拆 job → 签名 → 分发);跟进落地后回读本 skill 修 gap。

## Links

- 源:ZZZ `.github/workflows/`(build-release / test-check / mirrorchyan×2 / 其余运营类)、SR `.github/workflows/` + `.github/dev.md`。
