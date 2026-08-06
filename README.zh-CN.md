# Idea-to-Build Codex Plugin

[English](README.md) | **简体中文**

Idea-to-Build 是一个面向 Codex Desktop/CLI 的 Plugin，用来把数字产品想法转化为经过研究、用户确认、冻结且可测试的开发项目。它由一个 Skill、五类生命周期 Hook、Python 3.9+ 标准库 CLI 和 Git 组成；没有 MCP server、数据库、第三方 Python 运行时依赖或 Plugin 自建网络服务。

`0.4.0` 新增“四层仓库内项目记忆”和逐任务 Codex 开发指导。默认一次只处理一个任务：一个任务、一份 SPEC、一条分支、一个 Codex 对话。只有明确准备好且真正独立的任务，才使用 Codex 原生子智能体和 Git worktree。

## 保留的核心能力

Plugin 仍然先研究现有方案，再深入收集需求；保留七种研究决策、严格的 38 项需求台账、五份核心契约、人工确认与冻结、SHA-256 核心锁、冻结后禁止 AI 修改，以及通过 `docs/live/CHANGE_REQUESTS.md` 处理核心变更的流程。

Hook 始终加载已安装 Plugin 中的可信 runtime。仅仅打开生成项目，不会让 Hook 导入项目内可被篡改的 Python 副本。

## 四层项目记忆

| 层级 | 单一事实来源 | 人类视图 | 作用 |
| --- | --- | --- | --- |
| 规则层 | `AGENTS.md`、冻结的 `docs/core/**`、可变的 `docs/live/WORKING_RULES.md` | `docs/live/MEMORY_MAP.md` | Codex 必须如何工作，哪些约束不可改变 |
| 规格层 | `specs/<TASK-ID>/SPEC.md` 和 `PLAN.md` | 同一个任务目录 | 当前任务要交付什么、如何实现、如何验收 |
| 任务层 | `.idea-to-build/tasks.json` | `docs/live/TASKS.md`，以及简洁的 `STATUS.md`、`BACKLOG.md`、`ROADMAP.md` | 精确任务状态、依赖、所有权、分支/worktree 和下一步 |
| 质量层 | `.idea-to-build/quality_gates.json` 与被忽略的 `last_quality.json` | `docs/live/QUALITY_GATES.md` | 绑定当前 Git/worktree 快照的命令门禁和人工验收门禁 |

冲突优先级是：

`冻结核心 > 当前任务 SPEC > 工作规则 > 任务状态和 PLAN > 代码与测试证据 > 聊天中的临时描述`

仓库记忆能提高上下文恢复能力，但不是无限记忆；自动化检查能提高可靠性，但不能证明所有产品行为绝对正确。无法自动验证的内容必须保留为人工验收，不能伪装成自动测试。

## 环境要求

- Python 3.9 或更高版本（Windows 可用 `py -3`）。
- 已配置提交身份的 Git。
- 组织策略允许启用 Plugins 和 Hooks 的 Codex Desktop 或 Codex CLI。
- 只有进行实时方案研究时才需要 Web Search。

## 安装

```bash
git clone https://github.com/instl999/idea-to-build.git
cd idea-to-build
codex plugin marketplace add .
codex plugin add idea-to-build@idea-to-build-local
codex plugin marketplace list
```

如果 Plugin 没有出现，请重启 Codex。打开一个新的 Codex 任务，查看 `/hooks`，确认来源是本 Plugin 的 `hooks/hooks.json`，审查并信任对应 hash。建议显式调用：

```text
$idea-to-build 我想做一个本地优先的工具，把会议记录变成可追溯的团队简报。先研究现有方案；如果值得开发，再建立可测试的开发项目。
```

本 Skill 适合仍需研究、需求澄清或开发打包的软件/数字产品想法；不应因狭窄 bug 修复、代码解释、已经明确的小功能、泛软件推荐或非数字产品而触发。

## 从安装到第一个 Codex 开发任务

1. 初始化生成项目：

   ```bash
   python skills/idea-to-build/scripts/init_project.py --path ../my-product --name "My Product" --language zh-CN
   cd ../my-product
   ```

2. 使用 Skill 做带日期和来源的实时研究，再用生成项目中的 CLI 记录研究输入和开发决策。没有网络、证据冲突或候选为空时，必须得到 `INSUFFICIENT_RESEARCH`，不能凭空宣称市场空白。

3. 填完严格的 38 项台账并检查就绪状态：

   ```bash
   python scripts/project_state.py update-requirements --path . --input requirements-updates.json
   python scripts/requirements_check.py --path . --update-state
   ```

