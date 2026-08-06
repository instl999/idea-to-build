# AI 工作记录

## 2026-08-05 — 建立仓库内项目记忆系统

- 任务目标：系统调查现有仓库，根据代码、配置、测试和 Git 状态建立供后续 Codex 跨会话读取的项目记忆。
- 使用的主要上下文：插件/marketplace/Hook 清单，Skill 与全部参考协议，Python 运行时和 CLI，模板与冻结示例，测试套件，GitHub Actions，README/安全/隐私/架构/贡献文档，当前 Git 状态与最近五个提交。
- 新增或更新的文档：根级 `AGENTS.md`、`PROJECT_STATUS.md`、本文件，以及 `docs/` 下的索引、概览、领域、数据、API/集成、开发、测试、部署、决定、技术债务和待确认文档；增补中英文架构说明并纠正调度工具必需/可选的文档冲突。
- 重要发现：项目是无后端/数据库/MCP 的 Python 标准库 Codex Plugin；0.3.0 工作分支已实现原生子智能体/worktree adapter；`pyproject.toml` 版本仍为 0.2.0；真实 Codex 宿主端到端和调度 finalize 尚缺。
- 新增的待确认问题：正式用户/KPI、Codex-only 长期定位、dispatch 完成语义、质量工具策略、monorepo/运行时升级、数据保留、人类授权、0.3.0 发布、最低 Codex 版本、远端安全、运维责任和旧 SkillHub 发布物。
- 是否修改业务代码：否。仅修改 Markdown 文档。
- 验证结果：所有 CLI `--help` 成功；完整 `unittest` 共发现 79 项，其中 78 项通过、1 项因 Windows 目录 symlink 能力跳过；`compileall`、插件包校验、冻结示例 hash、仓库当前支持的发布审计完整模式（当前 tracked files 加 refs 邮箱检查）、Markdown 链接/围栏/尾随空白、敏感模式和 Markdown-only diff 检查均通过。

## 2026-08-06 — 独立怀疑式文档审查

- 任务目标：不扩写产品范围，从入口、运行时、Hook、配置、测试、CI、Git 和官方 Plugin 文档重新核验项目文档，并只修正文档层面的确定错误。
- 已确认并修正：阶段转换图并非所有命令的统一门禁；研究证据字段、状态字段和 package 文件集合只被部分校验；`last_test.json` 可改写且不能证明 recorder 执行；生成项目没有默认 `.gitignore`；Stop Hook 未被测试；adapter 不持久化/强制当前 wave、依赖合并或 merge order；Markdown 写入、初始化与 handoff 并非整体原子；发布审计不扫描历史 blob 或未跟踪文件；单测筛选命令、Plugin 安装说明和不存在的外部 validator 命令过时；版本/远端发布状态曾被混同。
- 文档遗漏补齐：不可伪造测试证据、日志/测试记录误提交、研究输入和 package 校验缺口、阶段绕过、Stop Hook 覆盖、非事务性失败、远端 tag 证据和宿主命令未能本机执行等安全、可靠性、部署风险。
- 信息不足处理：正式用户/KPI、0.3.0 发布、Plugins Directory 状态、最低 Codex 版本、数据保留、人类授权、dispatch 完成与波次强制语义、远端安全和旧发布物处置继续记录在 `docs/OPEN_QUESTIONS.md`，未写成事实。
- 是否修改业务代码：否。只修改 Markdown 文档。
- 验证结果：完整 `unittest` 共发现 79 项，其中 78 项通过、1 项因 Windows 目录 symlink 能力跳过；`compileall`、plugin package 校验、冻结示例校验、发布审计的 worktree/full 两种模式均通过；145 个 Markdown 文件的本地链接、代码围栏、尾随空白和高置信敏感模式检查通过。

## 2026-08-06 — readiness 后的条件式 MCP 支持

- 任务目标：在 Skill 已收集足够需求信息后，只在必要且合理时为用户产品引入 MCP server 方案，并提供可执行但由用户控制的安全指导。
- 主要修改：在 readiness 与核心草稿之间增加 MCP 适用性门禁；定义 `MCP_NOT_APPLICABLE`、`MCP_USE_EXISTING_SERVER`、`MCP_BUILD_CUSTOM_SERVER`、`MCP_DEFER` 四选一结论；补充现有/自建 server 的当前证据、宿主、transport、最小权限、凭据、测试、可观测性和回退协议；生成 `docs/design/MCP_INTEGRATION_GUIDE.md`；包校验要求新协议存在。
- 修改文件：`skills/idea-to-build/SKILL.md`、`references/mcp-integration.md` 及相关研究/readiness/文档协议，权威运行时与冻结示例副本，模板、包校验器、三个测试文件、冻结示例 MCP 指南/状态/README，中英文 README/架构/隐私/安全，以及项目概览、领域、数据、API/集成、决定、技术债务、测试、状态和 changelog。
- 关键决定：Plugin 自身继续不提供 MCP server、网络客户端或新依赖；不增加第 39 项需求、state schema 或 CLI。MCP 是生成产品的条件式架构决策，只有确认 agent 客户端、外部能力、兼容宿主和相对直接集成的实质优势后才采用；证据不足必须延后，现有 server 满足要求时优先复用。
- 兼容与风险：已有 schema/CLI/38 项台账保持兼容；重新生成 handoff 会多一份可变设计文档。候选说明、工具/资源和 server 输出按不可信输入处理；安装、凭据、宿主配置和核心冻结仍由用户控制。真实会话是否完成四选一判断尚无 JSON 运行时证明，已记录为 `K-020`。
- 验证结果：完整 `unittest` 共 82 项，81 项通过、1 项因 Windows 目录 symlink 能力跳过；`compileall`、Plugin package 校验、冻结示例核心 hash 和 `audit_public_release.py --worktree-only` 均通过。新增测试覆盖 readiness→MCP→核心顺序、MCP 指南生成、缺失协议失败和端到端生成。
- 遗留问题：未新增真实 MCP host/server 端到端测试，也未机器持久化 MCP 推荐；未来若要强制，需先设计版本化 schema、迁移、CLI、失败关闭和宿主兼容测试。
## 2026-08-06 — 整体代码审查、加固与 main 合并

