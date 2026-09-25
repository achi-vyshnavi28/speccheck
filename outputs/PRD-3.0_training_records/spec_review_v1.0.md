# Spec review: PRD 3.0: Training records and qualification gates

**Verdict:** NOT ready for development: 1 blocking (high) gap(s), 7 other.

| Story | Criteria | Draft test cases | Criteria without a test | Gaps (high) |
|---|---|---|---|---|
| TR-301 Assign training when an SOP changes | 3 | 4 | 1 | 2 (0) |
| TR-302 Record training completion | 3 | 5 | 0 | 0 (0) |
| TR-303 Block untrained users | 3 | 5 | 0 | 1 (0) |
| TR-304 Training evidence per batch | 3 | 5 | 1 | 3 (0) |
| TR-305 Correct a training record | 2 | 4 | 0 | 2 (1) |

## Questions for product (blocking first)

- **TR-305 [high]** "The coordinator can change the completion date.": A GMP-relevant action (override/delete/change/reject) without a required reason, e-signature or audit-trail entry (21 CFR 11.10(e), 11.50). → *Must this action require a reason, an e-signature and an audit-trail entry? Who may perform it?*
- **TR-301 [medium]** "Assign training when an SOP changes": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **TR-301 [medium]** "Users who are on leave are handled appropriately.": 'appropriately' has no pass/fail criterion. → *What is appropriate, specifically?*
- **TR-304 [medium]** "Training evidence per batch": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **TR-304 [medium]** "The report should be fast.": 'fast' has no pass/fail criterion. → *What response time, measured how?*
- **TR-305 [medium]** "Correct a training record": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **TR-303 [low]** "It must be possible to override this in an emergency.": Starts with a pronoun; the tester can't tell what it refers to. → *Name the object explicitly.*
- **TR-304 [low]** "The report should be fast.": 'should' makes it unclear whether this is mandatory. → *Is this mandatory ('must') or optional?*
