"""dag.py 自测(pytest)。全部用 tmp_path,零真实路径写入。

运行:`pytest test_dag.py -q`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import dag  # noqa: E402


def run(argv: list[str]) -> int:
    """与 progress 测试同构:直接调 main 断言 exit code。"""
    return dag.main(argv)


def f(tmp_path: Path) -> str:
    return str(tmp_path / 'dag.jsonl')


def seed(tmp_path: Path) -> str:
    """T-1(自由任务)已过;返回文件路径。"""
    path = f(tmp_path)
    # 直达 done 只对免审任务开放:seed 走直达,建账即声明 --review none
    assert run(['--file', path, 'add', '根任务', '--module', '流程', '--review', 'none']) == 0
    assert run(['--file', path, 'status', 'T-1', 'done', '--criteria', 'a.md']) == 0
    return path


# ---------- add ----------


class TestAdd:
    def test_basic_and_id_increment(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', '任务一', '--module', '流程']) == 0
        assert run(['--file', path, 'add', '任务二', '--module', '决策', '--dep', 'T-1']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems
        assert set(tasks) == {'T-1', 'T-2'}
        assert tasks['T-2'].deps == ['T-1']
        assert tasks['T-2'].status == 'todo'

    def test_module_enum_enforced(self, tmp_path: Path) -> None:
        assert run(['--file', f(tmp_path), 'add', 'x', '--module', '乱填']) == 2

    def test_dangling_dep_rejected(self, tmp_path: Path) -> None:
        assert run(['--file', f(tmp_path), 'add', 'x', '--module', '流程', '--dep', 'T-9']) == 2

    def test_add_with_cond_starts_wait(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程',
                    '--cond', '等语料,复查=汇报时']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert tasks['T-1'].status == 'wait'

    def test_cond_without_review_rejected(self, tmp_path: Path) -> None:
        assert run(['--file', f(tmp_path), 'add', 'x', '--module', '流程',
                    '--cond', '等语料到位后再启动']) == 2


# ---------- 流转矩阵 ----------


class TestTransitions:
    def test_legal_paths(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        # todo→doing→wait→todo→done 全链(直达链只对免审任务开放)
        assert run(['--file', path, 'add', 'x', '--module', '流程', '--review', 'none']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'self']) == 0
        assert run(['--file', path, 'status', 'T-1', 'wait',
                    '--cond', '等裁决,复查=明天']) == 0
        assert run(['--file', path, 'status', 'T-1', 'todo']) == 0
        assert run(['--file', path, 'status', 'T-1', 'done', '--criteria', 'a.md']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'done'

    def test_illegal_transitions(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程']) == 0
        # todo→wait 非法(wait 只能来自 doing 或 add)
        assert run(['--file', path, 'status', 'T-1', 'wait', '--cond', '等,复查=1']) == 2
        assert run(['--file', path, 'status', 'T-1', 'dead', '--why', '砍']) == 0
        # dead 终态:无出边
        assert run(['--file', path, 'status', 'T-1', 'todo']) == 2
        assert run(['--file', path, 'status', 'T-1', 'done', '--criteria', 'a.md']) == 2

    def test_required_fields(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        # 免审任务:done 缺 criteria 的必带校验只对直达边有意义(required 被直达门先拦)
        assert run(['--file', path, 'add', 'x', '--module', '流程', '--review', 'none']) == 0
        # doing 缺 assignee
        assert run(['--file', path, 'status', 'T-1', 'doing']) == 2
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        # done 缺 criteria
        assert run(['--file', path, 'status', 'T-1', 'done']) == 2
        # dead 缺 why
        assert run(['--file', path, 'status', 'T-1', 'dead']) == 2

    def test_done_revert_requires_why(self, tmp_path: Path) -> None:
        path = seed(tmp_path)
        assert run(['--file', path, 'status', 'T-1', 'todo']) == 2
        assert run(['--file', path, 'status', 'T-1', 'todo', '--why', '判据判错了']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'todo'


# ---------- 图运算 ----------


class TestGraph:
    def test_ready_and_dead_satisfies(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'a', '--module', '流程']) == 0
        assert run(['--file', path, 'add', 'b', '--module', '流程', '--dep', 'T-1']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert dag.ready_set(tasks) == ['T-1']  # T-2 被挡
        assert run(['--file', path, 'status', 'T-1', 'dead', '--why', '被取代']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert dag.ready_set(tasks) == ['T-2']  # dead 算满足,下游解锁

    def test_revert_blocks_downstream(self, tmp_path: Path) -> None:
        path = seed(tmp_path)
        assert run(['--file', path, 'add', '下游', '--module', '流程', '--dep', 'T-1']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert dag.ready_set(tasks) == ['T-2']
        assert run(['--file', path, 'status', 'T-1', 'todo', '--why', '返工']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        # 下游 T-2 自动回被挡;T-1 自己回到就绪(要重做)
        assert dag.ready_set(tasks) == ['T-1']
        assert dag.blocked_by(tasks, tasks['T-2']) == ['T-1']

    def test_cycle_rejected_on_dep_add(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'a', '--module', '流程']) == 0
        assert run(['--file', path, 'add', 'b', '--module', '流程', '--dep', 'T-1']) == 0
        assert run(['--file', path, 'add', 'c', '--module', '流程', '--dep', 'T-2']) == 0
        # T-1 加依赖 T-3 成环 T-1→T-3→T-2→T-1
        assert run(['--file', path, 'dep', 'T-1', '--add', 'T-3']) == 2
        assert run(['--file', path, 'dep', 'T-1', '--add', 'T-9']) == 2  # 悬空
        assert run(['--file', path, 'dep', 'T-1', '--add', 'T-1']) == 2  # 自依赖
        assert run(['--file', path, 'dep', 'T-2', '--del', 'T-9']) == 2  # 删不存在的边
        assert run(['--file', path, 'dep', 'T-2', '--del', 'T-1']) == 0  # 合法删
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems
        assert 'T-1' not in tasks['T-2'].deps

    def test_criteria_append_not_overwrite(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程',
                    '--criteria', '预注册判据', '--review', 'none']) == 0
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'report.md 实测过']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert tasks['T-1'].criteria == ['预注册判据', 'report.md 实测过']


# ---------- note / 视图 / check ----------


class TestViewsAndCheck:
    def test_note_appends(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程']) == 0
        assert run(['--file', path, 'note', 'T-1', '补充证据指针']) == 0
        assert run(['--file', path, 'note', 'T-1', '']) == 2
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert len(tasks['T-1'].notes) == 1

    def test_views_smoke(self, tmp_path: Path, capsys: object) -> None:
        path = seed(tmp_path)
        assert run(['--file', path, 'add', '下', '--module', '决策', '--dep', 'T-1']) == 0
        for cmd in (['ready'], ['list', '--all'], ['graph'], ['graph', '--mermaid'],
                    ['card', 'T-2'], ['who', 'T-1'], ['log', 'T-1'], ['check']):
            assert run(['--file', path, *cmd]) == 0, cmd

    def test_check_catches_manual_corruption(self, tmp_path: Path) -> None:
        path = seed(tmp_path)
        assert run(['--file', path, 'check']) == 0
        # 模拟直改坏档:把 done 行的凭据抹掉
        p = Path(path)
        raw = p.read_text(encoding='utf-8').replace('"criteria": ["a.md"]', '"criteria": []')
        p.write_text(raw, encoding='utf-8')
        assert run(['--file', path, 'check']) == 1

    def test_check_warns_cond_id_leak(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        # 用 wait 初始登记,cond 里写任务 ID 文字 = 该建 deps 边
        assert run(['--file', path, 'add', 'x', '--module', '流程',
                    '--cond', '等 T-1 完成,复查=明天']) == 0
        assert run(['--file', path, 'check']) == 0  # 告警不挡通过
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run(['--file', path, 'check'])
        assert '该建 deps 边' in buf.getvalue()

    def test_bad_json_line_survives_read(self, tmp_path: Path) -> None:
        path = Path(seed(tmp_path))
        with open(path, 'a', encoding='utf-8') as fh:
            fh.write('{坏行\n')
        tasks, _ = dag.fold(dag.load_events(path))
        assert len(tasks) == 1  # 坏行跳过不炸


# ---------- pending_review 态(交付-验收-打回,含文件存在门) ----------


class TestPendingReviewFlow:
    def seed_doing(self, tmp_path: Path) -> str:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        return path

    def touch(self, tmp_path: Path, rel: str) -> None:
        """在账本目录下创建真实报告/结论文件(文件存在门要求指针指向真文件)。"""
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('x', encoding='utf-8')

    def test_deliver_requires_criteria(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        assert run(['--file', path, 'status', 'T-1', 'pending_review']) == 2
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'pending_review'
        assert tasks['T-1'].criteria == ['reports/T-1-r1.md']
        assert tasks['T-1'].assignee == 'w1'  # 交付者保留,打回派返工的线索

    def test_deliver_requires_real_file(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        # 文件存在门:指针指向的文件不存在=交付登记打回
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 2
        # 非 path 类凭据(纯文字)同样过不了门:交付必须有真实文件
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', '报告已写完']) == 2
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0

    def test_accept_requires_verdict_criteria(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        # 交付报告已在凭据,验收过仍必带新凭据(验收结论指针),不许拿交付报告顶
        assert run(['--file', path, 'status', 'T-1', 'done']) == 2
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reviews/T-1-r1.md']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'done'
        assert tasks['T-1'].criteria == ['reports/T-1-r1.md', 'reviews/T-1-r1.md']

    def test_accept_requires_real_verdict_file(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        # 无 reviews/ 结论文件不得置 done(文件存在门)
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reviews/T-1-r1.md']) == 2
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reviews/T-1-r1.md']) == 0

    def test_reject_requires_why_and_assignee(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing']) == 2  # doing 必带 assignee
        assert run(['--file', path, 'status', 'T-1', 'doing',
                    '--assignee', 'w2']) == 2  # 打回必带 why
        # why 引用的结论文件不存在=打回无效
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w2',
                    '--why', '复现失败,详见 reviews/T-1-r1.md']) == 2
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w2',
                    '--why', '复现失败,详见 reviews/T-1-r1.md']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'doing'

    def test_full_rework_chain_keeps_all_criteria(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1',
                    '--why', '打回,详见 reviews/T-1-r1.md']) == 0
        self.touch(tmp_path, 'reports/T-1-r2.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r2.md']) == 0
        self.touch(tmp_path, 'reviews/T-1-r2.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reviews/T-1-r2.md']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems
        # 追加不覆盖:两轮交付报告+最终验收结论共存,整条链可溯
        assert tasks['T-1'].criteria == ['reports/T-1-r1.md', 'reports/T-1-r2.md',
                                         'reviews/T-1-r2.md']

    def test_pending_review_to_dead_needs_why(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        assert run(['--file', path, 'status', 'T-1', 'dead']) == 2
        assert run(['--file', path, 'status', 'T-1', 'dead', '--why', '验收前被砍']) == 0

    def test_pending_review_only_reachable_from_doing(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程', '--review', 'none']) == 0
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'r.md']) == 2  # todo→pending_review 非法(矩阵先拒)
        assert run(['--file', path, 'status', 'T-1', 'done', '--criteria', 'a.md']) == 0
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'r.md']) == 2  # done→pending_review 非法

    def test_log_timeline_and_counts(self, tmp_path: Path) -> None:
        import contextlib
        import io
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1',
                    '--why', '打回,详见 reviews/T-1-r1.md']) == 0
        self.touch(tmp_path, 'reports/T-1-r2.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r2.md']) == 0
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert run(['--file', path, 'log', 'T-1']) == 0
        out = buf.getvalue()
        assert '交付 2 次' in out and '打回 1 次' in out
        assert 'todo -> doing' in out
        assert 'pending_review -> done' not in out  # 本链未验收过

    def test_check_catches_pending_review_without_criteria(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        # 模拟直改坏档:抹掉 pending_review 事件的交付凭据
        p = Path(path)
        raw = p.read_text(encoding='utf-8').replace(
            '"criteria": ["reports/T-1-r1.md"]', '"criteria": []')
        p.write_text(raw, encoding='utf-8')
        assert run(['--file', path, 'check']) == 1

    def test_check_catches_missing_pending_review_file(self, tmp_path: Path) -> None:
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        # 模拟报告文件事后被删:check 重放应抓到 pending_review 凭据指向不存在的文件
        (tmp_path / 'reports' / 'T-1-r1.md').unlink()
        assert run(['--file', path, 'check']) == 1


# ---------- review 验收档(建账定档,缺省 required,直达门) ----------


class TestReviewGate:
    def touch(self, tmp_path: Path, rel: str) -> None:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('x', encoding='utf-8')

    def test_default_required_and_opt_out_none(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', '甲', '--module', '流程']) == 0
        assert run(['--file', path, 'add', '乙', '--module', '流程', '--review', 'none']) == 0
        assert run(['--file', path, 'add', '丙', '--module', '流程', '--review', '乱填']) == 2
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems
        assert tasks['T-1'].review == 'required'  # 缺省从严
        assert tasks['T-2'].review == 'none'

    def test_required_blocks_direct_done(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程']) == 0  # 缺省 required
        # todo→done 打回
        assert run(['--file', path, 'status', 'T-1', 'done', '--criteria', 'a.md']) == 2
        # doing→done 打回
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        assert run(['--file', path, 'status', 'T-1', 'done', '--criteria', 'a.md']) == 2
        # wait→done 打回
        assert run(['--file', path, 'add', 'y', '--module', '流程',
                    '--cond', '等语料,复查=明天']) == 0
        assert run(['--file', path, 'status', 'T-2', 'done', '--criteria', 'a.md']) == 2

    def test_required_done_via_pending_review_still_works(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reviews/T-1-r1.md']) == 0

    def test_none_allows_direct_done_and_keeps_escalation(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        # 直达:doing→done 凭据可以是 commit 等非文件指针(直达边不受文件存在门约束)
        assert run(['--file', path, 'add', 'x', '--module', '流程', '--review', 'none']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'self']) == 0
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'commit abc123 自测过']) == 0
        # 补记:todo→done
        assert run(['--file', path, 'add', 'y', '--module', '流程', '--review', 'none']) == 0
        assert run(['--file', path, 'status', 'T-2', 'done', '--criteria', 'a.md']) == 0
        # 升级口:免审任务照样可走全协议(交付时发现改动变大/判据说不清)
        assert run(['--file', path, 'add', 'z', '--module', '流程', '--review', 'none']) == 0
        assert run(['--file', path, 'status', 'T-3', 'doing', '--assignee', 'w1']) == 0
        self.touch(tmp_path, 'reports/T-3-r1.md')
        assert run(['--file', path, 'status', 'T-3', 'pending_review',
                    '--criteria', 'reports/T-3-r1.md']) == 0
        self.touch(tmp_path, 'reviews/T-3-r1.md')
        assert run(['--file', path, 'status', 'T-3', 'done',
                    '--criteria', 'reviews/T-3-r1.md']) == 0

    def test_views_show_review_level(self, tmp_path: Path) -> None:
        import contextlib
        import io
        path = f(tmp_path)
        assert run(['--file', path, 'add', '甲', '--module', '流程', '--review', 'none']) == 0
        assert run(['--file', path, 'add', '乙', '--module', '流程']) == 0
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert run(['--file', path, 'card', 'T-1']) == 0
            assert run(['--file', path, 'card', 'T-2']) == 0
            assert run(['--file', path, 'list', '--all']) == 0
            assert run(['--file', path, 'ready']) == 0
            assert run(['--file', path, 'log', 'T-1']) == 0
        out = buf.getvalue()
        assert '验收:免审' in out and '验收:需验收' in out
        assert '[免审]' in out and 'add:登记(免审)' in out

    def test_check_catches_required_done_without_accept(self, tmp_path: Path) -> None:
        """绕过写入门的坏档(required 直达 done)在 check 重放侧被抓;none 同历史不报。"""
        path = f(tmp_path)
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:00:00', 'actor': 't',
                                      'type': 'add', 'task': {
                                          'id': 'T-1', 'title': 'x', 'module': '流程',
                                          'status': 'todo', 'deps': [], 'cond': None,
                                          'priority': 0, 'criteria': [],
                                          'review': 'required'}})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:01:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'todo',
                                      'to': 'done', 'why': None, 'cond': None,
                                      'criteria': ['a.md'], 'assignee': None})
        assert run(['--file', path, 'check']) == 1
        path2 = f(tmp_path / 'n2')
        dag.append_event(Path(path2), {'v': 1, 'ts': '2026-09-11T00:00:00', 'actor': 't',
                                       'type': 'add', 'task': {
                                           'id': 'T-1', 'title': 'x', 'module': '流程',
                                           'status': 'todo', 'deps': [], 'cond': None,
                                           'priority': 0, 'criteria': [],
                                           'review': 'none'}})
        dag.append_event(Path(path2), {'v': 1, 'ts': '2026-09-11T00:01:00', 'actor': 't',
                                       'type': 'status', 'id': 'T-1', 'from': 'todo',
                                       'to': 'done', 'why': None, 'cond': None,
                                       'criteria': ['a.md'], 'assignee': None})
        assert run(['--file', path2, 'check']) == 0


# ---------- 旧名兼容(review → pending_review) ----------


class TestLegacyAlias:
    def seed_doing(self, tmp_path: Path) -> str:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        return path

    def touch(self, tmp_path: Path, rel: str) -> None:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('x', encoding='utf-8')

    def test_legacy_token_write_normalizes(self, tmp_path: Path) -> None:
        """写侧别名:旧名 review 收下,事件按规范名 pending_review 落盘,写入带更名提醒。"""
        import contextlib
        import io
        path = self.seed_doing(tmp_path)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            assert run(['--file', path, 'status', 'T-1', 'review',
                        '--criteria', 'reports/T-1-r1.md']) == 0
        assert '已更名 pending_review' in err.getvalue()
        events = dag.load_events(Path(path))
        last_to = [e.get('to') for e in events if e.get('type') == 'status'][-1]
        assert last_to == 'pending_review'  # 盘上是规范名,不是旧名
        tasks, problems = dag.fold(events)
        assert not problems and tasks['T-1'].status == 'pending_review'
        assert tasks['T-1'].criteria == ['reports/T-1-r1.md']

    def test_legacy_history_folds_to_new_name(self, tmp_path: Path) -> None:
        """读侧归一:手工构造旧名历史事件(模拟未迁移的旧账本),折叠出规范名且后续流转合法。"""
        path = f(tmp_path)
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-10T00:00:00', 'actor': 't',
                                      'type': 'add', 'task': {
                                          'id': 'T-1', 'title': 'x', 'module': '流程',
                                          'status': 'todo', 'deps': [], 'cond': None,
                                          'priority': 0, 'criteria': []}})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-10T00:01:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'todo',
                                      'to': 'doing', 'why': None, 'cond': None,
                                      'criteria': [], 'assignee': 'w1'})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-10T00:02:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'doing',
                                      'to': 'review', 'why': None, 'cond': None,
                                      'criteria': ['reports/T-1-r1.md'], 'assignee': None})
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems
        assert tasks['T-1'].status == 'pending_review'  # 旧名 to 归一
        assert tasks['T-1'].assignee == 'w1'  # 交付者保留
        # 归一后的态可继续合法流转:pending_review→done(文件存在门照常生效)
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reviews/T-1-r1.md']) == 0

    def test_check_flags_legacy_token_as_warning_only(self, tmp_path: Path) -> None:
        """旧名历史只给信息级警,不挡 check 通过(旧账本零迁移可继续用)。
        注:经 CLI 写旧名会先归一再落盘,盘上无旧 token;此处的旧名必须手工注入。"""
        import contextlib
        import io
        path = f(tmp_path)
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-10T00:00:00', 'actor': 't',
                                      'type': 'add', 'task': {
                                          'id': 'T-1', 'title': 'x', 'module': '流程',
                                          'status': 'todo', 'deps': [], 'cond': None,
                                          'priority': 0, 'criteria': []}})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-10T00:01:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'todo',
                                      'to': 'doing', 'why': None, 'cond': None,
                                      'criteria': [], 'assignee': 'w1'})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-10T00:02:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'doing',
                                      'to': 'review', 'why': None, 'cond': None,
                                      'criteria': ['reports/T-1-r1.md'], 'assignee': None})
        self.touch(tmp_path, 'reports/T-1-r1.md')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert run(['--file', path, 'check']) == 0  # 旧名不挡 check 通过
        assert '旧名 review' in buf.getvalue()


# ---------- 写锁(多方并发 append 串行化) ----------


class TestAppendLock:
    def test_lock_released_after_append(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        dag.append_event(Path(path), {'type': 'note', 'id': 'T-1', 'text': 'x'})
        assert Path(path).exists()
        assert not Path(path + '.lock').exists()  # 写完即放锁,不留残留

    def test_stale_lock_broken(self, tmp_path: Path) -> None:
        import os
        import time as _time
        path = f(tmp_path)
        lock = Path(path + '.lock')
        lock.write_text('999', encoding='utf-8')
        old = _time.time() - 120  # 比LOCK_STALE_S老的锁=持锁进程已死
        os.utime(lock, (old, old))
        dag.append_event(Path(path), {'type': 'note', 'id': 'T-1', 'text': 'x'})
        assert not lock.exists()  # 残留锁被强拆且写入成功

    def test_concurrent_appends_no_loss(self, tmp_path: Path) -> None:
        import threading
        path = f(tmp_path)

        def worker(n: int) -> None:
            for i in range(5):
                dag.append_event(Path(path), {'type': 'note', 'id': f'T-{n}',
                                              'text': f'{n}-{i}'})

        threads = [threading.Thread(target=worker, args=(k,)) for k in range(8)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        events = dag.load_events(Path(path))
        assert len(events) == 40  # 8 线程×5 条全落盘,锁串行化无互踩丢行


# ---------- 优先级与关键性排序 ----------


class TestPriority:
    def test_add_priority_and_prio_command(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'a', '--module', '流程', '--priority', '5']) == 0
        assert run(['--file', path, 'add', 'b', '--module', '流程']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems
        assert tasks['T-1'].priority == 5 and tasks['T-2'].priority == 0
        assert run(['--file', path, 'prio', 'T-2', '9']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert tasks['T-2'].priority == 9

    def test_prio_missing_task_rejected(self, tmp_path: Path) -> None:
        assert run(['--file', f(tmp_path), 'prio', 'T-9', '3']) == 2

    def test_priority_bounded_0_to_10(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'a', '--module', '流程', '--priority', '10']) == 0
        assert run(['--file', path, 'add', 'b', '--module', '流程', '--priority', '11']) == 2
        assert run(['--file', path, 'add', 'c', '--module', '流程', '--priority', '-1']) == 2
        assert run(['--file', path, 'prio', 'T-1', '11']) == 2
        assert run(['--file', path, 'prio', 'T-1', '10']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert tasks['T-1'].priority == 10

    def test_ready_order_priority_first(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', '低', '--module', '流程', '--priority', '1']) == 0
        assert run(['--file', path, 'add', '高', '--module', '流程', '--priority', '7']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert dag.ready_set(tasks) == ['T-2', 'T-1']

    def test_ready_order_criticality_breaks_ties(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        # 同优先级下关键链优先:T-1 挡着 T-2→T-3→T-4 三级活链,T-5 无下游
        assert run(['--file', path, 'add', '链头', '--module', '流程']) == 0
        assert run(['--file', path, 'add', '链中', '--module', '流程', '--dep', 'T-1']) == 0
        assert run(['--file', path, 'add', '链尾', '--module', '流程', '--dep', 'T-2']) == 0
        assert run(['--file', path, 'add', '延伸', '--module', '流程', '--dep', 'T-3']) == 0
        assert run(['--file', path, 'add', '独立件', '--module', '流程']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert dag.ready_set(tasks) == ['T-1', 'T-5']
        assert dag.criticality_map(tasks)['T-1'] == (3, 3)  # 最长下游活链 3,挡活下游 3
        assert dag.criticality_map(tasks)['T-5'] == (0, 0)

    def test_ready_numeric_id_order(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        for i in range(1, 11):  # T-1..T-10:字典序会让 T-10 排到 T-2 前,数字序不应
            assert run(['--file', path, 'add', f'x{i}', '--module', '流程']) == 0
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert dag.ready_set(tasks)[:3] == ['T-1', 'T-2', 'T-3']

    def test_ready_view_shows_scores(self, tmp_path: Path) -> None:
        import contextlib
        import io
        path = f(tmp_path)
        assert run(['--file', path, 'add', '链头', '--module', '流程', '--priority', '2']) == 0
        assert run(['--file', path, 'add', '链中', '--module', '流程', '--dep', 'T-1']) == 0
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert run(['--file', path, 'ready']) == 0
        out = buf.getvalue()
        assert 'P2' in out and '链1' in out and '挡1' in out


# ---------- rejected 打回泊位态(打回与返工解耦) ----------


class TestRejectedState:
    def seed_review(self, tmp_path: Path) -> str:
        """建到 pending_review 的任务;返回账本路径。"""
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        r = tmp_path / 'reports' / 'T-1-r1.md'
        r.parent.mkdir(parents=True, exist_ok=True)
        r.write_text('报告', encoding='utf-8')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        return path

    def seed_rejected(self, tmp_path: Path) -> str:
        path = self.seed_review(tmp_path)
        v = tmp_path / 'reviews' / 'T-1-r1.md'
        v.parent.mkdir(parents=True, exist_ok=True)
        v.write_text('reject', encoding='utf-8')
        assert run(['--file', path, 'status', 'T-1', 'rejected',
                    '--why', 'reviews/T-1-r1.md']) == 0
        return path

    def test_reject_park_requires_why_and_real_file(self, tmp_path: Path) -> None:
        path = self.seed_review(tmp_path)
        assert run(['--file', path, 'status', 'T-1', 'rejected']) == 2  # 必带 why
        assert run(['--file', path, 'status', 'T-1', 'rejected',
                    '--why', 'reviews/T-1-r1.md']) == 2  # 结论文件不存在(文件存在门)
        v = tmp_path / 'reviews' / 'T-1-r1.md'
        v.parent.mkdir(parents=True, exist_ok=True)
        v.write_text('reject', encoding='utf-8')
        assert run(['--file', path, 'status', 'T-1', 'rejected',
                    '--why', 'reviews/T-1-r1.md']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'rejected'
        assert tasks['T-1'].assignee == 'w1'  # 交付者保留,返工派工的线索

    def test_rework_dispatch_from_rejected(self, tmp_path: Path) -> None:
        path = self.seed_rejected(tmp_path)
        assert run(['--file', path, 'status', 'T-1', 'doing']) == 2  # 返工派工必带 assignee
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w2']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'doing'
        assert tasks['T-1'].assignee == 'w2'

    def test_rejected_in_ready_and_dead(self, tmp_path: Path) -> None:
        path = self.seed_rejected(tmp_path)
        tasks, _ = dag.fold(dag.load_events(Path(path)))
        assert 'T-1' in dag.ready_set(tasks)  # 打回待返工计入可派(返工派工也是派单)
        assert run(['--file', path, 'status', 'T-1', 'dead', '--why', '需求取消']) == 0

    def test_log_counts_parked_reject(self, tmp_path: Path) -> None:
        import contextlib
        import io
        path = self.seed_rejected(tmp_path)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert run(['--file', path, 'log', 'T-1']) == 0
        out = buf.getvalue()
        assert '交付 1 次,打回 1 次' in out


# ---------- pending_merge 合并泊位(worktree 任务:验收过 ≠ 已合并) ----------


class TestPendingMergeState:
    def touch(self, tmp_path: Path, rel: str) -> None:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('x', encoding='utf-8')

    def seed_delivered(self, tmp_path: Path) -> str:
        """带 worktree 的任务建到 pending_review;返回账本路径。"""
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程',
                    '--worktree', 'wt/T-1']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        return path

    def test_worktree_field_roundtrip(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程',
                    '--worktree', 'wt/T-160']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems
        assert tasks['T-1'].worktree == 'wt/T-160'
        # 无 --worktree = 老流转:事件不带 worktree 键,折叠出 None
        assert run(['--file', path, 'add', 'y', '--module', '流程']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-2'].worktree is None
        assert run(['--file', path, 'add', 'z', '--module', '流程', '--worktree', '']) == 2

    def test_full_merge_chain_then_done(self, tmp_path: Path) -> None:
        path = self.seed_delivered(tmp_path)
        # pending_review(验收过)→ pending_merge 泊位
        assert run(['--file', path, 'status', 'T-1', 'pending_merge']) == 0
        # pending_merge→done 必带 --criteria(合并报告),且过文件存在门
        assert run(['--file', path, 'status', 'T-1', 'done']) == 2
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reports/T-1-merge.md']) == 2
        self.touch(tmp_path, 'reports/T-1-merge.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reports/T-1-merge.md']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'done'
        # 追加不覆盖:交付报告+合并报告共存,整链可溯
        assert tasks['T-1'].criteria == ['reports/T-1-r1.md', 'reports/T-1-merge.md']

    def test_merge_reject_parks_then_rework(self, tmp_path: Path) -> None:
        path = self.seed_delivered(tmp_path)
        assert run(['--file', path, 'status', 'T-1', 'pending_merge']) == 0
        assert run(['--file', path, 'status', 'T-1', 'rejected']) == 2  # 必带 why
        assert run(['--file', path, 'status', 'T-1', 'rejected',
                    '--why', 'reviews/T-1-merge-fail.md']) == 2  # 结论文件须真实存在
        self.touch(tmp_path, 'reviews/T-1-merge-fail.md')
        assert run(['--file', path, 'status', 'T-1', 'rejected',
                    '--why', 'reviews/T-1-merge-fail.md']) == 0
        tasks, problems = dag.fold(dag.load_events(Path(path)))
        assert not problems and tasks['T-1'].status == 'rejected'
        # 打回泊位的返工路由不变
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w2']) == 0

    def test_pending_merge_dead_only_from_berth(self, tmp_path: Path) -> None:
        path = self.seed_delivered(tmp_path)
        assert run(['--file', path, 'status', 'T-1', 'pending_merge']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing',
                    '--assignee', 'w2']) == 2  # 矩阵无 pending_merge→doing 边
        assert run(['--file', path, 'status', 'T-1', 'dead', '--why', '分支废弃']) == 0

    def test_pending_merge_requires_worktree_field(self, tmp_path: Path) -> None:
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程']) == 0
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        # 无 worktree 字段:进泊位打回;老流转照常
        assert run(['--file', path, 'status', 'T-1', 'pending_merge']) == 2
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reviews/T-1-r1.md']) == 0

    def test_worktree_task_direct_done_rejected_with_hint(self, tmp_path: Path) -> None:
        import contextlib
        import io
        path = f(tmp_path)
        assert run(['--file', path, 'add', 'x', '--module', '流程',
                    '--worktree', 'wt/T-1']) == 0
        # doing 直达 done 打回,提示合并路由
        assert run(['--file', path, 'status', 'T-1', 'doing', '--assignee', 'w1']) == 0
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            assert run(['--file', path, 'status', 'T-1', 'done', '--criteria', 'a.md']) == 2
        assert 'worktree 任务验收后置 pending_merge,由合并者收敛' in err.getvalue()
        # pending_review 直达 done 同打回(验收过 ≠ 已合并)
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'pending_review',
                    '--criteria', 'reports/T-1-r1.md']) == 0
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reviews/T-1-r1.md']) == 2
        # 正路:验收 → 泊位 → 合并者收敛
        assert run(['--file', path, 'status', 'T-1', 'pending_merge']) == 0
        self.touch(tmp_path, 'reports/T-1-merge.md')
        assert run(['--file', path, 'status', 'T-1', 'done',
                    '--criteria', 'reports/T-1-merge.md']) == 0

    def test_views_show_berth_and_worktree(self, tmp_path: Path) -> None:
        import contextlib
        import io
        path = self.seed_delivered(tmp_path)
        assert run(['--file', path, 'status', 'T-1', 'pending_merge']) == 0
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert run(['--file', path, 'ready']) == 0
            assert run(['--file', path, 'list']) == 0
            assert run(['--file', path, 'card', 'T-1']) == 0
            assert run(['--file', path, 'who', 'T-1']) == 0
            assert run(['--file', path, 'graph']) == 0
            assert run(['--file', path, 'graph', '--mermaid']) == 0
        out = buf.getvalue()
        assert out.count('== pending_merge 待合并(1) ==') == 2  # ready 与 list 各一段
        assert out.count('wt/T-1') >= 6  # 泊位段/card/who/graph 文本+mermaid 均展示

    def test_check_catches_worktree_done_without_merge_event(self, tmp_path: Path) -> None:
        """绕过写入门的坏档(worktree 任务 pending_review→done)在 check 重放侧被抓。"""
        path = f(tmp_path)
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:00:00', 'actor': 't',
                                      'type': 'add', 'task': {
                                          'id': 'T-1', 'title': 'x', 'module': '流程',
                                          'status': 'todo', 'deps': [], 'cond': None,
                                          'priority': 0, 'criteria': ['reports/T-1-r1.md'],
                                          'review': 'required', 'worktree': 'wt/T-1'}})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:01:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'todo',
                                      'to': 'doing', 'why': None, 'cond': None,
                                      'criteria': [], 'assignee': 'w1'})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:02:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'doing',
                                      'to': 'pending_review', 'why': None, 'cond': None,
                                      'criteria': ['reports/T-1-r1.md'], 'assignee': None})
        self.touch(tmp_path, 'reports/T-1-r1.md')
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:03:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'pending_review',
                                      'to': 'done', 'why': None, 'cond': None,
                                      'criteria': ['reviews/T-1-r1.md'], 'assignee': None})
        self.touch(tmp_path, 'reviews/T-1-r1.md')
        assert run(['--file', path, 'check']) == 1  # 缺 pending_merge→done 合并事件

    def test_check_catches_merge_done_without_report(self, tmp_path: Path) -> None:
        """合并事件缺凭据/合并报告文件被删,check 重放侧抓到。"""
        path = f(tmp_path)
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:00:00', 'actor': 't',
                                      'type': 'add', 'task': {
                                          'id': 'T-1', 'title': 'x', 'module': '流程',
                                          'status': 'todo', 'deps': [], 'cond': None,
                                          'priority': 0, 'criteria': ['reports/T-1-r1.md'],
                                          'review': 'required', 'worktree': 'wt/T-1'}})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:01:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'todo',
                                      'to': 'doing', 'why': None, 'cond': None,
                                      'criteria': [], 'assignee': 'w1'})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:02:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'doing',
                                      'to': 'pending_review', 'why': None, 'cond': None,
                                      'criteria': ['reports/T-1-r1.md'], 'assignee': None})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:03:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'pending_review',
                                      'to': 'pending_merge', 'why': None, 'cond': None,
                                      'criteria': [], 'assignee': None})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:04:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'pending_merge',
                                      'to': 'done', 'why': None, 'cond': None,
                                      'criteria': [], 'assignee': None})
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'check']) == 1  # 合并事件无凭据
        # 补上凭据但文件不存在,仍打回(按整段 JSON 定位合并事件那条,唯一形状)
        events_path = Path(path)
        raw = events_path.read_text(encoding='utf-8').replace(
            '"from": "pending_merge", "to": "done", "why": null, "cond": null, "criteria": []',
            '"from": "pending_merge", "to": "done", "why": null, "cond": null, '
            '"criteria": ["reports/T-1-merge.md"]')
        events_path.write_text(raw, encoding='utf-8')
        assert run(['--file', path, 'check']) == 1
        self.touch(tmp_path, 'reports/T-1-merge.md')
        assert run(['--file', path, 'check']) == 0

    def test_check_catches_pending_merge_without_worktree(self, tmp_path: Path) -> None:
        """手工坏档:pending_merge 任务被抹掉 worktree 字段,check 抓必带字段缺失。"""
        path = f(tmp_path)
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:00:00', 'actor': 't',
                                      'type': 'add', 'task': {
                                          'id': 'T-1', 'title': 'x', 'module': '流程',
                                          'status': 'todo', 'deps': [], 'cond': None,
                                          'priority': 0, 'criteria': ['reports/T-1-r1.md'],
                                          'review': 'required'}})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:01:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'todo',
                                      'to': 'doing', 'why': None, 'cond': None,
                                      'criteria': [], 'assignee': 'w1'})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:02:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'doing',
                                      'to': 'pending_review', 'why': None, 'cond': None,
                                      'criteria': ['reports/T-1-r1.md'], 'assignee': None})
        dag.append_event(Path(path), {'v': 1, 'ts': '2026-09-11T00:03:00', 'actor': 't',
                                      'type': 'status', 'id': 'T-1', 'from': 'pending_review',
                                      'to': 'pending_merge', 'why': None, 'cond': None,
                                      'criteria': [], 'assignee': None})
        self.touch(tmp_path, 'reports/T-1-r1.md')
        assert run(['--file', path, 'check']) == 1  # pending_merge 缺 worktree 字段
