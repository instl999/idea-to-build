# 技术决定记录

以下只记录能从当前代码/配置确认的决定。“可能原因”没有作者原始记录时明确标为推测。

## D-001：采用本地 Codex Plugin，而非托管服务

- 决定：包由一个 Skill、生命周期 Hooks、模板和本地 CLI 组成，不提供 MCP server 或后端。
- 证据：`.codex-plugin/plugin.json`、`hooks/hooks.json`、`README.md`。
- 可能原因：推测是为了让状态、契约和 Git 操作留在用户仓库，并减少服务端密钥/运维面。
- 约束：功能受 Codex 宿主版本、Hook 信任和本地权限限制。
- 修改前考虑：认证、数据外传、部署、兼容、遥测、密钥和故障恢复边界会整体改变。

## D-002：Python 3.9+ 纯标准库运行时

- 决定：运行时和测试不依赖第三方 Python 包。
- 证据：`pyproject.toml`、所有 Python import、README。
- 可能原因：推测是降低安装摩擦、供应链和跨平台兼容成本。
- 约束：自行实现 schema、CLI、原子写入、路径和 Git 协议；没有成熟验证库的额外保障。
- 修改前考虑：依赖必要性、维护、许可、安全、隐私、平台、锁定和替代方案。

## D-003：固定 38 项需求账本并失败关闭

- 决定：需求 ID、分类、优先级、可逆性和 readiness 元数据由代码固定，文件不能覆写。
- 证据：`REQUIREMENT_SPECS`、`load_ledger()`、`check_readiness()`、`test_requirements_readiness.py`。
- 可能原因：推测是防止缺项或篡改门禁让不完整项目进入冻结。
- 约束：新增/删除需求属于 schema/兼容变更；必须同步模板、迁移和测试。
- 修改前考虑：旧项目加载、readiness 含义、默认迁移和用户数据保留。

## D-004：核心契约由人类确认并以 SHA-256/Git 冻结

- 决定：五份固定核心文件按规范化换行计算 hash，写锁、设只读位并提交；AI 不得确认或冻结。
- 证据：`CORE_FILES`、`confirm_core()`、`freeze_core()`、Hook `forbidden_request()`。
- 可能原因：推测是把产品/架构不可变边界与可变实现分开，并保留审计证据。
- 约束：当前没有原地 unlock/rehash/refreeze；hash 提供完整性，不提供身份认证或加密。
- 修改前考虑：人类授权、恢复、旧基线、迁移、审计和 Hook 绕过路径。

## D-005：打开的项目是不可信边界，Hook 只加载安装包运行时

- 决定：Hook 通过自身路径导入已安装插件的 `idea_to_build_lib.py`，不执行生成项目的 Python 副本。
- 证据：`hooks/_hooklib.py:load_runtime()`、`test_project_runtime_is_never_imported`。
- 可能原因：代码注释明确说明防止仅因打开仓库就执行仓库控制代码。
- 约束：安装包与生成项目副本可能版本不同；Hook 行为以安装包为准。
- 修改前考虑：信任根、缓存更新、版本绑定和兼容错误提示。

## D-006：路径和 Git 操作要求精确项目边界

- 决定：仓库相对路径拒绝绝对路径、`..`、盘符和链接/联接点；冻结/调度要求 exact Git top-level。
- 证据：`safe_project_path()`、`ensure_exact_git_root()`、初始化/冻结/调度测试。
- 可能原因：推测是防止模板覆盖、父仓库误提交和 worktree 逃逸。
- 约束：不能直接在父 monorepo 子目录中冻结生成项目；worktree 必须是直接同级目录。
- 修改前考虑：monorepo 支持、安全边界、Windows junction 和回滚语义。

## D-007：根智能体与子智能体按实际耦合选择

- 决定：单个有效工作流留在根任务；两个以上非重叠工作流生成 Codex 子任务、依赖波次和同级 worktree。
- 证据：`merge_overlapping_workstreams()`、`plan_threads()`、`_dependency_waves()`。
- 可能原因：Skill 文档明确把子智能体视为可逆执行策略，以避免不必要协调成本。
- 约束：同时写入路径不能重叠；根任务负责共享文件和集成。
- 修改前考虑：宿主并发槽位、提示词最小化、所有权、合并顺序和失败恢复。

