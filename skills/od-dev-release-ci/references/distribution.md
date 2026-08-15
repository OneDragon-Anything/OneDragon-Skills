# 分发与组织运营类 workflow(速览)

> 分发 = GitHub Release 之外的渠道;运营类 = issue / 社区自动化。各项目按需接入(接入顺序判据见 SKILL.md「快速判据」);具体 YAML 归各仓。

## mirrorchyan(镜像酱,国内高速分发)

- **两个 workflow 分工**:`mirrorchyan_uploading`(上传产物包,`MirrorChyan/uploading-action`)+ `mirrorchyan_release_note`(同步 release 说明,`MirrorChyan/release-note-action`)。
- **触发**:`workflow_run: [Build and Release] completed` + `workflow_dispatch` 兜底(note 另挂 `release: [edited]` —— 手动编辑 release 说明后重传)。
- **门控三连**:`repository_owner == org`(fork 不跑)+ `event != pull_request`(PR 构建不上传)+ `conclusion == 'success'`(构建失败不上传)。
- **双 arch matrix**:x86_64 传 WithRuntime-Full 包、aarch64 传 Full-Environment 包(镜像酱按架构分发);runner 用 `macos-latest`(action 作者要求,非构建需要)。
- 配置:rid(项目标识)/ `MirrorChyanUploadToken` secret。

## CNB 镜像(cnb.cool)

- 代码同步:push main 后单向同步(`sync-cnb.yml`)。
- release 同步:release job 尾部 API 触发 CNB 侧 build(见 build-release.md「发布后分发联动」),分发失败 `continue-on-error` 不阻塞。

## 组织运营类(按需)

| workflow | 用途 | 备注 |
|---|---|---|
| issue-automation | issue 打标 / 分诊 / 引导回复 | 体量大,规则随项目运营演进 |
| trusted-contributor-close-issue | 白名单贡献者关 issue | 防误报骚扰 |
| auto-close-issue / lock-closed-issues | 关闭无效 issue / 锁已关 issue 防挖坟 | 小 |
| update-contributors | 贡献者列表刷新 | 小 |
| update-redemption-code | 兑换码类运营 | 游戏相关项目用 |
| build-running-resources | 运行资源构建 | 项目按需 |
| build-test-branch | 测试分支构建 | 项目按需 |
| common-set-timestamp | 公共 timestamp 计算复用 | 被复用的公共 job |

> 判据:运营类 workflow 是「项目运营决策的自动化」,不是技术必需 —— 新项目先零运营跑通发布,运营负担出现时再逐个接(从 ZZZ 抄同型)。
