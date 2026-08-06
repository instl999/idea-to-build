# API 与集成

## 接口边界

仓库没有 HTTP/REST、GraphQL、RPC、WebSocket、webhook 或公共服务端 endpoint。可调用接口是本地 CLI、Codex Hook 的 stdin/stdout JSON 协议、Plugin/Skill 清单以及生成项目中的 JSON/Markdown 契约。

## 本地 CLI

所有项目 CLI 位于 `skills/idea-to-build/scripts/`。多数正常结果以 JSON 结束；`render_context --format text` 输出纯文本，`record-test` 还会把子进程输出直接写到终端后再输出 JSON。捕获到的 `IdeaToBuildError` 通常写 stderr 并退出 2。

| 命令 | 输入 | 输出/副作用 | 特殊退出状态 |
| --- | --- | --- | --- |
| `init_project.py` | `--path`；可选 `--name`、`--language`、`--force`、`--skip-initial-commit` | 预检输出冲突并复制模板/运行时，初始化精确 Git 根并通常提交骨架；Git/commit 晚期失败不回滚已写文件 | 错误 2 |
| `project_state.py` | `status`、`transition`、`set-decision`、`update-requirements`、`confirm-core`、`record-test` | 读取/更新 state、台账；`record-test` 执行 state 声明的命令并写可变测试记录 | 错误 2；确认只允许人类流程 |
| `research_report.py` | 项目路径与研究 JSON | 写 `docs/live/RESEARCH.md` 并直接更新研究状态/阶段；运行时未强制协议要求的全部证据字段 | 错误 2 |
| `requirements_check.py` | 项目路径、可选 `--update-state` | readiness JSON，可同步阶段 | ready=0，not ready=3，错误=2 |
| `freeze_core.py` | 项目路径、可选 tag | 创建锁、只读位和冻结提交 | 仅人类终端；错误 2 |
| `verify_core.py` | 项目路径 | 重算五份核心文件 hash | valid=0，invalid/not frozen=3，错误=2 |
| `render_context.py` | 项目路径、JSON/text 格式 | 输出有大小限制的 core/live 上下文 | valid/draft=0，invalid=3，错误=2 |
| `generate_handoff.py` | 项目路径、可选 workstreams JSON | 生成设计文档、handoff、prompts、dispatch manifest | 错误 2 |
| `codex_dispatch.py` | 六个子命令 | 预览/启动、创建 worktree、验证/合并结果、退休 wave | 错误 2 |
| `validate_package.py` | 插件或生成项目路径 | 结构、Python AST、清单、隐私模式校验 | valid=0，invalid=4，错误=2 |

发布辅助 `scripts/audit_public_release.py` 检查 tracked 文本、符号链接、常见凭证/私有路径和 Git 邮箱；发现问题退出 1。

## Hook 协议

`hooks/hooks.json` 注册：

- `SessionStart`：验证冻结核心并注入受限上下文。
- `UserPromptSubmit`：每次提示前重新验证并注入上下文。
- `PreToolUse`：对人工专属命令、受保护路径和冻结后的不透明 Git 变更返回 deny。
- `PostToolUse`：重新验证 hash，漂移时追加 guardrail log 并停止。
- `Stop`：仅在实质开发阶段、有未提交变更时要求当前测试证据和 `docs/live/STATUS.md` 更新。

Hook 从 stdin 读取单个 JSON 对象。生成项目通常向 stdout 输出一个宿主约定 JSON；未找到项目时不输出。Session/User/Pre/Post 默认超时 20 秒，Stop 30 秒；代码没有重试。

## 外部集成

