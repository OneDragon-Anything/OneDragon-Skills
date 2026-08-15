# 发布管线(build-release)方法论

> 以 ZZZ 领先版为基准提炼(多 job 分解 / SignPath / PR label 构建);SR 侧为早期形态(单 job、无签名),跟进清单见 skill design ADR。

## 触发与全局

- **三种触发**:`push: tags: ['v*']`(发版唯一入口)/ `workflow_dispatch`(手动,带 `create_release` 布尔 input,默认 false 只构建)/ `pull_request: [opened, synchronize, reopened, labeled]`(**PR 上打 `build` label 触发构建验证** —— label 触发让「何时构建 PR」成为显式动作,省 CI 时)。
- **concurrency**:`group: build-${{ PR number || ref }}` + `cancel-in-progress: ${{ PR 事件 }}` —— 同 PR 反复 push 只保留最新构建。
- **条件收敛**:`env.CREATE_RELEASE: ${{ (dispatch && input) || startsWith(ref, 'refs/tags/') }}` —— 「是否走发布链」全 workflow 只算一次,所有 step `if: env.CREATE_RELEASE == 'true'` 引用;在多处复制同一布尔式是漂移之源。

## job 分解(version → build → sign → release)

### version job
- 独立小 job:checkout + 跑版本脚本(`tools/ci/get_version.py`,从 tag/ref 推导),`outputs.version` 供下游。
- **版本写进版本源文件**(build job 里 `__version__ = '...'` 写 version.py)—— 运行时 / GUI 能读到正在跑的版本,排障必需;只在 release 元数据里带版本是不够的。

### build job
- **环境钉死**:`uv venv --python=3.11.x`(固定 patch 版本,别用浮动);`uv sync --group dev`。
- **UPX 固定版本**:下载固定版本 UPX 放进 `.venv/Scripts/upx.exe` —— pyinstaller 自动拾取同目录 UPX 压缩产物;版本浮动会导致产物大小 / 查杀误报漂移。
- **打包**:`cd deploy && uv run pyinstaller --noconfirm --clean <每个 .spec>`(多入口逐个:Installer / Launcher / RuntimeLauncher 类);**spec 由 pyinstaller 命令生成,别手改生成的 spec**(dev 文档里的生成命令是 spec 的源)。
- **wheels(离线依赖包)**:`uv export --no-hashes --no-dev --format requirements-txt` → `pip wheel --wheel-dir=...` → 压缩成 Environment.zip —— 安装器离线装依赖用。
- **产物组装脚本化**:Full(源码)/ Full-Environment(+ 环境 zip)/ WithRuntime(+ 内嵌运行时)/ WithRuntime-Full(+ 模型)系列产物用脚本组装(`tools/ci/prepare_release_assets.py`);**运行环境(uv / MinGit / cpython)与模型(OCR / YOLO)从组织级 release 仓拉**(OneDragon-Env / OneDragon-YOLO 的对应 release),绝不入 git(体积 + 版本解耦:模型更新不动代码仓)。
- **双模式上传分流**:
  - `CREATE_RELEASE == 'false'`(PR / 手动构建):逐产物 `upload-artifact`(Installer / Launcher / Wheels 各一个)—— 给 PR 验证下载;
  - `CREATE_RELEASE == 'true'`:dist 全量 artifact + **unsigned artifact(待签名的 exe 集合,id 传给 sign job)**。

### sign job(代码签名)
- **SignPath**(开源项目免费):`signpath/github-action-submit-signing-request`,`wait-for-completion: true`,签名产物落到指定目录。
- **owner 门控(关键)**:`if: github.repository_owner == '<org>' && (发版条件)` —— fork PR 永远不触发签名(fork 无 secrets,不消耗配额);secrets(`SIGNPATH_API_TOKEN`)与 vars(`ORGANIZATION_ID`)分开配。
- 签名策略 slug 固定(如 `release-signing`);审批人在 SignPath 侧配置(release body 里要列)。

### release job
- **依赖判定链**:`needs: [version, build, sign]` + `if: always() && needs.build.result == 'success' && 发版条件 && needs.sign.result == 'success'` —— **签名失败则整条发布不发生**(signed exe 覆盖 unsigned:download 两份 artifact,signed 解压覆盖同名)。
- **release body 模板**(softprops/action-gh-release):
  - 产物矩阵逐个说明用途(Full / Full-Environment / Installer / WithRuntime 系 / Launcher 更新包),「不要下载 Source Code」提示;
  - 安装指南 + 排障指南链接;
  - **SignPath 署名义务**(免费签名的条件):io/foundation 链接 + 审批人列表,中英双语;
  - 隐私政策链接。
- `prerelease: contains(version, '-beta.')` —— beta tag 自动预发布。
- `generate_release_notes: false` 时自行组织 body(或用 git describe 区间生成变更节)。

## 发布后分发联动

- **CNB 镜像**:release job 尾部 API 触发 CNB build(`https://api.cnb.cool/<org>/<repo>/-/build/start`,secrets 带 token,`continue-on-error: true` 分发失败不阻塞)。
- **mirrorchyan**:独立 workflow 经 `workflow_run`(Build and Release completed)联动 —— 详 `references/distribution.md`。

## 改动判据速查

| 改什么 | 动哪 |
|---|---|
| 依赖 / 入口 / 打包参数 | spec 重新生成 + build job;产物名变 → release body 的 files 列表 + 产物矩阵说明同步 |
| 新增产物 | prepare 脚本 + release files + body 说明;要签名则加进 unsigned 列表 |
| Python / UPX 版本 | build job 两处钉死值同步;跑一次手动构建验证体积 |
| 新环境资源 / 模型 | 组织 release 仓(OneDragon-Env / YOLO)先发,再改 prepare 脚本拉取点 |
