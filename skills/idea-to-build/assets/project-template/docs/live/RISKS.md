# Risks

| Risk | Likelihood | Impact | Trigger | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Incomplete market evidence | High | High | Live search unavailable or sources conflict | Use `INSUFFICIENT_RESEARCH`; do not claim a gap | Product owner | Open |
| Premature irreversible choice | Medium | High | Architecture selected while ledger remains open | Require explicit confirmation | Product owner | Open |
| Core drift after freeze | Low | High | SHA-256 mismatch | Stop, preserve evidence, use change request | Orchestrator | Monitored |