## D-008：子任务结果先验证再受控合并

- 决定：要求完整 commit ID、预期分支 tip、base ancestry、非空且无 rename 绕过的 owned diff；合并使用 `--no-ff` 并在冲突时 abort。
- 证据：`verify_codex_task_result()`、`merge_codex_task_result()`、`test_codex_dispatch.py`。
- 可能原因：推测是把子智能体文本汇报降级为不可信输入，以 Git 对象为证据。
- 约束：跨所有权共享更改必须由根任务处理；合并是串行门禁。
- 修改前考虑：merge strategy、签名提交、测试证据绑定和已合并幂等。

## D-009：测试记录使用流程性来源绑定，但不提供密码学证明

- 决定：`record-test` 只执行 state 中精确声明的命令，并记录项目 ID、固定 runner 标记、命令、子进程退出码、HEAD 和工作树摘要；PreToolUse 阻止 Hook 可观察的直接记录写入，Stop 拒绝跨项目、未知 runner、未声明、失败或 stale 记录。
- 证据：`project_state.py record-test`、`git_snapshot()`、`hooks/_hooklib.py`、`hooks/stop_check.py` 和 Stop 正反测试。
- 可能原因：降低把旧结果、其他项目结果或直接工具伪造当作当前测试证据的风险；普通 JSON 没有签名，仍不能防止有文件系统权限的外部进程伪造。
- 约束：工作树变化会让记录失效；命令不经 shell 执行，但可执行文件和参数来自可变 state，运行前仍须按不可信代码审查。旧格式记录需要重新运行 recorder。
- 修改前考虑：多命令测试、平台差异、耗时、timeout、宿主回执和结果签名。

## D-010：Codex-only 支持边界

- 决定：自 0.3.0 起明确不承诺 OpenClaw、通用 SkillHub、Claude Code 或跨宿主兼容；0.4.0 继续保持该边界。
- 证据：Plugin 描述、`SKILL.md`、README 的支持边界、`codex-orchestration.md`。
- 可能原因：明确原因是端到端契约依赖 Codex Plugins、Hooks、原生协作工具和 worktree。
- 约束：Markdown 可被其他宿主读取不等于可安装或行为兼容。
- 修改前考虑：每个新宿主需要独立适配、安全模型、安装和端到端测试。

## D-011：MCP 是 readiness 后的条件式生成产品集成

- 决定：Plugin 自身仍无 MCP server/客户端；Skill 只在 readiness 后为生成产品四选一推荐“不适用、使用现有、自建或延后”，优先直接集成或经过验证的现有 server。
- 证据：`SKILL.md`、`references/mcp-integration.md`、`DESIGN_DOCS` 和对应回归测试。
- 约束：不新增第 39 项需求、state schema、CLI、依赖或自动安装；核心边界受影响时必须在冻结前由用户审阅。
- 修改前考虑：若未来机器持久化/强制该决策，需定义 schema 迁移、旧项目默认、CLI/退出码、失败关闭、凭据与宿主兼容测试。

## D-012：四层记忆以规范任务和快照质量为中心，默认顺序开发

- 决定：冻结核心之后建立规则、规格、任务和质量四层记忆；任务 JSON 是状态唯一事实源，质量记录必须绑定当前快照，默认 `guided_sequential`，并行只接受规范 ready 任务。
- 证据：`load_tasks()`、`transition_task()`、`run_quality_gate()`、`memory_prompt()`、`render_context()`、`generate_handoff()`、Stop 和新增测试。
- 约束：仓库正文不可信；人工门禁不能由 AI 完成；Markdown 投影可重建但不是跨文件事务；记录和 Hook 不是密码学证明。
- 兼容：schema 1 加法字段；旧项目继续 last_test 路径，迁移不覆盖并可增加版本化兼容 runtime。
