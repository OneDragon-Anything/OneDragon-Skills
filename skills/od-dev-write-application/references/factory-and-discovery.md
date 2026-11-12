# Factory 注册 + 自动发现(reference)

> 本 skill(`od-dev-write-application`)的 situational reference。app 怎么被框架发现 + factory / const 怎么写。

## 1. 自动发现(约定式扫描,零手工注册)

框架的 `ApplicationFactoryManager` 扫描 `application_plugin_dirs` 声明的目录:
- **内置应用**:`src/<project>/application/<app>/`(提交进仓;绝对导入)。
- **第三方插件**:`<项目根>/plugins/<plugin>/`(gitignored;插件内可相对导入)。

扫描规则:
- 找 `*_factory.py` → 反射找唯一一个 `ApplicationFactory` 子类;找 `*_const.py` → 读元数据(必需)。
- **同一目录多个 `_factory.py` 或 `_const.py` → 该目录跳过**(冲突)。
- **`APP_ID` 全局唯一**,重复注册被拒。
- 运行时可 `ctx.refresh_application_registration()` 重新扫描(开发期 / 第三方插件更新后)。

## 2. const 文件(必需字段)

```python
APP_ID = 'my_app'           # 全局唯一
APP_NAME = '我的应用'        # GUI 展示名
DEFAULT_GROUP = True         # True → 进一条龙默认运行列表;False → 独立工具(不批量跑)
NEED_NOTIFY = True           # 是否要通知能力
```

第三方插件可加 GUI 元数据:`PLUGIN_AUTHOR` / `PLUGIN_HOMEPAGE` / `PLUGIN_VERSION` / `PLUGIN_DESCRIPTION`。

## 3. Factory 类

文件名必须 `*_factory.py`;同目录最多一个。最小签名:

```python
class MyAppFactory(ApplicationFactory):
    def __init__(self, ctx):
        ApplicationFactory.__init__(self, my_app_const)          # 传 const 模块
        self.ctx = ctx

    def create_application(self, instance_idx, group_id) -> Application:   # 必需
        return MyApp(self.ctx)

    def create_run_record(self, instance_idx) -> AppRunRecord:             # 有 run-record 才
        return MyAppRunRecord(instance_idx=instance_idx, ...)

    def create_config(self, instance_idx, group_id) -> ApplicationConfig:  # 有 config 才
        return MyAppConfig(instance_idx=instance_idx)
```

## 4. 第三方插件

- 放 `plugins/<plugin>/` 子目录(**不是** `plugins/` 根);`plugins/` gitignored。
- 插件内可用相对导入(`from . import xxx_const`)。
- 可带自己的 screen_info(`plugins/<plugin>/screen_info/*.yml`;`app_id` 可省,自动用插件的 APP_ID;进该 app 的局部 scope,不污染别的)。
- GUI 导入的 zip 包:顶层是插件目录(别把文件直接压 zip 根)。
