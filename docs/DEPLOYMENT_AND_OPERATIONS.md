# 部署与运维

## 交付模型

本项目不是托管服务，没有传统构建产物、数据库迁移或运行环境部署。仓库本身是 Codex Plugin 源包：`.codex-plugin/plugin.json` 指向 `skills/`，`hooks/hooks.json` 声明生命周期 Hook，`.agents/plugins/marketplace.json` 提供仓库本地 marketplace。

当前版本元数据为 `0.4.0`。最新已知 Git tag 是 `v0.2.0`；0.4.0 尚未推送、打 tag 或确认进入 Plugins Directory。仓库没有自动发布到 GitHub Releases、Plugins Directory、PyPI 或 SkillHub 的 workflow。

## 安装与更新

仓库本地 marketplace 的安装命令：

```bash
codex plugin marketplace add .
codex plugin add idea-to-build@idea-to-build-local
```

开发期更新使用官方 Plugin cachebuster helper 刷新本地缓存，再从实际 marketplace 名重新安装。重新安装后必须在新的 Codex 任务中验证 Skill 和 Hook；旧任务不会可靠地重新加载所有 Plugin 上下文。不要手工修改用户级 `marketplace.json` 或 `config.toml` 来模拟更新。

## 运行环境

- Codex Desktop/CLI 宿主，并且组织策略允许 Plugins、Hooks、原生协作工具和本地文件/Git 操作。
- Python 3.9+ 标准库和 Git。
- Host Web Search 只在实时方案研究时需要网络；Plugin 运行时本身没有网络服务。
- CI 目标是 Linux、Windows、macOS × Python 3.9/3.13；配置存在不等于最近远端 run 已成功。

没有 Dockerfile、Compose、Kubernetes、Terraform、云运行时或容器镜像。

## 旧项目迁移

先从当前 Plugin 源运行 dry-run：

```bash
python skills/idea-to-build/scripts/migrate_project.py --path /path/to/project
```

用户审查新增文件和人工协调项后，再显式应用：

```bash
python skills/idea-to-build/scripts/migrate_project.py --path /path/to/project --apply
```

迁移只添加缺失的 0.4 记忆资产和 CLI，不覆盖既有变量文件，不修改 `docs/core/**` 或核心锁，不重新冻结，也不访问网络。若旧运行时缺少新 API，迁移添加独立兼容副本，新 CLI 通过 `_memory_runtime.py` 加载它；旧 `idea_to_build_lib.py` 保持原样。

## CI 与发布前门禁

GitHub Actions 在 push/PR 上运行测试、编译、包校验、冻结示例校验和发布审计；不会部署、签名、创建 tag 或发布版本。正式发布前必须：

1. 同步 manifest、`pyproject.toml`、README、安全说明和 changelog。
2. 运行仓库规定的完整测试、`compileall`、包校验和冻结示例校验。
3. 暂存全部目标文件后运行 `python scripts/audit_public_release.py --worktree-only`；完整发布再运行不带该参数的模式并人工审查历史 blob 和未跟踪文件。
4. 人工审查依赖、权限、Hook hash、隐私、敏感数据和远端保护设置。
5. 安装本地 Plugin，在新的 Codex 任务中完成真实宿主 smoke test。
6. 创建 tag/发布前重新确认目标分支、远端状态和发布负责人。

## 本地状态、日志与证据

- `.idea-to-build/guardrail.log`：Hook 漂移事件；模板默认忽略。
- `.idea-to-build/last_test.json`：旧测试记录；模板默认忽略。
- `.idea-to-build/last_quality.json`：当前任务质量门禁结果；模板默认忽略。
- `.idea-to-build/tasks.json` 和 `quality_gates.json`：需要版本控制的规范配置。
- Codex/终端输出和 Git 历史提供其余诊断信息。

这些普通文件适合开发流程恢复，不是密码学证明。仓库没有集中日志、指标、trace、告警、遥测或健康检查服务。

## 回滚与恢复

- Plugin 更新失败：移除/重新安装当前本地 Plugin，检出已知良好 commit/tag，并在新任务验证 Hook 和 Skill。
- 核心 hash 异常：停止开发，保留 status/log/commit 证据，从已知良好 commit 恢复；禁止直接重算 hash 掩盖变化。
- 子任务合并冲突：adapter 执行 `merge --abort` 并保留子分支供调查。
- worktree 异常：脏 worktree 留给人工调查；正常退休只移除干净 worktree，并保留 branch。
- 任务 Markdown 投影陈旧：运行 `task_state.py sync-docs --path .` 从规范 JSON 幂等重建。
- 迁移回滚：删除本次新添加且尚未使用的文件，或从迁移前 Git commit 恢复；不得用历史重写掩盖问题。

Git 和本地日志不是敏感数据的安全删除机制。仓库没有自动备份或灾难恢复任务，恢复依赖本地/远端 Git、用户备份和宿主配置。

## 待确认的运维信息

- 0.4.0 的正式发布负责人、tag 策略、GitHub/Plugins Directory 渠道和支持承诺。
- 最低支持 Codex 版本、缓存更新策略和 Hook/协作能力矩阵。
- 分支保护、required checks、secret scanning 和 push protection 的实际启用状态。
- 事件响应、备份、RPO/RTO、日志保留和支持 SLA。