4. 审查 `docs/core/` 下五个文件，然后离开 AI 工具调用流程，由你亲自在终端运行：

   ```bash
   python scripts/project_state.py confirm-core --path . --confirmation "我确认并冻结此核心基线"
   python scripts/freeze_core.py --path . --tag core-v1
   ```

5. 创建或审查任务。新任务从 `backlog` 开始；先把 SPEC 里的占位验收项改成至少一个具体、可观察结果，才能进入 `ready`：

   ```bash
   python scripts/task_state.py create --path . --task TASK-0001 --title "第一个已确认功能" --owned-path src/feature
   python scripts/task_state.py ready --path . --task TASK-0001
   python scripts/task_state.py list --path .
   ```

6. 打印完整启动提示词：

   ```bash
   python scripts/memory_prompts.py show --path . --kind start-task --task TASK-0001
   ```

7. 复制第二条命令的全部输出，在项目根目录打开一个新的 Codex 对话并完整粘贴。等 Codex 复述目标、范围内外、不可变约束、验收条件、可写路径和检查命令之后，再允许它编码。不要只输入“继续开发”。

## 日常“一任务一对话”流程

```bash
python scripts/task_state.py list --path .
python scripts/memory_prompts.py show --path . --kind start-task --task TASK-0001
python scripts/task_state.py start --path . --task TASK-0001
```

同一任务内的小修复、测试和文档继续使用当前对话。任务 ID 改变、切换到独立模块、合并其他分支、上下文被压缩或开始混淆、所有权改变，或从实现切换到独立质量审查时，再开新对话。

收尾时运行：

```bash
python scripts/memory_prompts.py show --path . --kind finish-task --task TASK-0001
python scripts/quality_gate.py run --path .
python scripts/task_state.py review --path . --task TASK-0001
```

`quality_gate.py run` 使用当前任务，并运行全部已配置命令门禁。也可以显式选择：

```bash
python scripts/quality_gate.py status --path . --task TASK-0001
python scripts/quality_gate.py run --path . --task TASK-0001 --gate unit-tests
```

人工门禁只能由用户在 AI 工具调用流程之外的终端完成：

```bash
python scripts/quality_gate.py accept-manual --path . --task TASK-0001 --gate user-acceptance --confirmation "我确认接受此任务结果"
python scripts/task_state.py complete --path . --task TASK-0001
```

没有 SPEC/PLAN 和具体验收条件的任务不能进入 `ready`；依赖或阻塞项未完成时不能开始；只有当前快照上的全部必需命令门禁通过、且全部必需人工门禁由用户确认后，才能进入 `done`。重新打开 `done` 必须记录原因。

## 两种开发模式

`guided_sequential` 是默认模式，适合普通用户：一次只有一个进行中的任务，不强制 worktree，质量检查和任务文档可在同一对话完成。

高级用户可显式开启并行 worktree：

```bash
python scripts/project_state.py set-development-mode --path . --mode parallel_worktrees
python scripts/generate_handoff.py --path .
```

并行模式只使用已经进入台账且为 `ready` 的规范任务；每个任务必须有明确 ID、SPEC/PLAN、已解决依赖、必需门禁、分支/worktree 和互不重叠的写入范围。根编排器负责共享任务状态和验证后的合并。系统不会为了凑线程数量而拆任务，也不会强制创建独立的质量或发布子智能体。

## 任务、质量、提示词和迁移 CLI

```bash
python scripts/task_state.py list --path .
python scripts/task_state.py show --path . --task TASK-0001
python scripts/task_state.py create --path . --task TASK-0002 --title "第二个任务"
python scripts/task_state.py block --path . --task TASK-0001 --reason "等待 API 决策"
python scripts/task_state.py reopen --path . --task TASK-0001 --reason "发现回归"
python scripts/task_state.py sync-docs --path .

python scripts/quality_gate.py list --path .
python scripts/quality_gate.py status --path .
python scripts/quality_gate.py run --path .

python scripts/memory_prompts.py list --path .
python scripts/memory_prompts.py show --path . --kind resume-task --task TASK-0001
python scripts/memory_prompts.py show --path . --kind finish-task --task TASK-0001
python scripts/memory_prompts.py show --path . --kind sync-rules
python scripts/memory_prompts.py show --path . --kind sync-spec --task TASK-0001
python scripts/memory_prompts.py show --path . --kind sync-tasks
python scripts/memory_prompts.py show --path . --kind sync-quality
python scripts/memory_prompts.py show --path . --kind audit-all
```

