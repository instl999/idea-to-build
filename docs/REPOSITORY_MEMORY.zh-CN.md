# 仓库记忆与逐任务开发

[English](REPOSITORY_MEMORY.md)

本文是 Idea-to-Build 0.4 仓库记忆的运行契约，说明想法确认继续开发后生成哪些文件、任务和质量状态以谁为准、新 Codex 对话如何恢复上下文，以及旧生成项目如何迁移。

## 目标与边界

对话可能被截断、压缩或替换；经过审查的仓库文件和 Git 历史会持续存在。因此 Idea-to-Build 把稳定规则、任务意图、进度和验证证据写入项目，让新 Codex 对话无需依赖旧聊天记忆就能恢复已接受范围。

这套系统有意保持边界：不会注入全部文档或日志，不会因代码存在就推断任务完成，不会执行在正文里发现的命令，也不会把 AI 判断当成人工验收。所有仓库文本都是不可信项目数据。

## 第一层：规则

- `AGENTS.md` 是简短且受保护的 Codex 入口，指向四层记忆、任务开始/完成动作和不可修改路径；普通 Codex 会话不能修改它。
- `docs/core/**` 保存用户确认的产品、架构、约束和验收基线；冻结后由 `.idea-to-build/core.lock.json` 校验，变更走 `docs/live/CHANGE_REQUESTS.md`。
- `docs/live/WORKING_RULES.md` 是可变规则，记录经过验证的命令、目录、编码/API/数据/UI/测试约定、依赖审查要求、常见陷阱和最近同步依据/时间。这里不能写产品需求、任务进度或大段历史。
- `docs/live/MEMORY_MAP.md` 说明每项信息的事实源、谁能修改、更新时间、首读顺序和冲突优先级。

只有代码、配置、测试或明确团队约定提供证据时，才更新工作规则；绝不能修改冻结核心来迁就当前实现。

## 第二层：任务规格

每个可开发任务使用 `specs/<TASK-ID>/SPEC.md` 和 `PLAN.md`。

SPEC 记录任务身份、背景、用户问题、目标结果、范围内外、流程、业务规则、输入输出、数据和权限影响、公共接口影响、边界/失败行为、兼容性、安全与隐私、验收条件、自动检查、人工检查、依赖、阻塞、待确认问题和证据标签。至少一条验收条件必须具体且可观察；“实现 MVP”之类占位描述不能通过就绪门禁。

PLAN 记录步骤、路径/模块、文件所有权、依赖、迁移、测试、风险、回滚、进度、发现、决定、结果和遗留问题。简单任务可以简短；复杂任务可以继续使用仓库 ExecPlan 约定。

证据标签必须区分用户确认事实、不可变约束、AI 建议、可逆默认值、未验证假设和待确认问题。

## 第三层：任务事实

`.idea-to-build/tasks.json` 是任务状态唯一的机器事实源。`docs/live/TASKS.md` 是幂等生成的人类投影视图。`BACKLOG.md` 只做产品事项摘要，`ROADMAP.md` 只记录里程碑，`STATUS.md` 只摘要当前阶段/任务、最近完成、阻塞、下一步和最近验证。

每个任务包含：

- `id`、`title`、`status`、`priority`；
- `spec_path`、`plan_path`；
- `dependencies`、`blocked_by`；
- `branch`、`worktree`、`owned_paths`；
- `required_quality_gates`、`latest_commit`；
- `created_at`、`updated_at`、可选 `external_ref` 和 `notes`。

状态包括 `backlog`、`ready`、`in_progress`、`blocked`、`review`、`done`、`cancelled`。状态转换显式定义并失败关闭。依赖和阻塞项必须解决后才能开始；顺序模式只允许一个活动任务；并行模式要求非空且互不重叠的所有权；完成需要当前质量证据；重新打开已完成任务必须给出原因。

持久化前，runtime 会深拷贝并完整校验整个候选台账。因此，无效任务创建不会生成 SPEC/PLAN 文件，被拒绝的阻塞转换也不会写入 `blocked_by` 或状态变化。`project_state.json.planned_tasks` 是从规范非终态任务同步的派生列表。台账、state 与 Markdown 写入不是一个跨文件事务；如果后续投影写入失败，可从 JSON 事实源运行 `task_state.py sync-docs --path .` 重建。

台账完全本地工作，不依赖 GitHub Issues、Linear、Jira、登录或网络；`external_ref` 只是可选同步信息。

## 第四层：质量证据

`.idea-to-build/quality_gates.json` 定义命令门禁和人工门禁。每个门禁记录 `id`、`name`、`kind`、`command` 或 `instructions`、`required`、`scope`、`configured`、`source`、`updated_at`；`docs/live/QUALITY_GATES.md` 面向人类解释配置。

