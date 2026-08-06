# 项目概览

## 项目解决的问题

Idea-to-Build 旨在降低“产品想法尚未验证和结构化就进入 AI 编码”带来的重复造轮子、需求缺失、核心约束漂移和并行开发失控风险。仓库实现了先研究现成方案、再经过需求门禁、人工确认的核心契约和 Codex 调度生成开发项目包的流程；仓库没有用户研究或成效数据证明这些结果已经实现。产品定位证据：`README.md`、`skills/idea-to-build/SKILL.md`、`skills/idea-to-build/references/workflow.md`。

## 目标用户

- 使用 Codex Desktop 或 Codex CLI 规划并开发数字产品的人。
- 希望在 AI 编码前保留研究证据、需求决策和不可变产品边界的个人或团队。
- 需要在独立工作流之间使用 Codex 子智能体和 Git worktree，同时限制写入范围的项目负责人。

更具体的商业用户画像、付费意愿和组织规模无法从代码确认，见 [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)。

## 已实现的核心能力

- 16 个阶段定义和由 `TRANSITIONS` 约束的手工 `transition` 接口；若干专项命令直接写阶段并依赖各自前置条件，当前并非统一状态机门禁。
- 三类方案研究协议、12 项加权评分和 7 种唯一决策结果；离线、冲突或无候选时失败关闭，但运行时没有强制协议列出的全部研究证据字段。
- 固定 38 项需求台账、受保护元数据和 readiness 门禁。
- 五份核心契约的显式人类确认、SHA-256 冻结、精确 Git 根和提交/tag 支持。
- 22 份设计骨架（含条件式 MCP 集成指南）、Codex handoff、提示词和 hash 绑定的 `codex/dispatch.json` 生成。
- 根据文件所有权和耦合度选择根智能体或 Codex 子智能体；对子任务使用依赖波次、同级 worktree、分支 tip/祖先/所有权验证和冲突自动中止。
- SessionStart、UserPromptSubmit、PreToolUse、PostToolUse、Stop 五类 Hook 的上下文注入和纵深防护。
- 跨平台测试、包校验、冻结示例校验和启发式发布脱敏审计。

## 主要用户流程

1. 安装插件并在新 Codex 任务中调用 `$idea-to-build`。
2. 在宿主 Web Search 中研究直接方案、组合方案和可复用基础，并保存证据。
3. 记录 build/adopt 决策，分轮完成 38 项需求台账。
   readiness 通过后、核心冻结前，Skill 在“不适用/使用现有 MCP server/自建/延后”中记录一个有证据的结论；证据不足不默认引入 server。
4. readiness 通过后，由 Codex 起草并展示五份核心契约；人类在 AI 工具调用之外确认和冻结。
5. 生成设计文档与 Codex handoff。单工作流留在根任务；多个互不重叠工作流按依赖波次进入子智能体 worktree。
6. 校验子任务 commit、审查 diff、受控合并并重新验证核心和测试；发布状态和波次完成目前需要宿主/人工流程记录，代码没有 dispatch finalize。

## 当前成熟度与状态

- 本地 Git 有五个提交；`v0.2.0` 指向 `main`，当前分支 `codex/codex-orchestrator-adapter` 在其上增加 0.3.0 调度能力。
- `.codex-plugin/plugin.json`、`pyproject.toml`、README 和 `CHANGELOG.md` 已统一声明 `0.3.0`；最近确认的 Git tag 仍是 `v0.2.0`。
- CI 配置覆盖三个操作系统和 Python 3.9/3.13；测试目录包含单元、集成、Hook 和端到端场景。
- “alpha/beta/GA”等产品成熟度标签没有仓库证据，待确认。

## 当前明确不属于项目的功能

- Plugin 自身不提供或托管 MCP server、数据库、账号认证、遥测或网络 endpoint；它只对生成产品提供条件式 MCP 架构指导。
- 不以 OpenClaw、通用 SkillHub、Claude Code、ChatGPT 托管 Web 或其他宿主为受支持运行时。
- 不替代人工产品决策、安全评审、测试、代码审查和 Git 恢复。
- 不把搜索分数当作市场规模、产品安全或商业成功证明。
- 不允许 AI 代替人类确认/冻结核心或静默重写冻结基线。

## 待确认的产品信息

- 正式目标客户、成功指标、定价/商业模式和支持承诺。
- 0.3.0 是否已作为正式 GitHub/插件目录版本发布。
- 是否计划恢复 SkillHub/OpenClaw 兼容，或永久维持 Codex-only 边界。
