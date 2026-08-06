# 项目文档索引

本索引是仓库内项目记忆的导航入口。代码和配置始终是首要事实来源；文档冲突时按 [`docs/DECISIONS.md`](DECISIONS.md) 的证据规则处理。

| 文档 | 记录内容 | 何时阅读 | 何时必须更新 |
| --- | --- | --- | --- |
| [`../AGENTS.md`](../AGENTS.md) | Codex 执行规则、必读项、命令和禁止事项 | 每个任务开始前 | 工作流、目录、质量门禁或协作规则改变时 |
| [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) | 产品问题、用户、能力、范围和成熟度 | 理解产品定位、评审范围时 | 核心能力、目标用户或支持边界改变时 |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) / [`ARCHITECTURE.zh-CN.md`](ARCHITECTURE.zh-CN.md) | 系统组件、信任边界、状态和核心数据流 | 修改运行时、Hook、生成器或调度器前 | 模块边界、启动/数据流或外部依赖改变时 |
| [`DOMAIN_MODEL.md`](DOMAIN_MODEL.md) | 业务术语、实体、关系、状态和业务规则 | 修改状态机、需求、冻结或调度规则前 | 实体、枚举、状态转换或核心规则改变时 |
| [`DATA_MODEL.md`](DATA_MODEL.md) | 文件型持久化、JSON schema、生命周期与一致性风险 | 修改状态文件、锁文件、manifest 或 Git 记录前 | 字段、schema、迁移、保留或删除策略改变时 |
| [`API_AND_INTEGRATIONS.md`](API_AND_INTEGRATIONS.md) | CLI、Hook 协议、Codex/Git/Web Search 集成 | 修改命令、退出码、Hook 或宿主能力前 | 任何接口、超时、错误或集成契约改变时 |
| [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md) | 环境、安装、开发、调试和常用命令 | 开始实现或本地复现前 | 环境要求、命令、安装方式或开发流程改变时 |
| [`TESTING_AND_QUALITY.md`](TESTING_AND_QUALITY.md) | 测试层级、CI、覆盖范围和质量风险 | 修改行为或准备提交/发布前 | 测试、CI、校验器或质量标准改变时 |
| [`DEPLOYMENT_AND_OPERATIONS.md`](DEPLOYMENT_AND_OPERATIONS.md) | 插件安装、发布、运行边界、回滚和运维缺口 | 发布、安装、回滚或事故处理前 | 发布渠道、宿主要求、CI/CD 或恢复流程改变时 |
| [`DECISIONS.md`](DECISIONS.md) | 有代码证据的技术决定及其约束 | 计划架构性变化前 | 新决定落地或已有决定被替换时 |
| [`KNOWN_ISSUES_AND_TECH_DEBT.md`](KNOWN_ISSUES_AND_TECH_DEBT.md) | 已确认问题、风险和技术债务 | 规划工作、评审风险前 | 新问题确认、级别变化或问题解决时 |
| [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) | 无法从仓库确认的问题 | 需要产品/架构/运维判断时 | 问题新增、获得答案或答案影响落地时 |
| [`../PROJECT_STATUS.md`](../PROJECT_STATUS.md) | 当前阶段、已实现/未实现、阻塞与下一步 | 每个任务开始和结束时 | 每个实质任务完成、分支/发布状态变化时 |
| [`../CHANGELOG_AI.md`](../CHANGELOG_AI.md) | 跨会话 AI 工作记录 | 追溯 AI 生成文档和判断时 | 每次 AI 对仓库产生修改时 |
| [`PRIVACY.md`](PRIVACY.md) / [`PRIVACY.zh-CN.md`](PRIVACY.zh-CN.md) | 数据处理、搜索和发布脱敏 | 处理研究、提示词、个人/机密数据前 | 数据流、外部服务或保留方式改变时 |
| [`CHANGE_CONTROL.md`](CHANGE_CONTROL.md) / [`CHANGE_CONTROL.zh-CN.md`](CHANGE_CONTROL.zh-CN.md) | 冻结核心的变更和恢复流程 | 涉及 `docs/core/**` 或 hash 漂移时 | 冻结/解冻或恢复机制改变时 |
| [`../SECURITY.md`](../SECURITY.md) / [`../SECURITY.zh-CN.md`](../SECURITY.zh-CN.md) | 安全模型、漏洞报告和发布检查 | 安全评审、漏洞处理、发布前 | 威胁模型、支持版本或披露流程改变时 |

实现级协议位于 `skills/idea-to-build/references/`。它们属于 Skill 行为规范；修改前同时阅读 `skills/idea-to-build/SKILL.md` 和相关测试。
