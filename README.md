# Idea-to-Build Codex Plugin

`idea-to-build` 是一个可安装的、skills-only 的 Codex Plugin：先验证数字产品想法和当前替代方案，再把用户决定继续推进的想法收敛为可验收需求、受 SHA-256 保护的核心契约，以及可直接交给多个 Codex 任务/工作树的开发包。

当前版本：`0.1.0`。运行时仅依赖 Python 3.9+ 标准库和 Git，不需要网络服务或密钥；实时方案研究由宿主提供的 Web Search 完成。

## 它解决什么问题

这个插件不是一次性 PRD 生成器。它实现一条带门禁的 16 阶段状态机：

`IDEA_RECEIVED → SEARCH_REQUIRED → SEARCH_IN_PROGRESS → SOLUTION_FOUND/BUILD_DECISION_REQUIRED → REQUIREMENTS_GATHERING → REQUIREMENTS_CONFLICT/REQUIREMENTS_READY → CORE_REVIEW → CORE_FROZEN → DOCUMENTS_GENERATED → CODEX_HANDOFF_READY → DEVELOPMENT_ACTIVE → CHANGE_REQUESTED/RELEASE_READY → ARCHIVED`

关键约束：

- 先研究、后详细访谈；无实时检索时只能输出 `INSUFFICIENT_RESEARCH`。
- 分三层检索直接产品、组合式替代方案、可复用开源/Skill/MCP/SDK/模板。
- 方案结论只能是七个枚举之一：`ADOPT_DIRECTLY`、`ADOPT_WITH_CONFIGURATION`、`COMBINE_EXISTING_TOOLS`、`EXTEND_OPEN_SOURCE`、`BUILD_CUSTOM`、`INSUFFICIENT_RESEARCH`、`NOT_RECOMMENDED`。
- 需求台账固定覆盖 38 类，区分 `confirmed`、`assumed`、`open`、`conflicting`、`deferred`、`out_of_scope`。
- 百分比不是就绪依据；P0 冲突、不可逆假设、隐私/安全/部署/验收缺失都会阻止冻结。
- 冻结必须由人类显式确认并亲自运行命令。AI 不得确认、冻结、解锁或重冻。
- 冻结后 `docs/core/**` 和 `.idea-to-build/core.lock.json` 永久只读于正常开发流程；变更进入 `docs/live/CHANGE_REQUESTS.md`。
- 多任务开发先计算依赖图和文件所有权，再给出一个精确的任务数；同时进行的任务不得有路径重叠。

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

manifest 故意不声明显式 `hooks` 字段，而使用官方默认发现位置 `hooks/hooks.json`；这样同时符合默认生命周期发现规则和当前官方 plugin validator。

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

## 安装

前置条件：

- Python 3.9 或更高版本；Windows 同时应能运行 `py -3`。
- Git 可执行文件可用，并已配置提交身份。
- 支持 Plugins 与 Hooks 的当前 ChatGPT/Codex 版本；组织策略可能限制安装或 hook 执行。

这个仓库本身就是一个本地 marketplace 根目录：`.agents/plugins/marketplace.json` 中的 `source.path` 为 `./`，指向仓库根部的 plugin manifest。

在仓库根目录执行：

```bash
codex plugin marketplace add .
codex plugin add idea-to-build@idea-to-build-local
codex plugin list --json
```

也可以在 ChatGPT 桌面端重启后打开 **Plugins**，选择 **Idea-to-Build Local** 来源并安装。修改插件源码后，重启桌面端或刷新对应 marketplace；若技能未出现，也请重启宿主。

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

在 ChatGPT Work 中，从技能选择器选择 Idea-to-Build（界面通常使用 `@` 选择）；在 Codex CLI/IDE 中输入 `$idea-to-build` 或从 `/skills` 选择。描述符合前置触发条件时也允许隐式调用。

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

### 4. 由人类确认和冻结

先让 Codex 起草五份核心文档并展示冻结预览。用户确认内容后，必须离开 AI 代执行流程，由人类在终端亲自运行：