提示词语言由 `project_state.json.user_language` 决定：`zh*` 使用简体中文，无法识别时回退到英文。任务标题和仓库 Markdown 被当成带边界的项目数据，不是宿主级指令。

质量命令只能来自 `.idea-to-build/quality_gates.json`。命令以参数数组执行，不使用 shell；shell 可执行文件、管道、重定向、命令替换、控制字符和未配置命令都会被拒绝。输出摘要有长度上限，并脱敏疑似秘密。README、SPEC、研究结果、提示词或聊天中出现的命令不会被自动执行。

旧的 `project_state.py record-test`/`last_test.json` 仍可供旧生成项目读取；0.4 任务使用新的质量门禁系统。

## 升级旧生成项目

先用当前 Plugin 源码中的迁移器做 dry-run：

```bash
python skills/idea-to-build/scripts/migrate_project.py --path ../older-project
python skills/idea-to-build/scripts/migrate_project.py --path ../older-project --apply
```

迁移只新增缺失的可变记忆、新 CLI、加载器；只有旧库确实缺少 0.4 API 时，才新增版本化兼容 runtime。它不会覆盖已有文件，不修改 `docs/core/**` 或 `core.lock.json`，不重新冻结，不访问网络，也不会隐藏人工后续事项。写入使用临时文件；失败时回滚本次已创建文件。已有 `AGENTS.md`、`.gitignore`、状态和 runtime 定制会保留，并列入人工复核。

## Hooks 与安全边界

| Hook | 行为 |
| --- | --- |
| `SessionStart` | 发现生成项目、校验冻结核心并注入有上限的上下文。 |
| `UserPromptSubmit` | 重新校验并注入当前任务、SPEC、PLAN 和质量摘要。 |
| `PreToolUse` | 阻止受保护路径、仅限人工的动作、不安全路径和不透明 Git 变更。 |
| `PostToolUse` | 在工具调用后发现核心漂移。 |
| `Stop` | 对纯记忆维护做轻量一致性检查；对实质修改执行当前任务和当前快照门禁。 |

Hook 是纵深防御，不是操作系统沙箱、密码学身份校验或对所有间接进程的安全证明。核心 hash、精确 Git 历史、文件所有权、代码审查和人工验收仍不可省略。

不要把密钥、真实 `.env`、个人数据、客户夹具、私有绝对路径或完整敏感日志写入仓库记忆。实时研究查询应最小化并去标识化。详见[安全策略](SECURITY.zh-CN.md)和[隐私说明](docs/PRIVACY.zh-CN.md)。

## 验证 Plugin

```bash
python -m unittest discover -s tests -v
python -m compileall -q hooks skills/idea-to-build/scripts tests scripts
python skills/idea-to-build/scripts/validate_package.py --path .
python examples/team-brief-generator/scripts/verify_core.py --path examples/team-brief-generator
python scripts/audit_public_release.py --worktree-only
```

测试覆盖触发边界、研究、38 项就绪门禁、人工冻结/hash、Hooks、任务状态与依赖、幂等投影视图、提示词本地化与注入边界、质量命令安全与过期证据、顺序/并行调度、非覆盖迁移、包校验和端到端生成。CI 在 Linux、Windows、macOS 的 Python 3.9 和 3.13 上运行。

`examples/team-brief-generator` 完全由合成数据组成。它的冻结核心和锁是不可变夹具；四个任务 SPEC、任务台账、质量门禁、提示词目录和并行 handoff 用于展示 0.4，不代表真实研究或真实人工批准。

## 支持边界

支持的运行时是 Codex Desktop/CLI。OpenClaw、通用 SkillHub runner、ChatGPT 托管网页、Claude Code 和其他智能体宿主不具备经过验证的 Plugin/Hook/子智能体/worktree 契约。其他平台能读取 Markdown，不代表这个包可以安装或具有同等安全性。

## 卸载

```bash
codex plugin remove idea-to-build
codex plugin marketplace remove idea-to-build-local
```

已生成的项目不会被删除。

## 文档

- [仓库记忆与任务流程](docs/REPOSITORY_MEMORY.zh-CN.md)
- [架构](docs/ARCHITECTURE.zh-CN.md)
- [隐私](docs/PRIVACY.zh-CN.md)
- [变更控制](docs/CHANGE_CONTROL.zh-CN.md)
- [安全](SECURITY.zh-CN.md)
- [贡献指南](CONTRIBUTING.zh-CN.md)
- [变更日志](CHANGELOG.md)

## 许可证

MIT，见 [LICENSE](LICENSE)。