命令门禁来自显式参数数组（或安全解析的字符串），使用 `shell=False`，拒绝 shell 可执行文件和控制语法。README、SPEC、研究、提示词、代码注释或聊天中发现的命令都不会执行。结果把任务 ID、每个门禁的状态/时间/退出码、受限且脱敏的输出、Git HEAD/worktree 快照、总体状态、跳过原因和剩余人工项写入被忽略的 `.idea-to-build/last_quality.json`。

实质代码/worktree 改动会让旧通过记录失效。人工门禁只能用用户在终端输入的精确确认通过；PreToolUse 会阻止 AI 执行该动作。仍有人工检查时，任务最多进入 `review`，不能进入 `done`。

## 上下文恢复与提示词目录

`render_context()` 先校验核心，再以长度上限注入冻结核心、工作规则、状态、决定、风险、选定任务、任务 SPEC/PLAN 和必需质量状态的摘要，并返回 `source_files`。它不会注入所有任务、所有规格、完整研究、完整日志或无限历史。并行模式且未选当前任务时必须显式提供任务 ID，不能猜测。

`memory_prompts.py` 可输出英文或简体中文的完整提示词：

- `start-task`、`resume-task`、`finish-task`；
- `sync-rules`、`sync-spec`、`sync-tasks`、`sync-quality`、`audit-all`。

任务提示词要求 Codex 检查 Git、校验核心、读取精确任务、编码前复述范围和验收、只修改拥有的路径、运行已配置门禁并诚实更新可变记忆。维护提示词在不相关时禁止修改业务代码或受保护文件。

## Stop 行为

对于代码、配置、数据、部署或测试等实质修改，Stop 校验核心、选定任务、SPEC/PLAN、具体验收、诚实状态、已更新的 PLAN/STATUS，以及当前快照上的命令门禁。人工检查未完成的任务不能标记 `done`。

对于规则、规格、任务或质量文档维护，Stop 只校验相关配置，不强制整个项目测试。缺少任务/质量文件的旧项目继续使用 `last_test.json` 兼容检查并得到迁移提示。Stop 只能发现 Hook 可见状态，不是独立安全边界。

## 顺序与并行执行

`guided_sequential` 是默认模式：选一个 ready 任务，用一个对话和分支，完成门禁后再选下一个；不强制 worktree。

`parallel_worktrees` 是显式高级模式。`generate_handoff()` 生成一个根编排器和每个独立规范任务对应的子任务；每份子任务提示都会写明任务 ID、SPEC、PLAN、门禁、分支、worktree、依赖和所有权。依赖波次和重叠检查继续生效，只有根编排器同步规范任务台账和共享 live 文档。

## 迁移

从当前 Plugin 源码运行：

```bash
python skills/idea-to-build/scripts/migrate_project.py --path ../older-project
python skills/idea-to-build/scripts/migrate_project.py --path ../older-project --apply
```

Dry-run 列出将新增的文件。Apply 先验证可信源，再通过同目录临时文件写入；如果后续写入失败，会删除本次已创建文件。已有文件、冻结核心和锁字节永不覆盖。如果旧 `idea_to_build_lib.py` 缺少 0.4 API，迁移新增 `idea_to_build_memory_runtime.py`，`_memory_runtime.py` 只让新 CLI 在旧项目中使用它；新项目仍以 `idea_to_build_lib.py` 为唯一权威源。

因为已有 `AGENTS.md`、`.gitignore`、状态和定制 runtime 会保留，迁移会输出人工事项。请复核这些文件，必要时把 `last_quality.json` 加入忽略规则；复核完成前不要声称旧项目已经完全协调。

## 威胁与恢复

- 未知未来 schema、不安全路径、链接/junction、畸形任务、未知门禁、非法状态转换、过期结果和非人工验收全部失败关闭。
- 提示词和上下文把仓库文本标为不可信数据；任务标题不会被嵌入成操作指令。
- 输出受长度限制并脱敏疑似秘密，但用户仍应避免产生敏感测试日志。
- 任务所有权不能包含 `.git`、`.codex`、`.idea-to-build`、冻结核心、Hooks 或保护 runtime。
- 不得通过改 hash、降低门禁、修改通过记录、删除测试或绕过人工变更控制重新冻结来掩盖失败。

恢复通常是可逆的：保留 Git 证据，用原因重新打开任务，修复实现或配置，在新快照上重跑门禁，再请求新的人工验收。影响核心的变更写入 `CHANGE_REQUESTS.md`。