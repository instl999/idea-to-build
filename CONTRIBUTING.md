# Contributing

**English** | [简体中文](CONTRIBUTING.zh-CN.md)

Thank you for improving Idea-to-Build. By contributing, you agree that your work is provided under the MIT license and that you have the right to submit it.

## Development setup

Use Python 3.9+ and Git; there are no runtime package dependencies.

```bash
git clone https://github.com/instl999/idea-to-build.git
cd idea-to-build
python -m unittest discover -s tests -v
```

Create a focused branch, keep unrelated changes out, and preserve UTF-8 text and cross-platform standard-library behavior. Do not add dependencies without documenting necessity, maintenance, license, security/privacy, platform support, lock-in, and replacement options.

## Required checks

```bash
python -m unittest discover -s tests -v
python -m compileall -q hooks skills/idea-to-build/scripts tests scripts
python skills/idea-to-build/scripts/validate_package.py --path .
python examples/team-brief-generator/scripts/verify_core.py --path examples/team-brief-generator
python scripts/audit_public_release.py --worktree-only
```

Add regression tests for behavioral changes. Update English and Chinese documentation together, bump versions consistently when releasing, and update the changelog. Do not modify the example's frozen core or lock unless following documented human change control; regenerate mutable design/handoff/runtime files as needed and re-verify the hash.

## Privacy and commits

Use a GitHub no-reply or project-specific public email. Never commit secrets, personal records, private absolute paths, confidential research text, `.env` files, generated logs, or real customer/user fixtures. Use synthetic examples and minimize Web Search queries.

A pull request should explain the problem, security/privacy impact, solution, tests, compatibility, documentation changes, and remaining risks. Security reports follow [SECURITY.md](SECURITY.md), not public pull requests.

## Repository-memory changes

Changes to task state, gate schema, prompts, context injection, Stop, migration, or dispatch are compatibility- and security-sensitive. Document threats, failure/recovery behavior, and old-project behavior; add success and refusal regression tests; keep English/Chinese public docs synchronized; update `CHANGELOG_AI.md` and `PROJECT_STATUS.md`; and verify the frozen example core/lock bytes remain unchanged.
