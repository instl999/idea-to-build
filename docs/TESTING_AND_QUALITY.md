# 测试与质量

## 框架与目录

- 测试框架：Python 标准库 `unittest`。
- 测试入口：`python -m unittest discover -s tests -v`，来源为 `pyproject.toml`、README、CI 和贡献指南。
- 目录：`tests/`；共享夹具在 `tests/_support.py`，结构化研究/激活样例在 `tests/fixtures/`。
- 临时生成项目写入 `.test-tmp/`，该目录被 `.gitignore` 忽略。

## 覆盖范围

| 层级 | 文件 | 已覆盖行为 |
| --- | --- | --- |
| 单元 | `test_state_machine.py` | 默认字段、允许/拒绝转换、旧/未来 schema |
| 单元 | `test_research_workflow.py` | 研究决策、评分边界、冲突/离线/无候选、Markdown 转义 |
| 单元 | `test_requirements_readiness.py` | 38 项台账、P0 冲突、不可逆假设、元数据防篡改、readiness |
| 单元/集成 | `test_core_lock.py` | 精确确认、冻结、换行规范化、漂移、父 Git 根拒绝 |
| 单元/集成 | `test_prompt_generation.py` | 单/多工作流、所有权合并、危险路径/命令拒绝、自包含提示词、MCP 指南生成 |
| 集成 | `test_hooks.py` | 五类 Hook 的上下文/门禁；Stop 通过、缺记录、伪造记录、递归保护；受保护路径、人工命令、Git 变更和可信运行时加载 |
| 集成 | `test_codex_dispatch.py` | manifest、波次、脏树门禁、启动提交、真实 worktree、结果验证、合并与冲突恢复 |
| 端到端 | `test_end_to_end.py` | 初始化 → readiness → 冻结 → 文档/handoff → 包校验 |
| 安全/包 | `test_initialization_safety.py`、`test_package_validation.py`、`test_activation_cases.py` | 预检、链接路径、完整运行时与 .gitignore 复制、清单/版本/必需文件、MCP 阶段顺序/缺失协议反例、激活正反例 |
| 安全/发布 | `test_release_audit.py` | 官方/测试 no-reply 地址允许，以及个人邮箱和相似域名拒绝 |
| 测试基础设施 | `test_fixture_cleanup.py` | 临时目录清理的瞬态重试、重试耗尽和非瞬态错误传播 |

PR 基线加入发布审计与夹具清理回归后的隔离验证共发现 122 个测试：121 个通过，1 个 Windows 目录 symlink 场景因系统能力跳过。若测试数量发生变化，必须更新本段和 `PROJECT_STATUS.md`。

## 静态和包级检查

- `compileall`：确认 Python 源可编译，不是完整 lint 或类型检查。
- `validate_package.py`：检查 marketplace、Hook helper、完整 Skill CLI、项目记忆文档、插件名/Skill 目录、版本一致性、frontmatter/agent 配置、Hook 事件、现存 Python AST、常见私有路径和疑似 secret；它仍是显式清单与启发式扫描，不能替代宿主安装 smoke test。
- `verify_core.py`：验证冻结示例五份核心文件和聚合 SHA-256。
- `audit_public_release.py`：检查当前 tracked 文本/符号链接/常见私有路径与凭证模式；非 `--worktree-only` 模式另查所有 refs 的 author/committer 邮箱，只允许配置的 no-reply 后缀、测试域名和精确的 GitHub `noreply@github.com`。它不扫描未跟踪文件或历史 blob 内容。

当前没有配置 formatter、lint、静态 type checker、覆盖率采集/阈值、性能基准、依赖漏洞扫描或 SAST。

## CI 检查

`.github/workflows/ci.yml` 配置在 push 和 pull request 上以 Linux、Windows、macOS × Python 3.9、3.13 的矩阵运行完整 `unittest`、`compileall`、插件包校验、冻结示例校验和发布审计。仓库文件本身不能证明远端最近一次 run 已通过；其中“历史”部分只检查提交邮箱。Workflow 仅有 `contents: read` 权限；第三方 Actions 使用主版本标签而非 commit SHA。

## 尚未覆盖的关键流程

- 在真实 Codex Desktop/CLI 中安装、信任 Hooks、隐式激活并调用原生子智能体的自动端到端测试；本机 `codex.exe` 帮助也未能执行。
- Stop Hook 的 stale snapshot、STATUS 缺失、非开发阶段和真实 Codex 宿主事件行为；通过、缺记录、伪造记录与递归保护已有测试。
- 专项命令绕过 `TRANSITIONS` 的阶段跳转，以及 adapter 对 current wave/依赖/merge order 不强制的路径。
- 协议要求但研究运行时未强制的证据字段，以及 22 份设计文档内容级完整性。
- Host Web Search 的真实网络研究、日期/来源更新和提供商故障。
- 0.4.0 的实际 GitHub 发布、插件目录安装和跨版本升级/回滚。
- Hook 无法观察的外部编辑器、进程和专用工具路径。
- 长时间或挂起的 Git 子进程；当前 `_run_git()` 没有 timeout。
- 系统性代码覆盖率、性能和大规模 requirements/worktree 压力测试。

## 质量风险与规则

- 示例项目复制了运行时源文件；本次审查确认 10 个项目运行时副本均与权威源 hash 一致，但发布流程需要持续防止漂移。
- Windows symlink 测试可能跳过；CI 的其他平台应提供补充覆盖。
- 启发式 secret/path 扫描有漏报和误报可能，不能替代宿主 secret scanning 和人工审查；当前发布脚本不覆盖未跟踪文件或历史内容对象。
- 生成模板已默认忽略 `last_test.json`、`guardrail.log` 和常见本地敏感/临时文件；既有项目或强制添加仍可能进入 Git。测试记录带流程性来源元数据，但不是对外部进程的密码学证明。
- 不允许为通过测试而删除/跳过测试、降低断言、放宽冻结/所有权校验或伪造 `last_test.json`。
- 行为变化必须增加回归测试；跨平台路径、Git 恢复和失败关闭逻辑至少需要一个正例和一个反例。

## 0.4 新增覆盖

新增回归覆盖四层初始化、具体验收、路径拒绝、依赖与唯一 ID、顺序单活动任务、reopen 原因、幂等 TASKS 投影、中英文提示词与不可信标题、并行显式上下文、命令安全、输出脱敏/上限、stale 快照、人工门禁、当前任务 CLI、未来 schema、非覆盖迁移和旧 runtime 兼容加载。Hook 覆盖纯记忆维护不强制全量测试、实质修改缺质量证据阻断、人工门禁禁止 AI 调用和旧 last_test 兼容。
