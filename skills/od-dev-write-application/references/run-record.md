# Run-record(运行记录,reference)

> 本 skill 的 situational reference。app 的运行记录(`AppRunRecord`)怎么写。

每 app 一份运行记录(`AppRunRecord(YamlConfig)`),文件 `config/app_run_record/<app_id>.yml`(或实例级 `config/<idx>/app_run_record/<app_id>.yml`)。

## 1. 公共字段 + 周期重置

- `dt`(日期,判重置)/ `run_status`(WAIT=0 / SUCCESS=1 / FAIL=2 / RUNNING=3)/ `run_time`。
- **周期重置**(`AppRunRecordPeriod`):`DAILY`(默认,按游戏刷新点)/ `WEEKLY`(按周)。

## 2. 空壳起步 vs 子类加业务字段

- **简单 app 直接用 `AppRunRecord`**(只传 app_id,空壳)。
- **业务字段后加**:继承 `AppRunRecord`,加业务字段(如已完成列表 / 次数),重写 `reset_record` 同步重置,加业务方法(如 `add_record`)。APP_ID 要与 const 的 APP_ID 一致。

## 3. 用法(框架自动 + 一条龙)

- 框架在 `handle_init` 自动 `update_status(RUNNING)`;`after_operation_done` 自动按成功 / 失败 `update_status`(app 可重写加业务判定,如"全部完成才算 SUCCESS")。
- 一条龙运行前查 `run_record.is_done` → 已完成则跳过该 app。
- GUI 用 `run_status_under_now` 显示"今日已完成 / 未运行 / 失败"。
