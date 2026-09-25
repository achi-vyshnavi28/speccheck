# Spec review: PRD 1.1: Equipment cleaning log and batch rejection

**Verdict:** NOT ready for development: 3 blocking (high) gap(s), 6 other.

| Story | Criteria | Draft test cases | Criteria without a test | Gaps (high) |
|---|---|---|---|---|
| US-101 Record equipment cleaning | 3 | 5 | 0 | 1 (0) |
| US-102 Block batch start on dirty equipment | 2 | 6 | 0 | 0 (0) |
| US-103 Reject a batch | 3 | 4 | 1 | 3 (0) |
| US-104 Override | 1 | 4 | 0 | 3 (2) |
| US-105 Cleaning report | 1 | 4 | 0 | 2 (1) |

## Questions for product (blocking first)

- **US-104 [high]** "QA can override as needed.": 'as needed' has no pass/fail criterion. → *Under which exact conditions, and who decides?*
- **US-104 [high]** "QA can override as needed.": A GMP-relevant action (override/delete/change/reject) without a required reason, e-signature or audit-trail entry (21 CFR 11.10(e), 11.50). → *Must this action require a reason, an e-signature and an audit-trail entry? Who may perform it?*
- **US-105 [high]** "The report shows cleanings. TBD which filters.": Requirement is not decided yet. → *Please decide and specify before development starts.*
- **US-101 [medium]** "Record equipment cleaning": No criterion says what happens when a rule is broken. → *What does the system do on invalid input or a wrong role (message, block, audit entry)?*
- **US-103 [medium]** "The system should handle rejection quickly and be user-friendly.": 'quickly' has no pass/fail criterion. → *What response time, measured how (e.g. p95 < 2 s)?*
- **US-103 [medium]** "The system should handle rejection quickly and be user-friendly.": 'user-friendly' has no pass/fail criterion. → *Which usability criterion (e.g. task done in <= 3 clicks, no training)?*
- **US-104 [medium]** "Override": Only 1 acceptance criterion; negative and boundary behaviour are undefined. → *What should happen on invalid input, wrong role, and at the limits?*
- **US-105 [medium]** "Cleaning report": Only 1 acceptance criterion; negative and boundary behaviour are undefined. → *What should happen on invalid input, wrong role, and at the limits?*
- **US-103 [low]** "The system should handle rejection quickly and be user-friendly.": 'should' makes it unclear whether this is mandatory. → *Is this mandatory ('must') or optional?*
