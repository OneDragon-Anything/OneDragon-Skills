"""progress.py — 进度账本管理 CLI(写入格式门 + 结构体检 + 机械聚合 + 流水)。

规范单一源:本 skill 目录 SKILL.md(§2 结构 / §3 行文法 / §4 状态机 / §6 聚合 / §7 脚本)。
仅用 Python 3.11 标准库。所有写操作:Markdown 读→改→临时文件+os.replace 原子替换;
流水 JSONL 用 append 模式逐行写——.debug 不入 git 无版本兜底,半写残文件不可接受。

设计取舍(规格歧义处取保守):
- write 更新已有行时,新字段与旧行括号内容合并(--ref/--next/--pre/--condition/--note
  覆盖对应前缀的旧 token;无前缀的旧 token 视为指针/结论保留,--ref 提供时整体替换)。
  理由:更新状态时往往只带 --status,若不合并旧字段,「进行中→已过」会丢指针被打回。
- 流水藏活任务检测按规格只扫 kind=账本变更 条目;主题从 text 的「<文件名> <主题>:」格式解析。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# 七词封闭状态机(SKILL.md §4)
STATUSES: tuple[str, ...] = ('已过', '未做', '进行中', '锁定', '待激活', '不适用', '部分过')

# 自造词别名映射建议(SKILL.md §4;check 报错时列出,write 拒绝未映射词)
ALIAS_MAP: dict[str, str] = {
    '已修': '已过',
    '已挂': '待激活',
    '在飞': '进行中',
    '候用户': '锁定(前置=用户裁决)',
    '条件已解除': '未做(注:条件已解除)',
    '收编': '已过',
    '已落地': '已过',
    '已闭环': '已过',
}

MODULES: tuple[str, ...] = ('流程', '决策', '支撑')

# 叙事特征词(SKILL.md §7 check③):账本行内出现=流水账退化前兆,≥5 计 warning
NARRATIVE_RE: re.Pattern[str] = re.compile(r'(已派|验收\(|板面[:：]|判读\()')

# 指针特征:含路径分隔符 / .md / ADR / commit 哈希样字符串(check② 已过必带)
POINTER_RE: re.Pattern[str] = re.compile(r'(/|\.md|ADR|[0-9a-f]{7,40})')

# 行文法:[编号 ]<主题>——<状态词>(<括号内容>);破折号=两个全角「——」;子行两空格缩进
LINE_RE: re.Pattern[str] = re.compile(
    r'^(?P<indent>  )?(?:(?P<num>\d+[.、]?\s+)\s*)?'
    r'(?P<topic>.+?)——(?P<status>[^()——]+?)\((?P<body>.+?)\)\s*$'
)

MAX_JOURNAL_TEXT = 2000  # 流水单条 text 上限(字符)
MAX_LEDGER_LINES = 300  # 账本行数阈值,超了报警建议切档
MAX_NOTE = 80  # --note 一行补充上限(字)


class LedgerError(Exception):
    """带用户可读原因的打回异常(write 内部用,main 转 exit 2)。"""


# ---------- 基础 IO ----------


def read_file(path: Path) -> str:
    """UTF-8 无 BOM 读;字节读入保留原换行风格(join 时再还原)。"""
    data = path.read_bytes()
    if data.startswith(b'\xef\xbb\xbf'):
        # 历史 BOM 兼容读入,写回时不带——规范是无 BOM
        data = data[3:]
    return data.decode('utf-8')


def atomic_write(path: Path, text: str) -> None:
    """临时文件 + os.replace 原子替换,杜绝半写残文件(规格硬要求)。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + '.', suffix='.tmp')
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(text.encode('utf-8'))
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def detect_newline(text: str) -> str:
    return '\r\n' if '\r\n' in text else '\n'


def find_iter_dir(file_path: Path) -> Path | None:
    """从模块文件向上找迭代目录(判据:祖先目录存在入口 进度.md)。

    入口文件由 init 生成且含「# 迭代」头;仅凭祖先有同名文件不够——模块自己就叫 进度.md,
    所以校验内容头,防止把自己所在目录当迭代目录。
    """
    for anc in file_path.resolve().parents:
        entry = anc / '进度.md'
        if entry.exists() and read_file(entry).lstrip().startswith('# 迭代'):
            return anc
    return None