| 集成 | 用途 | 认证/数据 | 代码边界 |
| --- | --- | --- | --- |
| Codex Plugin/Skill/Hooks | 安装、激活、上下文和工具门禁 | 由宿主策略、信任和权限管理；插件不自建账号 | `.codex-plugin/plugin.json`、`SKILL.md`、`hooks.json` |
| Codex 原生协作工具 | `spawn_agent`/`wait_agent` 执行子任务；其他消息工具可选 | 使用宿主权限；生成提示词可能发送到模型服务 | Skill/参考协议声明；Python adapter 不实现宿主 API |
| Host Web Search | 当前方案、价格、许可和维护研究 | 查询文本离开仓库；必须最小化和假名化 | 仅由 Skill 指导宿主调用，Python 运行时没有网络客户端 |
| Git | 精确根校验、提交/tag、分支、worktree、diff 和 merge | 使用本地 Git 身份和权限 | `_run_git()` 及调度函数 |
| GitHub | 源码托管与 Actions CI | 发布内容进入远端；凭证由 Git/宿主管理 | `origin`、`.github/workflows/ci.yml` |

没有文件对象存储、支付、邮件、短信、AI API key、队列或缓存服务。

### 生成产品的条件式 MCP 集成

MCP 不是本 Plugin 的运行时外部集成或公共 API。Skill 仅在 requirements readiness 通过后，依据已确认的 agent 客户端、外部能力、宿主兼容、数据/安全/部署边界和直接 API/SDK 等替代方案，为生成产品记录 `MCP_NOT_APPLICABLE`、`MCP_USE_EXISTING_SERVER`、`MCP_BUILD_CUSTOM_SERVER` 或 `MCP_DEFER` 之一。

采用时，`docs/design/MCP_INTEGRATION_GUIDE.md` 记录由用户执行的安装/配置步骤、最小权限凭据、能力到 tools/resources/prompts 的映射、合成与负向测试、监控、禁用/移除和非 MCP 退路。Python 运行时不连接、安装或管理被推荐的 server。

## 重试、超时、幂等和错误处理

- CLI 不自动重试；预期业务错误通常为 `IdeaToBuildError` 和结构化错误 JSON。
- `record-test` 不使用 shell，但会以当前用户权限运行 mutable state 中声明的可执行文件/参数。精确匹配只绑定选择，不证明命令可信。记录包含项目 ID、runner 标记、命令、退出状态和 Git 快照；PreToolUse 阻止 Hook 可观察的直接写入，Stop 逐项校验，但外部进程仍可伪造普通 JSON。
- JSON 读取限制为 5 MiB；路径必须留在项目根且不能穿过 symlink/junction。
- JSON 写入使用同目录临时文件加 `os.replace`，降低部分写入风险。
- `preview` 无副作用；`materialize-wave` 仅在已存在 branch/worktree 完全匹配时可复用；创建中失败会回滚本次新建项。任意合法 wave 编号都可被 materialize，依赖/merge order 由宿主协议而非 adapter 完成状态强制。
- `merge-result` 重验任务；已经合并时返回 `ALREADY_MERGED`，冲突时执行 `merge --abort` 并保留分支。
- Hook 有超时但无重试；Git 命令没有统一超时参数，见技术债务文档。

## 契约或测试缺口

- 没有独立 JSON Schema/OpenAPI 来描述 state、ledger、lock、manifest 或 Hook payload；契约分散且校验深度不一致，`project_id` 等 state 字段不验证声明格式。
- 研究协议列出的日期、查询、许可、维护、隐私、价格等字段没有被运行时完整强制。
- MCP 四选一推荐及 readiness 先后顺序由 Skill 协议和测试约束，没有新增 state/ledger 字段或运行时命令证明真实会话已执行该判断。
- Codex 最低宿主版本和工具可用性没有机器可读约束；当前官方文档只确认 CLI marketplace 管理和 Desktop Plugins Directory 安装，本机 `codex.exe` 又无法执行帮助命令。
- `codex_dispatch_status=COMPLETE`、已完成 task/current wave 和 merge order 的写入/强制接口未找到。
- Stop Hook 的当前通过、缺记录、伪造记录和递归保护路径已有自动测试；stale、STATUS 缺失、非开发阶段以及真实 Codex 宿主事件仍需补充。
- package 校验器已覆盖 marketplace、Hook helper、完整 Skill CLI、项目记忆文档和版本一致性，但仍是显式清单与启发式内容扫描，不替代宿主安装或专业 secret scanning。