- 任务目标：在保留现有 Codex 编排与 readiness 后 MCP 工作的前提下整体审查代码，修复有明确证据且兼容风险可控的问题，完成验证后合并本地 `main`。
- 威胁与失败模式：直接写入 `last_test.json` 可伪造测试门禁；Plugin/生成项目缺少关键文件仍可能校验通过；版本源不一致会导致发布诊断错误；新项目缺少本地忽略规则会增加测试/日志/凭据误提交风险。
- 主要修改：测试记录增加 project ID、固定 runner 标记和声明命令校验；PreToolUse 保护 Hook 可观察的记录写入；Stop 覆盖通过、缺记录、伪造和递归保护路径。统一项目运行时清单，生成包要求 `.gitignore` 与全部 10 个脚本；Plugin 校验覆盖 marketplace、Hook helper、完整 CLI、CI、发布脚本、项目记忆和 0.3.0/cachebuster 版本一致性，并接受官方 helper 支持的小写字母/数字/连字符 token。
- 兼容与恢复：未改变阶段、38 项需求、冻结核心或 dispatch schema。旧 `last_test.json` 会失败关闭，重新执行 state 中已审查的 `project_state.py record-test` 即可恢复；既有生成项目不会自动获得 `.gitignore` 或新运行时，需要显式升级/复制。
- 文档与元数据：同步中英文 README、架构、隐私及项目记忆；Skill agent 元数据补充 readiness 后条件式 MCP；权威运行时修改同步到冻结示例副本。
- 验证结果：完整 `unittest` 共 91 项，90 项通过、1 项因 Windows 目录 symlink 能力跳过；`compileall`、仓库 package validator、官方 Plugin/Skill validator、冻结示例 hash 和公开发布脱敏审计全部通过。

## 2026-08-06 — 增加四层仓库记忆与规范任务开发流程

- 任务目标：在现有研究、需求台账、人工冻结和 Codex handoff 基础上，实现适合普通用户长期开发的项目级、任务级、执行质量级和可恢复提示词四层记忆，并提供安全的旧项目增量迁移。
- 威胁与失败模式：任务文本、研究和提示词可能包含注入；任务路径可能越界或相互重叠；命令型门禁可能被 shell 元字符放大；质量结果可能陈旧或被冒充；迁移可能覆盖现有项目或冻结核心；示例运行时可能与权威源漂移；未知 schema 可能被错误解释。
- 主要实现：新增 `.idea-to-build/tasks.json`、`quality_gates.json`、任务 SPEC/PLAN、记忆地图、工作规则、任务/质量投影、生命周期与维护提示词；新增 `task_state.py`、`quality_gate.py`、`memory_prompts.py`、`migrate_project.py` 和兼容运行时加载器；扩展状态字段、Stop Hook、上下文注入、包校验、模板和冻结示例。
- 调度适配：默认顺序模式只允许一个活动任务；并行模式只从规范任务台账派生子智能体、路径所有权、依赖波次、SPEC/PLAN 和质量门禁。工作树创建结果回传规范任务 ID，依赖未完成时可进入 ready，但不能开始实施。
- 安全与恢复：未知 schema、越界/链接路径、重叠所有权、非具体验收、陈旧门禁和非 human 人工验收均失败关闭；命令不用 shell；迁移预检后原子添加且失败回滚，不覆盖变量文件、冻结核心或锁文件，也不重新冻结。
- 文档：重写中英文 README；新增中英文仓库记忆说明；同步架构、安全、隐私、变更控制、贡献、索引、领域/数据/API、开发/测试/部署、决定、技术债务、待确认问题、变更日志和项目状态。
- 兼容性：保持 Python 3.9+ 标准库、Git、状态 schema 1、任务/质量/dispatch schema 1 和既有冻结 hash。旧项目可仅添加缺失资产；旧 `idea_to_build_lib.py` 保持不变，由独立兼容副本为新 CLI 提供 0.4 能力。
- 验证结果：112 项 `unittest` 中 111 通过、1 项因 Windows 目录符号链接能力跳过；`compileall`、包校验、冻结示例校验、公开发布审计、Plugin validator 和设置 `PYTHONUTF8=1` 的 Skill validator 均通过。示例冻结核心和锁文件没有被修改。
- 遗留事项：真实 Codex 宿主 smoke test、adapter finalize/更强波次强制、独立 JSON Schema、签名/provenance 和 0.4.0 远程发布仍未实现或未确认，已保留在技术债务与待确认问题中。
