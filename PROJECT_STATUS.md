# 项目状态

更新时间：2026-08-06（Asia/Shanghai）
代码基线：本地 `main`；远端发布状态见下文

## 当前阶段

仓库处于 0.3.0 Codex 原生开发编排、条件式 MCP 指导与本轮可靠性改进已合并本地 `main` 后的发布准备阶段。`origin/main` 与已确认 tag 仍停留在 `v0.2.0` 对应基线；2026-08-06 的只读 `git ls-remote --heads --tags origin` 仍只显示 `main` 和 `v0.2.0`，是否另有 Plugins Directory 发布无法从仓库确认。

## 已实现的主要功能

- Codex Plugin、单 Skill、五类生命周期 Hooks 和仓库本地 marketplace。
- 16 个阶段定义、手工转换图、方案研究和 7 类决策；专项命令尚未统一通过转换图。
- 固定 38 项需求台账及严格 readiness 门禁。
- readiness 通过后的条件式 MCP 评估、四选一推荐、现有/自建 server 安全指导和生成的 `MCP_INTEGRATION_GUIDE.md`；Plugin 自身仍无 MCP server。
- 五份核心契约的人类确认、SHA-256 冻结、精确 Git 根、提交和可选 tag。
- 22 份设计骨架、live 文档模板、Codex handoff、自包含 prompt 和 dispatch manifest。
- 单根智能体/多子智能体按需规划、依赖波次、同级 worktree、结果所有权验证和受控 merge。
- Python 标准库测试、三平台 CI 配置、包校验、冻结示例和公开发布脱敏审计。
- 英文/中文 README、安全、隐私、架构、变更控制和贡献说明。

## 部分实现的功能

- Host 集成：五类 Hook 和子智能体协议的主要路径已由 Python 模拟测试；仍没有真实 Codex 宿主自动端到端 CI。
- 发布流程：已有检查清单和 CI，但没有自动发布、签名、provenance 或 0.3.0 tag。
- schema 演进：能补部分旧字段、拒绝未来版本，但字段校验不完整，也没有独立 schema 和升级/降级工具。
- 可观测性：有本地 guardrail/test 记录，没有集中日志、指标或告警。

## 明显未实现的功能

- `codex_dispatch_status=COMPLETE` 的 finalize 命令和自动进入 `RELEASE_READY` 的门禁。
- adapter 级的当前 wave、依赖已合并和 merge order 持久化/强制门禁；目前主要依赖宿主协议。
- lint、format、静态 typecheck、覆盖率和性能基准。
- OpenClaw、通用 SkillHub、Claude Code 等跨宿主适配；当前明确不支持。
- Plugin 自营的数据库、认证、公共 HTTP API、MCP server、托管后端和遥测；这些仍是当前非目标。

## 当前进行中的工作

2026-08-06 已完成整体代码审查与改进：统一 0.3.0 版本并兼容官方 cachebuster token、补全 Plugin/生成项目必需文件校验、为生成项目加入本地忽略规则、强化测试记录的流程性来源校验，并覆盖 Stop Hook 成功/拒绝路径。完整 91 项测试中 90 项通过、1 项因 Windows symlink 能力跳过。

## 阻塞项

- 正式发布 0.3.0 前仍需确认 tag、远端 push/发布渠道与 Plugins Directory 状态；本地版本元数据已统一。
- 真实 Codex 宿主兼容性、最低版本和发布 smoke test 尚待确认。

## 已知问题和技术债务摘要

- Hook 是纵深防御而非沙箱；外部进程仍可绕过。
- 运行时在源、示例和用户生成项目中存在复制件，可能漂移。
- Git 子进程无统一 timeout。
- JSON 契约无独立 schema。
- `last_test.json` 已有 project/runner/command/snapshot 校验和 Hook 可见写保护，但外部进程仍可伪造普通 JSON。
- 研究证据字段和阶段转换的运行时校验仍不完整；package 显式必需文件已补全，但内容级完整性仍有限。
- MCP 推荐目前由 Skill 协议和人审保证，没有 state/ledger 字段或运行时命令证明真实会话完成了四选一判断。
- 发布审计与 package secret 检查都是启发式。
- CI Actions 使用主版本 tag 而非 commit SHA。

详见 [`docs/KNOWN_ISSUES_AND_TECH_DEBT.md`](docs/KNOWN_ISSUES_AND_TECH_DEBT.md)。

## 推荐下一步

1. 人工回答 [`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md) 中的发布版本、Codex 最低版本、调度完成/波次强制语义和旧 SkillHub 处置问题。
2. 决定测试门禁是否需要签名/宿主回执等强于当前流程性 provenance 的证明。
3. 统一阶段转换与研究输入 schema，并补 Stop Hook 的 stale/STATUS/非开发阶段测试。
4. 决定 0.3.0 的 tag、push、Plugins Directory 与升级/回滚策略。
5. 建立真实 Codex 安装/Hook/子智能体 smoke test 清单或受控集成测试。

## 最近的重要变化

- `3a5edd0`：加入 Codex 原生开发编排、hash 绑定 dispatch manifest、worktree/commit 验证和 Codex-only 定位。
- 2026-08-06 本轮审查：合并 readiness 后 MCP 四选一指导，并修复版本漂移、包完整性、生成项目忽略规则与 Stop 测试证据门禁；没有改变阶段/schema/38 项台账或新增依赖。
- `5f1ad20`（`v0.2.0`）：强化 Hook/路径/Git/readiness/测试记录和双语公开文档。
- `e699cb7`：加入仓库本地 marketplace 和使用指南。
- `fd8361f`：加入 guardrail 测试和冻结示例。
- `3b7a479`：初始工作流脚手架。

## 仍待确认的文档项

重点包括正式目标用户/KPI、0.3.0 发布状态、调度完成规则、最低 Codex 版本、数据保留、团队确认权限、远端安全配置和旧 SkillHub 发布物处置。
