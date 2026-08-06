# 项目文档索引

本索引是仓库内项目记忆的导航入口。实现事实以代码、配置和测试为准；版本、风险、决策或运行行为发生变化时，应同步对应专项文档。

| 文档 | 内容 | 何时读取/更新 |
| --- | --- | --- |
| [`../AGENTS.md`](../AGENTS.md) | Codex 协作规则、强制命令和保护边界 | 每个任务开始前；流程或门禁改变时更新 |
| [`../PROJECT_STATUS.md`](../PROJECT_STATUS.md) | 当前阶段、已实现/未实现、阻塞和下一步 | 每个实质任务开始和结束时 |
| [`REPOSITORY_MEMORY.zh-CN.md`](REPOSITORY_MEMORY.zh-CN.md) / [`REPOSITORY_MEMORY.md`](REPOSITORY_MEMORY.md) | 四层记忆、任务、质量、提示词、迁移 | 修改任务/质量/上下文/Stop/迁移前 |
| [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) | 产品定位、能力、范围和成熟度 | 理解项目或产品边界改变时 |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) / [`ARCHITECTURE.zh-CN.md`](ARCHITECTURE.zh-CN.md) | 组件、信任边界、状态和数据流 | 修改 runtime、Hook、生成器或调度器前 |
| [`DOMAIN_MODEL.md`](DOMAIN_MODEL.md) | 实体、状态、关系和业务规则 | 修改状态机、台账、冻结或调度规则前 |
| [`DATA_MODEL.md`](DATA_MODEL.md) | 文件持久化、JSON 字段、生命周期和一致性 | 修改 schema、迁移、锁或 manifest 前 |
| [`API_AND_INTEGRATIONS.md`](API_AND_INTEGRATIONS.md) | CLI、Hook、Codex/Git/Web Search 集成 | 修改命令、参数、退出码或宿主契约前 |
| [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md) | 环境、开发、调试和命令 | 开始实现或开发流程改变时 |
| [`TESTING_AND_QUALITY.md`](TESTING_AND_QUALITY.md) | 测试层级、CI、质量门禁和风险 | 修改行为或准备提交/发布前 |
| [`DEPLOYMENT_AND_OPERATIONS.md`](DEPLOYMENT_AND_OPERATIONS.md) | 安装、发布、回滚和运行边界 | 安装/发布/恢复流程改变时 |
| [`DECISIONS.md`](DECISIONS.md) | 有代码证据的技术决定 | 架构性决定落地或被替换时 |
| [`KNOWN_ISSUES_AND_TECH_DEBT.md`](KNOWN_ISSUES_AND_TECH_DEBT.md) | 已确认问题、风险和技术债务 | 规划工作或问题状态改变时 |
| [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) | 无法从仓库确认的事项 | 需要产品/架构/运维判断时 |
| [`PRIVACY.md`](PRIVACY.md) / [`PRIVACY.zh-CN.md`](PRIVACY.zh-CN.md) | 数据处理、搜索、日志和脱敏 | 数据流或保留方式改变时 |
| [`CHANGE_CONTROL.md`](CHANGE_CONTROL.md) / [`CHANGE_CONTROL.zh-CN.md`](CHANGE_CONTROL.zh-CN.md) | 冻结核心和任务规格的变更恢复 | 涉及核心、SPEC 或验收基线时 |
| [`../SECURITY.md`](../SECURITY.md) / [`../SECURITY.zh-CN.md`](../SECURITY.zh-CN.md) | 威胁模型、漏洞报告和发布检查 | 安全评审或信任边界改变时 |
| [`../CHANGELOG_AI.md`](../CHANGELOG_AI.md) | 跨会话 AI 工作记录 | 每次 AI 修改仓库时 |

Skill 的实现级协议位于 `skills/idea-to-build/references/`。修改前同时读取 `skills/idea-to-build/SKILL.md`、相关协议和测试。