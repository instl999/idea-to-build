# Idea-to-Build Codex Plugin

[English](README.md) | **简体中文**

`idea-to-build` 是一个 Codex 专用、可安装、由 Skill 与生命周期 Hooks 组成且不包含 MCP server 的 Plugin：先验证数字产品想法和当前替代方案，再把用户决定继续推进的想法收敛为可验收需求、受 SHA-256 保护的核心契约，并按实际耦合度由 Codex 根智能体或原生子智能体/工作树完成开发。

开发中 manifest 版本：`0.3.0`；2026-08-06 本地与远端可确认的最近 Git tag 仍为 `v0.2.0`。本地运行时仅依赖 Python 3.9+ 标准库和 Git，不需要第三方 Python 包、API 密钥或插件自建网络服务；实时方案研究需要宿主提供的 Web Search 和网络访问。

## 它解决什么问题

这个插件不是一次性 PRD 生成器。它定义一条 16 阶段工作流；手工 `transition` 命令受转换图门禁约束，但若干专项命令通过各自检查直接更新阶段，因此当前并非单一、统一拦截的状态机：

`IDEA_RECEIVED → SEARCH_REQUIRED → SEARCH_IN_PROGRESS → SOLUTION_FOUND/BUILD_DECISION_REQUIRED → REQUIREMENTS_GATHERING → REQUIREMENTS_CONFLICT/REQUIREMENTS_READY → CORE_REVIEW → CORE_FROZEN → DOCUMENTS_GENERATED → CODEX_HANDOFF_READY → DEVELOPMENT_ACTIVE → CHANGE_REQUESTED/RELEASE_READY → ARCHIVED`

关键约束：

- 先研究、后详细访谈；无实时检索时只能输出 `INSUFFICIENT_RESEARCH`。联网时，运行时仍未强制研究协议要求的全部证据字段。
- 分三层检索直接产品、组合式替代方案、可复用开源/Skill/MCP/SDK/模板。
- 方案结论只能是七个枚举之一：`ADOPT_DIRECTLY`、`ADOPT_WITH_CONFIGURATION`、`COMBINE_EXISTING_TOOLS`、`EXTEND_OPEN_SOURCE`、`BUILD_CUSTOM`、`INSUFFICIENT_RESEARCH`、`NOT_RECOMMENDED`。
- 需求台账固定覆盖 38 类，区分 `confirmed`、`assumed`、`open`、`conflicting`、`deferred`、`out_of_scope`。
- 百分比不是就绪依据；P0 冲突、不可逆假设、隐私/安全/部署/验收缺失都会阻止冻结。
- 仅在 readiness 通过后评估 MCP：四选一记录“不适用/使用现有 server/自建 server/延后”，优先直接集成或已维护的现有 server，绝不替用户安装或配置。
- 冻结必须由人类显式确认并亲自运行命令。AI 不得确认、冻结、解锁或重冻。
- 冻结后 `docs/core/**` 和 `.idea-to-build/core.lock.json` 永久只读于正常开发流程；变更进入 `docs/live/CHANGE_REQUESTS.md`。
- 先判断子智能体是否真的有价值：只有一个有效或高耦合工作流时由根智能体直接开发；存在两个以上互不重叠的独立工作流时，才生成子智能体提示词、依赖波次、分支、工作树和合并顺序。
- 核心冻结后，用户要求继续开发即启动 Codex 运行期编排；只有计划确实建议时才使用原生子智能体，任何子任务提交都必须验证后才能合并。

## 官方规范基线

实现于 2026-08-05 重新核对以下官方规范：

