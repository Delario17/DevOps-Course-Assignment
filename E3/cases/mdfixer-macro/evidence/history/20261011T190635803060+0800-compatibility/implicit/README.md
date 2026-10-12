# MDFixer IMPLICIT actual run

- Operator: Codex automated unified-entrypoint compatibility check; human review pending.
- Started: 2026-10-11T19:07:00.356476+08:00.
- Result: **PASS**, 34/34 assertions passed.

| Stage | Output |
|---|---|
| initial | 10 |
| before_fix_config_4_to_5_incremental | 10 |
| before_fix_config_4_to_5_clean | 11 |
| after_fix_config_4_clean | 10 |
| after_fix_config_4_to_5_incremental | 11 |
| after_fix_config_5_to_6_incremental | 12 |
| restored_output | 12 |

This validates a known reference patch, candidate rejection, and rollback; it is not MDFixer service output.
