# Config + GUI(reference)

> 本 skill 的 situational reference。app 配置(YamlConfig)+ 设置界面(setting card)怎么写。

## Config(YamlConfig 子类)

每个配置字段写三件:property(读)+ setter 调 `update`(写内存)+ `xxx_adapter` property(给 GUI)。

```python
class MyAppConfig(YamlConfig):
    def __init__(self, instance_idx=None):
        YamlConfig.__init__(self, 'my_app', instance_idx=instance_idx)

    @property
    def difficulty(self) -> int: return self.get('difficulty', 1)
    @difficulty.setter
    def difficulty(self, v): self.update('difficulty', v)

    @property
    def difficulty_adapter(self) -> YamlConfigAdapter:
        return YamlConfigAdapter(self, 'difficulty', 1, 'str', 'int')
```

- **文件位置**:`config/<module>.yml`(全局)or `config/<idx:02d>/<module>.yml`(实例级,传 `instance_idx`)。
- **多账号**:传 `instance_idx` → 读对应账号 yml;切换账号 → 项目的 Context reload。
- **PlanItem 列表配置**(如规划):app 自定义 PlanItem 类 + `init_xxx_list` 从 yml 反序列化 + `add/update/delete/move` + 重写 `save` 序列化(框架不管,纯 app 职责)。

## GUI(setting card interface)

每个 app 一个 `gui/interface/<app>/` 目录(**可选**;app 可无 GUI,用公共 interface)。
- 继承 `VerticalScrollInterface`(简单)或 `PivotNavigatorInterface`(复杂,多 tab 子页)。
- `get_content_widget` 装 setting card;`on_interface_shown` 用 adapter 绑定。
- 常用 card:`SwitchSettingCard`(bool)/ `ComboBoxSettingCard` / `EditableComboBoxSettingCard`(下拉)/ `TextSettingCard`(文本)/ `SettingCardGroup`(分组)。
- 绑定:`card.init_with_adapter(ctx.<app>_config.<field>_adapter)`(双向同步 GUI ↔ yml)。
- 注册到主窗口:**手动**在项目主窗口的 `create_sub_interface` 加 `add_sub_interface`(**框架不自动发现 GUI**,只自动发现 application/factory)。

> **GUI 要经 `ctx.<app>_config` 访问配置 → 有 GUI 的 app 需 Context 接线**(见 SKILL.md 步 6 特殊情况)。app 内部自用的 config 经 factory 拿,不用接线。