def journal_append(iter_dir: Path, kind: str, text: str) -> None:
    """当日流水 jsonl 追加一条(append 逐行写,天然并发安全到行级)。"""
    if len(text) > MAX_JOURNAL_TEXT:
        raise LedgerError(f'流水 text 超长({len(text)} > {MAX_JOURNAL_TEXT} 字符)')
    now = datetime.now()
    entry = {'ts': now.isoformat(timespec='seconds'), 'kind': kind, 'text': text, 'refs': []}
    path = iter_dir / f'流水-{now.strftime("%Y%m%d")}.jsonl'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# ---------- 行文法解析 ----------


class TaskLine:
    """一条任务行的解析结果。indent=是否缩进子行;raw=原始行文本(更新时逐位保真用)。"""

    def __init__(self, raw: str, indent: bool, topic: str, status: str, body: str, num: str | None = None) -> None:
        self.raw = raw
        self.indent = indent
        self.topic = topic
        self.status = status
        self.body = body
        self.num = num


def parse_task_line(line: str) -> tuple[TaskLine | None, str | None]:
    """解析一行任务行。返回 (TaskLine, None) 或 (None, 错误信息)。

    非任务行(# 头 / ## 分节 / > 治理指针 / 空行)返回 (None, None)——跳过不校验。
    """
    stripped = line.strip()
    if not stripped or stripped.startswith('#') or stripped.startswith('>'):
        return None, None
    m = LINE_RE.match(line)
    if not m:
        return None, f'行文法不符(期望 `[编号 ]<主题>——<状态词>(<括号内容>)`):{line.strip()}'
    topic = m.group('topic').strip()
    status = m.group('status').strip()
    body = m.group('body').strip()
    if not topic:
        return None, f'主题为空:{line.strip()}'
    if status not in STATUSES:
        hint = ALIAS_MAP.get(status)
        sug = f';建议映射:{status}→{hint}' if hint else f';非规范状态词,规范七词:{"/".join(STATUSES)}'
        return None, f'自造状态词「{status}」{sug}:{line.strip()}'
    if not body:
        return None, f'括号内容为空(指针/验证锚点/结论必填):{line.strip()}'
    return TaskLine(line, m.group('indent') is not None, topic, status, body, m.group('num')), None


def validate_status_fields(status: str, body: str) -> str | None:
    """状态-字段一致性(§4)。返回 None=合规,否则为打回原因(write 与 check 共用同一判据)。"""
    if status == '已过':
        if '下一步' in body:
            return '已过 不得含「下一步」(已闭环即无下一步)'
        if not POINTER_RE.search(body):
            return '已过 必带指针(括号内含 / 或 .md 或 ADR 或 commit 哈希样字符串)'
    elif status == '进行中':
        if '下一步' not in body:
            return '进行中 必带「下一步:<动作>」'
    elif status == '锁定':
        if '前置=' not in body:
            return '锁定 必带「前置=<任务标识>」'
    elif status == '待激活':
        if '条件=' not in body:
            return '待激活 必带「条件=<条件+复查时机>」'
        if '复查' not in body:
            return '待激活 必带复查时机(条件里含「复查」字样)'
    elif status == '部分过':
        if '缺=' not in body:
            return '部分过 必带「缺=<什么>」'
    elif status == '不适用':
        # 文法层已保证括号非空;这里表达语义:括号内容即「为何」
        return None
    return None


