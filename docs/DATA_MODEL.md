# 数据模型

## 持久化方式

项目没有数据库、ORM、migration 文件或 seed 机制。持久数据是 UTF-8 Markdown/JSON 文件和 Git 历史；访问由 Python `pathlib`、`json`、原子临时文件替换和 Git 子进程完成。证据：`idea_to_build_lib.py` 的 `write_json()`、`load_json()`、`git_commit_paths()`。

## 主要记录

| 路径/模型 | 关键内容 | 生命周期与约束 |
| --- | --- | --- |
| `.idea-to-build/project_state.json` | 项目 ID/名称、16 阶段之一、研究/构建/需求/冻结/调度状态、里程碑、工作流、测试命令 | 初始化创建；状态命令和生成/冻结/调度流程更新；schema 版本当前为 1 |
| `.idea-to-build/requirements_ledger.json` | 精确 38 项需求及状态、值、接受标记和说明 | 初始化创建；只能更新允许字段；ID 和优先级/可逆性/readiness 元数据由代码校验 |
| `.idea-to-build/core.lock.json` | 五个核心文件的路径、SHA-256、字节数、聚合 hash、人类确认和冻结时间 | 模板 marker 在初始化时移除；人工冻结后创建；正常开发中不可修改 |
| `codex/dispatch.json` | 项目/核心绑定、编排模式、能力要求、任务、所有权、prompt hash、依赖波次 | handoff 生成；整体有 `manifest_sha256`；启动前必须已提交 |
| `.idea-to-build/last_test.json` | schema、项目 ID、runner 标记、精确命令、状态、退出码、时间和 Git/worktree 摘要 | `record-test` 重写；模板默认忽略且 Hook 阻止可观察的直接写入，但有文件系统权限的外部进程仍可伪造 |
| `.idea-to-build/guardrail.log` | Hook 检测到的核心漂移摘要 | PostToolUse 追加；生成模板默认忽略；内容/覆盖范围不足以替代审计系统 |
| `docs/core/*.md` | 五份冻结业务契约 | 人工冻结前可评审；冻结后由 hash/Git/只读位/Hook 保护 |
| `docs/design/*.md`、`docs/live/*.md` | 可变设计骨架和运行记录 | 生成或开发期间更新，不得覆盖核心契约 |
| `docs/design/MCP_INTEGRATION_GUIDE.md` | readiness 后的 MCP 推荐、证据、能力映射、安全/配置/验证与回退指导 | handoff 生成骨架；若影响系统边界，冻结前由 `ARCHITECTURE_CONTRACT.md` 记录决定；没有新增 JSON 字段 |
| Git commit/tag/branch/worktree | 初始化、冻结、调度启动、任务结果和恢复证据 | Git 是版本与集成权威；子 worktree 退休后保留分支 |

## 主键、关联和唯一性

- 初始化会生成 UUID 字符串作为 `project_id`，用于比较 state 与 dispatch manifest；`migrate_state()` 不验证其类型或 UUID 格式，代码也没有跨项目索引。
- 需求主键是 `REQUIREMENT_SPECS` 中的 38 个稳定 ID；缺失、重复、未知或元数据漂移都会失败。
- 核心文件集合必须与 `CORE_FILES` 精确相等；聚合 hash 按固定路径顺序计算。
- 调度任务 ID、子智能体 `task_name` 和线程名称必须唯一；分支名和任务 ID受正则限制。
- 任务依赖通过任务 ID关联；`_dependency_waves()` 拒绝循环或无法解析的依赖。

## Schema 与迁移

- 当前 `SCHEMA_VERSION = 1`。
- `migrate_state()` 会把缺失的旧字段补为默认值；`ensure_supported_schema()` 把旧版本标记为当前版本。只有部分字段、枚举和嵌套结构被校验，不能把它等同于完整 schema 验证。
- 高于运行时支持版本的 JSON 明确拒绝，避免猜测性迁移。
- 未找到独立 migration 历史、降级工具或 schema JSON 文件；变更由 Python 代码和测试共同约束。

## 数据生命周期与删除

- 初始化写入模板和台账；研究/需求/冻结/生成/调度逐步追加或重写本地文件。初始化与 handoff 生成没有通用事务，晚期错误可能留下部分输出。
- 项目模板复制 `.gitignore`，默认忽略 `last_test.json`、`guardrail.log`、Python 缓存、本地虚拟环境和 `.env*`（保留 `.env.example`）；既有项目和显式强制添加仍需人工检查。
- 冻结基线不提供原地 unlock/rehash/refreeze；新基线走人工变更控制或新项目/分支。
- 工作树仅在干净时删除，任务分支保留。普通文件删除不清除 Git、备份、远端、搜索服务日志或已发送提示词中的副本。
- 没有软删除字段、数据库审计字段、自动保留期限或备份任务。

## 一致性风险

- state、core lock、dispatch manifest 和 Git HEAD 是多份关联状态；代码只对冻结和 dispatch 启动提供限定回滚，没有通用事务机制。
- `TRANSITIONS` 只约束手工 transition API；专项命令直接写 `current_phase`，可能产生转换图没有记录的跳转。
- `last_test.json` 没有签名：Hook 可见写入受保护，Stop 校验 project ID、runner 标记、声明命令、退出状态和快照，但外部进程仍能重算并伪造这些普通字段。
- `project_state.json` 的 `core_frozen` 是缓存式字段，安全判断必须以非模板锁和重新计算 hash 为准。
- 运行时同时存在源文件、初始化后的项目副本和冻结示例副本，发布时必须校验同步。
- Git 历史会永久保留误提交的敏感信息；删除工作树文件不能完成脱敏。

## 0.4 记忆数据

| 路径 | 角色 | 一致性/保留 |
| --- | --- | --- |
| `.idea-to-build/tasks.json` | 规范任务台账 | schema 1；原子替换；未来 schema 失败关闭 |
| `docs/live/TASKS.md` | 台账的人类投影 | 可由 `sync-docs` 幂等重建，不是状态源 |
| `.idea-to-build/quality_gates.json` | 显式命令/人工门禁配置 | schema 1；未知门禁和不安全命令拒绝 |
| `.idea-to-build/last_quality.json` | 当前任务/快照质量结果 | 可变且默认忽略；受限输出；不是签名证明 |
| `specs/<TASK-ID>/SPEC.md` / `PLAN.md` | 任务验收与实施事实 | 可变，但受冻结核心优先级约束 |
| `project_state.json` 的 `development_mode`、`planned_tasks`、`current_task_id` | 开发选择与当前任务 | schema 仍为 1 的加法兼容字段 |

迁移器只新增缺失文件。旧库缺 API 时新增版本化兼容 runtime，不覆盖原 runtime；迁移失败会删除本次已创建文件。JSON 台账是原子事实源，Markdown 投影发生失败时可从 JSON 重建，不宣称跨文件事务。
