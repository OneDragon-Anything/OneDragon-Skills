# od-dev-release-ci · 设计概览(what)

## 为什么做

OneDragon 系列项目的发布 / CI 体系在 ZZZ 侧领先演进(多 job 分解 / SignPath 签名 / PR label 构建 / 三层 fallback / mirrorchyan+CNB 分发 / requires_secrets 双档),SR 侧停在早期形态(单 job 巨石 / 无签名 / 两层 fallback)。体系是组织级方法论(同一套产品形态:Installer/Launcher/环境包/模型包;同一套组织 release 仓:OneDragon-Env / OneDragon-YOLO;同一套测试仓协作协议)→ 提炼公共 skill,作为各仓 workflow 的演进准绳与差异台账。

## 定位与边界
- **管**:发布管线方法论(触发 / job 分解 / 打包环境钉死 / 产物组装 / 签名门控 / release 模板 / 分发联动)+ test-check 联动机制(三层 fallback / secrets 双档 / 编码)。
- **不管**:具体 YAML / spec / 产物名(各仓);PR 协作流程语义(→ pr-review / pr-finishing);业务代码。

## 构成
- SKILL.md:checklist + 快速判据;references/build-release.md(管线主参考);references/test-check.md(测试仓联动);references/distribution.md(分发 + 运营类速览)。

## 提炼基准

**ZZZ 为基底**(领先版);SR 落后点见 [ADR-0001](decisions/0001-zzz-baseline-sr-gap.md) 的差距清单 —— SR 跟进时以本 skill 为准绳逐项补,不再反向参照旧实现。

## 落点
公共仓 `OneDragon-Skills/skills/od-dev-release-ci/`。消费方式见仓 `docs/setup/ai_coding.md`。

## 当前状态
方法论覆盖型(提炼自两仓已实操的 CI 配置,ZZZ 侧经多轮发布验证);RED 可省,GREEN 待做(下次任一项目改 CI / 发版时按本 skill 走,观察 gap)。