def build_body(
    ref: str | None,
    next_: str | None,
    pre: str | None,
    condition: str | None,
    note: str | None,
    old_body: str | None = None,
    drop_next: bool = False,
) -> str:
    """组装括号内容;old_body 提供时做字段合并(见模块头「设计取舍」)。

    token 规约:「下一步:…」「前置=…」「条件=…」「缺=…」为具名 token,新值覆盖旧值;
    其余 token 视为指针/一行结论,--ref 提供时被新 ref 替换,否则保留;--note 追加在末尾。
    """
    named_prefixes = ('下一步:', '下一步：', '前置=', '条件=', '缺=')
    old_tokens = [t.strip() for t in old_body.split(';')] if old_body else []
    named: dict[str, str] = {}
    free: list[str] = []
    for tok in old_tokens:
        if not tok:
            continue
        hit = next((p for p in named_prefixes if tok.startswith(p)), None)
        if hit:
            # 「下一步:」与全角冒号变体归一为半角 key
            key = '下一步:' if hit.startswith('下一步') else hit
            named[key] = tok
        else:
            free.append(tok)

    if ref is not None:
        free = [ref]
    if next_ is not None:
        named['下一步:'] = f'下一步:{next_}'
    elif drop_next:
        # 状态迁到「已过」时旧「下一步」必被丢弃(一致性硬约束:已过不得含下一步)
        named.pop('下一步:', None)
    if pre is not None:
        named['前置='] = f'前置={pre}'
    if condition is not None:
        named['条件='] = f'条件={condition}'
        # 复查时机通常写在 condition 值里,覆盖后旧条件作废,避免双条件残留
    if note is not None:
        if len(note) > MAX_NOTE:
            raise LedgerError(f'--note 超长({len(note)} > {MAX_NOTE} 字)')
        named['__note__'] = note

    parts: list[str] = list(free)
    for key in ('下一步:', '前置=', '条件=', '缺='):
        if key in named:
            parts.append(named[key])
    if '__note__' in named:
        parts.append(named['__note__'])
    return ';'.join(parts)


def format_line(task: TaskLine) -> str:
    """由解析字段重建行文本,保持文法形状(缩进/编号)。"""
    prefix = '  ' if task.indent else ''
    num = (task.num or '') if task.num else ''
    return f'{prefix}{num}{task.topic}——{task.status}({task.body})'


# ---------- init ----------


GOVERNANCE_LINE = '> 治理指针:流水=流水-YYYYMMDD.jsonl(append-only);归档=归档-<日期>.md(不入检索);账本行文法见 SKILL §3。'


def entry_text(iter_dir: Path, goal: str, criteria: str) -> str:
    """入口:迭代名 / 目标 / 判据 / 治理说明,各占一行(init 生成,此后不维护)。"""
    return f'# 迭代 {iter_dir.name}\n目标:{goal}\n判据:{criteria}\n{GOVERNANCE_LINE}\n'


def module_text(module: str) -> str:
    """模块账本头:类型行 + 治理指针;支撑文件首节固定「## 其他」(规格硬要求)。"""
    head = f'# {module}\n{GOVERNANCE_LINE}\n'
    if module == '支撑':
        head += '\n## 其他\n'
    return head


def cmd_init(args: argparse.Namespace) -> int:
    iter_dir = Path(args.iter_dir)
    iter_dir.mkdir(parents=True, exist_ok=True)
    entry = iter_dir / '进度.md'
    # 幂等:已存在不覆盖——迭代目录可能已有真实账本,覆盖=毁账
    if not entry.exists():
        atomic_write(entry, entry_text(iter_dir, args.goal, args.criteria))
    for module in MODULES:
        mdir = iter_dir / module
        mdir.mkdir(exist_ok=True)
        mfile = mdir / '进度.md'
        if not mfile.exists():
            atomic_write(mfile, module_text(module))
    print(f'init 完成:{iter_dir}(已存在的文件未覆盖)')
    return 0


# ---------- write ----------


def load_ledger(path: Path) -> tuple[str, list[str]]:
    text = read_file(path)
    lines = text.split('\n')
    # split('\n') 会因尾部换行多出一个空串,记回来以保逐位还原
    if lines and lines[-1] == '' and text.endswith('\n'):
        lines.pop()
    return detect_newline(text), lines


def find_task(lines: list[str], topic: str, indent: bool) -> int | None:
    """按主题精确等值 + 缩进层级找任务行下标。父任务在顶层找,子任务在缩进行找。"""
    for i, ln in enumerate(lines):
        task, err = parse_task_line(ln)
        if err or task is None:
            continue
        if task.topic == topic and task.indent == indent:
            return i
    return None


def section_insert_index(lines: list[str], section: str) -> int:
    """定位「## <section>」分节的插入点(节尾 = 下一个 ## 或 EOF);无该节则新开在文件尾。"""
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == f'## {section}':
            start = i
            break
    if start is None:
        # 新开节:前留一空行,节名 + 空行,返回内容插入点
        lines.extend(['', f'## {section}', ''])
        return len(lines)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip().startswith('## '):
            end = j
            break
    return end


def cmd_write(args: argparse.Namespace) -> int:
    try:
        return _write_impl(args)
    except LedgerError as e:
        print(f'打回:{e}', file=sys.stderr)
        return 2


