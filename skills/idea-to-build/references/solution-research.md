# Solution research protocol

## Evidence lanes

1. Direct commercial, SaaS, mobile, desktop, browser, IDE, agent, automation-template, and vertical solutions.
2. Alternative and combined workflows, including no-code/low-code, general tools, scripts, templates, plugins, and human-in-the-loop processes.
3. Reusable engineering foundations: official repositories, Agent Skills, MCP servers, SDKs, APIs, starter kits, components, databases, identity systems, deployment templates, and data sources.

Search with user-language and English queries. Do not hard-code any vendor as the only option.

## Required evidence fields

For every candidate record: search date, query, name, type, official source, license, latest maintenance evidence, core capability, requirement coverage, missing capability, deployment, privacy/data handling, approximate price with date, extension effort, vendor lock-in, security risk, and recommendation.

Label evidence, inference, unverified information, and facts likely to become stale. A search snippet is discovery evidence, not final verification.

## Scoring

Compare functional fit, workflow fit, user fit, data/integration fit, privacy/security fit, deployment fit, customizability, cost, maintenance, license risk, lock-in, and implementation time. Show weights and inputs. Scores rank alternatives; they are not market measurements.

## Decisions

- `ADOPT_DIRECTLY`
- `ADOPT_WITH_CONFIGURATION`
- `COMBINE_EXISTING_TOOLS`
- `EXTEND_OPEN_SOURCE`
- `BUILD_CUSTOM`
- `INSUFFICIENT_RESEARCH`
- `NOT_RECOMMENDED`

If live search is unavailable or evidence materially conflicts, use `INSUFFICIENT_RESEARCH`. If no candidate highly covers the request, use the exact concept “candidate requirement gap” and explain that user pain, frequency, current alternatives, adoption intent, and willingness to pay remain unvalidated.