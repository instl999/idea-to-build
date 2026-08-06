# 已知问题与技术债务

本文件只记录当前代码、测试和配置中可见的问题，不代表本次任务已修复。级别表示当前优先级判断；“推测”项需要负责人确认。

## 严重

当前未发现有足够证据列为“严重”的问题。Hook 本身不是安全沙箱，但仓库已明确该边界，不能把它误述为完全防护。

## 高

### K-001：真实 Codex 宿主端到端路径未自动验证

- 证据：五类 Hook 和调度都通过 Python 夹具/子进程模拟；`.github/workflows/ci.yml` 没有安装 Codex 或触发真实 Plugins/Hooks/子智能体。
- 影响：宿主 schema、Hook 事件、CLI 版本、rollout 或权限变化可能让本地测试通过但实际安装/调度失败。
- 确认状态：已确认测试缺口。
- 建议方向：增加受控宿主兼容矩阵或发布前人工 smoke checklist，固定最低支持版本。

### K-002：Hooks 是启发式纵深防御，存在不可观察/绕过路径

- 证据：`hooks/_hooklib.py` 通过工具名、命令正则和 token 推断；`SECURITY.md` 明确外部编辑器、进程和未上报工具可绕过。
- 影响：有文件系统权限的进程仍可修改受保护内容；不能把 Hook deny 当作安全或身份边界。
- 确认状态：已确认且属于设计限制。
- 建议方向：继续以 hash、精确 Git 历史、只读位、人审和 change control 为权威；为新工具事件增加正反测试。

### K-013：阶段转换图不是统一门禁

- 证据：`transition_state()` 校验 `TRANSITIONS`，但 `research_report.py`、`requirements_check.py`、`confirm_core()`、`generate_handoff()` 等直接写 `current_phase`；其中部分路径不校验来源阶段。
- 影响：调用专项命令可以产生转换图未声明的跳转，phase history 也不能作为完整流程证据。
- 确认状态：已确认实现差异；预期应统一图还是保留专项门禁待人工决定。
- 建议方向：为每个阶段写入定义统一 transition API 或显式来源门禁，并补从错误阶段调用的反例测试。

### K-014：Stop Hook 的测试证据仍不是密码学证明

- 证据：`record-test` 现在记录项目 ID、固定 runner 标记、仍在 state 中声明的命令、退出状态与 Git 快照；PreToolUse 保护 `.idea-to-build/last_test.json` 的 Hook 可观察写入，Stop 逐项校验，且已有通过/缺失/伪造回归测试。但该文件仍是普通 JSON。
- 影响：常见 AI 工具直接伪造已被阻止；有文件系统权限的外部进程或未上报工具仍能重算字段并伪造，不能把 Stop 视为安全证明。
- 确认状态：已部分缓解；流程性 provenance 已实现，是否需要更强执行证明待人工决定。
- 建议方向：如质量门禁需要跨进程信任，设计宿主执行回执、签名/nonce 或受隔离 runner；否则保持当前边界声明和外部进程风险提示。
## 中

### K-004：调度完成状态没有明确写入路径

- 证据：`CODEX_DISPATCH_STATUSES` 包含 `COMPLETE`，但仓库内没有把状态设置为 `COMPLETE` 的实现；adapter 也不持久化已完成 task/current wave，`materialize-wave` 和 `merge-result` 不强制依赖或 merge order。
- 影响：自动化无法从 state 判定全部 wave 是否完成，也无法仅靠 adapter 阻止提前运行后续 wave 或乱序合并，状态可能长期停留 `ACTIVE`。
- 确认状态：已确认代码缺口；是否有意留给人工待确认。
- 建议方向：定义完成门禁、测试/状态/live docs 要求和失败恢复后再实现显式 finalize 命令。

### K-005：没有 lint、format、静态类型和覆盖率门禁

- 证据：`pyproject.toml` 和 CI 只配置 `unittest`、`compileall`、包/核心/审计校验。
- 影响：未使用 import、风格漂移、类型错误和未覆盖分支主要依赖人工/运行测试发现。
- 确认状态：已确认。
- 建议方向：先决定纯标准库约束是否允许仅开发依赖，再逐项引入并固定配置。

### K-006：运行时存在多个物理副本

- 证据：权威脚本位于 `skills/idea-to-build/scripts/`，冻结示例也跟踪 `examples/team-brief-generator/scripts/` 的复制件；初始化还会复制到每个生成项目。
- 影响：修复可能只更新一个副本，导致 Hook、CLI、示例或用户项目行为分叉。
- 确认状态：架构上已确认；本次检查的 10 个示例运行时副本均与权威源 hash 一致。
- 建议方向：增加全量副本一致性测试或明确版本/升级工具；Hook 继续只加载安装包可信副本。

### K-007：Git 子进程没有统一超时

- 证据：`_run_git()` 和发布审计的 `subprocess.run()` 未传 `timeout`。
- 影响：异常凭证助手、钩子、文件系统或 Git 状态可能让 CLI/Hook 长时间挂起；宿主 Hook 外层超时不覆盖普通 CLI。
- 确认状态：已确认。
- 建议方向：定义各操作安全 timeout 和超时后的可恢复错误，特别验证 Windows 和大型仓库。

### K-008：JSON 契约没有独立 schema 文件