- [Plugin 打包、manifest、local marketplace 与生命周期 hooks](https://developers.openai.com/plugins/build/plugins)
- [Skill 结构、渐进披露、显式/隐式调用和 `agents/openai.yaml`](https://developers.openai.com/plugins/build/skills)
- [Codex Hooks 事件、信任、JSON I/O 与 `commandWindows`](https://learn.chatgpt.com/docs/hooks)
- [`AGENTS.md` 的目录作用域](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Subagents 的上下文、并行边界和输出汇总](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Git worktrees 的隔离与交接](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Web Search 的实时性与缓存语义](https://learn.chatgpt.com/docs/web-search)
- [Codex ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans)

manifest 故意不声明显式 `hooks` 字段，而使用文档约定的默认发现位置 `hooks/hooks.json`；该布局也通过仓库当前的 package validator。

## 目录结构

```text
idea-to-build/
├── .agents/plugins/marketplace.json     # 仓库即本地 marketplace
├── .codex-plugin/plugin.json            # Plugin manifest
├── hooks/                               # 5 个生命周期事件及公共保护逻辑
├── skills/idea-to-build/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/                      # 工作流、研究、就绪、文档、Git、安全规范
│   ├── assets/project-template/         # 可生成项目模板
│   └── scripts/                         # 确定性状态、校验、冻结、交接工具
├── examples/team-brief-generator/       # 完整冻结示例
└── tests/                               # 单元、hook、激活、包校验和端到端场景
```

生成项目包含 `AGENTS.md`、5 份核心文档、8 份 live 文档、ExecPlan 目录、Codex handoff/提示目录、状态/需求台账，以及全部项目侧运行脚本。

生成设计集还包含条件式 `MCP_INTEGRATION_GUIDE.md`，用于记录“不适用/使用现有/自建/延后”之一，而不是默认引入 MCP server。

## 安装

从 GitHub 获取源码：

```bash
git clone https://github.com/instl999/idea-to-build.git
cd idea-to-build
```

前置条件：

- Python 3.9 或更高版本；Windows 同时应能运行 `py -3`。
- Git 可执行文件可用，并已配置提交身份。
- 支持 Plugins、Hooks、原生子智能体和 Git 工作树的当前 Codex Desktop/CLI；组织策略可能限制部分能力。

这个仓库本身就是一个本地 marketplace 根目录：`.agents/plugins/marketplace.json` 中的 `source.path` 为 `./`，指向仓库根部的 plugin manifest。

在仓库根目录执行：

```bash
codex plugin marketplace add .
codex plugin marketplace list
```

也可以在 Codex Desktop 重启后打开 **Plugins**，选择 **Idea-to-Build Local** 来源并安装。更新插件时先 `git pull`，再移除并重新添加插件；版本或 Hook 哈希变化后重新审查信任，并在新任务中使用更新后的 Skill。若技能未出现，请重启宿主。

### Hook 信任与启用

安装后在新的 Codex 对话中输入 `/hooks`：

1. 核对 hook 来源是这个插件的 `hooks/hooks.json`。
2. 审查命令及哈希后选择信任。
3. 确认 `SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`Stop` 均启用。

非托管命令 hook 在被信任前会被跳过；源码变化会改变 hash，需重新审查。若配置中有 `[features] hooks = false`，应先恢复启用。不要用绕过信任的启动参数作为日常方案。

## 调用

最可靠的方式是显式调用：

```text
$idea-to-build 我想做一个本地优先的工具，把会议记录转换成可追溯的团队简报。请先检索现成方案；若值得继续，再把它整理成可开发、可验收的 Codex 项目。
```

在 Codex Desktop/CLI 中输入 `$idea-to-build` 或从 `/skills` 选择；描述符合前置触发条件时也允许隐式调用。

以下请求不应激活：窄范围 bug 修复、代码解释、已经定义清楚的小功能、普通软件推荐、无验证/开发意图的随意头脑风暴、非数字产品问题。

## 从想法到开发包

### 1. 初始化项目

插件在用户需要持久化产物时运行：

```bash
python skills/idea-to-build/scripts/init_project.py --path ../my-product --name "My Product"
```

默认初始化 Git 并创建骨架提交。`--skip-initial-commit` 仅用于 CI/夹具，普通工作流不要使用。

进入生成项目后，项目脚本均可从根目录运行：

```bash
python scripts/project_state.py status --path .
python scripts/verify_core.py --path .
python scripts/validate_package.py
```

### 2. 记录研究与决策

Web Search 必须覆盖三层方案并保存查询日期、官方 URL、证据、推理、冲突和可能过时字段。将结构化输入交给：

```bash
python scripts/research_report.py --path . --input research-input.json
python scripts/project_state.py set-decision --path . --build BUILD_CUSTOM
```

如果网络不可用或证据冲突，报告会停在 `INSUFFICIENT_RESEARCH`，不会把“没搜到”包装成市场空白。

### 3. 更新需求并检查就绪

```bash
python scripts/project_state.py update-requirements --path . --input requirements-updates.json
python scripts/requirements_check.py --path . --update-state
```

就绪门禁要求关键 P0 项为用户确认、不可逆项不是假设、无 P0 冲突、且已有 configure/combine/extend/build 决策。

### 冻结前的条件式 MCP 评估

readiness 通过后，只有在已确认的 AI/agent 客户端确实需要外部工具或资源、目标宿主当前支持 MCP，且 MCP 相比直接 API、SDK、Skill、CLI 或应用内模块具有实质优势时，Skill 才建议采用。结论必须是 `MCP_NOT_APPLICABLE`、`MCP_USE_EXISTING_SERVER`、`MCP_BUILD_CUSTOM_SERVER` 或 `MCP_DEFER` 之一。

若采用 MCP，指导必须覆盖当前官方来源核验、能力映射、最小权限认证与凭据、宿主/transport 假设、由用户亲自执行的安装步骤、合成与负向测试、可观测性、禁用/回滚和非 MCP 退路。影响系统边界的结论在冻结前进入 `ARCHITECTURE_CONTRACT.md`；实现细节保留在 `docs/design/MCP_INTEGRATION_GUIDE.md`。

### 4. 由人类确认和冻结

先让 Codex 起草五份核心文档并展示冻结预览。用户确认内容后，必须离开 AI 代执行流程，由人类在终端亲自运行：

```bash
python scripts/project_state.py confirm-core --path . --confirmation "I confirm and freeze this core baseline"
python scripts/freeze_core.py --path . --tag core-v1
```

冻结会规范化换行后计算每个文件与聚合 SHA-256、写入锁文件、更新状态、设只读位，并创建专用 Git commit。tag 可省略。冻结后不要让任何 AI “顺手更新锁”；通过 change request 评审产品基线变更。

### 5. 生成交接

可把自定义工作流数组传给 `--workstreams`；如果省略，生成器使用状态中的工作流或最小默认值：

```bash
python scripts/generate_handoff.py --path . --workstreams workstreams.json
python scripts/render_context.py --path .
python scripts/verify_core.py --path .
```

输出包括 22 份设计/质量/运维文档、`codex/HANDOFF.md` 和每个任务独立可理解的 `codex/prompts/*.md`。交接明确分支、工作树、文件所有权、依赖、启动/完成条件、测试和合并顺序。

### 6. 按需指导实际开发

`generate_handoff.py` 总会生成根智能体提示词和 `codex/dispatch.json`。它先合并所有权重叠的工作流，再选择执行方式：

- `SINGLE_AGENT`：只有一个有效或高耦合工作流。直接在当前集成工作树中遵循 `codex/prompts/00-*.md`，不引入子智能体协调成本。
- `SUBAGENTS`：存在两个以上互不重叠的独立工作流。交接文档会说明为什么值得并行，并为每项任务给出独立可读的提示词、文件所有权、依赖波次、分支、工作树、测试和合并顺序。

核心冻结后，当用户要求 Codex 继续实际开发时，Skill 会直接执行该计划：`SINGLE_AGENT` 模式留在根任务中；`SUBAGENTS` 模式使用 Codex 原生协作工具，并由适配器准备和验证执行：

```bash
python scripts/codex_dispatch.py preview --path . --max-parallel 3
python scripts/codex_dispatch.py start --path . --max-parallel 3
python scripts/codex_dispatch.py materialize-wave --path . --wave 1 --base-commit <完整HEAD>
python scripts/codex_dispatch.py verify-result --path . --task-id <任务ID> --commit <完整提交> --base-commit <完整波次基线>
python scripts/codex_dispatch.py merge-result --path . --task-id <任务ID> --commit <完整提交> --base-commit <完整波次基线>
python scripts/codex_dispatch.py retire-wave --path . --wave 1
```

Python 适配器负责门禁、Git 工作树、提示词 hash 绑定和结果验证；Skill 直接调用 Codex 原生 `spawn_agent`/`wait_agent`。生成提示词同时作为可审计记录和人工接管入口。本版本不定位或测试为 OpenClaw、通用 SkillHub、Claude Code 或跨宿主 Skill。

## Hooks 行为

| 事件 | 行为 |
|---|---|
| `SessionStart` | 若当前目录是生成项目，校验并注入受大小限制的核心/live 上下文。 |
| `UserPromptSubmit` | 追加当前阶段、核心状态和必要约束；普通咨询保持安静。 |
| `PreToolUse` | 冻结前允许核心草稿编辑；冻结后阻止工具写核心/锁文件、路径穿越、重定向、移动、删除和 Git restore 等明显绕过方式。核心确认/冻结命令始终仅允许人类。 |
| `PostToolUse` | 冻结后重新计算哈希；发现漂移时记录 `.idea-to-build/guardrail.log` 并要求停止。 |
| `Stop` | 仅在实质开发阶段检查核心、实际执行且绑定当前 Git/工作树快照的最近测试记录与 STATUS；使用 `stop_hook_active` 避免递归循环。普通问答不被强行续跑。 |

Hooks 是纵深防御，不是操作系统安全边界。文件只读位、hash 校验、Git 历史和开发纪律共同构成保护链。

## 测试与校验

从 plugin 根目录运行：

```bash
python -m unittest discover -s tests -v
python -m compileall -q hooks skills/idea-to-build/scripts tests
python skills/idea-to-build/scripts/validate_package.py --path .
```

当前测试覆盖 91 个独立场景，包括：代表性的合法/非法手工状态转换、旧 schema 迁移和新 schema 拒绝；联网/离线/冲突研究；38 类需求、就绪门禁及 readiness 后的 MCP 协议/指南；人类确认、换行规范化、hash 漂移；实际执行五类 Hook，并覆盖 Stop 的通过、缺记录、伪造记录和递归保护路径；以及激活、工作流合并、任务规划、初始化、冻结、文档生成、交接与包校验。最近本地运行 90 项通过，1 项因 Windows 目录 symlink 能力不可用而跳过。

仓库内的 `validate_package.py` 会检查 marketplace、Hook helper、完整 Skill CLI、项目记忆文档和版本一致性；它仍是源码包校验，不能替代 Codex 宿主安装 smoke test。发布时还应按本仓库使用的官方 `plugin-creator` 与 `skill-creator` 校验器运行检查。

完整冻结示例见 [`examples/team-brief-generator`](examples/team-brief-generator/README.md)。其研究候选是刻意虚构的测试夹具，不代表当前市场事实。

## Codex 专用支持边界

本插件只面向 Codex Desktop 和 Codex CLI。端到端契约依赖 Codex Plugins、生命周期 Hooks、原生协作工具、本地 Git 和同级工作树。宿主版本、灰度、套餐、工作区策略、可用协作槽位和 Hook 信任都可能限制执行。

OpenClaw、通用 SkillHub 运行时、ChatGPT 托管 Web、Claude Code 和其他智能体宿主不在支持边界内。其他环境也许能读取 Markdown 提示词，但这不表示适配器可以安装、安全运行或保持相同行为。
## 卸载

先在 Desktop Plugins Directory 中卸载插件；若不再需要本地 marketplace 来源，再运行：

```bash
codex plugin marketplace remove idea-to-build-local
codex plugin marketplace list
```

这不会删除已经生成的产品项目。若安装来自桌面 Plugins Directory，也应在其中移除插件。个人或团队曾复制 marketplace/plugin 文件时，确认不再被其他插件使用后再手动删除对应副本。

## 故障排查

- **插件未出现**：确认 `codex plugin marketplace list` 能看到 `idea-to-build-local`，检查 `.agents/plugins/marketplace.json`，重启宿主。
- **Skill 不触发**：新建对话并显式使用 `$idea-to-build`；确认插件已启用，且请求不是 frontmatter 中的负面边界。
- **Hook 被跳过**：运行 `/hooks`，审查并信任当前 hash；检查 Python 命令和 `[features] hooks`。
- **Windows 找不到 Python**：确认 `py -3 --version` 可运行；非 Windows 应提供 `python3`。
- **研究停在 `INSUFFICIENT_RESEARCH`**：启用 Web Search，或提供带日期和官方 URL 的研究输入；不要手改成乐观结论。
- **需求检查返回 3**：读取 JSON 中 `blockers`；解决必填项、不可逆假设、P0 冲突和 build decision。
- **冻结失败**：确认 Git 身份、干净且可写的仓库、显式人类确认和就绪状态；失败信息不会被吞掉。
- **核心校验失败**：停止开发，保留证据，在 `docs/live/CHANGE_REQUESTS.md` 记录请求；不要更新 hash 掩盖漂移。
- **Stop hook 反复提醒**：先在 `project_state.json` 声明精确 `test_commands`，再运行 `python scripts/project_state.py record-test --path . --test-command "<完全一致的命令>"`；该命令会真实执行测试并绑定当前 Git/工作树快照，但不会更新 STATUS；Hook 会校验项目 ID、recorder 标记、声明命令和当前 Git 快照，并阻止可观察的直接写入，但外部进程仍可伪造普通 JSON，因此不是密码学执行证明。hook 会识别 `stop_hook_active`，若仍重复请保存 hook 输入与 guardrail log 作为 bug 证据。

## 进一步文档

- [架构](docs/ARCHITECTURE.zh-CN.md)
- [隐私与数据处理](docs/PRIVACY.zh-CN.md)
- [核心变更控制](docs/CHANGE_CONTROL.zh-CN.md)
- [安全策略](SECURITY.zh-CN.md)
- [贡献指南](CONTRIBUTING.zh-CN.md)

## 已知限制

- Pre/Post tool hooks 只能观察宿主实际发送的匹配事件；托管 Web Search、专用工具、外部编辑器、人类或其他进程可能绕过某些事件。
- 只读文件不是安全沙箱；有文件系统权限的进程仍可改回权限。SHA-256、Git 和审查用于发现而非绝对阻止所有外部修改。
- 当前研究评分是透明决策辅助，不是市场规模、产品安全或商业成功证明；价格、许可证和维护状态必须实时复核。
- hook 的命令解析采用保守启发式，可能阻止可疑但无害的复杂 shell 命令；可改用明确、窄范围的工具调用。
- 冻结提交依赖 Git 可用及身份配置；可选 tag 在 commit 成功后失败时会明确报错，需要人类处理 tag，不会伪装为完整成功。
- 自动生成的设计文档是基于冻结约束的骨架与证据标签，仍需各专业任务补充实现细节和验证证据。
- 当前 schema 版本为 1；旧版本可迁移，遇到更高版本会拒绝猜测性解释。

## 后续演进

优先方向包括：增加 marketplace CI 和跨平台 hook 实机矩阵；为研究输入定义公开 JSON Schema；加入真实浏览搜索回放夹具；提供受审计的人类 change-request/unlock 工具；继续扩充 Git/tag 部分成功后的恢复指导；加入性能/可访问性报告适配器；发布到 Codex Plugins Directory 后再提供稳定的安装/分享链接。

## 许可证

MIT，见 [`LICENSE`](LICENSE)。