```bash
python scripts/project_state.py confirm-core --path . --confirmation "I confirm and freeze the reviewed core baseline"
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

输出包括 21 份设计/质量/运维文档、`codex/HANDOFF.md` 和每个任务独立可理解的 `codex/prompts/*.md`。交接明确分支、工作树、文件所有权、依赖、启动/完成条件、测试和合并顺序。

## Hooks 行为

| 事件 | 行为 |
|---|---|
| `SessionStart` | 若当前目录是生成项目，校验并注入受大小限制的核心/live 上下文。 |
| `UserPromptSubmit` | 追加当前阶段、核心状态和必要约束；普通咨询保持安静。 |
| `PreToolUse` | 冻结前允许核心草稿编辑；冻结后阻止工具写核心/锁文件、路径穿越、重定向、移动、删除和 Git restore 等明显绕过方式。核心确认/冻结命令始终仅允许人类。 |
| `PostToolUse` | 冻结后重新计算哈希；发现漂移时记录 `.idea-to-build/guardrail.log` 并要求停止。 |
| `Stop` | 仅在实质开发阶段检查核心、最近测试与 STATUS；使用 `stop_hook_active` 避免递归循环。普通问答不被强行续跑。 |

Hooks 是纵深防御，不是操作系统安全边界。文件只读位、hash 校验、Git 历史和开发纪律共同构成保护链。

## 测试与校验

从 plugin 根目录运行：

```bash
python -m unittest discover -s tests -v
python -m compileall -q hooks skills/idea-to-build/scripts tests
python skills/idea-to-build/scripts/validate_package.py --path .
```

测试覆盖 30 个以上独立场景，包括：16 阶段合法/非法迁移、旧 schema 迁移和新 schema 拒绝；联网/离线/冲突研究；38 类需求与就绪门禁；人类确认、换行规范化、hash 漂移；所有 5 类 hook；正反激活；重叠工作流合并；3-8 个任务规划；项目初始化、完整冻结、文档生成、交接与包校验。

发布前还应运行已安装的官方校验器：

```text
quick_validate.py skills/idea-to-build
validate_plugin.py .
```

完整冻结示例见 [`examples/team-brief-generator`](examples/team-brief-generator/README.md)。其研究候选是刻意虚构的测试夹具，不代表当前市场事实。

## ChatGPT Work、桌面端与 CLI 兼容性

| 表面 | Skill/Plugin | 本地仓库与 hooks | 推荐用途 |
|---|---|---|---|
| ChatGPT Work Web | 可使用受支持的已安装 plugin/skill | 运行在托管环境，不能假设可访问本机项目、Git、只读位或本地 hook | 想法梳理、研究、协作式需求收集；本地冻结和开发交接转到桌面/Codex |
| ChatGPT Work Desktop（本地） | 支持 Plugins Directory 与本地 marketplace | 可访问获准的本地文件；hook 是否生效取决于所选本地 Codex/Work 能力、组织策略和信任 | 安装、交互式研究、需求评审、人工冻结检查 |
| Codex Desktop | 完整的本地 plugin/skill、Git、worktree 与 hook 流程 | 支持本地项目、审批、review、任务和工作树 | 推荐的端到端产品化与开发交接表面 |
| Codex CLI | `codex plugin`、`$skill`/`/skills`、`/hooks` | 支持本地 Git、脚本、hooks 与工作树 | 可复现测试、自动化和工程团队使用 |

独立 repo/user Skill 也可在 IDE 中发现，但本仓库的主要分发单元是 Plugin。具体可用性仍受版本、套餐、灰度和 workspace 管理策略影响。

## 卸载

```bash
codex plugin remove idea-to-build@idea-to-build-local
codex plugin marketplace remove idea-to-build-local
codex plugin list --json
```

这不会删除已经生成的产品项目。若安装来自桌面 Plugins Directory，也应在其中移除插件。个人或团队曾复制 marketplace/plugin 文件时，确认不再被其他插件使用后再手动删除对应副本。

## 故障排查

- **插件未出现**：确认 `codex plugin marketplace list --json` 能看到 `idea-to-build-local`，检查 `.agents/plugins/marketplace.json`，重启宿主。
- **Skill 不触发**：新建对话并显式使用 `$idea-to-build`；确认插件已启用，且请求不是 frontmatter 中的负面边界。
- **Hook 被跳过**：运行 `/hooks`，审查并信任当前 hash；检查 Python 命令和 `[features] hooks`。
- **Windows 找不到 Python**：确认 `py -3 --version` 可运行；非 Windows 应提供 `python3`。
- **研究停在 `INSUFFICIENT_RESEARCH`**：启用 Web Search，或提供带日期和官方 URL 的研究输入；不要手改成乐观结论。
- **需求检查返回 3**：读取 JSON 中 `blockers`；解决必填项、不可逆假设、P0 冲突和 build decision。
- **冻结失败**：确认 Git 身份、干净且可写的仓库、显式人类确认和就绪状态；失败信息不会被吞掉。
- **核心校验失败**：停止开发，保留证据，在 `docs/live/CHANGE_REQUESTS.md` 记录请求；不要更新 hash 掩盖漂移。
- **Stop hook 反复提醒**：完成最近测试记录和 STATUS 更新；hook 会识别 `stop_hook_active`，若仍重复请保存 hook 输入与 guardrail log 作为 bug 证据。

## 已知限制

- Pre/Post tool hooks 只能观察宿主实际发送的匹配事件；托管 Web Search、专用工具、外部编辑器、人类或其他进程可能绕过某些事件。
- 只读文件不是安全沙箱；有文件系统权限的进程仍可改回权限。SHA-256、Git 和审查用于发现而非绝对阻止所有外部修改。
- 当前研究评分是透明决策辅助，不是市场规模、产品安全或商业成功证明；价格、许可证和维护状态必须实时复核。
- hook 的命令解析采用保守启发式，可能阻止可疑但无害的复杂 shell 命令；可改用明确、窄范围的工具调用。
- 冻结提交依赖 Git 可用及身份配置；可选 tag 在 commit 成功后失败时会明确报错，需要人类处理 tag，不会伪装为完整成功。
- 自动生成的设计文档是基于冻结约束的骨架与证据标签，仍需各专业任务补充实现细节和验证证据。
- 当前 schema 版本为 1；旧版本可迁移，遇到更高版本会拒绝猜测性解释。

## 后续演进

优先方向包括：增加 marketplace CI 和跨平台 hook 实机矩阵；为研究输入定义公开 JSON Schema；加入真实浏览搜索回放夹具；提供受审计的人类 change-request/unlock 工具；增强 Git 失败事务恢复；加入性能/可访问性报告适配器；发布到通用 Plugins Directory 后再提供稳定的安装/分享链接。

## 许可证

MIT，见 [`LICENSE`](LICENSE)。