- 证据：state、ledger、lock、dispatch 的校验分散在 `idea_to_build_lib.py`；没有 JSON Schema，且 state 的 `project_id`、时间/hash 等字段以及部分嵌套结构只做浅校验或不校验。
- 影响：外部工具难以提前验证，文档与实现更易漂移。
- 确认状态：已确认。
- 建议方向：从代码事实提取版本化 schema，并用测试保证与运行时一致。

### K-009：发布脱敏审计是启发式

- 证据：`scripts/audit_public_release.py` 只对当前 tracked 文件使用有限正则检查路径、邮箱和常见 token 格式；完整模式只额外遍历所有 refs 的提交邮箱，不扫描未跟踪文件或历史 blob。
- 影响：可能漏掉其他凭证、二进制、编码或历史对象中的敏感数据，也可能误报示例文本。
- 确认状态：已确认且已在隐私/安全文档披露。
- 建议方向：结合 GitHub secret scanning/push protection、专业扫描和人工审查；发现凭证先轮换再清历史。

### K-010：GitHub Actions 未按 commit SHA 固定

- 证据：`.github/workflows/ci.yml` 使用 `actions/checkout@v4` 和 `actions/setup-python@v5`。
- 影响：上游 tag 供应链风险高于不可变 SHA；实际风险取决于组织策略。
- 确认状态：配置事实已确认，风险程度为推测。
- 建议方向：评估组织供应链政策并考虑固定审核过的 commit SHA 与更新流程。

### K-015：研究证据协议只被部分机器校验

- 证据：`solution-research.md` 要求日期、查询、许可、维护、隐私、价格等字段；`decide_research()` 接受只含 http(s) `official_source` 的候选，缺失 12 项评分按 0 计算并仍可返回 `BUILD_CUSTOM`。
- 影响：结构不完整、不可审计的研究输入仍可能驱动 build/adopt 决策，文档中的“失败关闭”只覆盖离线、冲突、空候选和部分数值/URL错误。
- 确认状态：已确认实现缺口；是否把全部协议字段设为阻断兼容性决定待确认。
- 建议方向：定义版本化输入 schema、必需证据与错误级别，并补缺字段/过时字段测试。

### K-018：初始化和 handoff 生成不是事务

- 证据：`initialize_project()` 在文件复制后才执行 Git 根/commit；`generate_handoff()` 会依次写设计文档、删除旧 prompt、写 handoff/manifest/state，只有冻结和 dispatch start 有限定回滚。
- 影响：Git、编码、权限或后续校验失败时可能留下半初始化或跨文件不一致状态，重试/`--force` 可能覆盖调查证据。
- 确认状态：已确认控制流；具体故障恢复 UX 待设计。
- 建议方向：先扩展失败注入测试与恢复说明，再决定 staging directory/transaction journal/幂等重试。

### K-020：MCP 推荐没有机器持久化或运行时门禁

- 证据：四选一推荐、readiness 后置条件和安全指导位于 `SKILL.md`/参考协议；state/ledger 没有 MCP 字段，Python 只生成设计骨架，包测试只能验证协议顺序和文件存在。
- 影响：真实对话是否完成适用性判断、使用哪项推荐及证据是否齐全，仍依赖 Skill 执行和人审，不能从 JSON 状态独立证明。
- 确认状态：已确认且属于本次保持 schema/38 项兼容的设计取舍。
- 建议方向：先收集实际使用反馈；若需要机器门禁，再以版本化 schema、CLI、迁移、失败关闭和正反集成测试实现。

## 低

### K-011：生成的设计文档只是通用骨架

- 证据：`generate_design_documents()` 对每节写入相同的推荐/default/assumption 提示；README 明确要求后续专业任务补充。
- 影响：用户可能误把生成文件当成已完成设计。
- 确认状态：已确认设计行为。
- 建议方向：保持醒目标识，并在生成后要求责任人逐节补证据和验收。

### K-012：Windows 目录 symlink 安全测试可能跳过

- 证据：`test_initialization_safety.py` 在系统不允许创建目录 symlink 时调用 `skipTest`。
- 影响：该机器不能验证这一分支，但其他平台 CI 可覆盖。
- 确认状态：本次运行环境已观察到跳过。
- 建议方向：保留跨平台 CI，并考虑 junction 专项测试。

## 已在 2026-08-06 修复的审查问题

- **K-003**：`pyproject.toml` 已与 Plugin manifest 统一为 0.3.0，package validator 增加基准版本与 `+codex.*` cachebuster 一致性测试；远端 0.3.0 tag/发布仍是独立待确认事项。
- **K-016**：Plugin 必需清单现覆盖 marketplace、Hook helper、完整 CLI、发布脚本、CI 与项目记忆；生成项目校验复用统一 10 脚本清单并有缺文件反例。22 份设计文档的内容级完整性仍未强制。
- **K-017**：模板和冻结示例加入 `.gitignore`，默认忽略测试/guardrail、本地虚拟环境、Python 缓存和 `.env*`，并保留 `.env.example`。既有项目与已跟踪历史不自动迁移。
- **K-019**：Stop Hook 已增加当前快照通过、缺记录、伪造记录和 `stop_hook_active` 测试；stale、STATUS 缺失、非开发阶段和真实宿主事件仍可扩展。