def _write_impl(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        raise LedgerError(f'账本文件不存在(先跑 init):{path}')
    if args.status not in STATUSES:
        hint = ALIAS_MAP.get(args.status)
        raise LedgerError(f'非规范状态词「{args.status}」;规范七词:{"/".join(STATUSES)}' + (f';建议映射:{hint}' if hint else ''))

    newline, lines = load_ledger(path)
    old_task: TaskLine | None = None
    old_idx: int | None = None

    def ensure_body(body: str) -> None:
        # 行文法硬约束:括号内容非空(指针/验证锚点/一行结论至少其一)
        if not body:
            raise LedgerError('括号内容非空(至少提供 --ref/--next/--pre/--condition/--note 之一)')


    if args.parent:
        # 父行只在顶层找;不存在则自动创建(状态=进行中,必带 --next)
        parent_created = False
        p_idx = find_task(lines, args.parent, indent=False)
        if p_idx is None:
            if not args.next:
                raise LedgerError(f'父任务「{args.parent}」不存在,自动创建要求必带 --next')
            p_body = f'下一步:{args.next}'
            err = validate_status_fields('进行中', p_body)
            if err:
                raise LedgerError(err)
            lines.append(f'{args.parent}——进行中({p_body})')
            p_idx = len(lines) - 1
            parent_created = True
            # --next 语义归父行(自动创建的进行中态必带下一步),不再塞进子行 body
            child_next: str | None = None
        else:
            child_next = args.next
        # 子行插到父行既有子行块之后(紧跟父行也行,块尾更整洁)
        insert_at = p_idx + 1
        while insert_at < len(lines) and lines[insert_at].startswith('  '):
            insert_at += 1
        body = build_body(args.ref, child_next, args.pre, args.condition, args.note)
        ensure_body(body)
        err = validate_status_fields(args.status, body)
        if err:
            raise LedgerError(err)
        new_raw = f'  {args.topic}——{args.status}({body})'
        lines.insert(insert_at, new_raw)
        old_status = '新增'
    else:
        old_idx = find_task(lines, args.topic, indent=False)
        if old_idx is not None:
            old_task, _ = parse_task_line(lines[old_idx])
            assert old_task is not None
            body = build_body(args.ref, args.next, args.pre, args.condition, args.note,
                              old_body=old_task.body, drop_next=(args.status == '已过'))
            ensure_body(body)
            err = validate_status_fields(args.status, body)
            if err:
                raise LedgerError(err)
            new_task = TaskLine('', False, args.topic, args.status, body, old_task.num)
            lines[old_idx] = format_line(new_task)
            old_status = old_task.status
        else:
            body = build_body(args.ref, args.next, args.pre, args.condition, args.note)
            ensure_body(body)
            err = validate_status_fields(args.status, body)
            if err:
                raise LedgerError(err)
            if args.section:
                if not str(path).endswith(str(Path('支撑') / '进度.md')) and '/支撑/' not in str(path).replace('\\', '/') and not path.parent.name == '支撑':
                    raise LedgerError('--section 仅支撑文件可用')
                insert_at = section_insert_index(lines, args.section)
            else:
                insert_at = len(lines)
            lines.insert(insert_at, f'{args.topic}——{args.status}({body})')
            old_status = '新增'

    # 原子写回(读→改→os.replace)
    atomic_write(path, newline.join(lines) + ('\n' if lines else ''))

    # 每次变异必 journal 一条(审计链与账本损坏兜底二合一,SKILL §7)
    iter_dir = find_iter_dir(path)
    if iter_dir is None:
        raise LedgerError(f'未找到迭代目录(祖先无入口 进度.md),变异无法记流水:{path}')
    journal_append(iter_dir, '账本变更', f'{path.name} {args.topic}: {old_status}→{args.status}')
    print(f'write 完成:{args.topic} {old_status}→{args.status}')
    return 0


# ---------- check ----------


def iter_ledgers(iter_dir: Path) -> list[Path]:
    """全部账本 = 递归扫 进度.md(入口文件跳过——三行结构非任务行,文法校验会误伤)。"""
    out = []
    for p in sorted(iter_dir.rglob('进度.md')):
        if p.parent == iter_dir:
            continue
        out.append(p)
    return out


def check_ledger(path: Path) -> tuple[list[str], list[str], dict[str, TaskLine]]:
    """单文件体检①②③④。返回 (errors, warnings, {topic: task})。"""
    errors: list[str] = []
    warnings: list[str] = []
    text = read_file(path)
    lines = text.split('\n')
    if len(lines) > MAX_LEDGER_LINES:
        warnings.append(f'[④切档] {path} 共 {len(lines)} 行 > {MAX_LEDGER_LINES},建议切归档-<日期>.md')

    tasks: dict[str, TaskLine] = {}
    for ln in lines:
        task, err = parse_task_line(ln)
        if err:
            errors.append(f'[①文法] {path}: {err}')
            continue
        if task is None:
            continue
        tasks[task.topic] = task
        ferr = validate_status_fields(task.status, task.body)
        if ferr:
            errors.append(f'[②一致性] {path}: <{task.topic}> {ferr}')
        hits = len(NARRATIVE_RE.findall(ln))
        if hits >= 5:
            warnings.append(f'[③叙事] {path}: <{task.topic}> 命中叙事特征词 {hits} 处,过程叙事请入流水')

    # ⑥ 父子塌缩检查:父行(有缩进子行的顶层行) vs 其子行
    top_tasks: list[TaskLine] = [t for t in tasks.values() if not t.indent]
    child_of: dict[str, list[TaskLine]] = {}
    for t in tasks.values():
        if t.indent:
            # 子行归属:文中它上方最近的顶层任务行
            child_of.setdefault(t.topic, []).append(t)
    # 归属需按行序算,重扫一遍
    child_of = {}
    current_parent: TaskLine | None = None
    for ln in lines:
        task, _ = parse_task_line(ln)
        if task is None:
            continue
        if task.indent:
            if current_parent is not None:
                child_of.setdefault(current_parent.topic, []).append(task)
        else:
            current_parent = task
    for parent in top_tasks:
        kids = child_of.get(parent.topic, [])
        if not kids:
            continue
        if parent.status == '已过':
            unpassed = [k for k in kids if k.status not in ('已过', '不适用')]
            if unpassed:
                errors.append(
                    f'[⑥塌缩] {path}: 父行 <{parent.topic}> 标已过但有未过子行:{"/".join(k.topic for k in unpassed)}'
                )
        if all(k.status in ('已过', '不适用') for k in kids):
            warnings.append(f'[⑥塌缩] {path}: 父行 <{parent.topic}> 全部子行已过/不适用,可塌缩为父行一行收口')
    return errors, warnings, tasks


def check_journal_orphans(iter_dir: Path, all_tasks: dict[str, TaskLine]) -> list[str]:
    """check⑤ 流水藏活任务:kind=账本变更 条目的主题带「待/下一步」且账本无对应行 → 报警。"""
    warnings: list[str] = []
    for jp in sorted(iter_dir.glob('流水-*.jsonl')):
        for lineno, raw in enumerate(read_file(jp).splitlines(), 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                warnings.append(f'[⑤流水] {jp.name}:{lineno} 非法 JSON 行,跳过(流水为 append-only,建议人工修复)')
                continue
            if entry.get('kind') != '账本变更':
                continue
            text = str(entry.get('text', ''))
            # text 规约:「<文件名> <主题>: <旧|新增>→<新>」;取主题段
            if ' ' not in text or ':' not in text:
                continue
            topic = text.split(' ', 1)[1].split(':', 1)[0].strip()
            if ('待' in topic or '下一步' in topic) and topic not in all_tasks:
                warnings.append(f'[⑤流水] {jp.name}: 主题「{topic}」带待办字样但账本无对应行——流水藏活任务,待办请入模块任务行')
    return warnings


def cmd_check(args: argparse.Namespace) -> int:
    iter_dir = Path(args.iter_dir)
    if not iter_dir.exists():
        print(f'迭代目录不存在:{iter_dir}', file=sys.stderr)
        return 1
    errors: list[str] = []
    warnings: list[str] = []
    all_tasks: dict[str, TaskLine] = {}
    ledgers = iter_ledgers(iter_dir)
    if not ledgers:
        errors.append('未发现任何模块账本(进度.md);先跑 init')
    for p in ledgers:
        errs, warns, tasks = check_ledger(p)
        errors.extend(errs)
        warnings.extend(warns)
        all_tasks.update(tasks)
    warnings.extend(check_journal_orphans(iter_dir, all_tasks))

    for w in warnings:
        print(f'WARNING:{w}')
    for e in errors:
        print(f'ERROR:{e}')
    if errors:
        print(f'check 失败:{len(errors)} 错误 / {len(warnings)} 警告')
        return 1
    if warnings:
        print(f'check 通过(带 {len(warnings)} 条警告)')
        return 0
    print('OK')
    return 0


# ---------- summary ----------


def aggregate_status(children: list[TaskLine]) -> str:
    """聚合规则(§6):满足=已过+不适用;全过=已过;过半=部分过;其余=进行中;
    全部子项为锁定/待激活=锁定(先判,因为全锁定时「过半」判据无意义)。"""
    if not children:
        return '未做'
    if all(c.status in ('锁定', '待激活') for c in children):
        return '锁定'
    satisfied = sum(1 for c in children if c.status in ('已过', '不适用'))
    if satisfied == len(children):
        return '已过'
    if satisfied * 2 > len(children):
        return '部分过'
    return '进行中'


def summarize_file(path: Path) -> tuple[list[TaskLine], dict[str, str]]:
    """解析单账本:返回顶层任务列表与 {父主题: 聚合状态}(有子行的父行才算)。"""
    lines = read_file(path).split('\n')
    tops: list[TaskLine] = []
    child_of: dict[str, list[TaskLine]] = {}
    current: TaskLine | None = None
    for ln in lines:
        task, _ = parse_task_line(ln)
        if task is None:
            continue
        if task.indent:
            if current is not None:
                child_of.setdefault(current.topic, []).append(task)
        else:
            tops.append(task)
            current = task
    parent_agg = {p.topic: aggregate_status(child_of.get(p.topic, [])) for p in tops if child_of.get(p.topic)}
    return tops, parent_agg


def count_status(tasks: list[TaskLine], parent_agg: dict[str, str]) -> dict[str, int]:
    counts = {s: 0 for s in STATUSES}
    for t in tasks:
        counts[t.status] += 1
    return counts


def fmt_counts(counts: dict[str, int]) -> str:
    return ' '.join(f'{s}:{n}' for s, n in counts.items() if n)


def cmd_summary(args: argparse.Namespace) -> int:
    iter_dir = Path(args.iter_dir)
    if not iter_dir.exists():
        print(f'迭代目录不存在:{iter_dir}', file=sys.stderr)
        return 1
    print(f'# 进度汇总 {iter_dir.name}')
    app_agg_inputs: list[TaskLine] = []
    module_aggs: list[str] = []
    # 结构固定两级:<app>/<模块>/进度.md;模块目录直接账本
    for mfile in iter_ledgers(iter_dir):
        app = mfile.parent.parent.name if mfile.parent.parent != iter_dir else ''
        if args.app and app != args.app:
            continue
        tops, parent_agg = summarize_file(mfile)
        if not tops and not parent_agg:
            continue
        counts = count_status(tops, parent_agg)
        mod_agg = aggregate_status(
            [TaskLine('', False, p.topic, parent_agg.get(p.topic, p.status), p.body) for p in tops]
        )
        module_aggs.append(mod_agg)
        label = f'{app}/{mfile.parent.name}' if app else mfile.parent.name
        print(f'\n## {label}(任务 {len(tops)}:{fmt_counts(counts)})')
        if parent_agg:
            print('- 父任务聚合:')
            for topic, st in parent_agg.items():
                print(f'  - {topic} → {st}')
        print(f'- 模块聚合 → {mod_agg}')
        # app 层输入:把模块聚合当作一条伪任务参与同规则聚合
        app_agg_inputs.append(TaskLine('', False, label, mod_agg, ''))
    if app_agg_inputs:
        app_name = args.app or '全部'
        print(f'\n## {app_name} 汇总 → {aggregate_status(app_agg_inputs)}')
    return 0


# ---------- journal ----------


def cmd_journal(args: argparse.Namespace) -> int:
    if args.view:
        if not args.iter_dir:
            print('journal --view 需 <迭代目录> --date YYYYMMDD', file=sys.stderr)
            return 2
        return _journal_view(Path(args.iter_dir), args.date, args.kind)
    iter_dir = Path(args.iter_dir)
    if not iter_dir.exists():
        print(f'迭代目录不存在:{iter_dir}', file=sys.stderr)
        return 1
    journal_append(iter_dir, args.kind, args.text)
    print(f'journal 已记:{iter_dir}/流水-{datetime.now().strftime("%Y%m%d")}.jsonl')
    return 0


def _journal_view(iter_dir: Path, date: str, kind: str | None) -> int:
    if not re.fullmatch(r'\d{8}', date or ''):
        print('--date 需为 YYYYMMDD', file=sys.stderr)
        return 2
    path = iter_dir / f'流水-{date}.jsonl'
    if not path.exists():
        print(f'该日无流水:{path}', file=sys.stderr)
        return 1
    print(f'# 流水 {date}')
    for raw in read_file(path).splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            print(f'- (非法行){raw}')
            continue
        if kind and entry.get('kind') != kind:
            continue
        ts = str(entry.get('ts', ''))
        hms = ts.split('T')[-1] if 'T' in ts else ts
        print(f'- {hms} [{entry.get("kind", "")}] {entry.get("text", "")}')
    return 0


# ---------- CLI ----------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='progress.py', description='进度账本管理工具(规范见 SKILL.md)')
    sub = p.add_subparsers(dest='cmd', required=True)

    sp = sub.add_parser('init', help='生成迭代入口+默认模块(幂等)')
    sp.add_argument('iter_dir')
    sp.add_argument('--goal', required=True)
    sp.add_argument('--criteria', required=True)
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser('write', help='生成/更新一行任务行')
    sp.add_argument('--file', required=True)
    sp.add_argument('--topic', required=True)
    sp.add_argument('--status', required=True)
    sp.add_argument('--ref')
    sp.add_argument('--next')
    sp.add_argument('--pre')
    sp.add_argument('--condition')
    sp.add_argument('--parent')
    sp.add_argument('--note')
    sp.add_argument('--section')
    sp.set_defaults(func=cmd_write)

    sp = sub.add_parser('check', help='六项结构体检')
    sp.add_argument('iter_dir')
    sp.set_defaults(func=cmd_check)

    sp = sub.add_parser('summary', help='机械聚合现算现输出')
    sp.add_argument('iter_dir')
    sp.add_argument('--app')
    sp.set_defaults(func=cmd_summary)

    sp = sub.add_parser('journal', help='流水 append / 渲染')
    sp.add_argument('iter_dir', nargs='?')
    sp.add_argument('--kind')
    sp.add_argument('--text')
    sp.add_argument('--view', action='store_true')
    sp.add_argument('--date')
    sp.set_defaults(func=cmd_journal)
    return p


def force_utf8_stdio() -> None:
    """中文 Windows 控制台默认 GBK 代码页,①⑥ 等字符直接 UnicodeEncodeError 崩溃。

    目标环境就是中文 Windows(必现主路径),故入口强制 UTF-8 输出、不可编码字符降级为
    ? 而非崩溃;不要求用户设置 PYTHONIOENCODING。pytest 等场景 stdout 可能被替换为
    非 TextIOWrapper 对象(无 reconfigure),此时跳过。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if reconfigure is not None:
            try:
                reconfigure(encoding='utf-8', errors='replace')
            except (ValueError, OSError):
                # 已有读缓冲等少数场景不可重配;降级为不处理(不因体验修正引崩溃)
                pass


REMINDER_LINE = '[提醒] 进度维护必须按 od-dev-progress-tracking 规范运行,未阅读的请重新阅读规范再继续'


def main(argv: list[str]) -> int:
    force_utf8_stdio()
    args = build_parser().parse_args(argv)
    if args.cmd == 'journal' and not args.view:
        if not args.iter_dir or not args.kind or args.text is None:
            print('journal 记录模式需 <迭代目录> --kind --text', file=sys.stderr)
            print(REMINDER_LINE)
            return 2
        if len(args.text) > MAX_JOURNAL_TEXT:
            print(f'text 超长({len(args.text)} > {MAX_JOURNAL_TEXT})', file=sys.stderr)
            print(REMINDER_LINE)
            return 2
    code = int(args.func(args))
    # 每条命令输出末尾都带规范提醒:进度脚本的使用者可能只背了命令没读规范,
    # 提醒随操作结果出现 = 阅读时机前移到最容易漏的时刻
    print(REMINDER_LINE)
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
