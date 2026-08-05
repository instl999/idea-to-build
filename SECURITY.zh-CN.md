# 安全策略

[English](SECURITY.md) | **简体中文**

## 支持版本

仅为最新发布版本提供安全修复；当前支持 0.2.0。

## 报告漏洞

不要在公开 Issue 中提交利用细节、令牌、个人数据或尚未披露的漏洞。请使用仓库 GitHub 的 **Security → Report a vulnerability** 私有安全公告入口，说明受影响版本/commit、环境、复现步骤、影响和最小化且已脱敏的证明。如果私有入口不可用，只公开请求建立私密联系渠道，不要附带漏洞详情。

维护者应在七天内确认收到，完成验证和分级，协调修复与披露日期，并按报告者意愿署名。本项目不承诺漏洞奖金。

## 安全模型

插件不包含 MCP server、远程后端、认证或内置凭据。本地脚本拥有用户授予的文件系统与 Git 权限。实时研究由宿主 Web Search 完成，查询文字可能发送给宿主/搜索提供方。

冻结核心依赖精确 Git 根、SHA-256、锁文件、人工审查和 Git 历史；只读位与 Hooks 是辅助控制。Hooks 可以阻止或发现许多直接操作，但不能认证“人类身份”、撤销已执行修改，也看不到所有外部编辑器、进程或工具。生成提示词和研究输入都应按不可信数据处理。

## 维护者发布清单

- 审查完整 diff 和依赖面。
- 运行全部测试、编译、包校验、冻结示例校验和 `scripts/audit_public_release.py`。
- 确认所有 commit 作者/提交者邮箱都是获准的 no-reply 地址。
- 宿主套餐支持时启用 GitHub secret scanning、push protection、默认分支保护和必需 CI。
- 不得为了发布通过而削弱失败的保护规则。

另见[隐私](docs/PRIVACY.zh-CN.md)、[架构](docs/ARCHITECTURE.zh-CN.md)与[变更控制](docs/CHANGE_CONTROL.zh-CN.md)。