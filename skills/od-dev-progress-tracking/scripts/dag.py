"""dag.py — DAG 任务图管理 CLI(新正本,独立于 progress.py 的行文法账本)。

数据模型(与用户逐字段确认的设计,2026-09-05):
- 节点 Task:id / title / module(封闭枚举:流程|决策|支撑)/ status(七态)/
  deps(图内硬依赖,只存单侧,反向现算)/ cond(图外等待,wait 必带含「复查」)/
  criteria(完成凭据指针,追加式:预注册+实证共存;done 与 pending_review 流转必带)/
  review(验收档:required=需验收缺省|none=免审;建账定不可变)/
  priority(派单优先级,0..10 大者先派,缺省 0;ready 排序=优先级→关键链→挡下游)/
  assignee+since(doing 必带,挂了检测与恢复锚点;pending_review/rejected 保留交付者)/
  dead_reason / notes / created。
- 状态机七态:todo|doing|wait|pending_review|rejected|done|dead。流转矩阵见 ALLOWED_TRANSITIONS:
  「被前置挡住」不占状态(todo+图算),wait 只留给图外等待;pending_review=已交付待验收,
  rejected=打回已裁决、返工未启动(泊位);doing→pending_review 交付必带
  criteria(交付报告指针),pending_review→done 验收过必带 criteria(验收结论指针),
  pending_review→rejected 打回登记必带 why(结论文件路径),rejected→doing 返工派工必带
  assignee;以上四处均过文件存在门(指针须指向真实存在的文件=子 agent 自登记的机械担保);
  验收直达门:review=required 的任务 todo/doing/wait→done 写入打回,
  done 唯一入口=pending_review→done;review=none 全边保留,升级口照样可走 pending_review;
  dead 是终态不可出(依赖满足判定把 dead 当满足,复活会炸图);done→todo 与
  pending_review→doing(打回即返工,跳过泊位)是回边,均必带 why。环在写入时拒绝,不做事后体检。
- 旧名兼容:待验收态原名 review,裸 token 读不出「等验收」方向,更名
  pending_review。normalize_status 读侧归一旧事件流(append-only 正本不改写);status
  命令仍收旧名(归一后按规范名落盘+更名提醒),check 对残留旧名给信息级警。

存储:事件流 JSONL(append-only),「当前状态」=折叠现算,不落盘。
- 为什么事件流:审计链=正本本身(不存在「忘补流水」);
  status 事件自带 from,重放可检测乱序/冲突。
- 写路径:load→fold→校验→append 单行;append 由账本级锁文件串行化
  (O_EXCL 原子创建,残留锁按 mtime 强拆)——worker/reviewer 各自自记也并发安全,
  不再依赖单写者纪律(那是 progress.py 时代的约束)。

命令:add / status / prio / note / dep / ready / list / graph / card / who / log / check。
运行:`python dag.py --file <dag.jsonl> <cmd> ...`(默认 ./dag.jsonl)。
测试:`pytest test_dag.py -q`。
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ---------- 常量与类型 ----------

STATUSES: tuple[str, ...] = ('todo', 'doing', 'wait', 'pending_review', 'rejected', 'done', 'dead')
MODULES: tuple[str, ...] = ('流程', '决策', '支撑')
INITIAL_STATUSES: tuple[str, ...] = ('todo', 'wait')  # add 的合法初始态
# 验收档:建账定不可变;缺省 required=需验收(done 唯一入口=pending_review)
REVIEW_LEVELS: tuple[str, ...] = ('none', 'required')
DEFAULT_REVIEW: str = 'required'

# 旧状态名→规范名:review 因裸 token 歧义更名 pending_review;
# 读侧归一历史事件,写侧 status 命令仍收旧名(归一后落盘),账本历史不改写
STATUS_ALIASES: dict[str, str] = {'review': 'pending_review'}


def normalize_status(s: str) -> str:
    """旧状态名归一到规范名;未知值原样返回,由校验层打回。"""
    return STATUS_ALIASES.get(s, s)

# 流转矩阵(dead 终态无出边;rejected=打回泊位)
ALLOWED_TRANSITIONS: frozenset[tuple[str, str]] = frozenset({
    ('todo', 'doing'), ('todo', 'done'), ('todo', 'dead'),
    ('doing', 'done'), ('doing', 'wait'), ('doing', 'dead'), ('doing', 'pending_review'),
    ('wait', 'todo'), ('wait', 'done'), ('wait', 'dead'),
    ('pending_review', 'done'), ('pending_review', 'doing'), ('pending_review', 'dead'),
    ('pending_review', 'rejected'),
    ('rejected', 'doing'), ('rejected', 'dead'),
    ('done', 'todo'),
})

# 终态:依赖满足判定里视为「已满足」
SATISFYING: frozenset[str] = frozenset({'done', 'dead'})

ID_RE = re.compile(r'^T-\d+$')
COND_ID_LEAK_RE = re.compile(r'T-\d+')  # cond 里出现任务 ID = 该建 deps 边却写了文字
# why 里像产物路径的引用(打回 why 规范要求附验收报告路径;软告警不挡写入)
PATH_RE = re.compile(r'[\w\-./\\]+\.(?:md|txt|log|json|jsonl|py|yaml|yml|png)')

MAX_NOTE = 500  # 单条 note 上限(字符),防流水账堆进账本
MAX_PRIORITY = 10  # 优先级上限(下限 0):降权延后语义走 wait 态,不用负值表达


class DagError(Exception):
    """带可读原因的打回异常;main 转 exit 2。"""


@dataclass
class Task:
    """图节点。字段语义见模块 docstring;assignee/since 仅 doing 态有效。"""

    id: str
    title: str
    module: str
    status: str
    deps: list[str] = field(default_factory=list)
    cond: str | None = None
    priority: int = 0
    criteria: list[str] = field(default_factory=list)
    review: str = DEFAULT_REVIEW
    assignee: str | None = None
    since: str | None = None
    created: str = ''
    dead_reason: str | None = None
    notes: list[str] = field(default_factory=list)


# ---------- 基础 IO ----------


def now_iso() -> str:
    return datetime.now().isoformat(timespec='seconds')


def load_events(path: Path) -> list[dict]:
    """读全部事件;坏行跳过并在返回结构外由 check 兜底(读路径不炸)。"""
    if not path.exists():
        return []
    events: list[dict] = []
    for i, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(ev, dict):
            ev['_line'] = i  # 供 check 定位,不入盘
            events.append(ev)
    return events


LOCK_WAIT_S = 10.0   # 等锁上限:超时视为并发写堆积或残留锁,报错给人看
LOCK_STALE_S = 60.0  # 锁文件 mtime 超过此秒数=持锁进程已死,强拆


def _lock_path(path: Path) -> Path:
    return path.with_name(path.name + '.lock')


def _acquire_lock(path: Path) -> Path:
    """抢账本级写锁(O_EXCL 原子创建防双抢)。锁只串行化写,不挡读。"""
    lock = _lock_path(path)
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + LOCK_WAIT_S
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock
        except FileExistsError:
            pass  # 锁被正常占用,走残留检查后重试
        except PermissionError:
            # Windows 特有:创建瞬间撞上「删除挂起」的同名锁文件(另一释放者正在
            # unlink,名字仍被占)。语义=锁被占,重试,不能当致命错误吞掉整次写入
            pass
        try:
            stale = time.time() - lock.stat().st_mtime > LOCK_STALE_S
        except FileNotFoundError:
            stale = False  # 别的等待者刚拆掉重抢了,当无残留处理
        if stale:
            # OSError 兜住两case:已被拆(FileNotFoundError)/Windows 删除挂起(PermissionError)
            with contextlib.suppress(OSError):
                lock.unlink()  # 残留锁(持锁进程崩了没放)强拆,下轮重抢
            continue
        if time.monotonic() >= deadline:
            raise DagError(f'账本写锁等待超时:{lock}(并发写堆积或残留锁未清)')
        time.sleep(0.05)


def _release_lock(lock: Path) -> None:
    try:
        lock.unlink()
    except FileNotFoundError:
        pass  # 已被超时路径强拆,无需处理
    except PermissionError:
        pass  # Windows 删除挂起(并发读 handle 未关),文件随即消失,无需处理


def append_event(path: Path, ev: dict) -> None:
    """单行 append;账本级锁串行化,worker/reviewer 各自自记也并发安全(见模块 docstring)。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = _acquire_lock(path)
    try:
        with open(path, 'a', encoding='utf-8', newline='') as f:
            f.write(json.dumps(ev, ensure_ascii=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
    finally:
        _release_lock(lock)


def actor_of(args: argparse.Namespace) -> str:
    return getattr(args, 'actor', None) or 'self'


def check_file_refs(texts: list[str], ledger_dir: Path) -> tuple[list[str], list[str]]:
    """提取文本中形似路径的引用,返回(全部引用, 其中不存在的)。
    文件存在门=子 agent 自登记的机械担保(指针说了不算,文件在才算)。
    相对路径按账本所在目录解析(reports/reviews 与账本同级),退而按当前目录;绝对路径直查。"""
    refs: list[str] = []
    for text in texts:
        for ref in PATH_RE.findall(text):
            if ref not in refs:
                refs.append(ref)
    missing: list[str] = []
    for r in refs:
        p = Path(r)
        ok = p.exists() if p.is_absolute() else (ledger_dir / p).exists() or p.exists()
        if not ok:
            missing.append(r)
    return refs, missing


# ---------- 折叠(事件流 → 当前状态) ----------


def _apply_status(t: Task, ev: dict, problems: list[str]) -> None:
    """status 事件落账。from 冲突=乱序或并发写,记 problem 不应用。"""
    frm = ev.get('from')
    frm = None if frm is None else normalize_status(frm)
    if frm is not None and frm != t.status:
        problems.append(f"L{ev.get('_line')}: {t.id} from 冲突(事件带 {frm},当前 {t.status})")
        return
    to = normalize_status(ev.get('to', ''))
    t.status = to
    if to == 'doing':
        t.assignee = ev.get('assignee')
        t.since = ev.get('ts')
    elif to == 'pending_review':
        # 交付报告指针进凭据(追加式);assignee 保留=交付者,打回派返工时可知原 worker
        for c in ev.get('criteria') or []:
            if c not in t.criteria:
                t.criteria.append(c)
    elif to == 'done':
        # criteria 追加式:预注册(add 时)+ 实证(done 时)共存,不覆盖
        for c in ev.get('criteria') or []:
            if c not in t.criteria:
                t.criteria.append(c)
        t.assignee = None
        t.since = None
    elif to == 'wait':
        t.cond = ev.get('cond')
        t.assignee = None
        t.since = None
    elif to == 'todo':
        # wait→todo 条件已解除,cond 清;done→todo 回退本就无 assignee
        if frm == 'wait':
            t.cond = None
        t.assignee = None
        t.since = None
    elif to == 'dead':
        t.dead_reason = ev.get('why')
        t.assignee = None
        t.since = None


def fold(events: list[dict]) -> tuple[dict[str, Task], list[str]]:
    """重放事件流得当前状态。problems 收结构问题(坏引用/状态冲突),不抛异常。"""
    tasks: dict[str, Task] = {}
    problems: list[str] = []
    for ev in events:
        typ = ev.get('type')
        ts = str(ev.get('ts', ''))
        if typ == 'add':
            spec = ev.get('task') or {}
            t = Task(
                id=spec.get('id', ''),
                title=spec.get('title', ''),
                module=spec.get('module', ''),
                status=spec.get('status', 'todo'),
                deps=list(spec.get('deps') or []),
                cond=spec.get('cond'),
                priority=spec.get('priority', 0),
                criteria=list(spec.get('criteria') or []),
                review=spec.get('review') or DEFAULT_REVIEW,
                created=ts,
            )
            if t.id in tasks:
                problems.append(f"L{ev.get('_line')}: id 重复 add {t.id}")
            else:
                tasks[t.id] = t
        elif typ == 'status':
            t = tasks.get(ev.get('id', ''))
            if t is None:
                problems.append(f"L{ev.get('_line')}: status 指向不存在任务 {ev.get('id')}")
            else:
                _apply_status(t, ev, problems)
        elif typ == 'note':
            t = tasks.get(ev.get('id', ''))
            if t is None:
                problems.append(f"L{ev.get('_line')}: note 指向不存在任务 {ev.get('id')}")
            else:
                t.notes.append(f"{ts} {ev.get('text', '')}")
        elif typ == 'dep':
            t = tasks.get(ev.get('id', ''))
            dep = ev.get('dep', '')
            if t is None:
                problems.append(f"L{ev.get('_line')}: dep 指向不存在任务 {ev.get('id')}")
            elif ev.get('op') == 'add' and dep not in t.deps:
                t.deps.append(dep)
            elif ev.get('op') == 'del' and dep in t.deps:
                t.deps.remove(dep)
        elif typ == 'prio':
            t = tasks.get(ev.get('id', ''))
            if t is None:
                problems.append(f"L{ev.get('_line')}: prio 指向不存在任务 {ev.get('id')}")
            else:
                t.priority = ev.get('value', 0)
        else:
            problems.append(f"L{ev.get('_line')}: 未知事件类型 {typ}")
    return tasks, problems


# ---------- 图运算(全部现算) ----------


def is_ready(tasks: dict[str, Task], t: Task) -> bool:
    """todo 且所有前置已终态。dead 算满足(砍掉的前置不堵下游)。"""
    return t.status == 'todo' and all(
        (d in tasks and tasks[d].status in SATISFYING) for d in t.deps
    )


def blocked_by(tasks: dict[str, Task], t: Task) -> list[str]:
    """未满足的 deps(不存在/未终态都算挡)。"""
    return [d for d in t.deps if not (d in tasks and tasks[d].status in SATISFYING)]


def dependents(tasks: dict[str, Task], tid: str) -> list[str]:
    """反向查询:谁依赖我。边只存单侧,反向现算,防双源。"""
    return [t.id for t in tasks.values() if tid in t.deps]


def criticality_map(tasks: dict[str, Task]) -> dict[str, tuple[int, int]]:
    """关键性打分(纯图现算,不落盘):每任务 → (最长下游活链, 下游活任务数)。
    只延伸到未终态任务(done/dead 不再延伸)——解锁价值只对还活着的下游存在。
    ready 任务的这两个数=它的 done 一举解锁多少工作,是「关键路径件先派」的机械口径。"""
    live = {tid for tid, t in tasks.items() if t.status not in SATISFYING}
    outs: dict[str, list[str]] = {tid: [] for tid in tasks}
    for t in tasks.values():
        if t.id in live:
            for d in t.deps:
                if d in live:
                    outs[d].append(t.id)
    chain: dict[str, int] = {}
    count: dict[str, int] = {}

    def visit(u: str) -> None:
        if u in chain:
            return  # 环在写入时已拒绝,此处防御式防重入
        chain[u] = 0
        count[u] = 0
        best = 0
        total = 0
        for v in outs[u]:
            visit(v)
            best = max(best, chain[v] + 1)
            total += 1 + count[v]
        chain[u] = best
        count[u] = total

    for tid in live:
        visit(tid)
    return {tid: (chain.get(tid, 0), count.get(tid, 0)) for tid in tasks}


def ready_set(tasks: dict[str, Task]) -> list[str]:
    """可派集,派单优先序:priority 降 → 关键链降 → 挡下游数降 → id 数字升。
    rejected(打回待返工)计入可派——返工派工也是派单。
    排序即建议——派单方取第一行即「下一个任务」,无需现场判断。"""
    crit = criticality_map(tasks)
    return sorted(
        (t.id for t in tasks.values() if is_ready(tasks, t) or t.status == 'rejected'),
        key=lambda tid: (-tasks[tid].priority, -crit[tid][0], -crit[tid][1],
                         int(tid.split('-')[1])),
    )


def find_cycle(tasks: dict[str, Task], extra: tuple[str, list[str]] | None = None) -> list[str] | None:
    """环检测;extra 用于「加边前预检」(把待加边并入图再找环)。返回环路径或 None。"""
    deps_map: dict[str, list[str]] = {t.id: list(t.deps) for t in tasks.values()}
    if extra is not None:
        deps_map.setdefault(extra[0], []).extend(extra[1])
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {k: WHITE for k in deps_map}
    stack: list[str] = []

    def dfs(u: str) -> list[str] | None:
        color[u] = GRAY
        stack.append(u)
        for v in deps_map.get(u, []):
            if v not in color:
                continue
            if color[v] == GRAY:
                return stack[stack.index(v):] + [v]
            if color[v] == WHITE:
                got = dfs(v)
                if got:
                    return got
        stack.pop()
        color[u] = BLACK
        return None

    for k in deps_map:
        if color[k] == WHITE:
            got = dfs(k)
            if got:
                return got
    return None


def topo_order(tasks: dict[str, Task]) -> list[str]:
    """Kahn 拓扑序(前置在前);有环时退化为已排部分+剩余原序(check 会另报环)。"""
    indeg = {t.id: 0 for t in tasks.values()}
    outs: dict[str, list[str]] = {t.id: [] for t in tasks.values()}
    for t in tasks.values():
        for d in t.deps:
            if d in indeg:
                indeg[t.id] += 1
                outs[d].append(t.id)
    order: list[str] = [k for k, v in indeg.items() if v == 0]
    order.sort()
    i = 0
    while i < len(order):
        u = order[i]
        i += 1
        for v in sorted(outs[u]):
            indeg[v] -= 1
            if indeg[v] == 0:
                order.append(v)
    if len(order) < len(indeg):  # 环内节点补尾,保证输出完整
        order.extend(sorted(k for k in indeg if k not in set(order)))
    return order


# ---------- 写入前校验 ----------


def next_id(tasks: dict[str, Task]) -> str:
    mx = 0
    for tid in tasks:
        m = re.fullmatch(r'T-(\d+)', tid)
        if m:
            mx = max(mx, int(m.group(1)))
    return f'T-{mx + 1}'


def validate_add(tasks: dict[str, Task], title: str, module: str, deps: list[str],
                 cond: str | None, criteria: list[str], priority: int = 0,
                 review: str = DEFAULT_REVIEW) -> Task:
    if not title.strip():
        raise DagError('标题不能为空')
    if module not in MODULES:
        raise DagError(f'module 须为 {"|".join(MODULES)} 之一,得到:{module}')
    if review not in REVIEW_LEVELS:
        raise DagError(f'review 须为 {"|".join(REVIEW_LEVELS)} 之一(缺省 required=需验收),得到:{review}')
    if not 0 <= priority <= MAX_PRIORITY:
        raise DagError(f'priority 须在 0..{MAX_PRIORITY}(0=缺省,10=最紧急;降权延后用 wait 态而非负值),得到:{priority}')
    for d in deps:
        if d not in tasks:
            raise DagError(f'deps 引用不存在任务:{d}(先建前置,再建后继)')
        if d == '':
            raise DagError('deps 含空项')
    status = 'wait' if cond else 'todo'
    if cond is not None:
        if '复查' not in cond:
            raise DagError('wait 必带复查时机(cond 里含「复查」)')
    task = Task(id=next_id(tasks), title=title.strip(), module=module, status=status,
                deps=deps, cond=cond, priority=priority, criteria=criteria, review=review)
    if status == 'wait':
        pass
    cyc = find_cycle(tasks, (task.id, list(deps)))
    if cyc:
        raise DagError('加边成环,拒绝:' + ' -> '.join(cyc))
    return task


def validate_status(tasks: dict[str, Task], tid: str, to: str, why: str | None,
                    cond: str | None, criteria: list[str], assignee: str | None,
                    ledger_dir: Path) -> dict:
    """构造并校验 status 事件;返回事件体(不含 type/ts/actor)。"""
    to = normalize_status(to)  # 旧名 review 收下归一,入盘用规范名
    t = tasks.get(tid)
    if t is None:
        raise DagError(f'任务不存在:{tid}')
    if to not in STATUSES:
        raise DagError(f'未知状态:{to}(合法:{"|".join(STATUSES)};旧名 review 自动归一)')
    if (t.status, to) not in ALLOWED_TRANSITIONS:
        raise DagError(f'非法流转 {t.status} -> {to}(dead 是终态;见 ALLOWED_TRANSITIONS)')
    # 验收直达门:required 档 done 唯一入口=pending_review;免审须建账时显式声明
    if to == 'done' and t.review == 'required' and t.status != 'pending_review':
        raise DagError(f'{tid} 建账时声明需验收(review=required):done 只能经 '
                       f'pending_review(交付→验收);确属免审小件,dead 后新任务 --review none 承接')
    if to == 'doing' and not assignee:
        raise DagError('doing 必带 --assignee(谁在做:self 或子 agent 标识)')
    if to == 'done' and not criteria and not t.criteria:
        raise DagError('done 必带 --criteria(完成凭据指针;预注册也为空时不可缺)')
    if to == 'wait':
        if not cond:
            raise DagError('wait 必带 --cond(外部条件;doing→wait 挂起也要写清在等什么)')
        if '复查' not in cond:
            raise DagError('wait 必带复查时机(cond 里含「复查」)')
    if to == 'dead' and not why:
        raise DagError('dead 必带 --why(原因:被取代/作废/并入哪)')
    if to == 'pending_review' and not criteria:
        raise DagError('pending_review 必带 --criteria(交付报告指针:worker 完成报告的路径)')
    if t.status == 'pending_review' and to == 'done' and not criteria:
        raise DagError('pending_review→done 验收过必带 --criteria(验收结论指针,与交付报告分开)')
    if t.status == 'pending_review' and to == 'doing' and not why:
        raise DagError('pending_review→doing 打回必带 --why(原因+验收报告路径)')
    if t.status == 'pending_review' and to == 'rejected' and not why:
        raise DagError('pending_review→rejected 打回登记必带 --why(结论文件路径;返工派工在 rejected→doing)')
    if t.status == 'done' and to == 'todo' and not why:
        raise DagError('done→todo 回退必带 --why(判错/返工原因)')
    # 文件存在门(四道,只卡子 agent 自登记的流转):指针说了不算,文件真实存在才放行
    if t.status == 'doing' and to == 'pending_review':
        refs, missing = check_file_refs(criteria, ledger_dir)
        if not refs or missing:
            detail = 'criteria 未指向任何文件' if not refs else '文件不存在:' + ','.join(missing)
            raise DagError(f'交付登记无效({detail});先写完成报告到 reports/ 再登记')
    if t.status == 'pending_review' and to == 'done':
        refs, missing = check_file_refs(criteria, ledger_dir)
        if not refs or missing:
            detail = 'criteria 未指向任何文件' if not refs else '文件不存在:' + ','.join(missing)
            raise DagError(f'验收登记无效({detail});先写结论文件到 reviews/ 再登记')
    if t.status == 'pending_review' and to == 'doing' and why:
        _, missing = check_file_refs([why], ledger_dir)
        if missing:
            raise DagError(f'打回 why 引用的文件不存在:{",".join(missing)};先写结论文件到 reviews/ 再打回')
    if t.status == 'pending_review' and to == 'rejected' and why:
        _, missing = check_file_refs([why], ledger_dir)
        if missing:
            raise DagError(f'打回登记 why 引用的文件不存在:{",".join(missing)};先写结论文件到 reviews/ 再登记')
    return {'id': tid, 'from': t.status, 'to': to, 'why': why,
            'cond': cond, 'criteria': criteria, 'assignee': assignee}


def validate_dep(tasks: dict[str, Task], tid: str, op: str, dep: str) -> None:
    t = tasks.get(tid)
    if t is None:
        raise DagError(f'任务不存在:{tid}')
    if op not in ('add', 'del'):
        raise DagError('dep op 须为 add|del')
    if not ID_RE.fullmatch(dep):
        raise DagError(f'dep 须为任务 ID(T-N),得到:{dep}')
    if op == 'add':
        if dep not in tasks:
            raise DagError(f'deps 引用不存在任务:{dep}')
        if dep == tid:
            raise DagError('不能依赖自己')
        cyc = find_cycle(tasks, (tid, [dep]))
        if cyc:
            raise DagError('加边成环,拒绝:' + ' -> '.join(cyc))
    else:
        if dep not in t.deps:
            raise DagError(f'{tid} 并不依赖 {dep}')


# ---------- 视图 ----------


def _status_badge(t: Task) -> str:
    extra = ''
    if t.status in ('doing', 'pending_review', 'rejected') and t.assignee:
        extra = f'@{t.assignee}'  # doing=执行者;pending_review/rejected=交付者,打回时派返工的线索
    if t.status == 'dead' and t.dead_reason:
        extra = f'({t.dead_reason})'
    return f'{t.status}{extra}'


def render_list(tasks: dict[str, Task], show_all: bool) -> str:
    lines = []
    act = [t for t in tasks.values() if t.status not in SATISFYING]
    show = list(tasks.values()) if show_all else act
    for t in sorted(show, key=lambda x: int(x.id.split('-')[1])):
        wait = blocked_by(tasks, t)
        dep_s = ','.join(t.deps) if t.deps else '-'
        block_s = f' [挡:{",".join(wait)}]' if wait and t.status == 'todo' else ''
        rev = ' [免审]' if t.review == 'none' else ''
        lines.append(f'{t.id}  {t.module}{rev}  {_status_badge(t)}  {t.title}{block_s}  deps={dep_s}')
    if not show_all:
        done_n = len(tasks) - len(act)
        lines.append(f'-- 活任务 {len(act)},终态(不显示) {done_n};--all 看全量')
    return '\n'.join(lines)


def render_ready(tasks: dict[str, Task]) -> str:
    rs = ready_set(tasks)
    doing = [t for t in tasks.values() if t.status == 'doing']
    waiting = [t for t in tasks.values() if t.status == 'wait']
    lines = [f'== 可派 ready({len(rs)})(序=优先级→关键链→挡下游) ==']
    for tid in rs:
        t = tasks[tid]
        ch, bl = criticality_map(tasks)[tid]
        p = f' P{t.priority}' if t.priority else ''
        r = ' [打回]' if t.status == 'rejected' else ''
        nv = ' [免审]' if t.review == 'none' else ''
        lines.append(f'  {tid}{p}{r}{nv}  链{ch} 挡{bl}  {t.module}  {t.title}')
    lines.append(f'== doing({len(doing)}) ==')
    for t in doing:
        lines.append(f'  {t.id}  @{t.assignee}  since={t.since}  {t.title}')
    reviewing = [t for t in tasks.values() if t.status == 'pending_review']
    lines.append(f'== pending_review 待验收({len(reviewing)}) ==')
    for t in reviewing:
        lines.append(f'  {t.id}  交付者@{t.assignee or "-"}  {t.title}')
    lines.append(f'== wait 外部等待({len(waiting)}) ==')
    for t in waiting:
        lines.append(f'  {t.id}  {t.title}  cond={t.cond}')
    blocked = [t for t in tasks.values() if t.status == 'todo' and not is_ready(tasks, t)]
    lines.append(f'== 被前置挡住({len(blocked)}) ==')
    for t in blocked:
        lines.append(f'  {t.id}  {t.title}  等:{",".join(blocked_by(tasks, t))}')
    return '\n'.join(lines)


def render_graph(tasks: dict[str, Task], mermaid: bool) -> str:
    if mermaid:
        lines = ['graph TD']
        for t in tasks.values():
            label = f'{t.id} {t.title}'
            lines.append(f'  {t.id}["{label}"]:::{t.status}')
        for t in tasks.values():
            for d in t.deps:
                lines.append(f'  {d} --> {t.id}')
        lines.append('  classDef done fill:#dfe,stroke:#393;')
        lines.append('  classDef dead fill:#eee,stroke:#999,color:#999;')
        lines.append('  classDef doing fill:#def,stroke:#369;')
        lines.append('  classDef pending_review fill:#fdf,stroke:#939;')
        lines.append('  classDef rejected fill:#fcc,stroke:#933;')
        lines.append('  classDef wait fill:#fec,stroke:#c93;')
        lines.append('  classDef todo fill:#fff,stroke:#666;')
        return '\n'.join(lines)
    lines = ['id    模块  状态            标题  依赖']
    for tid in topo_order(tasks):
        t = tasks[tid]
        deps = ' '.join(f'←{d}' for d in t.deps) or '-'
        lines.append(f'{t.id}  {t.module}  {_status_badge(t):<14} {t.title}  {deps}')
    rs = ready_set(tasks)
    lines.append(f'\nready({len(rs)}): {" ".join(rs) if rs else "-"}')
    cyc = find_cycle(tasks)
    if cyc:
        lines.append('!! 环:' + ' -> '.join(cyc))
    return '\n'.join(lines)


def render_card(tasks: dict[str, Task], tid: str) -> str:
    t = tasks.get(tid)
    if t is None:
        raise DagError(f'任务不存在:{tid}')
    rev = '免审' if t.review == 'none' else '需验收'
    lines = [f'== {t.id} {t.title} ==',
             f'模块:{t.module}  状态:{_status_badge(t)}  优先级:{t.priority}  创建:{t.created}  验收:{rev}']
    if t.deps:
        lines.append('前置:')
        for d in t.deps:
            dt = tasks.get(d)
            if dt is None:
                lines.append(f'  {d}  (!! 引用不存在)')
            else:
                ok = '√' if dt.status in SATISFYING else '×'
                lines.append(f'  {d}  [{dt.status}] {ok} {dt.title}')
    else:
        lines.append('前置:无')
    if t.cond:
        lines.append(f'外部等待:{t.cond}')
    if t.criteria:
        lines.append('凭据(预注册+实证):')
        for c in t.criteria:
            lines.append(f'  - {c}')
    if t.dead_reason:
        lines.append(f'终态原因:{t.dead_reason}')
    if t.notes:
        lines.append('附注:')
        for n in t.notes:
            lines.append(f'  - {n}')
    dps = dependents(tasks, tid)
    lines.append(f'被依赖:{",".join(dps) if dps else "无"}')
    return '\n'.join(lines)


def render_who(tasks: dict[str, Task], tid: str) -> str:
    t = tasks.get(tid)
    if t is None:
        raise DagError(f'任务不存在:{tid}')
    lines = [f'== {tid} {t.title} [{t.status}] ==']
    waiting_on = blocked_by(tasks, t)
    if waiting_on:
        lines.append(f'它在等({len(waiting_on)}):')
        for d in waiting_on:
            dt = tasks.get(d)
            mark = dt.status if dt else '不存在'
            lines.append(f'  ← {d} [{mark}] {dt.title if dt else ""}')
    else:
        lines.append('它在等:无(前置全满足或无前置)')
    dps = dependents(tasks, tid)
    if dps:
        lines.append(f'它挡着({len(dps)}):')
        for p in dps:
            pt = tasks[p]
            lines.append(f'  → {p} [{pt.status}] {pt.title}')
    else:
        lines.append('它挡着:无')
    return '\n'.join(lines)


# ---------- check(体检) ----------


def cmd_check(args: argparse.Namespace) -> int:
    path = Path(args.file)
    events = load_events(path)
    if not events:
        print(f'空事件流:{path}')
        return 0
    tasks, problems = fold(events)
    errors = list(problems)
    warns: list[str] = []
    for t in tasks.values():
        if t.module not in MODULES:
            errors.append(f'{t.id}: module 非法 {t.module}')
        if t.status not in STATUSES:
            errors.append(f'{t.id}: status 非法 {t.status}')
        for d in t.deps:
            if d not in tasks:
                errors.append(f'{t.id}: deps 悬空引用 {d}')
        if t.status == 'wait':
            if not t.cond:
                errors.append(f'{t.id}: wait 缺 cond')
            elif '复查' not in t.cond:
                errors.append(f'{t.id}: wait 的 cond 缺复查时机')
            if t.cond and COND_ID_LEAK_RE.search(t.cond):
                warns.append(f'{t.id}: cond 里出现任务 ID,该建 deps 边而非文字({t.cond})')
        if t.review not in REVIEW_LEVELS:
            errors.append(f'{t.id}: review 非法 {t.review}(合法:{"|".join(REVIEW_LEVELS)})')
        if t.status == 'done' and not t.criteria:
            errors.append(f'{t.id}: done 缺 criteria')
        if t.status == 'done' and t.review == 'required':
            # 重放侧同规则:required 的 done 必须有 pending_review→done 验收事件背书
            accepted = any(
                e.get('type') == 'status' and e.get('id') == t.id
                and normalize_status(e.get('from', '')) == 'pending_review'
                and normalize_status(e.get('to', '')) == 'done'
                for e in events)
            if not accepted:
                errors.append(f'{t.id}: review=required 却直达 done(无 pending_review→done 验收事件)')
        if t.status in ('pending_review', 'rejected'):
            if not t.criteria:
                errors.append(f'{t.id}: {t.status} 缺 criteria(交付报告指针)')
            else:
                _, missing = check_file_refs(t.criteria, path.parent)
                if missing:
                    errors.append(f'{t.id}: {t.status} 交付报告文件不存在:{",".join(missing)}')
        if t.status == 'doing':
            if not t.assignee:
                errors.append(f'{t.id}: doing 缺 assignee')
            since = t.since or ''
            last_ts = max((str(e.get('ts', '')) for e in events
                           if e.get('id') == t.id and e.get('type') == 'status'), default='')
            if last_ts and since and last_ts < since:
                errors.append(f'{t.id}: doing 之后还有更晚事件,状态可疑')
    cyc = find_cycle(tasks)
    if cyc:
        errors.append('依赖环:' + ' -> '.join(cyc))
    dup: dict[str, int] = {}
    for e in events:
        if e.get('type') == 'add':
            tid = (e.get('task') or {}).get('id', '')
            dup[tid] = dup.get(tid, 0) + 1
    for tid, n in dup.items():
        if n > 1:
            errors.append(f'{tid}: add 重复 {n} 次')
    legacy_n = sum(1 for e in events if e.get('type') == 'status'
                   and 'review' in (e.get('from'), e.get('to')))
    if legacy_n:
        warns.append(f'事件流含 {legacy_n} 处旧名 review(=pending_review,读侧已归一;新事件请写新名)')
    if errors:
        print(f'check 不过({len(errors)} 错,{len(warns)} 警):')
        for e in errors:
            print(f'  [错] {e}')
    else:
        print(f'check 过({len(tasks)} 任务,事件 {len(events)} 条)')
    for w in warns:
        print(f'  [警] {w}')
    return 1 if errors else 0


# ---------- 命令实现 ----------


def cmd_add(args: argparse.Namespace) -> int:
    path = Path(args.file)
    tasks, problems = fold(load_events(path))
    if problems:
        print('事件流已有结构问题,先 check 修复再写:', file=sys.stderr)
        for p in problems[:5]:
            print(f'  {p}', file=sys.stderr)
        return 1
    deps = [d.strip() for d in (args.dep or '').split(',') if d.strip()]
    criteria = [c.strip() for c in (args.criteria or '').split(';') if c.strip()]
    task = validate_add(tasks, args.title, args.module, deps, args.cond, criteria,
                        args.priority, args.review)
    ev = {'v': 1, 'ts': now_iso(), 'actor': actor_of(args), 'type': 'add',
          'task': {'id': task.id, 'title': task.title, 'module': task.module,
                   'status': task.status, 'deps': task.deps, 'cond': task.cond,
                   'priority': task.priority, 'criteria': task.criteria,
                   'review': task.review}}
    append_event(path, ev)
    gate = 'wait(外部等待)' if task.status == 'wait' else 'todo'
    gate += '(被前置挡,前置过自动就绪)' if task.status == 'todo' and task.deps else ''
    print(f'已登记 {task.id} [{gate}] {task.title}')
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    path = Path(args.file)
    tasks, _ = fold(load_events(path))
    to = normalize_status(args.to)
    if args.to != to:  # 旧名写入:收下并提醒,事件落规范名
        print(f'[提醒] 状态旧名 {args.to} 已更名 {to},本次按 {to} 记账',
              file=sys.stderr)
    criteria = [c.strip() for c in (args.criteria or '').split(';') if c.strip()]
    body = validate_status(tasks, args.id, to, args.why, args.cond,
                           criteria, args.assignee, path.parent)
    # 打回 why 应附验收报告路径(规范=先写结论文件再打回);缺路径软告警不挡写入
    if body['from'] == 'pending_review' and to == 'doing' and args.why \
            and not PATH_RE.search(args.why):
        print('[警] 打回 why 未引用产物路径:规范要求附验收报告指针(reviews/T-N-rK.md)',
              file=sys.stderr)
    ev = {'v': 1, 'ts': now_iso(), 'actor': actor_of(args), 'type': 'status', **body}
    append_event(path, ev)
    extra = ''
    if to == 'doing':
        extra = f'@{args.assignee}'
    elif to == 'pending_review':
        extra = '交付:' + ';'.join(criteria)
    elif to == 'done':
        t = tasks[args.id]
        merged = list(dict.fromkeys(t.criteria + criteria))
        extra = '凭据:' + ';'.join(merged)
    elif to in ('dead',) and args.why:
        extra = args.why
    elif to == 'todo' and args.why:
        extra = args.why
    t2 = tasks[args.id]
    downstream = dependents(tasks, args.id)
    line = f'{args.id}: {body["from"]} -> {to} {extra}'.rstrip()
    print(line)
    if t2.deps and to == 'todo':
        pass
    if to in SATISFYING and downstream:
        print(f'下游自动重算就绪:{",".join(downstream)}(ready 子命令查可派清单)')
    return 0


def cmd_note(args: argparse.Namespace) -> int:
    path = Path(args.file)
    tasks, _ = fold(load_events(path))
    if args.id not in tasks:
        print(f'任务不存在:{args.id}', file=sys.stderr)
        return 1
    if not args.text.strip():
        print('note 不能为空', file=sys.stderr)
        return 2
    if len(args.text) > MAX_NOTE:
        print(f'note 超长({len(args.text)} > {MAX_NOTE});长内容放产物文档,note 存指针', file=sys.stderr)
        return 2
    append_event(path, {'v': 1, 'ts': now_iso(), 'actor': actor_of(args),
                        'type': 'note', 'id': args.id, 'text': args.text.strip()})
    print(f'{args.id} +note')
    return 0


def cmd_dep(args: argparse.Namespace) -> int:
    path = Path(args.file)
    tasks, _ = fold(load_events(path))
    for dep in args.add or []:
        validate_dep(tasks, args.id, 'add', dep)
    for dep in args.del_ or []:
        validate_dep(tasks, args.id, 'del', dep)
    for dep in args.add or []:
        append_event(path, {'v': 1, 'ts': now_iso(), 'actor': actor_of(args),
                            'type': 'dep', 'op': 'add', 'id': args.id, 'dep': dep})
        print(f'{args.id} +dep {dep}')
    for dep in args.del_ or []:
        append_event(path, {'v': 1, 'ts': now_iso(), 'actor': actor_of(args),
                            'type': 'dep', 'op': 'del', 'id': args.id, 'dep': dep})
        print(f'{args.id} -dep {dep}')
    return 0


def cmd_prio(args: argparse.Namespace) -> int:
    """设/改优先级(prio 事件入正本,重放折叠)。大者先派;用于插队与降权,不改变图。"""
    path = Path(args.file)
    tasks, _ = fold(load_events(path))
    if args.id not in tasks:
        raise DagError(f'任务不存在:{args.id}')
    if not 0 <= args.value <= MAX_PRIORITY:
        raise DagError(f'priority 须在 0..{MAX_PRIORITY}(0=缺省,10=最紧急;降权延后用 wait 态而非负值),得到:{args.value}')
    append_event(path, {'v': 1, 'ts': now_iso(), 'actor': actor_of(args),
                        'type': 'prio', 'id': args.id, 'value': args.value})
    print(f'{args.id} 优先级 -> {args.value}')
    return 0


def cmd_ready(args: argparse.Namespace) -> int:
    tasks, _ = fold(load_events(Path(args.file)))
    print(render_ready(tasks))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    tasks, _ = fold(load_events(Path(args.file)))
    print(render_list(tasks, args.all))
    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    tasks, _ = fold(load_events(Path(args.file)))
    print(render_graph(tasks, args.mermaid))
    return 0


def cmd_card(args: argparse.Namespace) -> int:
    tasks, _ = fold(load_events(Path(args.file)))
    print(render_card(tasks, args.id))
    return 0


def cmd_who(args: argparse.Namespace) -> int:
    tasks, _ = fold(load_events(Path(args.file)))
    print(render_who(tasks, args.id))
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    """任务事件时间线+交付/打回计数。历史查询单一入口,替代裸 grep dag.jsonl。"""
    path = Path(args.file)
    events = load_events(path)
    tasks, _ = fold(events)
    t = tasks.get(args.id)
    if t is None:
        raise DagError(f'任务不存在:{args.id}')
    lines = [f'== {t.id} {t.title} [{t.status}] 事件时间线 ==']
    delivered = rejected = 0
    for ev in events:
        typ = ev.get('type')
        if typ == 'add':
            if (ev.get('task') or {}).get('id') != t.id:
                continue
            desc = 'add:登记' + ('(免审)' if (ev.get('task') or {}).get('review') == 'none' else '')
        elif ev.get('id') != t.id:
            continue
        elif typ == 'status':
            frm, to = normalize_status(ev.get('from', '')), normalize_status(ev.get('to', ''))
            if to == 'pending_review':
                delivered += 1
            if frm == 'pending_review' and to in ('doing', 'rejected'):
                rejected += 1
            bits = []
            if ev.get('assignee'):
                bits.append(f"@{ev['assignee']}")
            if ev.get('criteria'):
                bits.append('凭据:' + ';'.join(ev['criteria']))
            if ev.get('why'):
                bits.append(f"why:{ev['why']}")
            if ev.get('cond'):
                bits.append(f"cond:{ev['cond']}")
            desc = f'{frm} -> {to}' + ('  ' + '  '.join(bits) if bits else '')
        elif typ == 'note':
            desc = f"note:{ev.get('text', '')}"
        elif typ == 'dep':
            desc = f"dep {ev.get('op')}: {ev.get('dep')}"
        else:
            continue
        lines.append(f"{ev.get('ts', '')} [{ev.get('actor', '')}] {desc}")
    # 返工熔断判据的官方口径:打回 ≥3 次=规格问题,停派返工、立项规格重审
    lines.append(f'-- 交付 {delivered} 次,打回 {rejected} 次;当前 {t.status}')
    print('\n'.join(lines))
    return 0


# ---------- CLI ----------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog='dag.py',
        description='DAG 任务图管理(事件流正本;数据模型与状态机见本文件 docstring)')
    p.add_argument('--file', default='dag.jsonl', help='事件流文件(默认 ./dag.jsonl)')
    p.add_argument('--actor', help='操作者标识(默认 self;编排者可填子 agent 汇报来源)')
    sub = p.add_subparsers(dest='cmd', required=True)

    sp = sub.add_parser('add', help='登记任务(默认 todo;给 --cond 即 wait)')
    sp.add_argument('title')
    sp.add_argument('--module', required=True, help='流程|决策|支撑')
    sp.add_argument('--dep', help='前置任务 ID,逗号分隔')
    sp.add_argument('--cond', help='外部等待条件(须含「复查」;提供则初始为 wait)')
    sp.add_argument('--criteria', help='完成凭据预注册,分号分隔')
    sp.add_argument('--priority', type=int, default=0,
                    help='派单优先级(0..10,大者先派;默认 0)')
    sp.add_argument('--review', default=DEFAULT_REVIEW,
                    help='验收档:required=需验收(缺省,done 只能经 pending_review)|'
                         'none=免审(可直达 done;免审资格判据见 SKILL §14)')
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser('status', help='状态流转(按流转矩阵校验)')
    sp.add_argument('id')
    sp.add_argument('to', help='todo|doing|wait|pending_review|rejected|done|dead(旧名 review 仍收,自动归一)')
    sp.add_argument('--assignee', help='doing 必带:谁在做')
    sp.add_argument('--criteria',
                    help='done 必带(验收过=结论指针);doing→pending_review 必带(交付报告指针);'
                         '分号分隔,追加不覆盖')
    sp.add_argument('--cond', help='wait 必带:外部条件+复查时机')
    sp.add_argument('--why', help='dead 必带;done→todo 回退必带;'
                                  'pending_review→doing 打回必带(原因+验收报告路径)')
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser('note', help='附加一条注记(不改状态)')
    sp.add_argument('id')
    sp.add_argument('text')
    sp.set_defaults(func=cmd_note)

    sp = sub.add_parser('dep', help='增删依赖边')
    sp.add_argument('id')
    sp.add_argument('--add', action='append', help='加前置(可多次)')
    sp.add_argument('--del', dest='del_', action='append', help='删前置(可多次)')
    sp.set_defaults(func=cmd_dep)

    sp = sub.add_parser('prio', help='设置优先级(0..10,大者先派;缺省 0)')
    sp.add_argument('id')
    sp.add_argument('value', type=int)
    sp.set_defaults(func=cmd_prio)

    sp = sub.add_parser('ready', help='可派(按 优先级→关键链→挡下游 排序)+doing+pending_review+wait+被挡(派单入口)')
    sp.set_defaults(func=cmd_ready)

    sp = sub.add_parser('list', help='活任务列表(--all 含终态)')
    sp.add_argument('--all', action='store_true')
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser('graph', help='拓扑视图(--mermaid 输出 mermaid)')
    sp.add_argument('--mermaid', action='store_true')
    sp.set_defaults(func=cmd_graph)

    sp = sub.add_parser('card', help='任务卡(派单直接引用)')
    sp.add_argument('id')
    sp.set_defaults(func=cmd_card)

    sp = sub.add_parser('who', help='阻断分析:它在等谁/它挡着谁')
    sp.add_argument('id')
    sp.set_defaults(func=cmd_who)

    sp = sub.add_parser('log', help='任务事件时间线+交付/打回计数(历史查询)')
    sp.add_argument('id')
    sp.set_defaults(func=cmd_log)

    sp = sub.add_parser('check', help='体检:重放校验+悬空+环+必带字段+验收档一致性')
    sp.set_defaults(func=cmd_check)
    return p


def force_utf8_stdio() -> None:
    """中文 Windows 控制台默认 GBK;强制 UTF-8 输出防中文崩(与 progress.py 同因)。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if reconfigure is not None:
            try:
                reconfigure(encoding='utf-8', errors='replace')
            except (ValueError, OSError):
                pass


REMINDER_LINE = '[提醒] dag.py 数据模型/状态机/流转矩阵见本脚本 docstring;改动设计先对齐规范再动代码'


def main(argv: list[str]) -> int:
    force_utf8_stdio()
    args = build_parser().parse_args(argv)
    try:
        code = int(args.func(args))
    except DagError as e:
        print(f'打回:{e}', file=sys.stderr)
        print(REMINDER_LINE)
        return 2
    print(REMINDER_LINE)
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
