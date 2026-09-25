# Spec review: PRD 4.1: Production logbook for equipment usage and cleaning (after spec review)

**Verdict:** Ready for development: 0 blocking (high) gap(s), 3 other.

| Story | Criteria | Draft test cases | Criteria without a test | Gaps (high) |
|---|---|---|---|---|
| LB-401 Record equipment usage | 5 | 4 | 1 | 0 (0) |
| LB-402 Record cleaning | 4 | 5 | 0 | 1 (0) |
| LB-403 Show equipment status | 3 | 5 | 0 | 2 (0) |
| LB-404 Correct a logbook entry | 4 | 4 | 0 | 0 (0) |
| LB-405 Logbook review | 4 | 4 | 0 | 0 (0) |

## Questions for product (blocking first)

- **LB-402 [medium]** "Until a major cleaning is verified, the equipment status stays "dirty".": A human action with no role: the record would not be attributable (ALCOA+ 'Attributable'). → *Which role performs this, and can the same person do the previous step?*
- **LB-403 [medium]** "Each item shows one of: in use, dirty, clean, clean hold expired.": 'expired' implies a limit, but no value is given. → *What is the exact value and unit?*
- **LB-403 [medium]** "When the hold time passes, the status changes to "clean hold expired" and starting usage is refused.": 'expired' implies a limit, but no value is given. → *What is the exact value and unit?*
