# 贡献指南

[English](CONTRIBUTING.md) | **简体中文**

感谢改进 Idea-to-Build。提交贡献即表示你有权提交相关内容，并同意其按 MIT 许可证提供。

## 开发环境

使用 Python 3.9+ 与 Git；运行时没有第三方包依赖。

```bash
git clone https://github.com/instl999/idea-to-build.git
cd idea-to-build
python -m unittest discover -s tests -v
```

创建聚焦的分支，不混入无关修改，保持 UTF-8 和跨平台标准库兼容。新增依赖前必须说明必要性、维护情况、许可证、安全/隐私、平台支持、锁定风险和替代方案。

## 必须执行的检查

```bash
python -m unittest discover -s tests -v
python -m compileall -q hooks skills/idea-to-build/scripts tests scripts
python skills/idea-to-build/scripts/validate_package.py --path .
python examples/team-brief-generator/scripts/verify_core.py --path examples/team-brief-generator
python scripts/audit_public_release.py --worktree-only
```

行为变更必须增加回归测试；中英文文档同步更新；发布时统一版本号并更新 changelog。除非遵循明确的人类变更控制，不得修改示例的冻结核心或锁；可以重新生成可变的设计、交接和运行时文件，随后重新校验 hash。

## 隐私与提交

使用 GitHub no-reply 或项目专用公开邮箱。不要提交秘密、个人记录、私人绝对路径、机密研究文字、`.env`、生成日志或真实客户/用户夹具。示例必须合成，Web Search 查询必须最小化。

PR 应说明问题、安全/隐私影响、方案、测试、兼容性、文档和剩余风险。安全问题按 [SECURITY.zh-CN.md](SECURITY.zh-CN.md) 私下报告，不要公开提交利用细节。

## 仓库记忆变更

任务状态、门禁 schema、提示词、上下文注入、Stop、迁移或调度属于兼容与安全敏感修改。必须记录威胁、失败/恢复和旧项目行为，补成功与拒绝回归测试，保持中英文公开文档语义同步，更新 `CHANGELOG_AI.md` 与 `PROJECT_STATUS.md`，并确认冻结示例的核心/锁字节未改变。
