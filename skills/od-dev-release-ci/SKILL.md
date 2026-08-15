---
name: od-dev-release-ci
description: 当要改 OneDragon 项目的发布管线(build-release workflow / 打包 / 签名 / 分发)或 CI 检查(test-check / 测试仓联动),或新项目搭这套 CI,或发版 / CI 出问题要排查时用。英文:modify release pipeline, packaging, code signing, CI workflows, set up CI for a new OneDragon project, troubleshoot a release。不触发:PR 的 checks 红了怎么收尾(od-dev-pr-finishing)、写业务代码。
---

# OneDragon 发布管线与 CI(构建 → 签名 → 发布 → 分发)

OneDragon 系列项目的发布与 CI 体系(自 ZZZ 领先实践提炼;各项目落地差异见各仓 `.github/workflows/`)。核心心智:**发布是一条流水线,不是一个脚本** —— version → build → sign → release → distribute,每环独立判据、独立失败语义。CI 检查(测试仓联动)与 PR 协作流程耦合(同名分支协议见 pr-review / pr-finishing)。

## 必做 checklist(改发布管线 / 搭新项目 CI 时按序过)

1. ☐ **触发设计**:tag push(发版)/ workflow_dispatch+create_release(手动)/ PR label `build`(PR 期构建验证)三模式都要有;加 `concurrency` 组(PR 重复 push 取消旧构建)。(必做)
2. ☐ **条件收敛**:「是否发 release」的布尔式收敛成一个 env(如 `CREATE_RELEASE`),所有 step 引用它,别在多处复制表达式。(必做)
3. ☐ **build 环境钉死**:Python 固定到 patch 版本建 venv;UPX 固定版本放进 venv Scripts(pyinstaller 自动拾取);pyinstaller 一律 `uv run pyinstaller --noconfirm --clean <spec>`。(必做)
4. ☐ **产物组装脚本化**:多产物(Full / Full-Environment / WithRuntime 系)用脚本组装(如 `tools/ci/prepare_release_assets.py`),运行环境与模型从**组织级 release 仓**拉(OneDragon-Env / OneDragon-YOLO),不入 git。(必做)
5. ☐ **双模式上传分流**:非 release 模式逐产物传 artifact(供 PR 验证);release 模式传 dist 全量 + unsigned(给签名 job)。(必做)
6. ☐ **签名 owner 门控**:签名 job 只在组织仓跑(`repository_owner` 判定,防 fork PR 触发);签名失败必须阻塞 release job。(必做)
7. ☐ **release body 含署名义务**:SignPath 免费签名要求 release 里带署名说明(io / foundation 链接 + 审批人);产物矩阵逐个说明用途。(必做)
8. ☐ **分发联动**:release 成功后触发镜像分发(mirrorchyan / CNB);分发 workflow 用 `workflow_run` 联动 + 非 PR 事件判定 + owner 门控。(必做)
9. ☐ **test-check 过三层 fallback + secrets 双档**(详 `references/test-check.md`)。(必做)

## 快速判据

- **改了依赖 / spec**:build job 重跑即可;别手改生成的 spec 文件(用 pyinstaller 命令再生成)。
- **版本号**:`v*` tag 是唯一发版入口;`-beta.N` 后缀自动标 prerelease;版本同时写入版本源文件(运行时可读)。
- **fork PR 构建不了 / 签不了名**:预期行为(owner 门控);label `build` 触发的构建走 artifact 验证,不进发布链。
- **新项目接入顺序**:先跑通「tag → GitHub Release」最小闭环(1-6),再加签名(6-7),最后加分发(8);别一步到位。

## 边界(这些去别的 skill / 各仓)

- PR checks 红 / CodeRabbit / 合并顺序 → `od-dev-pr-finishing`(收尾)/ `od-dev-pr-review`(审查)
- 测试仓怎么配合开发(同名分支 / fixture)→ pr-review §0 + 各仓测试仓约定;本 skill 只管 CI 侧联动机制
- 具体 YAML / spec / 产物名 → 各仓 `.github/workflows/` 与 `deploy/`(本 skill 是方法论,不是可复制配置库)

## 写完自检

- [ ] 触发三模式齐,concurrency 有,布尔条件收敛单点?
- [ ] build 环境钉死(Python patch / UPX 版本),pyinstaller 走 uv run?
- [ ] fork PR 不会触发签名 / 分发(owner 门控)?签名失败阻塞发布?
- [ ] 产物组装脚本化,环境 / 模型从组织 release 仓拉,没入 git?
- [ ] release body 有产物矩阵说明 + SignPath 署名?
- [ ] test-check 三层 fallback + requires_secrets 双档 + UTF-8 编码?
