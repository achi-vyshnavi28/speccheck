# Spec review: PRD 4.0: Production logbook for equipment usage and cleaning (first draft)

**Verdict:** NOT ready for development: 3 blocking (high) gap(s), 10 other.

| Story | Criteria | Draft test cases | Criteria without a test | Gaps (high) |
|---|---|---|---|---|
| LB-401 Record equipment usage | 3 | 5 | 0 | 2 (0) |
| LB-402 Record cleaning | 3 | 4 | 0 | 3 (0) |
| LB-403 Show equipment status | 3 | 5 | 0 | 3 (1) |
| LB-404 Correct a logbook entry | 1 | 5 | 0 | 3 (2) |
| LB-405 Logbook review | 2 | 6 | 0 | 2 (0) |

## Questions for product (blocking first)

- **LB-403 [high]** "Clean hold time is TBD per equipment.": Requirement is not decided yet. → *Please decide and specify before development starts.*
- **LB-404 [high]** "The supervisor can edit entries as needed.": 'as needed' has no pass/fail criterion. → *Under which exact conditions, and who decides?*
- **LB-404 [high]** "The supervisor can edit entries as needed.": A GMP-relevant action (override/delete/change/reject) without a required reason, e-signature or audit-trail entry (21 CFR 11.10(e), 11.50). → *Must this action require a reason, an e-signature and an audit-trail entry? Who may perform it?*
- **LB-401 [medium]** "Record equipment usage": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **LB-402 [medium]** "Record cleaning": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **LB-402 [medium]** "Cleaning is verified.": A human action with no role: the record would not be attributable (ALCOA+ 'Attributable'). → *Which role performs this, and can the same person do the previous step?*
- **LB-402 [medium]** "The entry is signed.": A human action with no role: the record would not be attributable (ALCOA+ 'Attributable'). → *Which role performs this, and can the same person do the previous step?*
- **LB-403 [medium]** "Show equipment status": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **LB-403 [medium]** "Each item shows one of: in use, dirty, clean, clean hold expired.": 'expired' implies a limit, but no value is given. → *What is the exact value and unit?*
- **LB-404 [medium]** "Correct a logbook entry": Only 1 acceptance criterion; negative and boundary behaviour are undefined. → *What should happen on invalid input, wrong role, and at the limits?*
- **LB-405 [medium]** "Logbook review": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **LB-405 [medium]** "QA reviews logbooks periodically.": 'periodically' has no pass/fail criterion. → *How often exactly?*
- **LB-401 [low]** "Recording should be quick on the shop floor.": 'should' makes it unclear whether this is mandatory. → *Is this mandatory ('must') or optional?*
