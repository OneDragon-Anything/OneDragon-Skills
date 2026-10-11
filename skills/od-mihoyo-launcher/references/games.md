# 逐游戏参数表（biz / 主程序 exe / 版本文件）

> 「已实测」= 本方法链在该游戏上完整走通过；「待核对」= 参数来自启动器数据/公开资料，首次操作时先实机核对。biz 的权威发现方法是注册表 UninstallString（见 SKILL.md 环境发现），本表是快捷参考与兜底。
> 版本文件 = `<游戏目录>\config.ini` 的 `[General] game_version`（米哈游 Unity 系通例）。

| 游戏 | biz | 主程序 exe（游戏目录内） | 版本文件 | 状态 |
|---|---|---|---|---|
| 原神 | `hk4e_cn` | `YuanShen.exe` | config.ini | 已实测（关联 + 启动） |
| 崩坏：星穹铁道 | `hkrpg_cn` | `StarRail.exe` | config.ini | 已实测（关联 + 更新 4.5→4.6 + 启动） |
| 绝区零 | `nap_cn` | `ZenlessZoneZero.exe` | config.ini（待核对） | 已实测（关联 + 启动） |
| 崩坏3 | `bh3_cn` | 待核对 | 待核对 | 未实测（本机未装） |
| 星布谷地 | `hyg_cn` | `PetitPlanet.exe` | 待核对 | 未实测（本机未装） |
| 崩坏：因缘精灵 | `abc_cn` | 待核对 | 待核对 | 未实测（本机未装） |

## 备注

- 国服 biz 后缀 `_cn`；国际服后缀不同（如星铁国际为 `hkrpg_global`），方法同构、未实测。
- `安装目录` = 直接包含主程序 exe 的目录；定位/关联时填这个目录，填上层会报「未查找到」。
- 崩坏3 曾在本机装过（注册表有卸载项），历史安装路径出现过 `D:\Honkai Impact 3rd Game` 与 `F:\miHoYo Launcher\games\Honkai Impact 3rd Game` 两种——以当期注册表 `GameInstallPath` 为准。
