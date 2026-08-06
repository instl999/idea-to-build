# 开发指南

## 环境要求

- Python 3.9 或更高版本。运行时代码仅使用标准库；本次调查环境为 Python 3.14.6。
- Git；冻结、调度和大部分集成测试依赖 Git。本次调查环境为 Git 2.55.0.windows.2。
- 要实际安装/运行插件，需要支持 Plugins、Hooks、原生协作工具和 Git worktree 的当前 Codex Desktop/CLI；最低宿主版本尚未在仓库中固定。
- 文件使用 UTF-8；核心 hash 会把 CRLF/CR 规范化为 LF。

仓库没有 `requirements.txt`、锁文件或第三方 Python 依赖。`pyproject.toml` 仅声明项目元数据、Python 版本和仓库测试命令，没有 `[build-system]`。

## 获取与安装

开发者检出：

```bash
git clone https://github.com/instl999/idea-to-build.git
cd idea-to-build
python --version
git --version
python -m unittest discover -s tests -v
```

无需执行 `pip install`。仓库内 marketplace 入口是 `.agents/plugins/marketplace.json`。截至 2026-08-06，[OpenAI 官方 Plugin 打包文档](https://developers.openai.com/plugins/build/plugins)确认可用 CLI 管理 marketplace 来源：

```bash
codex plugin marketplace add .
codex plugin marketplace list
```

官方文档要求在 ChatGPT Desktop/Codex 的 Plugins Directory 中选择该本地来源并安装/测试插件，没有记录仓库 README 中的 `codex plugin add ...` 或 `codex plugin list --json`。本次审查尝试只读运行本机 `codex.exe` 帮助，但系统拒绝执行，因此这些宿主命令没有本机实测。安装/更新会改变用户配置；完成后应审查 Hook hash，并在新任务中加载 Skill。

## 环境变量和数据库

- 运行时代码没有读取环境变量，也没有 `.env.example`；插件不需要自有 API key。
- Host Web Search 和 Codex 服务的凭证/策略由宿主管理，不应写入仓库。
- 项目没有数据库，不需要初始化、migration 或 seed。

## 本地运行方式

这是 CLI/Hook 插件，没有常驻服务或单一 `start` 命令。开发时直接运行对应命令或测试：

```bash
python skills/idea-to-build/scripts/init_project.py --help
python skills/idea-to-build/scripts/project_state.py --help
python skills/idea-to-build/scripts/codex_dispatch.py --help
```

创建一次性生成项目会写文件并初始化 Git，必须使用明确的目标目录：

```bash
python skills/idea-to-build/scripts/init_project.py --path ../my-product --name "My Product"
```

`--force` 会覆盖生成器管理的既有路径，只在已审查目标后使用；不要对未知目录运行。初始化只对输出冲突做写前预检，后续 Git 根检查、`git init` 或 commit 失败不会回滚已经复制的文件。

## 已验证的质量命令

```bash
python -m unittest discover -s tests -v
python -m compileall -q hooks skills/idea-to-build/scripts tests scripts
python skills/idea-to-build/scripts/validate_package.py --path .
python examples/team-brief-generator/scripts/verify_core.py --path examples/team-brief-generator
python scripts/audit_public_release.py --worktree-only
```

发布前运行带提交元数据检查的审计：

```bash
python scripts/audit_public_release.py
```

没有仓库配置支持的独立 lint、format、typecheck 或构建命令。不要自行把未配置的工具写成必需命令。两个审计模式都只扫描当前 Git 已跟踪文本；完整模式仅额外检查所有 refs 的 author/committer 邮箱，不扫描未跟踪文件或历史 blob 内容。

## 调试建议

- 先运行单个测试模块，例如 `python -m unittest discover -s tests -p test_core_lock.py -v`；直接运行 `python -m unittest tests.test_core_lock -v` 会因 `_support` 不在导入路径而失败。测试通过 `tests/_support.py` 动态加载权威运行时。
- CLI 成功和预期失败通常返回结构化 JSON；`render_context --format text` 是文本，`record-test` 的测试输出会先直通终端。查看 stderr 和退出码，不要假设 stdout 只有一个 JSON 对象。
- Hook 行为优先通过 `tests/test_hooks.py` 的模拟宿主事件复现。Hook 在非生成项目中应保持安静。
- 状态/锁/manifest 问题依次检查版本字段和代码内校验、精确项目根、`git status`、核心 hash、prompt hash 和分支 ancestry；仓库没有完整 JSON Schema。
- 运行 `project_state.py record-test` 前审查 `project_state.json` 的精确命令。它不经 shell，但仍会以当前权限执行指定程序；生成记录会绑定项目/runner/命令/快照并受 Hook 可见写路径保护，但仍可被有文件系统权限的外部进程伪造。
- 冻结示例用 `verify_core.py` 验证；不得为修复测试直接修改其 `docs/core/**` 或 lock。

## 常见问题

- Python 命令名称因平台不同：Hook 清单在非 Windows 使用 `python3`，Windows 使用 `py -3`；仓库开发命令以 `python` 展示。
- readiness 退出 3 表示未就绪，不是解析崩溃；读取 JSON `blockers`。
- 包校验退出 4 表示结构/隐私/AST 校验失败。
- 核心校验退出 3 表示未冻结或 hash 不一致；不要重算 hash 掩盖漂移。
- 调度要求精确 Git 根、干净 integration worktree、已提交 handoff/prompts/manifest 和人类冻结记录。
- Windows 可能无法创建目录 symlink；对应初始化安全测试会跳过，而不是视为通过了该平台能力。

## 推荐变更流程

### 修改运行时或 CLI

1. 明确受影响的状态、JSON/CLI 契约和失败模式。
2. 修改 `skills/idea-to-build/scripts/` 权威源。
3. 增加或更新对应 `tests/`；如涉及生成项目，确认复制件/端到端路径。
4. 更新 API、架构、测试、状态和变更日志文档。
5. 运行完整质量命令并检查 `git diff`。

### 修改 Hook

1. 阅读 `hooks/_hooklib.py`、`hooks/hooks.json` 和 `tests/test_hooks.py`。
2. 保持“打开的项目不可信，Hook 只加载已安装运行时”的边界。
3. 为允许和拒绝路径同时增加测试，覆盖 Windows 分隔符、路径穿越和 shell 控制符。
4. 更新安全/架构文档并提醒安装者重新审查 Hook hash。

### 修改模板或文档生成

1. 区分模板、生成设计骨架和冻结示例。
2. 保留五份核心契约和八份 live 文档的角色，不手工制造 lock。
3. 运行端到端生成、包校验和示例核心校验。

### 新增数据库、API、认证或公共类型

当前不存在这些子系统。新增前必须先在 `docs/DECISIONS.md` 记录决定，在 `docs/OPEN_QUESTIONS.md` 解决所有权、权限、数据保留、迁移、兼容和回滚问题，并补充集成/安全测试；不能把它当作普通局部改动。
