# 项目概览

## 项目解决的问题

Idea-to-Build 用于避免“产品想法尚未验证和结构化，就直接进入 AI 编码”造成的重复造轮子、需求缺失、核心约束漂移和并行开发失控。它先研究可复用方案，再通过需求门禁和人工确认冻结核心契约，随后用仓库内长期记忆、规范任务、质量门禁和 Codex 调度指导真实开发。

仓库没有用户研究或商业成效数据能够证明产品效果；目标用户、KPI 和支持承诺仍记录在 [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)。

## 目标用户与支持边界

- 使用 Codex Desktop 或 Codex CLI 规划并开发数字产品的个人或团队。
- 希望保留研究证据、需求决策、不可变产品边界和跨会话开发上下文的项目负责人。
- 需要默认按任务顺序开发，并只在独立工作确有收益时使用 Codex 子智能体和 Git worktree 的高级用户。

Plugin 只支持 Codex Desktop/CLI。它不承诺 OpenClaw、通用 SkillHub、Claude Code 或其他宿主兼容，也不提供数据库、认证、公共 HTTP API、MCP server 或托管后端。

## 已实现的核心能力

- 16 个阶段定义、手工转换图和各专项命令的前置条件；转换图不是所有命令的统一安全门禁。
- 三类方案研究、12 项加权评分、7 类唯一决策，以及 readiness 后的条件式 MCP 四选一指导。
- 固定 38 项需求台账、受保护元数据和严格 readiness 门禁。
- 五份核心契约的显式人类确认、SHA-256 冻结、精确 Git 根、提交和可选 tag。
- 四层仓库记忆：长期规则/地图、任务 SPEC/PLAN、任务状态台账/投影、质量门禁/结果，以及完整可恢复提示词。
- 规范任务状态、依赖、阻塞、重开、路径所有权、具体验收标准和当前任务上下文。
- 默认 `guided_sequential`；显式 `parallel_worktrees` 从规范任务台账生成依赖波次、子智能体提示词和 hash 绑定的 `codex/dispatch.json`。
- SessionStart、UserPromptSubmit、PreToolUse、PostToolUse、Stop 五类 Hook 的上下文注入和纵深防护。
- Python 标准库测试、三平台 CI、包校验、冻结示例和公开发布脱敏审计。

## 主要用户流程

1. 安装 Plugin，在新的 Codex 任务中调用 `$idea-to-build`。
2. 研究直接方案、组合方案和可复用基础，并记录证据与采用/扩展/自建决策。
3. 分轮完成 38 项需求；readiness 后仅在确有收益时评估 MCP。
4. Codex 起草五份核心契约，用户在 AI 工具调用之外确认并冻结。
5. 生成四层仓库记忆和第一个任务；在写代码前用 `memory_prompts.py` 恢复任务上下文。
6. 用 `task_state.py` 推进 draft、ready、in_progress、review、done；用 `quality_gate.py` 记录当前快照的命令门禁，由用户接受人工门禁。
7. 默认逐任务开发；只有显式选择高级并行模式且任务路径不重叠时，才生成子智能体/worktree 波次。
8. 审查 diff、验收和 commit，更新可变记忆；核心变化只进入 `docs/live/CHANGE_REQUESTS.md`。

## 当前成熟度与状态

- 当前源代码和公开文档版本为 `0.4.0`，位于本地 `main`；最新已知 tag 仍为 `v0.2.0`，0.4.0 尚未推送或打 tag。
- CI 配置覆盖 Linux、Windows、macOS 和 Python 3.9/3.13；本地验证覆盖单元、集成、Hook、迁移、工作树和端到端场景。
- 冻结示例保持原核心 hash，并新增四个规范任务和两波并行 dispatch。
- “alpha/beta/GA”等产品成熟度标签没有仓库证据，仍待人工确认。

## 已知限制

- 没有真实 Codex 宿主自动化端到端 CI，adapter 也没有独立 finalize 命令。
- Hook、状态、manifest hash 和本地质量记录是流程控制，不是沙箱、身份认证或签名 provenance。
- JSON 契约有版本检查但没有独立 JSON Schema；运行时副本仍可能漂移。
- 正式目标客户、KPI、0.4.0 发布渠道、最低 Codex 版本和远端安全设置仍待确认。

详细状态见 [`PROJECT_STATUS.md`](../PROJECT_STATUS.md)，架构见 [`ARCHITECTURE.md`](ARCHITECTURE.md)，记忆模型见 [`REPOSITORY_MEMORY.zh-CN.md`](REPOSITORY_MEMORY.zh-CN.md)。
