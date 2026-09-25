# Spec review: PRD 2.0: CAPA management

**Verdict:** NOT ready for development: 2 blocking (high) gap(s), 7 other.

| Story | Criteria | Draft test cases | Criteria without a test | Gaps (high) |
|---|---|---|---|---|
| CAPA-201 Create a CAPA from a deviation | 3 | 4 | 0 | 0 (0) |
| CAPA-202 Assign actions with due dates | 3 | 5 | 0 | 3 (0) |
| CAPA-203 Escalate overdue actions | 2 | 5 | 0 | 2 (0) |
| CAPA-204 Close a CAPA | 3 | 5 | 0 | 0 (0) |
| CAPA-205 Edit a closed CAPA | 1 | 4 | 0 | 2 (1) |
| CAPA-206 Effectiveness check | 3 | 4 | 1 | 2 (1) |

## Questions for product (blocking first)

- **CAPA-205 [high]** "The owner can edit any field of a closed CAPA.": A GMP-relevant action (override/delete/change/reject) without a required reason, e-signature or audit-trail entry (21 CFR 11.10(e), 11.50). → *Must this action require a reason, an e-signature and an audit-trail entry? Who may perform it?*
- **CAPA-206 [high]** "TBD: what happens if the CAPA was not effective.": Requirement is not decided yet. → *Please decide and specify before development starts.*
- **CAPA-202 [medium]** "Assign actions with due dates": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **CAPA-202 [medium]** "Due dates must be reasonable.": 'reasonable' has no pass/fail criterion. → *What is reasonable, specifically?*
- **CAPA-203 [medium]** "Escalate overdue actions": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **CAPA-203 [medium]** "Escalations happen quickly.": 'quickly' has no pass/fail criterion. → *What response time, measured how (e.g. p95 < 2 s)?*
- **CAPA-205 [medium]** "Edit a closed CAPA": Only 1 acceptance criterion; negative and boundary behaviour are undefined. → *What should happen on invalid input, wrong role, and at the limits?*
- **CAPA-206 [medium]** "Results are approved.": A human action with no role: the record would not be attributable (ALCOA+ 'Attributable'). → *Which role performs this, and can the same person do the previous step?*
- **CAPA-202 [low]** "The assignee should receive a notification.": 'should' makes it unclear whether this is mandatory. → *Is this mandatory ('must') or optional?*
