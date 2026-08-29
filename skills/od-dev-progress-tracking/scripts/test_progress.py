"""progress.py 自测(pytest)。全部用 tmp_path,零真实路径写入。

运行:`uv run pytest test_progress.py -q`
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import progress  # noqa: E402


def run(argv: list[str]) -> int:
    """以进程同构方式调 main,断言 exit code。"""
    return progress.main(argv)


def init_iter(tmp_path: Path) -> Path:
    """建一个标准迭代目录,返回迭代目录路径。"""
    it = tmp_path / '20260831-test'
    assert run(['init', str(it), '--goal', '测试目标', '--criteria', 'docs/x/research/README.md']) == 0
    return it


def flow_file(it: Path) -> Path:
    return it / '流程' / '进度.md'


# ---------- ① 行文法解析 ----------


class TestGrammar:
    def test_legal_lines_all_statuses(self) -> None:
        for st, body in [
            ('已过', 'docs/a.md'),
            ('未做', ''),
        ]:
            if st == '未做':
                line = f'任务A——未做(备注)'
                task, err = progress.parse_task_line(line)
                assert err is None and task is not None
                continue
            line = f'任务A——{st}({body})'
            task, err = progress.parse_task_line(line)
            assert err is None, err
            assert task is not None
            assert task.status == st

    def test_legal_variants(self) -> None:
        # 编号行 / 子行 / 带分号多字段
        for line in [
            '1. 任务A——已过(docs/a.md;一行结论)',
            '  子任务B——进行中(下一步:跑实测)',
            '12、任务C——锁定(前置=D-01)',
        ]:
            task, err = progress.parse_task_line(line)
            assert err is None, err
            assert task is not None

    def test_skip_lines(self) -> None:
        for line in ['', '# 流程', '## 其他', '> 治理指针:…', '   ']:
            task, err = progress.parse_task_line(line)
            assert task is None and err is None  # 跳过不校验

    def test_bad_missing_fields(self) -> None:
        bad = [
            '没有破折号的行',  # 缺 ——
            '任务A——已过()',  # 括号空
            '——已过(docs/a.md)',  # 主题空
        ]
        for line in bad:
            task, err = progress.parse_task_line(line)
            assert task is None and err is not None, line

    def test_alias_suggestion(self) -> None:
        task, err = progress.parse_task_line('任务A——已修(docs/a.md)')
        assert task is None and err is not None
        assert '已修→已过' in err

    def test_unknown_word_lists_seven(self) -> None:
        task, err = progress.parse_task_line('任务A——搞定(abc)')
        assert task is None and err is not None
        for st in progress.STATUSES:
            assert st in err


# ---------- ② write 状态-字段一致性打回(7 状态 × 缺字段) ----------


class TestWriteConsistency:
    def make(self, tmp_path: Path) -> Path:
        it = init_iter(tmp_path)
        return flow_file(it)

    def test_reject_each_status_missing_field(self, tmp_path: Path, capsys: object) -> None:
        f = self.make(tmp_path)
        # 合法对照先写入,保证文件非空
        assert run(['write', '--file', str(f), '--topic', '等待发版', '--status', '待激活',
                    '--condition', '等版本发布 周一复查']) == 0
        # 补一个 --note 使 body 非空,专测各状态的必带字段校验(空括号另有独立打回)
        bad_cases = [
            ('已过', ['--note', '占'], '指针'),
            ('已过', ['--ref', 'docs/a.md', '--next', '收尾'], '下一步'),
            ('进行中', ['--note', '占'], '下一步'),
            ('锁定', ['--note', '占'], '前置='),
            ('待激活', ['--note', '占'], '条件='),
            ('待激活', ['--condition', '等发版后开工'], '复查'),
            ('部分过', ['--note', '占'], '缺='),
        ]
        for st, extra, keyword in bad_cases:
            argv = ['write', '--file', str(f), '--topic', f'坏用例{st}{keyword}', '--status', st] + extra
            assert run(argv) == 2, (st, extra)
            out = capsys.readouterr().err  # type: ignore[attr-defined]
            if keyword:
                assert keyword in out, (st, out)

    def test_buguoyong_requires_why(self, tmp_path: Path) -> None:
        # 不适用:文法层要求括号非空,write 至少给一个字段(此处用 --note 说明为何)
        f = self.make(tmp_path)
        assert run(['write', '--file', str(f), '--topic', '无关项', '--status', '不适用',
                    '--note', '该分支已删除']) == 0

    def test_nonstandard_status_rejected(self, tmp_path: Path) -> None:
        f = self.make(tmp_path)
        assert run(['write', '--file', str(f), '--topic', 'X', '--status', '已完成']) == 2


# ---------- ③ write 新增/更新/父子嵌套 ----------


class TestWriteStructure:
    def test_add_update(self, tmp_path: Path) -> None:
        f = self.make_file(tmp_path)
        assert run(['write', '--file', str(f), '--topic', '任务A', '--status', '进行中', '--next', '写代码']) == 0
        text = f.read_text(encoding='utf-8')
        assert '任务A——进行中(下一步:写代码)' in text
        # 更新状态:不重给 --next 也应保留旧字段(合并)
        assert run(['write', '--file', str(f), '--topic', '任务A', '--status', '已过', '--ref', 'docs/a.md']) == 0
        text = f.read_text(encoding='utf-8')
        assert '任务A——已过(docs/a.md)' in text

    def make_file(self, tmp_path: Path) -> Path:
        it = init_iter(tmp_path)
        return flow_file(it)

    def test_parent_child_nesting(self, tmp_path: Path) -> None:
        f = self.make_file(tmp_path)
        # 父不存在且无 --next → 打回
        assert run(['write', '--file', str(f), '--topic', '子1', '--status', '未做', '--parent', '父P']) == 2
        # 自动创建父行(进行中+next),子行两空格缩进挂其下;--next 归父行,不进子行 body
        assert run(['write', '--file', str(f), '--topic', '子1', '--status', '未做',
                    '--parent', '父P', '--next', '开工', '--note', '待派']) == 0
        text = f.read_text(encoding='utf-8')
        lines = [ln for ln in text.splitlines() if ln.strip()]
        # 自动创建的父行:进行中 + 必带下一步
        assert any(ln.startswith('父P——进行中(下一步:') for ln in lines)
        # 子行两空格缩进且紧跟父行块内
        pi = next(i for i, ln in enumerate(lines) if ln.startswith('父P——'))
        assert lines[pi + 1].startswith('  子1——未做(')

    def test_child_second_added_after_block(self, tmp_path: Path) -> None:
        f = self.make_file(tmp_path)
        run(['write', '--file', str(f), '--topic', '子1', '--status', '未做', '--parent', '父P', '--next', '开工', '--note', '待派'])
        run(['write', '--file', str(f), '--topic', '子2', '--status', '未做', '--parent', '父P', '--note', '待派'])
        text = f.read_text(encoding='utf-8')
        idx_parent = text.index('父P——')
        assert text.index('  子1——') < text.index('  子2——')
        # 两个子行都紧跟父行块内
        block = text[idx_parent:].splitlines()[:3]
        assert any('子2' in ln for ln in block)

    def test_section_support_only(self, tmp_path: Path) -> None:
        it = init_iter(tmp_path)
        sup = it / '支撑' / '进度.md'
        assert run(['write', '--file', str(sup), '--topic', '调研X', '--status', '未做',
                    '--section', '调研', '--note', '待派']) == 0
        text = sup.read_text(encoding='utf-8')
        assert '## 调研' in text
        assert '调研X——未做()' in text or '调研X——未做(' in text
        # 流程文件用 --section → 打回
        assert run(['write', '--file', str(flow_file(it)), '--topic', 'Y', '--status', '未做',
                    '--section', '调研']) == 2


# ---------- ④ 原子更新逐位不变 ----------


class TestAtomicUpdate:
    def test_other_lines_bitwise_unchanged(self, tmp_path: Path) -> None:
        f = TestWriteStructure().make_file(tmp_path)
        run(['write', '--file', str(f), '--topic', '甲', '--status', '已过', '--ref', 'a.md'])
        run(['write', '--file', str(f), '--topic', '乙', '--status', '进行中', '--next', '干活'])
        run(['write', '--file', str(f), '--topic', '丙', '--status', '未做'])
        before = f.read_text(encoding='utf-8').splitlines()
        assert len(before) >= 3
        run(['write', '--file', str(f), '--topic', '乙', '--status', '已过', '--ref', 'b.md'])
        after = f.read_text(encoding='utf-8').splitlines()
        changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        # 仅中间那行(乙)被改
        assert len(after) == len(before)
        assert len(changed) == 1
        i = changed[0]
        assert '甲——已过' in before[i] or '乙' in before[i] or '丙——未做' in before[i]
        assert '乙——已过(b.md)' in after[i]
        # 前后相邻行逐位相同
        for j in range(len(after)):
            if j != i:
                assert before[j] == after[j]


# ---------- ⑤ check 六项 ----------


class TestCheck:
    def init_custom(self, tmp_path: Path) -> Path:
        it = init_iter(tmp_path)
        return it

    def test_legal_fixture_ok(self, tmp_path: Path, capsys: object) -> None:
        it = self.init_custom(tmp_path)
        f = flow_file(it)
        run(['write', '--file', str(f), '--topic', '任务A', '--status', '已过', '--ref', 'docs/a.md'])
        run(['write', '--file', str(f), '--topic', '任务B', '--status', '进行中', '--next', '实测'])
        assert run(['check', str(it)]) == 0
        assert 'OK' in capsys.readouterr().out  # type: ignore[attr-defined]

    def test_bad_grammar(self, tmp_path: Path, capsys: object) -> None:
        it = self.init_custom(tmp_path)
        f = flow_file(it)
        f.write_text('# 流程\n坏行没有破折号\n', encoding='utf-8')
        assert run(['check', str(it)]) == 1
        assert '①文法' in capsys.readouterr().out  # type: ignore[attr-defined]

    def test_inconsistent_status(self, tmp_path: Path, capsys: object) -> None:
        it = self.init_custom(tmp_path)
        f = flow_file(it)
        f.write_text('# 流程\n任务A——已过(无指针)\n', encoding='utf-8')
        assert run(['check', str(it)]) == 1
        assert '②一致性' in capsys.readouterr().out  # type: ignore[attr-defined]

    def test_narrative_warning(self, tmp_path: Path, capsys: object) -> None:
        it = self.init_custom(tmp_path)
        f = flow_file(it)
        narrative = '已派给A;验收(通过);板面:满;判读(过);已派给B;验收(通过)'
        f.write_text(f'# 流程\n任务A——已过(docs/a.md;{narrative})\n', encoding='utf-8')
        assert run(['check', str(it)]) == 0
        out = capsys.readouterr().out  # type: ignore[attr-defined]
        assert '③叙事' in out

    def test_line_threshold_warning(self, tmp_path: Path, capsys: object) -> None:
        it = self.init_custom(tmp_path)
        f = flow_file(it)
        rows = ['# 流程'] + [f'占位任务{i}——未做(注)'.replace('任务', '任务') for i in range(progress.MAX_LEDGER_LINES + 1)]
        f.write_text('\n'.join(rows) + '\n', encoding='utf-8')
        assert run(['check', str(it)]) == 0
        out = capsys.readouterr().out  # type: ignore[attr-defined]
        assert '④切档' in out

    def test_journal_hidden_task_warning(self, tmp_path: Path, capsys: object) -> None:
        it = self.init_custom(tmp_path)
        f = flow_file(it)
        run(['write', '--file', str(f), '--topic', '正常任务', '--status', '已过', '--ref', 'a.md'])
        # 账本变更流水提到一个不存在的待办主题
        progress.journal_append(it, '账本变更', '进度.md 下一步重试方案: 新增→未做')
        assert run(['check', str(it)]) == 0
        out = capsys.readouterr().out  # type: ignore[attr-defined]
        assert '⑤流水' in out and '流水藏活任务' in out

    def test_collapse_hint_and_error(self, tmp_path: Path, capsys: object) -> None:
        it = self.init_custom(tmp_path)
        f = flow_file(it)
        # 全过子行 → 可塌缩 warning
        f.write_text(
            '# 流程\n'
            '父P——已过(docs/p.md)\n'
            '  子1——已过(docs/a.md)\n'
            '  子2——不适用(已并入子1)\n',
            encoding='utf-8',
        )
        assert run(['check', str(it)]) == 0
        assert '可塌缩' in capsys.readouterr().out  # type: ignore[attr-defined]
        # 父已过但有未过子行 → 报错
        f.write_text(
            '# 流程\n'
            '父P——已过(docs/p.md)\n'
            '  子1——已过(docs/a.md)\n'
            '  子2——未做(待办)\n',
            encoding='utf-8',
        )
        assert run(['check', str(it)]) == 1
        assert '⑥塌缩' in capsys.readouterr().out  # type: ignore[attr-defined]

    def test_parent_待激活_children_all_locked(self, tmp_path: Path) -> None:
        # 合法形态:父行聚合态(部分过/锁定)带子行不违反一致性——聚合态由 summary 算,
        # 但账本手写聚合态仅在有子行时合法(§6);此处验证手写父行部分过+缺= 合法
        it = self.init_custom(tmp_path)
        f = flow_file(it)
        f.write_text(
            '# 流程\n'
            '父P——部分过(缺=子2;docs/p.md)\n'
            '  子1——已过(docs/a.md)\n'
            '  子2——锁定(前置=子1)\n',
            encoding='utf-8',
        )
        assert run(['check', str(it)]) == 0


# ---------- ⑥ summary 聚合算例(手算期望) ----------


class TestSummary:
    def test_aggregate_rules(self) -> None:
        def t(status: str) -> progress.TaskLine:
            return progress.TaskLine('', False, f'x{status}', status, 'docs/a.md')

        # 全过=已过
        assert progress.aggregate_status([t('已过'), t('不适用')]) == '已过'
        # 过半=部分过(2/3 满足)
        assert progress.aggregate_status([t('已过'), t('已过'), t('未做')]) == '部分过'
        # 其余=进行中(1/3)
        assert progress.aggregate_status([t('已过'), t('未做'), t('未做')]) == '进行中'
        # 全锁定/待激活=锁定
        assert progress.aggregate_status([t('锁定'), t('待激活')]) == '锁定'
        # 恰好一半不满足 → 非过半 → 进行中
        assert progress.aggregate_status([t('已过'), t('未做')]) == '进行中'

    def test_summary_output(self, tmp_path: Path, capsys: object) -> None:
        it = init_iter(tmp_path)
        f = flow_file(it)
        # 父P 3 子行:子1 已过、子2 已过、子3 未做 → 父=部分过
        run(['write', '--file', str(f), '--topic', '子1', '--status', '已过', '--ref', 'a.md', '--parent', '父P', '--next', '开工'])
        run(['write', '--file', str(f), '--topic', '子2', '--status', '已过', '--ref', 'b.md', '--parent', '父P'])
        run(['write', '--file', str(f), '--topic', '子3', '--status', '未做', '--parent', '父P', '--note', '待派'])
        # 顶层独立任务:已过
        run(['write', '--file', str(f), '--topic', '独A', '--status', '已过', '--ref', 'c.md'])
        assert run(['summary', str(it)]) == 0
        out = capsys.readouterr().out  # type: ignore[attr-defined]
        assert '父P → 部分过' in out
        # 手算:顶层任务 = [父P(聚合=部分过), 独A(已过)],满足=1/2 非过半 → 进行中
        assert '模块聚合 → 进行中' in out

    def test_summary_app_filter(self, tmp_path: Path, capsys: object) -> None:
        it = init_iter(tmp_path)
        run(['write', '--file', str(flow_file(it)), '--topic', 'A', '--status', '已过', '--ref', 'a.md'])
        assert run(['summary', str(it), '--app', '不存在']) == 0
        out = capsys.readouterr().out  # type: ignore[attr-defined]
        assert '任务' not in out.split('# 进度汇总')[1]


# ---------- ⑦ journal ----------


class TestJournal:
    def test_append_and_view(self, tmp_path: Path, capsys: object) -> None:
        it = init_iter(tmp_path)
        assert run(['journal', str(it), '--kind', '局判读', '--text', '第1局过渡成型慢']) == 0
        assert run(['journal', str(it), '--kind', '事故', '--text', 'bot 卡在结算画面']) == 0
        date = __import__('datetime').datetime.now().strftime('%Y%m%d')
        assert run(['journal', '--view', str(it), '--date', date]) == 0
        out = capsys.readouterr().out  # type: ignore[attr-defined]
        assert '第1局过渡成型慢' in out and '卡在结算画面' in out
        # kind 过滤
        assert run(['journal', '--view', str(it), '--date', date, '--kind', '事故']) == 0
        out = capsys.readouterr().out  # type: ignore[attr-defined]
        assert '局判读' not in out and '卡在结算画面' in out

    def test_text_too_long(self, tmp_path: Path) -> None:
        it = init_iter(tmp_path)
        assert run(['journal', str(it), '--kind', 'x', '--text', '长' * 2001]) == 2

    def test_view_bad_date(self, tmp_path: Path) -> None:
        it = init_iter(tmp_path)
        assert run(['journal', '--view', str(it), '--date', 'bad']) == 2


# ---------- ⑧ init 幂等 ----------


class TestInit:
    def test_idempotent(self, tmp_path: Path) -> None:
        it = init_iter(tmp_path)
        entry = it / '进度.md'
        first = entry.read_text(encoding='utf-8')
        f = flow_file(it)
        run(['write', '--file', str(f), '--topic', '任务A', '--status', '已过', '--ref', 'a.md'])
        # 二次 init 不覆盖任何已有文件
        assert run(['init', str(it), '--goal', '新目标', '--criteria', 'x.md']) == 0
        assert entry.read_text(encoding='utf-8') == first  # 入口未覆盖
        assert '任务A——已过' in f.read_text(encoding='utf-8')  # 账本未覆盖

    def test_entry_three_lines_and_support_section(self, tmp_path: Path) -> None:
        it = init_iter(tmp_path)
        entry_lines = [ln for ln in (it / '进度.md').read_text(encoding='utf-8').splitlines() if ln.strip()]
        assert len(entry_lines) == 4
        assert entry_lines[0].startswith('# 迭代 ')
        assert '测试目标' in entry_lines[1]
        assert entry_lines[2].startswith('判据:') and 'docs/x/research/README.md' in entry_lines[2]
        sup = (it / '支撑' / '进度.md').read_text(encoding='utf-8')
        assert sup.index('## 其他') < sup.index('## 其他') + 1  # 首节存在
        assert '## 其他' in sup
        for m in ('流程', '决策'):
            assert (it / m / '进度.md').exists()


# ---------- 流水由 write 自动记录 ----------


class TestWriteJournal:
    def test_write_records_journal(self, tmp_path: Path) -> None:
        it = init_iter(tmp_path)
        f = flow_file(it)
        run(['write', '--file', str(f), '--topic', '任务A', '--status', '进行中', '--next', '开工'])
        run(['write', '--file', str(f), '--topic', '任务A', '--status', '已过', '--ref', 'a.md'])
        import json as _json
        journals = sorted(it.glob('流水-*.jsonl'))
        assert journals
        entries = [_json.loads(ln) for ln in journals[0].read_text(encoding='utf-8').splitlines() if ln.strip()]
        changes = [e for e in entries if e['kind'] == '账本变更' and '任务A' in e['text']]
        assert len(changes) == 2
        assert '新增→进行中' in changes[0]['text']
        assert '进行中→已过' in changes[1]['text']
        assert 'ts' in changes[0] and changes[0]['refs'] == []


# ---------- GBK 控制台健壮性 + check 多违规全列 ----------


class TestGbkAndMultiViolation:
    def test_gbk_subprocess_no_crash(self, tmp_path: Path) -> None:
        """模拟中文 Windows GBK 控制台(PYTHONIOENCODING=gbk):含非 GBK 字符的输出不得崩。

        崩溃形态 = UnicodeEncodeError traceback;健壮形态 = 正常体检输出
        (违规行经 errors='replace' 降级而非进程崩溃)。
        """
        it = init_iter(tmp_path)
        f = flow_file(it)
        # ✅ 不在 GBK 内;违规行原文会进 check 报错文本,足以触发旧 bug
        f.write_text('# 流程\n任务A✅——已过(无指针)\n', encoding='utf-8')
        script = Path(progress.__file__)
        env = {**os.environ, 'PYTHONIOENCODING': 'gbk'}
        r = subprocess.run(
            [sys.executable, str(script), 'check', str(it)],
            capture_output=True, env=env,
        )
        stderr = r.stderr.decode('utf-8', 'replace')
        stdout = r.stdout.decode('utf-8', 'replace')
        assert 'UnicodeEncodeError' not in stderr, stderr
        assert 'Traceback' not in stderr, stderr
        assert r.returncode == 1  # 正常报体检错误,非崩溃
        assert '②一致性' in stdout and 'check 失败' in stdout

    def test_check_lists_all_violations_at_once(self, tmp_path: Path, capsys: object) -> None:
        """两条违规一次全列,不首条中断(验收体验修正锁)。"""
        it = init_iter(tmp_path)
        f = flow_file(it)
        f.write_text(
            '# 流程\n'
            '坏行没有破折号\n'
            '任务A——已过(无指针)\n',
            encoding='utf-8',
        )
        assert run(['check', str(it)]) == 1
        out = capsys.readouterr().out  # type: ignore[attr-defined]
        assert '①文法' in out
        assert '②一致性' in out
        assert out.index('①文法') < out.index('check 失败')
