# 项目状态

更新时间：2026-08-06（Asia/Shanghai）
代码基线：本地 `main`；0.4.0 变更尚未推送到 `origin/main`
最新已知发布标签：`v0.2.0`

## 当前阶段

仓库中的 0.4.0 功能实现与文档已经完成，正在等待本地提交。该版本在原有 Idea-to-Build 研究、38 项需求门禁、人工确认与冻结、Codex handoff 和 worktree 调度基础上，新增面向长期开发的四层仓库记忆、规范任务生命周期、质量门禁记录、可恢复提示词和增量迁移。

Plugin 仍然只面向 Codex Desktop/CLI；不支持 OpenClaw、通用 SkillHub 或 Claude Code。运行时保持 Python 3.9+ 标准库和 Git，无数据库、认证、公共 HTTP API、MCP server、托管后端或第三方 Python 依赖。

## 0.4.0 已实现能力

- 第一层“项目长期记忆”：`AGENTS.md`、冻结 `docs/core/**`、`docs/live/MEMORY_MAP.md`、`docs/live/WORKING_RULES.md`、状态、决策、风险、变更请求和 backlog。
- 第二层“任务级记忆”：`.idea-to-build/tasks.json` 是规范台账，`docs/live/TASKS.md` 是可重建的人类视图，每个任务有独立 `SPEC.md` 与 `PLAN.md`。
- 第三层“执行与质量记忆”：`.idea-to-build/quality_gates.json` 定义门禁，忽略提交的 `last_quality.json` 记录当前快照结果；命令门禁和人工验收分离。
- 第四层“可恢复提示词”：启动、恢复、收尾以及规则、规格、任务、质量和全局审计提示词，按项目语言输出并限定读取范围。
- 任务状态机：`draft → ready → in_progress → review → done`，支持阻塞、重开、依赖、路径所有权和具体验收标准校验。
- 默认 `guided_sequential` 模式一次只允许一个活动任务；显式 `parallel_worktrees` 模式从规范任务台账生成无重叠所有权、依赖波次和 Codex worktree manifest。
- `task_state.py`、`quality_gate.py`、`memory_prompts.py` 和 `migrate_project.py` 提供完整本地 CLI。
- 旧项目迁移只补缺失文件，不覆盖已有变量文件、不修改冻结核心、不重写锁文件、不重新冻结；旧运行时通过独立兼容副本承载新 CLI。
- Hook 注入只加载已安装 Plugin 的可信运行时；项目文本、研究结果、生成提示词和任务字段均按不可信输入处理。
- 中英文 README、仓库记忆、架构、安全、隐私、变更控制和贡献文档已同步到 0.4.0。

## 兼容与安全边界

- 状态、任务、质量和 dispatch 的未知或更高 schema 均失败关闭。
- `docs/core/**` 和 `.idea-to-build/core.lock.json` 冻结后不可由 AI 修改；变更只能记录到 `docs/live/CHANGE_REQUESTS.md`。
- 路径必须仓库相对且规范化，拒绝链接/联接点逃逸；并行任务不能拥有重叠写入范围。
- 质量命令使用参数数组或受限解析，不通过 shell 执行；项目文档中的命令不会被自动发现或执行。
- 人工质量门禁必须由 human actor 以精确确认语句接受；Hook、manifest hash、状态和本地记录是流程控制，不是密码学身份或独立安全边界。
- JSON 台账使用临时文件替换；Markdown 投影视为可重建视图，不宣称跨文件事务性。

## 已验证结果

2026-08-06 在 Windows 本地完成：

- `python -m unittest discover -s tests -v`：112 项，111 通过，1 项因目录符号链接能力不可用而跳过，0 失败。
- `python -m compileall -q hooks skills/idea-to-build/scripts tests scripts`：通过。
- `python skills/idea-to-build/scripts/validate_package.py --path .`：通过。
- `python examples/team-brief-generator/scripts/verify_core.py --path examples/team-brief-generator`：通过，冻结 hash 为 `409bf7fe207f8da0d0e50eff1f0c2ff16b1eb70720b89cfdabd2e742281e7b73`。
- `python scripts/audit_public_release.py --worktree-only`：通过。
- 官方 Plugin validator：通过。
- 官方 Skill quick validator：在 `PYTHONUTF8=1` 下通过；Windows 默认 GBK 运行上游脚本会因其未显式指定 UTF-8 而报解码错误。
- 冻结示例的 `docs/core/**` 与 `.idea-to-build/core.lock.json` 相对 Git 基线无差异。
- 示例 dispatch 生成两波：第一波 `TASK-0001`；第二波 `TASK-0002`、`TASK-0003`、`TASK-0004`。
- 示例 `start-task` 提示词能够恢复规范任务、SPEC、PLAN、质量门禁、冻结边界和执行前检查。

## 尚未实现或仍属部分实现

- 没有真实 Codex 宿主自动化端到端 CI；Hook、subagent 和 worktree 主路径由 Python 集成测试覆盖。
- 没有自动发布、签名、provenance、0.4.0 tag 或 Plugins Directory 发布确认。
- adapter 尚未提供独立 finalize 命令，也未把所有 wave/merge 顺序约束提升为不可绕过的宿主安全边界。
- 没有独立 JSON Schema、降级工具、集中日志、指标、告警、覆盖率或性能基准。
- 项目运行时仍在 Plugin 源、模板、示例和旧项目兼容副本之间复制，后续版本需要继续防止漂移。

详见 [`docs/KNOWN_ISSUES_AND_TECH_DEBT.md`](docs/KNOWN_ISSUES_AND_TECH_DEBT.md) 与 [`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md)。

## 推荐下一步

在一个新的 Codex 任务中加载刚刷新的本地 Plugin，并用冻结示例执行一次真实宿主 smoke test：

```text
使用 idea-to-build，在 examples/team-brief-generator 中为 TASK-0001 生成 start-task 指导；只复述上下文和计划，不修改代码。
```
