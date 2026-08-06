# 部署与运维

## 构建和发布模型

本项目不是托管服务，也没有传统构建产物。仓库本身是 Codex Plugin 源包：`.codex-plugin/plugin.json` 指向 `./skills/`，`hooks/hooks.json` 由默认发现机制加载，`.agents/plugins/marketplace.json` 提供仓库本地 marketplace。

仓库可以按当前 [OpenAI 官方 Plugin 文档](https://developers.openai.com/plugins/build/plugins)把本地 marketplace 加入 Codex：

```bash
codex plugin marketplace add .
codex plugin marketplace list
```

插件安装与测试应在 ChatGPT Desktop/Codex 的 Plugins Directory 中选择 `Idea-to-Build Local` 来源完成。官方文档没有记录 README 中的 `codex plugin add ...`/`codex plugin list --json`，且本次审查环境拒绝执行本机 `codex.exe` 帮助，故不能把它们列为已验证命令。更新采用 Git 拉取、重启/刷新本地来源、在 Desktop 重新审查安装与 Hook hash，并在新任务中加载 Skill。仓库没有自动发布到 GitHub Releases、Plugins Directory、PyPI 或 SkillHub 的 workflow。

## 运行环境

- Codex Desktop/CLI 宿主，且组织策略允许 Plugins、Hooks、原生协作工具和本地文件/Git 操作。
- Python 3.9+ 和 Git。
- Host Web Search 仅在实时方案研究时需要网络。
- Linux、Windows、macOS × Python 3.9/3.13 是 CI 配置目标；仓库配置本身不证明最近远端 run 已通过，真实宿主行为仍受版本和 rollout 影响。

没有 Dockerfile、Compose、Kubernetes、Terraform、云运行时或容器镜像。

## CI/CD

GitHub Actions 在 push/PR 上运行测试、编译、包校验、冻结示例校验和完整发布审计。CI 不执行部署或版本发布；没有审批环境、制品签名、provenance 或自动 changelog/tag 步骤。

## 环境区分和迁移

- 未定义 development/staging/production 环境；本地仓库、已安装插件缓存和用户生成项目是主要运行边界。
- 没有数据库 migration。
- JSON `schema_version` 由运行时代码做版本检查；高版本失败关闭，但字段校验不完整，也没有独立升级/降级命令。

## 日志、监控和告警

- Hook 漂移事件可追加到生成项目的 `.idea-to-build/guardrail.log`。
- 最近测试记录在 `.idea-to-build/last_test.json`；模板默认忽略它，Hook 校验 recorder 元数据并阻止可观察的直接写入，但外部进程仍可伪造普通 JSON，不能视为密码学执行证明。
- Codex/终端输出和 Git 历史提供其余诊断信息。
- 没有集中日志、指标、trace、告警、遥测或健康检查服务。

## 回滚和恢复

- 插件更新失败：移除当前本地插件，检出已知良好 Git commit/tag，再重新添加并审查 Hook hash。
- 核心 hash 异常：停止开发、保留 status/log/commit 证据，在恢复分支从已知良好 commit 恢复；禁止直接重算 hash。
- 子任务合并冲突：adapter 自动 `merge --abort`，保持 integration tree 干净并保留子分支。
- worktree 异常：脏 worktree 保留调查；正常退休只删除干净 worktree并保留 branch。
- Git tag `v0.2.0` 是本地与 2026-08-06 远端只读查询都能确认的最近 tag；当前 0.3.0 分支没有对应远端 release tag。Plugins Directory 是否另有发布仍待人工确认。

没有自动备份或灾难恢复任务。恢复能力依赖本地/远端 Git、用户备份和宿主配置；Git 不应被视为敏感数据的安全删除机制。

## 发布前检查

1. 同步版本清单、README、安全策略和 changelog。
2. 运行完整测试、`compileall`、包校验和冻结示例校验。
3. 运行 `python scripts/audit_public_release.py` 检查当前 tracked 内容和所有 refs 的提交邮箱；另用专门工具/人工审查未跟踪文件与历史 blob。
4. 人工审查依赖、权限、Hook hash、隐私和敏感数据。
5. 创建 tag/发布前确认目标分支和远端状态；仓库没有自动完成这些操作。

生成项目模板默认忽略 `.idea-to-build/last_test.json` 与 `guardrail.log`；既有项目、强制添加、归档和备份仍必须检查其保留与脱敏规则。初始化与 handoff 生成也不是事务；失败后需检查部分文件和 Git 状态再重试。

## 待确认的运维信息

- 0.3.0 的正式发布负责人、版本/tag 策略和发布渠道。
- Codex 支持的最低版本、插件缓存更新策略和 Hook 兼容矩阵。
- 默认分支保护、required checks、secret scanning/push protection 的实际启用状态。
- 事故响应、备份、恢复目标、日志保留和支持 SLA。
