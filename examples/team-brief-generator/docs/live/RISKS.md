# Risks

- R-001: rule-based extraction may miss linguistic variants; mitigate with golden and adversarial fixtures.
- R-002: source offsets can drift after normalization; mitigate with property tests and immutable source snapshots.
- R-003: local persistence migrations may lose data; mitigate with backup/restore and migration fixtures.
